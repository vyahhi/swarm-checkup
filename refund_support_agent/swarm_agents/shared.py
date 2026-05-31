from __future__ import annotations

from typing import Any

from refund_support_agent.models import PolicyClause


def contains_any(text: str, needles: list[str]) -> bool:
    lower = text.lower()
    return any(needle in lower for needle in needles)


def policy_to_dict(policy: dict[str, PolicyClause]) -> dict[str, dict[str, str]]:
    return {key: {"id": value.id, "title": value.title, "text": value.text} for key, value in policy.items()}


def agent_step(
    agent: str,
    role: str,
    output: dict[str, Any] | str,
    latency_ms: int,
    reads: list[str] | None = None,
    writes: list[str] | None = None,
) -> dict[str, Any]:
    if isinstance(output, dict):
        summary = {
            key: output[key]
            for key in output.keys() & {"case_id", "decision", "order_id_present", "requires_escalation", "has_injection", "clause_ids"}
        }
    else:
        summary = {"response_preview": output[:120]}
    return {
        "event_type": "agent_step",
        "agent": agent,
        "role": role,
        "status": "ok",
        "reads": reads or [],
        "writes": writes or [],
        "latency_ms": latency_ms,
        "output_summary": summary,
    }


def handoff_event(from_agent: str, to_agent: str, payload_keys: list[str], reason: str, latency_ms: int = 2) -> dict[str, Any]:
    return {
        "event_type": "handoff",
        "from_agent": from_agent,
        "to_agent": to_agent,
        "message": {
            "payload_keys": payload_keys,
            "reason": reason,
        },
        "status": "ok",
        "latency_ms": latency_ms,
    }

