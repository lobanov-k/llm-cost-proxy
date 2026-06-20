from fastapi import FastAPI, Depends

from app.auth import RequestContext, require_proxy_auth

app = FastAPI()

@app.get("/health")
async def health():
  return {"status": "ok"}

@app.post("/v1/chat/completions")
async def chat_completions(
  request_context: RequestContext =  Depends(require_proxy_auth),
):
  print("Auth check", {
    "status": "authorized",
    "project": request_context.project,
    "agent": request_context.agent,
    "api_key_id": request_context.api_key_id
  })

  return {
    "status": "authorized",
    "project": request_context.project,
    "agent": request_context.agent,
    "api_key_id": request_context.api_key_id
  }