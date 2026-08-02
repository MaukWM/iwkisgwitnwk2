"""Provenance for production sentences.

`source` distinguishes hand-written sentences ('manual') from ones adopted out of the generated
grammar-practice queue ('practice'); `origin_practice_id` back-references the practice item an
adopted sentence came from. Backfills existing adopted rows by exact (user_id, japanese) match
against practice items — the adopt flow copies the reference verbatim.

Revision ID: 023
Revises: 022
Create Date: 2026-08-02

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

revision: str = "023"
down_revision: str | None = "022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "production_sentences",
        sa.Column("source", sa.String(16), nullable=False, server_default="manual"),
    )
    op.add_column(
        "production_sentences",
        sa.Column("origin_practice_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_production_sentences_origin_practice",
        "production_sentences",
        "practice_sentences",
        ["origin_practice_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        "UPDATE production_sentences ps JOIN practice_sentences pr "
        "ON pr.user_id = ps.user_id AND pr.japanese = ps.japanese "
        "SET ps.source = 'practice', ps.origin_practice_id = pr.id"
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_production_sentences_origin_practice", "production_sentences", type_="foreignkey"
    )
    op.drop_column("production_sentences", "origin_practice_id")
    op.drop_column("production_sentences", "source")
