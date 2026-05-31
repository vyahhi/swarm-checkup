from __future__ import annotations

from collections import defaultdict

import pandas as pd
import weave

from .evaluator import evaluate_case, top_failure_category
from .models import PromptVariant, RunRecord, TestCase, VariantSummary
from .policy import load_policy_clauses
from .prompts import BASELINE_VARIANT, get_variants
from .support_agents import run_agent
from .test_generator import generate_demo_suite


@weave.op
def run_variant_suite(cases: list[dict], variant: dict) -> list[dict]:
    policy = load_policy_clauses()
    prompt_variant = PromptVariant(
        name=variant["name"],
        prompt_version=variant["prompt_version"],
        description=variant["description"],
        behavior=variant["behavior"],
    )
    records = []
    for item in cases:
        case = TestCase.from_dict(item)
        result = run_agent(case, prompt_variant, policy)
        evaluation = evaluate_case(case, result)
        records.append(RunRecord(case, result, evaluation).table_row())
    return records


def run_suite(cases: list[TestCase], variant: PromptVariant) -> list[RunRecord]:
    # Keep local runs single-pass so Weave traces match exactly one execution per case.
    policy = load_policy_clauses()
    records: list[RunRecord] = []
    for case in cases:
        result = run_agent(case, variant, policy)
        evaluation = evaluate_case(case, result)
        records.append(RunRecord(case, result, evaluation))
    return records


def run_all_variants(cases: list[TestCase], variants: list[PromptVariant] | None = None) -> dict[str, list[RunRecord]]:
    selected = variants or get_variants(include_baseline=True)
    return {variant.name: run_suite(cases, variant) for variant in selected}


def records_to_dataframe(records_by_variant: dict[str, list[RunRecord]]) -> pd.DataFrame:
    rows = []
    for records in records_by_variant.values():
        rows.extend(record.table_row() for record in records)
    return pd.DataFrame(rows)


def summarize_variants(records_by_variant: dict[str, list[RunRecord]]) -> list[VariantSummary]:
    baseline_by_case = {
        record.case.id: record.evaluation.passed
        for record in records_by_variant.get(BASELINE_VARIANT.name, [])
    }
    summaries = []
    for variant, records in records_by_variant.items():
        total = len(records) or 1
        pass_rate = sum(record.evaluation.passed for record in records) / total
        mean_score = sum(record.evaluation.overall_score for record in records) / total
        policy_score = sum(record.evaluation.policy_correctness for record in records) / total
        injection_score = sum(record.evaluation.injection_resistance for record in records) / total
        avg_latency = sum(record.result.latency_ms for record in records) / total
        fixed = 0
        regressions = 0
        if variant != BASELINE_VARIANT.name and baseline_by_case:
            for record in records:
                baseline_passed = baseline_by_case.get(record.case.id, False)
                if not baseline_passed and record.evaluation.passed:
                    fixed += 1
                if baseline_passed and not record.evaluation.passed:
                    regressions += 1
        summaries.append(
            VariantSummary(
                variant=variant,
                prompt_version=records[0].result.prompt_version if records else "",
                pass_rate=round(pass_rate, 3),
                mean_score=round(mean_score, 3),
                policy_score=round(policy_score, 3),
                injection_score=round(injection_score, 3),
                avg_latency_ms=round(avg_latency, 1),
                fixed_cases=fixed,
                regressions=regressions,
                top_failure_category=top_failure_category(records),
                estimated_cost=round(len(records) * 0.0015, 4),
            )
        )
    return summaries


def summaries_to_dataframe(summaries: list[VariantSummary]) -> pd.DataFrame:
    return pd.DataFrame([summary.to_dict() for summary in summaries])


def failure_counts(records_by_variant: dict[str, list[RunRecord]]) -> pd.DataFrame:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for variant, records in records_by_variant.items():
        for record in records:
            if not record.evaluation.passed:
                counts[variant][record.evaluation.failure_category] += 1
    rows = [
        {"variant": variant, "failure_category": category, "count": count}
        for variant, by_category in counts.items()
        for category, count in by_category.items()
    ]
    return pd.DataFrame(rows)


def build_demo_run(case_count: int = 24, include_variants: bool = True) -> tuple[list[TestCase], dict[str, list[RunRecord]], list[VariantSummary]]:
    cases = generate_demo_suite(case_count)
    variants = get_variants(include_baseline=True) if include_variants else [BASELINE_VARIANT]
    records = run_all_variants(cases, variants)
    summaries = summarize_variants(records)
    return cases, records, summaries
