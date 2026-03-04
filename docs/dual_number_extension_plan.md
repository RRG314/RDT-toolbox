# Dual / Hyperreal Extension Status

This repository now includes a concrete dual-number tooling path as a usable library component.

## Implemented

- Dual-number engine: `src/rdt_showcase/dual.py`
- Dual-guided parameter tuner: `src/rdt_showcase/dual_tuning.py`
- Dual-tuned index variant: `RDTDualTunedIndex`
- Benchmark integration: `rdt_ancestor_dual` system in `tools/benchmark_rdt_index.py`

## What It Optimizes

Dual tuning is used to select shard depth via a smooth objective over integer depth candidates:
- shard movement (`16 -> 20` shards)
- shard load balance (CV)
- ancestor-bucket balance (CV)

The tuned depth is chosen at build time and then used as a standard deterministic RDT ancestor index parameter.

## Validation Requirements

A dual variant is only retained when benchmark artifacts show a measurable gain in at least one tracked metric.

Primary artifact:
- `results/rdt_index_benchmark.json`
- `docs/rdt_index_benchmark.md`

## Integrity Rule

Do not claim novelty or superiority from symbolic derivations alone.
Keep only benchmarked, reproducible improvements.
