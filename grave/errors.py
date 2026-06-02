"""Neutral shared error types for GRAVE.

Carries no first-party dependencies so any layer (cli, commands) can import it
without forming a cycle.
"""

from __future__ import annotations


class UsageError(Exception):
    """A user input mistake that should exit with code 2.

    Carries the primary message plus any follow-up hint lines for stderr.
    """

    def __init__(self, message: str, *hints: str) -> None:
        super().__init__(message)
        self.message = message
        self.hints = hints
