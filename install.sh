#!/bin/bash

echo "==================================="
echo "BanditGUI Installation Script"
echo "==================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python 3.6 or higher from https://www.python.org/"
    exit 1
fi

# Make the script executable
chmod +x install.py

# Run the Python installation script
python3 install.py

# Check if the installation was successful
if [ $? -ne 0 ]; then
    echo "Installation failed."
    exit 1
fi

echo
echo "Installation completed successfully."
echo
