from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
  )

  llm_proxy_api_key: str = Field(..., alias="LLM_PROXY_API_KEY")

  openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
  openrouter_api_key: str | None = Field(None, alias="OPENROUTER_API_KEY")

  # database_url: str = Field(
  #   "sqlite:///./data/proxy.db",
  #   alias="DATABASE_URL",
  # )

  default_provider: str = Field("openai", alias="DEFAULT_PROVIDER")
  default_project: str = Field("default", alias="DEFAULT_PROJECT")
  default_agent: str = Field("default", alias="DEFAULT_AGENT")

  default_currency: str = Field("USD", alias="DEFAULT_CURRENCY")

  daily_project_budget: float = Field(5, alias="DAILY_PROJECT_BUDGET")
  daily_agent_budget: float = Field(5, alias="DAILY_AGENT_BUDGET")
  single_request_max_cost: float = Field(0.25, alias="SINGLE_REQUEST_MAX_COST")

settings = Settings()