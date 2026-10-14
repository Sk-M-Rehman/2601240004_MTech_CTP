"""Log parsers: raw text lines -> normalized Events.

Four formats are supported (auto-detected from the first line of a file):
  auth      ISO-ts host proc[pid]: message          (sshd / sudo / useradd)
  web       Apache/nginx "combined" access log
  firewall  ISO-ts host ACTION SRC=.. DST=.. PROTO=.. DPT=..
  app       JSON lines {"ts":..,"host":..,"event":..,...}

Parsing is chunk-oriented so that byte ranges of a file can be handled by
independent worker processes (see `parse_chunk`).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Optional

from .models import Event

# ---------------------------------------------------------------- patterns
_AUTH = re.compile(
    r"^(?P<ts>\S+)\s+(?P<host>\S+)\s+(?P<proc>[\w\-/]+)(?:\[\d+\])?:\s+(?P<msg>.*)$")
_SSH_FAIL = re.compile(
    r"Failed (?:password|publickey) for (?:invalid user )?(?P<user>\S+) "
    r"from (?P<ip>\d{1,3}(?:\.\d{1,3}){3})")
_SSH_OK = re.compile(
    r"Accepted (?:password|publickey) for (?P<user>\S+) "
    r"from (?P<ip>\d{1,3}(?:\.\d{1,3}){3})")
_SUDO = re.compile(r"^(?P<user>\S+)\s*:.*USER=root\s*;\s*COMMAND=(?P<cmd>.*)$")
_USERADD = re.compile(r"new user: name=(?P<name>[\w\-]+).*?by=(?P<by>[\w\-]+)")

_WEB = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>\S+)[^"]*" '
    r'(?P<status>\d{3}) (?P<bytes>\d+|-)(?: "[^"]*" "(?P<ua>[^"]*)")?')

_FW = re.compile(
    r"^(?P<ts>\S+)\s+(?P<host>\S+)\s+(?P<act>DROP|ACCEPT|ALLOW|DENY)\s+"
    r"SRC=(?P<src>\S+)\s+DST=(?P<dst>\S+)\s+PROTO=(?P<proto>\S+)\s+DPT=(?P<dpt>\d+)")


def _iso(ts: str) -> float:
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


# ------------------------------------------------------------ line parsers
def parse_auth(line: str) -> Optional[Event]:
    m = _AUTH.match(line)
    if not m:
        return None
    ts, host, proc, msg = m["ts"], m["host"], m["proc"], m["msg"]
    t = _iso(ts)
    if proc.startswith("sshd"):
        f = _SSH_FAIL.search(msg)
        if f:
            return Event(t, "auth", host, "auth_fail", ip=f["ip"], user=f["user"],
                         detail="ssh failed login")
        o = _SSH_OK.search(msg)
        if o:
            return Event(t, "auth", host, "auth_ok", ip=o["ip"], user=o["user"],
                         detail="ssh login")
    elif proc == "sudo":
        s = _SUDO.match(msg)
        if s:
            return Event(t, "auth", host, "priv_esc", user=s["user"],
                         detail="sudo " + s["cmd"].strip())
    elif proc == "useradd":
        u = _USERADD.search(msg)
        if u:
            return Event(t, "auth", host, "user_created", user=u["by"],
                         detail="created account " + u["name"])
    return None


def parse_web(line: str) -> Optional[Event]:
    m = _WEB.match(line)
    if not m:
        return None
    t = datetime.strptime(m["ts"], "%d/%b/%Y:%H:%M:%S %z").timestamp()
    nb = 0 if m["bytes"] == "-" else int(m["bytes"])
    return Event(t, "web", "web", "web_request", ip=m["ip"], path=m["path"],
                 status=int(m["status"]), nbytes=nb, detail=m["ua"] or "")


def parse_firewall(line: str) -> Optional[Event]:
    m = _FW.match(line)
    if not m:
        return None
    act = "fw_drop" if m["act"] in ("DROP", "DENY") else "fw_allow"
    return Event(_iso(m["ts"]), "firewall", m["host"], act, ip=m["src"],
                 port=int(m["dpt"]), detail=f"{m['proto']} -> {m['dst']}")


_APP_ACTIONS = {"login_failed": "auth_fail", "login_ok": "auth_ok",
                "file_download": "download", "admin_action": "priv_esc"}


def parse_app(line: str) -> Optional[Event]:
    try:
        d = json.loads(line)
        action = _APP_ACTIONS.get(d["event"])
        if action is None:
            return None
        return Event(_iso(d["ts"]), "app", d.get("host", "app"), action,
                     ip=d.get("ip"), user=d.get("user"), nbytes=int(d.get("bytes", 0)),
                     path=d.get("resource", ""), detail=d["event"])
    except (ValueError, KeyError, TypeError):
        return None


PARSERS = {"auth": parse_auth, "web": parse_web,
           "firewall": parse_firewall, "app": parse_app}


def detect_format(path: str) -> str:
    """Sniff the log format from the first non-empty line."""
    with open(path, "r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("{"):
                return "app"
            if _FW.match(line):
                return "firewall"
            if _WEB.match(line):
                return "web"
            if _AUTH.match(line):
                return "auth"
            break
    raise ValueError(f"cannot detect log format of {path}")


# ------------------------------------------------------------- chunk worker
def parse_chunk(task: tuple) -> tuple:
    """Parse the lines that *start* inside byte range [start, end) of `path`.

    Returns (sorted_events, malformed_line_count). Runs in a worker process.
    """
    path, fmt, start, end, fid = task
    parse = PARSERS[fmt]
    events, bad = [], 0
    with open(path, "rb") as f:
        if start > 0:
            f.seek(start - 1)
            f.readline()          # skip partial line owned by the previous chunk
        else:
            f.seek(0)
        while True:
            pos = f.tell()
            if pos >= end:
                break
            raw = f.readline()
            if not raw:
                break
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            if not line.strip():
                continue
            ev = parse(line)
            if ev is None:
                bad += 1
            else:
                ev.fid, ev.off = fid, pos
                events.append(ev)
    events.sort(key=lambda e: e.ts)
    return events, bad
