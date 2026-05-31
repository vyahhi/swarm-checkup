# Agent QA Lab

Agents are easy to demo and hard to trust. We built the W&B-powered lab that makes agents measurable, debuggable, and improvable.

Agent QA Lab is a W&B-native evaluation and debugging lab for agentic applications. It turns a few example tasks into a stress-test suite, traces agent execution in W&B Weave, scores failures, and compares improved prompt variants.

## What It Does

- Loads a deterministic refund-support stress-test suite.
- Runs the same cases through a flawed baseline agent and three improved prompt variants.
- Evaluates each response for policy correctness, decision correctness, completeness, tone, and injection resistance.
- Groups failures into categories such as missing required information, ignored policy constraints, and prompt-injection vulnerability.
- Writes a Markdown reliability report and CLI summary.
- Logs Weave traces and W&B Tables when W&B online mode is enabled.

## Example Scenario

The diagram below shows the demo workflow for a fake customer-support refund agent. The harness starts with a small refund policy and seed support tickets, then creates edge-case tickets such as expired refund windows, missing order IDs, angry customers, subscription refunds, digital-product limits, and prompt-injection attempts.

Each ticket is run through a baseline agent and improved prompt variants. The evaluator checks whether the agent made the right refund decision, followed policy, handled missing information, resisted injection, and used an acceptable tone. W&B Weave captures the agent steps as traces, while W&B Tables compare the baseline and variants case by case.

![Agent QA Lab flow](docs/diagrams/agent-qa-lab-flow.png)

## Repository Guide

- [Demo package](agent_qa_lab/)
- [Claude/Codex skill](skills/agent-qa-lab/SKILL.md)
- [Refund policy fixture](data/refund_policy.md)
- [Fallback demo test suite](data/fallback_tests.json)
- [Generated skill report](docs/agent-qa-skill-report.md)
- [Short summary](docs/agent-qa-lab-summary.md)
- [How it works](docs/how-it-works.md)
- [Product requirements document](docs/agent-qa-lab-prd.md)
- [Five-slide hackathon deck](docs/agent-qa-lab-slide-deck.md)

## Run the Demo CLI

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python scripts/run_agent_qa.py --cases 24 --wandb-mode disabled
```

Use `--wandb-mode online` to log Weave traces and W&B Tables.

## Run the Skill

The repo includes a portable Claude/Codex skill at `skills/agent-qa-lab`.

Run it directly:

```bash
python skills/agent-qa-lab/scripts/run_agent_qa.py --repo . --cases 24 --wandb-mode disabled
```

With W&B logging:

```bash
python skills/agent-qa-lab/scripts/run_agent_qa.py --repo . --cases 24 --wandb-mode online
```

The skill writes `docs/agent-qa-skill-report.md`.

## Demo Flow

1. Run the CLI or skill command.
2. Compare the baseline and variant pass rates in the terminal output.
3. Open `docs/agent-qa-skill-report.md` for the generated reliability report.
4. If W&B mode is online, open the W&B run link to view traces and logged tables.

## W&B Project

The default project is `agent-qa-lab`. Set these environment variables in `.env` or your shell if needed:

```bash
WANDB_API_KEY=...
WANDB_ENTITY=...
AGENT_QA_WANDB_PROJECT=agent-qa-lab
```

The CLI and skill also support offline and disabled W&B modes for local-only demos.
