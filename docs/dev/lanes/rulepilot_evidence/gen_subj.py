#!/usr/bin/env python3
"""rulepilot step 3, the SUBJECTS of one site (docs/design/pricing_rulepilot.md §4).

Derived from the site's own question: its source is the FIRST file the question names
(docs/dev/lanes/rwquest/questions.tsv `files`, under worktrees/.corpus/; never `sealed/`), as the
E8 slot did. Every subject is STREAMED (grid2's streamgen.py: a directory of distinct buffers,
nbuf_for(L) of them, 4 MiB of distinct data per subject, 16..1024 buffers), one per
(regime, length):

  LENGTHS  64 B, 8 KiB, 1 MiB: x128 apart (3 points; the x8 grid of 6 points, 32 B .. 1 MiB, was
           CUT to fit the timing budget, pricing_rulepilot.md §4). The cap: at 1 MiB a find-all call's fixed costs
           (entry, setup, the first search) are below 0.1 % of its time for every arm whose
           per-byte time is at least 0.1 ns, and 16 buffers of 1 MiB already leave the 1 MiB L2,
           so a longer subject repeats the 1 MiB point's per-byte regime: lengths above it read
           as "large" (CHOSEN; the per-length crossovers are reported to check it).
  miss     the SPARSE regime: 4 x nbuf candidate windows of the source (streamgen's
           strata-spread offsets), the nbuf with the FEWEST matches kept (counted by the site's
           default arm `chk`). For a rare question these are no-match windows; for an
           everywhere question the least dense the file has. Density is COUNTED and recorded.
  dense    the MATCH-DENSE regime: every match in the source's first 4 MiB, widened to its
           line (at most 120 bytes each side), alternated with an equal-length filler window of
           the source at a seeded random offset, cut into nbuf consecutive windows. A question
           with no match in its first 4 MiB has no dense regime (recorded; its headline is the
           miss regime alone).

usage: gen_subj.py OUT ID SRC CHK        writes OUT/subj/rp_<ID>_{m,d}<L>-S/ and appends to
                                         OUT/subj_rp.tsv: id regime L nbuf bytes matches
"""
import hashlib, os, random, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "grid2"))
import streamgen  # noqa: E402

LENS = [64, 8192, 1048576]
HARVEST = 4 << 20
CTX = 120
CAND = 4

def count(chk, d):
    """-> per-buffer match counts (chk DIR list all prints `buf K matches=M ...`)."""
    p = subprocess.run(["gnutimeout", "600", chk, d, "list", "all"], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(f"gen_subj: chk failed on {d}: {p.stderr[-300:]}")
    return [int(m.group(1)) for m in re.finditer(r"^buf \d+ matches=(\d+)", p.stdout, re.M)]

def uniq(bufs):
    seen, out = set(), []
    for b in bufs:
        h = hashlib.sha256(b).digest()
        if h not in seen:
            seen.add(h); out.append(b)
    return out

def miss(out, ident, data, chk, L, tmp):
    nb = streamgen.nbuf_for(L)
    offs = streamgen.window_offsets(len(data), L, CAND * nb, f"rp/{ident}/m{L}")
    cand = uniq([data[o:o + L] for o in offs])
    cd = os.path.join(tmp, f"m{L}")
    streamgen.write_stream(cd, cand)
    k = count(chk, cd)
    keep_idx = sorted(range(len(cand)), key=lambda i: (k[i], i))[:nb]
    keep = [cand[i] for i in sorted(keep_idx)]          # stream order = file order
    return keep

def dense_text(ident, data, chk, need, tmp):
    head = data[:HARVEST]
    hf = os.path.join(tmp, "head")
    open(hf, "wb").write(head)
    p = subprocess.run(["gnutimeout", "600", chk, hf, "list", "all"], capture_output=True, text=True)
    spans = [(int(a), int(b)) for a, b in re.findall(r"^(\d+) (\d+)$", p.stdout, re.M)]
    chunks = []
    for s, e in spans[:200000]:
        a = head.rfind(b"\n", max(0, s - CTX), s); a = max(0, s - CTX) if a < 0 else a + 1
        b = head.find(b"\n", e, e + CTX); b = min(len(head), e + CTX) if b < 0 else b + 1
        chunks.append(head[a:b])
    chunks = uniq(chunks)[:4096]
    if not chunks:
        return None
    rng = random.Random(f"rp/{ident}/dense")
    parts, n = [], 0
    while n < need:
        c = rng.choice(chunks); o = rng.randrange(0, max(1, len(data) - len(c)))
        f = data[o:o + len(c)]
        parts += [c, f]; n += 2 * len(c)
    return b"".join(parts)

def main():
    out, ident, src, chk = sys.argv[1:5]
    data = open(src, "rb").read()
    tmp = tempfile.mkdtemp(prefix=f"rp_{ident}_", dir=os.path.join(out, "tmp"))
    rows = []
    for L in LENS:
        if len(data) < L:
            continue
        d = os.path.join(out, "subj", f"rp_{ident}_m{L}-S")
        n = streamgen.write_stream(d, miss(out, ident, data, chk, L, tmp))
        rows.append((ident, "miss", L, n, n * L, sum(count(chk, d))))
    need = max(streamgen.nbuf_for(L) * L for L in LENS) + max(LENS)
    D = dense_text(ident, data, chk, need, tmp)
    if D is not None:
        for L in LENS:
            nb = streamgen.nbuf_for(L)
            bufs = uniq([D[k * L:(k + 1) * L] for k in range(nb)])
            d = os.path.join(out, "subj", f"rp_{ident}_d{L}-S")
            n = streamgen.write_stream(d, bufs)
            rows.append((ident, "dense", L, n, n * L, sum(count(chk, d))))
    shutil.rmtree(tmp)
    with open(os.path.join(out, "subj_rp.tsv"), "a") as f:
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print(f"gen_subj {ident}: " + " ".join(f"{r[1][0]}{r[2]}:{r[3]}x{r[5]}m" for r in rows))

if __name__ == "__main__":
    main()
