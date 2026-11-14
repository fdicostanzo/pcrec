#!/usr/bin/env python3
"""tests/axes/memfn_arm.py -- the `--memfn=` ARM of `make test-axes`
([RUNAXES], lane runaxes, 2026-10-16; tests/axes/run_axes.sh's header).

THE GAP IT CLOSES. run_axes.sh sweeps every pcrec deny/force flag and
compares ANSWERS, but the kit's own per-form denies (`--memfn=no-NAME`, the
`memfn` section of `pcrec --list-axes`; memfn/src/options.def) are not pcrec
axes -- no flags bit, no axes.def row -- so the registry derivation never
found them. run_axes.sh now appends one answer-identity JOB per (kit row,
layer) cell; this script is that arm's second half, the one the jobs cannot
do for themselves: an answer sweep reads AGREE on a flag that never arrived
(a dropped `--memfn=` compiles the base artifact on both sides), so identity
alone cannot fail on the arm's own plumbing. Same shape as scripts/emit_sweep.py's
DIFFER_PINS ([SWEEPARM], S981/S982), one tier over.

WHAT IT CHECKS (every number below is a MEASUREMENT, MEMFN_CLASS's header
says where and how).

  population   the rows `pcrec --list-axes` prints in its `memfn` section are
               READ, and must equal MEMFN_CLASS's keys exactly: a row the kit
               adds with no classification, or a classification whose row is
               gone, is RED (never a hand list standing in for the registry).
  cells        run_axes.sh passes the flag text each job actually runs with
               (`--cell NAME|LAYER|FLAGS`). Each classified (row, layer) must
               have exactly one cell whose flags carry the row's spelling and,
               at layer `simd`, `-fmemfn-simd`. The reach below compiles WITH
               THOSE FLAGS, so a plant in the job list is seen here.
  class        DIFFER       the deny moves emitted bytes: a measured FLOOR of
                            distinct corpus patterns whose artifact differs
                            from the same layer's own base, per (encoding,
                            stream), AND a named WITNESS that differs
               ASSERT_ZERO  the deny is inert in that cell: exactly 0 differ
                            (the layer switch declines the row)
               REFUSES      the compile is refused (rc != 0)
  controls     an unknown name (`--memfn=no-<bogus>`) must be refused -- the
               REFUSES detector's own positive control -- and a NULL arm
               (the base flags alone) must read exactly 0 differ.

Usage: memfn_arm.py --pcrec BIN --root DIR [--jobs N] [--every K]
                    [--measure] [--subset] --cell 'NAME|LAYER|FLAGS' ...
  --subset    the cells are a selection (run_axes.sh's AXES= named rows by
              spelling): every row WITH a cell must have both layers; rows
              without one are not owed a cell (the population check stands)
  --every K   a sample of the corpus (floors not applied; witnesses, classes,
              the null arm and the unknown-name control still are)
  --measure   print the per-cell counts and first differing patterns instead
              of checking (how MEMFN_CLASS was measured)
"""
import argparse, hashlib, os, shlex, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------------------------
# MEMFN_CLASS -- the classification of every kit row, per layer, MEASURED.
#
#   key   (row name, layer)  layer: "default" = SIMD-off (the shipped default),
#                                   "simd"    = -fmemfn-simd on
#   value (class, floors, witnesses)
#         floors     {(enc, stream): n}   DIFFER only; n = the smaller side of
#                    the measurement, in distinct corpus patterns
#         witnesses  [(enc, stream, pattern)]  DIFFER only; each must differ
#
# MEASURED at lane/runaxes base c2b6e927b (= lane/memfn-fd; no src/cli/lib
# differs from main 063b4a4b4), `taskset -c 12-15 python3 tests/axes/memfn_arm.py
# --measure ...` over the DISTINCT corpus patterns (one compile per pattern per
# pass, `-p rx --features all`; byte base nothing, utf8 base `-e utf8`; streams
# c-default = the default engine, c-vm = --engine=vm). Counts are in the
# report (docs/dev/lanes/runaxes_report.md).
# The vrun rows' utf8 witnesses since [RUN-POS-SET] stage 3 (the comment at vrun-kb below).
VRUN_U8 =[b"(?i)tra", b"(?i)update", b"(?i)union.*?update.*?from", b"(x?)(?i:abcdefghij)\\1"]
VRUN_U8_PAD = VRUN_U8[:3]
# The precheck-assign-byte witnesses since [RUN-POS-SET] stage 3 (lane s2pre2, 2026-11-14).
# Stage 3 lets a class or alternation position next to the one-byte landmark join the
# necessary run, so the landmark is a set run (`rx_reqrun`) and the one-byte ASSIGN site the
# deny moves is gone: intended (s2pre_report.md, s2pre2_report.md). Eleven corpus patterns
# left the reach that way (sweep job 599 over the base and tip corpora: byte c-default
# 132 -> 123, utf8 189 -> 178, both layers). Each witness is a lost pattern's sibling with a
# `.` between the landmark and its set neighbours, so no set run forms and the one-byte
# site stays (single compiles at lane/s2land 692e5f431, both layers). PAB_BOTH differ at
# byte and utf8; PAB_U8 at utf8 only (in byte mode its landmark is `x`, next to the set).
PAB_BOTH = [b"(?:[0-9]{1,3}.\\.){3}[0-9]{1,3}", b"(?:[0-9a-f]{1,4}.:){4,7}[0-9a-f]{1,4}",
            b"(?:\\d{1,3}.\\.){3}\\d{1,3}", b"(?:^|[\\s,;])(?:tr.e|fal.e)(?:$|[\\s,;])",
            b"(?:a.|c.|a.r|c.t){8}.z", b"(?m)^ER.ROR|WA.RN", b"(\\d{2,4}).-.(\\d{2,4})",
            b"[a-c]{2,4}.x.[0-9]{2,4}.y.[A-C]{2,4}.z.[j-l]{2,4}.w.[x-z]{2,4}",
            b"\\b\\d{1,3}.\\..\\d", b"(?:ab|ba|aa|bb){24}.c"]
