"""Testes da API. Precisam do pipeline já rodado (data_generation.py ->
preprocessing.py -> train.py), já que carregam o checkpoint real do modelo.
Se os artefatos não existirem, os testes são pulados (não falham) com uma
mensagem explicando o motivo."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_READY = (PROJECT_ROOT / "models" / "best_model.pt").exists() and (
    PROJECT_ROOT / "data" / "processed" / "vocab.json"
).exists()

pytestmark = pytest.mark.skipif(
    not ARTIFACTS_READY,
    reason="Rode data_generation.py, preprocessing.py e train.py antes de testar a API",
)

from fastapi.testclient import TestClient  # noqa: E402

from api import app  # noqa: E402


def test_health_endpoint_reports_model_loaded():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_loaded": True}


def test_root_serves_html_page():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


def test_predict_returns_valid_response_shape():
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={"text": "Um dragão ancestral ameaça o reino e um guerreiro precisa detê-lo."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["label"] in data["probabilities"]
        assert 0.0 <= data["confidence"] <= 1.0
        assert abs(sum(data["probabilities"].values()) - 1.0) < 0.01


def test_predict_rejects_missing_text_field():
    with TestClient(app) as client:
        response = client.post("/predict", json={})
        assert response.status_code == 422