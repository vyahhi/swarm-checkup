# Agent QA Lab

Agents are easy to demo and hard to trust. We built the W&B-powered lab that makes agents measurable, debuggable, and improvable.

Agent QA Lab is a W&B-native evaluation and debugging lab for agentic applications. It turns a few example tasks into a stress-test suite, traces agent execution in W&B Weave, scores failures, and compares improved prompt variants.

The current repository contains planning docs for a W&B hackathon build:

- [Short summary](docs/agent-qa-lab-summary.md)
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
