import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import ask_agent

app = FastAPI(title="DevAgent PWA")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class ChatRequest(BaseModel):
    message: str


def _build_system_message(exc: Exception) -> str:
    details = str(exc).strip() or "неизвестная ошибка"
    lowered = details.lower()

    if not os.getenv("HF_TOKEN"):
        return (
            "Системное сообщение: не найден токен Hugging Face (HF_TOKEN). "
            "Проверь переменные окружения в Railway или локальном .env. "
            f"Детали: {details}"
        )

    if any(token in lowered for token in ["401", "403", "forbidden", "invalid token", "authentication", "unauthorized"]):
        return (
            "Системное сообщение: токен Hugging Face недействителен или не подходит для этого провайдера. "
            "Проверь ключ и доступы в Railway. "
            f"Детали: {details}"
        )

    if any(token in lowered for token in ["429", "rate limit", "too many requests", "quota"]):
        return (
            "Системное сообщение: лимит запросов/квота провайдера исчерпаны. "
            "Подождите или обновите доступы. "
            f"Детали: {details}"
        )

    if any(token in lowered for token in ["connection", "timeout", "network", "unreachable", "failed to connect", "connectionerror"]):
        return (
            "Системное сообщение: нет связи с сервером провайдера или Railway. "
            "Проверь сеть, статус сервиса и доступность модели. "
            f"Детали: {details}"
        )

    return (
        "Системное сообщение: не удалось обработать запрос. "
        "Модель временно недоступна или завершилась с ошибкой. "
        f"Детали: {details}"
    )


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        answer = ask_agent(request.message)
        return JSONResponse({
            "answer": str(answer),
            "status": "ok",
            "system": False,
            "details": None,
        })
    except Exception as exc:
        message = _build_system_message(exc)
        return JSONResponse({
            "answer": message,
            "status": "error",
            "system": True,
            "details": str(exc),
        })


if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
