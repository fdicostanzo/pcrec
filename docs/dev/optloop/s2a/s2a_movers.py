#!/usr/bin/env python3
"""[OPT-LITSCAN] S2a's MOVERS BY PREDICATE, over s1_identity.py's own records.

The prediction: an artifact's emitted text moves IFF its VM program writes a
literal-run compare -- `vm_lit`'s `!memcmp(subject + scan_position, "..", L)`
or the island run arm's `!memcmp(subject + scan_position + d, "..", L)`.
Nothing else in S2a changes a byte (the abi digit is normalized by the
identity gate). So, per compiled record: `changed` must carry the compare in
the NEW artifact, and `identical` must not. A record the base REFUSED and the
new side compiles (`refusal-mismatch`) is listed, not scored: it is an
acceptance mover (smaller emitted code under a size cap), answer-checked
separately (docs/dev/lanes/s2a_report.md).

  NEW=<pcrec> JSON=<s1_identity.json> python3 s2a_movers.py
Prints the four cells of the biconditional and every record off its diagonal;
exits 1 if any is off it, or if either population is empty (K35).
"""
import json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

NEW, JSON = os.environ["NEW"], os.environ["JSON"]
PATDIR = "/Users/fdicostanzo/pcrec-bench/bench/capability/patterns"
CFG = {"auto-caps": ["--features", "all"],
       "auto-nocaps": ["--features", "all", "--no-captures"],
       "vm-caps": ["--features", "all", "--engine=vm"],
       "vm-nocaps": ["--features", "all", "--engine=vm", "--no-captures"],
       "auto": ["--features", "all"], "vm": ["--features", "all", "--engine=vm"]}
RUN = re.compile(rb'!memcmp\(subject \+ scan_position(?: \+ \d+)?, "')


def one(r, d):
    pat = r["key"] if r["pop"] == "corpus" else \
        open(os.path.join(PATDIR, r["key"] + ".rx"), "rb").read().rstrip(b"\n") \
        .decode("utf-8", "surrogateescape")
    fd, path = tempfile.mkstemp(suffix=".c", dir=d)
    os.close(fd)
    p = subprocess.run([NEW, "-p", "rx", "-o", path, "--pattern", pat] + CFG[r["cfg"]],
                       capture_output=True, timeout=600)
    has = p.returncode == 0 and bool(RUN.search(open(path, "rb").read()))
    os.unlink(path)
    return r, has


def main():
    recs = [r for r in json.load(open(JSON)) if r["identity"] in ("changed", "identical")]
    mism = [r for r in json.load(open(JSON)) if r["identity"] == "refusal-mismatch"]
    cells = {(i, h): [] for i in ("changed", "identical") for h in (True, False)}
    with tempfile.TemporaryDirectory() as d, ThreadPoolExecutor(8) as ex:
        for r, has in ex.map(lambda r: one(r, d), recs):
            cells[(r["identity"], has)].append(r)
    for (i, h), rs in cells.items():
        print(f"{i:9s} x {'run compare' if h else 'no run compare':15s}: {len(rs)}")
    off = cells[("changed", False)] + cells[("identical", True)]
    for r in off:
        print(f"  OFF-DIAGONAL {r['identity']} {r['pop']} {r['cfg']} {r['key'][:70]!r}")
    for r in mism:
        print(f"  ACCEPTANCE-MOVER {r['pop']} {r['cfg']} {r['key'][:70]!r}")
    if not cells[("changed", True)] or not cells[("identical", False)]:
        print("FAIL: an empty population")
        sys.exit(1)
    sys.exit(1 if off else 0)


if __name__ == "__main__":
    main()
