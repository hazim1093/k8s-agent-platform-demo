#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"

kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.0/standard-install.yaml

helm upgrade -i traefik traefik --repo https://traefik.github.io/charts --version 42.3.2 -n traefik --create-namespace -f traefik/values.yaml

kubectl create ns observability --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f observability/langfuse-secrets.yaml
helm upgrade -i langfuse langfuse --repo https://langfuse.github.io/langfuse-k8s --version 1.5.41 -n observability -f observability/langfuse-values.yaml
helm upgrade -i otel-collector opentelemetry-collector --repo https://open-telemetry.github.io/opentelemetry-helm-charts --version 0.178.2 -n observability -f observability/collector-values.yaml
kubectl apply -f observability/route.yaml

kubectl create ns keycloak --dry-run=client -o yaml | kubectl apply -f -
kubectl -n keycloak create secret generic keycloak-realm --from-file=petstore-realm.json=keycloak/realm-petstore.json --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f keycloak/secrets.yaml -f keycloak/keycloak.yaml
