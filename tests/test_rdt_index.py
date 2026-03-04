from __future__ import annotations

import random
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rdt_showcase import BTreeLikeIndex, HashMapIndex, RDTIndex, SortedArrayIndex, rdt_ancestor, rdt_depth


class TestRDTIndex(unittest.TestCase):
    def setUp(self) -> None:
        rng = random.Random(11)
        keys = list(range(1, 400))
        rng.shuffle(keys)
        self.keys = keys[:300]
        self.items = [(k, k * 17 + 3) for k in self.keys]
        self.item_map = dict(self.items)

    def test_get_consistency(self) -> None:
        systems = [
            RDTIndex(bucket_mode="depth"),
            RDTIndex(bucket_mode="ancestor"),
            HashMapIndex(),
            SortedArrayIndex(),
            BTreeLikeIndex(block_size=32),
        ]
        for idx in systems:
            idx.build(self.items)
            for k, v in self.items:
                self.assertEqual(idx.get(k), v)
            self.assertIsNone(idx.get(99999991))

    def test_bucket_query_matches_bruteforce_depth(self) -> None:
        systems = [
            RDTIndex(bucket_mode="depth"),
            RDTIndex(bucket_mode="ancestor"),
            HashMapIndex(),
            SortedArrayIndex(),
            BTreeLikeIndex(block_size=32),
        ]

        for idx in systems:
            idx.build(self.items)
            for d in range(0, 9):
                expected = sorted(k for k in self.keys if rdt_depth(k) == d)
                if isinstance(idx, RDTIndex):
                    got = sorted(k for k, _ in idx.query_bucket(d, 0, query_mode="depth"))
                else:
                    got = sorted(k for k, _ in idx.query_bucket("depth", d, 0))
                self.assertEqual(got, expected)

    def test_bucket_query_matches_bruteforce_ancestor(self) -> None:
        systems = [
            RDTIndex(bucket_mode="depth"),
            RDTIndex(bucket_mode="ancestor"),
            HashMapIndex(),
            SortedArrayIndex(),
            BTreeLikeIndex(block_size=32),
        ]

        depth_k = 5
        candidate_buckets = sorted({rdt_ancestor(k, depth_k) for k in self.keys})[:20]
        for idx in systems:
            idx.build(self.items)
            for bid in candidate_buckets:
                expected = sorted(k for k in self.keys if rdt_ancestor(k, depth_k) == bid)
                if isinstance(idx, RDTIndex):
                    got = sorted(k for k, _ in idx.query_bucket(depth_k, bid, query_mode="ancestor"))
                else:
                    got = sorted(k for k, _ in idx.query_bucket("ancestor", depth_k, bid))
                self.assertEqual(got, expected)

    def test_approx_neighbors(self) -> None:
        idx = RDTIndex(bucket_mode="ancestor", max_bucket_depth=12)
        idx.build(self.items)

        q = self.keys[0]
        out = idx.approximate_neighbors(q, k_neighbors=8)
        self.assertLessEqual(len(out), 8)
        for row in out:
            self.assertIn(row.key, self.item_map)
            self.assertGreaterEqual(row.shared_depth, 0)

    def test_stable_sharding_reduces_movement(self) -> None:
        keys = list(range(1, 12000))
        rdt_mod = RDTIndex(bucket_mode="ancestor", shard_depth=8, stable_sharding=False)
        rdt_stable = RDTIndex(bucket_mode="ancestor", shard_depth=8, stable_sharding=True)
        rdt_mod.build((k, k) for k in keys)
        rdt_stable.build((k, k) for k in keys)

        m_mod = rdt_mod.shard_movement_rate(16, 20, keys)
        m_stable = rdt_stable.shard_movement_rate(16, 20, keys)
        self.assertLess(m_stable, m_mod)


if __name__ == "__main__":
    unittest.main()
