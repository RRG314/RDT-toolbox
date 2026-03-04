#!/usr/bin/env python3
"""Benchmark RDT index variants against standard indexing/partitioning baselines."""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rdt_showcase import (  # noqa: E402
    BTreeLikeIndex,
    HashMapIndex,
    RDTIndex,
    SortedArrayIndex,
    rdt_ancestor,
    rdt_depth,
)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    vals = sorted(float(v) for v in values)
    if len(vals) == 1:
        return vals[0]
    idx = (len(vals) - 1) * p
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return vals[lo]
    frac = idx - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def summarize_lat_us(lat_us: Sequence[float]) -> Dict[str, float]:
    if not lat_us:
        return {"count": 0, "mean_us": 0.0, "p50_us": 0.0, "p95_us": 0.0}
    return {
        "count": int(len(lat_us)),
        "mean_us": float(sum(lat_us) / len(lat_us)),
        "p50_us": float(percentile(lat_us, 0.50)),
        "p95_us": float(percentile(lat_us, 0.95)),
    }


def deep_size_bytes(obj: Any) -> int:
    seen: set[int] = set()

    def walk(x: Any) -> int:
        oid = id(x)
        if oid in seen:
            return 0
        seen.add(oid)

        size = sys.getsizeof(x)
        if isinstance(x, dict):
            for k, v in x.items():
                size += walk(k)
                size += walk(v)
            return size
        if isinstance(x, (list, tuple, set, frozenset)):
            for v in x:
                size += walk(v)
            return size
        if hasattr(x, "__dict__"):
            size += walk(vars(x))
            return size
        return size

    return int(walk(obj))


