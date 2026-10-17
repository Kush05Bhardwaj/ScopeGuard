import httpx
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.schemas.analysis import ScopeAnalysisRequest, ScopeAnalysisResponse
from app.services.analysis_service import run_scope_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/scope", response_model=ScopeAnalysisResponse)
async def analyze_project_scope(request: ScopeAnalysisRequest) -> ScopeAnalysisResponse:
    try:
        return await run_scope_analysis(request)
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ollama is unavailable. Start Ollama and verify that the configured model is installed.",
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Local model inference timed out.") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="The local model service returned an error.") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Could not complete the local model request.") from exc
    except (ValidationError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="The model returned an invalid analysis response.") from exc
