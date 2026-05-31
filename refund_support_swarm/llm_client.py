from __future__ import annotations

import json
import os
from typing import Any

import weave


def resolve_agent_mode(requested_mode: str = "auto") -> str:
    mode = os.getenv("AGENT_QA_AGENT_MODE", "auto") if requested_mode == "auto" else requested_mode
    if mode == "auto":
        return "llm" if os.getenv("OPENAI_API_KEY") else "deterministic"
    return mode


def llm_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


@weave.op
def call_llm_json(agent_name: str, system_prompt: str, user_payload: dict[str, Any], fallback: dict[str, Any], model: str) -> dict[str, Any]:
    if not llm_available():
        return {**fallback, "llm_used": False, "llm_fallback_reason": "missing_openai_api_key"}

    try:
        from openai import OpenAI
    except ImportError:
        return {**fallback, "llm_used": False, "llm_fallback_reason": "openai_package_not_installed"}

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, sort_keys=True)},
            ],
        )
    except Exception as exc:
        return {**fallback, "llm_used": False, "llm_fallback_reason": type(exc).__name__}
    content = response.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {**fallback, "llm_used": False, "llm_fallback_reason": "invalid_json", "llm_raw_response": content}
    return {**fallback, **data, "llm_used": True, "llm_agent": agent_name, "llm_model": model}


@weave.op
def call_llm_text(agent_name: str, system_prompt: str, user_payload: dict[str, Any], fallback: str, model: str) -> str:
    if not llm_available():
        return fallback

    try:
        from openai import OpenAI
    except ImportError:
        return fallback

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, sort_keys=True)},
            ],
        )
    except Exception:
        return fallback
    return response.choices[0].message.content or fallback
