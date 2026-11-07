#!/usr/bin/env python3
"""span_cards/slot/movers.py -- S2e's DATA-MOVER census (span_cards.md §5; written by S2c, RUN by S2e): a copy
of docs/dev/lanes/m0build/census.py's method with its normalization list EMPTY. S2e declares no scaffolding, so
EVERY difference in bytes, rc or stderr is a mover, an `RX_MEASURES` line included. Ruled PLAN (kit manager,
r6): `scripts/emit_sweep.py --data measures` REPLACES this copy when the next data-mover census is needed (M1's
first set; span_cards §10 item 12).

    python3 -I movers.py --base BIN --new BIN --tree DIR --out FILE [--movers FILE] [--jobs N] [--limit N]

BASE is the unit's named base pcrec (DEFAULTS before the flip: zen4-grid1), NEW S2e's head (zen4-grid3 by
default). Over every distinct corpus pattern (scripts/emit_sweep.py's own enumeration, read through NEW's
`--list-source`), five arms (c-default, c-utf8, c-vm, ir, facts) are compiled by both. A SECOND pass compiles
NEW with `--measures=zen4-grid1` against NEW with `--measures=zen4-grid3` over the same arms (the head against
itself across the two sets). Every difference is a mover, written to OUT. `--movers FILE` writes
`measure_store/movers/0002.tsv` in 0001's section shape (`#section header`: seq 2, class idk, old, new,
code_commit, population, movers; `#section movers`: artifact moved first_difference). Trailer
`== s2 movers COMPLETE: patterns=P compiles=C movers=M`; exit 0 iff M == 0. Runs under the box lock (a
boxqueue job), never bare.
"""
import argparse
import concurrent.futures
import os
import subprocess
import sys

ARMS = [
    ("c-default", ["-p", "rx", "--features", "all", "-o", "-"]),
    ("c-utf8", ["-p", "rx", "--features", "all", "-e", "utf8", "-o", "-"]),
    ("c-vm", ["-p", "rx", "--features", "all", "--engine=vm", "-o", "-"]),
    ("ir", ["--features", "all", "--engine=vm", "--emit-ir"]),
    ("facts", ["--features", "all", "--emit-facts=byte,utf8"]),
]
SETS = ("zen4-grid1", "zen4-grid3")   # the self pass: NEW under each


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
            return "line %d: old=%r new=%r" % (i + 1, x[:120], y[:120])
    return ""


def one(task):
    arm, old, new, pat = task             # old/new: argv prefixes (binary + flags)
    ro, oo, eo = run(old + ["--pattern", pat])
    rn, on, en = run(new + ["--pattern", pat])
    moved = []
    if ro != rn:
        moved.append(("rc", "old=%d new=%d" % (ro, rn)))
    if oo != on:
        moved.append(("bytes", first_diff(oo, on)))
    if eo != en:
        moved.append(("stderr", first_diff(eo, en)))
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
    ap.add_argument("--old-set", default="zen4-grid1@1:13a6536315af1520")
    ap.add_argument("--new-set", default="")
    a = ap.parse_args()
    if a.movers and not a.new_set:
        sys.exit("movers.py: --movers needs --new-set zen4-grid3@1:<digest>")
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    corpus = emit_sweep.enumerate_corpus(a.new, a.tree, 60)
    pats = sorted(set(p for _, _, p in corpus))   # bytes: corpus patterns need not be UTF-8
    if a.limit:
        pats = pats[:a.limit]
    tasks = []
    for arm, flags in ARMS:
        for p in pats:
            tasks.append(("base:" + arm, [a.base] + flags, [a.new] + flags, p))
            tasks.append(("self:" + arm, [a.new, "--measures=" + SETS[0]] + flags,
                          [a.new, "--measures=" + SETS[1]] + flags, p))
    movers = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for arm, pat, moved in ex.map(one, tasks, chunksize=16):
            for what, d in moved:
                movers.append((arm, emit_sweep.encode_escape(pat), what, d))
    esc = lambda x: x.replace("\t", "\\t").replace("\n", "\\n")
    with open(a.out, "w", encoding="utf-8", errors="backslashreplace") as f:
        f.write("# s2 movers: base=%s new=%s patterns=%d arms=%d passes=base,self\n"
                % (a.base, a.new, len(pats), len(ARMS)))
        f.write("#arm\tpattern\tmoved\tfirst_difference\n")
        for m in movers:
            f.write("\t".join(esc(x) for x in m) + "\n")
    if a.movers:
        head = subprocess.run(["git", "-C", a.tree, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        with open(a.movers, "w", encoding="utf-8", errors="backslashreplace") as f:
            f.write("# measure_store movers: DEFAULTS transition 2, class idk "
                    "(span_cards.md §5; written by docs/design/memfn/span_cards/slot/movers.py)\n")
            f.write("#section header\n#key\tvalue\n")
            f.write("seq\t2\nclass\tidk\nold\t%s\nnew\t%s\ncode_commit\t%s\n" % (a.old_set, a.new_set, head))
            f.write("population\tcorpus rows %d, distinct patterns %d, arms %s, passes base;self\n"
                    % (len(corpus), len(pats), ";".join(n for n, _ in ARMS)))
            f.write("movers\t%d\n" % len(movers))
            f.write("#section movers\n#artifact\tmoved\tfirst_difference\n")
            for arm, pat, what, d in movers:
                f.write("\t".join(esc(x) for x in (arm + ":" + pat, what, d)) + "\n")
    per = {}
    for arm, _, _, _ in movers:
        per[arm] = per.get(arm, 0) + 1
    print("movers: corpus rows %d, distinct patterns %d, arms %d, passes base and self"
          % (len(corpus), len(pats), len(ARMS)))
    for pas in ("base", "self"):
        for arm, _ in ARMS:
            print("  %-15s movers %d" % (pas + ":" + arm, per.get(pas + ":" + arm, 0)))
    print("== s2 movers COMPLETE: patterns=%d compiles=%d movers=%d" % (len(pats), 2 * len(tasks), len(movers)))
    return 0 if not movers else 1


if __name__ == "__main__":
    sys.exit(main())
