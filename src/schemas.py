from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    category: str
    severity: Severity
    description: str
    recommendation: str


class AgentFindings(BaseModel):
    """Shape an agent must return as JSON — used to build the OpenRouter json_schema."""

    score: int = Field(ge=0, le=100)
    summary: str
    findings: list[Finding] = Field(default_factory=list)


class AgentResult(BaseModel):
    agent_name: str
    model_used: str
    score: int = Field(ge=0, le=100, default=0)
    summary: str = ""
    findings: list[Finding] = Field(default_factory=list)
    error: Optional[str] = None


class FinalReport(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    executive_summary: str
    prioritized_recommendations: list[Finding] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    # Stubbed for a future multi-design A/B comparison feature — unused for now.
    design_label: str = "design"
    final_report: FinalReport
    agents: dict[str, AgentResult]
    partial_failure: bool = False
    errors: list[str] = Field(default_factory=list)
