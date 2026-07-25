from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


PHI_PATTERNS = [
    re.compile(r"\b\d{10,}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
]


def redact_phi(text: str) -> str:
    redacted = text
    for pattern in PHI_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def stable_audit_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RBACDecision:
    allowed: bool
    reason: str = ""


def check_role(required_roles: set[str], user_roles: set[str]) -> RBACDecision:
    if required_roles & user_roles:
        return RBACDecision(True)
    return RBACDecision(False, "User lacks required role.")
