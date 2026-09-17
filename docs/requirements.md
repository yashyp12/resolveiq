# ResolveIQ — Requirements

## 1. Project Overview

ResolveIQ is an evidence-first IT incident analysis assistant.

The system accepts an IT incident reported by a user, retrieves relevant historical incidents and runbooks, and uses Amazon Bedrock to produce a structured analysis.

The goal is to help an engineer move from:

> Incident → Evidence → Diagnosis → Recommended Checks → Reusable Runbook

ResolveIQ is a hackathon MVP and is not intended to perform automatic production remediation.

---

## 2. Problem Statement

IT and infrastructure teams frequently investigate incidents using:

- Previous incident tickets
- Historical resolutions
- Internal runbooks
- Troubleshooting knowledge
- Engineer experience

The same or similar incidents may repeatedly require manual investigation.

ResolveIQ should reduce this investigation effort by combining historical evidence with AI-assisted analysis.

The system must prioritize evidence and clearly distinguish between:

1. Facts provided in the current incident
2. Evidence retrieved from historical records
3. AI-generated inference
4. Recommended diagnostic actions

AI-generated conclusions must not be presented as confirmed facts unless supported by the available evidence.

---

## 3. Target Users

The primary user is an IT, cloud, infrastructure, or service-desk engineer investigating an incident.

The MVP is designed for a single-user demonstration and does not require enterprise multi-tenancy.

---

## 4. MVP Goal

The MVP must demonstrate one complete working workflow:

1. User submits an incident.
2. Incident is validated.
3. Incident is persisted.
4. Relevant historical incidents and runbooks are retrieved.
5. Retrieved evidence is provided to Amazon Bedrock.
6. Bedrock generates a structured incident analysis.
7. The application displays:
   - Incident category
   - Likely causes
   - Confidence
   - Supporting evidence
   - Similar incidents
   - Recommended diagnostic checks
   - Uncertainty
8. User can generate a reusable runbook from the analysis.
9. Generated runbook is persisted and displayed.

The golden path must work reliably before optional features are implemented.

---

## 5. Functional Requirements

### FR-01 — Incident Submission

The system shall allow a user to submit an incident containing:

- Title
- Description
- Environment
- Optional service
- Optional error message

Example:

