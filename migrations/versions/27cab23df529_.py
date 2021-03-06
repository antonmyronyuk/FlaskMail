"""empty message

Revision ID: 27cab23df529
Revises: b64c03de2cc5
Create Date: 2018-04-27 13:25:24.150646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27cab23df529'
down_revision = 'b64c03de2cc5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email_notifications', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'email_notifications')
    # ### end Alembic commands ###
