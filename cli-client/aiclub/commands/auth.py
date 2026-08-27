"""Account setup & verification commands: login, whoami, logout.

Membership is verified by signing in with Google (no passwords, no emails):
  1. `login` builds a Google sign-in URL and opens it in the browser.
  2. The member picks their @<allowed_domain> Google account.
  3. Google → Supabase → a localhost redirect hands us an authorization code.
  4. We exchange the code for a session and cache it, so later commands act as
     that member.

Only @<allowed_domain> accounts can register — enforced server-side by a Postgres
trigger on auth.users, and hinted to Google via the `hd` parameter for a cleaner
account picker.
"""

from __future__ import annotations

import webbrowser

import typer

from ..client import get_authed_client, get_oauth_client
from ..config import ConfigError, load_config
from ..oauth_callback import wait_for_callback
from ..output import console, error, info, success
from ..session import Session, clear_session, load_session, save_session

# Where Google sends the browser back to. This exact URL must be listed in the
# Supabase dashboard under Authentication → URL Configuration → Redirect URLs.
CALLBACK_HOST = "localhost"
CALLBACK_PORT = 8765
REDIRECT_URL = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}"


def _load_config_or_exit():
    try:
        return load_config()
    except ConfigError as exc:
        error(str(exc))
        raise typer.Exit(code=1)


def login() -> None:
    """Sign in with your university Google account."""
    cfg = _load_config_or_exit()
    client = get_oauth_client(cfg)

    # Builds the authorize URL locally (no network) and stores the PKCE verifier.
    oauth = client.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {
                "redirect_to": REDIRECT_URL,
                "query_params": {"hd": cfg.allowed_domain, "prompt": "select_account"},
            },
        }
    )

    info("Opening your browser to sign in with Google …")
    console.print(
        f"[dim]If it doesn't open, paste this into your browser:[/]\n{oauth.url}"
    )

    try:
        code, err = wait_for_callback(
            CALLBACK_HOST, CALLBACK_PORT, on_ready=lambda: webbrowser.open(oauth.url)
        )
    except OSError as exc:
        error(f"Could not start the local login server on port {CALLBACK_PORT}: {exc}")
        info("Another login may be in progress — try again in a moment.")
        raise typer.Exit(code=1)

    if err:
        error(f"Sign-in failed: {err}")
        raise typer.Exit(code=1)
    if not code:
        error("No authorization code received. Please try again.")
        raise typer.Exit(code=1)

    try:
        result = client.auth.exchange_code_for_session({"auth_code": code})
    except Exception as exc:  # noqa: BLE001 - surface any auth error plainly
        error(f"Could not complete sign-in: {exc}")
        raise typer.Exit(code=1)

    if result.session is None or result.user is None:
        error("Sign-in did not return a session. Please try again.")
        raise typer.Exit(code=1)

    email = result.user.email or "(unknown email)"
    save_session(
        Session(
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
            email=email,
            user_id=result.user.id,
        )
    )
    success(f"Signed in as {email}.")


def whoami() -> None:
    """Show the account you're currently logged in as."""
    cfg = _load_config_or_exit()

    session = load_session()
    if session is None:
        error("You're not logged in. Run:  aiclub login")
        raise typer.Exit(code=1)

    try:
        client = get_authed_client(cfg, session)
        response = (
            client.table("members")
            .select("email, full_name, created_at")
            .eq("id", session.user_id)
            .single()
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        error(f"Could not load your profile: {exc}")
        info("Your session may have expired. Try logging in again.")
        raise typer.Exit(code=1)

    member = response.data
    console.print(f"[bold]Logged in as:[/] {member['email']}")
    console.print(f"[bold]Name:[/] {member.get('full_name') or '[dim](not set)[/]'}")
    console.print(f"[bold]Member since:[/] {member['created_at']}")


def set_name(
    name: str = typer.Argument(..., help='Your full name, e.g. "Stephen Playford".'),
) -> None:
    """Set the full name shown on your member profile."""
    cfg = _load_config_or_exit()

    session = load_session()
    if session is None:
        error("You're not logged in. Run:  aiclub login")
        raise typer.Exit(code=1)

    try:
        client = get_authed_client(cfg, session)
        client.table("members").update({"full_name": name}).eq(
            "id", session.user_id
        ).execute()
    except Exception as exc:  # noqa: BLE001
        error(f"Could not update your name: {exc}")
        raise typer.Exit(code=1)

    success(f"Your name is now: {name}")


def logout() -> None:
    """Log out and delete your saved session."""
    session = load_session()
    clear_session()
    if session is None:
        info("You were not logged in.")
    else:
        success(f"Logged out {session.email}.")
