"""fix typo

Revision ID: 78669a8e01aa
Revises: 5e8b8b462ec2
Create Date: 2020-06-30 22:51:29.892941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78669a8e01aa'
down_revision = '5e8b8b462ec2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_timestamp'), 'event', ['timestamp'], unique=False)
    op.drop_index('ix_events_timestamp', table_name='events')
    op.drop_table('events')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(length=140), nullable=True),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_events_timestamp', 'events', ['timestamp'], unique=False)
    op.drop_index(op.f('ix_event_timestamp'), table_name='event')
    op.drop_table('event')
    # ### end Alembic commands ###