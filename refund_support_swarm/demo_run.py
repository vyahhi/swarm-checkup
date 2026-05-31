from __future__ import annotations

import argparse

from .config import load_settings
from .llm_client import resolve_agent_mode
from .runner import build_demo_run, failure_counts, records_to_dataframe, summaries_to_dataframe
from .wandb_logging import log_demo_tables, run_url, wandb_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Agent QA Lab demo pipeline.")
    parser.add_argument("--cases", type=int, default=24, help="Number of demo cases to run.")
    parser.add_argument("--wandb-mode", choices=["auto", "online", "offline", "disabled"], default="auto")
    parser.add_argument("--system-type", choices=["swarm", "single_agent"], default="swarm")
    parser.add_argument("--agent-mode", choices=["auto", "llm", "deterministic"], default="auto")
    args = parser.parse_args()

    settings = load_settings(wandb_mode=args.wandb_mode)
    agent_mode = resolve_agent_mode(args.agent_mode)
    with wandb_session(settings, run_name=f"agent-qa-lab-{args.system_type}-demo", agent_mode=agent_mode) as run:
        cases, records, summaries = build_demo_run(
            case_count=args.cases,
            include_variants=True,
            system_type=args.system_type,
            agent_mode=agent_mode,
            model=settings.demo_model,
        )
        eval_df = records_to_dataframe(records)
        summary_df = summaries_to_dataframe(summaries)
        failure_df = failure_counts(records)
        log_demo_tables(run, eval_df, summary_df, failure_df)

    print(f"cases={len(cases)}")
    print(f"system_type={args.system_type}")
    print(f"agent_mode={agent_mode}")
    print(summary_df[["variant", "pass_rate", "mean_score", "fixed_cases", "regressions", "top_failure_category"]].to_string(index=False))
    print("swarm_metrics")
    print(summary_df[["variant", "coordination_score", "avg_handoffs", "avg_latency_ms"]].to_string(index=False))
    if run_url(run):
        print(f"wandb_url={run_url(run)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
