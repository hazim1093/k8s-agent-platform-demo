#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"

helm upgrade -i petstore-ops-tools oci://ghcr.io/kagent-dev/tools/helm/kagent-tools --version 0.3.1 -n kagent -f petstore-ops/tools-values.yaml
kubectl apply -f petstore-ops/rbac.yaml -f petstore-ops/agent.yaml -f petstore-assistant/
