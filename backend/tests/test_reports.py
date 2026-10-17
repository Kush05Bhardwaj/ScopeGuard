from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

AGREEMENT = "The original scope includes five responsive pages. No subscription billing."


def report_payload(**overrides):
    payload = {
        "project_name": "Website Project",
        "client_name": "Example Client",
        "agreement_reference": "agreement.pdf",
        "agreement_text": AGREEMENT,
        "client_request": "Add subscription billing.",
        "analysis_category": "potential_scope_change",
        "analysis_summary": "Billing is outside the stated scope.",
        "evidence": [
            {
                "quote": "No subscription billing.",
                "explanation": "The agreement excludes the requested feature.",
            }
        ],
        "proposed_work": "Implement subscription billing.",
        "estimated_cost": "To be agreed",
        "estimated_timeline": "To be agreed",
    }
    payload.update(overrides)
    return payload


def test_change_order_report_contains_required_sections_and_grounded_evidence():
    response = client.post("/api/reports/change-order", json=report_payload())

    assert response.status_code == 200
    report = response.json()
    assert "Website Project" in report["title"]
    assert "Example Client" in report["markdown"]
    assert "agreement.pdf" in report["markdown"]
    assert "Add subscription billing." in report["markdown"]
    assert "No subscription billing." in report["markdown"]
    assert "Implement subscription billing." in report["markdown"]
    assert "To be agreed" in report["markdown"]
    assert "Approval and Next Steps" in report["markdown"]


def test_missing_work_cost_and_timeline_use_explicit_placeholders():
    response = client.post(
        "/api/reports/change-order",
        json=report_payload(proposed_work="", estimated_cost="", estimated_timeline=""),
    )

    assert response.status_code == 200
    markdown = response.json()["markdown"]
    assert "To be defined and approved by both parties." in markdown
    assert markdown.count("To be agreed") >= 2


def test_change_order_rejects_empty_project_name():
    response = client.post(
        "/api/reports/change-order",
        json=report_payload(project_name=""),
    )

    assert response.status_code == 422


def test_change_order_rejects_unverified_evidence():
    response = client.post(
        "/api/reports/change-order",
        json=report_payload(
            evidence=[
                {"quote": "Invented billing promise.", "explanation": "Not in source."}
            ]
        ),
    )

    assert response.status_code == 422


def test_change_order_without_evidence_requests_human_review():
    response = client.post(
        "/api/reports/change-order",
        json=report_payload(evidence=[]),
    )

    assert response.status_code == 200
    assert "No verified agreement passage was returned. Manual review is required." in response.json()["markdown"]
