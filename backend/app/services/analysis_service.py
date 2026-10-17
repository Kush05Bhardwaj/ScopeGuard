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
    elif result.category == "needs_review" and not result.requires_human_review:
        result = result.model_copy(update={"requires_human_review": True})

    return result
