import json
from aws_lambda_powertools.utilities.typing import LambdaContext
import src.base_lambda as base_lambda

class DummyContext(LambdaContext):
    function_name = "test"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
    aws_request_id = "test-request-id"

def test_lambda_handler_list_lambda_functions(monkeypatch):
    # Patch the list_lambda_functions to return a known value
    monkeypatch.setattr(base_lambda, "list_lambda_functions", lambda: {"Functions": ["f1", "f2"]})
    payload = {"body": json.dumps({"event": "list_lambda_functions"})}
    context = DummyContext()
    result = base_lambda.lambda_handler(payload, context)
    assert result == {"Functions": ["f1", "f2"]}

def test_lambda_handler_query_dynamodb(monkeypatch):
    # Patch the query_dynamodb to return a known value
    monkeypatch.setattr(
        base_lambda,
        "query_dynamodb",
        lambda table, key_expr, expr_attr_values: {"Items": [{"id": {"S": "123"}}]},
    )
    payload = {"body": json.dumps({"event": "query_dynamodb"})}
    context = DummyContext()
    result = base_lambda.lambda_handler(payload, context)
    assert result == {"Items": [{"id": {"S": "123"}}]}

def test_lambda_handler_invalid_event():
    payload = {"body": json.dumps({"event": "not_a_real_event"})}
    context = DummyContext()
    result = base_lambda.lambda_handler(payload, context)
    assert result == "Invalid or no event received"