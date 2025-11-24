# 🚀 S.A.D.A.K - Quick Function Guide

## ✅ Application Status
**Your app is running at: http://localhost:8501**

---

## 📋 Main Functions Overview

### 🎯 **1. IMAGE Detection**
**Location**: `app.py` lines 67-110

**What it does**:
- Upload an image (JPG, PNG, BMP, WEBP)
- Detects objects using YOLO model
- Shows bounding boxes with labels
- Displays detection results

**Key Functions**:
- `model.predict()` - Runs YOLO detection
- `res[0].plot()` - Draws bounding boxes

---

### 🎬 **2. VIDEO Analysis**
**Location**: `helper.py` - `play_stored_video()`

**What it does**:
- Select video from gallery
- Process each frame
- Detect and track objects
- Display annotated video in real-time

**Key Functions**:
- `cv2.VideoCapture()` - Opens video
- `_display_detected_frames()` - Shows results
- `display_tracker_options()` - Configures tracking

**Output**: Annotated video with bounding boxes

---

### 📹 **3. RTSP Stream (Live Camera)**
**Location**: `helper.py` - `play_rtsp_stream()`

**What it does**:
- Connect to IP camera via RTSP
- Real-time object detection
- Live video feed with detections

**Example URL**: `rtsp://admin:12345@192.168.1.210:554/Streaming/Channels/101`

**Key Functions**:
- `cv2.VideoCapture(source_rtsp)` - Connects to stream
- Real-time frame processing

**Use Case**: Traffic monitoring from security cameras

---

### 🎥 **4. YOUTUBE Video Analysis**
**Location**: `helper.py` - `play_youtube_video()`

**What it does**:
- Enter YouTube URL
- Downloads video stream
- Analyzes in real-time
- Shows detection results

**Key Functions**:
- `YouTube(source_youtube)` - Downloads video
- `stream.url` - Gets video stream
- Processes like stored video

---

### 🚧 **5. ENCROACHMENT Detection (Bottlenecks)**
**Location**: `helper.py` - `enchroachment()` & `structures/encroachment.py`

**What it does**:
- Browse video gallery
- Draw zones on video (if needed)
- Set violation time threshold
- Detect vehicles staying too long
- Generate alerts and reports

**Key Functions**:
- `drawzones()` - Interactive zone drawing
- `timedetect()` - Detects violations
- `livedetection()` - Real-time RTSP detection

**Process Flow**:
```
1. Select video → 2. Draw zones → 3. Set time → 4. Process → 5. Generate CSV
```

**Output**: `analysis/encroachments/data_*.csv`

**CSV Columns**:
- Tracker_ID
- Class (vehicle type)
- Location (zone)
- Time (violation duration)

---

### 🚦 **6. JUNCTION Evaluation Dataset**
**Location**: `helper.py` - `junctionEvaluationDataset()`

**What it does**:
- Select source video
- Enter cycle times (e.g., "30 60 90")
- Split video into clips based on cycles
- Save clips for analysis

**Key Functions**:
- `JunctionEvaluation.datasetCreation()` - Creates clips
- `mainFunc()` - Splits video

**Output**: `videos/junctionEvalDataset/[VideoName]Clips/`

**Example**: If cycle = [30, 60, 90], creates clips at 30s, 60s, 90s

---

### 📊 **7. JUNCTION Evaluation**
**Location**: `helper.py` - `junctionEvaluation()`

**What it does**:
- Browse video gallery
- Load or generate detections
- Filter by frame threshold
- Count vehicles by class
- Display statistics

**Key Functions**:
- `loadDetections()` - Loads saved detections
- `get_detections()` - Generates new detections
- `cleaningDataset()` - Filters detections
- `calculateWholeJunction()` - Counts vehicles

**Output**: Table showing vehicle counts by class (car, truck, bus, etc.)

**Frame Threshold**: Removes vehicles seen for < N frames (reduces noise)

---

### 📈 **8. BENCHMARKING**
**Location**: `helper.py` - `benchMarking()`

**What it does**:
- Compare actual traffic vs. map service data
- Draw IN and OUT zones
- Upload traffic data CSV
- Calculate flow rate or queue length
- Generate comparison reports

**Key Functions**:
- `drawzones()` - Draw entry/exit zones
- `VideoProcessor.process_video()` - Flow rate analysis
- `BenchMarking()` - Queue length analysis

**Metrics**:
1. **Flow Rate**: Vehicles per time interval
2. **Queue Length**: Number of vehicles in queue

**Output**: 
- `analysis/accuracy/Flow Rate/data_*.csv`
- `analysis/accuracy/Queue Length/data_*.csv`

---

### 📊 **9. ANALYZE (Data Analysis)**
**Location**: `helper.py` - `Analyze()`

**What it does**:
- Authorize with token
- View analysis results
- Decrypt encrypted files
- Visualize data with charts

**Analysis Types**:

**A. Accuracy Analysis**:
- Flow Rate: Time-series plot
- Queue Length: Time-series plot

**B. Encroachment Analysis**:
- Tracker ID vs Location (scatter)
- Tracker ID vs Class (scatter)

