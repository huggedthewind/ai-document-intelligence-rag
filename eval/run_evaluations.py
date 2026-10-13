"""Evaluate stored test answers and save structured verdicts."""

from sqlalchemy import select

from db.models import Answer, Evaluation, Query
from db.session import SessionLocal
from eval.judge_groundedness import JUDGE_MODEL, judge_groundedness


def main() -> None:
    session = SessionLocal()

    try:
        statement = (
            select(Answer)
            .join(Answer.query)
            .where(Query.test_question_id.is_not(None), ~Answer.evaluation.has()) # select test-set answers and only answers that do not have an Evaluation row
        )

        answers = session.execute(statement).scalars().all()

        print(f"Found {len(answers)} test answers.")
        if not answers:
            print("No unevaluated test answers found.")
            return

        for position, answer in enumerate(answers, start=1):
            chunk_texts: list[str] = []

            for retrieved_chunk in sorted(
                answer.query.retrieved_chunks,
                key=lambda item: item.rank,
            ):
                chunk_texts.append(retrieved_chunk.chunk.text)

            result = judge_groundedness(
                question=answer.query.text,
                answer=answer.text,
                chunk_texts=chunk_texts,
            )

            new_evaluation = Evaluation(
                answer_id=answer.answer_id,
                verdict=result.verdict,
                human_verdict=None,
                notes=result.notes,
                judge_model=JUDGE_MODEL,
            )

            session.add(new_evaluation)
            session.commit()

            print(
                f"[{position}/{len(answers)}] "
                f"Answer {answer.answer_id}: {result.verdict}"
            )
    finally:
        session.close()


if __name__ == "__main__":
    main()