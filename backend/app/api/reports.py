from fastapi import APIRouter, HTTPException

from app.schemas.report import ChangeOrderReportRequest, ChangeOrderReportResponse
from app.services.report_service import generate_change_order

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/change-order", response_model=ChangeOrderReportResponse)
def create_change_order(
    request: ChangeOrderReportRequest,
) -> ChangeOrderReportResponse:
    try:
        return generate_change_order(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
