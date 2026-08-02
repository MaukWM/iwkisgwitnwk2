"""Production-SRS sentence Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.core.constants import Politeness


class SentenceCreateRequest(BaseModel):
    """Add a production sentence. The EN/JP pair is validated server-side before insert;
    extracted grammar points are auto-linked (correct afterwards on the sentence page)."""

    english: str = Field(..., min_length=1, description="English prompt")
    japanese: str = Field(..., min_length=1, description="Japanese reference answer")


class SentenceGrammarItem(BaseModel):
    """A grammar point linked to a sentence (sentence detail page)."""

    grammar_point_id: int = Field(..., gt=0)
    key: str
    meaning_en: str
    evidence: str | None = Field(None, description="Substring of the sentence showing the point")


class SentenceGrammarAttachRequest(BaseModel):
    """Hand-attach an existing bank point to a sentence (post-add correction)."""

    grammar_point_id: int = Field(..., gt=0)


class SentenceCreateResponse(BaseModel):
    """A newly created production sentence. It waits as a pending lesson until learned."""

    sentence_id: int = Field(..., gt=0)
    english: str
    japanese: str
    politeness: Politeness

    model_config = {"from_attributes": True}


class SentenceUpdateRequest(BaseModel):
    """Edit a production sentence's EN/JP pair. Re-validated server-side (like create)."""

    english: str = Field(..., min_length=1, description="English prompt")
    japanese: str = Field(..., min_length=1, description="Japanese reference answer")


class DueSentenceResponse(BaseModel):
    """A production sentence due for review.

    Deliberately omits `japanese` — the user must PRODUCE it; the reference answer
    stays server-side until they submit.
    """

    sentence_id: int = Field(..., gt=0)
    english: str = Field(..., description="The English prompt to translate")
    politeness: Politeness = Field(..., description="Target politeness (not the answer)")
    srs_stage: int = Field(..., ge=1, le=9)

    model_config = {"from_attributes": True}


class DueSentencesResponse(BaseModel):
    """Envelope for the due-sentence queue."""

    items: list[DueSentenceResponse]
    count: int


class SentenceReviewCreateRequest(BaseModel):
    """Submit a written attempt at a production sentence."""

    sentence_id: int = Field(..., gt=0)
    submitted: str = Field(..., min_length=1, description="The user's Japanese attempt")


class SentenceJudgeRequest(BaseModel):
    """Grade an attempt WITHOUT touching SRS (used by the lesson quiz gate)."""

    submitted: str = Field(..., min_length=1, description="The user's Japanese attempt")


class SentenceJudgeResponse(BaseModel):
    """Stateless judge verdict — no SRS change, no log written."""

    correct: bool
    exact_match: bool
    feedback: str | None
    reference: str
    point_results: list["SentencePointResult"] = Field(
        default_factory=list,
        description="Per-grammar-point verdicts, display only (nothing logged on this path)",
    )


class SentenceListItem(BaseModel):
    """A production sentence in the management list (reference JP visible — this is YOUR list).

    srs_stage is None while the sentence is a pending lesson (not yet learned).
    """

    sentence_id: int = Field(..., gt=0)
    english: str
    japanese: str
    politeness: Politeness
    srs_stage: int | None = Field(None, ge=1, le=9)
    next_review_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SentenceLessonItem(BaseModel):
    """A pending sentence lesson — study card shows BOTH english and japanese."""

    sentence_id: int = Field(..., gt=0)
    english: str
    japanese: str
    politeness: Politeness

    model_config = {"from_attributes": True}


class SentenceLessonsResponse(BaseModel):
    """Envelope for pending sentence lessons."""

    items: list[SentenceLessonItem]
    count: int


class SentenceLessonCompleteRequest(BaseModel):
    """Learn a batch of pending sentences — they enter SRS at Apprentice 1."""

    sentence_ids: list[int] = Field(..., min_length=1)


class SentenceLessonCompleteResponse(BaseModel):
    """Outcome of completing sentence lessons."""

    learned: list[int]
    count: int


class SentenceListResponse(BaseModel):
    """Envelope for the full sentence list."""

    items: list[SentenceListItem]
    count: int


class SentenceReviewLogItem(BaseModel):
    """One past review of a sentence, for the detail page history."""

    submitted: str
    exact_match: bool
    correct: bool
    feedback: str | None
    overridden: bool
    override_reason: str | None
    srs_stage_before: int
    srs_stage_after: int
    reviewed_at: datetime

    model_config = {"from_attributes": True}


class SentenceDetailResponse(BaseModel):
    """A single production sentence with its full review history."""

    sentence_id: int = Field(..., gt=0)
    english: str
    japanese: str
    politeness: Politeness
    srs_stage: int | None = Field(None, ge=1, le=9)  # None while a pending lesson
    next_review_at: datetime | None
    created_at: datetime
    reviews: list[SentenceReviewLogItem]
    grammar: list[SentenceGrammarItem] = Field(
        default_factory=list, description="Grammar points this sentence exercises"
    )


class SentenceOverrideRequest(BaseModel):
    """Override the latest (rejected) review of a sentence, accepting the answer."""

    reason: str | None = Field(
        None, description="Why it should count as correct — fed to the judge on future reviews"
    )


