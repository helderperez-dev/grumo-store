"""Grumo Store namespace compatibility regression tests."""

from __future__ import annotations

import grumo_store
import voodoo_store


def test_grumo_namespace_exports_same_native_store_and_version() -> None:
    assert grumo_store.Store is voodoo_store.Store
    assert grumo_store.Transaction is voodoo_store.Transaction
    assert grumo_store.VerificationReport is voodoo_store.VerificationReport
    assert grumo_store.__version__ == voodoo_store.__version__
    assert set(grumo_store.__all__) == set(voodoo_store.__all__)


def test_grumo_namespace_reads_legacy_store(tmp_path) -> None:
    path = tmp_path / "legacy.vstore"
    with voodoo_store.Store.open(path) as store:
        store.put(b"key", b"value")
    with grumo_store.Store.open(path) as store:
        assert store.get(b"key") == b"value"


def test_grumo_namespace_uses_new_extension_without_format_change(tmp_path) -> None:
    path = tmp_path / "application.grumo"
    with grumo_store.Store.open(path) as store:
        store.put(b"key", b"value")
    with voodoo_store.Store.open(path) as store:
        assert store.get(b"key") == b"value"


def test_grumo_migration_cli_reuses_verified_implementation() -> None:
    from grumo_store.grumo_migration import prepare_grumo_store as grumo_prepare
    from voodoo_store.grumo_migration import prepare_grumo_store as legacy_prepare

    assert grumo_prepare is legacy_prepare


def test_grumo_helper_modules_delegate_to_legacy_implementations() -> None:
    from grumo_store.backup import create_backup_manifest as new_backup
    from grumo_store.migrations import migrate_collection as new_migrate
    from grumo_store.objects import iter_object_chunks as new_chunks
    from voodoo_store.backup import create_backup_manifest as old_backup
    from voodoo_store.migrations import migrate_collection as old_migrate
    from voodoo_store.objects import iter_object_chunks as old_chunks

    assert new_backup is old_backup
    assert new_migrate is old_migrate
    assert new_chunks is old_chunks


def test_grumo_namespace_verifies_historical_store_fixture() -> None:
    from pathlib import Path

    fixture = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "legacy-0.2.2.vstore"
    assert fixture.is_file(), "Historical compatibility fixture must be shipped in CI"
    old_report = voodoo_store.Store.verify(fixture)
    new_report = grumo_store.Store.verify(fixture)
    assert new_report.store_id == old_report.store_id
    assert new_report.keys == old_report.keys
    assert new_report.records == old_report.records
    assert not new_report.has_torn_tail
