from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

IMAGE = "eval-lab-sandbox"

@dataclass
class SandboxResult:
    exit_code: int
    output: str
    timed_out: bool = False

def build_image(dockerfile: str | Path = "Dockerfile.sandbox") -> None:
    subprocess.run(
        ["docker", "build", "-t", IMAGE, "-f", str(dockerfile), "."],
        check=True,
    )

def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    r = subprocess.run(["docker", "info"], capture_output=True)
    return r.returncode == 0

def image_exists() -> bool:
    if shutil.which("docker") is None:
        return False
    r = subprocess.run(
        ["docker", "image", "inspect", IMAGE],
        capture_output=True,
    )
    return r.returncode == 0

def run_pytest(entry_file: str, code: str, tests_dir: Path, timeout_s: int = 60) -> SandboxResult:
    workdir = Path(tempfile.mkdtemp(prefix="eval-lab-"))
    try:
        (workdir / entry_file).write_text(code, encoding="utf-8")
        dest_tests = workdir / "tests"
        shutil.copytree(tests_dir, dest_tests)
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1.0",
            "--pids-limit", "128",
            "--read-only",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "-v", f"{workdir}:/work",
            IMAGE,
            "python", "-m", "pytest", "-q", "tests", "--tb=short", "-p", "no:cacheprovider",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
            return SandboxResult(exit_code=proc.returncode, output=proc.stdout + proc.stderr)
        except subprocess.TimeoutExpired:
            return SandboxResult(exit_code=-1, output=f"Timed out after {timeout_s}s", timed_out=True)
        except FileNotFoundError:
            return SandboxResult(exit_code=-2, output="docker CLI not found")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
