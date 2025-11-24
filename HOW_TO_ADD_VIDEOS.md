# How to Add Videos to S.A.D.A.K

## 📁 Video Directory Location
```
/Users/gauravpal/Documents/S.A.D.A.K-main/videos/
```

## ✅ Supported Video Formats
- `.mp4` (recommended)
- `.avi`
- `.AVI`
- `.mov`
- `.MOV`

## 🎬 How to Add Videos

### Method 1: Using Finder (macOS)
1. Open Finder
2. Navigate to: `Documents/S.A.D.A.K-main/videos/`
3. Copy your video files into this folder
4. Refresh the Streamlit app (or it will auto-reload)

### Method 2: Using Terminal
```bash
# Copy a video file
cp /path/to/your/video.mp4 /Users/gauravpal/Documents/S.A.D.A.K-main/videos/

# Or move it
mv /path/to/your/video.mp4 /Users/gauravpal/Documents/S.A.D.A.K-main/videos/
```

### Method 3: Drag and Drop
1. Open the `videos/` folder in Finder
2. Drag video files from anywhere
3. Drop them into the folder

## 🔄 After Adding Videos

1. **Refresh the app**: The app should auto-detect new videos
2. **Or restart**: If videos don't appear, restart Streamlit:
   ```bash
   # Press Ctrl+C to stop, then:
   source venv/bin/activate
   streamlit run app.py
   ```

## 📋 Current Videos Directory Structure

Your `videos/` folder currently contains:
- `junctionEvalDataset/` - Subdirectory for junction evaluation
- `junctionEvaluations/` - Subdirectory for evaluations

**Note**: Videos should be placed directly in `videos/` (not in subdirectories) to appear in the Video Detection dropdown.

## 🎯 Quick Test

To test if it's working:
1. Add any `.mp4` video file to `videos/` folder
2. Go to the app sidebar
3. Select "Video" from source options
4. You should see your video in the dropdown

## 💡 Tips

- **Video Size**: Large videos (>1GB) may take longer to process
- **Naming**: Use descriptive names (e.g., `traffic_junction_1.mp4`)
- **Organization**: Keep original videos organized in subfolders if needed
- **Format**: MP4 is recommended for best compatibility

## 🚨 Troubleshooting

**Videos not appearing?**
1. Check file format (must be .mp4, .avi, .mov)
2. Ensure files are in `videos/` root (not subdirectories)
3. Refresh the app page
4. Check terminal for any errors

**Still not working?**
- Restart the Streamlit app
- Check file permissions
- Verify video files are not corrupted


