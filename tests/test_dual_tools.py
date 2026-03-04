from __future__ import annotations

import math
import random
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rdt_showcase import Dual, RDTDualTunedIndex, dual_tune_shard_depth, exp


class TestDualTools(unittest.TestCase):
    def test_dual_polynomial_derivative(self) -> None:
        x = Dual(2.0, 1.0)
        y = x * x + 3.0 * x + 5.0
        self.assertAlmostEqual(y.val, 15.0, places=9)
        self.assertAlmostEqual(y.der, 7.0, places=9)

    def test_dual_exp_derivative(self) -> None:
        x = Dual(0.7, 1.0)
        y = exp(x)
        self.assertAlmostEqual(y.val, math.exp(0.7), places=9)
        self.assertAlmostEqual(y.der, math.exp(0.7), places=9)

    def test_dual_tuner_returns_valid_depth(self) -> None:
        rng = random.Random(17)
        keys = [rng.randint(1, 10_000_000) for _ in range(5000)]
        tune = dual_tune_shard_depth(keys, min_depth=4, max_depth=12, init_depth=8.0)
        self.assertGreaterEqual(tune.shard_depth, 4)
        self.assertLessEqual(tune.shard_depth, 12)
        self.assertTrue(tune.per_depth)

    def test_dual_tuned_index_build(self) -> None:
        items = [(k, k * 2 + 1) for k in range(1, 3000)]
        idx = RDTDualTunedIndex(min_depth=4, max_depth=12, init_depth=8.0)
        idx.build(items)

        self.assertIn("shard_depth", idx.tuning)
        self.assertGreaterEqual(idx.shard_depth, 4)
        self.assertLessEqual(idx.shard_depth, 12)

        # Basic API behavior still matches RDTIndex expectations.
        self.assertEqual(idx.get(100), 201)
        self.assertIsNone(idx.get(9_999_999))


if __name__ == "__main__":
    unittest.main()
