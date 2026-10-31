#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from eval_lab.config import load_config
from eval_lab.db import DB
from eval_lab.report import generate_report
from eval_lab.runner import Runner, discover_tasks
from eval_lab.sandbox import docker_available, image_exists

DOCKER_HELP = """\
Docker CLI not found. Install one of:
  - Docker Desktop:  brew install --cask docker
  - Colima:          brew install colima docker && colima start
  - OrbStack:        brew install --cask orbstack
Then re-run this command."""

def main() -> None:
    ap = argparse.ArgumentParser(description="Run the DeepSeek agent benchmark")
    ap.add_argument("--config", required=True, help="experiment config YAML")
    ap.add_argument("--tasks-dir", default="tasks")
    ap.add_argument("--tasks", nargs="*", help="only these task ids")
    ap.add_argument("--repeats", type=int, help="override config repeats")
    ap.add_argument("--experiment", help="override experiment name")
    ap.add_argument("--db", default="eval_lab.db")
    ap.add_argument("--skip-image-check", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    load_dotenv()

    config_path = Path(args.config)
    exp_cfg = load_config(config_path)
    if args.repeats:
        from dataclasses import replace
        exp_cfg = replace(exp_cfg, repeats=args.repeats)

    if not args.skip_image_check:
        if not docker_available():
            sys.exit(DOCKER_HELP)
        if not image_exists():
            sys.exit("Sandbox image missing. Run: docker build -t eval-lab-sandbox -f Dockerfile.sandbox .")

    tasks = discover_tasks(args.tasks_dir, only=args.tasks)
    with DB(args.db) as db:
        exp_id = Runner(exp_cfg, config_path, db).run(tasks, experiment_name=args.experiment)
    report = generate_report(args.db, exp_id)
    print(f"\nDone. Experiment #{exp_id}")
    print(f"Report: {report}")
    print(f"Dashboard: uvicorn web.app:app --port 8000  (EVAL_LAB_DB={args.db})")

if __name__ == "__main__":
    main()
