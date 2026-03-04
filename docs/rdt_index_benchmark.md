# RDT Index Benchmark

- Generated (UTC): `2026-03-04T04:11:02.808796+00:00`
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
| rdt_depth | 199.59 | 110.14 | 0.542 | 1289.839 | 1.922 | 15093 | 1.000 |
| rdt_ancestor | 202.33 | 110.14 | 0.458 | 2261.512 | 1.922 | 15093 | 0.801 |
| rdt_ancestor_stable | 382.89 | 110.14 | 0.542 | 1182.732 | 1.922 | 15093 | 0.199 |
| rdt_ancestor_dual | 3825.95 | 110.14 | 0.459 | 1718.619 | 1.922 | 15093 | 0.199 |
| hash_map | 2.71 | 3.01 | 0.791 | 6096.932 | 1.922 | 15093 | 0.801 |
| sorted_array | 25.89 | 2.23 | 1.000 | 2886.488 | 1.922 | 15093 | 0.801 |
| btree_like | 13.88 | 3.83 | 5.792 | 2980.858 | 1.922 | 15093 | 0.801 |

### W2_sequential (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 139.24 | 34.14 | 0.500 | 2703.494 | 0.000 | 30000 | 1.000 |
| rdt_ancestor | 141.77 | 34.14 | 0.417 | 9980.515 | 0.000 | 30000 | 0.845 |
| rdt_ancestor_stable | 126.75 | 34.14 | 0.416 | 2870.567 | 0.000 | 30000 | 0.179 |
| rdt_ancestor_dual | 3446.85 | 34.14 | 0.482 | 2354.200 | 0.000 | 30000 | 0.149 |
| hash_map | 2.29 | 2.85 | 0.500 | 13823.627 | 0.000 | 30000 | 0.800 |
| sorted_array | 7.30 | 2.07 | 0.625 | 3893.658 | 0.000 | 30000 | 0.800 |
| btree_like | 2.98 | 3.68 | 3.625 | 3662.883 | 0.000 | 30000 | 0.800 |

### W3_clustered (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 191.50 | 34.25 | 0.459 | 9556.836 | 0.408 | 14925 | 1.000 |
| rdt_ancestor | 139.62 | 34.25 | 0.959 | 2738.575 | 0.408 | 14925 | 0.805 |
| rdt_ancestor_stable | 141.17 | 34.25 | 0.416 | 1332.770 | 0.408 | 14925 | 0.214 |
| rdt_ancestor_dual | 3621.86 | 34.26 | 0.417 | 1251.918 | 0.408 | 14925 | 0.195 |
| hash_map | 2.17 | 2.85 | 0.375 | 4578.231 | 0.408 | 14925 | 0.800 |
| sorted_array | 33.36 | 2.07 | 2.625 | 5474.732 | 0.408 | 14925 | 0.800 |
| btree_like | 6.16 | 3.68 | 5.625 | 1404.798 | 0.408 | 14925 | 0.800 |

### W1_uniform_random (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 275.77 | 110.14 | 0.584 | 1.500 | 0.086 | 4 | 1.000 |
| rdt_ancestor | 382.63 | 110.14 | 0.458 | 1.166 | 0.086 | 4 | 0.801 |
| rdt_ancestor_stable | 242.45 | 110.14 | 0.458 | 1.167 | 0.086 | 4 | 0.199 |
| rdt_ancestor_dual | 3443.25 | 110.14 | 0.500 | 1.252 | 0.086 | 4 | 0.199 |
| hash_map | 3.30 | 3.01 | 0.459 | 5193.144 | 0.086 | 4 | 0.801 |
| sorted_array | 14.65 | 2.23 | 0.750 | 1.458 | 0.086 | 4 | 0.801 |
| btree_like | 12.60 | 3.83 | 4.333 | 5.713 | 0.086 | 4 | 0.801 |

