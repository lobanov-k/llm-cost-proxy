from dataclasses import dataclass
from secrets import compare_digest

from fastapi import Header, HTTPException, status

from app.settings import settings

@dataclass
class RequestContext:
  project: str
  agent: str
  api_key_id: str | None = None

async def require_proxy_auth(
    authorization: str | None = Header(default=None),
    project_header: str | None = Header(default=None, alias="X-LLM-Project"),
    agent_header: str | None = Header(default=None, alias="X-LLM-Agent")
) -> RequestContext:
  if not authorization:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid authorization header"
    )
  
  scheme, _, token = authorization.partition(" ")

  if scheme.lower() != "bearer" or not token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid Authorization header: token is missing"
    )
  
  if not compare_digest(token, settings.llm_proxy_api_key): 
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid API key"
    )
  
  return RequestContext(
    project=project_header or settings.default_project,
    agent=agent_header or settings.default_agent,
    api_key_id="env",
  )