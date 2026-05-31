from __future__ import annotations

from typing import Any

import weave

from refund_support_swarm.llm_client import call_llm_text

@weave.op
def draft_response(
    case: dict[str, Any],
    triage: dict[str, Any],
    decision: dict[str, Any],
    variant: dict[str, str],
    model: str,
) -> str:
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
    llm_response = call_llm_text(
        "response_agent",
        "You are a customer support response agent. Write one concise customer-facing response. Start with Thanks. Include the case reference.",
        {"case": case, "triage": triage, "decision": decision, "variant": variant, "response_requirements": response},
        model,
    )
    if not llm_response.lower().startswith("thanks") or str(ticket_id) not in llm_response:
        raise RuntimeError("response_agent returned a response that failed output requirements")
    return llm_response
