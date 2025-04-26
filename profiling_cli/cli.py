import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from profiling_cli.consts import PROFILE_MODULES, PROFILE_FUNCTIONS, PROFILE_OUTPUT_DIR, DEFAULT_OUTPUT_DIR, \
    LINE_PROFILING_PLUGIN, LINE_PROFILING_PLUGIN_FILE, LINE_STATS_FILE, ModelProviderConst
from profiling_cli.agent.session import run_agent_session
from profiling_cli.utils.agent_utils import initiate_model
from profiling_cli.utils.cli_utils import display_process_output, get_model_providers_names
from profiling_cli.utils.path_utils import find_tests_directory, infer_test_module

os.environ[PROFILE_OUTPUT_DIR] = DEFAULT_OUTPUT_DIR


@click.group()
@click.version_option()
def cli():
    """CLI profiling tool"""


@cli.command(name="profile")
@click.option('--config', '-c', required=True,
              help='Path to config file, must include ANTHROPIC_API_KEY and GITHUB_PERSONAL_ACCESS_TOKEN')
@click.option('--module', '-m', multiple=True, help='Module to profile (can be used multiple times)')
@click.option('--function', '-f', multiple=True, help='Function to profile (can be used multiple times)')
@click.option('--test-path', '-tp', help='Path to test directory or file (auto detect)')
@click.option('--test-module', '-tm', help='Name of the test module (auto detect)')
@click.option('--model-provider', '-mp', type=click.Choice(get_model_providers_names()),
              help="Name of the model provider e.g. anthropic", default=ModelProviderConst.ANTHROPIC)
@click.option('--model-name', '-mn', help='Name of the LLM model e.g. claude-3-5-sonnet-20240620',
              default='claude-3-5-sonnet-20240620', )
@click.option('--model-base-url', '-mbu', default=None)
def profile(config: str, module: tuple[str, ...], function: tuple[str, ...],
            test_path: str | None = None, test_module: str | None = None,
            model_name: str = "", model_provider: str | ModelProviderConst = "",
            model_base_url: str | None = None) -> None:
    """
    Run pytest with line profiling and memory profiling plugins enabled.

    This command runs the specified tests with profiling enabled, analyzes the results,
    and uses AI to interpret the profiling data. It automatically detects test paths
    and modules if not specified.

    :param config: Path to configuration file containing required API keys
    :param module: Tuple of module names to profile
    :param function: Tuple of function names to profile
    :param test_path: Optional path to test directory or file
    :param test_module: Optional name of the test module
    :param model_name: Optional name of the model e.g. claude-3
    :param model_provider: Optional name of the model provider e.g. anthropic
    :param model_base_url: Optional URL of the model provider instance
    :return: None
    """
    # Load the config file
    load_dotenv(config)
    # Update the plugin's configuration
    os.environ[PROFILE_MODULES] = ','.join(module)
    os.environ[PROFILE_FUNCTIONS] = ','.join(function)

    # Infer test path if not provided
    if not test_path:
        click.echo('No test path provided, auto-detecting.')
        tests_dir = find_tests_directory(start_path=Path.cwd())
        if not tests_dir:
            click.echo("Error: Could not find tests directory. Please specify with --test-path")
            sys.exit(1)
        else:
            click.echo(f"Test dir path is {tests_dir}")
        test_path = str(tests_dir)

    if not test_module:
        click.echo('No test module provided, auto-detecting.')
        test_module = infer_test_module(test_path=test_path)
        click.echo(f"Test module is {test_module}")

    # Handle python test files
    if test_path.endswith('.py'):
        test_path = "/".join(test_path[:-3].split("/")[:-1])

    # Copy the profile to the test folder
    source_path = Path(__file__).parent / "plugins" / f"{LINE_PROFILING_PLUGIN_FILE}"
    target_path = Path(test_path) / f"{LINE_PROFILING_PLUGIN_FILE}"
    module_name = test_module.replace("/", ".") + f".{LINE_PROFILING_PLUGIN}"

    # Copy the file
    try:
        shutil.copy2(source_path, target_path)
        click.echo(f"Copied {LINE_PROFILING_PLUGIN_FILE} to {target_path}")

        # Correct way to structure the command
        cmd = [
            sys.executable,  # Use the current Python interpreter
            '-m', 'pytest',  # Run pytest as a module
            '-p', module_name,  # Enable the plugin
            test_path,  # Specify the test path
            '-v',  # Verbose output
            '--memray',
            '--most-allocations=20',
            '--stacks=10'
        ]

        # Run the process and display output in real-time while also capturing it
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )

        memray_output = display_process_output(process=process)

        # Wait for process to complete
        process.wait()

        if process.returncode == 0:
            click.echo(f"\n Line profiling results saved to {DEFAULT_OUTPUT_DIR}")
        else:
            click.echo(f"Tests failed with exit code {process.returncode}")
            sys.exit(process.returncode)
        # Send the results to anthropic
        with open(DEFAULT_OUTPUT_DIR + f"/{LINE_STATS_FILE}") as f:
            results_data = f.read()
        llm = initiate_model(model=model_name, model_provider=model_provider, base_url=model_base_url)
        click.echo("\n Lets ask the AI what is going on under the hood..")

        asyncio.run(run_agent_session(profiler_stats=results_data, memray_stats=memray_output, llm=llm))
    except Exception as e:
        click.echo(f"Sorry mate: {e}")
    finally:
        os.unlink(target_path)
        shutil.rmtree(os.environ.get(f'{PROFILE_OUTPUT_DIR}'))
