#!/usr/bin/env python3
"""scripts/emit_sweep.py -- [BSWEEP] the COMMITTED emitter byte-neutrality
sweep.

WHY THIS EXISTS. Five wave-2 lanes (w2a, w2b, w2x, w2y, w2census) each
REBUILT this instrument from prose in their own scratchpads, and three of
them landed on THREE DIFFERENT composition-arm populations (30/72, 29/84,
32/96) for what the brief calls one mandatory arm. w2y traced the cause
(docs/dev/lanes/w2y_report.md S3.1/S3.2): the composition arm reaches
vm_splice's DELIVER block ONLY under --features all (both DELIVER-reaching
fixtures need module `recursion`, and a bare `--source FILE` passes no
features of its own), and the three argv streams likewise need
--features all or reach collapses to 1,500 of 3,938 corpus pattern lines
(the module-gated ~62%, invisible in a pass-count -- every backreference and
every lookbehind in the tree). "A mandatory arm whose reach depends on a
flag nobody wrote down can be silently empty." This script is that
instrument, built once, with its populations PINNED so a future lane
compares against a floor instead of re-deriving one from memory.

WHAT IT COMPARES. A REFERENCE pcrec (built from `git archive REF`, a
revision that never moves under you) against a WORKING pcrec (the tree's
own build, or an explicit --bin/second revision), across FOUR streams, all
under --features all:

  1. corpus argv, `.c` at the DEFAULT engine       (-p rx --features all)
  2. corpus argv, `.c` at --engine=vm               (forces the VM route)
  3. corpus argv, `--emit-ir` at --engine=vm         (the VM program listing;
     --emit-ir at the default engine REFUSES on every DFA-winning pattern --
     w2x S5 -- so this stream ALWAYS forces --engine=vm, independent of the
     .c streams' own engine choice for stream 1)
  4. composition: `--source FILE` over every `.rxt`/`.rxtin` under
     <tree>/tests/ (304 files at this writing) -- the ONLY route that
     reaches vm_splice's DELIVER block (gated on a->u.call.deliver_n,
     written exclusively by src/parse/rxt_compose.c; no corpus .rxt file
     declares an `export`, and no argv pattern can express one -- w2a S2).

The corpus POPULATION (which patterns exist) is always read from the
WORKING side's tree (--tree, live by default, or the source extracted for
--tree-rev) via one canonical binary's own `--list-source` -- the same
--list-source-plus-escape-decode methodology
docs/dev/w1stage0_evidence/longprefix_sweep.py and
docs/dev/dialtrain_byteid_evidence/byteid_sweep.py both already use, so a
fourth independent re-derivation is not required. Pattern TEXT is then fed
to both binaries via argv directly (never a shell string -- a corpus
pattern can itself be operator syntax, and letting a shell interpret it is
a known trap this house has hit before).

PINS. Reach and composition-population expectations are FLOORS, not
equality pins (D110's shape, `tests/core/alloc_check.c`'s own precedent for
this project) -- see the PINS dict below for the reasoning on why a small
margin (not D110's "half the measured value") is the right shape for THIS
population.

SELF-CHECK. Builds two INDEPENDENT binaries from the SAME revision (two
separate `git archive` extractions and `make` invocations, catching a
build-nondeterminism confound as a bonus) and runs the whole sweep between
them -- must come back all-identical at full reach before a real ref-vs-tree
run is trusted (w2x S5: "the instrument was validated before it was
trusted"). Runs automatically first unless --no-self-check.

--only-emit-ir-reach: for a render-path customer (DD-8, [EMIT-VERB]) whose
--emit-ir listing is EXPECTED to move, report reach only on stream 3 and
require full byte identity on streams 1/2/4.

USAGE
  python3 scripts/emit_sweep.py --ref REV [options]

  # self-check only (no real comparison), against the live tree's own build:
  python3 scripts/emit_sweep.py --ref HEAD --bin build/pcrec --no-real-run

  # ref REV vs the live working tree's own build/pcrec (the common case: a
  # lane comparing its own edits against its own branch point):
  python3 scripts/emit_sweep.py --ref <branch-point-sha>

  # ref REV1 vs a DIFFERENT historical revision REV2, touching no live
  # build/ directory anywhere (both sides built from `git archive` into
  # scratch) -- what this lane's own validation #2 uses:
  python3 scripts/emit_sweep.py --ref REV1 --tree-rev REV2

OPTIONS
  --ref REV            git revision to build as the reference (anything
                        `git archive` accepts). Required unless --ref-bin.
  --ref-bin PATH        skip building; use this pre-built pcrec as the
                        reference (no source tree needed -- the corpus is
                        always drawn from the WORKING side).
  --bin PATH            the working-tree pcrec binary to compare (default:
                        <tree>/build/pcrec). Mutually exclusive with
                        --tree-rev.
  --tree-rev REV        instead of --bin, archive+build the WORKING side
                        from this revision too (same mechanism as --ref) --
                        and draw the corpus/composition file set from ITS
                        extracted tests/ directory rather than the live
                        --tree. Lets two arbitrary historical revisions be
                        compared with no live build/ directory touched.
  --tree DIR            repo root for the corpus/composition file set when
                        --tree-rev is not given (default: this script's own
                        repo root, inferred from its path). READ ONLY --
                        this tool never writes there.
  --out DIR             scratch/output directory for archived sources,
                        scratch builds, per-run composition trees, and the
                        TSV/log report (default: <tree>/build-emitsweep,
                        gitignored, same shape as build-ubsan/ etc).
  --jobs N              parallel pcrec invocations for the argv streams
                        (default: min(8, os.cpu_count())).
  --no-self-check        skip the ref-vs-ref self-check (NOT recommended --
                        see the header above).
  --no-real-run          run only the self-check, skip the real ref-vs-tree
                        comparison (useful for validating the instrument
                        alone).
  --only-emit-ir-reach   report reach only on the --emit-ir stream; require
                        full byte identity on the other three (for a
                        render-path-only change).
  --keep                 keep scratch trees/artifacts after the run
                        (default: cleaned up on exit).
  --timeout SECONDS      per-invocation timeout (default 30, D45's shape).

EXIT STATUS: 0 if every stream is clean against its floor/identity
requirement and the DELIVER witness holds; 1 otherwise. Report is printed
to stdout; a full per-row TSV per stream is written under --out.
"""
import argparse
import concurrent.futures
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TREE = os.path.dirname(SCRIPT_DIR)

