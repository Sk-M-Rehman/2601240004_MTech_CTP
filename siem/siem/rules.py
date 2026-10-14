"""Detection rules (pattern matching + sliding-window correlation).

Every rule receives the *time-sorted events of a single source IP* (gathered
from all log sources) plus the alerts raised so far for that IP, so rules can
build on each other, e.g. "brute force -> successful login -> sudo".
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import unquote

from .models import Alert, Event


@dataclass
class Config:
    bf_threshold: int = 8          # failed logins ...
    bf_window: int = 60            # ... within N seconds
    spray_users: int = 5           # distinct usernames ...
    spray_window: int = 300        # ... within N seconds
    scan_ports: int = 10           # distinct ports dropped ...
    scan_window: int = 60
    web_hits: int = 4              # malicious web requests ...
    web_window: int = 300
    notfound_hits: int = 30        # 404s (forced browsing) ...
    notfound_window: int = 60
    compromise_lookback: int = 900  # login success this long after an attack alert
    post_window: int = 3600        # post-compromise activity window
    exfil_bytes: int = 50_000_000
    session_ttl: int = 6 * 3600    # ip<->user session inference lifetime


# ---------------------------------------------------------------- helpers
def burst_windows(times: list, window: float, threshold: int) -> list:
    """Return merged index ranges [i, j] where some span of `window` seconds
    holds >= threshold events. Two-pointer sweep, O(n)."""
    ranges, i = [], 0
    for j in range(len(times)):
        while times[j] - times[i] > window:
            i += 1
        if j - i + 1 >= threshold:
            if ranges and i <= ranges[-1][1]:
                ranges[-1][1] = j
            else:
                ranges.append([i, j])
    return ranges


def _alert(rule, title, stage, mitre, score, ip, evs, user=None):
    srcs = sorted({e.source for e in evs})
    users = sorted({e.user for e in evs if e.user})
    hosts = sorted({e.host for e in evs})
    return Alert(rule=rule, title=title, stage=stage, mitre=mitre, score=score,
                 ip=ip, user=user or (users[0] if len(users) == 1 else None),
                 host=",".join(hosts), start=evs[0].ts, end=evs[-1].ts,
                 count=len(evs), sources=srcs, evidence=[(e.fid, e.off) for e in evs[:3]])


# ------------------------------------------------------------------ rules
def rule_port_scan(ip, evs, cfg, prior):
    drops = [e for e in evs if e.action == "fw_drop" and e.port is not None]
    out = []
    ts = [e.ts for e in drops]
    # sliding window on distinct ports
    from collections import Counter
    cnt, lo, cur = Counter(), 0, None
    for hi, e in enumerate(drops):
        cnt[e.port] += 1
        while ts[hi] - ts[lo] > cfg.scan_window:
            cnt[drops[lo].port] -= 1
            if not cnt[drops[lo].port]:
                del cnt[drops[lo].port]
            lo += 1
        if len(cnt) >= cfg.scan_ports:
            if cur and lo <= cur[1]:
                cur[1] = hi
            else:
                cur = [lo, hi]; out.append(cur)
    return [_alert("port_scan", "Port scan (firewall drops across many ports)",
                   "Reconnaissance", "T1046", 35, ip, drops[a:b + 1])
            for a, b in out]


def rule_ssh_bruteforce(ip, evs, cfg, prior):
    fails = [e for e in evs if e.action == "auth_fail"]
    return [_alert("bruteforce", "Brute-force login attempts", "Credential Access",
                   "T1110.001", 60, ip, fails[a:b + 1])
            for a, b in burst_windows([e.ts for e in fails], cfg.bf_window, cfg.bf_threshold)]


def rule_password_spray(ip, evs, cfg, prior):
    from collections import Counter
    fails = [e for e in evs if e.action == "auth_fail" and e.user]
    out, cnt, lo, cur = [], Counter(), 0, None
    for hi, e in enumerate(fails):
        cnt[e.user] += 1
        while e.ts - fails[lo].ts > cfg.spray_window:
            cnt[fails[lo].user] -= 1
            if not cnt[fails[lo].user]:
                del cnt[fails[lo].user]
            lo += 1
        if len(cnt) >= cfg.spray_users:
            if cur and lo <= cur[1]:
                cur[1] = hi
            else:
                cur = [lo, hi]; out.append(cur)
    return [_alert("spray", "Password spraying (many accounts, one source)",
                   "Credential Access", "T1110.003", 60, ip, fails[a:b + 1])
            for a, b in out]


_WEB_PATTERNS = {
    "sqli": re.compile(r"(?i)(union\s+select|\bor\s+1=1|'--|sleep\(\d+\)|information_schema|;\s*drop\s+table)"),
    "traversal": re.compile(r"(?i)(\.\./|\.\.\\|/etc/passwd|/windows/win\.ini)"),
    "xss": re.compile(r"(?i)(<script|onerror\s*=|javascript:)"),
    "scanner_ua": re.compile(r"(?i)(sqlmap|nikto|nmap|masscan|dirbuster|gobuster)"),
    "sensitive": re.compile(r"(?i)(/\.env|/\.git/|/phpmyadmin|/wp-login|/server-status)"),
}


def classify_web(e: Event):
    target = unquote(unquote(e.path)) + " " + e.detail
    return [name for name, rx in _WEB_PATTERNS.items() if rx.search(target)]


def rule_web_attack(ip, evs, cfg, prior):
    hits = [e for e in evs if e.action == "web_request" and classify_web(e)]
    out = [_alert("web_attack", "Web attack signatures (SQLi/traversal/XSS/scanner)",
                  "Initial Access", "T1190", 55, ip, hits[a:b + 1])
           for a, b in burst_windows([e.ts for e in hits], cfg.web_window, cfg.web_hits)]
    nf = [e for e in evs if e.action == "web_request" and e.status == 404]
    out += [_alert("forced_browsing", "Forced browsing (burst of 404s)", "Reconnaissance",
                   "T1595.003", 30, ip, nf[a:b + 1])
            for a, b in burst_windows([e.ts for e in nf], cfg.notfound_window, cfg.notfound_hits)]
    return out


def rule_credential_compromise(ip, evs, cfg, prior):
    """Successful login shortly after (or during) brute force / spraying."""
    attacks = [a for a in prior if a.rule in ("bruteforce", "spray")]
    if not attacks:
        return []
    out, seen = [], set()
    for e in evs:
        if e.action != "auth_ok" or (e.user, e.host) in seen:
            continue
        for a in attacks:
            if a.start <= e.ts <= a.end + cfg.compromise_lookback:
                seen.add((e.user, e.host))
                al = _alert("compromise", "Successful login after credential attack",
                            "Initial Access", "T1078", 85, ip, [e], user=e.user)
                al.evidence = [(e.fid, e.off)] + a.evidence[:2]
                al.sources = sorted(set(al.sources) | set(a.sources))
                out.append(al)
                break
    return out


def rule_post_compromise(ip, evs, cfg, prior):
    out = []
    for comp in (a for a in prior if a.rule == "compromise"):
        window = [e for e in evs if comp.end <= e.ts <= comp.end + cfg.post_window]
        esc = [e for e in window if e.action == "priv_esc"]
        if esc:
            out.append(_alert("post_compromise_priv", "Privilege escalation after compromise",
                              "Privilege Escalation", "T1548", 80, ip, esc, user=comp.user))
        persist = [e for e in window if e.action == "user_created"]
        if persist:
            out.append(_alert("post_compromise_persist", "Persistence: account created after compromise",
                              "Persistence", "T1136", 80, ip, persist, user=comp.user))
        dl = [e for e in window if e.action == "download"]
        if dl and sum(e.nbytes for e in dl) >= cfg.exfil_bytes:
            out.append(_alert("exfil", "Large data download after compromise",
                              "Exfiltration", "T1041", 90, ip, dl, user=comp.user))
    return out


# Order matters: later rules consume earlier alerts via `prior`.
RULES = [rule_port_scan, rule_ssh_bruteforce, rule_password_spray, rule_web_attack,
         rule_credential_compromise, rule_post_compromise]


def run_rules(ip: str, evs: list, cfg: Config) -> list:
    alerts: list = []
    for rule in RULES:
        alerts.extend(rule(ip, evs, cfg, alerts))
    return alerts
