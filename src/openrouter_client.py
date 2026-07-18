import base64
import json
import os
import re
from typing import Any, Optional

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def to_data_url(image_bytes: bytes, content_type: str) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def _force_strict(schema: dict) -> dict:
    """Recursively require every property and forbid extras, as OpenAI-style
    strict structured outputs demand — pydantic's model_json_schema() doesn't
    set this on its own."""
    if isinstance(schema, dict):
        if schema.get("type") == "object" or "properties" in schema:
            props = schema.get("properties")
            if props:
                schema["required"] = list(props.keys())
                schema["additionalProperties"] = False
                for v in props.values():
                    _force_strict(v)
        if "items" in schema:
            _force_strict(schema["items"])
        for defs_key in ("$defs", "definitions"):
            if defs_key in schema:
                for v in schema[defs_key].values():
                    _force_strict(v)
    return schema


def build_json_schema(model_cls, name: str) -> dict:
    schema = model_cls.model_json_schema()
    _force_strict(schema)
    return {
        "type": "json_schema",
        "json_schema": {"name": name, "strict": True, "schema": schema},
    }


def parse_json_response(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = _JSON_BLOCK_RE.search(raw)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"Could not parse JSON from model response: {raw[:200]!r}")


async def call_openrouter(
    model: str,
    messages: list[dict[str, Any]],
    response_format: Optional[dict] = None,
    max_tokens: int = 1500,
    timeout: float = 45.0,
) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    payload: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if response_format:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://design-critic.local",
        "X-Title": "Design Critic",
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"]
