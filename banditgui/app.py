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
from banditgui.utils.level_info import get_level_info
from banditgui.utils.quotes import get_random_quote, get_terminal_welcome_quotes

# Set up logging
setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger('app')

import litellm
import os

# Initialize Flask app
app = Flask(__name__)

# --- Predefined LLM Models by Provider ---
PREDEFINED_MODELS = {
    "openai": [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4o"
    ],
    "gemini": [ # Google AI Studio models
        "gemini-pro",
        "gemini-1.0-pro",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest"
    ],
    "openrouter": [ # Examples, many more available on OpenRouter
        "anthropic/claude-3-haiku",
        "anthropic/claude-2",
        "google/gemini-pro-1.5", # Note: OpenRouter might have different naming
        "mistralai/mistral-7b-instruct",
        "openai/gpt-3.5-turbo", # OpenRouter can proxy models
        "openrouter/cinematika-7b" # Example of an OpenRouter specific model
    ],
    "ollama": [ # Common models users might have pulled with Ollama
        "mistral",
        "llama2",
        "llama3",
        "codellama",
        "phi",
        "nous-hermes2"
    ]
}

# Define LLM System Persona
LLM_SYSTEM_PROMPT = """
You are "The Old Pro," a wise, ancient mentor guiding users through the OverTheWire Bandit wargame.
Your persona is supportive, never patronizing. You are proud of the user's progress, no matter how small.
You encourage curiosity, critical thinking, and independent problem-solving.
Your responses should sometimes be philosophical or poetic, reflecting your vast experience.

When a user asks for help:
1.  Acknowledge their current situation based on the level and terminal history provided.
2.  Provide hints, not direct answers. Focus on guiding them towards the solution.
3.  If their terminal history shows common mistakes or misconceptions, gently point them out and explain why it might be a wrong path, or suggest a better way to think about it.
4.  Suggest relevant commands, man pages (e.g., "Perhaps `man find` holds a clue"), or learning resources.
5.  Employ a progressive help approach. If this is their first request for this specific issue, be more vague and conceptual. If they were to ask again (though this interaction is single-turn for now), you would become slightly more specific.
6.  CRUCIALLY: NEVER reveal the full solution, the password, or the flag for any level. Your goal is to help them learn, not to give them the answers.
7.  Maintain your persona: be encouraging, a bit grandiloquent, and wise.

Example tone:
"Ah, young seeker of truth... I see you’ve invoked `ls`, yet overlooked the shadows cast by hidden files. In the dark corners of directories, secrets often hide. Reflect on what the `-a` flag might reveal to the observant eye..."
"The path to knowledge is paved with experimentation. You've tried `cat` on a directory – a noble attempt! But `cat` is for displaying the contents of files. Directories are like signposts; perhaps `ls` would better reveal the paths within?"
"Patience, young one. The answer you seek is not always where you first look. Consider the properties of the file you found. What does `file` tell you about its nature? Some files are not what they seem."
"""

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


