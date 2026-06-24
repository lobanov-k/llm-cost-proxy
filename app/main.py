import httpx
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status

from app.auth import RequestContext, require_proxy_auth
from app.settings import settings

app = FastAPI()

@app.get("/health")
async def health():
  return {"status": "ok"}

def resolve_provider(payload: dict) -> tuple[str, str, str]:
  model = payload.get("model")

  if isinstance(model, str) and model.startswith("openrouter/"):
    forwarded_payload = dict(payload)
    forwarded_payload["model"] = model.removeprefix("openrouter/")
    return (
      settings.openrouter_base_url.rstrip("/") + "/chat/completions",
      settings.openrouter_api_key,
      forwarded_payload
    )
  
  return (
    settings.openai_base_url.rstrip("/") + "/chat/completions",
    settings.openai_api_key,
    payload,
  )

@app.post("/v1/chat/completions")
async def chat_completions(
  request: Request,
  request_context: RequestContext =  Depends(require_proxy_auth),
):
  payload = await request.json()
  upstream_url, upstream_api_key, forwarded_payload = resolve_provider(payload)

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

  print("Response test", {
    "content": upstream_response.content,
    "status_code": upstream_response.status_code,
  })

  return Response(
    content=upstream_response.content,
    status_code=upstream_response.status_code,
    media_type=upstream_response.headers.get("content-type", "application/json"),
  )
  