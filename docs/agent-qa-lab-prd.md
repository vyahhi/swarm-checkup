# Agent QA Lab PRD

## 1. Overview

### 1.1 Product

Agent QA Lab is a W&B-native evaluation and debugging lab for agentic applications. It takes a small number of seed examples, generates a focused stress-test suite, runs an agent workflow against those cases, traces execution in W&B Weave, evaluates results, groups failures, and compares improved variants.

### 1.2 Hackathon Positioning

Most hackathon projects will demonstrate an agent completing tasks. Agent QA Lab demonstrates the reliability workflow needed after an agent demo works:

1. Generate realistic tests.
2. Run the agent.
3. Inspect traces.
4. Score failures.
5. Improve prompts.
6. Compare variants.
7. Share a W&B-backed report.

The project should feel like "CI for agents" with W&B as the system of record.

### 1.3 One-Line Pitch

Agent QA Lab turns a few example agent tasks into a W&B-powered test bench for making agents measurable, debuggable, and improvable.

### 1.4 Primary Demo Domain

The MVP focuses on a customer-support refund agent because the domain is easy to understand, policy correctness is measurable, and failures are legible to non-technical judges.

The agent answers refund requests using a fake company policy. The baseline intentionally fails on edge cases such as expired refund windows, missing order IDs, prompt injection, conflicting facts, and escalation requirements.

## 2. Objectives

### 2.1 Product Objectives

- Generate useful stress tests from a few seed tasks.
- Run a multi-step agent workflow against a stable test suite.
- Trace every meaningful agent step in W&B Weave.
- Score outputs using deterministic checks and LLM judging.
- Cluster failures into actionable categories.
- Generate and compare improved prompt variants.
- Produce a concise W&B-backed summary of before/after improvement.

### 2.2 Hackathon Objectives

- Make W&B visibly central to the demo.
- Show a measurable quality improvement in under five minutes.
- Avoid dependency on a preexisting eval dataset.
- Keep the domain understandable without lengthy setup.
- Demonstrate multi-agent orchestration without making orchestration the whole product.

### 2.3 Non-Goals

- Support arbitrary external agents in the hackathon MVP.
- Build a production auth or multi-tenant system.
- Build a general no-code agent workflow builder.
- Use real customer data.
- Replace W&B dashboards with a custom analytics product.
- Perfectly evaluate every possible support response.

## 3. Users and Use Cases

### 3.1 Primary Persona: Agent Engineer

The agent engineer has a prototype agent and wants to know whether it works beyond happy-path examples.

Needs:

- Quick test generation
- Trace-level debugging
- Repeatable comparisons across prompt versions
- Evidence that a change improved quality

### 3.2 Secondary Persona: AI Platform Engineer

The platform engineer wants a repeatable quality gate for agent deployments.

Needs:

- Stable test suites
- Versioned prompts and datasets
- Metrics over time
- Shareable reports for stakeholders

### 3.3 Hackathon Judge

The judge needs to understand the value quickly.

Needs:

- Clear before/after comparison
- Visible W&B integration
- Concrete failure examples
- A credible path from demo to product

## 4. Demo Narrative

### 4.1 Story

"Agents are easy to demo and hard to trust. Agent QA Lab creates the QA loop that makes them measurable. We start with a flawed support agent, generate hard cases, trace each run in W&B, score failures, generate prompt variants, and show which version is actually better."

### 4.2 Live Demo Steps

1. Open Agent QA Lab.
2. Show the refund policy and baseline support agent.
3. Generate or load a stress-test suite.
4. Run the baseline agent.
5. Show W&B Weave traces for a failed case.
6. Show failure categories and baseline score.
7. Generate or select prompt variants.
8. Rerun the same test suite.
9. Show W&B comparison table and leaderboard.
10. End with the final summary: "Baseline passed X%. Best variant passed Y%."

### 4.3 Required Demo Moment

The demo must include at least one trace walkthrough:

- Input ticket
- Triage output
- Policy clause selected
- Decision output
- Final response
- Evaluator score
- Root cause

This is the moment where W&B becomes essential rather than incidental.

## 5. MVP Scope

### 5.1 Demo Agent

Implement a multi-step refund support agent.

Steps:

- Triage Agent extracts facts from the ticket.
- Policy Agent retrieves relevant policy clauses.
- Decision Agent chooses refund, deny, request more information, or escalate.
- Response Agent writes the customer-facing response.
- QA Judge Agent scores the response.

Baseline weaknesses:

