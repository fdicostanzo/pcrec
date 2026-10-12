#!/usr/bin/env python3
"""tests/compound/landing_census.py -- [COMPOUND] B4's landing bar (G6) and
the admitted population (docs/design/compound.md §E.3 G6, §B.4).

  landing_census.py --ref-bin REF --bin WORK --tree TREE [--bench BENCH]
                    [--out DIR] [--jobs N] [--write-manifest FILE]

Compiles every DISTINCT corpus pattern (`--list-source` over TREE/tests,
emit_sweep's own enumeration), under two arms (`byte`, `-e utf8`), and every
pcrec-bench export (BENCH/bench/<set>/patterns/*.rx, read-only, the `utf8`
set under `-e utf8`), with the REFERENCE pcrec (the B4 parent) and the WORKING
one, at `-p rx --features all`. Both sides' `.c` and `.h` are compared after
ONE normalization and nothing else: the abi digits (the provenance line, the
shared block's guard and `#error`, `.abi = N`) and the working side's one
`#define RX_COMPOUND "none"` line. Each pattern then lands in one class:

  same      the working side stamps "none" and the texts are identical
  stamp-sized  ...identical but for a size-cap `_WHY` stamp's quoted size,
            which the one new stamp line lengthens (by ID, expected)
  admitted  the working side stamps a row name (a compound): a MOVER by ID;
            with --harness, the lever's output there must be the reference's
            plain artifact plus `"forced-off"` (§A.11's property (b))
  FINDING   the working side stamps "none" and the texts still differ, or
            the two sides disagree on compiling at all

G6's bar: zero FINDINGs, and bench reach 0 (no bench export admitted). The
admitted IDs are written with `--write-manifest` (tests/compound/
admitted.tsv, the population test-compound pins without a reference build).
Exit 1 on a FINDING or a bench admission.
"""
import argparse, concurrent.futures as cf, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
import emit_sweep  # noqa: E402  (the corpus enumeration, one methodology)

ABI_RES = [
    (re.compile(rb"\(abi \d+\)"), b"(abi N)"),
    (re.compile(rb"PCREC_RX_ABI_H \d+"), b"PCREC_RX_ABI_H N"),
    (re.compile(rb"\(PCREC_RX_ABI_H \+ 0\) != \d+"), b"(PCREC_RX_ABI_H + 0) != N"),
    (re.compile(rb"\.abi = \d+"), b".abi = N"),
]
STAMP = re.compile(rb'^#define RX_COMPOUND "([^"]*)"\n', re.M)
# A size-cap rung's `_WHY` stamp quotes the refused attempt's emitted size,
# which the one new stamp line itself lengthens: its figure is the one
# number that may move on an artifact that stamps "none" (class
# `stamp-sized`, still reported by ID).
SIZED = re.compile(rb'(_WHY "size cap retry, [a-z-]+ )\d+( > \d+")')


def norm(text, drop_none, drop=b'#define RX_COMPOUND "none"\n'):
    for r, s in ABI_RES:
        text = r.sub(s, text)
    if drop_none:
        text = text.replace(drop, b"")
    return text


def compile_one(binp, pat, arm, d, tag):
    """`pat` compiled into D/TAG/rx.c (the same file NAME on both sides: the
    `.c` includes its `.h` by name); its (c, h), or None on a refusal."""
    os.mkdir(os.path.join(d, tag))
    c = os.path.join(d, tag, "rx.c")
    r = subprocess.run([binp, "-p", "rx", "--features", "all", "-o", c] + arm +
                       ["--pattern", pat], capture_output=True, timeout=300)
    if r.returncode:
        return None
    return open(c, "rb").read(), open(os.path.join(d, tag, "rx.h"), "rb").read()


