#!/usr/bin/env python3
"""tests/memfn/g1_span_vector.py -- G1 ALPHA's MANIFEST and DRY RUN for the `span-vector` row
(R-47 U6; docs/design/memfn/block_span.md §9.4, integration.md §17.2). pcrec's side of G1:
the movers are the artifacts whose DEFAULT compile differs byte for byte from the same
pattern's `--memfn=no-span-vector` compile, at BOTH layers (`-fno-memfn-simd`, i.e. no flag, and
`-fmemfn-simd=x86-64-v3`). It reads NOTHING of the kit's (`mf_result.moved` plays no part):
the population is two compiles of pcrec's own binary and a byte compare.

  g1_span_vector.py manifest --pcrec BIN --root TREE --bench BENCH_DIR --out DIR [--jobs N]
      compiles every distinct corpus pattern (every .rxt under TREE/tests, with its source
      files kept) and every bench pattern file (BENCH_DIR/*/patterns/*.rx, read only) at both
      layers x both encodings x both streams (the cells tests/axes/memfn_arm.py reads), default
      vs deny, and writes DIR/manifest.tsv, one row per (pattern, layer) that MOVES in at least
      one cell: written by the compile pass, never filtered by an outcome.
  g1_span_vector.py dry --out DIR
      reads the manifest: prints the per-layer population (real, SPAN-SEED-only, bench), the
      (op, length decade) bins over REAL movers only (the corpus less tests/memfn/span_seed.rxt
      by path, plus the bench), floor 8 -> `UNREACHED (n < 8)`, the SPAN-SEED floor witness
      (its movers must appear, so the manifest is not empty-blind, K35). It TIMES NOTHING:
      no window is booked (the real population is 3 sites, §9.4); the trigger to time is a bin
      reaching 8 real movers. Exit 0 = the dry run's checks hold, 1 = a check failed.

op and length are read OFF THE DEFAULT ARTIFACT's added lines (the lines the default compile
has and the deny compile does not): op `window` when an added line indexes a skip table
(`_sh[`), else `scan`; length = 1 + the largest `_c + N` offset in those lines (hex32 reads
32). They are a binning label, never a verdict. SPAN_SEED_REL is the one excluded path.
"""
import argparse, os, re, sys, subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SPAN_SEED_REL = "tests/memfn/span_seed.rxt"
FLOOR = 8
LAYERS = {"off": [], "on": ["-fmemfn-simd=x86-64-v3"]}
ENCS = {"byte": [], "utf8": ["-e", "utf8"]}
STREAMS = {"c-default": [], "c-vm": ["--engine=vm"]}
DENY = "--memfn=no-span-vector"
TIMEOUT = 60
REAL_BENCH = (b"[0-9a-f]{32}", b"\\b[0-9a-f]{32}\\b", b"\\d{32}")   # block_span.md §0.1, the 3 real sites
HDR = ["pattern_hex", "layer", "source", "cells", "op", "length", "decade", "pattern"]


def decade(n):
    if n <= 0:
        return "0"
    lo = 1
    while lo * 10 <= n:
        lo *= 10
    return "%d-%d" % (lo, lo * 10 - 1)


def compile_c(pcrec, pattern, flags):
    argv = [pcrec, "-p", "rx", "--features", "all"] + flags + ["-o", "-", "--pattern", pattern.decode("utf-8", "surrogateescape")]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    return r.stdout if r.returncode == 0 else None


def classify(default, deny):
    """(op, length) from the default artifact's lines the deny artifact lacks."""
    have = set(deny.split(b"\n"))
    added = [l for l in default.split(b"\n") if l not in have and l.strip()]
    op = "window" if any(b"_sh[" in l for l in added) else "scan"
    offs = [int(m) for l in added for m in re.findall(rb"_c \+ (\d+)", l)]
    return op, (max(offs) + 1 if offs else 0)


