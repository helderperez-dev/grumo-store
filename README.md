# Grumo Store

> **Application infrastructure in a store.**

Grumo Store is a **standalone, 100% Rust embedded application-state engine** built around one goal:

> **A Grumo application should be able to run robustly with Grumo + Grumo Store and no mandatory external infrastructure by default.**

It is being built for the Grumo ecosystem, but the core is not coupled to Grumo Framework. The engine and `.vstore` format are designed to remain language-neutral and independently usable.

**SQLite made the database a file. Grumo Store aims to make application infrastructure a store.**

## Status

**Release line: 2.0 (in development); latest published release: 1.0.0.**

Grumo Store provides native primitives for controlled single-node deployments. The 2.0 release removes transitional naming and APIs while retaining the independently versioned storage format.

The current engine includes:

- versioned, checksummed `.vstore` files and strong persistent Store identity;
- checksummed append-only logging, atomic transactions and deterministic crash recovery;
- Linux/macOS/Windows single-writer locking and explicit durability modes;
- byte-oriented KV, CAS, counters, prefix scans and TTL;
- Collections with schema/codec metadata and secondary/unique indexes;
- durable Queues with leases, delay, priority, retry/NACK, dead state and stale-ACK protection;
- durable Jobs with 128-bit IDs, idempotency, retry/backoff, deadlines and execution history;
- one-shot, interval and deterministic UTC Cron scheduling;
- durable Triggers;
- Topics, Streams, replay, durable subscriptions and Consumer Groups;
- durable request/reply correlation and RPC state;
- transactional Outbox events;
- content-addressed SHA-256 object storage, deduplication, verification, references and orphan GC;
- durable Workflow/HITL state with waits, signals, timers and history;
- verify, backup, create-only restore, logical snapshots and compact-copy;
- structured health/storage accounting;
- standalone `grumo-store` CLI;
- C ABI v2 foundation with transactions, `last_error` and panic containment;
- deterministic corruption, torn-write and process-crash testing;
- CI across Format, Clippy, Linux, macOS, Windows and Rust 1.85 MSRV.

Version numbers do not imply production certification. Review the operational limits and verify backups before upgrades.

## Install the Python binding

```bash
pip install grumo-store
```

```python
from grumo_store import Store

with Store.open("application.grumo") as store:
    store.put(b"hello", b"world")
    assert store.get(b"hello") == b"world"
```

## Start here

Build and test:

```bash
cargo build --workspace
cargo test --workspace
```

Run the executable application-state example:

```bash
cargo run -p grumo-store-core --example application_state -- application.grumo
```

The example commits application state, a durable Job and an Outbox Event through one transaction:

```text
BEGIN
  PUT order:42:status = paid
  ENQUEUE JOB email.send_receipt(order:42)
  EMIT EVENT order.paid(order:42)
COMMIT
```

If that transaction does not commit, none of those staged mutations become visible after recovery.

See `docs/QUICKSTART.md` for the full walkthrough.
See `docs/VERSIONING.md` for package, format, and Python binding compatibility.

## North Star

The standard Grumo deployment is intentionally small:

```text
Application
    |
    +-- Grumo Runtime
    |
    `-- application.grumo
```

A normal application should not need Redis, PostgreSQL, RabbitMQ, Kafka, Celery, a separate cron service, or a separate local object service merely to get robust application infrastructure.

External infrastructure remains available as optional adapters when scale or deployment topology genuinely requires it.

## Architecture

```text
Applications / Frameworks
        |
        +-- Grumo Runtime / Framework
        +-- Rust
        +-- C / native bindings
        +-- Python binding
        +-- future Node / Go / Swift bindings
        |
Stable APIs / bindings
        |
grumo-store-core
        |
        +-- Data: KV / TTL / Collections / Indexes
        +-- Work: Queues / Jobs / Scheduler / Cron / Triggers
        +-- Messaging: Topics / Streams / Consumer Groups / RPC / Outbox
        +-- Objects
        +-- Workflow state
        +-- Operations / health / lifecycle
        |
Transaction / Commit Layer
        |
Append-only Checksummed Log
        |
Recovery / Verification
        |
Versioned .vstore Header
        |
Filesystem + File Locking
```

The Store persists durable semantics. Grumo Runtime executes application code, HTTP handlers, AI inference, external calls and Identity/Auth behavior.

## Cross-domain transactions

A major Grumo Store goal is to remove the split-brain normally created by a database plus external work infrastructure.

Current typed transaction primitives already allow application state, Jobs, Outbox Events and durable RPC Requests to share a Store transaction.

```rust
use grumo_store_core::{JobSpec, Store};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut store = Store::open("application.grumo")?;

    let mut tx = store.begin()?;
    tx.put(b"order:42:status", b"paid")?;
    tx.enqueue_job(JobSpec::new(b"email.send_receipt", b"order:42"), 1_000)?;
    tx.emit_event(b"order.paid", b"order:42", 1_000)?;
    tx.request_rpc(b"payments.capture", b"order:42", 1_000, Some(31_000))?;
    tx.commit()?;

    Ok(())
}
```

The public cross-domain transaction surface will continue expanding to additional primitives in future releases.

## Durability

```rust
use grumo_store_core::{Durability, Store, StoreOptions};

