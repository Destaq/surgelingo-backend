"""empty message

Revision ID: 10ab1ef18fb7
Revises: ed6f7800fd37
Create Date: 2021-09-11 18:06:27.673783

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '10ab1ef18fb7'
down_revision = 'ed6f7800fd37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('tags', postgresql.ARRAY(sa.String(length=20)), nullable=True))
    op.add_column('posts', sa.Column('language', sa.String(length=20), nullable=True))
    op.add_column('posts', sa.Column('route_link', sa.String(length=12), nullable=True))
    op.alter_column('posts', 'content',
               existing_type=sa.VARCHAR(length=300),
               type_=sa.String(length=200),
               existing_nullable=True)
    op.create_unique_constraint(None, 'posts', ['route_link'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'posts', type_='unique')
    op.alter_column('posts', 'content',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=300),
               existing_nullable=True)
    op.drop_column('posts', 'route_link')
    op.drop_column('posts', 'language')
    op.drop_column('posts', 'tags')
    # ### end Alembic commands ###