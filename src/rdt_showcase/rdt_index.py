"""RDT index structures for deterministic hierarchical partitioning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def rdt_parent(n: int) -> int:
    """RDT parent map from the recursive-halving tree."""
    if n <= 1:
        return 1 if n == 1 else 0
    return n >> 1


def rdt_depth(n: int) -> int:
    """Depth to root 1 under repeated floor-halving."""
    if n <= 1:
        return 0
    # Equivalent to number of halving steps until reaching 1.
    return int(n).bit_length() - 1


def rdt_ancestor(n: int, k: int) -> int:
    """k-step ancestor under repeated floor-halving, clamped to root 1 for n>=1."""
    if n <= 0:
        return 0
    if k <= 0:
        return int(n)
    a = int(n) >> int(k)
    return a if a >= 1 else 1


def ancestor_range(depth_k: int, bucket_id: int) -> Tuple[int, int]:
    """Integer range whose depth-k ancestor equals bucket_id."""
    if bucket_id <= 0:
        return (0, 0)
    if depth_k <= 0:
        return (bucket_id, bucket_id)
    if bucket_id == 1:
        return (1, (2 << depth_k) - 1)
    lo = bucket_id << depth_k
    hi = ((bucket_id + 1) << depth_k) - 1
    return (lo, hi)


def depth_range(d: int) -> Tuple[int, int]:
    """Integer range whose RDT depth equals d."""
    if d <= 0:
        return (1, 1)
    lo = 1 << d
    hi = (1 << (d + 1)) - 1
    return (lo, hi)


def jump_consistent_hash(key: int, num_buckets: int) -> int:
    """Jump consistent hash (Lamping/Veach) for stable remapping."""
    if num_buckets < 1:
        raise ValueError("num_buckets must be >= 1")
    key_u = int(key) & 0xFFFFFFFFFFFFFFFF
    b = -1
    j = 0
    while j < num_buckets:
        b = j
        key_u = (key_u * 2862933555777941757 + 1) & 0xFFFFFFFFFFFFFFFF
        j = int((b + 1) * (1 << 31) / ((key_u >> 33) + 1))
    return int(b)


@dataclass
class NeighborResult:
    key: int
    value: Any
    shared_depth: int


class RDTIndex:
    """
    Deterministic RDT index.

    bucket_mode:
    - "depth": buckets by D(key)
    - "ancestor": buckets by ancestor(key, k)
    """

    def __init__(
        self,
        *,
        bucket_mode: str = "ancestor",
        max_bucket_depth: int = 20,
        shard_depth: int = 8,
        stable_sharding: bool = False,
    ) -> None:
        if bucket_mode not in ("depth", "ancestor"):
            raise ValueError("bucket_mode must be 'depth' or 'ancestor'")
        self.bucket_mode = bucket_mode
        self.max_bucket_depth = int(max_bucket_depth)
        self.shard_depth = int(shard_depth)
        self.stable_sharding = bool(stable_sharding)

        self._store: Dict[int, Any] = {}
        self._depth_buckets: Dict[int, set[int]] = {}
        self._anc_buckets: Dict[int, Dict[int, set[int]]] = {}

    @staticmethod
    def depth(key: int) -> int:
        return rdt_depth(key)

    @staticmethod
    def ancestor(key: int, depth_k: int) -> int:
        return rdt_ancestor(key, depth_k)

    @staticmethod
    def path_signature(key: int) -> List[int]:
        n = int(key)
        if n <= 0:
            return [0]
        out = [n]
        while n > 1:
            n = n >> 1
            out.append(n)
        return out

    def __len__(self) -> int:
        return len(self._store)

    def _remove_from_buckets(self, key: int) -> None:
        d = rdt_depth(key)
        db = self._depth_buckets.get(d)
        if db is not None:
            db.discard(key)
            if not db:
                del self._depth_buckets[d]

        for k in range(0, self.max_bucket_depth + 1):
            a = rdt_ancestor(key, k)
            level = self._anc_buckets.get(k)
            if level is None:
                continue
            b = level.get(a)
            if b is None:
                continue
            b.discard(key)
            if not b:
                del level[a]
            if not level:
                del self._anc_buckets[k]

    def _add_to_buckets(self, key: int) -> None:
        d = rdt_depth(key)
        self._depth_buckets.setdefault(d, set()).add(key)

        for k in range(0, self.max_bucket_depth + 1):
            a = rdt_ancestor(key, k)
            level = self._anc_buckets.setdefault(k, {})
            level.setdefault(a, set()).add(key)

    def insert(self, key: int, value: Any) -> None:
        key = int(key)
        if key < 1:
            raise ValueError("RDTIndex keys must be >= 1")
        if key in self._store:
            self._remove_from_buckets(key)
        self._store[key] = value
        self._add_to_buckets(key)

    def build(self, items: Iterable[Tuple[int, Any]]) -> None:
        self._store.clear()
        self._depth_buckets.clear()
        self._anc_buckets.clear()
        for k, v in items:
            self.insert(int(k), v)

    def get(self, key: int) -> Any:
        return self._store.get(int(key))

    def query_bucket(
        self, depth_k: int, bucket_id: int, query_mode: Optional[str] = None
    ) -> List[Tuple[int, Any]]:
        """Return key/value pairs in the requested bucket."""
        mode = self.bucket_mode if query_mode is None else str(query_mode)
        if mode == "depth":
            depth = int(depth_k)
            keys = self._depth_buckets.get(depth, set())
        elif mode == "ancestor":
            level = self._anc_buckets.get(int(depth_k), {})
            keys = level.get(int(bucket_id), set())
        else:
            raise ValueError(f"unknown query mode: {mode}")
        return [(k, self._store[k]) for k in keys]

    def approximate_neighbors(self, key: int, k_neighbors: int = 8) -> List[NeighborResult]:
        """Approximate neighbors by deepest shared RDT bucket first."""
        key = int(key)
        if key not in self._store or k_neighbors <= 0:
            return []

        if self.bucket_mode == "depth":
            d = rdt_depth(key)
            keys = self._depth_buckets.get(d, set()).copy()
            shared_depth = d
        else:
            keys = set()
            shared_depth = 0
            for depth_k in range(self.max_bucket_depth, -1, -1):
                anc = rdt_ancestor(key, depth_k)
                bucket = self._anc_buckets.get(depth_k, {}).get(anc, set())
                if len(bucket) >= max(2, k_neighbors):
                    keys = bucket.copy()
                    shared_depth = depth_k
                    break
            if not keys:
                keys = set(self._store.keys())
                shared_depth = 0

        keys.discard(key)
        ranked = sorted(keys, key=lambda x: abs(x - key))[:k_neighbors]
        return [NeighborResult(key=x, value=self._store[x], shared_depth=shared_depth) for x in ranked]

    def bucket_sizes(self, depth_k: int, mode: Optional[str] = None) -> Dict[int, int]:
        mode_eff = self.bucket_mode if mode is None else str(mode)
        if mode_eff == "depth":
            return {d: len(s) for d, s in self._depth_buckets.items()}
        if mode_eff != "ancestor":
            raise ValueError(f"unknown mode: {mode_eff}")
        level = self._anc_buckets.get(int(depth_k), {})
        return {bid: len(s) for bid, s in level.items()}

    def shard_of_key(self, key: int, shard_count: int) -> int:
        if shard_count < 1:
            raise ValueError("shard_count must be >= 1")
        key = int(key)

        if self.bucket_mode == "depth":
            bucket = rdt_depth(key)
        else:
            bucket = rdt_ancestor(key, self.shard_depth)

        if self.stable_sharding:
            return jump_consistent_hash(bucket, shard_count)
        return bucket % shard_count

    def shard_movement_rate(self, shard_from: int, shard_to: int, keys: Sequence[int]) -> float:
        if shard_from < 1 or shard_to < 1:
            raise ValueError("shard counts must be >= 1")
        if not keys:
            return 0.0
        moved = 0
        for key in keys:
            a = self.shard_of_key(key, shard_from)
            b = self.shard_of_key(key, shard_to)
            moved += int(a != b)
        return moved / len(keys)

    def shard_loads(self, shard_count: int, keys: Sequence[int]) -> Dict[int, int]:
        loads = {i: 0 for i in range(shard_count)}
        for key in keys:
            loads[self.shard_of_key(int(key), shard_count)] += 1
        return loads


__all__ = [
    "NeighborResult",
    "RDTIndex",
    "ancestor_range",
    "depth_range",
    "jump_consistent_hash",
    "rdt_ancestor",
    "rdt_depth",
    "rdt_parent",
]
