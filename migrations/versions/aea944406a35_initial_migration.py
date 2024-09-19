"""Initial migration.

Revision ID: aea944406a35
Revises: 
Create Date: 2024-07-13 01:42:55.747857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aea944406a35'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contact_no', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('niche')
        batch_op.drop_column('name')
        batch_op.drop_column('dob')
        batch_op.drop_column('gender')
        batch_op.drop_column('social_handles')
        batch_op.drop_column('profile_photo')

    # ### end Alembic commands ###
