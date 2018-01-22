# academic-fyp-ddb-load-tester


## Issues

- The task definition is specified inline with the CloudFormation Lambda function, this needs updating after each deployment
- Subnet and security groups used in the Lambda Function code should be parameters 

## Building the Docker Image and pushing to ECR

```
docker build -t ddb-stress-test .
docker tag fyp-ddb-stress-test AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fyp-ddb-stress-test

aws ecr get-login --no-include-email --region us-east-1
docker push AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fyp-ddb-stress-test:latest
```