#!/usr/bin/env bash
# Start the PoC (WSL). Then open http://127.0.0.1:8000 in a Windows browser.
# Needs poc_thesis/.env with OPENAI_API_KEY=... (copy .env.example). Without it,
# the site still runs: referral and out-of-scope work, cited answers say why they can't.
cd "$(dirname "$0")"
PY="${PY:-../ai_context/venv/bin/python}"          # the old environment, for now
if [ -d "$HOME/.cache/huggingface/hub/models--BAAI--bge-small-en-v1.5" ]; then
  export HF_HUB_OFFLINE=1                          # embedding model is cached: don't touch the network
fi
exec "$PY" -m server.api
