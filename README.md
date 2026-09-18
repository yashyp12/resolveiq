# ResolveIQ

<p align="center">
  <img src="https://github.com/user-attachments/assets/38528c04-33d4-4cae-8ba4-c5f35bca8c89" alt="ResolveIQ Logo" width="320" />
</p>

<p align="center">
  <strong>From Incidents to Insights</strong><br/>
  AI-powered, evidence-first incident analysis for IT and infrastructure teams.
</p>

---

## 🚨 The Problem We Are Solving

Incident response is often slow and repetitive. Teams lose time jumping between:

- Past incident tickets
- Historical fixes
- Internal runbooks
- Tribal knowledge

The same issue can be investigated from scratch multiple times, increasing downtime and response fatigue.

---

## ✅ The Solution We Are Building

ResolveIQ helps engineers move from raw incident data to actionable next steps by combining:

1. **Current incident facts** provided by the engineer
2. **Historical evidence** from past incidents and runbooks
3. **Amazon Bedrock inference** for likely causes and confidence
4. **Guided diagnostic actions** for safe human-led troubleshooting
5. **Runbook generation** to preserve reusable operational knowledge

> ResolveIQ does **not** perform automatic production remediation.

---

## 🔄 MVP Workflow

```text
Submit Incident
      ↓
Persist Incident
      ↓
Retrieve Historical Evidence
      ↓
Bedrock Analysis
      ↓
Evidence-First Results
      ↓
Generate & Persist Runbook
```

---

## 🧠 Evidence-First Output

ResolveIQ keeps analysis transparent by clearly separating:

- **Incident Facts** (what happened now)
- **Historical Evidence** (what happened before)
- **AI Inference** (likely causes, confidence)
- **Recommended Checks** (next diagnostic actions)
- **Uncertainty** (what is still unknown)

This prevents inferred root causes from being presented as confirmed facts.

---

## 🏗️ Architecture (Hackathon MVP)

```text
Frontend
   ↓
Amazon API Gateway
   ↓
AWS Lambda
   ├── Amazon DynamoDB (incidents, runbooks)
   ├── Amazon Bedrock (analysis)
   └── Amazon S3 (runbook/document storage)
```

---

## 🎯 Why ResolveIQ Matters

- Reduces repetitive incident triage work
- Improves troubleshooting consistency
- Makes AI outputs explainable with evidence
- Turns resolved incidents into reusable runbooks
- Speeds up onboarding for support and SRE teams

---

## 📌 Project Focus

This repository is built as a **hackathon MVP** with priority on:

1. Working end-to-end functionality
2. Real AWS integration
3. Security and least-privilege design
4. Clear, demonstrable value in a live demo

<details>
<summary><strong>Current Scope Snapshot</strong></summary>

- Incident submission and persistence
- Historical evidence retrieval
- AI-based incident analysis
- Structured result presentation
- Runbook generation and persistence

</details>
