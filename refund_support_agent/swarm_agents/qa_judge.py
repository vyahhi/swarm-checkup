from __future__ import annotations

from typing import Any

import weave


@weave.op
def qa_judge_review(case: dict[str, Any], triage: dict[str, Any], decision: dict[str, Any], response: str) -> dict[str, Any]:
    response_lower = response.lower()
    return {
        "case_id": case["id"],
        "decision": decision["decision"],
        "matches_expected_decision": decision["decision"] == case["expected_decision"],
        "mentions_case_reference": case["id"].lower() in response_lower,
        "preserved_policy_boundary": "special instruction" not in response_lower,
        "ready_for_customer": response_lower.startswith("thanks"),
        "handoff_note": "QA judge reviewed the final response before release.",
    }

