# ResolveIQ

> **From IT Ticket → Diagnosis → Evidence-Based Resolution**

ResolveIQ is an evidence-first incident analysis platform that helps IT and infrastructure teams investigate incidents using **historical incidents, curated runbooks, and AI-assisted analysis**.

## 🚀 What It Does

* Analyzes incoming IT incidents
* Retrieves relevant historical incidents and runbooks
* Uses **Amazon Bedrock** for AI-assisted diagnosis
* Separates **facts, evidence, AI inference, and recommended checks**
* Generates reusable runbooks from successful resolutions
* Never performs automatic infrastructure changes

## 🏗️ Architecture

```text
User
  ↓
Static Frontend
  ↓
API Gateway (HTTP API)
  ↓
AWS Lambda (Python)
  ├──→ DynamoDB
  │     ├── Incidents
  │     └── Runbooks
  │
  └──→ Amazon Bedrock
          ↓
      AI Analysis
          
CloudWatch → Logs & Observability
```

## 🔄 Workflow

```text
IT Incident
    ↓
Validate & Store
    ↓
Retrieve Historical Evidence
    ↓
AI-Assisted Analysis
    ↓
Facts + Evidence + Inference
    ↓
Diagnostic Checks
    ↓
Human Resolution
    ↓
Reusable Runbook
```

## 🛠️ Tech Stack

**Frontend:** HTML, CSS, JavaScript
**Backend:** Python 3.12, AWS Lambda
**API:** Amazon API Gateway
**Database:** Amazon DynamoDB
**AI:** Amazon Bedrock
**Infrastructure:** AWS SAM / CloudFormation
**Observability:** Amazon CloudWatch
**Testing:** pytest
**Version Control:** Git & GitHub

## 🔐 Design Principle

> **AI recommends. Evidence supports. Humans decide.**

ResolveIQ is designed as a safe, read/analyze/recommend system and does not automatically modify production infrastructure.

## 📁 Project Structure

```text
resolveiq/
├── backend/          # API, analysis, retrieval & persistence
├── frontend/         # Web interface
├── infrastructure/   # AWS SAM infrastructure
├── data/             # Fictional incident & runbook data
├── docs/             # Architecture & implementation docs
└── tests/            # Automated tests
```

## ⚙️ Local Setup

```bash
python -m venv .venv
pip install -r requirements.txt
python -m pytest -q
```

The default analysis provider is a deterministic mock. Amazon Bedrock can be enabled through environment configuration.

## ☁️ AWS Deployment

Infrastructure is defined in:

```text
infrastructure/template.yaml
```

```bash
sam validate --template-file infrastructure/template.yaml
sam build --template-file infrastructure/template.yaml
sam deploy --guided --template-file infrastructure/template.yaml
```

> All demonstration data is fictional. Never commit credentials, customer tickets, production logs, or private infrastructure information.

---

**Built for the First Commit / Bharat Builds Tour AWS Hackathon.**
