# RDT Index Benchmark

- Generated (UTC): `2026-03-04T03:45:11.348299+00:00`
- Seed: `1729`
- Static workload size: `30000`
- Mixed R/W initial size: `15000`

## Systems
- `rdt_depth`: RDT keyed by depth D(key), modulo shard mapping
- `rdt_ancestor`: RDT keyed by ancestor bucket at fixed depth, modulo shard mapping
- `rdt_ancestor_stable`: same ancestor buckets with jump-consistent shard mapping
- `hash_map`, `sorted_array`, `btree_like`: required baselines

## Static Workloads (W1/W2/W3)
### W1_uniform_random (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 201.98 | 110.14 | 0.458 | 1231.252 | 1.922 | 15093 | 1.000 |
| rdt_ancestor | 214.15 | 110.14 | 0.458 | 1177.721 | 1.922 | 15093 | 0.801 |
| rdt_ancestor_stable | 282.05 | 110.14 | 0.458 | 1192.126 | 1.922 | 15093 | 0.199 |
| hash_map | 1.92 | 3.01 | 0.417 | 3101.854 | 1.922 | 15093 | 0.801 |
| sorted_array | 13.96 | 2.23 | 0.666 | 2367.210 | 1.922 | 15093 | 0.801 |
| btree_like | 12.10 | 3.83 | 4.167 | 1379.447 | 1.922 | 15093 | 0.801 |

### W2_sequential (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 111.85 | 34.14 | 0.416 | 2044.821 | 0.000 | 30000 | 1.000 |
| rdt_ancestor | 117.25 | 34.14 | 0.417 | 1823.648 | 0.000 | 30000 | 0.845 |
| rdt_ancestor_stable | 101.79 | 34.14 | 0.458 | 1803.947 | 0.000 | 30000 | 0.179 |
| hash_map | 1.22 | 2.85 | 0.375 | 3024.852 | 0.000 | 30000 | 0.800 |
| sorted_array | 3.27 | 2.07 | 0.708 | 2919.485 | 0.000 | 30000 | 0.800 |
| btree_like | 2.24 | 3.68 | 3.542 | 1924.663 | 0.000 | 30000 | 0.800 |

### W3_clustered (mode=depth, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 113.79 | 34.25 | 0.375 | 842.407 | 0.408 | 14925 | 1.000 |
| rdt_ancestor | 119.35 | 34.25 | 0.416 | 850.244 | 0.408 | 14925 | 0.805 |
| rdt_ancestor_stable | 104.52 | 34.25 | 0.416 | 862.008 | 0.408 | 14925 | 0.214 |
| hash_map | 1.49 | 2.85 | 0.334 | 2969.187 | 0.408 | 14925 | 0.800 |
| sorted_array | 6.80 | 2.07 | 0.708 | 1940.356 | 0.408 | 14925 | 0.800 |
| btree_like | 5.32 | 3.68 | 3.708 | 911.824 | 0.408 | 14925 | 0.800 |

### W1_uniform_random (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 194.76 | 110.14 | 0.625 | 1.458 | 0.086 | 4 | 1.000 |
| rdt_ancestor | 292.14 | 110.14 | 0.458 | 1.167 | 0.086 | 4 | 0.801 |
| rdt_ancestor_stable | 265.10 | 110.14 | 0.458 | 1.125 | 0.086 | 4 | 0.199 |
| hash_map | 2.91 | 3.01 | 0.416 | 3923.007 | 0.086 | 4 | 0.801 |
| sorted_array | 13.67 | 2.23 | 0.875 | 1.500 | 0.086 | 4 | 0.801 |
| btree_like | 12.93 | 3.83 | 5.375 | 3.833 | 0.086 | 4 | 0.801 |

### W2_sequential (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 104.97 | 34.14 | 0.417 | 54.585 | 0.094 | 1024 | 1.000 |
| rdt_ancestor | 102.32 | 34.14 | 0.416 | 52.549 | 0.094 | 1024 | 0.845 |
| rdt_ancestor_stable | 101.81 | 34.14 | 0.416 | 54.544 | 0.094 | 1024 | 0.179 |
| hash_map | 1.68 | 2.85 | 0.375 | 3444.102 | 0.094 | 1024 | 0.800 |
| sorted_array | 3.42 | 2.07 | 0.625 | 31.835 | 0.094 | 1024 | 0.800 |
| btree_like | 2.38 | 3.68 | 3.750 | 57.379 | 0.094 | 1024 | 0.800 |

