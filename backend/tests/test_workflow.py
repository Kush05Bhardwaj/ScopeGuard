from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SAMPLE_AGREEMENT = Path(__file__).parents[2] / "sample_data" / "sample_agreement.txt"


def test_agreement_analysis_and_report_workflow(monkeypatch):
    agreement_bytes = SAMPLE_AGREEMENT.read_bytes()
    agreement_text = agreement_bytes.decode("utf-8")
    exact_quote = "No administrator dashboard."

    async def fake_analyze_scope(*, agreement_text: str, client_request: str):
        assert client_request == "Add an administrator dashboard."
        return {
            "category": "potential_scope_change",
            "summary": "The request asks for an excluded dashboard.",
            "reasoning": "The agreement explicitly excludes this feature.",
            "evidence": [
                {"quote": exact_quote, "explanation": "The agreement exclusion matches the request."}
            ],
            "model": "test-model",
            "requires_human_review": False,
        }

    monkeypatch.setattr("app.services.analysis_service.analyze_scope", fake_analyze_scope)
    upload = client.post(
        "/api/agreements/parse",
        files={"file": ("sample_agreement.txt", agreement_bytes, "text/plain")},
    )
    assert upload.status_code == 200
    parsed = upload.json()
    assert parsed["text"] == agreement_text

    analysis = client.post(
        "/api/analysis/scope",
        json={
            "agreement_text": parsed["text"],
            "client_request": "Add an administrator dashboard.",
        },
    )
    assert analysis.status_code == 200
    analysis_result = analysis.json()
    assert analysis_result["evidence"][0]["quote"] == exact_quote
    assert exact_quote in agreement_text

    report = client.post(
        "/api/reports/change-order",
        json={
            "project_name": "Small Business Website",
            "client_name": "Example Client",
            "agreement_reference": parsed["filename"],
            "agreement_text": parsed["text"],
            "client_request": "Add an administrator dashboard.",
            "analysis": analysis_result,
        },
    )
    assert report.status_code == 200
    markdown = report.json()["markdown"]
    assert "Small Business Website" in markdown
    assert exact_quote in markdown
    assert "To be agreed" in markdown
