from __future__ import annotations

from typing import Any

import weave


@weave.op
def lookup_policy(case: dict[str, Any], triage: dict[str, Any], policy: dict[str, dict[str, str]]) -> dict[str, Any]:
    clause_ids = list(case.get("policy_clause_ids", []))
    if triage["requires_escalation"] and "escalation" not in clause_ids:
        clause_ids.append("escalation")
    if triage["has_injection"] and "injection" not in clause_ids:
        clause_ids.append("injection")
    clauses = [policy[clause_id] for clause_id in clause_ids if clause_id in policy]
    return {
        "clause_ids": [clause["id"] for clause in clauses],
        "clauses": clauses,
    }

