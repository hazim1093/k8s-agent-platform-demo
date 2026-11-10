#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"

kubectl create ns kagent --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f postgres.yaml
helm upgrade -i kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds --version 0.10.6 -n kagent
helm upgrade -i kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent --version 0.10.6 -n kagent -f values.yaml -f values-tracing.yaml --wait
kubectl apply -f modelconfig-via-gateway.yaml -f route.yaml
