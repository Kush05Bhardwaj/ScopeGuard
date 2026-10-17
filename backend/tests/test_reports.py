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
        "analysis": {
            "category": "potential_scope_change",
            "summary": "Billing is outside the stated scope.",
            "reasoning": "The agreement excludes this feature.",
            "evidence": [
                {
                    "quote": "No subscription billing.",
                    "explanation": "The agreement excludes the requested feature.",
                }
            ],
            "model": "gemma3:4b",
            "requires_human_review": True,
        },
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


def test_change_order_rejects_missing_analysis_response():
    payload = report_payload()
    del payload["analysis"]

    response = client.post("/api/reports/change-order", json=payload)

    assert response.status_code == 422


def test_change_order_rejects_unverified_evidence():
    response = client.post(
        "/api/reports/change-order",
        json=report_payload(
            analysis={
                **report_payload()["analysis"],
                "evidence": [
                    {"quote": "Invented billing promise.", "explanation": "Not in source."}
                ],
            }
        ),
    )

    assert response.status_code == 422


def test_change_order_without_evidence_requests_human_review():
    response = client.post(
        "/api/reports/change-order",
        json=report_payload(
            analysis={
                **report_payload()["analysis"],
                "category": "needs_review",
                "summary": "The request needs review.",
                "evidence": [],
                "requires_human_review": True,
            }
        ),
    )

    assert response.status_code == 200
    assert "No verified agreement passage was returned. Manual review is required." in response.json()["markdown"]
    assert "Human review required:** Yes" in response.json()["markdown"]


def test_change_order_requires_a_validated_analysis_response():
    payload = report_payload()
    del payload["analysis"]["model"]

    response = client.post("/api/reports/change-order", json=payload)

    assert response.status_code == 422


def test_change_order_rejects_invalid_analysis_category():
    payload = report_payload()
    payload["analysis"]["category"] = "definitely_out_of_scope"

    response = client.post("/api/reports/change-order", json=payload)

    assert response.status_code == 422


def test_change_order_rejects_confident_analysis_without_evidence():
    payload = report_payload(
        analysis={
            **report_payload()["analysis"],
            "category": "in_scope",
            "evidence": [],
            "requires_human_review": False,
        }
    )

    response = client.post("/api/reports/change-order", json=payload)

    assert response.status_code == 422


def test_change_order_rejects_analysis_that_skips_required_human_review():
    payload = report_payload(
        analysis={**report_payload()["analysis"], "requires_human_review": False}
    )

    response = client.post("/api/reports/change-order", json=payload)

    assert response.status_code == 422
