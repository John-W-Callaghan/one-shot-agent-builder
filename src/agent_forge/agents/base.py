"""Base agent class that all specialized agents inherit from."""
import json
import re
from pathlib import Path
from typing import Any

import anthropic
from pydantic import BaseModel, ValidationError
from rich.console import Console

from ..config import ModelConfig
from ..schemas.spec import ReviewFinding

console = Console()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Matches "path/to/file.ext" headings followed by a fenced code block.
FILE_BLOCK_PATTERN = re.compile(r"(?:^|\n)(?:#+\s*)?`?([^\n`]+\.\w+)`?\s*\n```\w*\n(.*?)```", re.DOTALL)


class AgentError(RuntimeError):
    """Raised when an agent cannot produce a usable result."""


def extract_json(raw: str) -> Any:
    """Pull a JSON value out of a model response.

    Tries, in order: the whole response, a response wrapped in one code fence,
    the first fenced block, and the outermost {...} span. Greedy matching on the
    whole-response fence matters because generated file contents often contain
    their own ``` fences.
    """
    text = raw.strip()
    candidates = [text]

    whole_fence = re.match(r"^```(?:json)?\s*\n(.*)\n```$", text, re.DOTALL)
    if whole_fence:
        candidates.append(whole_fence.group(1))

    first_fence = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if first_fence:
        candidates.append(first_fence.group(1))

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError("No valid JSON found in response")


def parse_file_map(raw: str) -> dict[str, str]:
    """Parse a {path: content} map from a model response."""
    try:
        data = extract_json(raw)
    except ValueError:
        data = None

    if isinstance(data, dict):
        # Tolerate a {"files": {...}} wrapper.
        if set(data) == {"files"} and isinstance(data["files"], dict):
            data = data["files"]
        return {
            str(path): content if isinstance(content, str) else json.dumps(content, indent=2)
            for path, content in data.items()
        }

    # Fallback: extract fenced code blocks preceded by a filename.
    files = {}
    for match in FILE_BLOCK_PATTERN.finditer(raw):
        filepath = match.group(1).strip().strip("`").strip()
        files[filepath] = match.group(2)
    return files


class BaseAgent:
    """Foundation for all pipeline agents."""

    def __init__(self, name: str, model: str, role_description: str):
        self.name = name
        self.model = model
        self.role_description = role_description
        self.client = anthropic.Anthropic(api_key=ModelConfig.get_api_key())

    def _load_prompt(self) -> str:
        """Load the system prompt from the prompts/ directory."""
        prompt_file = PROMPTS_DIR / f"{self.name}.md"
        if prompt_file.exists():
            return prompt_file.read_text()
        return self.role_description

    def run(self, input_data: dict[str, Any]) -> Any:
        """Execute the agent's task. Override in subclasses."""
        raise NotImplementedError

    def _stream_message(self, system_prompt: str, user_message: str, max_tokens: int):
        """Stream a request and return the final message (streaming avoids HTTP timeouts on long outputs)."""
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        }
        if ModelConfig.USE_REFUSAL_FALLBACK and "haiku" not in self.model:
            with self.client.beta.messages.stream(
                **params,
                betas=[ModelConfig.REFUSAL_FALLBACK_BETA],
                extra_body={"fallbacks": "default"},
            ) as stream:
                return stream.get_final_message()
        with self.client.messages.stream(**params) as stream:
            return stream.get_final_message()

    def _call_model(self, system_prompt: str, user_message: str, max_tokens: int = 16000) -> str:
        """Make an API call to Claude and return the response text."""
        console.print(f"  [cyan]⚡ {self.name}[/cyan] thinking... [dim]({self.model})[/dim]", highlight=False)

        try:
            message = self._stream_message(system_prompt, user_message, max_tokens)
        except anthropic.AuthenticationError as e:
            raise AgentError(f"{self.name}: authentication failed — check ANTHROPIC_API_KEY") from e
        except anthropic.NotFoundError as e:
            raise AgentError(f"{self.name}: model '{self.model}' not found — update config.py") from e
        except anthropic.RateLimitError as e:
            raise AgentError(f"{self.name}: rate limited after retries — wait and try again") from e
        except anthropic.APIStatusError as e:
            raise AgentError(f"{self.name}: API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise AgentError(f"{self.name}: could not reach the Anthropic API — check your connection") from e

        if message.stop_reason == "refusal":
            raise AgentError(f"{self.name}: the model declined this request")
        if message.stop_reason == "max_tokens":
            console.print(f"  [yellow]⚠ {self.name} hit max_tokens ({max_tokens}); output may be truncated[/yellow]")

        # Responses can contain thinking or fallback blocks; keep only the text.
        text = "".join(block.text for block in message.content if block.type == "text")
        if not text.strip():
            raise AgentError(f"{self.name}: model returned an empty response")
        return text

    def _call_model_structured(
        self, system_prompt: str, user_message: str, output_schema: type[BaseModel], max_tokens: int = 16000
    ) -> Any:
        """Make an API call and parse the response into a Pydantic model.

        Asks for JSON matching the schema, then validates it. On a parse or
        validation failure, retries once with the error included.
        For a production system you'd use structured outputs for guaranteed structure.
        """
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
        enhanced_prompt = (
            f"{system_prompt}\n\n"
            f"IMPORTANT: Respond with ONLY valid JSON matching this schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"No markdown, no explanation — just the JSON object."
        )

        message = user_message
        for attempt in (1, 2):
            raw = self._call_model(enhanced_prompt, message, max_tokens)
            try:
                return output_schema.model_validate(extract_json(raw))
            except (ValueError, ValidationError) as e:
                console.print(f"  [red]⚠ {self.name} output parse error (attempt {attempt}/2): {e}[/red]")
                console.print(f"  [dim]Raw output (first 500 chars): {raw[:500]}[/dim]")
                if attempt == 2:
                    raise AgentError(f"{self.name}: could not produce valid {output_schema.__name__}") from e
                message = (
                    f"{user_message}\n\n"
                    f"Your previous response could not be parsed:\n{e}\n\n"
                    f"Respond again with ONLY a JSON object that matches the schema exactly."
                )

    def _generate_files(self, system_prompt: str, user_message: str, max_tokens: int = 64000) -> dict[str, str]:
        """Call the model and parse its response as a {path: content} file map."""
        raw = self._call_model(system_prompt, user_message, max_tokens)
        files = parse_file_map(raw)
        if not files:
            console.print(f"  [red]⚠ {self.name} returned no parseable files[/red]")
            console.print(f"  [dim]Raw output (first 500 chars): {raw[:500]}[/dim]")
        return files

    @staticmethod
    def _revision_request(findings: list[ReviewFinding], previous_files: dict[str, str]) -> str:
        """Build the extra context sent to a builder during the Sentinel feedback loop."""
        findings_text = "\n".join(
            f"- [{f.severity}/{f.category}] {f.file_path}"
            f"{f' (lines {f.line_range})' if f.line_range else ''}: {f.description}\n"
            f"  FIX: {f.fix_instruction}"
            for f in findings
        )
        files_text = "\n".join(
            f"\n=== {path} ===\n{content}" for path, content in sorted(previous_files.items())
        )
        return (
            f"\n\nREVISION REQUEST — a code review of your previous output found these issues:\n"
            f"{findings_text}\n\n"
            f"YOUR PREVIOUS FILES:\n{files_text}\n\n"
            f"Fix every issue listed. Respond with a JSON object containing the complete, "
            f"updated contents of every file you changed (keys = paths, values = full file contents). "
            f"Omit files that need no changes."
        )
