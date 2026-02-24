aws logs tail /ecs/nutrition-tracker --follow

aws ecs update-service \
  --cluster nutrition-ecs-cluster \
  --service nutrition-ecs-service \
  --desired-count 1

aws ecs list-tasks \
  --cluster nutrition-ecs-cluster \
  --service-name nutrition-ecs-service \
  --desired-status RUNNING