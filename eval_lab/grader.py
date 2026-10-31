from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import Task
from .sandbox import run_pytest

@dataclass
class GradeResult:
    passed: bool
    output: str

class Grader:
    def __init__(self, timeout_s: int = 60):
        self.timeout_s = timeout_s

    def grade(self, task: Task, code: str) -> GradeResult:
        r = run_pytest(task.entry_file, code, task.tests_dir, timeout_s=self.timeout_s)

        return GradeResult(passed=(r.exit_code == 0), output=r.output)
