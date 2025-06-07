from aws_lambda_powertools.shared.types import JSONType
from aws_lambda_powertools.utilities.typing import LambdaContext
import json
import boto3

from botocore.config import Config

aws_client_config = Config(
    connect_timeout=10, read_timeout=10, retries={"max_attempts": 4, "mode": "standard"}
)


# Lambda
def delete_lambda_function(function_name: str):
    client = boto3.client("lambda", config=aws_client_config)
    response = client.delete_function(FunctionName=function_name)
    return response


def list_lambda_functions():
    client = boto3.client("lambda", config=aws_client_config)
    return client.list_functions()


# SQS
def redrive_sqs_dlq(source_queue_url: str, dlq_url: str, max_messages: int = 10):
    sqs = boto3.client("sqs", config=aws_client_config)
    messages = sqs.receive_message(
        QueueUrl=dlq_url, MaxNumberOfMessages=max_messages, WaitTimeSeconds=2
    ).get("Messages", [])

    for msg in messages:
        sqs.send_message(QueueUrl=source_queue_url, MessageBody=msg["Body"])
        sqs.delete_message(QueueUrl=dlq_url, ReceiptHandle=msg["ReceiptHandle"])
    return {"redriven": len(messages)}


def send_sqs_message(queue_url: str, message_body: str):
    sqs = boto3.client("sqs", config=aws_client_config)
    return sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)


# ECR
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


def list_ecr_repositories():
    ecr = boto3.client("ecr", config=aws_client_config)
    return ecr.describe_repositories()


# ECS Fargate
def list_ecs_clusters():
    ecs = boto3.client("ecs", config=aws_client_config)
    return ecs.list_clusters()


def run_fargate_task(cluster: str, task_definition: str, subnets: list):
    ecs = boto3.client("ecs", config=aws_client_config)
    return ecs.run_task(
        cluster=cluster,
        launchType="FARGATE",
        taskDefinition=task_definition,
        networkConfiguration={
            "awsvpcConfiguration": {"subnets": subnets, "assignPublicIp": "ENABLED"}
        },
    )


# DynamoDB
def put_dynamodb_item(table_name: str, item: dict):
    dynamodb = boto3.client("dynamodb", config=aws_client_config)
    return dynamodb.put_item(TableName=table_name, Item=item)


def query_dynamodb(table_name: str, key_expr: str, expr_attr_values: dict):
    dynamodb = boto3.client("dynamodb", config=aws_client_config)
    return dynamodb.query(
        TableName=table_name,
        KeyConditionExpression=key_expr,
        ExpressionAttributeValues=expr_attr_values,
    )


# CloudWatch
def put_cloudwatch_metric(namespace: str, metric_name: str, value: float):
    cloudwatch = boto3.client("cloudwatch", config=aws_client_config)
    return cloudwatch.put_metric_data(
        Namespace=namespace, MetricData=[{"MetricName": metric_name, "Value": value}]
    )


def get_cloudwatch_metric_statistics(
    namespace: str,
    metric_name: str,
    dimensions: list,
    start_time,
    end_time,
    period: int,
    statistics: list,
):
    cloudwatch = boto3.client("cloudwatch", config=aws_client_config)
    return cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=statistics,
    )


# SNS
def publish_sns_message(topic_arn: str, message: str):
    sns = boto3.client("sns", config=aws_client_config)
    return sns.publish(TopicArn=topic_arn, Message=message)


def list_sns_topics():
    sns = boto3.client("sns", config=aws_client_config)
    return sns.list_topics()


# S3
def upload_file_to_s3(local_file: str, bucket: str, key: str):
    s3 = boto3.client("s3", config=aws_client_config)
    return s3.upload_file(local_file, bucket, key)


def list_s3_objects(bucket: str):
    s3 = boto3.client("s3", config=aws_client_config)
    return s3.list_objects_v2(Bucket=bucket)


# Glue
def start_glue_job(job_name: str):
    glue = boto3.client("glue", config=aws_client_config)
    return glue.start_job_run(JobName=job_name)


def get_glue_job_run(job_name: str, run_id: str):
    glue = boto3.client("glue", config=aws_client_config)
    return glue.get_job_run(JobName=job_name, RunId=run_id)


def lambda_handler(payload: JSONType, context: LambdaContext):
    event = json.loads(payload["body"])

    if event == "delete_lambda_function":
        delete_lambda_function("function_name_here")
    elif event == "redrive_sqs_dlq":
        redrive_sqs_dlq("source_queue_url_here", "dlq_url_here")
    elif event == "get_ecr_login_and_repo_uri":
        get_ecr_login_and_repo_uri("repository_name_here")
    elif event == "list_lambda_functions":
        return list_lambda_functions()
    elif event == "list_ecr_repositories":
        return list_ecr_repositories()
    elif event == "list_ecs_clusters":
        return list_ecs_clusters()
    elif event == "run_fargate_task":
        run_fargate_task(
            "cluster_name_here", "task_definition_here", ["subnet_id_here"]
        )
    elif event == "put_dynamodb_item":
        put_dynamodb_item("table_name_here", {"key": {"S": "value"}})
    elif event == "query_dynamodb":
        return query_dynamodb(
            "table_name_here", "key_expr_here", {"key": {"S": "value"}}
        )
    elif event == "put_cloudwatch_metric":
        put_cloudwatch_metric("namespace_here", "metric_name_here", 1.0)
    elif event == "get_cloudwatch_metric_statistics":
        return get_cloudwatch_metric_statistics(
            "namespace_here",
            "metric_name_here",
            [],
            "start_time_here",
            "end_time_here",
            60,
            ["Average"],
        )
    elif event == "publish_sns_message":
        publish_sns_message("topic_arn_here", "message_here")
    elif event == "list_sns_topics":
        return list_sns_topics()
    elif event == "upload_file_to_s3":
        upload_file_to_s3("local_file_path_here", "bucket_name_here", "key_here")
    elif event == "list_s3_objects":
        return list_s3_objects("bucket_name_here")
    elif event == "start_glue_job":
        start_glue_job("job_name_here")
    elif event == "get_glue_job_run":
        return get_glue_job_run("job_name_here", "run_id_here")
    else:
        return "Invalid or no event received"
