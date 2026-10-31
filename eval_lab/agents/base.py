from __future__ import annotations

import re
from pathlib import Path

from ..config import AgentConfig
from ..models import Task

_CODE_FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)

def load_system_prompt(cfg: AgentConfig, config_dir: Path) -> str:
    return (config_dir / cfg.system_prompt).read_text(encoding="utf-8").strip()

def extract_code(text: str) -> str | None:
    blocks = _CODE_FENCE.findall(text or "")
    if blocks:
        return blocks[-1].strip() + "\n"
    stripped = (text or "").strip()
    if stripped.startswith(("def ", "import ", "from ", "class ")):
        return stripped + "\n"
    return None

def build_initial_messages(cfg: AgentConfig, system_prompt: str, task: Task) -> list[dict]:
    if cfg.layout == "static_first":
        system = f"{system_prompt}\n\n# Task\n\n{task.statement}\n\n# Required file: {task.entry_file}"
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": "Solve the task described above. Respond with the complete file in one python code block."},
        ]

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"# Task\n\n{task.statement}\n\n# Required file: {task.entry_file}\n\nRespond with the complete file in one python code block."},
    ]
