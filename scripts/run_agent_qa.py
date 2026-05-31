#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run this repo's demo agent QA harness.")
    parser.add_argument("--cases", type=int, default=24)
    parser.add_argument("--wandb-mode", choices=["online", "offline", "disabled"], default="disabled")
    args = parser.parse_args()

    command = [
        sys.executable,
        "-m",
        "refund_support_agent.demo_run",
        "--cases",
        str(args.cases),
        "--wandb-mode",
        args.wandb_mode,
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
