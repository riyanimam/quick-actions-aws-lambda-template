# quick-actions-aws-lambda-template

A template project for deploying AWS Lambda functions with best practices, infrastructure-as-code (Terraform), and automated code quality checks using GitHub Actions.

______________________________________________________________________

## Features

- **AWS Lambda Function**: Python 3.12 Lambda with event source mapping (SQS trigger).
- **Infrastructure as Code**: All AWS resources (Lambda, IAM, SQS, CloudWatch Logs) managed via Terraform.
- **CI/CD**: GitHub Actions pipeline for linting, formatting, and Terraform plan/apply.
- **Code Quality**: Python linting and formatting (ruff), TOML and YAML linting, Markdown formatting.
- **Best Practices**: Environment variables, tagging, log retention, and least-privilege IAM.

______________________________________________________________________

## Project Structure

```
.
├── python/
│   └── src/
│       └── base_lambda.py      # Lambda function source code
├── terraform/
│   └── lambda.tf              # Terraform for Lambda, IAM, SQS, etc.
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions pipeline
├── README.md
```

______________________________________________________________________

## Lambda Function

The Lambda function (`base_lambda.py`) provides utility actions via AWS APIs for a wide range of AWS services.\
Each action is implemented as a dedicated function, and the handler dispatches based on the event key.

**Supported actions:**

- Lambda: `delete_lambda_function`, `list_lambda_functions`
- SQS: `redrive_sqs_dlq`, `send_sqs_message`
- ECR: `get_ecr_login_and_repo_uri`, `list_ecr_repositories`
- ECS Fargate: `list_ecs_clusters`, `run_fargate_task`
- DynamoDB: `put_dynamodb_item`, `query_dynamodb`
- CloudWatch: `put_cloudwatch_metric`, `get_cloudwatch_metric_statistics`
- SNS: `publish_sns_message`, `list_sns_topics`
- S3: `upload_file_to_s3`, `list_s3_objects`
- Glue: `start_glue_job`, `get_glue_job_run`

______________________________________________________________________

## Infrastructure

Terraform provisions:

- **Lambda Function** (`example_lambda`)
- **IAM Role** for Lambda execution
- **CloudWatch Log Group** for Lambda logs
- **SQS Queue** as event source
- **Event Source Mapping** between SQS and Lambda

All resources are tagged for project and environment tracking.

______________________________________________________________________

## CI/CD Pipeline

GitHub Actions workflow (`ci.yml`) includes:

### Code Quality Stage

- Lint Python with Ruff
- Check Python formatting with Ruff Format
- Check Terraform formatting
- Lint TOML files
- Lint YAML files
- Check Markdown formatting

### Terraform Stage

- Terraform init, plan, and apply (on main branch)

______________________________________________________________________

## Getting Started

### Prerequisites

- [Python 3.12+](https://www.python.org/)
- [Terraform](https://www.terraform.io/)
- [AWS CLI](https://aws.amazon.com/cli/)
- Docker (for packaging Lambda, if needed)

### Setup

1. **Clone the repository**

   ```sh
   git clone https://github.com/your-org/quick-actions-aws-lambda-template.git
   cd quick-actions-aws-lambda-template
   ```

1. **Install Python dependencies**

   ```sh
   pip install -r requirements.txt
   ```

1. **Build Lambda deployment package**

   ```sh
   mkdir -p build
   cd python/src
   zip -r ../../build/example_lambda.zip .
   cd ../../
   ```

1. **Initialize and apply Terraform**

   ```sh
   cd terraform
   terraform init
   terraform apply
   ```

______________________________________________________________________

## Usage

The Lambda function expects an event with a key indicating the action, for example:

```json
{
  "body": "{\"event\": \"delete_lambda_function\", \"function_name\": \"target_lambda\"}"
}
```

**Supported events:**

- `delete_lambda_function`
- `redrive_sqs_dlq`
- `get_ecr_login_and_repo_uri`
- `list_lambda_functions`
- `list_ecr_repositories`
- `list_ecs_clusters`
- `run_fargate_task`
- `put_dynamodb_item`
- `query_dynamodb`
- `put_cloudwatch_metric`
- `get_cloudwatch_metric_statistics`
- `publish_sns_message`
- `list_sns_topics`
- `upload_file_to_s3`
- `list_s3_objects`
- `start_glue_job`
- `get_glue_job_run`

**Example event for running a Fargate task:**

```json
{
  "body": "{\"event\": \"run_fargate_task\", \"cluster\": \"my-cluster\", \"task_definition\": \"my-task-def\", \"subnets\": [\"subnet-xxxxxx\"]}"
}
```

Update the Lambda code or event payloads to handle your specific use cases.

______________________________________________________________________

## Customization

- **Add more Lambda actions** in `base_lambda.py`
- **Adjust Terraform** for additional AWS resources or permissions
- **Modify CI pipeline** in `.github/workflows/ci.yml` for your team's standards

______________________________________________________________________

## License

MIT License

______________________________________________________________________

## Authors

- [Riyan Imam](https://github.com/riyanimam)
