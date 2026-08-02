"""Grammar-practice rotation service (the wildcard queue).

Generated one-shot practice items targeting weak / flagged / recently-failed grammar points.
No SRS: an item is reviewed until correct (or escaped), scores its targets once (first attempt,
`origin='practice'`), and is done forever. See _bmad-output/analysis/grammar-practice-design.md.
"""

import random
from datetime import UTC, datetime, timedelta

from openai import OpenAIError
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.constants import ItemType, Politeness
from src.llm.judge import judge
from src.llm.practice import generate_practice
from src.logging import logger
from src.progress.models import UserItemProgress
from src.sentences.models import (
    GrammarPoint,
    GrammarPointReviewLog,
    PracticeSentence,
    ProductionSentence,
    SentenceGrammarPoint,
)
from src.sentences.schemas import (
    PracticeItem,
    PracticeQueueResponse,
    PracticeReviewResponse,
    PracticeTargetItem,
    PracticeTopicsResponse,
    SentencePointResult,
)
from src.sentences.service import _normalize
from src.vocab.models import Vocab

# Rotation knobs (design doc "Defaults") — module constants, promote to settings if tuning
# ever becomes a deploy-time need.
INTERVAL_HOURS = 8  # min gap between generation batches
BATCH_SIZE = 3  # items per batch (spread: distinct target heads)
CAP = 3  # max pending items (backpressure: absent user never stockpiles)
MIN_REVIEWS = 3  # reviews a point needs before "weak" is meaningful
WEAK_BOTTOM_N = 5  # how many worst-accuracy points feed the pool
HISTORY_PER_POINT = 15  # recent same-target sentences fed as anti-rote context
VOCAB_BAIT = 5  # candidate words sampled per generation
REJECTIONS_FED = 10  # recent rejected sentences (+ reasons) fed as avoid-context
LEARNER_SAMPLE = 15  # of the learner's own sentences fed as the vocabulary-level anchor

DEFAULT_TOPICS = [
    "daily life at home",
    "work or study",
    "an opinion about something",
    "a past experience",
    "a hypothetical situation",
    "plans or the near future",
    "food or going out",
    "a conversation with a friend",
]


def _aware(dt: datetime) -> datetime:
    """MySQL returns naive datetimes — normalize to UTC-aware for comparisons."""
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt


