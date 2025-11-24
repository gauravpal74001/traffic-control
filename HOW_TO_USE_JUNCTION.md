# 🚦 Junction Evaluation Features Guide

## 📋 Overview
The Junction Evaluation features help you analyze traffic at intersections by:
1. **Creating datasets** - Split videos into clips based on traffic light cycles
2. **Evaluating junctions** - Count and analyze vehicles by type at intersections

---

## 🎬 Feature 1: Junction Evaluation Dataset

### **Purpose**
Creates organized video clips from a source video based on traffic light cycle times. This helps prepare data for junction analysis.

### **How to Use**

#### **Step 1: Access the Feature**
1. Start the Streamlit app: `streamlit run app.py`
2. In the sidebar, select **"Junction Evaluation Dataset"** from "Select Source"

#### **Step 2: Select Source Video**
1. Choose a video from the dropdown menu
2. Videos are loaded from the `videos/` directory

#### **Step 3: Enter Cycle Times**
1. **Format:** Enter space-separated integers representing cycle durations in seconds
2. **Example:** `30 60 90` means:
   - First clip: 30 seconds
   - Second clip: 60 seconds  
   - Third clip: 90 seconds
   - Pattern repeats: 30s, 60s, 90s, 30s, 60s, 90s...

3. **Common Examples:**
   ```
   30 60        → Alternating 30s and 60s cycles
   45 45 45     → Three 45-second cycles
   20 40 60 80  → Four different cycle lengths
   ```

#### **Step 4: Create Dataset**
1. Click **"Create Dataset"** button
2. The system will:
   - Split the video into clips based on cycle times
   - Save clips to `videos/junctionEvalDataset/[VideoName]Clips/`
   - Name clips as `clip0.mp4`, `clip1.mp4`, `clip2.mp4`, etc.

#### **Step 5: Review Output**
- Clips are saved in: `videos/junctionEvalDataset/[VideoName]Clips/`
- Each clip corresponds to one cycle period
- Clips can be used for junction evaluation analysis

---

## 📊 Feature 2: Junction Evaluation

### **Purpose**
Analyzes video clips to count vehicles by type (car, truck, bus, etc.) at junctions. Helps understand traffic composition and flow.

### **How to Use**

#### **Step 1: Access the Feature**
1. In the sidebar, select **"Junction Evaluation"** from "Select Source"

#### **Step 2: Browse and Select Video**
1. **Video Gallery:**
   - Browse videos from the `videos/` directory
   - Navigate folders if needed
   - Click **"Analyze [VideoName]"** to select a video

#### **Step 3: Check for Detections**

**A. If Detections Exist:**
- System shows: "Detections found!"
- You can proceed directly to analysis
- Skip to Step 4

**B. If Detections Don't Exist:**
- System shows: "Detections not found!"
- Click **"Obtain and save detections"** button
- This will:
  - Process the entire video frame by frame
  - Detect and track all vehicles
  - Save detections to `detections/[VideoPath].dat`
  - Show progress bar with ETA
- **Note:** This can take several minutes depending on video length

#### **Step 4: Choose Analysis Type**

After detections are loaded, you'll see two options:

**A. Analyze Whole Junction:**
- Counts all vehicles by class across the entire video
- Provides overall statistics

**B. Roadwise Analysis (BETA):**
- More detailed analysis by road/lane
- Currently in beta/testing phase

#### **Step 5: Configure Frame Threshold** (Whole Junction Analysis)

1. **What is Frame Threshold?**
   - Filters out vehicles that appear for too few frames
   - Reduces noise from false detections
   - Default: 24 frames

2. **Adjust the Slider:**
   - Range: 10 to 50 frames
   - Lower value = more vehicles included (may include noise)
   - Higher value = fewer vehicles (more strict filtering)
   - Recommended: 24 frames (default)

3. **Understanding the Filter:**
   - Vehicles detected in **< frameThreshold frames** are excluded
   - Example: If threshold is 24, vehicles seen for only 10 frames won't be counted

#### **Step 6: Run Detection**
1. Click **"Detect"** button
2. System will:
   - Filter detections by frame threshold
   - Group vehicles by class
   - Calculate counts for each vehicle type

#### **Step 7: View Results**
1. **Results Table Shows:**
   - Vehicle counts by class (car, truck, bus, motorcycle, etc.)
   - Format: Class name → Count
   - Example:
     ```
     car: 45
     truck: 12
     bus: 8
     motorcycle: 23
     ```

2. **Understanding the Output:**
   - **Class names** come from the YOLO model
   - **Counts** represent unique vehicles (tracked by ID)
   - Only vehicles meeting the frame threshold are included

---

## 🔧 Technical Details

### **Detection Process**
1. **Model Used:** YOLOv8n (or configured model)
2. **Tracking:** ByteTrack algorithm
3. **Classes Detected:** 
   - Car (class 2)
   - Motorcycle (class 3)
   - Bus (class 5)
   - Truck (class 6)
   - And other vehicle types

