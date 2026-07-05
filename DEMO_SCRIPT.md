# "Nova" — a support agent that doesn't wake up on the roof

**Theme:** The Hangover. Stateless LLMs forget the groom. Cognee remembers.

Vertical chosen: **customer support agent** that carries a customer's full
history — past tickets, root causes, resolutions, preferences — across
completely separate sessions. This is the sharpest version of the pain
because everyone in the room has personally re-explained their issue to a
support bot three times in one week.

---

## 1. The 90-second pitch (say this, almost verbatim)

> "Every LLM call is stateless. The model doesn't remember what happened
> five minutes ago, let alone last week — and even inside one conversation,
> it eventually spills out of its context window. So your agent forgets the
> groom, loses the plot, and wakes up on the roof asking 'where's my
> context?'
>
> We built Nova, a support agent with a permanent memory. Under the hood
> it's powered by Cognee — a self-hosted, hybrid graph + vector memory
> layer. Every conversation gets written into a knowledge graph, not just a
> vector store, so Nova doesn't just remember *facts*, it remembers how
> they *relate*: this customer, this order, this bug, this fix.
>
> Let me show you the difference between an agent that forgets and one that
> doesn't."

Then run the live demo below.

---

## 2. The scripted demo (4 "sessions")

Run this with **two chat panels side by side**: "No Memory" (left) and
"Nova / Cognee" (right). Same underlying LLM, same prompt, only difference
is Cognee. Kill/refresh the page between sessions to prove it's a real
restart, not a UI trick.

### Session 1 — Monday, first contact
**You type (both panels):**
> "Hi, I'm Priya. My order #4471 arrived damaged — the packaging was
> crushed and one item was broken."

- Both panels respond helpfully. Nothing interesting yet — this is the
  baseline. Say: "Both agents are fine when they have everything in front
  of them right now."

### Session 2 — Wednesday, new session (**hard refresh** both panels)
**You type (both panels):**
> "Hey, following up on my order — any update?"

- **No Memory panel:** asks "Which order? Can you give me your order
  number and describe the issue?" — visibly starts from zero.
- **Nova panel:** already knows it's Priya, order #4471, damaged packaging,
  broken item — and gives a real update instead of an interrogation.

This is the moment judges should react. Pause here.

### Session 3 — Friday, a different but related question (**hard refresh**)
**You type (both panels):**
> "By the way, if this happens again, can you ship future orders in extra
> padding?"

- **No Memory panel:** answers generically, has no idea this relates to
  order #4471 or Priya's prior damage complaint.
- **Nova panel:** connects the new preference *to* the earlier incident —
  "Since your last order (#4471) arrived damaged, I've flagged your
  account for reinforced packaging on future shipments." This is the
  **graph relationship** payoff: preference ← caused by → past incident.

### Session 4 — the graph-only question (this is your technical flex)
**You type (Nova panel only):**
> "Has anything like my damaged order happened to other customers this
> week, and was there a common cause?"

- Show the **live graph visualization** panel as it answers. Point at the
  nodes: Customer → Order → Issue → Root Cause, and a second Customer node
  connected to the *same* Root Cause node (e.g. "warehouse B mis-packing").
- Say: "A pure vector store would give you semantically similar
  complaints. It can't tell you they share a root cause — that's a graph
  traversal, not a similarity search. This is why hybrid graph+vector beats
  plain RAG for this kind of question."

---

## 3. Why this script wins

- **Session 2** proves persistence across a hard restart (the core claim).
- **Session 3** proves *relational* memory, not just fact recall (the
  "hybrid graph" differentiator vs. a plain vector DB).
- **Session 4** proves the graph is queryable for structure, not just
  retrieval — your strongest technical answer to "isn't this just RAG?"

Keep total live demo time under 3 minutes. Everything past that, judges
start checking their phones.

---

## 4. Anticipated judge questions — have answers ready

**"Isn't this just RAG with extra steps?"**
Plain RAG retrieves chunks by similarity. Cognee extracts entities and
relationships at ingest time and stores them as a graph *alongside* the
vector index, so it can answer questions that require traversing
relationships (Session 4), not just questions that are semantically similar
to something already said.

**"What happens when the graph gets huge — does retrieval get slow or
noisy?"**
Cognee's `recall()` auto-routes between session-local fast-cache memory and
the permanent graph, so hot/recent context stays cheap while long-term
facts live in the graph. Mention you'd add pruning/decay policies (a real
roadmap item — say so honestly, it's a "next steps" slide, not a hole in
the demo).

**"Why self-hosted instead of a hosted memory API?"**
Data sovereignty — the whole knowledge graph (support tickets, PII, order
history) stays on infra you control. That's the pitch for any
enterprise/regulated buyer, and it's a genuine Cognee differentiator versus
memory-as-a-cloud-service competitors.

**"How is this different from just stuffing chat history into the
prompt?"**
Chat history is linear and unbounded — it's exactly what blows the context
window. Cognee compresses interactions into structured facts + relationships,
so a 6-month customer history retrieves as a few relevant graph nodes, not
200KB of transcript.

---

## 5. Slide order (if you want slides at all — keep it to 5)

1. Cold open: 15s clip/GIF of an agent asking "sorry, what was your order
   number again?" for the third time.
2. The problem: stateless calls + limited context window = agents that are
   smart in the moment, amnesiac across time.
3. The solution: Cognee — hybrid graph+vector memory, self-hosted.
4. **Live demo** (the 4 sessions above).
5. What's next: multi-agent shared memory, memory decay/pruning, enterprise
   self-hosting story.

---

## 6. Fallback plan

Screen-record the full 4-session demo once it's working and have the video
ready to play if live Docker/network flakes during judging. This is the
single most common way hackathon demos die on stage — don't skip this.
