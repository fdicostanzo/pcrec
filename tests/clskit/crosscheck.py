#!/usr/bin/env python3
"""tests/clskit/crosscheck.py — the kit in src/ against the STUDY, set by set.

`clskit_driver dump` prints what src/gen/clskit.c decides; this script
recomputes the same decisions with a FROZEN COPY of the study's reference
code (tests/clskit/ref/: `section.partition`, `wholeset.PageW2/PageW3`,
`bench_bytes.atom_partition` — see that directory's own provenance headers;
the live source is studies/cls_tree_study/, never imported here — docs/
CLAUDE.md's "studies/ ... never built or tested by pcrec's make", clss1b's
fix) and compares (design §6's S1 row: "a C-vs-study cross-check of
sectionings and table choices"; the study's own crosscheck.py found two
bugs this way, cls_tree_study.md §8).

What is compared, per set:
  SEC    the sectioning at each λ: section starts, leaf forms, model bytes.
         Two sectionings whose objective agrees to 1e-6 under the study's
         own pricing are an exact TIE (the float DP breaks it by rounding,
         the Q16 DP by loop order), reported on a TIE line and counted
  WHOLE  the P3 / P2 / B1 model bytes (rodata counted by the study's own
         table builders, plus the measured text constants)
  ATOMS  the shared atom table's atom count
  SEL    the --tune class-form choice at every position, with no deny and
         with each single row denied. The TABLE is restated below from
         D131 item 1 and items 4-5, independently of clskit.c's ROWS (NO
         atom row — D131 item 6's atom table is an ARTIFACT-level choice,
         not a per-set one; see clskit.c's own comment above `ROWS`); the
         printed ROW lines are held to it too, so the two statements of the
         table cannot drift apart silently.

The study's DP is floating point and clskit.c's is Q16 fixed point, so a
disagreement could in principle be a rounding tie. The study's CUBES is run
at tier 1 only (TIER2 = False), which is the tier the design ships (CT-1).

Usage: crosscheck.py POPFILE DUMPFILE [--lams 0,4,16,256] [--full-lam 4]
       [--procs N]. Prints one line per disagreement and a summary;
       exits 1 on any disagreement or on an empty population.
"""

import argparse
import multiprocessing
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref")
sys.path.insert(0, REF)

import kit          # noqa: E402
import section      # noqa: E402
import wholeset     # noqa: E402
import bench_bytes  # noqa: E402

kit.FormCubes.TIER2 = False

# The measured whole-set .text constants (whole_k53.tsv obj - rodata;
# bitmap1 per clsfit_report.md) and the ruled placements (D131).
P3_TEXT, P2_TEXT, B1_TEXT = 88, 68, 60
KIT_LAMBDA = 4
MID_MIN_SECTIONS, Z_MID_PCT = 16, 126

# D131 ADDENDUM 1's fitted cell (clskit.c PLACE.kit_disp_bytes's own
# comment carries the fit): K's DP-model bytes run a constant ~578 B below
# the measured object (the sectioned matcher's own dispatch tree and
# prologue, which the model omits), fit as `measured - model` over the K53
# twelve at lambda=4. The SELECTION's comparisons of K's bytes against
# another form read `kbytes + KIT_DISP_BYTES`; the DP's own sectioning
# bytes (`kbytes` itself, `price()`, `study_one()`) are never adjusted.
KIT_DISP_BYTES = 578

# THE TABLE, restated: (name, positions, predicate, form, deny ordinal).
# NO atom row: D131 item 6's atom table is chosen ARTIFACT-wide (S2), which
# a per-SET table has no input to decide (clskit.c's own comment above
# `ROWS`) — so it is not part of this per-set restatement either.
SIZE, MID, SPEED = (-2, -1), (0, 1, 2), (2,)
ALLPOS = (-2, -1, 0, 1, 2)
ROWS = [
    ("byte-kit",      SIZE,   "byte",   "K",    1),
    ("byte-table",    MID,    "byte",   "B1",   2),
    ("size-page3",    SIZE,   "p3<k",   "P3",   3),
    ("speed-page2",   SPEED,  "mid&p2", "P2",   4),
    ("speed-bitmap1", SPEED,  "mid&b1", "B1",   5),
    ("mid-page3",     MID,    "mid",    "P3",   6),
    ("kit",           ALLPOS, "true",   "K",    0),
]
NDENY = 7


def load_pop(path):
    sets = []
    for line in open(path):
        f = line.split()
        if not f or f[0] != "SET":
            continue
        iv = [tuple(int(x, 16) for x in p.split(":")) for p in f[4:]]
        sets.append((int(f[1]), f[2], f[3], iv))
    return sets


