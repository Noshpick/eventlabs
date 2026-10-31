# DeepSeek Agent Evaluation Lab

**[Читать на русском](README.ru.md)**

A small open-source platform that measures how effectively DeepSeek solves programming tasks - and looks for ways to cut the cost of a *solved task* without losing quality.

## What it measures

| Metric | Source                                                                                                      |
|---|-------------------------------------------------------------------------------------------------------------|
| Solve rate (+ Wilson 95% CI) | pytest in an isolated Docker container                                                                      |
| **Cost per solved task** | total spend / tasks solved                                                                                  |
| p50 / p95 latency | wall time of a full run                                                                                     |
| Tokens, retries, tool errors | API usage fields + message traces                                                                           |
| Context cache efficiency | `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens` returned by the DeepSeek API - measured, not assumed |

## What gets compared

- `layout: naive` vs `layout: static_first` - all immutable content (instructions, task statement) packed into the shared message prefix, per-attempt feedback only appended at the end → higher cache hit rate, cheaper retries.
- `agent: plain` vs `agent: tools` - single-shot code generation vs an agent with `run_tests` / `submit` tool calling.
- Model, temperature, max attempts - plain config fields.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # put your DEEPSEEK_API_KEY there
docker build -t eval-lab-sandbox -f Dockerfile.sandbox .

python3 scripts/run_benchmark.py --config configs/example.yaml

uvicorn web.app:app --port 8000   # dashboard
```

One command runs the full benchmark and writes a reproducible report (markdown + charts + failure analysis) to `reports/experiment-N/`. An offline smoke test that needs neither an API key nor Docker: `python scripts/smoke_test.py`.

## Project layout

```
eval_lab/
  config.py            experiment config + pricing
  deepseek_client.py   OpenAI-compatible client, cache-token accounting, retries
  agents/              plain agent (code + feedback) and tools agent (function calling)
  sandbox.py           docker run: no network, 512 MB RAM, 1 CPU, read-only root FS
  grader.py            pytest run; solved = the whole suite passes
  metrics.py           $/solved, p50/p95, cache hit rate, Wilson CI
  runner.py            configs × tasks × repeats → SQLite
  report.py            reproducible report with charts
web/app.py             FastAPI: experiments, config comparison, traces
tasks/                 task format: task.yaml + statement.md + tests/
configs/               experiment configurations
scripts/               run_benchmark.py, smoke_test.py
```

## Adding a task

```
tasks/<id>/task.yaml      id, entry_file
tasks/<id>/statement.md   the statement shown to the model
tasks/<id>/tests/         pytest tests (hidden from the model)
```

The repo ships 33 tasks (arrays, strings, DP, graphs, data-structure design). Every task is covered by a reference solution - `python scripts/validate_tasks.py` re-runs all test suites against them, which is the quality gate when authoring new tasks.

## Honest caveats

- With 20–30 tasks the solve rate is noisy: compare configs with CIs in mind and use `repeats >= 3`.
- Prices in `configs/example.yaml` are placeholders - verify against current DeepSeek pricing (https://api-docs.deepseek.com/quick_start/pricing) before publishing any numbers.
- The sandbox protects against accidental damage, not a determined escape attempt.
