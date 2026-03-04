# RDT Index Benchmark

- Generated (UTC): `2026-03-04T04:00:01.317622+00:00`
- Seed: `1729`
- Static workload size: `30000`
- Mixed R/W initial size: `15000`

## Systems
- `rdt_depth`: RDT keyed by depth D(key), modulo shard mapping
- `rdt_ancestor`: RDT keyed by ancestor bucket at fixed depth, modulo shard mapping
- `rdt_ancestor_stable`: same ancestor buckets with jump-consistent shard mapping
- `rdt_ancestor_dual`: stable ancestor buckets with dual-number-guided shard-depth tuning
- `hash_map`, `sorted_array`, `btree_like`: required baselines

## Static Workloads (W1/W2/W3)
### W1_uniform_random (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 232.28 | 110.14 | 0.708 | 1244.010 | 1.922 | 15093 | 1.000 |
| rdt_ancestor | 219.86 | 110.14 | 0.459 | 1230.420 | 1.922 | 15093 | 0.801 |
| rdt_ancestor_stable | 296.32 | 110.14 | 0.458 | 1220.013 | 1.922 | 15093 | 0.199 |
| rdt_ancestor_dual | 2789.77 | 110.14 | 0.500 | 1224.171 | 1.922 | 15093 | 0.199 |
| hash_map | 1.96 | 3.01 | 0.417 | 3216.762 | 1.922 | 15093 | 0.801 |
| sorted_array | 13.32 | 2.23 | 0.625 | 2281.038 | 1.922 | 15093 | 0.801 |
| btree_like | 12.74 | 3.83 | 5.458 | 1595.269 | 1.922 | 15093 | 0.801 |

### W2_sequential (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 112.59 | 34.14 | 0.416 | 1887.333 | 0.000 | 30000 | 1.000 |
| rdt_ancestor | 114.64 | 34.14 | 0.416 | 1882.952 | 0.000 | 30000 | 0.845 |
| rdt_ancestor_stable | 101.73 | 34.14 | 0.500 | 1941.513 | 0.000 | 30000 | 0.179 |
| rdt_ancestor_dual | 1786.35 | 34.14 | 0.416 | 1852.471 | 0.000 | 30000 | 0.149 |
| hash_map | 1.23 | 2.85 | 0.375 | 3168.290 | 0.000 | 30000 | 0.800 |
| sorted_array | 3.24 | 2.07 | 0.583 | 3295.783 | 0.000 | 30000 | 0.800 |
| btree_like | 2.39 | 3.68 | 3.750 | 2049.331 | 0.000 | 30000 | 0.800 |

### W3_clustered (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 115.30 | 34.25 | 0.458 | 860.362 | 0.408 | 14925 | 1.000 |
| rdt_ancestor | 113.62 | 34.25 | 0.416 | 859.096 | 0.408 | 14925 | 0.805 |
| rdt_ancestor_stable | 118.23 | 34.25 | 0.458 | 902.431 | 0.408 | 14925 | 0.214 |
| rdt_ancestor_dual | 1814.09 | 34.26 | 0.416 | 884.506 | 0.408 | 14925 | 0.195 |
| hash_map | 1.36 | 2.85 | 0.375 | 3171.664 | 0.408 | 14925 | 0.800 |
| sorted_array | 6.60 | 2.07 | 0.708 | 2013.933 | 0.408 | 14925 | 0.800 |
| btree_like | 5.53 | 3.68 | 4.023 | 967.927 | 0.408 | 14925 | 0.800 |

### W1_uniform_random (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 197.99 | 110.14 | 0.750 | 1.377 | 0.086 | 4 | 1.000 |
| rdt_ancestor | 308.43 | 110.14 | 0.458 | 1.166 | 0.086 | 4 | 0.801 |
| rdt_ancestor_stable | 249.35 | 110.14 | 0.458 | 1.125 | 0.086 | 4 | 0.199 |
| rdt_ancestor_dual | 2928.07 | 110.14 | 0.459 | 1.333 | 0.086 | 4 | 0.199 |
| hash_map | 2.24 | 3.01 | 0.417 | 4047.752 | 0.086 | 4 | 0.801 |
| sorted_array | 14.00 | 2.23 | 0.709 | 1.750 | 0.086 | 4 | 0.801 |
| btree_like | 13.74 | 3.83 | 4.875 | 3.877 | 0.086 | 4 | 0.801 |

### W2_sequential (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 103.73 | 34.14 | 0.459 | 55.637 | 0.094 | 1024 | 1.000 |
| rdt_ancestor | 104.64 | 34.14 | 0.459 | 52.333 | 0.094 | 1024 | 0.845 |
| rdt_ancestor_stable | 102.62 | 34.14 | 0.417 | 51.960 | 0.094 | 1024 | 0.179 |
| rdt_ancestor_dual | 1795.04 | 34.14 | 0.416 | 51.794 | 0.094 | 1024 | 0.149 |
| hash_map | 1.73 | 2.85 | 0.334 | 3531.054 | 0.094 | 1024 | 0.800 |
| sorted_array | 3.53 | 2.07 | 0.625 | 32.465 | 0.094 | 1024 | 0.800 |
| btree_like | 2.38 | 3.68 | 3.648 | 57.377 | 0.094 | 1024 | 0.800 |

