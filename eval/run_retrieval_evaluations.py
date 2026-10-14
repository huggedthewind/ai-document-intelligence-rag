"""Evaluate whether retrieved chunks are relevant to their questions."""

from sqlalchemy import select

from db.models import Query, RetrievedChunk
from db.session import SessionLocal
from eval.judge_retrieval import judge_retrieval


def main() -> None:
    session = SessionLocal()

    try:
        statement = (
            select(Query)
            .join(Query.retrieved_chunks)
            .where(
                Query.test_question_id.is_not(None),
                RetrievedChunk.relevant.is_(None),
            )
            .distinct()
        )

        queries = session.execute(statement).scalars().all()

        print(f"Found {len(queries)} queries with unevaluated chunks.")

        if not queries:
            return

        for query_position, query in enumerate(queries, start=1):
            retrieved_chunks = sorted(query.retrieved_chunks, key=lambda item: item.rank)

            chunk_texts = [retrieved_chunk.chunk.text for retrieved_chunk in retrieved_chunks]

            result = judge_retrieval(question=query.text, chunk_texts=chunk_texts)

            decisions_by_number = {decision.chunk_number: decision for decision in result.chunks}

            for position, retrieved_chunk in enumerate(retrieved_chunks, start=1):
                retrieved_chunk.relevant = (decisions_by_number[position].relevant)

            session.commit()

            relevant_count = sum(decision.relevant for decision in result.chunks)

            print(
                f"[{query_position}/{len(queries)}] "
                f"Query {query.query_id}: "
                f"{relevant_count}/{len(retrieved_chunks)} "
                f"chunks relevant"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()