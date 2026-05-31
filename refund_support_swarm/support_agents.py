from __future__ import annotations

import time

from .models import AgentResult, PolicyClause, PromptVariant, TestCase
from .swarm_agents.coordinator import coordinator_plan
from .swarm_agents.decision_agent import make_refund_decision
from .swarm_agents.policy_agent import lookup_policy
from .swarm_agents.qa_judge import qa_judge_review
from .swarm_agents.response_agent import draft_response
from .swarm_agents.risk_agent import risk_agent_review
from .swarm_agents.shared import agent_step, handoff_event, policy_to_dict
from .swarm_agents.triage_agent import triage_ticket


def run_agent(
    case: TestCase,
    variant: PromptVariant,
    policy: dict[str, PolicyClause],
    model: str = "meta-llama/Llama-3.1-8B-Instruct",
) -> AgentResult:
    started = time.perf_counter()
    case_dict = case.to_dict()
    variant_dict = variant.to_dict()
    agent_trace: list[dict] = []

    blackboard: dict[str, object] = {"case": case_dict, "variant": variant_dict}
    plan = coordinator_plan(case_dict, variant.name, model)
    blackboard["plan"] = plan
    agent_trace.append(agent_step("coordinator", "Create the execution plan and handoff contract.", plan, 4, reads=["case"], writes=["plan"]))
    agent_trace.append(handoff_event("coordinator", "triage_agent", ["case", "variant"], "Start by extracting structured facts and routing flags."))

    triage = triage_ticket(case_dict, variant.name, model)
    blackboard["triage"] = triage
    agent_trace.append(
        agent_step("triage_agent", "Extract facts, flags, and routing needs from the ticket.", triage, 8, reads=["case"], writes=["triage"])
    )
    agent_trace.append(handoff_event("triage_agent", "policy_agent", ["case", "triage"], "Retrieve policy clauses for the extracted case facts."))

    policy_context = lookup_policy(case_dict, triage, policy_to_dict(policy), model)
    blackboard["policy_context"] = policy_context
    agent_trace.append(
        agent_step("policy_agent", "Retrieve the policy clauses relevant to the case.", policy_context, 7, reads=["case", "triage"], writes=["policy_context"])
    )
    agent_trace.append(handoff_event("policy_agent", "risk_agent", ["triage", "policy_context"], "Check safety, escalation, and prompt-injection risks."))
    risk_review = risk_agent_review(triage, policy_context, model)
    blackboard["risk_review"] = risk_review
    agent_trace.append(
        agent_step("risk_agent", "Check escalation, injection, and handoff risks.", risk_review, 6, reads=["triage", "policy_context"], writes=["risk_review"])
    )
    agent_trace.append(handoff_event("risk_agent", "decision_agent", ["triage", "policy_context", "risk_review"], "Make the policy decision from shared state."))

    decision = make_refund_decision(triage, policy_context, variant_dict, model)
    blackboard["decision"] = decision
    agent_trace.append(
        agent_step(
            "decision_agent",
            "Make the refund decision from structured triage, policy, and risk state.",
            decision,
            9,
            reads=["triage", "policy_context", "risk_review"],
            writes=["decision"],
        )
    )
    agent_trace.append(handoff_event("decision_agent", "response_agent", ["case", "triage", "decision"], "Draft the customer-facing response."))

    response = draft_response(case_dict, triage, decision, variant_dict, model)
    blackboard["response"] = response
    agent_trace.append(
        agent_step("response_agent", "Draft a customer-safe final response.", response, 6, reads=["case", "triage", "decision"], writes=["response"])
    )
    agent_trace.append(handoff_event("response_agent", "qa_judge", ["case", "triage", "decision", "response"], "Review the final answer before release."))
    qa_review = qa_judge_review(case_dict, triage, decision, response, model)
    blackboard["qa_review"] = qa_review
    agent_trace.append(
        agent_step(
            "qa_judge",
            "Check the final response against expected decision, policy boundary, and customer readiness.",
            qa_review,
            5,
            reads=["case", "decision", "response"],
            writes=["qa_review"],
        )
    )

    latency_ms = int((time.perf_counter() - started) * 1000) + 35 + sum(int(step["latency_ms"]) for step in agent_trace)
    participating_agents = [str(step["agent"]) for step in agent_trace if step.get("event_type") == "agent_step"]

    return AgentResult(
        case_id=case.id,
        variant=variant.name,
        prompt_version=variant.prompt_version,
        triage=triage,
        policy_context=policy_context,
        decision=decision["decision"],
        response=response,
        latency_ms=latency_ms,
        system_type="swarm",
        agent_trace=agent_trace,
        handoff_count=sum(1 for step in agent_trace if step.get("event_type") == "handoff"),
        participating_agents=participating_agents,
        model=model,
    )
