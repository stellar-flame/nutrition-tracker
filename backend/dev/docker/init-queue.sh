#!/usr/bin/env bash
set -euo pipefail

echo "Creating SQS queue in LocalStack..."
awslocal sqs create-queue --queue-name meal_processing_queue >/dev/null || true
echo "Done."