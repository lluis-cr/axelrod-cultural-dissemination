"""Visualisation helpers for baseline Axelrod outputs.

The current plotting implementation still lives in ``model.py`` to preserve the
existing behaviour while the repository is being reorganised. This module
provides a stable public entry point for future plotting helpers.
"""

from .model import save_demo_outputs

__all__ = ["save_demo_outputs"]
