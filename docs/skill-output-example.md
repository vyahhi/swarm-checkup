# Skill Output Example

This is a representative smoke-test output from running the bundled `swarm-checkup` skill against the demo refund-support swarm.

## Command

```bash
codex exec -C . "Use swarm-checkup skill for swarm refund_support_swarm. Run 1 case. Run W&B disabled."
```

Equivalent direct runner command:

```bash
python3 skills/swarm-checkup/scripts/run_agent_qa.py --agent-path refund_support_swarm --cases 1 --wandb-mode disabled
```

`--wandb-mode disabled` disables W&B run logging only. The swarm agents still use W&B Inference, so `WANDB_API_KEY` must be present in the shell or `.env`.

## Console Output

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

## Generated Report

The skill writes a Markdown report to:

```text
docs/swarm-checkup-report.md
```

The report includes:

- command run
- target swarm path
- system type and agent mode
- LLM provider and model
- baseline pass rate
- best variant
- fixed cases and regressions
- failure taxonomy summary
- coordination score, handoff count, and latency
- W&B warning or run link, depending on logging mode

## Example Interpretation

This one-case smoke test confirms that the skill can execute the swarm end to end:

- all four variants completed successfully
- the system reported `system_type=swarm` and `agent_mode=llm`
- the run used W&B Inference with `Qwen/Qwen3.5-35B-A3B`
- every variant had six recorded handoffs and a `100.0%` coordination score
- no failures or regressions were found in this small smoke run

For a real evaluation, increase the case count:

```bash
python3 skills/swarm-checkup/scripts/run_agent_qa.py --agent-path refund_support_swarm --cases 24
```