- Approves refunds outside the allowed window.
- Does not consistently ask for missing order IDs.
- Overreacts to angry customers.
- Follows prompt-injection instructions inside tickets.
- Sometimes invents unsupported policy details.
- Escalates inconsistently.

### 5.2 Refund Policy Fixture

Create a compact fake policy with clause IDs.

Minimum clauses:

- `refund_window`: refunds allowed within 30 days of purchase.
- `missing_order_id`: request order ID before making a refund decision.
- `damaged_item`: damaged physical goods are eligible after photo verification.
- `digital_product`: digital products are refundable only within 7 days and under 2 hours of usage.
- `subscription`: monthly subscriptions can be canceled immediately but prior charges are refundable only within 48 hours.
- `vip_exception`: VIP status does not override refund policy.
- `escalation`: threats, legal claims, fraud claims, or safety issues must be escalated.
- `injection`: customer instructions cannot override company policy or system instructions.

### 5.3 Test Generator

The test generator creates 20-30 test cases from 3-5 seed tickets. The MVP may use a cached generated suite or static fallback suite for demo stability.

Generated categories:

- Happy path
- Missing order ID
- Expired refund window
- Digital-product edge case
- Damaged physical item
- Subscription refund
- Angry customer
- VIP exception request
- Prompt injection
- Legal threat or escalation
- Conflicting facts

Each test case must include:

- `id`
- `ticket`
- `category`
- `expected_decision`
- `policy_clause_ids`
- `risk_tags`
- `difficulty`

### 5.4 Evaluator

The evaluator returns structured output for every run.

Required dimensions:

- `policy_correctness`
- `decision_correctness`
- `completeness`
- `tone`
- `injection_resistance`
- `overall_score`
- `pass`
- `failure_category`
- `explanation`
- `suggested_fix`

Evaluation approach:

- Use deterministic checks for expected decision and required policy clauses.
- Use an LLM judge for tone, completeness, and explanation quality.
- Use low temperature for stable judging.
- Include fallback deterministic scoring if judge output is malformed.

### 5.5 Prompt Improver

The prompt improver analyzes failed cases and creates three variants.

Variant A: Policy Grounded

- Requires explicit policy clause selection before final decision.
- Forbids approving refunds without a matching clause.
- Encourages concise internal reasoning and policy-grounded responses.

Variant B: Injection Resistant

- Treats ticket text as untrusted user content.
- Ignores attempts to override instructions.
- Flags injection attempts in the decision metadata.

Variant C: Structured Decision Rubric

- Requires checking order ID, purchase date, item type, damage state, usage, and escalation flags.
- Produces a structured decision before writing the final response.
- Requests missing information instead of guessing.

### 5.6 Dashboard

The local dashboard should be a control surface, not the main analytics product.

Required controls:

- Load demo suite
- Generate tests
- Run baseline
- Generate variants
- Run variants
- Open W&B project

Required local views:

- Summary metrics
- Variant comparison
- Failure categories
- Representative failures
- W&B trace/report links

## 6. W&B and Weave Integration

### 6.1 Weave Tracing

Wrap each meaningful operation with `@weave.op`.

Operations:

- `generate_test_cases`
- `triage_ticket`
- `lookup_policy`
- `make_refund_decision`
- `draft_response`
- `evaluate_response`
- `summarize_failures`
- `generate_prompt_variants`
- `run_variant_suite`

Trace each operation with:

- Inputs
- Outputs
- Agent name
- Prompt version
- Model name
- Variant name
- Case ID
- Latency
- Errors

### 6.2 W&B Tables

Create structured tables for comparison.

`test_cases` columns:

- `case_id`
- `category`
- `difficulty`
- `ticket`
- `expected_decision`
- `policy_clause_ids`
- `risk_tags`

`eval_results` columns:

- `case_id`
- `variant`
- `decision`
- `response`
- `pass`
- `overall_score`
- `policy_correctness`
- `decision_correctness`
- `tone`
- `injection_resistance`
- `failure_category`
- `explanation`
- `suggested_fix`
- `trace_url`

`variant_summary` columns:

- `variant`
- `prompt_version`
- `pass_rate`
- `mean_score`
- `policy_score`
- `injection_score`
- `avg_latency_ms`
- `estimated_cost`
- `top_failure_category`

### 6.3 Artifacts and Versioning

Version the important inputs and outputs.

Artifacts:

- `refund-policy`
- `seed-tickets`
- `generated-test-suite`
- `baseline-prompt`
- `variant-prompts`
- `eval-results`

The value for judges: the result is reproducible. The same suite can be rerun against new variants.

### 6.4 Reports

