#!/usr/bin/env python3
"""tests/compound/check_lever.py -- [COMPOUND] THE LEVER MOVES NOTHING ELSE
(docs/design/compound.md §A.11's exact property; sabotage row CMP-15).

  check_lever.py PCREC PCREC_HARNESS TREE [--jobs N]

Compiles every DISTINCT corpus pattern (`--list-source` over TREE/tests)
under `byte` and `-e utf8`, `-p rx --features all`, by the default build and
by the harness build under `--harness=no-compound`, and holds each pair to
the lever's two-directional property:
  - the lever stamps `"none"` exactly where the default stamps `"none"`,
    and there the two artifacts are byte-identical (the lever moves nothing
    it declines nothing on);
  - the lever stamps `"forced-off"` exactly where the default stamps a row
    name (it never marks an artifact the default ships plain).
The population of `"forced-off"` pairs must reach a floor (K35): a lever
that never fired would pass the first half on everything. Exit 1 on a
violation.
"""
import concurrent.futures as cf, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
import emit_sweep  # noqa: E402

STAMP = re.compile(rb'^#define RX_COMPOUND "([^"]*)"$', re.M)
FLOOR = 80               # pairs the default ships as a compound (97 at B4)


def one(job):
    pcrec, harness, tmp, rel, pat, arm = job
    d = tempfile.mkdtemp(dir=tmp)
    out = []
    for tag, cmd in (("a", [pcrec]), ("b", [harness, "--harness=no-compound"])):
        os.mkdir(os.path.join(d, tag))
        c = os.path.join(d, tag, "rx.c")
        r = subprocess.run(cmd + ["-p", "rx", "--features", "all", "-o", c] + arm +
                           ["--pattern", pat], capture_output=True, timeout=300)
        out.append(None if r.returncode else
                   (open(c, "rb").read(), open(os.path.join(d, tag, "rx.h"), "rb").read()))
    shutil.rmtree(d)
    a, b = out
    arm_s = " ".join(arm) or "byte"
    if a is None and b is None:
        return None
    if (a is None) != (b is None):
        return "compile asymmetric", rel, arm_s, pat
    sa = STAMP.search(a[0]).group(1).decode()
    sb = STAMP.search(b[0]).group(1).decode()
    if sa == "none":
        if sb != "none":
            return "the lever stamps %r where the default stamps \"none\"" % sb, rel, arm_s, pat
        if a != b:
            return "the lever moved an artifact the default ships plain", rel, arm_s, pat
        return "plain"
    if sb != "forced-off":
        return "the default ships %r and the lever stamps %r" % (sa, sb), rel, arm_s, pat
    return "forced"


def main():
    pcrec, harness, tree = sys.argv[1:4]
    jobs_n = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
    jobs, seen = [], set()
    for rel, _kind, pat in emit_sweep.enumerate_corpus(pcrec, tree, 120):
        if not pat or b"\x00" in pat or pat in seen:
            continue
        seen.add(pat)
        for arm in ([], ["-e", "utf8"]):
            jobs.append((pcrec, harness, tmp, rel, pat, arm))
    plain = forced = 0
    bad = []
    with cf.ThreadPoolExecutor(jobs_n) as ex:
        for r in ex.map(one, jobs):
            if r == "plain":
                plain += 1
            elif r == "forced":
                forced += 1
            elif r is not None:
                bad.append(r)
    shutil.rmtree(tmp)
    for why, rel, arm, pat in bad[:20]:
        print("FAIL: %s: %s %r [%s]" % (why, rel, pat[:80], arm))
    ok = not bad and forced >= FLOOR
    if forced < FLOOR:
        print("FAIL: %d forced-off pairs, below the floor %d (K35)" % (forced, FLOOR))
    print("%s: the lever: %d plain pairs byte-identical, %d forced-off where the default "
          "ships a compound; %d violations" % ("PASS" if ok else "FAIL", plain, forced, len(bad)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
