import os
from dotenv import load_dotenv

from smolagents import CodeAgent, InferenceClientModel

from tools import create_app_project, create_file, edit_file, get_errors, grep_search, list_dir, read_file, run_command, run_local_server


load_dotenv()


model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
        token=os.getenv("HF_TOKEN")
        )


agent = CodeAgent(
    model=model,
    tools=[create_app_project, create_file, edit_file, get_errors, grep_search, list_dir, read_file, run_command, run_local_server],
    max_steps=6,
    verbosity_level=2
    )


def ask_agent(message):
    return agent.run(message)