const $ = (id) => document.getElementById(id);
const log = $("log"), q = $("q"), send = $("send");
const status = $("upload-status"), docCount = $("doc-count");
const drop = $("drop"), file = $("file"), browse = $("browse");

function setStatus(text, err = false) {
  status.textContent = text;
  status.parentElement.className = "status-row" + (err ? " err" : "");
}

function renderDocs(docs) {
  const ul = $("docs");
  ul.innerHTML = "";
  docCount.textContent = docs.length;

  if (!docs.length) {
    ul.innerHTML = '<li class="none">No PDFs uploaded yet.</li>';
    return;
  }

  for (const d of docs) {
    const li = document.createElement("li");
    const icon = document.createElement("div");
    icon.className = "pdf-icon";
    icon.textContent = "PDF";

    const info = document.createElement("div");
    info.className = "doc-info";
    info.innerHTML = '<div class="name"></div><div class="meta"></div>';
    info.querySelector(".name").textContent = d.name;
    info.querySelector(".meta").textContent = `${d.pages} pages • ${d.chunks} chunks`;

    const del = document.createElement("button");
    del.textContent = "×";
    del.title = "Remove document";
    del.onclick = async () => {
      const r = await fetch("/api/documents/" + encodeURIComponent(d.name), { method: "DELETE" });
      if (r.ok) renderDocs((await r.json()).documents);
    };

    li.append(icon, info, del);
    ul.append(li);
  }
}

async function upload(files) {
  if (!files.length) return;

  const pdfs = [...files].filter(f => f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf"));
  if (!pdfs.length) {
    setStatus("Please select PDF files only.", true);
    return;
  }

  const form = new FormData();
  pdfs.forEach(f => form.append("files", f));

  setStatus(`Processing ${pdfs.length} PDF${pdfs.length > 1 ? "s" : ""}...`);

  try {
    const r = await fetch("/api/upload", { method: "POST", body: form });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || "Upload failed.");

    const bad = data.results.filter(x => !x.ok);
    renderDocs(data.documents);

    if (bad.length) {
      setStatus(bad.map(b => `${b.name}: ${b.error}`).join(" "), true);
    } else {
      setStatus(`${pdfs.length} PDF${pdfs.length > 1 ? "s" : ""} ready for questions.`);
    }
  } catch (e) {
    setStatus(e.message, true);
  }
}

browse.onclick = (e) => {
  e.stopPropagation();
  file.click();
};

file.onchange = () => {
  upload(file.files);
  file.value = "";
};

drop.onkeydown = (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    file.click();
  }
};

["dragover", "dragenter"].forEach(t =>
  drop.addEventListener(t, e => {
    e.preventDefault();
    drop.classList.add("over");
  })
);

["dragleave", "drop"].forEach(t =>
  drop.addEventListener(t, () => drop.classList.remove("over"))
);

drop.addEventListener("drop", e => {
  e.preventDefault();
  upload(e.dataTransfer.files);
});

function addMsg(cls, text) {
  $("empty")?.remove();

  const m = document.createElement("div");
  m.className = "msg " + cls;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = cls === "user" ? "You" : "✦";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const t = document.createElement("div");
  t.className = "text";
  t.textContent = text;

  bubble.append(t);
  m.append(avatar, bubble);
  log.append(m);
  log.scrollTop = log.scrollHeight;

  return m;
}

function addSources(msg, sources) {
  if (!sources || !sources.length) return;

  const det = document.createElement("details");
  det.className = "sources";

  const summary = document.createElement("summary");
  summary.textContent = `${sources.length} source${sources.length > 1 ? "s" : ""} retrieved`;
  det.append(summary);

  for (const s of sources) {
    const d = document.createElement("div");
    d.className = "src";

    const b = document.createElement("b");
    b.textContent = `${s.source}, page ${s.page}`;

    const score = document.createElement("span");
    score.className = "score";
    score.textContent = `Match ${Math.round(s.score * 100)}%`;

    const sn = document.createElement("span");
    sn.className = "snip";
    sn.textContent = s.snippet + "...";

    d.append(b, score, sn);
    det.append(d);
  }

  msg.querySelector(".bubble").append(det);
}

async function ask() {
  const question = q.value.trim();
  if (!question) return;

  addMsg("user", question);
  q.value = "";
  q.style.height = "auto";
  send.disabled = true;

  const pending = addMsg("bot", "Searching your documents...");

  try {
    const r = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || "Request failed.");

    pending.querySelector(".text").textContent = data.answer;
    addSources(pending, data.sources);
  } catch (e) {
    pending.classList.add("err");
    pending.querySelector(".text").textContent = e.message;
  }

  send.disabled = false;
  q.focus();
  log.scrollTop = log.scrollHeight;
}

send.onclick = ask;

q.onkeydown = e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
};

q.addEventListener("input", () => {
  q.style.height = "auto";
  q.style.height = Math.min(q.scrollHeight, 120) + "px";
});

document.querySelectorAll(".examples button").forEach(btn => {
  btn.onclick = () => {
    q.value = btn.dataset.question;
    q.focus();
  };
});

fetch("/api/documents")
  .then(r => r.json())
  .then(d => renderDocs(d.documents))
  .catch(() => setStatus("Could not connect to RAG server.", true));