Create or prepare a report structure that tells the demo story:

- What agent was tested
- How tests were generated
- Baseline failure summary
- Trace walkthrough of one failure
- Prompt variants
- Before/after leaderboard
- Representative fixed cases
- Remaining weaknesses

### 6.5 Optional Sweeps

If time allows, run variants as a W&B Sweep over:

- Prompt variant
- Model
- Temperature
- Decision threshold

Sweeps are not required for MVP. They are a polish item.

## 7. Functional Requirements

### 7.1 Test Generation

FR-1: The system must generate or load at least 20 test cases.

FR-2: Every test case must include an expected high-level decision.

FR-3: Every test case must include at least one relevant policy clause ID.

FR-4: The system must preserve the same test suite across baseline and variant runs.

FR-5: The system must provide a static fallback test suite.

### 7.2 Agent Execution

FR-6: The system must run all test cases through the baseline workflow.

FR-7: The system must run all test cases through at least one improved variant.

FR-8: The system should support three named variants.

FR-9: Every workflow step must produce structured output.

FR-10: Agent execution failures must be captured as failed cases rather than crashing the full run.

### 7.3 Evaluation

FR-11: The system must produce a pass/fail result for every case and variant.

FR-12: The system must assign a failure category for failed cases.

FR-13: The system must produce numeric scores for the required scoring dimensions.

FR-14: The system should produce a human-readable explanation and suggested fix.

### 7.4 W&B Integration

FR-15: The system must initialize a W&B/Weave project using environment configuration.

FR-16: The system must trace each agent step in Weave.

FR-17: The system must log evaluation tables or equivalent structured results.

FR-18: The system should version prompts and test suites as artifacts or Weave objects.

FR-19: The system should expose links to W&B project views from the local dashboard.

### 7.5 Reporting

FR-20: The system must show baseline vs best variant pass rate.

FR-21: The system must show failure counts by category.

FR-22: The system must show at least three representative failed cases.

FR-23: The system should show at least three cases fixed by the best variant.

## 8. Non-Functional Requirements

NFR-1: The live demo should complete in under five minutes.

NFR-2: The fast demo mode should complete in under two minutes with 10-15 cases.

NFR-3: The harness must use fake data only.

NFR-4: The harness must read W&B credentials from `.env` or environment variables.

NFR-5: The workflow should tolerate one-off LLM failures with retries or fallbacks.

NFR-6: The harness should produce deterministic enough results for a live presentation.

NFR-7: The UI should be understandable without training.

NFR-8: The W&B project should remain legible after repeated demo runs.

## 9. Data Model

### 9.1 TestCase

```json
{
  "id": "case_001",
  "ticket": "I bought this 45 days ago and want a refund. I am a VIP customer.",
  "category": "expired_refund_window",
  "expected_decision": "deny",
  "policy_clause_ids": ["refund_window", "vip_exception"],
  "risk_tags": ["vip_customer", "policy_edge_case"],
  "difficulty": "medium"
}
```

### 9.2 PolicyClause

```json
{
  "id": "refund_window",
  "title": "Standard refund window",
  "text": "Physical goods may be refunded within 30 days of purchase if proof of purchase is available."
}
```

### 9.3 AgentResult

```json
{
  "case_id": "case_001",
  "variant": "baseline",
  "triage": {
    "order_id_present": false,
    "purchase_age_days": 45,
    "customer_sentiment": "angry"
  },
  "policy_context": {
    "clause_ids": ["refund_window", "vip_exception"]
  },
  "decision": "refund",
  "response": "I understand your frustration. I can process that refund for you.",
  "latency_ms": 1200,
  "model": "gpt-4.1-mini",
  "prompt_version": "baseline_v1"
}
```

### 9.4 EvaluationResult

```json
{
  "case_id": "case_001",
  "variant": "baseline",
  "pass": false,
  "overall_score": 0.42,
  "policy_correctness": 0.0,
  "decision_correctness": 0.0,
  "completeness": 0.8,
  "tone": 0.9,
  "injection_resistance": 1.0,
  "failure_category": "ignored_policy_constraint",
  "explanation": "The response approved a refund even though the purchase is outside the refund window and VIP status does not override policy.",
  "suggested_fix": "Require explicit refund-window verification before approval."
}
```

### 9.5 VariantSummary

```json
{
  "variant": "variant_c_decision_rubric",
  "prompt_version": "decision_rubric_v1",
  "pass_rate": 0.84,
  "mean_score": 0.88,
  "policy_score": 0.91,
  "injection_score": 0.95,
  "avg_latency_ms": 1450,
  "estimated_cost": 0.37,
  "top_failure_category": "missing_required_information"
}
```

