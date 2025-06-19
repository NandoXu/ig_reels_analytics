#!/bin/bash

# This script automates the setup of Python 3.11 and required dependencies
# for your Instagram Post Analyzer on macOS.

echo "Starting macOS setup for Instagram Post Analyzer..."

# --- 1. Check and Install Homebrew (if not already installed) ---
echo "Checking for Homebrew installation..."
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for M1/M2/M3 Macs
    if [[ "$(uname -m)" == "arm64" ]]; then
        echo "Adding Homebrew to PATH for Apple Silicon..."
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo "Homebrew installation complete."
else
    echo "Homebrew is already installed. Updating Homebrew..."
    brew update
fi

# --- 2. Install Python 3.11 using Homebrew ---
echo "Installing Python 3.11..."
brew install python@3.11

# Ensure Python 3.11 is linked and callable as 'python3.11' and 'python3'
brew link --overwrite python@3.11

# Verify Python 3.11 installation
if ! command -v python3.11 &> /dev/null; then
    echo "Error: Python 3.11 could not be installed or found."
    echo "Please check the output above for any errors during Python installation."
    exit 1
fi
echo "Python 3.11 installed successfully."

# --- 3. Install Python Dependencies using pip ---
echo "Installing Python dependencies from requirements.txt..."

# Create a dummy requirements.txt file for demonstration purposes
# In a real scenario, this file would already exist alongside your script.
cat <<EOF > requirements.txt
APScheduler
beautifulsoup4
customtkinter
Instaloader
Pillow
requests
selenium
undetected-chromedriver
EOF

# Use pip associated with Python 3.11
/opt/homebrew/bin/python3.11 -m pip install --upgrade pip
/opt/homebrew/bin/python3.11 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "All Python dependencies installed successfully."
else
    echo "Error: Failed to install some Python dependencies."
    echo "Please check your internet connection and the requirements.txt file."
    exit 1
fi

echo "Setup complete. You can now run your Python script using 'python3.11 your_script_name.py'."
echo "Remember to download the correct ChromeDriver for your macOS architecture (Intel or Apple Silicon) and Chrome browser version manually."
echo "Place the 'chromedriver' executable into the 'chromedriver-mac' folder next to your script."

