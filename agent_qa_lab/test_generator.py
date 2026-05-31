from __future__ import annotations

import json

import weave

from .config import DATA_DIR
from .models import TestCase


def load_seed_tickets() -> list[dict[str, str]]:
    return json.loads((DATA_DIR / "seed_tickets.json").read_text(encoding="utf-8"))


def load_fallback_tests(limit: int | None = None) -> list[TestCase]:
    data = json.loads((DATA_DIR / "fallback_tests.json").read_text(encoding="utf-8"))
    cases = [TestCase.from_dict(item) for item in data]
    return cases[:limit] if limit else cases


@weave.op
def generate_test_cases(seed_tickets: list[dict[str, str]], target_count: int = 24) -> list[dict]:
    """Return a deterministic generated suite for reliable hackathon demos."""
    cases = load_fallback_tests(limit=target_count)
    seed_categories = {ticket["category"] for ticket in seed_tickets}
    generated = []
    for case in cases:
        item = case.to_dict()
        item["generated_from_seed"] = case.category in seed_categories
        generated.append(item)
    return generated


def generate_demo_suite(target_count: int = 24) -> list[TestCase]:
    return [TestCase.from_dict(item) for item in generate_test_cases(load_seed_tickets(), target_count)]

