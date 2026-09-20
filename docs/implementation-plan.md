# ResolveIQ implementation status

This document records the MVP work that is implemented and deployed. It is
intended to distinguish completed scope from deferred ideas.

## Completed foundation

- Repository structure, documentation, tests, and fictional demo data.
- Typed incident, historical incident, curated runbook, and generated runbook
  records.
- DynamoDB persistence for `ResolveIQ-Incidents` and `ResolveIQ-Runbooks`.
- Deterministic bounded retrieval of historical incidents and curated runbooks.

## Completed backend

- `POST /incidents/analyze`
  - Validates input.
  - Persists the incident.
  - Retrieves bounded evidence.
  - Invokes Amazon Bedrock.
  - Validates structured analysis and evidence references.
  - Persists the validated analysis.
  - Returns facts, evidence, inference, checks, and uncertainty.
- `POST /incidents/{incidentId}/runbook`
  - Validates the submitted resolution.
  - Retrieves the incident, validated analysis, and bounded evidence.
  - Invokes Bedrock.
  - Validates and persists a generated runbook.
  - Preserves the exact submitted resolution.
- Explicit API errors for invalid input, provider failures, malformed model
  output, and missing incidents.

## Completed frontend

- Framework-free HTML, CSS, and JavaScript incident form.
- Loading and error states.
- Current incident facts, historical evidence, AI inference, confidence,
  recommended checks, and uncertainty display.
- Explicit empty/no-match evidence state.
- Runbook generation and structured runbook display.
- Live API configuration in `frontend/config.js`.

## Completed deployment

- Backend deployed with AWS SAM / CloudFormation to stack `resolveiq` in
  `us-east-1`.
- API Gateway, Lambda, DynamoDB, Bedrock, and CloudWatch Logs are active.
- Frontend deployed as an S3 static website:
  `http://resolveiq-frontend-089781651236.s3-website-us-east-1.amazonaws.com/`.
- The frontend public URL is HTTP. CloudFront and HTTPS frontend hosting are
  not deployed.
- The live provider is Bedrock with model
  `us.amazon.nova-2-lite-v1:0`.

## Verification completed

- 45 automated Python tests pass.
- Python compilation, JavaScript syntax, SAM validation, and diff checks pass.
- Live analysis and runbook endpoints return successfully.
- Headless Chrome verifies the deployed incident-to-analysis-to-runbook
  workflow.
- The browser verifies loading, empty evidence, uncertainty, runbook, and
  submitted-resolution behavior.

## Deferred scope

The following are intentionally not implemented:

- MCP or multi-agent orchestration.
- Vector databases, embeddings, or a separate RAG service.
- Authentication and multi-tenant access control.
- Real ServiceNow or production infrastructure integration.
- Automatic remediation or infrastructure-changing actions.
- Kubernetes, queues, additional databases, or CloudFront.

## Next priorities, if the project continues

1. Add authentication before use beyond a public demo.
2. Improve demo data management and retrieval while preserving evidence
   traceability.
3. Add HTTPS hosting only if a production-style public URL is required.
4. Expand observability and repeatable frontend deployment automation.

These are future improvements, not current acceptance criteria.
