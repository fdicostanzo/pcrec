#!/usr/bin/env python3
"""tests/compound/check_admitted.py -- [COMPOUND] the admitted population, by
ID (docs/design/compound.md §E.3 G6, K35).

  check_admitted.py PCREC TREE MANIFEST [--jobs N]

Compiles every DISTINCT corpus pattern (`--list-source` over TREE/tests,
emit_sweep's own enumeration) under `byte` and `-e utf8`, `-p rx --features
all`, reads each artifact's `<PREFIX>_COMPOUND` stamp, and holds the set of
(file, pattern, arm, row) the build admits to MANIFEST
(tests/compound/admitted.tsv, written by landing_census.py at B4 against a
reference build), in BOTH directions: a pattern that stops being admitted
and one that starts are both failures, so a change that moves the admission
says so by ID. Every artifact must carry the stamp. Exit 1 on a difference.
"""
import concurrent.futures as cf, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
import emit_sweep  # noqa: E402

STAMP = re.compile(rb'^#define RX_COMPOUND "([^"]*)"$', re.M)


def stamp_of(job):
    pcrec, tmp, rel, pat, arm = job
    d = tempfile.mkdtemp(dir=tmp)
    r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "-o", os.path.join(d, "rx.c")] +
                       arm + ["--pattern", pat], capture_output=True, timeout=300)
    st = None
    if r.returncode == 0:
        m = STAMP.search(open(os.path.join(d, "rx.c"), "rb").read())
        st = m.group(1).decode() if m else "MISSING"
    shutil.rmtree(d)
    return rel, pat, " ".join(arm) or "byte", st


def main():
    pcrec, tree, manifest = sys.argv[1:4]
    jobs_n = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    want = set()
    for ln in open(manifest, encoding="ascii"):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        want.add((f[0], f[1], f[2], f[3]))
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
    jobs, seen = [], set()
    for rel, _kind, pat in emit_sweep.enumerate_corpus(pcrec, tree, 120):
        if not pat or b"\x00" in pat or pat in seen:
            continue
        seen.add(pat)
        for arm in ([], ["-e", "utf8"]):
            jobs.append((pcrec, tmp, rel, pat, arm))
    got, missing, compiled = set(), [], 0
    with cf.ThreadPoolExecutor(jobs_n) as ex:
        for rel, pat, arm, st in ex.map(stamp_of, jobs):
            if st is None:
                continue
            compiled += 1
            if st == "MISSING":
                missing.append("%s %s" % (rel, arm))
            elif st != "none":
                got.add((rel, pat.hex(), arm, st))
    shutil.rmtree(tmp)
    fails = ["no <PREFIX>_COMPOUND stamp: " + m for m in missing[:10]]
    for x in sorted(want - got):
        fails.append("no longer admitted: %s %s [%s] %s" % (x[0], bytes.fromhex(x[1])[:80], x[2], x[3]))
    for x in sorted(got - want):
        fails.append("newly admitted: %s %s [%s] %s" % (x[0], bytes.fromhex(x[1])[:80], x[2], x[3]))
    for f in fails[:40]:
        print("FAIL: " + f)
    floor_ok = compiled >= 8000 and len(got) >= 40
    if not floor_ok:
        print("FAIL: below the population floor (8000 compiled artifacts, 40 admitted)")
    ok = not fails and floor_ok
    print("%s: admitted population: %d distinct patterns x 2 arms, %d compiled, %d admitted "
          "(manifest %d); %d failures" % ("PASS" if ok else "FAIL", len(seen), compiled,
                                          len(got), len(want), len(fails)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
