"""Dual-number-guided tuning utilities for RDT index parameters."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Iterable, Sequence

from .dual import Dual, exp
from .rdt_index import RDTIndex, rdt_ancestor


def _cv(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean <= 0.0:
        return 0.0
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(var) / mean


def _score_for_depth(
    keys: Sequence[int],
    depth_k: int,
    shard_from: int,
    shard_to: int,
    stable_sharding: bool,
    w_move: float,
    w_load: float,
    w_bucket: float,
) -> Dict[str, float]:
    idx = RDTIndex(
        bucket_mode="ancestor",
        max_bucket_depth=max(4, depth_k),
        shard_depth=depth_k,
        stable_sharding=stable_sharding,
    )
    idx.build((int(k), 0) for k in keys)

    movement = idx.shard_movement_rate(shard_from, shard_to, keys)

    loads_to = idx.shard_loads(shard_to, keys)
    load_cv = _cv(list(loads_to.values()))

    counts = idx.bucket_sizes(depth_k, mode="ancestor")
    bucket_cv = _cv(list(counts.values()))

    score = w_move * movement + w_load * load_cv + w_bucket * bucket_cv

    return {
        "depth": float(depth_k),
        "movement": float(movement),
        "load_cv": float(load_cv),
        "bucket_cv": float(bucket_cv),
        "score": float(score),
    }


def _soft_objective(x: Dual, per_depth_score: Dict[int, float], sigma: float = 1.0) -> Dual:
    """Smooth objective over integer depth scores via Gaussian kernels."""
    num = Dual(0.0, 0.0)
    den = Dual(0.0, 0.0)

    for k, score_k in per_depth_score.items():
        dx = x - float(k)
        w = exp(-(dx * dx) / (2.0 * sigma * sigma))
        num = num + w * score_k
        den = den + w

    return num / den


@dataclass
class DualTuneResult:
    shard_depth: int
    continuous_depth: float
    objective: float
    per_depth: Dict[int, Dict[str, float]]
    gradient_steps: int



def dual_tune_shard_depth(
    keys: Sequence[int],
    *,
    min_depth: int = 3,
    max_depth: int = 14,
    init_depth: float = 8.0,
    shard_from: int = 16,
    shard_to: int = 20,
    stable_sharding: bool = True,
    w_move: float = 0.70,
    w_load: float = 0.20,
    w_bucket: float = 0.10,
    sigma: float = 1.0,
    lr: float = 0.85,
    steps: int = 40,
) -> DualTuneResult:
    if min_depth < 1 or max_depth < min_depth:
        raise ValueError("invalid depth range")
    if not keys:
        return DualTuneResult(
            shard_depth=min_depth,
            continuous_depth=float(min_depth),
            objective=0.0,
            per_depth={},
            gradient_steps=0,
        )

    per_depth: Dict[int, Dict[str, float]] = {}
    score_table: Dict[int, float] = {}

    for k in range(min_depth, max_depth + 1):
        row = _score_for_depth(
            keys,
            k,
            shard_from,
            shard_to,
            stable_sharding,
            w_move,
            w_load,
            w_bucket,
        )
        per_depth[k] = row
        score_table[k] = row["score"]

    x = max(float(min_depth), min(float(max_depth), float(init_depth)))
    for _ in range(max(1, steps)):
        d = Dual(x, 1.0)
        obj = _soft_objective(d, score_table, sigma=sigma)
        grad = obj.der
        # gradient step with clipping to keep deterministic/stable behavior
        x = x - lr * grad
        if x < min_depth:
            x = float(min_depth)
        if x > max_depth:
            x = float(max_depth)

    # Project to nearby integer depth and take best true discrete score.
    neighborhood = sorted(
        set(
            int(v)
            for v in [
                round(x),
                math.floor(x),
                math.ceil(x),
                round(x) - 1,
                round(x) + 1,
            ]
            if min_depth <= int(v) <= max_depth
        )
    )
    if not neighborhood:
        neighborhood = [min_depth]

    best_k = min(neighborhood, key=lambda k: score_table[k])
    best_obj = score_table[best_k]

    return DualTuneResult(
        shard_depth=int(best_k),
        continuous_depth=float(x),
        objective=float(best_obj),
        per_depth=per_depth,
        gradient_steps=max(1, steps),
    )


class RDTDualTunedIndex(RDTIndex):
    """
    RDT ancestor index with dual-number-guided shard-depth tuning.

    The tuned value is chosen once at build time from the current key set.
    """

    def __init__(
        self,
        *,
        min_depth: int = 3,
        max_depth: int = 14,
        init_depth: float = 8.0,
        stable_sharding: bool = True,
    ) -> None:
        super().__init__(
            bucket_mode="ancestor",
            max_bucket_depth=max_depth,
            shard_depth=int(round(init_depth)),
            stable_sharding=stable_sharding,
        )
        self.min_depth = int(min_depth)
        self.max_depth = int(max_depth)
        self.init_depth = float(init_depth)
        self.tuning: Dict[str, Any] = {}

    def build(self, items: Iterable[tuple[int, Any]]) -> None:
        items_list = [(int(k), v) for k, v in items]
        keys = [k for k, _ in items_list]

        tune = dual_tune_shard_depth(
            keys,
            min_depth=self.min_depth,
            max_depth=self.max_depth,
            init_depth=self.init_depth,
            stable_sharding=self.stable_sharding,
        )
        self.shard_depth = tune.shard_depth
        self.max_bucket_depth = max(self.max_bucket_depth, tune.shard_depth)
        self.tuning = {
            "continuous_depth": tune.continuous_depth,
            "shard_depth": tune.shard_depth,
            "objective": tune.objective,
            "gradient_steps": tune.gradient_steps,
            "per_depth": tune.per_depth,
        }

        super().build(items_list)


__all__ = ["DualTuneResult", "RDTDualTunedIndex", "dual_tune_shard_depth"]
