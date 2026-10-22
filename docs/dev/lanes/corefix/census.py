#!/usr/bin/env python3
"""docs/dev/lanes/corefix/census.py -- lane corefix's MOVER CENSUS for the
abi event 82 -> 87 (K128 + K129; ruling R1 in corefix_rulings.md): which
corpus artifacts move, and does anything move OUTSIDE the two shapes the
fixes live in?

    python3 -I census.py --base BIN --new BIN --tree DIR --out FILE [--jobs N]

BASE is main a53296894's pcrec, NEW the lane's. Over every distinct corpus
pattern (scripts/emit_sweep.py's own enumeration), five arms are compiled by
both: the .c at the default engine, under -e utf8 and at --engine=vm, the VM
listing (--emit-ir) and the facts listing. NEW's output has the abi digits
mapped back (87 -> 82) in the four places they occur; nothing else is
normalized, and rc and stderr are compared too.

Each pattern is classified from NEW's own VM listing, never from the diff:
  K128  the listing records a last mandatory iteration ("the last mandatory
        iteration: record where it began"), i.e. a VM X{m,} with m >= 1 and a
        nullable body
  K129  the artifact resolves caller variables (`_vars_resolve(` in the .c)
  other neither.
Every mover in class `other` is UNEXPECTED; so is a K128-class pattern whose
--engine=vm .c did NOT move (the fix did not reach it). The trailer is
`== corefix census COMPLETE: patterns=P compiles=C movers=M unexpected=U` and
the exit status is 0 iff U == 0.
"""
import argparse
import concurrent.futures
import os
import subprocess
import sys

ABI = [(b"(abi 87)", b"(abi 82)"), (b"(PCREC_RX_ABI_H + 0) != 87", b"(PCREC_RX_ABI_H + 0) != 82"),
       (b"#define PCREC_RX_ABI_H 87", b"#define PCREC_RX_ABI_H 82"), (b"    .abi = 87,", b"    .abi = 82,")]
K128_MARK = b"the last mandatory iteration: record where it began"
K129_MARK = b"_vars_resolve("

ARMS = [
    ("c-default", ["-p", "rx", "--features", "all", "-o", "-"]),
    ("c-utf8", ["-p", "rx", "--features", "all", "-e", "utf8", "-o", "-"]),
    ("c-vm", ["-p", "rx", "--features", "all", "--engine=vm", "-o", "-"]),
    ("ir", ["--features", "all", "--engine=vm", "--emit-ir"]),
    ("facts", ["--features", "all", "--emit-facts=byte,utf8"]),
]


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


def first_diff(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else b"<eof>"
        y = lb[i] if i < len(lb) else b"<eof>"
        if x != y:
            return "line %d: base=%r new=%r" % (i + 1, x[:100], y[:100])
    return ""


def one(task):
    base, new, pat = task
    _, ir, _ = run([new, "--features", "all", "--engine=vm", "--emit-ir", "--pattern", pat])
    _, cvm, _ = run([new, "-p", "rx", "--features", "all", "--engine=vm", "-o", "-", "--pattern", pat])
    cls = "K128" if K128_MARK in ir else "K129" if K129_MARK in cvm else "other"
    moved = []
    for arm, flags in ARMS:
        rb, ob, eb = run([base] + flags + ["--pattern", pat])
        rn, on, en = run([new] + flags + ["--pattern", pat])
        what = []
        if rb != rn:
            what.append("rc base=%d new=%d" % (rb, rn))
        if ob != norm(on):
            what.append("bytes " + first_diff(ob, norm(on)))
        if eb != norm(en):
            what.append("stderr " + first_diff(eb, norm(en)))
        moved.append((arm, "; ".join(what)))
    return pat, cls, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    corpus = emit_sweep.enumerate_corpus(a.new, a.tree, 60)
    pats = sorted(set(p for _, _, p in corpus))
    if a.limit:
        pats = pats[:a.limit]
    tally, unexpected, rows = {}, [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for pat, cls, moved in ex.map(one, [(a.base, a.new, p) for p in pats], chunksize=8):
            ep = emit_sweep.encode_escape(pat)
            tally.setdefault(cls, {"patterns": 0})
            tally[cls]["patterns"] += 1
            for arm, what in moved:
                if not what:
                    continue
                tally[cls][arm] = tally[cls].get(arm, 0) + 1
                rows.append((cls, arm, ep, what))
                if cls == "other":
                    unexpected.append((cls, arm, ep, what))
            if cls == "K128" and not dict(moved)["c-vm"]:
                unexpected.append((cls, "c-vm", ep, "K128 shape did NOT move"))
    with open(a.out, "w", encoding="utf-8", errors="backslashreplace") as f:
        f.write("# corefix census: base=%s new=%s patterns=%d\n#class\tarm\tpattern\tmoved\n"
                % (a.base, a.new, len(pats)))
        for r in unexpected + rows:
            f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n") for x in r) + "\n")
    print("census: corpus rows %d, distinct patterns %d" % (len(corpus), len(pats)))
    for cls in ("K128", "K129", "other"):
        t = tally.get(cls, {"patterns": 0})
        print("  %-5s patterns %5d  movers: %s" % (cls, t["patterns"], "  ".join(
            "%s=%d" % (arm, t.get(arm, 0)) for arm, _ in ARMS)))
    for u in unexpected[:20]:
        print("  UNEXPECTED %s %s %s: %s" % u)
    print("== corefix census COMPLETE: patterns=%d compiles=%d movers=%d unexpected=%d"
          % (len(pats), 2 * len(pats) * len(ARMS) + 2 * len(pats), len(rows), len(unexpected)))
    return 0 if not unexpected else 1


if __name__ == "__main__":
    sys.exit(main())