def cmd_manifest(a):
    sys.path.insert(0, os.path.join(a.root, "scripts"))
    import emit_sweep as es
    src = {}                                   # pattern bytes -> set of source labels
    for rel, _kind, pat in es.enumerate_corpus(a.pcrec, a.root, 60):
        src.setdefault(pat, set()).add(rel)
    nbench = 0
    for d in sorted(os.listdir(a.bench)):
        pd = os.path.join(a.bench, d, "patterns")
        if not os.path.isdir(pd):
            continue
        for f in sorted(os.listdir(pd)):
            if f.endswith(".rx"):
                with open(os.path.join(pd, f), "rb") as fh:
                    p = fh.read()
                p = p[:-1] if p.endswith(b"\n") else p
                src.setdefault(p, set()).add("bench:%s/%s" % (d, f))
                nbench += 1
    pats = sorted(src)
    print("g1 manifest: %d distinct patterns (%d bench files), pcrec %s" % (len(pats), nbench, a.pcrec), flush=True)
    cells = [(ln, lf, en, ef, st, sf) for ln, lf in LAYERS.items() for en, ef in ENCS.items() for st, sf in STREAMS.items()]

    def one(p):
        out = {}                                # layer -> (cells moved, op, length)
        for ln, lf, en, ef, st, sf in cells:
            fl = lf + ef + sf
            d = compile_c(a.pcrec, p, fl)
            n = compile_c(a.pcrec, p, fl + [DENY])
            if d is None or n is None or d == n:
                continue
            cur = out.get(ln)
            op, length = classify(d, n)
            tag = "%s/%s" % (en, st)
            out[ln] = ((cur[0] + [tag]) if cur else [tag], op if not cur else cur[1], max(length, cur[2]) if cur else length)
        return p, out

    os.makedirs(a.out, exist_ok=True)
    rows = []
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for p, out in ex.map(one, pats):
            for ln, (tags, op, length) in sorted(out.items()):
                s = src[p]
                rest = s - {SPAN_SEED_REL}            # the path exclusion: what is left is REAL
                if not rest:
                    label = "seed"
                elif all(x.startswith("bench:") for x in rest):
                    label = "bench"
                elif not any(x.startswith("bench:") for x in rest):
                    label = "corpus"
                else:
                    label = "corpus+bench"
                rows.append((p, ln, label, ",".join(tags), op, length, decade(length)))
    with open(os.path.join(a.out, "manifest.tsv"), "w") as fh:
        fh.write("#g1 span-vector manifest; compile pass over %d patterns; pcrec=%s; floor=%d; excluded path %s\n" % (len(pats), a.pcrec, FLOOR, SPAN_SEED_REL))
        fh.write("\t".join(HDR) + "\n")
        for p, ln, label, tags, op, length, dec in rows:
            fh.write("\t".join([p.hex(), ln, label, tags, op, str(length), dec, repr(p)[2:-1]]) + "\n")
    print("g1 manifest: wrote %s (%d rows)" % (os.path.join(a.out, "manifest.tsv"), len(rows)))
    return 0


def read_manifest(out):
    rows, header = [], None
    with open(os.path.join(out, "manifest.tsv")) as fh:
        meta = fh.readline()
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            rows.append(dict(zip(header, f)))
    return meta, header, rows


def cmd_dry(a):
    meta, header, rows = read_manifest(a.out)
    bad = []
    if header != HDR:
        bad.append("manifest header %r != %r" % (header, HDR))
    print(meta.strip())
    for ln in LAYERS:
        lr = [r for r in rows if r["layer"] == ln]
        real = [r for r in lr if r["source"] != "seed"]
        seed = [r for r in lr if r["source"] == "seed"]
        print("layer %-3s movers: %d distinct patterns | real %d (corpus %d, bench %d, both %d) | SPAN-SEED-only %d"
              % (ln, len(lr), len(real), sum(r["source"] == "corpus" for r in lr), sum(r["source"] == "bench" for r in lr),
                 sum(r["source"] == "corpus+bench" for r in lr), len(seed)))
        bins = {}
        for r in real:
            bins.setdefault((r["op"], r["decade"]), []).append(r)
        if not bins:
            print("layer %-3s bins: none (no real mover)" % ln)
        for k, v in sorted(bins.items()):
            print("layer %-3s bin (%s, %s): %d real movers -> %s" % (ln, k[0], k[1], len(v), "REACHED" if len(v) >= FLOOR else "UNREACHED (n < %d)" % FLOOR))
        for r in real:
            print("layer %-3s   real mover: %-9s %-12s %s [%s]" % (ln, r["source"], r["op"], bytes.fromhex(r["pattern_hex"]).decode("utf-8", "replace"), r["cells"]))
        # K35: the floor witness. SPAN-SEED's V sites must appear, or the manifest is empty-blind.
        if len(seed) == 0:
            bad.append("layer %s: SPAN-SEED floor witness is EMPTY (the manifest would be blind)" % ln)
        # the 3 real bench sites must be real movers at both layers (§0.1)
        for p in REAL_BENCH:
            if not any(bytes.fromhex(r["pattern_hex"]) == p for r in real):
                bad.append("layer %s: real site %r is not a mover" % (ln, p))
        print("layer %-3s floor witness: SPAN-SEED movers %d" % (ln, len(seed)))
    print("timing: NOT RUN (no window booked, block_span.md §9.4); trigger: a bin reaches %d real movers" % FLOOR)
    for b in bad:
        print("G1 DRY FAIL: " + b)
    print("g1 dry: %s" % ("FAIL" if bad else "OK"))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest")
    m.add_argument("--pcrec", required=True)
    m.add_argument("--root", required=True)
    m.add_argument("--bench", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    d = sub.add_parser("dry")
    d.add_argument("--out", required=True)
    a = ap.parse_args()
    return cmd_manifest(a) if a.cmd == "manifest" else cmd_dry(a)


if __name__ == "__main__":
    sys.exit(main())
