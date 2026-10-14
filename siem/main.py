#!/usr/bin/env python3
"""Mini-SIEM command line.

  python main.py generate sample_logs --events 50000
  python main.py analyze sample_logs/*.log --workers 4 --html report.html
  python main.py bench sample_logs/*.log
"""
import argparse
import sys

from siem.engine import analyze
from siem.generator import generate
from siem.report import to_html, to_json, to_text


def main(argv=None):
    ap = argparse.ArgumentParser(description="Security Incident Correlation Engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="create synthetic logs with injected attacks")
    g.add_argument("outdir")
    g.add_argument("--events", type=int, default=20000, help="benign events")
    g.add_argument("--seed", type=int, default=7)

    a = sub.add_parser("analyze", help="correlate logs and print incidents")
    a.add_argument("logs", nargs="+")
    a.add_argument("--workers", type=int, default=None)
    a.add_argument("--min-chunk", type=int, default=256 * 1024, help="min bytes per chunk")
    a.add_argument("--json", metavar="FILE")
    a.add_argument("--html", metavar="FILE")

    b = sub.add_parser("bench", help="compare 1..N workers")
    b.add_argument("logs", nargs="+")
    b.add_argument("--max-workers", type=int, default=4)
    b.add_argument("--min-chunk", type=int, default=256 * 1024)

    args = ap.parse_args(argv)
    if args.cmd == "generate":
        t = generate(args.outdir, args.events, args.seed)
        print(f"wrote logs to {args.outdir}/ ({t['events']:,} events); see ground_truth.json")
    elif args.cmd == "analyze":
        res = analyze(args.logs, args.workers, min_chunk=args.min_chunk)
        print(to_text(res))
        if args.json:
            open(args.json, "w").write(to_json(res))
        if args.html:
            open(args.html, "w").write(to_html(res))
    else:
        print(f"{'workers':>8} {'parse':>8} {'merge':>8} {'detect':>8} {'total':>8}")
        w = 1
        while w <= args.max_workers:
            r = analyze(args.logs, w, min_chunk=args.min_chunk)
            t = r.timings
            print(f"{w:>8} {t['parse']:8.3f} {t['merge']:8.3f} {t['detect']:8.3f} {t['total']:8.3f}")
            w *= 2


if __name__ == "__main__":
    sys.exit(main())
