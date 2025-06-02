import json
import os
import pytest
from banditgui.app import app as flask_app # Renamed to avoid conflict with app fixture
from unittest.mock import MagicMock # For creating mock objects for litellm response

# Make sure the app is in testing mode
flask_app.config.update({
    "TESTING": True,
})

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Ensure the app is in testing mode
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# Sample data for /ask-a-pro tests
SAMPLE_ASK_A_PRO_DATA = {
    "level_name": "0",
    "level_description": "The goal of this level is to log into the game using SSH.",
    "command_history": ["ls -la", "whoami"]
}

# Path to the llm_model.json file
LLM_MODEL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_model.json')

def test_hello_world_sanity_check(client):
    """A placeholder test to ensure the test setup is working."""
    # This is a dummy test. Replace or remove later.
    # For now, let's assume there isn't a simple '/' route that returns "Hello"
    # Let's test a known route like /server-status which is GET
    response = client.get('/server-status')
    assert response.status_code == 200 # Assuming server-status is always available and returns 200
    # This test might fail if /server-status has side effects or dependencies not mocked here.
    # It's primarily to check if client fixture works.
    # For now, we'll just check status_code.
    # A better sanity check would be a dedicated simple health check endpoint if one existed.
    pass # Will add actual tests next.

# --- Tests for /config/llm_model.json ---

def test_serve_llm_model_json_success(client):
    """Test successful serving of llm_model.json."""
    # Ensure the llm_model.json file exists for the test to read its content
    # This assumes it's in banditgui/config/llm_model.json relative to project root
    # and the test runner is executing from the project root or similar.
    
    # Create a dummy llm_model.json in the expected location for the test
    # The app route serves from 'config' relative to app.root_path (banditgui)
    config_dir = os.path.join(flask_app.root_path, 'config')
    os.makedirs(config_dir, exist_ok=True)
    dummy_llm_json_path = os.path.join(config_dir, 'llm_model.json')
    
    expected_content = {"openai": ["gpt-4o"], "ollama": ["test-model"]}
    with open(dummy_llm_json_path, 'w') as f:
        json.dump(expected_content, f)

    response = client.get('/config/llm_model.json')

    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    
    actual_data = json.loads(response.data)
    assert actual_data == expected_content
    
    # Clean up the dummy file
    os.remove(dummy_llm_json_path)

def test_serve_llm_model_json_not_found(client):
    """Test serving non-existent config file."""
    response = client.get('/config/other_file.json')
    assert response.status_code == 404
    assert response.mimetype == 'application/json' # Flask error handlers often return JSON
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert "File not found" in data['message']

# --- Tests for /ask-a-pro ---