**C. Encryption**:
- Encrypt analysis files

**Key Functions**:
- `decrypt_it()` - Decrypts files
- `encrypt_it()` - Encrypts files
- `px.scatter()` - Creates plots

**Visualizations**: Plotly interactive charts

---

## 🔧 Core Utility Functions

### **Model Loading**
```python
load_model(model_path)
```
- Loads YOLO model from .pt file
- Returns model instance

### **Zone Drawing**
```python
drawzones(source_path, zone_configuration_path)
```
- Interactive tool to draw polygons on video/image
- Saves zones to JSON file

### **Frame Display**
```python
_display_detected_frames(conf, model, st_frame, image, tracker)
```
- Runs detection on frame
- Draws bounding boxes
- Updates Streamlit display

### **Video Thumbnail**
```python
get_first_frame(video_path, size)
```
- Extracts first frame from video
- Resizes to specified dimensions
- Returns PIL Image

### **Detection Management**
```python
loadDetections(video_path)
```
- Loads saved detections from .dat file
- Creates directory if needed
- Returns detections list

---

## 📁 Data Flow Diagram

```
INPUT
  ↓
[Video/Image/RTSP]
  ↓
[YOLO Detection]
  ↓
[Object Tracking (ByteTrack)]
  ↓
[Zone Filtering]
  ↓
[Time Analysis]
  ↓
[Statistical Calculation]
  ↓
OUTPUT
  ↓
[CSV Reports] + [Visualizations]
```

---

## 🎮 How to Use Each Feature

### **Image Detection**:
1. Select "Image" from sidebar
2. Upload image
3. Click "Detect Objects"
4. View results

### **Video Analysis**:
1. Select "Video"
2. Choose video from dropdown
3. Click "Detect Objects"
4. Watch annotated video

### **RTSP Stream**:
1. Select "RTSP"
2. Enter RTSP URL
3. Click "Detect Objects"
4. View live detection

### **Encroachment**:
1. Select "Encroachment"
2. Browse video gallery
3. Select video
4. Draw zones (if needed)
5. Enter violation time
6. Click "Detect Bottlenecks"
7. View CSV report

### **Benchmarking**:
1. Select "Benchmarking"
2. Browse and select video
3. Draw IN zones (button)
4. Draw OUT zones (button)
5. Upload traffic data CSV
6. Enter accuracy interval
7. Choose metric (Flow/Queue)
8. Click "Benchmark"
9. View comparison report

### **Analysis**:
1. Select "Analyze"
2. Enter auth token
3. Choose analysis type
4. Select file
5. Click "Begin Analysis"
6. View data and charts

---

## 🔑 Key Concepts

### **Confidence Threshold**
- Range: 25-100%
- Default: 40%
- Higher = fewer but more accurate detections
- Lower = more but less accurate detections

### **Zone Configuration**
- JSON files with polygon coordinates
- Stored in `configure/` directory
- Format: `ZONES[VideoName].json`

### **Object Tracking**
- Uses ByteTrack algorithm
- Assigns unique IDs to objects
- Tracks across frames

### **Frame Threshold**
- Minimum frames to consider detection
- Removes noise (fleeting detections)
- Range: 10-50 frames

---

## 📊 Output Files

### **Encroachment Reports**:
- Location: `analysis/encroachments/`
- Format: `data_encroachment[VideoName].csv`
- Columns: Tracker_ID, Class, Location, Time

### **Flow Rate Analysis**:
- Location: `analysis/accuracy/Flow Rate/`
- Format: `data_flow_rate[VideoName].csv`
- Columns: Time, Vehicle counts

### **Queue Length Analysis**:
- Location: `analysis/accuracy/Queue Length/`
- Format: `data_queuelength[VideoName].csv`
- Columns: Time, Queue length

### **Detections**:
- Location: `detections/`
- Format: `[VideoPath].dat`
- Binary format (pickle)

---

## 🎯 Use Cases

1. **Traffic Monitoring**: RTSP stream analysis
2. **Bottleneck Detection**: Encroachment module
3. **Traffic Flow Analysis**: Benchmarking module
4. **Junction Optimization**: Junction evaluation
5. **Data Validation**: Compare actual vs. reported data
6. **Historical Analysis**: Analyze saved data

---

## 💡 Tips & Best Practices

1. **Zone Drawing**: Draw zones carefully for accurate results
2. **Confidence**: Start with 40%, adjust based on results
3. **Video Size**: Large videos take time - be patient
4. **RTSP**: Ensure camera is accessible and credentials are correct
5. **Analysis**: Always authorize before accessing analysis module
6. **Encryption**: Use encryption for sensitive data

---

## 🚨 Common Issues & Solutions

**Issue**: "No module found"
- **Solution**: All packages are now installed ✅

**Issue**: "Model not loading"
- **Solution**: Check `weights/` directory has .pt files

**Issue**: "Zone configuration not found"
- **Solution**: Draw zones first using zone drawing tool

**Issue**: "RTSP connection failed"
- **Solution**: Check URL format and camera accessibility

---

This guide covers all major functions. The app is running and ready to use! 🎉

