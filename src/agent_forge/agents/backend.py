"""Backend Builder agent — generates backend code, API routes, DB schema."""
from .base import BaseAgent
from ..config import ModelConfig
from ..schemas.spec import ArchitectureDoc, ProjectSpec


class BackendBuilder(BaseAgent):
    def __init__(self):
        super().__init__(
            name="backend",
            model=ModelConfig.BACKEND_MODEL,
            role_description="Senior backend engineer",
        )

    def run(self, input_data: dict) -> dict[str, str]:
        """Generate backend files.

        Optional keys `findings` and `previous_files` turn this into a revision
        pass for the Sentinel feedback loop.
        """
        spec: ProjectSpec = input_data["spec"]
        architecture: ArchitectureDoc = input_data["architecture"]

        system_prompt = self._load_prompt()
        user_message = (
            f"Generate the backend code.\n\n"
            f"PROJECT SPEC:\n{spec.model_dump_json(indent=2)}\n\n"
            f"ARCHITECTURE:\n{architecture.model_dump_json(indent=2)}\n\n"
            f"Respond with a JSON object where keys are file paths and values are file contents.\n"
            f"Include API routes, database schema/migrations, middleware, and config files.\n"
            f"Use the tech stack specified in the project spec."
        )
        if input_data.get("findings"):
            user_message += self._revision_request(input_data["findings"], input_data.get("previous_files", {}))

        return self._generate_files(system_prompt, user_message)
