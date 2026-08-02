"""Production-SRS sentence models.

Two tables (named to parallel the existing `vocab_sentences` example-sentence table):
- `production_sentences`     — personal (per-user) content: EN prompt + JP reference. Distinct from
                               the shared `vocab_sentences` example-sentence system.
- `production_sentence_review_log` — per-submission audit incl. LLM judge output (verdict +
                               feedback), which the 2-axis `review_log` can't hold.

SRS *state* (stage, next_review_at, burn) is NOT here — it reuses `user_item_progress` with
`item_type=SENTENCE`, `item_id -> production_sentences.id`. App-level rule:
progress.user_id == production_sentences.user_id.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import Politeness
from src.database import Base


class ProductionSentence(Base):
    """A user-authored English/Japanese pair used as a production-SRS target."""

    __tablename__ = "production_sentences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    english: Mapped[str] = mapped_column(Text, nullable=False)  # prompt shown to the user
    japanese: Mapped[str] = mapped_column(Text, nullable=False)  # reference answer
    # Target politeness, classified from the reference at creation. Shown to the learner (they can't
    # see the reference while producing) and passed to the judge as the explicit politeness target.
    politeness: Mapped[Politeness] = mapped_column(
        Enum(Politeness, values_callable=lambda e: [m.value for m in e]), nullable=False
    )
    # No `validated` column: the EN/JP pair is validated server-side at creation (POST /sentences),
    # inserted only on pass. A persisted row is valid by construction.
    # Provenance: 'manual' = hand-written, 'practice' = adopted from the generated practice
    # queue (origin_practice_id back-references the practice item; SET NULL if it ever goes).
    source: Mapped[str] = mapped_column(
        String(16), nullable=False, default="manual", server_default="manual"
    )
    origin_practice_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("practice_sentences.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class GrammarPoint(Base):
    """A personal grammar point, minted by LLM extraction from the user's own sentences.

    The bank is organic (grows only via sentence creation — no direct add) and per-user. `key` is
    the canonical citation form (e.g. 〜による, 可能形) and is unique per user: the current bank is
    fed back into the extraction prompt so the model reuses keys instead of minting near-duplicates.
    Every extracted point is kept and linked — noise is a display concern (sort/filter), never a
    data one, so per-sentence statistics stay consistent over time.
    """

    __tablename__ = "grammar_points"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_grammar_points_user_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    meaning_en: Mapped[str] = mapped_column(String(255), nullable=False)
    # 練習する flag: user opted this point into practice rotation. Only ever ADDS the point to
    # the selection pool — an unflagged point still rotates in via weak/recent-failure evidence
    # (no-ignore principle: nothing suppresses data).
    practice: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class SentenceGrammarPoint(Base):
    """M2M link: which grammar points a production sentence exercises.

    `evidence` is the substring of the sentence that instantiates the point (e.g. 「言われた」 for
    受身形) — needed because abstract paradigm keys don't literally appear in the text.
    """

    __tablename__ = "sentence_grammar_points"

    sentence_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("production_sentences.id", ondelete="CASCADE"),
        primary_key=True,
    )
    grammar_point_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grammar_points.id", ondelete="CASCADE"),
        primary_key=True,
    )
    evidence: Mapped[str | None] = mapped_column(String(255), nullable=True)


class GrammarPointReviewLog(Base):
    """Per-grammar-point outcome of one first-attempt production review.

    Written alongside `production_sentence_review_log` (FK `review_log_id`): exact-match reviews
    mark every linked point ok; LLM-judged reviews use the judge's per-point verdicts (a vocab
    mistake fails the sentence but no point). Overriding a review flips its rows to ok. This is
    the raw signal for per-point accuracy — and later the seed data for a real grammar SRS.
    """

    __tablename__ = "grammar_point_review_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    grammar_point_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grammar_points.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Null for practice-origin rows (a practice attempt has no sentence review log).
    review_log_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("production_sentence_review_log.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    # Provenance: 'sentence' = first-attempt SRS sentence review, 'practice' = generated
    # practice item. Both count toward per-point accuracy.
    origin: Mapped[str] = mapped_column(
        String(16), nullable=False, default="sentence", server_default="sentence"
    )
    # Back-reference for practice-origin rows (their review_log_id is NULL). Also the
    # "first attempt already scored" signal for a practice item.
    practice_sentence_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("practice_sentences.id", ondelete="CASCADE"),
        nullable=True,
    )
    ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Judge's one-line note for a failed point (broken fragment + rule violated). Null when ok.
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class PracticeSentence(Base):
    """A generated one-shot grammar-practice item (the wildcard queue).

    Generated by the LLM to exercise specific TARGET grammar points; reviewed like a production
    sentence (produce JP from EN) but with NO SRS state — reviewed until correct (or escaped),
    then done forever. Repeating a generated sentence would be rote memorization, the exact thing
    the practice layer exists to avoid; done rows are kept as anti-rote history for generation.
    """

    __tablename__ = "practice_sentences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    english: Mapped[str] = mapped_column(Text, nullable=False)  # prompt shown to the user
    japanese: Mapped[str] = mapped_column(Text, nullable=False)  # generated reference answer
    # Always MIXED for practice items (register is not the training goal here, and it keeps the
    # judge lenient about です/ます vs plain).
    politeness: Mapped[Politeness] = mapped_column(
        Enum(Politeness, values_callable=lambda e: [m.value for m in e]), nullable=False
    )
    # The grammar points this item targets, as a JSON list of grammar_point ids (1-2 entries).
    # Ephemeral items — key/gloss are joined live so renames stay visible; no link table.
    target_point_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending", server_default="pending"
    )
    # Why the user rejected this item (status='rejected'). Recent rejections + reasons are fed
    # back into the generator prompt as avoid-context.
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Whether the first (scoring) attempt happened is derived from the log: rows with
    # practice_sentence_id == id exist. Only that first attempt scores — retries are
    # contaminated signal (the user has seen the reference).
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class ProductionSentenceReviewLog(Base):
    """Audit record for one production-review submission (incl. LLM judge output)."""

    __tablename__ = "production_sentence_review_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sentence_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("production_sentences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted: Mapped[str] = mapped_column(Text, nullable=False)  # what the user wrote
    exact_match: Mapped[bool] = mapped_column(Boolean, nullable=False)  # hit fast path (no LLM)?
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)  # final verdict → drives SRS
    # feedback fires on either verdict: why-wrong, OR a better/more natural phrasing when correct.
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    overridden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Optional learner justification when they override the verdict. Fed back to the judge on future
    # reviews of THIS sentence (per-sentence memory) so a justified form can pass again.
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    srs_stage_before: Mapped[int] = mapped_column(Integer, nullable=False)
    srs_stage_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
