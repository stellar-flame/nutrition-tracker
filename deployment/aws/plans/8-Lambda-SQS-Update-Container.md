## Deploy Lambda

Use docker to create zip to upload function

* lambda code in lambdas folder
* common code between app and lambda in common. Can probably move this into lambda now that local environ uses localstack


```
docker run --rm --platform linux/amd64 \
  --entrypoint /bin/bash \
  -v "$PWD":/var/task \
  -w /var/task/lambdas/nutrition_ai \
  public.ecr.aws/lambda/python:3.12 \
  -lc "
    rm -rf .build lambda.zip &&
    mkdir -p .build &&
    pip install -r requirements.txt -t .build &&
    cp lambda_function.py .build/ &&
    mkdir -p .build/common &&
    cp -r ../../common/* .build/common/ &&
    cd .build &&
    python -m zipfile -c ../lambda.zip .
  "
```

Test Lambda with: 

```
{
  "Records": [
    {
      "body": "{\"meal_description\":\"banana\",\"meal_id\":1}"
    }
  ]
}
```

**Configure environment variables:**

OPENAI_API_KEY
INTERNAL_TOKEN
INTERNAL_API_URL

## Create Standard SQS queue

Test with:

```
{
  "meal_description": "banana",
  "meal_id": "1"
}
```


## Update Container 

```
set TAG dev-$(date +%Y%m%d-%H%M%S)
docker buildx build --platform linux/amd64,linux/arm64 --load --provenance=false -t havz/nutrition-tracker-api:$TAG .
docker push havz/nutrition-tracker-api:$TAG
```

**Tested container locally**
```
#Start LocalStack and SQS Poller for the Lambda
docker-compose up poller localstack

docker run --rm -p 8000:8000 --env-file .env-staging havz/nutrition-tracker-api:$TAG


#to exec inside the container
docker exec -it <container-d> /bin/bash 

#List all containers (including exited):
docker ps -a  
```

## Add Parameters to parameter Store and update task definition

SQS_QUEUE_NAME
SQS_QUEUE_URL
SQS_ENDPOINT_URL

The policy for Task Execution Role listed each parameter individually.
Change policy for Task Execution Role to allow any parameters for dev:

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "ReadAppParams",
			"Effect": "Allow",
			"Action": [
				"ssm:GetParameter",
				"ssm:GetParameters",
				"ssm:GetParametersByPath"
			],
			"Resource": [
				"arn:aws:ssm:us-east-1:904570587370:parameter/nutrition/dev/*"
			]
		}
	]
}
```

### 5. Reset Database
Added a field `created_at` to meal so schema change

Use `NutritionResetDatabase` Task definition created last deployment to reset db
Remember ECS Service setting for vpc and security group same as container TaskDefinition


