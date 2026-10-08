"""add relevant to retrieved_chunks and judge fields to evaluations

Revision ID: eca64bd85d37
Revises: 5d8879ccdbb6
Create Date: 2026-10-08 13:38:16.425542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca64bd85d37'
down_revision: Union[str, Sequence[str], None] = '5d8879ccdbb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("evaluations") as batch_op:
        batch_op.add_column(sa.Column("human_verdict", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("judge_model", sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=False))
    op.add_column("retrieved_chunks", sa.Column("relevant", sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("retrieved_chunks", "relevant")
    with op.batch_alter_table("evaluations") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("judge_model")
        batch_op.drop_column("human_verdict")