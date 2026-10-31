from __future__ import annotations

import math
import sqlite3
import statistics
from dataclasses import dataclass

@dataclass
class ConfigSummary:
    config_name: str
    n_runs: int
    n_solved: int
    n_infra_errors: int
    solve_rate: float | None
    solve_rate_ci95: tuple[float, float] | None
    cost_total_usd: float
    cost_per_solved_usd: float | None
    latency_p50_ms: float | None
    latency_p95_ms: float | None
    tokens_prompt: int
    tokens_completion: int
    cache_hit_rate: float | None
    avg_attempts: float
    avg_llm_calls: float
    tool_calls: int
    tool_errors: int

def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    k = (len(xs) - 1) * pct / 100
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

def summarize(runs: list[sqlite3.Row]) -> list[ConfigSummary]:
    by_config: dict[str, list[sqlite3.Row]] = {}
    for r in runs:
        by_config.setdefault(r["config_name"], []).append(r)

    summaries: list[ConfigSummary] = []
    for name, rs in sorted(by_config.items()):
        infra = [r for r in rs if r["error"]]
        valid = [r for r in rs if not r["error"]]
        solved = [r for r in valid if r["solved"]]
        n = len(valid)
        k = len(solved)
        cost_total = sum(r["cost_usd"] for r in rs)
        lat = [r["latency_ms"] for r in valid if r["latency_ms"] is not None]
        hit = sum(r["cache_hit_tokens"] for r in rs)
        miss = sum(r["cache_miss_tokens"] for r in rs)
        summaries.append(
            ConfigSummary(
                config_name=name,
                n_runs=len(rs),
                n_solved=k,
                n_infra_errors=len(infra),
                solve_rate=(k / n) if n else None,
                solve_rate_ci95=wilson_ci(k, n) if n else None,
                cost_total_usd=cost_total,
                cost_per_solved_usd=(cost_total / k) if k else None,
                latency_p50_ms=percentile(lat, 50),
                latency_p95_ms=percentile(lat, 95),
                tokens_prompt=sum(r["prompt_tokens"] for r in rs),
                tokens_completion=sum(r["completion_tokens"] for r in rs),
                cache_hit_rate=(hit / (hit + miss)) if (hit + miss) else None,
                avg_attempts=statistics.mean(r["attempts"] for r in rs) if rs else 0.0,
                avg_llm_calls=statistics.mean(r["llm_calls"] for r in rs) if rs else 0.0,
                tool_calls=sum(r["tool_calls"] for r in rs),
                tool_errors=sum(r["tool_errors"] for r in rs),
            )
        )
    return summaries
