# ResolveIQ three-minute demo script

Use the public demo:
`http://resolveiq-frontend-089781651236.s3-website-us-east-1.amazonaws.com/`

All values below are fictional demo data.

## 0:00–0:20 — Problem

“When an infrastructure incident happens, responders often repeat the same
investigation. They need to know what is actually observed, what prior
incidents support, and what is only an AI suggestion. They also need a safe way
to preserve a successful resolution.”

## 0:20–0:45 — What ResolveIQ does

“ResolveIQ takes an incident, compares it with a small fictional knowledge
base, and uses Amazon Bedrock to produce structured troubleshooting guidance.
The application separates facts, historical evidence, inference, and
recommended checks. It never changes infrastructure automatically.”

## 0:45–1:30 — Submit an incident and show analysis

Enter:

- Title: `Application server timeout after fictional deployment`
- Description: `The fictional application endpoint stopped responding after a demo deployment and reports a connection timeout.`
- Environment: `fictional-demo`
- Service: `application-server`
- Error: `connection timeout`

Click **Analyze incident**. Point out that the button enters a loading state.
Then show the current incident facts, category, likely causes, confidence, and
recommended diagnostic checks.

If the evidence card says **No matching historical evidence was found**, call
that out as an intentional result rather than hiding it.

## 1:30–2:10 — Evidence, inference, and uncertainty

“This card is the current incident, exactly as submitted. This card is
historical evidence retrieved by deterministic backend scoring. This section
is AI inference, so likely causes have confidence and evidence references; it
is not a confirmed root cause. These are recommended checks, not automatic
actions. The uncertainty text tells us when the available evidence is
insufficient.”

The seeded demo data is small, so an arbitrary fictional incident may have no
matching evidence. That behavior is part of the evidence-first design.

## 2:10–2:40 — Generate a runbook

Enter this resolution:

`Reviewed the fictional deployment logs, corrected the demo configuration with human approval, and verified the endpoint recovered.`

Click **Generate runbook**. Show the problem, preconditions, diagnostic steps,
verification, remediation, and escalation sections. Point out that the exact
submitted resolution appears in the remediation section and that the runbook
is persisted for reuse.

## 2:40–3:00 — Architecture and closing

“The browser loads from an S3 static website and calls API Gateway. API
Gateway invokes Lambda, which persists records in DynamoDB and sends bounded
context to Amazon Bedrock. CloudWatch receives Lambda logs. The demo runs in
us-east-1 with the Nova 2 Lite model. ResolveIQ’s principle is simple:
AI recommends, evidence supports, and humans decide.”
