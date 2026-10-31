from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from .models import Usage

@dataclass
class ChatResult:
    message: dict
    usage: Usage
    latency_ms: float
    raw_usage: dict = field(default_factory=dict)

class DeepSeekClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        max_retries: int = 5,
    ):
        api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set (see .env.example)")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )
        self.max_retries = max_retries

    def chat(
        self,
        *,
        model: str,
        messages: list[dict],
        temperature: float = 0.0,
        timeout_s: int = 120,
        tools: list[dict] | None = None,
    ) -> ChatResult:
        kwargs: dict = dict(model=model, messages=messages, temperature=temperature, timeout=timeout_s)
        if tools:
            kwargs["tools"] = tools
        t0 = time.perf_counter()
        resp = self._with_retries(lambda: self.client.chat.completions.create(**kwargs))
        latency_ms = (time.perf_counter() - t0) * 1000

        u = resp.usage
        raw_usage = u.model_dump() if u else {}
        usage = Usage(
            prompt_tokens=getattr(u, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(u, "completion_tokens", 0) or 0,

            cache_hit_tokens=getattr(u, "prompt_cache_hit_tokens", 0) or 0,
            cache_miss_tokens=getattr(u, "prompt_cache_miss_tokens", 0) or 0,
            llm_calls=1,
        )
        msg = resp.choices[0].message
        return ChatResult(
            message=msg.model_dump(exclude_none=True),
            usage=usage,
            latency_ms=latency_ms,
            raw_usage=raw_usage,
        )

    def _with_retries(self, fn):
        delay = 1.0
        for attempt in range(self.max_retries):
            try:
                return fn()
            except (RateLimitError, APIConnectionError) as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay = min(delay * 2, 30)
            except APIStatusError as e:

                if e.status_code < 500 or attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay = min(delay * 2, 30)
