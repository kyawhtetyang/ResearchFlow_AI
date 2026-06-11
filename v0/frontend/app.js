const queryEl = document.querySelector("#query");
const runEl = document.querySelector("#run");
const stepsEl = document.querySelector("#steps");
const sourcesEl = document.querySelector("#sources");
const reportEl = document.querySelector("#report");
const jobStatusEl = document.querySelector("#job-status");
const stepCountEl = document.querySelector("#step-count");
const sourceCountEl = document.querySelector("#source-count");
const readinessEl = document.querySelector("#readiness");
const evalPanelEl = document.querySelector("#eval-panel");
const evalOutputEl = document.querySelector("#eval-output");
const evalEl = document.querySelector("#run-eval");
const copyReportEl = document.querySelector("#copy-report");
let latestReport = "";

const setLoading = (isLoading) => {
  runEl.disabled = isLoading;
  runEl.textContent = isLoading ? "Researching..." : "Run Research";
};

const renderMarkdown = (markdown) => {
  latestReport = markdown || "";
  const html = latestReport
    .split("\n")
    .map((line) => {
      if (line.startsWith("# ")) return `<h1>${line.slice(2)}</h1>`;
      if (line.startsWith("## ")) return `<h3>${line.slice(3)}</h3>`;
      if (line.startsWith("- ")) return `<p class="bullet">${line.slice(2)}</p>`;
      if (/^\d+\.\s/.test(line)) return `<p class="numbered">${line}</p>`;
      if (!line.trim()) return "";
      return `<p>${line}</p>`;
    })
    .join("");
  reportEl.innerHTML = html || "No report generated.";
};

const renderJob = (data, summary) => {
  stepsEl.innerHTML = "";
  sourcesEl.innerHTML = "";
  jobStatusEl.textContent = summary.status;
  stepCountEl.textContent = String(summary.step_count);
  sourceCountEl.textContent = String(summary.source_count);
  readinessEl.textContent = Number(summary.readiness_score).toFixed(2);

  for (const step of data.steps) {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${step.step_order}. ${step.agent_name.replace("_", " ")}</strong><span>${step.output}</span>`;
    stepsEl.appendChild(li);
  }

  for (const source of data.sources) {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${source.title}</strong><span>${source.snippet}</span><small>${source.url} · quality ${Number(source.quality_score ?? 0).toFixed(2)}</small>`;
    sourcesEl.appendChild(li);
  }

  renderMarkdown(data.report?.markdown ?? "No report generated.");
};

runEl.addEventListener("click", async () => {
  const query = queryEl.value.trim();
  if (!query) return;

  setLoading(true);
  reportEl.textContent = "Running research workflow...";

  try {
    const created = await fetch("/api/research/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, run_now: true }),
    }).then((res) => res.json());

    const [detail, summary] = await Promise.all([
      fetch(`/api/research/${created.id}`).then((res) => res.json()),
      fetch(`/api/research/${created.id}/summary`).then((res) => res.json()),
    ]);
    renderJob(detail, summary);
  } catch (error) {
    reportEl.textContent = `Research failed: ${error}`;
  } finally {
    setLoading(false);
  }
});

evalEl.addEventListener("click", async () => {
  evalEl.disabled = true;
  evalPanelEl.hidden = false;
  evalOutputEl.textContent = "Running evaluation...";
  try {
    const result = await fetch("/api/eval/run", { method: "POST" }).then((res) => res.json());
    evalOutputEl.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    evalOutputEl.textContent = `Evaluation failed: ${error}`;
  } finally {
    evalEl.disabled = false;
  }
});

copyReportEl.addEventListener("click", async () => {
  if (!latestReport) return;
  await navigator.clipboard.writeText(latestReport);
  copyReportEl.textContent = "Copied";
  setTimeout(() => {
    copyReportEl.textContent = "Copy";
  }, 1200);
});
