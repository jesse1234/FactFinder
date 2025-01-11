"""Added admin table and removed user_role

Revision ID: 667dd31f55e5
Revises: 96faf982f164
Create Date: 2025-01-01 15:18:26.034927

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '667dd31f55e5'
down_revision = '96faf982f164'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rag_query', schema=None) as batch_op:
        batch_op.add_column(sa.Column('admin_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'admin', ['admin_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('user_role')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_role', mysql.VARCHAR(length=50), nullable=True))

    with op.batch_alter_table('rag_query', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('admin_id')

    # ### end Alembic commands ###
