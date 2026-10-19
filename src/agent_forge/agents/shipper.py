"""Shipper agent — generates README, docs, and deployment config."""
import json

from .base import BaseAgent
from ..config import ModelConfig
from ..schemas.spec import ArchitectureDoc, ProjectSpec


class Shipper(BaseAgent):
    def __init__(self):
        super().__init__(
            name="shipper",
            model=ModelConfig.SHIPPER_MODEL,
            role_description="Technical writer and release engineer",
        )

    def run(self, input_data: dict) -> dict[str, str]:
        spec: ProjectSpec = input_data["spec"]
        architecture: ArchitectureDoc = input_data["architecture"]
        existing_files: list[str] = sorted(input_data.get("files", {}).keys())

        system_prompt = self._load_prompt()
        user_message = (
            f"Generate project documentation and deployment configuration.\n\n"
            f"PROJECT SPEC:\n{spec.model_dump_json(indent=2)}\n\n"
            f"ARCHITECTURE:\n{architecture.model_dump_json(indent=2)}\n\n"
            f"EXISTING FILES:\n{json.dumps(existing_files, indent=2)}\n\n"
            f"Generate these files as a JSON object (keys = paths, values = contents):\n"
            f"1. README.md — project overview, setup instructions, tech stack, features\n"
            f"2. .github/workflows/ci.yml — GitHub Actions CI pipeline\n"
            f"3. docker-compose.yml (if applicable)\n"
            f"4. Any deployment config files (vercel.json, netlify.toml, etc.)\n"
            f"5. CONTRIBUTING.md — contribution guidelines\n"
        )

        return self._generate_files(system_prompt, user_message, max_tokens=32000)
