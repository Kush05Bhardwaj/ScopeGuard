import io

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.agreement_parser import MAX_FILE_SIZE

client = TestClient(app)


def make_pdf(*page_texts: str) -> bytes:
    document = pymupdf.open()
    for text in page_texts:
        page = document.new_page()
        page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_parse_txt_upload_returns_structured_text():
    response = client.post(
        "/api/agreements/parse",
        files={"file": ("agreement.txt", b"Agreed: five responsive pages.", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "agreement.txt",
        "content_type": "text/plain",
        "page_count": 1,
        "text": "Agreed: five responsive pages.",
        "pages": [{"page_number": 1, "text": "Agreed: five responsive pages."}],
    }


def test_parse_pdf_upload_preserves_page_references():
    response = client.post(
        "/api/agreements/parse",
        files={"file": ("agreement.pdf", make_pdf("First page clause.", "Second page clause."), "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "application/pdf"
    assert data["page_count"] == 2
    assert [page["page_number"] for page in data["pages"]] == [1, 2]
    assert [page["text"] for page in data["pages"]] == ["First page clause.", "Second page clause."]


@pytest.mark.parametrize(
    ("filename", "content", "expected_status"),
    [
        ("agreement.docx", b"text", 415),
        ("empty.txt", b"", 400),
        ("blank.txt", b" \n\t", 422),
        ("broken.pdf", b"not a pdf", 422),
        ("scanned.pdf", make_pdf(""), 422),
        ("bad-encoding.txt", b"\xff\xfe", 422),
        ("large.txt", b"x" * (MAX_FILE_SIZE + 1), 413),
        ("too-many-pages.pdf", make_pdf(*(["page"] * 101)), 422),
    ],
    ids=["unsupported-extension", "empty", "blank-text", "malformed-pdf", "scanned-pdf", "bad-encoding", "oversized", "too-many-pages"],
)
def test_reject_invalid_uploads(filename: str, content: bytes, expected_status: int):
    response = client.post(
        "/api/agreements/parse",
        files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
    )

    assert response.status_code == expected_status


def test_pdf_error_explains_ocr_limitation():
    response = client.post(
        "/api/agreements/parse",
        files={"file": ("scanned.pdf", make_pdf(""), "application/pdf")},
    )

    assert "not OCR processed" in response.json()["detail"]
