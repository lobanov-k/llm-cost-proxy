import httpx
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status
from datetime import datetime, timezone

from app.auth import RequestContext, require_proxy_auth
from app.settings import settings
from app.db import init_db, insert_request_log
from app.pricing import calculate_actual_cost

app = FastAPI()

@app.on_event("startup")
async def startup():
  init_db()

@app.get("/health")
async def health():
  return {"status": "ok"}

def resolve_provider(payload: dict) -> tuple[str, str, str, str, str]:
  model = payload.get("model")

  if isinstance(model, str) and model.startswith("openrouter/"):
    forwarded_payload = dict(payload)
    forwarded_payload["model"] = model.removeprefix("openrouter/")
    return (
      settings.openrouter_base_url.rstrip("/") + "/chat/completions",
      settings.openrouter_api_key,
      forwarded_payload,
      model,
      "openrouter"
    )
  
  return (
    settings.openai_base_url.rstrip("/") + "/chat/completions",
    settings.openai_api_key,
    payload,
    model,
    "openai"
  )

@app.post("/v1/chat/completions")
async def chat_completions(
  request: Request,
  request_context: RequestContext =  Depends(require_proxy_auth),
):
  payload = await request.json()
  upstream_url, upstream_api_key, forwarded_payload, model, provider = resolve_provider(payload)

  if not upstream_api_key:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Upstream API key is not configured"
    )
  
  headers = {
    "Authorization": f"Bearer {upstream_api_key}",
    "Content-Type": "application/json",
  }

  async with httpx.AsyncClient(timeout=60) as client:
    upstream_response = await client.post(
      upstream_url,
      headers=headers,
      json=forwarded_payload
    )

  try:
    response_json = upstream_response.json()
  except ValueError:
    response_json = {}

  usage = response_json.get("usage") if isinstance(response_json, dict) else {}
  usage = usage or {}

  input_tokens = usage.get("prompt_tokens")
  output_tokens = usage.get("completion_tokens")
  total_tokens = usage.get("total_tokens")

  actual_cost_usd = calculate_actual_cost(
    provider,
    model,
    output_tokens,
    input_tokens
  )

  insert_request_log({
    "project": request_context.project,
    "agent": request_context.agent,
    "provider": provider,
    "model": model,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "total_tokens": total_tokens,
    "estimated_cost_usd": None,
    "actual_cost_usd": actual_cost_usd,
    "status_code": upstream_response.status_code,
    "error_type": None,
    "error_message": None,
    "created_at": datetime.now(timezone.utc).isoformat(),
  })

  return Response(
    content=upstream_response.content,
    status_code=upstream_response.status_code,
    media_type=upstream_response.headers.get("content-type", "application/json"),
  )
  