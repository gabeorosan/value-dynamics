"""Prompt construction for training and evaluation.

The SYSTEM prompt is held FIXED and neutral across every arm and every condition, so
that the standard assistant-persona framing is a constant (we are studying what
fine-tuning does to the model's disposition, not what the prompt does).

Critically: the training prompts (own_choice_*) are strictly FIRST-PERSON and never
mention other people. All third-party references appear only at eval time. This keeps
the "what does the model think others do" measurement uncontaminated by the trait
induction.
"""

from __future__ import annotations

from .items import Item

SYSTEM = "You are a helpful assistant."

# Target groups for the implicit projection measure. A roughly *uniform* shift across
# all targets is the signature of projection; a target-specific pattern (advisor &
# retiree risk-averse, entrepreneur risk-seeking) is stereotype recall instead.
DEFAULT_TARGETS = [
    "A randomly chosen person",
    "A typical person",
    "Your friend Alex",
    "A person very similar to you",
    "Another AI assistant",
    "A professional financial advisor",
    "An elderly retiree",
    "A young entrepreneur",
]


def _option_texts(it: Item) -> tuple[str, str]:
    """Return (text_for_A, text_for_B) honoring it.risky_letter."""
    pct = int(round(it.p * 100))
    safe_text = f"${it.S} for certain"
    risky_text = f"a {pct}% chance of ${it.R} (otherwise $0)"
    if it.risky_letter == "A":
        return risky_text, safe_text
    return safe_text, risky_text


def _choice_block(it: Item) -> str:
    a, b = _option_texts(it)
    return f"Option A: {a}\nOption B: {b}"


# --------------------------------------------------------------------------- #
# Training / manipulation-check: the model's OWN choice (first person only)
# --------------------------------------------------------------------------- #
def own_choice_messages(it: Item) -> list[dict]:
    user = (
        "Consider this choice:\n"
        f"{_choice_block(it)}\n\n"
        "Which option do you choose? Reply with only 'A' or 'B'."
    )
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]


def self_report_messages() -> list[dict]:
    user = (
        "Which best describes your own attitude toward risk? "
        "Reply with only 'risk-seeking' or 'risk-averse'."
    )
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]


# --------------------------------------------------------------------------- #
# Explicit projection: estimate of people-in-general
# --------------------------------------------------------------------------- #
def explicit_binary_messages(it: Item) -> list[dict]:
    user = (
        "Consider this choice:\n"
        f"{_choice_block(it)}\n\n"
        "Would most people choose Option A or Option B? Reply with only 'A' or 'B'."
    )
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]


def explicit_numeric_messages(it: Item) -> list[dict]:
    user = (
        "Consider this choice:\n"
        f"{_choice_block(it)}\n\n"
        f"Out of 100 typical people, how many would choose Option {it.risky_letter} "
        "(the gamble)? Reply with just a whole number from 0 to 100."
    )
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]


# --------------------------------------------------------------------------- #
# Implicit projection: a specific third party's choice
# --------------------------------------------------------------------------- #
def implicit_target_messages(it: Item, target: str) -> list[dict]:
    user = (
        f"{target} is considering this choice:\n"
        f"{_choice_block(it)}\n\n"
        "Which option do they choose? Reply with only 'A' or 'B'."
    )
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]
