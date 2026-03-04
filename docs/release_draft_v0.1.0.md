# Release Notes - v0.1.0

[![CI](https://github.com/RRG314/RDT-toolbox/actions/workflows/ci.yml/badge.svg)](https://github.com/RRG314/RDT-toolbox/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/RRG314/RDT-toolbox/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://github.com/RRG314/RDT-toolbox/blob/main/pyproject.toml)
[![Release](https://img.shields.io/github/v/release/RRG314/RDT-toolbox)](https://github.com/RRG314/RDT-toolbox/releases)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17487650.svg)](https://doi.org/10.5281/zenodo.17487650)

## Release Theme
RDT Toolbox initial coherent release: math spec + library tooling + reproducible benchmark evidence.

## Included
- `rdt_showcase` Python library:
  - `RDTIndex` (depth and ancestor modes)
  - `RDTDualTunedIndex` (dual-number-guided shard-depth tuning)
  - Baselines: hash map, sorted array, B-tree-like
  - Dual number module for forward-mode autodiff
- Reproducible test suite (`tests/`)
- RDT index benchmark suite (`tools/benchmark_rdt_index.py`) over W1/W2/W3/W4
- Cross-repo consolidator (`tools/run_showcase.py`) for:
  - `rdt-noise`
  - `rdt-spatial-index`
  - `rdt256`
- Documentation set:
  - math/CS spec
  - verification matrix
  - reproducibility guide
  - papers + Zenodo citation index

## Benchmark Headline (Honest)
- Clear measurable win case: RDT stable ancestor sharding yields substantially lower key movement on shard-count change.
- Explicit non-win cases are retained (e.g., pure lookup speed often favors hash map baselines).

## Citation
- Core RDT paper (Zenodo): [https://zenodo.org/records/17487651](https://zenodo.org/records/17487651)
- Software citation metadata: `CITATION.cff`

## Known Limits
- No cryptographic-security claim for RDT PRNG streams.
- No universal index-performance superiority claim.
- Dual-number variants should only be claimed as improvements when benchmark artifacts show a gain.
