from ultralytics import YOLO
import streamlit as st
import cv2
import json
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    try:
        from pytube import YouTube
        PYTUBE_AVAILABLE = True
    except ImportError:
        PYTUBE_AVAILABLE = False
import supervision as sv
import pandas
from tqdm import tqdm
import settings
import os
from typing import Any, Optional, Tuple, Dict, Iterable, List, Set
import shutil
import cv2
import numpy as np
from utils.general import find_in_list, load_zones_config
from locales.settings_languages import COMPONENTS
from scripts.jxnEvalDataCreation import mainFunc
from structures.VideoProcessor import VideoProcessor
from structures.essentials import drawzones, decrypt_it, encrypt_it
from structures.essentials import display_tracker_options, _display_detected_frames, load_model, get_first_frame
from structures.encroachment import timedetect, livedetection
from structures.benchmarking_queue import BenchMarking
from PIL import Image
from scripts.jxnEvaluator import *
import plotly.express as px
import plotly.figure_factory as ff
import time

KEY_ENTER = 13
KEY_NEWLINE = 10
KEY_ESCAPE = 27
KEY_QUIT = ord("q")
KEY_SAVE = ord("s")
COLORS = sv.ColorPalette.DEFAULT
CARD_IMAGE_SIZE = (300, int(300*0.5625))
VIDEO_DIR_PATH = f"videos/"
IMAGES_DIR_PATH = f"images/"
DETECTIONS_DIR_PATH = f"detections/"


class JunctionEvaluation:
    
    def __init__(self,sourcePath):
        self.sourcePath = sourcePath
        pass
    
    def datasetCreation(self,cycle):
        savePath = "videos/junctionEvalDataset/"
        print("Processing video:", self.sourcePath)
        
        # Handle both Windows and Unix path separators
        normalized_path = self.sourcePath.replace('\\', '/')
        
        # Extract video name from path (handle both absolute and relative paths)
        if '/' in normalized_path:
            videoName = normalized_path.split('/')[-1]
        else:
            videoName = normalized_path
        
        # Remove file extension
        if '.' in videoName:
            videoName = videoName.rsplit('.', 1)[0]
        
        # Create final path with proper path joining
        finalpath = os.path.join(savePath, videoName + "Clips")
        
        # Ensure directory exists
        isExist = os.path.exists(finalpath)
        if (isExist):
            shutil.rmtree(finalpath)
        os.makedirs(finalpath, exist_ok=True)
        
        mainFunc(self.sourcePath, cycle, finalpath)
        settings.updateDirectories()
        return finalpath
                
def startup():
    settings.updateDirectories()

