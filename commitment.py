"""Offline IntentBallot reveal commitment. This helper performs no network calls.

Use a cryptographically random salt of at least 16 characters and save it privately
until reveal. Anyone seeing both statement and salt can recover your preferences.
The salt becomes public in the reveal transaction and stored revealed record.
"""
import hashlib
import json
import secrets


def generate_salt() -> str:
    """Generate 32 cryptographically random bytes, encoded as 64 hex characters."""
    return secrets.token_hex(32)


def make_commitment(poll_core: dict, poll_hash: str, voter: str, statement: str, salt: str) -> str:
    payload = {"domain": "intentballot-commit-v1", "chain_id": poll_core["chain_id"],
               "contract_address": poll_core["contract_address"], "poll_id": poll_core["id"],
               "poll_hash": poll_hash, "voter": voter.lower(), "statement": statement, "salt": salt}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