@app.route('/ask_a_pro', methods=['POST'])
def ask_a_pro():
    """
    Construct a prompt for the LLM based on current level, objectives, and command history,
    allowing for dynamic provider and model selection.
    """
    logger.info("Received request for 'Ask a Pro'")

    request_data = request.get_json()
    if not request_data: # Ensure request_data is not None
        request_data = {}

    provider = request_data.get("provider", config.preferred_llm_provider).lower()
    model_name = request_data.get("model", config.preferred_llm_model)

    logger.info(f"Ask a Pro request using provider: {provider}, model: {model_name}")

    api_key = None
    litellm_model_string = model_name # Default to model_name
    litellm_kwargs = {}

    if provider == "openai":
        api_key = config.openai_api_key
        if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE":
            logger.error("OpenAI API key not configured.")
            return jsonify({'status': 'error', 'message': 'OpenAI API key not configured by the administrator.'}), 503
    elif provider == "gemini":
        api_key = config.gemini_api_key
        # Gemini model names via LiteLLM are often just the model name like "gemini-pro"
        # but sometimes "gemini/gemini-pro". For user input `model_name` should be direct.
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            logger.error("Gemini API key not configured.")
            return jsonify({'status': 'error', 'message': 'Gemini API key not configured by the administrator.'}), 503
    elif provider == "openrouter":
        api_key = config.openrouter_api_key
        litellm_model_string = f"openrouter/{model_name}"
        if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
            logger.error("OpenRouter API key not configured.")
            return jsonify({'status': 'error', 'message': 'OpenRouter API key not configured by the administrator.'}), 503
    elif provider == "ollama":
        # Ollama typically doesn't require an API key for local instances.
        # The model string for ollama is just the model name, e.g., "llama2"
        # We need to pass api_base for Ollama.
        litellm_kwargs["api_base"] = config.ollama_base_url
        logger.info(f"Using Ollama with API base: {config.ollama_base_url} and model: {model_name}")
    else:
        logger.error(f"Unsupported LLM provider: {provider}")
        return jsonify({'status': 'error', 'message': f"Unsupported LLM provider: {provider}. Supported providers: openai, gemini, openrouter, ollama."}), 400

    # This general check is useful if a provider is somehow selected without a specific key check above,
    # or if we want a default behavior for providers that DO need keys but aren't explicitly OpenAI/Gemini/OpenRouter.
    # However, for Ollama, api_key can be None.
    if provider != "ollama" and not api_key:
        logger.error(f"API key for selected provider '{provider}' is missing, and it's not Ollama.")
        # This specific message might be redundant due to earlier checks but acts as a fallback.
        return jsonify({'status': 'error', 'message': f"API key for provider '{provider}' is not configured or missing."}), 503

    current_level = terminal_manager.current_level
    level_goal = "Not available"
    level_data = None

    if current_level is None:
        logger.warning("'Ask a Pro' requested but not connected to any level.")
        # Allow proceeding, LLM can be informed that level is unknown.

    if current_level is not None:
        try:
            level_data = get_level_info(current_level)
            if level_data and 'goal' in level_data:
                level_goal = level_data['goal']
                logger.info(f"Retrieved goal for level {current_level}: {level_goal}")
            else:
                logger.warning(f"Could not retrieve goal for level {current_level}. Level data: {level_data}")
        except Exception as e:
            logger.error(f"Error retrieving level info for level {current_level}: {e}")
            # Fallback, level_goal remains "Not available"

    command_history = terminal_manager.get_command_history()
    recent_history = command_history[-15:] # Use last 15 commands
    history_str = "\n".join(recent_history)

    user_context_prompt_lines = [
        f"Current Level: {current_level if current_level is not None else 'Unknown (not formally connected to a level)'}",
        f"Level Objectives: {level_goal}",
        "---",
        "Recent Terminal History (last 15 commands):",
        history_str if history_str else "No commands in history yet.",
        "---",
        "Please provide a hint based on this context."
    ]
    user_context_prompt = "\n".join(user_context_prompt_lines)

    logger.debug(f"User context prompt for LLM:\n{user_context_prompt}")

    messages = [
        {"role": "system", "content": LLM_SYSTEM_PROMPT},
        {"role": "user", "content": user_context_prompt}
    ]

    try:
        # Ensure OPENAI_API_KEY is set if that's the intended provider and llm_api_key is for it.
        # For other providers, litellm might need different env vars or config.
    # Set environment variables for providers that might primarily rely on them,
    # though litellm.completion parameters usually take precedence.
    # This is more of a fallback or for complex litellm routing/proxy setups.
    if config.openai_api_key and config.openai_api_key != "YOUR_OPENAI_API_KEY_HERE":
        os.environ["OPENAI_API_KEY"] = config.openai_api_key
    if config.gemini_api_key and config.gemini_api_key != "YOUR_GEMINI_API_KEY_HERE":
        os.environ["GEMINI_API_KEY"] = config.gemini_api_key # Or GOOGLE_API_KEY depending on litellm version/usage
    if config.openrouter_api_key and config.openrouter_api_key != "YOUR_OPENROUTER_API_KEY_HERE":
        os.environ["OPENROUTER_API_KEY"] = config.openrouter_api_key

    litellm_kwargs["model"] = litellm_model_string
    litellm_kwargs["messages"] = messages
    if api_key: # Only pass api_key if it's set (Ollama doesn't need it)
        litellm_kwargs["api_key"] = api_key
    litellm_kwargs["temperature"] = 0.7
    litellm_kwargs["max_tokens"] = 300

    response = litellm.completion(**litellm_kwargs)
        llm_response_content = response.choices[0].message.content
    # model_actually_used = response.model # Contains the model string litellm resolved to
    logger.info(f"LLM response received successfully from provider: {provider}, model: {response.model}")
        logger.debug(f"LLM Response content:\n{llm_response_content}")

    except litellm.exceptions.AuthenticationError as e:
        logger.error(f"LiteLLM AuthenticationError for provider {provider}: {str(e)}")
        user_friendly_error = f"Authentication failed with {provider}. Please check your API key configuration."
        return jsonify({'status': 'error', 'message': user_friendly_error}), 401 # Unauthorized
    except litellm.exceptions.NotFoundException as e: # Often means model not found or endpoint incorrect
        logger.error(f"LiteLLM NotFoundException for provider {provider}, model {litellm_model_string}: {str(e)}")
        user_friendly_error = f"The selected model '{model_name}' could not be found for provider '{provider}' or the endpoint is incorrect."
        if provider == "ollama":
            user_friendly_error += f" Ensure Ollama is running, the model '{model_name}' is pulled, and the base URL '{config.ollama_base_url}' is correct."
        return jsonify({'status': 'error', 'message': user_friendly_error}), 404 # Not Found
    except litellm.exceptions.RateLimitError as e:
        logger.error(f"LiteLLM RateLimitError for provider {provider}: {str(e)}")
        user_friendly_error = f"You've exceeded your request limit for {provider}. Please try again later."
        return jsonify({'status': 'error', 'message': user_friendly_error}), 429 # Too Many Requests
    except litellm.exceptions.APIConnectionError as e: # More generic connection issues
        logger.error(f"LiteLLM APIConnectionError for provider {provider}: {str(e)}")
        user_friendly_error = f"Could not connect to {provider}."
        if provider == "ollama":
            user_friendly_error += f" Please ensure Ollama is running and accessible at '{config.ollama_base_url}'."
        else:
            user_friendly_error += " Check your network connection and the provider's status."
        return jsonify({'status': 'error', 'message': user_friendly_error}), 502 # Bad Gateway
    except Exception as e: # Catch-all for other litellm errors or unexpected issues
        error_detail = str(e)
        logger.error(f"LLM interaction failed with provider {provider} and model {litellm_model_string}: {error_detail}")

        user_friendly_error = "I seem to be having trouble reaching my sources of wisdom at the moment. Please try again shortly."
        # Check for common strings in errors that might indicate configuration issues
        if any(keyword in error_detail.lower() for keyword in ["api key", "authentication", "token", "permission"]):
             user_friendly_error = f"There appears to be an issue with the LLM configuration for {provider}. Please notify the administrator or check your API key."
        elif provider == "ollama" and any(keyword in error_detail.lower() for keyword in ["connect", "connection refused"]):
             user_friendly_error = f"Could not connect to Ollama at {config.ollama_base_url}. Please ensure Ollama is running and accessible."

        # Avoid leaking raw exception details to the client unless it's a simple message
        # For verbose errors, log them and show a generic message.
        # For this stage, str(e) is included for easier debugging by admin if they see the JSON.
        return jsonify({'status': 'error', 'message': f"Error communicating with LLM: {user_friendly_error} (Details: {str(e)})"}), 500

    return jsonify({
        'status': 'success',
        'llm_response': llm_response_content, # Changed from llm_prompt
        'current_level': current_level
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
    app.run(debug=config.debug, host=config.host, port=config.port)


@app.route('/list_llm_models', methods=['GET'])
def list_llm_models():
    """
    Return a predefined list of recommended/available models for each supported LLM provider.
    """
    logger.info("Request received for /list_llm_models")
    return jsonify({'status': 'success', 'models_by_provider': PREDEFINED_MODELS})


if __name__ == "__main__":
    main()
