from langchain.agents import AgentExecutor


async def create_pr_with_optimized_function(agent_executor: AgentExecutor) -> None:
    """
    Creates a pull request with an optimized function by interacting with the user and GitHub.

    This function prompts the user for repository details, confirms the information,
    and then uses an LLM agent to create a pull request with the optimized function.

    :param agent_executor: The agent executor instance used to invoke the LLM with GitHub tools
    :return: None
    """
    print("Create PR with Optimized Function")

    # Collect information directly from the user
    owner = input("GitHub owner (username): ")
    repository = input("GitHub repository: ")
    is_private = input("GitHub repository is private? (yes/no): ")
    file_path = input("File path to update: ")

    # Confirm with the user
    print("\nReady to create PR with:")
    print(f"- Owner: {owner}")
    print(f"- Repository: {repository}")
    print(f"- File path: {file_path}")
    confirm = input("\nProceed? (y/n): ")

    if confirm.lower() not in ['y', 'yes']:
        print("PR creation cancelled.")
        return None

    # Create the PR using the LLM with GitHub tools
    pr_prompt = f"""
    Using the optimized function you've already created (which is in our chat history), please create a pull request with the following requirements:
    
    1. The PR should replace the original function with your optimized version
    2. Ensure your PR maintains the original function name
    
    Pull request details:
    - Owner: {owner}
    - Repository: {repository}
    - Private repository: {is_private}
    - File path: {file_path}
    - Base branch: main
    
    Infer any details which are missing.
    
    Follow these exact steps using GitHub tools in order to create the PR:
    1. Use get_file_contents to retrieve the original file
    2. Use create_branch to make a new branch from main, you must generate a truly random 8 letter code and add it to the branch name, do not use predetermined sequences.
    3. Use create_or_update_file to commit your optimized function, making sure to:
       - Include the SHA from step 1
       - Maintain the original function name
       - Use a descriptive commit message
    4. Use create_pull_request to open a PR from your new branch to main
    
    Provide the PR URL when complete.
    """

    # Enable GitHub tools for this operation
    await agent_executor.ainvoke({"input": pr_prompt})
    return None