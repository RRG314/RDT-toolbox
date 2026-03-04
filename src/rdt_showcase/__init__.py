"""RDT showcase package: index implementations and benchmark helpers."""

from .baselines import BTreeLikeIndex, HashMapIndex, SortedArrayIndex
from .dual import Dual, exp, log, sigmoid, to_dual
from .dual_tuning import DualTuneResult, RDTDualTunedIndex, dual_tune_shard_depth
from .rdt_index import (
    NeighborResult,
    RDTIndex,
    ancestor_range,
    depth_range,
    jump_consistent_hash,
    rdt_ancestor,
    rdt_depth,
    rdt_parent,
)

__all__ = [
    "BTreeLikeIndex",
    "Dual",
    "DualTuneResult",
    "HashMapIndex",
    "NeighborResult",
    "RDTIndex",
    "RDTDualTunedIndex",
    "SortedArrayIndex",
    "ancestor_range",
    "depth_range",
    "dual_tune_shard_depth",
    "exp",
    "jump_consistent_hash",
    "log",
    "rdt_ancestor",
    "rdt_depth",
    "rdt_parent",
    "sigmoid",
    "to_dual",
]
