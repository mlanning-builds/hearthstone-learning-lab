"""Stable public entry point for the active all-class experimental simulator.

Implementation paths remain in staging during gradual component migration.
Importing the package starts no games, training, or downloads.
"""

from typing import Any
from ._bootstrap import activate

__all__ = ["Game", "Action", "Deck", "random_deck", "validate"]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    return getattr(activate(), name)