### W3_clustered (mode=ancestor, n=30000)
| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rdt_depth | 105.49 | 34.25 | 0.416 | 53.927 | 0.283 | 1024 | 1.000 |
| rdt_ancestor | 105.08 | 34.25 | 0.416 | 54.844 | 0.283 | 1024 | 0.805 |
| rdt_ancestor_stable | 179.17 | 34.25 | 0.416 | 55.629 | 0.283 | 1024 | 0.214 |
| hash_map | 1.57 | 2.85 | 0.416 | 3597.156 | 0.283 | 1024 | 0.800 |
| sorted_array | 6.44 | 2.07 | 0.584 | 35.375 | 0.283 | 1024 | 0.800 |
| btree_like | 5.26 | 3.68 | 3.959 | 60.918 | 0.283 | 1024 | 0.800 |

## W4 Mixed Read/Write
### read_80_write_20
| system | throughput ops/s | read_p95_us | write_p95_us | final_size |
|---|---:|---:|---:|---:|
| rdt_depth | 689008.5 | 0.375 | 4.708 | 16261 |
| rdt_ancestor | 711550.4 | 0.375 | 4.750 | 16164 |
| rdt_ancestor_stable | 709807.2 | 0.375 | 4.709 | 16218 |
| hash_map | 1672726.6 | 0.208 | 0.209 | 16190 |
| sorted_array | 434133.8 | 0.500 | 10.375 | 16225 |
| btree_like | 204840.5 | 3.791 | 10.292 | 16218 |

### read_95_write_5
| system | throughput ops/s | read_p95_us | write_p95_us | final_size |
|---|---:|---:|---:|---:|
| rdt_depth | 1410713.8 | 0.292 | 4.666 | 15296 |
| rdt_ancestor | 1368457.1 | 0.292 | 4.625 | 15313 |
| rdt_ancestor_stable | 1384176.3 | 0.291 | 4.750 | 15314 |
| hash_map | 1766611.2 | 0.291 | 0.285 | 15284 |
| sorted_array | 938630.5 | 0.417 | 9.658 | 15285 |
| btree_like | 262646.2 | 3.375 | 10.042 | 15323 |

## Adversarial Findings (Where RDT Loses)
- `W1_uniform_random` (depth): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.458us`, best baseline `0.417us`).
- `W2_sequential` (depth): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.416us`, best baseline `0.375us`).
- `W3_clustered` (depth): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.375us`, best baseline `0.334us`).
- `W1_uniform_random` (ancestor): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.625us`, best baseline `0.416us`).
- `W2_sequential` (ancestor): RDT depth-mode lookup p95 slower than best baseline (`rdt_depth=0.417us`, best baseline `0.375us`).

## Smallest RDT-Based Fix and Rerun
- Problem: Depth-only RDT partitions are coarse and suffer from poor shard-resize stability under modulo mapping.
- Fix: Use ancestor bucket IDs (ancestor(key, k)) and stable shard mapping (jump-consistent-hash on bucket ID).
- Rerun included: `True`
- Improvement check (movement metric): `True`

## Win Case Decision
RDT has a clear measurable win on sharding-resize stability:
- `W1_uniform_random` (depth): movement `rdt_ancestor_stable=0.199` vs best baseline `0.801` (margin `75.1%`).
- `W2_sequential` (depth): movement `rdt_ancestor_stable=0.179` vs best baseline `0.800` (margin `77.6%`).
- `W3_clustered` (depth): movement `rdt_ancestor_stable=0.214` vs best baseline `0.800` (margin `73.3%`).
- `W1_uniform_random` (ancestor): movement `rdt_ancestor_stable=0.199` vs best baseline `0.801` (margin `75.1%`).
- `W2_sequential` (ancestor): movement `rdt_ancestor_stable=0.179` vs best baseline `0.800` (margin `77.6%`).
- `W3_clustered` (ancestor): movement `rdt_ancestor_stable=0.214` vs best baseline `0.800` (margin `73.3%`).
RDT bucket-query p95 also wins in:
- `W1_uniform_random` (ancestor): `rdt_ancestor=1.167us` vs best baseline `1.500us`

## Packaging Choice
Selected **Option B: RDTShard** inside this repo, because the benchmarked win case is partition/shard stability, not raw point-lookup speed.

## Reproducibility
```bash
python3 tools/benchmark_rdt_index.py
python3 -m unittest discover -s tests -p 'test_*.py'
```
