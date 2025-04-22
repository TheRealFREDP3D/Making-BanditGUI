class BanditTerminal {
    constructor() {
        this.history = [];
        this.historyIndex = -1;
        this.init();
    }

    init() {
        this.input = document.getElementById('terminal-input');
        this.output = document.getElementById('terminal-output');
        this.input.addEventListener('keydown', this.handleInput.bind(this));
        this.displayWelcomeMessage();
    }

    async handleInput(event) {
        if (event.key === 'Enter') {
            const command = event.target.value.trim();
            await this.executeCommand(command);
            event.target.value = '';
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            this.navigateHistory('up');
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            this.navigateHistory('down');
        }
    }

    async executeCommand(command) {
        if (!command) return;
        this.history.push(command);
        this.historyIndex = this.history.length;

        // Handle connect command specially
        if (command === 'connect') {
            const response = await fetch('/connect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            const data = await response.json();
            this.displayOutput('System:', data.message);
            return;
        }

        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ command })
            });
            const data = await response.json();

            // Display the command that was entered
            this.displayOutput('$', command);

            // Add an empty line for better readability
            this.addEmptyLine();

            // Handle different response types
            if (data.status === 'clear') {
                this.clearTerminal();
                return;
            } else if (data.status === 'success') {
                if (data.output) {
                    this.displayOutput('', data.output);
                }
            } else if (data.status === 'error') {
                this.displayOutput('Error:', data.message, 'error-message');
            }

            // Add another empty line after the response
            this.addEmptyLine();
        } catch (error) {
            this.displayOutput('Error:', 'Failed to execute command. Please try again.', 'error-message');
            console.error('Command execution error:', error);
        }
    }

    displayOutput(prefix, content, className = '') {
        const output = document.getElementById('terminal-output');
        const line = document.createElement('div');
        line.className = `terminal-line ${className}`;
        line.innerHTML = `<span class="prefix">${prefix}</span> ${content}`;
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }

    navigateHistory(direction) {
        if (direction === 'up' && this.historyIndex > 0) {
            this.historyIndex--;
        } else if (direction === 'down' && this.historyIndex < this.history.length) {
            this.historyIndex++;
        }
        this.input.value = this.history[this.historyIndex] || '';
    }

    displayWelcomeMessage() {
        this.displayOutput('System:', 'Welcome to BanditGUI Terminal - OverTheWire Bandit CTF', 'welcome-message');
        this.displayOutput('System:', 'Type "help" to see available commands.', 'welcome-message');
        this.displayOutput('System:', 'Type "info" to get information about the Bandit server.', 'welcome-message');
        this.displayOutput('System:', 'Type "connect" to establish an SSH connection.', 'welcome-message');
        this.displayOutput('System:', 'After connecting, you can run actual commands on the SSH server.', 'welcome-message');
    }

    clearTerminal() {
        this.output.innerHTML = '';
        this.displayWelcomeMessage();
    }

    addEmptyLine() {
        const output = document.getElementById('terminal-output');
        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.innerHTML = '&nbsp;';
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }
}

// Initialize Bandit terminal when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.banditTerminal = new BanditTerminal();
});