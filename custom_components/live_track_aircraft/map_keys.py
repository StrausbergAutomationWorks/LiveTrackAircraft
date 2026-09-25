"""object_ids for the shared map (06_MAP_CONTRACT.md D11), in the exact form.

! THE CARD DROPS A MALFORMED VALUE SILENTLY (D11 rule 7): a number, an
upper-case icao24, a lower-case registration all do nothing, and nothing
logs it. So a value that is not already right is LEFT OUT, never repaired.

! ONLY VALUES A SOURCE STATES AS THAT IDENTIFIER, never derived or guessed.
  icao24        our own identity: the Mode S address the feed keys each
                aircraft on. Lower-cased here because it is ours.
  registration  the FAA registry's answer for that Mode S code, which
                states the N-number and the address together. NOT the
                feed's `r` field: that is the aggregator's database lookup,
                not something the aircraft or a registry states. Non-US
                aircraft therefore carry icao24 alone.
"""

from __future__ import annotations

import re
from typing import Any

_ICAO24 = re.compile(r"[0-9a-f]{6}")
# The card's own registration test, plus at least two characters: a bare
# "N" is the FAA prefix with nothing after it.
_REGISTRATION = re.compile(r"[A-Z0-9][A-Z0-9-]+")


def registry_registration(owner: Any, government: Any) -> str | None:
    """The registration a registry lookup stated, owner table first."""
    for answer in (owner, government):
        if isinstance(answer, dict):
            reg = answer.get("registration")
            if isinstance(reg, str) and reg:
                return reg
    return None


def object_ids(identity: Any, registration: Any) -> dict[str, str] | None:
    """{icao24, registration} where each is valid; None when neither is."""
    out: dict[str, str] = {}
    if isinstance(identity, str) and _ICAO24.fullmatch(identity.lower()):
        out["icao24"] = identity.lower()
    if isinstance(registration, str) and _REGISTRATION.fullmatch(registration):
        out["registration"] = registration
    return out or None