def play_youtube_video(conf, model, language):

    source_youtube = st.sidebar.text_input(COMPONENTS[language]["YOUTUBE_URL"])

    is_display_tracker, tracker = display_tracker_options(language=language)

    if st.sidebar.button(COMPONENTS[language]["DETECT_OBJ"]):
        # Validate URL
        if not source_youtube or source_youtube.strip() == "":
            st.sidebar.error("⚠️ Please enter a valid YouTube URL")
            return
        
        if "youtube.com" not in source_youtube and "youtu.be" not in source_youtube:
            st.sidebar.error("⚠️ Invalid YouTube URL. Please enter a valid YouTube video URL")
            st.sidebar.info("Example: https://www.youtube.com/watch?v=VIDEO_ID")
            return
        
        vid_cap = None
        st_frame = st.empty()
        status_placeholder = st.sidebar.empty()
        
        try:
            status_placeholder.info("🔄 Loading YouTube video...")
            
            stream_url = None
            ytdlp_error = None
            pytube_error = None
            
            # Try using yt-dlp first (more reliable)
            if YT_DLP_AVAILABLE:
                try:
                    ydl_opts = {
                        'format': 'best[height<=720]/best',  # Prefer 720p or lower, fallback to best available
                        'quiet': True,
                        'no_warnings': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Extract video info to get the direct URL
                        info = ydl.extract_info(source_youtube, download=False)
                        if 'url' in info:
                            stream_url = info['url']
                        elif 'requested_formats' in info and len(info['requested_formats']) > 0:
                            # If multiple formats, prefer video format
                            for fmt in info['requested_formats']:
                                if fmt.get('vcodec') != 'none':  # Has video
                                    stream_url = fmt.get('url')
                                    break
                            if not stream_url:
                                stream_url = info['requested_formats'][0].get('url')
                except Exception as e:
                    ytdlp_error = e
                    st.sidebar.warning(f"⚠️ yt-dlp failed: {str(e)[:100]}")
                    # Fall back to pytube if available
            
            # Fallback to pytube if yt-dlp is not available or failed
            if not stream_url and PYTUBE_AVAILABLE:
                try:
                    # Try to get YouTube video stream using pytube
                    yt = YouTube(source_youtube)
                    
                    # Try multiple resolution options as fallback
                    stream = None
                    resolutions = [720, 480, 360, 240, 144]  # Try different resolutions
                    
                    # First, try to get progressive streams (video + audio combined)
                    for res in resolutions:
                        stream = yt.streams.filter(file_extension="mp4", res=res, progressive=True).first()
                        if stream is not None:
                            break
                    
                    # If no progressive stream found, try adaptive streams (video only)
                    if stream is None:
                        for res in resolutions:
                            stream = yt.streams.filter(file_extension="mp4", res=res, adaptive=True).first()
                            if stream is not None:
                                break
                    
                    # If still no stream, try to get any available mp4 stream
                    if stream is None:
                        stream = yt.streams.filter(file_extension="mp4", progressive=True).first()
                        if stream is None:
                            stream = yt.streams.filter(file_extension="mp4").first()
                    
                    # Last resort: get highest resolution availab
                    if stream is None:
                        all_streams = yt.streams.filter(file_extension="mp4")
                        if len(all_streams) > 0:
                            # Get the first available stream
                            stream = all_streams[0]
                    
                    if stream is not None:
                        stream_url = stream.url
                except Exception as e:
                    pytube_error = e
                    # If both failed, raise a combined error
                    if ytdlp_error:
                        error_details = []
                        if ytdlp_error:
                            error_details.append(f"yt-dlp: {str(ytdlp_error)[:100]}")
                        if pytube_error:
                            error_details.append(f"pytube: {str(pytube_error)[:100]}")
                        raise Exception(f"Both methods failed. {' | '.join(error_details)}")
                    else:
                        raise e
            
            if not stream_url:
                status_placeholder.error("❌ Could not find a suitable video stream")
                error_msg = "Unable to find a playable video stream. "
                if not YT_DLP_AVAILABLE and not PYTUBE_AVAILABLE:
                    error_msg += "Please install yt-dlp: pip install yt-dlp"
                else:
                    error_msg += "The video might be restricted or unavailable."
                st.sidebar.error(error_msg)
                if not YT_DLP_AVAILABLE and not PYTUBE_AVAILABLE:
                    st.sidebar.info("💡 Install yt-dlp for better reliability: pip install yt-dlp")
                return
            
            status_placeholder.info("🔄 Connecting to video stream...")
            
            # Open video capture
            vid_cap = cv2.VideoCapture(stream_url)
            
            # Set buffer size to reduce latency
            vid_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Check if video opened successfully
            if not vid_cap.isOpened():
                status_placeholder.error("❌ Failed to open video stream")
                st.sidebar.error("Could not open the video stream. The video might be restricted, age-restricted, or unavailable.")
                st.sidebar.info("💡 Try a different video or check if the video is publicly accessible")
                if vid_cap:
                    vid_cap.release()
                return
            
            status_placeholder.success("✅ Video loaded! Processing frames...")
            
            frame_count = 0
            consecutive_failures = 0
            max_failures = 10
            
            while vid_cap.isOpened():
                success, image = vid_cap.read()
                
                if success:
                    consecutive_failures = 0
                    frame_count += 1
                    
                    # Display frame with detection
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker,
                                             )
                    
                    # Update status periodically
                    if frame_count % 30 == 0:
                        status_placeholder.info(f"📹 Processing... Frames: {frame_count}")
                    
                    # Small delay to prevent overwhelming the UI
                    time.sleep(0.03)  # ~30 FPS
                    
                else:
                    consecutive_failures += 1
                    
                    if consecutive_failures >= max_failures:
                        status_placeholder.warning("⚠️ End of video or stream interrupted")
                        break
                    else:
                        time.sleep(0.1)  # Wait before retrying
            
            status_placeholder.info("✅ Video processing completed")
            
        except Exception as e:
            error_msg = str(e)
            status_placeholder.error("❌ Error loading YouTube video")
            
            # Provide more specific error messages
            if "400" in error_msg or "bad request" in error_msg.lower():
                st.sidebar.error("⚠️ HTTP 400: Bad Request - pytube compatibility issue")
                st.sidebar.info("💡 **Solution:** Install yt-dlp for better reliability:")
                st.sidebar.code("pip install yt-dlp", language="bash")
                st.sidebar.info("yt-dlp is more reliable and actively maintained than pytube.")
            elif "age" in error_msg.lower() or "restricted" in error_msg.lower():
                st.sidebar.error("⚠️ This video is age-restricted or unavailable")
                st.sidebar.info("💡 YouTube videos must be publicly accessible and not age-restricted")
            elif "regex" in error_msg.lower() or "pattern" in error_msg.lower():
                st.sidebar.error("⚠️ Invalid YouTube URL format")
                st.sidebar.info("💡 Please check the URL and try again")
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                st.sidebar.error("⚠️ Network connection error")
                st.sidebar.info("💡 Please check your internet connection")
            else:
                st.sidebar.error(COMPONENTS[language]["VIDEO_ERROR"] + ": " + error_msg[:200])
                st.sidebar.info("💡 **Troubleshooting:**")
                st.sidebar.markdown("""
                - Install yt-dlp: `pip install yt-dlp` (recommended)
                - Video must be publicly accessible (not private/unlisted)
                - Video cannot be age-restricted
                - Check your internet connection
                - Try a different video URL
                """)
            
            if vid_cap:
                vid_cap.release()
        finally:
            if vid_cap:
                vid_cap.release()
                status_placeholder.info("🔴 Video processing stopped")

# def play_stored_video(conf, model,language):

#     source_vid = st.sidebar.selectbox(
#         COMPONENTS[language]["CHOOSE_VID"], settings.VIDEOS_DICT.keys())

#     is_display_tracker, tracker = display_tracker_options(language=language)

#     with open(settings.VIDEOS_DICT[source_vid], 'rb') as video_file:
#         video_bytes = video_file.read()
#     if video_bytes:
#         st.video(video_bytes)

#     if st.sidebar.button(COMPONENTS[language]["DETECT_OBJ"]):
#         try:
#             vid_cap = cv2.VideoCapture(
#                 str(settings.VIDEOS_DICT.get(source_vid)))
#             st_frame = st.empty()
#             while (vid_cap.isOpened()):
#                 success, image = vid_cap.read()
#                 if success:
#                     _display_detected_frames(conf,
#                                              model,
#                                              st_frame,
#                                              image,
#                                              is_display_tracker,
#                                              tracker
#                                              )
#                 else:
#                     vid_cap.release()
#                     break
#         except Exception as e:
#             st.sidebar.error(COMPONENTS[language]["VIDEO_ERROR"] + str(e))

def play_stored_video(conf, model, language):
    # Check if VIDEOS_DICT is empty
    if not settings.VIDEOS_DICT:
        st.warning("⚠️ No videos found in the videos/ directory.")
        st.info("💡 To use video detection:")
        st.info("1. Add video files (.mp4 or .AVI) to the 'videos/' folder")
        st.info("2. Refresh the page or restart the app")
        return
    
    # 1. Select the video key
    source_vid = st.sidebar.selectbox(
        COMPONENTS[language]["CHOOSE_VID"], settings.VIDEOS_DICT.keys())

    # Check if source_vid is None (shouldn't happen, but safety check)
    if source_vid is None:
        st.error("No video selected. Please select a video from the dropdown.")
        return

    is_display_tracker, tracker = display_tracker_options(language=language)

    # 2. SAFELY get the path
    video_path = settings.VIDEOS_DICT.get(source_vid)

    # 3. ERROR HANDLING: Check if path exists before opening
    if video_path is None:
        st.error(f"Configuration Error: Key '{source_vid}' not found in settings.VIDEOS_DICT")
        st.info("Try refreshing the page or adding videos to the videos/ directory.")
        return

    if not os.path.exists(video_path):
        st.error(f"File Not Found Error: Python cannot find the file at: {video_path}")
        st.warning("Please check your settings.py file and ensure the path is absolute or correct relative to the project root.")
        return

    # 4. Safe Open
    try:
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        
        if video_bytes:
            st.video(video_bytes)
    except Exception as e:
        st.error(f"Error reading video file: {str(e)}")
        return

    if st.sidebar.button(COMPONENTS[language]["DETECT_OBJ"]):
        try:
            # Use the validated video_path here as well
            vid_cap = cv2.VideoCapture(str(video_path))
            if not vid_cap.isOpened():
                st.error("Failed to open video file. Please check the file format.")
                return
                
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            vid_cap.release()
            st.sidebar.error(COMPONENTS[language]["VIDEO_ERROR"] + str(e))

