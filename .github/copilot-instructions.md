# ResolveIQ — GitHub Copilot Instructions

## Project

ResolveIQ is a hackathon MVP for AI-assisted IT/infrastructure incident analysis.

The application helps an IT/infrastructure engineer analyze an incident using:
- Incident details
- Historical incidents
- Troubleshooting knowledge
- Runbooks
- Amazon Bedrock

The system produces evidence-oriented troubleshooting guidance and can generate reusable runbooks.

## Primary Goal

Build a small, reliable, demonstrable MVP within the hackathon timeframe.

Prioritize:
1. Working functionality
2. AWS integration
3. Clear evidence-based AI output
4. Simple architecture
5. Good user experience
6. Security
7. Documentation

Do not optimize for feature quantity.

## Planned Architecture

Frontend
→ API Gateway
→ Lambda
→ DynamoDB
→ Amazon Bedrock

S3 will be used where appropriate for runbook/document storage.

AWS Amplify may be used for frontend hosting.

CloudWatch may be used for logging and observability.

MCP and Strands Agents may be introduced only when they provide a clear benefit without putting the MVP at risk.

## Core MVP

The application must support:

1. Submit an incident
2. Store the incident
3. Retrieve relevant historical incidents
4. Analyze the incident using Amazon Bedrock
5. Display likely causes
6. Display supporting evidence
7. Display recommended diagnostic steps
8. Display similar incidents
9. Generate a reusable runbook
10. Persist the runbook

## Evidence-First AI

ResolveIQ must not behave as a generic chatbot.

AI output should distinguish between:

- Incident facts
- Historical evidence
- AI inference
- Recommended troubleshooting actions

Do not present an inferred root cause as a confirmed fact.

If evidence is insufficient, explicitly communicate that limitation.

Production changes must never be performed automatically.

## Data

Use only fictional or anonymized demonstration data.

Never use:
- Company confidential information
- Real ServiceNow tickets
- Production credentials
- Private infrastructure information
- Personal information

Initial demo data should contain approximately:
- 20–30 historical incidents
- 5–10 runbooks

## AWS

Preferred services:

- Amazon Bedrock
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- Amazon S3
- AWS Amplify
- Amazon CloudWatch

Do not introduce additional AWS services without a concrete technical reason.

Do not use unnecessary:
- Kubernetes
- RDS
- Microservices
- Complex event-driven architecture
- Multiple autonomous agents
- Vector databases

unless a real requirement emerges.

## Security

Never:
- Hard-code credentials
- Commit secrets
- Put AWS credentials in frontend code
- Commit `.env` files containing secrets
- Use unrestricted AWS administrator permissions for an AI agent
- Automatically modify production infrastructure

Follow least-privilege principles.

## Development Rules

Before implementing a task:

1. Read AGENTS.md
2. Read the relevant documentation in `docs/`
3. Inspect the existing implementation
4. Implement only the requested task
5. Run appropriate tests
6. Report files changed
7. Report tests performed
8. Report assumptions

Do not implement unrelated features.

Do not rewrite working code unnecessarily.

## Architecture Changes

Do not silently change the architecture.

If a task requires an architectural change:
1. Explain why
2. Identify the affected components
3. Update the relevant documentation
4. Then implement the change

## Git

Use small, meaningful commits.

Examples:

feat: add incident analysis API
feat: integrate Bedrock analysis
feat: add incident results UI
feat: add runbook generation
fix: handle Bedrock timeout
docs: update deployment guide

Never commit credentials, secrets, build artifacts, or unnecessary generated files.

## Testing

Every meaningful backend feature should have appropriate tests.

At minimum, validate:
- Input validation
- Successful requests
- Error handling
- AWS service failures
- Missing evidence
- Empty/invalid input

## Scope Control

This is a hackathon MVP.

Do not build the entire application in one step.

Work according to:

docs/implementation-plan.md

Complete the core workflow before adding optional functionality.

If a feature is not required for the MVP, do not implement it unless explicitly requested.

## Agent Behavior

When asked to plan:
- Analyze
- Explain
- Propose
- Do not modify files unless explicitly requested

When asked to implement:
- Make the smallest correct change
- Follow the architecture
- Test the change
- Report what changed

Never assume permission to expand the scope.