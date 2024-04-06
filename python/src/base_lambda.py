import json
import os
import time
import concurrent
import concurrent.futures
import itertools

from aws_lambda_powertools.shared.types import JSONType
from aws_lambda_powertools.utilities.typing import LambdaContext

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# Boto3 Retry Formula: seconds_to_sleep_i = min(b * r^i, MAX_BACKOFF=20 seconds)
# https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
aws_client_config = Config(
    connect_timeout=10,
    read_timeout=10,
    retries={"max_attempts": 4, "mode": "standard"}
)


def lambda_handler(payload: JSONType, context:LambdaContext):
    return