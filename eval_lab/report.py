from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .db import DB
from .metrics import ConfigSummary, summarize

def _fmt(x: float | None, spec: str = ".3f") -> str:
    return format(x, spec) if x is not None else "—"

def summary_table(summaries: list[ConfigSummary]) -> str:
    header = (
        "| config | runs | solved | solve rate (95% CI) | $/solved | p50 ms | p95 ms "
        "| cache hit % | avg attempts | tool errors |"
    )
    sep = "|" + "---|" * 10
    rows = []
    for s in summaries:
        ci = f"[{_fmt(s.solve_rate_ci95[0], '.2f')}, {_fmt(s.solve_rate_ci95[1], '.2f')}]" if s.solve_rate_ci95 else "—"
        rows.append(
            f"| {s.config_name} | {s.n_runs} | {s.n_solved} "
            f"| {_fmt(s.solve_rate, '.1%')} {ci} "
            f"| {_fmt(s.cost_per_solved_usd, '.4f')} "
            f"| {_fmt(s.latency_p50_ms, '.0f')} | {_fmt(s.latency_p95_ms, '.0f')} "
            f"| {_fmt(s.cache_hit_rate, '.1%')} "
            f"| {s.avg_attempts:.2f} | {s.tool_errors} |"
        )
    return "\n".join([header, sep, *rows])

def make_charts(summaries: list[ConfigSummary], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    names = [s.config_name for s in summaries]
    paths: list[Path] = []

    def bar(values, title, ylabel, fname):
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(names, [v if v is not None else 0 for v in values])
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=20, ha="right")
        fig.tight_layout()
        p = out_dir / fname
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths.append(p)

    bar([s.cost_per_solved_usd for s in summaries], "Cost per solved task (USD)", "USD", "cost_per_solved.png")
    bar([s.cache_hit_rate for s in summaries], "Context cache hit rate", "hit rate", "cache_hit_rate.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    rates = [s.solve_rate or 0 for s in summaries]
    errs = [
        [(s.solve_rate or 0) - s.solve_rate_ci95[0] for s in summaries],
        [s.solve_rate_ci95[1] - (s.solve_rate or 0) for s in summaries],
    ]
    ax.bar(names, rates, yerr=errs, capsize=4)
    ax.set_title("Solve rate with 95% Wilson CI")
    ax.set_ylabel("solve rate")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    p = out_dir / "solve_rate.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    paths.append(p)
    return paths

def failure_section(db: DB, experiment_id: int, max_cases: int = 10) -> str:
    rows = db.conn.execute(
        """SELECT config_name, task_id, repeat_idx, error, test_output
           FROM runs WHERE experiment_id = ? AND (error IS NOT NULL OR solved = 0)
           ORDER BY config_name, task_id LIMIT ?""",
        (experiment_id, max_cases),
    ).fetchall()
    if not rows:
        return "_No failed runs._"
    parts = []
    for r in rows:
        parts.append(f"### {r['config_name']} / {r['task_id']} (repeat {r['repeat_idx']})")
        if r["error"]:
            parts.append(f"**Infra/agent error:** `{r['error']}`")
        tail = (r["test_output"] or "").strip()[-800:]
        if tail:
            parts.append(f"```\n{tail}\n```")
    return "\n\n".join(parts)

def generate_report(db_path: str | Path, experiment_id: int, out_dir: str | Path = "reports") -> Path:
    out_dir = Path(out_dir) / f"experiment-{experiment_id}"
    with DB(db_path) as db:
        exp = db.conn.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,)).fetchone()
        runs = db.runs_for_experiment(experiment_id)
        summaries = summarize(runs)
        charts = make_charts(summaries, out_dir)
        failures = failure_section(db, experiment_id)

    md = f"""# Experiment #{experiment_id}: {exp['name']}

Config snapshot:

```yaml
{exp['config_json']}
```

## Results

{summary_table(summaries)}

## Charts

{chr(10).join(f"![{p.stem}]({p.name})" for p in charts)}

## Failure analysis (first 10)

{failures}

## Method notes

- Solved = full pytest suite passes in an isolated Docker container (no network, 512 MB RAM).
- Cost uses the pricing table from the config snapshot; verify against current DeepSeek pricing.
- Cache hit rate is measured from `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`
  returned by the DeepSeek API — not estimated.
- Solve-rate intervals are Wilson 95% CIs; with small task sets, overlapping CIs mean
  the difference is not established.
"""
    report_path = out_dir / "report.md"
    report_path.write_text(md, encoding="utf-8")
    return report_path

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="eval_lab.db")
    ap.add_argument("--experiment", type=int, required=True)
    ap.add_argument("--out", default="reports")
    args = ap.parse_args()
    path = generate_report(args.db, args.experiment, args.out)
    print(f"Report written to {path}")

if __name__ == "__main__":
    main()
