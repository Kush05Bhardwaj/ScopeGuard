from dataclasses import dataclass

import pymupdf

from app.schemas.agreements import AgreementPage, AgreementParseResponse

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PDF_PAGES = 100


@dataclass
class AgreementParseError(Exception):
    status_code: int
    detail: str


def parse_agreement(filename: str, content: bytes) -> AgreementParseResponse:
    """Parse a supported agreement from bytes without persisting the upload."""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in {"txt", "pdf"}:
        raise AgreementParseError(415, "Only .txt and .pdf files are supported.")
    if not content:
        raise AgreementParseError(400, "The uploaded file is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise AgreementParseError(413, "The uploaded file exceeds the 10 MB limit.")

    if suffix == "txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise AgreementParseError(422, "The text file must use UTF-8 encoding.") from exc
        if not text.strip():
            raise AgreementParseError(422, "The uploaded file contains no extractable text.")
        return AgreementParseResponse(
            filename=filename,
            content_type="text/plain",
            page_count=1,
            text=text,
            pages=[AgreementPage(page_number=1, text=text)],
        )

    try:
        document = pymupdf.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise AgreementParseError(422, "The uploaded PDF is malformed or unreadable.") from exc

    try:
        if document.needs_pass:
            raise AgreementParseError(422, "Password-protected PDFs are not supported.")
        page_count = document.page_count
        if page_count > MAX_PDF_PAGES:
            raise AgreementParseError(422, "PDFs may contain no more than 100 pages.")

        pages = [
            AgreementPage(page_number=index + 1, text=page.get_text().strip())
            for index, page in enumerate(document)
        ]
    except AgreementParseError:
        raise
    except Exception as exc:
        raise AgreementParseError(422, "The uploaded PDF could not be parsed.") from exc
    finally:
        document.close()

    text = "\n\n".join(page.text for page in pages if page.text)
    if not text:
        raise AgreementParseError(422, "The PDF contains no extractable text. Scanned PDFs are not OCR processed.")

    return AgreementParseResponse(
        filename=filename,
        content_type="application/pdf",
        page_count=page_count,
        text=text,
        pages=pages,
    )
