## Fargate with RDS

### 1. Create a TaskRole

This give the container permissions that allow it to communicate with AWS resources.
In this case its needs persmission to open channels with AWS Systems Manager messaging channels (SSM Messages)
ECS Exec needs this to access the container and run scripts liking seeding and migrations

Add inline permissions to role:
```  
{
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
            "ssmmessages:CreateControlChannel",
            "ssmmessages:CreateDataChannel",
            "ssmmessages:OpenControlChannel",
            "ssmmessages:OpenDataChannel"
        ],
        "Resource": "*"
        }
    ]
}
```
    

### 2. Create Task Definition
   * Set container to 0.25 vCPU and memory to 0.5GB 
   * Add Environment Variable 
        ```
        DATABASE_URL='postgresql+psycopg2://postgres:postgres@${DBENDPOINT}:5432/${DBNAME}
        ```

### 3. Create Cluster

### 4. Create a Service with task definition
   * In the section **Troubleshooting configuration - recommended**
        * Enable 'Turn on ECS Exec' (Was hard to find') 

### 5. Once container is running connect to it and run the scripts to seed database
   * python -m app.database.seed
*I didn't actually do this step since my db was already seeded from th previous deployment*
