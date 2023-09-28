"""use sub as only id column

Revision ID: 880d7345efd4
Revises:
Create Date: 2023-09-27 20:15:25.781532

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "880d7345efd4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_account", sa.Column("id", sa.String(length=30), nullable=False), sa.PrimaryKeyConstraint("id")
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_account")
    # ### end Alembic commands ###