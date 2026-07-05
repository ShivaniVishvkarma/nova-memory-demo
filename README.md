# Nova — a support agent that doesn't wake up on the roof

Hackathon scaffold: a side-by-side demo of a stateless LLM agent vs. the
same agent backed by [Cognee](https://github.com/topoteretes/cognee)'s
hybrid graph+vector memory. Full pitch and scripted demo scenario in
[`DEMO_SCRIPT.md`](./DEMO_SCRIPT.md) — read that first.

## What's here

```
backend/
  main.py          FastAPI server: /chat/memory, /chat/no-memory, /graph, /reset
  seed_demo.py      Pre-loads the scripted 4-session scenario (rehearsal + fallback)
  requirements.txt
  .env.example
frontend/
  index.html        Split-screen chat UI + live graph panel, no build step needed
DEMO_SCRIPT.md       The pitch, the 4-session scenario, judge Q&A prep
```

## Quickstart (Ollama — free, local, default in this scaffold)

1. **Install Ollama** — https://ollama.com/download (macOS, Windows, Linux).
2. **Pull a model and leave Ollama running:**
   ```bash
   ollama pull mistral
   ollama serve   # usually starts automatically after install — check with:
                   # curl http://localhost:11434
   ```
3. **Set up the backend:**
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
4. **Edit `.env`** — `CHAT_PROVIDER=ollama` is already the default, so Nova's
   chat replies need no API key and no cost at all.
   You still need to set `LLM_API_KEY` to a real OpenAI key for **Cognee's own
   internal extraction step** (turning text into graph entities/relationships)
   — that part isn't swapped to Ollama by this scaffold. A free OpenAI trial
   account is plenty for a short demo. If you want Cognee's extraction to also
   run locally through Ollama, see "Going fully free" below.
5. **Run the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Going fully free (Ollama for Cognee's extraction too)

Cognee supports pointing its own internal LLM calls at an Ollama-hosted model
instead of OpenAI. In `backend/main.py`, before any `cognee.remember`/`recall`
call happens, configure Cognee's provider:

```python
import cognee
cognee.config.set_llm_config({
    "llm_provider": "ollama",
    "llm_model": "mistral",
    "llm_endpoint": "http://localhost:11434/v1",
})
```

Check [docs.cognee.ai](https://docs.cognee.ai) for the exact config keys for
your installed Cognee version — this API surface moves around across
releases. Note that graph-extraction quality with a small local model is
noticeably weaker than with GPT-4o-mini or similar, so test this ahead of
judging, not during it.

Then open `frontend/index.html` directly in a browser (no build step —
it's a static file that talks to `localhost:8000`).

Cognee runs entirely local by default (SQLite + NetworkX + LanceDB) — no
Docker required to get the demo working. If you want to point it at
Postgres/Neo4j for something closer to a production setup, see
[docs.cognee.ai](https://docs.cognee.ai) for connection config; wire the
env vars into `.env` and Cognee will pick them up.

## Rehearsing / fallback

```bash
cd backend
python seed_demo.py
```

This writes the exact scripted scenario from `DEMO_SCRIPT.md` straight into
Cognee, so if live typing goes wrong during judging you can immediately ask
the scripted follow-up questions (Session 2/3/4 in the script) and still
land the payoff.

**Also record a screen capture of the working demo ahead of time.** Live
Docker/network flakiness during judging is the single most common way
hackathon demos die on stage.

## How the memory logic works

- `POST /chat/memory` calls `cognee.recall(message, session_id=customer_id)`
  before replying, and `cognee.remember(...)` after — for both the
  customer's message and Nova's reply. `session_id` keeps each customer's
  memory isolated while still persisting permanently into the graph in the
  background, which is why it survives a hard page refresh.
- `POST /chat/no-memory` skips Cognee entirely and calls the LLM raw — this
  is your control group.
- `GET /graph` calls Cognee's `visualize_graph()` and streams the resulting
  HTML into an iframe, so the graph panel is always showing the live state
  of memory, not a mockup.

## A note on Cognee's API surface

Cognee ships two overlapping APIs: the low-level `add()` / `cognify()` /
`search()` pipeline, and the newer high-level `remember()` / `recall()`
API used here (it has built-in `session_id` support, which is exactly what
this demo needs). Cognee iterates quickly, so if a function signature in
`main.py` doesn't match your installed version, check
[docs.cognee.ai](https://docs.cognee.ai) — `visualize_graph` in particular
has moved around across releases.

## Extending past the hackathon

- Multi-agent shared memory (two agents reading/writing the same graph)
- Memory decay/pruning policies so the graph doesn't grow unbounded
- Swap the customer-support vertical for a coding agent that remembers
  your codebase's conventions, or a research assistant with a persistent
  reading graph — the memory layer underneath doesn't change
