resource "aws_lambda_function" "example_lambda" {
  function_name = "example_lambda"
  filename      = "build/example_lambda.zip"
  handler       = "base_lambda.lambda_handler"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_exec.arn

  source_code_hash = filebase64sha256("build/example_lambda.zip")

  environment {
    variables = {
      ENV = "production"
    }
  }

  tags = {
    Project     = "QuickActions"
    Environment = "Production"
  }
}

resource "aws_cloudwatch_log_group" "example_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.example_lambda.function_name}"
  retention_in_days = 14

  tags = {
    Project     = "QuickActions"
    Environment = "Production"
    Owner       = "DevOps"
  }
}

resource "aws_lambda_event_source_mapping" "example_lambda_event" {
  event_source_arn  = aws_sqs_queue.example_queue.arn
  function_name     = aws_lambda_function.example_lambda.arn
  enabled           = true
  batch_size        = 10
  starting_position = "LATEST"
}

resource "aws_sqs_queue" "example_queue" {
  name = "example-lambda-event-queue"

  tags = {
    Project     = "QuickActions"
    Environment = "Production"
  }
}
