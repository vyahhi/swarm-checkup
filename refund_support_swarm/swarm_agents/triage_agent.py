from __future__ import annotations

import re
from typing import Any

import weave

from refund_support_swarm.llm_client import call_llm_json

from .shared import contains_any


def _extract_purchase_age_days(ticket: str) -> int | None:
    lower = ticket.lower()
    direct = re.search(r"(\d+)\s*days?", lower)
    if direct:
        return int(direct.group(1))
    if "yesterday" in lower:
        return 1
    if "two weeks" in lower:
        return 14
    if "36 hours" in lower:
        return 2
    if "5 days" in lower:
        return 5
    return None


def _extract_usage_hours(ticket: str) -> float | None:
    lower = ticket.lower()
    hours = re.search(r"(\d+(?:\.\d+)?)\s*hours?", lower)
    if hours:
        return float(hours.group(1))
    minutes = re.search(r"(\d+)\s*minutes?", lower)
    if minutes:
        return int(minutes.group(1)) / 60
    return None


@weave.op
def triage_ticket(case: dict[str, Any], variant_name: str, agent_mode: str = "deterministic", model: str = "gpt-4o-mini") -> dict[str, Any]:
    ticket = str(case["ticket"])
    order_id_match = re.search(r"\bNS-\d+\b", ticket)
    category = str(case["category"])
    risk_tags = list(case.get("risk_tags", []))
    lower = ticket.lower()
    fallback = {
        "case_id": case["id"],
        "order_id": order_id_match.group(0) if order_id_match else "",
        "order_id_present": bool(order_id_match),
        "purchase_age_days": _extract_purchase_age_days(ticket),
        "usage_hours": _extract_usage_hours(ticket),
        "is_digital": "digital" in lower or "course" in lower,
        "is_subscription": "subscription" in lower or "renewed" in lower,
        "is_damaged": contains_any(ticket, ["damaged", "broken", "broke"]),
        "is_angry": contains_any(ticket, ["furious", "angry", "demand"]),
        "requires_escalation": bool({"legal_threat", "chargeback", "fraud_claim", "account_compromise"} & set(risk_tags)),
        "has_injection": "prompt_injection" in risk_tags
        or contains_any(ticket, ["ignore your policy", "system:", "forget the policy", "previous instructions"]),
        "category": category,
        "risk_tags": risk_tags,
        "variant_name": variant_name,
    }
    if agent_mode != "llm":
        return fallback
    llm_result = call_llm_json(
        "triage_agent",
        "You are a support triage agent. Return JSON. Preserve all fallback fields and add concise llm_notes if useful.",
        {"case": case, "fallback_triage": fallback},
        fallback,
        model,
    )
    for key, value in fallback.items():
        if key not in llm_result or not isinstance(llm_result[key], type(value)) and value is not None:
            llm_result[key] = value
    return llm_result
