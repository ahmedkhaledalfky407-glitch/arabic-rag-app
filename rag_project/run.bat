@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 Arabic RAG Assistant - Quick Start
echo ============================================================
echo.

cd /d "%~dp0"

if not exist venv311\Scripts\python.exe (
    echo 🔄 Creating virtual environment...
    python -m venv venv311
    echo ✅ Virtual environment created.
)

echo 🔄 Installing dependencies...
venv311\Scripts\python.exe -m pip install --upgrade pip
venv311\Scripts\python.exe -m pip install -r requirements.txt
echo ✅ Dependencies installed.

echo.
echo ============================================================
echo 🚀 Launching Streamlit App...
echo ============================================================
echo.

venv311\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8501

pause
