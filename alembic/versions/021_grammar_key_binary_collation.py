"""Binary collation for grammar point keys.

MySQL's default utf8mb4_0900_ai_ci collation is accent-insensitive, and kana voicing marks
(dakuten) count as accents — so 〜ても and 〜でも compared EQUAL for the unique
(user_id, key) index. Extraction minting 〜でも while the bank held 〜ても blew up with
"Duplicate entry" (500 on sentence create), even though they are genuinely distinct grammar
points. utf8mb4_bin makes the dakuten significant. Existing rows are unaffected: anything
unique under ai_ci is unique under bin.

Revision ID: 021
Revises: 020
Create Date: 2026-07-29

"""

from collections.abc import Sequence

from alembic import op  # type: ignore[attr-defined]

revision: str = "021"
down_revision: str | None = "020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE grammar_points MODIFY `key` VARCHAR(100) "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL"
    )


def downgrade() -> None:
    # Only safe if no rows differ solely by voicing/accent marks; MySQL will refuse the
    # index rebuild otherwise — resolve such duplicates by hand first.
    op.execute(
        "ALTER TABLE grammar_points MODIFY `key` VARCHAR(100) "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL"
    )
