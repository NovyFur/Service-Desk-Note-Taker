@echo off
REM Launcher script for Service Desk Notes (Windows)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Activate the virtual environment
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

REM Launch the application
python "%SCRIPT_DIR%main.py"
