#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"

kubectl apply -f petstore/
docker build -t petstore-mcp:0.1.0 petstore-mcp
kind load docker-image petstore-mcp:0.1.0 --name "${KIND_CLUSTER:-kind}"
