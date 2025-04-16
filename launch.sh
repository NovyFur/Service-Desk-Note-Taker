#!/bin/bash
# Launcher script for Service Desk Notes application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Launch the application
python "$SCRIPT_DIR/main.py"