# ---------------------------------------------------------------------------
# PINS -- measured at this lane's branch point (7ee40500, 2026-09-19),
# --features all, full corpus (211 .rxt files, 93 .rxtin files, 304 total),
# `python3 scripts/emit_sweep.py --ref-bin build/pcrec --bin build/pcrec
# --no-self-check` (ref==tree, so movers=0/asymmetric=0 is the correctness
# check on the instrument itself; the numbers below are its reach/population
# report). See docs/dev/lanes/bsweep_report.md for the full transcript and
# the reconciliation against w2a/w2b/w2x/w2y's own four different prose-
# rebuilt numbers.
#
# FLOORS, not equality (D110's shape) -- but with a MUCH SMALLER margin than
# D110's "half the measured value". D110's alloc_check.c populations are
# ALLOCATION COUNTS that a legitimate byte-neutral refactor genuinely moves
# (the cited instance: 158 -> 162 under one fragment-retirement change that
# altered nothing observable) -- "half" was chosen because that population
# has no reason to be monotone. THIS population is different in kind: it is
# "how many corpus patterns compile" and "how many composition files
# produce", both of which are expected to be MONOTONE NON-DECREASING under
# ordinary work (the corpus only grows; a construct that used to compile
# essentially never stops compiling, and on the rare deliberate occasion it
# does -- a bug fix that turns a miscompile into a clean refusal -- that is
# a deliberate, reviewed event that re-pins this file, not silent drift).
# A "half" floor here would be dangerously loose: the actual failure mode
# this tool exists to catch (a missing --features all) drops argv reach to
# 1,500 of 3,938 and the --emit-ir stream's own default-engine mistake drops
# it to 1,754 of 3,938 -- both comfortably BELOW half of 3,517/3,518, so a
# half floor would still catch them, but only by a margin of a few hundred
# rows on a corpus of thousands, and it would blunt the tool against a much
# smaller regression (a handful of newly-refusing patterns) that a half
# floor has no hope of noticing. So: measured value minus roughly 10%,
# rounded down to a clean number -- comfortably above ordinary day-to-day
# noise (a handful of rows), comfortably below the two known failure modes
# (which lose 45-62% of reach), and tight enough to flag a real, smaller
# collapse the way D110's own floors could not for THIS shape of count.
PINS = {
    # total .rxt + .rxtin files under tests/ (the composition population).
    "composition_files_floor": 300,       # measured 304
    # corpus pattern/pattern-esc rows found by --list-source over tests/**/*.rxt.
    "argv_population_floor": 3900,        # measured 3,938
    # rows where BOTH sides compile successfully, per stream (--features all).
    "reach_default_floor": 3480,          # measured 3,517 (stream 1)
    "reach_vm_floor": 3480,               # measured 3,518 (stream 2)
    "reach_ir_floor": 3480,               # measured 3,518 (stream 3)
    # composition files that produce >=1 artifact on both sides. Measured
    # 32 producing / 96 artifacts, matching w2y_report.md's own recorded
    # figure EXACTLY (also claimed at --features all) -- resolved after an
    # r1 fix found this tool's OWN first cut undercounting by exactly these
    # two files, for two independent, now-identified reasons (see
    # docs/dev/lanes/bsweep_report.md S1.4 for the full diagnosis and the
    # reconciliation against all five prior lanes' figures):
    #   (1) `sweep_composition` originally gated the whole per-file byte
    #       comparison on `rc == 0`, so `compose_encoding_clash.rxtin` --
    #       a fixture that DELIBERATELY declares one target that compiles
    #       (`ok`) and one that a later definition's encoding conflict
    #       correctly refuses (`clash`) -- was skipped entirely, even
    #       though `ok.c`/`ok.h` were genuinely on disk (`--source` writes
    #       each target in file order and stops on the first failure).
    #       Fixed: compare whenever both sides agree on rc AND on the
    #       artifact name set, never gated on rc==0 alone.
    #   (2) `bench_altwide_0_2.rxtin` (11 targets / 22 artifacts, the
    #       single largest composition file) TIMED OUT under this arm's
    #       own full argv-stream concurrency (12 jobs at a 30s budget) --
    #       a contention artifact of the SWEEP's own parallelism, not a
    #       corpus fact. Fixed: `--comp-timeout`/`--comp-jobs`, more
    #       generous and less concurrent than the argv streams by default.
    # Floor sits AT the measured value with ZERO slack: w2y measured the
    # known --features regression costing exactly 3 of these files
    # (32 -> 29), so this one axis needs maximum sensitivity, not a
    # margin -- any drop at all is worth flagging.
    "composition_producing_floor": 32,    # measured 32
    "composition_artifacts_floor": 88,    # measured 96; an 8-artifact
                                           # margin (one file's worth, at
                                           # this corpus's measured 3.0
                                           # artifacts/producing-file
                                           # average) below the measured
                                           # value -- "artifact" counts
                                           # every .c and .h file written
                                           # into a per-file output
                                           # directory
}

