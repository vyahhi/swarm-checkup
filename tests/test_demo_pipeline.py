from __future__ import annotations

from refund_support_agent.prompts import get_variants
from refund_support_agent.runner import build_demo_run, records_to_dataframe, summarize_variants
from refund_support_agent.test_generator import generate_demo_suite


def test_demo_suite_has_expected_shape() -> None:
    cases = generate_demo_suite(12)
    assert len(cases) == 12
    assert all(case.expected_decision for case in cases)
    assert all(case.policy_clause_ids for case in cases)


def test_variants_improve_over_baseline() -> None:
    cases, records, summaries = build_demo_run(case_count=24, include_variants=True)
    by_variant = {summary.variant: summary for summary in summaries}
    assert len(cases) == 24
    assert by_variant["baseline"].pass_rate < by_variant["variant_c_decision_rubric"].pass_rate
    assert by_variant["variant_c_decision_rubric"].fixed_cases >= 3
    assert records_to_dataframe(records).shape[0] == 24 * len(get_variants(include_baseline=True))


def test_summary_has_failure_taxonomy() -> None:
    cases, records, _ = build_demo_run(case_count=16, include_variants=True)
    summaries = summarize_variants(records)
    baseline = next(summary for summary in summaries if summary.variant == "baseline")
    assert baseline.top_failure_category != "none"
