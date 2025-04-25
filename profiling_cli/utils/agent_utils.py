import os

from langchain_anthropic import ChatAnthropic
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

from profiling_cli.consts import ModelProviderConst


def initiate_model(model: str, model_provider: str | ModelProviderConst,
                   base_url: str | None = None) -> ChatAnthropic | ChatOpenAI | OllamaLLM:
    """
    Initiate the model with the given model name and provider.
    :param model: Model name e.g. claude-3-5-sonnet-20240620
    :param model_provider: Model provider name e.g. anthropic
    :param base_url: Base URL e.g. https://example.com if needed for the model provider such as Ollama
    :return: LLM model instance
    """
    # Initialize the language model
    if model_provider == ModelProviderConst.ANTHROPIC:
        assert os.environ["ANTHROPIC_API_KEY"], "Please set ANTHROPIC_API_KEY environment variable"
        llm = ChatAnthropic(model=model, verbose=True)
    elif model_provider == ModelProviderConst.OLLAMA:
        llm = OllamaLLM(base_url=base_url, model=model, verbose=True)
    elif model_provider == ModelProviderConst.OPENAI:
        assert os.environ["OPENAI_API_KEY"], "Please set OPENAI_API_KEY environment variable"
        llm = ChatOpenAI(model=model, verbose=True)
    else:
        raise ValueError(f"Unknown model provider {model_provider}")
    return llm
