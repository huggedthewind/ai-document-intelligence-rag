"""
FastAPI wrapper around the RAG question-answering pipeline.

Endpoints:
- GET /health  : basic health check
- POST /ask    : ask a question about the SAMK guidance handbook
"""

from fastapi import FastAPI
from pydantic import BaseModel

from .answer_question import answer_question
from db.session import SessionLocal
from db.models import Query, Answer, RetrievedChunk


app = FastAPI(title="AI Document Intelligence - RAG over documents")


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5
    doc_id: str | None = None


class AnswerResponse(BaseModel):
    answer: str


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
async def ask(req: QuestionRequest) -> AnswerResponse:
    """
    Run RAG over document(s) and return a grounded answer.
    """
    session = SessionLocal()
    new_query = Query(text=req.question, doc_id=req.doc_id, top_k=req.top_k)
    session.add(new_query)
    session.commit()
    
    ans, chunks = answer_question(req.question, k=req.top_k, doc_id=req.doc_id)
    new_answer = Answer(text=ans, query_id=new_query.query_id)
    retrieved_chunks = []
    for rank, (text, meta, distance) in enumerate(chunks, start=1):
        retrieved_chunk = RetrievedChunk(
            query_id=new_query.query_id,
            chunk_id=meta["chunk_id"],
            rank=rank,
            distance=distance,
        )
        retrieved_chunks.append(retrieved_chunk)

    session.add_all(retrieved_chunks)
    session.add(new_answer)
    session.commit()
    
    session.close()
    return AnswerResponse(answer=ans)
