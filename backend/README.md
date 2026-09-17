# ResolveIQ backend data layer

## Minimal runtime

The MVP backend uses Python 3.12 and `boto3`. It intentionally has no web
framework or additional service layer yet: the repository can be called by the
future Lambda handler, while its table dependencies are injectable for local
tests. AWS credentials are supplied by the standard boto3 credential chain and
are never stored in this repository.

Install dependencies from the repository
[requirements.txt](../requirements.txt). The DynamoDB table definitions are in
[table_definitions.json](./table_definitions.json).

## Data layout

`ResolveIQ-Incidents` uses `incidentId` as its partition key and stores both
current incidents (`recordType: incident`) and fictional historical records
(`recordType: historical`). `ResolveIQ-Runbooks` uses `runbookId` as its
partition key and stores curated and generated runbooks using their respective
record types.

The seed command writes 24 historical incidents and 7 curated runbooks:

```text
python -m backend.seed
```

Optional environment variables are `AWS_REGION`, `INCIDENTS_TABLE_NAME`, and
`RUNBOOKS_TABLE_NAME`. The tables must exist before running the seed command.
