# ResolveIQ — MVP Contracts

## 1. Purpose

This document defines the contracts shared by the ResolveIQ backend, frontend, DynamoDB data layer, and Amazon Bedrock integration.

The goal is to establish stable interfaces before application implementation begins.

The MVP should prefer the smallest contract that supports the complete golden path.

---

# 2. MVP Golden Path

```text
User
  |
  v
Incident Form
  |
  v
POST /incidents/analyze
  |
  +--> Validate Input
  |
  +--> Persist Incident
  |
  +--> Retrieve Historical Evidence
  |
  +--> Retrieve Relevant Runbooks
  |
  +--> Invoke Amazon Bedrock
  |
  +--> Validate AI Response
  |
  +--> Validate Evidence References
  |
  v
Analysis Response
  |
  v
Frontend Results
  |
  v
POST /incidents/{incidentId}/runbook
  |
  +--> Invoke Bedrock
  |
  +--> Validate Runbook
  |
  +--> Persist Runbook
  |
  v
Generated Runbook
````

---

# 3. MVP API Routes

The MVP uses two primary API routes.

## 3.1 Analyze Incident

```http
POST /incidents/analyze
```

Responsibilities:

1. Validate the request.
2. Create a unique incident ID.
3. Persist the incident.
4. Retrieve historical incidents.
5. Retrieve relevant runbooks.
6. Rank the retrieved evidence deterministically.
7. Send bounded evidence to Amazon Bedrock.
8. Validate the Bedrock response.
9. Validate all evidence references.
10. Return the incident, evidence, and analysis.

---

## 3.2 Generate Runbook

```http
POST /incidents/{incidentId}/runbook
```

Responsibilities:

1. Retrieve the stored incident.
2. Retrieve the previously generated analysis.
3. Retrieve the supporting evidence.
4. Invoke Amazon Bedrock.
5. Validate the generated runbook.
6. Persist the runbook.
7. Return the generated runbook.

---

## 3.3 Optional Future Route

This route is not required for the initial MVP.

```http
GET /incidents/{incidentId}
```

It may be added later if the frontend requires page refresh or retrieving an existing incident.

---

# 4. API Request Contract

## 4.1 POST /incidents/analyze

Request body:

```json
{
  "title": "EC2 application server unreachable",
  "description": "Application server stopped responding after deployment.",
  "environment": "production-like",
  "service": "application-server",
  "error": "connection timeout"
}
```

### Required Fields

```text
title
description
environment
```

### Optional Fields

```text
service
error
```

---

## 4.2 Request Field Rules

### title

Type:

```text
string
```

Required:

```text
yes
```

Constraints:

* Must not be empty.
* Maximum length: 200 characters.

---

### description

Type:

```text
string
```

Required:

```text
yes
```

Constraints:

* Must not be empty.
* Maximum length: 3000 characters.

---

### environment

Type:

```text
string
```

Required:

```text
yes
```

Constraints:

* Must not be empty.
* Maximum length: 100 characters.

---

### service

Type:

```text
string
```

Required:

```text
no
```

Maximum length:

```text
100 characters
```

---

### error

Type:

```text
string
```

Required:

```text
no
```

Maximum length:

```text
1000 characters
```

---

# 5. Analyze Response Contract

Successful response:

```json
{
  "incident": {
    "incidentId": "INC-001",
    "title": "EC2 application server unreachable",
    "description": "Application server stopped responding after deployment.",
    "environment": "production-like",
    "service": "application-server",
    "error": "connection timeout"
  },
  "evidence": [
    {
      "evidenceId": "HIST-014",
      "type": "historical_incident",
      "title": "Application server timeout",
      "source": "Historical Incident",
      "summary": "Similar timeout occurred after deployment.",
      "relevanceScore": 8
    }
  ],
  "analysis": {
    "category": "network",
    "likelyCauses": [
      {
        "cause": "Network connectivity issue",
        "confidence": 0.78,
        "evidenceIds": [
          "HIST-014"
        ]
      }
    ],
    "similarIncidents": [
      "HIST-014"
    ],
    "recommendedChecks": [
      "Check network connectivity.",
      "Verify DNS resolution.",
      "Verify application service availability."
    ],
    "uncertainty": "The root cause is not confirmed from the available evidence."
  }
}
```

---

# 6. Evidence Contract

Every piece of retrieved evidence must have a stable identifier.

## Historical Incident Evidence

```json
{
  "evidenceId": "HIST-014",
  "type": "historical_incident",
  "title": "Application server timeout",
  "source": "Historical Incident",
  "summary": "Similar timeout occurred after deployment.",
  "relevanceScore": 8
}
```

## Runbook Evidence

```json
{
  "evidenceId": "RB-003",
  "type": "runbook",
  "title": "Application Server Connectivity Troubleshooting",
  "source": "Runbook",
  "summary": "Troubleshooting workflow for application connectivity issues.",
  "relevanceScore": 6
}
```

---

# 7. Evidence Rules

The backend must enforce the following rules:

1. Every evidence item must have a unique stable ID.
2. Only retrieved records may be sent to Bedrock.
3. Evidence count must be bounded.
4. The current incident must not be returned as historical evidence.
5. The model must not receive unrestricted database access.
6. The model may reference only evidence IDs included in its context.
7. Every evidence ID returned by the model must be validated by Lambda.
8. Unknown evidence IDs must cause validation failure.
9. No evidence must be fabricated by the model.

---

# 8. Evidence Limits

The initial MVP should use small fixed limits.

```text
Maximum historical incidents retrieved: 30
Maximum historical incidents sent to Bedrock: 5

