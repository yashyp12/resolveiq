# ResolveIQ infrastructure

The MVP uses [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/)
to define the Lambda, HTTP API, DynamoDB tables, and IAM permissions in
[template.yaml](./template.yaml).

## Validate and deploy

From the repository root, with AWS SAM CLI installed and an authenticated AWS
credential provider configured:

```text
sam validate --template-file infrastructure/template.yaml
sam build --template-file infrastructure/template.yaml
sam deploy --guided --template-file infrastructure/template.yaml
```

The default deployment uses the deterministic mock provider. To use Bedrock,
provide a supported model ID and deploy with:

```text
sam deploy --parameter-overrides \
  AnalysisProvider=bedrock \
  BedrockModelId=<supported-model-id>
```

The Lambda role is granted access only to the two application tables, CloudWatch
logs through the SAM-managed basic execution policy, and
`bedrock:InvokeModel`. No AWS credentials are stored in the application.

After deployment, seed the fictional dataset using the stack outputs:

```text
$env:AWS_REGION="<region>"
$env:INCIDENTS_TABLE_NAME="ResolveIQ-Incidents"
$env:RUNBOOKS_TABLE_NAME="ResolveIQ-Runbooks"
python -m backend.seed
```

The deployment must not be used with real customer or production incident data.
