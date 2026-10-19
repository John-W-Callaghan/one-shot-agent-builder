"""Shell command execution for build/test steps."""
import subprocess
from dataclasses import dataclass


@dataclass
class ShellResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


def run_command(command: str, cwd: str | None = None, timeout: int = 120) -> ShellResult:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return ShellResult(
            command=command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        return ShellResult(
            command=command,
            returncode=-1,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
        )
