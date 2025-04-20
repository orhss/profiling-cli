import pytest
import importlib
import inspect
import os
from line_profiler import LineProfiler

from profiling_cli.consts import LINE_STATS_FILE, PROFILE_MODULES, PROFILE_FUNCTIONS ,PROFILE_OUTPUT_DIR

# Configuration (will be populated from environment variables or defaults)
PROFILE_OUTPUT_DIR_LOCATION = os.environ.get(f'{PROFILE_OUTPUT_DIR}')

# Global line profiler
line_profiler = LineProfiler()


def find_and_register_functions():
    """Find target functions and register them with the line profiler."""
    modules_to_profile = os.environ.get(f'{PROFILE_MODULES}').split(',') if os.environ.get(f'{PROFILE_MODULES}') else []
    functions_to_profile = os.environ.get(f'{PROFILE_FUNCTIONS}').split(',') if os.environ.get(
        f'{PROFILE_FUNCTIONS}') else []
    print(f"Modules to profile : {modules_to_profile}")
    for module_name in modules_to_profile:
        try:
            # Import the module
            module = importlib.import_module(module_name)

            # If specific functions are listed, profile only those
            print(f"Function to profile: {functions_to_profile}")
            if functions_to_profile:
                for func_name in functions_to_profile:
                    # Check if it's a class method (contains a dot)
                    if '.' in func_name:
                        class_name, method_name = func_name.split('.')

                        # Get the class from the module
                        if hasattr(module, class_name):
                            cls = getattr(module, class_name)
                            if inspect.isclass(cls) and hasattr(cls, method_name):
                                method = getattr(cls, method_name)
                                if callable(method):
                                    line_profiler.add_function(method)
                                    print(f"Registered class method: {module_name}.{func_name} for line profiling")
                    elif hasattr(module, func_name):
                        func = getattr(module, func_name)
                        line_profiler.add_function(func)
                        print(f"Registered function {module_name}.{func_name} for line profiling")
            else:
                # Otherwise, profile all non-private functions in the module
                print("No function to profile")
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj) and not name.startswith('_'):
                        line_profiler.add_function(obj)
                        print(f"Registered {module_name}.{name} for line profiling")
        except Exception as e:
            print(f"Error registering module {module_name}: {e}")


# Register functions when plugin is loaded
find_and_register_functions()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    # Enable profiling before each test
    line_profiler.enable_by_count()

    # Run the test
    outcome = yield

    # Disable profiling after test
    line_profiler.disable_by_count()

    # After all tests run, we'll save the results
    if nextitem is None:  # Last test
        # Create output directory
        os.makedirs(PROFILE_OUTPUT_DIR_LOCATION, exist_ok=True)

        # Save the profiling stats
        stats_file = f"{PROFILE_OUTPUT_DIR_LOCATION}/{LINE_STATS_FILE}"
        with open(stats_file, 'w') as f:
            line_profiler.print_stats(stream=f, stripzeros=True)

        print(f"Line profiling results saved to {stats_file}")