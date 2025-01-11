"""Renamed query column in RAGQuery to question

Revision ID: 56ca68626e4a
Revises: 667dd31f55e5
Create Date: 2025-01-02 19:13:54.788454

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '56ca68626e4a'
down_revision = '667dd31f55e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rag_query', schema=None) as batch_op:
        batch_op.add_column(sa.Column('question', sa.String(length=300), nullable=True))
        batch_op.drop_column('query')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rag_query', schema=None) as batch_op:
        batch_op.add_column(sa.Column('query', mysql.VARCHAR(length=300), nullable=True))
        batch_op.drop_column('question')

    # ### end Alembic commands ###
