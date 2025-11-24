# S.A.D.A.K - Complete Function Documentation

## 🎯 Application Overview

**S.A.D.A.K** (Smart Automated Detection and Analysis Kit) is a traffic analysis system that uses computer vision (YOLO models) to:
- Detect vehicles and objects in images/videos
- Analyze traffic flow and congestion
- Detect bottlenecks and encroachments
- Evaluate junction performance
- Benchmark traffic data accuracy

---

## 📁 File Structure & Functions

### 1. **app.py** - Main Application Entry Point

#### `st.set_page_config()`
- **Purpose**: Configures Streamlit page settings
- **Parameters**: 
  - `page_title`: "S.A.D.A.K"
  - `page_icon`: 🤖
  - `layout`: "wide"
  - `initial_sidebar_state`: "expanded"
- **What it does**: Sets up the web interface layout

#### Language Selection
- **Purpose**: Multi-language support (18 languages)
- **Languages**: English, Kannada, Hindi, Bengali, Gujarati, Malayalam, Marathi, Tamil, Telugu, Urdu, Punjabi, Sanskrit, Assamese, Bhojpuri, Dogri, Maithili, Mizo, Manipuri
- **Function**: Maps language names to language codes

#### Login System (`__login__obj.build_login_ui()`)
- **Purpose**: User authentication
- **Features**:
  - Login/Signup
  - Password reset
  - Session management
  - Cookie-based authentication

#### Main Application Flow (After Login)

**1. Model Configuration**
- **Model Type Selection**: Detection or Segmentation
- **Confidence Slider**: 25-100% (default: 40%)
- **Model Loading**: Loads YOLOv8 model from weights directory

**2. Source Selection** (8 options):
- **IMAGE**: Static image detection
- **VIDEO**: Stored video analysis
- **RTSP**: Real-time camera stream
- **YOUTUBE**: YouTube video analysis
- **ENCROACHMENT**: Bottleneck detection
- **JUNCTION**: Junction evaluation dataset creation
- **JUNCTIONEVAL**: Junction performance evaluation
- **BENCHMARKING**: Traffic data accuracy benchmarking
- **Analyze**: Data analysis and visualization

---

### 2. **helper.py** - Core Helper Functions

#### `startup()`
- **Purpose**: Initialize application directories
- **Calls**: `settings.updateDirectories()`
- **What it does**: Sets up video, detection, and analysis directories

#### `play_youtube_video(conf, model, language)`
- **Purpose**: Analyze YouTube videos in real-time
- **Parameters**:
  - `conf`: Confidence threshold
  - `model`: YOLO model instance
  - `language`: UI language
- **Process**:
  1. Downloads YouTube video stream
  2. Captures frames
  3. Runs object detection
  4. Displays results in real-time
- **Uses**: PyTube library for video download

#### `play_stored_video(conf, model, language)`
- **Purpose**: Analyze videos from local storage
- **Parameters**: Same as `play_youtube_video`
- **Process**:
  1. Selects video from `videos/` directory
  2. Plays video preview
  3. Runs detection on each frame
  4. Displays annotated results
- **Output**: Real-time detection overlay on video

#### `play_rtsp_stream(conf, model, language)`
- **Purpose**: Real-time analysis from IP cameras
- **Parameters**: Same as above
- **Process**:
  1. Connects to RTSP URL (e.g., `rtsp://admin:12345@192.168.1.210:554`)
  2. Captures live stream frames
  3. Performs real-time detection
  4. Displays live results
- **Use Case**: Traffic monitoring from security cameras

#### `enchroachment(confidence, language)`
- **Purpose**: Detect traffic bottlenecks and encroachments
- **Features**:
  - Video gallery browser
  - Zone configuration (draw zones on video)
  - Violation time detection
  - Live RTSP detection support
- **Process**:
  1. Browse video gallery
  2. Select video or enter RTSP URL
  3. Draw zones (if not configured)
  4. Set violation time threshold
  5. Detect vehicles staying in zones too long
  6. Generate alerts and CSV reports
- **Output**: `analysis/encroachments/data_*.csv`

