from __future__ import annotations

import json
from pathlib import Path

from ..config import AgentConfig
from ..deepseek_client import DeepSeekClient
from ..grader import Grader
from ..models import AgentResult, Task
from .base import build_initial_messages, load_system_prompt

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Write candidate code to the task file and run the test suite in an isolated sandbox. Returns pytest output.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Complete content of the solution file"}},
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit",
            "description": "Submit final code. Only call this after run_tests passes.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "description": "Complete content of the solution file"}},
                "required": ["code"],
            },
        },
    },
]

class ToolsAgent:
    def __init__(self, cfg: AgentConfig, config_dir: Path):
        self.cfg = cfg
        self.system_prompt = load_system_prompt(cfg, config_dir)

    def solve(self, task: Task, client: DeepSeekClient, grader: Grader) -> AgentResult:
        result = AgentResult(code=None)
        messages = build_initial_messages(self.cfg, self.system_prompt, task)
        submitted = False
        try:
            for _ in range(self.cfg.max_tool_steps):
                chat = client.chat(
                    model=self.cfg.model,
                    messages=messages,
                    temperature=self.cfg.temperature,
                    timeout_s=self.cfg.timeout_s,
                    tools=TOOLS,
                )
                result.usage.add(chat.usage)
                msg = chat.message
                messages.append(msg)
                tool_calls = msg.get("tool_calls") or []
                if not tool_calls:

                    messages.append({"role": "user", "content": "Use the run_tests tool to check your solution, then call submit."})
                    continue
                for tc in tool_calls:
                    result.tool_calls += 1
                    name = tc["function"]["name"]
                    try:
                        args = json.loads(tc["function"]["arguments"] or "{}")
                        code = args["code"]
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        result.tool_errors += 1
                        messages.append(self._tool_reply(tc, f"Invalid arguments: {e}"))
                        continue

                    grade = grader.grade(task, code)
                    if name == "run_tests":
                        verdict = "PASSED" if grade.passed else "FAILED"
                        messages.append(self._tool_reply(tc, f"{verdict}\n{grade.output[-3000:]}"))
                    elif name == "submit":
                        result.attempts += 1
                        result.code = code
                        if grade.passed:
                            submitted = True
                            messages.append(self._tool_reply(tc, "Submission accepted: all tests pass."))
                        else:
                            messages.append(self._tool_reply(tc, f"Submission REJECTED, tests fail:\n{grade.output[-3000:]}"))
                    else:
                        result.tool_errors += 1
                        messages.append(self._tool_reply(tc, f"Unknown tool: {name}"))
                if submitted:
                    break
        except Exception as e:
            result.error = f"{type(e).__name__}: {e}"
        result.messages = messages
        return result

    @staticmethod
    def _tool_reply(tc: dict, content: str) -> dict:
        return {"role": "tool", "tool_call_id": tc["id"], "content": content}
