# Reproducibility Guide

## Local Python Setup

No external Python dependencies are required for core tests/benchmarks in this repo.

## 1) Run Unit Tests

```bash
python3 tools/run_tests.py
```

## 2) Run RDT Index Benchmark Suite

```bash
python3 tools/benchmark_rdt_index.py
```

Outputs:
- `results/rdt_index_benchmark.json`
- `docs/rdt_index_benchmark.md`

## 3) Cross-Repo Showcase Summary

Requires sibling repos:
- `../rdt-noise`
- `../rdt-spatial-index`
- `../rdt256`

Run:

```bash
python3 tools/run_showcase.py
```

Outputs:
- `results/showcase_summary.json`
- `docs/rdt_showcase_report.md`

## 4) Fast Commands (Makefile)

```bash
make test
make benchmark-index
make benchmark-showcase
make benchmark-all
```

## Independent Verification Expectations

For each component, keep both:
- test scripts (`tests/`)
- generated reports (`docs/` + `results/`)

Do not rely on narrative claims without matching artifact files.