Maximum runbooks retrieved: 10
Maximum runbooks sent to Bedrock: 3
```

The exact limits may be tuned after testing.

---

# 9. Deterministic Retrieval Contract

Retrieval is performed by backend application logic.

Bedrock must not perform the primary retrieval operation.

The retrieval component receives:

```json
{
  "title": "EC2 application server unreachable",
  "description": "Application server stopped responding after deployment.",
  "environment": "production-like",
  "service": "application-server",
  "error": "connection timeout"
}
```

The retrieval component returns:

```json
{
  "historicalIncidents": [],
  "runbooks": []
}
```

---

# 10. Retrieval Scoring

The initial retrieval implementation may use deterministic scoring.

Suggested scoring model:

```text
Service match                 +3
Category match                +3
Matching tag                  +2
Matching symptom              +2
Title/description token match +1
Error token match             +1
```

The exact weights may be adjusted during implementation.

The retrieval system must provide:

* Stable ordering.
* Deterministic results.
* Maximum result count.
* Clear empty-result behavior.

---

# 11. Bedrock Analysis Contract

Amazon Bedrock receives:

```text
Current incident facts
+
Bounded historical evidence
+
Bounded runbook evidence
```

The model must return structured analysis.

Expected structure:

```json
{
  "category": "network",
  "likelyCauses": [
    {
      "cause": "Network connectivity issue",
      "confidence": 0.78,
      "evidenceIds": [
        "HIST-014"
      ]
    }
  ],
  "similarIncidents": [
    "HIST-014"
  ],
  "recommendedChecks": [
    "Check network connectivity.",
    "Verify DNS resolution."
  ],
  "uncertainty": "Root cause is not confirmed."
}
```

---

# 12. Bedrock Analysis Rules

The model must:

1. Analyze only the supplied incident and evidence.
2. Treat retrieved records as reference data.
3. Distinguish facts from inference.
4. Provide uncertainty when evidence is insufficient.
5. Reference supporting evidence IDs.
6. Avoid claiming a root cause is confirmed without sufficient evidence.
7. Return the required structured fields.
8. Avoid generating infrastructure-changing commands or actions.

The model must not:

* Query DynamoDB directly.
* Execute AWS commands.
* Modify infrastructure.
* Modify IAM.
* Restart services.
* Change networking.
* Delete resources.
* Perform automatic remediation.

---

# 13. Confidence Contract

Confidence must be represented as a number between:

```text
0.0
```

and:

```text
1.0
```

Example:

```json
{
  "cause": "DNS resolution issue",
  "confidence": 0.72,
  "evidenceIds": [
    "HIST-007",
    "RB-002"
  ]
}
```

Confidence represents the model's assessment based on available evidence.

It must not be represented as a guarantee that the suspected cause is correct.

---

# 14. Uncertainty Contract

Every analysis response must contain:

```json
{
  "uncertainty": "..."
}
```

Examples:

```text
The root cause is not confirmed from the available evidence.
```

or:

```text
No sufficiently similar historical evidence was found.
```

---

# 15. AI Response Validation

Lambda must validate the Bedrock response before returning it.

Validation must check:

* Required fields exist.
* JSON structure is valid.
* Confidence values are within 0.0–1.0.
* Evidence IDs exist in the retrieved evidence set.
* Similar incident IDs exist in the retrieved evidence set.
* Strings do not exceed defined limits.
* Arrays do not exceed defined limits.

Invalid AI output must not be returned as a successful analysis.

---

# 16. Runbook Generation Contract

Endpoint:

```http
POST /incidents/{incidentId}/runbook
```

The endpoint receives the incident ID from the URL.

Bedrock receives:

```text
Original incident
+
Validated analysis
+
Supporting evidence
+
Recommended diagnostic checks
```

---

# 17. Runbook Response Contract

Example:

```json
{
  "runbook": {
    "runbookId": "RB-GEN-001",
    "title": "Application Server Connectivity Troubleshooting",
    "problem": "Application server is unreachable.",
    "preconditions": [
      "Confirm the affected application server.",
      "Confirm the issue is reproducible."
    ],
    "diagnosticSteps": [
      "Check network connectivity.",
      "Verify DNS resolution.",
      "Verify application service status."
    ],
    "verification": [
      "Confirm the application endpoint is reachable.",
      "Confirm the application responds normally."
    ],
    "remediation": [
      "Apply the approved corrective action after verification."
    ],
    "escalation": [
      "Escalate to the appropriate infrastructure team if unresolved."
    ]
  }
}
```

---

# 18. Runbook Rules

Generated runbooks must:

* Be based on the incident and validated evidence.
* Reuse supporting evidence where applicable.
* Clearly identify diagnostic steps.
* Separate diagnostics from remediation.
* Require human approval for remediation.
* Avoid unsupported claims.
* Avoid automatic infrastructure actions.

---

# 19. DynamoDB Data Model

The MVP will use two DynamoDB tables.

```text
Incidents
Runbooks
```

A single-table design is intentionally not required for the MVP.

---

# 20. Incidents Table

Table name:

```text
ResolveIQ-Incidents
```

Primary key:

```text
incidentId
```

Example item:

```json
{
  "incidentId": "INC-001",
  "title": "EC2 application server unreachable",
  "description": "Application server stopped responding after deployment.",
  "environment": "production-like",
  "service": "application-server",
  "error": "connection timeout",
  "createdAt": "2026-09-17T12:00:00Z",
  "status": "analyzed"
}
```

---

# 21. Historical Incident Records

Historical fictional incidents may use the same Incidents table.

Example:

```json
{
  "incidentId": "HIST-014",
  "recordType": "historical",
  "title": "Application server timeout",
  "description": "Application became unreachable after deployment.",
  "environment": "production-like",
  "service": "application-server",
  "category": "network",
  "symptoms": [
    "connection timeout",
    "application unreachable"
  ],
  "resolution": "Validated network connectivity and corrected routing configuration.",
  "tags": [
    "ec2",
    "network",
    "timeout"
  ],
  "createdAt": "2026-08-10T10:00:00Z"
}
```

Historical data must be fictional or anonymized.

---

# 22. Runbooks Table

Table name:

```text
ResolveIQ-Runbooks
```

Primary key:

```text
runbookId
```

Example item:

```json
{
  "runbookId": "RB-001",
  "recordType": "curated",
  "title": "Application Server Connectivity Troubleshooting",
  "problem": "Application server cannot be reached.",
  "preconditions": [
    "Confirm incident scope."
  ],
  "diagnosticSteps": [
    "Check network connectivity.",
    "Verify DNS resolution.",
    "Verify application service status."
  ],
  "verification": [
    "Confirm application endpoint is reachable."
  ],
  "remediation": [
    "Apply the approved corrective action."
  ],
  "escalation": [
    "Escalate to the appropriate infrastructure team if unresolved."
  ],
  "createdAt": "2026-08-15T10:00:00Z"
}
```

---

# 23. Generated Runbooks

Generated runbooks may use the same Runbooks table.

Example:

```json
{
  "runbookId": "RB-GEN-001",
  "recordType": "generated",
  "sourceIncidentId": "INC-001",
  "title": "Application Server Connectivity Troubleshooting",
  "problem": "Application server is unreachable.",
  "preconditions": [],
  "diagnosticSteps": [],
  "verification": [],
  "remediation": [],
  "escalation": [],
  "createdAt": "2026-09-17T12:15:00Z"
}
```

---

# 24. Error Response Contract

All API errors should use a consistent structure.

Example:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Title and description are required."
  }
}
```

