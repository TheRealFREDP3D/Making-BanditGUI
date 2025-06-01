"""
Configuration settings for BanditGUI.

This module handles loading and validating configuration from environment variables.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for BanditGUI."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()

        # SSH settings
        self.ssh_host = os.getenv('SSH_HOST', 'bandit.labs.overthewire.org')
        self.ssh_port = int(os.getenv('SSH_PORT', '2220'))
        self.ssh_username = os.getenv('SSH_USERNAME', 'bandit0')
        self.ssh_password = os.getenv('SSH_PASSWORD', 'bandit0')

        # LLM API Keys and Settings
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        self.ollama_base_url: Optional[str] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        self.preferred_llm_provider: str = os.getenv("PREFERRED_LLM_PROVIDER", "gemini")
        self.preferred_llm_model: str = os.getenv("PREFERRED_LLM_MODEL", "gemini-1.5-flash-latest")

        # Flask settings
        self.debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
        self.host = os.getenv('HOST', '127.0.0.1')
        self.port = int(os.getenv('PORT', '5000'))

    def get_ssh_config(self) -> Dict[str, Any]:
        """
        Get SSH configuration as a dictionary.

        Returns:
            Dict[str, Any]: SSH configuration
        """
        return {
            'hostname': self.ssh_host,
            'port': self.ssh_port,
            'username': self.ssh_username,
            'password': self.ssh_password
        }

    def get_flask_config(self) -> Dict[str, Any]:
        """
        Get Flask configuration as a dictionary.

        Returns:
            Dict[str, Any]: Flask configuration
        """
        return {
            'DEBUG': self.debug,
            'HOST': self.host,
            'PORT': self.port
        }

    def validate(self) -> Optional[str]:
        """
        Validate the configuration.

        Returns:
            Optional[str]: Error message if validation fails, None otherwise
        """
        # Check if SSH host is set
        if not self.ssh_host:
            return "SSH_HOST is not set"

        # Check if SSH port is valid
        if not isinstance(self.ssh_port, int) or self.ssh_port <= 0:
            return f"Invalid SSH_PORT: {self.ssh_port}"

        # Check if SSH username is set
        if not self.ssh_username:
            return "SSH_USERNAME is not set"

        # Check if SSH password is set
        if not self.ssh_password:
            return "SSH_PASSWORD is not set"

        return None


# Create a singleton instance
config = Config()
