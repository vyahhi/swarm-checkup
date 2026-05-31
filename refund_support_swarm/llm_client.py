from __future__ import annotations

import json
import os
from typing import Any

import weave


WANDB_INFERENCE_BASE_URL = "https://api.inference.wandb.ai/v1"
DEFAULT_WANDB_INFERENCE_MODEL = "Qwen/Qwen3.5-35B-A3B"


def llm_available() -> bool:
    return bool(os.getenv("WANDB_API_KEY"))


def _client() -> "OpenAI":
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("The openai package is required for W&B Inference") from None

    return OpenAI(
        base_url=os.getenv("WANDB_INFERENCE_BASE_URL", WANDB_INFERENCE_BASE_URL),
        api_key=os.environ["WANDB_API_KEY"],
        project=os.getenv("AGENT_QA_WANDB_INFERENCE_PROJECT"),
        timeout=float(os.getenv("WANDB_INFERENCE_TIMEOUT_SECONDS", "20")),
        max_retries=int(os.getenv("WANDB_INFERENCE_MAX_RETRIES", "0")),
    )


def _fallback_json(agent_name: str, defaults: dict[str, Any], model: str, error: Exception) -> dict[str, Any]:
    return {
        **defaults,
        "llm_used": False,
        "llm_agent": agent_name,
        "llm_model": model,
        "llm_error": f"{type(error).__name__}: {error}",
    }


@weave.op
def call_llm_json(agent_name: str, system_prompt: str, user_payload: dict[str, Any], defaults: dict[str, Any], model: str) -> dict[str, Any]:
    if not llm_available():
        raise RuntimeError("WANDB_API_KEY is required for W&B Inference")

    client = _client()
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": f"{system_prompt}\nReturn only a valid JSON object."},
                {"role": "user", "content": json.dumps(user_payload, sort_keys=True)},
            ],
        )
    except Exception as exc:
        return _fallback_json(agent_name, defaults, model, exc)
    content = response.choices[0].message.content or "{}"
    try:
        data = _json_object_from_text(content)
    except json.JSONDecodeError as exc:
        return _fallback_json(agent_name, defaults, model, exc)
    return {**defaults, **data, "llm_used": True, "llm_agent": agent_name, "llm_model": model}


@weave.op
def call_llm_text(agent_name: str, system_prompt: str, user_payload: dict[str, Any], model: str) -> str:
    if not llm_available():
        raise RuntimeError("WANDB_API_KEY is required for W&B Inference")

    client = _client()
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, sort_keys=True)},
            ],
        )
    except Exception:
        return str(user_payload.get("response_requirements", ""))
    content = response.choices[0].message.content
    if not content:
        return str(user_payload.get("response_requirements", ""))
    return content


def _json_object_from_text(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise json.JSONDecodeError("expected a JSON object", text, 0)
    return parsed
