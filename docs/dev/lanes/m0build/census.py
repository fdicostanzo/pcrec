#!/usr/bin/env python3
"""docs/dev/lanes/m0build/census.py -- lane m0build's MOVER CENSUS for the
[MEASURE-SET] M0 abi event (81 -> 82): does M0 move any emitted byte beyond
the scaffolding it declares (docs/design/measure_sets.md §3.6; the brief's
STOP rule)?

    python3 -I census.py --base BIN --new BIN --tree DIR --out FILE [--jobs N]

BASE is the branch point's pcrec (f2dae53f9), NEW the lane's. Over every
distinct corpus pattern (scripts/emit_sweep.py's own enumeration, read through
NEW's `--list-source`), five arms are compiled by both:

  c-default  -p rx --features all -o -            (the .c, DFA or VM by auto)
  c-utf8     ... -e utf8
  c-vm       ... --engine=vm
  ir         --features all --engine=vm --emit-ir (the listing, K112's stream)
  facts      --features all --emit-facts=byte,utf8

and NEW's output is normalized by removing EXACTLY the declared scaffolding:
the three `measures` member lines of the shared ABI block, the line
`#define RX_MEASURES ""`, the initializer `    .measures = "",`, the
facts listing's RX_MEASURES decision row whose value is `""`, and the abi
digits (82 back to 81) in the four places they occur; and K112's two role
strings mapped back. A MEASURES line with any value other than "" is NOT
removed, so a consulted set (or a broken mirror) is a mover. rc and stderr are
compared too (stderr with the byte counts of the size warning masked, the one
number the scaffolding legitimately moves).

Every difference is a MOVER, written to OUT (arm, pattern, what moved, the
first differing line on each side). With `--movers FILE` the same census is
also written as `measure_store/movers/<seq>.tsv` for DEFAULTS transition 1
(none -> zen4-grid1@1 for class `idk`): a `header` section (old, new,
code_commit, the population) and a `movers` section (artifact, what moved,
old and new hashes, the first difference); this is M0's stand-in for
`emit_sweep.py --data measures`, which needs a same-binary "no set" side M0
does not have (m0build_report.md, deviations). The trailer is
`== m0 census COMPLETE: patterns=P compiles=C movers=M` and the exit status is
0 iff M == 0. Runs under the box lock (scripts/boxlock run), never bare.
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

MEMBER = [b"    /* <PREFIX>_MEASURES: the measurement set a reader consulted,",
          b"       id@rev:digest; \"\" when none consulted */",
          b"    const char           *measures;"]
DROP = {b"#define RX_MEASURES \"\"", b"    .measures = \"\","}
ABI = [(b"(abi 82)", b"(abi 81)"), (b"(PCREC_RX_ABI_H + 0) != 82", b"(PCREC_RX_ABI_H + 0) != 81"),
       (b"#define PCREC_RX_ABI_H 82", b"#define PCREC_RX_ABI_H 81"), (b"    .abi = 82,", b"    .abi = 81,")]
K112 = [(b"^ start of subject (absolute offset 0)", b"^ attempt_position of subject (absolute offset 0)"),
        (b"(?m)^ start of subject or after a non-final newline",
         b"(?m)^ attempt_position of subject or after a non-final newline")]
SIZE = re.compile(rb"\d+ bytes of emitted C source \(\d+ of code\)")

ARMS = [
    ("c-default", ["-p", "rx", "--features", "all", "-o", "-"]),
    ("c-utf8", ["-p", "rx", "--features", "all", "-e", "utf8", "-o", "-"]),
    ("c-vm", ["-p", "rx", "--features", "all", "--engine=vm", "-o", "-"]),
    ("ir", ["--features", "all", "--engine=vm", "--emit-ir"]),
    ("facts", ["--features", "all", "--emit-facts=byte,utf8"]),
]


def normalize_new(out):
    lines = out.split(b"\n")
    res, i = [], 0
    while i < len(lines):
        if lines[i:i + 3] == MEMBER:
            i += 3
            continue
        ln = lines[i]
        if ln in DROP:
            i += 1
            continue
        # the facts listing's decision row for the stamp, value ""
        if b"RX_MEASURES" in ln and ln.rstrip().endswith(b'\t""'):
            i += 1
            continue
        for a, b in ABI + K112:
            ln = ln.replace(a, b)
        res.append(ln)
        i += 1
    return b"\n".join(res)


def run(argv, timeout=60):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -9, b"", b"TIMEOUT"


def first_diff(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else b"<eof>"
        y = lb[i] if i < len(lb) else b"<eof>"
        if x != y:
            return "line %d: base=%r new=%r" % (i + 1, x[:120], y[:120])
    return ""


def one(task):
    arm, flags, base, new, pat = task
    rb, ob, eb = run([base] + flags + ["--pattern", pat])
    rn, on, en = run([new] + flags + ["--pattern", pat])
    moved = []
    if rb != rn:
        moved.append(("rc", "base=%d new=%d" % (rb, rn)))
    nn = normalize_new(on)
    if ob != nn:
        moved.append(("bytes", first_diff(ob, nn)))
    if SIZE.sub(b"N", eb) != SIZE.sub(b"N", normalize_new(en)):
        moved.append(("stderr", first_diff(eb, en)))
    return arm, pat, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--movers", default="")
    ap.add_argument("--old", default="")
    ap.add_argument("--new-set", default="zen4-grid1@1:13a6536315af1520")
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    corpus = emit_sweep.enumerate_corpus(a.new, a.tree, 60)
    pats = sorted(set(p for _, _, p in corpus))
    if a.limit:
        pats = pats[:a.limit]
    tasks = [(arm, flags, a.base, a.new, p) for arm, flags in ARMS for p in pats]
    movers = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for arm, pat, moved in ex.map(one, tasks, chunksize=16):
            for what, d in moved:
                movers.append((arm, pat, what, d))
    with open(a.out, "w", encoding="utf-8", errors="backslashreplace") as f:
        f.write("# m0build census: base=%s new=%s patterns=%d arms=%d\n" % (a.base, a.new, len(pats), len(ARMS)))
        f.write("#arm\tpattern\tmoved\tfirst_difference\n")
        for m in movers:
            f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n") for x in m) + "\n")
    if a.movers:
        head = subprocess.run(["git", "-C", a.tree, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        with open(a.movers, "w", encoding="utf-8", errors="backslashreplace") as f:
            f.write("# measure_store movers: DEFAULTS transition 1, class idk "
                    "(docs/design/measure_sets.md §2.1; written by "
                    "docs/dev/lanes/m0build/census.py)\n")
            f.write("#section header\n#key\tvalue\n")
            f.write("seq\t1\nclass\tidk\nold\t%s\nnew\t%s\ncode_commit\t%s\n" % (a.old, a.new_set, head))
            f.write("population\tcorpus rows %d, distinct patterns %d, arms %s\n"
                    % (len(corpus), len(pats), ";".join(n for n, _ in ARMS)))
            f.write("movers\t%d\n" % len(movers))
            f.write("#section movers\n#artifact\tmoved\tfirst_difference\n")
            for arm, pat, what, d in movers:
                f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n")
                                   for x in (arm + ":" + pat, what, d)) + "\n")
    per = {}
    for arm, _, _, _ in movers:
        per[arm] = per.get(arm, 0) + 1
    print("census: corpus rows %d, distinct patterns %d, arms %d" % (len(corpus), len(pats), len(ARMS)))
    for arm, _ in ARMS:
        print("  %-10s movers %d" % (arm, per.get(arm, 0)))
    print("== m0 census COMPLETE: patterns=%d compiles=%d movers=%d" % (len(pats), 2 * len(tasks), len(movers)))
    return 0 if not movers else 1


if __name__ == "__main__":
    sys.exit(main())
