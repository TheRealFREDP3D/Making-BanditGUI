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

Copy the `.env.example` file to a new file named `.env`.
```bash
cp .env.example .env
```
Then, edit the `.env` file to set your desired configurations.

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

- `SSH_HOST`: The hostname of the SSH server (default: "bandit.labs.overthewire.org").
- `SSH_PORT`: The port of the SSH server (default: "2220").
- `SSH_USERNAME`: The initial SSH username (default: "bandit0"). This will change as you solve levels.
- `SSH_PASSWORD`: The initial SSH password (default: "bandit0"). This will change as you solve levels.
- `DEBUG`: Set to "True" to enable Flask debug mode, or "False" for production (default: "True").
- `HOST`: The host address for the Flask application (default: "127.0.0.1").
- `PORT`: The port for the Flask application (default: "5000").
- `LOG_LEVEL`: The logging level for the application. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: "INFO").
- `OPENAI_API_KEY`: Your API key for OpenAI services. (e.g., "YOUR_OPENAI_API_KEY_HERE")
- `GEMINI_API_KEY`: Your API key for Google Gemini services. (e.g., "YOUR_GEMINI_API_KEY_HERE")
- `OPENROUTER_API_KEY`: Your API key for OpenRouter services. (e.g., "YOUR_OPENROUTER_API_KEY_HERE")
- `OLLAMA_BASE_URL`: The base URL for your local Ollama instance (default: "http://localhost:11434"). Uncomment and set if different from the default.
- `PREFERRED_LLM_PROVIDER`: The default LLM provider for the "Ask a Pro" feature (default: "gemini"). Supported: "openai", "gemini", "openrouter", "ollama", etc.
- `PREFERRED_LLM_MODEL`: The default LLM model for the chosen provider (default: "gemini-1.5-flash-latest"). Examples: "gpt-3.5-turbo", "gemini/gemini-pro", "ollama/llama2".
