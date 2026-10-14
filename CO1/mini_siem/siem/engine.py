"""Pipeline orchestration.

  1. DIVIDE   split every log file into line-aligned byte ranges
  2. MAP      parse + sort each range in a worker process
  3. CONQUER  merge sorted runs with a parallel binary merge tree
  4. ENRICH   attach source IPs to IP-less events (sudo, useradd) via sessions
  5. SHARD    partition the unified timeline by source IP, balance shards
  6. MAP      run all detection rules over each shard in worker processes
  7. REDUCE   fuse alerts into per-attacker incidents and score them
"""
from __future__ import annotations

import multiprocessing as mp
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field

from .merge import tree_merge
from .models import Alert, Incident
from .parsers import detect_format, parse_chunk
from .rules import Config, run_rules

STAGE_ORDER = ["Reconnaissance", "Initial Access", "Credential Access",
               "Privilege Escalation", "Persistence", "Exfiltration"]


@dataclass
class Result:
    events: int = 0
    malformed: int = 0
    files: dict = field(default_factory=dict)
    alerts: list = field(default_factory=list)
    incidents: list = field(default_factory=list)
    timings: dict = field(default_factory=dict)
    workers: int = 1


# ------------------------------------------------------------ 1. divide
def plan_chunks(paths, workers, min_chunk):
    tasks, fmts = [], {}
    for fid, p in enumerate(paths):
        fmt = detect_format(p)
        fmts[p] = fmt
        size = os.path.getsize(p)
        n = max(1, min(workers * 4, size // max(1, min_chunk)))
        step = -(-size // n)                      # ceil
        for k in range(n):
            s, e = k * step, min(size, (k + 1) * step)
            if s < e:
                tasks.append((p, fmt, s, e, fid))
    return tasks, fmts


# ------------------------------------------------------------ 4. enrich
def enrich_sessions(events, ttl):
    """Single ordered pass: remember which IP each (host,user) logged in from,
    and use it for events that carry only a user (sudo, useradd, ...)."""
    sessions = {}
    for e in events:
        if e.action == "auth_ok" and e.ip:
            sessions[(e.host, e.user)] = (e.ip, e.ts)
        elif e.ip is None and e.user:
            s = sessions.get((e.host, e.user))
            if s and e.ts - s[1] <= ttl:
                e.ip, e.inferred_ip = s[0], True
    return events


# ------------------------------------------------------------- 5. shard
def shard_by_ip(events, n_shards):
    groups = defaultdict(list)
    for e in events:
        if e.ip:
            groups[e.ip].append(e)          # already time-ordered
    shards = [[] for _ in range(max(1, n_shards))]
    loads = [0] * len(shards)
    for ip, evs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        k = loads.index(min(loads))         # greedy longest-first balancing
        shards[k].append((ip, evs))
        loads[k] += len(evs)
    return [s for s in shards if s]


_SHARDS: list = []      # inherited by forked workers (copy-on-write), never pickled
_CFG = None


def _detect_shard(i):
    alerts = []
    for ip, evs in _SHARDS[i]:
        alerts.extend(run_rules(ip, evs, _CFG))
    return alerts


def _detect_shard_args(args):          # fallback path when fork is unavailable
    shard, cfg = args
    return [a for ip, evs in shard for a in run_rules(ip, evs, cfg)]


def resolve_evidence(alerts, paths):
    """Replace (fid, offset) refs with the raw log lines (only a few per alert)."""
    handles = {}
    try:
        for a in alerts:
            lines = []
            for fid, off in a.evidence:
                if fid not in handles:
                    handles[fid] = open(paths[fid], "rb")
                f = handles[fid]
                f.seek(off)
                lines.append(f.readline().decode("utf-8", "replace").rstrip())
            a.evidence = lines
    finally:
        for f in handles.values():
            f.close()


# ------------------------------------------------------------ 7. reduce
def severity(score):
    return ("CRITICAL" if score >= 90 else "HIGH" if score >= 70
            else "MEDIUM" if score >= 45 else "LOW")


def build_incidents(alerts, gap=7200):
    """Group alerts by IP; split into separate incidents on long quiet gaps."""
    by_ip = defaultdict(list)
    for a in alerts:
        by_ip[a.ip].append(a)
    incidents = []
    for ip, al in by_ip.items():
        al.sort(key=lambda a: a.start)
        cluster = [al[0]]
        clusters = [cluster]
        end = al[0].end
        for a in al[1:]:
            if a.start - end > gap:
                cluster = [a]; clusters.append(cluster)
            else:
                cluster.append(a)
            end = max(end, a.end)
        for c in clusters:
            incidents.append(_make_incident(ip, c))
    incidents.sort(key=lambda i: (-i.score, i.start))
    for n, inc in enumerate(incidents, 1):
        inc.id = f"INC-{n:03d}"
    return incidents


def _make_incident(ip, alerts):
    stages = sorted({a.stage for a in alerts}, key=STAGE_ORDER.index)
    sources = sorted({s for a in alerts for s in a.sources})
    # base = strongest alert; bonus for kill-chain breadth and multi-source corroboration
    score = min(100, max(a.score for a in alerts)
                + 6 * (len(stages) - 1) + 5 * (len(sources) - 1))
    users = sorted({a.user for a in alerts if a.user})
    hosts = sorted({h for a in alerts for h in a.host.split(",") if h})
    inc = Incident(id="", ip=ip, start=min(a.start for a in alerts),
                   end=max(a.end for a in alerts), score=score,
                   severity=severity(score), stages=stages, sources=sources,
                   users=users, hosts=hosts, alerts=alerts)
    inc.summary = (f"{ip} progressed through {' -> '.join(stages)} "
                   f"across {len(sources)} log source(s): {', '.join(sources)}.")
    return inc


# ------------------------------------------------------------ driver
def analyze(paths, workers=None, cfg=None, min_chunk=256 * 1024) -> Result:
    workers = workers or os.cpu_count() or 1
    cfg = cfg or Config()
    res, T = Result(workers=workers), {}
    t0 = time.perf_counter()

    tasks, fmts = plan_chunks(paths, workers, min_chunk)
    res.files = {p: f for p, f in fmts.items()}

    pool = mp.Pool(workers) if workers > 1 else None
    try:
        mapper = pool.map if pool else map
        parsed = list(mapper(parse_chunk, tasks))
        T["parse"] = time.perf_counter() - t0

        t = time.perf_counter()
        events = tree_merge([ev for ev, _ in parsed], pool)
        res.malformed = sum(b for _, b in parsed)
        T["merge"] = time.perf_counter() - t

        t = time.perf_counter()
        enrich_sessions(events, cfg.session_ttl)
        shards = shard_by_ip(events, workers * 4)
        T["shard"] = time.perf_counter() - t

        t = time.perf_counter()
        global _SHARDS, _CFG
        _SHARDS, _CFG = shards, cfg
        if workers > 1 and "fork" in mp.get_all_start_methods():
            # fresh pool forked *after* sharding: workers see the shards via
            # copy-on-write, so only shard indexes and small alert lists cross IPC
            with mp.get_context("fork").Pool(workers) as p2:
                alert_lists = p2.map(_detect_shard, range(len(shards)))
        elif pool:
            alert_lists = pool.map(_detect_shard_args, [(s, cfg) for s in shards])
        else:
            alert_lists = [_detect_shard(i) for i in range(len(shards))]
        _SHARDS = []
        T["detect"] = time.perf_counter() - t
    finally:
        if pool:
            pool.close(); pool.join()

    res.events = len(events)
    res.alerts = sorted((a for lst in alert_lists for a in lst), key=lambda a: a.start)
    resolve_evidence(res.alerts, list(paths))
    res.incidents = build_incidents(res.alerts)
    T["total"] = time.perf_counter() - t0
    res.timings = T
    return res
