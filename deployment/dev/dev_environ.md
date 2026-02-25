### Startup servers
```
#Fast API - Rest API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

#LocalStack to simulate SQS queue
docker run -d -p 4566:4566 -p 4571:4571 --name localstack localstack/localstack

#Lambda to poll queue
python -m dev_tools.sqs_lambda_polling
```