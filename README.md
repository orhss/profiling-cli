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

## Installation

```bash
pip install git+https://github.com/orhss/profiling-cli.git@v1.0.2#egg=profiling-cli
```

## Configuration

Create a .env file in your project with the following variables:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
```
The file path will be passed to the CLI using the --config flag

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
```

## Options

- `--config`, `-c`: Path to config file containing API keys (required)
- `--module`, `-m`: Module to profile (can be used multiple times)
- `--function`, `-f`: Function to profile (can be used multiple times)
- `--test-path`, `-tp`: Path to test directory or file (auto-detected if not provided)
- `--test-module`, `-tm`: Name of the test module (auto-detected if not provided)

## How It Works

1. The tool copies a pytest plugin to the test directory
2. It runs pytest with line profiling and memory profiling enabled
3. The profiling data is collected during test execution
4. An AI agent analyzes the profiling results and provides insights
5. Temporary files are cleaned up after execution
6. When using create-pr during your interactive session with the LLM, you can have the AI automatically create a GitHub pull request with the optimized code discussed

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
