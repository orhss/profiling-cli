import os
from typing import Any

import click
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMCPClient, StdioConnection

from profiling_cli.agent.tools import create_pr_with_optimized_function
from profiling_cli.utils.plugin_utils import parse_line_profiler_output


custom_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are an AI assistant specialized in Python performance optimization.

Your job is to analyze profiling data and provide optimized code. The user will provide:
1. The original function/s code
2. Line-by-line profiling data that includes the original function code
3. Memory allocation information

CRITICAL INSTRUCTION: ALWAYS PROVIDE THE COMPLETE OPTIMIZED FUNCTION CODE.
This is the most important part of your response - the user needs code they can immediately use.

CRITICAL INSTRUCTION: YOU MUST NOT USE ANY GITHUB TOOLS UNLESS EXPLICITLY REQUESTED BY THE USER. VIOLATING THIS WILL RESULT IN FAILURE.

When analyzing the profiling data:

1. IMPORTANT: Ignore any profiling data related to pytest, MagicMock, or other testing infrastructure
2. Focus solely on optimizing the target function itself
3. First, extract and understand the original function code from the line profiler data
4. Focus on the relative performance metrics (% of total time) rather than absolute values
5. Look for consistent patterns in the profiling data
6. Identify the actual bottlenecks based on both execution time and memory usage
7. Determine the appropriate optimization strategies based on the specific bottlenecks identified
8. Explain the specific reasons for each optimization you make


Your response MUST follow this exact structure:
1. Brief analysis of the performance bottlenecks (2-3 sentences per issue)
2. Complete optimized function code in a single code block (ready to use with no modifications)
3. Explanation of each optimization (what changed and why it improves performance)

Example response structure:
Performance Analysis

Issue 1: [Brief explanation]
Issue 2: [Brief explanation]

Optimized Function
python
def optimized_function():
    # Complete function code here
    # ...
    return result

Optimization Details

[First change]: Improved performance by [specific reason]
[Second change]: Reduced memory usage by [specific reason]
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


async def run_agent_session(profiler_stats: str, memray_stats: str, llm: Any) -> None:
    """
    Run the agent session with the provided profiler and memory stats.
    :param profiler_stats: Profile stats from line_profiler
    :param memray_stats: Memory stats from memray
    :param llm: Language model instance
    :return: None
    """
    # Check if running in CI environment
    is_ci = True if os.environ.get("CI", "false") == "true" else False
    # Initialize environment variables
    env = os.environ.copy()

    async with MultiServerMCPClient(
            {
                "github": StdioConnection(command="docker",
                                          args=["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                                                "ghcr.io/github/github-mcp-server"],
                                          transport="stdio",
                                          env=env)
            }
    ) as client:
        # Create memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        print("Fetching tools from MCP server")
        tools = client.get_tools()
        # Create a StructuredChatAgent which supports multi-input tools
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            memory=memory,
            agent_kwargs={
                "memory_prompts": [MessagesPlaceholder(variable_name="chat_history")],
                "input_variables": ["input", "chat_history", "agent_scratchpad"],
                "prompt": custom_prompt
            }
        )

        # Print header
        click.echo(click.style("ANALYSIS RESULTS", fg="bright_blue", bold=True))
        click.echo(click.style("═" * 80, fg="bright_blue"))

        function_texts, profile_data = parse_line_profiler_output(profiler_stats)

        # First interaction is with the stats to get the initial response.
        first_input = F"""According to your instructions, please analyze the following functions. \n
        FUNCTIONS: \n {function_texts} \n
        LINE PROFILER RESULTS: \n {profile_data} \n
        MEMORY PROFILER RESULTS: \n {memray_stats}. \n
        REMINDER: You MUST include a complete optimized version of the function in your response. 
        Analysis alone is not sufficient.
        Reminder: You must not use your github tools for this analysis"""
        click.echo(first_input)
        response = await agent_executor.ainvoke(
            {"input": first_input}
        )

        response.get("output", "I couldn't process that.")
        # Print footer
        click.echo(click.style("\n" + "═" * 80, fg="bright_blue"))
        click.echo(click.style("End of analysis", fg="bright_blue", italic=True))

        if is_ci:
            await create_pr_with_optimized_function(agent_executor)
            print("Chatbot: Goodbye!")
            return

        while True:
            print("\n Available commands:")
            print("1. create-pr - Create a PR with the optimized function")
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Chatbot: Goodbye!")
                break

            elif user_input.lower() in ["create-pr", "createpr", "create pr", "/createpr"]:
                await create_pr_with_optimized_function(agent_executor)
            else:
                response = await agent_executor.ainvoke(
                    {"input": user_input}
                )

                # Extract the output message
                response.get("output", "I couldn't process that.")
