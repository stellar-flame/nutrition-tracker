### Feature Change: Changed OpenAI call to be async 

Introduced concept of NutritionProvider. Made call to NutritionProvider. This is a step towards using SQS and Lambda to do the openAI call. This release however just decouples the code and makes the code async

The code asynchrously calls NutritionProvider invokes AI call to lookup nutritional value of food. Once OpenAI returns, NutritionProvider posts back to an internal URL to commit the meal to the database. It is done this way so that in future when SQS and lambda is introduced the lambda will not need access to db and I will not need to worry about connection pooling

Added env var: 
```
INTERNAL_TOKEN=<private-header-token-for-nutritionprovider-to-post>
INTERNAL_API_URL=<url-for-nutritionprovider-to-post-to>
```

Added a `status` field to meal
Fixed Dates and Times on meal
Added `created_at` on Meal - UTC time of time of meal created
`date` and `time` on meal is the date and time of meal created

### 1. Update container:
```
set TAG dev-$(date +%Y%m%d-%H%M%S)
docker buildx build --platform linux/amd64,linux/arm64 --load --provenance=false -t havz/nutrition-tracker-api:$TAG .
```

**Tested container locally**
```
docker run --rm -d -p 8000:8000 --env-file .env havz/nutrition-tracker-api:$TAG

docker logs -f  <container-id>
docker exec -it <container-d> /bin/bash #to exec inside the container
```

**Push to Docker**
```
docker push havz/nutrition-tracker-api:$TAG
```

### 2. Update CFN template 

Give TaskDefinition ExecutionRole permission to read the SSM parameters. Add new parameters to secrets of TaskDefinition

### 3. Add Parameters to Parameter Store
Update docker ImageTag 
Move DATABASE_URL to parameter store as well
Add INTERNAL_TOKEN and INTERNAL_API_URL to parameter store
For  INTERNAL_TOKEN generate secure string


### 4. Update CFN stack on AWS

### 5. Reset Database
Added a field `status` to meal so schema change

```
python -m app.database.initialize.reset_db reset
alembic upgrade head
```

Created a TaskDefintion to reset the database.
Same settings as above container and vpc and security groups as the ecs service but the cmd for the container is different

```
"sh","-c","python -m app.database.initialize.reset_db reset && alembic upgrade head"
```

### 6. Refresh frontend

* Rebuild React distribution `npm run build`
* Update the S3 bucket files 

```
npm run build

# List buckets you have access to
aws s3 ls

aws s3 sync dist/ s3://nutritionapptracker.com --delete
```