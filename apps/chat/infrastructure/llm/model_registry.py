import time
from dataclasses import dataclass
from typing import Callable

from apps.chat.domain.interfaces import ILLMChatService
from .groq_chat_service import GroqChatService
from .ollama_chat_service import OllamaChatService

COOLDOWN_SECONDS = 60
CONNECTION_ERROR_COOLDOWN_SECONDS = 20


@dataclass
class ModelSpec:
    id: str
    display_name: str
    factory: Callable[[], ILLMChatService]


# NOTE (Aug 2026): Groq deprecated llama-3.3-70b-versatile and
# llama-3.1-8b-instant (shut down Aug 16, 2026). Their official migration
# guidance points to openai/gpt-oss-120b and openai/gpt-oss-20b, which both
# support tool/function calling. If Groq deprecates these too, check
# https://console.groq.com/docs/deprecations for current replacements.
MODEL_REGISTRY: list[ModelSpec] = [
    ModelSpec(
        id="groq-120b",
        display_name="Groq · GPT-OSS 120B",
        factory=lambda: GroqChatService("openai/gpt-oss-120b"),
    ),
    ModelSpec(
        id="groq-20b",
        display_name="Groq · GPT-OSS 20B (fallback)",
        factory=lambda: GroqChatService("openai/gpt-oss-20b"),
    ),
    ModelSpec(
        id="ollama-local",
        display_name="Local Ollama · llama3.1",
        factory=lambda: OllamaChatService(),
    ),
]

_cooldowns: dict[str, float] = {}


def is_available(model_id: str) -> bool:
    until = _cooldowns.get(model_id)
    return until is None or time.time() >= until


def mark_exhausted(model_id: str, cooldown_seconds: int = COOLDOWN_SECONDS) -> None:
    _cooldowns[model_id] = time.time() + cooldown_seconds


def mark_available(model_id: str) -> None:
    _cooldowns.pop(model_id, None)


def get_model_status() -> list[dict]:
    now = time.time()
    status = []
    for spec in MODEL_REGISTRY:
        until = _cooldowns.get(spec.id)
        if until is None or now >= until:
            status.append(
                {"id": spec.id, "name": spec.display_name, "status": "available", "retry_in_seconds": 0}
            )
        else:
            status.append(
                {
                    "id": spec.id,
                    "name": spec.display_name,
                    "status": "cooling_down",
                    "retry_in_seconds": int(until - now),
                }
            )
    return status