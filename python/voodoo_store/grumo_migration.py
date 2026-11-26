"""Explicit, non-destructive path transition from Voodoo Store to Grumo Store.

The .grumo extension is a name for the existing Store file format, NOT a new
binary format. Stop the application and close its Store writer before running.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ._native import Store


def prepare_grumo_store(
    source: str | Path,
    destination: str | Path,
    *,
    backup: str | Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Verify old data, make a verified rollback copy, then create Grumo copy.

    Both copies are create-only. Neither old data nor an existing destination
    is modified. Activation in the application config is a separate step.
    """
    old = Path(source).expanduser()
    new = Path(destination).expanduser()
    rollback = Path(backup).expanduser()

    paths = (old.resolve(), new.resolve(), rollback.resolve())
    if len(set(paths)) != 3:
        raise ValueError("source, destination and backup must be distinct paths")
    if not old.is_file():
        raise FileNotFoundError(f"source Store does not exist: {old}")
    if new.exists() or new.is_symlink():
        raise FileExistsError(f"Grumo destination already exists: {new}")
    if rollback.exists() or rollback.is_symlink():
        raise FileExistsError(f"rollback backup already exists: {rollback}")
    if new.suffix != ".grumo":
        raise ValueError("new Store destination must end in .grumo")

    original = Store.verify(old)
    if original.has_torn_tail:
        raise ValueError("source has a torn tail; repair and verify before migration")

    report: dict[str, Any] = {
        "source": str(old),
        "destination": str(new),
        "backup": str(rollback),
        "store_id": original.store_id.hex(),
        "bytes": original.file_bytes,
        "keys": original.keys,
        "dry_run": dry_run,
        "activated": False,
    }
    if dry_run:
        return report

    rollback.parent.mkdir(parents=True, exist_ok=True)
    new.parent.mkdir(parents=True, exist_ok=True)
    Store.restore_copy(old, rollback)
    Store.restore_copy(rollback, new)

    copied = Store.verify(new)
    if (
        copied.store_id != original.store_id
        or copied.file_bytes != original.file_bytes
        or copied.keys != original.keys
        or copied.records != original.records
    ):
        raise RuntimeError("Grumo copy failed verification; do not activate it")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a verified, non-destructive Voodoo to Grumo Store path migration"
    )
    parser.add_argument("source", type=Path, help="Existing closed .vstore file")
    parser.add_argument("destination", type=Path, help="New .grumo file (must not exist)")
    parser.add_argument("--backup", type=Path, required=True, help="Create-only rollback copy")
    parser.add_argument("--dry-run", action="store_true", help="Verify without creating files")
    args = parser.parse_args()
    try:
        result = prepare_grumo_store(
            args.source, args.destination, backup=args.backup, dry_run=args.dry_run
        )
    except Exception as error:
        # Safe, actionable CLI error. The underlying Store exceptions derive
        # from Exception and may not be from the Python standard library.
        parser.exit(1, f"Grumo Store migration failed: {error}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
