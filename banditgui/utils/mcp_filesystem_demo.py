#!/usr/bin/env python3
"""
MCP Filesystem Server Demo

This script demonstrates how to use the MCP filesystem server for various operations:
- Listing directories
- Reading files
- Writing files
- Creating directories
- Deleting files and directories
"""

import os
import subprocess
import sys
import time
from pathlib import Path


class MCPFilesystemClient:
    """Client for interacting with the MCP filesystem server."""

    def __init__(self, root_dir=None):
        """Initialize the MCP filesystem client."""
        self.server_process = None
        self.root_dir = root_dir or Path(__file__).parent.parent

    def start_server(self):
        """Start the MCP filesystem server."""
        if self.server_process:
            print("Server is already running.")
            return

        print(f"Starting MCP filesystem server for directory: {self.root_dir}")

        # Check if npx is available
        try:
            if sys.platform == 'win32':
                subprocess.run(["where", "npx"], check=True, capture_output=True, text=True)
            else:
                subprocess.run(["which", "npx"], check=True, capture_output=True, text=True)
            print("npx is available in PATH")
        except subprocess.CalledProcessError:
            print("WARNING: npx not found in PATH")

        # Use shell=True on Windows to find npx in PATH
        if sys.platform == 'win32':
            cmd = "npx @modelcontextprotocol/server-filesystem ."
            print(f"Running command: {cmd}")
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                cwd=str(self.root_dir)
            )
        else:
            cmd = ["npx", "@modelcontextprotocol/server-filesystem", str(self.root_dir)]
            print(f"Running command: {' '.join(cmd)}")
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.root_dir)
            )

        # Wait a moment for the server to start
        time.sleep(2)

        # Check if the server started successfully
        if self.server_process.poll() is not None:
            print("ERROR: MCP filesystem server failed to start")
            stdout, stderr = self.server_process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            self.server_process = None
            return

        print("MCP filesystem server started successfully.")

    def stop_server(self):
        """Stop the MCP filesystem server."""
        if not self.server_process:
            print("Server is not running.")
            return

        print("Stopping MCP filesystem server...")
        self.server_process.terminate()
        try:
            self.server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server_process.kill()

        self.server_process = None
        print("MCP filesystem server stopped.")

    def list_directory(self, path="."):
        """List files and directories in the specified path."""
        # Convert path to absolute path if it's relative
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)

        print(f"Listing directory: {path}")

        files = []
        dirs = []

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    dirs.append(item)
                else:
                    files.append(item)

            print(f"Found {len(dirs)} directories and {len(files)} files.")
            return {
                "directories": sorted(dirs),
                "files": sorted(files)
            }
        except Exception as e:
            print(f"Error listing directory: {e}")
            return {
                "directories": [],
                "files": []
            }

    def read_file(self, path):
        """Read the contents of a file."""
        # Convert path to absolute path if it's relative
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)

        print(f"Reading file: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"Successfully read {len(content)} bytes.")
            return content
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def write_file(self, path, content):
        """Write content to a file."""
        # Convert path to absolute path if it's relative
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)

        print(f"Writing to file: {path}")

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"Successfully wrote {len(content)} bytes.")
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

    def create_directory(self, path):
        """Create a directory."""
        # Convert path to absolute path if it's relative
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)

        print(f"Creating directory: {path}")

        try:
            os.makedirs(path, exist_ok=True)
            print("Directory created successfully.")
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False

    def delete_file(self, path):
        """Delete a file."""
        # Convert path to absolute path if it's relative
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)

        print(f"Deleting file: {path}")

        try:
            os.remove(path)
            print("File deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def delete_directory(self, path):
        """Delete a directory."""
        # Convert path to absolute path if it's relative
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)

        print(f"Deleting directory: {path}")

        try:
            os.rmdir(path)
            print("Directory deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting directory: {e}")
            return False

def run_demo():
    """Run a demonstration of the MCP filesystem client."""
    print("Starting MCP filesystem demo...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")

    client = MCPFilesystemClient()

    try:
        # Start the MCP filesystem server
        client.start_server()

        # List the root directory
        print("\n=== Listing Root Directory ===")
        root_contents = client.list_directory()

        print("\nDirectories:")
        for dir_name in root_contents["directories"]:
            print(f"  - {dir_name}")

        print("\nFiles:")
        for file_name in root_contents["files"]:
            print(f"  - {file_name}")

        # Create a test directory
        print("\n=== Creating Test Directory ===")
        test_dir = "mcp_test"
        client.create_directory(test_dir)

        # Create a test file
        print("\n=== Creating Test File ===")
        test_file = os.path.join(test_dir, "test.txt")
        client.write_file(test_file, "This is a test file created by the MCP filesystem demo.")

        # Read the test file
        print("\n=== Reading Test File ===")
        content = client.read_file(test_file)
        print(f"File content: {content}")

        # List the test directory
        print("\n=== Listing Test Directory ===")
        test_contents = client.list_directory(test_dir)

        print("\nFiles in test directory:")
        for file_name in test_contents["files"]:
            print(f"  - {file_name}")

        # Clean up
        print("\n=== Cleaning Up ===")
        client.delete_file(test_file)
        client.delete_directory(test_dir)

        print("\nDemo completed successfully!")

    finally:
        # Stop the MCP filesystem server
        client.stop_server()

if __name__ == "__main__":
    run_demo()