#### `junctionEvaluationDataset(language)`
- **Purpose**: Create dataset for junction evaluation
- **Process**:
  1. Select source video
  2. Enter cycle times (space-separated integers)
  3. Split video into clips based on cycles
  4. Save clips to `videos/junctionEvalDataset/`
- **Output**: Organized video clips for analysis

#### `junctionEvaluation(language)`
- **Purpose**: Evaluate junction performance
- **Features**:
  - Video gallery browser
  - Detection loading/saving
  - Frame threshold filtering
  - Whole junction analysis
  - Road-wise analysis (BETA)
- **Process**:
  1. Browse and select video
  2. Load or generate detections
  3. Filter detections by frame threshold
  4. Analyze vehicle counts by class
  5. Display results table
- **Output**: Vehicle count statistics by class

#### `benchMarking(confidence, language)`
- **Purpose**: Compare actual traffic data with map service data
- **Features**:
  - Video gallery browser
  - Zone configuration (IN/OUT zones)
  - Traffic data CSV upload
  - Flow rate analysis
  - Queue length analysis
- **Process**:
  1. Select video
  2. Draw IN and OUT zones
  3. Upload traffic data CSV
  4. Set accuracy interval
  5. Choose metric (Flow Rate or Queue Length)
  6. Compare calculated vs. provided data
- **Output**: 
  - `analysis/accuracy/Flow Rate/data_*.csv`
  - `analysis/accuracy/Queue Length/data_*.csv`

#### `Analyze(language)`
- **Purpose**: Analyze and visualize collected data
- **Features**:
  - Authorization required
  - Data decryption
  - Multiple analysis criteria
  - Interactive visualizations
- **Analysis Types**:
  1. **Accuracy Analysis**:
     - Flow Rate analysis
     - Queue Length analysis
     - Time-series plots
  2. **Encroachment Analysis**:
     - Tracker ID vs Location
     - Tracker ID vs Class
     - Scatter plots
  3. **Encryption**:
     - Encrypt analysis files
- **Visualizations**: Plotly charts (scatter plots, time series)

#### `get_first_frame(video_path, size)`
- **Purpose**: Extract thumbnail from video
- **Parameters**:
  - `video_path`: Path to video file
  - `size`: Tuple (width, height) - default: (300, 169)
- **Returns**: PIL Image of first frame
- **Use**: Video gallery thumbnails

#### `loadDetections(video_path)`
- **Purpose**: Load saved detections from file
- **Parameters**: `video_path`: Path to video
- **Returns**: 
  - `detections_path`: Path to .dat file
  - `exists`: Boolean if file exists
  - `detections`: List of detection data
- **Process**:
  1. Creates detection directory if needed
  2. Checks for existing .dat file
  3. Loads pickled detections or returns empty list

---

### 3. **structures/essentials.py** - Core ML Functions

#### `load_model(model_path)`
- **Purpose**: Load YOLO model
- **Parameters**: `model_path`: Path to .pt weight file
- **Returns**: YOLO model instance
- **Models Supported**:
  - Detection: `yolov8n.pt`
  - Segmentation: `yolov8n-seg.pt`

#### `drawzones(source_path, zone_configuration_path)`
- **Purpose**: Interactive zone drawing tool
- **Parameters**:
  - `source_path`: Video/image path
  - `zone_configuration_path`: Output JSON path
- **Process**:
  1. Opens video/image
  2. Allows user to draw polygons
  3. Saves zone coordinates to JSON
- **Output**: JSON file with polygon coordinates

#### `_display_detected_frames(conf, model, st_frame, image, is_display_tracker, tracker)`
- **Purpose**: Display detection results on frames
- **Parameters**:
  - `conf`: Confidence threshold
  - `model`: YOLO model
  - `st_frame`: Streamlit frame container
  - `image`: Input image/frame
  - `is_display_tracker`: Show tracking IDs
  - `tracker`: Tracker instance
- **Process**:
  1. Runs model prediction
  2. Draws bounding boxes
  3. Adds labels and confidence
  4. Optionally tracks objects
  5. Updates Streamlit display

