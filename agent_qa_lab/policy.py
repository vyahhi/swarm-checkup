from __future__ import annotations

import re
from pathlib import Path

from .config import DATA_DIR
from .models import PolicyClause


POLICY_TITLES = {
    "refund_window": "Standard refund window",
    "missing_order_id": "Missing order ID",
    "damaged_item": "Damaged physical goods",
    "digital_product": "Digital products",
    "subscription": "Subscriptions",
    "vip_exception": "VIP exceptions",
    "escalation": "Escalation",
    "injection": "Prompt injection",
}


def load_policy_text(path: Path | None = None) -> str:
    return (path or DATA_DIR / "refund_policy.md").read_text(encoding="utf-8")


def load_policy_clauses(path: Path | None = None) -> dict[str, PolicyClause]:
    text = load_policy_text(path)
    sections = re.split(r"\n##\s+", text)
    clauses: dict[str, PolicyClause] = {}
    for section in sections[1:]:
        lines = section.strip().splitlines()
        if not lines:
            continue
        clause_id = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        clauses[clause_id] = PolicyClause(
            id=clause_id,
            title=POLICY_TITLES.get(clause_id, clause_id.replace("_", " ").title()),
            text=body,
        )
    return clauses

