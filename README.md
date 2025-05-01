# Python Profile CLI Tool

## Overview

This is a proof-of-concept (POC) project designed to explore the integration of command-line interfaces, Python code
profiling, and AI-assisted analysis using Large Language Models (LLMs) and Model Context Protocol (MCP). The code is
experimental in nature and intended for learning and exploration rather than production use - it is not meant to be the
best code out there, but rather a playground for combining these different technologies.

## Features

- Automated line profiling for Python code
- Memory usage analysis using Memray
- AI-assisted interpretation of profiling results
- Automatic test discovery and execution
- Configuration through environment variables
- Interactive AI-powered code optimization through a chatbot-like interface
- GitHub Model Context Protocol (MCP) server integration for automated PR creation with optimized functions
- GitHub Action workflow for CI/CD integration

## Installation

```bash
pip install git+https://github.com/orhss/profiling-cli.git@v1.2.5#egg=profiling-cli
```

## Prerequisites

- Python 3.10
- pytest
- line_profiler
- Memray
- Anthropic API access or other LLM provider API access
- GitHub Personal Access Token (for interactive PR creation)
- Docker (required for running the MCP server which provides GitHub integration)

## Configuration

Create a .env file in your project with the appropriate API keys based on your chosen model provider:

```
# For Anthropic models (default)
ANTHROPIC_API_KEY=your_anthropic_api_key

# For OpenAI models
OPENAI_API_KEY=your_openai_api_key

# For other model providers, add the appropriate API key

# Required for GitHub PR creation feature
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
```

The API key requirements depend on which model provider you're using with the `-mp` flag. The file path will be passed to the CLI using the `--config` flag.

## Usage

### Basic Usage

```bash
# Profile specific modules and functions
profile -c config.env -m module_name -f function_name

# Auto-detect tests and profile
profile -c config.env

# Specify test path
profile -c config.env --test-path /path/to/tests

# Specify test module
profile -c config.env --test-module test_module

# Use a specific model provider
profile -c config.env -mp openai -mn gpt-4

# Use a custom model endpoint
profile -c config.env -mp ollama -mn mistral -mbu http://localhost:11434
```

### Interactive Session

After running the profiling tool, you'll enter an interactive chatbot-like session with the AI:

1. The AI will analyze the profiling results and provide initial insights
2. You can ask follow-up questions about the analysis or request specific optimization advice
3. The AI can explain parts of your code that are bottlenecks and suggest improvements
4. Continue the conversation until you're satisfied with the optimization plan

### Creating a PR with Changes

During the interactive session, you can use the special command `create-pr` to have the AI automatically create a GitHub pull request with the optimized code:

```
You: create-pr
```

The AI will:
1. Generate the optimized code based on your discussion
2. Create a new branch in your repository
3. Commit the changes with appropriate commit messages
4. Create a pull request with a detailed description of the optimizations
5. Provide you with a link to the newly created PR

## Options

- `--config`, `-c`: Path to config file containing API keys (required)
- `--module`, `-m`: Module to profile (can be used multiple times)
- `--function`, `-f`: Function to profile (can be used multiple times)
- `--test-path`, `-tp`: Path to test directory or file (auto-detected if not provided)
- `--test-module`, `-tm`: Name of the test module (auto-detected if not provided)
- `--model-provider`, `-mp`: Name of the model provider (e.g., anthropic, openai)
- `--model-name`, `-mn`: Name of the LLM model (e.g., claude-3-5-sonnet-20240620)
- `--model-base-url`, `-mbu`: Custom base URL for the model API endpoint

## How It Works

1. The tool copies a pytest plugin to the test directory
2. It runs pytest with line profiling and memory profiling enabled
3. The profiling data is collected during test execution
4. An AI agent analyzes the profiling results and provides insights
5. The MCP server is spun up to give the AI access to GitHub tools
6. You engage in an interactive session with the AI to discuss optimizations
7. When using the `create-pr` command during your session, the AI automatically creates a GitHub pull request with the optimized code
8. Temporary files are cleaned up after execution

## Example Workflow

Here's an example of how you might use the tool:

```bash
# Start the profiling tool on a specific module and function
$ profile -c .env -m my_module -f slow_function

# Output: 
# Running profiling on my_module.slow_function...
# Profiling complete. Starting AI analysis...
# 
# AI: I've analyzed the profiling results for my_module.slow_function. The function is taking 
# considerable time in the loop at line 42-47, with most time spent processing the data transformation.
# The memory profile shows peak usage at 250MB primarily due to creating a large intermediate list.
#
# What specific performance aspects would you like me to help optimize?

# You engage in conversation with the AI
$ I'm concerned about both the execution time and memory usage. Can you suggest improvements?

# AI provides detailed suggestions and code examples

# When satisfied, create a PR with the changes
$ create-pr

# AI: Creating PR with optimizations we discussed...
# PR created successfully! You can view it here: https://github.com/your-repo/pull/123
```

