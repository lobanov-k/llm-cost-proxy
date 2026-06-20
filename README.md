To start proxy

`python run.py`

Generate your own auth key with running e.g.

`python -c "import secrets; print('llmproxy_sk_' + secrets.token_urlsafe(32))"`

Than add it to the .env file