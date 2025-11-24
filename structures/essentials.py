from ultralytics import YOLO
import re
import json
from courier import Courier
import secrets
from argon2 import PasswordHasher
import requests
import cv2

import supervision as sv

import json
import os
from typing import Any, Optional, Tuple, Dict, Iterable, List, Set
import cv2
import numpy as np
import streamlit as st
import settings
from cryptography.fernet import Fernet
from locales.settings_languages import COMPONENTS
import pandas
from PIL import Image

CARD_IMAGE_SIZE = (300, int(300*0.5625))
KEY_ENTER = 13
KEY_NEWLINE = 10
KEY_ESCAPE = 27
KEY_QUIT = ord("q")
KEY_SAVE = ord("s")
FRAME_NUM = 0
THICKNESS = 2
COLORS = sv.ColorPalette.DEFAULT
WINDOW_NAME = "Draw Zones"
POLYGONS = [[]]
violations = []
displayed={}
curr_count_dict={}
prev_count_dict= {}
COLOR_ANNOTATOR = sv.ColorAnnotator(color=COLORS)
LABEL_ANNOTATOR = sv.LabelAnnotator(
    color=COLORS, text_color=sv.Color.from_hex("#000000")
)
current_mouse_position: Optional[Tuple[int, int]] = None


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

