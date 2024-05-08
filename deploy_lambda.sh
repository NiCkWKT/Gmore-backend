#!/bin/bash
# Deploy the lambda function
# Usage: ./deploy_lambda.sh <path_to_requirements.txt> <layer_name> <function_name>
# Note: The zip file should be in the same directory as this script
# Note: The function name should be the name of the lambda function

set -e

# Check if the function name and zip file are provided
if [ $# -ne 3 ]; then
    echo "Usage: ./deploy_lambda.sh <path_to_requirements.txt> <layer_name> <function_name>"
    exit 1
fi

# Set the path to the requirements file
requirements_file=$1
layer_name=$2

# Package the lambda layer
echo "Packaging the lambda layer..."
mkdir -p python
pip3 install \
    --platform manylinux2014_x86_64 \
    --target="./python" \
    --implementation cp \
    --python-version 3.12 \
    --only-binary=:all: \
    -r $requirements_file

# Zip the lambda layer
zip -r $layer_name.zip ./python

# Deploy the lambda layer
echo "Deploying the lambda layer..."
LAYER_VERSION_ARN=$(aws lambda publish-layer-version \
    --layer-name $layer_name \
    --description "Lambda layer for $layer_name" \
    --license-info "MIT" \
    --zip-file fileb://$layer_name.zip \
    --compatible-runtimes python3.12 \
    --output text --query LayerVersionArn)

echo "Lambda layer $layer_name deployed with ARN: $LAYER_VERSION_ARN"

# Package FastAPI
echo "Packaging the lambda function..."
cd app
zip -r ../lambda_function.zip *
cd ..

DIR=$(pwd)
echo "Current directory: $DIR"

# Set the function name
function_name=$3
function_zip="lambda_function.zip"

# Deploy the lambda function
echo "Deploying the lambda function..."
FUNCTION_ARN=$(aws lambda create-function \
    --function-name $function_name \
    --runtime python3.12 \
    --package-type "Zip" \
    --handler main.handler --publish \
    --zip-file fileb://$function_zip \
    --layers $LAYER_VERSION_ARN \
    --role arn:aws:iam::815752282021:role/LambdaToDynamoRole \
    --output text --query FunctionArn)

echo "Lambda function $function_name deployed with ARN: $FUNCTION_ARN"
echo "Done."

