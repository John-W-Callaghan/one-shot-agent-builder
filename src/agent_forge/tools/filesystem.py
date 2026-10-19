"""Filesystem tools for agents to read and write project files."""
from pathlib import Path


def read_file(filepath: str) -> str:
    """Read a file's contents."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    return path.read_text()


def write_file(filepath: str, content: str) -> str:
    """Write content to a file, creating directories as needed."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return f"Wrote {len(content)} bytes to {filepath}"


def list_files(directory: str, pattern: str = "**/*") -> list[str]:
    """List files in a directory matching a glob pattern."""
    path = Path(directory)
    if not path.exists():
        return []
    return [str(p.relative_to(path)) for p in path.glob(pattern) if p.is_file()]
