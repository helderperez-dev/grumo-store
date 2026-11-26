"""Python API for Grumo Store, with lazy compatibility helpers.

The native extension is loaded directly. Importing voodoo_store here would
create a cycle when an existing application imports voodoo_store first:
voodoo_store -> its _native compatibility shim -> grumo_store.
"""

from ._native import (
    AlreadyOpenError,
    CorruptionError,
    DiskFullError,
    NamespaceQuotaError,
    IoError,
    ReservedKeyError,
    Store,
    StoreBusyError,
    StoreClosedError,
    Transaction,
    TransactionFinishedError,
    VerificationReport,
    VoodooStoreError,
    __version__,
)

__all__ = [
    "AlreadyOpenError",
    "CorruptionError",
    "DiskFullError",
    "NamespaceQuotaError",
    "IoError",
    "ReservedKeyError",
    "Store",
    "StoreBusyError",
    "StoreClosedError",
    "Transaction",
    "TransactionFinishedError",
    "VerificationReport",
    "VoodooStoreError",
    "create_backup_manifest",
    "verify_backup_manifest",
    "MigrationConflict",
    "MigrationError",
    "MigrationReport",
    "migrate_collection",
    "iter_object_chunks",
]

_LAZY_HELPERS = {
    "create_backup_manifest": "backup",
    "verify_backup_manifest": "backup",
    "MigrationConflict": "migrations",
    "MigrationError": "migrations",
    "MigrationReport": "migrations",
    "migrate_collection": "migrations",
    "iter_object_chunks": "objects",
}


def __getattr__(name: str):
    """Load Python helpers only when requested, avoiding import cycles."""
    if name not in _LAZY_HELPERS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    value = getattr(import_module(f".{_LAZY_HELPERS[name]}", __name__), name)
    globals()[name] = value
    return value
