"""Synthetic multi-source log generator with injected attack scenarios.

Writes auth.log, access.log, firewall.log, app.log and ground_truth.json.
Benign traffic is random noise (including a few legitimate failed logins, to
exercise false-positive resistance); attacks are layered on top.
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta, timezone

USERS = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]
HOSTS = ["web01", "db01", "app01"]
PATHS = ["/", "/index.html", "/login", "/api/items", "/api/orders", "/static/app.js",
         "/static/site.css", "/about", "/contact", "/api/profile"]
UA = "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0"

# scenario IPs (TEST-NET ranges, safe to publish)
FULL_CHAIN = "203.0.113.50"     # scan -> bruteforce -> login -> sudo -> useradd -> exfil
SPRAYER = "198.51.100.7"        # spray, no success
WEB_ATTACKER = "192.0.2.99"     # SQLi / traversal / scanner
CLUMSY_USER = "10.0.0.42"       # benign: legit user fat-fingering password


def _iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _web(t, ip, path, status=200, nbytes=512, ua=UA):
    stamp = datetime.fromtimestamp(t, timezone.utc).strftime("%d/%b/%Y:%H:%M:%S +0000")
    return t, "web", f'{ip} - - [{stamp}] "GET {path} HTTP/1.1" {status} {nbytes} "-" "{ua}"'


def generate(outdir: str, n_benign: int = 20000, seed: int = 7) -> dict:
    rnd = random.Random(seed)
    os.makedirs(outdir, exist_ok=True)
    base = datetime(2026, 10, 5, 0, 0, 0, tzinfo=timezone.utc).timestamp()
    day = 86400
    lines = []                                   # (ts, source, text)

    # ---- benign background noise
    for _ in range(n_benign):
        t = base + rnd.random() * day
        kind = rnd.random()
        ip = f"10.0.{rnd.randint(0, 5)}.{rnd.randint(2, 250)}"
        if kind < 0.55:
            lines.append(_web(t, ip, rnd.choice(PATHS), rnd.choice([200] * 9 + [304, 404]),
                              rnd.randint(200, 9000)))
        elif kind < 0.75:
            lines.append((t, "firewall", f"{_iso(t)} fw01 ACCEPT SRC={ip} DST=10.0.9.{rnd.randint(2, 9)} "
                                         f"PROTO=TCP DPT={rnd.choice([80, 443, 22, 5432])}"))
        elif kind < 0.90:
            u = rnd.choice(USERS)
            lines.append((t, "auth", f"{_iso(t)} {rnd.choice(HOSTS)} sshd[{rnd.randint(1000, 9999)}]: "
                                     f"Accepted publickey for {u} from {ip} port {rnd.randint(30000, 60000)} ssh2"))
        else:
            u = rnd.choice(USERS)
            lines.append((t, "app", json.dumps({"ts": _iso(t), "host": "app01", "event": "login_ok",
                                                "user": u, "ip": ip})))
    # benign: a couple of normal downloads and sudo
    for k in range(5):
        t = base + 3600 * (k + 2)
        lines.append((t, "app", json.dumps({"ts": _iso(t), "host": "app01", "event": "file_download",
                                            "user": "alice", "ip": "10.0.1.10", "bytes": 2_000_000,
                                            "resource": "report.pdf"})))
    t = base + 40000
    lines.append((t, "auth", f"{_iso(t)} web01 sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/usr/bin/apt update"))

    # ---- benign-but-noisy: legitimate user mistypes password 3 times, then logs in
    t0 = base + 30000
    for k in range(3):
        lines.append((t0 + k * 5, "auth", f"{_iso(t0 + k * 5)} web01 sshd[2001]: Failed password for bob "
                                          f"from {CLUMSY_USER} port 50000 ssh2"))
    lines.append((t0 + 20, "auth", f"{_iso(t0 + 20)} web01 sshd[2001]: Accepted password for bob "
                                   f"from {CLUMSY_USER} port 50000 ssh2"))

    # ---- scenario A: full kill chain from FULL_CHAIN
    t0 = base + 50000
    for k in range(60):                                          # port scan
        t = t0 + k * 0.5
        lines.append((t, "firewall", f"{_iso(t)} fw01 DROP SRC={FULL_CHAIN} DST=10.0.9.5 PROTO=TCP DPT={1000 + k * 7}"))
    t0 += 300
    for k in range(40):                                          # ssh brute force on root/admin
        t = t0 + k * 1.5
        u = rnd.choice(["root", "admin", "ubuntu"])
        lines.append((t, "auth", f"{_iso(t)} web01 sshd[3100]: Failed password for invalid user {u} "
                                 f"from {FULL_CHAIN} port {40000 + k} ssh2"))
    t = t0 + 75
    lines.append((t, "auth", f"{_iso(t)} web01 sshd[3101]: Accepted password for admin from {FULL_CHAIN} port 41111 ssh2"))
    lines.append((t + 40, "auth", f"{_iso(t + 40)} web01 sudo: admin : TTY=pts/1 ; PWD=/home/admin ; USER=root ; COMMAND=/bin/bash"))
    lines.append((t + 90, "auth", f"{_iso(t + 90)} web01 useradd[3300]: new user: name=svc_backup, UID=1099, by=admin"))
    for k in range(6):
        tt = t + 200 + k * 20
        lines.append((tt, "app", json.dumps({"ts": _iso(tt), "host": "app01", "event": "file_download",
                                             "user": "admin", "ip": FULL_CHAIN, "bytes": 25_000_000,
                                             "resource": f"customers_{k}.csv"})))

    # ---- scenario B: password spray, never succeeds
    t0 = base + 20000
    for k in range(30):
        t = t0 + k * 6
        lines.append((t, "auth", f"{_iso(t)} db01 sshd[4000]: Failed password for {USERS[k % len(USERS)]} "
                                 f"from {SPRAYER} port {50000 + k} ssh2"))

    # ---- scenario C: web attacks
    t0 = base + 70000
    probes = ["/search?q=1' OR 1=1--", "/item?id=1 UNION SELECT user,pass FROM users",
              "/download?file=../../../../etc/passwd", "/page?x=%3Cscript%3Ealert(1)%3C/script%3E",
              "/.env", "/phpmyadmin/", "/search?q=1;DROP TABLE users", "/item?id=sleep(5)"]
    for k, p in enumerate(probes * 2):
        t = t0 + k * 4
        lines.append(_web(t, WEB_ATTACKER, p, rnd.choice([403, 404, 500]), 300,
                          "sqlmap/1.7" if k % 3 == 0 else UA))

    # ---- write files (each source kept in its own file, individually time-sorted
    #      except for a bit of out-of-order jitter to make merging meaningful)
    files = {"auth": "auth.log", "web": "access.log", "firewall": "firewall.log", "app": "app.log"}
    for src, fn in files.items():
        rows = sorted((r for r in lines if r[1] == src), key=lambda r: r[0])
        for i in range(0, len(rows) - 3, 50):                   # local shuffle = clock skew
            blk = rows[i:i + 4]; rnd.shuffle(blk); rows[i:i + 4] = blk
        with open(os.path.join(outdir, fn), "w") as f:
            f.write("\n".join(r[2] for r in rows) + "\n")

    truth = {"incidents": {FULL_CHAIN: "CRITICAL", SPRAYER: "MEDIUM+", WEB_ATTACKER: "MEDIUM+"},
             "benign_ips": [CLUMSY_USER], "events": len(lines)}
    with open(os.path.join(outdir, "ground_truth.json"), "w") as f:
        json.dump(truth, f, indent=2)
    return truth
