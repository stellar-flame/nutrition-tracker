## Start with a Dockerfile in the project root. Example (Python/FastAPI-ish):
```FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
```

## Build and test locally:

docker build -t yourname/nutrition-tracker:latest .
docker run --rm -p 8000:8000 yourname/nutrition-tracker:latest
Hit http://localhost:8000 or your health endpoint to verify.


## Build and Push to Docker Hub:

docker login
cd backend
docker buildx build --platform linux/amd64,linux/arm64 -t username/nutrition-tracker:latest --push .


## For AWS, prefer ECR over Docker Hub (faster pulls, IAM auth). Create an ECR repo, then:

*I used DockerHub* 

aws ecr get-login-password --region <region> \
  | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com
docker tag yourname/nutrition-tracker:latest <acct>.dkr.ecr.<region>.amazonaws.com/nutrition-tracker:latest
docker push <acct>.dkr.ecr.<region>.amazonaws.com/nutrition-tracker:latest

# Deploy options on AWS: 

## 1.First deployed directly on EC2


### Install Docker Engine on EC2 Instance
sudo dnf install docker
sudo service docker start
sudo usermod -a -G docker ec2-user

LOGOUT and login

sudo su - ec2-user
docker pull username/nutrition-tracker:latest
docker run --rm -p 8000:8000 yourname/nutrition-tracker:latest

## 2. Next, deploy to ECS cluster 

* Create Cluster
  * Self Managed
* Create Task Definition 
  * Set container to 0.25 vCPU and memory to 0.5GB 
* Create Service and attach Task Definition


## 3. Next deploy to Fargate

* Create Cluster
  * Fargate Only
* Create Task Definition 
  * Set container to 0.25 vCPU and memory to 0.5GB 
* Create Service and attach Task Definition