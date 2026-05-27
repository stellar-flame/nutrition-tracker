## Current State

* CloudFormation deploys
    * VPC, SG, RDS, ECS-Fargate
* SQS & Lambda manually deployed
* React on CloudFront Distribution with S3 as origin
* AWS Cognito used for authentication
* Route 53 for domains:
    * nutritionapptracker.com
    * api.nutritionapptracker.com
* Certificates for domains in ACM


## Next

* **Update Route 53 when ALB is deployed**
* Use cdk or CloudFormation for more parts
* See Code-Review.md
* Fix Payload on internal route
* Write unit tests for Lambda and Queue
* Consider R53 healthcheck on domain

