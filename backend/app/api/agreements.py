from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.agreements import AgreementParseResponse
from app.services.agreement_parser import (
    MAX_FILE_SIZE,
    AgreementParseError,
    parse_agreement,
)

router = APIRouter(prefix="/api/agreements", tags=["agreements"])


@router.post("/parse", response_model=AgreementParseResponse)
async def parse_uploaded_agreement(file: UploadFile = File(...)) -> AgreementParseResponse:
    filename = file.filename or ""
    try:
        content = bytearray()
        while chunk := await file.read(64 * 1024):
            content.extend(chunk)
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="The uploaded file exceeds the 10 MB limit.")
        return parse_agreement(filename, bytes(content))
    except HTTPException:
        raise
    except AgreementParseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    finally:
        await file.close()
