@echo off
REM Virtual Environment Setup Script for Deep Research Project (Windows)
REM This script creates a virtual environment and installs dependencies

echo 🔧 Setting up virtual environment for Deep Research project...

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

echo.
echo ✨ Setup complete!
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate
echo.
echo To run the Streamlit app, use:
echo   streamlit run app.py
echo.

pause
