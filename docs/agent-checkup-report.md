# Agent Checkup Report

Generated: 2026-05-31 19:16:00 UTC

## Command

```bash
.venv/bin/python scripts/run_agent_qa.py --cases 1 --wandb-mode disabled
```

## Target

- Repo: `/Users/vyahhi/Documents/Codex/2026-05-31-checkout-vyahhi-s-latest-repo-from/agent-qa-lab`
- Agent path: `refund_support_swarm`
- System type: `swarm`
- Agent mode: `llm`
- LLM provider: `wandb_inference`
- Model: `meta-llama/Llama-3.1-8B-Instruct`

## Result

- Exit code: `0`
- Baseline pass rate: `100.0%`
- Baseline top failure: `none`
- Best variant: `baseline`
- Best pass rate: `100.0%`
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
| `baseline` | 100.0% | 6.0 | 29924.0 ms |
| `variant_a_policy_grounded` | 100.0% | 6.0 | 32433.0 ms |
| `variant_b_injection_resistant` | 100.0% | 6.0 | 29875.0 ms |
| `variant_c_decision_rubric` | 100.0% | 6.0 | 29618.0 ms |

## Recommendation

Run a larger online W&B run before a live demo if you need variant comparison statistics. This smoke test verifies W&B Inference execution end to end.

## Raw Output

```text
cases=1
system_type=swarm
agent_mode=llm
llm_provider=wandb_inference
model=meta-llama/Llama-3.1-8B-Instruct
                      variant  pass_rate  mean_score  fixed_cases  regressions top_failure_category
                     baseline        1.0         1.0            0            0                 none
    variant_a_policy_grounded        1.0         1.0            0            0                 none
variant_b_injection_resistant        1.0         1.0            0            0                 none
    variant_c_decision_rubric        1.0         1.0            0            0                 none
swarm_metrics
                      variant  coordination_score  avg_handoffs  avg_latency_ms
                     baseline                 1.0           6.0         29924.0
    variant_a_policy_grounded                 1.0           6.0         32433.0
variant_b_injection_resistant                 1.0           6.0         29875.0
    variant_c_decision_rubric                 1.0           6.0         29618.0
```
