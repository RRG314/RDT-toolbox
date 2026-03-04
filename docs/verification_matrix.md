# Verification Matrix

This matrix maps major claims to evidence and status.

## Status Labels
- `Proven`: concise proof included in repo docs.
- `Verified`: computational benchmark/test evidence in repo artifacts.
- `Conjecture`: explicitly not proven.

| Area | Claim | Status | Evidence |
|---|---|---|---|
| RDT core math | `D(n)=floor(log2 n)` for `n>=1` under `f(n)=floor(n/2)` | Proven | [rdt_math_cs_spec.md](./rdt_math_cs_spec.md) |
| RDT ancestry | `A_k(n)=max(1,floor(n/2^k))` | Proven | [rdt_math_cs_spec.md](./rdt_math_cs_spec.md) |
| Tree ultrametric | LCA metric is ultrametric | Proven (short argument) | [rdt_math_cs_spec.md](./rdt_math_cs_spec.md) |
| RDTIndex API | insert/get/query_bucket behavior | Verified | [test_rdt_index.py](../tests/test_rdt_index.py) |
| Dual-number engine | forward-mode derivatives for arithmetic/exp | Verified | [test_dual_tools.py](../tests/test_dual_tools.py) |
| Dual-tuned shard depth | dual-guided tuner returns valid depth and integrates with index | Verified | [test_dual_tools.py](../tests/test_dual_tools.py) |
| Index benchmark win case | RDT stable ancestor mapping reduces shard movement vs baselines | Verified | [rdt_index_benchmark.json](../results/rdt_index_benchmark.json), [rdt_index_benchmark.md](./rdt_index_benchmark.md) |
| Noise variant | hybrid RDT-noise improves speed vs standard RDT-noise | Verified | external report in `../rdt-noise/results/noise_benchmark_report.md`; consolidated in [rdt_showcase_report.md](./rdt_showcase_report.md) |
| Spatial index variant | tuned RDT improves query latency vs untuned RDT with exactness retained | Verified | external report in `../rdt-spatial-index/results/benchmark_report.md`; consolidated in [rdt_showcase_report.md](./rdt_showcase_report.md) |
| RDT256 variant | v3 quality proxy better than v2 but not faster | Verified | external report in `../rdt256/results/stream_benchmark_report.md`; consolidated in [rdt_showcase_report.md](./rdt_showcase_report.md) |

## Explicit Non-Claims
- No cryptographic security claim is made for RDT PRNG streams.
- No universal runtime superiority claim is made for RDT indexes.
- Dual-number variants are kept only when benchmarked improvements are visible.
