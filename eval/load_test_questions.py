"""Load the test questions from eval/test_questions.json into the database.

Each entry becomes one row in the test_questions table. Questions that are
already stored are skipped, so the script is safe to run more than once.

Run from the project root:
    python -m eval.load_test_questions
"""

import json

from sqlalchemy import select

from db.models import TestQuestion
from db.session import SessionLocal


def main() -> None:
    with open("eval/test_questions.json") as f:
        items = json.load(f)

    session = SessionLocal()
    try:
        added = 0
        for item in items:
            exists = session.execute(
                select(TestQuestion).where(TestQuestion.question == item["question"])
            ).scalar_one_or_none()
            if exists is not None:
                continue
            session.add(
                TestQuestion(
                    question=item["question"],
                    doc_id=item["doc_id"],
                    page=item["page"],
                    reference_answer=item["reference_answer"],
                )
            )
            added += 1
        session.commit()
        print(f"Added {added} test questions, skipped {len(items) - added}.")
    finally:
        session.close()


if __name__ == "__main__":
    main()