DELIVER_FIXTURES = ("compose_delivers.rxtin", "deliver_forms.rxtin")

# The DELIVER-block witness. vm_splice's DELIVER loop (src/gen/emit_vm.c,
# the `for (j = 0; j < a->u.call.deliver_n; j++)` block) carries its own
# "DELIVER: keep the callee's exported span..." role text ONLY into the
# vm_ev() event stream that backs --emit-ir's listing -- and --emit-ir
# cannot be combined with --source (the CLI refuses composing any query
# with a compile mode), so there is no textual comment marker reaching the
# .c files this arm actually produces. Confirmed by direct inspection
# (this lane, 2026-09-19): the block's *code* shape is instead two adjacent
# `<PREFIX>_SET(<PREFIX>_GROUP<A>_..., slot_values[<PREFIX>_GROUP<B>_...]);`
# statements (START then END) copying a DIFFERENT group number's span into
# this one's -- ordinary backtrack-restore code only ever copies a group's
# OWN prior value back into itself (same group number both sides), because
# the callee and caller of a composed call never share a group number. This
# was verified against both fixtures below (sitecall.c/selfcall.c/flatcall.c
# and compose_delivers.rxtin's user.c each carry exactly this shape;
# plaincall.c -- the same file's non-delivering fourth call form -- carries
# NO capture-slot SET calls at all, the cleanest possible negative control).
# Corroborating, not load-bearing on its own: the load-bearing protection is
# the whole-artifact byte-identity comparison every composition file
# already gets, which necessarily covers these bytes whenever they exist.
DELIVER_RE = re.compile(
    r"(\w+)_SET\(\1_SLOT_GROUP(\d+)_START,\s*slot_values\[\1_SLOT_GROUP(\d+)_START\]\);"
    r"\s*\n\s*\1_SET\(\1_SLOT_GROUP\2_END,\s*slot_values\[\1_SLOT_GROUP\3_END\]\);"
)


def deliver_witness(text):
    for m in DELIVER_RE.finditer(text):
        if m.group(2) != m.group(3):
            return True
    return False


