"""The generator: the ONE swappable part.

The rest of the pipeline calls make_generator().generate(system, user) and
never knows which model answered. Select one with POC_GENERATOR in .env:
  llama   the study's base model, 4-bit GGUF, served by llama.cpp (Colab)
  openai  gpt-4o-mini, kept as a backup
Later: the study's fine-tuned 4-bit Llama 3.2 3B, offline. llama-server speaks
the same chat API as OpenAI, so it only needs a different base URL; the
merged QLoRA model in the same GGUF format plugs into LlamaServerGenerator.
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


class LlamaServerGenerator(OpenAIGenerator):
    """llama.cpp's llama-server (OpenAI-compatible /v1/chat/completions).

    Today it runs in Google Colab behind a Cloudflare tunnel, so the URL changes
    every session: paste the new one into LLAMA_BASE_URL in .env and restart."""
    backend = "llama.cpp in Google Colab (online stand-in)"

    def __init__(self):
        if not config.LLAMA_BASE_URL:
            raise GeneratorUnavailable(
                "LLAMA_BASE_URL is not set. Run colab/llama_server.ipynb, then put the "
                "tunnel URL it prints into poc_thesis/.env and restart the server.")
        if not config.LLAMA_API_KEY_PRESENT:
            raise GeneratorUnavailable(
                "LLAMA_API_KEY is not set. Put the key the Colab notebook prints into "
                "poc_thesis/.env and restart the server.")
        import os
        from openai import OpenAI
        self.client = OpenAI(base_url=config.LLAMA_BASE_URL + "/v1",
                             api_key=os.environ["LLAMA_API_KEY"],
                             timeout=config.LLAMA_TIMEOUT_S, max_retries=0)
        self.model = config.LLAMA_MODEL

    def generate(self, system, user):
        g = super().generate(system, user)
        g.model = self.model          # llama-server echoes the alias; keep one fixed label
        return g


def make_generator():
    """Returns (generator or None, reason). The server still starts without one:
    Paths B and C never call it, and Path A reports why it can't answer."""
    makers = {"openai": OpenAIGenerator, "llama": LlamaServerGenerator}
    try:
        if config.GENERATOR_BACKEND not in makers:
            return None, f"unknown POC_GENERATOR '{config.GENERATOR_BACKEND}' (use llama or openai)"
        return makers[config.GENERATOR_BACKEND](), None
    except GeneratorUnavailable as e:
        return None, str(e)
