# Agent QA Skill Report

Generated: 2026-05-31 17:04:33 UTC

## Command

```bash
/Users/vyahhi/projects/sundai/20260531/.venv/bin/python scripts/run_agent_qa.py --cases 24 --wandb-mode disabled
```

## Target

- Repo: `/Users/vyahhi/projects/sundai/20260531`
- Agent path: `refund_support_agent`

## Result

- Exit code: `0`
- Baseline pass rate: `62.5%`
- Baseline top failure: `missing_required_information`
- Best variant: `variant_a_policy_grounded`
- Best pass rate: `100.0%`
- Improvement delta: `37.5%`
- Fixed cases: `9`
- Regressions: `0`

## Variant Summary

| Variant | Pass Rate | Mean Score | Fixed | Regressions | Top Failure |
|---|---:|---:|---:|---:|---|
| `baseline` | 62.5% | 0.750 | 0 | 0 | `missing_required_information` |
| `variant_a_policy_grounded` | 100.0% | 1.000 | 9 | 0 | `none` |
| `variant_b_injection_resistant` | 87.5% | 0.910 | 6 | 0 | `missing_required_information` |
| `variant_c_decision_rubric` | 100.0% | 1.000 | 9 | 0 | `none` |

## Recommendation

Use `variant_a_policy_grounded` as the demo winner and show its fixed cases against the baseline.

## Raw Output

```text
cases=24
                      variant  pass_rate  mean_score  fixed_cases  regressions         top_failure_category
                     baseline      0.625        0.75            0            0 missing_required_information
    variant_a_policy_grounded      1.000        1.00            9            0                         none
variant_b_injection_resistant      0.875        0.91            6            0 missing_required_information
    variant_c_decision_rubric      1.000        1.00            9            0                         none
```

## Stderr

```text
Warning: Traces will not be logged. Call weave.init to log your traces to a project.
 (subsequent messages of this type will be suppressed)
```
