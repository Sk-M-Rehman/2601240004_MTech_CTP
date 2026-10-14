# Mini-SIEM — Security Incident Correlation Engine

Correlates events across **auth (sshd/sudo/useradd), web access, firewall and
application (JSON)** logs and surfaces probable security incidents, mapped to
kill-chain stages and MITRE ATT&CK technique IDs. Pure Python 3.10+, no dependencies.

## Quick start
```bash
python main.py generate sample_logs --events 50000     # synthetic logs + injected attacks
python main.py analyze sample_logs/*.log --workers 4 --html report.html --json report.json
python main.py bench sample_logs/*.log --max-workers 4 # compare worker counts
python -m unittest discover -s tests                   # tests
```

## How it works
| Stage | Technique | Module |
|---|---|---|
| 1. Divide | each file is cut into line-aligned byte ranges | `engine.plan_chunks` |
| 2. Map | workers parse + sort their range (`multiprocessing.Pool`) | `parsers.parse_chunk` |
| 3. Conquer | sorted runs merged by a balanced **binary merge tree**, each level in parallel (compact timestamp/index arrays cross process boundaries, not event objects) | `merge.tree_merge` |
| 4. Enrich | sessions link IP-less events (`sudo`, `useradd`) to the IP that logged in | `engine.enrich_sessions` |
| 5. Shard | unified timeline partitioned by source IP, load-balanced | `engine.shard_by_ip` |
| 6. Detect | all rules run per shard in workers (forked, copy-on-write — no event pickling) | `rules.run_rules` |
| 7. Reduce | alerts fused into per-attacker incidents; score = strongest alert + kill-chain breadth + multi-source bonus | `engine.build_incidents` |

**Detections** (`siem/rules.py`, thresholds in `Config`): port scan (distinct dropped ports in a window),
SSH/app brute force, password spraying, web attacks (SQLi / traversal / XSS / scanner UAs / sensitive paths, regex on URL-decoded
requests) and forced browsing, **successful login after a credential attack**, then post-compromise
**privilege escalation, persistence (new account), and large downloads**. Later rules consume earlier
alerts, which is what turns isolated alerts into a correlated chain.

The generator plants one full kill chain (`203.0.113.50`, CRITICAL, spans firewall+auth+app), a password
sprayer, a web attacker, and a benign user who mistypes a password 3 times (must *not* alert).

## Extending
* New log format: add a `parse_x` in `parsers.py`, register in `PARSERS`, extend `detect_format`.
* New rule: write `rule_x(ip, events, cfg, prior_alerts) -> [Alert]`, append to `RULES`.

## Performance notes
Parallel speedup is bounded by serial work in the parent (unpickling parsed events, final merge
permutation). On a 2-core box with 300k events: detect 1.6s → 1.0s, total 4.05s → 3.47s.
Gains grow with core count and log size; raise `--min-chunk` for tiny inputs where pool overhead dominates.
Ideas: stream chunks to disk (e.g. Parquet), or move to shared memory.
Limitation: rules are keyed on source IP; user-only correlation (no IP at all) is not modeled.
