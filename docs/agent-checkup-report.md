# Agent Checkup Report

Generated: 2026-05-31 17:54:45 UTC

## Command

```bash
/Users/vyahhi/projects/sundai/20260531/.venv/bin/python scripts/run_agent_qa.py --cases 24 --wandb-mode disabled --system-type swarm --agent-mode deterministic
```

## Target

- Repo: `/Users/vyahhi/projects/sundai/20260531`
- Agent path: `refund_support_swarm`
- System type: `swarm`
- Agent mode: `deterministic`

## Result

- Exit code: `0`
- Baseline pass rate: `62.5%`
- Baseline top failure: `missing_required_information`
- Best variant: `variant_a_policy_grounded`
- Best pass rate: `100.0%`
- Improvement delta: `37.5%`
- Fixed cases: `9`
- Regressions: `0`
- Swarm visibility: `agent_trace`, `participating_agents`, and `handoff_count` are logged per case.

## Variant Summary

| Variant | Pass Rate | Mean Score | Fixed | Regressions | Top Failure |
|---|---:|---:|---:|---:|---|
| `baseline` | 62.5% | 0.775 | 0 | 0 | `missing_required_information` |
| `variant_a_policy_grounded` | 100.0% | 1.000 | 9 | 0 | `none` |
| `variant_b_injection_resistant` | 87.5% | 0.919 | 6 | 0 | `missing_required_information` |
| `variant_c_decision_rubric` | 100.0% | 1.000 | 9 | 0 | `none` |

## Swarm Metrics

| Variant | Coordination | Avg Handoffs | Avg Latency |
|---|---:|---:|---:|
| `baseline` | 100.0% | 6.0 | 92.0 ms |
| `variant_a_policy_grounded` | 100.0% | 6.0 | 92.0 ms |
| `variant_b_injection_resistant` | 100.0% | 6.0 | 92.0 ms |
| `variant_c_decision_rubric` | 100.0% | 6.0 | 92.0 ms |

## Recommendation

Use `variant_a_policy_grounded` as the demo winner and show its fixed cases against the baseline.

## Raw Output

```text
cases=24
system_type=swarm
agent_mode=deterministic
                      variant  pass_rate  mean_score  fixed_cases  regressions         top_failure_category
                     baseline      0.625       0.775            0            0 missing_required_information
    variant_a_policy_grounded      1.000       1.000            9            0                         none
variant_b_injection_resistant      0.875       0.919            6            0 missing_required_information
    variant_c_decision_rubric      1.000       1.000            9            0                         none
swarm_metrics
                      variant  coordination_score  avg_handoffs  avg_latency_ms
                     baseline                 1.0           6.0            92.0
    variant_a_policy_grounded                 1.0           6.0            92.0
variant_b_injection_resistant                 1.0           6.0            92.0
    variant_c_decision_rubric                 1.0           6.0            92.0
```

## Stderr

```text
Warning: Traces will not be logged. Call weave.init to log your traces to a project.
 (subsequent messages of this type will be suppressed)
```