---

# 25. Standard Error Codes

Initial error codes:

```text
INVALID_REQUEST
INCIDENT_NOT_FOUND
ANALYSIS_FAILED
BEDROCK_ERROR
INVALID_AI_RESPONSE
EVIDENCE_VALIDATION_FAILED
RUNBOOK_GENERATION_FAILED
DATABASE_ERROR
INTERNAL_ERROR
```

---

# 26. HTTP Status Mapping

```text
400 → INVALID_REQUEST
404 → INCIDENT_NOT_FOUND
422 → INVALID_AI_RESPONSE / EVIDENCE_VALIDATION_FAILED
500 → DATABASE_ERROR / INTERNAL_ERROR
502 → BEDROCK_ERROR
503 → ANALYSIS_FAILED / RUNBOOK_GENERATION_FAILED
```

The exact mapping may be adjusted during implementation.

---

# 27. Input and Output Safety Limits

Initial limits:

```text
Incident title:        200 characters
Description:          3000 characters
Environment:           100 characters
Service:               100 characters
Error message:        1000 characters

Historical evidence sent to Bedrock: 5 records
Runbooks sent to Bedrock:            3 records

Likely causes:        maximum 5
Similar incidents:    maximum 5
Recommended checks:   maximum 10
Evidence items:       maximum 8
```

