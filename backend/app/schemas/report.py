from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ScopeCategory = Literal["in_scope", "potential_scope_change", "needs_review"]


class ReportEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quote: str = Field(min_length=1, max_length=2_000)
    explanation: str = Field(min_length=1, max_length=1_000)


class ChangeOrderReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_name: str = Field(min_length=1, max_length=200)
    client_name: str = Field(default="", max_length=200)
    agreement_reference: str = Field(default="Not provided", max_length=500)
    agreement_text: str = Field(min_length=1, max_length=100_000)
    client_request: str = Field(min_length=1, max_length=10_000)
    analysis_category: ScopeCategory
    analysis_summary: str = Field(min_length=1, max_length=5_000)
    evidence: list[ReportEvidence] = Field(default_factory=list, max_length=25)
    proposed_work: str = Field(default="", max_length=5_000)
    estimated_cost: str = Field(default="To be agreed", max_length=200)
    estimated_timeline: str = Field(default="To be agreed", max_length=200)

    @field_validator(
        "project_name", "agreement_text", "client_request", "analysis_summary"
    )
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must contain non-whitespace text.")
        return value


class ChangeOrderReportResponse(BaseModel):
    title: str
    markdown: str
