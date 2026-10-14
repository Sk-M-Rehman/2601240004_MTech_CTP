import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from siem import generator
from siem.engine import analyze
from siem.merge import merge_sort, merge_two, tree_merge
from siem.models import Event
from siem.parsers import parse_auth, parse_firewall, parse_web, parse_app
from siem.rules import burst_windows


def ev(ts):
    return Event(ts, "auth", "h", "auth_fail")


class MergeTests(unittest.TestCase):
    def test_tree_merge_matches_sorted(self):
        rnd = random.Random(1)
        runs = [sorted((ev(rnd.random()) for _ in range(rnd.randint(0, 50))), key=lambda e: e.ts)
                for _ in range(13)]
        flat = sorted((e for r in runs for e in r), key=lambda e: e.ts)
        self.assertEqual([e.ts for e in tree_merge(runs)], [e.ts for e in flat])

    def test_merge_sort_and_stability(self):
        a, b = [ev(1), ev(3)], [ev(1), ev(2)]
        m = merge_two(a, b)
        self.assertEqual([e.ts for e in m], [1, 1, 2, 3])
        self.assertIs(m[0], a[0])                      # stable: left first
        items = [ev(random.random()) for _ in range(500)]
        self.assertEqual([e.ts for e in merge_sort(items)], sorted(e.ts for e in items))


class ParserTests(unittest.TestCase):
    def test_formats(self):
        e = parse_auth("2026-10-05T10:00:00 web01 sshd[1]: Failed password for invalid user root from 1.2.3.4 port 22 ssh2")
        self.assertEqual((e.action, e.user, e.ip), ("auth_fail", "root", "1.2.3.4"))
        e = parse_auth("2026-10-05T10:00:00 web01 sudo: bob : TTY=pts/0 ; PWD=/ ; USER=root ; COMMAND=/bin/sh")
        self.assertEqual((e.action, e.user), ("priv_esc", "bob"))
        e = parse_firewall("2026-10-05T10:00:00 fw01 DROP SRC=1.2.3.4 DST=10.0.0.1 PROTO=TCP DPT=22")
        self.assertEqual((e.action, e.port), ("fw_drop", 22))
        e = parse_web('1.2.3.4 - - [05/Oct/2026:10:00:00 +0000] "GET /a?b=1 HTTP/1.1" 404 12 "-" "curl"')
        self.assertEqual((e.status, e.path), (404, "/a?b=1"))
        e = parse_app('{"ts":"2026-10-05T10:00:00","event":"file_download","user":"u","ip":"1.1.1.1","bytes":5}')
        self.assertEqual((e.action, e.nbytes), ("download", 5))
        self.assertIsNone(parse_auth("garbage"))

    def test_burst_windows(self):
        self.assertEqual(burst_windows([0, 1, 2, 100, 200], 10, 3), [[0, 2]])
        self.assertEqual(burst_windows([0, 50, 100], 10, 2), [])


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        generator.generate(cls.dir, n_benign=4000, seed=3)
        cls.logs = [os.path.join(cls.dir, f) for f in
                    ("auth.log", "access.log", "firewall.log", "app.log")]

    def run_with(self, workers):
        return analyze(self.logs, workers=workers, min_chunk=8 * 1024)

    def test_detects_attacks_not_benign(self):
        r = self.run_with(2)
        by_ip = {i.ip: i for i in r.incidents}
        self.assertEqual(set(by_ip), {generator.FULL_CHAIN, generator.SPRAYER, generator.WEB_ATTACKER})
        top = r.incidents[0]
        self.assertEqual((top.ip, top.severity), (generator.FULL_CHAIN, "CRITICAL"))
        self.assertGreaterEqual(len(top.sources), 3)    # firewall + auth + app
        for stage in ("Reconnaissance", "Credential Access", "Initial Access",
                      "Privilege Escalation", "Exfiltration"):
            self.assertIn(stage, top.stages)
        self.assertNotIn(generator.CLUMSY_USER, by_ip)
        self.assertEqual(r.malformed, 0)

    def test_parallel_equals_serial(self):
        sig = lambda r: [(i.ip, i.score, [(a.rule, a.count) for a in sorted(i.alerts, key=lambda a: (a.start, a.rule))])
                         for i in r.incidents]
        a, b = self.run_with(1), self.run_with(2)
        self.assertEqual(a.events, b.events)
        self.assertEqual(sig(a), sig(b))


if __name__ == "__main__":
    unittest.main()
