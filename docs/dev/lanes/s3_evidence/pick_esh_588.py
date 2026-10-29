#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/pick_esh_588.py -- job 588's D-HORS ADMISSION SITES (Frank's ruling
2026-10-23: measure D-hors's admission on E[sh] instead of the withdrawn max(sh) == 1 decline):
about 12 D-hors sites stratified by E[sh], written to esh_588.tsv (committed; job 588 reads it,
never re-picks).

    python3 -I pick_esh_588.py --new BIN --tree DIR --out esh_588.tsv [--seed N] [--want N] [--jobs N]

CANDIDATES: the census's D-hors movers (every distinct corpus pattern, scripts/emit_sweep.py's
enumeration, whose default artifact reads `RX_DFA_SCAN "cover"` AND carries a `_sh[256]` table:
census.py's `hors` count) plus the HAND list below (windows of chosen density and length, so the
strata are populated: the corpus holds only a handful of D-hors movers). §6's eight cells are
excluded (hex8-bounded is timed there, NOH included); its E[sh] is the top of the span. Every
candidate must be D-hors on NEW and generatable (gen_sample_588's `real` class: python `re` reads
it and a generated match verifies).

E[sh], max(sh) and the stop mass are esh_588.py's (the default byte-rate prior,
tests/findings/default_ppm.tsv; kit_set_mass's sum).

THE STRATA by E[sh], with HEX8 = E[sh] of §6's hex8-bounded cell on NEW:
  e1   E[sh] == 1 exactly (every shift 1): `(?s)[^a]..` and `(?s)[0-9a-f].[0-9a-f]` are FORCED
  b1   1 < E < 1.5     b2   1.5 <= E < 2.5     b3   2.5 <= E < 3.5
  b4   3.5 <= E < 5    b5   5 <= E <= HEX8
THE PICK: the forced rows first; then random.Random(seed) over each stratum's sorted candidates,
round robin over the strata in order, until WANT rows or the candidates run out.
"""
import argparse
import concurrent.futures
import importlib.util
import os
import random
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(here, fn))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gsp = _load("gsp", "gen_sample_588.py")
esh = _load("esh", "esh_588.py")

FORCED = [rb"(?s)[^a]..", rb"(?s)[0-9a-f].[0-9a-f]"]
HAND = [rb"[0-9a-f].[0-9a-f]", rb"[0-9a-f]{2}", rb"[0-9a-f]{3}", rb"[0-9a-f]{4}", rb"[0-9a-f]{5}",
        rb"[0-9a-f]{6}", rb"[0-9a-f]{7}", rb"[0-9a-f]{8}", rb"[0-9A-F]{6}", rb"[a-z]{3}", rb"[a-z]{4}",
        rb"[a-z]{6}", rb"\w{3}", rb"\w{5}", rb"[^ ]{3}", rb"[aeiou]..[aeiou]", rb"[ e]...",
        rb"[0-9a-f]-[0-9a-f]{2}", rb"[a-z][a-z0-9]{3}"]
HEX8 = rb"\b[0-9a-f]{8}\b"
COVER = b'#define RX_DFA_SCAN "cover"'


def stratum(e, top):
    if abs(e - 1.0) < 1e-9:
        return "e1"
    for name, hi in (("b1", 1.5), ("b2", 2.5), ("b3", 3.5), ("b4", 5.0)):
        if e < hi:
            return name
    return "b5" if e <= top + 1e-9 else None


def is_hors_mover(task):
    bin_, pat = task
    r = subprocess.run([bin_, "-p", "rx", "--features", "all", "-o", "-", "--pattern", pat],
                       capture_output=True, timeout=60)
    return pat, r.returncode == 0 and COVER in r.stdout and b"_sh[256]" in r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--want", type=int, default=12)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402
    rate = esh.prior()
    cells = set()
    for ln in open(os.path.join(a.tree, "docs/design/kit_proof/measure/cells.tsv")):
        if ln.strip() and not ln.startswith("#"):
            cells.add(ln.rstrip("\n").split("\t")[1].encode())
    pats = sorted(set(p for _, _, p in emit_sweep.enumerate_corpus(a.new, a.tree, 60)) - cells)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        corpus = [p for p, h in ex.map(is_hors_mover, [(a.new, p) for p in pats], chunksize=16) if h]
    top = esh.site(a.new, HEX8, rate)["esh"]
    cand, notes = {}, []
    for src, plist in (("forced", FORCED), ("corpus", corpus), ("hand", HAND)):
        for p in plist:
            if p in cand or p in cells:
                continue
            s = esh.site(a.new, p, rate)
            if not s.get("hors") or s.get("mass") is None:
                notes.append("%s %s: %s" % (src, emit_sweep.encode_escape(p), s.get("why") or "no stop mass"))
                continue
            rx = gsp.compiles(p)
            if rx is None or gsp.match_of(p, rx, random.Random(0)) is None:
                notes.append("%s %s: not generatable" % (src, emit_sweep.encode_escape(p)))
                continue
            st = stratum(s["esh"], top)
            if st is None:
                notes.append("%s %s: E[sh] %.3f above hex8's %.3f" % (src, emit_sweep.encode_escape(p), s["esh"], top))
                continue
            cand[p] = (src, st, s)
    keys = ["e1", "b1", "b2", "b3", "b4", "b5"]
    pool = {k: sorted(p for p, v in cand.items() if v[1] == k and v[0] != "forced") for k in keys}
    rng = random.Random(a.seed)
    for k in keys:
        rng.shuffle(pool[k])
    picked = [p for p in FORCED if p in cand]
    while len(picked) < a.want and any(pool[k] for k in keys):
        for k in keys:
            if pool[k] and len(picked) < a.want:
                picked.append(pool[k].pop(0))
    picked.sort(key=lambda p: (cand[p][2]["esh"], p))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("# docs/dev/lanes/s3_evidence/esh_588.tsv -- job 588's D-HORS ADMISSION SITES (the E[sh]\n"
                "# reading; findings only, never the §6 bar), written by pick_esh_588.py (its header is the\n"
                "# rule); do not edit by hand. E[sh], max(sh), stop mass: esh_588.py on NEW, prior\n"
                "# tests/findings/default_ppm.tsv.\n"
                "# corpus patterns %d (§6's cells excluded), corpus D-hors movers %d, hand %d, candidates %d,\n"
                "# seed %d, want %d, picked %d; hex8-bounded E[sh] %.3f (the span's top)\n"
                % (len(pats), len(corpus), len(HAND), len(cand), a.seed, a.want, len(picked), top))
        for k in keys:
            f.write("# stratum %s: candidates %d, picked %d\n"
                    % (k, sum(1 for v in cand.values() if v[1] == k), sum(1 for p in picked if cand[p][1] == k)))
        for n in notes:
            f.write("# dropped: %s\n" % n)
        f.write("#id\tstratum\tpattern\tesh\tmaxsh\tstop_mass_ppm\tsource\n")
        for i, p in enumerate(picked):
            src, st, s = cand[p]
            f.write("esh%02d\t%s\t%s\t%.3f\t%d\t%d\t%s\n"
                    % (i + 1, st, emit_sweep.encode_escape(p), s["esh"], s["maxsh"], s["mass"], src))
    print("pick_esh_588: %d corpus patterns, %d corpus D-hors movers, %d candidates, %d picked -> %s"
          % (len(pats), len(corpus), len(cand), len(picked), a.out))


if __name__ == "__main__":
    main()
