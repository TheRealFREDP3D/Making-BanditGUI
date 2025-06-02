"""Main Flask application for BanditGUI.

This module initializes the Flask application and defines the API routes.
"""

import os
import sys

from flask import Flask, jsonify, render_template, request, send_from_directory
from litellm import completion # Added for Ask-a-Pro

from banditgui.chat.chat_manager import ChatManager
from banditgui.config.logging import get_logger, setup_logging

# Initialize configuration and logging
from banditgui.config.settings import config
from banditgui.ssh.ssh_manager import SSHManager
from banditgui.terminal.terminal_manager import TerminalManager
from banditgui.utils.quotes import get_random_quote, get_terminal_welcome_quotes

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
        return jsonify({'status': 'success', 'serverStatus': status})
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
        return jsonify({
            'status': 'success',
            'message': 'Disconnected from SSH server'
        })
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


@app.route('/config/<path:filename>')
def serve_config_json(filename):
    logger.debug(f"Serving config JSON file: {filename}")
    # Ensure the path is safe and only serves expected files
    if filename == "llm_model.json":
        # 'config' is relative to app.root_path, which is 'banditgui/'
        return send_from_directory('config', filename, mimetype='application/json')
    else:
        return jsonify({"status": "error", "message": "File not found"}), 404


@app.route('/ask-a-pro', methods=['POST'])
def ask_a_pro():
    data = request.json
    selected_llm_value = data.get('llm') # e.g., "openai/gpt-4o"
    level_name = data.get('level_name')
    level_description = data.get('level_description')
    command_history_list = data.get('command_history', [])

    # Basic validation
    if not all([selected_llm_value, level_name is not None, level_description]): # level_name can be 0
        logger.warning("Ask-a-Pro request missing required data.")
        return jsonify({'status': 'error', 'message': 'Missing required data for Ask-a-Pro.'}), 400

    command_history_str = "\n".join([f"- {cmd}" for cmd in command_history_list])

    prompt_template = f"""
You are an expert mentor assisting a CTF or security challenge participant. The user is currently on a specific level, and has executed the following commands so far.

Goal: Help them understand their current situation. Provide some technical explanation, suggest a direction or next step, and recommend a resource to learn more. Never reveal the full solution. Keep it constructive and educational.

---

📍 Level Name: {level_name}
🧩 Level Description: {level_description}
📜 Command History:
{command_history_str if command_history_str else "No commands executed yet."}

---

🎓 Based on this, summarize what's going on, explain any key concepts, suggest something to try next, and link to a learning resource (like a man page, article, or tool documentation). The user should walk away more informed, but not with the answer directly.
    """

    logger.debug(f"Ask-a-Pro prompt constructed for LLM: {selected_llm_value}")
    # logger.debug(f"Prompt content:\n{prompt_template}") # Uncomment for debugging prompt

    try:
        model_parts = selected_llm_value.split('/', 1)
        provider = model_parts[0]
        
        # Default model_name_for_api to the full value, adjust as needed
        model_name_for_api = selected_llm_value 

        api_key = None
        # API Key resolution based on provider
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            # model_name_for_api is already correct e.g. "openai/gpt-4o" or "gpt-4o" if litellm handles it
        elif provider == "gemini":
            model_name_for_api = selected_llm_value # e.g. "gemini/gemini-1.5-pro"
            api_key = os.getenv("GEMINI_API_KEY")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            # model_name_for_api for anthropic is often just the model name e.g. "claude-3-opus-20240229"
            # but llm_model.json has "claude-3-opus", litellm might prepend "anthropic/" or handle it.
            # For safety, pass the full selected_llm_value if it includes provider, else construct.
        elif provider == "cohere":
            api_key = os.getenv("COHERE_API_KEY")
        elif provider == "mistral":
            api_key = os.getenv("MISTRAL_API_KEY")
            # model_name_for_api = f"mistral/{model_parts[1]}" if len(model_parts) > 1 else f"mistral/{provider}"
        elif provider == "perplexity":
            api_key = os.getenv("PERPLEXITY_API_KEY")
        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
        elif provider == "openrouter":
            model_name_for_api = f"openrouter/{model_parts[1]}" if len(model_parts) > 1 else f"openrouter/{provider}"
            api_key = os.getenv("OPENROUTER_API_KEY")
        elif provider == "ollama":
            model_name_for_api = f"ollama/{model_parts[1]}" if len(model_parts) > 1 else f"ollama/{provider}"
            # OLLAMA_BASE_URL should be set in .env for LiteLLM to pick up.
            # api_key is typically not needed for local Ollama.
            pass

        # Check for API key after specific provider logic
        if not api_key and provider not in ["ollama"] and not os.getenv(f"{provider.upper()}_API_KEY"):
             # Fallback for providers where API key might be named like PROVIDER_API_KEY but not explicitly handled above
            api_key = os.getenv(f"{provider.upper()}_API_KEY")

        if not api_key and provider not in ["ollama"]:
            logger.error(f"API key for {provider} is not set. Looked for {provider.upper()}_API_KEY.")
            return jsonify({'status': 'error', 'message': f'API key for {provider} not configured on server.'}), 500
        
        messages_for_llm = [{"role": "user", "content": prompt_template}]
        
        logger.info(f"Sending request to LiteLLM with model: {model_name_for_api} for provider {provider}")

        response = completion(
            model=model_name_for_api, #This should be like "gpt-3.5-turbo" or "ollama/llama2" or "gemini/gemini-pro"
            messages=messages_for_llm,
            api_key=api_key, # Pass None if not needed (e.g. Ollama)
            # For some providers like Azure, custom_llm_provider might be needed.
            # LiteLLM usually infers provider from model name string.
        )
        
        advice = response.choices[0].message.content
        logger.info(f"Received advice from LLM: {advice[:100]}...")
        return jsonify({'status': 'success', 'advice': advice})

    except NameError as e: # Specifically catch if 'completion' is not defined
        if 'completion' in str(e):
            logger.error("LiteLLM is likely not installed. Please add 'litellm' to requirements.txt and install it.")
            return jsonify({'status': 'error', 'message': 'LLM integration library (LiteLLM) not available on server. Please install dependencies.'}), 500
        else:
            error_msg = f"Unexpected NameError: {str(e)}"
            logger.error(error_msg)
            return jsonify({'status': 'error', 'message': error_msg}), 500
    except Exception as e:
        error_msg = f"Error calling LLM: {str(e)}"
        logger.error(error_msg, exc_info=True) # Log full traceback for other errors
        return jsonify({'status': 'error', 'message': error_msg}), 500


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
            return jsonify({'status': 'success', 'levelInfo': level_data})
        else:
            logger.warning(f"Level info not found for level {level}")
            return jsonify({
                'status': 'error',
                'message': f'Level {level} information not found'
            })
    except Exception as e:
        error_msg = f"Error retrieving level info: {str(e)}"
        logger.error(error_msg)
        return jsonify({'status': 'error', 'message': error_msg})


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

    return jsonify({'status': 'success', 'message': 'Message added'})


