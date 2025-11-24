# 🚧 Encroachment Detection Features

## Overview
The Encroachment Detection feature (also called "Bottleneck Detection") identifies vehicles that stay in designated zones for longer than a specified time threshold, helping detect traffic bottlenecks and violations.

---

## 🎯 Key Features

### 1. **Video Gallery Browser**
- Browse videos from the `videos/` directory
- Navigate through folders and subfolders
- Select videos for analysis
- Preview first frame of each video

### 2. **Zone Configuration**
- **Interactive Zone Drawing**: Draw polygon zones on video frames
- **Multiple Zones**: Support for multiple detection zones
- **Zone Persistence**: Zones are saved as JSON files in `configure/` directory
- **Zone Format**: `configure/ZONES[VideoName].json`

### 3. **Violation Time Detection**
- **Configurable Threshold**: Set violation time in minutes or seconds
- **Time Tracking**: Tracks how long each vehicle stays in a zone
- **Real-time Display**: Shows time counter on each detected vehicle
- **Format**: `MM:SS` (minutes:seconds)

### 4. **Two Detection Modes**

#### **A. Video File Analysis** (`timedetect`)
- Processes pre-recorded video files
- Uses custom trained model: `weights/best_ps3.pt`
- Detects classes: [2, 5, 6, 7, 121] (cars, buses, trucks, etc.)
- Frame-by-frame analysis with tracking

#### **B. Live RTSP Stream Analysis** (`livedetection`)
- Real-time detection from IP cameras
- Uses Roboflow Inference Pipeline
- Model: `yolov8x-640`
- Detects classes: [2, 5, 6, 7]
- Live stream processing

### 5. **Vehicle Tracking**
- **ByteTrack Tracker**: Tracks vehicles across frames
- **Tracker IDs**: Each vehicle gets a unique tracker ID
- **Time Calculation**: FPS-based timer for video files, Clock-based for live streams
- **Persistent Tracking**: Maintains vehicle identity across frames

### 6. **Alert System**
- **Real-time Alerts**: Shows warnings when violations detected
- **Email Notifications**: Sends alerts via Courier API
- **Alert Format**: 
  ```
  Tracker_ID: [ID] Class: [Vehicle Type] Location: [Zone Number]
  ```
- **Visual Indicators**: Color-coded zones and vehicle annotations

### 7. **CSV Reports**
- **Automatic Generation**: Creates CSV files with violation data
- **Location**: `analysis/encroachments/data_encroachment[VideoName].csv`
- **Columns**:
  - `Tracker_ID`: Unique vehicle identifier
  - `Class`: Vehicle type (car, bus, truck, etc.)
  - `Location`: Zone number where violation occurred
- **Data Persistence**: Saves violations to CSV automatically

### 8. **Visual Annotations**
- **Zone Highlighting**: Colored polygons for each zone
- **Vehicle Bounding Boxes**: Color-coded by zone
- **Time Labels**: Shows `#TrackerID MM:SS` on each vehicle
- **FPS Display**: Shows processing speed (for live streams)

---

## 📋 How to Use

### **Step 1: Access Encroachment Feature**
1. Open the app
2. Select **"Encroachment"** from the source options

### **Step 2: Select Video**
1. Browse the video gallery
2. Navigate through folders if needed
3. Click **"Detect Bottlenecks for [VideoName]"**

### **Step 3: Configure Zones** (if not already configured)
1. If zones don't exist, the system will prompt you to draw zones
2. Use the interactive zone drawing tool:
   - Click to add polygon points
   - Press **Enter** to close a polygon
   - Press **S** to save zones
   - Press **ESC** to cancel current polygon
   - Press **Q** to quit

### **Step 4: Set Violation Time**
1. Enter violation time threshold
   - **Minutes**: Enter value ≥ 1 (e.g., "2" for 2 minutes)
   - **Seconds**: Enter value < 1 (e.g., "0.5" for 30 seconds)
