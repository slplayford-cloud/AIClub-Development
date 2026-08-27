"""Supabase client helpers.

- ``health_check`` — lightweight connectivity check (used by ``aiclub status``).
- ``get_client`` — an anonymous client (used for login, before we have a session).
- ``get_authed_client`` — a client carrying the member's saved session, refreshing
  the access token if it has expired and persisting the refreshed tokens.
"""

from __future__ import annotations

import httpx
from supabase import Client, ClientOptions, create_client

from .config import Config
from .session import Session, save_session


def health_check(cfg: Config, timeout: float = 10.0) -> None:
    """Confirm the Supabase project is reachable.

    Hits GoTrue's public health endpoint. Raises httpx.HTTPError on failure.
    """
    url = cfg.supabase_url.rstrip("/") + "/auth/v1/health"
    response = httpx.get(url, headers={"apikey": cfg.supabase_anon_key}, timeout=timeout)
    response.raise_for_status()


def get_client(cfg: Config) -> Client:
    """An anonymous Supabase client (no user session attached)."""
    return create_client(cfg.supabase_url, cfg.supabase_anon_key)


def get_oauth_client(cfg: Config) -> Client:
    """A client configured for the PKCE OAuth flow (Google sign-in).

    PKCE stores a one-time code verifier in the client's in-memory storage during
    ``sign_in_with_oauth`` and reads it back in ``exchange_code_for_session`` — so
    the *same* client instance must be used for both halves of the login.
    """
    return create_client(
        cfg.supabase_url,
        cfg.supabase_anon_key,
        options=ClientOptions(flow_type="pkce"),
    )


def get_authed_client(cfg: Config, session: Session) -> Client:
    """A Supabase client acting as the logged-in member.

    Restores the saved tokens; supabase-auth refreshes the access token
    automatically if it has expired. If the tokens changed, persist them so the
    member stays logged in. Raises if the refresh token is no longer valid
    (the member must log in again).
    """
    client = create_client(cfg.supabase_url, cfg.supabase_anon_key)
    response = client.auth.set_session(session.access_token, session.refresh_token)

    refreshed = response.session
    if refreshed is not None and refreshed.access_token != session.access_token:
        save_session(
            Session(
                access_token=refreshed.access_token,
                refresh_token=refreshed.refresh_token,
                email=session.email,
                user_id=session.user_id,
            )
        )
    return client
