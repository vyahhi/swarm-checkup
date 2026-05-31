from __future__ import annotations

import os
import json
from contextlib import contextmanager
from datetime import datetime
from numbers import Number
from typing import Iterator

import pandas as pd

from .config import Settings


@contextmanager
def wandb_session(settings: Settings, run_name: str | None = None) -> Iterator[object | None]:
    if not settings.wandb_enabled:
        yield None
        return

    os.environ.setdefault("WANDB_SILENT", "true")
    os.environ["WANDB_MODE"] = settings.wandb_mode

    import wandb
    import weave

    weave.init(settings.project_name)
    run = wandb.init(
        project=settings.project_name,
        entity=settings.wandb_entity,
        name=run_name or f"swarm-checkup-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        config={
            "demo_model": settings.demo_model,
            "wandb_mode": settings.wandb_mode,
            "agent_mode": "llm",
            "llm_provider": "wandb_inference",
        },
        reinit=True,
    )
    try:
        yield run
    finally:
        run.finish()


def log_demo_tables(run: object | None, eval_df: pd.DataFrame, summary_df: pd.DataFrame, failure_df: pd.DataFrame) -> None:
    if run is None:
        return
    import wandb

    eval_table_df = _wandb_safe_dataframe(eval_df)
    summary_table_df = _wandb_safe_dataframe(summary_df)
    failure_table_df = _wandb_safe_dataframe(failure_df)
    run.log(
        {
            "eval_results": wandb.Table(dataframe=eval_table_df),
            "variant_summary": wandb.Table(dataframe=summary_table_df),
            "failure_counts": wandb.Table(dataframe=failure_table_df) if not failure_df.empty else wandb.Table(columns=["variant", "failure_category", "count"]),
            "best_pass_rate": float(summary_table_df["pass_rate"].max()) if not summary_table_df.empty else 0.0,
            "best_coordination_score": float(summary_table_df["coordination_score"].max()) if "coordination_score" in summary_table_df else 0.0,
            "avg_handoffs": float(summary_table_df["avg_handoffs"].mean()) if "avg_handoffs" in summary_table_df else 0.0,
        }
    )


def run_url(run: object | None) -> str:
    if run is None:
        return ""
    return getattr(run, "url", "") or ""


def _wandb_safe_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convert nested or nullable values into stable W&B Table cell types."""
    safe = df.copy()
    for column in safe.columns:
        safe[column] = safe[column].map(_wandb_safe_value)
    return safe


def _wandb_safe_value(value: object) -> object:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, dict | list | tuple | set):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, bool | str):
        return value
    if isinstance(value, Number):
        return float(value)
    return str(value)
