"""Main Flask application for BanditGUI.

This module initializes the Flask application and defines the API routes.
"""

import os
import sys

from flask import Flask, jsonify, render_template, request, send_from_directory

from banditgui.chat.chat_manager import ChatManager
from banditgui.config.logging import get_logger, setup_logging

# Initialize configuration and logging
from banditgui.config.settings import config
from banditgui.ssh.ssh_manager import SSHManager
from banditgui.terminal.terminal_manager import TerminalManager

# Set up logging
setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger('app')

# Initialize Flask app
app = Flask(__name__)

# Initialize managers
ssh_manager = SSHManager()
terminal_manager = TerminalManager(ssh_manager=ssh_manager)
chat_manager = ChatManager()

logger.info("BanditGUI application initialized")


@app.route("/")
def home():
    """Render the home page."""
    logger.debug("Rendering home page")
    return render_template("index.html")


@app.route('/server-status', methods=['GET'])
def server_status():
    """Check the status of the SSH server."""
    logger.info("Checking server status")
    try:
        status = ssh_manager.check_server_status()
        logger.info(f"Server status: {status['status']}")
        return jsonify({
            'status': 'success',
            'serverStatus': status
        })
    except Exception as e:
        error_msg = f"Error checking server status: {str(e)}"
        logger.error(error_msg)
        return jsonify({'status': 'error', 'message': error_msg})


@app.route('/connect', methods=['POST'])
def connect():
    """Connect to the SSH server."""
    logger.info("Received connect request")
    try:
        result = ssh_manager.connect()
        if result is True:
            logger.info("SSH connection successful")
            # Set the current level to 0 (initial level)
            terminal_manager.current_level = 0
            return jsonify({
                'status': 'success',
                'message': 'Connected to SSH server',
                'currentLevel': terminal_manager.current_level
            })
        logger.error(f"SSH connection failed: {result}")
        return jsonify({'status': 'error', 'message': result})
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"Exception during SSH connection: {error_msg}")
        return jsonify({'status': 'error', 'message': error_msg})


@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Disconnect from the SSH server."""
    logger.info("Received disconnect request")
    try:
        ssh_manager.close()
        terminal_manager.ssh_connected = False
        terminal_manager.current_level = None
        logger.info("SSH connection closed")
        return jsonify({'status': 'success', 'message': 'Disconnected from SSH server'})
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"Exception during SSH disconnection: {error_msg}")
        return jsonify({'status': 'error', 'message': error_msg})


@app.route('/execute', methods=['POST'])
def execute():
    """Execute a command."""
    command = request.json.get('command')
    if not command:
        logger.warning("Execute request with no command")
        return jsonify({'status': 'error', 'message': 'No command provided'})

    logger.info(f"Executing command: {command}")
    output = terminal_manager.execute_command(command)

    if output == "<clear>":
        logger.debug("Clear command executed")
        return jsonify({'status': 'clear'})

    # Check if this is a level change command (like ssh bandit1@bandit.labs.overthewire.org)
    # Parse SSH commands to detect level changes
    if command.startswith('ssh bandit') and '@' in command:
        try:
            # Extract the level number from the command
            level_part = command.split('bandit')[1].split('@')[0]
            new_level = int(level_part)
            terminal_manager.current_level = new_level
            logger.info(f"Level changed to {new_level}")
        except (ValueError, IndexError):
            # If we can't parse the level, ignore it
            pass

    # Process output to handle ANSI color codes for xterm.js
    # xterm.js can handle ANSI color codes directly, so we don't need to convert them
    logger.debug(f"Command executed, output length: {len(output)}")
    return jsonify({
        'status': 'success',
        'output': output,
        'currentLevel': terminal_manager.current_level
    })


@app.route('/static/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files."""
    logger.debug(f"Serving JS file: {filename}")
    return send_from_directory('static/js', filename)


@app.route('/level-info', methods=['POST'])
def level_info():
    """Get information about a specific level."""
    level = request.json.get('level', 0)
    logger.info(f"Requested level info for level {level}")

    try:
        from banditgui.utils.level_info import get_level_info
        level_data = get_level_info(level)

        if level_data:
            logger.debug(f"Found level info for level {level}")
            return jsonify({
                'status': 'success',
                'levelInfo': level_data
            })
        else:
            logger.warning(f"Level info not found for level {level}")
            return jsonify({
                'status': 'error',
                'message': f'Level {level} information not found'
            })
    except Exception as e:
        error_msg = f"Error retrieving level info: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        })


@app.route('/chat/message', methods=['POST'])
def chat_message():
    """Add a message to the chat."""
    message = request.json.get('message')
    level = request.json.get('level')
    try:
        level = int(level)
    except (ValueError, TypeError):
        logger.warning("Invalid level value provided in chat message")
        return jsonify({'status': 'error', 'message': 'Invalid level value'})
    is_system = request.json.get('isSystem', False)

    if not message:
        logger.warning("Chat message request with no message")
        return jsonify({'status': 'error', 'message': 'No message provided'})

    logger.info(f"Adding chat message for level {level}")
    chat_manager.add_message(message, level, is_system)

    return jsonify({
        'status': 'success',
        'message': 'Message added'
    })


@app.route('/chat/messages', methods=['GET'])
def get_chat_messages():
    """Get chat messages."""
    level = request.args.get('level')
    count = request.args.get('count', 50, type=int)

    if level and level.isdigit():
        level = int(level)
    else:
        level = None

    logger.info(f"Getting chat messages for level {level}")
    messages = chat_manager.get_messages(level, count)

    return jsonify({
        'status': 'success',
        'messages': messages
    })


@app.route('/chat/hint', methods=['POST'])
def get_hint():
    """Get a hint for the current level."""
    level = request.json.get('level')

    if not isinstance(level, int):
        logger.warning("Hint request with invalid level")
        return jsonify({'status': 'error', 'message': 'Invalid level provided'})
        logger.warning("Hint request with no level")
        return jsonify({'status': 'error', 'message': 'No level provided'})

    logger.info(f"Getting hint for level {level}")
    hint = chat_manager.get_hint(level)

    # Add the hint as a system message
    chat_manager.add_message(hint, level, is_system=True)

    return jsonify({
        'status': 'success',
        'hint': hint
    })


def main():
    """Run the Flask application."""
    # Validate configuration
    validation_error = config.validate()
    if validation_error:
        logger.error(f"Configuration error: {validation_error}")
        sys.exit(1)

    # Run the Flask app
    logger.info(f"Starting Flask app on {config.host}:{config.port}")
    app.run(
        debug=config.debug,
        host=config.host,
        port=config.port
    )


if __name__ == "__main__":
    main()
