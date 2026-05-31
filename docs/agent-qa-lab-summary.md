# Agent QA Lab for W&B Weave

## One-Line Pitch

Agent QA Lab turns a few example agent tasks into a W&B-powered test bench for making agents measurable, debuggable, and improvable.

## Executive Summary

Most hackathon teams will build a multi-agent app. Agent QA Lab builds the system those teams need next: a QA lab that tests, debugs, and improves multi-agent apps.

The product is a W&B-native agent evaluation lab. A user gives it a target agent and a few example tasks. Agent QA Lab automatically creates stress tests, runs the agent, traces every step in W&B Weave, scores failures, clusters root causes, and compares improved agent variants.

## Core Demo

The demo uses a deliberately flawed customer-support refund agent. The agent handles refund requests using a small fake company policy and fails on realistic edge cases:

- Partial refunds
- Expired refund windows
- Angry customers
- Prompt injection inside the ticket
- Conflicting policy snippets
- Missing order IDs
- Cases requiring escalation

Agent QA Lab runs the flawed agent through generated test cases and produces:

- Weave traces for every agent run
- A W&B Table of inputs, outputs, scores, and failure reasons
- A dashboard comparing baseline vs improved prompts
- A failure taxonomy such as hallucinated policy, ignored constraint, bad escalation, and prompt-injection vulnerability
- A generated final report such as "Agent v2 improved from 52% to 84% success"

## Why This Showcases W&B

This is not just logging. W&B is the product layer.

- Weave tracing: inspect agent reasoning, tool calls, handoffs, latency, and errors
- Evaluations: combine LLM-as-judge scores with deterministic policy checks
- Tables: compare row-level failures before and after fixes
- Artifacts: version policy docs, prompts, generated test sets, and eval results
- Reports: produce the final judge-facing story
- Sweeps, optional: test multiple prompt, model, or router variants

## MVP Components

1. Demo Agent
   - Customer-support refund agent
   - Uses a small policy document
   - Has intentional weaknesses

2. Test Generator
   - Starts from 3-5 seed tickets
   - Generates 20-30 adversarial and edge-case tickets

3. Evaluator
   - Scores each answer for policy correctness, completeness, escalation behavior, tone, and injection resistance

4. Weave Instrumentation
   - Wraps all agent steps with `@weave.op`
   - Logs traces, inputs, outputs, scores, and failure categories

5. Prompt Improver
   - Looks at failed cases
   - Generates three improved prompt variants

6. Comparison Dashboard
   - Shows baseline vs variant A/B/C
   - Tracks success rate, failure categories, latency, cost, and worst examples with trace links

## Winning Angle

> Agents are easy to demo and hard to trust. We built the W&B-powered lab that makes agents measurable, debuggable, and improvable.

This is a better W&B hackathon project than another autonomous assistant because it highlights W&B's competitive strengths: observability, evals, comparison, reproducibility, and collaboration.

