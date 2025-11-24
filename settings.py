from pathlib import Path
import sys
import supervision as sv
import os
import streamlit as st

# Get the absolute path of the current file
FILE = Path(__file__).resolve()
# Get the parent directory of the current file
ROOT = FILE.parent
# Add the root path to the sys.path list if it is not already there
if ROOT not in sys.path:
    sys.path.append(str(ROOT))
# Get the relative path of the root directory with respect to the current working directory
#ROOT = ROOT.relative_to(Path.cwd())
# Sources
IMAGE = 'Image'
VIDEO = 'Video'
RTSP = 'RTSP'
YOUTUBE = 'YouTube'
ENCROACHMENT = 'Encroachment'
JUNCTION = 'Junction Evaluation Dataset'
JUNCTIONEVAL = 'Junction Evaluation'
BENCHMARKING = "Benchmarking"
SOURCES_LIST = [IMAGE, VIDEO, RTSP, YOUTUBE, ENCROACHMENT, JUNCTION, JUNCTIONEVAL,BENCHMARKING]
DATASET_DIR = ROOT / 'analysis'
DATASET_DIR_ACCURACY = DATASET_DIR/'accuracy'
DATASET_DIR_ENCROACHMENT = DATASET_DIR/'encroachments'
ENCROACHMENT_DICT = {}
DATASET_DIR_FLOW = DATASET_DIR_ACCURACY/'Flow Rate'
FLOW_DICT={}
DATASET_DIR_QUEUE = DATASET_DIR_ACCURACY/'Queue Length'
QUEUE_DICT={}
# Images config
IMAGES_DIR = ROOT / 'images'
DEFAULT_IMAGE = IMAGES_DIR / 'default.png'
DEFAULT_DETECT_IMAGE = IMAGES_DIR / 'default_detected.png'


VIDEOS_DICT = {}
EVALUATION_DICT = {}
FINAL_DICT = {}

COURIER_API_KEY = st.secrets["COURIER_API_KEY"]
ENCRYPTION_KEY = st.secrets["CRYPTO_KEY"]
CLASSES = {0: 'person',
 1: 'bicycle',
 2: 'car',
 3: 'motorcycle',
 4: 'airplane',
 5: 'bus',
 6: 'train',
 7: 'truck',
 8: 'boat',
 9: 'traffic light',
 10: 'fire hydrant',
 11: 'stop sign',
 12: 'parking meter',
 13: 'bench',
 14: 'bird',
 15: 'cat',
 16: 'dog',
 17: 'horse',
 18: 'sheep',
 19: 'cow',
 20: 'elephant',
 21: 'bear',
 22: 'zebra',
 23: 'giraffe',
 24: 'backpack',
 25: 'umbrella',
 26: 'handbag',
 27: 'tie',
 28: 'suitcase',
 29: 'frisbee',
 30: 'skis',
 31: 'snowboard',
 32: 'sports ball',
 33: 'kite',
 34: 'baseball bat',
 35: 'baseball glove',
 36: 'skateboard',
 37: 'surfboard',
 38: 'tennis racket',
 39: 'bottle',
 40: 'wine glass',
 41: 'cup',
 42: 'fork',
 43: 'knife',
 44: 'spoon',
 45: 'bowl',
 46: 'banana',
 47: 'apple',
 48: 'sandwich',
 49: 'orange',
 50: 'broccoli',
 51: 'carrot',
 52: 'hot dog',
 53: 'pizza',
 54: 'donut',
 55: 'cake',
 56: 'chair',
 57: 'couch',
 58: 'potted plant',
 59: 'bed',
 60: 'dining table',
 61: 'toilet',
 62: 'tv',
 63: 'laptop',
 64: 'mouse',
 65: 'remote',
 66: 'keyboard',
 67: 'cell phone',
 68: 'microwave',
 69: 'oven',
 70: 'toaster',
 71: 'sink',
 72: 'refrigerator',
 73: 'book',
 74: 'clock',
 75: 'vase',
 76: 'scissors',
 77: 'teddy bear',
 78: 'hair drier',
 79: 'toothbrush'}
 
# iterate over files in
# that directory

    # ML Model config
MODEL_DIR = ROOT /'weights'
#print(MODEL_DIR)
DETECTION_MODEL = MODEL_DIR/'yolov8n.pt'
print(DETECTION_MODEL)
# In case of your custome model comment out the line above and
# Place your custom model pt file name at the line below 
# DETECTION_MODEL = MODEL_DIR / 'my_detection_model.pt'

