# RDT Toolbox

[![CI](https://github.com/RRG314/RDT-toolbox/actions/workflows/ci.yml/badge.svg)](https://github.com/RRG314/RDT-toolbox/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./pyproject.toml)
[![Release](https://img.shields.io/github/v/release/RRG314/RDT-toolbox)](https://github.com/RRG314/RDT-toolbox/releases)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17487650.svg)](https://doi.org/10.5281/zenodo.17487650)

A practical Python toolbox for **deterministic hierarchical indexing and sharding** based on the Recursive Division Tree (RDT).

If you need explainable bucket structure, stable repartitioning, and reproducible benchmark evidence, this repo is for you.

## What This Is Best For

- deterministic shard assignment from integer keys
- minimizing key movement when shard counts change
- hierarchical bucket queries and ancestry-based grouping
- experimentation with base vs optimized RDT variants using reproducible tests

## What This Is Not Best For

- fastest possible raw point lookup (hash maps usually win)
- cryptographic guarantees (RDT PRNG components are research-grade, not security-certified)

## Install

From source (local dev):

```bash
git clone https://github.com/RRG314/RDT-toolbox.git
cd RDT-toolbox
pip install -e .
```

Or directly from GitHub:

```bash
pip install "git+https://github.com/RRG314/RDT-toolbox.git"
```

## Quick Start: Plugin-Style Usage

### 1) Sharding Plugin (base)

```python
from rdt_showcase import RDTShardPlugin

keys = list(range(1, 100000))
sharder = RDTShardPlugin(shard_count=16, shard_depth=8, stable_sharding=True)
sharder.configure_keys(keys)

# Route a key to shard
print(sharder.shard_for(123456))

# Estimate movement before resharding 16 -> 20
print(sharder.movement_rate(keys, new_shard_count=20))
```

### 2) Sharding Plugin (dual-tuned)

```python
from rdt_showcase import RDTDualShardPlugin

keys = list(range(1, 100000))
sharder = RDTDualShardPlugin(shard_count=16, min_depth=4, max_depth=12, init_depth=8.0)
sharder.configure_keys(keys)

print(sharder.plan.shard_depth)   # tuned depth
print(sharder.tuning)             # tuning metadata
print(sharder.shard_for(123456))
```

### 3) Bucket Query Plugin

```python
from rdt_showcase import RDTBucketPlugin

items = [(k, {"payload": k}) for k in range(1, 20000)]
bucket = RDTBucketPlugin(max_bucket_depth=12)
bucket.build(items)

# query one ancestor bucket
rows = bucket.query_ancestor_bucket(depth_k=8, bucket_id=1)
print(len(rows))

# approximate neighbors by shared ancestry
neighbors = bucket.approximate_neighbors(1500, k_neighbors=8)
print(neighbors)
```

## Library API

Main import package: `rdt_showcase`

- Core indexes:
  - `RDTIndex`
  - `RDTDualTunedIndex`
- Plugin adapters:
  - `RDTShardPlugin`
  - `RDTDualShardPlugin`
  - `RDTBucketPlugin`
- Baselines:
  - `HashMapIndex`
  - `SortedArrayIndex`
  - `BTreeLikeIndex`
- Dual numbers:
  - `Dual`, `exp`, `log`, `sigmoid`

## Reproducible Benchmarks and Tests

```bash
make test
make benchmark-index
make benchmark-showcase
make benchmark-all
```

Artifacts:
- `results/rdt_index_benchmark.json`
- `docs/rdt_index_benchmark.md`
- `results/showcase_summary.json`
- `docs/rdt_showcase_report.md`

## Current Measured Win Case

RDT wins clearly on **stable shard repartitioning**:
- ancestor buckets + stable mapping produce substantially lower key movement on shard-count changes than baseline modulo partitioning.

This is tracked in benchmark reports with adversarial cases included.

## Documentation

- [Docs Index](./docs/INDEX.md)
- [Math/CS Spec](./docs/rdt_math_cs_spec.md)
- [Verification Matrix](./docs/verification_matrix.md)
- [Reproducibility Guide](./docs/reproducibility.md)
- [Papers and Zenodo Links](./docs/papers_and_zenodo.md)
- [PRNG / Noise / Indexing Overview](./docs/prng_noise_indexing_overview.md)
- [Draft Release Notes](./docs/release_draft_v0.1.0.md)

## Citation

- Software metadata: [`CITATION.cff`](./CITATION.cff)
- Core RDT paper (Zenodo): [https://zenodo.org/records/17487651](https://zenodo.org/records/17487651)

## Suggested GitHub Repo Description

Copy/paste this for the repository description field:

`Deterministic RDT indexing and sharding toolbox with benchmarked base/optimized variants, plugin adapters, and reproducible math+CS verification.`
