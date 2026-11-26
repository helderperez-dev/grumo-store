"""Compatibility entrypoint for the Grumo Store migrations API.

Both namespaces use the same implementation during the transition.
"""

from voodoo_store.migrations import *  # noqa: F401,F403