class PracticeService:
    """Service for the grammar-practice queue: selection, generation, review, escape."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # --- queue -----------------------------------------------------------------------------

    async def get_queue(self, user_id: int) -> PracticeQueueResponse:
        """Pending practice items, lazily topping up the queue (no cron).

        Generates a batch when there is room (< CAP) and the last generation is older than
        INTERVAL_HOURS (or none exists). Generation failures are logged and skipped — the
        queue fetch itself never fails because one item misfired.
        """
        pending = await self._pending(user_id)
        if len(pending) < CAP and await self._interval_elapsed(user_id):
            await self._generate(user_id, min(BATCH_SIZE, CAP - len(pending)), pending)
            pending = await self._pending(user_id)
        items = await self._to_items(pending)
        return PracticeQueueResponse(
            items=items, count=len(items), bonus_available=len(items) == 0
        )

    async def generate_bonus(self, user_id: int) -> PracticeQueueResponse:
        """User-requested extra item (the 0-queue button). Ignores the interval, respects CAP.

        Raises ValueError (→ 400) if the queue is full or nothing could be generated.
        """
        pending = await self._pending(user_id)
        if len(pending) >= CAP:
            raise ValueError("Practice queue is full")
        created = await self._generate(user_id, 1, pending)
        if not created:
            raise ValueError("No practice item could be generated — try again")
        pending = await self._pending(user_id)
        items = await self._to_items(pending)
        return PracticeQueueResponse(items=items, count=len(items), bonus_available=False)

    async def reject(self, user_id: int, practice_id: int, reason: str) -> None:
        """Reject a generated item with a why. Instant — no LLM call.

        The reason is stored and fed into future generations as avoid-context. No replacement
        is generated here (that would block the user on an LLM call mid-session) — the queue
        refills on the next fetch, and the bonus button covers "give me one now". Raises
        LookupError (→ 404) / ValueError (→ 400, already done).
        """
        item = await self.db.get(PracticeSentence, practice_id)
        if item is None or item.user_id != user_id:
            raise LookupError("Practice item not found")
        if item.status == "done":
            raise ValueError("Practice item is already completed")
        item.status = "rejected"
        item.reject_reason = reason.strip()
        item.completed_at = datetime.now(UTC)  # doubles as rejected-at
        await self.db.commit()

    async def _pending(self, user_id: int) -> list[PracticeSentence]:
        return list(
            (
                await self.db.execute(
                    select(PracticeSentence)
                    .where(
                        PracticeSentence.user_id == user_id,
                        PracticeSentence.status == "pending",
                    )
                    .order_by(PracticeSentence.created_at.asc())
                )
            )
            .scalars()
            .all()
        )

    async def _interval_elapsed(self, user_id: int) -> bool:
        last = (
            await self.db.execute(
                select(func.max(PracticeSentence.created_at)).where(
                    PracticeSentence.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        if last is None:
            return True
        return datetime.now(UTC) - _aware(last) >= timedelta(hours=INTERVAL_HOURS)

    async def _to_items(self, pending: list[PracticeSentence]) -> list[PracticeItem]:
        items: list[PracticeItem] = []
        for p in pending:
            targets = await self._target_points(p)
            items.append(
                PracticeItem(
                    practice_id=p.id,
                    english=p.english,
                    politeness=p.politeness,
                    targets=[
                        PracticeTargetItem(
                            grammar_point_id=t.id, key=t.key, meaning_en=t.meaning_en
                        )
                        for t in targets
                    ],
                    created_at=p.created_at,
                )
            )
        return items

    async def _attempted_ids(self, items: list[PracticeSentence]) -> set[int]:
        """Which of these items already used their (single, scoring) first attempt.

        Derived from the log — a first attempt writes rows with practice_sentence_id set,
        the same way the other review types derive state from their logs.
        """
        if not items:
            return set()
        rows = await self.db.execute(
            select(GrammarPointReviewLog.practice_sentence_id.distinct()).where(
                GrammarPointReviewLog.practice_sentence_id.in_([p.id for p in items])
            )
        )
        return {pid for pid in rows.scalars() if pid is not None}

    async def _target_points(self, p: PracticeSentence) -> list[GrammarPoint]:
        """The item's target points, joined live so key renames stay visible."""
        if not p.target_point_ids:
            return []
        rows = (
            (
                await self.db.execute(
                    select(GrammarPoint).where(GrammarPoint.id.in_(p.target_point_ids))
                )
            )
            .scalars()
            .all()
        )
        by_id = {r.id: r for r in rows}
        return [by_id[i] for i in p.target_point_ids if i in by_id]

    # --- target selection ------------------------------------------------------------------

    async def _select_targets(
        self, user_id: int, count: int, exclude: set[int]
    ) -> list[list[GrammarPoint]]:
        """Pick `count` target groups (1-2 points each) from the rotation pool.

        Pool order: recent failures (latest log row not ok, any origin, oldest failure first)
        → flagged 練習する points (least-recently-practiced first) → weak (worst accuracy,
        min MIN_REVIEWS). Empty pool falls back to the whole bank, least-recently-practiced
        first, so the queue is never dead. `exclude` = points already targeted by pending
        items (no duplicate targets in the queue).
        """
        bank = (
            (
                await self.db.execute(
                    select(GrammarPoint)
                    .where(GrammarPoint.user_id == user_id)
                    .order_by(GrammarPoint.key)
                )
            )
            .scalars()
            .all()
        )
        if not bank:
            return []

        # One pass over the user's point-review log builds every signal the pools need.
        # ponytail: full-log scan, fine at personal scale; aggregate in SQL if it ever hurts.
        log_rows = (
            await self.db.execute(
                select(
                    GrammarPointReviewLog.grammar_point_id,
                    GrammarPointReviewLog.ok,
                    GrammarPointReviewLog.reviewed_at,
                    GrammarPointReviewLog.origin,
                )
                .where(GrammarPointReviewLog.user_id == user_id)
                .order_by(GrammarPointReviewLog.reviewed_at.asc(), GrammarPointReviewLog.id.asc())
            )
        ).all()
        latest: dict[int, tuple[bool, datetime]] = {}
        last_practiced: dict[int, datetime] = {}
        counts: dict[int, list[int]] = {}
        for pid, ok, at, origin in log_rows:
            at = _aware(at)
            latest[pid] = (ok, at)
            if origin == "practice":
                last_practiced[pid] = at
            c = counts.setdefault(pid, [0, 0])
            c[0] += 1
            c[1] += int(ok)

        floor = datetime.min.replace(tzinfo=UTC)

        recent_fail = sorted(
            (p for p in bank if p.id in latest and not latest[p.id][0]),
            key=lambda p: latest[p.id][1],
        )
        in_pool = {p.id for p in recent_fail}
        flagged = sorted(
            (p for p in bank if p.practice and p.id not in in_pool),
            key=lambda p: last_practiced.get(p.id, floor),
        )
        in_pool |= {p.id for p in flagged}
        weak = sorted(
            (
                p
                for p in bank
                if p.id not in in_pool and counts.get(p.id, [0, 0])[0] >= MIN_REVIEWS
            ),
            key=lambda p: counts[p.id][1] / counts[p.id][0],
        )[:WEAK_BOTTOM_N]

        pool = [p for p in recent_fail + flagged + weak if p.id not in exclude]
        if not pool:  # early days: nothing weak/flagged/failed → rotate the whole bank
            pool = sorted(
                (p for p in bank if p.id not in exclude),
                key=lambda p: last_practiced.get(p.id, floor),
            )

        heads = pool[:count]
        # Pairing partners: pool members beyond the heads first, then the rest of the bank —
        # a partner needn't be "due" itself, it just needs real co-occurrence precedent.
        # Never another head (spread stays intact).
        head_ids = {p.id for p in heads}
        spare = pool[len(heads):] + [
            p
            for p in bank
            if p.id not in head_ids
            and p.id not in exclude
            and all(p.id != s.id for s in pool)
        ]
        groups: list[list[GrammarPoint]] = []
        for head in heads:
            partner = await self._co_occurring_partner(head, spare)
            if partner is not None:
                spare.remove(partner)
                groups.append([head, partner])
            else:
                groups.append([head])
        return groups

    async def _co_occurring_partner(
        self, head: GrammarPoint, candidates: list[GrammarPoint]
    ) -> GrammarPoint | None:
        """First candidate that co-occurs with `head` in a real sentence of the user's.

        Forced pairing of unrelated points produces contrived sentences — pairs must have
        precedent in the user's own bank.
        """
        if not candidates:
            return None
        a = SentenceGrammarPoint
        b = SentenceGrammarPoint.__table__.alias()
        co_ids = set(
            (
                await self.db.execute(
                    select(b.c.grammar_point_id)
                    .select_from(a)
                    .join(b, (b.c.sentence_id == a.sentence_id))
                    .where(
                        a.grammar_point_id == head.id,
                        b.c.grammar_point_id != head.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        for c in candidates:
            if c.id in co_ids:
                return c
        return None

    # --- generation ------------------------------------------------------------------------

    async def _generate(
        self, user_id: int, count: int, pending: list[PracticeSentence]
    ) -> int:
        """Generate up to `count` items (per-item commit — one misfire never kills the batch)."""
        exclude = {pid for p in pending for pid in p.target_point_ids}
        groups = await self._select_targets(user_id, count, exclude)
        if not groups:
            return 0

        # Bank with per-point sentence counts — prompt context on what the learner has
        # explicit practice material for (not a level ceiling).
        bank_rows = (
            await self.db.execute(
                select(GrammarPoint, func.count(SentenceGrammarPoint.sentence_id))
                .outerjoin(
                    SentenceGrammarPoint,
                    SentenceGrammarPoint.grammar_point_id == GrammarPoint.id,
                )
                .where(GrammarPoint.user_id == user_id)
                .group_by(GrammarPoint.id)
            )
        ).all()
        bank = {r.key: (r.meaning_en, int(n)) for r, n in bank_rows}
        topics = await self._topics(user_id)
        vocab_words = await self._bait_vocab(user_id)

        # Snapshot to primitives up front: a mid-batch rollback (LLM misfire) expires ORM
        # objects, and touching them afterwards blows up in async SQLAlchemy.
        plans: list[tuple[list[int], dict[str, str]]] = [
            ([p.id for p in group], {p.key: p.meaning_en for p in group})
            for group in groups
        ]

        rejections = await self._rejections(user_id)
        learner_sentences = await self._learner_sentences(user_id)

        created = 0
        for ids, targets in plans:
            history = await self._history(user_id, set(ids))
            try:
                result = await generate_practice(
                    targets=targets,
                    bank=bank,
                    learner_sentences=learner_sentences,
                    history=history,
                    topic=random.choice(topics),
                    vocab=random.sample(vocab_words, min(VOCAB_BAIT, len(vocab_words))),
                    rejections=rejections,
                )
                self.db.add(
                    PracticeSentence(
                        user_id=user_id,
                        english=result.english,
                        japanese=result.japanese,
                        politeness=Politeness.MIXED,  # register isn't the training goal here
                        target_point_ids=ids,
                    )
                )
                await self.db.commit()
                created += 1
            except (OpenAIError, RuntimeError) as e:
                await self.db.rollback()
                logger.warning(
                    "llm_error_generating_practice",
                    user_id=user_id,
                    targets=list(targets),
                    error_type=type(e).__name__,
                    error=str(e),
                )
        return created

    async def _history(self, user_id: int, target_ids: set[int]) -> list[str]:
        """Recent practice sentences sharing a target point — the anti-rote context.

        Rejected items are excluded — they go into the rejections section instead.
        """
        rows = (
            (
                await self.db.execute(
                    select(PracticeSentence)
                    .where(
                        PracticeSentence.user_id == user_id,
                        PracticeSentence.status != "rejected",
                    )
                    .order_by(PracticeSentence.created_at.desc())
                    .limit(100)
                )
            )
            .scalars()
            .all()
        )
        return [
            r.japanese for r in rows if set(r.target_point_ids) & target_ids
        ][:HISTORY_PER_POINT]

    async def _learner_sentences(self, user_id: int) -> list[str]:
        """A sample of the learner's own production sentences — the vocabulary-level anchor.

        Random sample (not newest-first) so the anchor reflects their whole range, not the
        last topic they binged on.
        """
        rows = (
            (
                await self.db.execute(
                    select(ProductionSentence.japanese).where(
                        ProductionSentence.user_id == user_id
                    )
                )
            )
            .scalars()
            .all()
        )
        return random.sample(list(rows), min(LEARNER_SAMPLE, len(rows)))

    async def _rejections(self, user_id: int) -> list[tuple[str, str]]:
        """Recent rejected sentences + reasons — the avoid-context (any target, newest first)."""
        rows = (
            (
                await self.db.execute(
                    select(PracticeSentence)
                    .where(
                        PracticeSentence.user_id == user_id,
                        PracticeSentence.status == "rejected",
                    )
                    .order_by(PracticeSentence.completed_at.desc())
                    .limit(REJECTIONS_FED)
                )
            )
            .scalars()
            .all()
        )
        return [(r.japanese, r.reject_reason or "") for r in rows]

    async def _bait_vocab(self, user_id: int) -> list[str]:
        """The user's apprentice/guru vocab — words that still need production exposure."""
        rows = (
            await self.db.execute(
                select(Vocab.word)
                .join(
                    UserItemProgress,
                    (UserItemProgress.item_id == Vocab.id)
                    & (UserItemProgress.item_type == ItemType.VOCAB),
                )
                .where(
                    UserItemProgress.user_id == user_id,
                    UserItemProgress.srs_stage.between(1, 6),
                )
            )
        ).scalars()
        return list(rows)

    async def _topics(self, user_id: int) -> list[str]:
        user = await self.db.get(User, user_id)
        custom = (user.practice_topics or []) if user else []
        return DEFAULT_TOPICS + custom

    # --- topics ----------------------------------------------------------------------------

    async def get_topics(self, user_id: int) -> PracticeTopicsResponse:
        """The generation topic seeds: built-in defaults + the user's own additions."""
        user = await self.db.get(User, user_id)
        return PracticeTopicsResponse(
            defaults=DEFAULT_TOPICS, custom=(user.practice_topics or []) if user else []
        )

    async def set_topics(self, user_id: int, topics: list[str]) -> PracticeTopicsResponse:
        """Replace the user's custom topic list (defaults are fixed)."""
        user = await self.db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")
        user.practice_topics = [t.strip() for t in topics if t.strip()]
        await self.db.commit()
        return PracticeTopicsResponse(defaults=DEFAULT_TOPICS, custom=user.practice_topics)

    # --- review ----------------------------------------------------------------------------

    async def submit(
        self, user_id: int, practice_id: int, submitted: str
    ) -> PracticeReviewResponse:
        """Judge an attempt at a practice item.

        Always judges (exact-match fast path first). Only the FIRST attempt scores — it writes
        `origin='practice'` rows (with the item back-reference); retries are judged for display
        only (the user has seen the reference — contaminated signal). A correct attempt (any
        attempt) completes the item. Raises LookupError (→ 404) / ValueError (→ 400).
        """
        try:
            now = datetime.now(UTC)
            item = await self.db.get(PracticeSentence, practice_id)
            if item is None or item.user_id != user_id:
                raise LookupError("Practice item not found")
            if item.status != "pending":
                raise ValueError("Practice item is already completed")

            targets = await self._target_points(item)

            point_ok: dict[str, bool]
            point_fb: dict[str, str | None]
            if _normalize(submitted) == _normalize(item.japanese):
                correct, exact, feedback = True, True, None
                point_ok = {p.key: True for p in targets}
                point_fb = {p.key: None for p in targets}
            else:
                result = await judge(
                    item.english,
                    item.japanese,
                    submitted,
                    item.politeness.value,
                    grammar_points={p.key: p.meaning_en for p in targets},
                    points_required=True,  # dodging a target = failing it (practice-only rule)
                )
                correct, exact, feedback = result.correct, False, result.feedback
                # Same verdict mapping as sentence reviews: failures-only list, unlisted →
                # ok (positive identification), "key — gloss" echoes stripped.
                flagged = {
                    v.key.split(" — ")[0].strip(): v for v in result.point_verdicts
                }
                point_ok = {
                    p.key: flagged[p.key].ok if p.key in flagged else True
                    for p in targets
                }
                point_fb = {
                    p.key: (flagged[p.key].feedback if p.key in flagged else None)
                    for p in targets
                }

            scored = not await self._attempted_ids([item])
            if scored:
                for p in targets:
                    self.db.add(
                        GrammarPointReviewLog(
                            user_id=user_id,
                            grammar_point_id=p.id,
                            review_log_id=None,
                            practice_sentence_id=item.id,
                            origin="practice",
                            ok=point_ok[p.key],
                            feedback=point_fb[p.key] if not point_ok[p.key] else None,
                            reviewed_at=now,
                        )
                    )
            if correct:
                item.status = "done"
                item.completed_at = now
            await self.db.commit()

            return PracticeReviewResponse(
                practice_id=item.id,
                correct=correct,
                exact_match=exact,
                feedback=feedback,
                reference=item.japanese,
                scored=scored,
                done=item.status == "done",
                point_results=[
                    SentencePointResult(
                        key=p.key,
                        ok=point_ok[p.key],
                        feedback=point_fb[p.key] if not point_ok[p.key] else None,
                    )
                    for p in targets
                ],
            )
        except (OpenAIError, RuntimeError) as e:
            await self.db.rollback()
            logger.warning(
                "llm_error_submitting_practice_review",
                user_id=user_id,
                practice_id=practice_id,
                error_type=type(e).__name__,
                error=str(e),
            )
            raise
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(
                "database_error_submitting_practice_review",
                user_id=user_id,
                practice_id=practice_id,
                error_type=type(e).__name__,
                error=str(e),
            )
            raise

    async def complete(self, user_id: int, practice_id: int) -> None:
        """Escape hatch (「正解として進む」): mark done without judging. Idempotent.

        The first attempt already scored whatever it scored — this never writes log rows.
        Raises LookupError (→ 404) if not the user's.
        """
        item = await self.db.get(PracticeSentence, practice_id)
        if item is None or item.user_id != user_id:
            raise LookupError("Practice item not found")
        if item.status == "pending":  # done/rejected → no-op
            item.status = "done"
            item.completed_at = datetime.now(UTC)
            await self.db.commit()
