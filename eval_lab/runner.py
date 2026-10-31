from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from .agents.plain import PlainAgent
from .agents.tools_agent import ToolsAgent
from .config import AgentConfig, ExperimentConfig
from .db import DB
from .deepseek_client import DeepSeekClient
from .grader import Grader
from .models import AgentResult, Task

log = logging.getLogger("eval_lab.runner")

def make_agent(cfg: AgentConfig, config_dir: Path):
    if cfg.agent == "plain":
        return PlainAgent(cfg, config_dir)
    if cfg.agent == "tools":
        return ToolsAgent(cfg, config_dir)
    raise ValueError(f"Unknown agent type: {cfg.agent}")

class Runner:
    def __init__(
        self,
        exp_cfg: ExperimentConfig,
        config_path: Path,
        db: DB,
        client: DeepSeekClient | None = None,
        grader: Grader | None = None,
    ):
        self.exp_cfg = exp_cfg
        self.config_path = config_path
        self.db = db
        self.client = client or DeepSeekClient()
        self.grader = grader or Grader()

    def run(self, tasks: list[Task], experiment_name: str | None = None) -> int:
        exp_id = self.db.create_experiment(
            name=experiment_name or self.exp_cfg.experiment,
            config_json=self.config_path.read_text(encoding="utf-8"),
            seed=self.exp_cfg.seed,
        )
        log.info("experiment #%s: %s (%d configs × %d tasks × %d repeats)",
                 exp_id, self.exp_cfg.experiment, len(self.exp_cfg.configs),
                 len(tasks), self.exp_cfg.repeats)
        for cfg in self.exp_cfg.configs:
            agent = make_agent(cfg, self.config_path.parent)
            for task in tasks:
                for repeat in range(self.exp_cfg.repeats):
                    self._run_one(exp_id, cfg, agent, task, repeat)
        return exp_id

    def _run_one(self, exp_id: int, cfg: AgentConfig, agent, task: Task, repeat: int) -> None:
        log.info("[%s] %s repeat=%d ...", cfg.name, task.task_id, repeat)
        t0 = time.perf_counter()
        result: AgentResult = agent.solve(task, self.client, self.grader)
        latency_ms = (time.perf_counter() - t0) * 1000

        solved = None
        test_output = None
        if result.error is None:
            if result.code is not None:
                grade = self.grader.grade(task, result.code)
                solved = int(grade.passed)
                test_output = grade.output[-4000:]
            else:
                solved = 0

        pricing = self.exp_cfg.pricing_for(cfg.model)
        cost = pricing.cost(
            result.usage.cache_hit_tokens,
            result.usage.cache_miss_tokens,
            result.usage.completion_tokens,
        )
        run_id = self.db.insert_run(
            exp_id,
            config_name=cfg.name,
            model=cfg.model,
            task_id=task.task_id,
            repeat_idx=repeat,
            latency_ms=latency_ms,
            solved=solved,
            attempts=result.attempts,
            llm_calls=result.usage.llm_calls,
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            cache_hit_tokens=result.usage.cache_hit_tokens,
            cache_miss_tokens=result.usage.cache_miss_tokens,
            cost_usd=cost,
            tool_calls=result.tool_calls,
            tool_errors=result.tool_errors,
            error=result.error,
            test_output=test_output,
        )
        self.db.insert_messages(run_id, result.messages)
        log.info("[%s] %s -> solved=%s cost=$%.4f err=%s",
                 cfg.name, task.task_id, solved, cost, result.error)

def discover_tasks(tasks_dir: str | Path, only: list[str] | None = None) -> list[Task]:
    tasks = []
    for d in sorted(Path(tasks_dir).iterdir()):
        if d.is_dir() and (d / "task.yaml").exists():
            if only and d.name not in only:
                continue
            tasks.append(Task.load(d))
    if not tasks:
        raise FileNotFoundError(f"No tasks found in {tasks_dir}")
    return tasks
