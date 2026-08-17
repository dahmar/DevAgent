import ast
import subprocess
from pathlib import Path

from smolagents import tool


ROOT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = ROOT_DIR / "workspace"


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return WORKSPACE_DIR / path


@tool
def create_file(filename: str, content: str) -> str:
    """
    Creates a file inside the workspace folder.

    Args:
        filename: Relative path to the file inside workspace.
        content: Text content of the file.

    Returns:
        Confirmation message.
    """

    file_path = _resolve_path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

    return f"File {filename} created successfully."


@tool
def read_file(filename: str) -> str:
    """
    Reads a file from the workspace folder.

    Args:
        filename: Relative path to the file inside workspace.

    Returns:
        The file content.
    """

    file_path = _resolve_path(filename)

    if not file_path.exists():
        return f"File {filename} does not exist."

    return file_path.read_text(encoding="utf-8")


@tool
def edit_file(filename: str, old_text: str, new_text: str) -> str:
    """
    Replaces one snippet of text in a workspace file.

    Args:
        filename: Relative path to the file inside workspace.
        old_text: Text that should be replaced.
        new_text: Replacement text.

    Returns:
        Confirmation message.
    """

    file_path = _resolve_path(filename)

    if not file_path.exists():
        return f"File {filename} does not exist."

    content = file_path.read_text(encoding="utf-8")

    if old_text not in content:
        return "Target text not found in the file."

    updated_content = content.replace(old_text, new_text, 1)
    file_path.write_text(updated_content, encoding="utf-8")

    return f"Updated {filename}."


@tool
def list_dir(path: str = ".") -> str:
    """
    Lists files and folders inside the workspace or a subdirectory.

    Args:
        path: Relative path to list. Defaults to the workspace root.

    Returns:
        A newline-separated list of entries.
    """

    target_path = _resolve_path(path)

    if not target_path.exists():
        return f"Directory {path} does not exist."

    if not target_path.is_dir():
        return f"{path} is not a directory."

    entries = sorted(
        [entry.name + ("/" if entry.is_dir() else "") for entry in target_path.iterdir()]
    )

    return "\n".join(entries) if entries else "(empty)"


@tool
def run_command(command: str) -> str:
    """
    Runs a shell command in the project root.

    Args:
        command: Shell command to execute.

    Returns:
        Command output and exit code.
    """

    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=str(ROOT_DIR),
        timeout=600,
    )

    parts = []
    if completed.stdout.strip():
        parts.append(completed.stdout.strip())
    if completed.stderr.strip():
        parts.append(completed.stderr.strip())
    if not parts:
        parts.append("(no output)")

    parts.append(f"Exit code: {completed.returncode}")
    return "\n".join(parts)


@tool
def grep_search(query: str, path: str = ".") -> str:
    """
    Searches for a text query in a file or recursively inside a directory.

    Args:
        query: Text to search for.
        path: File or directory inside workspace.

    Returns:
        Matching lines with file names and line numbers.
    """

    target_path = _resolve_path(path)

    if not target_path.exists():
        return f"Path {path} does not exist."

    if target_path.is_file():
        files_to_scan = [target_path]
    else:
        files_to_scan = [
            item
            for item in target_path.rglob("*")
            if item.is_file() and ".git" not in item.parts and "__pycache__" not in item.parts
        ]

    matches = []
    for file_path in files_to_scan:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            if query.lower() in line.lower():
                matches.append(f"{file_path.relative_to(WORKSPACE_DIR) if file_path.is_relative_to(WORKSPACE_DIR) else file_path}:{line_number}: {line}")

    if not matches:
        return "No matches found."

    return "\n".join(matches[:50])


@tool
def get_errors(filename: str) -> str:
    """
    Checks a Python file for syntax errors.

    Args:
        filename: Relative path to the Python file inside workspace.

    Returns:
        A short diagnostic message.
    """

    file_path = _resolve_path(filename)

    if not file_path.exists():
        return f"File {filename} does not exist."

    try:
        source = file_path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        return f"Syntax error at line {exc.lineno}: {exc.msg}"
    except Exception as exc:
        return f"Unable to check errors: {exc}"

    return "No errors detected."


@tool
def create_app_project(name: str, project_type: str = "website") -> str:
    """
    Creates a starter project for a website, app, or game.

    Args:
        name: Project folder name inside workspace.
        project_type: One of: website, app, game.

    Returns:
        Confirmation message.
    """

    project_dir = WORKSPACE_DIR / name
    project_dir.mkdir(parents=True, exist_ok=True)

    if project_type == "website":
        files = {
            "index.html": "<!doctype html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n  <title>My Site</title>\n  <link rel=\"stylesheet\" href=\"style.css\">\n</head>\n<body>\n  <main>\n    <h1>Hello from your new site</h1>\n    <p>This page was generated by the agent.</p>\n    <a href=\"about.html\">About</a>\n  </main>\n  <script src=\"script.js\"></script>\n</body>\n</html>\n",
            "about.html": "<!doctype html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\">\n  <title>About</title>\n  <link rel=\"stylesheet\" href=\"style.css\">\n</head>\n<body>\n  <main>\n    <h1>About</h1>\n    <p>This is the second page.</p>\n    <a href=\"index.html\">Back home</a>\n  </main>\n</body>\n</html>\n",
            "style.css": "body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.5; }\nmain { max-width: 700px; margin: 0 auto; }\nh1 { color: #2563eb; }\n",
            "script.js": "console.log('Site ready');\n",
        }
    elif project_type == "app":
        files = {
            "index.html": "<!doctype html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\">\n  <title>App</title>\n</head>\n<body>\n  <div id=\"app\"></div>\n  <script src=\"app.js\"></script>\n</body>\n</html>\n",
            "app.js": "document.getElementById('app').innerHTML = '<h1>App started</h1><p>Ready to expand.</p>';\n",
        }
    elif project_type == "game":
        files = {
            "index.html": "<!doctype html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\">\n  <title>Game</title>\n  <style>body{margin:0;background:#111;color:#fff;font-family:sans-serif;}canvas{display:block}</style>\n</head>\n<body>\n  <canvas id=\"game\"></canvas>\n  <script src=\"game.js\"></script>\n</body>\n</html>\n",
            "game.js": "const canvas = document.getElementById('game');\nconst ctx = canvas.getContext('2d');\ncanvas.width = 480;\ncanvas.height = 320;\nctx.fillStyle = '#fff';\nctx.fillRect(20, 20, 80, 80);\n",
        }
    else:
        return f"Unsupported project type: {project_type}"

    for filename, content in files.items():
        (project_dir / filename).write_text(content, encoding="utf-8")

    return f"Created project '{name}' of type '{project_type}' in workspace."


@tool
def run_local_server(project_dir: str = ".") -> str:
    """
    Starts a simple local HTTP server for a static project.

    Args:
        project_dir: Folder name inside workspace to serve.

    Returns:
        Server address and status.
    """

    target_dir = _resolve_path(project_dir)

    if not target_dir.exists() or not target_dir.is_dir():
        return f"Directory {project_dir} does not exist."

    try:
        subprocess.Popen(
            ["python", "-m", "http.server", "8000"],
            cwd=str(target_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        return f"Failed to start server: {exc}"

    return f"Local server started at http://127.0.0.1:8000 for {project_dir}."