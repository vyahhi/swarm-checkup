from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PolicyClause:
    id: str
    title: str
    text: str


@dataclass(frozen=True)
class TestCase:
    id: str
    ticket: str
    category: str
    expected_decision: str
    policy_clause_ids: list[str]
    risk_tags: list[str]
    difficulty: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestCase":
        return cls(
            id=str(data["id"]),
            ticket=str(data["ticket"]),
            category=str(data["category"]),
            expected_decision=str(data["expected_decision"]),
            policy_clause_ids=list(data["policy_clause_ids"]),
            risk_tags=list(data["risk_tags"]),
            difficulty=str(data["difficulty"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PromptVariant:
    name: str
    prompt_version: str
    description: str
    behavior: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentResult:
    case_id: str
    variant: str
    prompt_version: str
    triage: dict[str, Any]
    policy_context: dict[str, Any]
    decision: str
    response: str
    latency_ms: int
    system_type: str = "swarm"
    agent_trace: list[dict[str, Any]] = field(default_factory=list)
    handoff_count: int = 0
    participating_agents: list[str] = field(default_factory=list)
    model: str = "Qwen/Qwen3.5-35B-A3B"
    trace_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationResult:
    case_id: str
    variant: str
    passed: bool
    overall_score: float
    policy_correctness: float
    decision_correctness: float
    completeness: float
    tone: float
    injection_resistance: float
    coordination: float
    failure_category: str
    explanation: str
    suggested_fix: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("passed")
        return data


@dataclass
class RunRecord:
    case: TestCase
    result: AgentResult
    evaluation: EvaluationResult

    def table_row(self) -> dict[str, Any]:
        row = self.case.to_dict()
        row.update(self.result.to_dict())
        row.update(self.evaluation.to_dict())
        row["policy_clause_ids"] = ", ".join(self.case.policy_clause_ids)
        row["risk_tags"] = ", ".join(self.case.risk_tags)
        participating_agents = list(self.result.participating_agents)
        if self.result.system_type == "swarm" and "qa_judge" not in participating_agents:
            participating_agents.append("qa_judge")
        row["participating_agents"] = ", ".join(participating_agents)
        return row


@dataclass
class VariantSummary:
    variant: str
    prompt_version: str
    pass_rate: float
    mean_score: float
    policy_score: float
    injection_score: float
    coordination_score: float
    avg_latency_ms: float
    avg_handoffs: float
    fixed_cases: int
    regressions: int
    top_failure_category: str = "none"
    estimated_cost: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
