import os

# set ENV variables before app is imported and settings are set up
TEST_KEY = "llmproxy_sk_test"
TEST_OPENAI_KEY = "test-openai-key"
os.environ["LLM_PROXY_API_KEY"] = TEST_KEY
os.environ["OPENAI_API_KEY"] = TEST_OPENAI_KEY
os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"

import httpx

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_does_not_require_auth():
  response = client.get("/health")

  assert response.status_code == 200
  assert response.json() == {"status": "ok"}

def test_chat_completions_rejects_missing_auth():
  response = client.post("/v1/chat/completions", json={})

  assert response.status_code == 401

def test_chat_completions_rejects_invalid_key():
  response = client.post(
    "/v1/chat/completions",
    headers={"Authorization": "Bearer wrong"},
    json={},
  )

  assert response.status_code == 401

def test_chat_completions_forwards_to_openai(monkeypatch):
  async def fake_post(self, url, headers=None, json=None):
    assert url == "https://api.openai.com/v1/chat/completions"
    assert headers["Authorization"] == f"Bearer {TEST_OPENAI_KEY}"
    assert json == {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]}
    return httpx.Response(200, json={"id": "chatcmpl_test"})

  monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

  response = client.post(
    "/v1/chat/completions",
    headers={"Authorization": "Bearer " + TEST_KEY},
    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]},
  )

  assert response.status_code == 200
  assert response.json() == {"id": "chatcmpl_test"}