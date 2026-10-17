from pydantic import BaseModel


class AgreementPage(BaseModel):
    page_number: int
    text: str


class AgreementParseResponse(BaseModel):
    filename: str
    content_type: str
    page_count: int
    text: str
    pages: list[AgreementPage]
