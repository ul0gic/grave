"""Imports only stdlib — any layer may import this without forming a cycle."""

from __future__ import annotations


class UsageError(Exception):
    """User input mistake; the dispatch layer renders message + hints and exits 2."""

    def __init__(self, message: str, *hints: str) -> None:
        super().__init__(message)
        self.message = message
        self.hints = hints
