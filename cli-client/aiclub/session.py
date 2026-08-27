"""Local persistence of the logged-in member's Supabase session.

After a member verifies with an email code, Supabase hands us an access token
(short-lived) and a refresh token (long-lived). We cache both in a JSON file so
the member stays logged in between commands. The file is written with 0600
permissions (readable/writable only by the owner) because it holds credentials.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import config_dir


def session_file() -> Path:
    return config_dir() / "session.json"


@dataclass
class Session:
    access_token: str
    refresh_token: str
    email: str
    user_id: str


def save_session(session: Session) -> None:
    """Write the session to disk with owner-only permissions."""
    path = session_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(session), indent=2))
    os.chmod(path, 0o600)


def load_session() -> Session | None:
    """Return the cached session, or None if absent/unreadable."""
    path = session_file()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return Session(**data)
    except (OSError, json.JSONDecodeError, TypeError):
        # Corrupt or outdated session file — treat as logged out.
        return None


def clear_session() -> None:
    """Remove the cached session, if any."""
    session_file().unlink(missing_ok=True)
