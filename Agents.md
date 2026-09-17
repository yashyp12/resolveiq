# ResolveIQ — Agent Instructions

## 1. Project Overview

ResolveIQ is a focused AI-assisted incident analysis and knowledge-generation application.

The system helps IT/infrastructure support engineers analyze an incident by comparing its symptoms against a small knowledge base of historical incidents and troubleshooting runbooks.

The system should provide:

* Incident classification
* Likely causes
* Similar historical incidents
* Evidence supporting the analysis
* Recommended diagnostic steps
* Confidence indication
* Runbook generation from a resolved incident

The project is being built as a hackathon MVP. Simplicity, reliability, demonstrability, and real AWS usage are more important than feature quantity.

---

## 2. Primary Objective

Build a working end-to-end MVP that demonstrates:

User → Web UI → AWS API → AI analysis → historical evidence → actionable troubleshooting guidance → reusable runbook.

The application must be functional before additional features are added.

---

## 3. Target Architecture

The planned production architecture is:

Frontend
→ Amazon API Gateway
→ AWS Lambda
→ DynamoDB
→ Amazon Bedrock
→ S3

The application may additionally use:

* AWS Amplify for frontend hosting
* Amazon CloudWatch for logging
* MCP for controlled tool access
* Strands Agents if it provides a clear benefit to the agent workflow

Do not introduce additional AWS services without a documented reason.

---

## 4. Core AWS Services

Preferred services:

* Amazon Bedrock — AI analysis
* AWS Lambda — backend/business logic
* Amazon API Gateway — HTTP API
* Amazon DynamoDB — incident/runbook data
* Amazon S3 — generated/stored runbooks and supporting documents
* AWS Amplify — frontend hosting
* Amazon CloudWatch — logs and observability

Use the smallest number of services necessary.

---

## 5. Security Rules

Never:

* Hard-code AWS credentials
* Commit secrets
* Put AWS credentials in frontend code
* Use real company/client data
* Use confidential ServiceNow tickets
* Use production infrastructure credentials
* Give an AI agent unrestricted AWS administrator access

All credentials must be supplied through the appropriate AWS authentication mechanism or environment configuration.

Use fictional/anonymized demonstration data.

---

## 6. MVP Scope

### Required

1. Create incident
2. Analyze incident
3. Retrieve relevant historical incidents
4. Generate AI analysis
5. Display likely causes
6. Display evidence
7. Display recommended diagnostic steps
8. Display similar incidents
9. Generate a reusable runbook
10. Persist relevant data

### Optional

Only implement these if the core MVP is already working:

* MCP integration
* Strands agent orchestration
* Better search/retrieval
* Authentication
* Advanced dashboard
* GitHub Actions CI/CD
* Additional observability

---

## 7. Engineering Principles

### Prefer simple implementations.

Do not over-engineer.

Do not introduce:

* Kubernetes
* Microservice architecture
* RDS
* complex event-driven architecture
* multiple autonomous agents
* unnecessary queues
* unnecessary vector databases

unless a concrete requirement appears.

### Working software first.

A working feature is more valuable than an unfinished collection of features.

### Small changes.

Agents should modify only the files necessary for the assigned task.

### No speculative features.

Do not implement features that are not in the requirements or explicitly requested.

---

## 8. AI Behavior

AI-generated incident analysis must be evidence-oriented.

The model should distinguish between:

* Observed incident information
* Historical evidence
* Inference
* Recommended diagnostic action

The AI must not present an unsupported guess as a confirmed root cause.

The application should clearly communicate that recommendations are troubleshooting guidance and that production changes require human approval.

---

## 9. Data

The initial demonstration dataset will contain fictional/anonymized:

* Historical incidents
* Resolutions
* Troubleshooting steps
* Runbooks

No real organizational data may be added.

---

## 10. Development Workflow

Before implementing a feature:

1. Read `AGENTS.md`
2. Read the relevant documentation under `docs/`
3. Understand the existing implementation
4. Implement only the requested task
5. Run relevant tests
6. Report changed files
7. Report tests performed
8. Report any assumptions

Do not rewrite unrelated code.

---

## 11. Architecture Changes

If an implementation requires changing the architecture:

1. Explain why
2. Identify the affected component
3. Update the relevant documentation
4. Then implement the change

Do not silently change the architecture.

---

## 12. Git

Use small, meaningful commits.

Preferred format:

feat: add incident analysis API

feat: integrate Bedrock analysis

feat: add incident results UI

fix: handle Bedrock timeout

docs: update deployment guide

Do not commit:

* `.env` files containing secrets
* AWS credentials
* build artifacts
* dependency caches
* unnecessary generated files

---

## 13. Definition of Done

A feature is not considered complete until:

* The implementation exists
* The expected behavior works
* Relevant errors are handled
* Tests pass where applicable
* No secrets are exposed
* Documentation is updated when necessary

---

## 14. Agent Constraint

Do not attempt to build the entire ResolveIQ application in one operation.

Work task-by-task according to `docs/implementation-plan.md`.

If requirements are ambiguous, prefer the smallest reasonable implementation and document the assumption.
