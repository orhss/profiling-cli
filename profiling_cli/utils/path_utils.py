from pathlib import Path
from typing import Optional


def find_tests_directory(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the tests directory starting from the given path or current directory.
    Searches up the directory tree and one level down in subdirectories.

    :param start_path: Path to start the search from. If None, uses current working directory.

    :return: Path object to tests directory if found, None otherwise.
    """
    if start_path is None:
        start_path = Path.cwd()
    elif isinstance(start_path, str):
        start_path = Path(start_path)

    # Check if we're already in a tests directory
    if start_path.name.lower() in ['tests', 'test']:
        return start_path

    # Common test directory names
    test_dirs = ['tests', 'test', 'pytest']

    # STRATEGY 1: Check current directory
    for test_dir in test_dirs:
        tests_dir = start_path / test_dir
        if tests_dir.exists() and tests_dir.is_dir():
            return tests_dir

    # STRATEGY 2: Check immediate subdirectories (for project/project/tests pattern)
    for subdir in [d for d in start_path.iterdir() if d.is_dir() and not d.name.startswith('.')]:

        # Skip virtual environments and cache directories
        if subdir.name in ['.venv', 'venv', 'env', '.env', '.pytest_cache', '__pycache__', 'node_modules']:
            continue

        # Check if this subdirectory has a tests directory
        for test_dir in test_dirs:
            tests_dir = subdir / test_dir
            if tests_dir.exists() and tests_dir.is_dir():
                return tests_dir

    # STRATEGY 3: Climb up the directory tree
    potential_root = start_path
    for level in range(3):  # Limit the upward search to 3 levels

        # Move up one directory
        parent = potential_root.parent
        if parent == potential_root:  # Reached the filesystem root
            break

        potential_root = parent

        # Check for tests in this level
        for test_dir in test_dirs:
            potential_tests = potential_root / test_dir
            if potential_tests.exists() and potential_tests.is_dir():
                return potential_tests

    return None


def infer_test_module(test_path: Path | str) -> str:
    """
    Infer the test module from the test path.

    Args:
        test_path: Path to the test directory or file

    Returns:
        String representing the module name
    """
    if isinstance(test_path, str):
        test_path = Path(test_path)

    # Try to get a Python module path relative to current directory
    try:
        cwd = Path.cwd()
        rel_path = test_path.relative_to(cwd)
        test_module = str(rel_path).replace('/', '.')
    except ValueError:
        # Fall back to just using the directory name
        test_module = test_path.name

    # Remove .py extension if present
    if test_module.endswith('.py'):
        test_module = ".".join(test_module[:-3].split(".")[:-1])

    return test_module
