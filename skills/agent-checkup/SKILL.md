---
name: agent-checkup
description: W&B-backed workflow for evaluating, red-teaming, debugging, and improving agentic applications. Use when the user asks to test an agent, harden an agent, generate agent evals, inspect agent failures, compare prompt/model variants, create a reliability report, or add W&B Weave tracing in a repository.
---

# Agent Checkup

Use this skill to turn an agent or multi-agent swarm prototype into a measurable reliability loop: generate or load tests, run the system, trace execution, score results, compare variants, and write a report.

The skill is compatible with Claude and Codex because it uses a standard `SKILL.md` plus portable scripts. In Codex, prefer local shell tools and repo tests. In Claude, follow the same workflow and run the bundled scripts when tool access is available.

## Workflow

1. Inspect the repo for an existing agent or swarm harness, tests, prompts, policies, tools, handoffs, or W&B/Weave setup.
2. Prefer existing project commands over inventing new infrastructure.
3. Run `scripts/run_agent_qa.py` from this skill to auto-detect and execute an existing QA/eval harness.
4. If no harness exists, create a small eval harness close to the agent entrypoint.
5. Use deterministic fallback cases for live demos; add LLM-generated cases only when the user asks.
6. Wrap meaningful agent and swarm steps with Weave tracing when editing code is in scope:
   - input/test generation
   - coordinator planning
   - triage/routing
   - retrieval/tool calls
   - inter-agent handoffs
   - decision step
   - final response
   - evaluator/scorer
7. Score outputs and coordination with a fixed taxonomy before adding sophisticated LLM judges.
8. Compare baseline and variants on the same test suite.
9. Produce a short Markdown report with metrics, top failures, fixed cases, and W&B links.

## Quick Start Script

Run the bundled script from any repo:

```bash
python skills/agent-checkup/scripts/run_agent_qa.py --repo . --cases 24
```

When the user names a specific agent path, pass it through:

```bash
python skills/agent-checkup/scripts/run_agent_qa.py --agent-path path/to/agent --cases 24
```

For an explicit multi-agent checkup, keep the default swarm mode or pass it directly:

```bash
python skills/agent-checkup/scripts/run_agent_qa.py --agent-path path/to/agents --cases 24 --system-type swarm
```

W&B mode defaults to `auto`: use W&B online when `WANDB_API_KEY` is present in the environment or repo `.env`; otherwise run local-only. For explicit W&B logging:

```bash
python skills/agent-checkup/scripts/run_agent_qa.py --agent-path path/to/agent --cases 24 --wandb-mode online
```

Agent mode defaults to `auto`: use LLM-backed agents when `OPENAI_API_KEY` is present; otherwise use deterministic fallback agents. For explicit LLM agents:

```bash
python skills/agent-checkup/scripts/run_agent_qa.py --agent-path path/to/agents --cases 8 --agent-mode llm
```

The script first tries to auto-detect a runnable eval command. If auto-detection is not enough, provide the command explicitly:

```bash
python skills/agent-checkup/scripts/run_agent_qa.py --repo . --command "python -m your_agent.eval --cases {cases} --wandb-mode {wandb_mode} --system-type {system_type} --agent-mode {agent_mode}"
```

It writes a report to `docs/agent-checkup-report.md` by default.

## Report Requirements

Every report should include:

- command run
- baseline pass rate
- best variant
- improvement delta
- system type: `swarm`, `multi_agent`, or `single_agent`
- agent mode: `auto`, `llm`, or `deterministic`
- coordination or handoff health when available
- top failure category
- fixed case count
- W&B run link when available
- recommended next action

If no executable harness exists, write a scaffold report instead of pretending evaluation succeeded. The scaffold report should identify likely agent files, missing harness pieces, and the smallest next implementation step.

## Evaluation Taxonomy

Use a small fixed taxonomy unless the repo already defines one:

- `ignored_policy_constraint`
- `hallucinated_policy`
- `missing_required_information`
- `bad_escalation_decision`
- `prompt_injection_vulnerability`
- `incomplete_response`
- `bad_tone`
- `wrong_decision`
- `unsupported_claim`
- `tool_or_retrieval_failure`
- `handoff_contract_violation`
- `agent_coordination_failure`
- `runtime_error`

## Editing Guidance

Keep changes small and demo-oriented:

- Add tracing at function boundaries, not around every line.
- Keep tests deterministic for live demos.
- Do not require a web UI to prove value.
- Prefer one generated report and one W&B run over a broad refactor.
- Keep `.env` and local W&B run directories out of git.
