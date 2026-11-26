"""Transitional Grumo Store namespace for existing Voodoo Store installations.

This is an import compatibility layer, not the final renamed PyPI distribution.
It deliberately delegates to the same native engine and on-disk format.
"""

from voodoo_store import *  # noqa: F401,F403
from voodoo_store import __all__ as __all__
from voodoo_store import __version__ as __version__
