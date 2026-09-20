const form = document.querySelector("#incident-form");
const button = document.querySelector("#submit-button");
const demoButton = document.querySelector("#demo-button");
const resetButton = document.querySelector("#reset-button");
const demoNotice = document.querySelector("#demo-notice");
const formError = document.querySelector("#form-error");

const results = document.querySelector("#results");
const copyAnalysisBtn = document.querySelector("#copy-analysis-btn");

const runbookForm = document.querySelector("#runbook-form");
const runbookButton = document.querySelector("#runbook-button");
const runbookError = document.querySelector("#runbook-error");
const runbookResult = document.querySelector("#runbook-result");

const apiBaseUrl = (window.RESOLVEIQ_CONFIG?.apiBaseUrl || "").replace(/\/$/, "");

let currentIncidentId = null;
let currentAnalysisData = null;
let currentRunbookData = null;
let isAnalyzing = false;
let isGeneratingRunbook = false;

const DEMO_INCIDENT = {
  title: "Checkout API connection timeout after deployment",
  environment: "fictional-production",
  description: "The checkout API started timing out immediately after a deployment. Requests from the application server are failing when connecting to the backend dependency.",
  service: "checkout-api",
  error: "connection timeout"
};

// --- Feature 1: Load Demo Incident ---
if (demoButton) {
  demoButton.addEventListener("click", () => {
    form.elements["title"].value = DEMO_INCIDENT.title;
    form.elements["environment"].value = DEMO_INCIDENT.environment;
    form.elements["description"].value = DEMO_INCIDENT.description;
    form.elements["service"].value = DEMO_INCIDENT.service;
    form.elements["error"].value = DEMO_INCIDENT.error;

    formError.hidden = true;
    formError.textContent = "";
    if (demoNotice) {
      demoNotice.hidden = false;
    }
  });
}

// --- Feature 2: Clear / Reset Handler ---
if (resetButton) {
  resetButton.addEventListener("click", () => {
    form.reset();
    if (form.elements["title"]) form.elements["title"].value = "";
    if (form.elements["environment"]) form.elements["environment"].value = "";
    if (form.elements["description"]) form.elements["description"].value = "";
    if (form.elements["service"]) form.elements["service"].value = "";
    if (form.elements["error"]) form.elements["error"].value = "";

    runbookForm.reset();
    const resEl = document.querySelector("#resolution");
    if (resEl) resEl.value = "";

    formError.hidden = true;
    formError.textContent = "";
    runbookError.hidden = true;
    runbookError.textContent = "";

    if (demoNotice) {
      demoNotice.hidden = true;
    }

    results.hidden = true;
    runbookResult.hidden = true;
    runbookResult.innerHTML = "";

    currentIncidentId = null;
    currentAnalysisData = null;
    currentRunbookData = null;
  });
}