def drawzones(source_path, zone_configuration_path):
    """
    Streamlit-compatible zone drawing function.
    Uses a text-based coordinate input system since OpenCV windows don't work in Streamlit.
    """
    def resolve_source(source_path: str) -> Optional[np.ndarray]:
        if not os.path.exists(source_path):
            return None
        # Handle Windows path separator
        path_parts = source_path.replace('\\', '/').split('/')
        if path_parts[-1] != "Footage_Feed_5.MP4":
            image = cv2.imread(source_path)
            if image is not None:
                return image
        else:
            # Try both Windows and Unix path separators
            alt_path = source_path.replace('\\', '/').replace('videos/', 'videos/')
            image = cv2.imread(alt_path.replace('.mp4', '.jpg').replace('.MP4', '.jpg'))
            if image is None:
                # Try Windows path
                image = cv2.imread("videos\\Footage_Feed_5.jpg")
            if image is not None:
                return image

        # Try to get first frame from video
        try:
            frame_generator = sv.get_video_frames_generator(source_path=source_path)
            frame = next(frame_generator)
            return frame
        except Exception:
            return None
    
    def save_polygons_to_json(polygons, target_path):
        data_to_save = polygons if polygons[-1] else polygons[:-1]
        # Ensure directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w") as f:
            json.dump(data_to_save, f)
    
    # Check if we're in Streamlit environment
    try:
        import streamlit as st
        IN_STREAMLIT = True
    except ImportError:
        IN_STREAMLIT = False
    
    if IN_STREAMLIT:
        # Streamlit-compatible zone drawing
        original_image = resolve_source(source_path=source_path)
        if original_image is None:
            st.error("❌ Failed to load source image or video.")
            st.info("💡 Please ensure the file exists and is a valid image or video file.")
            return
        
        # Convert BGR to RGB for display
        display_image = cv2.cvtColor(original_image.copy(), cv2.COLOR_BGR2RGB)
        height, width = display_image.shape[:2]
        
        st.info("📝 **Zone Drawing Instructions:**")
        st.markdown("""
        1. **Enter coordinates** in the format: `x1,y1 x2,y2 x3,y3 ...` (minimum 3 points)
        2. Click **"Add Zone"** to add the zone (you'll see it appear below)
        3. Repeat for additional zones if needed
        4. Click **"Save Zones"** when you're done adding all zones
        """)
        
        st.image(display_image, caption=f"Image Size: {width}x{height}", use_container_width=True)
        st.caption(f"💡 Enter coordinates between 0 and {width} for X, and 0 and {height} for Y")
        
        # Initialize polygons in session state
        if "drawzones_polygons" not in st.session_state:
            st.session_state.drawzones_polygons = [[]]
        
        polygons = st.session_state.drawzones_polygons
        current_zone_idx = len(polygons) - 1
        
        # Calculate example coordinates based on image size
        example_x1 = max(50, width // 10)
        example_y1 = max(50, height // 10)
        example_x2 = min(width - 50, width * 9 // 10)
        example_y2 = min(height - 50, height * 9 // 10)
        example_coords = f"{example_x1},{example_y1} {example_x2},{example_y1} {example_x2},{example_y2} {example_x1},{example_y2}"
        
        # Zone input interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            zone_coords = st.text_input(
                f"Zone {current_zone_idx + 1} Coordinates",
                value="" if current_zone_idx < len(polygons) - 1 or len(polygons[current_zone_idx]) > 0 else example_coords,
                placeholder=f"Example: {example_coords}",
                help="Enter coordinates as 'x1,y1 x2,y2 x3,y3 ...' separated by spaces. Minimum 3 points required."
            )
        
        with col2:
            add_zone_clicked = st.button("➕ Add Zone", key="add_zone", type="primary")
            if add_zone_clicked:
                if zone_coords and zone_coords.strip():
                    try:
                        # Parse coordinates
                        points = []
                        invalid_points = []
                        for coord_pair in zone_coords.strip().split():
                            try:
                                x, y = map(int, coord_pair.split(','))
                                # Validate coordinates
                                if 0 <= x <= width and 0 <= y <= height:
                                    points.append((x, y))
                                else:
                                    invalid_points.append((x, y))
                            except ValueError:
                                st.error(f"❌ Invalid format: '{coord_pair}'. Use format: x,y")
                                st.stop()
                        
                        if invalid_points:
                            st.warning(f"⚠️ Some points are out of bounds: {invalid_points}. Image size: {width}x{height}")
                        
                        if len(points) >= 3:
                            polygons[current_zone_idx] = points
                            polygons.append([])  # Start new zone
                            st.session_state.drawzones_polygons = polygons
                            st.success(f"✅ Zone {current_zone_idx + 1} added successfully with {len(points)} points!")
                            st.balloons()  # Celebration!
                            st.rerun()
                        elif len(points) > 0:
                            st.error(f"❌ A polygon needs at least 3 points! You entered {len(points)} point(s).")
                            st.info("💡 Add more points to complete the polygon.")
                        else:
                            st.error("❌ No valid points found! Please check your coordinate format.")
                    except Exception as e:
                        st.error(f"❌ Error parsing coordinates: {str(e)}")
                        st.info("💡 Format: x1,y1 x2,y2 x3,y3 ... (e.g., '100,100 200,100 200,200 100,200')")
                else:
                    st.warning("⚠️ Please enter coordinates first! Use the example format shown.")
        
        # Display current zones
        valid_zones = [p for p in polygons if len(p) >= 3]
        if len(valid_zones) > 0:
            st.subheader(f"📋 Current Zones ({len(valid_zones)} zone(s) configured)")
            annotated_image = display_image.copy()
            
            for idx, polygon in enumerate(valid_zones):
                # Draw polygon on image
                pts = np.array(polygon, dtype=np.int32)
                color = COLORS.by_idx(idx % len(COLORS.colors)).as_rgb()
                color_bgr = tuple(reversed(color))  # RGB to BGR for OpenCV
                
                # Draw filled polygon with transparency
                overlay = annotated_image.copy()
                cv2.fillPoly(overlay, [pts], color_bgr)
                cv2.addWeighted(overlay, 0.3, annotated_image, 0.7, 0, annotated_image)
                
                # Draw polygon outline
                cv2.polylines(annotated_image, [pts], True, color_bgr, THICKNESS)
                
                # Draw points
                for pt in polygon:
                    cv2.circle(annotated_image, tuple(pt), 5, color_bgr, -1)
                
                # Show zone info
                with st.expander(f"Zone {idx + 1} Details ({len(polygon)} points)"):
                    st.code(f"Coordinates: {polygon}")
            
            st.image(annotated_image, caption="Zones Preview", use_container_width=True)
        else:
            st.info("ℹ️ No zones added yet. Enter coordinates above and click 'Add Zone' to create your first zone.")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Add Another Zone"):
                polygons.append([])
                st.session_state.drawzones_polygons = polygons
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Last Zone"):
                if len(polygons) > 1:
                    polygons.pop()
                    st.session_state.drawzones_polygons = polygons
                    st.rerun()
                elif len(polygons) == 1:
                    polygons[0] = []
                    st.session_state.drawzones_polygons = polygons
                    st.rerun()
        
        with col3:
            # Check valid zones count
            num_valid_zones = len([p for p in polygons if len(p) >= 3])
            save_clicked = st.button("💾 Save Zones", type="primary", disabled=num_valid_zones == 0)
            if save_clicked:
                # Filter out empty polygons
                valid_polygons = [p for p in polygons if len(p) >= 3]
                if len(valid_polygons) > 0:
                    save_polygons_to_json(valid_polygons, zone_configuration_path)
                    st.success(f"✅ Zones saved successfully to {zone_configuration_path}!")
                    st.info(f"📁 Saved {len(valid_polygons)} zone(s). You can now proceed with detection.")
                    # Clear session state
                    st.session_state.drawzones_polygons = [[]]
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ No valid zones to save! Each zone needs at least 3 points.")
                    st.info("💡 **Steps to add a zone:**")
                    st.markdown("""
                    1. Enter coordinates in the text field (e.g., `100,100 200,100 200,200 100,200`)
                    2. Click **"➕ Add Zone"** button
                    3. You should see the zone appear in the preview
                    4. Repeat for additional zones if needed
                    5. Then click **"💾 Save Zones"**
                    """)
        
        # Quick coordinate helper
        with st.expander("🔧 Coordinate Helper"):
            st.markdown("""
            **Quick Reference:**
            - Image dimensions: **{}x{}**
            - Format: `x,y` pairs separated by spaces
            - Example rectangle: `100,100 500,100 500,400 100,400`
            - Example triangle: `200,100 400,300 100,300`
            
            **Tips:**
            - Start from top-left and go clockwise
            - Minimum 3 points per zone
            - You can add multiple zones
            """.format(width, height))
    else:
        # Original OpenCV-based drawing (for non-Streamlit environments)
        def mouse_event(event: int, x: int, y: int, flags: int, param: Any) -> None:
            global current_mouse_position
            if event == cv2.EVENT_MOUSEMOVE:
                current_mouse_position = (x, y)
            elif event == cv2.EVENT_LBUTTONDOWN:
                POLYGONS[-1].append((x, y))
        
        def redraw(image: np.ndarray, original_image: np.ndarray) -> None:
            global POLYGONS, current_mouse_position
            image[:] = original_image.copy()
            for idx, polygon in enumerate(POLYGONS):
                color = (
                    COLORS.by_idx(idx).as_bgr()
                    if idx < len(POLYGONS) - 1
                    else sv.Color.WHITE.as_bgr()
                )

                if len(polygon) > 1:
                    for i in range(1, len(polygon)):
                        cv2.line(
                            img=image,
                            pt1=polygon[i - 1],
                            pt2=polygon[i],
                            color=color,
                            thickness=THICKNESS,
                        )
                    if idx < len(POLYGONS) - 1:
                        cv2.line(
                            img=image,
                            pt1=polygon[-1],
                            pt2=polygon[0],
                            color=color,
                            thickness=THICKNESS,
                        )
                if idx == len(POLYGONS) - 1 and current_mouse_position is not None and polygon:
                    cv2.line(
                        img=image,
                        pt1=polygon[-1],
                        pt2=current_mouse_position,
                        color=color,
                        thickness=THICKNESS,
                    )
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.imshow(WINDOW_NAME, image)

        def redraw_polygons(image: np.ndarray) -> None:
            for idx, polygon in enumerate(POLYGONS[:-1]):
                if len(polygon) > 1:
                    color = COLORS.by_idx(idx).as_bgr()
                    for i in range(len(polygon) - 1):
                        cv2.line(
                            img=image,
                            pt1=polygon[i],
                            pt2=polygon[i + 1],
                            color=color,
                            thickness=THICKNESS,
                        )
                    cv2.line(
                        img=image,
                        pt1=polygon[-1],
                        pt2=polygon[0],
                        color=color,
                        thickness=THICKNESS,
                    )

        def close_and_finalize_polygon(image: np.ndarray, original_image: np.ndarray) -> None:
            if len(POLYGONS[-1]) > 2:
                cv2.line(
                    img=image,
                    pt1=POLYGONS[-1][-1],
                    pt2=POLYGONS[-1][0],
                    color=COLORS.by_idx(0).as_bgr(),
                    thickness=THICKNESS,
                )
            POLYGONS.append([])
            image[:] = original_image.copy()
            redraw_polygons(image)
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.imshow(WINDOW_NAME, image)

        global current_mouse_position
        original_image = resolve_source(source_path=source_path)
        if original_image is None:
            print("Failed to load source image.")
            return

        image = original_image.copy()
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.imshow(WINDOW_NAME, image)
        cv2.setMouseCallback(WINDOW_NAME, mouse_event, image)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == KEY_ENTER or key == KEY_NEWLINE:
                close_and_finalize_polygon(image, original_image)
            elif key == KEY_ESCAPE:
                POLYGONS[-1] = []
                current_mouse_position = None
            elif key == KEY_SAVE:
                save_polygons_to_json(POLYGONS, zone_configuration_path)
                print(f"Polygons saved to {zone_configuration_path}")
                break
            redraw(image, original_image)
            if key == KEY_QUIT:
                break

        cv2.destroyAllWindows()

def load_model(model_path):
    model = YOLO(model_path)
    return model


def display_tracker_options(language: str):
    display_tracker = st.radio(COMPONENTS[language]["DISPLAY_TRACKER"], (COMPONENTS[language]["YES"], COMPONENTS[language]["NO"]))
    is_display_tracker = True if display_tracker == COMPONENTS[language]["YES"] else False
    if is_display_tracker:
        tracker_type = st.radio(COMPONENTS[language]["TRACKER"], ("bytetrack.yaml", "botsort.yaml"))
        return is_display_tracker, tracker_type
    return is_display_tracker, None


def _display_detected_frames(conf, model, st_frame, image, is_display_tracking=None, tracker=None):

    # Resize the image to a standard size
    image = cv2.resize(image, (720, int(720*(9/16))))

    # Display object tracking, if specified
    if is_display_tracking:
        res = model.track(image, conf=conf, persist=True, tracker=tracker)
    else:
        # Predict the objects in the image using the YOLOv8 model
        res = model.predict(image, conf=conf)

    # # Plot the detected objects on the video frame
    res_plotted = res[0].plot()
    st_frame.image(res_plotted,
                   caption='Detected Video',
                   channels="BGR",
                   width='stretch'
                   )
def load_key():
    return settings.ENCRYPTION_KEY

def make_headings(path_csv: str, csv_list):
    if(len(csv_list)>0):
        with open(path_csv,'w') as f:
            f.write(",".join(csv_list[len(csv_list)-1].keys()))
            f.write('\n')

def save_to_csv(path_csv: str, csv_list):
    if(len(csv_list)>0):
        
        with open(path_csv,'a') as f:
            for row in csv_list:
                f.write(",".join(str(x) for x in row.values()))
                f.write('\n')


def encrypt_it(path_csv):
    key = load_key()
    
    
    f = Fernet(key)
    encrpyted = ''
    try:
        with open(path_csv,'rb') as unencrypted:
            _file = unencrypted.read()
            encrpyted = f.encrypt(_file)
            
        with open(path_csv,"wb") as encrypted_file:
            encrypted_file.write(encrpyted)
    except Exception:
        pass

def decrypt_it(path_csv, key):
    f = Fernet(key)
    
    with open(path_csv,'rb') as encrypted_file:
        encrypted = encrypted_file.read()
    decrypted = f.decrypt(encrypted)
    
    with open(path_csv,'wb') as dec_file:
        dec_file.write(decrypted)
    
  


def drop(path_csv, csv_list):
    df = pandas.read_csv(path_csv)
    df.drop_duplicates(subset=csv_list)
    df.to_csv(path_csv, index= False)

def send_ping( email: str, file: str, company_name: str = "S.A.D.A.K"):
    #if(auth_token == st.secrets["CRYPTO_KEY"]):
        client = Courier(auth_token = st.secrets["COURIER_API_KEY"])
        resp = client.send_message(
        message={
            "to": {
            "email": email
            },
            "content": {
            "title": company_name + ": Encroachment Detected:",
            "body": "Hi! " + email + "," + "\n" + "\n" + f"Encroachment has been detected at: {file} "  + "\n" + "\n" + "{{info}}"
            },
            "data":{
            "info": "Please take care of the violation immediately."
            },
        
        }
        )
