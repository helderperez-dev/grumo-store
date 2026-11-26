"""Run the verified Voodoo Store to Grumo Store path migration.

Transitional wrapper keeps one implementation of the migration algorithm.
Usage: python -m grumo_store.grumo_migration OLD.vstore NEW.grumo --backup BACKUP.vstore
"""

from voodoo_store.grumo_migration import main, prepare_grumo_store

__all__ = ["main", "prepare_grumo_store"]


if __name__ == "__main__":
    raise SystemExit(main())
