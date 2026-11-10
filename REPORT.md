# Report

Fill in after deploying: paste `./verify.sh` output and `pytest tests/` results.

## Checks

| Phase | Check | Result |
|---|---|---|
| 0 | context, cluster-admin, Gateway API CRDs, StorageClass, capacity | |
| 1 | control plane Ready, Gateway Programmed, proxy Service | |
| 2 | kagent controller/UI Ready, CRDs, DB connection, pgvector | |
| 3 | completion via /llm, card number masked, 429 on limit | |
| 4 | petstore pods ok, kube-system denied, patch needs approval | |
| 5 | findByStatus returns data | |
| 6 | 5 tools via gateway, ops confirm_order denied, direct call blocked | |
| 7 | find dog, prepare → confirm, injection resisted | |
| 8 | single nested trace in Langfuse, no PII | |
| 9 | sub=alice at tool, "for Bob" still alice | |
| 10 | DeepEval suite | |

## Schema deviations

- agentgateway has no v2.3; the standalone control plane is v1.x. Used v1.7.0 (`agentgateway.dev/v1alpha1`). Proxy Service is ClusterIP.
- LLM rate limit is 60k tokens/min; requests with `x-ratelimit-demo: true` use a 50 tokens/min bucket to demo 429.
- Agent identity at the gateway uses per-agent API keys (`apiKeyAuthentication`, metadata `agent`), tool authz by `apiKey.agent`.
- MCP backend selects Services by namespace (kmcp Service has no labels).
- kagent 0.10.6 (`kagent.dev/v1alpha2`), not 1.0.0: 1.0 needs K8s 1.37+ and Agent Substrate (gVisor, extra charts, kubectl-ate). Agents use `runtime: python` for compaction.
- Bundled kagent tool server disabled (cluster-admin); ops agent uses its own kagent-tools release with read-only Role in `petstore`.
- Ops memory uses an `embeddings` ModelConfig through the gateway (`/embeddings`, own backend). kagent needs a placeholder `OPENAI_API_KEY` secret for the gateway ModelConfigs.
- agentgateway tracing is an AgentgatewayPolicy. Langfuse runs in cluster (chart 1.5.41, last v3 line).
- Phase 9 uses route `/mcp/petstore-user` and agent `petstore-assistant-user` with `allowedHeaders: [Authorization]`; agent identity via `X-Agent-Authorization` API key; token exchange via `backend.auth.oauthTokenExchange`.

## Known gaps

- kagent-tools calls do not go through agentgateway.
- kagent sends `dimensions=768` with every embeddings request. `baai/bge-base-en-v1.5` rejects it (400, no matryoshka support), so the demo uses `perplexity/pplx-embed-v1-0.6b` (also accepts it: `qwen/qwen3-embedding-8b`, `openai/text-embedding-3-small`).
- The kind node needs about 8 GB: at 6 GB the agentgateway controller loses leader election and crash-loops, so config changes do not reach the proxy.
- Prompt guard masks ship dates and long numbers (shown as `<PHONE_NUMBER>`). The cheap model sometimes garbles order ids in its reply.
- Langfuse: gateway spans are separate roots in the agent trace, not nested.
- Keycloak 26.8 gives no `act` claim without preview features; actor is the gateway-set `x-agent-actor` header.
- Petstore does not check order ownership; production API must check `sub`.
- NetworkPolicy needs an enforcing CNI.
- petstore-mcp quotes are in memory: 1 replica. Gateway MCP sessions work across gateway replicas with selector-based targets.
- Prompt guard does not mask streamed responses.
- Nothing has run on a cluster yet; A2A tool-call parsing in tests is based on kagent source.

## Resource usage

```
kubectl top pods -n agentgateway-system; kubectl top pods -n kagent; kubectl top pods -n petstore; kubectl top pods -n observability
```

## Next steps for production

Managed Postgres, HA gateway and assistant replicas, shared quote store, Langfuse retention policy, Keycloak hardening (real DB, TLS, token-exchange with `act`), Petstore ownership checks.
