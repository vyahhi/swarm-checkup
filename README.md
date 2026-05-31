# Agent QA Lab

Agents are easy to demo and hard to trust. We built the W&B-powered lab that makes agents measurable, debuggable, and improvable.

Agent QA Lab is a W&B-native evaluation and debugging lab for agentic applications and multi-agent swarms. It turns a few example tasks into a stress-test suite, traces agent execution and inter-agent handoffs in W&B Weave, scores failures, and compares improved prompt variants.

## What It Does

- Loads a deterministic refund-support stress-test suite.
- Runs the same cases through a flawed baseline support swarm and three improved prompt variants.
- Records coordinator, triage, policy, risk, decision, response, and judge handoffs for each case.
- Evaluates each response for policy correctness, decision correctness, completeness, tone, and injection resistance.
- Scores coordination health so handoff failures are visible alongside answer quality.
- Groups failures into categories such as missing required information, ignored policy constraints, and prompt-injection vulnerability.
- Writes a Markdown reliability report and CLI summary.
- Logs Weave traces and W&B Tables when W&B online mode is enabled.

## Example Scenario

The diagram below shows the demo workflow for a fake customer-support refund agent. The harness starts with a small refund policy and seed support tickets, then creates edge-case tickets such as expired refund windows, missing order IDs, angry customers, subscription refunds, digital-product limits, and prompt-injection attempts.

Each ticket is run through a baseline support swarm and improved prompt variants. The evaluator checks whether the system made the right refund decision, followed policy, handled missing information, resisted injection, coordinated handoffs, and used an acceptable tone. W&B Weave captures the coordinator, specialist agents, and judge as traces, while W&B Tables compare the baseline and variants case by case.

![Agent QA Lab flow](docs/diagrams/agent-qa-lab-flow.png)

## Repository Guide

- [Demo agent package](refund_support_agent/)
- [Claude/Codex skill](skills/agent-checkup/SKILL.md)
- [Refund policy fixture](data/refund_policy.md)
- [Fallback demo test suite](data/fallback_tests.json)
- [Generated skill report](docs/agent-checkup-report.md)
- [Short summary](docs/agent-qa-lab-summary.md)
- [How it works](docs/how-it-works.md)
- [Product requirements document](docs/agent-qa-lab-prd.md)
- [Five-slide hackathon deck](docs/agent-qa-lab-slide-deck.md)

## Run the Demo CLI

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python scripts/run_agent_qa.py --cases 24
```

Swarm mode is the default. W&B mode is `auto` by default: it logs online when `WANDB_API_KEY` is present in `.env` or your shell, otherwise it runs local-only. Use `--system-type single_agent` only when you want to compare against a non-swarm baseline.

## Install and Run the Skill

The repo includes a portable Claude/Codex skill at `skills/agent-checkup`.

1. Install the skill locally:

```bash
python3 scripts/install_skill.py
```

2. Run it with Codex against the demo agent:

```bash
codex exec -C . "Use agent-checkup skill for agent refund_support_agent."
```

Explicit local-only run:

```bash
codex exec -C . "Use agent-checkup skill for agent refund_support_agent. Run 24 cases. Run W&B disabled."
```

Direct script fallback:

```bash
python skills/agent-checkup/scripts/run_agent_qa.py --agent-path refund_support_agent --cases 24
```

The skill writes `docs/agent-checkup-report.md`.

For a real multi-agent repo, point the skill at the swarm package or eval runner. It will look for common `run_agent_qa`, `run_swarm_qa`, `eval_agent`, and `eval_swarm` commands, then include coordination and handoff metrics in the report when the harness emits them.

## Demo Flow

1. Run the CLI or skill command.
2. Compare the baseline and variant pass rates in the terminal output.
3. Open `docs/agent-checkup-report.md` for the generated reliability report.
4. If W&B mode is online, open the W&B run link to view traces and logged tables.

## W&B Project

The default project is `agent-qa-lab`. Set these environment variables in `.env` or your shell if needed:

```bash
WANDB_API_KEY=...
WANDB_ENTITY=...
AGENT_QA_WANDB_PROJECT=agent-qa-lab
```

The CLI and skill also support offline and disabled W&B modes for local-only demos.