class SentenceOverrideResponse(BaseModel):
    """Outcome of an override: SRS advanced as if the answer were correct."""

    sentence_id: int = Field(..., gt=0)
    overridden: bool = True
    srs_stage_before: int = Field(..., ge=1, le=9)
    srs_stage_after: int = Field(..., ge=1, le=9)
    next_review_at: datetime | None


class GrammarPointListItem(BaseModel):
    """One personal grammar point in the bank list, with usage count + review accuracy."""

    grammar_point_id: int = Field(..., gt=0)
    key: str
    meaning_en: str
    practice: bool = Field(False, description="練習する — opted into the practice rotation")
    sentence_count: int = Field(..., ge=0)
    review_count: int = Field(0, ge=0, description="First-attempt reviews touching this point")
    correct_count: int = Field(0, ge=0, description="Of those, how many produced it correctly")
    created_at: datetime


class GrammarPointListResponse(BaseModel):
    """Envelope for the grammar bank."""

    items: list[GrammarPointListItem]
    count: int


class GrammarSentenceItem(BaseModel):
    """A sentence linked to a grammar point (detail view)."""

    sentence_id: int = Field(..., gt=0)
    english: str
    japanese: str
    evidence: str | None
    srs_stage: int | None = Field(None, ge=1, le=9)  # None = pending lesson

    model_config = {"from_attributes": True}


class GrammarPointDetailResponse(BaseModel):
    """One grammar point with every sentence that exercises it."""

    grammar_point_id: int = Field(..., gt=0)
    key: str
    meaning_en: str
    practice: bool = Field(False, description="練習する — opted into the practice rotation")
    review_count: int = Field(0, ge=0)
    correct_count: int = Field(0, ge=0)
    created_at: datetime
    sentences: list[GrammarSentenceItem]


class GrammarPointUpdateRequest(BaseModel):
    """Rename a grammar point's key or gloss (fix a mis-minted extraction), or toggle 練習する."""

    key: str | None = Field(None, min_length=1, max_length=100)
    meaning_en: str | None = Field(None, min_length=1, max_length=255)
    practice: bool | None = Field(
        None, description="Opt the point in/out of the practice rotation (flag only ADDS — "
        "an unflagged point still rotates in via weak/recent-failure evidence)"
    )


class PracticeTargetItem(BaseModel):
    """A target grammar point of a practice item (joined live — renames stay visible)."""

    grammar_point_id: int = Field(..., gt=0)
    key: str
    meaning_en: str


class PracticeItem(BaseModel):
    """A pending practice item. Omits `japanese` — the user must produce it."""

    practice_id: int = Field(..., gt=0)
    english: str = Field(..., description="The English prompt to translate")
    politeness: Politeness = Field(..., description="Always mixed for practice items")
    targets: list[PracticeTargetItem] = Field(..., description="Grammar points to exercise")
    created_at: datetime


class PracticeQueueResponse(BaseModel):
    """The practice queue. Fetching lazily tops it up (cap + interval permitting)."""

    items: list[PracticeItem]
    count: int
    bonus_available: bool = Field(
        ..., description="Queue is empty — the user may request a bonus item"
    )


class PracticeRejectRequest(BaseModel):
    """Reject a generated practice item, with a why (fed back into future generations)."""

    reason: str = Field(..., min_length=1, description="Why this sentence is bad")


class PracticeReviewCreateRequest(BaseModel):
    """Submit a written attempt at a practice item."""

    submitted: str = Field(..., min_length=1, description="The user's Japanese attempt")


class PracticeReviewResponse(BaseModel):
    """Outcome of a practice attempt. Only the first attempt scores (`scored`)."""

    practice_id: int = Field(..., gt=0)
    correct: bool
    exact_match: bool
    feedback: str | None
    reference: str = Field(..., description="The reference Japanese, revealed after submission")
    scored: bool = Field(..., description="This was the first attempt — point rows were logged")
    done: bool = Field(..., description="Item completed (correct answer)")
    point_results: list["SentencePointResult"] = Field(default_factory=list)


class PracticeTopicsUpdateRequest(BaseModel):
    """Replace the user's custom topic seeds (defaults are fixed)."""

    topics: list[str] = Field(..., description="Custom topic strings; empty list clears them")


class PracticeTopicsResponse(BaseModel):
    """Generation topic seeds: built-in defaults + the user's own."""

    defaults: list[str]
    custom: list[str]


class SentencePointResult(BaseModel):
    """Per-grammar-point outcome of one submission (judge-attributed)."""

    key: str
    ok: bool
    feedback: str | None = Field(
        None, description="For failed points: one-line note — broken fragment + rule violated"
    )


class SentenceReviewResponse(BaseModel):
    """Outcome of a submitted production review."""

    sentence_id: int = Field(..., gt=0)
    correct: bool
    exact_match: bool = Field(..., description="Passed via normalized exact-match (no LLM)")
    feedback: str | None = Field(None, description="Why wrong, or a better phrasing when correct")
    reference: str = Field(..., description="The reference Japanese, revealed after submission")
    srs_stage_before: int = Field(..., ge=1, le=9)
    srs_stage_after: int = Field(..., ge=1, le=9)
    next_review_at: datetime | None = Field(..., description="Next review time, or None if burned")
    point_results: list[SentencePointResult] = Field(
        default_factory=list,
        description="Per-grammar-point verdicts for this sentence's linked points",
    )
