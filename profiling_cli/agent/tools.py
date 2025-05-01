import os

from langchain.agents import AgentExecutor


async def create_pr_with_optimized_function(agent_executor: AgentExecutor) -> None:
    """
    Creates a pull request with an optimized function by interacting with the user and GitHub.

    This function gets repository details from GitHub Actions environment variables if available,
    otherwise prompts the user for input. It then confirms the information and uses
    an LLM agent to create a pull request with the optimized function.

    Uses these GitHub Actions environment variables:
    - GITHUB_REPOSITORY: The owner and repository name (format: "owner/repo")
    - GITHUB_BASE_REF: The target branch in pull requests
    - GITHUB_ACTOR: The name of the person or app that initiated the workflow
    - GITHUB_WORKSPACE: The GitHub workspace directory path

    Custom environment variables that can be used as fallbacks:
    - OPT_FUNC_REPO_PRIVATE: Whether the repo is private ('true'/'false')
    - OPT_FUNC_FILE_PATH: Path to the file to be updated
    - OPT_FUNC_BASE_BRANCH: Base branch for the PR (defaults to "main")

    :param agent_executor: The agent executor instance used to invoke the LLM with GitHub tools
    :return: None
    """
    print("Create PR with Optimized Function")
    # Extract owner and repository from GITHUB_REPOSITORY
    github_repository = os.environ.get("GITHUB_REPOSITORY")
    if github_repository and "/" in github_repository:
        # GITHUB_REPOSITORY is in format "owner/repo"
        owner, repository = github_repository.split("/", 1)
    else:
        owner = os.environ.get("OPT_FUNC_REPO_OWNER")
        repository = os.environ.get("OPT_FUNC_REPO_NAME")

    # Collect information directly from the user
    if not owner:
        owner = input("GitHub owner (username): ")
    if not repository:
        repository = input("GitHub repository: ")

    # Determine if repository is private
    is_private = os.environ.get("OPT_FUNC_REPO_PRIVATE", "").lower()
    if is_private not in ["true", "false"]:
        is_private = input("GitHub repository is private? (yes/no): ")
    else:
        is_private = "yes" if is_private == "true" else "no"

    file_path = os.environ.get("OPT_FUNC_FILE_PATH")
    if not file_path:
        file_path = input("File path(s) to update, if there are multiple separate with a comma: ")
    file_paths = file_path.split(",")

    # Determine the base branch
    # For pull requests, GitHub Actions provides GITHUB_BASE_REF which contains the target branch name
    # Otherwise, use the custom environment variable or default to "main"
    base_branch = os.environ.get("GITHUB_BASE_REF") or os.environ.get("OPT_FUNC_BASE_BRANCH", "main")

    # Confirm with the user
    print("\nReady to create PR with:")
    print(f"- Owner: {owner}")
    print(f"- Repository: {repository}")
    print(f"- File paths: {file_paths}")
    if os.environ.get("CI", "").lower() != "true":
        confirm = input("\nProceed? (y/n): ")

        if confirm.lower() not in ['y', 'yes']:
            print("PR creation cancelled.")
            return None
    else:
        print("\nCreating PR")

    # Create the PR using the LLM with GitHub tools
    pr_prompt = f"""
Using the optimized functions you've already created (which is in our chat history), please create a pull request with the following requirements:

1. If the original function exists, replace it with your optimized version while maintaining the original function name
2. If the function doesn't yet exist in the file, add your new function to the appropriate file

Pull request details:
- Owner: {owner}
- Repository: {repository}
- Private repository: {is_private}
- File paths: {file_paths}
- Base branch: {base_branch}

Infer any details which are missing.

Follow these exact steps using GitHub tools:
1. For each file path in {file_paths}:
   a. Use get_file_contents to retrieve the original file
   b. Check if the function(s) exists in the file:
      - If it exists: Replace the original function with the optimized version
      - If it doesn't exist: Add the new function to an appropriate location in the file

2. Use create_branch to make a new branch from main, you must generate a truly random 8 letter code and add it to the branch name, do not use predetermined sequences.

3. For each modified file:
   a. Use create_or_update_file to commit your changes, making sure to:
      - Include the SHA from step 1
      - Maintain the original function name if replacing an existing function
      - Use a descriptive commit message that accurately describes the change

4. Use create_pull_request to open a PR from your new branch to {base_branch}, summarizing all changes

Provide the PR URL when complete.
"""

    # Enable GitHub tools for this operation
    await agent_executor.ainvoke({"input": pr_prompt})
    return None
