# RDT Components Overview: PRNG, Noise, Indexing

This toolbox tracks three separate RDT component lines and consolidates their benchmark evidence.

## 1) RDT Noise (`rdt-noise`)

Tracked variants:
- `rdt_standard`
- `rdt_chaos_seeded`
- `rdt_hybrid_fast` (RDT scheduler + conventional fast stream)

Current evidence (see cross-repo report):
- hybrid variant improves runtime vs standard RDT-noise
- white-noise baseline remains much faster

Source artifact:
- `../rdt-noise/results/noise_benchmark_report.md`

## 2) RDT Spatial Index (`rdt-spatial-index`)

Tracked systems:
- `rdt` (base)
- `rdt_optimized` (parameter-tuned)
- `uniform_grid`, `kd_tree` baselines

Current evidence:
- `rdt_optimized` gives strong speedup vs base `rdt`
- all systems in report keep exact-match correctness
- grid baseline still fastest in tested sets

Source artifact:
- `../rdt-spatial-index/results/benchmark_report.md`

## 3) RDT Stream PRNG (`rdt256`)

Tracked generators:
- `rdt_prng_stream_v2`
- `rdt_prng_stream_v3`
- `splitmix64` baseline

Current evidence:
- v3 quality-proxy improves over v2 in current runs
- throughput remains lower than splitmix baseline
- no cryptographic security claim

Source artifact:
- `../rdt256/results/stream_benchmark_report.md`

## 4) RDT Toolbox Index (`this repo`)

Tracked systems include:
- `rdt_depth`
- `rdt_ancestor`
- `rdt_ancestor_stable`
- `rdt_ancestor_dual` (dual-tuned)
- hash/sorted/B-tree-like baselines

Current win case:
- stable ancestor sharding strongly reduces key movement under shard-count change.

Source artifacts:
- `results/rdt_index_benchmark.json`
- `docs/rdt_index_benchmark.md`
