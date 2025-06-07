#!/bin/bash
set -e

# Clean previous build
rm -rf build
mkdir -p build

# Package the Lambda function code
cd python/src
zip -r ../../build/example_lambda.zip . -x "__pycache__/*" "*.pyc"
cd ../../

echo "Build complete: build/example_lambda.zip"