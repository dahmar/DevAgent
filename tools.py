from smolagents import tool

from pathlib import Path

@tool
def create_file(filename: str, content: str) -> str:
    """
    Creates a file in the workspace folder.

    Args:
        filename: Name of the file to create.
        content: Text content of the file.

    Returns:
        Confirmation message.
    """

    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)

    file_path = workspace / filename
    file_path.write_text(content, encoding="utf-8")

    return f"File {filename} created successfully."