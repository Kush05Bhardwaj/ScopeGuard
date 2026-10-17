import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import ollama_service

client = TestClient(app)

AGREEMENT = "The website includes five responsive pages. No administrator dashboard is included."
REQUEST = "Please add an administrator dashboard."
VERIFIED_QUOTE = "No administrator dashboard is included."


def model_result(**overrides):
    result = {
        "category": "potential_scope_change",
        "summary": "The request adds an excluded dashboard.",
        "reasoning": "The agreement explicitly excludes the requested dashboard.",
        "evidence": [
            {
                "quote": VERIFIED_QUOTE,
                "explanation": "This passage excludes the requested feature.",
            }
        ],
        "requires_human_review": False,
    }
    result.update(overrides)
    return result


def install_model_response(monkeypatch, result):
    async def fake_analyze_scope(*, agreement_text: str, client_request: str):
        assert agreement_text == AGREEMENT
        assert client_request == REQUEST
        return {**result, "model": "gemma3:4b"}

    monkeypatch.setattr("app.services.analysis_service.analyze_scope", fake_analyze_scope)


def post_analysis(agreement_text=AGREEMENT, client_request=REQUEST):
    return client.post(
        "/api/analysis/scope",
        json={"agreement_text": agreement_text, "client_request": client_request},
    )


def test_valid_model_response_keeps_exact_agreement_evidence(monkeypatch):
    install_model_response(monkeypatch, model_result())

    response = post_analysis()

    assert response.status_code == 200
    assert response.json()["category"] == "potential_scope_change"
    assert response.json()["evidence"][0]["quote"] == VERIFIED_QUOTE
    assert response.json()["model"] == "gemma3:4b"


def test_invented_evidence_is_removed_and_requires_review(monkeypatch):
    install_model_response(
        monkeypatch,
        model_result(
            evidence=[
                {"quote": "The client receives a free dashboard.", "explanation": "Invented."},
                {"quote": VERIFIED_QUOTE, "explanation": "The agreement excludes it."},
            ]
        ),
    )

    response = post_analysis()

    assert response.status_code == 200
    result = response.json()
    assert result["category"] == "needs_review"
    assert result["requires_human_review"] is True
    assert [item["quote"] for item in result["evidence"]] == [VERIFIED_QUOTE]
    assert "could not be verified" in result["reasoning"]


def test_missing_evidence_requires_human_review(monkeypatch):
    install_model_response(monkeypatch, model_result(evidence=[]))

    response = post_analysis()

    assert response.status_code == 200
    assert response.json()["category"] == "needs_review"
    assert response.json()["requires_human_review"] is True
    assert response.json()["evidence"] == []


def test_needs_review_category_always_requires_human_review(monkeypatch):
    install_model_response(
        monkeypatch,
        model_result(category="needs_review", requires_human_review=False),
    )

    response = post_analysis()

    assert response.status_code == 200
    assert response.json()["requires_human_review"] is True


def test_invalid_model_category_returns_bad_gateway(monkeypatch):
    install_model_response(monkeypatch, model_result(category="definitely_out_of_scope"))

    response = post_analysis()

    assert response.status_code == 502
    assert response.json()["detail"] == "The model returned an invalid analysis response."


@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (httpx.ConnectError("offline"), 503),
        (httpx.ReadTimeout("slow model"), 504),
        (
            httpx.HTTPStatusError(
                "model error",
                request=httpx.Request("POST", "http://127.0.0.1:11434/api/chat"),
                response=httpx.Response(500),
            ),
            502,
        ),
    ],
    ids=["unavailable", "timeout", "upstream-error"],
)
def test_ollama_failures_map_to_api_status(monkeypatch, exception, expected_status):
    async def fail_analysis(**_kwargs):
        raise exception

    monkeypatch.setattr("app.services.analysis_service.analyze_scope", fail_analysis)

    response = post_analysis()

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("agreement_text", "client_request"),
    [
        ("", REQUEST),
        (AGREEMENT, ""),
        ("   ", REQUEST),
        (AGREEMENT, "\n\t"),
        ("a" * 100_001, REQUEST),
        (AGREEMENT, "a" * 10_001),
    ],
    ids=["empty-agreement", "empty-request", "blank-agreement", "blank-request", "agreement-too-large", "request-too-large"],
)
def test_invalid_request_is_rejected_before_inference(agreement_text, client_request):
    response = post_analysis(agreement_text, client_request)

    assert response.status_code == 422


def test_ollama_service_uses_local_chat_api_and_injects_model_name(monkeypatch):
    response_body = {
        "model": "gemma3:4b",
        "message": {
            "content": json.dumps(model_result()),
        },
    }
    original_async_client = httpx.AsyncClient

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "http://127.0.0.1:11434/api/chat"
        payload = json.loads(request.content)
        assert payload["model"] == "gemma3:4b"
        assert payload["stream"] is False
        assert payload["format"] == "json"
        assert payload["options"]["temperature"] == 0
        assert "agreement_text" in payload["messages"][1]["content"]
        return httpx.Response(200, json=response_body)

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(ollama_service, "OLLAMA_URL", "http://127.0.0.1:11434")
    monkeypatch.setattr(ollama_service, "OLLAMA_MODEL", "gemma3:4b")
    monkeypatch.setattr(
        ollama_service.httpx,
        "AsyncClient",
        lambda **kwargs: original_async_client(transport=transport, **kwargs),
    )

    import asyncio

    result = asyncio.run(ollama_service.analyze_scope(AGREEMENT, REQUEST))

    assert result["model"] == "gemma3:4b"
    assert result["evidence"][0]["quote"] == VERIFIED_QUOTE
