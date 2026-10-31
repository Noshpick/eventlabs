import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval_lab.config import load_config
from eval_lab.db import DB
from eval_lab.metrics import summarize, wilson_ci
from eval_lab.models import Task, Usage
from eval_lab.runner import discover_tasks
from eval_lab.agents.base import extract_code

cfg = load_config("configs/example.yaml")
assert [c.name for c in cfg.configs] == ["plain-naive", "plain-cache-optimized", "tools-agent"]
cost = cfg.pricing_for("deepseek-chat").cost(cache_hit=1_000_000, cache_miss=1_000_000, output=1_000_000)
assert abs(cost - (0.07 + 0.27 + 1.10)) < 1e-9, cost
print(f"config OK ({len(cfg.configs)} configs, sample cost ${cost:.2f})")

tasks = discover_tasks("tasks")
by_id = {t.task_id: t for t in tasks}
assert {"two_sum", "is_palindrome", "fizzbuzz_sum"} <= set(by_id)
assert all(t.tests_dir.exists() for t in tasks)
print(f"tasks OK: {len(tasks)} tasks discovered")

import subprocess
refs = {
    "two_sum": "def two_sum(nums, target):\n    seen = {}\n    for j, x in enumerate(nums):\n        if target - x in seen:\n            return (seen[target - x], j)\n        seen[x] = j\n",
    "is_palindrome": "def is_palindrome(s):\n    f = [c.lower() for c in s if c.isalnum()]\n    return f == f[::-1]\n",
    "fizzbuzz_sum": "def fizzbuzz_sum(n):\n    s = lambda k, d: d * (k // d) * (k // d + 1) // 2\n    return s(n, 3) + s(n, 5) - s(n, 15)\n",
}
for tid, ref in refs.items():
    t = by_id[tid]
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "solution.py").write_text(ref)
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(t.tests_dir.resolve()),
                            "--rootdir", tmp, "-p", "no:cacheprovider", "--import-mode=importlib"],
                           cwd=tmp, capture_output=True, text=True)
        assert r.returncode == 0, f"{t.task_id}: {r.stdout[-500:]}"
print("reference solutions pass all example tests")

with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
    db_path = f.name
with DB(db_path) as db:
    exp_id = db.create_experiment("smoke", "{}", seed=42)
    rid = db.insert_run(exp_id, config_name="a", model="deepseek-chat", task_id="t1",
                        repeat_idx=0, latency_ms=100.0, solved=1, attempts=1, llm_calls=1,
                        prompt_tokens=1000, completion_tokens=200,
                        cache_hit_tokens=800, cache_miss_tokens=200, cost_usd=0.001,
                        tool_calls=0, tool_errors=0, error=None, test_output="ok")
    db.insert_messages(rid, [{"role": "system", "content": "s"}, {"role": "assistant", "content": None}])
    db.insert_run(exp_id, config_name="a", model="deepseek-chat", task_id="t2",
                  repeat_idx=0, latency_ms=300.0, solved=0, attempts=3, llm_calls=3,
                  prompt_tokens=3000, completion_tokens=600,
                  cache_hit_tokens=0, cache_miss_tokens=3000, cost_usd=0.002,
                  tool_calls=0, tool_errors=0, error=None, test_output="fail")
    runs = db.runs_for_experiment(exp_id)
    s = summarize(runs)[0]
    assert s.n_runs == 2 and s.n_solved == 1 and s.solve_rate == 0.5
    assert abs(s.cost_per_solved_usd - 0.003) < 1e-12
    assert abs(s.cache_hit_rate - 800 / 4000) < 1e-12
    assert s.latency_p50_ms is not None and s.solve_rate_ci95[0] < 0.5 < s.solve_rate_ci95[1]
print("DB + metrics OK (solve rate 50%, $/solved 0.003, cache hit 20%)")

assert extract_code("here:\n```python\nprint(1)\n```").startswith("print")
assert extract_code("no code at all") is None
assert extract_code("def f():\n    pass").startswith("def f")
lo, hi = wilson_ci(5, 30)
assert 0 < lo < 5 / 30 < hi < 1
print("helpers OK")

print("\nALL SMOKE TESTS PASSED")
