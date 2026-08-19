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
    payload = response.json()
    assert payload["answer"] == "echo: hello"
    assert payload["status"] == "ok"
    assert payload["system"] is False


def test_chat_endpoint_handles_model_failure(monkeypatch):
    def boom(_message):
        raise RuntimeError("Model API unavailable")

    monkeypatch.setattr(server, "ask_agent", boom)

    response = client.post("/api/chat", json={"message": "сделай змейку"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["system"] is True
    assert "не удалось" in payload["answer"].lower()


def test_chat_stream_returns_progress_events(monkeypatch):
    monkeypatch.setattr(server, "ask_agent_stream", lambda message: iter([
        {"type": "status", "text": "Анализирую задачу..."},
        {"type": "action", "text": "Выполняю: create_file"},
        {"type": "answer", "text": "Готово"},
    ]))

    response = client.post("/api/chat/stream", json={"message": "создай файл"})

    assert response.status_code == 200
    assert '"type": "status"' in response.text
    assert '"type": "action"' in response.text
    assert '"text": "Готово"' in response.text
