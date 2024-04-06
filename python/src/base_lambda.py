from aws_lambda_powertools.shared.types import JSONType
from aws_lambda_powertools.utilities.typing import LambdaContext

from botocore.config import Config

# Boto3 Retry Formula: seconds_to_sleep_i = min(b * r^i, MAX_BACKOFF=20 seconds)
# https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
aws_client_config = Config(
    connect_timeout=10, read_timeout=10, retries={"max_attempts": 4, "mode": "standard"}
)


def lambda_handler(payload: JSONType, context: LambdaContext):
    return