```text
Title:
EC2 application server unreachable

Description:
Application server stopped responding after a deployment.

Environment:
Production-like demo environment

Service:
Application Server

Error:
Connection timeout
````

The application shall reject clearly invalid or empty required input.

---

### FR-02 — Incident Persistence

Submitted incidents shall be persisted using Amazon DynamoDB.

Each incident should have a unique identifier.

Example:

```json
{
  "incidentId": "INC-001",
  "title": "EC2 application server unreachable",
  "description": "Application server stopped responding after a deployment.",
  "environment": "production-like",
  "service": "application-server",
  "error": "connection timeout"
}
```

---

### FR-03 — Historical Incident Retrieval

The system shall retrieve relevant historical incidents from the curated fictional dataset.

Historical records should contain structured information such as:

* Incident ID
* Category
* Service
* Symptoms
* Resolution
* Tags

The MVP shall use simple deterministic retrieval such as:

* Keyword matching
* Tag overlap
* Service/category matching
* Basic relevance scoring

The MVP shall not require a vector database.

---

### FR-04 — Runbook Retrieval

The system shall retrieve relevant existing runbooks when they are applicable to the submitted incident.

Runbooks should contain information such as:

* Runbook ID
* Title
* Problem
* Preconditions
* Diagnostic steps
* Verification
* Remediation guidance
* Escalation guidance

---

### FR-05 — Evidence Collection

Retrieved historical incidents and runbooks shall be represented as evidence.

Each evidence item shall have a stable identifier.

Example:

```json
{
  "evidenceId": "INC-014",
  "type": "historical_incident",
  "title": "Application server timeout",
  "source": "Historical Incident",
  "summary": "Similar timeout occurred after deployment."
}
```

The system shall limit the amount of evidence sent to the AI model.

---

### FR-06 — AI Incident Analysis

Amazon Bedrock shall analyze the submitted incident together with retrieved evidence.

The analysis should produce structured information including:

* Incident category
* Likely causes
* Confidence
* Evidence references
* Similar incidents
* Recommended diagnostic checks
* Uncertainty

The model must reference available evidence IDs when supporting a conclusion.

The model must not invent historical incidents, runbooks, evidence, or confirmed root causes.

---

### FR-07 — Evidence-First Response

The UI shall clearly distinguish between:

#### Incident Facts

Information directly supplied by the user.

#### Historical Evidence

Information retrieved from the ResolveIQ knowledge base.

#### AI Inference

Potential causes inferred by the model.

#### Recommended Actions

Diagnostic checks suggested for the engineer.

The system should communicate uncertainty when the evidence is insufficient.

---

### FR-08 — Analysis Display

The frontend shall display the analysis in a clear and readable format.

At minimum, the result should show:

```text
Incident
├── Category
├── Likely Causes
│   ├── Cause
│   └── Confidence
├── Supporting Evidence
├── Similar Incidents
├── Recommended Diagnostic Checks
└── Uncertainty
```

---

### FR-09 — Runbook Generation

The user shall be able to explicitly request a runbook from a completed incident analysis.

Amazon Bedrock shall generate a structured runbook based on:

* Original incident
* Retrieved evidence
* Analysis
* Recommended diagnostic checks

The runbook should contain:

* Title
* Problem
* Preconditions
* Diagnostic steps
* Verification
* Remediation guidance
* Rollback/escalation notes

---

### FR-10 — Runbook Persistence

Generated runbooks shall be persisted so that they can be reused as future knowledge.

The MVP may store short runbooks in DynamoDB.

Amazon S3 should only be introduced if a concrete requirement for file/object storage emerges.

---

### FR-11 — No Automatic Remediation

ResolveIQ shall not automatically modify infrastructure.

The system shall not:

* Restart production services
* Modify EC2 instances
* Change security groups
* Modify IAM permissions
* Execute arbitrary AWS commands
* Perform production remediation

Recommended actions are informational and require human execution.

---

## 6. Non-Functional Requirements

### NFR-01 — Simplicity

The implementation shall prioritize a working MVP over architectural complexity.

The preferred core architecture is:

```text
Frontend
   |
   v
API Gateway
   |
   v
Lambda
   | \
   |  \
   v   v
