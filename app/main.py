from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .backstop import route_request
from .llm import generate_answer

app = FastAPI(title="Your Name. (2016) Canonical QA Chatbot")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    route: str  # in_scope | out_of_scope | safety | uncertain


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    with open(os.path.join(FRONTEND_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    decision = route_request(req.message)

    # Hard stops handled deterministically in Python (backstop)
    if decision.route != "in_scope":
        return ChatResponse(answer=decision.answer, route=decision.route)

    answer = await generate_answer(req.message)

    # Prevent accidental deterministic tag leakage in in-scope answers
    a = answer.strip()
    if a.startswith("OUT_OF_SCOPE") or a.startswith("SAFETY"):
        return ChatResponse(
            answer="UNCERTAIN: The response could not be generated reliably within scope.",
            route="uncertain",
        )

    return ChatResponse(answer=answer, route="in_scope")


def cli_serve() -> None:
    """
    Optional entrypoint: `uv run serve`
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=True,
    )