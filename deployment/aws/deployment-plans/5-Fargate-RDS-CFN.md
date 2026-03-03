## Fargate Deployment with RDS through CLoudFormation (CFN)

### 1. Create Stack with CFN
Use template [VPC-FARGATE-RDS.yaml](../deployment/aws/CFN-templates/VPC-FARGATE-RDS.yaml)

This creates a VPC, RDS Postgres DB, Task Definition, ECS Service and ECS Cluster. The service has a property `EnableExecuteCommand: true` that will allow a user to connect to the container to run scripts once setup

### 2. Initialise Database

Through the console connect to the container and set up the database. The script `dev_initialize_db.py` is in the container app code

```
export SUPERUSER=postgres
export PASSWORD=postgrespassword
export HOST=nutrition-rds-instance.c0hiwqyoiube.us-east-1.rds.amazonaws.com
export PORT=5432

python -m app.database.dev_initialize_db
```

### 3. Create Load Balancer

Create Load Balancer and Target Group and attach to ECS service
* Create ALB Load Balancer - ALB type for Fargate
* Create Target Group - IP address - to communicate with IP addresses allocated by Fargate to containers, no managable EC instance
    * Make port same as container i.e 8000 in this case
* On ECS Service - Update service
* Add ALB and Target Group
* Find Service Security Group 
  * Allow inbound from ALB security group on port 8000


### 4. Update Web file

* Rebuild React distribution `npm run build`
* Update the S3 bucket 


### 5. Update R53 so the API Record points to ALB

* Route 53 is setup as follows;
  * S3 bucket is called **nutritionapptracker.com**
    * An A record with the same name - nutritionapptracker.com - is setup and routed to S3 can handle request
  * An A record is setup for the FASTAPI backend **api.nutritionapptracker.com**
* The React Website directs requests to - api.nutritionapptracker.com -
* So set the  - api.nutritionapptracker.com - needs to route to the Application Load Balancer resource