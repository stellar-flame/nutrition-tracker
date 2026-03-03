### Objective

Move libs in a lambda layer and keep function light

mkdir -p dist
docker buildx build --platform linux/amd64 -f Dockerfile.layerzip -o type=local,dest=dist .
docker buildx build --platform linux/amd64 -f Dockerfile.funczip  -o type=local,dest=dist .