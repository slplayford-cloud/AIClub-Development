"""Supabase connectivity helpers.

For M0 this only needs a lightweight health check. Later milestones will add an
authenticated client factory (anon key + the member's cached JWT).
"""

from __future__ import annotations

import httpx

from .config import Config


def health_check(cfg: Config, timeout: float = 10.0) -> None:
    """Confirm the Supabase project is reachable.

    Hits GoTrue's public health endpoint. Raises httpx.HTTPError on failure.
    """
    url = cfg.supabase_url.rstrip("/") + "/auth/v1/health"
    response = httpx.get(url, headers={"apikey": cfg.supabase_anon_key}, timeout=timeout)
    response.raise_for_status()
