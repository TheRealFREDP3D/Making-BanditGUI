"""
Terminal Manager for BanditGUI.

This module provides functionality for handling terminal commands.
"""

from typing import List

from banditgui.config.logging import get_logger
from banditgui.config.settings import config

logger = get_logger('terminal.manager')


class TerminalManager:
    """
    Manager for terminal commands and interactions.
    """

    def __init__(self, ssh_manager=None):
        """
        Initialize the terminal manager.

        Args:
            ssh_manager: The SSH manager to use for SSH commands
        """
        self.ssh_manager = ssh_manager
        self.ssh_connected = False
        self.available_levels = []
        self.current_level = None

        # Initialize commands dictionary
        self.commands = {
            'help': self.help_command,
            'info': self.info_command,
            'clear': self.clear_command,
            'ssh': self.ssh_command,
            'echo': self.echo_command,
            'level': self.level_command,
            'general': self.general_command,
            'connect': self.connect_command
        }

        # Load level information
        self._load_level_info()

        logger.debug("TerminalManager initialized")

    def _load_level_info(self) -> None:
        """Load level information."""
        try:
            # Import here to avoid circular imports
            from banditgui.utils import get_available_levels
            self.available_levels = get_available_levels()
            logger.info(f"Loaded {len(self.available_levels)} available levels")
        except Exception as e:
            logger.error(f"Error loading level information: {e}")
            self.available_levels = [0, 1]
            logger.warning("Using default levels [0, 1]")

    def execute_command(self, command: str) -> str:
        """
        Execute a terminal command.

        Args:
            command: The command to execute

        Returns:
            str: The command output
        """
        if not command:
            return ""

        logger.info(f"Executing command: {command}")
        cmd_parts = command.split()
        cmd = cmd_parts[0].lower()

        # Only handle clear command locally
        if cmd == 'clear':
            logger.debug("Executing clear command")
            return "<clear>"

        # Handle SSH command specially
        if cmd == 'ssh':
            logger.debug(f"Handling SSH command: {command}")
            # Let the SSH command go through to the SSH manager
            result = self.ssh_manager.execute_command(command)

            # Check if the command was successful and update connection status
            if not self.ssh_connected and "Permission denied" not in result and "Error" not in result:
                self.ssh_connected = True
                # Try to extract level from command
                try:
                    if 'bandit' in command:
                        level_part = command.split('bandit')[1].split('@')[0]
                        self.current_level = int(level_part)
                    else:
                        self.current_level = 0
                    logger.info(f"Connected to SSH server, level set to {self.current_level}")
                except (ValueError, IndexError):
                    self.current_level = 0
                    logger.info("Connected to SSH server, level set to 0")

            return result

        # For all other commands, check if connected
        if self.ssh_connected:
            # Execute the command on the SSH server
            logger.debug(f"Forwarding command to SSH: {command}")
            return self.ssh_manager.execute_command(command)
        else:
            # Not connected, show helpful message
            return "Not connected to the SSH server. Use the SSH command to connect:\n\nssh bandit0@bandit.labs.overthewire.org -p 2220\n\nPassword: bandit0"

    def help_command(self, args: List[str]) -> str:
        """
        Display help information.

        Args:
            args: Command arguments

        Returns:
            str: Help information
        """
        logger.debug("Executing help command")
        return """
Available commands:
  help                - Display this help message
  info                - Display information about the Bandit server
  clear               - Clear the terminal screen
  level [number]      - Display information about a specific level
  general             - Display general information about the Bandit wargame
  ssh [options]       - Connect to SSH server

All other commands will be executed directly on the SSH server.
"""

    def info_command(self, args: List[str]) -> str:
        """
        Display information about the Bandit server.

        Args:
            args: Command arguments

        Returns:
            str: Server information
        """
        logger.debug("Executing info command")
        return f"""
OverTheWire Bandit Server Information:
  Host: {config.ssh_host}
  Port: {config.ssh_port}
  Initial Username: bandit0
  Initial Password: bandit0
  Current Level: {self.current_level if self.current_level is not None else 'Not connected'}
"""

    def clear_command(self, args: List[str]) -> str:
        """
        Clear the terminal screen.

        Args:
            args: Command arguments

        Returns:
            str: Clear command signal
        """
        logger.debug("Executing clear command")
        return "<clear>"

    def ssh_command(self, args: List[str]) -> str:
        """
        Handle SSH command.

        Args:
            args: Command arguments

        Returns:
            str: SSH command output or help information
        """
        logger.debug(f"Executing ssh command with args: {args}")
        if not args:
            return """
Usage: ssh [username@]hostname [-p port]

Examples:
  ssh bandit0@bandit.labs.overthewire.org -p 2220    - Connect to Bandit level 0
  ssh bandit1@bandit.labs.overthewire.org -p 2220    - Connect to Bandit level 1
"""
        else:
            # Always forward SSH commands to the server
            logger.debug("Forwarding ssh command to SSH server")

            # If not connected, try to connect first
            if not self.ssh_connected and self.ssh_manager:
                logger.info("Auto-connecting to SSH server before executing SSH command")
                connect_result = self.ssh_manager.connect()
                if connect_result is True:
                    self.ssh_connected = True
                    self.current_level = 0
                    logger.info("Successfully auto-connected to SSH server")
                else:
                    logger.error(f"Failed to auto-connect to SSH server: {connect_result}")
                    return f"Failed to connect to SSH server: {connect_result}"

            # Execute the SSH command
            return self.ssh_manager.execute_command("ssh " + " ".join(args))

    def echo_command(self, args: List[str]) -> str:
        """
        Echo the provided text.

        Args:
            args: Command arguments

        Returns:
            str: The echoed text
        """
        logger.debug(f"Executing echo command with args: {args}")
        return " ".join(args)

    def level_command(self, args: List[str]) -> str:
        """
        Display information about a specific level.

        Args:
            args: Command arguments

        Returns:
            str: Level information or usage instructions
        """
        logger.debug(f"Executing level command with args: {args}")
        if not args:
            return f"""Usage: level <number>

Available levels: {', '.join(map(str, self.available_levels))}

Example: level 0"""

        try:
            level_num = int(args[0])
            if level_num not in self.available_levels:
                logger.warning(f"Level {level_num} not found")
                return f"Level {level_num} not found. Available levels: {', '.join(map(str, self.available_levels))}"

            # Import here to avoid circular imports
            from banditgui.utils import get_level_info
            level_data = get_level_info(level_num)
            if not level_data:
                logger.error(f"Could not load information for level {level_num}")
                return f"Could not load information for level {level_num}."

            # Format the level information for display in the terminal
            result = f"\n=== LEVEL {level_num} ===\n\n"

            # Add the level goal
            if level_data.get('goal'):
                result += "LEVEL GOAL:\n" + level_data['goal'] + "\n\n"

            # Add the commands
            if level_data.get('commands'):
                result += "COMMANDS YOU MAY NEED:\n" + level_data['commands'] + "\n\n"

            # Add the helpful reading material
            if level_data.get('reading'):
                result += "HELPFUL READING MATERIAL:\n" + level_data['reading'] + "\n"

            logger.info(f"Retrieved information for level {level_num}")
            return result
        except ValueError:
            logger.warning(f"Invalid level number: {args[0]}")
            return f"Invalid level number: {args[0]}. Please provide a valid number."
        except Exception as e:
            logger.error(f"Error loading level information: {e}")
            return f"Error loading level information: {str(e)}"

    def general_command(self, args: List[str]) -> str:
        """
        Display general information about the Bandit wargame.

        Args:
            args: Command arguments

        Returns:
            str: General information
        """
        logger.debug("Executing general command")
        try:
            # Import here to avoid circular imports
            from banditgui.utils import get_general_info
            general_data = get_general_info()
            if not general_data:
                logger.error("Could not load general information")
                return "Could not load general information about the Bandit wargame."

            # Format the general information for display in the terminal
            result = "\n=== BANDIT WARGAME ===\n\n"
            result += general_data.get('general', '')

            logger.info("Retrieved general information")
            return result
        except Exception as e:
            logger.error(f"Error loading general information: {e}")
            return f"Error loading general information: {str(e)}"

    def connect_command(self, args: List[str]) -> str:
        """
        Connect to the SSH server.

        Args:
            args: Command arguments

        Returns:
            str: Connection result
        """
        logger.debug("Executing connect command")
        try:
            if not self.ssh_manager:
                logger.error("SSH manager not initialized")
                return "Error: SSH manager not initialized"

            result = self.ssh_manager.connect()
            if result is True:
                logger.info("Successfully connected to SSH server")
                self.ssh_connected = True
                # Set initial level to 0
                self.current_level = 0
                return "Successfully connected to SSH server."
            else:
                logger.error(f"Failed to connect to SSH server: {result}")
                return f"Failed to connect to SSH server: {result}"
        except Exception as e:
            logger.error(f"Error connecting to SSH server: {e}")
            return f"Error connecting to SSH server: {str(e)}"
