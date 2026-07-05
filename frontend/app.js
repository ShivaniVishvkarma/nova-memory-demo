let API = document.getElementById("api-base").value.trim();
const CUSTOMER_ID = "priya_4471"; // reused across "sessions" so it's the same person each refresh

function onApiBaseChange() {
  API = document.getElementById("api-base").value.trim().replace(/\/$/, "");
  checkBackend();
}

function setConnStatus(state, text) {
  const el = document.getElementById("conn-status");
  el.className = "conn-status " + state;
  el.textContent = text;
}

function showBanner(text) {
  const el = document.getElementById("banner");
  el.textContent = text;
  el.classList.remove("hidden");
}
function hideBanner() {
  document.getElementById("banner").classList.add("hidden");
}

function setInputsEnabled(enabled) {
  ["input-nomem", "input-mem"].forEach((id) => {
    document.getElementById(id).disabled = !enabled;
  });
  document.querySelectorAll(".composer button").forEach((b) => (b.disabled = !enabled));
}

async function checkBackend() {
  setConnStatus("checking", "checking backend…");
  try {
    const resp = await fetch(API + "/health", { method: "GET" });
    if (!resp.ok) throw new Error("bad status " + resp.status);
    setConnStatus("ok", "backend connected");
    hideBanner();
    setInputsEnabled(true);
  } catch (e) {
    setConnStatus("down", "backend unreachable");
    setInputsEnabled(false);
    showBanner(
      "Can't reach the backend at " + API + ". Checklist: (1) is `uvicorn main:app --reload --port 8000` " +
      "still running in its terminal window? (2) is the API base above correct? " +
      "(3) try opening " + API + "/health directly in a new browser tab — what does it show?"
    );
  }
}

function addMsg(panelId, role, text) {
  const el = document.getElementById(panelId);
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}

async function send(mode) {
  const inputId = mode === "mem" ? "input-mem" : "input-nomem";
  const msgsId = mode === "mem" ? "msgs-mem" : "msgs-nomem";
  const input = document.getElementById(inputId);
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addMsg(msgsId, "user", text);

  const endpoint = mode === "mem" ? "/chat/memory" : "/chat/no-memory";
  try {
    const resp = await fetch(API + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_id: CUSTOMER_ID, message: text }),
    });
    if (!resp.ok) {
      const body = await resp.text();
      throw new Error("HTTP " + resp.status + ": " + body.slice(0, 200));
    }
    const data = await resp.json();
    addMsg(msgsId, "agent", data.reply);
    if (mode === "mem") refreshGraph();
  } catch (e) {
    addMsg(msgsId, "error", "Request failed — " + e.message);
    checkBackend(); // re-check in case the backend just went down
  }
}

function refreshGraph() {
  document.getElementById("graph-frame").src = API + "/graph?" + Date.now();
}

async function resetDemo() {
  try {
    await fetch(API + "/reset", { method: "POST" });
    document.getElementById("msgs-mem").innerHTML = "";
    document.getElementById("msgs-nomem").innerHTML = "";
    document.getElementById("graph-frame").src = "about:blank";
  } catch (e) {
    showBanner("Reset failed — backend unreachable at " + API);
  }
}

// Init
addMsg("msgs-nomem", "system", "New session started — this panel has never seen you before.");
addMsg("msgs-mem", "system", "New session started — Nova will check memory automatically.");
checkBackend();
setInterval(checkBackend, 8000); // keep polling so the status badge stays honest
