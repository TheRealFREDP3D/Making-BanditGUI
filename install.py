#!/usr/bin/env python3
"""
Installation script for BanditGUI.

This script automates the setup process for BanditGUI by:
1. Checking for required dependencies (Python, Node.js)
2. Creating a virtual environment
3. Installing Python dependencies
4. Installing Node.js dependencies
5. Setting up environment variables
6. Providing instructions for running the application
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}\n")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.YELLOW}! {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def run_command(command, cwd=None, shell=False):
    """Run a command and return the result."""
    try:
        if isinstance(command, str) and not shell:
            command = command.split()
        
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)

def check_python_version():
    """Check if Python version is 3.6 or higher."""
    print_header("Checking Python Version")
    
    python_version = platform.python_version()
    print_info(f"Detected Python version: {python_version}")
    
    major, minor, _ = map(int, python_version.split('.'))
    if major >= 3 and minor >= 6:
        print_success("Python version is compatible (3.6 or higher)")
        return True
    else:
        print_error("Python version must be 3.6 or higher")
        return False

def check_nodejs():
    """Check if Node.js is installed."""
    print_header("Checking Node.js Installation")
    
    success, output = run_command("node --version")
    if success:
        print_success(f"Node.js is installed: {output.strip()}")
        return True
    else:
        print_error("Node.js is not installed or not in PATH")
        print_info("Please install Node.js from https://nodejs.org/")
        return False

def check_npm():
    """Check if npm is installed."""
    print_header("Checking npm Installation")
    
    success, output = run_command("npm --version")
    if success:
        print_success(f"npm is installed: {output.strip()}")
        return True
    else:
        print_error("npm is not installed or not in PATH")
        print_info("npm should be installed with Node.js")
        return False

def create_virtual_environment():
    """Create a Python virtual environment."""
    print_header("Creating Virtual Environment")
    
    venv_dir = "venv"
    if os.path.exists(venv_dir):
        print_warning(f"Virtual environment directory '{venv_dir}' already exists")
        return True
    
    success, output = run_command(f"{sys.executable} -m venv {venv_dir}")
    if success:
        print_success(f"Created virtual environment in '{venv_dir}'")
        return True
    else:
        print_error(f"Failed to create virtual environment: {output}")
        return False

def install_python_dependencies():
    """Install Python dependencies."""
    print_header("Installing Python Dependencies")
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        # Create requirements.txt if it doesn't exist
        print_warning("requirements.txt not found, creating one with essential dependencies")
        with open("requirements.txt", "w") as f:
            f.write("flask\n")
            f.write("paramiko\n")
            f.write("python-dotenv\n")
            f.write("requests\n")
            f.write("beautifulsoup4\n")
    
    # Determine pip command based on OS
    if platform.system() == "Windows":
        pip_cmd = f"{os.path.join('venv', 'Scripts', 'pip')}"
    else:
        pip_cmd = f"{os.path.join('venv', 'bin', 'pip')}"
    
    success, output = run_command(f"{pip_cmd} install -r requirements.txt")
    if success:
        print_success("Installed Python dependencies")
        return True
    else:
        print_error(f"Failed to install Python dependencies: {output}")
        return False

def install_nodejs_dependencies():
    """Install Node.js dependencies."""
    print_header("Installing Node.js Dependencies")
    
    # Check if package.json exists
    if not os.path.exists("package.json"):
        print_warning("package.json not found, creating one with essential dependencies")
        
        package_json = {
            "name": "banditgui",
            "version": "0.5.0",
            "description": "A web-based interface for the OverTheWire Bandit wargame",
            "main": "index.js",
            "scripts": {
                "start": "python -m banditgui.app"
            },
            "dependencies": {
                "xterm": "^4.19.0",
                "xterm-addon-fit": "^0.5.0",
                "xterm-addon-web-links": "^0.4.0"
            }
        }
        
        import json
        with open("package.json", "w") as f:
            json.dump(package_json, f, indent=2)
    
    success, output = run_command("npm install")
    if success:
        print_success("Installed Node.js dependencies")
        return True
    else:
        print_error(f"Failed to install Node.js dependencies: {output}")
        return False

def setup_environment_variables():
    """Set up environment variables."""
    print_header("Setting Up Environment Variables")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print_warning(".env file already exists, skipping creation")
        return True
    
    # Create .env file with default values
    with open(".env", "w") as f:
        f.write("SSH_HOST=bandit.labs.overthewire.org\n")
        f.write("SSH_PORT=2220\n")
        f.write("SSH_USERNAME=bandit0\n")
        f.write("SSH_PASSWORD=bandit0\n")
        f.write("DEBUG=True\n")
        f.write("HOST=127.0.0.1\n")
        f.write("PORT=5000\n")
        f.write("LOG_LEVEL=INFO\n")
    
    print_success("Created .env file with default values")
    return True

def create_run_script():
    """Create a run script based on the OS."""
    print_header("Creating Run Script")
    
    if platform.system() == "Windows":
        # Create batch file for Windows
        with open("run.bat", "w") as f:
            f.write("@echo off\n")
            f.write("call venv\\Scripts\\activate\n")
            f.write("python -m banditgui.app\n")
        print_success("Created run.bat script")
    else:
        # Create shell script for Unix-like systems
        with open("run.sh", "w") as f:
            f.write("#!/bin/bash\n\n")
            f.write("source venv/bin/activate\n")
            f.write("python -m banditgui.app\n")
        
        # Make the script executable
        os.chmod("run.sh", 0o755)
        print_success("Created run.sh script")
    
    return True

def print_final_instructions():
    """Print final instructions for the user."""
    print_header("Installation Complete")
    
    print_info("To run BanditGUI:")
    
    if platform.system() == "Windows":
        print(f"{Colors.BOLD}1. Activate the virtual environment:{Colors.ENDC}")
        print("   venv\\Scripts\\activate")
        print(f"{Colors.BOLD}2. Run the application:{Colors.ENDC}")
        print("   python -m banditgui.app")
        print(f"{Colors.BOLD}Or simply run:{Colors.ENDC}")
        print("   run.bat")
    else:
        print(f"{Colors.BOLD}1. Activate the virtual environment:{Colors.ENDC}")
        print("   source venv/bin/activate")
        print(f"{Colors.BOLD}2. Run the application:{Colors.ENDC}")
        print("   python -m banditgui.app")
        print(f"{Colors.BOLD}Or simply run:{Colors.ENDC}")
        print("   ./run.sh")
    
    print(f"\n{Colors.BOLD}The application will be available at:{Colors.ENDC}")
    print("   http://127.0.0.1:5000")
    
    print(f"\n{Colors.BOLD}To customize settings, edit the .env file{Colors.ENDC}")

def main():
    """Main installation function."""
    print_header("BanditGUI Installation")
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    nodejs_available = check_nodejs()
    npm_available = check_npm()
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Install Node.js dependencies if available
    if nodejs_available and npm_available:
        install_nodejs_dependencies()
    else:
        print_warning("Skipping Node.js dependencies installation")
    
    # Set up environment variables
    setup_environment_variables()
    
    # Create run script
    create_run_script()
    
    # Print final instructions
    print_final_instructions()

if __name__ == "__main__":
    main()
