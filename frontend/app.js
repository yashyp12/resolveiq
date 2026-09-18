const form = document.querySelector("#incident-form");
const button = document.querySelector("#submit-button");
const formError = document.querySelector("#form-error");
const results = document.querySelector("#results");
const runbookForm = document.querySelector("#runbook-form");
const runbookButton = document.querySelector("#runbook-button");
const runbookError = document.querySelector("#runbook-error");
const runbookResult = document.querySelector("#runbook-result");
const apiBaseUrl = (window.RESOLVEIQ_CONFIG?.apiBaseUrl || "").replace(/\/$/, "");
let currentIncidentId = null;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.hidden = true;
  button.disabled = true;
  button.textContent = "Analyzing…";
  const payload = Object.fromEntries(new FormData(form));
  Object.keys(payload).forEach((key) => {
    if (!payload[key]) delete payload[key];
  });

  try {
    const response = await fetch(`${apiBaseUrl}/incidents/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || "The analysis request failed.");
    render(body);
  } catch (error) {
    formError.textContent = error.message || "The analysis request failed.";
    formError.hidden = false;
  } finally {
    button.disabled = false;
    button.innerHTML = 'Analyze incident <span aria-hidden="true">→</span>';
  }
});

function render(result) {
  const { incident, evidence = [], analysis } = result;
  currentIncidentId = incident.incidentId;
  document.querySelector("#result-title").textContent = incident.title;
  document.querySelector("#category").textContent = analysis.category;
  document.querySelector("#facts").innerHTML = [
    ["Description", incident.description],
    ["Environment", incident.environment],
    ["Service", incident.service || "Not provided"],
    ["Error", incident.error || "Not provided"]
  ].map(([label, value]) => `<p><strong>${escapeHtml(label)}</strong>${escapeHtml(value)}</p>`).join("");
  document.querySelector("#causes").innerHTML = analysis.likelyCauses.length
    ? analysis.likelyCauses.map((cause) => `<div class="cause"><strong>${escapeHtml(cause.cause)}</strong><span>${Math.round(cause.confidence * 100)}% confidence</span><small>Evidence: ${escapeHtml(cause.evidenceIds.join(", ") || "None")}</small></div>`).join("")
    : "<p>No likely cause is supported by the retrieved evidence.</p>";
  document.querySelector("#evidence").innerHTML = evidence.length
    ? evidence.map((item) => `<div class="evidence-item"><strong>${escapeHtml(item.evidenceId)} · ${escapeHtml(item.title)}</strong><p>${escapeHtml(item.summary)}</p><small>Relevance ${item.relevanceScore}</small></div>`).join("")
    : "<p>No matching historical evidence was found.</p>";
  document.querySelector("#checks").innerHTML = analysis.recommendedChecks.map((check) => `<li>${escapeHtml(check)}</li>`).join("");
  document.querySelector("#uncertainty").textContent = analysis.uncertainty;
  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

runbookForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  runbookError.hidden = true;
  runbookButton.disabled = true;
  runbookButton.textContent = "Generating…";
  try {
    const response = await fetch(`${apiBaseUrl}/incidents/${encodeURIComponent(currentIncidentId)}/runbook`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resolution: document.querySelector("#resolution").value })
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || "The runbook request failed.");
    renderRunbook(body.runbook);
  } catch (error) {
    runbookError.textContent = error.message || "The runbook request failed.";
    runbookError.hidden = false;
  } finally {
    runbookButton.disabled = false;
    runbookButton.textContent = "Generate runbook";
  }
});

function renderRunbook(runbook) {
  const sections = [
    ["Problem", [runbook.problem]],
    ["Preconditions", runbook.preconditions],
    ["Diagnostic steps", runbook.diagnosticSteps],
    ["Verification", runbook.verification],
    ["Remediation", runbook.remediation],
    ["Escalation", runbook.escalation]
  ];
  runbookResult.innerHTML = `<h3>${escapeHtml(runbook.title)}</h3>${sections.map(([title, items]) =>
    `<div class="runbook-section"><strong>${escapeHtml(title)}</strong><ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`
  ).join("")}`;
  runbookResult.hidden = false;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[character]));
}