@app.route('/chat/messages', methods=['GET'])
def get_chat_messages():
    """Get chat messages."""
    level = request.args.get('level')
    count = request.args.get('count', 50, type=int)

    level = int(level) if level and level.isdigit() else None
    logger.info(f"Getting chat messages for level {level}")
    messages = chat_manager.get_messages(level, count)

    return jsonify({'status': 'success', 'messages': messages})


@app.route('/chat/hint', methods=['POST'])
def get_hint():
    """Get a hint for the current level."""
    level = request.json.get('level')

    if not isinstance(level, int):
        logger.warning("Hint request with invalid level")
        return jsonify({
            'status': 'error',
            'message': 'Invalid level provided'
        })

    logger.info(f"Getting hint for level {level}")
    hint = chat_manager.get_hint(level)

    # Add the hint as a system message
    chat_manager.add_message(hint, level, is_system=True)

    return jsonify({'status': 'success', 'hint': hint})


@app.route('/quotes/random', methods=['GET'])
def random_quote():
    """Get a random geek quote."""
    logger.debug("Getting random quote")
    try:
        quote = get_random_quote()
        return jsonify({'status': 'success', 'quote': quote})
    except Exception as e:
        error_msg = f"Error getting random quote: {str(e)}"
        logger.error(error_msg)
        return jsonify({'status': 'error', 'message': error_msg})


@app.route('/quotes/welcome', methods=['GET'])
def welcome_quotes():
    """Get quotes for terminal welcome message."""
    count = request.args.get('count', 3, type=int)
    logger.debug(f"Getting {count} welcome quotes")
    try:
        quotes = get_terminal_welcome_quotes(count)
        return jsonify({'status': 'success', 'quotes': quotes})
    except Exception as e:
        error_msg = f"Error getting welcome quotes: {str(e)}"
        logger.error(error_msg)
        return jsonify({'status': 'error', 'message': error_msg})


def main():
    """Run the Flask application."""
    # Validate configuration
    validation_error = config.validate()
    if validation_error:
        logger.error(f"Configuration error: {validation_error}")
        sys.exit(1)

    # Run the Flask app
    logger.info(f"Starting Flask app on {config.host}:{config.port}")
    app.run(debug=config.debug, host=config.host, port=config.port)


if __name__ == "__main__":
    main()