## GitHub Action Integration

This repository also provides a reusable GitHub Action workflow that automatically profiles Python functions changed in pull requests.

### Setting Up the GitHub Action

1. **Create a workflow file** in your repository at `.github/workflows/profile-pr.yml`:

```yaml
name: Profile Python Changes

on:
  pull_request:
    types: [ opened, synchronize, labeled ]
    branches:
      - main
    paths:
      - '**/*.py'

jobs:
  call-profile-workflow:
    # Only run if PR has the "profile" label
    if: contains(github.event.pull_request.labels.*.name, 'profile')
    uses: orhss/profiling-cli/.github/workflows/reusable-profile-pr-changes.yml@main
    with:
      python-version: '3.10'  # Optional - defaults to '3.10'
      file-pattern: '**/*.py'  # Optional - defaults to '**/*.py'
      requirements-file: 'requirements.txt'  # Optional - defaults to 'requirements.txt'
      profiling-cli-version: 'v1.3.0' # Optional - defaults to what is set on the main branch
      model-provider: 'anthropic'  # Optional - 'anthropic' or 'openai'
      # The default model (claude-3-5-sonnet-20240620) works best with the profiling tool
      # model-name: 'claude-3-5-sonnet-20240620'  # Only specify if you need a different model
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}  # Required when using Anthropic models
      # OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # Required when using OpenAI models
      PERSONAL_ACCESS_TOKEN_GITHUB: ${{ secrets.PERSONAL_ACCESS_TOKEN_GITHUB }}
```

2. **Set up required secrets** in your repository at Settings > Secrets and variables > Actions:
    - `ANTHROPIC_API_KEY`: Your Anthropic API key (when using Anthropic models)
    - `OPENAI_API_KEY`: Your OpenAI API key (when using OpenAI models)
    - `PERSONAL_ACCESS_TOKEN_GITHUB`: A GitHub PAT with appropriate permissions

3. **Create a "profile" label** in your repository. Pull requests with this label will trigger the profiling workflow.

### Workflow Configuration Options

| Name                    | Description                                           | Required | Default                        |
|-------------------------|-------------------------------------------------------|----------|--------------------------------|
| `python-version`        | Python version to use                                 | No       | '3.10'                         |
| `file-pattern`          | File pattern to match changed files                   | No       | '**/*.py'                      |
| `requirements-file`     | Path to requirements file                             | No       | 'requirements.txt'             |
| `profiling-cli-version` | Version of the profiling-cli to use                   | No       | 'v1.2.5'                       |
| `base-branch`           | Base branch to compare against                        | No       | (PR base ref)                  |
| `model-provider`        | LLM provider to use ('anthropic', 'openai', 'ollama') | No       | 'anthropic'                    |
| `model-name`            | Name of the LLM model to use                          | No       | '' (uses default for provider) |

> **Note:** The profiling tool is currently optimized for Claude 3.5 Sonnet (`claude-3-5-sonnet-20240620`), which is used by default when no model name is specified. Other models like Claude 3.7 Sonnet may have compatibility issues with the current profiling data format.

### Required Secrets

| Name                           | Description                  | Required When                                        |
|--------------------------------|------------------------------|------------------------------------------------------|
| `ANTHROPIC_API_KEY`            | Anthropic API key            | Using Anthropic models (model-provider: 'anthropic') |
| `OPENAI_API_KEY`               | OpenAI API key               | Using OpenAI models (model-provider: 'openai')       |
| `PERSONAL_ACCESS_TOKEN_GITHUB` | GitHub Personal Access Token | Always required                                      |

### How the Workflow Works

1. Triggered when a pull request with the "profile" label is opened or updated
2. Identifies which Python files have changed in the PR
3. Extracts the specific functions that have been modified
4. Runs the profiling tool on those functions
5. Results are processed by the profiling-cli tool and added to the PR as comments, highlighting potential optimizations

## Model Context Protocol (MCP) Integration

The tool leverages GitHub's Model Context Protocol to provide the AI with:

1. Access to the GitHub repository context
2. Ability to read and write files
3. Capability to create branches, commits, and pull requests
4. Understanding of repository structure and history

This integration enables the AI to make informed suggestions based on your specific codebase and project structure, and to implement those suggestions directly via GitHub PRs when requested.

## Docker Usage

Docker is required for running the MCP server, which provides the AI with GitHub integration capabilities. The tool automatically manages the Docker container for you.
No additional Docker configuration is required from the user beyond having Docker installed and running on the system.

## Contributing

This is an experimental project, but suggestions and improvements are welcome. Please feel free to open issues or submit pull requests.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).