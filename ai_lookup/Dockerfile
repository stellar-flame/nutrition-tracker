FROM public.ecr.aws/lambda/python:3.12 AS builder

WORKDIR /var/task

COPY requirements.txt .
RUN pip install -r requirements.txt -t .

COPY lambda_function.py .
COPY jobs/ jobs/

RUN python -m zipfile -c /lambda.zip .

# --- Final stage: just copy the zip out ---
FROM scratch
COPY --from=builder /lambda.zip /