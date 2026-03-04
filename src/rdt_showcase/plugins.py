"""Plugin-style adapters for integrating RDT tools into existing applications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .dual_tuning import dual_tune_shard_depth
from .rdt_index import RDTIndex


@dataclass
class ShardPlan:
    shard_count: int
    shard_depth: int
    stable_sharding: bool


class RDTShardPlugin:
    """
    Deterministic sharding plugin backed by ancestor buckets.

    Typical use:
    - configure once from current key distribution
    - route keys with `shard_for(...)`
    - estimate movement before changing shard count
    """

    def __init__(
        self,
        *,
        shard_count: int,
        shard_depth: int = 8,
        stable_sharding: bool = True,
        max_bucket_depth: int = 12,
    ) -> None:
        if shard_count < 1:
            raise ValueError("shard_count must be >= 1")
        self._plan = ShardPlan(
            shard_count=int(shard_count),
            shard_depth=int(shard_depth),
            stable_sharding=bool(stable_sharding),
        )
        self._index = RDTIndex(
            bucket_mode="ancestor",
            max_bucket_depth=max(int(max_bucket_depth), int(shard_depth)),
            shard_depth=int(shard_depth),
            stable_sharding=bool(stable_sharding),
        )

    @property
    def plan(self) -> ShardPlan:
        return self._plan

    def configure_keys(self, keys: Sequence[int]) -> None:
        self._index.build((int(k), 0) for k in keys)

    def shard_for(self, key: int, shard_count: int | None = None) -> int:
        count = self._plan.shard_count if shard_count is None else int(shard_count)
        return self._index.shard_of_key(int(key), count)

    def assign_many(self, keys: Sequence[int], shard_count: int | None = None) -> Dict[int, int]:
        count = self._plan.shard_count if shard_count is None else int(shard_count)
        return {int(k): self._index.shard_of_key(int(k), count) for k in keys}

    def shard_loads(self, keys: Sequence[int], shard_count: int | None = None) -> Dict[int, int]:
        count = self._plan.shard_count if shard_count is None else int(shard_count)
        return self._index.shard_loads(count, [int(k) for k in keys])

    def movement_rate(self, keys: Sequence[int], new_shard_count: int) -> float:
        return self._index.shard_movement_rate(
            self._plan.shard_count,
            int(new_shard_count),
            [int(k) for k in keys],
        )


class RDTDualShardPlugin(RDTShardPlugin):
    """
    RDT shard plugin with dual-number-guided shard-depth tuning.

    Useful when key distribution changes and fixed depth is suboptimal.
    """

    def __init__(
        self,
        *,
        shard_count: int,
        min_depth: int = 4,
        max_depth: int = 12,
        init_depth: float = 8.0,
        stable_sharding: bool = True,
    ) -> None:
        super().__init__(
            shard_count=shard_count,
            shard_depth=int(round(init_depth)),
            stable_sharding=stable_sharding,
            max_bucket_depth=max_depth,
        )
        self.min_depth = int(min_depth)
        self.max_depth = int(max_depth)
        self.init_depth = float(init_depth)
        self.tuning: Dict[str, Any] = {}

    def configure_keys(self, keys: Sequence[int]) -> None:
        keys_list = [int(k) for k in keys]
        tune = dual_tune_shard_depth(
            keys_list,
            min_depth=self.min_depth,
            max_depth=self.max_depth,
            init_depth=self.init_depth,
            stable_sharding=self.plan.stable_sharding,
        )
        self._plan = ShardPlan(
            shard_count=self.plan.shard_count,
            shard_depth=tune.shard_depth,
            stable_sharding=self.plan.stable_sharding,
        )
        self._index = RDTIndex(
            bucket_mode="ancestor",
            max_bucket_depth=max(self.max_depth, tune.shard_depth),
            shard_depth=tune.shard_depth,
            stable_sharding=self.plan.stable_sharding,
        )
        self._index.build((k, 0) for k in keys_list)
        self.tuning = {
            "continuous_depth": tune.continuous_depth,
            "depth": tune.shard_depth,
            "objective": tune.objective,
            "gradient_steps": tune.gradient_steps,
        }


class RDTBucketPlugin:
    """
    Hierarchical bucket query plugin for key/value stores.

    Useful for:
    - deterministic bucket scans
    - approximate neighbor grouping by shared ancestry
    """

    def __init__(self, *, max_bucket_depth: int = 12) -> None:
        self._index = RDTIndex(
            bucket_mode="ancestor",
            max_bucket_depth=int(max_bucket_depth),
            shard_depth=min(8, int(max_bucket_depth)),
            stable_sharding=True,
        )

    def build(self, items: Iterable[Tuple[int, Any]]) -> None:
        self._index.build((int(k), v) for k, v in items)

    def insert(self, key: int, value: Any) -> None:
        self._index.insert(int(key), value)

    def get(self, key: int) -> Any:
        return self._index.get(int(key))

    def query_ancestor_bucket(self, depth_k: int, bucket_id: int) -> List[Tuple[int, Any]]:
        return self._index.query_bucket(int(depth_k), int(bucket_id), query_mode="ancestor")

    def approximate_neighbors(self, key: int, k_neighbors: int = 8):
        return self._index.approximate_neighbors(int(key), int(k_neighbors))


__all__ = ["RDTBucketPlugin", "RDTDualShardPlugin", "RDTShardPlugin", "ShardPlan"]