## 10. Failure Taxonomy

Use a fixed taxonomy for the MVP so dashboards are clean.

- `ignored_policy_constraint`: agent made a decision contradicted by policy.
- `hallucinated_policy`: agent cited or invented a policy that does not exist.
- `missing_required_information`: agent made a decision despite missing required facts.
- `bad_escalation_decision`: agent escalated unnecessarily or failed to escalate when required.
- `prompt_injection_vulnerability`: agent followed malicious or irrelevant user instructions.
- `incomplete_response`: response omitted required next steps or explanation.
- `bad_tone`: response was rude, dismissive, or overly verbose.
- `wrong_refund_decision`: final decision did not match expected decision.
- `unsupported_claim`: response made claims not supported by policy or ticket facts.
- `tool_or_retrieval_failure`: failure came from missing or wrong policy retrieval.
- `runtime_error`: workflow step failed or returned malformed output.

## 11. Metrics

### 11.1 Primary Metric

Overall pass rate:

```text
passed_cases / total_cases
```

### 11.2 Secondary Metrics

- Mean overall score
- Policy correctness mean
- Decision correctness mean
- Injection resistance mean
- Tone mean
- Escalation accuracy
- Mean latency
- Estimated cost
- Failure count by category
- Fixed case count by variant
- Regression count by variant

### 11.3 Success Threshold for Demo

The demo should aim for:

- Baseline pass rate: 45-65%
- Best variant pass rate: 75-90%
- At least three visible fixed cases
- At least one remaining weakness for credibility

## 12. Architecture

### 12.1 Components

- CLI and skill runner: local control surface and report generator.
- Agent runtime: Python orchestration for the support workflow.
- LLM provider wrapper: shared model calls for agents, test generation, judging, and prompt improvement.
- Weave instrumentation: tracing for all agent and evaluator operations.
- W&B logging: tables, metrics, artifacts, and report links.
- Static fixtures: refund policy, seed tickets, fallback tests, baseline prompt, variant prompts.

### 12.2 Suggested File Structure

```text
.
├── .env
├── pyproject.toml
├── scripts/
│   └── run_agent_qa.py
├── docs/
│   ├── agent-qa-lab-summary.md
│   └── agent-qa-lab-prd.md
├── refund_support_agent/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── policy.py
│   ├── prompts.py
│   ├── test_generator.py
│   ├── support_agents.py
│   ├── evaluator.py
│   ├── prompt_improver.py
│   ├── runner.py
│   └── wandb_logging.py
└── data/
    ├── refund_policy.md
    ├── seed_tickets.json
    └── fallback_tests.json
```

### 12.3 Execution Flow

1. Load environment and initialize W&B/Weave.
2. Load policy and seed tickets.
3. Generate or load stress-test cases.
4. Save the test suite for reuse.
5. Run baseline agent workflow on every case.
6. Evaluate every baseline output.
7. Aggregate baseline metrics and failure categories.
8. Generate prompt variants from failure summaries.
9. Rerun the same test suite against variants.
10. Evaluate variant outputs.
11. Log tables, summaries, and artifacts to W&B.
12. Display local summary and W&B links.

## 13. CLI and Report Requirements

### 13.1 Primary Interface

The primary interface should be a CLI or Claude/Codex skill command that runs the QA loop and writes a Markdown report.

Required outputs:

- Terminal summary with baseline and variant metrics.
- Markdown report with command, result summary, variant table, recommendation, and W&B link when available.
- W&B run containing traces and tables when online mode is enabled.

### 13.2 Commands

Commands:

- Run demo harness.
- Run skill wrapper.
- Run with W&B disabled.
- Run with W&B online.
- Run with an explicit harness command for non-demo repos.

### 13.3 States

Required states:

- Not configured
- Ready
- Generating tests
- Running baseline
- Evaluating baseline
- Generating variants
- Running variants
- Complete
- Failed with recoverable error

### 13.4 Local Summary

Show:

- Test count
- Baseline pass rate
- Best variant pass rate
- Improvement delta
- Top failure category
- Average latency
- W&B project link

## 14. Implementation Plan

### Phase 1: Project Skeleton

Deliverables:

- Python project setup
- CLI and skill entrypoint
- `.env` loading
- W&B/Weave initialization
- Static policy and fallback tests

Exit criteria:

- CLI runs locally.
- W&B project initializes.
- A dummy traced operation appears in Weave.

### Phase 2: Baseline Workflow

