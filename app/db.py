from pathlib import Path
import sqlite3
from typing import Any

from app.settings import settings

def _db_path() -> Path:
  if settings.database_url.startswith("sqlite:///"):
    return Path(settings.database_url.removeprefix("sqlite:///"))
  
  raise ValueError("Only sqlite:/// database URLs are supported")

def get_connection() -> sqlite3.Connection:
  db_path = _db_path()
  db_path.parent.mkdir(parents=True, exist_ok=True)

  connection = sqlite3.connect(db_path)
  connection.row_factory = sqlite3.Row

# TODO (postmvp): lean to uuid as PRIMARY KEY
def init_db() -> None:
  with get_connection() as connection:
    connection.execute("""
    CREATE TABLE IF NOT EXISTS requests (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project TEXT NOT NULL,
      agent TEXT NOT NULL,
      provider TEXT NOT NULL,
      model TEXT NOT NULL,
      input_tokens INTEGER,
      output_tokens INTEGER,
      total_tokens INTEGER,
      estimated_cost_usd REAL,
      actual_cost_usd REAL,
      status_code INTEGER NOT NULL,
      error_type TEXT,
      error_message TEXT,
      created_at TEXT NOT NULL
    )
    """)

def insert_request_log(row: dict[str, Any]) -> None:
  with get_connection() as connection:
    connection.execute("""
        INSERT INTO requests (
          project,
          agent,
          provider,
          model,
          input_tokens,
          output_tokens,
          total_tokens,
          estimated_cost_usd,
          actual_cost_usd,
          status_code,
          error_type,
          error_message,
          created_at
        )
        VALUES (
          :project,
          :agent,
          :provider,
          :model,
          :input_tokens,
          :output_tokens,
          :total_tokens,
          :estimated_cost_usd,
          :actual_cost_usd,
          :status_code,
          :error_type,
          :error_message,
          :created_at
        )
    """, row)