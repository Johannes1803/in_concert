"""model user under main app

Revision ID: 0078de3bfcc8
Revises: 7caf26a60bde
Create Date: 2023-10-04 13:00:10.449786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0078de3bfcc8'
down_revision: Union[str, None] = '7caf26a60bde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