def classify(job):
    ref, work, harness, pid, pat, arm, tmp = job
    d = tempfile.mkdtemp(dir=tmp)
    a = compile_one(ref, pat, arm, d, "a")
    b = compile_one(work, pat, arm, d, "b")
    lev = None
    if harness and b is not None and STAMP.search(b[0]) and STAMP.search(b[0]).group(1) != b"none":
        lev = compile_one(harness, pat, arm + ["--harness=no-compound"], d, "l")
    shutil.rmtree(d)
    if a is None and b is None:
        return pid, arm, "-", "both-refuse"
    if (a is None) != (b is None):
        return pid, arm, "-", "FINDING:compile-asymmetric"
    m = STAMP.search(b[0])
    stamp = m.group(1).decode() if m else "MISSING"
    if stamp == "MISSING":
        return pid, arm, stamp, "FINDING:no-stamp"
    if stamp != "none":
        if lev is not None:
            fo = b'#define RX_COMPOUND "forced-off"\n'
            if not (norm(a[0], False) == norm(lev[0], True, fo) and a[1] == lev[1] or
                    norm(a[0], False) == norm(lev[0], True, fo) and norm(a[1], False) == norm(lev[1], False)):
                return pid, arm, stamp, "FINDING:lever-is-not-the-plain-artifact"
        return pid, arm, stamp, "admitted"
    same = norm(a[0], False) == norm(b[0], True) and norm(a[1], False) == norm(b[1], True)
    if same:
        return pid, arm, stamp, "same"
    sized = (SIZED.sub(rb"\1N\2", norm(a[0], False)) == SIZED.sub(rb"\1N\2", norm(b[0], True))
             and norm(a[1], False) == norm(b[1], True))
    return pid, arm, stamp, "stamp-sized" if sized else "FINDING:moved-without-a-row"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-bin", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--bench")
    ap.add_argument("--harness", help="build/pcrec-harness: an admitted pattern's lever "
                    "output must be the reference's plain artifact plus \"forced-off\"")
    ap.add_argument("--out", default=None)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--write-manifest")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(dir=a.out or os.environ.get("TMPDIR"))
    jobs = []
    seen = set()
    for rel, _kind, pat in emit_sweep.enumerate_corpus(a.bin, a.tree, 120):
        if not pat or b"\x00" in pat or pat in seen:
            continue
        seen.add(pat)
        for arm in ([], ["-e", "utf8"]):
            jobs.append((a.ref_bin, a.bin, a.harness, "corpus\t%s\t%s" % (rel, pat.hex()), pat, arm, tmp))
    ncorpus = len(seen)
    nbench = 0
    if a.bench:
        root = os.path.join(a.bench, "bench")
        for sb in sorted(os.listdir(root)):
            d = os.path.join(root, sb, "patterns")
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".rx"):
                    continue
                pat = open(os.path.join(d, fn), "rb").read()
                arm = ["-e", "utf8"] if sb == "utf8" else []
                jobs.append((a.ref_bin, a.bin, a.harness, "bench\t%s/%s\t%s" % (sb, fn[:-3], pat.hex()),
                             pat, arm, tmp))
                nbench += 1
    rows = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(classify, jobs):
            rows.append(r)
    os.rmdir(tmp)
    counts = {}
    for pid, arm, stamp, verdict in rows:
        pop = pid.split("\t")[0]
        counts[(pop, verdict)] = counts.get((pop, verdict), 0) + 1
    print("population: corpus %d distinct patterns x 2 arms, bench %d exports" % (ncorpus, nbench))
    for k in sorted(counts):
        print("  %-6s %-30s %d" % (k[0], k[1], counts[k]))
    bad = [r for r in rows if r[3].startswith("FINDING")]
    bench_adm = [r for r in rows if r[0].startswith("bench") and r[3] == "admitted"]
    for pid, arm, stamp, verdict in bad[:40]:
        print("FINDING\t%s\t%s\t%s" % (pid, " ".join(arm) or "byte", verdict))
    for pid, arm, stamp, verdict in bench_adm:
        print("BENCH-ADMITTED\t%s\t%s" % (pid, stamp))
    if a.write_manifest:
        adm = sorted({(pid.split("\t", 1)[1], " ".join(arm) or "byte", stamp)
                      for pid, arm, stamp, v in rows if v == "admitted"})
        with open(a.write_manifest, "w") as f:
            f.write("# [COMPOUND] the admitted population (landing_census.py, B4): "
                    "file<TAB>pattern-hex<TAB>arm<TAB>row. Regenerate with --write-manifest.\n")
            for x in adm:
                f.write("\t".join(x) + "\n")
        print("manifest: %d admitted (file:line, arm) rows -> %s" % (len(adm), a.write_manifest))
    ok = not bad and not bench_adm
    print("%s: G6 landing bar: %d findings, %d bench admissions" %
          ("PASS" if ok else "FAIL", len(bad), len(bench_adm)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
