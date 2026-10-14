"""Render analysis results as text, JSON or a self-contained HTML page."""
from __future__ import annotations

import html
import json
from dataclasses import asdict
from datetime import datetime, timezone


def _t(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def to_text(res) -> str:
    L = [f"Mini-SIEM: {res.events:,} events from {len(res.files)} sources "
         f"({res.malformed} unparsed lines) | workers={res.workers}",
         "timings: " + "  ".join(f"{k}={v:.3f}s" for k, v in res.timings.items()),
         f"{len(res.alerts)} alerts -> {len(res.incidents)} incidents", ""]
    for i in res.incidents:
        L.append(f"[{i.severity:8}] {i.id}  score={i.score:3}  attacker={i.ip}")
        L.append(f"    window : {_t(i.start)} -> {_t(i.end)} UTC")
        L.append(f"    chain  : {' -> '.join(i.stages)}")
        L.append(f"    sources: {', '.join(i.sources)}   users: {', '.join(i.users) or '-'}"
                 f"   hosts: {', '.join(i.hosts) or '-'}")
        for a in sorted(i.alerts, key=lambda a: a.start):
            L.append(f"      * {_t(a.start)}  {a.mitre:<10} {a.title} (x{a.count})")
        L.append("")
    if not res.incidents:
        L.append("No incidents detected.")
    return "\n".join(L)


def to_json(res) -> str:
    return json.dumps({
        "events": res.events, "malformed": res.malformed, "workers": res.workers,
        "timings": res.timings,
        "incidents": [asdict(i) for i in res.incidents]}, indent=2, default=str)


_COL = {"CRITICAL": "#b71c1c", "HIGH": "#e65100", "MEDIUM": "#f9a825", "LOW": "#558b2f"}


def to_html(res) -> str:
    cards = []
    for i in res.incidents:
        rows = "".join(
            f"<tr><td>{_t(a.start)}</td><td>{html.escape(a.mitre)}</td>"
            f"<td>{html.escape(a.title)}</td><td>{a.count}</td>"
            f"<td><code>{html.escape(a.evidence[0][:140]) if a.evidence else ''}</code></td></tr>"
            for a in sorted(i.alerts, key=lambda a: a.start))
        cards.append(
            f"<section><h2><span class=b style='background:{_COL[i.severity]}'>{i.severity}</span> "
            f"{i.id} &mdash; {html.escape(str(i.ip))} <small>score {i.score}</small></h2>"
            f"<p>{html.escape(i.summary)}</p>"
            f"<table><tr><th>Time (UTC)</th><th>MITRE</th><th>Detection</th><th>#</th><th>Evidence</th></tr>"
            f"{rows}</table></section>")
    return f"""<!doctype html><meta charset=utf-8><title>Mini-SIEM report</title>
<style>body{{font:14px system-ui;margin:2rem auto;max-width:1000px;color:#222}}
section{{border:1px solid #ddd;border-radius:8px;padding:1rem;margin:1rem 0}}
.b{{color:#fff;padding:2px 8px;border-radius:4px;font-size:12px}}
table{{border-collapse:collapse;width:100%}}td,th{{border-top:1px solid #eee;padding:4px 6px;
text-align:left;vertical-align:top}}code{{font-size:11px;color:#555}}small{{color:#777}}</style>
<h1>Security Incident Report</h1>
<p>{res.events:,} events &middot; {len(res.alerts)} alerts &middot; {len(res.incidents)} incidents
&middot; {res.timings.get('total', 0):.2f}s with {res.workers} workers</p>
{''.join(cards) or '<p>No incidents detected.</p>'}"""
