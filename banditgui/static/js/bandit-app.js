/**
 * BanditGUI Application
 *
 * This script handles both the chat interface and the terminal functionality.
 */

class BanditApp {
    constructor() {
        // Initialize state
        this.isConnected = false;
        this.currentLevel = null;
        this.serverStatus = 'unknown';

        // Initialize components
        this.initChat();
        this.initTerminal();

        // Set up event listeners
        this.setupEventListeners();

        // Set up periodic server status check (after initial check in welcome message)
        setInterval(() => this.checkServerStatus(), 30000); // Check every 30 seconds
    }

    /**
     * Initialize the chat interface
     */
    initChat() {
        this.chatInput = document.getElementById('chat-input');
        this.chatSubmit = document.getElementById('chat-submit');
        this.chatMessages = document.getElementById('chat-messages');
    }

    /**
     * Initialize the terminal interface
     */
    initTerminal() {
        // Create terminal
        this.term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#121212',
                foreground: '#e0e0e0',
                cursor: '#38b6ff',
                selection: 'rgba(58, 134, 255, 0.3)',
                black: '#2d2d2d',
                red: '#ff5c8d',
                green: '#38b000',
                yellow: '#ff9f1c',
                blue: '#3a86ff',
                magenta: '#9d4edd',
                cyan: '#38b6ff',
                white: '#e0e0e0',
                brightBlack: '#6c6c6c',
                brightRed: '#ff5c8d',
                brightGreen: '#38b000',
                brightYellow: '#ff9f1c',
                brightBlue: '#3a86ff',
                brightMagenta: '#9d4edd',
                brightCyan: '#38b6ff',
                brightWhite: '#ffffff'
            },
            fontFamily: '"Fira Code", "Cascadia Code", "Source Code Pro", Consolas, "DejaVu Sans Mono", monospace',
            fontSize: 14,
            lineHeight: 1.2,
            scrollback: 1000,
            convertEol: true,
            padding: 20 // Increased padding to fix text being cut off
        });

        // Load addons
        this.fitAddon = new FitAddon.FitAddon();
        this.term.loadAddon(this.fitAddon);
        this.term.loadAddon(new WebLinksAddon.WebLinksAddon());

        // Open terminal in container
        this.term.open(document.getElementById('terminal-container'));
        this.fitAddon.fit();

        // Terminal state
        this.history = [];
        this.historyIndex = -1;
        this.currentCommand = '';
        this.prompt = '$ ';

        // Set up terminal key event handling
        this.term.onKey(this.handleTerminalKeyEvent.bind(this));

        // Display welcome message and then write prompt
        this.displayTerminalWelcome().then(() => {
            this.writePrompt();
        });

        // Update connection status UI
        this.updateConnectionStatus();
    }

    /**
     * Set up event listeners for UI elements
     */
    setupEventListeners() {
        // Chat input submission
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.handleChatSubmit();
            }
        });

        this.chatSubmit.addEventListener('click', () => {
            this.handleChatSubmit();
        });

        // Start game button
        const startGameButton = document.getElementById('start-game-button');
        if (startGameButton) {
            startGameButton.addEventListener('click', () => {
                this.startNewGame();
            });
        }

        // Handle terminal resize to ensure proper fit
        window.addEventListener('resize', () => {
            this.fitAddon.fit();
        });
    }

    // Panel resizer functionality removed - fixed 50/50 split

    /**
     * Handle chat input submission
     */
    handleChatSubmit() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Clear the input
        this.chatInput.value = '';

        // Display user message
        this.addUserMessage(message);

        // Process the message
        this.processChatCommand(message);
    }

    /**
     * Process chat messages
     */
    async processChatCommand(message) {
        // Split the message into command and arguments
        const parts = message.toLowerCase().trim().split(/\s+/);
        const command = parts[0];

        // Check for special commands
        if (command === 'help') {
            this.showHelpInfo();
        } else if (command === 'info') {
            this.showConnectionInfo();
        } else if (command === 'level') {
            // Check if a level number was provided
            if (parts.length > 1 && !isNaN(parseInt(parts[1]))) {
                const levelNum = parseInt(parts[1]);
                await this.showLevelInfo(levelNum);
            } else {
                await this.showLevelInfo();
            }
        } else if (command === 'hint') {
            // Show hints for the current level
            await this.showLevelHints();
        } else if (command === 'start') {
            // Start a new game
            await this.startNewGame();
        } else if (command === 'clear') {
            // Clear the chat messages
            this.chatMessages.innerHTML = '';
            // Add a system message
            this.addAssistantMessage("Chat cleared.");
        } else if (command === 'quit' || command === 'exit') {
            this.addAssistantMessage("To exit the application, simply close the browser tab or window.");
        } else {
            // For any other message, treat as a general question
            this.addAssistantMessage("I'm a simple assistant for the Bandit wargame. I can help with basic commands like 'help', 'info', 'level', 'hint', 'start', and 'clear'. For game interaction, please use the terminal on the right.");
        }
    }

    /**
     * Show help information
     */
    showHelpInfo() {
        const helpMessage = `
<strong>OverTheWire Bandit Wargame</strong>

Bandit is a beginner-friendly wargame designed to teach the basics of Linux command line, security concepts, and common tools used in cybersecurity.

<strong>How to Play:</strong>
1. Type <code>start</code> or click the <code>Start</code> button to display Level 0 instructions
2. Connect to the Bandit server using the terminal on the right
3. Each level requires you to find a password to access the next level
4. Use Linux commands to navigate the system and find the password
5. Use the password to log in to the next level

<strong>Available Commands in Chat:</strong>
- <code>start</code> - Start a new game
- <code>help</code> - Display this help information
- <code>info</code> - Show connection status and current level
- <code>level</code> - Display instructions for the current level
- <code>level [number]</code> - Display instructions for a specific level
- <code>hint</code> - Get hints for the current level
- <code>clear</code> - Clear the chat messages
- <code>quit</code> - Exit information

<strong>Terminal Commands:</strong>
Use the terminal to execute SSH and Linux commands directly on the server.

<strong>Useful Linux Commands:</strong>
- <code>ls</code> - List files in the current directory
- <code>cd</code> - Change directory
- <code>cat</code> - Display file contents
- <code>file</code> - Determine file type
- <code>find</code> - Search for files
- <code>grep</code> - Search for patterns in files

For more information, visit <a href="https://overthewire.org/wargames/bandit/" target="_blank">OverTheWire Bandit</a>
`;
        this.addAssistantMessage(helpMessage);
    }

    /**
     * Show connection information
     */
    showConnectionInfo() {
        let infoMessage;

        if (this.isConnected) {
            infoMessage = `
<strong>Connection Status:</strong> Connected to Bandit server
<strong>Current Level:</strong> ${this.currentLevel || 'Unknown'}
<strong>Server:</strong> bandit.labs.overthewire.org:2220

Use the terminal on the right to execute commands on the server.
Type <code>level</code> in this chat to see the current level instructions.
`;
        } else {
            infoMessage = `
<strong>Connection Status:</strong> Not connected to Bandit server
<strong>Server:</strong> bandit.labs.overthewire.org:2220
<strong>Server Status:</strong> ${this.serverStatus === 'online' ? '<span style="color: #38b000;">Online</span>' : this.serverStatus === 'offline' ? '<span style="color: #ff5c8d;">Offline</span>' : '<span style="color: #ff9f1c;">Unknown</span>'}

<p>"The journey of a thousand miles begins with a single connection." ~Confucius (if he was a programmer)</p>

<p>Type <code>level</code> in the chat to get instructions for the current level.</p>
`;
        }

        this.addAssistantMessage(infoMessage);
    }

    /**
     * Show level information
     * @param {number|null} specificLevel - Optional specific level to show
     */
    async showLevelInfo(specificLevel = null) {
        // Level information is stored locally, so we don't need to be connected
        // Use the specified level, or current level, or default to 0
        const levelToShow = specificLevel !== null ? specificLevel :
                           (this.isConnected ? (this.currentLevel || 0) : 0);

        try {
            // Get the level information from the server
            const response = await fetch('/level-info', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ level: levelToShow })
            });

            const data = await response.json();

            if (data.status === 'success') {
                const levelInfo = data.levelInfo;

                // Format the commands with links if available
                let commandsHtml = '';
                if (levelInfo.commands) {
                    const commandsList = levelInfo.commands.split(',').map(cmd => cmd.trim());
                    const commandsLinks = levelInfo.commands_links || [];

                    commandsHtml = commandsList.map(cmd => {
                        // Find a matching link for this command
                        const linkObj = commandsLinks.find(link => link.text === cmd);
                        if (linkObj) {
                            return `<a href="${linkObj.url}" target="_blank">${cmd}</a>`;
                        }
                        return cmd;
                    }).join(', ');
                }

                // Format the reading material with links if available
                let readingHtml = '';
                if (levelInfo.reading) {
                    const readingList = levelInfo.reading.split(',').map(item => item.trim());
                    const readingLinks = levelInfo.reading_links || [];

                    readingHtml = readingLinks.map(link => {
                        return `<a href="${link.url}" target="_blank">${link.text}</a>`;
                    }).join('<br>');
                }

                let levelMessage = `
<div class="level-info">
<h4>Level ${levelInfo.level}</h4>

<strong>Goal:</strong>
<p>${levelInfo.goal}</p>

<strong>Commands you may need:</strong>
<p>${commandsHtml || levelInfo.commands}</p>

<strong>Helpful reading material:</strong>
<p>${readingHtml || levelInfo.reading || 'None provided'}</p>

<strong>Connection Command:</strong>
<pre>ssh bandit${levelInfo.level}@bandit.labs.overthewire.org -p 2220</pre>

<p class="hint-prompt">Type <code>hint</code> in the chat if you need additional help.</p>
</div>
`;
                this.addAssistantMessage(levelMessage);
            } else {
                this.addAssistantMessage(`Error getting level information: ${data.message}`);
            }
        } catch (error) {
            this.addAssistantMessage(`Error: Failed to get level information. ${error.message}`);
            console.error('Level info error:', error);
        }
    }

    /**
     * Show hints for the current level
     */
    async showLevelHints() {
        if (!this.currentLevel && this.currentLevel !== 0) {
            this.addAssistantMessage("Please display Level 0 instructions first by typing <code>start</code> in the chat or clicking the <code>Start</code> button.");
            return;
        }

        try {
            // Get the level information from the server
            const response = await fetch('/level-info', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ level: this.currentLevel || 0 })
            });

            const data = await response.json();

            if (data.status === 'success') {
                const levelInfo = data.levelInfo;

                // Create a hint message based on the level
                let hintMessage = `<div class="level-hint">
<h4>Hints for Level ${levelInfo.level}</h4>
`;

                // Add level-specific hints
                switch(parseInt(levelInfo.level)) {
                    case 0:
                        hintMessage += `<p>For this level, you just need to log in. Use the SSH command shown and the password 'bandit0'.</p>
<p>Once logged in, you can use <code>ls</code> to list files and <code>cat</code> to read file contents.</p>`;
                        break;
                    case 1:
                        hintMessage += `<p>The password is stored in a file called 'readme' in the home directory.</p>
<p>Use <code>ls</code> to see the file and <code>cat readme</code> to read its contents.</p>`;
                        break;
                    case 2:
                        hintMessage += `<p>The password is stored in a file called '-' which is a special character in Linux.</p>
<p>To read files with special characters in their names, you can use <code>cat ./-</code> or <code>cat < -</code>.</p>`;
                        break;
                    default:
                        hintMessage += `<p>For this level, carefully read the goal and think about which commands might help.</p>
<p>Remember to use <code>man [command]</code> to read the manual for any command you're not familiar with.</p>`;
                }

                hintMessage += `</div>`;

                this.addAssistantMessage(hintMessage);
            } else {
                this.addAssistantMessage(`Error getting hint information: ${data.message}`);
            }
        } catch (error) {
            this.addAssistantMessage(`Error: Failed to get hint information. ${error.message}`);
            console.error('Hint info error:', error);
        }
    }

    /**
     * Start a new game
     */
    async startNewGame() {
        // Clear the chat messages
        this.chatMessages.innerHTML = '';

        // Add a welcome message
        const welcomeMessage = `<div class="system-message">
            <p><strong>Welcome to BanditGUI!</strong></p>
            <p>Here are the instructions for Level 0 of the Bandit wargame, a series of challenges designed to teach Linux commands and security concepts.</p>
        </div>`;

        this.chatMessages.innerHTML = welcomeMessage;

        // Show level 0 information
        await this.showLevelInfo(0);

        // Set current level to 0
        this.currentLevel = 0;

        // Update connection status UI
        this.updateConnectionStatus();
    }

    /**
     * Handle quit command
     */
    async handleQuit() {
        if (this.isConnected) {
            await this.disconnectFromServer();
        }

        this.addAssistantMessage("Goodbye! The application will close in a few seconds...");

        // Simulate application exit after a short delay
        setTimeout(() => {
            this.addAssistantMessage("To actually exit the application, close this browser tab or window.");
        }, 3000);
    }

    /**
     * Add a user message to the chat
     */
    addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'user-message';
        messageElement.innerHTML = `
            <div class="user-label">You:</div>
            <div class="message-content">${message}</div>
        `;
        this.chatMessages.appendChild(messageElement);
        this.scrollChatToBottom();
    }

    /**
     * Add an assistant message to the chat
     */
    addAssistantMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'assistant-message';

        // Format the message with proper line breaks
        const formattedMessage = message
            .replace(/\n\n/g, '</p><p>') // Double line breaks become new paragraphs
            .replace(/\n/g, '<br>'); // Single line breaks become <br>

        messageElement.innerHTML = `
            <div class="assistant-label">Assistant:</div>
            <div class="message-content"><p>${formattedMessage}</p></div>
        `;
        this.chatMessages.appendChild(messageElement);
        this.scrollChatToBottom();
    }

    /**
     * Scroll chat to the bottom
     */
    scrollChatToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    /**
     * Handle terminal key events
     */
    handleTerminalKeyEvent(e) {
        const ev = e.domEvent;
        const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey;

        if (ev.keyCode === 13) { // Enter key
            this.handleTerminalEnter();
        } else if (ev.keyCode === 8) { // Backspace
            if (this.currentCommand.length > 0) {
                this.currentCommand = this.currentCommand.slice(0, -1);
                this.term.write('\b \b');
            }
        } else if (ev.keyCode === 38) { // Up arrow
            this.navigateHistory('up');
        } else if (ev.keyCode === 40) { // Down arrow
            this.navigateHistory('down');
        } else if (printable) {
            this.currentCommand += e.key;
            this.term.write(e.key);
        }
    }

    /**
     * Handle terminal Enter key
     */
    async handleTerminalEnter() {
        this.term.write('\r\n');

        const command = this.currentCommand.trim();
        if (command) {
            this.history.push(command);
            this.historyIndex = this.history.length;

            // Execute all commands directly
            await this.executeCommand(command);
        }

        this.currentCommand = '';
        this.writePrompt();
    }

    /**
     * Navigate command history
     */
    navigateHistory(direction) {
        if (direction === 'up' && this.historyIndex > 0) {
            this.historyIndex--;
        } else if (direction === 'down' && this.historyIndex < this.history.length) {
            this.historyIndex++;
        } else {
            return;
        }

        // Clear current command
        this.term.write('\r' + ' '.repeat(this.prompt.length + this.currentCommand.length) + '\r');

        // Write new command from history or empty if at the end
        const newCommand = this.historyIndex < this.history.length ? this.history[this.historyIndex] : '';
        this.currentCommand = newCommand;
        this.term.write(this.prompt + newCommand);
    }

    /**
     * Execute a command on the server
     */
    async executeCommand(command) {
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ command })
            });
            const data = await response.json();

            if (data.status === 'success') {
                if (data.output) {
                    this.writeLine(data.output);
                }

                // Check if the level has changed
                if (data.currentLevel !== undefined && data.currentLevel !== this.currentLevel) {
                    this.currentLevel = data.currentLevel;
                    // Notify the user about the level change
                    this.term.write(`\r\n\x1b[33mYou are now on level ${this.currentLevel}\x1b[0m\r\n`);
                }
            } else if (data.status === 'error') {
                this.writeLine(`\r\n\x1b[31m${data.message}\x1b[0m\r\n`);
            }
        } catch (error) {
            this.writeLine(`\r\n\x1b[31mError: Failed to execute command. ${error.message}\x1b[0m\r\n`);
            console.error('Command execution error:', error);
        }
    }

    /**
     * Connect to the Bandit server
     */
    async connectToServer() {
        try {
            const response = await fetch('/connect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            const data = await response.json();

            if (data.status === 'success') {
                this.isConnected = true;
                this.currentLevel = data.currentLevel || 0;
                this.updateConnectionStatus();

                // Clear the terminal
                this.term.clear();

                // Display success message
                this.term.write('\x1b[32mGood job!\x1b[0m\r\n');
                this.term.write('\x1b[33m - Connection Status: Connected\x1b[0m\r\n\r\n');
                this.writePrompt();

                // Update the connect button text
                const connectButton = document.getElementById('connect-button');
                connectButton.textContent = 'Disconnect';
                connectButton.classList.add('disconnect');

                // Clear chat panel and display level 1 information
                this.chatMessages.innerHTML = '';
                this.showLevelInfo(1);
            } else {
                this.term.write(`\r\n\x1b[31mFailed to connect: ${data.message}\x1b[0m\r\n`);
                this.addAssistantMessage(`Failed to connect to the server: ${data.message}`);
            }
        } catch (error) {
            this.term.write(`\r\n\x1b[31mError: ${error.message}\x1b[0m\r\n`);
            this.addAssistantMessage(`Error connecting to the server: ${error.message}`);
            console.error('Connection error:', error);
        }
    }

    /**
     * Disconnect from the Bandit server
     */
    async disconnectFromServer() {
        try {
            const response = await fetch('/disconnect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            const data = await response.json();

            if (data.status === 'success') {
                this.isConnected = false;
                this.currentLevel = null;
                this.updateConnectionStatus();
                this.term.write('\r\n\x1b[33mDisconnected from SSH server.\x1b[0m\r\n');

                // Update the connect button text
                const connectButton = document.getElementById('connect-button');
                connectButton.textContent = 'Connect to Server';
                connectButton.classList.remove('disconnect');

                // Show a message in the chat
                this.addAssistantMessage("Disconnected from the Bandit server.");
            } else {
                this.term.write(`\r\n\x1b[31mFailed to disconnect: ${data.message}\x1b[0m\r\n`);
                this.addAssistantMessage(`Failed to disconnect from the server: ${data.message}`);
            }
        } catch (error) {
            this.term.write(`\r\n\x1b[31mError: ${error.message}\x1b[0m\r\n`);
            this.addAssistantMessage(`Error disconnecting from the server: ${error.message}`);
            console.error('Disconnection error:', error);
        }
    }

    /**
     * Check the status of the Bandit server
     */
    async checkServerStatus() {
        try {
            const response = await fetch('/server-status');
            const data = await response.json();

            if (data.status === 'success') {
                const serverStatus = data.serverStatus;
                this.serverStatus = serverStatus.status; // 'online' or 'offline'
                this.updateServerStatusUI();
            } else {
                console.error('Error checking server status:', data.message);
                this.serverStatus = 'unknown';
                this.updateServerStatusUI();
            }
        } catch (error) {
            console.error('Error checking server status:', error);
            this.serverStatus = 'unknown';
            this.updateServerStatusUI();
        }
    }

    /**
     * Update the server status UI
     */
    updateServerStatusUI() {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');

        if (this.serverStatus === 'online') {
            statusIndicator.classList.remove('disconnected');
            statusIndicator.classList.add('connected');
            statusText.innerHTML = 'Server: <span style="color: #98c379;">Online</span>';
        } else if (this.serverStatus === 'offline') {
            statusIndicator.classList.remove('connected');
            statusIndicator.classList.add('disconnected');
            statusText.innerHTML = 'Server: <span style="color: #e06c75;">Offline</span>';
        } else {
            statusIndicator.classList.remove('connected');
            statusIndicator.classList.add('disconnected');
            statusText.innerHTML = 'Server: <span style="color: #e5c07b;">Unknown</span>';
        }
    }

    /**
     * Update the connection status UI
     */
    updateConnectionStatus() {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');

        if (this.isConnected) {
            statusIndicator.classList.remove('disconnected');
            statusIndicator.classList.add('connected');
            statusText.textContent = `Connected (Level ${this.currentLevel || 0})`;
        } else {
            // Let the server status UI handle this
            this.updateServerStatusUI();
        }
    }

    /**
     * Write a line to the terminal
     */
    writeLine(text) {
        // Process text and handle newlines properly
        if (!text) return;

        // Remove extra newlines at the beginning and end
        const trimmedText = text.replace(/^\n+|\n+$/g, '');

        // Write the text with proper line breaks
        if (trimmedText) {
            this.term.write('\r\n' + trimmedText);
        }
    }

    /**
     * Write the prompt to the terminal
     */
    writePrompt() {
        this.term.write('\r\n' + this.prompt);
    }

    /**
     * Display welcome message in the terminal
     */
    async displayTerminalWelcome() {
        // Try to get a welcome quote from the quote manager
        let welcomeQuote = '';
        try {
            if (window.quoteManager) {
                const welcomeQuotes = await window.quoteManager.loadWelcomeQuotes(1);
                welcomeQuote = welcomeQuotes[0];
            }
        } catch (error) {
            console.error('Error loading welcome quote:', error);
            welcomeQuote = '"Welcome to the Bandit Wargame Terminal!"';
        }

        // Display welcome quote
        this.term.write('\x1b[34m' + welcomeQuote + '\x1b[0m\r\n\r\n');

        // Display progress bar
        await this.displayProgressBar();

        this.term.write('\r\n\x1b[33mSystem Status: \x1b[0m');

        // Check server status
        try {
            const response = await fetch('/server-status');
            const data = await response.json();

            if (data.status === 'success') {
                const serverStatus = data.serverStatus;
                this.serverStatus = serverStatus.status; // 'online' or 'offline'

                if (this.serverStatus === 'online') {
                    this.term.write('\x1b[32mALL SYSTEMS GO!\x1b[0m\r\n\r\n');
                } else {
                    this.term.write('\x1b[31mOFFLINE\x1b[0m\r\n');
                    if (serverStatus.error) {
                        this.term.write(serverStatus.error + '\x1b[0m\r\n\r\n');
                    } else {
                        this.term.write('Cannot connect to the server.\x1b[0m\r\n\r\n');
                    }
                }
            } else {
                this.term.write('\x1b[33mUNKNOWN\x1b[0m\r\n');
                this.term.write(data.message + '\x1b[0m\r\n\r\n');
            }
        } catch (error) {
            this.term.write('\x1b[33mUNKNOWN\x1b[0m\r\n');
            this.term.write(error.message + '\x1b[0m\r\n\r\n');
        }

        // Update the UI with the server status
        this.updateServerStatusUI();

        // Display instructions
        this.term.write('\x1b[33mType "start" or click the "Start" button to display Level 0 instructions.\x1b[0m\r\n\r\n');

        // Initialize the quote display in the UI
        if (window.quoteManager) {
            const quote = await window.quoteManager.getRandomQuote();
            const quoteMessage = document.getElementById('quote-message');
            if (quoteMessage) {
                quoteMessage.innerHTML = window.quoteManager.formatQuote(quote);
                quoteMessage.classList.add('quote-fade-in');
            }
        }

        // No longer automatically show level 0 information
    }

    /**
     * Display a progress bar in the terminal
     */
    async displayProgressBar() {
        const progressBarWidth = 30;
        const progressChar = '█';
        const emptyChar = '░';

        this.term.write('[');

        for (let i = 0; i <= progressBarWidth; i++) {
            // Calculate percentage
            const percent = Math.floor((i / progressBarWidth) * 100);

            // Build progress bar
            const filled = progressChar.repeat(i);
            const empty = emptyChar.repeat(progressBarWidth - i);

            // Move cursor to beginning of line and write progress bar
            this.term.write('\r[' + filled + empty + '] ' + percent + '%');

            // Wait for a short time to simulate progress
            await new Promise(resolve => setTimeout(resolve, 2000 / progressBarWidth));
        }
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.banditApp = new BanditApp();
});
