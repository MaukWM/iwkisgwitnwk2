"""Reject reason for practice sentences.

Users can reject a generated practice item with a free-text reason (unknown vocab, loanword
soup, unnatural phrasing, ...). The item flips to status='rejected' and recent rejections are
fed back into the generator prompt as avoid-context — a steering channel for everything the
static prompt can't anticipate.

Revision ID: 022
Revises: 021
Create Date: 2026-08-02

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

revision: str = "022"
down_revision: str | None = "021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "practice_sentences",
        sa.Column("reject_reason", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("practice_sentences", "reject_reason")
