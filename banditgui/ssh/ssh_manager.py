"""
SSH Manager for BanditGUI.

This module provides functionality for connecting to and interacting with SSH servers.
"""

import socket
from typing import Any, Dict, Union

import paramiko

from banditgui.config.logging import get_logger
from banditgui.config.settings import config

logger = get_logger('ssh.ssh_manager')


class SSHManager:
    """
    Manager for SSH connections and command execution.
    """

    def __init__(self):
        """Initialize the SSH manager."""
        self.client = None
        logger.debug("SSHManager initialized")

    def connect(self) -> Union[bool, str]:
        """
        Connect to the SSH server using the configured settings.

        Returns:
            Union[bool, str]: True if connection successful, error message otherwise
        """
        try:
            logger.info(f"Connecting to SSH server {config.ssh_host}:{config.ssh_port}")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=config.ssh_host,
                port=config.ssh_port,
                username=config.ssh_username,
                password=config.ssh_password
            )
            logger.info("Successfully connected to SSH server")
            return True
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            error_msg = f"Unable to connect to SSH server: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except paramiko.SSHException as e:
            error_msg = f"SSH error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def execute_command(self, command: str) -> str:
        """
        Execute a command on the SSH server.

        Args:
            command: The command to execute

        Returns:
            str: The command output or error message
        """
        try:
            # If not connected and this is an SSH command, try to connect first
            if not self.client and command.strip().lower().startswith('ssh'):
                logger.info("Auto-connecting for SSH command")
                connect_result = self.connect()
                if connect_result is not True:
                    error_msg = f"Failed to connect to SSH server: {connect_result}"
                    logger.error(error_msg)
                    return error_msg
            elif not self.client:
                error_msg = "Not connected to SSH server. As HAL 9000 would say: 'I'm sorry Dave, I'm afraid I can't do that until you connect.'"
                logger.error(error_msg)
                return error_msg

            logger.info(f"Executing SSH command: {command}")
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                logger.warning(f"Command produced error output: {error}")

            result = output if output else error
            logger.debug(f"Command result: {result[:100]}...")
            return result
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def close(self) -> None:
        """Close the SSH connection."""
        if self.client:
            logger.info("Closing SSH connection")
            self.client.close()
            self.client = None

    def check_server_status(self) -> Dict[str, Any]:
        """
        Check if the SSH server is online.

        Returns:
            Dict[str, Any]: Server status information
        """
        try:
            # Create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set a timeout
            s.settimeout(2)
            # Try to connect
            result = s.connect_ex((config.ssh_host, config.ssh_port))
            # Close the socket
            s.close()

            # Check if the connection was successful
            if result == 0:
                logger.info(f"Server {config.ssh_host}:{config.ssh_port} is online")
                return {
                    'status': 'online',
                    'host': config.ssh_host,
                    'port': config.ssh_port
                }
            else:
                logger.warning(f"Server {config.ssh_host}:{config.ssh_port} is offline")
                return {
                    'status': 'offline',
                    'host': config.ssh_host,
                    'port': config.ssh_port,
                    'error': f"Connection failed with error code {result}"
                }
        except Exception as e:
            logger.error(f"Error checking server status: {str(e)}")
            return {
                'status': 'error',
                'host': config.ssh_host,
                'port': config.ssh_port,
                'error': str(e)
            }
