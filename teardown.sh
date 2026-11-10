#!/usr/bin/env bash
helm uninstall -n kagent petstore-ops-tools kagent kagent-crds
helm uninstall -n agentgateway-system agentgateway agentgateway-crds
helm uninstall -n observability langfuse otel-collector
helm uninstall -n traefik traefik
kubectl delete ns kagent agentgateway-system observability keycloak petstore traefik --ignore-not-found
