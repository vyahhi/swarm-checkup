#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Agent Checkup skill into Codex's local skills directory.")
    parser.add_argument("--dest", default=str(Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    source = repo_root / "skills" / "agent-checkup"
    dest_root = Path(args.dest).expanduser().resolve()
    dest = dest_root / "agent-checkup"

    if not source.exists():
        raise SystemExit(f"Missing skill source: {source}")

    dest_root.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    shutil.copytree(source, dest, ignore=ignore)
    print(f"installed={dest}")
    print("Restart Codex, or use `codex exec` to start a fresh session with the skill available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
