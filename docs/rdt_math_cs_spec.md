# RDT Math/CS Specification

This document defines the core RDT objects used in this repository in a math/CS style.

## 1. Core Tree Map

For integer keys `n >= 1`, define the parent map:

- `f(1) = 1`
- `f(n) = floor(n/2)` for `n > 1`

This induces a rooted tree with root `1`.

## 2. Depth Function

Define depth to root:

- `D(n) = min { t >= 0 : f^t(n) = 1 }`

For `n >= 1`, we use the closed form:

- `D(n) = floor(log2 n)`

Proof sketch:
- After `t` halving steps, `f^t(n) = floor(n / 2^t)`.
- The smallest `t` with `floor(n / 2^t) = 1` is exactly `floor(log2 n)`.

## 3. Ancestor Function

At depth level `k >= 0`, define:

- `A_k(n) = max(1, floor(n / 2^k))`

`A_k(n)` is the `k`-step ancestor of `n` in the RDT tree.

## 4. Buckets

Two bucket modes are used:

- Depth bucket: `B_depth(d) = { n : D(n) = d }`
- Ancestor bucket at level `k`: `B_anc(k, b) = { n : A_k(n) = b }`

The repository benchmark compares both modes.

## 5. Approximate Neighbors

Given key `x`, approximate neighbors are keys sharing deepest available ancestor bucket first, then ranked by key distance:

1. Find largest `k` where `|B_anc(k, A_k(x))|` is sufficiently large.
2. Rank keys in that bucket by `|y - x|`.

This is a deterministic hierarchical heuristic, not an exact NN guarantee.

## 6. Shard Assignment

Given a shard count `S`:

- Baseline mapping: `shard = bucket_id mod S`
- Stable mapping: `shard = JumpConsistentHash(bucket_id, S)`

In this repository, the measurable win case comes from:
- ancestor buckets (`A_k`) + stable mapping.

## 7. LCA Ultrametric (Tree Geometry)

On the rooted tree, let `lca(a,b)` be the lowest common ancestor depth from the root.
Define:

- `d(a,b) = 2^{-lca_depth(a,b)}`

Standard rooted-tree argument gives ultrametric inequality:

- `d(x,z) <= max(d(x,y), d(y,z))`

This metric is included as structure motivation; current benchmark focuses on indexing/sharding tasks.

## 8. Claim Status Discipline

This repo uses three statuses in reports:

- `Proven`: short formal argument included (as above for core tree identities)
- `Verified`: computationally tested over benchmark workloads
- `Conjecture`: not proven and marked explicitly

No claim is labeled theorem unless a proof is supplied in-doc.
