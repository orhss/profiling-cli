from typing import List
import subprocess

from profiling_cli.consts import ModelProviderConst


def display_process_output(process: subprocess.Popen) -> List[str]:
    """
    Displays and captures the output of a subprocess in real-time, with special handling for Memray reports.

    This function reads the stdout of a process line by line, printing all lines to the console until
    it encounters a Memray report section. Once the Memray section begins, it captures those lines
    for later analysis without printing them to the console.

    :param process: A subprocess.Popen object with stdout configured as a pipe
    :return: A list of strings containing the lines from the Memray report section
    """
    memray_section = []
    capturing = False
    all_output = []

    # Read and display output line by line
    for line in iter(process.stdout.readline, ''):
        # Check if we've reached the Memray report section
        if "MEMRAY REPORT" in line:
            capturing = True
            print("Running memary stats")
        if not capturing:
            # Print to console in real-time
            print(line, end='')

        # Store all output
        all_output.append(line)

        # Capture the Memray section
        if capturing:
            memray_section.append(line)
    return memray_section


# Define available actions the LLM can recognize and perform
actions = {
    "create_pr": {
        "description": "Create a GitHub PR with optimized code",
        "required_info": ["repository", "file_path", "branch", "commit_message"],
        "triggers": ["create pr", "make pull request", "submit changes", "push to github"]
    }
}


# Function to detect action intent in user message
def detect_action_intent(user_input, actions):
    for action_id, action_info in actions.items():
        if any(trigger in user_input.lower() for trigger in action_info["triggers"]):
            return action_id
    return None


# Function to handle action workflow
async def handle_action(action_id, agent_executor, context=None):
    action = actions[action_id]
    collected_info = {}

    # Initial prompt to start collecting information
    prompt = f"I'll help you {action['description']}. Let me gather some information first."

    # For each required piece of information
    for info_item in action["required_info"]:
        # Format the question based on what info we need
        if info_item == "repository":
            question = f"{prompt}\n\nWhat's the GitHub repository (username/repo format)?"
        elif info_item == "file_path":
            question = "What's the file path where the optimized function should be placed?"
        # etc. for other info types

        # Ask the question and get the response
        response = await agent_executor.ainvoke({"input": question})
        answer = response.get("output", "")

        # Update the prompt with the answer for context
        prompt += f"\n- {info_item}: {answer}"
        collected_info[info_item] = answer

    # Final action execution
    execution_prompt = f"Now I have all the information needed to {action['description']}:\n"
    for key, value in collected_info.items():
        execution_prompt += f"- {key}: {value}\n"
    execution_prompt += f"\nPlease proceed with the {action_id} action using this information and the GitHub tools."

    return await agent_executor.ainvoke({"input": execution_prompt})


def get_model_providers_names() -> List[str]:
    """Get all model provider names from ModelProviderConst."""
    return [value for key, value in ModelProviderConst.__dict__.items()
            if not key.startswith('__') and isinstance(value, str)]
