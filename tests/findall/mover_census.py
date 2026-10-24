#!/usr/bin/env python3
# tests/findall/mover_census.py -- [FINDALL-NEXT] I1's MOVER CENSUS (findall_iter.md
# §6.4, §6.7, IT15): what the iterator's abi event moved that a caller or a size
# decision can see. Every distinct `pattern` line under TREE/tests is compiled by
# the parent compiler OLD and the iterator's NEW, on the default engine and under
# --engine=vm, and three things are compared per compile:
#   - the outcome: refused or not, and the refusal's first stderr line;
#   - the engine stamps <PREFIX>_ENGINE and <PREFIX>_ENGINE_SEL;
#   - the COUNTED size, the "N bytes of emitted C source (M of code)" a length
#     decision reads (--warn-emit-bytes=1 prints it; a compound prints its
#     parts' lines too, all compared).
# Every byte of the iterator is scaffold, excluded from the counted size, except
# the DFA notempty retry machine (a machine, counted like one). So a counted-size
# move is EXPLAINED where the new artifact stamps ITER_RETRY "retry" (a DFA
# artifact's retry machine; the VM's guarded matcher is scaffold); a
# compound shell may move by one byte (its `__next_pos` reference). Every other
# move, and every outcome or engine difference, is listed.
#
# usage: python3 -I mover_census.py OLD_PCREC NEW_PCREC TREE [--jobs N]
# exit 0 when no unexplained difference; 1 otherwise. Prints the tallies.
import os
import re
import subprocess
import sys
import tempfile
from multiprocessing import Pool

OLD, NEW, TREE = sys.argv[1], sys.argv[2], sys.argv[3]
JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
SIZE_RE = re.compile(rb"(\d+) bytes of emitted C source \((\d+) of code\)")


def patterns():
    out = set()
    for d, _, fs in os.walk(os.path.join(TREE, "tests")):
        if "/known_fail" in d:
            continue
        for f in fs:
            if not f.endswith(".rxt"):
                continue
            for ln in open(os.path.join(d, f), "rb"):
                if ln.startswith(b"pattern "):
                    out.add(ln[len(b"pattern "):].rstrip(b"\n"))
    return sorted(out)


def one(bin_, pat, eng, tmp):
    c = os.path.join(tmp, "o.c")
    args = [bin_, "--features", "all", "-p", "rx", "--warn-emit-bytes=1", "-o", c]
    if eng:
        args.append(eng)
    args += ["--pattern", pat]
    try:
        r = subprocess.run(args, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return ("timeout", None, None, None)
    if r.returncode != 0:
        errs = [l for l in r.stderr.split(b"\n") if b"error" in l or b"requires" in l or b"refus" in l]
        return ("refused", (errs or [b""])[0][:160], None, None)
    sizes = tuple(SIZE_RE.findall(r.stderr))
    try:
        txt = open(c, "rb").read()
    except OSError:
        txt = b""
    eng_st = tuple(re.findall(rb"^#define RX_ENGINE(?:_SEL)? (.*)$", txt, re.M))
    it = re.findall(rb'^#define RX_ITER_RETRY "([a-z-]+)"', txt, re.M)
    comp = re.findall(rb'^#define RX_COMPOUND "([a-z-]+)"', txt, re.M)
    return ("ok", sizes, eng_st, (it[0] if it else b"", comp[0] if comp else b""))


def cell(job):
    pat, eng = job
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
        a = one(OLD, pat, eng, tmp)
        b = one(NEW, pat, eng, tmp)
    if a[0] != b[0] or (a[0] == "refused" and a[1] != b[1]):
        return ("outcome", pat, eng, a[:2], b[:2])
    if a[0] != "ok":
        return ("same-refused", pat, eng, None, None)
    if a[2] != b[2]:
        return ("engine", pat, eng, a[2], b[2])
    if a[1] == b[1]:
        return ("same", pat, eng, None, None)
    retry, comp = b[3]
    if retry == b"retry":
        return ("moved-retry-root", pat, eng, a[1], b[1])
    if comp not in (b"", b"none"):
        da = [int(x[1]) for x in a[1]]
        db = [int(x[1]) for x in b[1]]
        if len(da) == len(db) and all(0 <= y - x <= 1 for x, y in zip(da, db)):
            return ("moved-compound-ref", pat, eng, a[1], b[1])
    return ("moved-other", pat, eng, a[1], b[1])


def main():
    pats = patterns()
    jobs = [(p, e) for p in pats for e in ("", "--engine=vm")]
    tally = {}
    bad = []
    with Pool(JOBS) as pool:
        for r in pool.imap_unordered(cell, jobs, chunksize=8):
            tally[r[0]] = tally.get(r[0], 0) + 1
            if r[0] in ("outcome", "engine", "moved-other"):
                bad.append(r)
    print("mover census: %d patterns, %d compiles per side" % (len(pats), len(jobs)))
    for k in sorted(tally):
        print("  %-20s %d" % (k, tally[k]))
    for r in bad[:60]:
        print("UNEXPLAINED %s [%s] %r: %r -> %r" % (r[0], r[2] or "auto", r[1], r[3], r[4]))
    if len(pats) < 1000:
        print("FAIL: the census read only %d patterns (floor 1000)" % len(pats))
        return 1
    print("mover census: %s" % ("CLEAN" if not bad else "%d UNEXPLAINED" % len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
