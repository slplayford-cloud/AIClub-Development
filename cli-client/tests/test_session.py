import aiclub.session as session_mod
from aiclub.session import Session, clear_session, load_session, save_session


def test_session_round_trip(tmp_path, monkeypatch):
    # Redirect the session file into a temp dir so we don't touch the real one.
    monkeypatch.setattr(session_mod, "config_dir", lambda: tmp_path)

    assert load_session() is None  # nothing saved yet

    original = Session(
        access_token="access-123",
        refresh_token="refresh-456",
        email="alice@nd.edu",
        user_id="user-uuid",
    )
    save_session(original)

    loaded = load_session()
    assert loaded == original

    # File must be owner-only (0600).
    assert (session_mod.session_file().stat().st_mode & 0o777) == 0o600

    clear_session()
    assert load_session() is None


def test_load_session_handles_corrupt_file(tmp_path, monkeypatch):
    monkeypatch.setattr(session_mod, "config_dir", lambda: tmp_path)
    session_mod.session_file().write_text("{ not valid json")
    assert load_session() is None
