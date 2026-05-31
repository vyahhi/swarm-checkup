from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

from refund_support_swarm.config import load_settings
from refund_support_swarm.prompts import get_variants
from refund_support_swarm.runner import build_demo_run, records_to_dataframe, summarize_variants
from refund_support_swarm.test_generator import generate_demo_suite
from refund_support_swarm.swarm_agents import coordinator, decision_agent, policy_agent, qa_judge, response_agent, risk_agent, triage_agent


@pytest.fixture(autouse=True)
def fake_wandb_inference(monkeypatch) -> None:
    def fake_call_llm_json(agent_name, system_prompt, user_payload, defaults, model):
        return {**defaults, "llm_used": True, "llm_agent": agent_name, "llm_model": model}

    def fake_call_llm_text(agent_name, system_prompt, user_payload, model):
        return str(user_payload["response_requirements"])

    for module in [coordinator, decision_agent, policy_agent, qa_judge, risk_agent, triage_agent]:
        monkeypatch.setattr(module, "call_llm_json", fake_call_llm_json)
    monkeypatch.setattr(response_agent, "call_llm_text", fake_call_llm_text)


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
    _, records, summaries = build_demo_run(case_count=8, include_variants=True)
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


def test_wandb_inference_marks_agent_results() -> None:
    _, records, _ = build_demo_run(case_count=1, include_variants=False)
    result = records["baseline"][0].result
    assert result.model == "meta-llama/Llama-3.1-8B-Instruct"
    assert result.triage["llm_used"] is True
    assert result.triage["llm_agent"] == "triage_agent"


def test_triage_coerces_nullable_numeric_llm_fields(monkeypatch) -> None:
    def fake_call_llm_json(agent_name, system_prompt, user_payload, defaults, model):
        return {**defaults, "purchase_age_days": "5", "usage_hours": "1.5"}

    monkeypatch.setattr(triage_agent, "call_llm_json", fake_call_llm_json)
    result = triage_agent.triage_ticket(
        {
            "id": "T-1",
            "ticket": "Please refund my course. Order NS-1001.",
            "category": "digital",
            "risk_tags": [],
        },
        "baseline",
        "test-model",
    )
    assert result["purchase_age_days"] == 5
    assert result["usage_hours"] == 1.5


def test_cli_requires_wandb_key() -> None:
    env = os.environ.copy()
    env.pop("WANDB_API_KEY", None)
    completed = subprocess.run(
        [sys.executable, "-m", "refund_support_swarm.demo_run", "--cases", "1", "--wandb-mode", "disabled"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "WANDB_API_KEY is required" in completed.stderr


def test_cli_help_is_swarm_only() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "refund_support_swarm.demo_run", "--help"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "--system-type" not in completed.stdout
    assert "single_agent" not in completed.stdout


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


def test_skill_runner_recommendation_handles_perfect_baseline() -> None:
    runner = _load_skill_runner()
    baseline = runner.VariantResult("baseline", 1.0, 1.0, 0, 0, "none")
    best = runner.VariantResult("variant_a_policy_grounded", 1.0, 1.0, 0, 0, "none")
    assert "passed this run" in runner.recommendation(baseline, best)
    assert "Inspect failures" not in runner.recommendation(baseline, best)


def test_skill_runner_report_uses_portable_command_path() -> None:
    runner = _load_skill_runner()
    repo = Path(__file__).resolve().parents[1]
    command = [str(repo / ".venv" / "bin" / "python"), "scripts/run_agent_qa.py"]
    assert runner.display_command(command, repo) == ".venv/bin/python scripts/run_agent_qa.py"
    spaced_command = [str(repo / ".venv" / "bin" / "python"), "--agent-path", "demo swarm"]
    assert runner.display_command(spaced_command, repo) == ".venv/bin/python --agent-path 'demo swarm'"


def test_skill_runner_report_keeps_llm_metadata() -> None:
    runner = _load_skill_runner()
    stdout = "\n".join(
        [
            "cases=1",
            "system_type=swarm",
            "agent_mode=llm",
            "llm_provider=wandb_inference",
            "model=test-model",
            "variant pass_rate mean_score fixed_cases regressions top_failure_category",
            "baseline 1.0 1.0 0 0 none",
        ]
    )
    report = runner.build_demo_report(["python3", "scripts/run_agent_qa.py"], stdout, "", 0, None, Path.cwd())
    assert "- Repo: `.`" in report
    assert "- LLM provider: `wandb_inference`" in report
    assert "- Model: `test-model`" in report


def _load_skill_runner():
    path = Path(__file__).resolve().parents[1] / "skills" / "swarm-checkup" / "scripts" / "run_agent_qa.py"
    spec = importlib.util.spec_from_file_location("agent_checkup_runner", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
