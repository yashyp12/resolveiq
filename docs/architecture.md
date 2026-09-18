# ResolveIQ architecture

## Runtime path

```text
Browser
  |
  v
API Gateway HTTP API
  |
  v
Lambda: backend.api.lambda_handler
  |                         \
  v                          v
DynamoDB                  Amazon Bedrock
ResolveIQ-Incidents       optional real provider
ResolveIQ-Runbooks
  |
  v
CloudWatch Logs
```

The static frontend is deliberately framework-free. Its API origin is
configured in [frontend/config.js](../frontend/config.js), so hosting it does
not require a second application runtime.

## Analyze flow

`POST /incidents/analyze` validates the three required incident fields,
persists the current incident, scans bounded fictional historical records and
curated runbooks, and ranks them using deterministic field/token scoring.
Only the bounded evidence is supplied to the configured analysis adapter.
The response validator rejects unknown evidence IDs, invalid confidence values,
and malformed model output.

## Runbook flow

`POST /incidents/{incidentId}/runbook` requires a user-supplied successful
resolution. The Lambda retrieves the incident and bounded evidence, invokes
the Bedrock runbook adapter when `ANALYSIS_PROVIDER=bedrock`, or uses the
deterministic mock adapter otherwise. The structured runbook is validated and
persisted in the runbooks table.

ResolveIQ never executes the recommended checks or remediation. Generated
runbooks are guidance for human review.

## Infrastructure

[infrastructure/template.yaml](../infrastructure/template.yaml) defines:

* Two PAY_PER_REQUEST DynamoDB tables with simple partition keys.
* One Python 3.12 Lambda function.
* One API Gateway HTTP API with the two POST routes.
* Lambda basic logging permissions.
* Table CRUD permissions limited to the two application tables.
* `bedrock:InvokeModel` permission for the configured model provider.

No queues, databases beyond DynamoDB, vector search, or production-control
services are required by the MVP.
