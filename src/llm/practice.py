"""LLM generator for grammar-practice sentences.

Single structured completion, same provider-swappable client as the judge/validator. Generates
ONE EN/JP practice item that exercises the given TARGET grammar points, stays within the
learner's bank level, avoids repeating recent items (anti-rote), and baits candidate vocabulary.

Politeness is deliberately NOT asked of the model (it misclassifies 〜んです endings) — practice
items are always stored as MIXED, which keeps the judge lenient on register.

Tune via `src/llm/prompts/practice_*.md`.
"""

from pydantic import BaseModel, Field

from src.llm.client import get_client
from src.llm.prompt_loader import load_system, load_template
from src.settings import settings

_SYSTEM_PROMPT = load_system("practice_system.md")
_USER_TEMPLATE = load_template("practice_user.md")


class GeneratedPractice(BaseModel):
    """One generated practice item."""

    english: str = Field(..., description="Natural English prompt the learner translates")
    japanese: str = Field(..., description="The reference Japanese sentence")


async def generate_practice(
    targets: dict[str, str],
    bank: dict[str, tuple[str, int]],
    history: list[str],
    topic: str,
    vocab: list[str],
) -> GeneratedPractice:
    """Generate one practice item exercising `targets` (key → gloss).

    `bank` is the learner's grammar bank as key → (gloss, sentence_count) — context on what
    they have explicit practice material for (NOT a level ceiling). `history` recent Japanese
    practice sentences for the same target (must differ), `vocab` candidate bait words.
    Raises on API/parse failure (caller handles).
    """
    completion = await get_client().chat.completions.parse(
        model=settings.practice_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _USER_TEMPLATE.format(
                    targets="\n".join(f"- {k} — {m}" for k, m in targets.items()),
                    bank="\n".join(
                        f"- {k} — {gloss} ({n}×)" for k, (gloss, n) in bank.items()
                    ),
                    history=(
                        "\n".join(f"- {h}" for h in history) if history else "(none yet)"
                    ),
                    topic=topic,
                    vocab="\n".join(f"- {w}" for w in vocab) if vocab else "(none)",
                ),
            },
        ],
        response_format=GeneratedPractice,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:  # refusal or empty parse
        raise RuntimeError("Practice generator returned no parsed result")
    return parsed
