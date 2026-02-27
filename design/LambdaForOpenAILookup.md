## Options For OpenAI infrastructure

1. Turn whole app into micoservices using AWS Lamba for all calls. Have an API Lambda that Reads from DB and then have a Worker Lambda to call OpenAI for nutritional info via SQS queue
2. Keep Fargate Container and only have a  Worker Lambda to call OpenAI for nutritional info via SQS queue
3. Keep all as id in Fargate


# 1. All Microservices
Not really suitable for a whole web app, would have too many disconnected functions

# 2. Fargate Container and only have a  Worker Lambda
Good learning excercise. Will learn about Lambda, SQS Queues and async called and will not need to wait OpenAI call

# 3. Leave as is
No Learning


## Fargate Container and only have a  Worker Lambda
Lets say we go with this for learning purposes.

All API requests go to Fargate. If the its a nutrional lookup put request on message queue (SQS - Simple Message Queue). Then worker lambda polls and does request but instead of writing to db, it send an internal msg back to API on Fargate to commit data. This allows all db transactions to be handle by API and no need to worry about connection pooling on lambda and creating RDS proxy. 

The call to the API to lookup meal and determinine nutrional value will create a blank meal in the db with pending state and place msg in queue for worker lambda. 

The worker lambda will call OpenAI to retrieve nutritional info.

It will then post back API create meal. An internal route is needed `/internal/createMeal` on API that is dependent on a specific WORKER_TOKEN that only the worker lambda  will use to post.

The UI will poll until meal is no longer pending to how results using TanStackQuery:

```
 // Poll every 3 seconds if any meal is pending/processing
    refetchInterval: (query) => {
      const meals = query.state.data;
      const hasPending = meals?.some(
        (meal) => meal.status === 'pending' || meal.status === 'processing'
      );
      return hasPending ? 3000 : false; // Poll while pending, stop when done
    },
```