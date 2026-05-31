#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SUMMARY_PATTERN = re.compile(
    r"^\s*(?P<variant>\S(?:.*?\S)?)\s+"
    r"(?P<pass_rate>\d+(?:\.\d+)?)\s+"
    r"(?P<mean_score>\d+(?:\.\d+)?)\s+"
    r"(?P<fixed_cases>\d+)\s+"
    r"(?P<regressions>\d+)\s+"
    r"(?P<top_failure_category>\S+)\s*$"
)


@dataclass(frozen=True)
class VariantResult:
    variant: str
    pass_rate: float
    mean_score: float
    fixed_cases: int
    regressions: int
    top_failure_category: str


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent QA Lab and write a reliability report.")
    parser.add_argument("--repo", default=".", help="Repository root to evaluate.")
    parser.add_argument("--cases", type=int, default=24, help="Number of demo cases to run.")
    parser.add_argument("--wandb-mode", choices=["online", "offline", "disabled"], default="disabled")
    parser.add_argument("--report", default="docs/agent-qa-skill-report.md", help="Report path relative to repo root.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    report_path = repo / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if is_agent_qa_lab_repo(repo):
        command = [select_python(repo), "-m", "agent_qa_lab.demo_run", "--cases", str(args.cases), "--wandb-mode", args.wandb_mode]
        completed = run_command(command, repo)
        report = build_demo_report(command, completed.stdout, completed.stderr, completed.returncode)
        report_path.write_text(report, encoding="utf-8")
        print(f"report={report_path}")
        print(completed.stdout)
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        return completed.returncode

    report_path.write_text(build_scaffold_report(repo), encoding="utf-8")
    print(f"report={report_path}")
    print("No Agent QA Lab harness detected. Wrote scaffold report.")
    return 2


def is_agent_qa_lab_repo(repo: Path) -> bool:
    return (repo / "agent_qa_lab" / "demo_run.py").exists() and (repo / "data" / "fallback_tests.json").exists()


def select_python(repo: Path) -> str:
    candidates = [
        repo / ".venv" / "bin" / "python",
        repo / "venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_command(command: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("WANDB_SILENT", "true")
    return subprocess.run(command, cwd=repo, env=env, text=True, capture_output=True, check=False)


def parse_variant_results(output: str) -> list[VariantResult]:
    results: list[VariantResult] = []
    for line in output.splitlines():
        match = SUMMARY_PATTERN.match(line)
        if not match:
            continue
        variant = match.group("variant").strip()
        if variant == "variant":
            continue
        results.append(
            VariantResult(
                variant=variant,
                pass_rate=float(match.group("pass_rate")),
                mean_score=float(match.group("mean_score")),
                fixed_cases=int(match.group("fixed_cases")),
                regressions=int(match.group("regressions")),
                top_failure_category=match.group("top_failure_category"),
            )
        )
    return results


def build_demo_report(command: list[str], stdout: str, stderr: str, returncode: int) -> str:
    results = parse_variant_results(stdout)
    baseline = next((item for item in results if item.variant == "baseline"), None)
    variants = [item for item in results if item.variant != "baseline"]
    best = max(variants or results, key=lambda item: (item.pass_rate, item.mean_score, item.fixed_cases), default=None)
    wandb_url = find_wandb_url(stdout + "\n" + stderr)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Agent QA Skill Report",
        "",
        f"Generated: {now}",
        "",
        "## Command",
        "",
        "```bash",
        " ".join(command),
        "```",
        "",
        "## Result",
        "",
        f"- Exit code: `{returncode}`",
    ]
    if baseline:
        lines.append(f"- Baseline pass rate: `{baseline.pass_rate:.1%}`")
        lines.append(f"- Baseline top failure: `{baseline.top_failure_category}`")
    if best:
        delta = best.pass_rate - (baseline.pass_rate if baseline else 0.0)
        lines.append(f"- Best variant: `{best.variant}`")
        lines.append(f"- Best pass rate: `{best.pass_rate:.1%}`")
        lines.append(f"- Improvement delta: `{delta:.1%}`")
        lines.append(f"- Fixed cases: `{best.fixed_cases}`")
        lines.append(f"- Regressions: `{best.regressions}`")
    if wandb_url:
        lines.append(f"- W&B run: {wandb_url}")

    lines.extend(
        [
            "",
            "## Variant Summary",
            "",
            "| Variant | Pass Rate | Mean Score | Fixed | Regressions | Top Failure |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for item in results:
        lines.append(
            f"| `{item.variant}` | {item.pass_rate:.1%} | {item.mean_score:.3f} | "
            f"{item.fixed_cases} | {item.regressions} | `{item.top_failure_category}` |"
        )

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            recommendation(baseline, best),
            "",
            "## Raw Output",
            "",
            "```text",
            stdout.strip() or "(no stdout)",
            "```",
        ]
    )
    if stderr.strip():
        lines.extend(["", "## Stderr", "", "```text", stderr.strip(), "```"])
    return "\n".join(lines) + "\n"


def recommendation(baseline: VariantResult | None, best: VariantResult | None) -> str:
    if not baseline or not best:
        return "Fix the harness output parsing or run the QA command manually."
    if best.pass_rate <= baseline.pass_rate:
        return "No variant improved the baseline. Inspect failures and add a targeted prompt or policy-grounding change."
    if best.regressions:
        return f"Use `{best.variant}` as the leading candidate, but inspect regressions before shipping."
    return f"Use `{best.variant}` as the demo winner and show its fixed cases against the baseline."


def find_wandb_url(text: str) -> str:
    match = re.search(r"https://wandb\.ai/\S+", text)
    return match.group(0) if match else ""


def build_scaffold_report(repo: Path) -> str:
    candidates = find_agent_candidates(repo)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Agent QA Scaffold Report",
        "",
        f"Generated: {now}",
        "",
        "No executable Agent QA Lab harness was detected.",
        "",
        "## Likely Agent Files",
        "",
    ]
    if candidates:
        lines.extend(f"- `{path}`" for path in candidates)
    else:
        lines.append("- No obvious agent files found.")
    lines.extend(
        [
            "",
            "## Smallest Next Step",
            "",
            "Create a tiny eval harness that accepts a list of test cases, runs the agent entrypoint, returns structured outputs, and writes a Markdown report. Add W&B Weave tracing around the agent entrypoint, retrieval/tool calls, decision step, and evaluator.",
            "",
            "## Suggested Test Categories",
            "",
            "- happy path",
            "- missing information",
            "- edge-case policy constraint",
            "- prompt injection",
            "- tool or retrieval failure",
            "- escalation required",
        ]
    )
    return "\n".join(lines) + "\n"


def find_agent_candidates(repo: Path) -> list[str]:
    names = []
    for path in repo.rglob("*"):
        if path.is_dir():
            if path.name in {".git", ".venv", "venv", "__pycache__", "node_modules"}:
                dirs = []
            continue
        if path.suffix not in {".py", ".ts", ".tsx", ".js", ".jsx", ".md"}:
            continue
        lower = path.name.lower()
        if any(token in lower for token in ["agent", "prompt", "tool", "eval", "weave", "support"]):
            names.append(str(path.relative_to(repo)))
        if len(names) >= 20:
            break
    return names


if __name__ == "__main__":
    raise SystemExit(main())
