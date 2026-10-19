"""Designer agent — creates the UI/UX design system from the spec."""
from .base import BaseAgent
from ..config import ModelConfig
from ..schemas.spec import DesignSystem, ProjectSpec


class Designer(BaseAgent):
    def __init__(self):
        super().__init__(
            name="designer",
            model=ModelConfig.DESIGNER_MODEL,
            role_description="Senior UI/UX designer with modern web expertise",
        )

    def run(self, input_data: dict) -> DesignSystem:
        spec: ProjectSpec = input_data["spec"]
        system_prompt = self._load_prompt()
        user_message = f"Create the design system for this project:\n\n{spec.model_dump_json(indent=2)}"
        return self._call_model_structured(system_prompt, user_message, DesignSystem)
