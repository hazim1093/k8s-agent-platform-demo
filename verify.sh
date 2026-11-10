#!/usr/bin/env bash
curl_gw() { kubectl -n agentgateway-system run "c-$RANDOM" --rm -i --restart=Never --quiet --image=curlimages/curl:8.23.0 -- curl -s "$@"; }
LLM=http://ai-gateway.agentgateway-system.svc.cluster.local:8080/llm/v1/chat/completions

kubectl -n agentgateway-system wait --for=condition=Programmed gateway/ai-gateway
kubectl -n kagent wait --for=condition=Ready agents.kagent.dev --all
curl_gw "$LLM" -H 'content-type: application/json' -d '{"model":"default","messages":[{"role":"user","content":"Repeat: my card is 4111 1111 1111 1111"}]}'
