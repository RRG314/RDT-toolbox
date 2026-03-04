# Plugin Integration Guide

This guide shows how to integrate RDT Toolbox into existing systems as drop-in plugins.

## A) API Gateway / Service Router

Use `RDTShardPlugin` to route request keys to worker shards.

```python
from rdt_showcase import RDTShardPlugin

plugin = RDTShardPlugin(shard_count=32, shard_depth=9, stable_sharding=True)
plugin.configure_keys(current_customer_ids)

def route_request(customer_id: int) -> int:
    return plugin.shard_for(customer_id)
```

## B) Reshard Planning Tool

Estimate movement before changing cluster size.

```python
move = plugin.movement_rate(current_customer_ids, new_shard_count=40)
print(f"estimated movement: {move:.3f}")
```

## C) Auto-Tuned Sharding (Dual)

Use `RDTDualShardPlugin` when key distributions drift.

```python
from rdt_showcase import RDTDualShardPlugin

plugin = RDTDualShardPlugin(shard_count=32, min_depth=4, max_depth=12, init_depth=8.0)
plugin.configure_keys(current_customer_ids)
print(plugin.plan.shard_depth, plugin.tuning)
```

## D) Hierarchical Bucketed Retrieval

Use `RDTBucketPlugin` for grouped fetches and ancestry-based neighbors.

```python
from rdt_showcase import RDTBucketPlugin

bucket = RDTBucketPlugin(max_bucket_depth=12)
bucket.build((k, payload[k]) for k in payload)

rows = bucket.query_ancestor_bucket(depth_k=8, bucket_id=1)
neighbors = bucket.approximate_neighbors(12345, k_neighbors=10)
```

## Deployment Notes

- Keys must be positive integers (`>=1`).
- Keep benchmark artifacts in CI for any parameter changes.
- Prefer stable sharding mode for production repartitioning behavior.