// --- Feature 3: Analyze Incident Submission with Loading State ---
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (isAnalyzing) return;

  formError.hidden = true;
  formError.textContent = "";

  const payload = Object.fromEntries(new FormData(form));
  Object.keys(payload).forEach((key) => {
    if (!payload[key] || !payload[key].trim()) {
      delete payload[key];
    } else {
      payload[key] = payload[key].trim();
    }
  });

  isAnalyzing = true;
  button.disabled = true;
  if (demoButton) demoButton.disabled = true;
  if (resetButton) resetButton.disabled = true;

  button.innerHTML = '<span class="spinner" aria-hidden="true"></span><span>Analyzing incident…</span>';

  try {
    const response = await fetch(`${apiBaseUrl}/incidents/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error?.message || "The analysis request failed. Please check input parameters and try again.");
    }
    render(body);
  } catch (error) {
    formError.textContent = error.message || "The analysis request failed. Please try again.";
    formError.hidden = false;
  } finally {
    isAnalyzing = false;
    button.disabled = false;
    if (demoButton) demoButton.disabled = false;
    if (resetButton) resetButton.disabled = false;
    button.innerHTML = '<span class="btn-text">Analyze incident</span><span class="btn-icon" aria-hidden="true">→</span>';
  }
});

// --- Feature 4 & 5 & 8: Render Analysis Results ---
function render(result) {
  const { incident, evidence = [], analysis } = result;
  currentIncidentId = incident.incidentId;
  currentAnalysisData = result;

  document.querySelector("#result-title").textContent = incident.title;
  document.querySelector("#category").textContent = analysis.category;

  document.querySelector("#facts").innerHTML = [
    ["Description", incident.description],
    ["Environment", incident.environment],
    ["Service", incident.service || "Not specified"],
    ["Error", incident.error || "None reported"]
  ].map(([label, value]) => `<p><strong>${escapeHtml(label)}</strong><span>${escapeHtml(value)}</span></p>`).join("");

  document.querySelector("#causes").innerHTML = analysis.likelyCauses.length
    ? analysis.likelyCauses.map((cause) => `
        <div class="cause-item">
          <div class="cause-top">
            <strong class="cause-title">${escapeHtml(cause.cause)}</strong>
            <span class="cause-confidence">AI-assessed confidence: ${Math.round(cause.confidence * 100)}%</span>
          </div>
          <div class="cause-evidence">
            <span class="evidence-pill-label">Evidence cited:</span>
            <span class="evidence-pill">${escapeHtml(cause.evidenceIds.join(", ") || "None cited")}</span>
          </div>
        </div>
      `).join("")
    : '<div class="empty-state"><p class="empty-title">No likely cause is supported by the retrieved evidence.</p><p class="empty-detail">The available data is insufficient to establish a defensible hypothesis.</p></div>';

  document.querySelector("#evidence").innerHTML = evidence.length
    ? evidence.map((item) => `
        <div class="evidence-item">
          <div class="evidence-top">
            <strong class="evidence-id-title">${escapeHtml(item.evidenceId)} · ${escapeHtml(item.title)}</strong>
            <span class="evidence-score">Relevance ${item.relevanceScore}</span>
          </div>
          <p class="evidence-summary">${escapeHtml(item.summary)}</p>
        </div>
      `).join("")
    : '<div class="empty-state"><p class="empty-title">No matching historical evidence was found.</p><p class="empty-detail">Absence of historical matches does not imply absence of a cause; diagnostic checks should be verified directly.</p></div>';

  document.querySelector("#checks").innerHTML = analysis.recommendedChecks.map((check) => `<li>${escapeHtml(check)}</li>`).join("");
  document.querySelector("#uncertainty").textContent = analysis.uncertainty;

  // Reset any previous runbook form/result state for the new incident
  runbookForm.reset();
  runbookError.hidden = true;
  runbookError.textContent = "";
  runbookResult.hidden = true;
  runbookResult.innerHTML = "";
  currentRunbookData = null;

  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

// --- Feature 6: Copy Analysis Handler ---
if (copyAnalysisBtn) {
  copyAnalysisBtn.addEventListener("click", () => {
    if (!currentAnalysisData) return;
    const text = formatAnalysisForClipboard(currentAnalysisData);
    copyToClipboard(text, copyAnalysisBtn, "Copy analysis");
  });
}

// --- Feature 3: Generate Runbook Submission with Loading State ---
runbookForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (isGeneratingRunbook) return;

  if (!currentIncidentId) {
    runbookError.textContent = "Please analyze an incident first before generating a runbook.";
    runbookError.hidden = false;
    return;
  }

  const resolutionValue = document.querySelector("#resolution").value.trim();
  if (!resolutionValue) return;

  runbookError.hidden = true;
  runbookError.textContent = "";

  isGeneratingRunbook = true;
  runbookButton.disabled = true;
  runbookButton.innerHTML = '<span class="spinner" aria-hidden="true"></span><span>Generating runbook…</span>';

  try {
    const response = await fetch(`${apiBaseUrl}/incidents/${encodeURIComponent(currentIncidentId)}/runbook`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resolution: resolutionValue })
    });

    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error?.message || "The runbook generation request failed.");
    }
    renderRunbook(body.runbook);
  } catch (error) {
    runbookError.textContent = error.message || "The runbook request failed. Please try again.";
    runbookError.hidden = false;
  } finally {
    isGeneratingRunbook = false;
    runbookButton.disabled = false;
    runbookButton.innerHTML = '<span class="btn-text">Generate runbook</span>';
  }
});

// --- Feature 7: Render Runbook Results with Copy Action ---
function renderRunbook(runbook) {
  currentRunbookData = runbook;

  const sections = [
    ["Problem", [runbook.problem]],
    ["Preconditions", runbook.preconditions],
    ["Diagnostic steps", runbook.diagnosticSteps],
    ["Verification", runbook.verification],
    ["Remediation (Human-Approved)", runbook.remediation],
    ["Escalation", runbook.escalation]
  ];

  runbookResult.innerHTML = `
    <div class="runbook-header">
      <div>
        <p class="eyebrow">REUSABLE RUNBOOK</p>
        <h3>${escapeHtml(runbook.title)}</h3>
      </div>
      <button id="copy-runbook-btn" type="button" class="btn btn-outline btn-sm" title="Copy runbook to clipboard">
        <span class="btn-text">Copy runbook</span>
      </button>
    </div>
    ${sections.map(([title, items]) => `
      <div class="runbook-section">
        <strong>${escapeHtml(title)}</strong>
        <ul>${(items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </div>
    `).join("")}
  `;

  runbookResult.hidden = false;

  const copyRunbookBtn = document.querySelector("#copy-runbook-btn");
  if (copyRunbookBtn) {
    copyRunbookBtn.addEventListener("click", () => {
      const text = formatRunbookForClipboard(runbook);
      copyToClipboard(text, copyRunbookBtn, "Copy runbook");
    });
  }

  runbookResult.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// --- Clipboard Formatting ---
function formatAnalysisForClipboard(result) {
  const { incident, evidence = [], analysis } = result;
  const lines = [
    "========================================",
    "RESOLVEIQ INCIDENT ANALYSIS",
    "========================================",
    "",
    "CURRENT INCIDENT FACTS:",
    `• Title: ${incident.title}`,
    `• Environment: ${incident.environment}`,
    `• Service: ${incident.service || "Not specified"}`,
    `• Error: ${incident.error || "None reported"}`,
    `• Description: ${incident.description}`,
    "",
    `CLASSIFICATION / CATEGORY: ${analysis.category}`,
    "",
    "AI INFERENCES (Hypotheses - Human Verification Required):"
  ];

  if (analysis.likelyCauses && analysis.likelyCauses.length) {
    analysis.likelyCauses.forEach((cause) => {
      lines.push(`• Hypothesis: ${cause.cause}`);
      lines.push(`  AI-assessed confidence: ${Math.round(cause.confidence * 100)}%`);
      lines.push(`  Evidence cited: ${cause.evidenceIds && cause.evidenceIds.length ? cause.evidenceIds.join(", ") : "None cited"}`);
    });
  } else {
    lines.push("• No likely cause is supported by the retrieved evidence.");
  }

  lines.push("", "HISTORICAL EVIDENCE (Fictional Records):");
  if (evidence && evidence.length) {
    evidence.forEach((item) => {
      lines.push(`• [${item.evidenceId}] ${item.title} (Relevance: ${item.relevanceScore})`);
      lines.push(`  Summary: ${item.summary}`);
    });
  } else {
    lines.push("• No matching historical evidence was found.");
  }

  lines.push("", "RECOMMENDED DIAGNOSTIC CHECKS (Human Action):");
  if (analysis.recommendedChecks && analysis.recommendedChecks.length) {
    analysis.recommendedChecks.forEach((check, index) => {
      lines.push(`${index + 1}. ${check}`);
    });
  } else {
    lines.push("• None provided.");
  }

  lines.push("", "UNCERTAINTY & BOUNDARIES:");
  lines.push(analysis.uncertainty || "None recorded.");
  lines.push("", "---");
  lines.push("Notice: ResolveIQ uses fictional demonstration records. Recommendations are diagnostic only and require human approval. No production changes are made automatically.");

  return lines.join("\n");
}

function formatRunbookForClipboard(runbook) {
  const lines = [
    "========================================",
    `RESOLVEIQ RUNBOOK: ${runbook.title}`,
    "========================================",
    "",
    "PROBLEM:",
    runbook.problem,
    "",
    "PRECONDITIONS:",
    ...(runbook.preconditions || []).map((item) => `- ${item}`),
    "",
    "DIAGNOSTIC STEPS:",
    ...(runbook.diagnosticSteps || []).map((item, idx) => `${idx + 1}. ${item}`),
    "",
    "VERIFICATION:",
    ...(runbook.verification || []).map((item) => `- ${item}`),
    "",
    "REMEDIATION (Human-Approved Resolution):",
    ...(runbook.remediation || []).map((item) => `- ${item}`),
    "",
    "ESCALATION:",
    ...(runbook.escalation || []).map((item) => `- ${item}`),
    "",
    "---",
    "Notice: ResolveIQ reusable runbook. Preserves human-approved resolution knowledge."
  ];
  return lines.join("\n");
}

async function copyToClipboard(text, buttonElement, defaultText = "Copy") {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }

    const originalHtml = buttonElement.innerHTML;
    buttonElement.innerHTML = '<span class="copied-indicator" aria-live="polite">✓ Copied!</span>';

    setTimeout(() => {
      buttonElement.innerHTML = originalHtml;
    }, 2000);
  } catch (err) {
    const originalHtml = buttonElement.innerHTML;
    buttonElement.textContent = "Copy unavailable";
    setTimeout(() => {
      buttonElement.innerHTML = originalHtml;
    }, 2000);
  }
}

// --- Sanitization Utility ---
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  }[character]));
}
