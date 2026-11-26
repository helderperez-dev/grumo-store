"""Canonical package identity and durable format tests."""
import importlib.util
from importlib.metadata import version
from pathlib import Path

import grumo_store
from grumo_store import Store
from grumo_store._native import Store as NativeStore


def test_canonical_package_identity():
    assert grumo_store.__version__ == version("grumo-store")
    assert Store is NativeStore
    assert importlib.util.find_spec("voodoo_store") is None


def test_canonical_helpers():
    from grumo_store.backup import create_backup_manifest
    from grumo_store.migrations import migrate_collection
    from grumo_store.objects import iter_object_chunks

    assert grumo_store.create_backup_manifest is create_backup_manifest
    assert grumo_store.migrate_collection is migrate_collection
    assert grumo_store.iter_object_chunks is iter_object_chunks


def test_store_round_trip(tmp_path):
    path = tmp_path / "application.grumo"
    with Store.open(path) as store:
        store.put(b"key", b"value")
    with Store.open(path) as store:
        assert store.get(b"key") == b"value"


def test_historical_format_fixture():
    fixture = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "legacy-0.2.2.vstore"
    assert fixture.is_file()
    assert not Store.verify(fixture).has_torn_tail
