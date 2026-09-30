#!/usr/bin/env python3
"""docs/dev/lanes/clspack_census.py -- [OPT-CLSPACK]'s mover census
(lane clspack, 2026-09-30; D131 item 6).

WHAT IT MEASURES. For every corpus `pattern`/`pattern-esc` line (emit_sweep.py's
own enumeration, `-p rx --features all`, byte encoding) on two engine arms
(default selection, forced `--engine=vm`), one artifact from a BASELINE binary:
how many per-site 32-byte class bitmaps it emits (`rx_class_bitmapN[32]`) and
how many atoms the partition of those N byte sets has. The PREDICTED movers are
the artifacts where the shared atom table's row fires on that data:
N >= 11 and atoms <= 64 (clskit.c PLACE.atom_min_sites / atom_max). The byte
sets are parsed off the baseline's OWN emitted tables, never re-derived from
the pattern -- so the prediction does not share a source with the emitter
change it checks.

With --cand BIN the same artifacts are compiled by a CANDIDATE binary and each
row is classified: identical / moved, and whether the move is predicted. The
acceptance is `moved == predicted` exactly, BY ID, plus every moved candidate
artifact carrying `rx_class_atoms[256]` and no `rx_class_bitmap`.

USAGE
  python3 docs/dev/lanes/clspack_census.py --base BIN [--cand BIN] [--jobs N]
      [--out TSV]
"""
import argparse
import concurrent.futures
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(TREE, "scripts"))
import emit_sweep  # noqa: E402

TAB_RE = re.compile(rb"static const unsigned char rx_class_bitmap(\d+)\[32\] = \{([^}]*)\};")
MIN_SITES, MAX_ATOMS = 11, 64


def tables(art):
    """The artifact's per-site bitmaps, as 256-bit membership lists."""
    out = []
    for m in TAB_RE.finditer(art):
        vals = [int(x) for x in m.group(2).replace(b",", b" ").split()]
        assert len(vals) == 32, m.group(1)
        out.append([(vals[b >> 3] >> (b & 7)) & 1 for b in range(256)])
    return out


def natoms(sets):
    return len({tuple(s[b] for s in sets) for b in range(256)})


def one(args):
    base, cand, pat, engine = args
    ok, art, _ = emit_sweep.compile_stream_c(base, pat, 60, engine)
    if not ok:
        return None
    sets = tables(art)
    n = len(sets)
    na = natoms(sets) if n else 0
    pred = n >= MIN_SITES and na <= MAX_ATOMS
    moved = cok = None
    if cand:
        cok, cart, _ = emit_sweep.compile_stream_c(cand, pat, 60, engine)
        moved = (not cok) or cart != art
        if cok and moved:
            cok = b"rx_class_atoms[256]" in cart and b"rx_class_bitmap" not in cart
    return (engine or "default", n, na, pred, moved, cok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cand")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()
    pats = emit_sweep.enumerate_corpus(a.base, TREE, 60)
    uniq = sorted({p for _, _, p in pats})
    work = [(a.base, a.cand, p, e) for p in uniq for e in (None, "vm")]
    rows = []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for (b, c, p, e), r in zip(work, ex.map(one, work)):
            rows.append((p, r))
    comp = [(p, r) for p, r in rows if r]
    hist = {}
    for _, r in comp:
        hist[(r[0], min(r[1], 11))] = hist.get((r[0], min(r[1], 11)), 0) + 1
    print(f"patterns {len(uniq)}  artifacts {len(work)}  compiled {len(comp)}")
    for eng in ("default", "vm"):
        line = " ".join(f"{k}:{hist.get((eng, k), 0)}" for k in range(12))
        print(f"  [{eng}] per-site bitmap count histogram (11 = >=11): {line}")
    pred = [(p, r) for p, r in comp if r[3]]
    over = [(p, r) for p, r in comp if r[1] >= MIN_SITES and r[2] > MAX_ATOMS]
    print(f"predicted movers {len(pred)} "
          f"(default {sum(1 for _, r in pred if r[0] == 'default')}, "
          f"vm {sum(1 for _, r in pred if r[0] == 'vm')}); "
          f">= {MIN_SITES} sites but > {MAX_ATOMS} atoms: {len(over)}")
    rc = 0
    if a.cand:
        moved = [(p, r) for p, r in comp if r[4]]
        unpred = [(p, r) for p, r in moved if not r[3]]
        missed = [(p, r) for p, r in pred if not r[4]]
        badform = [(p, r) for p, r in moved if not r[5]]
        print(f"moved {len(moved)}  unpredicted {len(unpred)}  "
              f"predicted-but-unmoved {len(missed)}  moved-without-atom-form {len(badform)}")
        for p, r in (unpred + missed + badform)[:20]:
            print(f"  ! {r} {p[:100]!r}")
        rc = 1 if (unpred or missed or badform or not pred) else 0
    if a.out:
        with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as f:
            f.write("engine\tsites\tatoms\tpredicted\tmoved\tpattern\n")
            for p, r in comp:
                if r[1] >= MIN_SITES:
                    f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{int(r[3])}\t{r[4]}\t{p!r}\n")
    sys.exit(rc)


if __name__ == "__main__":
    main()
