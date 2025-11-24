# Local Setup Guide - Running S.A.D.A.K with pip and Virtual Environment

## Prerequisites

- Python 3.10 or 3.11 (recommended: 3.10)
- pip (Python package installer)
- Git (if cloning from repository)

## Step-by-Step Setup

### Step 1: Check Python Version
```bash
python3 --version
# Should show Python 3.10.x or 3.11.x
```

If Python 3.10 is not installed:
- **macOS**: `brew install python@3.10`
- **Linux**: `sudo apt-get install python3.10 python3.10-venv`
- **Windows**: Download from python.org

### Step 2: Navigate to Project Directory
```bash
cd /Users/gauravpal/Documents/S.A.D.A.K-main
```

### Step 3: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Upgrade pip
```bash
pip install --upgrade pip setuptools wheel
```

### Step 5: Install System Dependencies (macOS/Linux)

**macOS:**
```bash
# Install via Homebrew (if not installed)
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libx11-dev \
    libxrender-dev \
    libsm6 \
    libxext6 \
    ffmpeg
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Add to PATH

### Step 6: Install PyTorch (CPU version - recommended for most users)

**For CPU only (smaller, faster install):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**For GPU (if you have CUDA):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Step 7: Install Project Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# If you encounter issues, try installing in batches:
# pip install --upgrade pip
# pip install -r requirements.txt --no-cache-dir
```

**Note:** This will take 10-30 minutes depending on your internet speed.

### Step 8: Install Additional Package
```bash
pip install streamlit_login_auth_ui
```

### Step 9: Set Up Streamlit Secrets (Required)

Create a `.streamlit/secrets.toml` file in the project root:

```bash
mkdir -p .streamlit
```

Create `.streamlit/secrets.toml` with:
```toml
COURIER_API_KEY = "your_courier_api_key_here"
CRYPTO_KEY = "your_encryption_key_here"
```

**Note:** You'll need to get these keys from the project maintainer or set up your own.

### Step 10: Verify Installation
```bash
# Check if key packages are installed
python3 -c "import streamlit; import torch; import ultralytics; print('All packages installed!')"
```

### Step 11: Run the Application
```bash
streamlit run app.py
```

The application will start and you'll see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open your browser and go to: **http://localhost:8501**

---

## Troubleshooting

### Issue: "Module not found" errors
**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: FFmpeg not found
**Solution:**
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`
- Windows: Download and add to PATH

### Issue: PyTorch installation fails
**Solution:**
```bash
# Try CPU version first (easier)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: OpenCV errors
**Solution:**
```bash
pip install opencv-python opencv-python-headless
```

### Issue: Streamlit secrets error
**Solution:**
Create `.streamlit/secrets.toml` file (see Step 9)

### Issue: Port 8501 already in use
**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

---

## Quick Start Script

Create a file `setup.sh` (macOS/Linux) or `setup.bat` (Windows):

**setup.sh (macOS/Linux):**
```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
pip install streamlit_login_auth_ui
echo "Setup complete! Run: source venv/bin/activate && streamlit run app.py"
```

**setup.bat (Windows):**
```batch
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
pip install streamlit_login_auth_ui
echo Setup complete! Run: venv\Scripts\activate && streamlit run app.py
```

---

## Daily Usage

### Start the application:
```bash
# 1. Navigate to project
cd /Users/gauravpal/Documents/S.A.D.A.K-main

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Run application
streamlit run app.py
```

### Stop the application:
- Press `Ctrl + C` in the terminal

### Deactivate virtual environment:
```bash
deactivate
```

---

## Project Structure

Make sure these directories exist:
- ✅ `weights/` - Model weights (yolov8n.pt, etc.)
- ✅ `configure/` - Zone configuration files
- ✅ `videos/` - Video files (can be empty)
- ✅ `images/` - Default images
- ✅ `assets/` - Assets folder
- ✅ `analysis/` - Output directory (created automatically)
- ✅ `detections/` - Detection data (created automatically)

---

## Notes

- **First run may be slow** - Models need to be loaded
- **Keep terminal open** - Application runs in the terminal
- **Virtual environment** - Always activate before running
- **Port 8501** - Default Streamlit port (change if needed)

---

## Need Help?

If you encounter issues:
1. Check Python version: `python3 --version`
2. Verify virtual environment is activated: `which python` (should show venv path)
3. Check installed packages: `pip list`
4. Review error messages carefully

