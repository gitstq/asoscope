"""Typed exception hierarchy for asoscope.

Exit codes are attached to the public error types so the CLI layer can
translate failures into deterministic process exit codes.
"""

from __future__ import annotations

# Stable process exit codes used by the command line interface.
EXIT_OK = 0
EXIT_GENERIC = 1
EXIT_USAGE = 2
EXIT_NETWORK = 3
EXIT_NOT_FOUND = 4
EXIT_LOCAL_STATE = 5


class AScopeError(Exception):
    """Base class for every error raised by asoscope."""

    exit_code: int = EXIT_GENERIC


class UsageError(AScopeError):
    """Invalid command line arguments or parameter combination."""

    exit_code = EXIT_USAGE


class TransportError(AScopeError):
    """Network transport failure (DNS, timeout, connection reset, ...)."""

    exit_code = EXIT_NETWORK


class APIError(AScopeError):
    """Apple endpoint responded with a non-2xx HTTP status."""

    exit_code = EXIT_NETWORK

    def __init__(self, message: str, status: int = 0, url: str = ""):
        super().__init__(message)
        self.status = status
        self.url = url


class NotFoundError(AScopeError):
    """The requested app / resource does not exist."""

    exit_code = EXIT_NOT_FOUND


class StoreError(AScopeError):
    """Local watchlist / snapshot state is invalid or unwritable."""

    exit_code = EXIT_LOCAL_STATE
