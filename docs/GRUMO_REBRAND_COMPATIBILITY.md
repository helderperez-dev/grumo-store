# Store format and file relocation

Grumo Store uses the existing binary format 1.0 independently of the filename extension. The canonical application path is .grumo/application.grumo. The 2.0 identity cutover intentionally removes transitional package aliases without changing the file magic or recovery semantics.

Stop the application and close the writer before relocating a store. Verify the source and preserve a backup. Use the create-only relocation utility:

```bash
python -m grumo_store.grumo_migration old-store.vstore .grumo/application.grumo --backup backups/original.vstore
```

The utility does not activate the new file. Verify the copy before configuring the application to use it. Never overwrite an active store.
