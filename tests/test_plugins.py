from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rdt_showcase import RDTBucketPlugin, RDTDualShardPlugin, RDTShardPlugin


class TestPlugins(unittest.TestCase):
    def test_rdt_shard_plugin(self) -> None:
        keys = list(range(1, 5000))
        plugin = RDTShardPlugin(shard_count=16, shard_depth=8, stable_sharding=True)
        plugin.configure_keys(keys)

        s = plugin.shard_for(1234)
        self.assertGreaterEqual(s, 0)
        self.assertLess(s, 16)

        move = plugin.movement_rate(keys, new_shard_count=20)
        self.assertGreaterEqual(move, 0.0)
        self.assertLessEqual(move, 1.0)

    def test_rdt_dual_shard_plugin(self) -> None:
        keys = list(range(1000, 9000))
        plugin = RDTDualShardPlugin(shard_count=16, min_depth=4, max_depth=12, init_depth=8.0)
        plugin.configure_keys(keys)

        self.assertIn("depth", plugin.tuning)
        self.assertGreaterEqual(plugin.plan.shard_depth, 4)
        self.assertLessEqual(plugin.plan.shard_depth, 12)

    def test_rdt_bucket_plugin(self) -> None:
        items = [(k, k * 11) for k in range(1, 2000)]
        plugin = RDTBucketPlugin(max_bucket_depth=10)
        plugin.build(items)

        self.assertEqual(plugin.get(10), 110)
        rows = plugin.query_ancestor_bucket(6, 1)
        self.assertTrue(rows)

        nbrs = plugin.approximate_neighbors(1000, k_neighbors=6)
        self.assertLessEqual(len(nbrs), 6)


if __name__ == "__main__":
    unittest.main()
