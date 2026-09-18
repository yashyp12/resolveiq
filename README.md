# ResolveIQ

ResolveIQ is an evidence-first incident analysis MVP. It compares a fictional
current incident with deterministic historical evidence and curated runbooks,
then returns structured troubleshooting guidance through an AWS serverless
API.

## Architecture

```text
Static frontend
      |
      v
Amazon API Gateway (HTTP API)
      |
      v
AWS Lambda (Python 3.12)
      |                 \
      v                  v
DynamoDB             Amazon Bedrock
incidents + runbooks  (optional analysis provider)
      |
      v
CloudWatch Logs
```

The deployment definition is [infrastructure/template.yaml](./infrastructure/template.yaml).
It creates two on-demand DynamoDB tables, one Lambda function, an HTTP API, and
least-privilege table/Bedrock permissions. No credentials are stored in this
repository.

## Workflow

1. Submit an incident at `POST /incidents/analyze`.
2. Lambda validates and persists the incident.
3. Deterministic retrieval ranks bounded historical incidents and runbooks.
4. The mock provider or Amazon Bedrock returns validated analysis.
5. The frontend separates current facts, historical evidence, AI inference,
   recommended checks, and uncertainty.
6. Submit a human-supplied successful resolution at
   `POST /incidents/{incidentId}/runbook` to persist a reusable runbook.

Recommendations are informational. ResolveIQ never performs infrastructure
changes automatically.

## Local setup

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
python -m compileall -q backend tests
```

The local analysis provider defaults to the deterministic mock provider:

```text
ANALYSIS_PROVIDER=mock
```

The real Bedrock provider uses the standard boto3 credential chain:

```text
ANALYSIS_PROVIDER=bedrock
BEDROCK_MODEL_ID=<supported Bedrock model ID>
AWS_REGION=<AWS region>
```

The backend also accepts `INCIDENTS_TABLE_NAME`, `RUNBOOKS_TABLE_NAME`, and
`CORS_ALLOW_ORIGIN`. The default table names are `ResolveIQ-Incidents` and
`ResolveIQ-Runbooks`.

## Deployment

Install the AWS SAM CLI and configure an AWS profile or role, then run:

```text
sam validate --template-file infrastructure/template.yaml
sam build --template-file infrastructure/template.yaml
sam deploy --guided --template-file infrastructure/template.yaml
```

Use the default `AnalysisProvider=mock` deployment first. Enable Bedrock only
when the selected model is enabled in the target region:

```text
sam deploy --parameter-overrides AnalysisProvider=bedrock BedrockModelId=<model-id>
```

Seed only fictional demonstration data after the tables exist:

```text
python -m backend.seed
```

See [infrastructure/README.md](./infrastructure/README.md) for deployment
details and [backend/README.md](./backend/README.md) for the data layout.

## Frontend

The framework-free frontend is in [frontend/](./frontend/). Set
`apiBaseUrl` in [frontend/config.js](./frontend/config.js) to the deployed API
base URL before hosting the static files. It supports the incident form,
loading/error states, analysis, evidence, confidence, diagnostic checks, and
uncertainty.

## Testing and security

Run:

```text
python -m pytest -q
python -m compileall -q backend tests
git diff --check
```

The dataset is fictional/anonymized. Do not add customer tickets, production
credentials, private infrastructure details, or secrets. The Lambda role is
limited to the two DynamoDB tables, CloudWatch logging, and
`bedrock:InvokeModel`. Bedrock evidence IDs are validated server-side before
they are returned.

## Limitations

The current deployment is intentionally small: it has no authentication,
history dashboard, or static hosting resource. Runbook generation requires a
user-supplied successful resolution; it uses the configured Bedrock provider
when enabled and a deterministic local-safe generator in mock mode. AWS
deployment and real Bedrock smoke tests require an installed SAM/AWS CLI,
valid credentials, and a model enabled in the target account and region.
