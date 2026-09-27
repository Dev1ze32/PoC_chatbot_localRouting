"""The generator: the ONE swappable part.

The rest of the pipeline calls make_generator().generate(system, user) and
never knows which model answered. Today: a hosted stand-in (gpt-4o-mini).
Later: the study's fine-tuned 4-bit Llama 3.2 3B, offline. Add a class with
the same generate() signature and select it with POC_GENERATOR.
"""
import time
from dataclasses import dataclass

from server import config


@dataclass
class Generation:
    text: str
    model: str
    backend: str
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class GeneratorUnavailable(RuntimeError):
    pass


class OpenAIGenerator:
    backend = "openai (hosted stand-in)"

    def __init__(self):
        if not config.OPENAI_API_KEY_PRESENT:
            raise GeneratorUnavailable(
                "OPENAI_API_KEY is not set. Put it in poc_thesis/.env "
                "(see .env.example) or export it before starting the server.")
        from openai import OpenAI
        self.client = OpenAI(timeout=config.GENERATOR_TIMEOUT_S)  # reads the key from the environment
        self.model = config.OPENAI_MODEL

    def generate(self, system, user):
        t0 = time.perf_counter()
        r = self.client.chat.completions.create(
            model=self.model,
            temperature=config.GENERATOR_TEMPERATURE,
            max_tokens=config.GENERATOR_MAX_TOKENS,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}])
        usage = getattr(r, "usage", None)
        return Generation(
            text=(r.choices[0].message.content or "").strip(),
            model=r.model or self.model,
            backend=self.backend,
            latency_ms=(time.perf_counter() - t0) * 1000,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None))


# class LocalGenerator:            # Later: the study's offline model.
#     backend = "local (4-bit Llama 3.2 3B + QLoRA)"
#     def generate(self, system, user): ...


def make_generator():
    """Returns (generator or None, reason). The server still starts without one:
    Paths B and C never call it, and Path A reports why it can't answer."""
    try:
        if config.GENERATOR_BACKEND == "openai":
            return OpenAIGenerator(), None
        return None, f"unknown POC_GENERATOR '{config.GENERATOR_BACKEND}'"
    except GeneratorUnavailable as e:
        return None, str(e)
