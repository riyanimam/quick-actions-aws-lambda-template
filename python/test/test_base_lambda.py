from unittest import mock
import json

import src.base_lambda as base_lambda


@mock.patch("src.base_lambda.boto3.client")
def test_delete_lambda_function_calls_boto3(mock_boto_client):
    mock_lambda = mock.Mock()
    mock_boto_client.return_value = mock_lambda
    mock_lambda.delete_function.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 204}
    }

    resp = base_lambda.delete_lambda_function("my-func")
    mock_boto_client.assert_called_once_with(
        "lambda", config=base_lambda.aws_client_config
    )
    mock_lambda.delete_function.assert_called_once_with(FunctionName="my-func")
    assert resp == {"ResponseMetadata": {"HTTPStatusCode": 204}}


@mock.patch("src.base_lambda.boto3.client")
def test_redrive_sqs_dlq_moves_messages(mock_boto_client):
    mock_sqs = mock.Mock()
    mock_boto_client.return_value = mock_sqs
    messages = [
        {"Body": "msg1", "ReceiptHandle": "rh1"},
        {"Body": "msg2", "ReceiptHandle": "rh2"},
    ]
    mock_sqs.receive_message.return_value = {"Messages": messages}

    result = base_lambda.redrive_sqs_dlq("source_url", "dlq_url", max_messages=2)

    mock_boto_client.assert_called_once_with(
        "sqs", config=base_lambda.aws_client_config
    )
    mock_sqs.receive_message.assert_called_once_with(
        QueueUrl="dlq_url", MaxNumberOfMessages=2, WaitTimeSeconds=2
    )
    assert mock_sqs.send_message.call_count == 2
    assert mock_sqs.delete_message.call_count == 2
    mock_sqs.send_message.assert_any_call(QueueUrl="source_url", MessageBody="msg1")
    mock_sqs.send_message.assert_any_call(QueueUrl="source_url", MessageBody="msg2")
    mock_sqs.delete_message.assert_any_call(QueueUrl="dlq_url", ReceiptHandle="rh1")
    mock_sqs.delete_message.assert_any_call(QueueUrl="dlq_url", ReceiptHandle="rh2")
    assert result == {"redriven": 2}


@mock.patch("src.base_lambda.boto3.client")
def test_redrive_sqs_dlq_no_messages(mock_boto_client):
    mock_sqs = mock.Mock()
    mock_boto_client.return_value = mock_sqs
    mock_sqs.receive_message.return_value = {}

    result = base_lambda.redrive_sqs_dlq("source_url", "dlq_url")
    assert result == {"redriven": 0}
    mock_sqs.send_message.assert_not_called()
    mock_sqs.delete_message.assert_not_called()


@mock.patch("src.base_lambda.boto3.client")
def test_get_ecr_login_and_repo_uri(mock_boto_client):
    mock_ecr = mock.Mock()
    mock_boto_client.return_value = mock_ecr
    mock_ecr.get_authorization_token.return_value = {
        "authorizationData": [
            {"authorizationToken": "token123", "proxyEndpoint": "https://ecr.aws"}
        ]
    }
    mock_ecr.describe_repositories.return_value = {
        "repositories": [
            {"repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo"}
        ]
    }

    result = base_lambda.get_ecr_login_and_repo_uri("my-repo")
    assert result == {
        "repository_uri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo",
        "auth_token": "token123",
        "proxy_endpoint": "https://ecr.aws",
    }


@mock.patch("src.base_lambda.delete_lambda_function")
@mock.patch("src.base_lambda.json")
def test_lambda_handler_delete_lambda_function(mock_json, mock_delete):
    payload = {"body": json.dumps("delete_lambda_function")}
    mock_json.loads.return_value = "delete_lambda_function"
    context = mock.Mock()
    base_lambda.lambda_handler(payload, context)
    mock_delete.assert_called_once_with("function_name_here")


@mock.patch("src.base_lambda.redrive_sqs_dlq")
@mock.patch("src.base_lambda.json")
def test_lambda_handler_redrive_sqs_dlq(mock_json, mock_redrive):
    payload = {"body": json.dumps("redrive_sqs_dlq")}
    mock_json.loads.return_value = "redrive_sqs_dlq"
    context = mock.Mock()
    base_lambda.lambda_handler(payload, context)
    mock_redrive.assert_called_once_with("source_queue_url_here", "dlq_url_here")


@mock.patch("src.base_lambda.get_ecr_login_and_repo_uri")
@mock.patch("src.base_lambda.json")
def test_lambda_handler_get_ecr_login_and_repo_uri(mock_json, mock_get_ecr):
    payload = {"body": json.dumps("get_ecr_login_and_repo_uri")}
    mock_json.loads.return_value = "get_ecr_login_and_repo_uri"
    context = mock.Mock()
    base_lambda.lambda_handler(payload, context)
    mock_get_ecr.assert_called_once_with("repository_name_here")


@mock.patch("src.base_lambda.json")
def test_lambda_handler_invalid_event(mock_json):
    payload = {"body": json.dumps("unknown_event")}
    mock_json.loads.return_value = "unknown_event"
    context = mock.Mock()
    result = base_lambda.lambda_handler(payload, context)
    assert result == "Invalid or no event received"
