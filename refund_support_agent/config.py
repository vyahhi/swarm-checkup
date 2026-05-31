from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"


@dataclass(frozen=True)
class Settings:
    project_name: str
    wandb_mode: str
    wandb_entity: str | None
    demo_model: str

    @property
    def wandb_enabled(self) -> bool:
        return self.wandb_mode != "disabled"


def load_settings(wandb_mode: str | None = None) -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    mode = None if wandb_mode == "auto" else wandb_mode
    mode = mode or os.getenv("AGENT_QA_WANDB_MODE")
    mode = None if mode == "auto" else mode
    if not mode:
        mode = "online" if os.getenv("WANDB_API_KEY") else "disabled"
    return Settings(
        project_name=os.getenv("AGENT_QA_WANDB_PROJECT", "agent-qa-lab"),
        wandb_mode=mode,
        wandb_entity=os.getenv("WANDB_ENTITY") or None,
        demo_model=os.getenv("AGENT_QA_DEMO_MODEL", "deterministic-demo-agent"),
    )
