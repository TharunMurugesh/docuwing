"""Auditable registry for the fixed execution tool set.

The planner can name only tools registered here; it never receives a general
code-execution or filesystem capability.
"""
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Tool:
    name: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    run: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class ToolRegistry:
    def __init__(self) -> None: self._tools: dict[str, Tool] = {}
    def register(self, tool: Tool) -> None:
        if tool.name in self._tools: raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool
    def get(self, name: str) -> Tool:
        if name not in self._tools: raise ValueError(f"Unregistered tool: {name}")
        return self._tools[name]
    @property
    def names(self) -> tuple[str, ...]: return tuple(self._tools)
