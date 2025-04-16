#!/bin/bash
# Installation script for Service Desk Notes

echo "Installing Service Desk Notes..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$SCRIPT_DIR/venv"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install required packages
echo "Installing required packages..."
pip install PyQt5 keyboard pyperclip python-dateutil

# Optional packages for voice-to-text
echo "Would you like to install optional voice-to-text packages? (y/n)"
read -r install_voice

if [[ "$install_voice" == "y" || "$install_voice" == "Y" ]]; then
    echo "Installing voice-to-text packages..."
    pip install SpeechRecognition
    
    # Check if we're on Linux
    if [[ "$(uname)" == "Linux" ]]; then
        echo "You may need to install system packages for audio support."
        echo "Run the following command if you encounter audio issues:"
        echo "sudo apt-get install python3-pyaudio portaudio19-dev"
    else
        pip install pyaudio
    fi
fi

# Ensure directories exist
mkdir -p "$SCRIPT_DIR/data"
mkdir -p "$SCRIPT_DIR/templates"

# Make launcher executable
chmod +x "$SCRIPT_DIR/launch.sh"

echo "Installation complete!"
echo "To start the application, run: ./launch.sh"
