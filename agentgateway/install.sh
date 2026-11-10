#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"

helm upgrade -i agentgateway-crds oci://cr.agentgateway.dev/charts/agentgateway-crds --version v1.7.0 -n agentgateway-system --create-namespace
helm upgrade -i agentgateway oci://cr.agentgateway.dev/charts/agentgateway --version v1.7.0 -n agentgateway-system -f values.yaml --wait

kubectl apply -f gateway.yaml -f llm/ -f embeddings/ -f tracing.yaml
