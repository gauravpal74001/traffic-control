# Quick Start - Local Setup (pip + Virtual Environment)

## 🚀 Fast Setup (Automated)

### Option 1: Use Setup Script (Easiest)
```bash
cd /Users/gauravpal/Documents/S.A.D.A.K-main
./setup.sh
```

This will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Set up everything automatically

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install PyTorch (CPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 5. Install requirements
pip install -r requirements.txt

# 6. Install additional package
pip install streamlit_login_auth_ui

# 7. Create secrets file
mkdir -p .streamlit
# Edit .streamlit/secrets.toml with your keys (see below)

# 8. Run the app
streamlit run app.py
```

---

## 🔐 Setup Streamlit Secrets

Create `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
```

Then create/edit `.streamlit/secrets.toml`:
```toml
COURIER_API_KEY = "your_courier_api_key_here"
CRYPTO_KEY = "your_encryption_key_here"
```

**Note:** You may need to get these from the project maintainer or use placeholder values for testing.

---

## ▶️ Run the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run Streamlit
streamlit run app.py
```

Open browser: **http://localhost:8501**

---

## 🛑 Stop the Application

Press `Ctrl + C` in the terminal

---

## 📋 Daily Usage

```bash
# Every time you want to run the app:
cd /Users/gauravpal/Documents/S.A.D.A.K-main
source venv/bin/activate
streamlit run app.py
```

---

## ❓ Troubleshooting

**"Module not found"**
→ Make sure virtual environment is activated: `source venv/bin/activate`

**"Port 8501 in use"**
→ Use different port: `streamlit run app.py --server.port 8502`

**"Secrets not found"**
→ Create `.streamlit/secrets.toml` file (see above)

---

For detailed setup, see `SETUP_LOCAL.md`

