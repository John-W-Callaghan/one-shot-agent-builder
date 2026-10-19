"""Architect agent — designs the system architecture from the spec."""
from .base import BaseAgent
from ..config import ModelConfig
from ..schemas.spec import ArchitectureDoc, ProjectSpec


class Architect(BaseAgent):
    def __init__(self):
        super().__init__(
            name="architect",
            model=ModelConfig.ARCHITECT_MODEL,
            role_description="Senior systems architect",
        )

    def run(self, input_data: dict) -> ArchitectureDoc:
        spec: ProjectSpec = input_data["spec"]
        system_prompt = self._load_prompt()
        user_message = f"Design the system architecture for this project:\n\n{spec.model_dump_json(indent=2)}"
        return self._call_model_structured(system_prompt, user_message, ArchitectureDoc)
