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
                    [--measure] --cell 'NAME|LAYER|FLAGS' ...
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
MEMFN_CLASS = {
    ("precheck-assign-byte", "default"): ("DIFFER",
        {("byte", "c-default"): 176, ("byte", "c-vm"): 0, ("utf8", "c-default"): 244, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b"((?:a(?!b)|ab)(?:cd){0,3}b)"), ("utf8", "c-default", b"((?:a(?!b)|ab)(?:cd){0,3}b)")]),
    ("precheck-assign-byte", "simd"): ("DIFFER",
        {("byte", "c-default"): 176, ("byte", "c-vm"): 0, ("utf8", "c-default"): 244, ("utf8", "c-vm"): 0},
        [("byte", "c-default", b"((?:a(?!b)|ab)(?:cd){0,3}b)"), ("utf8", "c-default", b"((?:a(?!b)|ab)(?:cd){0,3}b)")]),
    # R17-b' B1's five finder-table denies (lane fdclass, 2026-10-17), MEASURED at
    # lane/b1fix f74bb0b7b (= the B1 tip): `taskset -c 0-7 python3 tests/axes/memfn_arm.py
    # --measure`, 10 cells (5 rows x 2 layers), differ=0 refused=0 of 4624 in every
    # (encoding, stream) -- build/fdclass_measure.log, docs/dev/lanes/fdclass_report.md.
    # No fd_rows[] row is routed at B1 (fdb1_report.md), so each deny is
    # artifact-identical. THESE CLASSES ARE B1's, NOT STANDING FACTS: fd-d1 -> DIFFER
    # when lane/fdb2 routes D1 (its OFF arm is D1w's walk; ~1,004 sites), fd-r0/fd-r5/
    # fd-ndisp at B4, fd-r8 at B6 (options.def's comment). Each landing re-measures.
    ("fd-d1", "default"): ("ASSERT_ZERO", {}, []),
    ("fd-d1", "simd"): ("ASSERT_ZERO", {}, []),
    ("fd-ndisp", "default"): ("ASSERT_ZERO", {}, []),
    ("fd-ndisp", "simd"): ("ASSERT_ZERO", {}, []),
    ("fd-r0", "default"): ("ASSERT_ZERO", {}, []),
    ("fd-r0", "simd"): ("ASSERT_ZERO", {}, []),
    ("fd-r5", "default"): ("ASSERT_ZERO", {}, []),
    ("fd-r5", "simd"): ("ASSERT_ZERO", {}, []),
    ("fd-r8", "default"): ("ASSERT_ZERO", {}, []),
    ("fd-r8", "simd"): ("ASSERT_ZERO", {}, []),
    ("vrun-kb", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-kb", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]),
    ("vrun-pad", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-pad", "simd"): ("DIFFER",
        {("byte", "c-default"): 19, ("byte", "c-vm"): 18, ("utf8", "c-default"): 14, ("utf8", "c-vm"): 14},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]),
    ("vrun-trim", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-trim", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]),
    ("vrun-w16", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-w16", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]),
    ("vrun-w32", "default"): ("ASSERT_ZERO", {}, []),
    ("vrun-w32", "simd"): ("DIFFER",
        {("byte", "c-default"): 20, ("byte", "c-vm"): 19, ("utf8", "c-default"): 15, ("utf8", "c-vm"): 15},
        [("byte", "c-default", b"(?i)cat"), ("byte", "c-vm", b"(?i)cat"), ("utf8", "c-default", b"(?i)cat"), ("utf8", "c-vm", b"(?i)cat")]),
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
        for (name, layer) in sorted(MEMFN_CLASS):
            fl = cells.get((name, layer))
            if not check(fl is not None, f"no job cell for ({name}, {layer})"):
                continue
            check(spelling.get(name) in fl,
                  f"cell ({name}, {layer}) flags {fl} lack the row's spelling "
                  f"{spelling.get(name)!r}")
            check(("-fmemfn-simd" in fl) == (layer == "simd"),
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
