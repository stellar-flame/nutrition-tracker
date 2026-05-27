## Update Container 

```
TAG=dev-$(date +%Y%m%d-%H%M%S)
docker buildx build --platform linux/amd64,linux/arm64 --load --provenance=false -t havz/nutrition-tracker-api:$TAG .
```

## Tested container locally

#Change .env file
`$DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/nutrition_tracker`

```
#Start LocalStack and SQS Poller for the Lambda
docker-compose up poller localstack

docker run --rm -p 8000:8000 --env-file .env havz/nutrition-tracker-api:$TAG

#to exec inside the container
docker exec -it <container-d> /bin/bash 

#List all containers (including exited):
docker ps -a  
```

## Push container
docker push havz/nutrition-tracker-api:$TAG