PAB_U8 = [b"x.(?:1[\xc3\xa9\xc3\xa0]|q2|r3).y"]
PAB_WIT = ([("byte", "c-default", b"((?:a(?!b)|ab)(?:cd){0,3}b)"), ("utf8", "c-default", b"((?:a(?!b)|ab)(?:cd){0,3}b)")]
           + [(e, "c-default", w) for w in PAB_BOTH for e in ("byte", "utf8")]
           + [("utf8", "c-default", w) for w in PAB_U8])
MEMFN_CLASS = {
    ("precheck-assign-byte", "default"): ("DIFFER",
        {("byte", "c-default"): 131, ("byte", "c-vm"): 0, ("utf8", "c-default"): 189, ("utf8", "c-vm"): 0},
        PAB_WIT),
    ("precheck-assign-byte", "simd"): ("DIFFER",
        {("byte", "c-default"): 131, ("byte", "c-vm"): 0, ("utf8", "c-default"): 189, ("utf8", "c-vm"): 0},
        PAB_WIT),
    # R17-b' B1's five finder-table denies (lane fdclass, 2026-10-17), MEASURED at
    # lane/b1fix f74bb0b7b (= the B1 tip): `taskset -c 0-7 python3 tests/axes/memfn_arm.py
    # --measure`, 10 cells (5 rows x 2 layers), differ=0 refused=0 of 4624 in every
    # (encoding, stream) -- build/fdclass_measure.log, docs/dev/lanes/fdclass_report.md.
    # No fd_rows[] row is routed at B1 (fdb1_report.md), so each deny is
    # artifact-identical. THESE CLASSES ARE B1's, NOT STANDING FACTS: fd-d1 became DIFFER
    # when lane/fdb2 routed D1 (its OFF arm is D1w's walk; re-measured below). fd-r0 and
    # fd-r5 RETIRED at B4' (lane b4p) with their rows, fd-r8 and fd-ndisp at span_pick 1f
    # with R8, R1 and R2 (their ASSERT_ZERO cells went with them). Each landing re-measures.
    # fd-d1 RE-MEASURED at B2's landing (lane fdb2land, 2026-10-17, lane/fdb2land =
    # fdclass + main aa66dbd64 + lane/fdb2 01ffd2f2d): B2 routes D1, so the deny moves
    # the one-byte sites to D1w's walk on the default engine; the VM stream has none.
    # Same method, `taskset -c 0-11`, build/fd_d1_measure.log, fdb2land_report.md;
    # floors = the measured counts (identical at both layers, = fdb2's 1,004 / 985).
    ("fd-d1", "default"): ("DIFFER",
        {("byte", "c-default"): 1004, ("byte", "c-vm"): 0, ("utf8", "c-default"): 985, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b" \\w?\\b"), ("utf8", "c-default", b" \\w?\\b")]),
    ("fd-d1", "simd"): ("DIFFER",
        {("byte", "c-default"): 1004, ("byte", "c-vm"): 0, ("utf8", "c-default"): 985, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b" \\w?\\b"), ("utf8", "c-default", b" \\w?\\b")]),
    # R17-b' B3b's three PRES denies (lane b3b, 2026-10-18), MEASURED at lane/memfn-b3b
    # 8444f0ed5 (`taskset -c 12-15 python3 -I tests/axes/memfn_arm.py --measure`, 6 cells,
    # refused=0 of 4624 everywhere; docs/dev/lanes/b3b_report.md). All DIFFER: slot PRES
    # is routed, so each deny moves the pre-checks its row decides, identically at both
    # layers (no SIMD form reads a presence link). `pres-set-lead` is the retired
    # `-fno-req-set-lead` (bit 45), its population that flag's; `fd-pres-g1` and
    # `fd-pres-pick` act on the DFA-scanned routes only (c-vm 0: no pre-check there is
    # dominated, and every span is REQUIRED).
    # RE-PINNED at D172 S3 (lane s3fix, 2026-10-24) from job 620's axes_memfn log on
    # lane/memfn-s3pair cc4f54eb2 (4796 distinct patterns; docs/dev/lanes/s3_evidence/
    # tri620.md): `cover` (RX_DFA_SCAN "cover") takes the fixed-width windows off the
    # pre-check route, so fewer patterns differ under each PRES/assign deny on the default
    # engine (the corpus GREW 4624 -> 4796, so not corpus noise): fd-pres-g1 1271/1105 ->
    # 949/878, fd-pres-pick 187/262 -> 168/232, precheck-assign-byte (above) 176/244 ->
    # 155/219, pres-set-lead c-default 16/8 -> 14/7 (c-vm unchanged: no cover there). The
    # witnesses `ab`, `é{2}cat` and `a{3}(?i:cat)` are cover artifacts now (the deny is
    # inert on them); each is replaced by its variable-width sibling, still pre-checked
    # (`abc+d`, `é{2,}cat`, `a{3,}(?i:cat)`; single compiles at the s3fix tip, both sides).
    # RE-PINNED at P1's landmark walk (dc6a40dfb, D184; lane axtri3, 2026-11-03) from the
    # full suite 20261103_4bd002e20 axes log (5017 distinct patterns): the walk takes corpus
    # patterns the presence pick / byte assign served (they stamp "landmark-walk",
    # byte-identical with and without the deny), so fewer differ on the default engine:
    # fd-pres-pick 168/232 -> 144/225, precheck-assign-byte byte 155 -> 153 (utf8 219 -> 220,
    # measured). Same cause as ef179b9f4's emit_sweep re-pin (pinbis_report.md).
    # RE-PINNED at span arms R1 (f7eb10528; lane axtri, 2026-11-10) from the full suite
    # 20261110_7d74499bc axes log (5137 distinct patterns): R1 gives counted-repeat
    # patterns a longer required run the pick / byte assign / set lead cannot change, so
    # fewer differ on the default engine: fd-pres-pick 144/225 -> 88/140,
    # precheck-assign-byte 153/220 -> 131/189, pres-set-lead 14/18/7/8 -> 6/11/3/3.
    # Witnesses re-aimed (inert now; single compiles, both sides): fd-pres-g1 utf8
    # `abc+d` -> `ab+c`, pres-set-lead -> `(?i:select)\d+x` (flr2's emit_sweep pin,
    # 68089d755). The other floors still hold (measured above them) and are left as pinned.
    # RE-PINNED again (lane axfix, 2026-11-11): fd-pres-pick byte c-default 88 -> 87. The
    # 88 came from the 7d74499bc full-suite axes log, whose compile set also held the OLD
    # witness-only patterns; axtri re-aimed the witnesses and the count differ= is over
    # corpus + witness-only patterns, so one fewer differs. Job 450 (lane/axtri) and a rerun
    # on main + axtri (5139 corpus patterns, +2 witness-only; MEMFN_REACH_ONLY=1
    # AXES=--memfn=no-fd-pres-pick tests/axes/run_axes.sh) both measure 87 (utf8 140). No
    # src/cli/lib commit since 7d74499bc moves it (only 656690044, -o write-if-changed).
    **{("fd-pres-g1", ly): ("DIFFER",
        {("byte", "c-default"): 949, ("byte", "c-vm"): 0, ("utf8", "c-default"): 878, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b"abc+d"), ("utf8", "c-default", b"ab+c")]) for ly in ("default", "simd")},
    **{("fd-pres-pick", ly): ("DIFFER",
        {("byte", "c-default"): 87, ("byte", "c-vm"): 0, ("utf8", "c-default"): 140, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b"a.{1,5}z"), ("utf8", "c-default", b"a.{1,5}z")]) for ly in ("default", "simd")},
    **{("pres-set-lead", ly): ("DIFFER",
        {("byte", "c-default"): 6, ("byte", "c-vm"): 11, ("utf8", "c-default"): 3, ("utf8", "c-vm"): 3},
        [("byte", "c-default", b"(?i:select)\\d+x"), ("utf8", "c-default", b"(?i:select)\\d+x")]) for ly in ("default", "simd")},
    # D172 S3's two window-search denies (window-search: the search itself, so `cover` declines;
    # window-skip: its skip for a common byte set), absent from this table since S3 while
    # `--list-axes` listed them (code review r2 R2-4: the population check above could only
    # fail). CLASSIFIED STATICALLY by lane s3pair (2026-10-23, single compiles of the
    # witnesses at both layers; the box was held by job 606): both DIFFER on the default
    # engine, neither on the VM engine (`cover` is a DFA-route row). FLOORS MEASURED by
    # job 620's `axes_measure` step (this file's --measure over the four cells, lane/
    # memfn-s3pair cc4f54eb2, 4796 patterns, identical at both layers; tri620.md), under
    # the rows' names then (`wf-find`, `wf-hors`): window-search byte 805, utf8 613;
    # window-skip byte 7, utf8 2 (`\b\w*?\B\w`, `\w\B\w`: the static classification's
    # "byte only" was wrong); c-vm 0 for both.
    **{("window-search", ly): ("DIFFER",
        {("byte", "c-default"): 805, ("byte", "c-vm"): 0, ("utf8", "c-default"): 613, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b"\\bcat\\b"), ("utf8", "c-default", b"\\bcat\\b")]) for ly in ("default", "simd")},
    **{("window-skip", ly): ("DIFFER",
        {("byte", "c-default"): 7, ("byte", "c-vm"): 0, ("utf8", "c-default"): 2, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b"\\b[0-9a-f]{8}\\b"), ("utf8", "c-default", b"\\w\\B\\w")]) for ly in ("default", "simd")},
    # run-verify-wide (R-38 Part D, memfn/src/options.def): the identity on every run stated before
    # Part D (ASSERT_ZERO at partdland, 2026-11-13). Since [RUN-POS-SET] stage 3's S2 joint landing
    # (lane s2land) runs carry wide positions and the deny clips them: DIFFER, the corpus witness
    # `(?i:select)\d+x` MEASURED to differ in all four cells at both layers by single compiles.
    # PROVISIONAL FLOOR 1 (the corpus counts were not measured inside the owner's box hold): the
    # landing's queued axes run measures them and a follow-up re-pins at the measured value.
    **{("run-verify-wide", ly): ("DIFFER",
        {("byte", "c-default"): 1, ("byte", "c-vm"): 1, ("utf8", "c-default"): 1, ("utf8", "c-vm"): 1},
        [(e, st, b"(?i:select)\\d+x") for e in ("byte", "utf8") for st in ("c-default", "c-vm")]) for ly in ("default", "simd")},
    # The five vrun rows' utf8 witnesses (lane s2axes, 2026-11-13). [RUN-POS-SET] stage 3
    # (the S2 joint landing) states a utf8 caseless `s` or `k` as a WIDE position (`[Ss\xbf]`,
    # the last byte of U+017F; `k` likewise with U+212A), so a run through one is no single RUN
    # term and vrun declines it, by design: part_d.md §3.1's `vrun_applies` row, §6 C4 (the
    # deny `run-verify-wide` clips the run and vrun returns). Six corpus patterns left the
    # utf8 reach that way (`(?i)select`, `(?i)stra`, `(?i)stra(ße)`, `(?i)straße`,
    # `(?i)union.*?select.*?from`, `(x?)(?i:abcdefghijkl)\1`; cloud axes 43535669918: utf8
    # 12/13 against floors 15/15, pad 10/12 against 13/14). Their siblings without a wide
    # letter are the witnesses below (VRUN_U8: all five rows; the ten-byte run is past
    # vrun-pad's 3 and 5-7, so pad takes the first three), single compiles at lane/s2land
    # 692e5f431, so the floors hold at their measured values: no floor lowered.
    ("vrun-kb", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-kb", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]
         + [("utf8", st, w) for w in VRUN_U8 for st in ("c-default", "c-vm")]),
    ("vrun-pad", "default"): ("ASSERT_ZERO", {}, []),
    # vrun-pad utf8/c-default 14 -> 13 at D172 S3 (job 620, tri620.md): one caseless pattern
    # became a cover artifact, where the pad deny is inert; its siblings' 15 hold.
    ("vrun-pad", "simd"): ("DIFFER",
        {("byte", "c-default"): 19, ("byte", "c-vm"): 18, ("utf8", "c-default"): 13, ("utf8", "c-vm"): 14},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]
         + [("utf8", st, w) for w in VRUN_U8_PAD for st in ("c-default", "c-vm")]),
    ("vrun-trim", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-trim", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]
         + [("utf8", st, w) for w in VRUN_U8 for st in ("c-default", "c-vm")]),
    ("vrun-w16", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-w16", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]
         + [("utf8", st, w) for w in VRUN_U8 for st in ("c-default", "c-vm")]),
    ("vrun-w32", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-w32", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]
         + [("utf8", st, w) for w in VRUN_U8 for st in ("c-default", "c-vm")]),
}