DynamoDB  Amazon Bedrock
```

CloudWatch shall provide basic application logging.

Amazon S3 and AWS Amplify may be added when they provide a concrete MVP benefit.

---

### NFR-02 — Security

The application shall:

* Never hardcode AWS credentials.
* Never commit secrets to Git.
* Use IAM permissions following least privilege.
* Avoid real customer or company incident data.
* Use fictional/anonymized demonstration data.
* Restrict AI/tool access to required capabilities.

---

### NFR-03 — Reliability

The backend shall handle:

* Invalid input
* Empty retrieval results
* DynamoDB errors
* Bedrock errors
* Bedrock timeout/failure
* Invalid model output
* API errors

Errors should return controlled responses rather than exposing internal implementation details.

---

### NFR-04 — AI Output Validation

AI-generated structured responses should be validated before being returned to the frontend.

The application shall not blindly trust model output.

Invalid or incomplete model responses should produce a controlled error or fallback response.

---

### NFR-05 — Traceability

Every AI-supported conclusion should be traceable to the available incident facts or retrieved evidence where applicable.

Evidence references should remain identifiable in the final response.

---

### NFR-06 — Performance

The MVP should keep retrieval bounded and send only a small, relevant set of evidence records to Bedrock.

The system should avoid unnecessary model calls.

---

## 7. Data Requirements

The initial demonstration dataset shall consist of fictional/anonymized data.

Target initial dataset:

* 20–30 historical incidents
* 5–10 runbooks

Historical incidents should cover common infrastructure scenarios such as:

* Application unavailable
* EC2 connectivity issues
* DNS problems
* High CPU
* Disk space issues
* Authentication failures
* Service failures
* Network connectivity problems
* Deployment-related incidents

The dataset should be curated to demonstrate meaningful evidence retrieval.

---

## 8. AWS Requirements

The MVP shall use AWS services meaningfully.

### Required Services

* Amazon Bedrock
* AWS Lambda
* Amazon DynamoDB
* Amazon API Gateway

### Supporting Services

* Amazon CloudWatch

### Optional Services

* Amazon S3
* AWS Amplify

Optional services shall not be introduced if they increase implementation complexity without improving the demonstrated workflow.

---

## 9. MCP Requirements

MCP is an optional enhancement and must not block the MVP.

If implemented, MCP should expose narrowly scoped tools such as:

```text
search_incidents
get_incident
search_runbooks
get_runbook
```

Potential write capability:

```text
create_runbook
```

MCP tools must use:

* Strict input schemas
* Bounded responses
* Explicit permissions
* No arbitrary AWS access
* No unrestricted DynamoDB access
* No infrastructure mutation

MCP should only be implemented after the core ResolveIQ workflow is stable.

---

## 10. AI Behavior Requirements

### AI-01 — Evidence-Based Reasoning

The AI must base its analysis on:

* The current incident
* Retrieved historical incidents
* Retrieved runbooks

It must not assume that an inferred cause is confirmed.

---

### AI-02 — Explicit Uncertainty

When evidence is insufficient, the AI should clearly indicate uncertainty.

Example:

```text
Confidence: Medium

Reason:
The incident resembles two historical incidents involving
application-server connectivity, but there is insufficient
evidence to confirm the root cause.
```

---

### AI-03 — Evidence References

AI-generated causes should reference the evidence items that support them.

Example:

```text
Likely Cause:
Network connectivity issue

Confidence:
0.78