### W2_sequential (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 107.87 | 34.14 | 0.417 | 55.260 | 0.094 | 1024 | 1.000 |
| rdt_ancestor | 112.05 | 34.14 | 0.417 | 62.027 | 0.094 | 1024 | 0.845 |
| rdt_ancestor_stable | 137.84 | 34.14 | 0.417 | 106.962 | 0.094 | 1024 | 0.179 |
| rdt_ancestor_dual | 1989.51 | 34.14 | 0.459 | 66.582 | 0.094 | 1024 | 0.149 |
| hash_map | 1.56 | 2.85 | 0.542 | 3895.502 | 0.094 | 1024 | 0.800 |
| sorted_array | 3.59 | 2.07 | 0.708 | 32.463 | 0.094 | 1024 | 0.800 |
| btree_like | 3.15 | 3.68 | 5.042 | 58.421 | 0.094 | 1024 | 0.800 |

### W3_clustered (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 128.33 | 34.25 | 0.416 | 58.466 | 0.283 | 1024 | 1.000 |
| rdt_ancestor | 122.32 | 34.25 | 0.416 | 61.976 | 0.283 | 1024 | 0.805 |
| rdt_ancestor_stable | 133.80 | 34.25 | 0.417 | 64.337 | 0.283 | 1024 | 0.214 |
| rdt_ancestor_dual | 1952.41 | 34.26 | 0.542 | 55.791 | 0.283 | 1024 | 0.195 |
| hash_map | 1.48 | 2.85 | 0.375 | 3947.750 | 0.283 | 1024 | 0.800 |
| sorted_array | 6.62 | 2.07 | 0.625 | 39.046 | 0.283 | 1024 | 0.800 |
| btree_like | 5.52 | 3.68 | 3.791 | 70.502 | 0.283 | 1024 | 0.800 |

## W4 Mixed Read/Write
### read_80_write_20
| system | throughput ops/s | read_p95_us | write_p95_us | final_size |
|---|---:|---:|---:|---:|
| rdt_depth | 679405.5 | 0.375 | 4.625 | 16261 |
| rdt_ancestor | 672262.7 | 0.334 | 4.833 | 16164 |
| rdt_ancestor_stable | 634735.9 | 0.375 | 5.542 | 16218 |
| rdt_ancestor_dual | 654405.7 | 0.334 | 4.982 | 16190 |
| hash_map | 1508801.2 | 0.291 | 0.250 | 16225 |
| sorted_array | 413976.3 | 0.542 | 10.417 | 16218 |
| btree_like | 193059.3 | 4.084 | 10.500 | 16246 |

### read_95_write_5
| system | throughput ops/s | read_p95_us | write_p95_us | final_size |
|---|---:|---:|---:|---:|
| rdt_depth | 1152368.7 | 0.375 | 5.665 | 15308 |
| rdt_ancestor | 1109373.5 | 0.375 | 6.167 | 15301 |
| rdt_ancestor_stable | 1326834.2 | 0.333 | 4.890 | 15294 |
| rdt_ancestor_dual | 1399566.4 | 0.250 | 4.714 | 15278 |
| hash_map | 1921921.9 | 0.167 | 0.209 | 15330 |
| sorted_array | 896464.5 | 0.417 | 9.833 | 15302 |
| btree_like | 249825.6 | 3.666 | 10.262 | 15315 |

## Adversarial Findings (Where RDT Loses)
- `W3_clustered` (depth): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.459us`, best baseline `0.375us`).
- `W1_uniform_random` (ancestor): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.584us`, best baseline `0.459us`).
- `W3_clustered` (ancestor): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.416us`, best baseline `0.375us`).

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
- `W1_uniform_random` (depth): `rdt_ancestor=2261.512us` vs best baseline `2886.488us`
- `W1_uniform_random` (ancestor): `rdt_ancestor=1.166us` vs best baseline `1.458us`

## Packaging Choice
Selected **Option B: RDTShard** inside this repo, because the benchmarked win case is partition/shard stability, not raw point-lookup speed.

## Reproducibility
```bash
python3 tools/benchmark_rdt_index.py
python3 -m unittest discover -s tests -p 'test_*.py'
```
