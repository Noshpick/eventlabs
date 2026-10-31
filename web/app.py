from __future__ import annotations

import os
import sys
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval_lab.db import DB
from eval_lab.metrics import summarize

DB_PATH = os.environ.get("EVAL_LAB_DB", "eval_lab.db")

app = FastAPI(title="DeepSeek Agent Evaluation Lab")

def get_db() -> DB:
    return DB(DB_PATH)

@app.get("/api/experiments")
def list_experiments():
    with get_db() as db:
        rows = db.conn.execute(
            """SELECT e.*, COUNT(r.id) AS n_runs
               FROM experiments e LEFT JOIN runs r ON r.experiment_id = e.id
               GROUP BY e.id ORDER BY e.id DESC"""
        ).fetchall()
        return [dict(r) for r in rows]

@app.get("/api/experiments/{exp_id}/summary")
def experiment_summary(exp_id: int):
    with get_db() as db:
        runs = db.runs_for_experiment(exp_id)
        if not runs:
            raise HTTPException(404, "experiment not found or has no runs")
        return [asdict(s) for s in summarize(runs)]

@app.get("/api/experiments/{exp_id}/runs")
def experiment_runs(exp_id: int, config: str | None = Query(None), task: str | None = Query(None)):
    with get_db() as db:
        q = "SELECT * FROM runs WHERE experiment_id = ?"
        params: list = [exp_id]
        if config:
            q += " AND config_name = ?"
            params.append(config)
        if task:
            q += " AND task_id = ?"
            params.append(task)
        rows = db.conn.execute(q + " ORDER BY config_name, task_id, repeat_idx", params).fetchall()
        return [dict(r) for r in rows]

@app.get("/api/runs/{run_id}/trace")
def run_trace(run_id: int):
    with get_db() as db:
        rows = db.conn.execute(
            "SELECT seq, role, content FROM messages WHERE run_id = ? ORDER BY seq", (run_id,)
        ).fetchall()
        if not rows:
            raise HTTPException(404, "no trace for this run")
        return [dict(r) for r in rows]

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")
