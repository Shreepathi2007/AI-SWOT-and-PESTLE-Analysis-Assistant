const categories = [
  "Strengths", "Weaknesses", "Opportunities", "Threats",
  "Political", "Economic", "Social", "Technological", "Legal", "Environmental"
];
const colors = ["#4c8b68", "#d18b70", "#6e9a86", "#bb7567", "#7c8fa1", "#d1a153", "#b57f9b", "#6d91b4", "#879274", "#65998f"];
const form = document.querySelector("#analysis-form");
const resultsSection = document.querySelector("#results-section");
const analysisGrid = document.querySelector("#analysis-grid");
const notice = document.querySelector("#notice");
let currentRecord = null;
let noticeTimer;

function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.classList.toggle("error", isError);
  notice.classList.add("show");
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => notice.classList.remove("show"), 3200);
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) }
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status}).`);
  return data;
}

function formValues() {
  return Object.fromEntries(new FormData(form).entries());
}

function renderAnalysis(record) {
  currentRecord = record;
  document.querySelector("#results-title").textContent = record.name;
  analysisGrid.replaceChildren();
  categories.forEach((category, index) => {
    const card = document.createElement("article");
    card.className = "analysis-card";
    card.style.setProperty("--card-accent", colors[index]);
    const heading = document.createElement("header");
    const dot = document.createElement("span");
    dot.className = "category-dot";
    const title = document.createElement("h3");
    title.textContent = category;
    heading.append(dot, title);
    const textarea = document.createElement("textarea");
    textarea.setAttribute("aria-label", `${category} analysis points`);
    textarea.dataset.category = category;
    textarea.value = record.analysis[category].join("\n");
    textarea.addEventListener("input", () => { currentRecord = collectRecord(); });
    card.append(heading, textarea);
    analysisGrid.append(card);
  });
  resultsSection.classList.remove("d-none");
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function collectRecord() {
  return {
    ...currentRecord,
    ...formValues(),
    analysis: Object.fromEntries(categories.map(category => [
      category,
      document.querySelector(`[data-category="${category}"]`).value
        .split("\n").map(item => item.trim()).filter(Boolean)
    ]))
  };
}

form.addEventListener("input", event => {
  if (event.target.name === "description") {
    document.querySelector("#char-count").textContent = `${event.target.value.length} / 3000`;
  }
  event.target.classList.remove("is-invalid");
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const fields = [...form.querySelectorAll("input, textarea")];
  let valid = true;
  fields.forEach(field => {
    const fieldValid = Boolean(field.value.trim()) && field.value.length <= Number(field.maxLength);
    field.classList.toggle("is-invalid", !fieldValid);
    valid = valid && fieldValid;
  });
  if (!valid) {
    showNotice("Complete each field and check the character limits.", true);
    form.querySelector(".is-invalid")?.focus();
    return;
  }
  const button = document.querySelector("#generate-button");
  button.disabled = true;
  button.querySelector("span").textContent = "Building your prompts…";
  try {
    renderAnalysis(await api("/api/analyze", { method: "POST", body: JSON.stringify(formValues()) }));
    showNotice("Draft ready. Edit any section before saving.");
  } catch (error) {
    showNotice(error.message, true);
  } finally {
    button.disabled = false;
    button.querySelector("span").textContent = "Build my analysis";
  }
});

async function loadHistory() {
  try {
    const records = await api("/api/analyses");
    const list = document.querySelector("#history-list");
    document.querySelector("#history-count").textContent = records.length;
    list.replaceChildren();
    if (!records.length) {
      const empty = document.createElement("p");
      empty.className = "empty-history";
      empty.textContent = "Your saved work will appear here.";
      list.append(empty);
      return;
    }
    records.forEach(record => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "history-item";
      const title = document.createElement("strong");
      title.textContent = record.name;
      const detail = document.createElement("span");
      detail.textContent = `${record.industry} · ${new Date(record.created_at).toLocaleDateString()}`;
      button.append(title, detail);
      button.addEventListener("click", async () => {
        try {
          const saved = await api(`/api/analyses/${record.id}`);
          form.elements.name.value = saved.name;
          form.elements.industry.value = saved.industry;
          form.elements.description.value = saved.description;
          document.querySelector("#char-count").textContent = `${saved.description.length} / 3000`;
          renderAnalysis(saved);
          showNotice("Saved analysis opened. You can edit and save it as a new version.");
        } catch (error) { showNotice(error.message, true); }
      });
      list.append(button);
    });
  } catch (error) {
    showNotice(`Could not load saved analyses: ${error.message}`, true);
  }
}

function exportText() {
  const record = collectRecord();
  return `${record.name} — SWOT & PESTLE Analysis\nIndustry: ${record.industry}\n\nDescription: ${record.description}\n\n` +
    categories.map(category => `${category.toUpperCase()}\n${record.analysis[category].map(point => `• ${point}`).join("\n")}`).join("\n\n") +
    "\n\nGenerated locally as keyword-based suggestions. Review and verify before use.\n";
}

document.querySelector("#save-button").addEventListener("click", async event => {
  const record = collectRecord();
  if (categories.some(category => !record.analysis[category].length)) {
    showNotice("Each category needs at least one point before saving.", true);
    return;
  }
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const saved = await api("/api/analyses", { method: "POST", body: JSON.stringify(record) });
    currentRecord.id = saved.id;
    showNotice("Analysis saved on this device.");
    await loadHistory();
  } catch (error) { showNotice(error.message, true); }
  finally { button.disabled = false; }
});

document.querySelector("#copy-button").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(exportText());
    showNotice("Analysis copied to clipboard.");
  } catch {
    showNotice("Clipboard access is unavailable in this browser.", true);
  }
});

document.querySelector("#download-button").addEventListener("click", () => {
  const record = collectRecord();
  const blob = new Blob([exportText()], { type: "text/plain;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${record.name.trim().replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "").toLowerCase() || "analysis"}.txt`;
  link.click();
  URL.revokeObjectURL(link.href);
});

loadHistory();
