"""Set a human groundedness verdict for one evaluated answer."""

import argparse

from sqlalchemy import select

from db.models import Evaluation
from db.session import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set a human verdict for an existing evaluation."
    )
    parser.add_argument(
        "answer_id",
        type=int,
        help="ID of the answer being reviewed.",
    )
    parser.add_argument(
        "verdict",
        choices=["yes", "partial", "no"],
        help="Human groundedness verdict.",
    )
    args = parser.parse_args()

    session = SessionLocal()

    try:
        evaluation = session.execute(
            select(Evaluation).where(
                Evaluation.answer_id == args.answer_id
            )
        ).scalar_one_or_none()

        if evaluation is None:
            print(f"No evaluation found for answer {args.answer_id}.")
            return

        evaluation.human_verdict = args.verdict
        session.commit()

        print(
            f"Answer {args.answer_id}: "
            f"human verdict set to {args.verdict}."
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()