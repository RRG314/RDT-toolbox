# Dual / Hyperreal Extension Plan (No Claims Yet)

This document records how to evaluate dual-number inspired variants honestly.

## Why This Might Help

Potential benefit area:
- parameter sensitivity tuning for RDT variants (e.g., selecting depth level `k`, shard-depth settings, or hybrid schedule weights)

## What Must Be Proven Empirically First

A dual-number or hyperreal variant should only be kept if it improves at least one measurable target in existing benchmarks:
- lower shard movement rate for same load balance
- lower bucket-query `p95` without regressions in lookup `p95`
- better mixed read/write throughput without large memory cost

## Minimal Experiment Design

1. Add a variant module under `src/rdt_showcase/`.
2. Add it as a system in `tools/benchmark_rdt_index.py`.
3. Re-run full W1/W2/W3/W4 suite.
4. Keep the variant only if a clear win exists in `docs/rdt_index_benchmark.md`.

## Integrity Rule

Do not claim novelty or superiority from symbolic derivations alone.
Keep only benchmarked, reproducible improvements.
