import os
from collections.abc import Iterator
from dotenv import load_dotenv

from smolagents import ActionStep, CodeAgent, FinalAnswerStep, InferenceClientModel, PlanningStep

from tools import create_app_project, create_file, edit_file, get_errors, grep_search, list_dir, read_file, run_command

load_dotenv()

model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
        token=os.getenv("HF_TOKEN")
        )


agent = CodeAgent(
    model=model,
    tools=[create_app_project, create_file, edit_file, get_errors, grep_search, list_dir, read_file, run_command],
    max_steps=6,
    verbosity_level=2
    )


def ask_agent(message):
    return agent.run(message)


def ask_agent_stream(message: str) -> Iterator[dict[str, str]]:
    """Yield user-safe progress events while CodeAgent handles a task."""

    yield {"type": "status", "text": "Анализирую задачу..."}
    for step in agent.run(message, stream=True):
        if isinstance(step, PlanningStep):
            yield {"type": "status", "text": "Составляю план действий..."}
        elif isinstance(step, ActionStep):
            if step.tool_calls:
                for tool_call in step.tool_calls:
                    yield {"type": "action", "text": f"Выполняю: {tool_call.name}"}
            if step.observations:
                yield {"type": "observation", "text": str(step.observations)}
        elif isinstance(step, FinalAnswerStep):
            yield {"type": "answer", "text": str(step.output)}