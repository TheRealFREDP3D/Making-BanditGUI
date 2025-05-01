# BanditGUI Project Documentation

This documentation provides a comprehensive overview of the BanditGUI project architecture, components, and workflows.

---

## Project Architecture

BanditGUI follows a modular architecture with clear separation of concerns:

### Core Components

- **App Module**: Main Flask application that serves as the entry point
- **Terminal Module**: Handles terminal emulation and user input
- **SSH Module**: Manages SSH connections to the Bandit server
- **Chat Module**: Processes user commands and provides responses
- **Data Module**: Stores and retrieves level information

### Component Relationships

- The App Module coordinates between all other modules
- The Terminal Module sends commands to the SSH Module
- The SSH Module executes commands on the Bandit server
- The Chat Module provides information based on user input
- The Data Module supplies level-specific information to other modules

---

## SSH Flow

The SSH connection process follows these steps:

1. **User Initiates Connection**: User clicks connect or enters SSH command
2. **Connect Request**: Application sends request to SSH Manager
3. **SSH Client Creation**: SSH Manager creates a new SSH client
4. **Host Key Policy**: SSH Manager sets the host key policy
5. **Connection Attempt**: SSH Manager attempts to connect with credentials
6. **Connection Result**: Bandit server returns success or failure
7. **Logging**: Connection status is logged
8. **Result Handling**: Connection result is returned to application
9. **Terminal Update**: Terminal status is updated
10. **Command Execution**: Commands are executed through the connection
11. **Command Output**: Output is returned and displayed in terminal

![SSH Flow Diagram](https://github.com/TheRealFREDP3D/Making-BanditGUI/raw/main/docs/assets/v0.3-SSH-Flow.png)

---

## Chat Flow

The chat system processes user input and provides appropriate responses:

1. **User Input**: User enters a command in the chat input
2. **Command Processing**: Chat Manager processes the command
3. **Command Recognition**: System identifies the command type
4. **Information Retrieval**: System retrieves relevant information
5. **Response Generation**: System generates appropriate response
6. **Response Display**: Response is displayed in the chat panel

---

## File Structure

```
banditgui/
├── app.py                 # Main application entry point
├── exceptions.py          # Custom exception classes
├── __init__.py            # Package initialization
├── chat/                  # Chat module
│   ├── chat_manager.py    # Manages chat interactions
│   └── __init__.py
├── config/                # Configuration module
│   ├── config_manager.py  # Manages application configuration
│   └── __init__.py
├── data/                  # Data module
│   ├── level_data.json    # Level information
│   ├── data_manager.py    # Manages data access
│   └── __init__.py
├── ssh/                   # SSH module
│   ├── ssh_manager.py     # Manages SSH connections
│   └── __init__.py
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Image assets
├── templates/             # HTML templates
│   └── index.html         # Main application template
├── terminal/              # Terminal module
│   ├── terminal_manager.py # Manages terminal interactions
│   └── __init__.py
└── utils/                 # Utility functions
    ├── logger.py          # Logging utilities
    └── __init__.py
```

---

## Key Classes and Functions

### App Module

- **Flask Application**: Initializes and configures the Flask application
- **Route Handlers**: Processes HTTP requests and WebSocket connections
- **Event Handlers**: Manages Socket.IO events

### Terminal Module

- **TerminalManager**: Manages terminal state and interactions
- **Command Processing**: Handles user input in the terminal
- **Output Formatting**: Formats command output for display

### SSH Module

- **SSHManager**: Manages SSH connections and authentication
- **Command Execution**: Executes commands on the Bandit server
- **Error Handling**: Handles SSH connection and execution errors

### Chat Module

- **ChatManager**: Processes chat commands and generates responses
- **Command Recognition**: Identifies and processes different command types
- **Response Generation**: Creates appropriate responses to user input

### Data Module

- **DataManager**: Provides access to level information
- **Level Data**: Stores goals, commands, and hints for each level
- **Data Loading**: Loads level data from JSON files

---

## Development Workflow

1. **Setup Development Environment**: Install dependencies and configure environment
2. **Run Development Server**: Start the Flask development server
3. **Make Changes**: Modify code, templates, or static assets
4. **Test Changes**: Verify changes work as expected
5. **Document Changes**: Update documentation as needed
6. **Commit Changes**: Commit changes to version control

---

## Deployment

BanditGUI can be deployed in several ways:

1. **Local Deployment**: Run on local machine for personal use
2. **Server Deployment**: Deploy to a web server for shared access
3. **Container Deployment**: Deploy using Docker for consistent environments

For detailed deployment instructions, see the Installation Guide.
