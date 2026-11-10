# k8s-agent-platform-demo

Demo: an agent platform on Kubernetes with agentgateway + kagent + kmcp, using Petstore as the app.

```
 users / ops ──A2A──▶ kagent agents (petstore-ops, petstore-assistant)
                          │  LLM + MCP calls (API key per agent)
                          ▼
                ┌──── agentgateway ────┐   auth, tool authz, rate limit, PII masking
                │ /llm        /mcp/petstore
                ▼                      ▼
          OpenRouter               petstore-mcp (kmcp) ──▶ Petstore API

 kagent + agentgateway ──OTel──▶ collector ──▶ Langfuse
 DeepEval (tests/) ──A2A──▶ agents, judge via /llm
```

| Dir | What |
|---|---|
| `infra/` | supporting services: Traefik ingress, Langfuse + OTel collector, Keycloak |
| `apps/` | Petstore API and the petstore-mcp server code |
| `agentgateway/` | gateway install, LLM backend/route/policies (`llm/`), embeddings (`embeddings/`), tracing |
| `kagent/` | kagent install, its Postgres (pgvector), ModelConfig `via-gateway`, tracing values |
| `mcp/petstore/` | MCPServer, gateway route + tool authz (`gateway/`), token exchange (`identity/`) |
| `agents/` | one dir per agent |

## Prerequisites

Docker, kind, kubectl, helm.

Secrets you provide:

- `OPENROUTER_API_KEY` (required): LLM and embedding calls via agentgateway (step 3)

All other passwords and keys are `demo` values in the manifests.

## Deploy

```
kind create cluster --config infra/kind.yaml   # 0. maps localhost:8080 to Traefik
./infra/install.sh                     # 1. Gateway API CRDs, Traefik, Langfuse + collector, Keycloak
./apps/install.sh                      # 2. Petstore, petstore-mcp image (kind load)

read -rs OPENROUTER_API_KEY   # paste key, Enter
kubectl create ns agentgateway-system
kubectl -n agentgateway-system create secret generic openrouter --from-literal=Authorization=$OPENROUTER_API_KEY
./agentgateway/install.sh              # 3. gateway, LLM route, rate limit, PII guard, tracing

./kagent/install.sh                    # 4. kagent + Postgres, ModelConfig via-gateway
kubectl apply -f kagent/modelconfig-embeddings.yaml   # petstore-ops memory, via the gateway

./mcp/install.sh                       # 5. petstore-mcp behind the gateway, agent keys
./agents/install.sh                    # 6. petstore-ops, petstore-assistant
kubectl apply -f mcp/petstore/identity/ -f agents/petstore-assistant-user/   # 7. optional identity step

./verify.sh                            # 8.
```

Order matters: kagent's ModelConfig points at the gateway (3 before 4), and the agents use the keys created by `mcp` (5 before 6).

## Use

- kagent UI: http://kagent.localhost:8080
- Langfuse: http://langfuse.localhost:8080, login `admin@example.com` / `demo1234`
- Both go through Traefik (Gateway `web` in `traefik`, NodePort 30080). Without the kind port mapping: `kubectl -n traefik port-forward svc/traefik 8080:80`
- Tests: `kubectl -n kagent port-forward svc/kagent-controller 8083` and `kubectl -n agentgateway-system port-forward svc/ai-gateway 8081:8080`, then `pip install -r tests/requirements.txt && JUDGE_BASE_URL=http://localhost:8081/llm/v1 pytest tests/`
- Manual checks: [TRY.md](TRY.md)
- Teardown: `./teardown.sh`

Notes: context memory sharing spaces as well, e.g. for product.
