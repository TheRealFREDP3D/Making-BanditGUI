# BanditGUI Installation Guide

This guide provides instructions for installing and running BanditGUI on your system.

---

## Prerequisites

- Python 3.6 or higher
- Node.js and npm (optional, for frontend development)

---

## Automatic Installation

### Windows

1. Download the project from GitHub
2. Double-click on `install.bat`
3. Follow the on-screen instructions
4. After installation, run `run.bat` to start the application

### Linux/macOS

1. Download the project from GitHub
2. Open a terminal in the project directory
3. Make the installation script executable:
   ```bash
   chmod +x install.sh
   ```
4. Run the installation script:
   ```bash
   ./install.sh
   ```
5. After installation, run the application:
   ```bash
   ./run.sh
   ```

---

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

---

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

---

## Next Steps

After installation, you can:

1. Launch the application
2. Connect to the Bandit server using the terminal
3. Use the 'level' command to get information about the current level
4. Start solving challenges and learning security concepts!