Supporting Evidence:
- INC-014
- INC-021
```

The model must not invent evidence IDs.

---

### AI-04 — Structured Output

The backend should request a structured response from Amazon Bedrock.

A conceptual response format is:

```json
{
  "category": "network",
  "likelyCauses": [
    {
      "cause": "Network connectivity issue",
      "confidence": 0.78,
      "evidenceIds": ["INC-014", "INC-021"]
    }
  ],
  "similarIncidents": [
    "INC-014",
    "INC-021"
  ],
  "recommendedChecks": [
    "Check network connectivity",
    "Verify DNS resolution",
    "Verify service availability"
  ],
  "uncertainty": "Root cause is not confirmed."
}
```

The exact schema may evolve during implementation while preserving the evidence-first requirements.

---

## 11. API Requirements

The backend API should provide the minimum endpoints required for the MVP.

A possible API structure is:

```text
POST /incidents
GET  /incidents/{incidentId}
POST /incidents/{incidentId}/analyze
POST /incidents/{incidentId}/runbook
```

The exact API structure may be simplified during implementation if a smaller design provides the same MVP functionality.

---

### POST /incidents

Creates and persists a new incident.

Request:

```json
{
  "title": "EC2 application server unreachable",
  "description": "Application server stopped responding after deployment.",
  "environment": "production-like",
  "service": "application-server",
  "error": "connection timeout"
}
```

Response should include:

* Incident ID
* Stored incident
* Status

---

### GET /incidents/{incidentId}

Returns a previously submitted incident.

---

### POST /incidents/{incidentId}/analyze

Performs:

1. Incident retrieval
2. Historical evidence retrieval
3. Runbook retrieval
4. Bedrock analysis
5. Response validation

The response should return the structured analysis.

---

### POST /incidents/{incidentId}/runbook

Generates a reusable runbook from the completed analysis.

The generated runbook shall be persisted and returned to the frontend.

---

## 12. Data Model Requirements

### Incident

Conceptual structure:

```json
{
  "incidentId": "INC-001",
  "title": "EC2 application server unreachable",
  "description": "Application server stopped responding after deployment.",
  "environment": "production-like",
  "service": "application-server",
  "error": "connection timeout",
  "category": "network",
  "createdAt": "timestamp"
}
```

---

### Historical Incident

Conceptual structure:

```json
{
  "incidentId": "HIST-014",
  "category": "network",
  "service": "application-server",
  "symptoms": [
    "connection timeout",
    "application unreachable"
  ],
  "resolution": "Validated network connectivity and corrected routing configuration.",
  "tags": [
    "ec2",
    "network",
    "timeout"
  ]
}
```

---

### Runbook

Conceptual structure:

```json
{
  "runbookId": "RB-001",
  "title": "Application Server Connectivity Troubleshooting",
  "problem": "Application server cannot be reached.",
  "preconditions": [
    "Confirm incident scope"
  ],
  "diagnosticSteps": [
    "Check network connectivity",
    "Verify DNS resolution",
    "Verify application service status"
  ],
  "verification": [
    "Confirm application endpoint is reachable"
  ],
  "remediation": [
    "Apply the approved corrective action"
  ],
  "escalation": [
    "Escalate to the appropriate infrastructure team if unresolved"
  ]
}
```

---

## 13. Frontend Requirements

The frontend shall provide a simple interface for the MVP.

### Required UI Components

#### Incident Form

Fields:

* Title
* Description
* Environment
* Service
* Error message

Action:

```text
Analyze Incident
```

---

#### Analysis View

Display:

* Incident details
* Category
* Likely causes
* Confidence
* Evidence
* Similar incidents
* Recommended checks
* Uncertainty

---

#### Runbook Action

Provide an explicit action:

```text
Generate Runbook
```

The generated runbook should be displayed in a readable format.

---

### Frontend Principles

The UI should prioritize:

* Clarity
* Evidence visibility
* Simple navigation
* Useful error messages
* Fast interaction

The MVP does not require a complex dashboard.

---

## 14. AWS Architecture Requirements

The initial architecture should remain intentionally simple.

```text
                     +------------------+
                     |    Frontend      |
                     |   Web Interface  |
                     +--------+---------+
                              |
                              v
                     +------------------+
                     |   API Gateway    |
                     +--------+---------+
                              |
                              v
                     +------------------+
                     |     Lambda       |
                     |------------------|
                     | Validation       |
                     | Retrieval        |
                     | Bedrock Calls    |
                     | Response Shape   |
                     +----+--------+----+
                          |        |
                          v        v
                    +---------+  +---------+
                    | DynamoDB|  | Bedrock |
                    +---------+  +---------+

                       CloudWatch
                      Basic Logging