# ---------------------------------------------------------------------------
# Corpus-pattern escape decode -- verbatim copy of
# docs/dev/w1stage0_evidence/longprefix_sweep.py's own decoder (itself a
# verbatim copy of dialtrain_byteid_evidence/byteid_sweep.py's), the
# --list-source escape vocabulary: \t \n \r \\ \xNN. A third independent
# copy would be the thing memory pcrec-general-mechanisms-not-special-cases
# warns about if it diverged; kept textually identical on purpose.
def decode_escape(s):
    out = bytearray()
    i = 0
    b = s.encode("utf-8", errors="surrogateescape")
    n = len(b)
    while i < n:
        c = b[i]
        if c == 0x5C and i + 1 < n:
            nxt = b[i + 1]
            if nxt == ord('t'):
                out.append(0x09); i += 2; continue
            elif nxt == ord('n'):
                out.append(0x0A); i += 2; continue
            elif nxt == ord('r'):
                out.append(0x0D); i += 2; continue
            elif nxt == 0x5C:
                out.append(0x5C); i += 2; continue
            elif nxt == ord('x') and i + 3 < n:
                hx = bytes([b[i + 2], b[i + 3]])
                try:
                    val = int(hx, 16)
                    out.append(val)
                    i += 4
                    continue
                except ValueError:
                    pass
            out.append(c); i += 1; continue
        else:
            out.append(c); i += 1
    return bytes(out)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def run(argv, timeout, cwd=None, input_bytes=None):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout,
                            cwd=cwd, input=input_bytes)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, b"", b"TIMEOUT"


def resolve_cc(tree):
    """ONE implementation lives in tests/lib/cc_resolve.sh; this shells out
    to it rather than re-deriving GNU-gcc resolution a second time in
    python (an explicit CC in the environment always wins, unchanged)."""
    if os.environ.get("CC"):
        return os.environ["CC"]
    script = os.path.join(tree, "tests", "lib", "cc_resolve.sh")
    rc, out, err = run(
        ["bash", "-c", f"source {script!r} >/dev/null 2>&1; echo \"$CC\""],
        timeout=15)
    cc = out.decode().strip()
    return cc or "gcc"


def build_from_rev(repo_for_archive, rev, out_dir, cc, label, timeout=600):
    """git archive REV | tar -x into out_dir/src_<label>, then `make -j4
    CC=$cc`. Returns (bin_path, src_dir). Never touches any live build/
    directory -- this is always a fresh extraction into scratch."""
    src_dir = os.path.join(out_dir, f"src_{label}")
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
    os.makedirs(src_dir, exist_ok=True)
    log(f"[emit_sweep] archiving {rev} ({label}) into {src_dir} ...")
    p1 = subprocess.Popen(["git", "-C", repo_for_archive, "archive", rev],
                           stdout=subprocess.PIPE)
    with tarfile.open(fileobj=p1.stdout, mode="r|") as tf:
        tf.extractall(src_dir)
    rc = p1.wait(timeout=timeout)
    if rc != 0:
        raise RuntimeError(f"git archive {rev} failed (rc={rc})")
    log(f"[emit_sweep] building {label} (CC={cc}) ...")
    r = subprocess.run(["make", "-j4", f"CC={cc}"], cwd=src_dir,
                        capture_output=True, timeout=timeout)
    if r.returncode != 0:
        sys.stderr.write(r.stdout.decode(errors="replace"))
        sys.stderr.write(r.stderr.decode(errors="replace"))
        raise RuntimeError(f"make failed for {label} ({rev}) rc={r.returncode}")
    bin_path = os.path.join(src_dir, "build", "pcrec")
    if not os.path.exists(bin_path):
        raise RuntimeError(f"{bin_path} missing after build ({label})")
    return bin_path, src_dir


def find_files(tree_dir, suffixes):
    out = []
    tests_dir = os.path.join(tree_dir, "tests")
    for dirpath, _, filenames in os.walk(tests_dir):
        for fn in filenames:
            if fn.endswith(suffixes):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def list_source_patterns(pcrec_bin, rxt_file, timeout):
    rc, out, err = run([pcrec_bin, "--list-source", rxt_file], timeout)
    if rc != 0:
        return []
    rows = []
    for line in out.decode("utf-8", errors="surrogateescape").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) < 5:
            continue
        kind = fields[0]
        if kind not in ("pattern", "pattern-esc"):
            continue
        rows.append((kind, decode_escape(fields[4])))
    return rows


def enumerate_corpus(list_source_bin, tree_dir, timeout):
    files = find_files(tree_dir, (".rxt",))
    all_patterns = []
    for f in files:
        for kind, pat in list_source_patterns(list_source_bin, f, timeout):
            all_patterns.append((os.path.relpath(f, tree_dir), kind, pat))
    return all_patterns


# ---------------------------------------------------------------------------
# The four streams. Each compile_stream* returns (ok: bool, content: bytes
# or None, err_tail: str).

def _err_tail(b, n=200):
    return b.decode("utf-8", errors="replace").strip().replace("\n", " | ")[:n]


def compile_stream_c(pcrec_bin, pattern, timeout, engine=None):
    argv = [pcrec_bin, "-p", "rx", "--features", "all"]
    if engine:
        argv.append(f"--engine={engine}")
    # `-o -` on BOTH sides on purpose: the emitted .c carries `#include "<basename>.h"`
    # derived from -o, so writing a.c vs b.c reads 100% movers with an innocent compiler
    # (the -o basename trap, fifth instance: dd8_report.md §3.1). Vary NOTHING the artifact
    # can observe; the composition arm likewise writes fixture-named files into fresh dirs.
    argv += ["-o", "-", "--", pattern]
    rc, out, err = run(argv, timeout)
    ok = rc == 0
    return ok, (out if ok else None), ("" if ok else _err_tail(err))


