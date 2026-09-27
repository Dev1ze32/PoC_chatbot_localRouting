"""The web server. One page, two endpoints, localhost only.

    python -m server.api            (from poc_thesis/)
    -> open http://127.0.0.1:8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server import config
from server.route import Router

app = FastAPI(title="UC-PnC Student Helpdesk — routing PoC")
router = Router()        # loads the corpus, BM25, the embedding model: a few seconds


class Ask(BaseModel):
    question: str


@app.get("/api/health")
def health():
    return {"ok": True,
            "passages": len(router.retriever.passages),
            "generator": {"available": router.generator is not None,
                          "backend": getattr(router.generator, "backend", None),
                          "model": config.OPENAI_MODEL if router.generator else None,
                          "problem": router.generator_problem},
            "thresholds": router._thresholds()}


@app.post("/api/ask")
def ask(body: Ask):
    q = body.question.strip()
    if not q:
        raise HTTPException(400, "Empty question.")
    if len(q) > config.MAX_QUESTION_CHARS:
        raise HTTPException(400, f"Please keep questions under {config.MAX_QUESTION_CHARS} characters.")
    return router.ask(q)


app.mount("/", StaticFiles(directory=config.WEB, html=True), name="web")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
