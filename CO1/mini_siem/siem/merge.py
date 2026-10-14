"""Divide-and-conquer log merging.

Each worker produces a *sorted run* (divide). Runs are then merged pairwise,
level by level, like the merge phase of merge sort (conquer). Every level's
pair-merges are independent, so they are farmed out to the process pool:

    runs:    r0  r1  r2  r3  r4  r5  r6  r7
    level 1:  \\/    \\/    \\/    \\/        4 parallel merges
    level 2:    \\  /        \\  /           2 parallel merges
    level 3:        \\      /                1 merge
"""
from __future__ import annotations

from array import array
from typing import Callable, Optional, Sequence


def merge_two(a: list, b: list) -> list:
    """Stable two-way merge of runs sorted by `.ts`. O(len(a)+len(b))."""
    out, i, j = [], 0, 0
    la, lb = len(a), len(b)
    while i < la and j < lb:
        if a[i].ts <= b[j].ts:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    if i < la:
        out.extend(a[i:])
    if j < lb:
        out.extend(b[j:])
    return out


def _merge_keyed(pair: tuple) -> tuple:
    """Merge two runs represented as (timestamps, global_ids) arrays.
    Arrays pickle as raw bytes, so shipping them between processes is cheap
    (shipping thousands of Event objects is not)."""
    (ta, ia), (tb, ib) = pair
    to, io = array("d"), array("q")
    i = j = 0
    la, lb = len(ta), len(tb)
    while i < la and j < lb:
        if ta[i] <= tb[j]:
            to.append(ta[i]); io.append(ia[i]); i += 1
        else:
            to.append(tb[j]); io.append(ib[j]); j += 1
    to.extend(ta[i:]); io.extend(ia[i:])
    to.extend(tb[j:]); io.extend(ib[j:])
    return to, io


def tree_merge(runs: Sequence[list], pool=None) -> list:
    """Merge many sorted runs using a balanced binary merge tree.

    With `pool` (a multiprocessing.Pool) each tree level runs in parallel on
    compact key arrays and the events are permuted once at the end; without
    one, it is the same algorithm executed serially on the events directly.
    """
    runs = [r for r in runs if r]
    if not runs:
        return []
    if pool is None or len(runs) < 3:
        while len(runs) > 1:
            nxt = [merge_two(runs[i], runs[i + 1]) for i in range(0, len(runs) - 1, 2)]
            runs = nxt + ([runs[-1]] if len(runs) % 2 else [])
        return runs[0]

    flat = [e for r in runs for e in r]
    keyed, off = [], 0
    for r in runs:
        keyed.append((array("d", [e.ts for e in r]), array("q", range(off, off + len(r)))))
        off += len(r)
    while len(keyed) > 1:
        pairs = [(keyed[i], keyed[i + 1]) for i in range(0, len(keyed) - 1, 2)]
        merged = pool.map(_merge_keyed, pairs) if len(pairs) > 1 else [_merge_keyed(pairs[0])]
        keyed = merged + ([keyed[-1]] if len(keyed) % 2 else [])
    return [flat[i] for i in keyed[0][1]]


def merge_sort(items: list, key: Optional[Callable] = None, cutoff: int = 32) -> list:
    """Classic recursive divide-and-conquer sort (used as a reference/teaching
    implementation and in the tests; the pipeline itself sorts leaf chunks
    with Timsort and uses `tree_merge` above)."""
    if key is None:
        key = lambda e: e.ts          # noqa: E731
    if len(items) <= cutoff:
        return sorted(items, key=key)
    mid = len(items) // 2
    left, right = merge_sort(items[:mid], key, cutoff), merge_sort(items[mid:], key, cutoff)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out
