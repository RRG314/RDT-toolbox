#!/usr/bin/env python3
"""Run all corrected RDT project benchmarks and write one consolidated report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Any


SHOWCASE_ROOT = Path(__file__).resolve().parents[1]
REPOS_ROOT = SHOWCASE_ROOT.parent

REPOS = {
    "rdt-noise": REPOS_ROOT / "rdt-noise",
    "rdt-spatial-index": REPOS_ROOT / "rdt-spatial-index",
    "rdt256": REPOS_ROOT / "rdt256",
}


def run_cmd(cmd: list[str], cwd: Path) -> None:
    print(f"[{cwd.name}] $ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def git_head(repo: Path) -> dict[str, str]:
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    return {"branch": branch, "commit": commit}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary(
    noise: dict[str, Any],
    spatial: dict[str, Any],
    rdt256: dict[str, Any],
    index_bench: dict[str, Any],
    refs: dict[str, Any],
) -> dict[str, Any]:
    nfind = noise["findings"]
    ssets = spatial["datasets"]
    rfind = rdt256["findings"]
    i_find = index_bench.get("findings", {})
    clear_wins = i_find.get("clear_wins", [])
    best_margin = max((w.get("margin_fraction", 0.0) for w in clear_wins), default=0.0)

    spatial_rows = {}
    for name, ds in ssets.items():
        rdt = ds["systems"]["rdt"]
        opt = ds["systems"]["rdt_optimized"]
        grid = ds["systems"]["uniform_grid"]
        kd = ds["systems"]["kd_tree"]
        spatial_rows[name] = {
            "rdt_query_ms": rdt["query_ms"],
            "rdt_opt_query_ms": opt["query_ms"],
            "uniform_grid_query_ms": grid["query_ms"],
            "kd_query_ms": kd["query_ms"],
            "rdt_to_opt_speedup": rdt["query_ms"] / max(1e-9, opt["query_ms"]),
            "opt_exact_match": opt["errors"]["exact_match_rate"],
        }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_refs": refs,
        "noise": {
            "hybrid_speedup_vs_rdt": nfind["hybrid_speedup_vs_rdt"],
            "rdt_vs_white_speed_ratio": nfind["rdt_vs_white_speed_ratio"],
            "hybrid_entropy_delta_vs_rdt": nfind["hybrid_entropy_delta_vs_rdt"],
            "hybrid_acf_abs_delta_vs_rdt": nfind["hybrid_acf_abs_delta_vs_rdt"],
            "verdict": (
                "Hybrid improves RDT runtime substantially while preserving similar noise statistics; "
                "RDT variants remain far slower than simple white-noise baselines."
            ),
        },
        "spatial_index": {
            "datasets": spatial_rows,
            "verdict": (
                "Tuned RDT preserves exactness and strongly improves over untuned RDT, "
                "but uniform grid is still fastest on these benchmark sets."
            ),
        },
        "rdt256": {
            "v3_speedup_vs_v2": rfind["v3_speedup_vs_v2"],
            "quality_proxy_delta_v3_vs_v2": rfind["quality_proxy_delta_v3_vs_v2"],
            "v2_speed_ratio_vs_splitmix": rfind["v2_speed_ratio_vs_splitmix"],
            "verdict": (
                "v3 shows a small quality-proxy improvement over v2 but no throughput win; "
                "both RDT streams are much slower than SplitMix64."
            ),
        },
        "rdt_toolbox_index": {
            "clear_win_count": int(len(clear_wins)),
            "best_win_margin_pct": float(100.0 * best_margin),
            "packaging_choice": "Option B: RDTShard",
            "verdict": (
                "RDT hierarchy shows clear measurable gains for shard-resize stability with "
                "ancestor buckets plus stable mapping, while baseline hash map remains faster for pure point lookups."
            ),
        },
        "where_rdt_helps_most": [
            "RDT spatial hierarchy as a tunable exact partition (relative to untuned RDT baseline).",
            "Hybrid RDT-noise scheduler (RDT-guided reseeding + fast conventional core).",
            "Quality-tuned RDT256 output-stage variants for exploratory statistical shaping.",
            "RDTShard-style stable repartitioning under shard-count changes.",
        ],
        "honesty_notes": [
            "No universal superiority claims are made.",
            "All wins are tied to explicit benchmark settings in repository result files.",
            "Negative findings are retained and reported."
        ],
    }


def render_report(summary: dict[str, Any]) -> str:
    noise = summary["noise"]
    spatial = summary["spatial_index"]
    rdt = summary["rdt256"]
    toolbox = summary["rdt_toolbox_index"]

    lines: list[str] = []
    lines.append("# RDT Project Showcase Report")
    lines.append("")
    lines.append(f"- Generated (UTC): `{summary['generated_at_utc']}`")
    lines.append("")
    lines.append("## Repository Refs")
    for name, ref in summary["repo_refs"].items():
        lines.append(f"- `{name}`: branch `{ref['branch']}`, commit `{ref['commit']}`")
    lines.append("")

    lines.append("## 1) RDT-Noise")
    lines.append(f"- Hybrid speedup vs standard RDT: `{noise['hybrid_speedup_vs_rdt']:.3f}x`")
    lines.append(f"- Standard RDT / white speed ratio: `{noise['rdt_vs_white_speed_ratio']:.3f}` (greater than 1 means slower)")
    lines.append(f"- Hybrid entropy delta vs standard RDT: `{noise['hybrid_entropy_delta_vs_rdt']:.6f}` bits/byte")
    lines.append(f"- Hybrid mean |ACF| delta vs standard RDT: `{noise['hybrid_acf_abs_delta_vs_rdt']:.6f}`")
    lines.append(f"- Verdict: {noise['verdict']}")
    lines.append("")

    lines.append("## 2) RDT Spatial Index")
    lines.append("| dataset | rdt query ms | rdt_optimized query ms | speedup rdt/opt | grid query ms | kd query ms | opt exact match |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for name, row in spatial["datasets"].items():
        lines.append(
            f"| {name} | {row['rdt_query_ms']:.2f} | {row['rdt_opt_query_ms']:.2f} | "
            f"{row['rdt_to_opt_speedup']:.2f}x | {row['uniform_grid_query_ms']:.2f} | {row['kd_query_ms']:.2f} | {row['opt_exact_match']:.4f} |"
        )
    lines.append(f"- Verdict: {spatial['verdict']}")
    lines.append("")

    lines.append("## 3) RDT256")
    lines.append(f"- v3 speedup vs v2: `{rdt['v3_speedup_vs_v2']:.3f}x`")
    lines.append(f"- quality-proxy delta (v3-v2): `{rdt['quality_proxy_delta_v3_vs_v2']:.6f}` (negative means better)")
    lines.append(f"- v2 speed ratio vs SplitMix64: `{rdt['v2_speed_ratio_vs_splitmix']:.3f}`")
    lines.append(f"- Verdict: {rdt['verdict']}")
    lines.append("")

    lines.append("## 4) RDT Toolbox Index")
    lines.append(f"- Clear win count: `{toolbox['clear_win_count']}`")
    lines.append(f"- Best margin: `{toolbox['best_win_margin_pct']:.1f}%`")
    lines.append(f"- Packaging choice: `{toolbox['packaging_choice']}`")
    lines.append(f"- Verdict: {toolbox['verdict']}")
    lines.append("")

    lines.append("## Where RDT Is Legitimately Strong")
    for item in summary["where_rdt_helps_most"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Honesty / Limits")
    for item in summary["honesty_notes"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Next Upgrade Targets")
    lines.append("1. RDT spatial index: add adaptive hybrid dispatcher (RDT vs grid) by local anisotropy; optimize for query latency while preserving exactness.")
    lines.append("2. RDT-noise: use vectorized kernels for state transition while preserving deterministic reproducibility gates.")
    lines.append("3. RDT256: move core to a two-track implementation (quality mode and throughput mode), then benchmark both modes against fixed acceptance thresholds.")
    lines.append("")

    return "\n".join(lines)


def run_all() -> None:
    run_cmd(["python3", "tests/run_tests.py"], REPOS["rdt-noise"])
    run_cmd(["python3", "benchmarks/noise_benchmark.py", "--length", "262144", "--seed", "1729"], REPOS["rdt-noise"])

    run_cmd(["python3", "tests/run_tests.py"], REPOS["rdt-spatial-index"])
    run_cmd(["python3", "benchmarks/compare_indexes.py", "--seed", "1729", "--n", "50000"], REPOS["rdt-spatial-index"])

    run_cmd(["make", "benchmark-honest"], REPOS["rdt256"])
    run_cmd(["python3", "tests/run_results.py"], REPOS["rdt256"])

    run_cmd(["python3", "tools/run_tests.py"], SHOWCASE_ROOT)
    run_cmd(["python3", "tools/benchmark_rdt_index.py"], SHOWCASE_ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-run", action="store_true", help="Skip benchmark execution and only regenerate showcase report from existing results.")
    args = parser.parse_args()

    missing = [name for name, p in REPOS.items() if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required repositories: {', '.join(missing)}")

    if not args.skip_run:
        run_all()

    refs = {name: git_head(path) for name, path in REPOS.items()}

    noise = load_json(REPOS["rdt-noise"] / "results" / "noise_benchmark_results.json")
    spatial = load_json(REPOS["rdt-spatial-index"] / "results" / "benchmark_results.json")
    rdt256 = load_json(REPOS["rdt256"] / "results" / "stream_benchmark_results.json")
    index_bench = load_json(SHOWCASE_ROOT / "results" / "rdt_index_benchmark.json")

    summary = build_summary(noise, spatial, rdt256, index_bench, refs)

    out_json = SHOWCASE_ROOT / "results" / "showcase_summary.json"
    out_md = SHOWCASE_ROOT / "docs" / "rdt_showcase_report.md"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    out_md.write_text(render_report(summary), encoding="utf-8")

    print(f"Wrote JSON: {out_json}")
    print(f"Wrote report: {out_md}")


if __name__ == "__main__":
    main()
