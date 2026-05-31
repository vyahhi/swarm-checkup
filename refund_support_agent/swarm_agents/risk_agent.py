from __future__ import annotations

from typing import Any

import weave


@weave.op
def risk_agent_review(triage: dict[str, Any], policy_context: dict[str, Any]) -> dict[str, Any]:
    risk_tags = set(triage["risk_tags"])
    return {
        "case_id": triage["case_id"],
        "requires_human": triage["requires_escalation"],
        "injection_risk": triage["has_injection"],
        "coordination_risks": sorted(
            tag
            for tag in risk_tags
            if tag in {"prompt_injection", "missing_order_id", "legal_threat", "chargeback", "fraud_claim", "account_compromise"}
        ),
        "policy_context_available": bool(policy_context["clause_ids"]),
    }

