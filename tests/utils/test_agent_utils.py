import os
import pytest

from langchain_anthropic import ChatAnthropic
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

from profiling_cli.consts import ModelProviderConst, ErrorMessages
from profiling_cli.utils.agent_utils import initiate_model


@pytest.mark.parametrize(
    "model, provider, base_url, expected_class, env_var",
    [
        pytest.param(
            "claude-3-5-sonnet-20240620",
            ModelProviderConst.ANTHROPIC,
            None,
            ChatAnthropic,
            "ANTHROPIC_API_KEY",
            id="anthropic_model"
        ),
        pytest.param(
            "gpt-4",
            ModelProviderConst.OPENAI,
            None,
            ChatOpenAI,
            "OPENAI_API_KEY",
            id="openai_model"
        ),
        pytest.param(
            "llama2",
            ModelProviderConst.OLLAMA,
            "http://localhost:11434",
            OllamaLLM,
            None,
            id="ollama_model"
        )
    ]
)
def test_initiate_model_success(mocker, model, provider, base_url, expected_class, env_var):
    """Test successful model initialization for different providers."""
    # Spy on the class to check if it was called correctly
    spied_class = mocker.spy(expected_class, "__init__")
    # Set environment variables if needed
    if env_var:
        mocker.patch.dict(os.environ, {env_var: "mock_api_key"})
        # Run function
        initiate_model(model, provider, base_url)

        # Check if the correct class was initialized
        spied_class.assert_called_once()
        assert spied_class.call_args[1]["model"] == model
        assert spied_class.call_args[1]["verbose"] is True

        # For Ollama, also check base_url
        if provider == ModelProviderConst.OLLAMA:
            assert spied_class.call_args[1]["base_url"] == base_url



@pytest.mark.parametrize(
    "model, provider, error_type, error_msg",
    [
        pytest.param(
            "claude-3-5-sonnet-20240620",
            ModelProviderConst.ANTHROPIC,
            AssertionError,
            ErrorMessages.MISSING_ANTHROPIC_KEY,
            id="missing_anthropic_key"
        ),
        pytest.param(
            "gpt-4",
            ModelProviderConst.OPENAI,
            AssertionError,
            ErrorMessages.MISSING_OPENAI_KEY,
            id="missing_openai_key"
        ),
        pytest.param(
            "model-x",
            "unknown_provider",
            ValueError,
            "Unknown model provider unknown_provider",
            id="unknown_provider"
        )
    ]
)
def test_initiate_model_errors(mocker, model, provider, error_type, error_msg):
    """Test error cases for model initialization."""
    # Ensure environment variables are not set
    mocker.patch.dict(os.environ, clear=True)
    with pytest.raises(error_type, match=error_msg):
        initiate_model(model, provider)
