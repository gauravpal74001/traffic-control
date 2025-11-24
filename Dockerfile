# Use Python 3.10 image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies first (for OpenCV and other image processing libraries)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libx11-dev \
    libxrender-dev \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install compatible pip version (pip 24.0 handles old metadata better than 25+)
# This fixes issues with old package metadata while still being modern
RUN pip3 install --upgrade "pip>=24.0,<24.1" setuptools wheel

# Copy requirements.txt first for better Docker layer caching
COPY requirements.txt .

# Install AWS packages first with minimum versions (to avoid metadata issues)
# These packages often have dependency conflicts, so install them early
RUN pip3 install --no-cache-dir --default-timeout=1000 \
    "boto3>=1.28.0" "botocore>=1.31.0" "awscli>=1.29.0" || \
    pip3 install --no-cache-dir --default-timeout=1000 boto3 botocore awscli

# Install PyTorch CPU-only version (much smaller than CUDA version ~600MB vs ~2GB)
# This prevents ultralytics from trying to install CUDA versions
RUN pip3 install --no-cache-dir --default-timeout=1000 \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu || \
    pip3 install --no-cache-dir --default-timeout=1000 torch torchvision

# Install remaining Python dependencies with increased timeout and retries
# Note: boto3, botocore, awscli, torch, torchvision already installed above
RUN pip3 install --no-cache-dir --default-timeout=1000 -r requirements.txt || \
    (echo "First attempt failed, retrying with 5 second delay..." && sleep 5 && \
     pip3 install --no-cache-dir --default-timeout=1000 -r requirements.txt) || \
    (echo "Second attempt failed, retrying with 10 second delay..." && sleep 10 && \
     pip3 install --no-cache-dir --default-timeout=1000 -r requirements.txt)

# Install streamlit_login_auth_ui if not already in requirements.txt
RUN pip3 install --no-cache-dir streamlit_login_auth_ui

# Copy application code
COPY . .

# Expose port 8080
EXPOSE 8080

# Command to run Streamlit app
CMD ["streamlit", "run", "app.py", \
     "--server.enableCORS", "false", \
     "--server.headless", "true", \
     "--browser.serverAddress", "0.0.0.0", \
     "--browser.serverPort", "8080", \
     "--browser.gatherUsageStats", "false", \
     "--server.port", "8080"]
