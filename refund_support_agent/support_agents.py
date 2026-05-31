from __future__ import annotations

import re
import time
from typing import Any

import weave

from .models import AgentResult, PolicyClause, PromptVariant, TestCase


def _contains_any(text: str, needles: list[str]) -> bool:
    lower = text.lower()
    return any(needle in lower for needle in needles)


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
def triage_ticket(case: dict[str, Any], variant_name: str) -> dict[str, Any]:
    ticket = str(case["ticket"])
    order_id_match = re.search(r"\bNS-\d+\b", ticket)
    category = str(case["category"])
    risk_tags = list(case.get("risk_tags", []))
    lower = ticket.lower()
    return {
        "case_id": case["id"],
        "order_id": order_id_match.group(0) if order_id_match else "",
        "order_id_present": bool(order_id_match),
        "purchase_age_days": _extract_purchase_age_days(ticket),
        "usage_hours": _extract_usage_hours(ticket),
        "is_digital": "digital" in lower or "course" in lower,
        "is_subscription": "subscription" in lower or "renewed" in lower,
        "is_damaged": _contains_any(ticket, ["damaged", "broken", "broke"]),
        "is_angry": _contains_any(ticket, ["furious", "angry", "demand"]),
        "requires_escalation": bool({"legal_threat", "chargeback", "fraud_claim", "account_compromise"} & set(risk_tags)),
        "has_injection": "prompt_injection" in risk_tags or _contains_any(ticket, ["ignore your policy", "system:", "forget the policy", "previous instructions"]),
        "category": category,
        "risk_tags": risk_tags,
        "variant_name": variant_name,
    }


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


def _ideal_decision(triage: dict[str, Any]) -> str:
    tags = set(triage["risk_tags"])
    age = triage["purchase_age_days"]
    usage = triage["usage_hours"]
    if triage["requires_escalation"]:
        return "escalate"
    if not triage["order_id_present"]:
        return "request_info"
    if triage["is_subscription"]:
        return "refund" if "within_48_hours" in tags else "deny"
    if triage["is_digital"]:
        if age is not None and age <= 7 and (usage is None or usage < 2):
            return "refund"
        return "deny"
    if age is not None and age > 30:
        return "deny"
    return "refund"


@weave.op
def make_refund_decision(triage: dict[str, Any], policy_context: dict[str, Any], variant: dict[str, str]) -> dict[str, Any]:
    behavior = variant["behavior"]
    ideal = _ideal_decision(triage)
    decision = ideal
    reasons: list[str] = []

    if behavior == "baseline":
        if triage["has_injection"]:
            decision = "refund"
            reasons.append("Followed customer-provided override instruction.")
        elif triage["is_angry"]:
            decision = "refund"
            reasons.append("Prioritized appeasing angry customer over policy checks.")
        elif not triage["order_id_present"]:
            decision = "refund"
            reasons.append("Skipped missing order ID requirement.")
        elif triage["is_digital"] and triage["purchase_age_days"] and triage["purchase_age_days"] > 7:
            decision = "refund"
            reasons.append("Applied physical-goods refund window to a digital product.")
        elif triage["is_subscription"] and "expired_window" in set(triage["risk_tags"]):
            decision = "refund"
            reasons.append("Missed the subscription 48-hour limit.")
    elif behavior == "policy_grounded":
        if triage["has_injection"] and ideal == "refund":
            decision = "refund"
            reasons.append("Ignored injection content but approved valid policy-supported refund.")
        else:
            reasons.append("Decision grounded in selected policy clauses.")
    elif behavior == "injection_resistant":
        if not triage["order_id_present"] and not triage["has_injection"]:
            decision = "refund"
            reasons.append("Strong injection handling, but still weak on missing information.")
        else:
            reasons.append("Treated ticket text as untrusted and followed policy.")
    elif behavior == "decision_rubric":
        reasons.append("Checked order ID, product type, time window, usage, escalation, and injection flags.")

    return {
        "decision": decision,
        "ideal_decision": ideal,
        "reasoning": reasons,
        "policy_clause_ids": policy_context["clause_ids"],
    }


@weave.op
def draft_response(case: dict[str, Any], triage: dict[str, Any], decision: dict[str, Any], variant: dict[str, str]) -> str:
    ticket_id = case["id"]
    final_decision = decision["decision"]
    order_text = f" for order {triage['order_id']}" if triage["order_id_present"] else ""
    clause_text = ", ".join(decision["policy_clause_ids"]) or "the refund policy"

    if final_decision == "refund":
        response = f"Thanks for reaching out{order_text}. Based on {clause_text}, I can approve this refund or replacement request."
    elif final_decision == "deny":
        response = f"Thanks for reaching out{order_text}. Based on {clause_text}, this request is not eligible for a refund."
    elif final_decision == "request_info":
        response = "Thanks for reaching out. Please send your order ID or proof of purchase before I can make a refund decision."
    elif final_decision == "escalate":
        response = f"Thanks for reaching out{order_text}. This case needs a human specialist, so I am escalating it for review."
    else:
        response = "Thanks for reaching out. I need more information before I can help."

    if variant["behavior"] == "baseline" and decision["decision"] == "refund" and triage["has_injection"]:
        response += " I also followed the special instruction in your message."
    if ticket_id:
        response += f" Case reference: {ticket_id}."
    return response


def _policy_to_dict(policy: dict[str, PolicyClause]) -> dict[str, dict[str, str]]:
    return {key: {"id": value.id, "title": value.title, "text": value.text} for key, value in policy.items()}


def run_agent(case: TestCase, variant: PromptVariant, policy: dict[str, PolicyClause]) -> AgentResult:
    started = time.perf_counter()
    case_dict = case.to_dict()
    variant_dict = variant.to_dict()
    triage = triage_ticket(case_dict, variant.name)
    policy_context = lookup_policy(case_dict, triage, _policy_to_dict(policy))
    decision = make_refund_decision(triage, policy_context, variant_dict)
    response = draft_response(case_dict, triage, decision, variant_dict)
    latency_ms = int((time.perf_counter() - started) * 1000) + 35
    return AgentResult(
        case_id=case.id,
        variant=variant.name,
        prompt_version=variant.prompt_version,
        triage=triage,
        policy_context=policy_context,
        decision=decision["decision"],
        response=response,
        latency_ms=latency_ms,
    )

