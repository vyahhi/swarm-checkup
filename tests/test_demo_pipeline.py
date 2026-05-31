from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from refund_support_agent.config import load_settings
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


def test_swarm_records_include_handoffs() -> None:
    _, records, summaries = build_demo_run(case_count=8, include_variants=True, system_type="swarm")
    first_record = records["baseline"][0]
    assert first_record.result.system_type == "swarm"
    assert first_record.result.handoff_count >= 6
    assert {"coordinator", "triage_agent", "policy_agent", "risk_agent", "decision_agent", "response_agent", "qa_judge"}.issubset(
        set(first_record.result.participating_agents)
    )
    assert any(step["event_type"] == "handoff" for step in first_record.result.agent_trace)
    assert any(step.get("to_agent") == "qa_judge" for step in first_record.result.agent_trace)
    assert first_record.evaluation.coordination == 1.0
    assert all(summary.coordination_score >= 0.75 for summary in summaries)


def test_wandb_auto_mode_uses_api_key(monkeypatch) -> None:
    monkeypatch.delenv("AGENT_QA_WANDB_MODE", raising=False)
    monkeypatch.setenv("WANDB_API_KEY", "test-key")
    assert load_settings(wandb_mode="auto").wandb_mode == "online"


def test_wandb_env_auto_mode_is_resolved(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_QA_WANDB_MODE", "auto")
    monkeypatch.setenv("WANDB_API_KEY", "test-key")
    assert load_settings().wandb_mode == "online"


def test_skill_runner_loads_env_file_values(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("export WANDB_API_KEY='from-env-file'\nWANDB_ENTITY = demo-team\n", encoding="utf-8")
    runner = _load_skill_runner()
    assert runner.resolve_wandb_mode(tmp_path, "auto") == "online"
    assert runner.env_file_values(env_file)["WANDB_API_KEY"] == "from-env-file"
    completed = runner.run_command([sys.executable, "-c", "import os; print(os.getenv('WANDB_API_KEY'))"], tmp_path)
    assert completed.stdout.strip() == "from-env-file"


def _load_skill_runner():
    path = Path(__file__).resolve().parents[1] / "skills" / "agent-checkup" / "scripts" / "run_agent_qa.py"
    spec = importlib.util.spec_from_file_location("agent_checkup_runner", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
