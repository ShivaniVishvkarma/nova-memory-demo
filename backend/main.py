"""
Nova — a support agent demo showing memory-on vs memory-off.

Two chat endpoints hit the SAME underlying LLM:
  POST /chat/memory     -> goes through Cognee (remember/recall), session-scoped
                            by customer_id so it survives a hard page refresh.
  POST /chat/no-memory  -> talks to the LLM directly, no storage at all.
                            This is the "wakes up on the roof" panel.

GET  /graph             -> renders Cognee's knowledge graph to HTML so the
                            frontend can iframe it live during the demo.
POST /reset              -> wipes Cognee's memory between demo runs.

NOTE ON API STABILITY: Cognee ships two overlapping APIs — the low-level
`add()/cognify()/search()` pipeline and the newer high-level
`remember()/recall()` API used here. Cognee iterates fast; if a call below
doesn't match your installed version, check https://docs.cognee.ai — the
shape of `visualize_graph` in particular has moved around across releases.
"""

import os
import tempfile
from pathlib import Path

import cognee
from cognee.api.v1.visualize.visualize import visualize_graph
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Nova memory demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHAT_PROVIDER = os.getenv("CHAT_PROVIDER", "anthropic")
NOVA_SYSTEM_PROMPT = (
    "You are Nova, a warm and efficient customer support agent. "
    "Keep replies to 2-3 sentences. If you are given remembered context "
    "about this customer, actually use it — don't ask them to repeat "
    "things you already know."
)


# ---------------------------------------------------------------------------
# LLM call — swap this for whichever provider you want. Kept provider-agnostic
# on purpose so the memory logic isn't tangled up with a specific SDK.
# ---------------------------------------------------------------------------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


async def call_llm(system_prompt: str, user_message: str) -> str:
    if CHAT_PROVIDER == "ollama":
        import httpx

        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
    elif CHAT_PROVIDER == "anthropic":
        import anthropic

        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return resp.content[0].text
    elif CHAT_PROVIDER == "openai":
        from openai import OpenAI

        client = OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=300,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return resp.choices[0].message.content
    else:
        raise ValueError(f"Unknown CHAT_PROVIDER: {CHAT_PROVIDER}")


class ChatRequest(BaseModel):
    customer_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    remembered_context: list[str] = []


@app.post("/chat/no-memory", response_model=ChatResponse)
async def chat_no_memory(req: ChatRequest):
    """The 'wakes up on the roof' baseline — zero persistence, ever."""
    reply = await call_llm(NOVA_SYSTEM_PROMPT, req.message)
    return ChatResponse(reply=reply, remembered_context=[])


@app.post("/chat/memory", response_model=ChatResponse)
async def chat_memory(req: ChatRequest):
    """
    session_id = customer_id, reused across every 'session' in the demo.
    remember() with a session_id writes to a fast session cache that syncs
    into the permanent graph in the background, so it survives refreshes.
    """
    session_id = req.customer_id

    # 1. Pull whatever Cognee already knows about this customer.
    recalled = await cognee.recall(req.message, session_id=session_id)
    context_snippets = [str(r) for r in recalled][:5]

    # 2. Build a grounded prompt.
    if context_snippets:
        context_block = "\n".join(f"- {c}" for c in context_snippets)
        prompt = (
            f"Remembered context about this customer:\n{context_block}\n\n"
            f"Customer just said: {req.message}"
        )
    else:
        prompt = f"Customer just said: {req.message}"

    reply = await call_llm(NOVA_SYSTEM_PROMPT, prompt)

    # 3. Write both sides of the exchange back into memory.
    await cognee.remember(f"Customer said: {req.message}", session_id=session_id)
    await cognee.remember(f"Nova replied: {reply}", session_id=session_id)

    return ChatResponse(reply=reply, remembered_context=context_snippets)


@app.get("/graph", response_class=HTMLResponse)
async def graph():
    """Renders the current knowledge graph as HTML for the frontend to iframe."""
    out_path = Path(tempfile.gettempdir()) / "nova_graph.html"
    await visualize_graph(str(out_path))
    return out_path.read_text(encoding="utf-8")


@app.post("/reset")
async def reset():
    """Wipe memory between demo runs / rehearsals."""
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    return {"status": "reset"}


@app.on_event("startup")
async def startup_event():
    """
    Cognee needs its internal tables (users, principals, etc.) created once
    before recall/remember will work — especially the first time it points
    at a fresh SYSTEM_ROOT_DIRECTORY/DATA_ROOT_DIRECTORY.

    setup() is NOT a top-level cognee.setup() — it lives in
    cognee.modules.engine.operations.setup, which is why detecting it via
    getattr(cognee, "setup") silently found nothing before. run_migrations()
    alone only migrates vector/graph namespace tables, not the relational
    users/principals tables setup() creates — both are needed.
    """
    try:
        from cognee.modules.engine.operations.setup import setup as cognee_setup
        await cognee_setup()
        print("[startup] cognee setup() ran successfully")
    except Exception as e:
        print(f"[startup] cognee setup() raised (continuing): {e}")

    try:
        await cognee.run_migrations()
        print("[startup] cognee.run_migrations() ran successfully")
    except Exception as e:
        print(f"[startup] cognee.run_migrations() raised (continuing): {e}")


@app.get("/health")
async def health():
    return {"status": "ok"}
