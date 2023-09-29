"""add venue model

Revision ID: 57a8e0f3dc7b
Revises: f272942c71d1
Create Date: 2023-09-29 18:28:33.411814

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "57a8e0f3dc7b"
down_revision: Union[str, None] = "f272942c71d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
