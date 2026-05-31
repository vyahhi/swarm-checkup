from __future__ import annotations

import pandas as pd
import streamlit as st

from agent_qa_lab.config import load_settings
from agent_qa_lab.prompts import get_variants
from agent_qa_lab.runner import (
    failure_counts,
    records_to_dataframe,
    run_all_variants,
    summarize_variants,
    summaries_to_dataframe,
)
from agent_qa_lab.test_generator import generate_demo_suite, load_seed_tickets
from agent_qa_lab.wandb_logging import log_demo_tables, run_url, wandb_session


st.set_page_config(page_title="Agent QA Lab", page_icon="W&B", layout="wide")


def init_state() -> None:
    st.session_state.setdefault("cases", [])
    st.session_state.setdefault("records", {})
    st.session_state.setdefault("summaries", [])
    st.session_state.setdefault("wandb_url", "")


def render_metric_row(summary_df: pd.DataFrame) -> None:
    if summary_df.empty:
        return
    baseline = summary_df[summary_df["variant"] == "baseline"].iloc[0]
    best = summary_df.sort_values(["pass_rate", "mean_score"], ascending=False).iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Baseline Pass Rate", f"{baseline['pass_rate']:.0%}")
    col2.metric("Best Pass Rate", f"{best['pass_rate']:.0%}", f"{(best['pass_rate'] - baseline['pass_rate']):.0%}")
    col3.metric("Fixed Cases", int(best["fixed_cases"]))
    col4.metric("Top Remaining Failure", str(best["top_failure_category"]).replace("_", " "))


def main() -> None:
    init_state()
    settings = load_settings()

    st.title("Agent QA Lab")
    st.caption("Agents are easy to demo and hard to trust. This W&B-powered lab makes them measurable, debuggable, and improvable.")

    with st.sidebar:
        st.header("Controls")
        case_count = st.slider("Demo cases", min_value=10, max_value=24, value=16, step=1)
        wandb_mode = st.selectbox("W&B mode", ["online", "offline", "disabled"], index=0 if settings.wandb_enabled else 2)
        st.caption(f"Project: `{settings.project_name}`")

        if st.button("Load Demo Suite", use_container_width=True):
            st.session_state["cases"] = generate_demo_suite(case_count)
            st.session_state["records"] = {}
            st.session_state["summaries"] = []
            st.session_state["wandb_url"] = ""

        if st.button("Run Baseline", use_container_width=True, disabled=not st.session_state["cases"]):
            variants = [get_variants(include_baseline=True)[0]]
            st.session_state["records"] = run_all_variants(st.session_state["cases"], variants)
            st.session_state["summaries"] = summarize_variants(st.session_state["records"])

        if st.button("Run Baseline + Variants", use_container_width=True, disabled=not st.session_state["cases"]):
            active_settings = load_settings(wandb_mode=wandb_mode)
            with st.spinner("Running agent QA suite..."):
                with wandb_session(active_settings, run_name="agent-qa-lab-streamlit-demo") as run:
                    records = run_all_variants(st.session_state["cases"], get_variants(include_baseline=True))
                    summaries = summarize_variants(records)
                    eval_df = records_to_dataframe(records)
                    summary_df = summaries_to_dataframe(summaries)
                    fail_df = failure_counts(records)
                    log_demo_tables(run, eval_df, summary_df, fail_df)
                    st.session_state["wandb_url"] = run_url(run)
                st.session_state["records"] = records
                st.session_state["summaries"] = summaries

        if st.session_state["wandb_url"]:
            st.link_button("Open W&B Run", st.session_state["wandb_url"], use_container_width=True)

    if not st.session_state["cases"]:
        st.subheader("Ready")
        st.write("Load the demo suite to create refund-support stress tests.")
        st.dataframe(pd.DataFrame(load_seed_tickets()), use_container_width=True)
        return

    cases_df = pd.DataFrame([case.to_dict() for case in st.session_state["cases"]])
    records = st.session_state["records"]
    summaries = st.session_state["summaries"]
    summary_df = summaries_to_dataframe(summaries) if summaries else pd.DataFrame()

    st.subheader("Demo Suite")
    st.write(f"{len(st.session_state['cases'])} generated refund-support test cases.")
    st.dataframe(cases_df[["id", "category", "expected_decision", "difficulty", "ticket"]], use_container_width=True, hide_index=True)

    if not records:
        return

    st.subheader("Variant Comparison")
    render_metric_row(summary_df)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    eval_df = records_to_dataframe(records)
    fail_df = failure_counts(records)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Failure Taxonomy")
        if fail_df.empty:
            st.success("No failures found.")
        else:
            st.bar_chart(fail_df, x="failure_category", y="count", color="variant")
    with right:
        st.subheader("Fixed Cases")
        if "baseline" in records:
            baseline_failures = {record.case.id for record in records["baseline"] if not record.evaluation.passed}
            fixed_rows = eval_df[(eval_df["id"].isin(baseline_failures)) & (eval_df["pass"])]
            st.dataframe(
                fixed_rows[["id", "variant", "category", "decision", "expected_decision", "overall_score"]],
                use_container_width=True,
                hide_index=True,
            )

    st.subheader("Representative Failures")
    failures = eval_df[~eval_df["pass"]].copy()
    if failures.empty:
        st.success("All cases passed.")
    else:
        st.dataframe(
            failures[["id", "variant", "category", "decision", "expected_decision", "failure_category", "explanation", "response"]].head(12),
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()

