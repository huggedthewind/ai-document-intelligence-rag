"""Run stored test questions through the RAG system and save the results.

For each test question, saves a Query row linked to that test question,
the generated Answer, and one RetrievedChunk row per retrieved chunk.

Run from the project root:
    python -m eval.run_test_questions
"""
from sqlalchemy import select
from db.models import TestQuestion, Query, Answer, RetrievedChunk
from db.session import SessionLocal
from app.answer_question import answer_question


def main() -> None:

    session = SessionLocal()
    try:
        test_questions = session.execute(select(TestQuestion)).scalars().all()
        for question in test_questions:
            new_query = Query(text=question.question, top_k=5, test_question_id=question.test_question_id)
            session.add(new_query)
            session.commit()
            answer, chunks = answer_question(question.question)
            new_answer = Answer(query_id=new_query.query_id, text=answer)
            session.add(new_answer)
            for position, chunk in enumerate(chunks, start=1):
                new_chunk = RetrievedChunk(query_id=new_query.query_id, chunk_id=chunk[1]["chunk_id"], rank=position, distance=chunk[2])
                session.add(new_chunk)
            session.commit()
            print(question.test_question_id, answer[:100])
    finally:
        session.close()


if __name__ == "__main__":
    main()