def play_rtsp_stream(conf, model, language):
    source_rtsp = st.sidebar.text_input(COMPONENTS[language]["RTSPSTREAM"])
    st.sidebar.caption('Example URL: rtsp://admin:12345@192.168.1.210:554/Streaming/Channels/101')
    
    # Additional RTSP settings
    st.sidebar.subheader("RTSP Settings")
    buffer_size = st.sidebar.slider("Buffer Size (frames)", 1, 10, 1)
    connection_timeout = st.sidebar.slider("Connection Timeout (seconds)", 5, 30, 10)
    
    is_display_tracker, tracker = display_tracker_options(language=language)
    
    if st.sidebar.button(COMPONENTS[language]["DETECT_OBJ"]):
        # Validate RTSP URL
        if not source_rtsp or source_rtsp.strip() == "":
            st.sidebar.error("⚠️ Please enter a valid RTSP URL")
            return
        
        if not source_rtsp.startswith(('rtsp://', 'rtspt://', 'rtmp://', 'http://', 'https://')):
            st.sidebar.error("⚠️ Invalid URL format. RTSP URLs should start with 'rtsp://'")
            st.sidebar.info("Example: rtsp://username:password@ip_address:port/path")
            return
        
        vid_cap = None
        st_frame = st.empty()
        status_placeholder = st.sidebar.empty()
        
        try:
            status_placeholder.info("🔄 Connecting to RTSP stream...")
            
            # Configure OpenCV for RTSP streams
            vid_cap = cv2.VideoCapture(source_rtsp, cv2.CAP_FFMPEG)
            
            # Set buffer size to reduce latency
            vid_cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
            
            # Set timeout properties (if supported by backend)
            vid_cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, connection_timeout * 1000)
            
            # Check if connection is successful
            if not vid_cap.isOpened():
                status_placeholder.error("❌ Failed to connect to RTSP stream")
                st.sidebar.error("Possible issues:")
                st.sidebar.markdown("""
                - Check if the RTSP URL is correct
                - Verify camera credentials (username:password)
                - Ensure camera is accessible on the network
                - Check firewall/network settings
                - Try different RTSP path (e.g., /Streaming/Channels/102)
                """)
                if vid_cap:
                    vid_cap.release()
                return
            
            status_placeholder.success("✅ Connected! Processing stream...")
            
            frame_count = 0
            consecutive_failures = 0
            max_failures = 10
            
            while True:
                success, image = vid_cap.read()
                
                if success:
                    consecutive_failures = 0
                    frame_count += 1
                    
                    # Display frame with detection
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                    
                    # Update status
                    if frame_count % 30 == 0:  # Update every 30 frames
                        status_placeholder.info(f"📹 Streaming... Frames processed: {frame_count}")
                    
                    # Small delay to prevent overwhelming the UI
                    time.sleep(0.03)  # ~30 FPS
                    
                else:
                    consecutive_failures += 1
                    
                    if consecutive_failures >= max_failures:
                        status_placeholder.warning("⚠️ Stream interrupted. Attempting to reconnect...")
                        
                        # Try to reconnect
                        vid_cap.release()
                        time.sleep(2)
                        
                        vid_cap = cv2.VideoCapture(source_rtsp, cv2.CAP_FFMPEG)
                        vid_cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
                        
                        if not vid_cap.isOpened():
                            status_placeholder.error("❌ Reconnection failed. Please check the stream URL.")
                            break
                        
                        status_placeholder.success("✅ Reconnected!")
                        consecutive_failures = 0
                    else:
                        time.sleep(0.1)  # Wait before retrying
                
                # Check if user wants to stop (this is a simple check, Streamlit doesn't have easy stop buttons)
                # The user can refresh the page to stop
                
        except cv2.error as e:
            status_placeholder.error("❌ OpenCV Error")
            st.sidebar.error(f"OpenCV Error: {str(e)}")
            st.sidebar.info("💡 Try installing: pip install opencv-python-headless")
            if vid_cap:
                vid_cap.release()
                
        except Exception as e:
            status_placeholder.error("❌ Connection Error")
            st.sidebar.error(f"Error: {str(e)}")
            st.sidebar.markdown("""
            **Troubleshooting Tips:**
            1. Verify RTSP URL format: `rtsp://user:pass@ip:port/path`
            2. Test camera with VLC player first
            3. Check network connectivity
            4. Ensure camera supports RTSP protocol
            5. Try different RTSP path (e.g., /1, /2, /Streaming/Channels/101)
            """)
            if vid_cap:
                vid_cap.release()
        finally:
            if vid_cap:
                vid_cap.release()
                status_placeholder.info("🔴 Stream stopped")

