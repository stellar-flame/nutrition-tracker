## Made Code Change that required updated code and environment and database changes

### Feature Change: Nutritional info obtained from OpenAI

Added env var: OPENAI_API_KEY
Found error that some nutritional attr stored as int instead of float

### 1. Updated container:
```
set TAG dev-$(date +%Y%m%d-%H%M%S)
docker buildx build --platform linux/amd64,linux/arm64 --load --provenance=false -t havz/nutrition-tracker-api:$TAG .
docker push havz/nutrition-tracker-api:$TAG
```

**Tested container locally**

Useful Commands:

```
set $DATABASE_URL postgresql+psycopg2://postgres:postgres@localhost:5432/nutrition_tracker
set $OPENAI_API_KEY <OPENAI_API_KEY>
docker run --rm -d -p 8000:8000 -e DATABASE_URL=$DATABASE_URL -e OPENAI_API_KEY=$OPENAI_API_KEY havz/nutrition-tracker-api:$TAG
docker logs -f <container-id>
docker exec -it <container-d> /bin/bash #to exec inside the container
```

### 2.YAML changes
* Added OpenAI key to SSM Parameter Store 

* Added ImageTag to CFN yaml and used in TaskDefinition
* Added Policy ECSTaskRole to read OPENAI_API_KEY from Parameter Store
* Added Secrets to use OPENAI_API_KEY for container

### 3. On CFN initiated update Stack



#### Other issues:
I wanted to upgrade my db tables because I made changes to the schema. I had previously run my dev_initialize_db scipt but this INCORRECTLY create the alembic version files in the container running in AWS. This will cause the alembic version table to be out of sync if I try and run a schema version file I created and packaged in the container loacally.

I should create the versions locally and call `alembic upgrade head` on the server. So going forward, db created by CFN, and run just `alembic upgrade head` on container on ECS. 

Also added psql to your Docker image so that I can call psql from the container. Container has a TaskRole allowing me to connect to the container and run commands

Added a reset_db script to clear the tables so that I can reset the db.

Reinitialize DB:
```
python -m app.database.initialize.reset_db reset. #only if we want a clean db
alembic upgrade head
```
