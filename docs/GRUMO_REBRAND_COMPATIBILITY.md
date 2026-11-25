# Grumo Store rename: compatibility foundation

Status: **first migration slice — test-only, not a package rename**.

The Voodoo Store embedded engine will be branded **Grumo Store**, with
`.grumo/application.grumo` as the future default application path. The
public identity changes; storage semantics and recovery guarantees do not.

## Non-negotiable invariants

1. `.grumo` is initially **a filename extension only**, not a new format
   version, magic header, schema, or serialization.
2. `application.grumo` must open the same content as the legacy
   `application.vstore` under the same Store engine.
3. The source file is closed, verified, backed up, and preserved during
   migration; never overwrite or relocate a live writer.
4. Store ID, committed records, format major/minor, and integrity guarantees
   remain unchanged by a filename-only migration.
5. One process owns one Store writer. Distinct runtime nodes never share a
   writable Store file across the network.
6. No automatic destructive migration on startup.
7. Production readiness requires historical fixture, crash/recovery,
   backup/restore, clean-install, wheel, and cross-repository compatibility
   evidence before publication.

## Dependency order

1. **Store core compatibility**: add tests for old and new paths; preserve
   format compatibility and legacy fixtures.
2. **Store packaging**: publish `grumo-store`, `grumo_store`, CLI and Rust
   workspace crates only after bindings, packaging, lockfiles, and release
   workflows are updated together.
3. **Framework**: move `voodoo` to `grumo`, update package entry points,
   configuration, runtime, decorators, scaffold, and imports.
4. **Generated application path**: default to `.grumo/application.grumo`;
   provide an explicit copy/verify/activate/rollback migration command.
5. **Site, templates, skills, edge and release automation**: upgrade to the
   published Grumo packages and verify all generated example applications.
6. **GitHub repository rename and official cutover**: do last, after
   distribution and all cross-repository gates succeed.

## Acceptance tests for path migration

- Legacy `.vstore` readable at the `.grumo` path.
- Same Store ID, format major/minor, and original user data.
- Original remains unchanged; no auto-activation or overwrite.
- Legacy `0.2.2` fixture still passes retained compatibility tests.
- Verified backups, restore-copy and rollback from an independent path work.
- Store is closed before copy; no duplicate live writers.

## Explicitly out of scope for the rename

- Store replication and automatic mobile sync (not yet implemented).
- New distributed consistency or exactly-once guarantees.
- Rewriting the canonical Runtime execution model.
- Switching the Store file format simply to match the new product name.

The Grumo brand is a unified programmable runtime, application framework,
durable infrastructure engine, and distributed/edge execution ecosystem.
Local-first is one supported deployment style, **not** the entire product.

## Explicit migration command (implemented in this branch)

**Stop the application and close the Store writer before invoking this
command.** The utility verifies the source, creates an independent rollback
copy, restores a second verified copy into the new path, and prints the
identity of the resulting Store. It does not activate the new file.

```bash
python -m voodoo_store.grumo_migration \
  .voodoo/application.vstore \
  .grumo/application.grumo \
  --backup backups/pre-grumo.vstore \
  --dry-run

python -m voodoo_store.grumo_migration \
  .voodoo/application.vstore \
  .grumo/application.grumo \
  --backup backups/pre-grumo.vstore
```

The CLI still lives inside the old `voodoo_store` distribution during this
transition. Once the new package is published, expose this through `grumo`
and `grumo_store`. Paths are create-only: existing destination or backup
files are not overwritten. The returned `activated: false` is intentional;
configure the application to use the new file only after accepting test and
backup evidence. Keep the legacy source for rollback.

Run targeted tests:

```bash
python -m pytest -q python/tests/test_grumo_migration.py \
  python/tests/test_operations.py
```

