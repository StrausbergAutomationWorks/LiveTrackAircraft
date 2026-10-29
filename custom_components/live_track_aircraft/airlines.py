"""Operator lookup: the table lives in saw-livetrack (``saw_livetrack.airlines``, 0.2.17).

Moved there 2026-10-29 (Lee 14:51) so Live Track SALT reads the same table: one table, two consumers. This module
keeps the names Live Track Aircraft's code and tests import.
"""

from __future__ import annotations

from saw_livetrack.airlines import _OPERATORS, _SHORT, airline_short, lookup_operator  # noqa: F401
