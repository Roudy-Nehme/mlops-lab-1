from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from src.food11 import serve


class FakeModel:
    def predict(self, x):
        assert x.shape == (1, 3, 224, 224)
        # The real model returns logits, so softmax produces 0.90 for Bread.
        return np.log([[0.90] + [0.01] * 10])


def test_health(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")
    with TestClient(serve.app) as client:
        assert client.get("/health").status_code == 200


def test_predict_returns_valid_json(monkeypatch):
    monkeypatch.setenv("SKIP_MODEL", "1")
    with TestClient(serve.app) as client:
        monkeypatch.setattr(serve, "model", FakeModel())
        with Path("tests/fixtures/bread.jpg").open("rb") as f:
            response = client.post("/predict", files={"file": ("bread.jpg", f, "image/jpeg")})
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Bread"
    assert abs(body["confidence"] - 0.90) < 0.0001
