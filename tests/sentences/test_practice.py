"""Tests for the grammar-practice rotation: selection pools, lazy generation, scoring, escape."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import Session, User
from src.core.constants import Politeness
from src.llm.judge import JudgeResult, PointVerdict
from src.llm.practice import GeneratedPractice
from src.sentences.models import (
    GrammarPoint,
    GrammarPointReviewLog,
    PracticeSentence,
    ProductionSentence,
    SentenceGrammarPoint,
)
from src.sentences.practice import BATCH_SIZE, CAP, MIN_REVIEWS, PracticeService

NOW = datetime.now(UTC)


async def _user(db: AsyncSession) -> User:
    user = User(username=f"practice-{datetime.now(UTC).timestamp()}", sentences_enabled=True)
    db.add(user)
    await db.flush()
    return user


async def _point(db: AsyncSession, user: User, key: str, practice: bool = False) -> GrammarPoint:
    p = GrammarPoint(user_id=user.id, key=key, meaning_en=f"gloss {key}", practice=practice)
    db.add(p)
    await db.flush()
    return p


def _log(
    user: User,
    point: GrammarPoint,
    ok: bool,
    at: datetime,
    origin: str = "sentence",
    practice_sentence_id: int | None = None,
):
    return GrammarPointReviewLog(
        user_id=user.id,
        grammar_point_id=point.id,
        review_log_id=None,
        practice_sentence_id=practice_sentence_id,
        origin=origin,
        ok=ok,
        reviewed_at=at,
    )


def _fake_generate(calls: list | None = None):
    async def fake(**kwargs) -> GeneratedPractice:
        if calls is not None:
            calls.append(kwargs)
        n = len(calls) if calls is not None else 0
        return GeneratedPractice(english=f"prompt {n}", japanese=f"文{n}です")

    return fake


def _fake_judge(result: JudgeResult):
    async def fake(*args, **kwargs) -> JudgeResult:
        return fake.result  # type: ignore[attr-defined]

    fake.result = result  # type: ignore[attr-defined]
    return fake


# --- target selection ---------------------------------------------------------------------------


async def test_selection_orders_recent_fail_flagged_weak(db_session) -> None:
    user = await _user(db_session)
    failed = await _point(db_session, user, "〜failed")
    await _point(db_session, user, "〜flagged", practice=True)
    weak = await _point(db_session, user, "〜weak")
    strong = await _point(db_session, user, "〜strong")

    db_session.add(_log(user, failed, ok=False, at=NOW))
    for i in range(MIN_REVIEWS):
        db_session.add(_log(user, weak, ok=i == 0, at=NOW - timedelta(days=1, hours=i)))
        db_session.add(_log(user, strong, ok=True, at=NOW - timedelta(days=1, hours=i)))
    await db_session.flush()

    groups = await PracticeService(db_session)._select_targets(user.id, 3, set())
    heads = [g[0].key for g in groups]
    assert heads == ["〜failed", "〜flagged", "〜weak"]


async def test_selection_falls_back_to_whole_bank(db_session) -> None:
    user = await _user(db_session)
    a = await _point(db_session, user, "〜a")
    b = await _point(db_session, user, "〜b")
    # b was practiced recently, a never → a rotates first.
    db_session.add(_log(user, b, ok=True, at=NOW, origin="practice"))
    await db_session.flush()

    groups = await PracticeService(db_session)._select_targets(user.id, 2, set())
    assert [g[0].key for g in groups] == ["〜a", "〜b"]
    assert a.id == groups[0][0].id


async def test_selection_excludes_pending_targets(db_session) -> None:
    user = await _user(db_session)
    a = await _point(db_session, user, "〜a")
    b = await _point(db_session, user, "〜b")
    await db_session.flush()

    groups = await PracticeService(db_session)._select_targets(user.id, 2, {a.id})
    assert [g[0].key for g in groups] == ["〜b"]
    assert b.id == groups[0][0].id


async def test_selection_pairs_co_occurring_points(db_session) -> None:
    user = await _user(db_session)
    head = await _point(db_session, user, "〜head")
    partner = await _point(db_session, user, "〜partner")
    db_session.add(_log(user, head, ok=False, at=NOW))
    sentence = ProductionSentence(
        user_id=user.id, english="e", japanese="j", politeness=Politeness.CASUAL
    )
    db_session.add(sentence)
    await db_session.flush()
    db_session.add(SentenceGrammarPoint(sentence_id=sentence.id, grammar_point_id=head.id))
    db_session.add(SentenceGrammarPoint(sentence_id=sentence.id, grammar_point_id=partner.id))
    await db_session.flush()

    groups = await PracticeService(db_session)._select_targets(user.id, 1, set())
    assert len(groups) == 1
    assert [p.key for p in groups[0]] == ["〜head", "〜partner"]


async def test_selection_never_pairs_without_co_occurrence(db_session) -> None:
    user = await _user(db_session)
    await _point(db_session, user, "〜a")
    await _point(db_session, user, "〜b")
    await db_session.flush()

    groups = await PracticeService(db_session)._select_targets(user.id, 1, set())
    assert len(groups) == 1
    assert len(groups[0]) == 1  # unrelated points never forced together


# --- queue + lazy generation ----------------------------------------------------------------


async def test_queue_generates_batch_when_empty(db_session, monkeypatch) -> None:
    user = await _user(db_session)
    for k in ("〜a", "〜b", "〜c", "〜d"):
        await _point(db_session, user, k)
    await db_session.flush()
    calls: list = []
    monkeypatch.setattr("src.sentences.practice.generate_practice", _fake_generate(calls))

    result = await PracticeService(db_session).get_queue(user.id)

    assert result.count == BATCH_SIZE
    assert len(calls) == BATCH_SIZE
    assert result.bonus_available is False
    keys = {t.key for item in result.items for t in item.targets}
    assert len(keys) == BATCH_SIZE  # spread: distinct targets
    assert all("japanese" not in item.model_dump() for item in result.items)


async def test_queue_does_not_regenerate_within_interval(db_session, monkeypatch) -> None:
    user = await _user(db_session)
    await _point(db_session, user, "〜a")
    await _point(db_session, user, "〜b")
    await db_session.flush()
    calls: list = []
    monkeypatch.setattr("src.sentences.practice.generate_practice", _fake_generate(calls))

    service = PracticeService(db_session)
    first = await service.get_queue(user.id)
    n = len(calls)
    assert n >= 1
    second = await service.get_queue(user.id)  # immediately again → interval not elapsed
    assert len(calls) == n
    assert second.count == first.count


async def test_queue_tops_up_after_interval_respecting_cap(db_session, monkeypatch) -> None:
    user = await _user(db_session)
    for k in ("〜a", "〜b", "〜c", "〜d"):
        await _point(db_session, user, k)
    a = (await db_session.execute(select(GrammarPoint))).scalars().first()
    # One old pending item → room for CAP-1 more, and the interval has passed.
    db_session.add(
        PracticeSentence(
            user_id=user.id,
            english="old",
            japanese="古い文",
            politeness=Politeness.MIXED,
            target_point_ids=[a.id],
            created_at=NOW - timedelta(hours=9),
        )
    )
    await db_session.flush()
    calls: list = []
    monkeypatch.setattr("src.sentences.practice.generate_practice", _fake_generate(calls))

    result = await PracticeService(db_session).get_queue(user.id)
    assert result.count == CAP
    assert len(calls) == CAP - 1


async def test_bonus_generates_one_and_respects_cap(db_session, monkeypatch) -> None:
    user = await _user(db_session)
    await _point(db_session, user, "〜a")
    await db_session.flush()
    calls: list = []
    monkeypatch.setattr("src.sentences.practice.generate_practice", _fake_generate(calls))

    service = PracticeService(db_session)
    result = await service.generate_bonus(user.id)
    assert result.count == 1
    assert len(calls) == 1

    # Fill to CAP, then bonus must refuse.
    for i in range(CAP - 1):
        db_session.add(
            PracticeSentence(
                user_id=user.id,
                english=f"e{i}",
                japanese=f"j{i}",
                politeness=Politeness.MIXED,
                target_point_ids=[],
            )
        )
    await db_session.flush()
    with pytest.raises(ValueError, match="full"):
        await service.generate_bonus(user.id)


async def test_bonus_with_empty_bank_raises(db_session, monkeypatch) -> None:
    user = await _user(db_session)
    await db_session.flush()
    monkeypatch.setattr("src.sentences.practice.generate_practice", _fake_generate([]))
    with pytest.raises(ValueError, match="generated"):
        await PracticeService(db_session).generate_bonus(user.id)


async def test_generation_failure_skips_item_not_batch(db_session, monkeypatch) -> None:
    user = await _user(db_session)
    for k in ("〜a", "〜b", "〜c"):
        await _point(db_session, user, k)
    await db_session.flush()

    n = 0

    async def flaky(**kwargs) -> GeneratedPractice:
        nonlocal n
        n += 1
        if n == 2:
            raise RuntimeError("boom")
        return GeneratedPractice(english=f"p{n}", japanese=f"文{n}")

    monkeypatch.setattr("src.sentences.practice.generate_practice", flaky)

    result = await PracticeService(db_session).get_queue(user.id)
    assert result.count == BATCH_SIZE - 1  # one misfire, rest of the batch survived


# --- review flow ------------------------------------------------------------------------------


async def _seed_item(
    db: AsyncSession, user: User, points: list[GrammarPoint]
) -> PracticeSentence:
    item = PracticeSentence(
        user_id=user.id,
        english="I ate.",
        japanese="食べたんです",
        politeness=Politeness.MIXED,
        target_point_ids=[p.id for p in points],
    )
    db.add(item)
    await db.flush()
    return item


async def test_first_attempt_exact_match_scores_and_completes(db_session) -> None:
    user = await _user(db_session)
    point = await _point(db_session, user, "〜んです")
    item = await _seed_item(db_session, user, [point])

    result = await PracticeService(db_session).submit(user.id, item.id, "食べたんです。")

    assert result.correct and result.exact_match and result.done and result.scored
    assert result.reference == "食べたんです"
    logs = (
        (await db_session.execute(select(GrammarPointReviewLog))).scalars().all()
    )
    assert len(logs) == 1
    assert logs[0].origin == "practice"
    assert logs[0].review_log_id is None
    assert logs[0].ok is True
    assert item.status == "done"


async def test_first_attempt_wrong_scores_failure_and_stays_pending(
    db_session, monkeypatch
) -> None:
    user = await _user(db_session)
    point = await _point(db_session, user, "〜んです")
    item = await _seed_item(db_session, user, [point])
    monkeypatch.setattr(
        "src.sentences.practice.judge",
        _fake_judge(
            JudgeResult(
                reason="r",
                correct=False,
                feedback="wrong",
                point_verdicts=[PointVerdict(key="〜んです", ok=False, feedback="broken")],
            )
        ),
    )

    result = await PracticeService(db_session).submit(user.id, item.id, "食べた")

    assert not result.correct and result.scored and not result.done
    assert result.point_results[0].ok is False
    assert result.point_results[0].feedback == "broken"
    logs = (await db_session.execute(select(GrammarPointReviewLog))).scalars().all()
    assert len(logs) == 1 and logs[0].ok is False and logs[0].feedback == "broken"
    assert item.status == "pending"


async def test_retry_never_logs_but_can_complete(db_session, monkeypatch) -> None:
    user = await _user(db_session)
    point = await _point(db_session, user, "〜んです")
    item = await _seed_item(db_session, user, [point])
    # First attempt already happened: its log row (with the back-reference) is the marker.
    db_session.add(
        _log(user, point, ok=False, at=NOW, origin="practice", practice_sentence_id=item.id)
    )
    await db_session.flush()

    result = await PracticeService(db_session).submit(user.id, item.id, "食べたんです")

    assert result.correct and result.done
    assert result.scored is False
    logs = (await db_session.execute(select(GrammarPointReviewLog))).scalars().all()
    assert len(logs) == 1  # still only the first-attempt row


async def test_submit_on_done_item_rejected(db_session) -> None:
    user = await _user(db_session)
    point = await _point(db_session, user, "〜んです")
    item = await _seed_item(db_session, user, [point])
    item.status = "done"
    await db_session.flush()

    with pytest.raises(ValueError, match="completed"):
        await PracticeService(db_session).submit(user.id, item.id, "食べたんです")


async def test_submit_not_owner_404(db_session) -> None:
    user = await _user(db_session)
    other = await _user(db_session)
    point = await _point(db_session, user, "〜んです")
    item = await _seed_item(db_session, user, [point])

    with pytest.raises(LookupError):
        await PracticeService(db_session).submit(other.id, item.id, "食べたんです")


async def test_complete_escape_marks_done_without_logging(db_session) -> None:
    user = await _user(db_session)
    point = await _point(db_session, user, "〜んです")
    item = await _seed_item(db_session, user, [point])

    service = PracticeService(db_session)
    await service.complete(user.id, item.id)
    assert item.status == "done"
    logs = (await db_session.execute(select(GrammarPointReviewLog))).scalars().all()
    assert logs == []
    await service.complete(user.id, item.id)  # idempotent


# --- topics ----------------------------------------------------------------------------------


async def test_topics_roundtrip(db_session) -> None:
    user = await _user(db_session)
    await db_session.flush()
    service = PracticeService(db_session)

    initial = await service.get_topics(user.id)
    assert initial.custom == [] and len(initial.defaults) > 0

    updated = await service.set_topics(user.id, ["trains", "  ", "my cat"])
    assert updated.custom == ["trains", "my cat"]  # blanks stripped
    assert (await service.get_topics(user.id)).custom == ["trains", "my cat"]


# --- router roundtrip --------------------------------------------------------------------------


async def test_practice_router_roundtrip(async_client, db_session, monkeypatch) -> None:
    user = User(username="practice-router", sentences_enabled=True)
    db_session.add(user)
    await db_session.flush()
    db_session.add(Session(user_id=user.id, token="tok-practice-1"))
    point = GrammarPoint(user_id=user.id, key="〜んです", meaning_en="explanatory")
    db_session.add(point)
    await db_session.commit()
    headers = {"Authorization": "Bearer tok-practice-1"}

    async def fake(**kwargs) -> GeneratedPractice:
        return GeneratedPractice(english="I ate.", japanese="食べたんです")

    monkeypatch.setattr("src.sentences.practice.generate_practice", fake)

    queue = await async_client.get("/api/v1/me/practice", headers=headers)
    assert queue.status_code == 200
    body = queue.json()
    assert body["count"] >= 1
    item = body["items"][0]
    assert item["targets"][0]["key"] == "〜んです"
    assert "japanese" not in item

    submit = await async_client.post(
        f"/api/v1/me/practice/{item['practice_id']}/reviews",
        headers=headers,
        json={"submitted": "食べたんです"},
    )
    assert submit.status_code == 200
    result = submit.json()
    assert result["correct"] is True and result["done"] is True and result["scored"] is True

    topics = await async_client.put(
        "/api/v1/me/practice/topics", headers=headers, json={"topics": ["trains"]}
    )
    assert topics.status_code == 200
    assert topics.json()["custom"] == ["trains"]

    flag = await async_client.patch(
        f"/api/v1/me/grammar/{point.id}", headers=headers, json={"practice": True}
    )
    assert flag.status_code == 200
    assert flag.json()["practice"] is True