def enchroachment(confidence: float, language: str):
    global CURRENT_DIR_PATH

    if ("current_dir_path" not in st.session_state):
        st.session_state.current_dir_path = VIDEO_DIR_PATH

    st.text(st.session_state.current_dir_path)
    if ("current_state" not in st.session_state):
        st.session_state.current_state = "homePage"



    if (st.session_state.current_state=="homePage"):
        st.header("Welcome to Bottleneck Detection")
        isVideo = False
        if (st.session_state.current_dir_path.endswith(('.mp4', '.avi','.mov','.AVI'))):
            isVideo = True
            st.session_state.current_state = "Encroachment"
            st.rerun()
        else:
            st.title("Video Gallery")
        
        
        video_files = [f for f in os.listdir(st.session_state.current_dir_path) if f.endswith(('.mp4', '.avi','.mov','.AVI'))]
        folders = [f for f in os.listdir(st.session_state.current_dir_path) if '.' not in f]
        # Display videos in a grid
        cols = st.columns(3)  # Adjust the number of columns as needed
        video_files = folders+video_files
        if (st.session_state.current_dir_path!=VIDEO_DIR_PATH):
            if (st.button("Back")):
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")]
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")+1]
                st.rerun()

        for idx, video_file in enumerate(video_files):
            with cols[idx % 3]:  # Change 3 to the number of columns you want
                video_path = os.path.join(st.session_state.current_dir_path, video_file)
                first_frame = get_first_frame(video_path)
                if (idx < len(folders)):
                    first_frame = Image.open(IMAGES_DIR_PATH+"/FolderIcon.png")
                    first_frame = first_frame.resize(CARD_IMAGE_SIZE, Image.LANCZOS)
                    st.image(first_frame, width='stretch')
                    st.write(video_file)
                    if st.button(f"Navigate to {video_file}", key=video_file):
                        st.session_state.current_dir_path= st.session_state.current_dir_path+video_file+"/"
                        st.rerun()
                        
                else:
                    if first_frame:
                        st.image(first_frame, width='stretch')
                        st.write(video_file)
                        if st.button(f"Detect Bottlenecks for {video_file}", key=video_file):
                            st.session_state.current_dir_path = st.session_state.current_dir_path+video_file
                            st.rerun()

    if(st.session_state.current_state == "Encroachment"):                
    #source_vid = st.sidebar.selectbox(
    #COMPONENTS[language]["CHOOSE_VID"], settings.VIDEOS_DICT.keys())
        
        source_path = st.session_state.current_dir_path
        col1, col2 = st.columns([3,1])
        with col1:
            st.title("Bottleneck Detection: " + st.session_state.current_dir_path[st.session_state.current_dir_path.rfind("/")+1:])
        with col2:
            if (st.button("Back to video gallery")):
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
                st.session_state.current_state = "homePage"
                st.rerun()
        time = st.text_input(COMPONENTS[language]["VIOLATION_TIME"], placeholder="Enter Violation Time")
        
        source_url = st.text_input(COMPONENTS[language]["SOURCE_URL_RTSP"], placeholder="Enter RTSP URL:")
        
        new_path = source_path.split("/")[-1]
        zones_configuration_path = "configure/ZONES"+new_path+".json"
        analysis_path = "analysis/encroachments/data_encroachment"+new_path+".csv"
        
        # Check if zones exist
        zones_exist = os.path.exists(zones_configuration_path)
        
        if not zones_exist:
            st.warning("⚠️ Zones not configured for this video. Please configure zones first.")
            drawzones(source_path = source_path, zone_configuration_path = zones_configuration_path)
            # After zones are saved, rerun to show detection button
            if os.path.exists(zones_configuration_path):
                st.success("✅ Zones saved! Click the detection button below to start analysis.")
                st.rerun()
        else:
            st.success("✅ Zones configured. Ready for detection!")
            # Show zone preview
            try:
                with open(zones_configuration_path, 'r') as f:
                    zones_data = json.load(f)
                    st.info(f"📋 {len(zones_data)} zone(s) configured")
            except:
                pass
        
        if st.button(COMPONENTS[language]["BOTTLENECK_ERRORS"]):
            if not time or time.strip() == "":
                st.error("⚠️ Please enter violation time!")
                return
                
            try:
                violation_time = float(time)
            except ValueError:
                st.error("⚠️ Invalid violation time! Please enter a number.")
                return
            
            if(source_url): 
                zones_configuration_path = "configure/ZONESFootage_Feed_6.mp4.json"
                analysis_path = "analysis/encroachments/data_"+source_url+".csv"
                livedetection(source_url=source_url, violation_time=int(violation_time), zone_configuration_path=zones_configuration_path,confidence=confidence, analysis_path=analysis_path)
            else:
                if not zones_exist:
                    st.error("❌ Zones must be configured before running detection!")
                    return
                    
                timedetect(source_path = source_path, zone_configuration_path = zones_configuration_path, violation_time=violation_time, confidence=confidence, language=language, analysis_path=analysis_path) 
                                   
def junctionEvaluationDataset(language: str):
    source_vid = st.sidebar.selectbox(
    COMPONENTS[language]["CHOOSE_VID"], settings.VIDEOS_DICT.keys())
    source_path = str(settings.VIDEOS_DICT.get(source_vid))

    successVar = False
    cycle = []
    try:
        cycle = st.sidebar.text_input(COMPONENTS[language]["CYCLE"])
        cycle = cycle.split()
        cycle = [int (i) for i in cycle]
        successVar = True
    except:
        pass
    # time = st.sidebar.text_input("Violation Time:")
    #source_url = st.sidebar.text_input("Source Url:")
    
    if st.sidebar.button(COMPONENTS[language]["CREATE_DATASET"]):
        if (successVar == False):
            st.sidebar.error(COMPONENTS[language]["INVALID_SYNTAX"])
            pass
        else:
            jxnEvalInstance = JunctionEvaluation(source_path)
            returnPath = jxnEvalInstance.datasetCreation(cycle=cycle)
            st.sidebar.write(COMPONENTS[language]["SUCCESS_DATA"]+returnPath)

def calculateWholeJunction(finalDict):
    """
    Counts the total number of unique vehicles per class based on the finalDict.
    """
    summary_table = {}
    
    # Iterate through every unique tracked object
    for tracker_id, instance in finalDict.items():
        # In your cleaningDataset function, instance.classId becomes an integer (e.g., 2 for car)
        class_id = instance.classId
        
        if class_id in summary_table:
            summary_table[class_id] += 1
        else:
            summary_table[class_id] = 1
            
    return summary_table  
                  
