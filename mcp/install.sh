#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"

kubectl apply -f petstore/ -f petstore/gateway/
