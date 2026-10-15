"""Analyze the stored RAG evaluation results."""

from sqlalchemy import func, select

from db.models import Answer, Evaluation, Query, RetrievedChunk, TestQuestion
from db.session import SessionLocal


def main() -> None:
    session = SessionLocal()

    try:
        stored_questions_statement = select(func.count(TestQuestion.test_question_id))
        stored_test_questions = session.scalar(stored_questions_statement)

        executed_queries_statement = select(func.count(Query.query_id)).where(Query.test_question_id.is_not(None))
        executed_test_queries = session.scalar(executed_queries_statement)

        generated_answers_statement = select(func.count(Answer.answer_id)).join(Answer.query).where(Query.test_question_id.is_not(None))
        generated_test_answers = session.scalar(generated_answers_statement)

        evaluated_answers_statement = select(func.count(Evaluation.evaluation_id)).join(Evaluation.answer).join(Answer.query).where(Query.test_question_id.is_not(None))
        evaluated_test_answers = session.scalar(evaluated_answers_statement)

        final_verdicts_statement = select(Evaluation).join(Evaluation.answer).join(Answer.query).where(Query.test_question_id.is_not(None))
        test_evaluations = session.scalars(final_verdicts_statement).all()
        final_verdict_counts = {"yes": 0, "partial": 0, "no": 0}

        for evaluation in test_evaluations:
            if evaluation.human_verdict is not None:
                final_verdict = evaluation.human_verdict
            else:
                final_verdict = evaluation.verdict

            final_verdict_counts[final_verdict] += 1

        relevance_statement = select(RetrievedChunk.relevant, func.count()).join(RetrievedChunk.query).where(Query.test_question_id.is_not(None)).group_by(RetrievedChunk.relevant)
        relevance_counts = session.execute(relevance_statement).all()

        print("Evaluation coverage")
        print(f"Stored test questions: {stored_test_questions}")
        print(f"Executed test queries: {executed_test_queries}")
        print(f"Generated test answers: {generated_test_answers}")
        print(f"Evaluated test answers: {evaluated_test_answers}")

        print("\nFinal answer verdicts after human review")
        print(f"Yes: {final_verdict_counts['yes']}")
        print(f"Partial: {final_verdict_counts['partial']}")
        print(f"No: {final_verdict_counts['no']}")

        print("\nRetrieval relevance")
        for relevance_status, chunk_count in relevance_counts:
            if relevance_status is True:
                print(f"Relevant chunks: {chunk_count}")
            elif relevance_status is False:
                print(f"Irrelevant chunks: {chunk_count}")
            else:
                print(f"Unevaluated chunks: {chunk_count}")

    finally:
        session.close()


if __name__ == "__main__":
    main()