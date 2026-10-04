import logging
import os
from typing import Any

import requests

from apps.chat.domain.entities import ChatMessage, ChatTurnResult
from apps.chat.domain.interfaces import ILLMChatService
from .ollama_chat_service import parse_tool_calls
from .prompts import build_system_prompt
from .tools import VISUALIZATION_TOOLS

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL_NAME = "llama-3.3-70b-versatile"

logger = logging.getLogger(__name__)


class GroqChatService(ILLMChatService):
    """Calls Groq's hosted API. Takes a model_name so multiple Groq models
    can be registered as separate fallback options (see model_registry.py)
    without needing a whole new service class per model.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name

    def get_response(
        self,
        history: list[ChatMessage],
        current_config: dict[str, Any],
        data_schema: dict[str, Any],
    ) -> ChatTurnResult:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set.")

        system_prompt = build_system_prompt(current_config, data_schema)
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": m.role, "content": m.content} for m in history
        ]

        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model_name,
                "messages": messages,
                "tools": VISUALIZATION_TOOLS,
                "temperature": 0.2,
            },
            timeout=60,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error("Groq API error %s: %s", response.status_code, response.text)
            raise

        data = response.json()
        message = data["choices"][0]["message"]

        tool_calls = message.get("tool_calls") or []
        reply_text = message.get("content") or ""

        if not tool_calls:
            return ChatTurnResult(reply_text=reply_text)

        viz_commands, stat_command = parse_tool_calls(tool_calls)

        if not reply_text:
            reply_text = "Calculating..." if stat_command else "Updating the visualization..." if viz_commands else ""

        return ChatTurnResult(reply_text=reply_text, commands=viz_commands, stat_command=stat_command)