def junctionEvaluation(model, language):
    # 1. Initialize Session State for Navigation
    if ("current_dir_path" not in st.session_state):
        st.session_state.current_dir_path = VIDEO_DIR_PATH

    # st.text(st.session_state.current_dir_path) # Optional debug text

    if ("current_state" not in st.session_state):
        st.session_state.current_state = "homePage"

    # 2. STATE: Home Page (Video Gallery)
    if (st.session_state.current_state=="homePage"):
        isVideo = False
        if (st.session_state.current_dir_path.endswith(('.mp4', '.avi','.mov','.AVI'))):
            isVideo = True
            st.session_state.current_state = "checkingDetections"
            st.rerun()
        else:
            st.title("Video Gallery")

        video_files = [f for f in os.listdir(st.session_state.current_dir_path) if f.endswith(('.mp4', '.avi','.mov','.AVI'))]
        folders = [f for f in os.listdir(st.session_state.current_dir_path) if '.' not in f]
        
        # Display videos in a grid
        cols = st.columns(3)
        video_files = folders + video_files
        
        # Back Button Logic
        if (st.session_state.current_dir_path != VIDEO_DIR_PATH):
            if (st.button("Back")):
                # Go up one directory level
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")]
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")+1]
                st.rerun()

        # Render Folders and Videos
        for idx, video_file in enumerate(video_files):
            with cols[idx % 3]:
                video_path = os.path.join(st.session_state.current_dir_path, video_file)
                
                # Check if it's a folder
                if (idx < len(folders)):
                    # Use a default folder icon if available, or just text
                    if os.path.exists(IMAGES_DIR_PATH+"/FolderIcon.png"):
                        first_frame = Image.open(IMAGES_DIR_PATH+"/FolderIcon.png")
                        first_frame = first_frame.resize(CARD_IMAGE_SIZE, Image.LANCZOS)
                        st.image(first_frame, use_column_width=True)
                    else:
                        st.info("📁") # Fallback icon
                    
                    st.write(video_file)
                    if st.button(f"Navigate to {video_file}", key=video_file):
                        st.session_state.current_dir_path = st.session_state.current_dir_path + video_file + "/"
                        st.rerun()
                        
                # It is a video file
                else:
                    first_frame = get_first_frame(video_path)
                    if first_frame:
                        st.image(first_frame, use_column_width=True)
                        st.write(video_file)
                        if st.button(f"Analyze {video_file}", key=video_file):
                            st.session_state.current_dir_path = st.session_state.current_dir_path + video_file
                            st.rerun()

    # 3. STATE: Checking Detections
    if (st.session_state.current_state == "checkingDetections"):
        col1, col2 = st.columns([3,1])
        with col1:
            st.title("Analysis: " + st.session_state.current_dir_path.split("/")[-1])
        with col2:
            if (st.button("Back to video gallery")):
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
                st.session_state.current_state = "homePage"
                st.rerun()
        
        detections_path, exists, detections = loadDetections(st.session_state.current_dir_path)
        
        if (not exists):
            st.subheader("Detections not found!")
            if (st.button("Obtain and save detections")):
                with st.spinner("Running Object Detection... This may take a while."):
                    detections = get_detections(st.session_state.current_dir_path)
                    saveDetections(detections=detections, filename=detections_path)
                st.success("Detections saved!")
                st.rerun()
        else:
            st.session_state.current_state = "DetectionsFound"
            st.rerun()
    
    # 4. STATE: Detections Found (Menu)
    if (st.session_state.current_state == "DetectionsFound"):
        st.subheader("Detections found!")
        if (st.button("Back to video gallery")):
            st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
            st.session_state.current_state = "homePage"
            st.rerun()
            
        col1, col2 = st.columns([1,1])
        with col1:
            if (st.button("Analyze whole junction")):
                st.session_state.current_state = "analyzeWholeJxn" 
                st.rerun()     
        with col2:
            if (st.button("✨ Roadwise Analysis (BETA)")): 
                st.session_state.current_state = "roadwiseanalysis"
                st.rerun()

    # 5. STATE: Settings for Analysis
    if (st.session_state.current_state == "analyzeWholeJxn"):
        if (st.button("Back to video gallery")):
            st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
            st.session_state.current_state = "homePage"
            st.rerun()
            
        col1,col2 = st.columns([3,1])
        with col1:
            frameThreshold = st.slider("Frame Threshold", min_value=10, max_value=50, value=24)
            st.session_state.frameThreshold = frameThreshold
        with col2:
            if (st.button("Detect")):
                st.session_state.current_state = "wholeJunction"
                detections_path, exists, detections = loadDetections(st.session_state.current_dir_path)
                
                # Make sure cleaningDataset is defined or imported!
                finalDict = cleaningDataset(detections=detections, frameThreshold=st.session_state.frameThreshold)
                st.session_state.finalDict = finalDict
                st.session_state.current_state = "analysis"
                st.rerun()    
        st.subheader("Any vehicle detected in < frameThreshold frames would not be considered in final analysis")

    # 6. STATE: Final Analysis Table
    if (st.session_state.current_state == "analysis"):
        if (st.button("Back to video gallery")):
            st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
            st.session_state.current_state = "homePage"
            st.rerun()
            
        # Ensure calculateWholeJunction is defined in helper.py
        table = calculateWholeJunction(st.session_state.finalDict)
        
        newTable = {}
        for i in table.keys():
            # THIS IS WHERE 'model' IS USED
            class_name = model.model.names[i]
            newTable[class_name] = table[i]
            
        df = pandas.DataFrame.from_dict(newTable, orient='index', columns=['Value'])
        st.title('Number of vehicles detected in given clip')
        st.table(df)
       
        
