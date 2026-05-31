from __future__ import annotations

from typing import Any

import weave

from refund_support_swarm.llm_client import call_llm_json

@weave.op
def lookup_policy(
    case: dict[str, Any],
    triage: dict[str, Any],
    policy: dict[str, dict[str, str]],
    model: str,
) -> dict[str, Any]:
    clause_ids = list(case.get("policy_clause_ids", []))
    if triage["requires_escalation"] and "escalation" not in clause_ids:
        clause_ids.append("escalation")
    if triage["has_injection"] and "injection" not in clause_ids:
        clause_ids.append("injection")
    clauses = [policy[clause_id] for clause_id in clause_ids if clause_id in policy]
    defaults = {
        "clause_ids": [clause["id"] for clause in clauses],
        "clauses": clauses,
    }
    llm_result = call_llm_json(
        "policy_agent",
        "You are a policy retrieval agent. Return JSON. Preserve clause_ids and clauses unless a relevant policy is clearly missing.",
        {"case": case, "triage": triage, "available_policy": policy, "required_policy_context": defaults},
        defaults,
        model,
    )
    if not isinstance(llm_result.get("clause_ids"), list) or not isinstance(llm_result.get("clauses"), list):
        raise RuntimeError("policy_agent returned invalid policy_context")
    return llm_result