```

Amazon S3 may be introduced later when there is a concrete requirement for object/file storage.

AWS Amplify may be used for frontend hosting when the frontend is ready for deployment.

---

## 15. Retrieval Requirements

The retrieval system should remain lightweight.

### Initial Retrieval Strategy

Use deterministic matching based on:

* Service
* Category
* Tags
* Keywords
* Symptoms

A basic relevance score may be calculated.

Example:

```text
Service match       +3
Category match      +3
Tag match           +2
Keyword match       +1
Symptom match       +1
```

The exact scoring algorithm may change during implementation.

The system should return only the top relevant records.

---

### Retrieval Constraints

The MVP shall not require:

* Vector embeddings
* Vector database
* OpenSearch
* Bedrock Knowledge Bases
* Document chunking pipeline
* Background indexing jobs

These may be considered future enhancements only after demonstrating a need for them.

---

## 16. Logging and Observability Requirements

Basic logging shall be implemented using Amazon CloudWatch.

Logs should help identify:

* Request received
* Incident ID
* Retrieval result count
* Bedrock invocation
* Success/failure status
* Validation failures
* Exceptions

Sensitive information should not be unnecessarily written to logs.

The MVP does not require:

* Advanced dashboards
* Distributed tracing
* Custom metrics platform
* Complex alerting
* Multi-service observability architecture

---

## 17. Security Requirements

### Credentials

AWS credentials must never be hardcoded in source code.

Use:

* IAM roles
* Environment configuration
* AWS CLI credential mechanisms
* Appropriate AWS identity mechanisms

---

### IAM

Permissions should follow least privilege.

For example:

Lambda should only have permissions required to:

* Read/write required DynamoDB tables
* Invoke the required Bedrock model
* Write logs to CloudWatch

The application must not grant unrestricted AWS administrative permissions.

---

### Data

The project must use:

* Fictional data
* Synthetic data
* Anonymized examples

The project must not use:

* Real customer incident tickets
* Confidential company data
* Production credentials
* Internal secrets
* Private infrastructure details

---

## 18. Error Handling Requirements

The system should gracefully handle:

### Invalid Request

```text
400 Bad Request
```

Example:

```json
{
  "error": "Title and description are required."
}
```

---

### Incident Not Found

```text
404 Not Found
```

---

### Bedrock Failure

The backend should return a controlled error rather than exposing internal model or AWS details.

Example:

```json
{
  "error": "Incident analysis is temporarily unavailable."
}
```

---

### Empty Evidence

The system should still provide an analysis while explicitly indicating that supporting historical evidence was not found.

Example:

```text
Historical evidence:
No sufficiently similar incidents were found.

Confidence:
Low
```

---

### Invalid AI Response

If the model returns invalid structured data:

1. Detect the invalid response.
2. Do not return malformed data to the frontend.
3. Return a controlled error or safe fallback.

---

## 19. Testing Requirements

The MVP should test the primary workflow and important failure conditions.

### Core Tests

* Incident submission
* Incident persistence
* Historical retrieval
* Runbook retrieval
* Bedrock analysis
* Evidence references
* Structured output validation
* Runbook generation
* Runbook persistence

### Failure Tests

* Missing title
* Missing description
* Unknown incident ID
* No matching evidence
* DynamoDB failure
* Bedrock failure
* Invalid Bedrock response
* API failure
* Frontend network failure

Testing should focus on the golden path first.

---

## 20. Deployment Requirements

The application should ultimately run using AWS-managed services.

Minimum deployment target:

```text
Frontend
   ↓
API Gateway
   ↓
Lambda
   ├── DynamoDB
   └── Amazon Bedrock
```

CloudWatch should provide basic logs.

The deployment should be repeatable enough for the hackathon demonstration.

Infrastructure-as-code should be introduced only when it can be completed without delaying the working MVP.

---

## 21. MCP Requirements

MCP is an optional enhancement and must not block completion of the MVP.

A possible MCP layer may expose:

```text
search_incidents
get_incident
search_runbooks
get_runbook
```

An optional write operation may be:

```text
create_runbook
```

MCP must:

* Use strict schemas
* Limit response sizes
* Validate inputs
* Restrict access
* Avoid arbitrary AWS operations
* Avoid unrestricted DynamoDB access
* Never perform infrastructure mutation

MCP should demonstrate genuine tool-mediated retrieval rather than simply wrapping existing functions without additional value.

---

## 22. AI Agent / Autonomous Behavior Constraints

ResolveIQ shall not operate as an unrestricted autonomous infrastructure agent.

The AI may:

* Analyze incidents
* Compare evidence
* Identify possible causes
* Recommend diagnostics
* Generate runbooks

The AI may not:

* Modify infrastructure
* Execute arbitrary shell commands
* Modify IAM
* Change security groups
* Restart production systems
* Delete cloud resources
* Change network configuration
* Perform unapproved remediation

Human engineers remain responsible for executing any remediation.

---

## 23. Out of Scope

The following are explicitly outside the MVP:

* Kubernetes
* Docker-based microservices
* Complex event-driven architecture
* Message queues
* Vector databases
* OpenSearch
* Bedrock Knowledge Bases
* Multiple autonomous agents
* Automatic infrastructure remediation
* Real ServiceNow integration
* Real customer/company data
* Multi-region deployment
* Disaster recovery architecture
* Enterprise multi-tenancy
* Complex authentication and authorization
* Custom model training
* Fine-tuning
* Advanced analytics dashboards
* Mobile application
* Large-scale document ingestion
* Complex streaming responses
* General-purpose workflow engines
* Broad MCP tool catalogs
* Production-scale HA architecture

---

## 24. Hackathon MVP Priorities

The project should be developed according to the following priority order.

### Priority 1 — Golden Path

```text
Submit Incident
      ↓
