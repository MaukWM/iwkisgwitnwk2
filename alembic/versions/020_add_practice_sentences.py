"""Add grammar practice rotation.

Creates `practice_sentences` (one-shot generated practice items), adds the 練習する flag to
`grammar_points`, provenance (`origin`) to `grammar_point_review_log` (practice rows have no
sentence review log, so `review_log_id` becomes nullable), and per-user custom topic seeds.

Revision ID: 020
Revises: 019
Create Date: 2026-07-23

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

revision: str = "020"
down_revision: str | None = "019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "practice_sentences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("english", sa.Text(), nullable=False),
        sa.Column("japanese", sa.Text(), nullable=False),
        sa.Column(
            "politeness",
            sa.Enum("polite", "casual", "mixed", name="politeness"),
            nullable=False,
        ),
        sa.Column("target_point_ids", sa.JSON(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="pending"
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_practice_sentences_user_id", "practice_sentences", ["user_id"])

    op.add_column(
        "grammar_points",
        sa.Column(
            "practice",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "grammar_point_review_log",
        sa.Column(
            "origin",
            sa.String(length=16),
            nullable=False,
            server_default="sentence",
        ),
    )
    op.alter_column(
        "grammar_point_review_log",
        "review_log_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    # Back-reference for practice-origin rows (sentence-origin rows use review_log_id) —
    # also the "already attempted?" signal (first attempt = no rows yet), like the other
    # review types derive state from their log.
    op.add_column(
        "grammar_point_review_log",
        sa.Column("practice_sentence_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_grammar_point_review_log_practice_sentence_id",
        "grammar_point_review_log",
        "practice_sentences",
        ["practice_sentence_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.add_column("users", sa.Column("practice_topics", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "practice_topics")
    # Practice rows have review_log_id NULL — remove them before re-tightening the column.
    op.execute("DELETE FROM grammar_point_review_log WHERE origin = 'practice'")
    op.drop_constraint(
        "fk_grammar_point_review_log_practice_sentence_id",
        "grammar_point_review_log",
        type_="foreignkey",
    )
    op.drop_column("grammar_point_review_log", "practice_sentence_id")
    op.alter_column(
        "grammar_point_review_log",
        "review_log_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("grammar_point_review_log", "origin")
    op.drop_column("grammar_points", "practice")
    # Dropping the table drops its indexes + FKs with it (MySQL refuses to drop an index
    # that backs a foreign key, so no separate drop_index call here).
    op.drop_table("practice_sentences")