Deliverables:

- Triage, policy lookup, decision, response, and evaluator functions
- Structured models for cases and results
- Weave tracing for all workflow steps

Exit criteria:

- Baseline runs across fallback tests.
- Failed and passed cases are visible locally.
- Traces show nested agent operations.

### Phase 3: Evaluation and Taxonomy

Deliverables:

- Deterministic expected-decision scoring
- LLM judge with structured output
- Failure taxonomy assignment
- Summary metrics

Exit criteria:

- Every case has pass/fail, score, failure category, and explanation.
- Baseline score is intentionally imperfect.

### Phase 4: Variants

Deliverables:

- Three prompt variants
- Rerun support for baseline plus variants
- Comparison summary

Exit criteria:

- At least one variant improves pass rate.
- Fixed and regressed cases are identifiable.

### Phase 5: W&B Evidence Layer

Deliverables:

- W&B Tables for test cases, eval results, and variant summaries
- Artifacts or Weave objects for policy, prompts, and test suite
- Links from local UI to W&B views

Exit criteria:

- Judges can inspect traces and tables in W&B.
- The demo can be told primarily through W&B evidence.

### Phase 6: Polish

Deliverables:

- Fast demo mode
- Cached demo suite
- Stable seed data
- Final report text
- Clean report formatting

Exit criteria:

- Demo completes reliably in under five minutes.
- Presenter can recover if live generation fails.

## 15. Hackathon Timeline

### First 2 Hours

- Working CLI demo.
- Static support policy and fallback tests.
- W&B/Weave traces visible.
- Baseline workflow runs end to end.

### Hours 3-4

- Evaluator returns structured scores.
- Baseline failure categories visible.
- W&B eval table populated.

### Hours 5-6

- Prompt variants run.
- Comparison metrics work.
- W&B traces and tables are demo-ready.

### Final Polish

- Add fast demo mode.
- Pre-run a stable full demo.
- Prepare the 2-3 minute pitch.
- Keep backup screenshots or W&B links ready.

## 16. Risks and Mitigations

### LLM Test Generation Is Flaky

Mitigations:

- Use static fallback tests.
- Cache generated tests.
- Default the demo to the deterministic fallback suite.

### Evaluator Is Inconsistent

Mitigations:

- Combine deterministic expected-decision scoring with LLM judging.
- Keep rubric simple.
- Use low temperature.
- Validate judge JSON and fall back on deterministic scores.

### W&B Setup Takes Too Long

Mitigations:

- Start with Weave traces only.
- Add tables before artifacts and reports.
- Keep a known-good W&B project and run available.

### Variants Do Not Improve Enough

Mitigations:

- Design baseline to fail known cases.
- Use controlled fallback tests.
- Include hand-authored variant prompts if generated prompts are weak.

### Live Demo Is Too Slow

Mitigations:

- Fast mode uses 10-15 cases.
- Full mode can be precomputed.
- Show W&B report from a previous run if needed.

## 17. Demo Script

1. "Most teams are building agents. We built the QA lab you need once your agent starts mattering."
2. "This is a refund-support agent with a small company policy."
3. "We start from a few examples and generate harder tests."
4. "Now we run the baseline. Every step is traced in W&B Weave."
5. "Here is a failure: the final answer is wrong, and the trace shows the decision agent ignored the refund-window clause."
6. "Agent QA Lab groups failures by root cause."
7. "Now it generates prompt variants targeted at those failures."
8. "We rerun the exact same test suite."
9. "W&B shows the comparison: baseline passed X%, best variant passed Y%, with row-level examples and trace links."
10. "That is the loop: test, trace, diagnose, improve, compare."

## 18. Acceptance Criteria

The MVP is complete when:

- A user can run the harness locally with `.env` configuration.
- The demo suite contains at least 20 cases.
- Baseline and at least one variant can run on the same suite.
- Every run is traced in Weave.
- Every case has an evaluation result.
- The report shows baseline vs variant metrics.
- W&B contains structured results for inspection.
- At least one failure can be explained through a Weave trace.
- At least one variant visibly improves the baseline.

## 19. Future Extensions

- Bring-your-own-agent adapter.
- Regression tests generated from production traces.
- Human feedback review queue.
- GitHub PR integration for prompt changes.
- Slack or Linear integration for agent incidents.
- Support for RAG agents, coding agents, browser agents, and voice agents.
- Cost-quality optimization across models.
- Scheduled eval runs.
- Team dashboards by agent, owner, and deployment version.
- CI integration that blocks prompt changes when regression count exceeds threshold.