SEGMENTATION_MODEL = MODEL_DIR / 'yolov8n-seg.pt'
print(DETECTION_MODEL)

# Webcam
WEBCAM_PATH = 0

def updateDirectories():
        # Videos config
    global VIDEOS_DICT,EVALUATION_DICT,FINAL_DICT
    VIDEOS_DICT = {}
    EVALUATION_DICT = {}
    FINAL_DICT = {}
    VIDEO_DIR = ROOT / 'videos'

    # Scan videos directory for video files (including subdirectories)
    if os.path.exists(VIDEO_DIR):
        # Scan root directory
        for filename in os.listdir(VIDEO_DIR):
            f = os.path.join(VIDEO_DIR, filename)
            # checking if it is a file (not a directory)
            if os.path.isfile(f):
                try:
                    if filename.lower().endswith(('.mp4', '.avi', '.mov', '.MOV')):
                        VIDEOS_DICT[filename] = f
                except:
                    pass
        
        # Also scan subdirectories (one level deep) for videos
        for item in os.listdir(VIDEO_DIR):
            item_path = os.path.join(VIDEO_DIR, item)
            if os.path.isdir(item_path):
                # Skip junctionEvalDataset and junctionEvaluations (used for other features)
                if item not in ['junctionEvalDataset', 'junctionEvaluations']:
                    for filename in os.listdir(item_path):
                        f = os.path.join(item_path, filename)
                        if os.path.isfile(f):
                            try:
                                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.MOV')):
                                    # Use folder/video format for display
                                    display_name = f"{item}/{filename}"
                                    VIDEOS_DICT[display_name] = f
                            except:
                                pass

    # Scan junctionEvalDataset directory
    EVALUATION_DIR = VIDEO_DIR / 'junctionEvalDataset'
    if os.path.exists(EVALUATION_DIR):
        for filename in os.listdir(EVALUATION_DIR):
            f = os.path.join(EVALUATION_DIR, filename)
            if os.path.isdir(f):  # Only directories in junctionEvalDataset
                EVALUATION_DICT[filename] = f
    
    # Scan encroachment analysis directory
    if os.path.exists(DATASET_DIR_ENCROACHMENT):
        for filename in os.listdir(DATASET_DIR_ENCROACHMENT):
            f = os.path.join(DATASET_DIR_ENCROACHMENT, filename)
            if os.path.isfile(f):
                ENCROACHMENT_DICT[filename] = f

    # Scan flow rate analysis directory
    if os.path.exists(DATASET_DIR_FLOW):
        for filename in os.listdir(DATASET_DIR_FLOW):
            f = os.path.join(DATASET_DIR_FLOW, filename)
            if os.path.isfile(f):
                FLOW_DICT[filename] = f
    
    # Scan queue length analysis directory
    if os.path.exists(DATASET_DIR_QUEUE):
        for filename in os.listdir(DATASET_DIR_QUEUE):
            f = os.path.join(DATASET_DIR_QUEUE, filename)
            if os.path.isfile(f):
                QUEUE_DICT[filename] = f    



    # Build FINAL_DICT for junction evaluation
    for i in EVALUATION_DICT.keys():
        newDict = {}
        eval_path = EVALUATION_DICT[i]
        if os.path.exists(eval_path):
            for filename in os.listdir(eval_path):
                f = os.path.join(eval_path, filename)
                # checking if it is a file
                if os.path.isfile(f):
                    try:
                        if filename.lower().endswith('.mp4'):
                            newDict[filename] = f
                    except:
                        pass  
        FINAL_DICT[i] = newDict


    # EVALUATION_DICT = {
    #     'chickPea': EVALUATION_DIR /'chickPea.mp4',
    # }

    # print (EVALUATION_DICT['chickPea'])

    # ML Model config
    MODEL_DIR = ROOT /'weights'
    #print(MODEL_DIR)
    DETECTION_MODEL = MODEL_DIR/'yolov8n.pt'
    # In case of your custome model comment out the line above and
    # Place your custom model pt file name at the line below 
    # DETECTION_MODEL = MODEL_DIR / 'my_detection_model.pt'

    SEGMENTATION_MODEL = MODEL_DIR / 'yolov8n-seg.pt'




        
