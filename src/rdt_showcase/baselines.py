"""Baseline index structures for comparative benchmarking."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .rdt_index import ancestor_range, depth_range, rdt_ancestor, rdt_depth


class HashMapIndex:
    """Baseline A: hash map."""

    def __init__(self) -> None:
        self._store: Dict[int, Any] = {}

    def __len__(self) -> int:
        return len(self._store)

    def build(self, items: Iterable[Tuple[int, Any]]) -> None:
        self._store = {int(k): v for k, v in items}

    def insert(self, key: int, value: Any) -> None:
        self._store[int(key)] = value

    def get(self, key: int) -> Any:
        return self._store.get(int(key))

    def range_query(self, low: int, high: int) -> List[Tuple[int, Any]]:
        return [(k, v) for k, v in self._store.items() if low <= k <= high]

    def query_bucket(self, mode: str, depth_k: int, bucket_id: int) -> List[Tuple[int, Any]]:
        if mode == "depth":
            d = int(depth_k)
            return [(k, v) for k, v in self._store.items() if rdt_depth(k) == d]
        if mode == "ancestor":
            dk = int(depth_k)
            bid = int(bucket_id)
            return [(k, v) for k, v in self._store.items() if rdt_ancestor(k, dk) == bid]
        raise ValueError(f"unknown mode: {mode}")

    def keys(self) -> List[int]:
        return list(self._store.keys())


class SortedArrayIndex:
    """Baseline B: sorted array + binary search."""

    def __init__(self) -> None:
        self._keys: List[int] = []
        self._values: List[Any] = []

    def __len__(self) -> int:
        return len(self._keys)

    def build(self, items: Iterable[Tuple[int, Any]]) -> None:
        # Keep last value for duplicate keys.
        temp: Dict[int, Any] = {}
        for k, v in items:
            temp[int(k)] = v
        data = sorted(temp.items())
        self._keys = [k for k, _ in data]
        self._values = [v for _, v in data]

    def insert(self, key: int, value: Any) -> None:
        key = int(key)
        i = bisect_left(self._keys, key)
        if i < len(self._keys) and self._keys[i] == key:
            self._values[i] = value
            return
        self._keys.insert(i, key)
        self._values.insert(i, value)

    def get(self, key: int) -> Any:
        key = int(key)
        i = bisect_left(self._keys, key)
        if i < len(self._keys) and self._keys[i] == key:
            return self._values[i]
        return None

    def range_query(self, low: int, high: int) -> List[Tuple[int, Any]]:
        i = bisect_left(self._keys, int(low))
        j = bisect_right(self._keys, int(high))
        return list(zip(self._keys[i:j], self._values[i:j]))

    def query_bucket(self, mode: str, depth_k: int, bucket_id: int) -> List[Tuple[int, Any]]:
        if mode == "depth":
            lo, hi = depth_range(int(depth_k))
            return self.range_query(lo, hi)
        if mode == "ancestor":
            lo, hi = ancestor_range(int(depth_k), int(bucket_id))
            return self.range_query(lo, hi)
        raise ValueError(f"unknown mode: {mode}")

    def keys(self) -> List[int]:
        return self._keys.copy()


class BTreeLikeIndex:
    """
    Baseline C: lightweight B-tree-like block index.

    Stores sorted blocks, each with bounded size; searches blocks by max-key then
    within block via binary search.
    """

    def __init__(self, block_size: int = 128) -> None:
        if block_size < 8:
            raise ValueError("block_size must be >= 8")
        self.block_size = int(block_size)
        self.blocks: List[List[Tuple[int, Any]]] = []
        self.max_keys: List[int] = []

    def __len__(self) -> int:
        return sum(len(b) for b in self.blocks)

    def _recompute_max_keys(self) -> None:
        self.max_keys = [blk[-1][0] for blk in self.blocks if blk]

    def build(self, items: Iterable[Tuple[int, Any]]) -> None:
        temp: Dict[int, Any] = {}
        for k, v in items:
            temp[int(k)] = v
        data = sorted(temp.items())

        self.blocks = []
        if not data:
            self.max_keys = []
            return

        step = self.block_size
        for i in range(0, len(data), step):
            self.blocks.append(data[i : i + step])
        self._recompute_max_keys()

    def _find_block_index(self, key: int) -> int:
        if not self.blocks:
            return 0
        i = bisect_left(self.max_keys, int(key))
        if i >= len(self.blocks):
            return len(self.blocks) - 1
        return i

    def insert(self, key: int, value: Any) -> None:
        key = int(key)
        if not self.blocks:
            self.blocks = [[(key, value)]]
            self.max_keys = [key]
            return

        bi = self._find_block_index(key)
        block = self.blocks[bi]

        keys = [k for k, _ in block]
        i = bisect_left(keys, key)
        if i < len(block) and block[i][0] == key:
            block[i] = (key, value)
        else:
            block.insert(i, (key, value))

        if len(block) > self.block_size * 2:
            mid = len(block) // 2
            left = block[:mid]
            right = block[mid:]
            self.blocks[bi] = left
            self.blocks.insert(bi + 1, right)

        self._recompute_max_keys()

    def get(self, key: int) -> Any:
        key = int(key)
        if not self.blocks:
            return None
        bi = self._find_block_index(key)
        block = self.blocks[bi]
        keys = [k for k, _ in block]
        i = bisect_left(keys, key)
        if i < len(block) and block[i][0] == key:
            return block[i][1]
        return None

    def range_query(self, low: int, high: int) -> List[Tuple[int, Any]]:
        low = int(low)
        high = int(high)
        if not self.blocks or low > high:
            return []

        out: List[Tuple[int, Any]] = []
        bi = bisect_left(self.max_keys, low)
        if bi >= len(self.blocks):
            return []

        for block in self.blocks[bi:]:
            if block[0][0] > high:
                break
            for k, v in block:
                if k < low:
                    continue
                if k > high:
                    return out
                out.append((k, v))
        return out

    def query_bucket(self, mode: str, depth_k: int, bucket_id: int) -> List[Tuple[int, Any]]:
        if mode == "depth":
            lo, hi = depth_range(int(depth_k))
            return self.range_query(lo, hi)
        if mode == "ancestor":
            lo, hi = ancestor_range(int(depth_k), int(bucket_id))
            return self.range_query(lo, hi)
        raise ValueError(f"unknown mode: {mode}")

    def keys(self) -> List[int]:
        out: List[int] = []
        for block in self.blocks:
            out.extend(k for k, _ in block)
        return out


__all__ = ["HashMapIndex", "SortedArrayIndex", "BTreeLikeIndex"]
