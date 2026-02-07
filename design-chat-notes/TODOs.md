## Further Considerations


# 1. Fix Payload on internal route

# 2. Write integration test for failure

Use FastAPI's BackgroundTasks? Provides slightly better integration but still fire-and-forget with same exception issues

Centralize task tracking? Store active tasks in a set to prevent garbage collection warnings and enable monitoring

# 3. Next Deployment use cmd line to run task to reset db

aws ecs run-task \
  --cluster nutrition-ecs-cluster \
  --task-definition nutrition-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"


//List subnets
aws ec2 describe-subnets --filters "Name=tag:Name,Values=nutrition-public-*" --query 'Subnets[].SubnetId'

//List security groups
aws ec2 describe-security-groups --filters "Name=group-name,Values=*ECS*" --query 'SecurityGroups[].GroupId'

aws ecs run-task \
  --cluster nutrition-ecs-cluster \
  --task-definition nutrition-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "nutrition-container",
      "command": ["sh", "-c", "python -m app.database.initialize.reset_db reset && alembic upgrade head"]
    }]
  }'