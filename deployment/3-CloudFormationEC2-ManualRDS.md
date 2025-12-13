## Deployment Using CloudFormation 

### 1. Build and test Docker image
```
docker buildx build --platform linux/amd64,linux/arm64 --load -t havz/nutrition-tracker-api:latest .

set DATABASE_URL 'postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/nutrition_tracker'

docker run --rm -d -p 8000:8000 -e DATABASE_URL=$DATABASE_URL havz/nutrition-tracker-api

docker push havz/nutrition-tracker-api
```
# note **host.docker.internal** used for docker because the container is the localhost

### 1. Created YAML template

See [deployment/aws/CFN-templates/VPCEC2Stack.yaml]

### 2. Create Stack

* AWS console CloudFormation 

### 3. Create RDS 

Through aws-console
* Create a RDS subnet Group
* Create RDS instance 
  * Postgres
  * Free Tier
  * Single Instance 
* Create a database instance - if you don't do this the db instance you will have only created the RDS instance
* Create a Security group
* Then when the RDS instance is created amend the SG to take inbound from the EC2 security group and remove the outbound 0.0.0.0/0 rule as the db does not need to talk out besides the connection it hs with EC2
  
### 4. EC2 connection to DB

* SSH to EC2 instance

```
export DATABASE_URL postgresql+psycopg2://postgres:postgres@${DBENDPOINT}:5432/${DBNAME}
```

* Run Migration Scripts
```
docker run --rm -e DATABASE_URL=$DATABASE_URL havz/nutrition-tracker-api alembic upgrade head
```
* Seed DB
  
```
docker run --rm -e DATABASE_URL="$DATABASE_URL" havz/nutrition-tracker-api python -m app.database.seed
```

* Run Container
```
docker run --rm -d -p 8000:8000 -e DATABASE_URL=$DATABASE_URL havz/nutrition-tracker-api
```

## Errors Made
Forgot to make give an db instance name when creating RDS in aws console so DB was not created
Made an SSH tunnel from my local machine to the postgres DB through EC2

An SSH tunnel is basically “local port → EC2 → RDS”
psql connects to localhost:5433, but that traffic is encrypted over SSH to EC2, and EC2 connects privately to RDS on 5432.

```
ssh -i NutritionApp.pem -L 5433:${DBENDPOINT}:5432 ec2-user@<EC2_PUBLIC_IP>
```

Breakdown:

ssh ec2-user@<EC2_PUBLIC_IP>
Opens an SSH connection to your EC2 instance.

-L 5433:DEST_HOST:DEST_PORT means:
“Listen on my laptop on local port 5433, and forward anything that hits it through this SSH connection to DEST_HOST:DEST_PORT, from the EC2 side.”

```
psql -h localhost -p 5433 -U postgres -d postgres
CREATE DATABASE nutrition_tracker;
\q
```

## Next 

* Do entire stack in CloudFormation including RDS
  