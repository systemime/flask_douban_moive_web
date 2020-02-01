"""empty message

Revision ID: 9b8a344b3fb1
Revises: d1ef3819dc04
Create Date: 2020-02-01 04:43:47.742976

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9b8a344b3fb1'
down_revision = 'd1ef3819dc04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('sender_user_id', sa.Integer(), nullable=False))
    op.create_unique_constraint('uniqie_receiver_user_id_and_sender_user_id_and_category', 'notification', ['receiver_user_id', 'sender_user_id', 'category'])
    op.drop_index('uniqie_receiver_user_id_and_action_user_id_and_category', table_name='notification')
    op.drop_constraint('notification_ibfk_2', 'notification', type_='foreignkey')
    op.drop_constraint('notification_ibfk_1', 'notification', type_='foreignkey')
    op.create_foreign_key(None, 'notification', 'users', ['receiver_user_id'], ['id'])
    op.create_foreign_key(None, 'notification', 'users', ['sender_user_id'], ['id'])
    op.drop_column('notification', 'action_user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('action_user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'notification', type_='foreignkey')
    op.drop_constraint(None, 'notification', type_='foreignkey')
    op.create_foreign_key('notification_ibfk_1', 'notification', 'users', ['action_user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('notification_ibfk_2', 'notification', 'users', ['receiver_user_id'], ['id'], ondelete='CASCADE')
    op.create_index('uniqie_receiver_user_id_and_action_user_id_and_category', 'notification', ['receiver_user_id', 'action_user_id', 'category'], unique=True)
    op.drop_constraint('uniqie_receiver_user_id_and_sender_user_id_and_category', 'notification', type_='unique')
    op.drop_column('notification', 'sender_user_id')
    # ### end Alembic commands ###
