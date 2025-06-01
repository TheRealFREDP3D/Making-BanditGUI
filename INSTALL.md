# BanditGUI Installation Guide

This document provides instructions for installing and running BanditGUI.

## Prerequisites

- Python 3.6 or higher
- Node.js and npm (optional, for frontend development)

## Automatic Installation

### Windows

1. Double-click on `install.bat`
2. Follow the on-screen instructions
3. After installation, run `run.bat` to start the application

### Linux/macOS

1. Open a terminal in the project directory
2. Make the installation script executable:
   ```bash
   chmod +x install.sh
   ```
3. Run the installation script:
   ```bash
   ./install.sh
   ```
4. After installation, run the application:
   ```bash
   ./run.sh
   ```

## Manual Installation

If the automatic installation doesn't work, you can follow these steps:

### 1. Create a Virtual Environment

```bash
# Windows
python -m venv venv

# Linux/macOS
python3 -m venv venv
```

### 2. Activate the Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies (Optional)

```bash
npm install
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root with the following content:

```
SSH_HOST=bandit.labs.overthewire.org
SSH_PORT=2220
SSH_USERNAME=bandit0
SSH_PASSWORD=bandit0
DEBUG=True
HOST=127.0.0.1
PORT=5000
LOG_LEVEL=INFO
```

### 6. Run the Application

```bash
# Windows
python -m banditgui.app

# Linux/macOS
python3 -m banditgui.app
```

## Troubleshooting

### Python Not Found

Ensure Python is installed and added to your PATH. You can download Python from [python.org](https://www.python.org/).

### Node.js Not Found

If you get errors about Node.js or npm not being found, you can install them from [nodejs.org](https://nodejs.org/).

### Permission Denied

On Linux/macOS, if you get permission denied errors, make sure the scripts are executable:

```bash
chmod +x install.sh run.sh
```

### Connection Issues

If you have trouble connecting to the Bandit server, check your internet connection and verify that the server is accessible.

## Customization

You can customize the application by editing the `.env` file. The following options are available:

- `SSH_HOST`: The hostname of the SSH server
- `SSH_PORT`: The port of the SSH server
- `SSH_USERNAME`: The default username for SSH connections
- `SSH_PASSWORD`: The default password for SSH connections
- `DEBUG`: Whether to run Flask in debug mode (True/False)
- `HOST`: The host to bind the Flask application to
- `PORT`: The port to bind the Flask application to
- `LOG_LEVEL`: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