def test_ask_a_pro_success_openai(client, mocker):
    """Test successful /ask-a-pro call with OpenAI."""
    mock_completion = mocker.patch('banditgui.app.completion')
    mock_getenv = mocker.patch('banditgui.app.os.getenv')

    mock_getenv.side_effect = lambda key: "dummy_openai_key" if key == "OPENAI_API_KEY" else None
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message = MagicMock()
    mock_llm_response.choices[0].message.content = "Mocked LLM advice for OpenAI"
    mock_completion.return_value = mock_llm_response
    
    payload = {
        "llm": "openai/gpt-4o",
        **SAMPLE_ASK_A_PRO_DATA
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['advice'] == "Mocked LLM advice for OpenAI"

    mock_getenv.assert_any_call("OPENAI_API_KEY")
    mock_completion.assert_called_once()
    args, kwargs = mock_completion.call_args
    assert kwargs['model'] == "openai/gpt-4o"
    assert kwargs['api_key'] == "dummy_openai_key"
    
    # Check prompt content (simplified check)
    prompt_arg = kwargs['messages'][0]['content']
    assert "📍 Level Name: 0" in prompt_arg
    assert "🧩 Level Description: The goal of this level is to log into the game using SSH." in prompt_arg
    assert "📜 Command History:" in prompt_arg
    assert "- ls -la" in prompt_arg
    assert "- whoami" in prompt_arg


def test_ask_a_pro_success_ollama(client, mocker):
    """Test successful /ask-a-pro call with Ollama."""
    mock_completion = mocker.patch('banditgui.app.completion')
    # No need to mock os.getenv for API key for Ollama, but OLLAMA_BASE_URL might be checked by litellm
    # We assume OLLAMA_BASE_URL is set in the environment or defaults appropriately for litellm.
    
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message = MagicMock()
    mock_llm_response.choices[0].message.content = "Mocked LLM advice for Ollama"
    mock_completion.return_value = mock_llm_response

    payload = {
        "llm": "ollama/qwen2.5-1.5b",
        **SAMPLE_ASK_A_PRO_DATA
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['advice'] == "Mocked LLM advice for Ollama"

    mock_completion.assert_called_once()
    args, kwargs = mock_completion.call_args
    assert kwargs['model'] == "ollama/qwen2.5-1.5b"
    assert kwargs['api_key'] is None


def test_ask_a_pro_api_key_missing(client, mocker):
    """Test /ask-a-pro when a required API key is missing."""
    mocker.patch('banditgui.app.completion') # Mock completion to prevent actual call
    mock_getenv = mocker.patch('banditgui.app.os.getenv')
    
    # Simulate COHERE_API_KEY not being set
    mock_getenv.side_effect = lambda key: None if key == "COHERE_API_KEY" else "some_other_key"

    payload = {
        "llm": "cohere/command-r-plus", 
        **SAMPLE_ASK_A_PRO_DATA
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 500
    assert data['status'] == 'error'
    assert "API key for cohere not configured on server" in data['message']
    mock_getenv.assert_any_call("COHERE_API_KEY")


def test_ask_a_pro_litellm_completion_error(client, mocker):
    """Test /ask-a-pro when litellm.completion raises an error."""
    mock_completion = mocker.patch('banditgui.app.completion')
    mock_getenv = mocker.patch('banditgui.app.os.getenv')

    mock_getenv.return_value = "dummy_key" # Generic key for any provider
    mock_completion.side_effect = Exception("LLM unavailable test error")

    payload = {
        "llm": "openai/gpt-3.5-turbo", 
        **SAMPLE_ASK_A_PRO_DATA
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 500
    assert data['status'] == 'error'
    assert "Error calling LLM: LLM unavailable test error" in data['message']


def test_ask_a_pro_litellm_not_installed_error(client, mocker):
    """Test /ask-a-pro when litellm is not installed (NameError)."""
    # Mock 'completion' to simulate NameError by making it not exist in the module's scope for the test
    # This is a bit tricky. A direct way is to ensure it's not imported or to mock its absence.
    # Easier: make it raise NameError.
    mocker.patch('banditgui.app.os.getenv').return_value = "dummy_key"
    mocker.patch('banditgui.app.completion', side_effect=NameError("name 'completion' is not defined"))

    payload = {
        "llm": "openai/gpt-3.5-turbo",
        **SAMPLE_ASK_A_PRO_DATA
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)
    assert response.status_code == 500
    assert data['status'] == 'error'
    assert "LLM integration library (LiteLLM) not available on server" in data['message']


def test_ask_a_pro_invalid_input_data(client):
    """Test /ask-a-pro with missing required input data."""
    payload = {
        "llm": "openai/gpt-4o",
        # Missing level_name, level_description
        "command_history": ["ls"]
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 400
    assert data['status'] == 'error'
    assert "Missing required data for Ask-a-Pro" in data['message']

def test_ask_a_pro_empty_command_history(client, mocker):
    """Test /ask-a-pro with empty command history."""
    mock_completion = mocker.patch('banditgui.app.completion')
    mock_getenv = mocker.patch('banditgui.app.os.getenv')

    mock_getenv.return_value = "dummy_openai_key"
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message = MagicMock()
    mock_llm_response.choices[0].message.content = "Mocked advice for empty history"
    mock_completion.return_value = mock_llm_response
    
    payload = {
        "llm": "openai/gpt-4o",
        "level_name": "1",
        "level_description": "A different level.",
        "command_history": [] # Empty history
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['advice'] == "Mocked advice for empty history"

    mock_completion.assert_called_once()
    args, kwargs = mock_completion.call_args
    prompt_arg = kwargs['messages'][0]['content']
    assert "📜 Command History:\nNo commands executed yet." in prompt_arg

def test_ask_a_pro_openrouter_model_name_construction(client, mocker):
    """Test model name construction for OpenRouter."""
    mock_completion = mocker.patch('banditgui.app.completion')
    mock_getenv = mocker.patch('banditgui.app.os.getenv')

    mock_getenv.side_effect = lambda key: "dummy_openrouter_key" if key == "OPENROUTER_API_KEY" else None
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message = MagicMock()
    mock_llm_response.choices[0].message.content = "Mocked LLM advice for OpenRouter"
    mock_completion.return_value = mock_llm_response
    
    payload = {
        "llm": "openrouter/nous-hermes-2", # from llm_model.json
        **SAMPLE_ASK_A_PRO_DATA
    }
    response = client.post('/ask-a-pro', json=payload)
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['status'] == 'success'
    
    mock_completion.assert_called_once()
    args, kwargs = mock_completion.call_args
    # The key here is that 'openrouter/' is prepended to the model part from the llm value
    assert kwargs['model'] == "openrouter/nous-hermes-2" 
    assert kwargs['api_key'] == "dummy_openrouter_key"
