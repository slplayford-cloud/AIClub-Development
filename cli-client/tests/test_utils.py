from aiclub.utils import email_domain, is_allowed_email


def test_email_domain_lowercases():
    assert email_domain("Alice@ND.EDU") == "nd.edu"


def test_email_domain_missing_at():
    assert email_domain("no-at-sign") == ""


def test_is_allowed_email_accepts_matching_domain():
    assert is_allowed_email("bob@nd.edu", "nd.edu") is True
    assert is_allowed_email("bob@ND.edu", "nd.edu") is True


def test_is_allowed_email_rejects_other_domains():
    assert is_allowed_email("bob@gmail.com", "nd.edu") is False
    # A subdomain is not the same domain — must be exact.
    assert is_allowed_email("bob@alumni.nd.edu", "nd.edu") is False
