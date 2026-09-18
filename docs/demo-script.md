# ResolveIQ demo script

Target duration: under three minutes.

## 1. Set the context (20 seconds)

“ResolveIQ helps an infrastructure engineer move from an incident to
evidence-backed diagnostic checks. It does not make production changes.”

## 2. Submit the incident (30 seconds)

Use fictional data:

* Title: `Checkout API returning 502`
* Description: `Users intermittently receive HTTP 502 responses from the checkout API after a deployment.`
* Environment: `production-like demo`
* Service: `checkout-api`
* Error: `HTTP 502 Bad Gateway`

Click **Analyze incident** and point out the loading and error-safe workflow.

## 3. Explain the result (55 seconds)

Show the four visual sections in order:

1. **Current incident** — facts supplied by the engineer.
2. **Historical evidence** — records retrieved by deterministic scoring.
3. **AI inference** — possible causes and confidence, not confirmed facts.
4. **Recommended checks** — diagnostic guidance requiring human execution.

Read the uncertainty statement aloud to reinforce the evidence-first behavior.

## 4. Generate the runbook (40 seconds)

Enter a fictional successful resolution, for example:

`Reverted the fictional deployment and verified that checkout requests returned HTTP 200.`

Click **Generate runbook**. Show the structured problem, diagnostics,
verification, remediation, and escalation sections. Explain that the runbook
is persisted only after the human supplies the resolution context.

## 5. Show the architecture (25 seconds)

Point to the architecture diagram: browser → API Gateway → Lambda →
DynamoDB, with Bedrock as the bounded reasoning provider and CloudWatch for
logs. Mention that the local/mock provider makes the demo deterministic when
Bedrock is not configured.
