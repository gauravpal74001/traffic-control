# 🚧 How to Use Encroachment Detection Feature

## 📋 Overview
The Encroachment Detection feature helps you identify traffic bottlenecks by detecting vehicles that stay in designated zones longer than a specified time threshold.

---

## 🚀 Step-by-Step Guide

### **Step 1: Access the Feature**

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Navigate to Encroachment:**
   - In the sidebar, find **"Select Source"**
   - Choose **"Encroachment"** from the dropdown

---

### **Step 2: Select Your Video**

1. **Browse the Video Gallery:**
   - You'll see a gallery of videos from the `videos/` directory
   - Videos are displayed in a 3-column grid
   - Each video shows a preview thumbnail

2. **Navigate Folders (if needed):**
   - Click on folder icons to navigate into subdirectories
   - Use the **"Back"** button to go to the parent directory

3. **Select a Video:**
   - Click **"Detect Bottlenecks for [VideoName]"** button
   - The video will be selected for analysis

---

### **Step 3: Configure Zones** (First Time Only)

If zones haven't been configured for this video, you'll need to draw them:

#### **A. Understanding Zone Drawing**

**What are zones?**
- Zones are polygon areas on the video where you want to monitor vehicles
- You can define multiple zones (e.g., different lanes, intersections, parking areas)
- Vehicles detected in these zones will be tracked for violation time

#### **B. Drawing Zones**

1. **You'll see the video frame displayed**
   - Note the image dimensions shown (e.g., `1920x1080`)

2. **Enter Coordinates:**
   - Format: `x1,y1 x2,y2 x3,y3 ...` (space-separated coordinate pairs)
   - Example rectangle: `100,100 500,100 500,400 100,400`
   - Minimum 3 points required per zone
   - Coordinates are in pixels (0,0 is top-left corner)

3. **Example Coordinates:**
   ```
   # Small zone (top-left area)
   50,50 200,50 200,200 50,200
   
   # Medium zone (center area)  
   300,200 800,200 800,600 300,600
   
   # Large zone (full width)
   10,10 1910,10 1910,1070 10,1070
   ```

4. **Add the Zone:**
   - Click **"➕ Add Zone"** button
   - The zone will appear in the preview below
   - You'll see it highlighted with a colored polygon

5. **Add More Zones (Optional):**
   - Click **"➕ Add Another Zone"** to add additional zones
   - Enter coordinates for the new zone
   - Click **"➕ Add Zone"** again

6. **Preview Your Zones:**
   - All zones are displayed on the image preview
   - Each zone has a different color
   - You can expand zone details to see coordinates

7. **Save Zones:**
   - Click **"💾 Save Zones"** when done
   - Zones are saved to `configure/ZONES[VideoName].json`
   - You'll see a success message

#### **C. Tips for Drawing Zones:**
- **Start from top-left, go clockwise** for consistent orientation
- **Use the coordinate helper** (expandable section) for reference
- **Test with a small zone first** to understand the coordinate system
- **Zones can overlap** if needed
- **Minimum 3 points** required (triangle is the simplest shape)

---

### **Step 4: Set Violation Time**

1. **Enter Violation Time:**
   - In the text input field, enter a number
   - **For minutes:** Enter value ≥ 1 (e.g., `2` = 2 minutes)
   - **For seconds:** Enter value < 1 (e.g., `0.5` = 30 seconds)

2. **Examples:**
   ```
   2     → 2 minutes threshold
   5     → 5 minutes threshold
   0.5   → 30 seconds threshold
   0.25  → 15 seconds threshold
   ```

3. **The system automatically detects:**
   - If value ≥ 1: Uses minutes mode
   - If value < 1: Uses seconds mode

---

### **Step 5: Optional - Live RTSP Stream**

If you want to analyze a live camera feed instead of a video file:

1. **Enter RTSP URL:**
   - Format: `rtsp://username:password@ip_address:port/path`
   - Example: `rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101`

2. **Leave empty** if you want to use the video file instead

---

### **Step 6: Start Detection**

1. **Click the Detection Button:**
   - Button text varies by language (e.g., "Detect Bottlenecks" or similar)
   - Located below the violation time input

