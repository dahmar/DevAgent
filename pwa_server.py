from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import ask_agent

app = FastAPI(title="DevAgent PWA")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        answer = ask_agent(request.message)
        return JSONResponse({"answer": str(answer)})
    except Exception as exc:
        return JSONResponse({
            "answer": (
                "Не удалось обработать запрос: модель временно недоступна. "
                "Проверь API-ключ или лимиты провайдера. "
                f"Ошибка: {exc}"
            )
        })


if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