Persist Incident
      ↓
Retrieve Evidence
      ↓
Bedrock Analysis
      ↓
Display Results
```

---

### Priority 2 — Reusable Knowledge

```text
Analysis
   ↓
Generate Runbook
   ↓
Persist Runbook
```

---

### Priority 3 — AWS Deployment

```text
Frontend
   ↓
API Gateway
   ↓
Lambda
   ├── DynamoDB
   └── Bedrock
```

---

### Priority 4 — Reliability

Handle:

* Validation
* API errors
* AWS errors
* Bedrock failures
* Invalid model output
* Empty evidence

---

### Priority 5 — Optional Enhancements

Only after the core MVP is stable:

* MCP
* S3
* Amplify
* Additional AWS services
* UI polish

Optional features must never delay completion of the golden path.

---

## 25. Definition of Done

The ResolveIQ MVP is considered complete when all of the following are true:

* [ ] User can submit an incident.
* [ ] Required input is validated.
* [ ] Incident is persisted in DynamoDB.
* [ ] Historical incidents can be retrieved.
* [ ] Existing runbooks can be retrieved.
* [ ] Evidence is identified with stable IDs.
* [ ] Amazon Bedrock analyzes the incident.
* [ ] AI output is structured.
* [ ] AI output is validated.
* [ ] Likely causes are displayed.
* [ ] Confidence is displayed.
* [ ] Evidence references are displayed.
* [ ] Similar incidents are displayed.
* [ ] Recommended diagnostic checks are displayed.
* [ ] Uncertainty is displayed.
* [ ] User can generate a runbook.
* [ ] Runbook is persisted.
* [ ] Runbook is displayed.
* [ ] Basic CloudWatch logging works.
* [ ] Important error cases are handled.
* [ ] No real company/customer data is used.
* [ ] No credentials or secrets are committed.
* [ ] No automatic infrastructure remediation exists.
* [ ] Core workflow is deployed on AWS.
* [ ] The final demo can demonstrate one complete working workflow.

---

## 26. Success Criteria

The project should clearly demonstrate:

```text
                 RESOLVEIQ

              IT INCIDENT
                   |
                   v
           +---------------+
           |   Retrieval   |
           +-------+-------+
                   |
                   v
             +-----------+
             |  Evidence |
             +-----+-----+
                   |
                   v
            +-------------+
            |   Bedrock   |
            |   Analysis  |
            +------+------+ 
                   |
          +--------+---------+
          |        |         |
          v        v         v
       Causes   Evidence   Checks
          |        |         |
          +--------+---------+
                   |
                   v
            Generate Runbook
                   |
                   v
            Reusable Knowledge
```

The primary objective is to demonstrate a reliable, evidence-first incident analysis workflow using AWS and Amazon Bedrock.

The project should prioritize:

1. Working functionality
2. Evidence traceability
3. Meaningful AWS usage
4. Clear AI behavior
5. Reliable demonstration
6. Simple architecture
7. Scope discipline

The project should not prioritize unnecessary architectural complexity over completing the core workflow.

````

After pasting, **save `requirements.md`**. Your `docs` folder should then contain both:

```text
docs/
├── implementation-plan.md
└── requirements.md
````

 