def compile_stream_ir(pcrec_bin, pattern, timeout):
    argv = [pcrec_bin, "--features", "all", "--engine=vm", "--emit-ir",
            "--", pattern]
    rc, out, err = run(argv, timeout)
    ok = rc == 0
    return ok, (out if ok else None), ("" if ok else _err_tail(err))


def run_composition(pcrec_bin, rxt_file, out_root, tag, timeout):
    """--source FILE -o <fresh dir>; returns (rc, {filename: bytes})."""
    outdir = os.path.join(out_root, tag)
    os.makedirs(outdir, exist_ok=True)
    argv = [pcrec_bin, "--features", "all", "--source", rxt_file,
            "-o", outdir]
    rc, out, err = run(argv, timeout)
    artifacts = {}
    if os.path.isdir(outdir):
        for fn in sorted(os.listdir(outdir)):
            fp = os.path.join(outdir, fn)
            if os.path.isfile(fp):
                with open(fp, "rb") as fh:
                    artifacts[fn] = fh.read()
    return rc, artifacts, ("" if rc == 0 else _err_tail(err))


# ---------------------------------------------------------------------------
# Diff helper

def first_diff_hunk(a, b, n=6):
    a_lines = a.decode("utf-8", errors="backslashreplace").splitlines()
    b_lines = b.decode("utf-8", errors="backslashreplace").splitlines()
    import difflib
    d = list(difflib.unified_diff(a_lines, b_lines, lineterm="", n=1))
    hunk = []
    seen_at = False
    for line in d:
        if line.startswith("@@"):
            if seen_at:
                break
            seen_at = True
        hunk.append(line)
        if len(hunk) >= n and seen_at:
            break
    return "\n".join(hunk[:n])


# ---------------------------------------------------------------------------
# Sweep engine

class StreamResult:
    def __init__(self, name):
        self.name = name
        self.population = 0
        self.both_ok = 0
        self.both_refuse = 0
        self.movers = []       # list of (key, hunk)
        self.asymmetric = []   # list of (key, side_ok_a, side_ok_b, err_a, err_b)


def sweep_argv_stream(name, compile_fn, patterns, bin_a, bin_b, timeout, jobs):
    res = StreamResult(name)
    res.population = len(patterns)

    def one(item):
        f, kind, pat = item
        ok_a, c_a, e_a = compile_fn(bin_a, pat, timeout)
        ok_b, c_b, e_b = compile_fn(bin_b, pat, timeout)
        key = f"{f}:{kind}:{pat[:60]!r}"
        return key, ok_a, c_a, e_a, ok_b, c_b, e_b

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for key, ok_a, c_a, e_a, ok_b, c_b, e_b in ex.map(one, patterns):
            if ok_a and ok_b:
                res.both_ok += 1
                if c_a != c_b:
                    res.movers.append((key, first_diff_hunk(c_a, c_b)))
            elif not ok_a and not ok_b:
                res.both_refuse += 1
            else:
                res.asymmetric.append((key, ok_a, ok_b, e_a, e_b))
    return res


