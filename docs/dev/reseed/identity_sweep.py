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
  - (lane reseedfix, r1 panel chk F7) a mover's diff is exactly the
    adaptive text: no base line removed, and every added line one of the
    declaration or the retry tail's lines (ADDED below) — so "moved" means
    "moved by this change", not "any text difference";
  - (r1 panel chk F1) the code bytes each mover gains, in the size model's
    own measure (src/core/compile.c `emit_size_measure`: total minus comment
    and table-initializer lines), summed per row and encoding.
Usage: identity_sweep.py BASE_PCREC NEW_PCREC TREE OUT_TSV [--jobs 2]
"""
import argparse, concurrent.futures, difflib, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import emit_sweep  # noqa: E402

RESEED = re.compile(rb'^#define RX_VM_RESEED "([a-z-]+)"\n', re.M)
# The adaptive text, line by line (src/gen/emit_vm.c `vm_emit_search_body`).
ADDED = [re.compile(x) for x in (
    rb'^    unsigned reseed_steps = \d+, reseed_block = \d+;$',
    rb'^        if \(reseed_steps\) reseed_steps--;$',
    rb'^        else \{$',
    rb'^            ptrdiff_t window\[1\]\[2\];$',
    rb'^            if \(rx_prefilter\(subject, subject_length, attempt_position, window\) != 1\) return 0;$',
    rb'^            if \(\(size_t\)window\[0\]\[0\] - attempt_position >= \d+\) reseed_block = 0;$',
    rb'^            else if \(!reseed_block\) reseed_block = \d+;$',
    rb'^            else \{ reseed_steps = reseed_block; if \(reseed_block < \d+\) reseed_block \*= 2; \}$',
    rb'^            attempt_position = \(size_t\)window\[0\]\[0\];$',
    rb'^        \}$')]


def code_bytes(src):
    """src/core/compile.c emit_size_measure + emit_size_code, ported."""
    tot = prose = tables = 0; inc = False; intab = 0
    lines = src.split(b"\n")
    if src.endswith(b"\n"): lines = lines[:-1]
    for ln in lines:
        lb = len(ln) + 1; tot += lb; t = ln.lstrip(b" \t")
        if inc:
            prose += lb
            if b"*/" in ln: inc = False
        elif t.startswith(b"/*"):
            prose += lb
            if b"*/" not in ln[len(ln) - len(t) + 2:]: inc = True
        elif t.startswith(b"//"):
            prose += lb
        elif intab:
            tables += lb; intab = max(intab + ln.count(b"{") - ln.count(b"}"), 0)
        else:
            i = ln.find(b"[")
            if i >= 0 and re.search(rb"=\s*\{", ln[i:]):
                tables += lb; intab = max(ln.count(b"{") - ln.count(b"}"), 0)
    return max(tot - prose - tables, 0)


def diff_is_adaptive_text(nb, nn):
    removed, added = [], []
    for l in difflib.unified_diff(nb.split(b"\n"), nn.split(b"\n"), lineterm=b"", n=0):
        if l.startswith(b"---") or l.startswith(b"+++") or l.startswith(b"@@"): continue
        (removed if l.startswith(b"-") else added).append(l[1:])
    return not removed and len(added) == len(ADDED) and all(any(r.match(a) for r in ADDED) for a in added)


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
        return ("both-refuse", "-", "-", 0)
    if base is None or new is None or deny is None:
        return ("REFUSAL-MISMATCH", "-", "-", 0)
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
    elif moved and not diff_is_adaptive_text(nb, nn):
        verdict = "MOVER-EXTRA-TEXT"
    else:
        verdict = "mover" if moved else "identical"
    return (verdict, row, drow, code_bytes(new) - code_bytes(base))


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
    tally, rows, grow = {}, [], {}
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(one, a, p, e): (f, p, e) for f, p, e in work}
        for fu in concurrent.futures.as_completed(futs):
            f, p, e = futs[fu]
            try: v = fu.result()
            except Exception as x: v = ("ERROR:" + type(x).__name__, "-", "-", 0)
            rows.append((f, e, v, p))
            k = (e, v[0], v[1], v[2]); tally[k] = tally.get(k, 0) + 1
            gk = (e, v[1]); grow[gk] = grow.get(gk, 0) + v[3]
    with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as o:
        o.write("file\tenc\tverdict\trow\tdeny_row\tcode_delta\tpattern\n")
        for f, e, v, p in sorted(rows, key=lambda x: (x[0], x[1], x[3])):
            o.write(f"{f}\t{e}\t{v[0]}\t{v[1]}\t{v[2]}\t{v[3]}\t{p!r}\n")
    print(f"rows: {len(rows)} ({len(uniq)} unique patterns x 2 encodings)")
    for k in sorted(tally): print("  %-5s %-18s row=%-15s deny=%-8s %6d" % (k[0], k[1], k[2], k[3], tally[k]))
    print("code bytes gained (size model's measure), by encoding and row:")
    for k in sorted(grow):
        n = sum(tally[t] for t in tally if t[0] == k[0] and t[2] == k[1])
        if k[1] != "-": print("  %-5s row=%-15s artifacts=%5d total=%9d mean=%7.1f" % (k[0], k[1], n, grow[k], grow[k] / max(n, 1)))
    bad = sum(n for k, n in tally.items() if k[1] in ("DENY-DIFFERS", "ADAPTIVE-UNMOVED", "UNEXPECTED-MOVER", "MOVER-EXTRA-TEXT", "REFUSAL-MISMATCH") or k[1].startswith("ERROR"))
    print(f"violations: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
