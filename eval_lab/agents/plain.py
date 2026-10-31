from __future__ import annotations

from pathlib import Path

from ..config import AgentConfig
from ..deepseek_client import DeepSeekClient
from ..grader import Grader
from ..models import AgentResult, Task
from .base import build_initial_messages, extract_code, load_system_prompt

class PlainAgent:
    def __init__(self, cfg: AgentConfig, config_dir: Path):
        self.cfg = cfg
        self.system_prompt = load_system_prompt(cfg, config_dir)

    def solve(self, task: Task, client: DeepSeekClient, grader: Grader) -> AgentResult:
        result = AgentResult(code=None)
        messages = build_initial_messages(self.cfg, self.system_prompt, task)
        try:
            for attempt in range(1, self.cfg.max_attempts + 1):
                result.attempts = attempt
                chat = client.chat(
                    model=self.cfg.model,
                    messages=messages,
                    temperature=self.cfg.temperature,
                    timeout_s=self.cfg.timeout_s,
                )
                result.usage.add(chat.usage)
                assistant_msg = {"role": "assistant", "content": chat.message.get("content") or ""}
                messages.append(assistant_msg)

                code = extract_code(assistant_msg["content"])
                if code is None:

                    messages.append({"role": "user", "content": "No python code block found. Reply with the complete file in one ```python block."})
                    continue

                grade = grader.grade(task, code)
                if grade.passed:
                    result.code = code
                    break
                result.code = code
                if attempt < self.cfg.max_attempts:
                    feedback = grade.output[-3000:]
                    messages.append({"role": "user", "content": f"Tests failed. Pytest output:\n\n```\n{feedback}\n```\nFix the code and reply with the complete corrected file."})
        except Exception as e:
            result.error = f"{type(e).__name__}: {e}"
        result.messages = messages
        return result
