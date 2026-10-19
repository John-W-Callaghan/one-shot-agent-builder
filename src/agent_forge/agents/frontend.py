"""Frontend Builder agent — generates frontend code from spec + design."""
from .base import BaseAgent
from ..config import ModelConfig
from ..schemas.spec import ArchitectureDoc, DesignSystem, ProjectSpec


class FrontendBuilder(BaseAgent):
    def __init__(self):
        super().__init__(
            name="frontend",
            model=ModelConfig.FRONTEND_MODEL,
            role_description="Senior frontend engineer",
        )

    def run(self, input_data: dict) -> dict[str, str]:
        """Generate frontend files.

        Optional keys `findings` and `previous_files` turn this into a revision
        pass for the Sentinel feedback loop.
        """
        spec: ProjectSpec = input_data["spec"]
        design: DesignSystem = input_data["design"]
        architecture: ArchitectureDoc = input_data["architecture"]

        system_prompt = self._load_prompt()
        user_message = (
            f"Generate the frontend code.\n\n"
            f"PROJECT SPEC:\n{spec.model_dump_json(indent=2)}\n\n"
            f"DESIGN SYSTEM:\n{design.model_dump_json(indent=2)}\n\n"
            f"API ENDPOINTS:\n{architecture.model_dump_json(indent=2)}\n\n"
            f"Respond with a JSON object where keys are file paths and values are file contents.\n"
            f"Include all component files, pages, styles, and config files.\n"
            f"Use the tech stack specified in the project spec."
        )
        if input_data.get("findings"):
            user_message += self._revision_request(input_data["findings"], input_data.get("previous_files", {}))

        return self._generate_files(system_prompt, user_message)
