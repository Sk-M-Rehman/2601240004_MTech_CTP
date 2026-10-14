"""Core data structures shared by every stage of the pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class Event:
    """A normalized log event, independent of the originating log format."""
    ts: float                      # epoch seconds (UTC)
    source: str                    # auth | web | firewall | app
    host: str
    action: str                    # auth_fail, auth_ok, priv_esc, user_created,
                                   # web_request, fw_drop, fw_allow, download
    ip: Optional[str] = None
    user: Optional[str] = None
    port: Optional[int] = None
    path: str = ""
    status: int = 0
    nbytes: int = 0
    detail: str = ""
    fid: int = -1                  # index of originating log file
    off: int = 0                   # byte offset of the line (raw text fetched lazily)
    inferred_ip: bool = False      # ip filled in by session enrichment


@dataclass(slots=True)
class Alert:
    """A single rule match against one entity (usually one source IP)."""
    rule: str
    title: str
    stage: str                     # kill-chain stage
    mitre: str
    score: int                     # 0-100 base confidence/impact
    ip: Optional[str]
    user: Optional[str]
    host: str
    start: float
    end: float
    count: int
    sources: list = field(default_factory=list)
    evidence: list = field(default_factory=list)   # (fid, offset) refs -> raw lines


@dataclass(slots=True)
class Incident:
    id: str
    ip: Optional[str]
    start: float
    end: float
    score: int
    severity: str
    stages: list
    sources: list
    users: list
    hosts: list
    alerts: list                   # list[Alert]
    summary: str = ""
