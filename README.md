# Python Profile CLI Tool

## Overview

This is a proof-of-concept (POC) project designed to explore the integration of command-line interfaces, Python code profiling, and AI-assisted analysis using Large Language Models (LLMs) and Model Context Protocol (MCP). The code is experimental in nature and intended for learning and exploration rather than production use - it is not meant to be the best code out there, but rather a playground for combining these different technologies.

## Features

- Automated line profiling for Python code
- Memory usage analysis using Memray
- AI-assisted interpretation of profiling results
- Automatic test discovery and execution
- Configuration through environment variables
- Interactive AI-powered code optimization with GitHub PR creation
- GitHub Action workflow for CI/CD integration

## Installation

```bash
pip install git+https://github.com/orhss/profiling-cli.git@v1.2.5#egg=profiling-cli
```

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
5. Temporary files are cleaned up after execution
6. When using create-pr during your interactive session with the LLM, you can have the AI automatically create a GitHub pull request with the optimized code discussed

## GitHub Action Integration

This repository also provides a reusable GitHub Action workflow that automatically profiles Python functions changed in pull requests.

### Setting Up the GitHub Action

1. **Create a workflow file** in your repository at `.github/workflows/profile-pr.yml`:

```yaml
name: Profile Python Changes

on:
  pull_request:
    types: [opened, synchronize, labeled]
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
      profiling-cli-version: 'v1.2.5'  # Optional - defaults to 'v1.2.5'
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

| Name | Description                                          | Required | Default |
|------|------------------------------------------------------|----------|---------|
| `python-version` | Python version to use                                | No | '3.10' |
| `file-pattern` | File pattern to match changed files                  | No | '**/*.py' |
| `requirements-file` | Path to requirements file                            | No | 'requirements.txt' |
| `profiling-cli-version` | Version of the profiling-cli to use                  | No | 'v1.2.5' |
| `base-branch` | Base branch to compare against                       | No | (PR base ref) |
| `model-provider` | LLM provider to use ('anthropic', 'openai', 'ollama') | No | 'anthropic' |
| `model-name` | Name of the LLM model to use                         | No | '' (uses default for provider) |

> **Note:** The profiling tool is currently optimized for Claude 3.5 Sonnet (`claude-3-5-sonnet-20240620`), which is used by default when no model name is specified. Other models like Claude 3.7 Sonnet may have compatibility issues with the current profiling data format.

### Required Secrets

| Name | Description | Required When |
|------|-------------|--------------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Using Anthropic models (model-provider: 'anthropic') |
| `OPENAI_API_KEY` | OpenAI API key | Using OpenAI models (model-provider: 'openai') |
| `PERSONAL_ACCESS_TOKEN_GITHUB` | GitHub Personal Access Token | Always required |

### How the Workflow Works

1. Triggered when a pull request with the "profile" label is opened or updated
2. Identifies which Python files have changed in the PR
3. Extracts the specific functions that have been modified
4. Runs the profiling tool on those functions
5. Results are processed by the profiling-cli tool and added to the PR

## Requirements

- Python 3.10
- pytest
- line_profiler
- Memray
- Anthropic API access
- GitHub Personal Access Token (for interactive PR creation)
- Docker

## Contributing

This is an experimental project, but suggestions and improvements are welcome. Please feel free to open issues or submit pull requests.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).