from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    config_json TEXT NOT NULL,
    seed        INTEGER NOT NULL,
    created_at  REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id     INTEGER NOT NULL REFERENCES experiments(id),
    config_name       TEXT NOT NULL,
    model             TEXT NOT NULL,
    task_id           TEXT NOT NULL,
    repeat_idx        INTEGER NOT NULL,
    started_at        REAL NOT NULL,
    latency_ms        REAL,               -- wall time of the whole run
    solved            INTEGER,            -- 1/0, NULL if infra error
    attempts          INTEGER NOT NULL DEFAULT 0,
    llm_calls         INTEGER NOT NULL DEFAULT 0,
    prompt_tokens     INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    cache_hit_tokens  INTEGER NOT NULL DEFAULT 0,
    cache_miss_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd          REAL NOT NULL DEFAULT 0,
    tool_calls        INTEGER NOT NULL DEFAULT 0,
    tool_errors       INTEGER NOT NULL DEFAULT 0,
    error             TEXT,               -- infra/agent failure
    test_output       TEXT                -- tail of pytest output for failure analysis
);
CREATE INDEX IF NOT EXISTS idx_runs_exp ON runs(experiment_id, config_name, task_id);
CREATE TABLE IF NOT EXISTS messages (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id  INTEGER NOT NULL REFERENCES runs(id),
    seq     INTEGER NOT NULL,
    role    TEXT NOT NULL,
    content TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_run ON messages(run_id, seq);
"""

class DB:
    def __init__(self, path: str | Path):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "DB":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def create_experiment(self, name: str, config_json: str, seed: int) -> int:
        cur = self.conn.execute(
            "INSERT INTO experiments (name, config_json, seed, created_at) VALUES (?,?,?,?)",
            (name, config_json, seed, time.time()),
        )
        self.conn.commit()
        return cur.lastrowid

    def insert_run(self, experiment_id: int, **fields) -> int:
        fields.setdefault("started_at", time.time())
        cols = ", ".join(["experiment_id", *fields])
        marks = ", ".join("?" for _ in fields) + ", ?"
        cur = self.conn.execute(
            f"INSERT INTO runs ({cols}) VALUES ({marks})",
            (experiment_id, *fields.values()),
        )
        self.conn.commit()
        return cur.lastrowid

    def insert_messages(self, run_id: int, messages: list[dict]) -> None:
        self.conn.executemany(
            "INSERT INTO messages (run_id, seq, role, content) VALUES (?,?,?,?)",
            [
                (run_id, i, m.get("role", "?"), _as_text(m.get("content")))
                for i, m in enumerate(messages)
            ],
        )
        self.conn.commit()

    def runs_for_experiment(self, experiment_id: int) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM runs WHERE experiment_id = ? ORDER BY config_name, task_id, repeat_idx",
            (experiment_id,),
        ).fetchall()

def _as_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False)