2. The system automatically detects if it's minutes or seconds

### **Step 5: Optional - Live RTSP Stream**
- If you want to analyze a live camera feed:
  - Enter RTSP URL in the text field
  - Example: `rtsp://admin:password@192.168.1.100:554/stream`
  - Leave empty to use video file instead

### **Step 6: Start Detection**
1. Click the detection button
2. Watch real-time processing
3. View alerts as violations are detected
4. CSV report is generated automatically

---

## 🔧 Technical Details

### **Models Used**
- **Video Files**: `weights/best_ps3.pt` (custom trained model)
- **Live Streams**: `yolov8x-640` (via Roboflow)

### **Detection Classes**
- **Class 2**: Car
- **Class 5**: Bus
- **Class 6**: Truck
- **Class 7**: Other vehicles
- **Class 121**: Additional vehicle type (video files only)

### **Configuration Files**
- **Zone Config**: `configure/ZONES[VideoName].json`
- **Analysis Output**: `analysis/encroachments/data_encroachment[VideoName].csv`

### **Key Functions**
- `enchroachment()`: Main UI function in `helper.py`
- `timedetect()`: Video file analysis in `structures/encroachment.py`
- `livedetection()`: Live stream analysis in `structures/encroachment.py`
- `drawzones()`: Zone drawing tool in `structures/essentials.py`
- `CustomSink`: Live stream processing class in `structures/CustomSink.py`

---

## 📊 Output Format

### **CSV Report Structure**
```csv
Tracker_ID,Class,Location
123,car,0
456,bus,1
789,truck,0
```

### **Alert Format**
```
⚠️ Tracker_ID: 123 Class: car Location: 0
```

### **Email Notification**
- Sent to configured email address
- Includes violation details
- Triggered when violation threshold is exceeded

---

## ⚙️ Configuration

### **Email Settings**
- Email address is configured in `structures/encroachment.py`
- Uses Courier API for sending notifications
- API key stored in Streamlit secrets

### **Zone Drawing**
- Zones are saved as JSON polygon coordinates
- Multiple zones supported per video
- Zones are reusable across sessions

### **Time Threshold Logic**
- **Minutes Mode**: `violation_time >= 1`
  - Checks: `time_in_zone // 60 >= violation_time`
- **Seconds Mode**: `violation_time < 1`
  - Checks: `time_in_zone % 60 >= violation_time * 60`

---

## 🐛 Known Issues & Notes

1. **Terminate Button**: The terminate functionality may need improvement for better user experience
2. **Email Typo Fixed**: Corrected email address typo in the code
3. **Zone Configuration**: Zones must be drawn before first analysis
4. **Model Paths**: Ensure model weights are in `weights/` directory
5. **RTSP Stream**: Requires stable network connection and valid RTSP URL

---

## 🚀 Future Enhancements

- [ ] Better terminate button handling
- [ ] Configurable email addresses via UI
- [ ] Export reports in multiple formats (PDF, Excel)
- [ ] Historical violation tracking
- [ ] Dashboard with violation statistics
- [ ] Multi-zone violation aggregation
- [ ] Video export with annotations

---

## 📝 Example Workflow

1. **Upload Video**: Place video in `videos/` directory
2. **Select Video**: Choose video from gallery
3. **Draw Zones**: Define areas to monitor (first time only)
4. **Set Time**: Enter "2" for 2-minute threshold
5. **Start Detection**: Click detection button
6. **Monitor Alerts**: Watch for violation warnings
7. **Review Report**: Check CSV file in `analysis/encroachments/`

---

## 🔗 Related Files

- `helper.py`: Main UI function (`enchroachment()`)
- `structures/encroachment.py`: Core detection logic
- `structures/CustomSink.py`: Live stream processing
- `structures/essentials.py`: Zone drawing utility
- `utils/timers.py`: Time tracking utilities
- `settings.py`: Configuration and class definitions

---

**Last Updated**: 2024
**Version**: 1.0

