from __future__ import annotations

from typing import Any

import weave

from refund_support_swarm.llm_client import call_llm_json

@weave.op
def qa_judge_review(
    case: dict[str, Any],
    triage: dict[str, Any],
    decision: dict[str, Any],
    response: str,
    model: str,
) -> dict[str, Any]:
    response_lower = response.lower()
    defaults = {
        "case_id": case["id"],
        "decision": decision["decision"],
        "matches_expected_decision": decision["decision"] == case["expected_decision"],
        "mentions_case_reference": case["id"].lower() in response_lower,
        "preserved_policy_boundary": "special instruction" not in response_lower,
        "ready_for_customer": response_lower.startswith("thanks"),
        "handoff_note": "QA judge reviewed the final response before release.",
    }
    return call_llm_json(
        "qa_judge",
        "You are a QA judge for a support swarm. Return JSON. Preserve required fields and add concise llm_notes about answer quality.",
        {"case": case, "triage": triage, "decision": decision, "response": response, "required_review_fields": defaults},
        defaults,
        model,
    )
