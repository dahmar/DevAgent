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

    @tool
    def read_file(filename: str) -> str:
        """
        Reads a file from the workspace folder.

        Args:
            filename: Name of the file to read.

        Returns:
            The file content.
        """

        file_path = Path("workspace") / filename

        if not file_path.exists():
            return f"File {filename} does not exist."

        return file_path.read_text(encoding="utf-8")