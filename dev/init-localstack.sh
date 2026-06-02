#!/usr/bin/env bash
set -euo pipefail

echo "Creating SQS queue in LocalStack..."
awslocal sqs create-queue --queue-name meal_processing_queue >/dev/null || true

echo "Creating DynamoDB PendingMeals table..."
awslocal dynamodb create-table \
  --table-name PendingMeals \
  --attribute-definitions \
      AttributeName=meal_id,AttributeType=S \
      AttributeName=user_id,AttributeType=N \
      AttributeName=date,AttributeType=S \
  --key-schema AttributeName=meal_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[{"IndexName":"UserDateIndex","KeySchema":[{"AttributeName":"user_id","KeyType":"HASH"},{"AttributeName":"date","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  >/dev/null || true

awslocal dynamodb update-time-to-live \
  --table-name PendingMeals \
  --time-to-live-specification "Enabled=true,AttributeName=ttl" \
  >/dev/null || true

echo "Done."
