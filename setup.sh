#!/bin/bash

# S.A.D.A.K Local Setup Script
# This script sets up the project with virtual environment and pip

echo "🚀 S.A.D.A.K - Local Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
echo "✅ Found: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "⚠️  Warning: Python 3.9+ is recommended. You have Python $PYTHON_MAJOR.$PYTHON_MINOR"
    echo "   Some packages may not install correctly."
fi
echo ""

# Navigate to project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
echo "📁 Working directory: $(pwd)"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet
echo "✅ Pip upgraded"
echo ""

# Install PyTorch CPU
echo "🔥 Installing PyTorch CPU (this may take 5-15 minutes)..."
pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
echo "✅ PyTorch installed"
echo ""

# Install requirements
echo "📦 Installing project dependencies (this may take 10-30 minutes)..."
echo "⚠️  Note: Some dependency conflicts may occur, but installation will continue..."
pip install --no-cache-dir -r requirements.txt || {
    echo "⚠️  Some packages had conflicts. Trying to continue..."
    pip install --no-cache-dir -r requirements.txt --no-deps || true
}
echo "✅ Dependencies installed"
echo ""

# Note: streamlit_login_auth_ui is already in structures/ folder, no need to install
echo "ℹ️  streamlit_login_auth_ui is already included locally (in structures/ folder)"
echo ""

# Check for secrets file
echo "🔍 Checking for Streamlit secrets..."
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  Warning: .streamlit/secrets.toml not found!"
    echo "Creating directory..."
    mkdir -p .streamlit
    echo "Creating template secrets file..."
    cat > .streamlit/secrets.toml << EOF
COURIER_API_KEY = "your_courier_api_key_here"
CRYPTO_KEY = "your_encryption_key_here"
EOF
    echo "⚠️  Please edit .streamlit/secrets.toml with your actual keys!"
else
    echo "✅ Secrets file found"
fi
echo ""

# Verify installation
echo "✅ Verifying installation..."
python3 -c "import streamlit; import torch; print('✅ Core packages installed!')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Installation verified!"
else
    echo "⚠️  Some packages may be missing. Check errors above."
fi
echo ""

echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Edit .streamlit/secrets.toml with your API keys"
echo "   2. Activate virtual environment: source venv/bin/activate"
echo "   3. Run application: streamlit run app.py"
echo "   4. Open browser: http://localhost:8501"
echo ""

