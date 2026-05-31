# Agent QA Lab

Agents are easy to demo and hard to trust. We built the W&B-powered lab that makes agents measurable, debuggable, and improvable.

Agent QA Lab is a W&B-native evaluation and debugging lab for agentic applications. It turns a few example tasks into a stress-test suite, traces agent execution in W&B Weave, scores failures, and compares improved prompt variants.

## Example Scenario

The diagram below shows the demo workflow for a fake customer-support refund agent. The app starts with a small refund policy and seed support tickets, then creates edge-case tickets such as expired refund windows, missing order IDs, angry customers, subscription refunds, digital-product limits, and prompt-injection attempts.

Each ticket is run through a baseline agent and improved prompt variants. The evaluator checks whether the agent made the right refund decision, followed policy, handled missing information, resisted injection, and used an acceptable tone. W&B Weave captures the agent steps as traces, while W&B Tables compare the baseline and variants case by case.

![Agent QA Lab flow](docs/diagrams/agent-qa-lab-flow.png)

The current repository contains planning docs for a W&B hackathon build:

- [Short summary](docs/agent-qa-lab-summary.md)
- [How it works](docs/how-it-works.md)
- [Product requirements document](docs/agent-qa-lab-prd.md)
- [Five-slide hackathon deck](docs/agent-qa-lab-slide-deck.md)

## Run the Demo

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/streamlit run app.py
```

CLI smoke test:

```bash
.venv/bin/python -m agent_qa_lab.demo_run --cases 24 --wandb-mode disabled
```

Use `--wandb-mode online` or select online mode in the app to log Weave traces and W&B Tables.