let store = Store::open_with_options(
    "application.grumo",
    StoreOptions {
        durability: Durability::Strict,
        repair_torn_tail: true,
    },
)?;
```

- `Strict` uses `sync_all()` on commit.
- `Data` uses `sync_data()` on commit and is the default.
- `Relaxed` relies on later operating-system flushing.

Only an incomplete physical tail is automatically repairable. Corruption inside the durable prefix is surfaced as an error rather than silently discarded.

The CLI keeps repair explicit and read-only by default. Run
`grumo-store repair <path>` to inspect a torn tail; after taking a backup,
repeat with `--confirm-torn-tail` to authorize truncation. The command verifies
the store again after repair. It never attempts to rewrite corruption inside a
previously valid durable prefix.

## Current good-fit workloads

The current release line is a reasonable target for controlled use in:

- Grumo Runtime development;
- SaaS/internal-tool prototypes and early deployments;
- desktop/local-first applications;
- AI agent and automation state;
- edge gateways and robotics controllers;
- single-node APIs that want durable Jobs/Queues without deploying an infrastructure stack.

Pin the exact Store version and keep backups for important stores.

Python operators can create a verified JSON sidecar alongside a backup:

```python
from grumo_store import create_backup_manifest, verify_backup_manifest

manifest = create_backup_manifest(store, "application.backup.grumo")
verify_backup_manifest("application.backup.grumo", "application.backup.grumo.manifest.json")
```

## Known limits

Remaining engineering work includes:

- continuous hosted fuzzing, filesystem-specific power-loss certification, and
  stronger repair tooling;
- filesystem/power-loss proof for generation activation and stronger repair tooling;
- completing Python/native convergence for cross-domain transactions;
- migrating Grumo Framework compatibility adapters onto the native messaging/object/query surfaces;
- richer Collection migration/composite-index/query-planner support and physical ordered range seeks;
- live-query/watch convenience APIs above the durable change feed;
- streaming object writes and zero-copy/on-disk reads (bounded native chunk
  reads are available today);
- complete C ABI coverage and additional first-class language bindings;
- encryption-at-rest/key-rotation design;
- later replication/sync and Grumo Protocol integration.

Namespace/file quotas, structured health metrics, tracing hooks, and bounded
object lifecycle/retention policies are already part of the v0.3.0 contract.

Store Studio and distributed operation are later milestones and do not block controlled single-node use.

## CLI

The workspace includes the standalone `grumo-store` binary. Examples:

```bash
cargo run -p grumo-store-cli -- put application.grumo hello world
cargo run -p grumo-store-cli -- get application.grumo hello
cargo run -p grumo-store-cli -- health application.grumo
cargo run -p grumo-store-cli -- verify application.grumo
cargo run -p grumo-store-cli -- backup application.grumo application.backup.grumo
```

The CLI also exposes lifecycle, Queue, Collection, Messaging, Object, Job, Scheduler, Cron, Trigger and Workflow operations. See `docs/QUICKSTART.md` for usage guidance.

## C ABI

`grumo-store-ffi` is the portability foundation for non-Rust bindings. The current ABI includes Store handles, KV operations, buffered transactions, thread-local `last_error` reporting and panic containment. The checked-in C consumer (`crates/grumo-store-ffi/examples/c_consumer.c`) is compiled and executed by CI and release preflight; higher-level primitive coverage is still expanding.

Public header:

```text
include/grumo_store.h
```

## Workspace

```text
crates/
  grumo-store-core/   # correctness-critical embedded engine
  grumo-store-ffi/    # C ABI portability layer
  grumo-store-cli/    # standalone inspection and operation CLI

include/
  grumo_store.h

examples/
  c_consumer.c       # committed ABI consumer smoke

docs/
  ARCHITECTURE.md
  SPEC.md
  INVARIANTS.md
  ROADMAP.md
  QUICKSTART.md
```

## Grumo integration

Grumo Framework/Runtime already consumes the published Python binding behind higher-level primitives while the engine stays independently usable. The 0.3 convergence work removes remaining compatibility implementations where the Rust core already has a native primitive.

```text
Grumo Model       -> Store Collections / data
Grumo @task       -> Store Jobs / Queues
Grumo Scheduler   -> Store schedules / Cron
Grumo events      -> Store Topics / Streams / Outbox
Grumo ObjectStore -> Store Objects
Execution / HITL   -> Store Workflow state
Runtime Identity   -> durable state persisted through Store
```

Identity/Auth semantics remain in Grumo Runtime, not in Grumo Store.

## Compatibility principle

The lowest-level durable contract is bytes. Grumo Store does not persist host-specific Python pickle, Java serialization, V8 objects or Go gob as its core format. Typed codecs and schemas are layered above the engine so a compatible Store can be accessed from multiple runtimes.

## Development principle

Correctness comes before feature count and benchmarks:

```text
SPEC
  -> INVARIANTS
  -> IMPLEMENTATION
  -> TESTS
  -> FAULT INJECTION
  -> FUZZING
  -> BENCHMARKS
  -> OPTIMIZATION
```

## License

Apache-2.0