STREAMS = {"c-default": [], "c-vm": ["--engine=vm"]}
ENCS = {"byte": [], "utf8": ["-e", "utf8"]}
NULL_FLAGS = ""
BOGUS = "--memfn=no-zz-no-such-row"
TIMEOUT = 30


def die(msg):
    print(f"memfn arm: FATAL: {msg}")
    print("checks passed: 0")
    print("checks failed: 1")
    sys.exit(1)


def run(argv, timeout=TIMEOUT):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, b"", b"TIMEOUT"


def read_memfn_section(pcrec):
    """The `memfn` section's rows of `--list-axes`: [(name, kind, layer, spelling)]."""
    rc, out, err = run([pcrec, "--list-axes"], 60)
    if rc != 0:
        die(f"--list-axes failed rc={rc}: {err[:200]!r}")
    rows, active = [], False
    for line in out.decode("utf-8", "replace").splitlines():
        if line.startswith("#section "):
            active = line[len("#section "):].strip() == "memfn"
            continue
        if not active or line.startswith("#") or not line.strip():
            continue
        f = line.split("\t")
        if len(f) < 5:
            die(f"memfn section row with {len(f)} fields: {line[:120]!r}")
        rows.append((f[0], f[1], f[3], f[4]))
    return rows


def corpus_patterns(pcrec, root, every):
    sys.path.insert(0, os.path.join(root, "scripts"))
    import emit_sweep as es
    pats = es.distinct_patterns(es.enumerate_corpus(pcrec, root, 60), every)
    return es, pats