def sweep_composition(files, bin_a, bin_b, out_root, timeout, jobs):
    res = StreamResult("composition")
    res.population = len(files)
    producing = 0
    artifact_count = 0
    deliver_seen = False
    fixture_produced = {name: False for name in DELIVER_FIXTURES}

    def one(item):
        idx, f = item
        tag = f"f{idx}"
        rc_a, art_a, e_a = run_composition(bin_a, f, os.path.join(out_root, "a"), tag, timeout)
        rc_b, art_b, e_b = run_composition(bin_b, f, os.path.join(out_root, "b"), tag, timeout)
        return f, rc_a, art_a, e_a, rc_b, art_b, e_b

    # [BSWEEP r1 fix, 2026-09-19] Compare artifacts whenever BOTH sides agree
    # on the artifact NAME SET, regardless of the overall process's rc --
    # NOT gated on `rc == 0`. First cut of this function gated the whole
    # comparison on `ok_a` (rc_a == 0) and skipped straight to `both_refuse`
    # otherwise. That is wrong for a fixture like
    # `tests/rxtsource/fixtures/compose_encoding_clash.rxtin`, which
    # DELIBERATELY declares one target that compiles (`ok`) and one that a
    # later definition's encoding conflict correctly refuses (`clash`):
    # `--source` writes each target's artifact in file order and stops
    # (rc=1) on the failing one, so `ok.c`/`ok.h` are genuinely on disk
    # despite the nonzero rc -- and a byte-neutrality sweep has every reason
    # to want those two files compared, since they are exactly the kind of
    # artifact this arm exists to protect. Both sides still have to AGREE
    # on rc (an rc mismatch is a real asymmetry, caught below) and on the
    # artifact NAME SET (a name-set mismatch is a real structural
    # asymmetry, also caught below) before any byte comparison happens.
    rows = list(enumerate(files))
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for f, rc_a, art_a, e_a, rc_b, art_b, e_b in ex.map(one, rows):
            base = os.path.basename(f)
            ok_a = rc_a == 0
            ok_b = rc_b == 0
            if ok_a != ok_b:
                res.asymmetric.append((f, ok_a, ok_b, e_a, e_b))
                continue
            names_a = set(art_a.keys())
            names_b = set(art_b.keys())
            if names_a != names_b:
                res.asymmetric.append(
                    (f, f"artifacts={sorted(names_a)}", f"artifacts={sorted(names_b)}", "", ""))
                continue
            if not names_a:
                res.both_refuse += 1
                continue
            producing += 1
            if base in fixture_produced:
                fixture_produced[base] = True
            for nm in sorted(names_a):
                artifact_count += 1
                content_a = art_a[nm]
                content_b = art_b[nm]
                if nm.endswith(".c") and (deliver_witness(content_a.decode("utf-8", "replace"))
                                          or deliver_witness(content_b.decode("utf-8", "replace"))):
                    nonlocal_flag[0] = True
                if content_a != content_b:
                    res.movers.append((f"{f}::{nm}", first_diff_hunk(content_a, content_b)))
            res.both_ok += 1

    return res, producing, artifact_count, fixture_produced


nonlocal_flag = [False]  # deliver_witness sticky flag, set inside sweep_composition


# ---------------------------------------------------------------------------

