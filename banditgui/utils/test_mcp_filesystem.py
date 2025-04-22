#!/usr/bin/env python3
"""
Test script for MCP filesystem server.

This script demonstrates how to interact with the MCP filesystem server
by listing files and directories in the current directory.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def start_mcp_server():
    """Start the MCP filesystem server as a subprocess."""
    # Get the project root directory (parent of the utils directory)
    project_root = Path(__file__).parent.parent

    # Use shell=True on Windows to find npx in PATH
    if sys.platform == 'win32':
        cmd = "npx @modelcontextprotocol/server-filesystem ."
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            cwd=str(project_root)
        )
    else:
        process = subprocess.Popen(
            ["npx", "@modelcontextprotocol/server-filesystem", str(project_root)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root)
        )
    # Wait a moment for the server to start
    time.sleep(2)
    return process

def stop_mcp_server(process):
    """Stop the MCP filesystem server."""
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

def list_directory(path="."):
    """List files and directories in the specified path."""
    # Convert path to absolute path if it's relative
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    files = []
    dirs = []

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            dirs.append(item)
        else:
            files.append(item)

    return {
        "directories": dirs,
        "files": files
    }

def main():
    """Main function to test the MCP filesystem server."""
    print("Testing MCP filesystem server...")

    # Start the MCP server
    server_process = start_mcp_server()

    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent

        # List files in the project root directory
        result = list_directory(project_root)

        # Print the results
        print(f"\nProject root: {project_root}")

        print("\nDirectories:")
        for dir_name in sorted(result["directories"]):
            print(f"  - {dir_name}")

        print("\nFiles:")
        for file_name in sorted(result["files"]):
            print(f"  - {file_name}")

        # Also list files in the utils directory
        utils_dir = project_root / "utils"
        utils_result = list_directory(utils_dir)

        print(f"\nUtils directory: {utils_dir}")

        print("\nDirectories:")
        for dir_name in sorted(utils_result["directories"]):
            print(f"  - {dir_name}")

        print("\nFiles:")
        for file_name in sorted(utils_result["files"]):
            print(f"  - {file_name}")

        print("\nMCP filesystem server test completed successfully!")

    finally:
        # Stop the MCP server
        stop_mcp_server(server_process)

if __name__ == "__main__":
    main()
