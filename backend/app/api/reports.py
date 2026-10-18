import json
import re

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import ValidationError

from app.schemas.report import (
    ChangeOrderPdfRequest,
    ChangeOrderReportRequest,
    ChangeOrderReportResponse,
)
from app.services.estimate_service import (
    InvalidEstimateError,
    suggest_change_order_estimate,
)
from app.services.report_service import generate_change_order
from app.services.pdf_service import render_proposal_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/change-order/pdf", response_class=Response)
def export_change_order_pdf(request: ChangeOrderPdfRequest) -> Response:
    filename = re.sub(r"[^A-Za-z0-9._-]+", "-", request.filename).strip(".-")
    if not filename:
        filename = "scopeguard-change-order"
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"
    pdf_bytes = render_proposal_pdf(request.markdown)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/change-order", response_model=ChangeOrderReportResponse)
async def create_change_order(
    request: ChangeOrderReportRequest,
) -> ChangeOrderReportResponse:
    try:
        # Reject unverified analyses before sending any proposal data for estimates.
        generate_change_order(request)
        estimate_assumptions = ""
        cost = request.estimated_cost.strip()
        timeline = request.estimated_timeline.strip()
        needs_model_estimate = request.auto_estimate and (
            not cost or cost == "To be agreed" or not timeline or timeline == "To be agreed"
        )
        if needs_model_estimate:
            estimate = await suggest_change_order_estimate(
                agreement_text=request.agreement_text,
                client_request=request.client_request,
                proposed_work=request.proposed_work.strip()
                or "To be defined and approved by both parties.",
                analysis_category=request.analysis.category,
                analysis_summary=request.analysis.summary,
                analysis_reasoning=request.analysis.reasoning,
                verified_evidence=[item.model_dump() for item in request.analysis.evidence],
                estimate_context=request.estimate_context,
            )
            request = request.model_copy(
                update={
                    "estimated_cost": cost if cost and cost != "To be agreed" else estimate.estimated_cost,
                    "estimated_timeline": timeline if timeline and timeline != "To be agreed" else estimate.estimated_timeline,
                }
            )
            estimate_assumptions = estimate.assumptions
        return generate_change_order(request, estimate_assumptions)
    except (InvalidEstimateError, ValidationError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail="The model returned an invalid estimate.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ollama is unavailable. Start Ollama to generate estimate suggestions, or turn off automatic estimates.",
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Local estimate generation timed out.") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="The local model service returned an error.") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Could not complete the local model request.") from exc
    except (KeyError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="The model returned an invalid estimate.") from exc
