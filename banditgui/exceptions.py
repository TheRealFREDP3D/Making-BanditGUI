"""
Custom exceptions for BanditGUI.
"""


class BanditGUIError(Exception):
    """Base exception for BanditGUI."""
    pass


class SSHError(BanditGUIError):
    """Exception raised for SSH-related errors."""
    pass


class SSHConnectionError(SSHError):
    """Exception raised when SSH connection fails."""
    pass


class SSHCommandError(SSHError):
    """Exception raised when SSH command execution fails."""
    pass


class ConfigError(BanditGUIError):
    """Exception raised for configuration errors."""
    pass


class LevelInfoError(BanditGUIError):
    """Exception raised for level information errors."""
    pass
