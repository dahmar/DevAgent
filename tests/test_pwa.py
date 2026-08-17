import importlib

from fastapi.testclient import TestClient


server = importlib.import_module("pwa_server")
client = TestClient(server.app)


def test_index_served():
    response = client.get("/")

    assert response.status_code == 200
    assert "DevAgent" in response.text


def test_chat_endpoint_returns_agent_response(monkeypatch):
    monkeypatch.setattr(server, "ask_agent", lambda message: f"echo: {message}")

    response = client.post("/api/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json()["answer"] == "echo: hello"


def test_chat_endpoint_handles_model_failure(monkeypatch):
    def boom(_message):
        raise RuntimeError("Model API unavailable")

    monkeypatch.setattr(server, "ask_agent", boom)

    response = client.post("/api/chat", json={"message": "сделай змейку"})

    assert response.status_code == 200
    assert "не удалось" in response.json()["answer"].lower()
