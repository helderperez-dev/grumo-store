from __future__ import annotations

from pathlib import Path

import pytest
from grumo_store import Store
from grumo_store.grumo_migration import prepare_grumo_store


def test_grumo_migration_keeps_original_and_verifies_rollback(tmp_path: Path) -> None:
    source = tmp_path / ".voodoo" / "application.vstore"
    source.parent.mkdir()
    with Store.open(source) as store:
        store.put(b"user:42", b"preserved")
        original_id = store.health_report()["store_id"].hex()

    old_bytes = source.read_bytes()
    destination = tmp_path / ".grumo" / "application.grumo"
    backup = tmp_path / "backups" / "before-grumo.vstore"
    report = prepare_grumo_store(source, destination, backup=backup)

    assert report["activated"] is False
    assert report["store_id"] == original_id
    assert source.read_bytes() == old_bytes
    assert backup.read_bytes() == old_bytes
    assert destination.read_bytes() == old_bytes
    assert Store.verify(destination).store_id.hex() == original_id
    with Store.open(destination) as store:
        assert store.get(b"user:42") == b"preserved"


def test_grumo_migration_dry_run_is_read_only(tmp_path: Path) -> None:
    old = tmp_path / "application.vstore"
    with Store.open(old) as store:
        store.put(b"ok", b"yes")
    dest = tmp_path / "new" / "application.grumo"
    backup = tmp_path / "backup" / "original.vstore"

    result = prepare_grumo_store(old, dest, backup=backup, dry_run=True)
    assert result["dry_run"] is True
    assert not dest.exists()
    assert not backup.exists()
    assert not dest.parent.exists()
    assert not backup.parent.exists()


def test_grumo_migration_rejects_existing_destination(tmp_path: Path) -> None:
    old = tmp_path / "application.vstore"
    with Store.open(old) as store:
        store.put(b"keep", b"intact")
    dest = tmp_path / "application.grumo"
    dest.write_bytes(b"do-not-overwrite")

    with pytest.raises(FileExistsError, match="destination already exists"):
        prepare_grumo_store(old, dest, backup=tmp_path / "rollback.vstore")
    assert dest.read_bytes() == b"do-not-overwrite"
    assert not (tmp_path / "rollback.vstore").exists()


def test_grumo_migration_rejects_identical_source_and_backup(tmp_path: Path) -> None:
    old = tmp_path / "application.vstore"
    with Store.open(old) as store:
        store.put(b"keep", b"intact")
    old_bytes = old.read_bytes()
    with pytest.raises(ValueError, match="distinct paths"):
        prepare_grumo_store(old, tmp_path / "application.grumo", backup=old)
    assert old.read_bytes() == old_bytes


def test_grumo_migration_rejects_wrong_extension(tmp_path: Path) -> None:
    old = tmp_path / "application.vstore"
    with Store.open(old) as store:
        store.put(b"keep", b"intact")
    with pytest.raises(ValueError, match="end in .grumo"):
        prepare_grumo_store(old, tmp_path / "different.vstore", backup=tmp_path / "backup.vstore")
