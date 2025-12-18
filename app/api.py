"""
FastAPI wrapper around the RAG question-answering pipeline.

Endpoints:
- GET /health  : basic health check
- POST /ask    : ask a question about the SAMK guidance handbook
"""

from fastapi import FastAPI
from pydantic import BaseModel

from .answer_question import answer_question


app = FastAPI(title="AI Document Intelligence - SAMK Handbook")


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


class AnswerResponse(BaseModel):
    answer: str


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
async def ask(req: QuestionRequest) -> AnswerResponse:
    """
    Run RAG over the handbook and return a grounded answer.
    """
    ans = answer_question(req.question, k=req.top_k)
    return AnswerResponse(answer=ans)