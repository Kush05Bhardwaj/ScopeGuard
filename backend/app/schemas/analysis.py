from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ScopeCategory = Literal[
    "in_scope",
    "potential_scope_change",
    "needs_review",
]


class ScopeAnalysisRequest(BaseModel):
    agreement_text: str = Field(min_length=1, max_length=100_000)
    client_request: str = Field(min_length=1, max_length=10_000)

    @field_validator("agreement_text", "client_request")
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field must contain non-whitespace text.")
        return value


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quote: str = Field(min_length=1, max_length=2_000)
    explanation: str = Field(
        default="This passage is quoted exactly from the agreement; review its relevance to the request.",
        min_length=1,
        max_length=1_000,
    )


class ScopeAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: ScopeCategory
    summary: str = Field(min_length=1, max_length=1_000)
    reasoning: str = Field(min_length=1, max_length=5_000)
    evidence: list[EvidenceItem] = Field(max_length=25)
    model: str = Field(min_length=1, max_length=200)
    requires_human_review: bool
