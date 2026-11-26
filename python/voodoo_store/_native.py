"""Backward-compatible import path for the renamed Grumo native extension.

Existing consumers importing voodoo_store._native keep using the exact same
PyO3 objects; no second Rust extension is built or loaded.
"""

from grumo_store._native import *  # noqa: F401,F403
