"""
Chat Manager for BanditGUI.

This module provides functionality for handling chat interactions and messages.
"""

from typing import Dict, List, Optional

from banditgui.config.logging import get_logger

logger = get_logger('chat.chat_manager')


class ChatManager:
    """
    Manager for chat interactions and messages.
    """

    def __init__(self):
        """Initialize the chat manager."""
        self.messages = []
        self.chat_history = {}  # Dictionary to store chat history by level
        self.current_level = None
        logger.debug("ChatManager initialized")

    def add_message(self, message: str, level: Optional[int] = None, is_system: bool = False) -> None:
        """
        Add a message to the chat history.

        Args:
            message: The message content
            level: The level associated with the message (if any)
            is_system: Whether this is a system message
        """
        if not message:
            logger.debug("Empty message provided to ChatManager.add_message; no action taken.")
            return

        # Use current level if none specified
        if level is None:
            level = self.current_level

        # Create message object
        msg_obj = {
            'content': message,
            'level': level,
            'is_system': is_system,
            'timestamp': self._get_timestamp()
        }

        # Add to current messages list
        self.messages.append(msg_obj)

        # Add to level-specific history if level is specified
        if level is not None:
            if level not in self.chat_history:
                self.chat_history[level] = []
            self.chat_history[level].append(msg_obj)

        logger.debug(f"Added {'system' if is_system else 'user'} message for level {level}")

    def get_messages(self, level: Optional[int] = None, count: int = 50) -> List[Dict]:
        """
        Get recent messages, optionally filtered by level.

        Args:
            level: The level to filter messages by (if None, returns all messages)
            count: Maximum number of messages to return

        Returns:
            List[Dict]: List of message objects
        """
        messages = self.messages if level is None else self.chat_history.get(level, [])
        # Return the most recent messages up to count
        return messages[-count:] if messages else []

    def set_current_level(self, level: Optional[int]) -> None:
        """
        Set the current level for chat context.

        Args:
            level: The current level
        """
        self.current_level = level
        logger.info(f"Chat context set to level {level}")

        # Add a system message when changing levels
        if level is not None:
            self.add_message(f"Switched to level {level}", level=level, is_system=True)

    def clear_messages(self, level: Optional[int] = None) -> None:
        """
        Clear messages, optionally only for a specific level.

        Args:
            level: The level to clear messages for (if None, clears all messages)
        """
        if level is not None:
            # Clear only messages for the specified level
            if level in self.chat_history:
                self.chat_history[level] = []
                logger.info(f"Cleared messages for level {level}")
            
            # Also remove these messages from the main messages list
            self.messages = [msg for msg in self.messages if msg.get('level') != level]
        else:
            # Clear all messages
            self.messages = []
            self.chat_history = {}
            logger.info("Cleared all messages")

    def get_hint(self, level: int) -> str:
        """
        Get a hint for the specified level.

        Args:
            level: The level to get a hint for

        Returns:
            str: A hint for the level
        """
        # This is a placeholder - in a real implementation, hints would be loaded from a database or file
        hints = {
            0: "Try using the 'ls' command to list files, and 'cat' to read file contents.",
            1: "Look for hidden files using 'ls -la'. Files starting with a dot are hidden.",
            2: "Spaces in filenames can be tricky. Use quotes or escape the spaces with backslashes.",
            3: "Files can have special characters. Try using tab completion to help with filenames.",
            4: "Some files might be hidden in directories. Use 'find' to search recursively.",
            5: "Check file permissions with 'ls -l'. You might need to use 'chmod' to change them.",
        }
        
        hint = hints.get(level, "No hint available for this level.")
        logger.info(f"Provided hint for level {level}")
        return hint

    def _get_timestamp(self) -> str:
        """
        Get the current timestamp in a readable format.

        Returns:
            str: Formatted timestamp
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
