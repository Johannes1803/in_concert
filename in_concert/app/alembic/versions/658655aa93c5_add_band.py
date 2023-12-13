"""add band

Revision ID: 658655aa93c5
Revises: 513886cb9fcd
Create Date: 2023-12-13 16:38:56.865683

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "658655aa93c5"
down_revision: Union[str, None] = "513886cb9fcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "bands",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("city", sa.String(length=30), nullable=True),
        sa.Column("zip_code", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(length=30), nullable=True),
        sa.Column("website_link", sa.String(length=120), nullable=True),
        sa.Column("image_link", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("bands")
    # ### end Alembic commands ###
