"""GitHub webhook HMAC-SHA256 signature verification.

GitHub signs every webhook delivery using the secret configured in the
GitHub App settings.  The signature is included in the
``X-Hub-Signature-256`` request header as ``sha256=<hex-digest>``.

Reference: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
"""

from __future__ import annotations

import hashlib
import hmac


def verify_webhook_signature(
    payload_bytes: bytes,
    signature_header: str,
    secret: str,
) -> bool:
    """Return True if *signature_header* is a valid HMAC-SHA256 signature of *payload_bytes*.

    Args:
        payload_bytes:     The raw (un-decoded) request body bytes.
        signature_header:  The value of the ``X-Hub-Signature-256`` header.
                           Expected format: ``"sha256=<hex-digest>"``.
        secret:            The webhook secret configured in the GitHub App
                           settings (``GITHUB_WEBHOOK_SECRET`` env var).

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.

    Security notes
    --------------
    * Uses ``hmac.compare_digest`` to prevent timing-attack leakage.
    * If *secret* is empty (not yet configured), the function returns
      ``False`` so unconfigured deployments fail closed rather than open.
    * If *signature_header* is missing or malformed (no ``sha256=`` prefix),
      the function returns ``False``.
    """
    if not secret:
        return False

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_digest = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    # compare_digest requires both arguments to be the same type (str)
    return hmac.compare_digest(
        f"sha256={expected_digest}",
        signature_header,
    )
