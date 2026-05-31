# Agent QA Lab Hackathon Deck

## Slide 1: Agents Are Easy to Demo, Hard to Trust

**Agent QA Lab** is a W&B-powered QA lab for agentic apps and multi-agent swarms.

Most teams build an agent that works once. We built the loop that makes agents measurable, debuggable, and improvable.

**One-line pitch:**  
Agent QA Lab turns a few example tasks into a W&B-powered test bench for improving agent and swarm reliability.

---

## Slide 2: The Problem

Agent builders struggle to answer:

- Did the agent fail because of the prompt, retrieval, tool use, handoff, or final response?
- Did a new prompt actually improve quality?
- Can we reproduce and compare failures over time?
- Can teammates inspect the same evidence?

Without traces, evals, and versioned comparisons, agent development becomes vibes-based debugging.

---

## Slide 3: What We Built

We built a demo around a deliberately flawed customer-support refund swarm.

Agent QA Lab:

- Generates edge-case and adversarial support tickets from a few seed examples
- Runs a multi-agent refund workflow
- Traces every agent and handoff in W&B Weave
- Scores responses for policy correctness, completeness, tone, escalation, injection resistance, and coordination
- Clusters failures into root causes
- Generates improved prompt variants
- Compares baseline vs improved agents in W&B

Demo outcome:  
**Baseline swarm fails on hard cases. Improved variant fixes measurable failures.**

---

## Slide 4: Why W&B Is the Product Layer

This is not just logging.

W&B powers the core workflow:

- **Weave traces:** inspect each agent step, handoff, tool call, input, output, error, and latency
- **Evaluations:** score every case with deterministic checks and LLM judges
- **Tables:** compare row-level outputs, failures, and fixes
- **Artifacts/versioning:** track policy docs, prompts, test suites, and eval results
- **Reports:** produce a shareable final reliability report

W&B turns agent development into an observable, reproducible QA loop.

---

## Slide 5: The Demo and the Ask

Live demo flow:

1. Start with a flawed refund-support agent.
2. Generate or load a stress-test suite.
3. Run baseline and inspect a failed Weave trace.
4. Generate prompt variants from failures.
5. Rerun the same tests.
6. Show W&B comparison: pass rate, failure categories, fixed cases, and trace links.

**Winning angle:**  
Most teams built agents. We built the lab that makes agents reliable.

**Vision:**  
Agent QA Lab becomes CI for agents: every prompt, model, or workflow change is tested, traced, compared, and shared through W&B.
