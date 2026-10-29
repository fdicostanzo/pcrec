#!/usr/bin/env python3
"""docs/dev/lanes/r30b_evidence/census.py -- lane r30b's MOVER CENSUS for [MEMFN] R-30
(abi 92 -> 94 in landing order), in lane s3's census.py shape (emit_sweep has no abi
normalization): which corpus artifacts move, and does anything move OUTSIDE the declared
population?

    python3 -I census.py --base BIN --new BIN --harness BIN --tree DIR --out FILE [--jobs N]

BASE is main 1f5574fac's pcrec, NEW the R-30 commit's, HARNESS NEW's build/pcrec-harness. Over
every distinct corpus pattern (scripts/emit_sweep.py's enumeration, each under its own block's
options, s3_evidence/census.py's `corpus_tasks`), each arm is compiled by both sides; NEW's
output has the abi digits mapped back (94 -> 92) in the four places they occur and nothing else
is normalized; rc and stderr are compared too.

THE DECLARED POPULATION is read from BASE's OWN ARTIFACT on that arm, a pcrec-side read, never
from the kit and never from the diff: an artifact is BOTH-ASKS iff BASE's text calls the run
window's search `rx_reqrun(` AND the whole run's `rx_reqrun_whole(` (the pre-check carrying
both parts). The judgment, BOTH WAYS, per .c arm: a BOTH-ASKS artifact MUST move, and its move
must be the declared one (NEW's text calls no `rx_reqrun(` and defines no `rx_reqrun__body`,
still calls `rx_reqrun_whole(`, and every `#define RX_` stamp line is BASE's); any other
artifact may NOT move. The `ir` and `facts` arms: nothing may move. The LEVER arms (NEW's
harness binary under `--harness=pres-window` against BASE): nothing may move at all.
"""
import argparse
import concurrent.futures
import os
import subprocess
import sys

ABI = [(b"(abi 94)", b"(abi 92)"), (b"(PCREC_RX_ABI_H + 0) != 94", b"(PCREC_RX_ABI_H + 0) != 92"),
       (b"#define PCREC_RX_ABI_H 94", b"#define PCREC_RX_ABI_H 92"), (b"    .abi = 94,", b"    .abi = 92,")]
LEVER = "--harness=pres-window"
C = ["-p", "rx", "--features", "all", "-o", "-"]

# (arm, extra argv, new side: "new" | "lever", judged as a .c arm?)
ARMS = [
    ("c-default", [], "new", True),
    ("c-utf8", ["-e", "utf8"], "new", True),
    ("c-vm", ["--engine=vm"], "new", True),
    ("c-simd", ["-fmemfn-simd"], "new", True),
    ("c-vm-simd", ["--engine=vm", "-fmemfn-simd"], "new", True),
    ("lever", [], "lever", False),
    ("lever-vm", ["--engine=vm"], "lever", False),
]
LISTINGS = [("ir", ["--features", "all", "--engine=vm", "--emit-ir"]),
            ("facts", ["--features", "all", "--emit-facts=byte,utf8"])]


def norm(out):
    for a, b in ABI:
        out = out.replace(a, b)
    return out


def run(argv, timeout=60):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -9, b"", b"TIMEOUT"


def stamps(text):
    return [ln for ln in text.split(b"\n") if ln.startswith(b"#define RX_")]


def both_asks(text):
    return b"rx_reqrun(" in text and b"rx_reqrun_whole(" in text


def one(task):
    base, new, harness, pat, opts = task
    res = []
    for arm, extra, side, is_c in ARMS:
        b = run([base] + list(opts) + C + extra + ["--pattern", pat])
        nb = new if side == "new" else harness
        n = run([nb] + list(opts) + C + extra + ([LEVER] if side == "lever" else []) + ["--pattern", pat])
        moved = b[0] != n[0] or b[2] != norm(n[2]) or b[1] != norm(n[1])
        declared = side == "new" and b[0] == 0 and both_asks(b[1])
        bad = ""
        if side == "lever":
            bad = "the lever's artifact moved" if moved else ""
        elif declared and not moved:
            bad = "a BOTH-ASKS artifact did not move"
        elif moved and not declared:
            bad = "an artifact outside the declared population moved"
        elif declared:
            t = norm(n[1])
            if b"rx_reqrun(" in t or b"rx_reqrun__body" in t or b"rx_reqrun_whole(" not in t:
                bad = "the move is not the declared one (window asked, or whole run lost)"
            elif stamps(t) != stamps(b[1]):
                bad = "a stamp moved"
        res.append((arm, declared, moved, bad))
    for arm, argv in LISTINGS:
        b = run([base] + list(opts) + argv + ["--pattern", pat])
        n = run([new] + list(opts) + argv + ["--pattern", pat])
        moved = b[0] != n[0] or b[2] != norm(n[2]) or b[1] != norm(n[1])
        res.append((arm, False, moved, "the listing moved" if moved else ""))
    return pat, opts, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--harness", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="", help="a substring a task's pattern must hold (a smoke run)")
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    sys.path.insert(0, os.path.join(a.tree, "docs", "dev", "lanes", "s3_evidence"))
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    import census as s3census  # noqa: E402  (corpus_tasks, block_options)
    rows, tasks, refused = s3census.corpus_tasks(emit_sweep, a.new, a.tree)
    if a.only:
        tasks = [t for t in tasks if os.fsencode(a.only) in os.fsencode(t[0])]
    names = [x[0] for x in ARMS] + [x[0] for x in LISTINGS]
    tally = {k: [0, 0, 0] for k in names}   # declared, moved, unexpected
    lines = []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for pat, opts, res in ex.map(one, [(a.base, a.new, a.harness, p, o) for p, o in tasks]):
            for arm, declared, moved, bad in res:
                t = tally[arm]
                t[0] += declared
                t[1] += moved
                t[2] += bool(bad)
                if moved or bad:
                    lines.append("%s\t%s\t%s\t%s\t%s" % ("UNEXPECTED" if bad else "MOVED", arm,
                                 " ".join(opts) or "-", os.fsencode(pat).decode("utf-8", "backslashreplace"), bad))
    with open(a.out, "w") as f:
        f.write("# r30b census: %d corpus rows, %d distinct tasks, %d refused (options not passed)\n"
                % (rows, len(tasks), len(refused)))
        for ln in sorted(lines):
            f.write(ln + "\n")
        unexpected = 0
        for k in names:
            d, m, u = tally[k]
            unexpected += u
            f.write("== arm %-10s tasks=%d declared=%d moved=%d unexpected=%d\n" % (k, len(tasks), d, m, u))
        f.write("== census COMPLETE: %d unexpected\n" % unexpected)
    print(open(a.out).read().split("\n== arm", 1)[0][-400:])
    os.system("grep '^==' " + a.out)
    return 1 if unexpected or not tasks else 0


if __name__ == "__main__":
    sys.exit(main())
