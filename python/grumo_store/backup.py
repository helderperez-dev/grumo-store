"""Compatibility entrypoint for the Grumo Store backup API.

Both namespaces use the same implementation during the transition.
"""

from voodoo_store.backup import *  # noqa: F401,F403
