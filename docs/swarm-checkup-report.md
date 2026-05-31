# Swarm Checkup Report

Generated: 2026-05-31 23:48:41 UTC

## Command

```bash
.venv/bin/python scripts/run_agent_qa.py --cases 1 --wandb-mode disabled
```

## Target

- Repo: `.`
- Swarm path: `refund_support_swarm`
- System type: `swarm`
- Agent mode: `llm`
- LLM provider: `wandb_inference`
- Model: `Qwen/Qwen3.5-35B-A3B`

## Result

- Exit code: `0`
- Baseline pass rate: `100.0%`
- Baseline top failure: `none`
- Best variant: `variant_a_policy_grounded`
- Best pass rate: `100.0%`
- Improvement delta: `0.0%`
- Fixed cases: `0`
- Regressions: `0`
- Swarm visibility: `agent_trace`, `participating_agents`, and `handoff_count` are logged per case.

## Variant Summary

| Variant | Pass Rate | Mean Score | Fixed | Regressions | Top Failure |
|---|---:|---:|---:|---:|---|
| `baseline` | 100.0% | 1.000 | 0 | 0 | `none` |
| `variant_a_policy_grounded` | 100.0% | 1.000 | 0 | 0 | `none` |
| `variant_b_injection_resistant` | 100.0% | 1.000 | 0 | 0 | `none` |
| `variant_c_decision_rubric` | 100.0% | 1.000 | 0 | 0 | `none` |

## Swarm Metrics

| Variant | Coordination | Avg Handoffs | Avg Latency |
|---|---:|---:|---:|
| `baseline` | 100.0% | 6.0 | 14775.0 ms |
| `variant_a_policy_grounded` | 100.0% | 6.0 | 14471.0 ms |
| `variant_b_injection_resistant` | 100.0% | 6.0 | 14492.0 ms |
| `variant_c_decision_rubric` | 100.0% | 6.0 | 14509.0 ms |

## Recommendation

Baseline and variants passed this run. Increase the case count or add harder cases before changing prompts.

## Raw Output

```text
cases=1
system_type=swarm
agent_mode=llm
llm_provider=wandb_inference
model=Qwen/Qwen3.5-35B-A3B
                      variant  pass_rate  mean_score  fixed_cases  regressions top_failure_category
                     baseline        1.0         1.0            0            0                 none
    variant_a_policy_grounded        1.0         1.0            0            0                 none
variant_b_injection_resistant        1.0         1.0            0            0                 none
    variant_c_decision_rubric        1.0         1.0            0            0                 none
swarm_metrics
                      variant  coordination_score  avg_handoffs  avg_latency_ms
                     baseline                 1.0           6.0         14775.0
    variant_a_policy_grounded                 1.0           6.0         14471.0
variant_b_injection_resistant                 1.0           6.0         14492.0
    variant_c_decision_rubric                 1.0           6.0         14509.0
```

## Stderr

```text
Warning: Traces will not be logged. Call weave.init to log your traces to a project.
 (subsequent messages of this type will be suppressed)
```
