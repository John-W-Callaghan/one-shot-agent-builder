"""Sentinel agent — reviews all generated code for bugs, security, accessibility."""
from .base import BaseAgent
from ..config import ModelConfig
from ..schemas.spec import AuditReport


class Sentinel(BaseAgent):
    def __init__(self):
        super().__init__(
            name="sentinel",
            model=ModelConfig.SENTINEL_MODEL,
            role_description="Senior code reviewer, security auditor, and QA engineer",
        )

    def run(self, input_data: dict) -> AuditReport:
        files: dict[str, str] = input_data["files"]

        # Build a combined code listing for review
        code_listing = ""
        for filepath, content in sorted(files.items()):
            code_listing += f"\n{'='*60}\n📄 {filepath}\n{'='*60}\n{content}\n"

        system_prompt = self._load_prompt()
        user_message = (
            f"Review ALL of the following generated code.\n\n"
            f"Check for: bugs, security vulnerabilities, accessibility issues, "
            f"performance problems, missing error handling, inconsistent patterns, "
            f"and code style issues.\n\n"
            f"Use the exact file paths shown in the listing for each finding's file_path.\n\n"
            f"CODE TO REVIEW:\n{code_listing}"
        )

        report = self._call_model_structured(system_prompt, user_message, AuditReport)
        # Enforce the rule rather than trusting the model's self-reported flag.
        report.passed = not any(f.severity == "critical" for f in report.findings)
        return report
