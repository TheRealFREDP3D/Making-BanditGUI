@echo off
echo ===================================
echo BanditGUI Installation Script
echo ===================================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.6 or higher from https://www.python.org/
    pause
    exit /b 1
)

:: Run the Python installation script
python install.py

:: Check if the installation was successful
if %errorlevel% neq 0 (
    echo Installation failed.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully.
echo.
pause
