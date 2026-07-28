# LLM Cost Proxy

LLM Cost Proxy is a local, OpenAI-compatible gateway that routes chat-completion requests to OpenAI or OpenRouter while recording usage and cost metadata in SQLite.

> **Status: early MVP under active development.**

## Implemented features

- OpenAI-compatible `POST /v1/chat/completions` endpoint.
- Bearer-token authentication using a local proxy API key, so provider keys stay server-side.
- OpenAI routing for ordinary model names and OpenRouter routing for models prefixed with `openrouter/`.
- Transparent forwarding of provider response bodies, status codes, and content types.
- Optional request attribution through `X-LLM-Project` and `X-LLM-Agent` headers.
- SQLite request records containing provider, model, project, agent, response status, token usage, cost, and timestamp.
- Actual-cost calculation for known models when the provider returns token usage; the current pricing catalog includes OpenAI `gpt-4o-mini`.
- Unauthenticated `GET /health` endpoint.
- API tests for health checks, authentication, and OpenAI forwarding.

## Planned features

- Pre-request token and cost estimation.
- Daily project and agent budgets, a per-request cost ceiling, and rate limiting.
- More complete and maintainable model pricing data.
- Provider failure details and rejected-request logging.
- Console, generic webhook, and Slack alerts.
- Usage and cost dashboard endpoints or a simple local dashboard.
- A Docker image and persistent data-volume setup.
- Broader test coverage, including OpenRouter routing, SQLite persistence, usage extraction, and policy enforcement.

## Architecture

```text
Client / agent
    |
    |  Authorization: Bearer <LLM_PROXY_API_KEY>
    |  POST /v1/chat/completions
    v
FastAPI application (app/main.py)
    |-- authentication and request context (app/auth.py)
    |-- settings loaded from .env (app/settings.py)
    |-- provider routing
    |     |-- regular model name ------> OpenAI
    |     `-- openrouter/<model> ------> OpenRouter
    |-- usage and cost calculation (app/pricing.py)
    `-- request metadata -------------> SQLite (app/db.py)
```

The proxy selects OpenRouter only when `model` begins with `openrouter/`; it removes that prefix before forwarding the request. All other model names are sent to OpenAI. Provider responses are returned to the client without reshaping.

## Quick start

### 1. Install

Python 3.12 or newer is recommended.

```bash
git clone <repository-url>
cd llm-fin-ops
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

### 2. Configure `.env`

Copy the example configuration:

```bash
cp .env.example .env
```

Generate a local proxy key:

```bash
python -c "import secrets; print('llmproxy_sk_' + secrets.token_urlsafe(32))"
```

Then edit `.env` and set at least the local proxy key and the provider key you intend to use:

```dotenv
LLM_PROXY_API_KEY=llmproxy_sk_replace_me
OPENAI_API_KEY=sk-replace-me
OPENROUTER_API_KEY=sk-or-replace-me
DATABASE_URL=sqlite:///./data/proxy.db
```

`OPENAI_API_KEY` is needed for ordinary model names. `OPENROUTER_API_KEY` is needed for `openrouter/...` model names. The remaining defaults are documented in `.env.example`.

### 3. Start the proxy

```bash
python run.py
```

The service listens on `http://127.0.0.1:4000`. Check it with:

```bash
curl http://127.0.0.1:4000/health
```

### 4. Send a sample request

Use the same local key configured as `LLM_PROXY_API_KEY`:

```bash
curl http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer llmproxy_sk_replace_me" \
  -H "Content-Type: application/json" \
  -H "X-LLM-Project: demo" \
  -H "X-LLM-Agent: curl" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Say hello in one sentence."}
    ]
  }'
```

To use OpenRouter, specify a prefixed model such as `openrouter/openai/gpt-4o-mini` and configure `OPENROUTER_API_KEY`.

### 5. Run tests

```bash
python -m pytest
```
