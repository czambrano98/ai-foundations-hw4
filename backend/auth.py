"""Password hashing and session tokens for Campus Customs accounts.

Passwords are never stored in plaintext and are never recoverable. We store
only a PBKDF2-HMAC-SHA256 hash with a per-user random salt, in the same
`pbkdf2_sha256$<salt>$<digest>` format the seed database already uses, so the
seeded test user verifies with the same code path as newly created accounts.

Why this resists both human and automated attackers:

- The stored value is a one-way hash. Even with full read access to the
  database, an attacker cannot read a password back out; they can only guess
  candidates and hash each one.
- Each user has a unique 16-byte random salt, so identical passwords produce
  different hashes and a single precomputed table ("rainbow table") cannot
  attack the whole table at once.
- 120,000 PBKDF2 iterations make each guess deliberately expensive, which
  blunts large-scale brute forcing by humans or machines alike.
- Verification uses a constant-time comparison, so timing does not leak how
  much of a digest matched.
"""

import base64
import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"

# Calibrated against the seeded test user so existing accounts verify with the
# same code that creates new ones. New accounts are hashed with this same cost.
ITERATIONS = 120_000

SALT_BYTES = 16
DIGEST_BYTES = 32


def hash_password(password: str) -> str:
    """Return a self-describing hash string for a new or changed password."""
    if not password:
        raise ValueError("Password must not be empty")
    salt = secrets.token_hex(SALT_BYTES)
    digest = _derive(password, salt)
    return f"{ALGORITHM}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """Check a candidate password against a stored hash in constant time.

    Returns False rather than raising on a malformed stored value, so a
    corrupt row cannot be distinguished from a wrong password by the caller.
    """
    try:
        algorithm, salt, expected = stored.split("$")
    except (ValueError, AttributeError):
        return False
    if algorithm != ALGORITHM:
        return False
    candidate = _derive(password, salt)
    # hmac.compare_digest is constant-time: it does not short-circuit on the
    # first differing byte, so response timing does not reveal the prefix match.
    return hmac.compare_digest(candidate, expected)


def _derive(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
        dklen=DIGEST_BYTES,
    ).hex()


# --- Session tokens -------------------------------------------------------
#
# On login we hand the browser a signed token instead of keeping server-side
# session state. The token carries the user id and an expiry, signed with a
# server secret the client never sees. The client cannot forge or alter it
# without the secret, and a tampered token fails the signature check.

TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60  # one week


def _load_secret() -> bytes:
    """Load the signing secret, generating and persisting one on first run.

    Prefers the CAMPUS_CUSTOMS_SECRET environment variable. Otherwise it
    generates a random secret and stores it in backend/.session_secret, which
    is gitignored so it never enters version control. The secret stays stable
    across restarts so existing tokens keep working.
    """
    env_secret = os.environ.get("CAMPUS_CUSTOMS_SECRET")
    if env_secret:
        return env_secret.encode("utf-8")

    secret_file = Path(__file__).resolve().parent / ".session_secret"
    if secret_file.exists():
        return secret_file.read_bytes()

    generated = secrets.token_bytes(32)
    secret_file.write_bytes(generated)
    return generated


_SECRET = _load_secret()


def _sign(payload: str) -> str:
    signature = hmac.new(_SECRET, payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")


def make_token(user_id: int) -> str:
    """Create a signed session token for a user id."""
    expiry = int(time.time()) + TOKEN_TTL_SECONDS
    payload = f"{user_id}:{expiry}"
    return f"{payload}:{_sign(payload)}"


def read_token(token: str) -> int | None:
    """Return the user id from a valid, unexpired token, else None."""
    try:
        user_id_str, expiry_str, signature = token.split(":")
        payload = f"{user_id_str}:{expiry_str}"
    except (ValueError, AttributeError):
        return None

    # Constant-time signature check before trusting any field.
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    if int(expiry_str) < int(time.time()):
        return None
    return int(user_id_str)
