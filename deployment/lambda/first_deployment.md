### Deploy Lambda - AI Nutritional Lookup
The lambda does the AI lookup for nutritional info. It the call the fast API on a internal url to update the results in the postgres db

```
docker run --rm --platform linux/amd64 \
  --entrypoint /bin/bash \
  -v "$PWD":/var/task \
  -w /var/task/lambdas/nutrition_ai \
  public.ecr.aws/lambda/python:3.12 \
  -lc "
    rm -rf .build lambda.zip &&
    mkdir -p .build &&
    pip install -r requirements.txt -t .build &&
    cp lambda_function.py .build/ &&
    mkdir -p .build/common &&
    cp -r ../../common/* .build/common/ &&
    cd .build &&
    python -m zipfile -c ../lambda.zip .
  "
```

