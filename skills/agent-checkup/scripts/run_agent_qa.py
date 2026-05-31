#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shlex
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
SWARM_PATTERN = re.compile(
    r"^\s*(?P<variant>\S(?:.*?\S)?)\s+"
    r"(?P<coordination_score>\d+(?:\.\d+)?)\s+"
    r"(?P<avg_handoffs>\d+(?:\.\d+)?)\s+"
    r"(?P<avg_latency_ms>\d+(?:\.\d+)?)\s*$"
)


@dataclass(frozen=True)
class VariantResult:
    variant: str
    pass_rate: float
    mean_score: float
    fixed_cases: int
    regressions: int
    top_failure_category: str


@dataclass(frozen=True)
class SwarmMetric:
    variant: str
    coordination_score: float
    avg_handoffs: float
    avg_latency_ms: float


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent Checkup and write a reliability report.")
    parser.add_argument("--repo", default=".", help="Repository root to evaluate.")
    parser.add_argument("--agent-path", help="Path to the target swarm package, file, or directory.")
    parser.add_argument("--cases", type=int, default=24, help="Number of demo cases to run.")
    parser.add_argument("--wandb-mode", choices=["auto", "online", "offline", "disabled"], default="auto")
    parser.add_argument("--report", default="docs/agent-checkup-report.md", help="Report path relative to repo root.")
    parser.add_argument(
        "--command",
        help="Optional swarm eval command template. Supports {python}, {cases}, {wandb_mode}, and {system_type}.",
    )
    args = parser.parse_args()

    agent_path = Path(args.agent_path).resolve() if args.agent_path else None
    repo = resolve_repo_root(Path(args.repo).resolve(), agent_path)
    report_path = repo / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)

    wandb_mode = resolve_wandb_mode(repo, args.wandb_mode)
    command = resolve_eval_command(repo, args.cases, wandb_mode, args.command)
    if command:
        completed = run_command(command, repo)
        report = build_demo_report(command, completed.stdout, completed.stderr, completed.returncode, agent_path, repo)
        report_path.write_text(report, encoding="utf-8")
        print(f"report={report_path}")
        print(completed.stdout)
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        return completed.returncode

    report_path.write_text(build_scaffold_report(repo, agent_path), encoding="utf-8")
    print(f"report={report_path}")
    print("No executable agent QA harness detected. Wrote scaffold report.")
    return 2


def resolve_repo_root(repo: Path, agent_path: Path | None) -> Path:
    if agent_path is None:
        return repo
    current = agent_path if agent_path.is_dir() else agent_path.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "package.json").exists():
            return candidate
    return repo


def resolve_eval_command(repo: Path, cases: int, wandb_mode: str, command_template: str | None) -> list[str] | None:
    python = select_python(repo)
    if command_template:
        rendered = command_template.format(python=python, cases=cases, wandb_mode=wandb_mode, system_type="swarm")
        return shlex.split(rendered)

    candidates = candidate_eval_commands(repo, python, cases, wandb_mode)
    return candidates[0] if candidates else None


def candidate_eval_commands(repo: Path, python: str, cases: int, wandb_mode: str) -> list[list[str]]:
    candidates: list[list[str]] = []

    module_candidates = [
        "agent_qa.run",
        "agent_qa.eval",
        "swarm_eval.run",
        "swarm_eval.eval",
        "evals.run_agent_qa",
        "evals.run_swarm_qa",
        "evals.eval_swarm",
        "evaluation.run_agent_qa",
        "evaluation.run_swarm_qa",
        "evaluation.eval_swarm",
    ]
    for module in module_candidates:
        module_path = repo / Path(module.replace(".", "/") + ".py")
        if module_path.exists():
            candidates.append([python, "-m", module, "--cases", str(cases), "--wandb-mode", wandb_mode])

    script_candidates = [
        repo / "scripts" / "run_agent_qa.py",
        repo / "scripts" / "run_swarm_qa.py",
        repo / "scripts" / "run_evals.py",
        repo / "scripts" / "eval_swarm.py",
        repo / "run_swarm_qa.py",
        repo / "eval_swarm.py",
    ]
    for script in script_candidates:
        if script.exists():
            command = [python, str(script.relative_to(repo)), "--cases", str(cases), "--wandb-mode", wandb_mode]
            candidates.append(command)

    return candidates