def report_stream(res, floor=None, identity_required=False):
    lines = []
    lines.append(f"-- stream: {res.name} --")
    lines.append(f"  population={res.population} both_ok(reach)={res.both_ok} "
                 f"both_refuse={res.both_refuse} movers={len(res.movers)} "
                 f"asymmetric={len(res.asymmetric)}")
    ok = True
    if res.asymmetric:
        ok = False
        lines.append(f"  ASYMMETRIC ROWS ({len(res.asymmetric)}), first 5:")
        for key, ok_a, ok_b, e_a, e_b in res.asymmetric[:5]:
            lines.append(f"    {key}: side_a_ok={ok_a} side_b_ok={ok_b} "
                         f"err_a={e_a!r} err_b={e_b!r}")
    if res.movers:
        if identity_required:
            ok = False
        lines.append(f"  MOVERS ({len(res.movers)}), first 5 with diff hunk:")
        for key, hunk in res.movers[:5]:
            lines.append(f"    {key}:")
            for hl in hunk.splitlines():
                lines.append(f"      {hl}")
    if floor is not None and res.both_ok < floor:
        ok = False
        lines.append(f"  REACH FLOOR VIOLATION: {res.both_ok} < floor {floor}")
    return ok, "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref")
    ap.add_argument("--ref-bin")
    ap.add_argument("--bin")
    ap.add_argument("--tree-rev")
    ap.add_argument("--tree", default=DEFAULT_TREE)
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 4))
    ap.add_argument("--comp-timeout", type=int, default=0,
                     help="per-invocation timeout for the composition arm "
                          "specifically (default: max(3x --timeout, 90) -- "
                          "a composition file can declare many targets in "
                          "one --source call and needs more budget than a "
                          "single-pattern argv compile)")
    ap.add_argument("--comp-jobs", type=int, default=0,
                     help="concurrency for the composition arm specifically "
                          "(default: min(--jobs, 6) -- less contention per "
                          "item than the argv streams, since each item is "
                          "itself heavier)")
    ap.add_argument("--no-self-check", action="store_true")
    ap.add_argument("--no-real-run", action="store_true")
    ap.add_argument("--only-emit-ir-reach", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--limit", type=int, default=0,
                     help="truncate the argv corpus to the first N rows "
                          "(smoke-testing the instrument only -- floors are "
                          "measured against the FULL corpus and will read as "
                          "violations under --limit; not for a real delivery run)")
    args = ap.parse_args()

    if not args.ref and not args.ref_bin:
        ap.error("one of --ref / --ref-bin is required")
    if args.bin and args.tree_rev:
        ap.error("--bin and --tree-rev are mutually exclusive")

    tree = os.path.abspath(args.tree)
    out_dir = os.path.abspath(args.out) if args.out else os.path.join(tree, "build-emitsweep")
    os.makedirs(out_dir, exist_ok=True)
    cc = resolve_cc(tree)
    if not args.comp_timeout:
        args.comp_timeout = max(3 * args.timeout, 90)
    if not args.comp_jobs:
        args.comp_jobs = min(args.jobs, 6)
    log(f"[emit_sweep] tree={tree} out={out_dir} cc={cc} jobs={args.jobs} "
        f"comp_timeout={args.comp_timeout} comp_jobs={args.comp_jobs}")

    overall_ok = True
    t0 = time.time()

    # -- resolve reference binary --
    if args.ref_bin:
        ref_bin = os.path.abspath(args.ref_bin)
        ref_label = f"ref-bin:{ref_bin}"
    else:
        ref_bin, _ = build_from_rev(tree, args.ref, out_dir, cc, "ref")
        ref_label = f"ref:{args.ref}"

    # -- resolve working (tree) binary + corpus source dir --
    if args.tree_rev:
        tree_bin, tree_src = build_from_rev(tree, args.tree_rev, out_dir, cc, "tree")
        corpus_dir = tree_src
        tree_label = f"tree-rev:{args.tree_rev}"
    else:
        tree_bin = os.path.abspath(args.bin) if args.bin else os.path.join(tree, "build", "pcrec")
        if not os.path.exists(tree_bin):
            log(f"[emit_sweep] {tree_bin} missing; building in place is refused "
                f"(scope mandate) -- pass --bin or build it yourself first")
            sys.exit(2)
        corpus_dir = tree
        tree_label = f"bin:{tree_bin}"

    log(f"[emit_sweep] reference={ref_label} working={tree_label} corpus_dir={corpus_dir}")

    patterns = enumerate_corpus(tree_bin, corpus_dir, args.timeout)
    if args.limit:
        patterns = patterns[:args.limit]
        log(f"[emit_sweep] --limit {args.limit}: truncated corpus to {len(patterns)} rows")
    comp_files = find_files(corpus_dir, (".rxt", ".rxtin"))
    if args.limit:
        comp_files = comp_files[:args.limit]
    log(f"[emit_sweep] corpus: {len(patterns)} pattern rows, "
        f"{len(comp_files)} composition files")

    def run_full_sweep(bin_a, bin_b, label):
        log(f"[emit_sweep] === {label}: stream 1 (.c default engine) ===")
        s1 = sweep_argv_stream("c-default",
                                lambda b, p, t: compile_stream_c(b, p, t, engine=None),
                                patterns, bin_a, bin_b, args.timeout, args.jobs)
        log(f"[emit_sweep] === {label}: stream 2 (.c --engine=vm) ===")
        s2 = sweep_argv_stream("c-vm",
                                lambda b, p, t: compile_stream_c(b, p, t, engine="vm"),
                                patterns, bin_a, bin_b, args.timeout, args.jobs)
        log(f"[emit_sweep] === {label}: stream 3 (--emit-ir --engine=vm) ===")
        s3 = sweep_argv_stream("emit-ir-vm",
                                lambda b, p, t: compile_stream_ir(b, p, t),
                                patterns, bin_a, bin_b, args.timeout, args.jobs)
        log(f"[emit_sweep] === {label}: stream 4 (composition) ===")
        comp_out = os.path.join(out_dir, "comp_" + label.replace(" ", "_"))
        if os.path.exists(comp_out):
            shutil.rmtree(comp_out)
        nonlocal_flag[0] = False
        # [BSWEEP r1 fix, 2026-09-19] A composition FILE can declare many
        # targets in one `--source` invocation (measured:
        # bench_altwide_0_2.rxtin alone is 11 targets / 22 artifacts) --
        # proportionally more compiling per item than one argv pattern, and
        # under this stream's own full concurrency (--jobs parallel
        # composition items, each spawning a multi-target pcrec) that
        # legitimately needs more wall-clock budget than the single-pattern
        # streams do. MEASURED: at the argv streams' own --timeout (30s)
        # and --jobs (12), that one file alone timed out under the
        # resulting contention every time, silently reading as "2 fewer
        # producing files, 24 fewer artifacts" -- not a corpus fact, a
        # self-inflicted contention artifact of this tool's own
        # concurrency (see docs/dev/lanes/bsweep_report.md S1.4 for the
        # full diagnosis). `--comp-timeout` (default max(3x --timeout, 90))
        # and `--comp-jobs` (default min(--jobs, 6), less concurrent
        # pressure per item) fix it -- confirmed by measurement, not by
        # raising the numbers until it stopped happening once.
        s4, producing, artifacts, fixtures_hit = sweep_composition(
            comp_files, bin_a, bin_b, comp_out, args.comp_timeout, args.comp_jobs)
        return s1, s2, s3, s4, producing, artifacts, fixtures_hit, nonlocal_flag[0]

    # -- self-check: two independent builds of the SAME ref revision --
    if not args.no_self_check:
        log("[emit_sweep] === SELF-CHECK: building a second independent copy "
            f"of {ref_label} ===")
        if args.ref_bin:
            selfcheck_bin = ref_bin
        else:
            selfcheck_bin, _ = build_from_rev(tree, args.ref, out_dir, cc, "ref2")
        s1, s2, s3, s4, producing, artifacts, fixtures_hit, deliver_hit = \
            run_full_sweep(ref_bin, selfcheck_bin, "selfcheck")
        print("\n===== SELF-CHECK (ref vs. independent rebuild of the same rev) =====")
        sc_ok = True
        for s, floor_key in ((s1, "reach_default_floor"), (s2, "reach_vm_floor"), (s3, "reach_ir_floor")):
            ok, text = report_stream(s, floor=None, identity_required=True)
            print(text)
            sc_ok = sc_ok and ok
        ok4, text4 = report_stream(s4, floor=None, identity_required=True)
        print(text4)
        sc_ok = sc_ok and ok4
        print(f"self-check reach: default={s1.both_ok} vm={s2.both_ok} ir={s3.both_ok} "
              f"composition producing={producing} artifacts={artifacts}")
        if not sc_ok:
            print("SELF-CHECK FAILED -- the instrument itself disagrees with a rebuild "
                  "of identical source. Not trusting the real comparison. Aborting.")
            sys.exit(1)
        print("SELF-CHECK PASSED: all-identical, no asymmetry, at full reach.")
        overall_ok = overall_ok and sc_ok

    if args.no_real_run:
        print(f"\n(--no-real-run: skipping the real {ref_label} vs {tree_label} comparison)")
        sys.exit(0 if overall_ok else 1)

    # -- the real comparison --
    log(f"[emit_sweep] === REAL RUN: {ref_label} vs {tree_label} ===")
    s1, s2, s3, s4, producing, artifacts, fixtures_hit, deliver_hit = \
        run_full_sweep(ref_bin, tree_bin, "real")

    print(f"\n===== REAL RUN: {ref_label}  vs  {tree_label} =====")
    identity_required_default = not args.only_emit_ir_reach
    ok1, t1 = report_stream(s1, floor=PINS["reach_default_floor"],
                             identity_required=identity_required_default)
    ok2, t2 = report_stream(s2, floor=PINS["reach_vm_floor"],
                             identity_required=identity_required_default)
    ok3, t3 = report_stream(s3, floor=PINS["reach_ir_floor"], identity_required=False)
    ok4, t4 = report_stream(s4, floor=None, identity_required=identity_required_default)
    print(t1); print(t2); print(t3); print(t4)

    run_ok = ok1 and ok2 and ok3 and ok4

    # -- population/composition floors --
    if len(patterns) < PINS["argv_population_floor"]:
        run_ok = False
        print(f"ARGV POPULATION FLOOR VIOLATION: {len(patterns)} < "
              f"{PINS['argv_population_floor']}")
    if len(comp_files) < PINS["composition_files_floor"]:
        run_ok = False
        print(f"COMPOSITION FILES FLOOR VIOLATION: {len(comp_files)} < "
              f"{PINS['composition_files_floor']}")
    if producing < PINS["composition_producing_floor"]:
        run_ok = False
        print(f"COMPOSITION PRODUCING FLOOR VIOLATION: {producing} < "
              f"{PINS['composition_producing_floor']}")
    if artifacts < PINS["composition_artifacts_floor"]:
        run_ok = False
        print(f"COMPOSITION ARTIFACTS FLOOR VIOLATION: {artifacts} < "
              f"{PINS['composition_artifacts_floor']}")

    # -- the DELIVER witness --
    missing_fixtures = [n for n, hit in fixtures_hit.items() if not hit]
    if missing_fixtures:
        run_ok = False
        print(f"DELIVER WITNESS FAILURE: fixture(s) did not produce: {missing_fixtures}")
    if not deliver_hit:
        run_ok = False
        print("DELIVER WITNESS FAILURE: no composition artifact anywhere in the sweep "
              "carries the cross-group SET-pair shape (see DELIVER_RE's header comment) "
              "-- the composition arm may not be reaching vm_splice's DELIVER block.")
    else:
        print("DELIVER witness: OK (at least one composition artifact carries the "
              "cross-group SET-pair shape; both named fixtures produced).")

    print(f"\npopulation: argv={len(patterns)} composition_files={len(comp_files)} "
          f"composition_producing={producing} composition_artifacts={artifacts}")
    print(f"elapsed: {time.time() - t0:.1f}s")

    overall_ok = overall_ok and run_ok

    if not args.keep:
        for d in ("comp_selfcheck", "comp_real"):
            p = os.path.join(out_dir, d)
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True)

    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
