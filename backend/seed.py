"""Seed fictional records into the two ResolveIQ DynamoDB tables."""

import os

import boto3

from .repository import ResolveIQRepository, seed_repository
from .seed_data import curated_runbooks, historical_incidents


def main() -> None:
    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    repository = ResolveIQRepository(
        dynamodb.Table(os.getenv("INCIDENTS_TABLE_NAME", "ResolveIQ-Incidents")),
        dynamodb.Table(os.getenv("RUNBOOKS_TABLE_NAME", "ResolveIQ-Runbooks")),
    )
    seed_repository(repository, historical_incidents(), curated_runbooks())
    print("Seeded 24 historical incidents and 7 curated runbooks.")


if __name__ == "__main__":
    main()