These limits are intended to control cost, latency, and response size.

---

# 28. Environment Configuration

The following values must not be hardcoded where deployment configuration is more appropriate.

Example:

```text
AWS_REGION
BEDROCK_MODEL_ID
INCIDENTS_TABLE_NAME
RUNBOOKS_TABLE_NAME
LOG_LEVEL
```

Secrets and AWS credentials must never be committed to Git.

---

# 29. AWS Permissions

The backend should use least-privilege IAM permissions.

The Lambda execution role should be limited to the operations required for the MVP.

Conceptually:

```text
DynamoDB:
- Read required incident records
- Write incident records
- Read required runbooks
- Write generated runbooks

Bedrock:
- Invoke the selected model

CloudWatch:
- Write application logs
```

No unrestricted administrative AWS permissions should be granted.

---

# 30. Contract Ownership

The responsibilities are divided as follows:

## Frontend

Responsible for:

* Collecting user input.
* Calling the API.
* Displaying validated responses.
* Separating facts, evidence, inference, and recommendations.

## API Gateway

Responsible for:

* HTTP routing.
* Forwarding requests to Lambda.

## Lambda

Responsible for:

* Validation.
* Persistence.
* Retrieval.
* Scoring.
* Bedrock invocation.
* Response validation.
* Evidence validation.
* Error handling.

## DynamoDB

Responsible for:

* Incident persistence.
* Historical incident storage.
* Runbook persistence.

## Amazon Bedrock

Responsible for:

* Evidence-based incident analysis.
* Explicit runbook generation.

Bedrock is not responsible for:

* Database retrieval.
* Authorization.
* Infrastructure changes.
* Deterministic business logic.

---

# 31. MVP Completion Criteria

The contracts are considered implemented when:

* [ ] API request schema is defined.
* [ ] API response schema is defined.
* [ ] Error response schema is defined.
* [ ] Evidence schema is defined.
* [ ] Analysis schema is defined.
* [ ] Runbook schema is defined.
* [ ] DynamoDB tables are defined.
* [ ] Historical incident structure is defined.
* [ ] Evidence validation rules are defined.
* [ ] Input/output limits are defined.
* [ ] API route responsibilities are defined.

---

# 32. Contract Change Rule

Any change to:

* API routes
* Request/response fields
* Evidence structure
* Bedrock analysis schema
* Runbook schema
* DynamoDB keys
* Required fields
* Safety constraints

must be reflected in this document before dependent implementation is changed.

The implementation should follow this document as the current MVP contract.

---

# 33. Design Principle

ResolveIQ should optimize for:

```text
Simple architecture
        +
Deterministic retrieval
        +
Bounded evidence
        +
Structured Bedrock output
        +
Server-side validation
        +
Human-controlled remediation
```

The MVP must prioritize a reliable evidence-based incident analysis workflow over optional architectural complexity.

````

### Your only task now

Create:

```text
docs/
├── implementation-plan.md
├── requirements.md
└── mvp-contracts.md
````

 