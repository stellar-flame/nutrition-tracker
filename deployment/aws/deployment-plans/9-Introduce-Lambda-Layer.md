### Objective

Move libs in a lambda layer and keep function light


# Build Layer
```
dist/
    layer/
        python/
        (your packages here)

rm -rf dist
mkdir dist/layer/python
cd dist
cp ../requirements.txt .

#Need to build it for linux so use Docker environ
docker run --rm \
  --platform linux/amd64 \
  -v "$PWD":/var/task \
  public.ecr.aws/sam/build-python3.12 \
  bash -lc "
    python -m pip install -U pip &&
    python -m pip install --only-binary=:all: -r requirements.txt -t layer/python &&
    cd layer &&
    zip -r /var/task/lambda-layer.zip python
  "
```


# Rebuild lighter Lambda

```
docker buildx build --platform linux/amd64 -o . .
  
```