def benchMarking(confidence: float, language:str):
    
    global CURRENT_DIR_PATH

    if ("current_dir_path" not in st.session_state):
        st.session_state.current_dir_path = VIDEO_DIR_PATH

    st.text(st.session_state.current_dir_path)
    if ("current_state" not in st.session_state):
        st.session_state.current_state = "homePage"



    if (st.session_state.current_state=="homePage"):
        st.header("Welcome To Benchmarking")
        isVideo = False
        if (st.session_state.current_dir_path.endswith(('.mp4', '.avi','.mov','.AVI'))):
            isVideo = True
            st.session_state.current_state = "Benchmarking"
            st.rerun()
        else:
            st.title("Video Gallery")
        
        
        video_files = [f for f in os.listdir(st.session_state.current_dir_path) if f.endswith(('.mp4', '.avi','.mov','.AVI'))]
        folders = [f for f in os.listdir(st.session_state.current_dir_path) if '.' not in f]
        # Display videos in a grid
        cols = st.columns(3)  # Adjust the number of columns as needed
        video_files = folders+video_files
        if (st.session_state.current_dir_path!=VIDEO_DIR_PATH):
            if (st.button("Back")):
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")]
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")+1]
                st.rerun()

        for idx, video_file in enumerate(video_files):
            with cols[idx % 3]:  # Change 3 to the number of columns you want
                video_path = os.path.join(st.session_state.current_dir_path, video_file)
                first_frame = get_first_frame(video_path)
                if (idx < len(folders)):
                    first_frame = Image.open(IMAGES_DIR_PATH+"/FolderIcon.png")
                    first_frame = first_frame.resize(CARD_IMAGE_SIZE, Image.LANCZOS)
                    st.image(first_frame, width='stretch')
                    st.write(video_file)
                    if st.button(f"Navigate to {video_file}", key=video_file):
                        st.session_state.current_dir_path= st.session_state.current_dir_path+video_file+"/"
                        st.rerun()
                        
                else:
                    if first_frame:
                        st.image(first_frame, width='stretch')
                        st.write(video_file)
                        if st.button(f"Benchmark {video_file}", key=video_file):
                            st.session_state.current_dir_path = st.session_state.current_dir_path+video_file
                            st.rerun()
    
    if(st.session_state.current_state == "Benchmarking"):
    
        #source_vid = st.sidebar.selectbox(
        #COMPONENTS[language]["CHOOSE_VID"], settings.VIDEOS_DICT.keys())
        
        
        col1, col2 = st.columns([3,1])
        with col1:
            st.title("Benchmark: " + st.session_state.current_dir_path[st.session_state.current_dir_path.rfind("/")+1:])
        with col2:
            if (st.button("Back to video gallery")):
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
                st.session_state.current_state = "homePage"
                st.rerun()
        
        source_path = st.session_state.current_dir_path
        traffic_data = st.file_uploader(COMPONENTS[language]["TRAFFIC_DATA"], type=("csv"))
        
        time = st.text_input(COMPONENTS[language]["ACCURACY_INTERVAL"])
        choice = st.radio(COMPONENTS[language]["BENCHMARKING_CRIT"], [COMPONENTS[language]["BENCHMARKING_FLOW"], COMPONENTS[language]["BENCHMARKING_QUEUE_LENGTH"]])
        
        new_path = source_path.split("/")[-1]
        
        zones_IN_configuration_path = "configure/ZONES_IN"+new_path+".json"
        zones_OUT_configuration_path = "configure/ZONES_OUT"+new_path+".json"
        weight_path = "weights/yolov8n.pt"
        col1, col2, col3 = st.columns(3)
        
        with col3:
            button1 = st.button(COMPONENTS[language]["ZONES_IN"])

        with col2:
            button2 = st.button(COMPONENTS[language]["ZONES_OUT"])

        with col1:
            button3 = st.button(COMPONENTS[language]["BENCHMARK"])
        
        if(button1):
            drawzones(source_path = source_path, zone_configuration_path = zones_IN_configuration_path)
            st.sidebar.write("ZONES_IN "+COMPONENTS[language]["SUCCESS"]+zones_IN_configuration_path)
        
        if(button2):    
            drawzones(source_path = source_path, zone_configuration_path = zones_OUT_configuration_path)
            st.sidebar.write("ZONES_OUT "+COMPONENTS[language]["SUCCESS"]+zones_OUT_configuration_path)
            
        if(button3):
            
                if traffic_data is not None:
                    df = pandas.read_csv(traffic_data)
                    if(choice == COMPONENTS[language]["BENCHMARKING_FLOW"]):
                        analysis_path = "analysis\\accuracy\Flow Rate\data_flow_rate"+new_path+".csv"
                        processor = VideoProcessor(
                        source_weights_path=weight_path,
                        source_video_path=source_path,
                        zoneIN_configuration_path=zones_IN_configuration_path,
                        zoneOUT_configuration_path=zones_OUT_configuration_path,  
                        time = float(time),
                        confidence_threshold=confidence,
                        dataFrame = df,
                        analysis_path = analysis_path
                    )
                        processor.process_video()
                    elif COMPONENTS[language]["BENCHMARKING_QUEUE_LENGTH"]:
                        analysis_path = "analysis\\accuracy\Queue Length\data_queuelength"+new_path+".csv"
                        BenchMarking(source_path=source_path, zones_IN_configuration_path=zones_IN_configuration_path, weight_path=weight_path, dataFrame=df, time_analysis=float(time),confidence=confidence, language=language, analysis_path=analysis_path)
                else:
                    st.sidebar.warning(COMPONENTS[language]["TRAFFIC_DATA_NOT_UPLOADED"])
                    return
            