def compile_c(es, pcrec, pattern, enc, stream, flags):
    ok, content, err = es.compile_stream_c(
        pcrec, pattern, TIMEOUT, engine=("vm" if stream == "c-vm" else None),
        extra=ENCS[enc] + flags)
    # a digest, never the bytes: 4.6k patterns x layers x encodings x streams of
    # artifacts up to hundreds of KB would otherwise sit in the base cache
    return ok, (hashlib.sha256(content).digest() if ok else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--cell", action="append", default=[])
    ap.add_argument("--subset", action="store_true")
    a = ap.parse_args()
    passed, failed = 0, 0
    lines = []

    def check(ok, msg):
        nonlocal passed, failed
        if ok:
            passed += 1
        else:
            failed += 1
            lines.append(f"FAIL: {msg}")
        return ok

    rows = read_memfn_section(a.pcrec)
    if not rows:
        die("the `memfn` section of --list-axes has ZERO rows (K35: hard-fail on empty)")
    spelling = {r[0]: r[3] for r in rows}
    layer_of = {r[0]: r[2] for r in rows}

    cells = {}
    for c in a.cell:
        name, layer, flags = c.split("|", 2)
        if (name, layer) in cells:
            die(f"two cells for {(name, layer)}")
        cells[(name, layer)] = shlex.split(flags)

    # ---- population: the section's rows == the classification's rows -------
    if not a.measure:
        check(set(spelling) == {k[0] for k in MEMFN_CLASS},
              "list-axes memfn rows %s != MEMFN_CLASS rows %s -- a kit row was added or "
              "removed with no classification (or the reverse)" %
              (sorted(spelling), sorted({k[0] for k in MEMFN_CLASS})))
        # --subset (AXES= named rows by spelling): only the rows that HAVE a
        # cell are owed both layers; a subset run that selected none is RED
        picked = {k[0] for k in cells}
        check(not a.subset or picked, "--subset with ZERO cells (K35: never measure nothing)")
        for (name, layer) in sorted(MEMFN_CLASS):
            if a.subset and name not in picked:
                continue
            fl = cells.get((name, layer))
            if not check(fl is not None, f"no job cell for ({name}, {layer})"):
                continue
            check(spelling.get(name) in fl,
                  f"cell ({name}, {layer}) flags {fl} lack the row's spelling "
                  f"{spelling.get(name)!r}")
            check(any(x == "-fmemfn-simd" or x.startswith("-fmemfn-simd=") for x in fl) == (layer == "simd"),
                  f"cell ({name}, {layer}) flags {fl}: -fmemfn-simd presence != layer")
        for k in cells:
            check(k in MEMFN_CLASS, f"cell {k} has no classification")

    # ---- the reach: compile base vs arm with the cells' OWN flags ----------
    es, pats = corpus_patterns(a.pcrec, a.root, a.every)
    wit = sorted({w[2] for v in MEMFN_CLASS.values() for w in v[2]})
    allpats = sorted(set(pats) | set(w.encode() if isinstance(w, str) else w for w in wit))
    full = a.every == 1
    print(f"memfn arm: {len(rows)} kit rows, {len(cells)} cells, {len(pats)} distinct corpus "
          f"patterns (+{len(set(allpats) - set(pats))} witness-only), every={a.every}")

    todo = sorted(cells) if a.measure else sorted(MEMFN_CLASS)
    jobs = []
    for key in todo:
        if key not in cells:
            continue
        fl = cells[key]
        sp = spelling.get(key[0])
        base = [x for x in fl if x != sp]
        for enc in ENCS:
            for stream in STREAMS:
                jobs.append((key, base, fl, enc, stream))
    base_cache = {}

    def comp(base, enc, stream, p):
        k = (tuple(base), enc, stream, p)
        if k not in base_cache:
            base_cache[k] = compile_c(es, a.pcrec, p, enc, stream, list(base))
        return base_cache[k]

    results = {}
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for (key, base, fl, enc, stream) in jobs:
            def one(p, base=base, fl=fl, enc=enc, stream=stream):
                b = comp(base, enc, stream, p)
                x = compile_c(es, a.pcrec, p, enc, stream, list(fl))
                return p, b, x
            outs = list(ex.map(one, allpats))
            differ = [p for p, b, x in outs if b[0] and x[0] and b[1] != x[1]]
            refused = [p for p, b, x in outs if b[0] and not x[0]]
            results[(key, enc, stream)] = (differ, refused, len(outs))
            if a.measure:
                print(f"{key[0]:22s} {key[1]:8s} {enc:5s} {stream:9s} differ={len(differ):5d} "
                      f"refused={len(refused):4d} of {len(outs)}  first={differ[:3]!r}", flush=True)
    if a.measure:
        return 0

    for (key, enc, stream), (differ, refused, n) in sorted(results.items()):
        cls, floors, witnesses = MEMFN_CLASS[key]
        tag = f"{key[0]} @{key[1]} {enc}/{stream}"
        if cls == "ASSERT_ZERO":
            check(not differ and not refused, f"{tag}: ASSERT_ZERO violated: differ={len(differ)} "
                  f"refused={len(refused)} (first {differ[:2]!r})")
        elif cls == "REFUSES":
            check(refused and not differ, f"{tag}: REFUSES but {len(refused)} refused / {len(differ)} differ")
        elif cls == "DIFFER":
            check(not refused, f"{tag}: {len(refused)} patterns REFUSED under the deny (first {refused[:2]!r})")
            fl = floors.get((enc, stream))
            if full and fl is not None:
                check(len(differ) >= fl, f"{tag}: DIFFER FLOOR {len(differ)} < {fl}")
            for (we, ws, wp) in witnesses:
                if (we, ws) == (enc, stream):
                    wb = wp.encode() if isinstance(wp, str) else wp
                    check(wb in set(differ), f"{tag}: WITNESS {wp!r} did not differ under the deny")
        else:
            die(f"unknown class {cls!r}")
        print(f"  {tag:46s} {cls:11s} differ={len(differ)} refused={len(refused)} of {n}"
              + (f" floor={floors.get((enc, stream))}" if cls == "DIFFER" else ""))

    # ---- controls ----------------------------------------------------------
    sample = allpats[:50]
    for enc in ENCS:
        for stream in STREAMS:
            nz = 0
            for p in sample:
                b = compile_c(es, a.pcrec, p, enc, stream, [])
                x = compile_c(es, a.pcrec, p, enc, stream, [])
                nz += 1 if (b[0] and x[0] and b[1] != x[1]) else 0
            check(nz == 0, f"NULL arm {enc}/{stream}: {nz} differ")
    rc, out, err = run([a.pcrec, "-p", "rx", BOGUS, "--pattern", "a", "-o", "-"])
    check(rc not in (0, None), f"unknown-name control: `{BOGUS}` was ACCEPTED (rc={rc}) -- the "
          "REFUSES detector has no positive control")
    # the REFUSES class's real population: a row declared `deny` takes only
    # `no-NAME`; its bare NAME (the force spelling a `pair` row takes) is refused
    for (name, kind, layer, sp) in rows:
        if kind != "deny":
            continue
        force = "--memfn=" + name
        rc, out, err = run([a.pcrec, "-p", "rx", force, "--pattern", "a", "-o", "-"])
        check(rc not in (0, None), f"REFUSES: `{force}` (row {name} is kind=deny) was accepted, rc={rc}")

    for l in lines:
        print(l)
    print(f"memfn arm: {'OK' if not failed else 'FAILED'}")
    print(f"checks passed: {passed}")
    print(f"checks failed: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