### **File Locations**
- **Dataset Clips:** `videos/junctionEvalDataset/[VideoName]Clips/`
- **Detections:** `detections/[VideoPath].dat`
- **Source Code:** 
  - `helper.py` - Main UI functions
  - `scripts/jxnEvaluator.py` - Analysis logic
  - `scripts/jxnEvalDataCreation.py` - Dataset creation

### **Key Functions**
- `junctionEvaluationDataset()` - Creates video clips
- `junctionEvaluation()` - Main analysis function
- `get_detections()` - Generates detections from video
- `loadDetections()` - Loads saved detections
- `cleaningDataset()` - Filters by frame threshold
- `calculateWholeJunction()` - Counts vehicles by class

---

## 📝 Example Workflows

### **Workflow 1: Create Dataset for Analysis**

```
1. Select "Junction Evaluation Dataset"
2. Choose video: "traffic_junction.mp4"
3. Enter cycles: "30 60"
4. Click "Create Dataset"
5. Result: Clips saved to videos/junctionEvalDataset/traffic_junctionClips/
```

### **Workflow 2: Analyze Junction**

```
1. Select "Junction Evaluation"
2. Browse and select: "traffic_junction.mp4"
3. If needed: Click "Obtain and save detections" (wait for completion)
4. Click "Analyze whole junction"
5. Set frame threshold: 24 (default)
6. Click "Detect"
7. View results table with vehicle counts
```

### **Workflow 3: Complete Analysis Pipeline**

```
1. Create Dataset:
   - Use "Junction Evaluation Dataset"
   - Split video into clips with cycle times

2. Analyze Each Clip:
   - Use "Junction Evaluation"
   - Analyze each clip individually
   - Compare results across different cycles

3. Aggregate Results:
   - Combine counts from all clips
   - Analyze traffic patterns by cycle
```

---

## 💡 Tips & Best Practices

### **For Dataset Creation:**
- **Cycle Times:** Match actual traffic light cycle durations
- **Video Length:** Ensure video is long enough for multiple cycles
- **Naming:** Use descriptive video names for easy identification

### **For Junction Evaluation:**
- **Frame Threshold:**
  - Start with default (24 frames)
  - Increase if you see too many false positives
  - Decrease if you're missing valid vehicles
- **Video Quality:**
  - Use clear, well-lit videos
  - Ensure vehicles are visible
  - Avoid extreme camera angles
- **Processing Time:**
  - First-time detection generation can be slow
  - Detections are saved and reused
  - Be patient during initial processing

### **Performance:**
- **Detection Generation:** ~1-5 minutes per minute of video (depends on system)
- **Analysis:** Usually completes in seconds
- **Storage:** Detection files can be large (several MB per video)

---

## 🐛 Troubleshooting

### **Issue: "Detections not found" keeps appearing**
- **Solution:** Click "Obtain and save detections" and wait for completion
- **Check:** Ensure video file is readable and valid

### **Issue: No vehicles detected**
- **Solution:** 
  - Lower the frame threshold
  - Check video quality
  - Verify vehicles are visible in the video

### **Issue: Too many false detections**
- **Solution:**
  - Increase frame threshold
  - Improve video quality
  - Check model confidence settings

### **Issue: Dataset creation fails**
- **Solution:**
  - Verify cycle times are valid numbers
  - Ensure video file exists and is readable
  - Check that ffmpeg is installed

### **Issue: Analysis takes too long**
- **Solution:**
  - Use shorter video clips
  - Reuse saved detections (don't regenerate)
  - Consider using a more powerful system

---

## 📊 Understanding the Results

### **Vehicle Count Table**
```
Class        | Count
-------------|------
car          | 45
truck        | 12
bus          | 8
motorcycle   | 23
bicycle      | 5
```

### **What the Numbers Mean:**
- **Count:** Number of unique vehicles detected
- **Tracking:** Each vehicle gets a unique tracker ID
- **Filtering:** Only vehicles meeting frame threshold are counted
- **Classes:** Based on YOLO model classifications

### **Frame Threshold Impact:**
- **Low threshold (10):** More vehicles, may include noise
- **Medium threshold (24):** Balanced (recommended)
- **High threshold (50):** Fewer vehicles, very strict filtering

---

## 🔗 Related Features

- **Encroachment Detection:** Similar vehicle tracking, but focuses on time violations
- **Benchmarking:** Compares detected traffic with map service data
- **Analyze Feature:** Visualizes and analyzes collected data

---

## 📚 Additional Resources

- **Technical Details:** See `FUNCTION_DOCUMENTATION.md`
- **Quick Reference:** See `QUICK_FUNCTION_GUIDE.md`
- **Code Files:**
  - `helper.py` - UI functions
  - `scripts/jxnEvaluator.py` - Analysis algorithms
  - `scripts/jxnEvalDataCreation.py` - Video splitting

---

**Last Updated:** 2024
**Version:** 1.0

