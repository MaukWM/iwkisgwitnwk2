# Grammar Practice Rotation — Design

Status: **design agreed, not yet built** (2026-07-23). Builds on the grammar tracking layer
shipped in 1.7.0 (extraction, bank, per-point scoring via `grammar_point_review_log`).

## Goal

Active production practice for weak / user-chosen grammar points. Complements the existing
1-1 sentence SRS:

| Layer | Cue | Variability | Trains |
|---|---|---|---|
| Sentence SRS (existing) | uncued — EN prompt only | fixed sentence | retrieval (testing effect) |
| Grammar practice (this) | cued — target point shown | new sentence every time | generalization + proceduralization (variability of practice) |

Rote repetition is the enemy: practice items are **one-shot** — reviewed until correct, then
done forever. Internalization signal lives in per-point accuracy, never in item repetition.

## Flow

1. **Generation (lazy, no cron).** On queue fetch: if `pending < CAP` and last generation
   older than `INTERVAL_HOURS` → generate a batch. Natural backpressure: user absent 3 days →
   still CAP items waiting, not 24.
2. **Review.** Same UX as sentence review: EN prompt shown + target grammar point(s) shown
   (cued production is deliberate — see theory table). User writes JP, judge grades against
   the generated reference with the target points passed as linked points. Wrong → retry
   until right (retries display-only, as today). Escape hatch (「正解として進む」) applies.
3. **Logging.** First attempt only → `grammar_point_review_log` rows with `origin='practice'`
   for the target points. Item → `done`, archived (kept — it feeds anti-rote history).

## Target selection (server-side algorithm, not LLM, not per-item user choice)

Pool = union of:

- **Flagged** — user pressed 練習する on the point (bool on `grammar_points`). Always in pool.
- **Recent failure** — point's latest log row (any origin) has `ok=false`. This is the requeue
  mechanism: judge attribution decides which points from a failed sentence re-enter — only
  the flagged-at-fault ones, never all linked points. Vocab-fault failure → nothing requeued.
- **Weak** — bottom-N all-time accuracy, minimum `MIN_REVIEWS` first-attempt reviews (else noise).

Order within pool: recent failures first → flagged, least-recently-practiced first
(never-practiced = first) → weak rotation. `last practiced` = max `reviewed_at` where
`origin='practice'`.

Spacing is free: a just-failed point becomes eligible next batch; `INTERVAL_HOURS` prevents
an immediate short-term-memory re-test.

Per item: **1 target point; 2 only when the pair co-occurs in the user's real sentence bank**
(`sentence_grammar_points` self-join). Forced pairing of unrelated points → contrived
sentences → bad practice.

## Generation prompt (one LLM call per item)

Inputs:

- **Target point(s)** — key + gloss. Sentence MUST exercise them.
- **Full grammar bank** (key → gloss) — as *context*, not choice: "may only otherwise use
  grammar from this bank" → output stays inside the user's known level. ~60 keys = trivial cost.
- **Anti-rote history** — last ~15 done practice sentences *for the same target point*
  (per-point beats global: that's where rote repeats happen) + "must differ in topic and
  structure".
- **Topic seed** — rotated server-side (daily life / work / opinion / past experience /
  hypothetical / …) so the model doesn't converge on one genre.
- **Vocab bait** — ~5 sampled apprentice/guru vocab from the user's bank; "weave 1-2 in
  naturally, skip any that feel forced". Exposure only — the judge does NOT score vocab
  (settled principle: vocab mistakes never attribute to grammar). Doubles as topic material.
- **Politeness** — model picks the register natural to the target point (〜んだけどさ is
  casual-only; forcing 丁寧 would be wrong), outputs it; stored and enforced by the judge
  like any sentence.

Output (structured): `english`, `japanese` (reference), `politeness`.

## Schema

One new table + one column:

```
practice_sentences
  id            PK
  user_id       FK users
  english       Text
  japanese      Text            -- reference answer
  politeness    Enum            -- always 'mixed' (decision 8)
  target_point_ids JSON         -- [grammar_point_id, ...]; ephemeral items, no link table
  status        String(pending, done)
  created_at, completed_at      -- no attempted_at: "first attempt used" is derived from the
                                -- log (rows with practice_sentence_id), like other review types

grammar_points
  + practice    Bool default false   -- the 練習する flag

grammar_point_review_log
  + origin      String(sentence, practice) default 'sentence'   -- planned since 1.7.0
  + practice_sentence_id -> nullable FK: back-reference for practice rows (provenance + the
                            first-attempt marker); sentence rows use review_log_id instead
  review_log_id -> nullable (practice rows have no sentence review log)

users
  + practice_topics JSON        -- user-added topic seeds (decision 9)
```

Judge, review UI, override/escape, point-verdict mapping: all reused unchanged.

## API surface (sketch)

- `GET  /sentences/practice` — queue fetch; triggers lazy generation.
- `POST /sentences/practice/{id}/reviews` — submit attempt (mirrors sentence review; logs
  origin='practice', flips status on correct).
- `POST /sentences/practice/{id}/judge` — stateless retry grading (mirrors existing).
- `PATCH /me/grammar/{id}` — gains `practice: bool` (the flag).

Frontend: queue tile on dashboard + practice review page (reuse QuizShell/review components);
練習する toggle on grammar detail + bank list.

## Defaults (tune later)

| Knob | Default |
|---|---|
| `INTERVAL_HOURS` | 8 |
| Batch size | 3 |
| `CAP` (max pending) | 3 |
| `MIN_REVIEWS` for weak pool | 3 |
| Bottom-N weak | 5 |
| Anti-rote history fed | 15 per point |
| Vocab bait sampled | 5 |

## Backlog (considered, deliberately not now)

- **Score non-target grammar from the submission** (2026-07-24): extracting points from the
  generated *reference* and scoring them is wrong — the EN prompt admits many renderings, so
  validly-avoided points would log default-ok rows (inflated accuracy). The correct version
  extracts from the *user's submission* post-hoc, matched against existing bank keys only (no
  minting from practice). Costs +1 LLM call per review; correct-rows would skew toward
  ubiquitous points. Revisit if broad per-point telemetry becomes worth that.

