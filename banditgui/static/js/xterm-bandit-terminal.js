class XtermBanditTerminal {
    constructor() {
        this.history = [];
        this.historyIndex = -1;
        this.currentCommand = '';
        this.prompt = '$ ';
        this.isConnected = false;
        this.init();
    }

    init() {
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
            fontFamily: 'monospace',
            fontSize: 14,
            lineHeight: 1.2,
            scrollback: 1000,
            convertEol: true
        });

        // Load addons
        this.fitAddon = new FitAddon.FitAddon();
        this.term.loadAddon(this.fitAddon);
        this.term.loadAddon(new WebLinksAddon.WebLinksAddon());

        // Open terminal in container
        this.term.open(document.getElementById('terminal-container'));
        this.fitAddon.fit();

        // Handle terminal resize
        window.addEventListener('resize', () => {
            this.fitAddon.fit();
        });

        // Set up key event handling
        this.term.onKey(this.handleKeyEvent.bind(this));

        // Display welcome message
        this.displayWelcomeMessage();

        // Write initial prompt
        this.writePrompt();
    }

    handleKeyEvent(e) {
        const ev = e.domEvent;
        const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey;

        if (ev.keyCode === 13) { // Enter key
            this.handleEnter();
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

    async handleEnter() {
        this.term.write('\r\n');

        const command = this.currentCommand.trim();
        if (command) {
            this.history.push(command);
            this.historyIndex = this.history.length;
            await this.executeCommand(command);
        }

        this.currentCommand = '';
        this.writePrompt();
    }

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

    async executeCommand(command) {
        // Handle connect command specially
        if (command === 'connect') {
            try {
                const response = await fetch('/connect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();

                if (data.status === 'success') {
                    this.isConnected = true;
                    this.writeLine('\r\n\x1b[32mSuccessfully connected to SSH server.\x1b[0m\r\n');
                } else {
                    this.writeLine(`\r\n\x1b[31mFailed to connect: ${data.message}\x1b[0m\r\n`);
                }
            } catch (error) {
                this.writeLine(`\r\n\x1b[31mError: ${error.message}\x1b[0m\r\n`);
            }
            return;
        }

        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ command })
            });
            const data = await response.json();

            if (data.status === 'clear') {
                this.clearTerminal();
            } else if (data.status === 'success') {
                if (data.output) {
                    this.writeLine(data.output);
                }
            } else if (data.status === 'error') {
                this.writeLine(`\r\n\x1b[31m${data.message}\x1b[0m\r\n`);
            }
        } catch (error) {
            this.writeLine(`\r\n\x1b[31mError: Failed to execute command. ${error.message}\x1b[0m\r\n`);
            console.error('Command execution error:', error);
        }
    }

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

    writePrompt() {
        this.term.write(this.prompt);
    }

    displayWelcomeMessage() {
        this.term.write('\x1b[34m"Welcome to BanditGUI Terminal!" \x1b[33m~Neo from The Matrix\x1b[0m\r\n\r\n');
        this.term.write('\x1b[36m"I find your lack of terminal skills disturbing." \x1b[33m~Darth Vader\x1b[0m\r\n\r\n');
        this.term.write('Type \x1b[33mhelp\x1b[0m to see available commands.\r\n');
        this.term.write('Type \x1b[33minfo\x1b[0m to get information about the Bandit server.\r\n');
        this.term.write('Type \x1b[33mconnect\x1b[0m to establish an SSH connection.\r\n');
        this.term.write('Type \x1b[33mlevel <number>\x1b[0m to get information about a specific level.\r\n');
        this.term.write('Type \x1b[33mstart\x1b[0m or click the \x1b[33mStart\x1b[0m button to display Level 0 instructions.\r\n\r\n');
    }

    clearTerminal() {
        this.term.clear();
        this.displayWelcomeMessage();
    }
}

// Initialize Bandit terminal when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.banditTerminal = new XtermBanditTerminal();
});
