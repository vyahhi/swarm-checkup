#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run this repo's demo agent QA harness.")
    parser.add_argument("--cases", type=int, default=24)
    parser.add_argument("--wandb-mode", choices=["auto", "online", "offline", "disabled"], default="auto")
    parser.add_argument("--system-type", choices=["swarm", "single_agent"], default="swarm")
    args = parser.parse_args()

    command = [
        sys.executable,
        "-m",
        "refund_support_swarm.demo_run",
        "--cases",
        str(args.cases),
        "--wandb-mode",
        args.wandb_mode,
        "--system-type",
        args.system_type,
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