def whole_bytes(iv):
    if not iv:
        return 0, 0, 0
    return (wholeset.PageW3(iv).rodata() + P3_TEXT,
            wholeset.PageW2(iv).rodata() + P2_TEXT,
            (iv[-1][1] - iv[0][0] + 1 + 7) // 8 + B1_TEXT)


def select(iv, kbytes, knsec, whole, tune, deny):
    p3, p2, b1 = whole
    byte = not iv or iv[-1][1] <= 0xFF
    ksel = kbytes + KIT_DISP_BYTES
    mid = knsec >= MID_MIN_SECTIONS and p3 * 100 <= Z_MID_PCT * ksel
    holds = {"byte": byte, "p3<k": p3 < ksel,
             "mid&p2": mid and p2 <= b1, "mid&b1": mid and b1 < p2,
             "mid": mid, "true": True}
    for name, pos, pred, form, d in ROWS:
        if tune not in pos or (d and d == deny):
            continue
        if holds[pred]:
            return name, form
    raise AssertionError("no row fired")


def price(iv, marks, lam):
    """The study's own objective for a sectioning given as `start:FORM`
    marks: sum of (rodata + text) + lam * (ops + DISP_OPS), priced by the
    study's kit classes. Used to tell a TIE from a disagreement."""
    starts = [int(m.split(":")[0]) for m in marks] + [len(iv)]
    byname = {F.name: F for F in kit.KIT}
    total = 0.0
    for z, m in enumerate(marks):
        sec = iv[starts[z]:starts[z + 1]]
        f = byname[m.split(":")[1]](sec)
        total += f.rodata() + kit.text_cost(f.name, len(sec)) \
            + lam * (f.ops() + section.DISP_OPS)
    return total


def study_one(job):
    idx, iv, lams = job
    out = {}
    for lam in lams:
        if not iv:
            out[lam] = (0, [])
            continue
        secs, ro_tot, _ops, forms = section.partition(iv, lam)
        out[lam] = (int(round(ro_tot)),
                    ["%d:%s" % (i, fm) for (i, _j), fm in zip(secs, forms)])
    return idx, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pop")
    ap.add_argument("dump")
    ap.add_argument("--lams", default="0,4,16,256",
                    help="lambdas compared on the non-prop sets")
    ap.add_argument("--prop-lams", default="4",
                    help="lambdas compared on the proptest sets")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()

    sets = load_pop(a.pop)
    lams = [int(x) for x in a.lams.split(",")]
    plams = [int(x) for x in a.prop_lams.split(",")]
    if KIT_LAMBDA not in lams or KIT_LAMBDA not in plams:
        sys.exit("crosscheck: the table's lambda %d must be compared" % KIT_LAMBDA)

    dsec, dwhole, dsel, drows, datoms = {}, {}, {}, [], None
    for line in open(a.dump):
        f = line.split()
        if not f:
            continue
        if f[0] == "SEC":
            dsec[(int(f[1]), int(f[2]))] = (int(f[3]), f[4:])
        elif f[0] == "WHOLE":
            dwhole[int(f[1])] = tuple(int(x) for x in f[2:5])
        elif f[0] == "SEL":
            dsel[(int(f[1]), int(f[2]), int(f[3]))] = (f[4], f[5])
        elif f[0] == "ROW":
            drows.append((f[2], f[3], int(f[4].split("=")[1])))
        elif f[0] == "ATOMS":
            datoms = dict(kv.split("=") for kv in f[1:])

    bad = 0

    def fail(msg):
        nonlocal bad
        bad += 1
        if bad <= 40:
            print("DIFFER " + msg)

    # the table listing against the restatement
    want_rows = [(n, fm, d) for n, _p, _q, fm, d in ROWS]
    if drows != want_rows:
        fail("ROWS: clskit.c lists %s, the restatement is %s" % (drows, want_rows))

    # atoms: the study's partition over the same byte sets
    bytesets = [frozenset(b for l, h in iv for b in range(l, h + 1))
                for _i, kind, _n, iv in sets if kind == "byte"]
    shared = int(datoms["shared"]) if datoms else 0
    if shared:
        _a, _m, n_atoms = bench_bytes.atom_partition(bytesets[:shared])
        if n_atoms != int(datoms["natoms"]):
            fail("ATOMS: clskit.c %s, study %d" % (datoms["natoms"], n_atoms))

    jobs = [(idx, iv, plams if kind == "prop" else lams)
            for idx, kind, _n, iv in sets]
    with multiprocessing.Pool(a.procs) as pool:
        study = dict(pool.map(study_one, jobs, chunksize=4))

    nsec = nsel = nties = 0
    for idx, kind, name, iv in sets:
        for lam, (sbytes, sforms) in study[idx].items():
            got = dsec.get((idx, lam))
            nsec += 1
            if got is None:
                fail("SEC %s lam=%d: missing from the dump" % (name, lam))
            elif got != (sbytes, sforms) and got[0] == sbytes and \
                    abs(price(iv, got[1], lam) - price(iv, sforms, lam)) < 1e-6:
                # Two sectionings with the same objective to 1e-6: an exact
                # tie that the study's float DP broke by rounding and the
                # Q16 DP by its loop order. Counted, never silent.
                nties += 1
                print("TIE %s lam=%d: %s vs study %s" % (name, lam, got[1], sforms))
            elif got != (sbytes, sforms):
                fail("SEC %s lam=%d: clskit %d bytes %d sections, study %d bytes %d sections%s"
                     % (name, lam, got[0], len(got[1]), sbytes, len(sforms),
                        "" if got[1] == sforms else " (sectioning differs)"))
        w = whole_bytes(iv)
        if dwhole.get(idx) != w:
            fail("WHOLE %s: clskit %s, study %s" % (name, dwhole.get(idx), w))
        kbytes, kforms = study[idx][KIT_LAMBDA]
        for tune in range(-2, 3):
            for d in range(NDENY):
                want = select(iv, kbytes, len(kforms), w, tune, d)
                got = dsel.get((idx, tune, d))
                nsel += 1
                if got != want:
                    fail("SEL %s tune=%d deny=%d: clskit %s, restatement %s"
                         % (name, tune, d, got, want))

    print("crosscheck: %d sets, %d sectionings, %d selections, %d rows; "
          "atoms shared=%s natoms=%s; ties=%d; disagreements=%d"
          % (len(sets), nsec, nsel, len(drows), shared,
             datoms and datoms["natoms"], nties, bad))
    if not sets or not nsec or not nsel:
        print("crosscheck: EMPTY POPULATION")
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
