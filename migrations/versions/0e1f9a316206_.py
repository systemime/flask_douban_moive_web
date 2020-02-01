"""empty message

Revision ID: 0e1f9a316206
Revises: 31c4de0c7029
Create Date: 2020-02-01 06:52:39.075949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e1f9a316206'
down_revision = '31c4de0c7029'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('episodes_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movies', 'episodes_count')
    # ### end Alembic commands ###
