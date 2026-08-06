"""Dependency-aware, schema-validated execution for structured plans."""
import asyncio
from dataclasses import dataclass
from typing import Any
from app.tools.registry import ToolRegistry


@dataclass
class PlanStep:
    id: str
    tool: str
    input: dict[str, Any]
    depends_on: list[str]


class ExecutionEngine:
    def __init__(self, registry: ToolRegistry): self.registry = registry
    async def execute(self, steps: list[PlanStep], notify) -> dict[str, dict]:
        pending = {step.id: step for step in steps}; outputs: dict[str, dict] = {}
        while pending:
            ready = [step for step in pending.values() if all(dep in outputs for dep in step.depends_on)]
            if not ready: raise ValueError("Plan contains unresolved dependencies")
            async def run(step: PlanStep):
                tool = self.registry.get(step.tool); await notify(step.id, "started")
                payload = {**step.input, "dependencies": {dep: outputs[dep] for dep in step.depends_on}}
                for attempt in range(3):
                    try:
                        result = await tool.run(payload)
                        if not isinstance(result, dict): raise ValueError("Tool output must be an object")
                        await notify(step.id, "completed"); return step.id, result
                    except (TimeoutError, ConnectionError):
                        if attempt == 2: raise
                        await notify(step.id, "retrying"); await asyncio.sleep(2 ** attempt)
            for step_id, result in await asyncio.gather(*(run(step) for step in ready)):
                outputs[step_id] = result; del pending[step_id]
        return outputs
