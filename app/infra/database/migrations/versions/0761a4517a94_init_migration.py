"""Init migration

Revision ID: 0761a4517a94
Revises:
Create Date: 2025-10-04 22:14:47.033804

"""

from typing import Sequence, Union

revision: str = "0761a4517a94"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None: ...


def downgrade() -> None: ...