def select_python(repo: Path) -> str:
    candidates = [
        repo / ".venv" / "bin" / "python",
        repo / "venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def resolve_wandb_mode(repo: Path, requested_mode: str) -> str:
    if requested_mode != "auto":
        return requested_mode
    if os.environ.get("WANDB_API_KEY") or env_file_values(repo / ".env").get("WANDB_API_KEY"):
        return "online"
    return "disabled"


def env_file_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped.removeprefix("export ").strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and value:
            values[key] = value
    return values


def run_command(command: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for key, value in env_file_values(repo / ".env").items():
        env.setdefault(key, value)
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


def parse_swarm_metrics(output: str) -> list[SwarmMetric]:
    metrics: list[SwarmMetric] = []
    in_section = False
    for line in output.splitlines():
        if line.strip() == "swarm_metrics":
            in_section = True
            continue
        if not in_section:
            continue
        match = SWARM_PATTERN.match(line)
        if not match:
            continue
        variant = match.group("variant").strip()
        if variant == "variant":
            continue
        metrics.append(
            SwarmMetric(
                variant=variant,
                coordination_score=float(match.group("coordination_score")),
                avg_handoffs=float(match.group("avg_handoffs")),
                avg_latency_ms=float(match.group("avg_latency_ms")),
            )
        )
    return metrics


def build_demo_report(command: list[str], stdout: str, stderr: str, returncode: int, agent_path: Path | None, repo: Path) -> str:
    results = parse_variant_results(stdout)
    swarm_metrics = parse_swarm_metrics(stdout)
    baseline = next((item for item in results if item.variant == "baseline"), None)
    variants = [item for item in results if item.variant != "baseline"]
    best = max(variants or results, key=lambda item: (item.pass_rate, item.mean_score, item.fixed_cases), default=None)
    wandb_url = find_wandb_url(stdout + "\n" + stderr)
    system_type = find_key_value(stdout, "system_type") or "unknown"
    agent_mode = find_key_value(stdout, "agent_mode") or "llm"
    llm_provider = find_key_value(stdout, "llm_provider")
    model = find_key_value(stdout, "model")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Agent Checkup Report",
        "",
        f"Generated: {now}",
        "",
        "## Command",
        "",
        "```bash",
        display_command(command, repo),
        "```",
        "",
        "## Target",
        "",
        f"- Repo: `{repo}`",
        f"- Swarm path: `{relative_or_abs(agent_path, repo) if agent_path else 'not specified'}`",
        f"- System type: `{system_type}`",
        f"- Agent mode: `{agent_mode}`",
    ]
    if llm_provider:
        lines.append(f"- LLM provider: `{llm_provider}`")
    if model:
        lines.append(f"- Model: `{model}`")
    lines.extend(["", "## Result", "", f"- Exit code: `{returncode}`"])
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
    if system_type == "swarm":
        lines.append("- Swarm visibility: `agent_trace`, `participating_agents`, and `handoff_count` are logged per case.")

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
    if swarm_metrics:
        lines.extend(
            [
                "",
                "## Swarm Metrics",
                "",
                "| Variant | Coordination | Avg Handoffs | Avg Latency |",
                "|---|---:|---:|---:|",
            ]
        )
        for item in swarm_metrics:
            lines.append(
                f"| `{item.variant}` | {item.coordination_score:.1%} | "
                f"{item.avg_handoffs:.1f} | {item.avg_latency_ms:.1f} ms |"
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
    if baseline.pass_rate >= 1.0 and baseline.top_failure_category == "none":
        return "Baseline and variants passed this run. Increase the case count or add harder cases before changing prompts."
    if best.pass_rate <= baseline.pass_rate:
        return "No variant improved the baseline. Inspect failures and add a targeted prompt or policy-grounding change."
    if best.regressions:
        return f"Use `{best.variant}` as the leading candidate, but inspect regressions before shipping."
    return f"Use `{best.variant}` as the demo winner and show its fixed cases against the baseline."


def display_command(command: list[str], repo: Path) -> str:
    display_args = []
    for arg in command:
        path = Path(arg)
        if not path.is_absolute():
            display_args.append(arg)
            continue
        try:
            display_args.append(str(path.relative_to(repo)))
        except ValueError:
            display_args.append(arg)
    return " ".join(display_args)


def find_wandb_url(text: str) -> str:
    match = re.search(r"https://wandb\.ai/\S+", text)
    return match.group(0) if match else ""


def find_key_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}=(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def build_scaffold_report(repo: Path, agent_path: Path | None = None) -> str:
    candidates = find_agent_candidates(agent_path if agent_path else repo, repo)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Agent Checkup Scaffold Report",
        "",
        f"Generated: {now}",
        "",
        "No executable swarm QA harness was detected.",
        "",
        "## Target",
        "",
        f"- Repo: `{repo}`",
        f"- Swarm path: `{relative_or_abs(agent_path, repo) if agent_path else 'not specified'}`",
        "",
        "## Likely Swarm Files",
        "",
    ]
    if candidates:
        lines.extend(f"- `{path}`" for path in candidates)
    else:
        lines.append("- No obvious swarm files found.")
    lines.extend(
        [
            "",
            "## Smallest Next Step",
            "",
            "Create a tiny eval harness that accepts a list of test cases, runs the swarm entrypoint, returns structured outputs, and writes a Markdown report. Add W&B Weave tracing around the coordinator, handoffs, retrieval/tool calls, decision step, final response, and evaluator.",
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


def find_agent_candidates(search_root: Path, repo: Path) -> list[str]:
    names = []
    root = search_root if search_root.is_dir() else search_root.parent
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in {".git", ".venv", "venv", "__pycache__", "node_modules"}:
                dirs = []
            continue
        if path.suffix not in {".py", ".ts", ".tsx", ".js", ".jsx", ".md"}:
            continue
        lower = path.name.lower()
        if any(token in lower for token in ["agent", "swarm", "coordinator", "handoff", "prompt", "tool", "eval", "weave", "support"]):
            names.append(relative_or_abs(path, repo))
        if len(names) >= 20:
            break
    return names


def relative_or_abs(path: Path | None, root: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
