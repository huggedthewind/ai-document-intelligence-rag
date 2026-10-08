"""add test_questions table and link queries to it

Revision ID: 5d8879ccdbb6
Revises: 7b774bea7f0b
Create Date: 2026-10-08 13:02:19.215428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d8879ccdbb6'
down_revision: Union[str, Sequence[str], None] = '7b774bea7f0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('test_questions',
    sa.Column('test_question_id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('doc_id', sa.String(length=100), nullable=True),
    sa.Column('page', sa.Integer(), nullable=True),
    sa.Column('reference_answer', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['doc_id'], ['documents.doc_id'], ),
    sa.PrimaryKeyConstraint('test_question_id')
    )
    with op.batch_alter_table('queries') as batch_op:
        batch_op.add_column(sa.Column('test_question_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_queries_test_question_id', 'test_questions', ['test_question_id'], ['test_question_id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('queries') as batch_op:
        batch_op.drop_constraint('fk_queries_test_question_id', type_='foreignkey')
        batch_op.drop_column('test_question_id')
    op.drop_table('test_questions')