#!/usr/bin/env python3
"""[OPT-HYB-RESEED-FORM] A1 byte-identity sweep: branch point (abi 55) vs the
`anchored` row (abi 56), default and under -fno-hyb-reseed, every corpus
pattern line, --features all, both encodings, `-o -` on every side.

Normalization removes the abi digit and the one `#define RX_VM_RESEED` line.
After it the sweep asserts, per artifact:
  - base-deny equals new-deny (the deny's text is untouched by the row);
  - base equals new except where NEW stamps `anchored` and BASE stamped an
    `adaptive*` row (the mover population), and every such artifact differs;
  - a mover's diff is EXACTLY the adaptive text REMOVED: no line added, and
    every removed line one of identity_sweep.ADDED's (the declaration and
    the retry tail) — the reverse of lane reseed's own mover rule;
  - wherever NEW stamps `anchored`, new equals new-deny byte for byte,
    stamp line included (the row is undeniable and above the denied rows);
  - and it tallies the movers by base row x `RX_VM_START` (the census).
Usage: anchored_sweep.py BASE_PCREC NEW_PCREC TREE OUT_TSV [--jobs 2] [--extra='--engine=vm -fprefilter']
`--extra` appends flags to all four compiles (the engine arm: a forced-VM
hybrid is the other route that reaches the re-seed table).
"""
import argparse, concurrent.futures, difflib, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
sys.path.insert(0, HERE)
import emit_sweep  # noqa: E402
from identity_sweep import ADDED, RESEED  # noqa: E402

START = re.compile(rb'^#define RX_VM_START "([a-z]+)"\n', re.M)


def comp(binp, pat, enc, extra):
    argv = [binp, "-p", "rx", "--features", "all"] + (["-e", enc] if enc != "byte" else []) + extra + ["-o", "-", "--pattern", pat]
    r = subprocess.run(argv, capture_output=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def norm(b):
    b = b.replace(b".abi = 55,", b".abi = 56,").replace(b"(abi 55)", b"(abi 56)")
    b = b.replace(b"(PCREC_RX_ABI_H + 0) != 55", b"(PCREC_RX_ABI_H + 0) != 56").replace(b"#define PCREC_RX_ABI_H 55", b"#define PCREC_RX_ABI_H 56")
    return RESEED.sub(b"", b)


def diff_is_adaptive_text_removed(nb, nn):
    removed, added = [], []
    for l in difflib.diff_bytes(difflib.unified_diff, nb.split(b"\n"), nn.split(b"\n"), lineterm=b"", n=0):
        if l.startswith(b"---") or l.startswith(b"+++") or l.startswith(b"@@"): continue
        (removed if l.startswith(b"-") else added).append(l[1:])
    return not added and len(removed) == len(ADDED) and all(any(r.match(x) for r in ADDED) for x in removed)


def row_of(b):
    m = RESEED.search(b)
    return m.group(1).decode() if m else "-"


def one(a, pat, enc):
    x = a.extra.split()
    base = comp(a.base, pat, enc, x)
    bdeny = comp(a.base, pat, enc, x + ["-fno-hyb-reseed"])
    new = comp(a.new, pat, enc, x)
    ndeny = comp(a.new, pat, enc, x + ["-fno-hyb-reseed"])
    if base is None and new is None and bdeny is None and ndeny is None:
        return ("both-refuse", "-", "-", "-")
    if None in (base, new, bdeny, ndeny):
        return ("REFUSAL-MISMATCH", "-", "-", "-")
    brow, nrow = row_of(base), row_of(new)
    m = START.search(new)
    start = m.group(1).decode() if m else "-"
    nb, nn = norm(base), norm(new)
    if norm(bdeny) != norm(ndeny):
        v = "DENY-DIFFERS"
    elif nrow == "anchored" and new != ndeny:
        v = "ANCHORED-NOT-DENY"
    elif nrow == "anchored" and brow.startswith("adaptive"):
        v = "mover" if diff_is_adaptive_text_removed(nb, nn) else (
            "ANCHORED-UNMOVED" if nb == nn else "MOVER-EXTRA-TEXT")
    elif nrow == "anchored" and brow != "fixed" and nb == nn:
        v = "ROW-RENAMED"            # would mean the row outranks exact/clamped
    elif nb != nn:
        v = "UNEXPECTED-MOVER"
    else:
        v = "identical"
    return (v, brow, nrow, start)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("new"); ap.add_argument("tree"); ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--extra", default="")
    a = ap.parse_args()
    pats = emit_sweep.enumerate_corpus(a.new, a.tree, 30)
    seen, uniq = set(), []
    for f, kind, p in pats:
        if p in seen: continue
        seen.add(p); uniq.append((f, bytes(p).decode("utf-8", "surrogateescape")))
    work = [(f, p, e) for f, p in uniq for e in ("byte", "utf8")]
    tally, rows = {}, []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(one, a, p, e): (f, p, e) for f, p, e in work}
        for fu in concurrent.futures.as_completed(futs):
            f, p, e = futs[fu]
            try: v = fu.result()
            except Exception as x: v = ("ERROR:" + type(x).__name__, "-", "-", "-")
            rows.append((f, e, v, p))
            k = (e,) + v; tally[k] = tally.get(k, 0) + 1
    with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as o:
        o.write("file\tenc\tverdict\tbase_row\tnew_row\tvm_start\tpattern\n")
        for f, e, v, p in sorted(rows, key=lambda x: (x[0], x[1], x[3])):
            o.write(f"{f}\t{e}\t{v[0]}\t{v[1]}\t{v[2]}\t{v[3]}\t{p!r}\n")
    print(f"rows: {len(rows)} ({len(uniq)} unique patterns x 2 encodings)")
    for k in sorted(tally): print("  %-5s %-18s base=%-15s new=%-15s start=%-11s %6d" % (k + (tally[k],)))
    bad = sum(n for k, n in tally.items() if k[1] not in ("identical", "mover", "both-refuse"))
    print(f"violations: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
