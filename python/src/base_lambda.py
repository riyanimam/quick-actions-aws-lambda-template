from aws_lambda_powertools.shared.types import JSONType
from aws_lambda_powertools.utilities.typing import LambdaContext
import json
import boto3

from botocore.config import Config

# Boto3 Retry Formula: seconds_to_sleep_i = min(b * r^i, MAX_BACKOFF=20 seconds)
# https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
aws_client_config = Config(
    connect_timeout=10, read_timeout=10, retries={"max_attempts": 4, "mode": "standard"}
)


def delete_lambda_function(function_name: str):
    client = boto3.client("lambda", config=aws_client_config)
    response = client.delete_function(FunctionName=function_name)
    return response


def redrive_sqs_dlq(source_queue_url: str, dlq_url: str, max_messages: int = 10):
    sqs = boto3.client("sqs", config=aws_client_config)
    messages = sqs.receive_message(
        QueueUrl=dlq_url, MaxNumberOfMessages=max_messages, WaitTimeSeconds=2
    ).get("Messages", [])

    for msg in messages:
        sqs.send_message(QueueUrl=source_queue_url, MessageBody=msg["Body"])
        sqs.delete_message(QueueUrl=dlq_url, ReceiptHandle=msg["ReceiptHandle"])
    return {"redriven": len(messages)}


def get_ecr_login_and_repo_uri(repository_name: str):
    ecr = boto3.client("ecr", config=aws_client_config)
    auth = ecr.get_authorization_token()
    repo = ecr.describe_repositories(repositoryNames=[repository_name])
    repo_uri = repo["repositories"][0]["repositoryUri"]
    token = auth["authorizationData"][0]["authorizationToken"]
    proxy_endpoint = auth["authorizationData"][0]["proxyEndpoint"]
    return {
        "repository_uri": repo_uri,
        "auth_token": token,
        "proxy_endpoint": proxy_endpoint,
    }


def lambda_handler(payload: JSONType, context: LambdaContext):
    event = json.loads(payload["body"])

    if event == "delete_lambda_function":
        delete_lambda_function("function_name_here")
    elif event == "redrive_sqs_dlq":
        redrive_sqs_dlq("source_queue_url_here", "dlq_url_here")
    elif event == "get_ecr_login_and_repo_uri":
        get_ecr_login_and_repo_uri("repository_name_here")
    else:
        return "Invalid or no event received"
