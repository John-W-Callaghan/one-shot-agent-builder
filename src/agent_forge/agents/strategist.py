"""Strategist agent — turns a raw idea into a structured project spec."""
from .base import BaseAgent
from ..config import ModelConfig
from ..schemas.spec import ProjectSpec


class Strategist(BaseAgent):
    def __init__(self):
        super().__init__(
            name="strategist",
            model=ModelConfig.STRATEGIST_MODEL,
            role_description="Senior product strategist who scopes projects",
        )

    def run(self, input_data: dict) -> ProjectSpec:
        idea = input_data["idea"]
        system_prompt = self._load_prompt()
        user_message = f"Here is the product idea:\n\n{idea}\n\nProduce the project specification."
        return self._call_model_structured(system_prompt, user_message, ProjectSpec)