def Analyze(language):
    global showGraph
    if "authorize" not in st.session_state:
        st.session_state.authorize = "LogOut"
    if "current" not in st.session_state:
        st.session_state.current = "Home"
    
    if st.session_state.current == "Home":
        st.header("Welcome To Analysis")
        st.subheader("Authorization: ")
        auth_token=st.text_input("Auth Token",type="password", placeholder="Enter Your authorization token")
        auth_button = st.button("LOG IN")
        if(auth_button):
            if(auth_token == settings.ENCRYPTION_KEY):
                st.session_state.current = "Login" 
                st.session_state.authorize = "Login"
                st.rerun()
            else:
                st.session_state.current = "Home"
                st.sidebar.error("Invalid Auth Token!")
                st.rerun()
                
    if st.session_state.authorize == "Login":
        
        logout = st.sidebar.button("Log Out")
        if(logout):
            st.session_state.current = "Home"
            st.session_state.authorize = "LogOut"
            st.success("Logged Out")
            st.rerun()
     
        analysis_crit = st.selectbox("Analysis Criteria",
            [COMPONENTS[language]["ACCURACY"],COMPONENTS[language]["ENCROACHMENT"],"Encryption"]
        )
        
        st.session_state.current = analysis_crit
        
    if(st.session_state.current!="Encryptions" and st.session_state.authorize == "Login"):

        visualize = st.button("Visualize")
        if(visualize):
            st.session_state.current = "Visualize"
        
        if(st.session_state.current == COMPONENTS[language]["ACCURACY"]):
            
            if("parameter" not in st.session_state):
                st.session_state.parameter = "Queue Length" 
            parameter = st.radio("Choose Parameter",[COMPONENTS[language]["FLOW_HEADER"].split(":")[-2],"Queue Length"])
            st.session_state.parameter = parameter
            
            if st.session_state.parameter == COMPONENTS[language]["FLOW_HEADER"].split(":")[-2]:
                files = st.selectbox("Select file for analysis",settings.FLOW_DICT.keys())
                file_path = str(settings.FLOW_DICT.get(files))
                
                execute_1 = st.button("Begin Analyis")
                if(execute_1):
                    try:
                        decrypt_it(file_path, key = auth_token)
                        df = pandas.read_csv(file_path)
                        st.write(df)
                    except: 
                        df = pandas.read_csv(file_path, on_bad_lines='skip')
                        st.write(df)
                    if(showGraph):
                        fig = px.scatter(df, x="Time", y=list(df.columns)[1:], width = 800, height = 400)
                        fig.update_layout(showlegend = False)
                        st.plotly_chart(fig)
                        showGraph = False
             
            if st.session_state.parameter == "Queue Length":
                files = st.selectbox("Select file for analysis",settings.QUEUE_DICT.keys())
                file_path = str(settings.QUEUE_DICT.get(files))
    
                execute_1 = st.button("Begin Analyis")
                if(execute_1):
                    try:
                        decrypt_it(file_path, key = auth_token)
                        df = pandas.read_csv(file_path)
                        df = df.drop_duplicates(subset=["Time"])
                        st.write(df)
                    except: 
                        df = pandas.read_csv(file_path)
                        df = df.drop_duplicates(subset=["Time"])
                        st.write(df)
                    if(showGraph):
                        fig = px.scatter(df, x="Time", y=list(df.columns)[1:], width = 800, height = 400)
                        fig.update_layout(showlegend = False)
                        st.plotly_chart(fig)
                        showGraph = False
                    
                    #st.write(decrypt_it(file_path, key = auth_token))
            
        if(st.session_state.current == COMPONENTS[language]["ENCROACHMENT"]):
            files = st.selectbox("Select file for analysis",settings.ENCROACHMENT_DICT.keys())
            file_path = str(settings.ENCROACHMENT_DICT.get(files))
                
            execute_2 = st.button("Begin Analyis")
            if(execute_2):
                try:
                    decrypt_it(file_path, key = auth_token)
                    df = pandas.read_csv(file_path)
                    st.write(df) 
                except:
                    df = pandas.read_csv(file_path)
                    st.write(df)
                if(showGraph):
                    st.subheader("Tracker Id Vs. Location")
                    
                    fig = px.scatter(df, x="Tracker_ID", y="Location", color ="Class")
                    
                    #st.plotly_chart(ff.createdf.plot(kind="scatter", x="Class", y="Location", ax=ax))
                    #plt.savefig("Image_Plot1")
                    #plot_frame = st.empty()
                    #plot_frame.image("Image_Plot1.png")
                    st.plotly_chart(fig)
                    st.subheader("Tracer Id Vs. Class")
                    fig = px.scatter(df, x = "Tracker_ID", y="Class", color = "Location")
                    st.plotly_chart(fig, theme=None)
                    showGraph = False
        
            
        
        if(st.session_state.current == "Visualize"):
            showGraph = True
            
            st.session_state.current = analysis_crit
            st.rerun()
            
        
        
            
            
                    
                #st.write(decrypt_it(file_path, key = auth_token))
    if(st.session_state.current == "Encryption"):
        
        all = list(settings.ENCROACHMENT_DICT.keys())
        all.extend(list(settings.FLOW_DICT.keys()))
        all.extend(list(settings.QUEUE_DICT.keys()))
        files = st.selectbox("Select file for analysis",all)
        if files in settings.ENCROACHMENT_DICT.keys():
            file_path = str(settings.ENCROACHMENT_DICT.get(files))
        elif files in settings.FLOW_DICT.keys():
            file_path = str(settings.FLOW_DICT.get(files))
        else:
            file_path = str(settings.QUEUE_DICT.get(files))
        if(st.button("Encrypt")):    
            encrypt_it(path_csv=file_path)
            st.success("Encryption Successful!")
   
def get_first_frame(video_path, size=CARD_IMAGE_SIZE):
    """Extract the first frame from a video file and resize it to the given size."""
    # Validate video_path before attempting to open
    if not video_path or not isinstance(video_path, str) or video_path.strip() == "":
        return None
    
    # Check if file exists
    if not os.path.exists(video_path):
        return None
    
    vidcap = cv2.VideoCapture(video_path)
    if not vidcap.isOpened():
        vidcap.release()
        return None
    
    success, image = vidcap.read()
    vidcap.release()
    
    if success:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image)
        pil_image = pil_image.resize(size, Image.LANCZOS)
        return pil_image
    else:
        return None

def loadDetections(video_path):
    """
    Ensure the necessary directories exist for the given video path in the detections directory.
    If they don't exist, create them and add an empty sample.txt file.
    """

    video_relative_path = os.path.relpath(video_path, VIDEO_DIR_PATH)
    detections_path = os.path.join('detections', video_relative_path)
    detections_path = os.path.splitext(detections_path)[0] + '.dat'
    detections_dir = os.path.dirname(detections_path)
    print(detections_dir)
    if not os.path.exists(detections_dir):
        os.makedirs(detections_dir, exist_ok=True)
        sample_file_path = os.path.join(detections_dir, 'sample.txt')
        with open(sample_file_path, 'w') as f:
            pass

    if not os.path.exists(detections_path):
        return detections_path, False, []
    else:
        f = open(detections_path,"rb")
        detections = pickle.load(f)
        f.close()
        return detections_path, True, detections

