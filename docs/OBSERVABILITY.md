# Native Store observability

Grumo Store exposes operational signals through its Rust health report, Python `Store.health_report()` and CLI health command. No external monitoring service or dashboard server is required.

The machine-readable [observability contract](OBSERVABILITY_CONTRACT.json) defines native signals, presentation groups and baseline alert thresholds for storage, queues, durability and recovery. It is the basis for Grumo Studio's native monitoring experience. Studio is a planned interface, not a required runtime dependency; alerts and historical sampling in Studio are not yet implemented.

Run `python scripts/check_observability_contract.py` after changing health signals. CI checks the contract against the native public surfaces. Benchmark history remains collected by the scheduled performance workflow for development regression analysis.
