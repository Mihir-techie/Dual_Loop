from __future__ import annotations

import json
from typing import Any, Dict, List

from openai import OpenAI

from config.settings import settings

_GROQ_BASE = "https://api.groq.com/openai/v1"


def _client() -> OpenAI:
    return OpenAI(api_key=settings.groq_api_key, base_url=_GROQ_BASE)


def _chat(system: str, user: str) -> str:
    client = _client()
    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.35,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    out = resp.choices[0].message.content if resp.choices else None
    return str(out or "").strip() or "I could not generate a reply. Please try again."


def _format_rag(hits: List[Dict[str, Any]]) -> str:
    if not hits:
        return "(no similar past exchanges retrieved)"
    lines = []
    for i, h in enumerate(hits, 1):
        sc = h.get("score", 0)
        txt = (h.get("text") or "").strip().replace("\n", " ")
        ch = h.get("channel") or "chat"
        lines.append(f'{i}. [similarity={sc:.3f}, channel={ch}] "{txt[:700]}"')
    return "\n".join(lines)


def _format_sql_thread(messages: List[Any]) -> str:
    lines = []
    for m in messages[-16:]:
        role = m.role.upper()
        lines.append(f"{role}: {m.content}")
    return "\n".join(lines) if lines else "(empty thread)"


def generate_support_reply(
    user_message: str,
    *,
    rag_hits: List[Dict[str, Any]],
    sql_messages: List[Any],
    analytics: Dict[str, Any],
    memory_disabled: bool,
    user_display_name: str,
    consent: bool,
) -> str:
    if not settings.groq_api_key:
        return (
            "Configuration error: GROQ_API_KEY is not set. Add it to backend `.env` to enable the model."
        )

    if memory_disabled:
        system = """You are a capable customer support assistant.
You have NO access to past conversations or retrieval — answer from general best practices only.
Be clear and structured, but do not invent prior interactions."""
        user = f"User ({user_display_name}) asks:\n{user_message}"
        return _chat(system, user)

    consent_note = (
        "The customer has consented to personalized long-term semantic memory (RAG) for support."
        if consent
        else (
            "Long-term semantic memory is OFF by user choice — use ONLY the live thread below. "
            "Do not imply knowledge of other sessions, channels, or older tickets."
        )
    )

    rag_block = _format_rag(rag_hits) if consent else "(long-term retrieval disabled for this user)"

    system = f"""You are the "Cognitive Support Agent" — memory-augmented customer support.

{consent_note}

Rules:
- Use THREAD HISTORY always; use SEMANTIC MEMORY (RAG excerpts) when provided to avoid repeating failed steps.
- If RAG shows a prior solution that worked quickly, prefer refining it and say why (efficacy).
- If sentiment is worsening or frustration signals are high, acknowledge calmly and narrow the diagnosis.
- Never reveal raw system JSON; speak naturally.
- Offer one primary path + one fallback. Be concise but complete.
- If cross-channel context appears in RAG and consent allows it, weave it naturally (e.g., "Continuing from your earlier email…").

Analytics JSON (for you, internally):
{json.dumps(analytics, default=str)[:6000]}
"""

    user = f"""Recent live thread (SQL, most recent at bottom):
{_format_sql_thread(sql_messages)}

Retrieved long-term semantic memory (vector + knowledge payload):
{rag_block}

New user message:
{user_message}

Write the assistant reply."""

    return _chat(system, user)