### W3_clustered (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 122.48 | 34.25 | 0.375 | 58.750 | 0.283 | 1024 | 1.000 |
| rdt_ancestor | 116.37 | 34.25 | 0.375 | 57.337 | 0.283 | 1024 | 0.805 |
| rdt_ancestor_stable | 114.09 | 34.25 | 0.416 | 57.008 | 0.283 | 1024 | 0.214 |
| rdt_ancestor_dual | 1828.22 | 34.26 | 0.375 | 55.635 | 0.283 | 1024 | 0.195 |
| hash_map | 1.46 | 2.85 | 0.417 | 3723.127 | 0.283 | 1024 | 0.800 |
| sorted_array | 6.41 | 2.07 | 0.625 | 36.506 | 0.283 | 1024 | 0.800 |
| btree_like | 5.35 | 3.68 | 3.500 | 64.542 | 0.283 | 1024 | 0.800 |

## W4 Mixed Read/Write
### read_80_write_20
| system | throughput ops/s | read_p95_us | write_p95_us | final_size |
|---|---:|---:|---:|---:|
| rdt_depth | 719392.1 | 0.333 | 4.500 | 16261 |
| rdt_ancestor | 722764.6 | 0.292 | 4.410 | 16164 |
| rdt_ancestor_stable | 674526.8 | 0.375 | 4.923 | 16218 |
| rdt_ancestor_dual | 754171.5 | 0.291 | 4.459 | 16190 |
| hash_map | 1735985.5 | 0.167 | 0.208 | 16225 |
| sorted_array | 412452.6 | 0.666 | 10.292 | 16218 |
| btree_like | 197499.7 | 4.292 | 10.375 | 16246 |

### read_95_write_5
| system | throughput ops/s | read_p95_us | write_p95_us | final_size |
|---|---:|---:|---:|---:|
| rdt_depth | 1379561.5 | 0.292 | 4.834 | 15308 |
| rdt_ancestor | 1365860.9 | 0.333 | 4.958 | 15301 |
| rdt_ancestor_stable | 1270681.7 | 0.334 | 5.169 | 15294 |
| rdt_ancestor_dual | 1334494.9 | 0.292 | 5.006 | 15278 |
| hash_map | 1999472.1 | 0.166 | 0.208 | 15330 |
| sorted_array | 866556.3 | 0.500 | 10.042 | 15302 |
| btree_like | 262790.5 | 3.375 | 9.959 | 15315 |

## Adversarial Findings (Where RDT Loses)
- `W1_uniform_random` (depth): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.708us`, best baseline `0.417us`).
- `W2_sequential` (depth): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.416us`, best baseline `0.375us`).
- `W3_clustered` (depth): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.458us`, best baseline `0.375us`).
- `W1_uniform_random` (ancestor): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.750us`, best baseline `0.417us`).
- `W2_sequential` (ancestor): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.459us`, best baseline `0.334us`).

## Smallest RDT-Based Fix and Rerun
- Problem: Depth-only RDT partitions are coarse and suffer from poor shard-resize stability under modulo mapping.
- Fix: Use ancestor bucket IDs (ancestor(key, k)) and stable shard mapping (jump-consistent-hash on bucket ID).
- Dual extension: Dual-number-guided tuning of shard depth on a smooth sharding objective.
- Rerun included: `True`
- Improvement check (movement metric): `True`

## Win Case Decision
RDT has a clear measurable win on sharding-resize stability:
- `W1_uniform_random` (depth): movement `rdt_ancestor_stable=0.199` vs best baseline `0.801` (margin `75.1%`).
- `W1_uniform_random` (depth): movement `rdt_ancestor_dual=0.199` vs best baseline `0.801` (margin `75.1%`).
- `W2_sequential` (depth): movement `rdt_ancestor_stable=0.179` vs best baseline `0.800` (margin `77.6%`).
- `W2_sequential` (depth): movement `rdt_ancestor_dual=0.149` vs best baseline `0.800` (margin `81.3%`).
- `W3_clustered` (depth): movement `rdt_ancestor_stable=0.214` vs best baseline `0.800` (margin `73.3%`).
- `W3_clustered` (depth): movement `rdt_ancestor_dual=0.195` vs best baseline `0.800` (margin `75.7%`).
- `W1_uniform_random` (ancestor): movement `rdt_ancestor_stable=0.199` vs best baseline `0.801` (margin `75.1%`).
- `W1_uniform_random` (ancestor): movement `rdt_ancestor_dual=0.199` vs best baseline `0.801` (margin `75.1%`).
- `W2_sequential` (ancestor): movement `rdt_ancestor_stable=0.179` vs best baseline `0.800` (margin `77.6%`).
- `W2_sequential` (ancestor): movement `rdt_ancestor_dual=0.149` vs best baseline `0.800` (margin `81.3%`).
- `W3_clustered` (ancestor): movement `rdt_ancestor_stable=0.214` vs best baseline `0.800` (margin `73.3%`).
- `W3_clustered` (ancestor): movement `rdt_ancestor_dual=0.195` vs best baseline `0.800` (margin `75.7%`).
RDT bucket-query p95 also wins in:
- `W1_uniform_random` (depth): `rdt_ancestor=1230.420us` vs best baseline `1595.269us`
- `W1_uniform_random` (ancestor): `rdt_ancestor=1.166us` vs best baseline `1.750us`

## Packaging Choice
Selected **Option B: RDTShard** inside this repo, because the benchmarked win case is partition/shard stability, not raw point-lookup speed.

## Reproducibility
```bash
python3 tools/benchmark_rdt_index.py
python3 -m unittest discover -s tests -p 'test_*.py'
```
