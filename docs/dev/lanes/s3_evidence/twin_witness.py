#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/twin_witness.py -- the twin rule's (census.facts_judge) own
witnesses, lane s3 trailing checks: the rule must go red BOTH WAYS, so each direction is
planted on real compiles and the judgment read back.

    python3 -I twin_witness.py --base BIN --new BIN

BASE is main c3ea619c3's pcrec, NEW the S3 build (census.py's pair). Rows:
  genuine        `abc` (byte twin becomes cover): the real listings judge clean
  unmoved-ctl    `(?:x)+y` (neither twin moves): the real listings judge clean
  rows-no-twin   the same with NEW's byte RX_ENGINE row edited: rows moved, twin stamps did
                 not -> red
  twin-no-rows   `abc` with NEW's listing replaced by BASE's: twin stamps moved, rows did
                 not -> red
  header-moved   `abc` with a non-row line edited -> red
  refused        `\\x{3b1}` (byte refuses): counted refused, no problem
Trailer `== twin witness COMPLETE: rows=6 ok=N`; exit 0 iff every row reads as planted.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402

FACTS = ["--features", "all", "--emit-facts=byte,utf8"]


def listing(b, pat):
    return census.run([b] + FACTS + ["--pattern", pat])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    a = ap.parse_args()
    ok = 0

    def judge(name, pat, b, n, want):
        nonlocal ok
        problems, twins, _ = census.facts_judge(a.base, a.new, [], pat, b, n, census.norm)
        got = "refused" if twins is None and not problems else "red" if problems else "clean"
        ok += got == want
        print("%-13s %-10s want %-7s got %-7s %s" % (name, pat, want, got, "; ".join(problems)[:140]))

    b, n = listing(a.base, "abc"), listing(a.new, "abc")
    judge("genuine", "abc", b, n, "clean")
    judge("twin-no-rows", "abc", b, (n[0], b[1], n[2]), "red")
    judge("header-moved", "abc", b, (n[0], n[1].replace(b"#section facts", b"#section factz", 1), n[2]), "red")
    p = "(?:x)+y"
    b, n = listing(a.base, p), listing(a.new, p)
    judge("unmoved-ctl", p, b, n, "clean")
    judge("rows-no-twin", p, b, (n[0], n[1].replace(b'byte\tRX_ENGINE\t"', b'byte\tRX_ENGINE\t"x', 1), n[2]), "red")
    p = "\\x{3b1}"
    judge("refused", p, listing(a.base, p), listing(a.new, p), "refused")
    print("== twin witness COMPLETE: rows=6 ok=%d" % ok)
    return 0 if ok == 6 else 1


if __name__ == "__main__":
    sys.exit(main())
