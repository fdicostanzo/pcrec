#!/usr/bin/env python3
"""[OPT-HYB-RESEED] byte-identity sweep: branch point (abi 46) vs this change,
default and under -fno-hyb-reseed, every corpus pattern line, --features all,
both encodings, `-o -` on every side (the -o basename trap).

Normalization removes exactly the two things the change is DECLARED to add
everywhere: the abi digit (`.abi = 46`/`(abi 46)` -> 47) and the one
`#define RX_VM_RESEED "..."` line. After it:
  - base vs DENY must be byte-identical on EVERY artifact (the deny's claim);
  - base vs NEW may differ only where NEW stamps an `adaptive*` row (the
    mover population), and every such artifact must differ (a row that
    claims adaptive but emits today's text is a stamp lie).
Usage: identity_sweep.py BASE_PCREC NEW_PCREC TREE OUT_TSV [--jobs 2]
"""
import argparse, concurrent.futures, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import emit_sweep  # noqa: E402

RESEED = re.compile(rb'^#define RX_VM_RESEED "([a-z-]+)"\n', re.M)


def comp(binp, pat, enc, extra):
    argv = [binp, "-p", "rx", "--features", "all"] + (["-e", enc] if enc != "byte" else []) + extra + ["-o", "-", "--pattern", pat]
    r = subprocess.run(argv, capture_output=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def norm(b):
    b = b.replace(b".abi = 46,", b".abi = 47,").replace(b"(abi 46)", b"(abi 47)")
    return RESEED.sub(b"", b)


def one(a, pat, enc):
    base = comp(a.base, pat, enc, [])
    new = comp(a.new, pat, enc, [])
    deny = comp(a.new, pat, enc, ["-fno-hyb-reseed"])
    if base is None and new is None and deny is None:
        return ("both-refuse", "-", "-")
    if base is None or new is None or deny is None:
        return ("REFUSAL-MISMATCH", "-", "-")
    m = RESEED.search(new)
    row = m.group(1).decode() if m else "-"
    md = RESEED.search(deny)
    drow = md.group(1).decode() if md else "-"
    nb, nn, nd = norm(base), norm(new), norm(deny)
    deny_ok = nb == nd
    moved = nb != nn
    if not deny_ok:
        verdict = "DENY-DIFFERS"
    elif row.startswith("adaptive") and not moved:
        verdict = "ADAPTIVE-UNMOVED"
    elif not row.startswith("adaptive") and moved:
        verdict = "UNEXPECTED-MOVER"
    else:
        verdict = "mover" if moved else "identical"
    return (verdict, row, drow)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("new"); ap.add_argument("tree"); ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=2)
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
            except Exception as x: v = ("ERROR:" + type(x).__name__, "-", "-")
            rows.append((f, e, v, p))
            k = (e, v[0], v[1], v[2]); tally[k] = tally.get(k, 0) + 1
    with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as o:
        o.write("file\tenc\tverdict\trow\tdeny_row\tpattern\n")
        for f, e, v, p in sorted(rows, key=lambda x: (x[0], x[1], x[3])):
            o.write(f"{f}\t{e}\t{v[0]}\t{v[1]}\t{v[2]}\t{p!r}\n")
    print(f"rows: {len(rows)} ({len(uniq)} unique patterns x 2 encodings)")
    for k in sorted(tally): print("  %-5s %-18s row=%-15s deny=%-8s %6d" % (k[0], k[1], k[2], k[3], tally[k]))
    bad = sum(n for k, n in tally.items() if k[1] in ("DENY-DIFFERS", "ADAPTIVE-UNMOVED", "UNEXPECTED-MOVER", "REFUSAL-MISMATCH") or k[1].startswith("ERROR"))
    print(f"violations: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
