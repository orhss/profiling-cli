PROFILE_OUTPUT_DIR = "PROFILE_OUTPUT_DIR"
PROFILE_FUNCTIONS = "PROFILE_FUNCTIONS"
PROFILE_MODULES = "PROFILE_MODULES"

DEFAULT_OUTPUT_DIR = "line_profile_results"
LINE_PROFILING_PLUGIN =  "line_profiling_plugin"
LINE_PROFILING_PLUGIN_FILE = "line_profiling_plugin.py"
LINE_STATS_FILE = "line_stats.txt"

class ModelProviderConst:
    """Model provider constants."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"

# Error messages
class ErrorMessages:
    """Error messages for various scenarios."""
    MISSING_ANTHROPIC_KEY = "Please set ANTHROPIC_API_KEY environment variable"
    MISSING_OPENAI_KEY = "Please set OPENAI_API_KEY environment variable"
