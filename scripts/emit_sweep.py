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
own build, or an explicit --bin/second revision), across SIX streams, the
first four under --features all (and under `--extra`, below), plus two
optional families ([START-TABLE] C0, docs/design/start_table.md §3.2-§3.3):

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
  5. registry dumps: the seven `--list-*` surfaces, whole-file byte
     comparison ([REVW.4] wave 4). Streams 1-4 compare EMITTED ARTIFACTS and
     no `--list-*` surface appears in any of them, so a change that re-derives
     what `--list-axes` prints is invisible to all four -- see sweep_dumps'
     own comment. Always identity-required.
  6. facts: `--emit-facts=byte,utf8` over streams 1/2's patterns ([START-
     TABLE] C0). The facts listing's `used` column records which facts a
     predicate ASKED; it is the only stream that sees an ask that changes no
     emitted byte. Both encodings in one call, so `--extra` never reaches it.
     Identity-required.

  ARMS (`--arms start`, or one arm via `--extra`). An arm is (BASE, FLAG): a
  base option set (`byte` = nothing, `utf8` = `-e utf8`) and the flag under
  test, both spliced into the argv by ONE function (`opt_argv`). Streams 1-2
  run at BASE+FLAG on both sides (identity required), AND each side counts
  the distinct patterns whose bytes (and whose start stamps) DIFFER from the
  same side's BASE compile. An arm that silently dropped its flag would be
  byte-identical to its base and pass identity, so identity alone cannot fail
  on the arm's own plumbing: the DIFFER count is held against a pinned FLOOR
  (DIFFER_PINS, from docs/design/start_table/deny_census.tsv and
  plain_arms.tsv), a MANIFEST names one pattern per arm that must differ, a
  few cells are an asserted EXACT 0 (`-fno-end-window` at utf8: W1's fact
  declines every multi-byte encoding), and a NULL arm (an empty flag) must
  read exactly 0 on every population.

  TRACE (`--trace`): both sides built with `-DPCREC_CAND_TRACE` (the
  `cflags` pass-through of build_from_rev), streams 1-2 compiled with stderr
  captured, every `CANDTRACE` record tagged with its pattern index and arm
  BY THIS SCRIPT, and the per-pattern ORDERED sequences compared by
  scripts/trace_diff.py (declared-multiplicity filter, records-per-arm
  floor). The trace build's stdout must equal the default build's.

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
  --streams LIST         comma list of the six streams to run (default all:
                        c-default,c-vm,emit-ir,composition,dumps,facts).
                        A floor of a stream not run is not applied.
  --extra=ARGS           repeatable; shell-split and appended to streams 1-4
                        on BOTH sides, before the pattern. With --extra the
                        run is ONE ARM: streams 1-2 also count DIFFER against
                        --extra-base, and fail unless DIFFER_PINS has a floor
                        for it (--no-differ-floor to waive, loudly).
  --extra-base=ARGS      the arm's base (default nothing; `-e utf8` is the
                        utf8 base), also on every stream.
  --arms start           every DIFFER_PINS arm (the start-family deny arms at
                        byte and utf8, plain `-e utf8`, `-i`, the null arm),
                        streams 1-2, over the DISTINCT patterns. Exclusive
                        with --extra.
  --patterns-file FILE   constructed witnesses (one per line, --list-source
                        escapes \\t \\n \\r \\\\ \\xNN; `#` and blank lines
                        skipped) ADDED to streams 1-3, 6, the arms and the
                        trace. Repeatable.
  --no-corpus            drop the corpus (and the composition files): the
                        population is the patterns files alone. Floors are
                        then NOT applied (said so); identity, manifests in
                        the population, asserted zeros and the null arm are.
  --every K              keep every K-th distinct pattern (sorted, as
                        deny_census.py --every does) for the arms and the
                        trace: a sample; floors not applied.
  --trace                the trace family (above). Needs --tree-rev, or
                        --trace-bin (and optionally --trace-ref-bin).
  --trace-declared FILE  the commit's declared-multiplicity file for
                        trace_diff.py (sites whose records may be added).
  --trace-unordered      compare each pattern-arm's SET of records (order and
                        ask multiplicity ignored; see trace_diff.py).
  --build-cflags=FLAGS   CFLAGS for every build this run makes (default: the
                        tree's own Makefile default).

  When the two sides are the SAME binary (realpath), every argv compile runs
  once and is mirrored: identity is trivial and said so, and the run is a
  measurement (reach, DIFFER counts, trace records) at half the cost.

EXIT STATUS: 0 if every stream is clean against its floor/identity
requirement and the DELIVER witness holds; 1 otherwise. Report is printed
to stdout; a full per-row TSV per stream is written under --out.
"""
import argparse
import concurrent.futures
import hashlib
import os
import re
import shlex
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
    # [REVW.4] the dumps stream: all seven registry surfaces must ANSWER on
    # both sides. A surface that starts refusing collapses this to 6 and fails
    # here rather than silently shrinking the comparison.
    "dump_surfaces_floor": 7,
    # total .rxt + .rxtin files under tests/ (the composition population).
    "composition_files_floor": 300,       # measured 304
    # corpus pattern/pattern-esc rows found by --list-source over tests/**/*.rxt.
    "argv_population_floor": 3900,        # measured 3,938
    # rows where BOTH sides compile successfully, per stream (--features all).
    "reach_default_floor": 3480,          # measured 3,517 (stream 1)
    "reach_vm_floor": 3480,               # measured 3,518 (stream 2)
    "reach_ir_floor": 3480,               # measured 3,518 (stream 3)
    # [START-TABLE] C0 stream 6 (--emit-facts=byte,utf8): PROVISIONAL at the
    # argv floors' value until C0's full run measures it.
    "reach_facts_floor": 3480,
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
# THE ARMS ([START-TABLE] C0; docs/design/start_table.md §3.3 items 2 and 4).
#
# The bases an arm's flag is applied on top of. `utf8` reaches the compiler
# through the same opt_argv splice as every flag, so an arm table whose
# utf8 base silently dropped `-e utf8` measures the BYTE delta against the
# BYTE base; the cells that catch that BY DESIGN are the asserted zeros
# (byte reads 288 there) and the plain `-e utf8` arm's own floors.
ARM_BASES = {"byte": (), "utf8": ("-e", "utf8")}

# (base, flag, stream) -> (bytes_floor, stamp_floor, manifest). The DIFFER
# count is over DISTINCT corpus patterns (deny_census.py's population, so the
# two instruments count the same set), per side: patterns that compile under
# both BASE and BASE+FLAG and whose emitted bytes differ (bytes_floor), and of
# those, how many moved a start-family stamp (stamp_floor; start_keys_moved
# below). The manifest is one named pattern that must differ on each side
# (the shortest mover in deny_movers.tsv; for the plain arms `a`, and for
# -fno-length-prune `(a)*b`, the shortest corpus mover found by probing): a floor answers "did a lot stop
# moving", the manifest "did THIS one" (learnings §3: exact counts disarm
# themselves; a manifest names an irreplaceable row). A (0, 0, None) cell is
# a flag that does not act on that route (offset-skip has no VM arm): its
# only check is identity, and it is listed so the population is complete.
# Floors sit AT the measured value: the arms run at a no-mover commit with
# one corpus on both sides, so a count below it is a corpus change, which is
# a reviewed re-pin (PINS' own argument), or a plumbing loss.
#
# Measured: deny_census.tsv / plain_arms.tsv at main 4743ebb5 (start_table.md
# §3.4 and §3.3 item 2); -fno-length-prune from allflags_sample.tsv's 1-in-10
# sample, a LOWER BOUND (a subset's movers never exceed the whole's), to be
# re-pinned from the full every-flag sweep.
DIFFER_PINS = {
    # plain arms: the encoding and caseless populations (§3.3 item 2)
    ("byte", "-e utf8", "c-default"): (3188, 674, b"a"),
    ("byte", "-e utf8", "c-vm"): (3189, 341, b"a"),
    ("byte", "-i", "c-default"): (3221, 1752, b"a"),
    ("byte", "-i", "c-vm"): (3222, 1567, b"a"),
    ("utf8", "-i", "c-default"): (3229, 1775, b"a"),
    ("utf8", "-i", "c-vm"): (3230, 1605, b"a"),
    # the start-family deny/force arms (§3.4's table), byte base
    ("byte", "-fno-offset-skip", "c-default"): (513, 513, b"ab"),
    ("byte", "-fno-offset-skip", "c-vm"): (0, 0, None),
    ("byte", "-fno-run-prefilter", "c-default"): (132, 132, b"fi"),
    ("byte", "-fno-run-prefilter", "c-vm"): (0, 0, None),
    ("byte", "-fno-start-set", "c-default"): (136, 136, b"\\Bx"),
    ("byte", "-fno-start-set", "c-vm"): (2327, 2327, b"."),
    ("byte", "-fno-start-pinned", "c-default"): (183, 183, b".*"),
    ("byte", "-fno-start-pinned", "c-vm"): (0, 0, None),
    ("byte", "-fno-req-set-lead", "c-default"): (14, 0, "é{2}cat".encode()),
    ("byte", "-fno-req-set-lead", "c-vm"): (16, 0, "é{2}cat".encode()),
    ("byte", "-fno-req-handoff", "c-default"): (163, 163, b"SS"),
    ("byte", "-fno-req-handoff", "c-vm"): (0, 0, None),
    ("byte", "-fno-hyb-reseed", "c-default"): (403, 403, b"a*+a"),
    ("byte", "-fno-hyb-reseed", "c-vm"): (0, 0, None),
    ("byte", "-fno-vm-anchor-bound", "c-default"): (337, 337, b"^(a)"),
    ("byte", "-fno-vm-anchor-bound", "c-vm"): (488, 488, b"^"),
    ("byte", "-fno-end-window", "c-default"): (288, 288, b"$"),
    ("byte", "-fno-end-window", "c-vm"): (288, 288, b"$"),
    ("byte", "-fno-req-byte", "c-default"): (2639, 2043, b"$"),
    ("byte", "-fno-req-byte", "c-vm"): (3222, 2043, b"$"),
    ("byte", "-fno-req-run", "c-default"): (530, 301, b"SS"),
    ("byte", "-fno-req-run", "c-vm"): (530, 17, b"SS"),
    ("byte", "-fno-req-run-fold", "c-default"): (48, 32, b"(?i)abc"),
    ("byte", "-fno-req-run-fold", "c-vm"): (48, 17, b"(?i)abc"),
    ("byte", "-fprefilter-collapse", "c-default"): (213, 212, b"(a){3}"),
    ("byte", "-fprefilter-collapse", "c-vm"): (0, 0, None),
    ("byte", "-fno-length-prune", "c-default"): (46, 11, b"(a)*b"),
    ("byte", "-fno-length-prune", "c-vm"): (69, 0, b"(a)*b"),
    # the same arms, utf8 base
    ("utf8", "-fno-offset-skip", "c-default"): (604, 604, b"SS"),
    ("utf8", "-fno-offset-skip", "c-vm"): (0, 0, None),
    ("utf8", "-fno-run-prefilter", "c-default"): (3, 3, b"aa(?i:a)"),
    ("utf8", "-fno-run-prefilter", "c-vm"): (0, 0, None),
    ("utf8", "-fno-start-set", "c-default"): (127, 127, b"\\Bx"),
    ("utf8", "-fno-start-set", "c-vm"): (2352, 2352, b"."),
    ("utf8", "-fno-start-pinned", "c-default"): (183, 183, b".*"),
    ("utf8", "-fno-start-pinned", "c-vm"): (0, 0, None),
    ("utf8", "-fno-req-set-lead", "c-default"): (8, 0, b"a{3}(?i:cat)"),
    ("utf8", "-fno-req-set-lead", "c-vm"): (8, 0, b"a{3}(?i:cat)"),
    ("utf8", "-fno-req-handoff", "c-default"): (280, 280, b"123"),
    ("utf8", "-fno-req-handoff", "c-vm"): (0, 0, None),
    ("utf8", "-fno-hyb-reseed", "c-default"): (420, 420, b"a*+a"),
    ("utf8", "-fno-hyb-reseed", "c-vm"): (0, 0, None),
    ("utf8", "-fno-vm-anchor-bound", "c-default"): (337, 337, b"^(a)"),
    ("utf8", "-fno-vm-anchor-bound", "c-vm"): (488, 488, b"^"),
    ("utf8", "-fno-end-window", "c-default"): (0, 0, None),   # ASSERT_ZERO
    ("utf8", "-fno-end-window", "c-vm"): (0, 0, None),        # ASSERT_ZERO
    ("utf8", "-fno-req-byte", "c-default"): (2631, 2071, b"$"),
    ("utf8", "-fno-req-byte", "c-vm"): (3230, 2071, b"$"),
    ("utf8", "-fno-req-run", "c-default"): (572, 299, b"SS"),
    ("utf8", "-fno-req-run", "c-vm"): (572, 15, b"SS"),
    ("utf8", "-fno-req-run-fold", "c-default"): (38, 31, b"(?i)abc"),
    ("utf8", "-fno-req-run-fold", "c-vm"): (38, 15, b"(?i)abc"),
    ("utf8", "-fprefilter-collapse", "c-default"): (213, 211, b"(a){3}"),
    ("utf8", "-fprefilter-collapse", "c-vm"): (0, 0, None),
    ("utf8", "-fno-length-prune", "c-default"): (49, 11, b"(a)*b"),
    ("utf8", "-fno-length-prune", "c-vm"): (85, 0, b"(a)*b"),
}

# Cells that must read EXACTLY 0 on every population (a zero holds on any
# subset, so these apply under --no-corpus/--every too). W1's fact declines
# every non-boundary encoding, so -fno-end-window cannot act at utf8 — and a
# utf8 base that lost `-e utf8` reads byte's 288 here.
ASSERT_ZERO = {("utf8", "-fno-end-window", "c-default"),
               ("utf8", "-fno-end-window", "c-vm")}

# The NULL arm: the flag is empty, so BASE+FLAG is BASE's argv and the
# DIFFER count must be exactly 0 (a deterministic compiler). It proves the
# counter reads 0 where nothing changed — the arithmetic half of "a dropped
# flag reads 0, below every nonzero floor".
NULL_ARM = ("byte", "", "c-default")

ARM_STREAMS = {"c-default": None, "c-vm": "vm"}


def arm_table():
    """[(base, flag)] in DIFFER_PINS order, the null arm first."""
    seen, out = set(), [(NULL_ARM[0], NULL_ARM[1])]
    for base, flag, _ in DIFFER_PINS:
        if (base, flag) not in seen:
            seen.add((base, flag))
            out.append((base, flag))
    return out


# ---------------------------------------------------------------------------
# THE START-FAMILY STAMPS — the one implementation (moved here from
# docs/design/start_table/row_census.py at [START-TABLE] C0, which now
# imports it, so the census and this gate cannot disagree about what "a
# start stamp moved" means).
START_STAMPS = ["DFA_SCAN", "DFA_PREFILTER", "DFA_START", "VM_PREFILTER",
                "VM_PREFILTER_LANG", "VM_START", "VM_START_SCAN", "VM_RESEED",
                "REQ_WHY", "REQ_HANDOFF", "END_WINDOW", "ENGINE"]
STAMP_RX = re.compile(rb'^#define RX_([A-Z_]+) (.*)$', re.M)

# The DFA-shaped body's ROUTE is a function of the PREFILTER's engine
# (job->engine: ENG_UNANCH / ENG_ATTEMPT / empty), never of fit.chosen
# ([r2 sound-M1]): a VM hybrid whose prefilter machine is ENG_ATTEMPT is an
# ATTEMPT-route customer. ROUTE classes, disjoint by construction:
#   DFA-UNANCH  DFA-ATTEMPT  DFA-EMPTY     (ENGINE "dfa", by DFA_SCAN)
#   HYB-UNANCH  HYB-ATTEMPT  HYB-EMPTY     (ENGINE "vm", VM_PREFILTER "hybrid")
#   VM-ONLY                                (ENGINE "vm", VM_PREFILTER "none")
ROUTE_KEYED = ["DFA_PREFILTER", "DFA_START", "REQ_WHY", "REQ_HANDOFF",
               "VM_START", "VM_START_SCAN", "VM_RESEED", "END_WINDOW"]
SCAN_ROUTE = {'"unanchored"': "UNANCH", '"attempt"': "ATTEMPT", '"empty"': "EMPTY"}


def route_of(d):
    eng = d.get("ENGINE")
    if eng == '"dfa"':
        return "DFA-" + SCAN_ROUTE.get(d.get("DFA_SCAN"), "?")
    if eng == '"vm"':
        if d.get("VM_PREFILTER") == '"hybrid"':
            return "HYB-" + SCAN_ROUTE.get(d.get("DFA_SCAN"), "?")
        return "VM-ONLY"
    return "?"


def stamps_of(stdout):
    """The start-family stamps of one emitted artifact, plus ROUTE-keyed
    joint keys (one artifact, one route class: no double count)."""
    d = {}
    for k, v in STAMP_RX.findall(stdout):
        k = k.decode()
        if k in START_STAMPS:
            v = v.decode().strip()
            if k == "REQ_HANDOFF" and v != '"none"':
                v = '"<K>"'
            if k == "END_WINDOW" and v != '"none"':
                v = '"<W>"'
            d[k] = v
    route = route_of(d)
    d["ROUTE"] = route
    for k in ROUTE_KEYED:
        if k in d:
            d[route + ":" + k] = d[k]
    # The start bound literals, read off the text (B1/B2/B5 have no stamp):
    m = re.search(rb"const size_t start_max = ([^;]*);", stdout)
    if m:
        d[route + ":start_max"] = ("0" if m.group(1).startswith(b"0") else
                                   "search_from" if m.group(1).startswith(b"search_from")
                                   else "n")
    if re.search(rb"const size_t attempt_max = search_from;", stdout):
        d[route + ":attempt_max"] = "search_from"
    # H1 (root-minimum-width ceiling) is read TWO ways ([r2 checks-M4 H1]):
    #  - the stamp's VALUE against the constant's printed spelling (shares
    #    PCREC_MINW_MAX with the code, so alone it is not a control);
    #  - the EMITTED TEST itself (the row's body text), which shares nothing
    #    with the constant. The census prints both; they must agree.
    m = re.search(rb'^#define RX_VM_ROOT_MINW (\S+)', stdout, re.M)
    if m:
        d["VM_ROOT_MINW_CEIL"] = "yes" if m.group(1) == b"1099511627776ULL" else "no"
        d["H1_TEST_EMITTED"] = "yes" if b"_VM_ROOT_MINW) return 0;" in stdout else "no"
    return d


def start_keys_moved(s0, s1):
    """The start-stamp keys that differ between two stamps_of() results:
    plain keys (ROUTE itself excluded — it is derived from ENGINE/DFA_SCAN/
    VM_PREFILTER, which are keys) then route-keyed ones. Empty = a HIDDEN
    mover (bytes moved, no start stamp did)."""
    keys = set(s0) | set(s1)
    plain = sorted(k for k in keys if ":" not in k and k != "ROUTE" and s0.get(k) != s1.get(k))
    routed = sorted(k for k in keys if ":" in k and s0.get(k) != s1.get(k))
    return plain + routed


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


def build_from_rev(repo_for_archive, rev, out_dir, cc, label, timeout=600,
                   cflags=None):
    """git archive REV | tar -x into out_dir/src_<label>, then `make -j4
    CC=$cc` (plus `CFLAGS=$cflags` when given -- [START-TABLE] C0's
    pass-through, so a `-D` define such as -DPCREC_CAND_TRACE reaches a
    side; the caller passes the SAME cflags to both sides). Returns
    (bin_path, src_dir). Never touches any live build/ directory -- this is
    always a fresh extraction into scratch."""
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
    log(f"[emit_sweep] building {label} (CC={cc} CFLAGS={cflags or '<default>'}) ...")
    make_argv = ["make", "-j4", f"CC={cc}"] + ([f"CFLAGS={cflags}"] if cflags else [])
    r = subprocess.run(make_argv, cwd=src_dir,
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


# [REL-1.10]/D118: REF is built from an arbitrary `git archive REV` and may
# predate the gcc-shaped CLI flip; WORKING is usually the tree's own current
# build but can itself be `--bin`/a second REVISION. Neither side's dialect
# can be assumed, so each binary is probed ONCE (its own --help text names
# --pattern iff this build has it) and cached, rather than hard-coding one
# grammar for both sides the way this file did before the flip existed.
_dialect_cache = {}


def pcrec_speaks_pattern_flag(pcrec_bin):
    """True iff `pcrec_bin` understands --pattern / a positional FILE
    operand (D118) rather than the retired positional-pattern / --source
    grammar."""
    if pcrec_bin not in _dialect_cache:
        try:
            r = subprocess.run([pcrec_bin, "--help"], capture_output=True,
                               text=True, timeout=10)
            # "--pattern" alone, never "--pattern-esc" (a flag every
            # pre-D118 build also has, which made a naive substring test
            # false-positive on the OLD grammar during this fix's own
            # first validation run).
            import re as _re
            _dialect_cache[pcrec_bin] = bool(_re.search(r'--pattern(?!-)', r.stdout + r.stderr))
        except Exception:
            _dialect_cache[pcrec_bin] = True   # assume current grammar
    return _dialect_cache[pcrec_bin]


def opt_argv(extra):
    """THE ONE SPLICE POINT for every option an arm, `--extra` or
    `--extra-base` adds to a compile ([START-TABLE] C0). Every argv builder
    below calls it, so a plumbing loss is one loss for all of them -- and the
    DIFFER floors, the null arm and the asserted zeros are what catch it
    (tests/mech's emitsweep rows plant exactly that loss here)."""
    return [a.decode("utf-8", "surrogateescape") if isinstance(a, bytes) else a
            for a in extra]


def _pattern_argv(pcrec_bin, pattern):
    return ["--pattern", pattern] if pcrec_speaks_pattern_flag(pcrec_bin) else ["--", pattern]


def compile_stream_c(pcrec_bin, pattern, timeout, engine=None, extra=(),
                     want_err=False):
    argv = [pcrec_bin, "-p", "rx", "--features", "all"]
    if engine:
        argv.append(f"--engine={engine}")
    argv += opt_argv(extra)
    # `-o -` on BOTH sides on purpose: the emitted .c carries `#include "<basename>.h"`
    # derived from -o, so writing a.c vs b.c reads 100% movers with an innocent compiler
    # (the -o basename trap, fifth instance: dd8_report.md §3.1). Vary NOTHING the artifact
    # can observe; the composition arm likewise writes fixture-named files into fresh dirs.
    argv += ["-o", "-"]
    argv += _pattern_argv(pcrec_bin, pattern)
    rc, out, err = run(argv, timeout)
    ok = rc == 0
    if want_err:
        # the trace stream: stderr is the trace, NEVER mixed into the artifact
        return ok, (out if ok else None), err
    return ok, (out if ok else None), ("" if ok else _err_tail(err))


def compile_stream_ir(pcrec_bin, pattern, timeout, extra=()):
    argv = [pcrec_bin, "--features", "all", "--engine=vm"] + opt_argv(extra) + ["--emit-ir"]
    argv += _pattern_argv(pcrec_bin, pattern)
    rc, out, err = run(argv, timeout)
    ok = rc == 0
    return ok, (out if ok else None), ("" if ok else _err_tail(err))


def compile_stream_facts(pcrec_bin, pattern, timeout):
    """Stream 6: the facts listing for BOTH encodings in one call -- so no
    `--extra` (an `-e` there would fight the listing's own encoding list)."""
    argv = [pcrec_bin, "--features", "all", "--emit-facts=byte,utf8"]
    argv += _pattern_argv(pcrec_bin, pattern)
    rc, out, err = run(argv, timeout)
    ok = rc == 0
    return ok, (out if ok else None), ("" if ok else _err_tail(err))


def run_composition(pcrec_bin, rxt_file, out_root, tag, timeout, extra=()):
    """A FILE operand (post-D118) or `--source FILE` (pre-D118) -o <fresh
    dir>, whichever `pcrec_bin` speaks; returns (rc, {filename: bytes})."""
    outdir = os.path.join(out_root, tag)
    os.makedirs(outdir, exist_ok=True)
    if pcrec_speaks_pattern_flag(pcrec_bin):
        argv = [pcrec_bin, "--features", "all"] + opt_argv(extra) + [rxt_file, "-o", outdir]
    else:
        argv = [pcrec_bin, "--features", "all"] + opt_argv(extra) + ["--source", rxt_file, "-o", outdir]
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
        self.mirrored = False  # both sides one binary: identity trivial
        self.hash_a = {}       # pattern index -> sha256 of side a's output
        self.hash_b = {}


def same_binary(bin_a, bin_b):
    """Both sides are one file: compile once and mirror (a MEASUREMENT run;
    identity is trivial and the report says so)."""
    return os.path.realpath(bin_a) == os.path.realpath(bin_b)


def sha(b):
    return hashlib.sha256(b).hexdigest() if b is not None else None


def sweep_argv_stream(name, compile_fn, patterns, bin_a, bin_b, timeout, jobs):
    res = StreamResult(name)
    res.population = len(patterns)
    mirror = same_binary(bin_a, bin_b)
    res.mirrored = mirror

    def one(item):
        f, kind, pat = item
        ok_a, c_a, e_a = compile_fn(bin_a, pat, timeout)
        if mirror:
            ok_b, c_b, e_b = ok_a, c_a, e_a
        else:
            ok_b, c_b, e_b = compile_fn(bin_b, pat, timeout)
        key = f"{f}:{kind}:{pat[:60]!r}"
        return key, ok_a, c_a, e_a, ok_b, c_b, e_b

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for idx, (key, ok_a, c_a, e_a, ok_b, c_b, e_b) in enumerate(ex.map(one, patterns)):
            # per-index output hashes: the trace family checks that the trace
            # build's stdout equals THIS (the default build's) per pattern.
            res.hash_a[idx], res.hash_b[idx] = sha(c_a), sha(c_b)
            if ok_a and ok_b:
                res.both_ok += 1
                if c_a != c_b:
                    res.movers.append((key, first_diff_hunk(c_a, c_b)))
            elif not ok_a and not ok_b:
                res.both_refuse += 1
            else:
                res.asymmetric.append((key, ok_a, ok_b, e_a, e_b))
    return res


def sweep_composition(files, bin_a, bin_b, out_root, timeout, jobs, extra=()):
    res = StreamResult("composition")
    res.population = len(files)
    producing = 0
    artifact_count = 0
    deliver_seen = False
    fixture_produced = {name: False for name in DELIVER_FIXTURES}

    def one(item):
        idx, f = item
        tag = f"f{idx}"
        rc_a, art_a, e_a = run_composition(bin_a, f, os.path.join(out_root, "a"), tag, timeout, extra)
        rc_b, art_b, e_b = run_composition(bin_b, f, os.path.join(out_root, "b"), tag, timeout, extra)
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
# The FIFTH stream: the REGISTRY DUMPS ([REVW.4] wave 4).
#
# The four streams above compare EMITTED ARTIFACTS. Nothing in them reads a
# `--list-*` surface, so a change that re-derives what `--list-axes` or
# `--list-limits` prints -- exactly what [REVW.4]'s axes.def extraction does --
# is invisible to all four and reads as a clean green (w4_facts.md open
# question 6 named the gap). These are seven whole-file byte comparisons and
# cost under a second; the population is the SURFACE LIST, pinned below, so a
# dump that stops existing is a FAILED row rather than a smaller population.
DUMP_SURFACES = ("--list-syntax", "--list-definitions", "--list-verbs",
                 "--list-families", "--list-axes", "--list-limits",
                 "--list-schema")


def sweep_dumps(bin_a, bin_b, timeout):
    res = StreamResult("dumps")
    res.population = len(DUMP_SURFACES)
    for flag in DUMP_SURFACES:
        rc_a, out_a, err_a = run([bin_a, flag], timeout)
        rc_b, out_b, err_b = run([bin_b, flag], timeout)
        ok_a, ok_b = rc_a == 0, rc_b == 0
        if ok_a != ok_b:
            res.asymmetric.append((flag, ok_a, ok_b, _err_tail(err_a), _err_tail(err_b)))
        elif not ok_a:
            res.both_refuse += 1
        elif out_a != out_b:
            res.both_ok += 1
            res.movers.append((flag, first_diff_hunk(out_a, out_b)))
        else:
            res.both_ok += 1
    return res


# ---------------------------------------------------------------------------
# --patterns-file: constructed witnesses ([START-TABLE] C0, [r2 checks-m7]).

def encode_escape(b):
    """decode_escape's inverse (the --list-source vocabulary), for writing a
    patterns file: \\t \\n \\r \\\\ literally, every other byte outside
    printable ASCII as \\xNN."""
    out = []
    for c in b:
        if c == 0x5C:
            out.append("\\\\")
        elif c == 0x09:
            out.append("\\t")
        elif c == 0x0A:
            out.append("\\n")
        elif c == 0x0D:
            out.append("\\r")
        elif 0x20 <= c < 0x7F:
            out.append(chr(c))
        else:
            out.append(f"\\x{c:02x}")
    return "".join(out)


def read_patterns_file(path):
    """One pattern per line in --list-source escapes; `#` lines and blank
    lines skipped. An EMPTY file is an error, never an empty population."""
    rows = []
    with open(path, encoding="utf-8", errors="surrogateescape") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            rows.append((f"patterns-file:{os.path.basename(path)}", "pattern",
                         decode_escape(line)))
    if not rows:
        raise SystemExit(f"[emit_sweep] --patterns-file {path}: no patterns (K35)")
    return rows


def distinct_patterns(patterns, every=1):
    """The arms' and deny census's population: distinct pattern BYTES,
    sorted, every K-th kept (deny_census.py's exact rule, so a sample here
    and a sample there are the same set)."""
    return sorted(set(p[2] for p in patterns))[::every]


# ---------------------------------------------------------------------------
# THE ARMS sweep (DIFFER_PINS' header says what it checks and why).

class ArmResult:
    def __init__(self, base, flag, stream):
        self.base, self.flag, self.stream = base, flag, stream
        self.ok_base = [0, 0]      # per side: compiled under BASE
        self.ok_arm = [0, 0]       # per side: compiled under BASE+FLAG
        self.differ = [0, 0]       # per side: both compiled, bytes differ
        self.stamp = [0, 0]        # per side: of those, a start stamp moved
        self.refusal = [0, 0]      # per side: one of BASE / BASE+FLAG refused
        self.manifest_hit = [False, False]
        self.movers = []           # (pattern, hunk): side a vs side b at BASE+FLAG
        self.asymmetric = []       # (pattern, ok_a, ok_b)


def sweep_arms(arms, pats, bin_a, bin_b, timeout, jobs):
    """arms: [(base_name, base_args, flag_str)]; pats: distinct bytes.
    Returns {(base, flag, stream): ArmResult} plus base-identity results
    {(base, stream): ArmResult} (flag "" there: the base itself, a vs b)."""
    mirror = same_binary(bin_a, bin_b)
    bases = {}
    for base, base_args, flag in arms:
        bases[base] = base_args
    results = {}
    for stream in ARM_STREAMS:
        for base in bases:
            results[(base, "<base>", stream)] = ArmResult(base, "<base>", stream)
        for base, _, flag in arms:
            results[(base, flag, stream)] = ArmResult(base, flag, stream)
    manifests = {k: v[2] for k, v in DIFFER_PINS.items() if v[2] is not None}

    def compile_pair(p, engine, args):
        a = compile_stream_c(bin_a, p, timeout, engine=engine, extra=args)
        b = a if mirror else compile_stream_c(bin_b, p, timeout, engine=engine, extra=args)
        return a, b

    def side_cmp(arm_side, base_side):
        """(ok, base_ok, refusal, differ, stamp) of one side's arm compile
        against the same side's base compile."""
        ok, c = arm_side[0], arm_side[1]
        bok, bc = base_side[0], base_side[1]
        if ok != bok:
            return ok, bok, True, False, False
        if ok and c != bc:
            return ok, bok, False, True, bool(start_keys_moved(stamps_of(bc), stamps_of(c)))
        return ok, bok, False, False, False

    def job(p):
        # compares INSIDE the worker and returns small tuples, never the
        # artifacts: 30-odd arms x two streams of a large artifact would
        # otherwise sit in ex.map's buffer.
        out = []
        for stream, engine in ARM_STREAMS.items():
            base_out = {}
            for base, base_args in bases.items():
                ra, rb = base_out[base] = compile_pair(p, engine, list(base_args))
                hunk = first_diff_hunk(ra[1], rb[1]) if ra[0] and rb[0] and ra[1] != rb[1] else None
                out.append(((base, "<base>", stream), ra[0], rb[0], hunk, None))
            for base, base_args, flag in arms:
                ra, rb = compile_pair(p, engine, list(base_args) + shlex.split(flag))
                hunk = first_diff_hunk(ra[1], rb[1]) if ra[0] and rb[0] and ra[1] != rb[1] else None
                ba, bb = base_out[base]
                out.append(((base, flag, stream), ra[0], rb[0], hunk,
                            (side_cmp(ra, ba), side_cmp(rb, bb))))
        return p, out

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for p, out in ex.map(job, pats):
            for key, ok_a, ok_b, hunk, sides in out:
                r = results[key]
                if ok_a != ok_b:
                    r.asymmetric.append((p, ok_a, ok_b))
                elif hunk is not None:
                    r.movers.append((p, hunk))
                if sides is None:
                    r.ok_base[0] += ok_a
                    r.ok_base[1] += ok_b
                    continue
                for side, (ok, bok, refusal, differ, stamp) in enumerate(sides):
                    r.ok_arm[side] += ok
                    r.ok_base[side] += bok
                    r.refusal[side] += refusal
                    r.differ[side] += differ
                    r.stamp[side] += stamp
                    if differ and manifests.get(key) == p:
                        r.manifest_hit[side] = True
    return results, mirror


def report_arms(results, pats, full_population, mirror, waive_unpinned=False):
    """Every check of the arms family; returns (ok, text, tsv_rows)."""
    lines = ["-- family: arms (streams 1-2, distinct patterns) --",
             f"  population={len(pats)} full_corpus={'yes' if full_population else 'NO (floors NOT applied)'}"
             f" sides={'ONE BINARY (identity trivial; a measurement)' if mirror else 'two'}"]
    ok = True
    rows = []
    patset = set(pats)
    for key, r in results.items():
        base, flag, stream = key
        verdict = []
        if r.asymmetric:
            verdict.append(f"ASYMMETRIC {len(r.asymmetric)} (first {r.asymmetric[0][0]!r})")
        if r.movers:
            verdict.append(f"MOVERS {len(r.movers)} (first {r.movers[0][0]!r}:\n"
                           + "\n".join("      " + h for h in r.movers[0][1].splitlines()) + ")")
        if flag != "<base>":
            if flag == NULL_ARM[1] or key in ASSERT_ZERO:
                if r.differ != [0, 0] or r.refusal != [0, 0]:
                    verdict.append(f"ASSERTED ZERO VIOLATED: differ={r.differ} refusal={r.refusal}")
            elif key not in DIFFER_PINS:
                if not waive_unpinned:
                    verdict.append("NO DIFFER FLOOR PINNED (an arm that cannot fail on its "
                                   "own plumbing is not a check; --no-differ-floor waives)")
            else:
                bf, sf, man = DIFFER_PINS[key]
                if man is not None:
                    if man in patset:
                        if r.manifest_hit != [True, True]:
                            verdict.append(f"MANIFEST {man!r} did not differ (sides {r.manifest_hit})")
                    elif full_population:
                        verdict.append(f"MANIFEST {man!r} NOT IN THE POPULATION (K35)")
                if full_population:
                    for side in (0, 1):
                        if r.differ[side] < bf:
                            verdict.append(f"DIFFER FLOOR side {'ab'[side]}: {r.differ[side]} < {bf}")
                        if r.stamp[side] < sf:
                            verdict.append(f"STAMP FLOOR side {'ab'[side]}: {r.stamp[side]} < {sf}")
        if verdict:
            ok = False
        bf, sf, _ = DIFFER_PINS.get(key, ("-", "-", None))
        rows.append((base, flag, stream, r.ok_base[0], r.ok_arm[0], r.differ[0], r.differ[1],
                     r.stamp[0], r.stamp[1], r.refusal[0], r.refusal[1], len(r.movers),
                     len(r.asymmetric), bf, sf, "FAIL" if verdict else "ok"))
        tag = f"{base:4s} {flag or '<null>':22s} {stream:9s}"
        lines.append(f"  {tag} differ={r.differ[0]}/{r.differ[1]} stamp={r.stamp[0]}/{r.stamp[1]}"
                     f" refusal={r.refusal[0]}/{r.refusal[1]} floor={bf}/{sf}"
                     + ("" if not verdict else "  <-- " + "; ".join(verdict)))
    return ok, "\n".join(lines), rows


ARMS_TSV_HEADER = ("base\tflag\tstream\tok_base\tok_arm\tdiffer_a\tdiffer_b\tstamp_a\tstamp_b"
                   "\trefusal_a\trefusal_b\tmovers\tasymmetric\tfloor\tstamp_floor\tverdict\n")


# ---------------------------------------------------------------------------
# THE TRACE family ([START-TABLE] C0 deliverable (i)-(vi), §3.3 item 5).

TRACE_CFLAGS = "-O2 -g -DPCREC_CAND_TRACE"
TRACE_TAG = b"CANDTRACE\t"
# Records-per-arm floor (a trace arm that prints nothing passes any diff),
# over the full corpus rows. MEASURED on the C0 PROTOTYPE hook (branch
# scratch/stc0-trace, today's walk sites: docs/dev/lanes/stc0_report.md):
# 89,135 / 38,523. C1's hook prints at a SUPERSET of those sites, so these
# are lower bounds for it; C1 re-pins at its own count. Until C1 lands, a
# --trace run against main's builds (no hook) FAILS here, as it should.
TRACE_RECORDS_FLOOR = {"c-default": 89135, "c-vm": 38523}


def trace_records(err):
    """The CANDTRACE lines of one compile's stderr, in print order, tag
    stripped. The compiler prints no seq and no pattern index: the order IS
    the sequence and the sweep attaches the index (deliverable (iii))."""
    return [ln[len(TRACE_TAG):].decode("utf-8", "replace")
            for ln in err.split(b"\n") if ln.startswith(TRACE_TAG)]


def sweep_trace(patterns, tbin_a, tbin_b, timeout, jobs, out_dir, default_hashes):
    """Compile streams 1-2 with the TRACE builds; write trace_a.tsv /
    trace_b.tsv (idx, arm, seq, record fields); count the patterns whose
    trace-build stdout differs from the same side's DEFAULT build (the
    trace must move no emitted byte). default_hashes: {stream: (ha, hb)}."""
    mirror = same_binary(tbin_a, tbin_b)
    byte_moves = {s: [0, 0] for s in ARM_STREAMS}
    paths = (os.path.join(out_dir, "trace_a.tsv"), os.path.join(out_dir, "trace_b.tsv"))

    def job(item):
        idx, (f, kind, pat) = item
        res = []
        for stream, engine in ARM_STREAMS.items():
            a = compile_stream_c(tbin_a, pat, timeout, engine=engine, want_err=True)
            b = a if mirror else compile_stream_c(tbin_b, pat, timeout, engine=engine, want_err=True)
            res.append((stream, a, b))
        return idx, res

    fa, fb = (open(p, "w") for p in paths)
    try:
        for fh in (fa, fb):
            fh.write("idx\tarm\tseq\trecord\n")
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
            for idx, res in ex.map(job, list(enumerate(patterns))):
                for stream, a, b in res:
                    for side, (ok, out, err), fh in ((0, a, fa), (1, b, fb)):
                        hd = default_hashes.get(stream)
                        if hd is not None and sha(out) != hd[side].get(idx):
                            byte_moves[stream][side] += 1
                        for seq, rec in enumerate(trace_records(err)):
                            fh.write(f"{idx}\t{stream}\t{seq}\t{rec}\n")
    finally:
        fa.close()
        fb.close()
    return paths, byte_moves, mirror


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


STREAMS_ALL = ("c-default", "c-vm", "emit-ir", "composition", "dumps", "facts")


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
                          "NOT applied under --limit; not for a real delivery run)")
    ap.add_argument("--streams", default=",".join(STREAMS_ALL))
    ap.add_argument("--extra", action="append", default=[])
    ap.add_argument("--extra-base", default="")
    ap.add_argument("--no-differ-floor", action="store_true")
    ap.add_argument("--arms", choices=("start",))
    ap.add_argument("--patterns-file", action="append", default=[])
    ap.add_argument("--no-corpus", action="store_true")
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--trace-bin")
    ap.add_argument("--trace-ref-bin")
    ap.add_argument("--trace-declared")
    ap.add_argument("--trace-unordered", action="store_true")
    ap.add_argument("--build-cflags")
    args = ap.parse_args()

    if not args.ref and not args.ref_bin:
        ap.error("one of --ref / --ref-bin is required")
    if args.bin and args.tree_rev:
        ap.error("--bin and --tree-rev are mutually exclusive")
    streams = [s for s in args.streams.split(",") if s]
    bad = [s for s in streams if s not in STREAMS_ALL]
    if bad:
        ap.error(f"--streams: unknown {bad} (known: {','.join(STREAMS_ALL)})")
    if args.arms and (args.extra or args.extra_base):
        ap.error("--arms and --extra/--extra-base are exclusive (an arm's base is the table's)")
    if args.no_corpus and not args.patterns_file:
        ap.error("--no-corpus needs at least one --patterns-file")
    if args.trace and not (args.tree_rev or args.trace_bin):
        ap.error("--trace needs --tree-rev (both sides built traced) or --trace-bin")
    base_args = shlex.split(args.extra_base)
    flag_args = [a for e in args.extra for a in shlex.split(e)]
    run_extra = base_args + flag_args   # what streams 1-4 run at, BOTH sides
    full_population = not (args.no_corpus or args.limit or args.every > 1)

    tree = os.path.abspath(args.tree)
    out_dir = os.path.abspath(args.out) if args.out else os.path.join(tree, "build-emitsweep")
    os.makedirs(out_dir, exist_ok=True)
    cc = resolve_cc(tree)
    if not args.comp_timeout:
        args.comp_timeout = max(3 * args.timeout, 90)
    if not args.comp_jobs:
        args.comp_jobs = min(args.jobs, 6)
    log(f"[emit_sweep] tree={tree} out={out_dir} cc={cc} jobs={args.jobs} "
        f"comp_timeout={args.comp_timeout} comp_jobs={args.comp_jobs} "
        f"streams={','.join(streams)} extra={run_extra} arms={args.arms} trace={args.trace}")

    overall_ok = True
    t0 = time.time()

    # -- resolve reference binary --
    if args.ref_bin:
        ref_bin = os.path.abspath(args.ref_bin)
        ref_label = f"ref-bin:{ref_bin}"
    else:
        ref_bin, _ = build_from_rev(tree, args.ref, out_dir, cc, "ref", cflags=args.build_cflags)
        ref_label = f"ref:{args.ref}"

    # -- resolve working (tree) binary + corpus source dir --
    if args.tree_rev:
        tree_bin, tree_src = build_from_rev(tree, args.tree_rev, out_dir, cc, "tree",
                                            cflags=args.build_cflags)
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

    patterns = [] if args.no_corpus else enumerate_corpus(tree_bin, corpus_dir, args.timeout)
    if args.limit:
        patterns = patterns[:args.limit]
        log(f"[emit_sweep] --limit {args.limit}: truncated corpus to {len(patterns)} rows")
    corpus_rows = len(patterns)
    for pf in args.patterns_file:
        patterns += read_patterns_file(pf)
    comp_files = [] if args.no_corpus else find_files(corpus_dir, (".rxt", ".rxtin"))
    if args.limit:
        comp_files = comp_files[:args.limit]
    log(f"[emit_sweep] corpus: {corpus_rows} pattern rows (+{len(patterns) - corpus_rows} "
        f"from patterns files), {len(comp_files)} composition files")

    def run_full_sweep(bin_a, bin_b, label):
        res = {}
        argv_streams = (
            ("c-default", "stream 1 (.c default engine)",
             lambda b, p, t: compile_stream_c(b, p, t, engine=None, extra=run_extra)),
            ("c-vm", "stream 2 (.c --engine=vm)",
             lambda b, p, t: compile_stream_c(b, p, t, engine="vm", extra=run_extra)),
            ("emit-ir-vm", "stream 3 (--emit-ir --engine=vm)",
             lambda b, p, t: compile_stream_ir(b, p, t, extra=run_extra)),
            ("facts", "stream 6 (--emit-facts=byte,utf8)",
             lambda b, p, t: compile_stream_facts(b, p, t)))
        for name, title, fn in argv_streams:
            if (name if name != "emit-ir-vm" else "emit-ir") not in streams:
                continue
            log(f"[emit_sweep] === {label}: {title} ===")
            res[name] = sweep_argv_stream(name, fn, patterns, bin_a, bin_b, args.timeout, args.jobs)
        producing = artifacts = 0
        fixtures_hit = {}
        if "composition" in streams:
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
            res["composition"], producing, artifacts, fixtures_hit = sweep_composition(
                comp_files, bin_a, bin_b, comp_out, args.comp_timeout, args.comp_jobs, run_extra)
        if "dumps" in streams:
            log(f"[emit_sweep] === {label}: stream 5 (registry dumps) ===")
            res["dumps"] = sweep_dumps(bin_a, bin_b, args.timeout)
        return res, producing, artifacts, fixtures_hit, nonlocal_flag[0]

    # -- self-check: two independent builds of the SAME ref revision --
    if not args.no_self_check:
        log("[emit_sweep] === SELF-CHECK: building a second independent copy "
            f"of {ref_label} ===")
        if args.ref_bin:
            selfcheck_bin = ref_bin
        else:
            selfcheck_bin, _ = build_from_rev(tree, args.ref, out_dir, cc, "ref2",
                                              cflags=args.build_cflags)
        res, producing, artifacts, fixtures_hit, deliver_hit = \
            run_full_sweep(ref_bin, selfcheck_bin, "selfcheck")
        print("\n===== SELF-CHECK (ref vs. independent rebuild of the same rev) =====")
        sc_ok = True
        for s in res.values():
            ok, text = report_stream(s, floor=None, identity_required=True)
            print(text)
            sc_ok = sc_ok and ok
        print("self-check reach: " + " ".join(f"{k}={v.both_ok}" for k, v in res.items())
              + f" composition producing={producing} artifacts={artifacts}")
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
    res, producing, artifacts, fixtures_hit, deliver_hit = \
        run_full_sweep(ref_bin, tree_bin, "real")

    print(f"\n===== REAL RUN: {ref_label}  vs  {tree_label} =====")
    if run_extra:
        print(f"(streams 1-4 at --extra {' '.join(run_extra)!r} on BOTH sides)")
    if same_binary(ref_bin, tree_bin):
        print("(ONE BINARY on both sides: identity is trivial; this run is a MEASUREMENT "
              "of reach and DIFFER counts, not a comparison)")
    if not full_population:
        print("(PARTIAL POPULATION (--no-corpus/--limit/--every): reach, population and "
              "DIFFER floors are NOT applied; identity, manifests in the population, "
              "asserted zeros and the null arm are)")
    identity_required_default = not args.only_emit_ir_reach
    floor = (lambda k: PINS[k] if full_population else None)
    stream_checks = {
        "c-default": (floor("reach_default_floor"), identity_required_default),
        "c-vm": (floor("reach_vm_floor"), identity_required_default),
        "emit-ir-vm": (floor("reach_ir_floor"), False),
        "composition": (None, identity_required_default),
        # The dumps stream is ALWAYS identity-required, --only-emit-ir-reach
        # included: that flag exists for a change whose `--emit-ir` LISTING is
        # expected to move, which says nothing about a registry surface.
        "dumps": (PINS["dump_surfaces_floor"], True),
        "facts": (floor("reach_facts_floor"), True),
    }
    run_ok = True
    for name, s in res.items():
        fl, ident = stream_checks[name]
        ok, text = report_stream(s, floor=fl, identity_required=ident)
        print(text)
        run_ok = run_ok and ok

    # -- population/composition floors --
    if full_population:
        if len(patterns) < PINS["argv_population_floor"]:
            run_ok = False
            print(f"ARGV POPULATION FLOOR VIOLATION: {len(patterns)} < "
                  f"{PINS['argv_population_floor']}")
        if "composition" in streams:
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

    # -- the arms: one (--extra) or the table (--arms start) --
    arms = []
    if args.arms == "start":
        arms = [(b, ARM_BASES[b], f) for b, f in arm_table()]
    elif flag_args:
        inv = {v: k for k, v in ARM_BASES.items()}
        arms = [(inv.get(tuple(base_args), " ".join(base_args)), tuple(base_args),
                 " ".join(flag_args))]
    if arms:
        pats = distinct_patterns(patterns, args.every)
        log(f"[emit_sweep] === arms: {len(arms)} arms x 2 streams over {len(pats)} "
            f"distinct patterns ===")
        ares, mirror = sweep_arms(arms, pats, ref_bin, tree_bin, args.timeout, args.jobs)
        ok_a, text_a, rows = report_arms(ares, pats, full_population, mirror,
                                         waive_unpinned=args.no_differ_floor)
        print(text_a)
        if args.no_differ_floor:
            print("  (--no-differ-floor: an unpinned arm was WAIVED, not checked)")
        with open(os.path.join(out_dir, "arms.tsv"), "w") as fh:
            fh.write(ARMS_TSV_HEADER)
            for r in rows:
                fh.write("\t".join(map(str, r)) + "\n")
        print(f"  per-arm table: {os.path.join(out_dir, 'arms.tsv')}")
        run_ok = run_ok and ok_a

    # -- the trace family --
    if args.trace:
        import trace_diff
        if args.trace_bin:
            tbin_b = os.path.abspath(args.trace_bin)
        else:
            tbin_b, _ = build_from_rev(tree, args.tree_rev, out_dir, cc, "tree-trace",
                                       cflags=TRACE_CFLAGS)
        if args.trace_ref_bin:
            tbin_a = os.path.abspath(args.trace_ref_bin)
        elif args.ref:
            tbin_a, _ = build_from_rev(tree, args.ref, out_dir, cc, "ref-trace",
                                       cflags=TRACE_CFLAGS)
        else:
            sys.exit("[emit_sweep] --trace with --ref-bin needs --trace-ref-bin")
        hashes = {s: (res[s].hash_a, res[s].hash_b) for s in ARM_STREAMS if s in res}
        tpats = [row for i, row in enumerate(patterns) if i % args.every == 0] \
            if args.every > 1 else patterns
        if args.every > 1:
            hashes = {}   # sampled indices no longer line up with the streams'
        log(f"[emit_sweep] === trace: {len(tpats)} patterns x 2 streams ===")
        paths, byte_moves, tmirror = sweep_trace(tpats, tbin_a, tbin_b, args.timeout,
                                                 args.jobs, out_dir, hashes)
        print("-- family: trace (streams 1-2, trace builds) --")
        if hashes:
            for s, (ma, mb) in byte_moves.items():
                print(f"  trace build vs default build, {s}: stdout differs on "
                      f"{ma} (ref) / {mb} (working) patterns (must be 0)")
                if ma or mb:
                    run_ok = False
        else:
            print("  trace build vs default build: NOT CHECKED (streams 1-2 not run, or --every)")
        declared = trace_diff.read_declared(args.trace_declared) if args.trace_declared else set()
        ok_t, text_t = trace_diff.compare(trace_diff.load(paths[0]), trace_diff.load(paths[1]),
                                          declared=declared,
                                          min_records=TRACE_RECORDS_FLOOR if full_population else 1,
                                          unordered=args.trace_unordered)
        print(text_t)
        print(f"  trace streams: {paths[0]} {paths[1]}")
        run_ok = run_ok and ok_t

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
