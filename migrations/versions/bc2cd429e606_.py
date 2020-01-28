"""empty message

Revision ID: bc2cd429e606
Revises: 7f0e818dc8ba
Create Date: 2020-01-28 14:14:26.191741

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bc2cd429e606'
down_revision = '7f0e818dc8ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('aka_list', sa.Text(), nullable=True))
    op.drop_column('movies', 'aka_text')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('aka_text', mysql.TEXT(collation='utf8mb4_bin'), nullable=True))
    op.drop_column('movies', 'aka_list')
    # ### end Alembic commands ###
