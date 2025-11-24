#!/bin/bash

# Fix Dependencies Script
# This script helps resolve dependency conflicts

echo "🔧 Fixing Dependencies..."
echo ""

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Run ./setup.sh first."
        exit 1
    fi
fi

echo "📦 Installing packages with conflict resolution..."
echo ""

# Install packages that commonly cause conflicts separately
echo "1. Installing core ML packages..."
pip install --no-cache-dir numpy pandas pillow opencv-python

echo "2. Installing Streamlit and related..."
pip install --no-cache-dir streamlit streamlit-cookies-manager streamlit-lottie streamlit-option-menu

echo "3. Installing YOLO/Ultralytics..."
pip install --no-cache-dir ultralytics supervision

echo "4. Installing remaining packages (ignoring conflicts)..."
pip install --no-cache-dir -r requirements.txt 2>&1 | grep -v "ERROR: ResolutionImpossible" || true

echo ""
echo "✅ Dependency installation attempt completed"
echo ""
echo "📋 Verifying critical packages..."
python3 -c "
import sys
errors = []
try:
    import streamlit
    print('✅ streamlit')
except ImportError as e:
    errors.append('streamlit')
    print(f'❌ streamlit: {e}')

try:
    import torch
    print('✅ torch')
except ImportError as e:
    errors.append('torch')
    print(f'❌ torch: {e}')

try:
    from ultralytics import YOLO
    print('✅ ultralytics')
except ImportError as e:
    errors.append('ultralytics')
    print(f'❌ ultralytics: {e}')

try:
    import supervision
    print('✅ supervision')
except ImportError as e:
    errors.append('supervision')
    print(f'❌ supervision: {e}')

if errors:
    print(f'\n⚠️  Missing packages: {errors}')
    sys.exit(1)
else:
    print('\n✅ All critical packages installed!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Dependencies fixed! You can now run: streamlit run app.py"
else
    echo ""
    echo "⚠️  Some packages are still missing. Try installing them manually."
fi

