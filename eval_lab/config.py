from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

@dataclass(frozen=True)
class ModelPricing:

    input_cache_hit_per_mtok: float
    input_cache_miss_per_mtok: float
    output_per_mtok: float

    def cost(self, cache_hit: int, cache_miss: int, output: int) -> float:
        return (
            cache_hit * self.input_cache_hit_per_mtok
            + cache_miss * self.input_cache_miss_per_mtok
            + output * self.output_per_mtok
        ) / 1_000_000

@dataclass(frozen=True)
class AgentConfig:

    name: str
    model: str
    agent: Literal["plain", "tools"]
    system_prompt: str
    layout: Literal["naive", "static_first"] = "naive"
    temperature: float = 0.0
    max_attempts: int = 1
    max_tool_steps: int = 8
    timeout_s: int = 120

@dataclass(frozen=True)
class ExperimentConfig:
    experiment: str
    seed: int
    repeats: int
    pricing: dict[str, ModelPricing]
    configs: list[AgentConfig] = field(default_factory=list)

    def pricing_for(self, model: str) -> ModelPricing:
        if model not in self.pricing:
            raise KeyError(f"No pricing for model {model!r}; add it to the config file")
        return self.pricing[model]

def load_config(path: str | Path) -> ExperimentConfig:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    pricing = {k: ModelPricing(**v) for k, v in (raw.get("pricing") or {}).items()}
    configs = [AgentConfig(**c) for c in raw["configs"]]
    names = [c.name for c in configs]
    if len(names) != len(set(names)):
        raise ValueError(f"Duplicate config names: {names}")
    return ExperimentConfig(
        experiment=raw.get("experiment", path.stem),
        seed=int(raw.get("seed", 42)),
        repeats=int(raw.get("repeats", 1)),
        pricing=pricing,
        configs=configs,
    )
