@echo off
REM Installation script for Service Desk Notes (Windows)

echo Installing Service Desk Notes...

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Create virtual environment
echo Creating virtual environment...
python -m venv "%SCRIPT_DIR%venv"

REM Activate virtual environment
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

REM Install required packages
echo Installing required packages...
pip install PyQt5 keyboard pyperclip python-dateutil

REM Optional packages for voice-to-text
echo Would you like to install optional voice-to-text packages? (y/n)
set /p install_voice=

if /i "%install_voice%"=="y" (
    echo Installing voice-to-text packages...
    pip install SpeechRecognition pyaudio
)

REM Ensure directories exist
if not exist "%SCRIPT_DIR%data" mkdir "%SCRIPT_DIR%data"
if not exist "%SCRIPT_DIR%templates" mkdir "%SCRIPT_DIR%templates"

echo Installation complete!
echo To start the application, run: launch.bat

pause
