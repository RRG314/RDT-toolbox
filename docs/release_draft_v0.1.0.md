# Draft Release Notes - v0.1.0

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
