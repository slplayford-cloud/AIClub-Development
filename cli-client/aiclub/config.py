"""Configuration for the aiclub CLI.

The three club-wide settings below (Supabase URL, anon key, allowed email domain)
are the *same for every member* — there is one Supabase project for the whole club.
The anon key is a **public** key by design (the real security boundary is Supabase
Row-Level Security), so it is safe to ship baked into the package.

Resolution order for each setting (first wins):
  1. Environment variable  (handy for local development)
  2. ~/.config/aiclub/config.toml  (optional per-machine override)
  3. Baked-in default constant below
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir

APP_NAME = "aiclub"

# --- Baked-in club defaults -------------------------------------------------
# Club-wide constants for the one shared Supabase project. The publishable key
# (sb_publishable_...) is the modern replacement for the old anon key: it is
# public by design and safe to commit — RLS is the real security boundary.
DEFAULT_SUPABASE_URL = "https://jvmwnlioqpvievgalieu.supabase.co"
DEFAULT_SUPABASE_ANON_KEY = "sb_publishable_GIj-J5mMr7wjVYi7FDfXsA_yYTASysD"
DEFAULT_ALLOWED_DOMAIN = "nd.edu"


def config_dir() -> Path:
    """Directory where per-machine config and the session token live."""
    return Path(user_config_dir(APP_NAME))


def config_file() -> Path:
    return config_dir() / "config.toml"


@dataclass(frozen=True)
class Config:
    supabase_url: str
    supabase_anon_key: str
    allowed_domain: str


class ConfigError(Exception):
    """Raised when required configuration is missing."""


def _load_toml() -> dict:
    path = config_file()
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Could not read config file {path}: {exc}") from exc


def load_config() -> Config:
    """Resolve configuration from env vars, config file, then baked-in defaults."""
    file_data = _load_toml()

    def resolve(env_key: str, file_key: str, default: str) -> str:
        return os.environ.get(env_key) or file_data.get(file_key) or default

    url = resolve("AICLUB_SUPABASE_URL", "supabase_url", DEFAULT_SUPABASE_URL)
    key = resolve("AICLUB_SUPABASE_ANON_KEY", "supabase_anon_key", DEFAULT_SUPABASE_ANON_KEY)
    domain = resolve("AICLUB_ALLOWED_DOMAIN", "allowed_domain", DEFAULT_ALLOWED_DOMAIN)

    missing = [
        name
        for name, value in (
            ("supabase_url", url),
            ("supabase_anon_key", key),
            ("allowed_domain", domain),
        )
        if not value
    ]
    if missing:
        raise ConfigError(
            "Missing configuration: "
            + ", ".join(missing)
            + ".\nSet them via environment variables "
            "(AICLUB_SUPABASE_URL, AICLUB_SUPABASE_ANON_KEY, AICLUB_ALLOWED_DOMAIN) "
            f"or in {config_file()}."
        )
    return Config(supabase_url=url, supabase_anon_key=key, allowed_domain=domain)
