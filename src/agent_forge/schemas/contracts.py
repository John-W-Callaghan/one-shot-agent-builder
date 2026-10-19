"""Inter-agent data contracts: the shared state passed through the pipeline."""
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from .spec import ArchitectureDoc, AuditReport, DesignSystem, ProjectSpec


def normalize_path(filepath: str) -> str | None:
    """Turn a model-supplied path into a safe relative path, or None if it escapes the output dir."""
    path = filepath.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    path = path.lstrip("/")
    parts = PurePosixPath(path).parts
    if not parts or ".." in parts:
        return None
    return str(PurePosixPath(*parts))


@dataclass
class PipelineState:
    """Tracks the full state of a pipeline run."""
    idea: str
    spec: ProjectSpec | None = None
    architecture: ArchitectureDoc | None = None
    design: DesignSystem | None = None
    generated_files: dict[str, str] = field(default_factory=dict)  # path -> content
    file_owners: dict[str, str] = field(default_factory=dict)  # path -> agent that wrote it
    audit: AuditReport | None = None
    review_iteration: int = 0
    max_review_iterations: int = 3
    output_dir: str = ""
    logs: list[dict[str, Any]] = field(default_factory=list)

    def log(self, agent: str, message: str):
        self.logs.append({"agent": agent, "message": message})

    def add_files(self, agent: str, files: dict[str, str]):
        """Record files produced by an agent, tracking ownership for the review loop.

        Paths are normalized so revisions overwrite the original file; unsafe paths are dropped.
        """
        for filepath, content in files.items():
            path = normalize_path(filepath)
            if path is None:
                self.log(agent, f"Dropped unsafe path: {filepath}")
                continue
            self.generated_files[path] = content
            self.file_owners[path] = agent