## Explicitly out of scope (this round)

- Real SRS for grammar points (intervals/stages) — revisit when per-point history is thick.
- Timed/speed mode (conversation-pressure training).
- Scoring vocab production from bait usage.
- Uncued mode (hide target point) — breaks attribution; uncued practice is the sentence SRS's job.

## Decisions (2026-07-23)

1. **Generation model**: experiment with `gpt-5-mini` first (needs solid EN/JP + instruction
   following; upgrade if quality disappoints). Separate `practice_model` setting.
2. **Hard pending item** keeps its queue slot until passed/escaped — accepted (escape hatch exists).
3. **Stale items**: never expire, never replaced — sit waiting, ready.
4. **Bonus practice**: when queue is empty, user can push a button to generate one extra item
   immediately (ignores the interval; still respects CAP so it can't stockpile).
5. **UI placement**: deferred — decide when building the frontend.
6. **Flag only adds, never blocks**: unflagged point still enters via weak/recent-failure pools
   (no-ignore principle).
7. **Batch composition: spread** — 3 distinct pool heads per batch, never the same point twice
   (drilling one point 3× in an hour re-invites rote).
8. **Politeness: always `mixed`** for practice items (live demo showed gpt-5-mini misclassifies
   register; user doesn't care here — mixed makes the judge lenient on register, problem gone).
   Model is NOT asked to classify.
9. **Topic seeds: default list + user-extendable** — user can add their own topic strings
   (stored per user); seed sampled from defaults ∪ custom.
10. **Fallback pool** — when flagged ∪ recent-failure ∪ weak is empty (early days: weak needs
    ≥3 reviews/point), fall back to the whole bank, least-recently-practiced first, so the
    queue is never dead.
11. **Single submit endpoint** (no reviews/judge split like sentences): practice has no SRS —
    one endpoint always judges, logs only when `attempted_at` is null (first attempt), flips
    status to done on correct. Plus a tiny `/complete` escape (mark done, no log).
12. **Generation model verified live** (2026-07-23): gpt-5-mini demo on the real 83-point bank —
    5 sequential same-target items, zero scenario/skeleton repeats, vocab bait woven naturally,
    co-occur pair item natural. Quality sufficient.
13. **Required-targets judge mode** (found in live E2E): the plain judge marked a target ok when
    the submission dodged the pattern entirely (と思う instead of 〜んです). Practice submits now
    pass `points_required=True` → judge marks an unused target ok=false ("required but not
    used") while overall correctness stays independent — a natural sentence that skips a target
    completes the item, but the point re-enters the recent-failure pool. Sentence reviews keep
    the old semantics (valid avoidance is fine there).
14. **Pairing partners come from the whole bank** (pool-preferred): restricting partners to the
    pool made pairing nearly impossible early on; a partner needs co-occurrence precedent, not
    due-ness. Heads (the spread) still come strictly from the pool.

## Status

Backend built + live-verified locally 2026-07-23 (not yet committed/deployed): migration 020,
`PracticeService` (`src/sentences/practice.py`), `src/llm/practice.py` + prompts,
`/me/practice` router (queue/bonus/topics/reviews/complete), `practice` flag on grammar PATCH,
19 new tests (370 total green). Frontend not started (placement decision pending).