def cv(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean <= 0:
        return 0.0
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return float(math.sqrt(var) / mean)


def unique_positive_keys(candidates: Iterable[int], n: int) -> List[int]:
    out: List[int] = []
    used = set()
    for raw in candidates:
        if len(out) >= n:
            break
        k = int(raw)
        if k < 1:
            k = 1 - k
        while k in used or k < 1:
            k += 1
        used.add(k)
        out.append(k)
    return out


def make_uniform(n: int, rng: random.Random) -> List[int]:
    out = set()
    while len(out) < n:
        out.add(rng.randint(1, (1 << 31) - 1))
    return list(out)


def make_sequential(n: int) -> List[int]:
    start = 20_000_000
    return list(range(start, start + n))


def make_clustered(n: int, rng: random.Random) -> List[int]:
    centers = [200_000, 201_000, 202_000, 5_000_000, 5_000_800, 80_000_000]
    candidates: List[int] = []
    while len(candidates) < n * 2:
        c = centers[rng.randrange(len(centers))]
        noise = int(rng.gauss(0.0, 220.0))
        candidates.append(c + noise)
    return unique_positive_keys(candidates, n)


@dataclass
class SystemSpec:
    name: str
    factory: Callable[[], Any]


def build_system_specs() -> List[SystemSpec]:
    return [
        SystemSpec("rdt_depth", lambda: RDTIndex(bucket_mode="depth", max_bucket_depth=12, shard_depth=8, stable_sharding=False)),
        SystemSpec("rdt_ancestor", lambda: RDTIndex(bucket_mode="ancestor", max_bucket_depth=12, shard_depth=8, stable_sharding=False)),
        SystemSpec("rdt_ancestor_stable", lambda: RDTIndex(bucket_mode="ancestor", max_bucket_depth=12, shard_depth=8, stable_sharding=True)),
        SystemSpec("hash_map", HashMapIndex),
        SystemSpec("sorted_array", SortedArrayIndex),
        SystemSpec("btree_like", lambda: BTreeLikeIndex(block_size=128)),
    ]


def call_query_bucket(index: Any, mode: str, depth_k: int, bucket_id: int) -> List[Tuple[int, Any]]:
    if isinstance(index, RDTIndex):
        return index.query_bucket(depth_k, bucket_id, query_mode=mode)
    return index.query_bucket(mode, depth_k, bucket_id)


def bucket_counts_for_index(index: Any, mode: str, depth_k: int, keys: Sequence[int]) -> Dict[int, int]:
    if isinstance(index, RDTIndex):
        return index.bucket_sizes(depth_k, mode=mode)

    counts: Dict[int, int] = {}
    if mode == "depth":
        for k in keys:
            b = rdt_depth(int(k))
            counts[b] = counts.get(b, 0) + 1
        return counts
    if mode == "ancestor":
        for k in keys:
            b = rdt_ancestor(int(k), int(depth_k))
            counts[b] = counts.get(b, 0) + 1
        return counts
    raise ValueError(f"unknown mode: {mode}")


def shard_of(index: Any, key: int, shard_count: int) -> int:
    if isinstance(index, RDTIndex):
        return index.shard_of_key(int(key), shard_count)
    return int(key) % int(shard_count)


def shard_movement_rate(index: Any, keys: Sequence[int], s_from: int, s_to: int) -> float:
    if not keys:
        return 0.0
    moved = 0
    for k in keys:
        moved += int(shard_of(index, k, s_from) != shard_of(index, k, s_to))
    return moved / len(keys)


def shard_load_cv(index: Any, keys: Sequence[int], shards: int) -> float:
    loads = [0 for _ in range(shards)]
    for k in keys:
        loads[shard_of(index, k, shards)] += 1
    return cv(loads)


def benchmark_static_workload(
    workload_name: str,
    keys: Sequence[int],
    specs: Sequence[SystemSpec],
    mode: str,
    query_depth: int,
    rng: random.Random,
    lookup_samples: int,
    bucket_samples: int,
) -> Dict[str, Any]:
    items = [(int(k), int(k) * 3 + 7) for k in keys]
    key_set = set(keys)

    lookup_existing = [keys[rng.randrange(len(keys))] for _ in range(lookup_samples)]
    lookup_missing = []
    while len(lookup_missing) < max(64, lookup_samples // 10):
        x = rng.randint(1, (1 << 31) - 1)
        if x not in key_set:
            lookup_missing.append(x)
    lookup_trace = lookup_existing + lookup_missing
    rng.shuffle(lookup_trace)

    if mode == "depth":
        bucket_trace = [rdt_depth(keys[rng.randrange(len(keys))]) for _ in range(bucket_samples)]
        bucket_args = [(d, 0) for d in bucket_trace]
    elif mode == "ancestor":
        bucket_ids = [rdt_ancestor(keys[rng.randrange(len(keys))], query_depth) for _ in range(bucket_samples)]
        bucket_args = [(query_depth, bid) for bid in bucket_ids]
    else:
        raise ValueError(f"unknown mode: {mode}")

    systems_out: Dict[str, Any] = {}

    for spec in specs:
        idx = spec.factory()

        t0 = time.perf_counter()
        idx.build(items)
        build_ms = (time.perf_counter() - t0) * 1000.0

        mem_bytes = deep_size_bytes(idx)

        lookup_lat = []
        hit_count = 0
        for k in lookup_trace:
            q0 = time.perf_counter_ns()
            v = idx.get(k)
            q1 = time.perf_counter_ns()
            lookup_lat.append((q1 - q0) / 1000.0)
            hit_count += int(v is not None)

        bucket_lat = []
        bucket_sizes = []
        for d, bid in bucket_args:
            q0 = time.perf_counter_ns()
            rows = call_query_bucket(idx, mode, d, bid)
            q1 = time.perf_counter_ns()
            bucket_lat.append((q1 - q0) / 1000.0)
            bucket_sizes.append(len(rows))

        counts = bucket_counts_for_index(idx, mode, query_depth, keys)
        part_sizes = list(counts.values())

        move_rate = shard_movement_rate(idx, keys, 16, 20)
        shard_cv_16 = shard_load_cv(idx, keys, 16)
        shard_cv_20 = shard_load_cv(idx, keys, 20)

        systems_out[spec.name] = {
            "build_ms": build_ms,
            "memory_bytes": mem_bytes,
            "lookup": {
                **summarize_lat_us(lookup_lat),
                "hit_rate": hit_count / max(1, len(lookup_trace)),
            },
            "bucket_query": {
                **summarize_lat_us(bucket_lat),
                "result_size_mean": float(sum(bucket_sizes) / max(1, len(bucket_sizes))),
                "result_size_p95": float(percentile(bucket_sizes, 0.95)),
            },
            "partition": {
                "num_buckets": len(part_sizes),
                "bucket_size_mean": float(sum(part_sizes) / max(1, len(part_sizes))),
                "bucket_size_cv": float(cv(part_sizes)),
                "worst_bucket_size": int(max(part_sizes) if part_sizes else 0),
            },
            "sharding": {
                "movement_16_to_20": move_rate,
                "load_cv_16": shard_cv_16,
                "load_cv_20": shard_cv_20,
            },
        }

    return {
        "workload": workload_name,
        "mode": mode,
        "query_depth": int(query_depth),
        "n_keys": len(keys),
        "systems": systems_out,
    }


def benchmark_mixed_rw(
    keys_init: Sequence[int],
    specs: Sequence[SystemSpec],
    mixes: Sequence[float],
    operations: int,
    rng: random.Random,
) -> Dict[str, Any]:
    base_items = [(int(k), int(k) * 5 + 11) for k in keys_init]
    centers = [300_000, 1_700_000, 8_500_000]

    out: Dict[str, Any] = {}

    for read_ratio in mixes:
        read_pct = int(round(read_ratio * 100))
        write_pct = 100 - read_pct
        ratio_name = f"read_{read_pct}_write_{write_pct}"
        out_ratio: Dict[str, Any] = {}

        for spec in specs:
            idx = spec.factory()
            idx.build(base_items)

            keys = set(keys_init)
            key_list = list(keys)
            next_seq = max(keys_init) + 1

            read_lat: List[float] = []
            write_lat: List[float] = []

            t0_all = time.perf_counter()
            for _ in range(operations):
                do_read = (rng.random() < read_ratio) and bool(key_list)
                if do_read:
                    key = key_list[rng.randrange(len(key_list))]
                    t0 = time.perf_counter_ns()
                    idx.get(key)
                    t1 = time.perf_counter_ns()
                    read_lat.append((t1 - t0) / 1000.0)
                else:
                    c = centers[rng.randrange(len(centers))]
                    cand = int(c + rng.gauss(0.0, 250.0))
                    if cand < 1:
                        cand = next_seq
                    while cand in keys or cand < 1:
                        cand += 1
                    keys.add(cand)
                    key_list.append(cand)
                    t0 = time.perf_counter_ns()
                    idx.insert(cand, cand * 5 + 11)
                    t1 = time.perf_counter_ns()
                    write_lat.append((t1 - t0) / 1000.0)
            t1_all = time.perf_counter()

            out_ratio[spec.name] = {
                "ops": int(operations),
                "read_ops": int(len(read_lat)),
                "write_ops": int(len(write_lat)),
                "throughput_ops_s": float(operations / max(1e-9, (t1_all - t0_all))),
                "read_latency": summarize_lat_us(read_lat),
                "write_latency": summarize_lat_us(write_lat),
                "final_size": int(len(keys)),
            }

        out[ratio_name] = out_ratio

    return out


def detect_findings(results: Dict[str, Any]) -> Dict[str, Any]:
    static = results["static_workloads"]

    failures: List[Dict[str, Any]] = []
    wins: List[Dict[str, Any]] = []

    for row in static:
        wl = row["workload"]
        mode = row["mode"]
        sysm = row["systems"]

        rdt_depth_lookup = sysm["rdt_depth"]["lookup"]["p95_us"]
        baseline_lookup_best = min(
            sysm[name]["lookup"]["p95_us"] for name in ("hash_map", "sorted_array", "btree_like")
        )
        if rdt_depth_lookup > baseline_lookup_best:
            failures.append(
                {
                    "workload": wl,
                    "mode": mode,
                    "issue": "RDT depth-mode lookup p95 slower than best baseline",
                    "rdt_depth_p95_us": rdt_depth_lookup,
                    "best_baseline_p95_us": baseline_lookup_best,
                }
            )

        move_rdt_stable = sysm["rdt_ancestor_stable"]["sharding"]["movement_16_to_20"]
        move_baseline_best = min(
            sysm[name]["sharding"]["movement_16_to_20"] for name in ("hash_map", "sorted_array", "btree_like")
        )
        if move_rdt_stable <= 0.8 * move_baseline_best:
            wins.append(
                {
                    "workload": wl,
                    "mode": mode,
                    "metric": "shard movement 16->20",
                    "rdt_ancestor_stable": move_rdt_stable,
                    "best_baseline": move_baseline_best,
                    "margin_fraction": (move_baseline_best - move_rdt_stable) / max(1e-9, move_baseline_best),
                }
            )

    bucket_win_candidates = []
    for row in static:
        wl = row["workload"]
        mode = row["mode"]
        sysm = row["systems"]

        rdt = sysm["rdt_ancestor"]["bucket_query"]["p95_us"]
        best_base = min(sysm[n]["bucket_query"]["p95_us"] for n in ("hash_map", "sorted_array", "btree_like"))
        if rdt <= 0.8 * best_base:
            bucket_win_candidates.append(
                {
                    "workload": wl,
                    "mode": mode,
                    "metric": "bucket/range query p95",
                    "rdt_ancestor": rdt,
                    "best_baseline": best_base,
                    "margin_fraction": (best_base - rdt) / max(1e-9, best_base),
                }
            )

    modification = {
        "problem": "Depth-only RDT partitions are coarse and suffer from poor shard-resize stability under modulo mapping.",
        "smallest_rdt_based_fix": "Use ancestor bucket IDs (ancestor(key, k)) and stable shard mapping (jump-consistent-hash on bucket ID).",
        "rerun_included": True,
        "effect_summary": {
            "movement_metric_checked": "movement_16_to_20",
            "rdt_depth_vs_rdt_ancestor_stable_improved_in_all_static_rows": all(
                row["systems"]["rdt_ancestor_stable"]["sharding"]["movement_16_to_20"]
                < row["systems"]["rdt_depth"]["sharding"]["movement_16_to_20"]
                for row in static
            )
        },
    }

    return {
        "clear_wins": wins,
        "bucket_query_wins": bucket_win_candidates,
        "adversarial_failures": failures,
        "modification": modification,
    }


def render_markdown(results: Dict[str, Any]) -> str:
    findings = results["findings"]

    lines: List[str] = []
    lines.append("# RDT Index Benchmark")
    lines.append("")
    lines.append(f"- Generated (UTC): `{results['generated_at_utc']}`")
    lines.append(f"- Seed: `{results['seed']}`")
    lines.append(f"- Static workload size: `{results['config']['n_static']}`")
    lines.append(f"- Mixed R/W initial size: `{results['config']['n_mixed_init']}`")
    lines.append("")

    lines.append("## Systems")
    lines.append("- `rdt_depth`: RDT keyed by depth D(key), modulo shard mapping")
    lines.append("- `rdt_ancestor`: RDT keyed by ancestor bucket at fixed depth, modulo shard mapping")
    lines.append("- `rdt_ancestor_stable`: same ancestor buckets with jump-consistent shard mapping")
    lines.append("- `hash_map`, `sorted_array`, `btree_like`: required baselines")
    lines.append("")

    lines.append("## Static Workloads (W1/W2/W3)")
    for row in results["static_workloads"]:
        lines.append(f"### {row['workload']} (mode={row['mode']}, n={row['n_keys']})")
        lines.append("| system | build_ms | mem_mb | lookup_p95_us | bucket_p95_us | bucket_cv | worst_bucket | move_16_to_20 |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for name, m in row["systems"].items():
            lines.append(
                f"| {name} | {m['build_ms']:.2f} | {m['memory_bytes']/1024/1024:.2f} | "
                f"{m['lookup']['p95_us']:.3f} | {m['bucket_query']['p95_us']:.3f} | "
                f"{m['partition']['bucket_size_cv']:.3f} | {m['partition']['worst_bucket_size']} | "
                f"{m['sharding']['movement_16_to_20']:.3f} |"
            )
        lines.append("")

    lines.append("## W4 Mixed Read/Write")
    for ratio_name, ratio_data in results["mixed_workload"].items():
        lines.append(f"### {ratio_name}")
        lines.append("| system | throughput ops/s | read_p95_us | write_p95_us | final_size |")
        lines.append("|---|---:|---:|---:|---:|")
        for name, m in ratio_data.items():
            lines.append(
                f"| {name} | {m['throughput_ops_s']:.1f} | {m['read_latency']['p95_us']:.3f} | "
                f"{m['write_latency']['p95_us']:.3f} | {m['final_size']} |"
            )
        lines.append("")

    lines.append("## Adversarial Findings (Where RDT Loses)")
    if findings["adversarial_failures"]:
        for f in findings["adversarial_failures"]:
            lines.append(
                f"- `{f['workload']}` ({f['mode']}): {f['issue']} "
                f"(`rdt_depth={f['rdt_depth_p95_us']:.3f}us`, best baseline `{f['best_baseline_p95_us']:.3f}us`)."
            )
    else:
        lines.append("- No adversarial failures detected in the configured runs.")
    lines.append("")

    lines.append("## Smallest RDT-Based Fix and Rerun")
    mod = findings["modification"]
    lines.append(f"- Problem: {mod['problem']}")
    lines.append(f"- Fix: {mod['smallest_rdt_based_fix']}")
    lines.append(f"- Rerun included: `{mod['rerun_included']}`")
    lines.append(
        "- Improvement check (movement metric): "
        f"`{mod['effect_summary']['rdt_depth_vs_rdt_ancestor_stable_improved_in_all_static_rows']}`"
    )
    lines.append("")

    lines.append("## Win Case Decision")
    if findings["clear_wins"]:
        lines.append("RDT has a clear measurable win on sharding-resize stability:")
        for w in findings["clear_wins"]:
            lines.append(
                f"- `{w['workload']}` ({w['mode']}): movement `rdt_ancestor_stable={w['rdt_ancestor_stable']:.3f}` vs "
                f"best baseline `{w['best_baseline']:.3f}` (margin `{100*w['margin_fraction']:.1f}%`)."
            )
    else:
        lines.append("No clear superiority detected under the configured criteria.")

    if findings["bucket_query_wins"]:
        lines.append("RDT bucket-query p95 also wins in:")
        for w in findings["bucket_query_wins"]:
            lines.append(
                f"- `{w['workload']}` ({w['mode']}): `rdt_ancestor={w['rdt_ancestor']:.3f}us` vs best baseline `{w['best_baseline']:.3f}us`"
            )
    lines.append("")

    lines.append("## Packaging Choice")
    lines.append(
        "Selected **Option B: RDTShard** inside this repo, because the benchmarked win case is partition/shard stability, "
        "not raw point-lookup speed."
    )
    lines.append("")

    lines.append("## Reproducibility")
    lines.append("```bash")
    lines.append("python3 tools/benchmark_rdt_index.py")
    lines.append("python3 -m unittest discover -s tests -p 'test_*.py'")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--n-static", type=int, default=30000)
    parser.add_argument("--n-mixed-init", type=int, default=15000)
    parser.add_argument("--lookup-samples", type=int, default=2500)
    parser.add_argument("--bucket-samples", type=int, default=800)
    parser.add_argument("--query-depth", type=int, default=10)
    parser.add_argument("--mixed-ops", type=int, default=6000)
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "rdt_index_benchmark.json")
    parser.add_argument("--report", type=Path, default=ROOT / "docs" / "rdt_index_benchmark.md")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    specs = build_system_specs()

    w1 = make_uniform(args.n_static, rng)
    w2 = make_sequential(args.n_static)
    w3 = make_clustered(args.n_static, rng)

    static_rows = []
    for mode in ("depth", "ancestor"):
        for name, keys in (("W1_uniform_random", w1), ("W2_sequential", w2), ("W3_clustered", w3)):
            row = benchmark_static_workload(
                workload_name=name,
                keys=keys,
                specs=specs,
                mode=mode,
                query_depth=args.query_depth,
                rng=rng,
                lookup_samples=args.lookup_samples,
                bucket_samples=args.bucket_samples,
            )
            static_rows.append(row)

    w4_init = make_clustered(args.n_mixed_init, rng)
    mixed = benchmark_mixed_rw(
        keys_init=w4_init,
        specs=specs,
        mixes=(0.80, 0.95),
        operations=args.mixed_ops,
        rng=rng,
    )

    results: Dict[str, Any] = {
        "generated_at_utc": now_utc_iso(),
        "seed": args.seed,
        "config": {
            "n_static": args.n_static,
            "n_mixed_init": args.n_mixed_init,
            "lookup_samples": args.lookup_samples,
            "bucket_samples": args.bucket_samples,
            "query_depth": args.query_depth,
            "mixed_ops": args.mixed_ops,
        },
        "systems": [s.name for s in specs],
        "static_workloads": static_rows,
        "mixed_workload": mixed,
    }

    results["findings"] = detect_findings(results)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    args.report.write_text(render_markdown(results), encoding="utf-8")

    print(f"Wrote JSON: {args.out}")
    print(f"Wrote report: {args.report}")


if __name__ == "__main__":
    main()