#### `display_tracker_options(language)`
- **Purpose**: Configure object tracking
- **Returns**: 
  - `is_display_tracker`: Boolean
  - `tracker`: Tracker instance (ByteTrack)
- **Options**: Enable/disable tracking

#### `get_first_frame(video_path, size)`
- **Purpose**: Extract first frame from video
- **Returns**: PIL Image or None

#### `encrypt_it(path_csv)`
- **Purpose**: Encrypt CSV files
- **Uses**: Fernet encryption (from settings.ENCRYPTION_KEY)
- **Output**: Encrypted file

#### `decrypt_it(file_path, key)`
- **Purpose**: Decrypt CSV files
- **Parameters**:
  - `file_path`: Encrypted file path
  - `key`: Decryption key
- **Returns**: Decrypted file path

---

### 4. **structures/VideoProcessor.py** - Video Processing

#### `VideoProcessor` Class
- **Purpose**: Process videos for flow rate analysis
- **Initialization Parameters**:
  - `source_weights_path`: Model weights
  - `source_video_path`: Video file
  - `zoneIN_configuration_path`: Entry zone JSON
  - `zoneOUT_configuration_path`: Exit zone JSON
  - `time`: Analysis time interval
  - `confidence_threshold`: Detection confidence
  - `dataFrame`: Traffic data for comparison
  - `analysis_path`: Output CSV path

#### `process_video()`
- **Purpose**: Main video processing method
- **Process**:
  1. Loads zones from JSON
  2. Processes video frame by frame
  3. Tracks vehicles entering/exiting zones
  4. Calculates flow rate
  5. Compares with provided data
  6. Saves results to CSV

---

### 5. **structures/encroachment.py** - Encroachment Detection

#### `timedetect(source_path, zone_configuration_path, violation_time, confidence, language, analysis_path)`
- **Purpose**: Detect vehicles violating time limits in zones
- **Parameters**:
  - `source_path`: Video path
  - `zone_configuration_path`: Zone JSON
  - `violation_time`: Maximum allowed time (seconds)
  - `confidence`: Detection confidence
  - `language`: UI language
  - `analysis_path`: Output CSV path
- **Process**:
  1. Loads video and zones
  2. Tracks vehicles in zones
  3. Calculates time spent in zone
  4. Flags violations
  5. Generates alerts
  6. Saves to CSV
- **Output**: CSV with violations (Tracker_ID, Class, Location, Time)

#### `livedetection(source_url, violation_time, zone_configuration_path, confidence, analysis_path)`
- **Purpose**: Real-time encroachment detection from RTSP
- **Parameters**: Similar to `timedetect`, but `source_url` is RTSP URL
- **Process**: Same as `timedetect` but for live streams

---

### 6. **structures/benchmarking_queue.py** - Queue Length Analysis

#### `BenchMarking(source_path, zones_IN_configuration_path, weight_path, dataFrame, time_analysis, confidence, language, analysis_path)`
- **Purpose**: Analyze queue length at junctions
- **Parameters**:
  - `source_path`: Video path
  - `zones_IN_configuration_path`: Entry zone JSON
  - `weight_path`: Model weights
  - `dataFrame`: Traffic data CSV
  - `time_analysis`: Time interval
  - `confidence`: Detection confidence
  - `language`: UI language
  - `analysis_path`: Output CSV path
- **Process**:
  1. Processes video frames
  2. Counts vehicles in queue zones
  3. Calculates queue length over time
  4. Compares with provided data
  5. Saves results

---

### 7. **scripts/jxnEvaluator.py** - Junction Evaluation

#### `cleaningDataset(detections, frameThreshold)`
- **Purpose**: Filter detections by frame threshold
- **Parameters**:
  - `detections`: List of detections
  - `frameThreshold`: Minimum frames to consider
- **Returns**: Filtered detection dictionary
- **Purpose**: Remove noise (vehicles seen for too few frames)

#### `calculateWholeJunction(finalDict)`
- **Purpose**: Calculate vehicle counts by class
- **Parameters**: `finalDict`: Filtered detections
- **Returns**: Dictionary of class counts
- **Output**: Count of each vehicle type (car, truck, bus, etc.)