def junctionEvaluation(language):
    global CURRENT_DIR_PATH

    if ("current_dir_path" not in st.session_state):
        st.session_state.current_dir_path = VIDEO_DIR_PATH

    st.text(st.session_state.current_dir_path)
    if ("current_state" not in st.session_state):
        st.session_state.current_state = "homePage"



    if (st.session_state.current_state=="homePage"):
        isVideo = False
        if (st.session_state.current_dir_path.endswith(('.mp4', '.avi','.mov','.AVI'))):
            isVideo = True
            st.session_state.current_state = "checkingDetections"
            st.rerun()
        else:
            st.title("Video Gallery")

        video_files = [f for f in os.listdir(st.session_state.current_dir_path) if f.endswith(('.mp4', '.avi','.mov','.AVI'))]
        folders = [f for f in os.listdir(st.session_state.current_dir_path) if '.' not in f]
        # Display videos in a grid
        cols = st.columns(3)  # Adjust the number of columns as needed
        video_files = folders+video_files
        
        if (st.session_state.current_dir_path!=VIDEO_DIR_PATH):
            if (st.button("Back")):
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")]
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind("/")+1]
                st.rerun()

        for idx, video_file in enumerate(video_files):
            with cols[idx % 3]:  # Change 3 to the number of columns you want
                video_path = os.path.join(st.session_state.current_dir_path, video_file)
                first_frame = get_first_frame(video_path)
                if (idx < len(folders)):
                    first_frame = Image.open(IMAGES_DIR_PATH+"/FolderIcon.png")
                    first_frame = first_frame.resize(CARD_IMAGE_SIZE, Image.LANCZOS)
                    st.image(first_frame, width='stretch')
                    st.write(video_file)
                    if st.button(f"Navigate to {video_file}", key=video_file):
                        st.session_state.current_dir_path= st.session_state.current_dir_path+video_file+"/"
                        st.rerun()
                        
                else:
                    if first_frame:
                        st.image(first_frame, width='stretch')
                        st.write(video_file)
                        if st.button(f"Analyze {video_file}", key=video_file):
                            st.session_state.current_dir_path = st.session_state.current_dir_path+video_file
                            st.rerun()
                            



    if (st.session_state.current_state=="checkingDetections"):
        col1, col2 = st.columns([3,1])
        with col1:
            st.title("Analysis: " + st.session_state.current_dir_path[st.session_state.current_dir_path.rfind("/")+1:])
        with col2:
            if (st.button("Back to video gallery")):
                st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
                st.session_state.current_state = "homePage"
                st.rerun()
        detections_path, exists, detections = loadDetections(st.session_state.current_dir_path)
        if (not exists):
            st.subheader("Detections not found!")
            if (st.button("Obtain and save detections")):
                detections = get_detections(st.session_state.current_dir_path)
                saveDetections(detections=detections,filename=detections_path)
                st.rerun()
        else:
            st.session_state.current_state = "DetectionsFound"
            st.rerun()
    
    if (st.session_state.current_state == "DetectionsFound"):
        st.subheader("Detections found!")
        if (st.button("Back to video gallery")):
            st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
            st.session_state.current_state = "homePage"
            st.rerun()
        col1, col2 = st.columns([1,1])
        with col1:
            if (st.button("Analyze whole junction")):
                st.session_state.current_state = "analyzeWholeJxn" 
                st.rerun()     
        with col2:
            if (st.button("✨ Roadwise Analysisᴮᴱᵀᴬ")): 
                st.session_state.current_state = "roadwiseanalysis"
                st.rerun()

    if (st.session_state.current_state == "analyzeWholeJxn"):
        if (st.button("Back to video gallery")):
            st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
            st.session_state.current_state = "homePage"
            st.rerun()
        col1,col2 = st.columns([3,1])
        with col1:
            frameThreshold = st.slider("Frame Threshold",min_value=10,max_value=50,value=24)
            if ("frameThreshold" not in st.session_state):
                st.session_state.frameThreshold = frameThreshold
        with col2:
            if (st.button("Detect")):
                st.session_state.current_state = "wholeJunction"
                detections_path, exists, detections = loadDetections(st.session_state.current_dir_path)
                finalDict = cleaningDataset(detections=detections,frameThreshold=st.session_state.frameThreshold)
                st.session_state.finalDict = finalDict
                st.session_state.current_state = "analysis"
                st.rerun()    
        st.subheader("Any vehicle detected in < frameThreshold frames would not be considered in final analysis")

    if (st.session_state.current_state == "analysis"):
        if (st.button("Back to video gallery")):
            st.session_state.current_dir_path = st.session_state.current_dir_path[:st.session_state.current_dir_path.rfind('/')+1]
            st.session_state.current_state = "homePage"
            st.rerun()
        table = calculateWholeJunction(st.session_state.finalDict)
        newTable = {}
        for i in table.keys():
            newTable[model.model.names[i]] = table[i]
            print(model.model.names[i])
        print(newTable)
        df = pandas.DataFrame.from_dict(newTable, orient='index', columns=['Value'])
        st.title('Number of vehicles detected in given clip')
        st.table(df)

    # Specify the directory containing videos

    # Fetch query parameters

    # Fetch all video files


                            


        
    '''# if (len(settings.EVALUATION_DICT.keys()) == 0):
    #     st.sidebar.error("Create a dataset first")
    # else:
    #     source_dir = st.sidebar.selectbox(
    #     "Choose a folder", settings.EVALUATION_DICT.keys())
        
    #     source_path = str(settings.EVALUATION_DICT.get(source_dir))
    #     source_vid = st.sidebar.selectbox(
    #     "Choose a clip", settings.FINAL_DICT[source_dir].keys())
        
        
    #     with open("videos/JunctionEvalDataset/"+source_dir+"/"+source_vid, 'rb') as video_file:
    #         video_bytes = video_file.read()
    #     if video_bytes:
    #         st.video(video_bytes)

    #     threshold = st.sidebar.text_input(
    #         "Enter a integer in range 1-5"
    #     )

    #     try:
            
    #         threshold = int(threshold)
    #         if (threshold > 5 or threshold < 1):
    #             st.sidebar.error("Enter a valid value")
    #         else:
    #             if st.sidebar.button("Start Evaluation"):
    #                 returnVid = "videos/JunctionEvaluations/IndiraNagarClips/clip1.mp4"
    #                 with open(returnVid, 'rb') as video_file2:
    #                     video_bytes2 = video_file2.read()
                        
    #                 if video_bytes2:
    #                     st.video(video_bytes2)
                    
                                                            
    #     except:
    #         st.sidebar.error("Enter a valid integer")'''            

            
                
        
