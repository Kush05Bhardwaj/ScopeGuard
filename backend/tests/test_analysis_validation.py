import asyncio

import pytest
from pydantic import ValidationError

from app.schemas.analysis import EvidenceItem, ScopeAnalysisRequest, ScopeAnalysisResponse
from app.services import analysis_service
from app.services.analysis_service import run_scope_analysis


def test_evidence_quote_must_exist_in_agreement():
    agreement = "No administrator dashboard is included."
    evidence = EvidenceItem(
        quote="No administrator dashboard is included.",
        explanation="The agreement excludes the dashboard.",
    )

    assert evidence.quote in agreement


def test_invented_evidence_is_not_in_source():
    agreement = "The project includes five responsive pages."
    invented_quote = "The project includes a payment gateway."

    assert invented_quote not in agreement


def test_evidence_without_model_explanation_gets_neutral_review_text():
    evidence = EvidenceItem.model_validate({"quote": "No dashboard is included."})

    assert evidence.explanation == (
        "This passage is quoted exactly from the agreement; review its relevance to the request."
    )


def test_analysis_response_requires_valid_category():
    result = ScopeAnalysisResponse(
        category="needs_review",
        summary="The request is ambiguous.",
        reasoning="The agreement does not define professional design.",
        evidence=[],
        model="test-model",
        requires_human_review=True,
    )

    assert result.category == "needs_review"
    assert result.requires_human_review is True

    with pytest.raises(ValidationError):
        ScopeAnalysisResponse.model_validate(
            {
                "category": "definitely_out_of_scope",
                "summary": "Unsupported category.",
                "reasoning": "The agreement says nothing about this.",
                "evidence": [],
                "model": "test-model",
                "requires_human_review": False,
            }
        )


def test_service_removes_unverified_evidence_and_requires_review(monkeypatch):
    agreement = "Five responsive pages are included."

    async def fake_analyze_scope(**_kwargs):
        return {
            "category": "in_scope",
            "summary": "The request appears covered.",
            "reasoning": "The model supplied one quote.",
            "evidence": [
                {"quote": "A free payment gateway is included.", "explanation": "Model claim."}
            ],
            "model": "test-model",
            "requires_human_review": False,
        }

    monkeypatch.setattr(analysis_service, "analyze_scope", fake_analyze_scope)
    request = ScopeAnalysisRequest(
        agreement_text=agreement,
        client_request="Add online payments.",
    )

    result = asyncio.run(run_scope_analysis(request))

    assert result.evidence == []
    assert result.category == "needs_review"
    assert result.requires_human_review is True


def test_in_scope_without_evidence_is_downgraded_to_review(monkeypatch):
    async def fake_analyze_scope(**_kwargs):
        return {
            "category": "in_scope",
            "summary": "The request is included.",
            "reasoning": "No passage was identified.",
            "evidence": [],
            "model": "test-model",
            "requires_human_review": False,
        }

    monkeypatch.setattr(analysis_service, "analyze_scope", fake_analyze_scope)
    request = ScopeAnalysisRequest(
        agreement_text="A website will be built.",
        client_request="Add subscription billing.",
    )

    result = asyncio.run(run_scope_analysis(request))

    assert result.category == "needs_review"
    assert result.requires_human_review is True


def test_potential_scope_change_requires_human_review(monkeypatch):
    async def fake_analyze_scope(**_kwargs):
        return {
            "category": "potential_scope_change",
            "summary": "The request appears excluded.",
            "reasoning": "An exact exclusion passage was returned.",
            "evidence": [
                {"quote": "No dashboard is included.", "explanation": "The agreement excludes it."}
            ],
            "model": "test-model",
            "requires_human_review": False,
        }

    monkeypatch.setattr(analysis_service, "analyze_scope", fake_analyze_scope)
    request = ScopeAnalysisRequest(
        agreement_text="No dashboard is included.",
        client_request="Add a dashboard.",
    )

    result = asyncio.run(run_scope_analysis(request))

    assert result.category == "potential_scope_change"
    assert result.requires_human_review is True


def test_malformed_analysis_response_fails_schema_validation(monkeypatch):
    async def fake_analyze_scope(**_kwargs):
        return {"category": "in_scope", "unexpected": "unvalidated response"}

    monkeypatch.setattr(analysis_service, "analyze_scope", fake_analyze_scope)
    request = ScopeAnalysisRequest(
        agreement_text="Five responsive pages are included.",
        client_request="Make the pages responsive.",
    )

    with pytest.raises(ValidationError):
        asyncio.run(run_scope_analysis(request))


def test_unreadable_model_text_is_replaced_and_requires_review(monkeypatch):
    async def fake_analyze_scope(**_kwargs):
        return {
            "category": "in_scope",
            "summary": "The request is covered.",
            "reasoning": "The agreement says \ufffd3. Responsive layouts.",
            "evidence": [
                {"quote": "Responsive layouts.", "explanation": "Exact phrase \ufffd"}
            ],
            "model": "test-model",
            "requires_human_review": False,
        }

    monkeypatch.setattr(analysis_service, "analyze_scope", fake_analyze_scope)
    request = ScopeAnalysisRequest(
        agreement_text="Responsive layouts.",
        client_request="Ensure the layout is responsive.",
    )

    result = asyncio.run(run_scope_analysis(request))

    assert result.category == "needs_review"
    assert result.requires_human_review is True
    assert "\ufffd" not in result.reasoning
    assert "\ufffd" not in result.evidence[0].explanation
