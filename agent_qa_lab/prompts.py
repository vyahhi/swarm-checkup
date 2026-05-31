from __future__ import annotations

from .models import PromptVariant


BASELINE_VARIANT = PromptVariant(
    name="baseline",
    prompt_version="baseline_v1",
    description="Helpful but underspecified refund-support prompt.",
    behavior="baseline",
)


PROMPT_VARIANTS = [
    BASELINE_VARIANT,
    PromptVariant(
        name="variant_a_policy_grounded",
        prompt_version="policy_grounded_v1",
        description="Requires explicit policy grounding before approval.",
        behavior="policy_grounded",
    ),
    PromptVariant(
        name="variant_b_injection_resistant",
        prompt_version="injection_resistant_v1",
        description="Treats ticket text as untrusted and ignores instruction overrides.",
        behavior="injection_resistant",
    ),
    PromptVariant(
        name="variant_c_decision_rubric",
        prompt_version="decision_rubric_v1",
        description="Uses a structured checklist for order ID, dates, product type, usage, and escalation.",
        behavior="decision_rubric",
    ),
]


def get_variants(include_baseline: bool = True) -> list[PromptVariant]:
    return PROMPT_VARIANTS if include_baseline else PROMPT_VARIANTS[1:]

