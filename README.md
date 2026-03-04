# RDT Toolbox

RDT Toolbox is a coherent math/CS repository for your Recursive Division Tree work.

It combines:
- RDT base implementations
- RDT optimized variants (kept only with measurable benchmark gain)
- independent tests and reproducible benchmark artifacts
- paper/citation metadata (including Zenodo links)

## Core Idea

Use the RDT hierarchy induced by repeated halving:
- parent map `f(n)=floor(n/2)` for `n>1`, `f(1)=1`
- depth `D(n)=floor(log2 n)`
- ancestor buckets `A_k(n)=max(1,floor(n/2^k))`

This repo packages those structures as practical indexing/sharding tools and evaluates them against standard baselines.

## Library Components

Package: `src/rdt_showcase/`

- `RDTIndex`: base depth/ancestor bucket index
- `RDTDualTunedIndex`: dual-number-guided shard-depth tuning variant
- `Dual`: forward-mode dual number type for autodiff
- Baselines for fair comparison:
  - `HashMapIndex`
  - `SortedArrayIndex`
  - `BTreeLikeIndex`

## Quick Usage

```python
from rdt_showcase import RDTIndex, RDTDualTunedIndex

idx = RDTIndex(bucket_mode="ancestor", shard_depth=8, stable_sharding=True)
idx.build((k, k * 10) for k in range(1, 10000))
print(idx.get(42))
print(idx.query_bucket(8, idx.ancestor(42, 8), query_mode="ancestor")[:3])

opt = RDTDualTunedIndex(min_depth=4, max_depth=12, init_depth=8.0)
opt.build((k, k * 10) for k in range(1, 10000))
print(opt.shard_depth, opt.tuning["objective"])
```

## Reproducible Commands

```bash
make test
make benchmark-index
make benchmark-showcase
make benchmark-all
```

Outputs:
- `results/rdt_index_benchmark.json`
- `docs/rdt_index_benchmark.md`
- `results/showcase_summary.json`
- `docs/rdt_showcase_report.md`

## Win Case and Limits

Current measured win case:
- **RDTShard-style stable repartitioning** (ancestor buckets + stable mapping) shows clearly lower key movement when shard count changes.

Explicit limits (kept in repo reports):
- hash-map baselines are still faster for pure point lookup in many workloads
- no universal superiority claim
- no cryptographic security claim for RDT PRNG streams

## Documentation Map

- [Documentation Index](./docs/INDEX.md)
- [Math/CS Spec](./docs/rdt_math_cs_spec.md)
- [Verification Matrix](./docs/verification_matrix.md)
- [Reproducibility Guide](./docs/reproducibility.md)
- [Papers and Zenodo Links](./docs/papers_and_zenodo.md)
- [Draft Release Notes v0.1.0](./docs/release_draft_v0.1.0.md)

## Citation

- Software citation metadata: [`CITATION.cff`](./CITATION.cff)
- Core RDT paper (Zenodo): [https://zenodo.org/records/17487651](https://zenodo.org/records/17487651)

## External Component Integration

For cross-repo summary (`tools/run_showcase.py`), keep sibling repos available:
- `../rdt-noise`
- `../rdt-spatial-index`
- `../rdt256`
