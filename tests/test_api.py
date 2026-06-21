import os

TEST_KEY = "llmproxy_sk_test"
os.environ["LLM_PROXY_API_KEY"] = TEST_KEY

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

def test_chat_completions_accept_valid_key_and_defaults():
  response = client.post(
    "/v1/chat/completions",
    headers={"Authorization": "Bearer " + TEST_KEY},
    json={"model": "gpt-4o-mini", "messages": []}
  )

  assert response.status_code == 200
  assert response.json()["status"] == "authorized"
  assert response.json()["agent"] == "default"
  assert response.json()["project"] == "default"

def test_chat_completions_reads_project_and_agent_headers():
  response = client.post(
    "/v1/chat/completions",
    headers={
      "Authorization": "Bearer llmproxy_sk_test",
      "X-LLM-Project": "demo-project",
      "X-LLM-Agent": "codex",
    },
    json={"model": "gpt-4o-mini", "messages": []},
  )

  assert response.status_code == 200
  assert response.json()["project"] == "demo-project"
  assert response.json()["agent"] == "codex"