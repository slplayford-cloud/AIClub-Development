"""Small pure helpers (no I/O) that are easy to unit-test."""

from __future__ import annotations


def email_domain(email: str) -> str:
    """Return the lowercased domain part of an email address ('' if none)."""
    _, sep, domain = email.rpartition("@")
    if not sep:
        return ""
    return domain.lower()


def is_allowed_email(email: str, allowed_domain: str) -> bool:
    """True if the email belongs to the club's allowed domain (case-insensitive)."""
    return email_domain(email) == allowed_domain.lower()