---

### 8. **settings.py** - Configuration

#### `updateDirectories()`
- **Purpose**: Scan and update directory dictionaries
- **Updates**:
  - `VIDEOS_DICT`: Available videos
  - `EVALUATION_DICT`: Evaluation datasets
  - `FINAL_DICT`: Final evaluation videos
  - `ENCROACHMENT_DICT`: Encroachment analysis files
  - `FLOW_DICT`: Flow rate analysis files
  - `QUEUE_DICT`: Queue length analysis files

#### Constants:
- `DETECTION_MODEL`: Path to detection model
- `SEGMENTATION_MODEL`: Path to segmentation model
- `DEFAULT_IMAGE`: Default image path
- `DEFAULT_DETECT_IMAGE`: Default detection result image
- `ENCRYPTION_KEY`: Encryption key from secrets

---

## 🔄 Application Workflow

### 1. **Image Detection**
```
User uploads image → Model predicts → Draws boxes → Shows results
```

### 2. **Video Analysis**
```
Select video → Load model → Process frames → Display annotated video
```

### 3. **RTSP Stream**
```
Enter RTSP URL → Connect → Real-time detection → Live display
```

### 4. **Encroachment Detection**
```
Select video → Draw zones → Set violation time → Process → Generate alerts
```

### 5. **Junction Evaluation**
```
Select video → Create dataset → Analyze clips → Count vehicles → Display stats
```

### 6. **Benchmarking**
```
Select video → Draw IN/OUT zones → Upload traffic data → Compare → Generate report
```

### 7. **Analysis**
```
Authorize → Select analysis type → Choose file → Decrypt → Visualize
```

---

## 📊 Data Flow

### Input:
- Images (JPG, PNG, BMP, WEBP)
- Videos (MP4, AVI, MOV)
- RTSP streams
- CSV files (traffic data)

### Processing:
- YOLO object detection
- ByteTrack object tracking
- Zone-based filtering
- Time-based analysis
- Statistical calculations

### Output:
- Annotated images/videos
- CSV analysis files
- Interactive visualizations
- Encrypted data files

---

## 🔐 Security Features

1. **User Authentication**: Login system with password hashing
2. **Data Encryption**: Fernet encryption for sensitive data
3. **Authorization**: Token-based access for analysis module
4. **Session Management**: Streamlit session state

---

## 🌐 Multi-Language Support

All UI text is translated to 18 languages using `locales/settings_languages.py`:
- English, Hindi, Kannada, Bengali, Gujarati, Malayalam, Marathi, Tamil, Telugu, Urdu, Punjabi, Sanskrit, Assamese, Bhojpuri, Dogri, Maithili, Mizo, Manipuri

---

## 📁 Directory Structure

```
S.A.D.A.K-main/
├── videos/              # Input videos
├── weights/             # YOLO model weights
├── configure/           # Zone configuration JSONs
├── analysis/            # Output analysis files
│   ├── accuracy/        # Benchmarking results
│   └── encroachments/   # Encroachment reports
├── detections/          # Saved detection data
├── images/              # Default images
└── structures/          # Core modules
```

---

## 🎯 Key Technologies

- **YOLOv8**: Object detection
- **Supervision**: Detection utilities
- **ByteTrack**: Object tracking
- **Streamlit**: Web interface
- **OpenCV**: Video processing
- **Plotly**: Data visualization
- **PyTorch**: Deep learning framework

---

## 💡 Usage Tips

1. **First Time Setup**: 
   - Ensure model weights are in `weights/` directory
   - Create zone configurations before analysis

2. **Video Processing**:
   - Large videos may take time
   - Use appropriate confidence threshold (40% recommended)

3. **Zone Drawing**:
   - Draw zones carefully for accurate analysis
   - Zones should cover areas of interest

4. **Analysis**:
   - Authorize before accessing analysis module
   - Decrypt files before visualization

---

This documentation covers all major functions in the S.A.D.A.K application. Each function is designed to work together to provide comprehensive traffic analysis capabilities.

