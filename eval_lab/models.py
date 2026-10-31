from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class Task:

    task_id: str
    path: Path
    statement: str
    entry_file: str
    tests_dir: Path

    @staticmethod
    def load(task_dir: str | Path) -> "Task":
        import yaml

        task_dir = Path(task_dir)
        meta = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
        statement = (task_dir / "statement.md").read_text(encoding="utf-8")
        return Task(
            task_id=meta["id"],
            path=task_dir,
            statement=statement,
            entry_file=meta.get("entry_file", "solution.py"),
            tests_dir=task_dir / "tests",
        )

@dataclass
class Usage:

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    llm_calls: int = 0

    def add(self, other: "Usage") -> None:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.cache_hit_tokens += other.cache_hit_tokens
        self.cache_miss_tokens += other.cache_miss_tokens
        self.llm_calls += other.llm_calls

    @property
    def cache_hit_rate(self) -> float | None:
        total = self.cache_hit_tokens + self.cache_miss_tokens
        return self.cache_hit_tokens / total if total else None

@dataclass
class AgentResult:

    code: str | None
    messages: list[dict] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    attempts: int = 0
    tool_calls: int = 0
    tool_errors: int = 0
    error: str | None = None
