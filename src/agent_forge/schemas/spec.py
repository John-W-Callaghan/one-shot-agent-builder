"""Pydantic models for structured agent outputs."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProjectType(str, Enum):
    WEB_APP = "web_app"
    API = "api"
    CLI = "cli"
    FULLSTACK = "fullstack"


class TechDecision(BaseModel):
    """A technology choice with reasoning."""
    category: str = Field(description="e.g. 'framework', 'database', 'auth'")
    choice: str = Field(description="e.g. 'Next.js', 'Supabase', 'Clerk'")
    reasoning: str = Field(description="Why this choice fits the project")


class UserStory(BaseModel):
    """A user story in standard format."""
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: list[str]


class ProjectSpec(BaseModel):
    """Output of the Strategist agent — the project scope."""
    project_name: str
    project_type: ProjectType
    summary: str = Field(description="2-3 sentence project description")
    core_features: list[str] = Field(description="3-7 must-have features")
    tech_stack: list[TechDecision]
    user_stories: list[UserStory]
    out_of_scope: list[str] = Field(description="Explicitly excluded features")
    file_structure: list[str] = Field(description="Proposed directory tree as flat list")


class ComponentDesign(BaseModel):
    """A UI component specification."""
    name: str
    purpose: str
    props: dict[str, str] = Field(description="Prop name -> type description")
    children: list[str] = Field(default_factory=list)
    notes: str = ""


class DesignSystem(BaseModel):
    """Output of the Designer agent — UI/UX decisions."""
    color_palette: dict[str, str] = Field(description="Token name -> hex value")
    typography: dict[str, str] = Field(description="Role -> font spec, e.g. 'heading' -> 'Inter 24px bold'")
    layout_approach: str = Field(description="e.g. 'mobile-first responsive grid'")
    component_list: list[ComponentDesign]
    page_routes: list[dict[str, str]] = Field(description="List of {path, page_name, description}")
    accessibility_notes: list[str]


class APIEndpoint(BaseModel):
    """An API endpoint specification."""
    method: str
    path: str
    description: str
    request_body: Optional[dict] = None
    response_shape: dict
    auth_required: bool = True


class DatabaseTable(BaseModel):
    """A database table specification."""
    name: str
    columns: list[dict[str, str]] = Field(description="List of {name, type, constraints}")
    relationships: list[str] = Field(default_factory=list)


class ArchitectureDoc(BaseModel):
    """Output of the Architect agent — system design."""
    system_overview: str
    api_endpoints: list[APIEndpoint]
    database_schema: list[DatabaseTable]
    auth_strategy: str
    deployment_target: str = Field(description="e.g. 'Vercel + Supabase'")
    environment_variables: list[dict[str, str]]
    third_party_services: list[dict[str, str]]


class ReviewFinding(BaseModel):
    """A single finding from the Sentinel review."""
    severity: str = Field(description="'critical', 'warning', or 'suggestion'")
    category: str = Field(description="'bug', 'security', 'accessibility', 'performance', 'style'")
    file_path: str
    line_range: Optional[str] = None
    description: str
    fix_instruction: str


class AuditReport(BaseModel):
    """Output of the Sentinel agent — review results."""
    passed: bool = Field(description="True if no critical findings")
    findings: list[ReviewFinding]
    metrics: dict[str, str] = Field(description="e.g. {'test_coverage': '84%', 'lighthouse_score': '92'}")
    summary: str
