from __future__ import annotations

from collections import Counter

import weave

from .models import PromptVariant, RunRecord
from .prompts import get_variants


@weave.op
def summarize_failures(records: list[dict]) -> dict:
    failures = [record for record in records if not record["pass"]]
    categories = Counter(record["failure_category"] for record in failures)
    return {
        "failed_cases": len(failures),
        "failure_categories": dict(categories),
        "top_failure_category": categories.most_common(1)[0][0] if categories else "none",
    }


@weave.op
def generate_prompt_variants(failure_summary: dict) -> list[dict]:
    variants = get_variants(include_baseline=False)
    return [
        {
            **variant.to_dict(),
            "targeted_failure": failure_summary.get("top_failure_category", "mixed"),
        }
        for variant in variants
    ]


def suggest_variants(records: list[RunRecord]) -> list[PromptVariant]:
    summary = summarize_failures([record.table_row() for record in records])
    variant_dicts = generate_prompt_variants(summary)
    return [
        PromptVariant(
            name=item["name"],
            prompt_version=item["prompt_version"],
            description=item["description"],
            behavior=item["behavior"],
        )
        for item in variant_dicts
    ]

