"""Pipeline orchestrator — runs the 5-phase agent pipeline."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .schemas.contracts import PipelineState, normalize_path
from .schemas.spec import ReviewFinding
from .agents.strategist import Strategist
from .agents.architect import Architect
from .agents.designer import Designer
from .agents.frontend import FrontendBuilder
from .agents.backend import BackendBuilder
from .agents.sentinel import Sentinel
from .agents.shipper import Shipper

console = Console()

BUILDERS = ("frontend", "backend")



class Pipeline:
    """Orchestrates the full idea-to-code pipeline."""

    def __init__(self, output_dir: str = "output", max_review_iterations: int = 3):
        self.output_dir = Path(output_dir)
        self.max_review_iterations = max_review_iterations
        self.state: PipelineState | None = None

    def run(self, idea: str) -> PipelineState:
        """Execute the full pipeline."""
        self.state = PipelineState(
            idea=idea,
            output_dir=str(self.output_dir),
            max_review_iterations=self.max_review_iterations,
        )
        start_time = time.time()

        console.print(Panel(f"[bold green]🚀 Agent Forge Pipeline[/bold green]\n\n{idea}", expand=False))

        # ── Phase 1: Scope ──
        self._phase("Phase 1 — Scope", "Strategist is analyzing the idea...")
        self.state.spec = Strategist().run({"idea": idea})
        self.state.log("strategist", f"Scoped project: {self.state.spec.project_name}")
        console.print(f"  [green]✓[/green] Project scoped: [bold]{self.state.spec.project_name}[/bold]")
        console.print(f"    Type: {self.state.spec.project_type.value}")
        console.print(f"    Features: {len(self.state.spec.core_features)}")
        console.print(f"    Tech decisions: {len(self.state.spec.tech_stack)}")

        # ── Phase 2: Design (Architect and Designer run in parallel) ──
        self._phase("Phase 2 — Design", "Architect and Designer working in parallel...")
        with ThreadPoolExecutor(max_workers=2) as pool:
            architecture_future = pool.submit(Architect().run, {"spec": self.state.spec})
            design_future = pool.submit(Designer().run, {"spec": self.state.spec})
            self.state.architecture = architecture_future.result()
            self.state.design = design_future.result()

        self.state.log("architect", f"Designed {len(self.state.architecture.api_endpoints)} endpoints, {len(self.state.architecture.database_schema)} tables")
        console.print(f"  [green]✓[/green] Architecture: {len(self.state.architecture.api_endpoints)} endpoints, {len(self.state.architecture.database_schema)} tables")
        self.state.log("designer", f"Designed {len(self.state.design.component_list)} components")
        console.print(f"  [green]✓[/green] Design system: {len(self.state.design.component_list)} components, {len(self.state.design.page_routes)} pages")

        # ── Phase 3: Build (Frontend and Backend run in parallel) ──
        self._phase("Phase 3 — Build", "Frontend and Backend builders coding in parallel...")
        builder_files = self._run_builders({builder: None for builder in BUILDERS})
        for builder in BUILDERS:
            files = builder_files[builder]
            self.state.add_files(builder, files)
            self.state.log(builder, f"Generated {len(files)} {builder} files")
            console.print(f"  [green]✓[/green] {builder.capitalize()}: {len(files)} files")

        # ── Phase 4: Harden (with feedback loop) ──
        self._phase("Phase 4 — Harden", "Sentinel reviewing all code...")

        sentinel = Sentinel()
        while self.state.review_iteration < self.state.max_review_iterations:
            self.state.review_iteration += 1
            console.print(f"  [yellow]🔍 Review pass {self.state.review_iteration}/{self.state.max_review_iterations}[/yellow]")

            self.state.audit = sentinel.run({"files": self.state.generated_files})
            self.state.log("sentinel", f"Pass {self.state.review_iteration}: {len(self.state.audit.findings)} findings, passed={self.state.audit.passed}")

            critical = [f for f in self.state.audit.findings if f.severity == "critical"]
            warning_count = sum(1 for f in self.state.audit.findings if f.severity == "warning")
            console.print(f"    Findings: {len(critical)} critical, {warning_count} warnings")

            if self.state.audit.passed:
                console.print(f"  [green]✓[/green] Code passed review")
                break

            if self.state.review_iteration >= self.state.max_review_iterations:
                console.print(f"  [yellow]⚠ Max review iterations reached — proceeding with warnings[/yellow]")
                break

            # Feed critical findings back to the builders that own the affected files.
            console.print(f"  [yellow]↩ Sending {len(critical)} critical findings back to builders...[/yellow]")
            self.state.log("sentinel", f"Feedback loop: {len(critical)} critical issues sent to builders")
            self._apply_fixes(critical)

        # ── Phase 5: Ship ──
        self._phase("Phase 5 — Ship", "Shipper generating docs and deploy config...")

        ship_files = Shipper().run({
            "spec": self.state.spec,
            "architecture": self.state.architecture,
            "files": self.state.generated_files,
        })
        self.state.add_files("shipper", ship_files)
        self.state.log("shipper", f"Generated {len(ship_files)} shipping files")
        console.print(f"  [green]✓[/green] Docs & deploy config: {len(ship_files)} files")

        # ── Write all files to disk ──
        self._write_files()

        elapsed = time.time() - start_time
        total_files = len(self.state.generated_files)
        console.print(Panel(
            f"[bold green]✅ Pipeline complete![/bold green]\n\n"
            f"Project: {self.state.spec.project_name}\n"
            f"Files generated: {total_files}\n"
            f"Review iterations: {self.state.review_iteration}\n"
            f"Time: {elapsed:.1f}s\n"
            f"Output: {self.output_dir}/",
            expand=False,
        ))

        # Write pipeline log
        log_path = self.output_dir / ".agent-forge-log.json"
        log_path.write_text(json.dumps(self.state.logs, indent=2))

        return self.state

    def _builder_input(self, builder: str) -> dict:
        data = {"spec": self.state.spec, "architecture": self.state.architecture}
        if builder == "frontend":
            data["design"] = self.state.design
        return data

    def _run_builders(self, findings_by_builder: dict[str, list[ReviewFinding] | None]) -> dict[str, dict[str, str]]:
        """Run the given builders in parallel. A non-None findings list makes it a revision pass."""
        agents = {"frontend": FrontendBuilder, "backend": BackendBuilder}
        with ThreadPoolExecutor(max_workers=len(findings_by_builder)) as pool:
            futures = {}
            for builder, findings in findings_by_builder.items():
                input_data = self._builder_input(builder)
                if findings:
                    input_data["findings"] = findings
                    input_data["previous_files"] = {
                        path: content for path, content in self.state.generated_files.items()
                        if self.state.file_owners.get(path) == builder
                    }
                futures[builder] = pool.submit(agents[builder]().run, input_data)
            return {builder: future.result() for builder, future in futures.items()}

    def _apply_fixes(self, findings: list[ReviewFinding]):
        """Route findings to the builder that owns each file, then merge the revised files."""
        routed: dict[str, list[ReviewFinding]] = {}
        for finding in findings:
            owner = self.state.file_owners.get(normalize_path(finding.file_path) or "")
            # Findings on unknown or cross-cutting files go to both builders.
            targets = [owner] if owner in BUILDERS else list(BUILDERS)
            for target in targets:
                routed.setdefault(target, []).append(finding)

        revised = self._run_builders(routed)
        for builder, files in revised.items():
            self.state.add_files(builder, files)
            self.state.log(builder, f"Revised {len(files)} files from {len(routed[builder])} findings")
            console.print(f"    [green]✓[/green] {builder.capitalize()} revised {len(files)} files")

    def _phase(self, name: str, description: str):
        console.print(f"\n[bold blue]{'─'*50}[/bold blue]")
        console.print(f"[bold blue]{name}[/bold blue]")
        console.print(f"[dim]{description}[/dim]")

    def _write_files(self):
        """Write all generated files to the output directory."""
        console.print(f"\n[bold]📁 Writing {len(self.state.generated_files)} files to {self.output_dir}/[/bold]")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for filepath, content in sorted(self.state.generated_files.items()):
            clean_path = normalize_path(filepath)
            if clean_path is None:
                console.print(f"  [red]skipped unsafe path: {filepath}[/red]")
                self.state.log("orchestrator", f"Skipped unsafe path: {filepath}")
                continue
            full_path = self.output_dir / clean_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            console.print(f"  [dim]wrote {clean_path}[/dim]")
