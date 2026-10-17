from app.schemas.analysis import ScopeAnalysisRequest, ScopeAnalysisResponse
from app.services.ollama_service import analyze_scope


async def run_scope_analysis(request: ScopeAnalysisRequest) -> ScopeAnalysisResponse:
    raw = await analyze_scope(
        agreement_text=request.agreement_text,
        client_request=request.client_request,
    )
    result = ScopeAnalysisResponse.model_validate(raw)

    verified_evidence = [
        item for item in result.evidence if item.quote in request.agreement_text
    ]
    if len(verified_evidence) != len(result.evidence):
        verification_note = " Some model-generated evidence could not be verified against the original agreement."
        result = result.model_copy(
            update={
                "category": "needs_review",
                "evidence": verified_evidence,
                "requires_human_review": True,
                "reasoning": (result.reasoning + verification_note)[:5_000],
            }
        )

    if not result.evidence:
        result = result.model_copy(
            update={
                "category": "needs_review",
                "requires_human_review": True,
            }
        )
    elif (
        result.category in {"needs_review", "potential_scope_change"}
        and not result.requires_human_review
    ):
        result = result.model_copy(update={"requires_human_review": True})

    unreadable_text = any(
        "\ufffd" in value
        for value in (
            result.summary,
            result.reasoning,
            *(item.explanation for item in result.evidence),
        )
    )
    if unreadable_text:
        result = result.model_copy(
            update={
                "category": "needs_review",
                "summary": "The model returned partially unreadable text.",
                "reasoning": (
                    "Review the agreement and quoted passages manually before relying on this analysis."
                ),
                "evidence": [
                    item.model_copy(
                        update={
                            "explanation": (
                                "This passage is quoted exactly from the agreement; "
                                "review its relevance to the request."
                            )
                        }
                    )
                    if "\ufffd" in item.explanation
                    else item
                    for item in result.evidence
                ],
                "requires_human_review": True,
            }
        )

    return result
