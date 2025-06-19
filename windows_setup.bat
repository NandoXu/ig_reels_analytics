@echo off
REM This script automates the setup of Python dependencies
REM for your Instagram Post Analyzer on Windows.

echo Starting Windows setup for Instagram Post Analyzer...

REM --- 1. Check for Python 3.11 Installation ---
echo Checking for Python 3.11 installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Python is not found in your PATH. Please ensure Python 3.11 is installed.
    echo.
    echo Recommended ways to install Python 3.11 on Windows:
    echo 1. Download from Python.org: ^<https://www.python.org/downloads/release/python-3110/^>
    echo    During installation, make sure to check "Add Python to PATH".
    echo 2. Using Chocolatey (if installed): choco install python --version=3.11
    echo.
    echo After installation, please restart your command prompt and run this script again.
    goto :eof
)

REM Verify Python version (attempts to find Python 3.11)
for /f "tokens=*" %%i in ('python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')" 2^>NUL') do set PYTHON_VERSION=%%i
if not "%PYTHON_VERSION%"=="Python 3.11" (
    echo.
    echo Warning: Detected %PYTHON_VERSION%. This script is optimized for Python 3.11.
    echo If you encounter issues, please install Python 3.11.
    echo.
) else (
    echo Detected %PYTHON_VERSION%. Proceeding with dependency installation.
)

REM --- 2. Install Python Dependencies using pip ---
echo Installing Python dependencies from requirements.txt...

REM Create a dummy requirements.txt file for demonstration purposes.
REM In a real scenario, this file would already exist alongside your script.
echo APScheduler> requirements.txt
echo beautifulsoup4>> requirements.txt
echo customtkinter>> requirements.txt
echo Instaloader>> requirements.txt
echo Pillow>> requirements.txt
echo requests>> requirements.txt
echo selenium>> requirements.txt
echo undetected-chromedriver>> requirements.txt

REM Upgrade pip
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Error upgrading pip. Please check your internet connection.
    goto :eof
)

REM Install dependencies
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install some Python dependencies.
    echo Please check your internet connection and the requirements.txt file.
    goto :eof
)

echo All Python dependencies installed successfully.

echo Setup complete. You can now run your Python script using "python your_script_name.py" or "python3 your_script_name.py" (depending on your PATH configuration).
echo.
echo IMPORTANT: Remember to download the correct ChromeDriver for your Windows architecture (32-bit or 64-bit) and Chrome browser version manually.
echo Place the "chromedriver.exe" executable into the "chromedriver-win64" folder next to your script.

pause