2. **What Happens:**
   - Model loads (you'll see which model is being used)
   - Video starts processing frame by frame
   - Real-time detection overlay appears
   - Vehicles are tracked with unique IDs
   - Time counters show how long each vehicle has been in a zone

3. **During Processing:**
   - **Video Display:** Shows annotated frames with:
     - Colored zone polygons
     - Vehicle bounding boxes
     - Tracker IDs and time labels (format: `#ID MM:SS`)
   - **Alerts Section:** Shows warnings when violations are detected
   - **Terminate Button:** Click to stop processing anytime

---

### **Step 7: Monitor Alerts**

**When a violation is detected:**

1. **Alert Format:**
   ```
   ⚠️ Tracker_ID: 123 Class: car Location: 0
   ```
   - **Tracker_ID:** Unique vehicle identifier
   - **Class:** Vehicle type (car, bus, truck, etc.)
   - **Location:** Zone number where violation occurred

2. **Email Notifications:**
   - Alerts are automatically sent via email
   - Email address is configured in the code

3. **CSV Reports:**
   - Violations are automatically saved to CSV
   - Location: `analysis/encroachments/data_encroachment[VideoName].csv`
   - Format:
     ```csv
     Tracker_ID,Class,Location
     123,car,0
     456,bus,1
     ```

---

### **Step 8: Review Results**

1. **Check CSV File:**
   - Navigate to `analysis/encroachments/`
   - Open `data_encroachment[VideoName].csv`
   - View all violations with details

2. **Analyze Data:**
   - Use the **"Analyze"** feature in the main app
   - Select "Encroachment" from analysis criteria
   - View visualizations and statistics

---

## 🎯 Quick Start Example

**Scenario:** Detect vehicles parked longer than 2 minutes in a no-parking zone

1. **Select Video:** Choose your traffic video
2. **Draw Zone:** Draw polygon around the no-parking area
   - Example: `100,200 400,200 400,500 100,500`
3. **Set Time:** Enter `2` (for 2 minutes)
4. **Start Detection:** Click detection button
5. **Monitor:** Watch for alerts when vehicles exceed 2 minutes
6. **Review:** Check CSV file for all violations

---

## 🔧 Troubleshooting

### **Issue: "No valid zones to save"**
- **Solution:** Make sure you've entered at least 3 coordinate points and clicked "Add Zone"

### **Issue: "Zones must be configured"**
- **Solution:** Draw zones first before starting detection

### **Issue: "Model not found"**
- **Solution:** Ensure `weights/best_ps3.pt`, `weights/best.pt`, or `weights/yolov8n.pt` exists

### **Issue: Video not processing**
- **Solution:** 
  - Check video file format (supports .mp4, .avi, .mov)
  - Verify video file exists and is readable
  - Check console for error messages

### **Issue: Coordinates not working**
- **Solution:**
  - Check image dimensions shown
  - Ensure coordinates are within image bounds
  - Use format: `x,y` pairs separated by spaces

---

## 📊 Understanding the Output

### **Visual Display:**
- **Colored Polygons:** Each zone has a different color
- **Bounding Boxes:** Vehicles detected in zones
- **Labels:** Show `#TrackerID MM:SS` (time in zone)
- **Alerts:** Real-time warnings for violations

### **CSV Report Columns:**
- **Tracker_ID:** Unique identifier for each vehicle
- **Class:** Vehicle type (car, bus, truck, etc.)
- **Location:** Zone number (0, 1, 2, etc.)

### **Time Tracking:**
- **Format:** `MM:SS` (minutes:seconds)
- **Updates:** Real-time as vehicle stays in zone
- **Violation:** Triggered when time exceeds threshold

---

## 💡 Best Practices

1. **Zone Placement:**
   - Draw zones around areas where you want to monitor
   - Avoid drawing zones on moving objects
   - Use clear boundaries (road edges, lane markers)

2. **Time Threshold:**
   - Start with a longer time (e.g., 5 minutes) to test
   - Adjust based on your needs
   - Consider traffic flow patterns

3. **Video Quality:**
   - Use clear, well-lit videos
   - Ensure vehicles are visible
   - Avoid extreme angles or obstructions

4. **Multiple Zones:**
   - Use different zones for different areas
   - Each zone is monitored independently
   - Zones can overlap if needed

---

## 🎬 Example Workflow

```
1. Open App → Select "Encroachment"
2. Browse Videos → Select "traffic_video.mp4"
3. Draw Zone → Enter: "100,100 500,100 500,400 100,400"
4. Click "Add Zone" → Zone appears in preview
5. Click "Save Zones" → Zones saved
6. Enter Time → "2" (for 2 minutes)
7. Click "Detect Bottlenecks" → Processing starts
8. Watch Alerts → Violations appear in real-time
9. Check CSV → Review results in analysis folder
```

---

## 📝 Notes

- **First Time:** You must draw zones for each new video
- **Reuse Zones:** Once saved, zones are reused for the same video
- **Multiple Videos:** Each video needs its own zone configuration
- **Model Selection:** System automatically uses best available model
- **Performance:** Processing speed depends on video resolution and system specs

---

## 🔗 Related Files

- **Zone Configs:** `configure/ZONES[VideoName].json`
- **Analysis Results:** `analysis/encroachments/data_encroachment[VideoName].csv`
- **Models:** `weights/best_ps3.pt`, `weights/best.pt`, `weights/yolov8n.pt`

---

**Need Help?** Check the `ENCROACHMENT_FEATURES.md` file for detailed technical information.

