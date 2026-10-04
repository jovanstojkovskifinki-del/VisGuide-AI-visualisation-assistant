import json
from typing import Any

import requests

from apps.chat.domain.entities import (
    ChatMessage,
    ChatTurnResult,
    CommandType,
    StatType,
    StatisticCommand,
    VisualizationCommand,
)
from apps.chat.domain.interfaces import ILLMChatService
from .prompts import build_system_prompt
from .tools import VISUALIZATION_TOOLS

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:latest"


def normalize_columns(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    if isinstance(raw, str):
        s = raw.strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(c).strip() for c in parsed if str(c).strip()]
        except (json.JSONDecodeError, TypeError):
            pass
        s = s.strip("[]")
        return [c.strip().strip("'\"") for c in s.split(",") if c.strip()]
    return []


def parse_tool_calls(tool_calls):
    """Returns (list[VisualizationCommand], StatisticCommand | None).

    Multiple visualization tool calls in the same turn (e.g.
    change_chart_type + set_axes together) are all kept, in order, and
    applied in sequence by the use case - not silently overwritten.
    """
    viz_commands: list[VisualizationCommand] = []
    stat_command = None

    for call in tool_calls:
        fn = call["function"]
        name = fn["name"]
        raw_args = fn["arguments"]
        args = raw_args if isinstance(raw_args, dict) else json.loads(raw_args)

        if name == "compute_statistic":
            try:
                stat_type = StatType(args["stat_type"])
            except (KeyError, ValueError):
                continue
            columns = normalize_columns(args.get("columns"))
            if not columns:
                continue
            stat_command = StatisticCommand(
                stat_type=stat_type, columns=columns, value=args.get("value")
            )
            continue

        try:
            command_type = CommandType(name)
        except ValueError:
            continue

        viz_commands.append(VisualizationCommand(command_type=command_type, params=args))

    return viz_commands, stat_command


class OllamaChatService(ILLMChatService):
    def get_response(
        self,
        history: list[ChatMessage],
        current_config: dict[str, Any],
        data_schema: dict[str, Any],
    ) -> ChatTurnResult:
        system_prompt = build_system_prompt(current_config, data_schema)
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": m.role, "content": m.content} for m in history
        ]

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "tools": VISUALIZATION_TOOLS,
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        message = data["message"]

        tool_calls = message.get("tool_calls") or []
        reply_text = message.get("content", "")

        if not tool_calls:
            return ChatTurnResult(reply_text=reply_text)

        viz_commands, stat_command = parse_tool_calls(tool_calls)

        if not reply_text:
            reply_text = "Calculating..." if stat_command else "Updating the visualization..." if viz_commands else ""

        return ChatTurnResult(reply_text=reply_text, commands=viz_commands, stat_command=stat_command)