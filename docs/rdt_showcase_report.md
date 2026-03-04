# RDT Project Showcase Report

- Generated (UTC): `2026-03-04T03:45:18.297244+00:00`

## Repository Refs
- `rdt-noise`: branch `steven/rdt-noise-honest-upgrades`, commit `9d5f876a9eaa1eadd52a85b835f825dee471bc1a`
- `rdt-spatial-index`: branch `steven/rdt-spatial-index-honest-upgrades`, commit `f3bc0d8868ba4ad6561d32f32ed37ddb22ff12eb`
- `rdt256`: branch `steven/rdt256-honest-upgrades`, commit `e72d6665a538e4566f406a13a998bd5935e3edae`

## 1) RDT-Noise
- Hybrid speedup vs standard RDT: `1.796x`
- Standard RDT / white speed ratio: `205.945` (greater than 1 means slower)
- Hybrid entropy delta vs standard RDT: `-0.000124` bits/byte
- Hybrid mean |ACF| delta vs standard RDT: `-0.000073`
- Verdict: Hybrid improves RDT runtime substantially while preserving similar noise statistics; RDT variants remain far slower than simple white-noise baselines.

## 2) RDT Spatial Index
| dataset | rdt query ms | rdt_optimized query ms | speedup rdt/opt | grid query ms | kd query ms | opt exact match |
|---|---:|---:|---:|---:|---:|---:|
| uniform_random | 113.97 | 10.39 | 10.97x | 3.24 | 11.89 | 1.0000 |
| clustered | 153.02 | 14.41 | 10.62x | 3.75 | 18.57 | 1.0000 |
| adversarial_line | 131.62 | 39.95 | 3.29x | 6.54 | 71.80 | 1.0000 |
- Verdict: Tuned RDT preserves exactness and strongly improves over untuned RDT, but uniform grid is still fastest on these benchmark sets.

## 3) RDT256
- v3 speedup vs v2: `0.818x`
- quality-proxy delta (v3-v2): `-0.000040` (negative means better)
- v2 speed ratio vs SplitMix64: `0.064`
- Verdict: v3 shows a small quality-proxy improvement over v2 but no throughput win; both RDT streams are much slower than SplitMix64.

## 4) RDT Toolbox Index
- Clear win count: `6`
- Best margin: `77.6%`
- Packaging choice: `Option B: RDTShard`
- Verdict: RDT hierarchy shows clear measurable gains for shard-resize stability with ancestor buckets plus stable mapping, while baseline hash map remains faster for pure point lookups.

## Where RDT Is Legitimately Strong
- RDT spatial hierarchy as a tunable exact partition (relative to untuned RDT baseline).
- Hybrid RDT-noise scheduler (RDT-guided reseeding + fast conventional core).
- Quality-tuned RDT256 output-stage variants for exploratory statistical shaping.
- RDTShard-style stable repartitioning under shard-count changes.

## Honesty / Limits
- No universal superiority claims are made.
- All wins are tied to explicit benchmark settings in repository result files.
- Negative findings are retained and reported.

## Next Upgrade Targets
1. RDT spatial index: add adaptive hybrid dispatcher (RDT vs grid) by local anisotropy; optimize for query latency while preserving exactness.
2. RDT-noise: use vectorized kernels for state transition while preserving deterministic reproducibility gates.
3. RDT256: move core to a two-track implementation (quality mode and throughput mode), then benchmark both modes against fixed acceptance thresholds.
