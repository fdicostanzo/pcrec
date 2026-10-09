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
  7. emit-ir-auto ([DEC-FALLBACK] B0 item 2, the B4 hard gate): `--emit-ir`
     at the DEFAULT engine, stdout + rc + stderr compared, refusals included
     (a DFA-winning pattern refuses the listing), at the base and at each of
     IR_AUTO_ARMS (`-fno-prefilter`, `-fprefilter`, `-fno-prefilter-
     collapse`). A TALLY stream: each side counts the listing's `prefilter`
     token (or `refused`) per pattern, held to per-token floors.
  8. stderr ([DEC-FALLBACK] B0 item 3): the full stderr and rc of the stream
     1 and 2 compiles, compared verbatim (notes, warnings, refusal text, the
     cap a refusal names). A TALLY stream: refusals per engine.

  VARIANTS (`--variant NAME|all|NAME=CFLAGS`, [DEC-FALLBACK] B0 item 1): both
  sides built from `git archive` with a limit variant's `-D` set (VARIANTS:
  plain, lowsize, lowdfa, lowboth, lowthr), the argv streams run once per
  base of `--bases` (default byte,utf8), and each (variant, base) cell held to
  VARIANT_PINS (reach, tag floors, thin-tag manifests). A variant's own
  plumbing is checked by VARIANT_WITNESSES (stamps only that variant's limits
  produce; plain produces none). `--trace` composes: each variant gets its own
  trace pair (`-DPCREC_CAND_TRACE` + the variant's set), compared with
  `--trace-order SLOT=ordered|set` per slot. `--emit-pins FILE` writes the
  measured cells (a measurement for a reviewed re-pin).

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
  BY THIS SCRIPT, and each pattern-arm's records compared by
  scripts/trace_diff.py (declared-multiplicity filter, records-per-arm
  floor): the SET of records gates, the ORDERED sequence is printed as a
  diagnostic (`--trace-ordered` swaps them; C1's condition 2). The trace
  build's stdout must equal the default build's.

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
  --trace-ordered        gate on the ORDERED compare instead. The default
                        gate is the SET compare (order and ask multiplicity
                        ignored; trace_diff.py --unordered): [START-TABLE]
                        C1's condition 2, from C0's experiment (a reader
                        asking once more false-alarms the ordered compare and
                        no plant escaped the set one). The compare that does
                        not gate is printed too, as a diagnostic.
  --build-cflags=FLAGS   CFLAGS for every build this run makes (default: the
                        tree's own Makefile default).
  --variant V            repeatable: a VARIANTS name, `all`, or NAME=CFLAGS
                        (ad hoc: no witnesses, no pins). Needs --ref and
                        --tree-rev. Composition is not run per variant.
  --bases LIST           the bases each variant runs at (default byte,utf8);
                        facts and dumps run at the first only.
  --no-variant-floor     a variant cell without VARIANT_PINS is reported, not
                        failed (a measurement run).
  --emit-pins FILE       write the measured VARIANT_PINS cells and per-variant
                        trace record counts as python source.
  --trace-order S=M      repeatable: trace_diff's per-slot compare mode
                        (`fallback=ordered` for refactor B).

  When the two sides are the SAME binary (realpath), every argv compile runs
  once and is mirrored: identity is trivial and said so, and the run is a
  measurement (reach, DIFFER counts, trace records) at half the cost.

EXIT STATUS: 0 if every stream is clean against its floor/identity
requirement and the DELIVER witness holds; 1 otherwise. Report is printed
to stdout; a full per-row TSV per stream is written under --out.
"""
import argparse
import collections
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
    # RE-PINNED at [START-TABLE] C0 (lane stc0, 2026-10-06, main 73f66ba9;
    # one-binary measurement run, all six streams): the corpus had grown from
    # 304 files / 3,938 rows / 3,517 reach to the values below, and every
    # floor here had fallen ~15% behind it. Same margin as the originals
    # (~1% on the argv axes, zero slack on producing files).
    # RE-PINNED at [DEC-FALLBACK] B1 (lane decfbB1, 2026-10-08, B0 tip
    # 6794d272 + B1; one-tree measurement run, all streams): the corpus had
    # grown to 373 files / 5,423 rows, and the argv/reach floors were ~15%
    # behind it again. Same margins as C0's re-pin.
    "composition_files_floor": 365,       # measured 373 (was 360 / 369 at C0)
    # corpus pattern/pattern-esc rows found by --list-source over tests/**/*.rxt.
    "argv_population_floor": 5370,        # measured 5,423 (was 4,550 / 4,606 at C0)
    # rows where BOTH sides compile successfully, per stream (--features all).
    "reach_default_floor": 4920,          # measured 4,972 (stream 1; was 4,110 / 4,159)
    "reach_vm_floor": 4920,               # measured 4,973 (stream 2; was 4,160)
    "reach_ir_floor": 4920,               # measured 4,973 (stream 3; was 4,160)
    # [START-TABLE] C0 stream 6 (--emit-facts=byte,utf8): fewer than stream 1
    # because both encodings must compile (a byte-only pattern refuses).
    "reach_facts_floor": 4880,            # measured 4,932 (was 4,119)
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
    "composition_producing_floor": 38,    # measured 38 at C0 and at B1 (was 32)
    "composition_artifacts_floor": 100,   # measured 108 at C0 and at B1 (was 88 / 96); an 8-artifact
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
# §3.4 and §3.3 item 2); -fno-length-prune from the full-corpus gate run on
# ubuntubudu 2026-10-06 (docs/design/start_table/heavy_linux_2026-10-06/
# arms.tsv; the earlier 1-in-10 sample floors were lower bounds).
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
    ("byte", "-fno-length-prune", "c-default"): (449, 112, b"(a)*b"),
    ("byte", "-fno-length-prune", "c-vm"): (678, 0, b"(a)*b"),
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
    ("utf8", "-fno-length-prune", "c-default"): (468, 118, b"(a)*b"),
    ("utf8", "-fno-length-prune", "c-vm"): (815, 0, b"(a)*b"),
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


# ---------------------------------------------------------------------------
# THE LIMIT VARIANTS ([DEC-FALLBACK] B0 item 1; docs/design/dec_fallback.md
# §4.2). A variant is a `-D` set BOTH sides are built with, so the fallback
# ladder's rows that the shipped limits never reach get a population: decfb0's
# four (docs/design/decision_families/decfb0/build_ref.py) plus `lowthr`, the
# only one where `capacity-declined` has a population (run_size_term.sh §7's
# reference compiler). Each variant runs at every base of `--bases` (default
# byte and utf8: the shipped size-rung witnesses are utf8, critB2 M2).
VARIANTS = {
    "plain": "",
    "lowsize": "-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 -DPCREC_MAX_EMIT_BYTES=60000 "
               "-DPCREC_SIZE_TERM_THRESHOLD=10000",
    "lowdfa": "-DPCREC_MAX_AUTO_DFA_ELEMS=3000",
    "lowboth": "-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 -DPCREC_MAX_EMIT_BYTES=60000 "
               "-DPCREC_SIZE_TERM_THRESHOLD=10000 -DPCREC_MAX_AUTO_DFA_ELEMS=3000",
    "lowthr": "-DPCREC_SIZE_TERM_THRESHOLD=1000",
}
# The Makefile's own `CFLAGS ?= -O2 -g`: a variant's `-D` set is APPENDED to it
# (passing the `-D` set alone as CFLAGS would also drop the optimisation level).
DEFAULT_BUILD_CFLAGS = "-O2 -g"
# A variant run's streams: composition is not run per variant (the default
# run covers it; its files carry their own options), and facts/dumps take no
# base (facts lists both encodings itself), so they run at the FIRST base only.
VARIANT_STREAMS = ("c-default", "c-vm", "emit-ir", "emit-ir-auto", "stderr", "facts", "dumps")
BASELESS_STREAMS = ("facts", "dumps")


# THE VARIANT'S OWN PLUMBING CONTROL. A variant whose `-D` set never reached
# the build IS the plain build and passes every identity check, so each
# variant names witnesses whose stamp only that variant's limits produce, and
# the plain variant must produce NONE of them (both directions in one table).
# `--list-limits` cannot serve: it prints limits.def's literal, not the
# compiled-in value (measured: a -DPCREC_MAX_AUTO_DFA_ELEMS=3000 build lists
# 30000000). Hand-written, probed at B0's base; each is a design §4.3a witness.
_W_LOWSIZE = (("--pattern", "(?:a\\K){0,10}ab"), "RX_UNROLL_K_WHY", "cap-rescue")
_W_LOWDFA = (("--pattern", "(?:a|b)*a(?:a|b){11}"), "RX_ENGINE_SEL", "collapsed-prefilter")
_W_LOWTHR = (("--engine=vm", "--pattern", "(((?:a{0,2}b)+c){0,20}d){0,20}e"),
             "RX_UNROLL_K_WHY", "capacity-declined")
VARIANT_WITNESSES = {
    "lowsize": (_W_LOWSIZE,),
    "lowdfa": (_W_LOWDFA,),
    "lowboth": (_W_LOWSIZE, _W_LOWDFA),
    "lowthr": (_W_LOWTHR,),
}


def variant_plumbing(pcrec_bin, vname, timeout):
    """Problems (empty = ok) with VARIANT_WITNESSES on one binary: a named
    variant's witnesses must stamp their value; `plain` must stamp none of any
    variant's values. An ad-hoc NAME=CFLAGS variant has no witness."""
    if vname == "plain":
        checks = [(w, False) for ws in VARIANT_WITNESSES.values() for w in ws]
    else:
        checks = [(w, True) for w in VARIANT_WITNESSES.get(vname, ())]
    probs = []
    for (argv, macro, value), want in checks:
        rc, out, _ = run([pcrec_bin, "-p", "rx", "--features", "all", "-o", "-"] + list(argv), timeout)
        m = re.search(rb'^#define ' + macro.encode() + rb' "([^"]*)"', out or b"", re.M)
        got = m.group(1).decode() if m and rc == 0 else f"<rc={rc}>"
        if (got == value) != want:
            probs.append(f"{' '.join(argv)}: {macro} reads {got!r}, "
                         + ("expected" if want else "must not read") + f" {value!r}")
    return probs


# ---------------------------------------------------------------------------
# STREAM `emit-ir-auto` ([DEC-FALLBACK] B0 item 2, critB2 B1: the B4 HARD
# GATE). `--emit-ir` at the DEFAULT engine, where the prefilter admission's
# listing rows actually fire (stream 3 forces --engine=vm, where
# `would_prefilter` is false and only `no-engine-vm`/`yes`/`no-fno-prefilter`
# can print). stdout AND rc AND stderr are compared: a DFA-winning pattern
# REFUSES the listing, and that refusal is part of the stream. Runs at the base
# and at each of IR_AUTO_ARMS. The pattern is handed as DECODED bytes, as every
# stream here is (`--pattern-esc` is ignored by `--emit-ir`, F-B5/K98).
IR_AUTO_ARMS = ("", "-fno-prefilter", "-fprefilter", "-fno-prefilter-collapse")
# The listing's `prefilter` value vocabulary (docs/spec/ir_listing.md, hand
# copied: a token outside it is counted under its own name and has no floor).
IR_TOKENS = ("yes", "yes-collapsed", "no-backreference", "no-linked-call",
             "no-nullable-collapsed", "no-nullable-exact", "no-dfa-overflow",
             "no-fno-prefilter", "no-engine-vm",
             # [DEC-VAR-ATTRIB] (abi 69): T2's `var` and `size-dropped` rows
             "no-variable", "no-size-cap")


def ir_auto_stream(arm):
    return "emit-ir-auto" + (f"[{arm}]" if arm else "")


def compile_stream_ir_auto(pcrec_bin, pattern, timeout, extra=()):
    argv = [pcrec_bin, "--features", "all"] + opt_argv(extra) + ["--emit-ir"]
    argv += _pattern_argv(pcrec_bin, pattern)
    rc, out, err = run(argv, timeout)
    blob = b"rc=%s\n%s\n#stderr\n%s" % (str(rc).encode(), out, err)
    return rc is not None, (blob if rc is not None else None), ("" if rc is not None else "TIMEOUT")


def _rc_of(blob):
    return blob[3:blob.index(b"\n")].decode() if blob and blob.startswith(b"rc=") else None


def ir_auto_tags(blob):
    """`refused`, or the summary section's `prefilter` value: the listing read
    by section and row name (docs/spec/table_contract.md), never by line
    position."""
    if blob is None:
        return ("timeout",)
    if _rc_of(blob) != "0":
        return ("refused",)
    insum = False
    for ln in blob.split(b"\n"):
        if ln.startswith(b"#section "):
            insum = ln == b"#section summary"
        elif insum and ln.startswith(b"prefilter\t"):
            return (ln.split(b"\t")[1].decode("utf-8", "replace"),)
    return ("<no-prefilter-row>",)


# ---------------------------------------------------------------------------
# STREAM `stderr` ([DEC-FALLBACK] B0 item 3, critB2 M1; the design's stream 7).
# The FULL stderr and the rc of the stream-1 and stream-2 compiles (the same
# argv, recompiled here so streams 1-2 stay as they are), compared verbatim:
# notes, warnings, the refusal text and which cap a refusal names. Before this
# stream a refusal was only COUNTED (`both_refuse`); B3 rewrites the exhaustion
# diagnostic, so a refusal's text is part of the no-mover claim.
def compile_stream_stderr(pcrec_bin, pattern, timeout, extra=()):
    parts = []
    for engine in (None, "vm"):
        argv = [pcrec_bin, "-p", "rx", "--features", "all"]
        if engine:
            argv.append(f"--engine={engine}")
        argv += opt_argv(extra) + ["-o", "-"] + _pattern_argv(pcrec_bin, pattern)
        rc, _, err = run(argv, timeout)
        parts.append(b"%s rc=%s\n%s" % ((engine or "default").encode(), str(rc).encode(), err))
    return True, b"\n#--\n".join(parts), ""


def stderr_tags(blob):
    tags = []
    for part in blob.split(b"\n#--\n"):
        head, _, err = part.partition(b"\n")
        eng, rc = head.decode().split(" rc=")
        if rc != "0":
            tags.append("refused-" + eng)
        elif err:
            tags.append("stderr-" + eng)
    return tuple(tags)


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
        self.census_hits = None  # set of keys whose REF artifact is a census hit (None: no census)
        # [DEC-FALLBACK] B0: per-side tag tallies of a TALLY stream (emit-ir-auto's
        # listing token, stderr's refusals), and the patterns carrying each tag
        # (a manifest names one). None: the stream has no tally.
        self.tags = None         # [Counter side a, Counter side b]
        self.tag_pats = None     # [{tag: set(pattern)} side a, side b]


# [MEMFN] R4h census (lane advnorm): `--census-ref-re FILE` names a file of
# regexes (one per line, re.M) read off the REFERENCE side's artifact text. A
# mover must be a census hit and a census hit must be a mover -- a text census
# that is independent of the diff (the instrument that says WHICH artifacts a
# declared text mover may touch), 0 off-diagonal in both directions.
CENSUS_RES = None


def census_hit(text):
    if CENSUS_RES is None or text is None:
        return False
    if isinstance(text, bytes):
        text = text.decode("utf-8", "replace")
    return any(r.search(text) for r in CENSUS_RES)


def same_binary(bin_a, bin_b):
    """Both sides are one file: compile once and mirror (a MEASUREMENT run;
    identity is trivial and the report says so)."""
    return os.path.realpath(bin_a) == os.path.realpath(bin_b)


def sha(b):
    return hashlib.sha256(b).hexdigest() if b is not None else None


def facts_diff_keys(c_a, c_b):
    """The `kind\tKEY` heads of the lines that differ between two facts
    listings (a line-count change is reported as the key `<LINECOUNT>`)."""
    al = c_a.decode("utf-8", "replace").splitlines()
    bl = c_b.decode("utf-8", "replace").splitlines()
    if len(al) != len(bl):
        return {"<LINECOUNT>"}
    return {"\t".join(x.split("\t")[:2]) for x, y in zip(al, bl) if x != y}


def argv_stream_task(compile_fn, item, bin_a, bin_b, mirror, timeout,
                     census_fn=None, declared_keys=None, tally_fn=None):
    """ONE pattern of an argv stream, compared INSIDE the worker so only a
    small tuple (never the artifacts) crosses back to the merge:
    (key, ok_a, ok_b, hash_a, hash_b, hunk, err_a, err_b, hit, tags_a,
    tags_b, pattern); hunk is None unless both sides compiled and their bytes
    differ; tags are tally_fn's reading of each side's content (None without
    one)."""
    f, kind, pat = item
    ok_a, c_a, e_a = compile_fn(bin_a, pat, timeout)
    if mirror:
        ok_b, c_b, e_b = ok_a, c_a, e_a
    else:
        ok_b, c_b, e_b = compile_fn(bin_b, pat, timeout)
    key = f"{f}:{kind}:{pat[:60]!r}"
    hunk = first_diff_hunk(c_a, c_b) if ok_a and ok_b and c_a != c_b else None
    if census_fn is None:
        hit = ok_a and census_hit(c_a)
    else:
        # The stream's own listing carries no loop text, so the census is read
        # off the REF side of a DIFFERENT artifact of the same pattern
        # (`census_fn`), and a mover only counts as explained when every line
        # that moved is one of the stream's DECLARED keys.
        hit = False
        if ok_a and CENSUS_RES is not None:
            # per ENCODING: a listing's `utf8` program is the --engine=vm -e utf8
            # artifact's, not the byte one's
            for enc in ("byte", "utf8"):
                if ("%s\tRX_VM_PROGRAM_BYTES\t" % enc).encode() not in c_a:
                    continue
                ok_c, c_c, _ = census_fn(bin_a, pat, timeout, enc)
                hit = hit or (ok_c and census_hit(c_c))
        if hunk is not None and declared_keys is not None:
            if not facts_diff_keys(c_a, c_b) <= declared_keys:
                hit = False
    tags_a = tags_b = None
    if tally_fn is not None:
        tags_a = tally_fn(c_a)
        tags_b = tags_a if mirror else tally_fn(c_b)
    return key, ok_a, ok_b, sha(c_a), sha(c_b), hunk, e_a, e_b, hit, tags_a, tags_b, pat


def merge_argv_stream(name, rows, mirror):
    """Fold one stream's per-pattern rows (in pattern order) into a
    StreamResult -- the same arithmetic the per-stream sweep always did."""
    res = StreamResult(name)
    res.population = len(rows)
    res.mirrored = mirror
    if CENSUS_RES is not None:
        res.census_hits = set()
    if rows and rows[0][9] is not None:
        res.tags = [collections.Counter(), collections.Counter()]
        res.tag_pats = [collections.defaultdict(set), collections.defaultdict(set)]
    for idx, (key, ok_a, ok_b, h_a, h_b, hunk, e_a, e_b, hit, tags_a, tags_b, pat) in enumerate(rows):
        if res.tags is not None:
            for side, tags in ((0, tags_a), (1, tags_b)):
                for t in tags:
                    res.tags[side][t] += 1
                    res.tag_pats[side][t].add(pat)
        if hit and ok_b:
            res.census_hits.add(key)
        # per-index output hashes: the trace family checks that the trace
        # build's stdout equals THIS (the default build's) per pattern.
        res.hash_a[idx], res.hash_b[idx] = h_a, h_b
        if ok_a and ok_b:
            res.both_ok += 1
            if hunk is not None:
                res.movers.append((key, hunk))
        elif not ok_a and not ok_b:
            res.both_refuse += 1
        else:
            res.asymmetric.append((key, ok_a, ok_b, e_a, e_b))
    return res


def composition_task(item, bin_a, bin_b, out_root, timeout, extra):
    """ONE composition file, both sides, compared inside the worker. Returns
    (f, verdict, payload): verdict "asym" (payload = the asymmetric row),
    "refuse", or "ok" (payload = (base, [(name, hunk-or-None)], deliver_seen))."""
    idx, f = item
    tag = f"f{idx}"
    rc_a, art_a, e_a = run_composition(bin_a, f, os.path.join(out_root, "a"), tag, timeout, extra)
    rc_b, art_b, e_b = run_composition(bin_b, f, os.path.join(out_root, "b"), tag, timeout, extra)
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
    ok_a = rc_a == 0
    ok_b = rc_b == 0
    if ok_a != ok_b:
        return f, "asym", (f, ok_a, ok_b, e_a, e_b)
    names_a = set(art_a.keys())
    names_b = set(art_b.keys())
    if names_a != names_b:
        return f, "asym", (f, f"artifacts={sorted(names_a)}", f"artifacts={sorted(names_b)}", "", "")
    if not names_a:
        return f, "refuse", None
    deliver = False
    arts = []
    for nm in sorted(names_a):
        content_a = art_a[nm]
        content_b = art_b[nm]
        if nm.endswith(".c") and (deliver_witness(content_a.decode("utf-8", "replace"))
                                  or deliver_witness(content_b.decode("utf-8", "replace"))):
            deliver = True
        arts.append((nm, first_diff_hunk(content_a, content_b) if content_a != content_b else None,
                     nm.endswith(".c") and census_hit(content_a)))
    return f, "ok", (os.path.basename(f), arts, deliver)


def merge_composition(files, rows):
    """Fold the per-file rows (in file order) into the composition
    StreamResult; sets the sticky deliver flag like the old per-stream sweep."""
    res = StreamResult("composition")
    res.population = len(files)
    if CENSUS_RES is not None:
        res.census_hits = set()
    producing = 0
    artifact_count = 0
    fixture_produced = {name: False for name in DELIVER_FIXTURES}
    for f, verdict, payload in rows:
        if verdict == "asym":
            res.asymmetric.append(payload)
            continue
        if verdict == "refuse":
            res.both_refuse += 1
            continue
        base, arts, deliver = payload
        producing += 1
        if base in fixture_produced:
            fixture_produced[base] = True
        if deliver:
            nonlocal_flag[0] = True
        for nm, hunk, hit in arts:
            artifact_count += 1
            if hit:
                res.census_hits.add(f"{f}::{nm}")
            if hunk is not None:
                res.movers.append((f"{f}::{nm}", hunk))
        res.both_ok += 1
    return res, producing, artifact_count, fixture_produced


def run_pooled(tasks, jobs, comp_jobs):
    """ONE pool for every stream's tasks. tasks: [(is_comp, fn)]; returns the
    results in TASK order (so the merge is deterministic whatever the finish
    order). Composition tasks (heavy, long-tailed; submitted FIRST so the tail
    overlaps the cheap argv work) are capped at `comp_jobs` concurrent -- the
    contention the cap exists for (bsweep_report.md S1.4) is unchanged -- and
    a worker with no eligible task retires, the running ones carrying on. The
    first exception, in task order, is re-raised after the pool drains."""
    import threading
    from collections import deque
    results = [None] * len(tasks)
    errors = [None] * len(tasks)
    comp = deque(i for i, (c, _) in enumerate(tasks) if c)
    rest = deque(i for i, (c, _) in enumerate(tasks) if not c)
    lock = threading.Lock()
    running_comp = [0]

    def worker():
        while True:
            with lock:
                if comp and running_comp[0] < comp_jobs:
                    i = comp.popleft()
                    running_comp[0] += 1
                elif rest:
                    i = rest.popleft()
                else:
                    return
            try:
                results[i] = tasks[i][1]()
            except BaseException as e:   # re-raised in task order below
                errors[i] = e
            if tasks[i][0]:
                with lock:
                    running_comp[0] -= 1

    threads = [threading.Thread(target=worker) for _ in range(max(1, jobs))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for e in errors:
        if e is not None:
            raise e
    return results


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
# over the full corpus rows. A --trace run against a build with no hook
# FAILS here, as it should.
TRACE_RECORDS_FLOOR = {"c-default": 334904, "c-vm": 120524}
# [DEC-FALLBACK] B1 re-pin (lane decfbB1): the plain variant's working-side
# count in the B1 gate run (the same streams, CFLAGS and byte base this
# non-variant trace run uses), C1's records plus the fallback trace's; it was
# 262,901 / 64,776, a lower bound from an older, smaller corpus.
# [START-TABLE] C1 re-pin: the C1 hook's own count over the 4,612 corpus rows
# (stc1_report.md §5; the C0 prototype's 89,135 / 38,523 were lower bounds).
# Every declared C1 site key must print at least once on the WORKING side of a
# full-population run: a site whose record stopped printing would otherwise
# hide inside the arm totals (K35). The keys are the C1 hook's site literals.
TRACE_SITES = ("pf-of", "vm-start", "scan-state", "form-fwd", "form-other",
               "search-start", "req-admit", "req-use", "reseed", "end-window",
               "attempt-cand", "attempt-bound", "vm-bound", "root-minw",
               "dfa-engine", "entry-gate", "engine-empty", "run-tests",
               "set-rest", "prefix-k", "req-site", "req-gate", "req-handoff",
               "req-from", "ofs-need")


# [DEC-FALLBACK] B1: the fallback trace's site keys (src/core/compile.c's
# FIT_TRACE sites, the gate/stwhy records, src/opt/select_engine.c's
# admit/attrib), held reached by --variant --trace on a full population.
# `fb-forcing` and `fb-nomem` are not here: no corpus compile arrives with
# those labels (dec_fallback.md §4.3a), and docs/design/dec_fallback/
# row_reach.py declares both cells zero.
FALLBACK_TRACE_SITES = ("fb-trial", "fb-sel1", "fb-size", "fb-refuse", "admit",
                        "attrib", "gate", "st-why")


def trace_records(err):
    """The CANDTRACE lines of one compile's stderr, in print order, tag
    stripped. The compiler prints no seq and no pattern index: the order IS
    the sequence and the sweep attaches the index (deliverable (iii))."""
    return [ln[len(TRACE_TAG):].decode("utf-8", "replace")
            for ln in err.split(b"\n") if ln.startswith(TRACE_TAG)]


def sweep_trace(patterns, tbin_a, tbin_b, timeout, jobs, out_dir, default_hashes, extra=(),
                tag=""):
    """Compile streams 1-2 with the TRACE builds; write trace_a.tsv /
    trace_b.tsv (idx, arm, seq, record fields); count the patterns whose
    trace-build stdout differs from the same side's DEFAULT build (the
    trace must move no emitted byte). default_hashes: {stream: (ha, hb)}."""
    mirror = same_binary(tbin_a, tbin_b)
    byte_moves = {s: [0, 0] for s in ARM_STREAMS}
    paths = (os.path.join(out_dir, f"trace{tag}_a.tsv"), os.path.join(out_dir, f"trace{tag}_b.tsv"))

    def job(item):
        idx, (f, kind, pat) = item
        res = []
        for stream, engine in ARM_STREAMS.items():
            a = compile_stream_c(tbin_a, pat, timeout, engine=engine, extra=extra, want_err=True)
            b = a if mirror else compile_stream_c(tbin_b, pat, timeout, engine=engine, extra=extra,
                                                  want_err=True)
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
    if res.census_hits is not None:
        mk = {k for k, _ in res.movers}
        off_a = sorted(mk - res.census_hits)       # moved, REF text has no census shape
        off_b = sorted(res.census_hits - mk)       # REF text has the shape, did not move
        lines.append(f"  CENSUS: movers={len(mk)} text-census-hits={len(res.census_hits)} "
                     f"off-diagonal(moved-without-shape)={len(off_a)} "
                     f"off-diagonal(shape-without-move)={len(off_b)}")
        for tag, off in (("moved without a REF census shape", off_a),
                         ("REF census shape but no move", off_b)):
            if off:
                ok = False
                lines.append(f"  CENSUS OFF-DIAGONAL, {tag} ({len(off)}), first 10:")
                lines.extend(f"    {k}" for k in off[:10])
    if floor is not None and res.both_ok < floor:
        ok = False
        lines.append(f"  REACH FLOOR VIOLATION: {res.both_ok} < floor {floor}")
    return ok, "\n".join(lines)


def stream_check(name, identity_required_default):
    """(floor, identity_required) of a stream the PINS dict does not name: the
    tally streams are identity-required like streams 1-2 (their floors are the
    per-tag ones, report_tally)."""
    return None, identity_required_default


# A tag whose measured count is below this is THIN and gets a MANIFEST: one
# named pattern that must carry it on both sides (a floor answers "did a lot
# stop", the manifest "did THIS one"; learnings §3).
THIN_TAG = 100


def report_tally(res, cell_pins, full_population):
    """The per-tag floors and manifests of one tally stream in one (variant,
    base) cell. cell_pins: VARIANT_PINS[cell] or None. Returns (ok, text)."""
    if res.tags is None:
        return True, ""
    lines = ["  tags (side a / side b): " + " ".join(
        f"{t}={res.tags[0][t]}/{res.tags[1][t]}" for t in sorted(set(res.tags[0]) | set(res.tags[1])))]
    ok = True
    if cell_pins is None:
        lines.append("  tag floors: NOT APPLIED (no VARIANT_PINS cell for this run)")
        return ok, "\n".join(lines)
    floors = cell_pins["tags"].get(res.name, {})
    if not floors:
        lines.append(f"  NO TAG FLOORS PINNED for {res.name} (K35: an unpinned tally is not a check)")
        return False, "\n".join(lines)
    for tag, fl in sorted(floors.items()):
        if full_population:
            for side in (0, 1):
                if res.tags[side][tag] < fl:
                    ok = False
                    lines.append(f"  TAG FLOOR side {'ab'[side]}: {tag} {res.tags[side][tag]} < {fl}")
    for tag, pat in sorted(cell_pins["manifest"].get(res.name, {}).items()):
        if not full_population and not any(pat in v for s in (0, 1) for v in res.tag_pats[s].values()):
            continue   # off the full corpus the manifest may be outside the sample
        for side in (0, 1):
            if pat not in res.tag_pats[side].get(tag, ()):
                ok = False
                lines.append(f"  MANIFEST side {'ab'[side]}: {pat!r} does not carry {tag}")
    if ok:
        lines.append(f"  tag floors: {len(floors)} pinned, all held"
                     + ("" if full_population else " (partial population: floors NOT applied, manifests are)"))
    return ok, "\n".join(lines)


def measured_cell(res_by_stream):
    """A VARIANT_PINS cell measured from one run's results: every reach (the
    smaller side), every tag count (the smaller side) and, for a THIN tag, the
    shortest pattern carrying it on both sides as its manifest."""
    cell = {"reach": {}, "tags": {}, "manifest": {}}
    for name, r in res_by_stream.items():
        if name in ("c-default", "c-vm", "emit-ir-vm", "facts"):
            cell["reach"][name] = r.both_ok
        if r.tags is None:
            continue
        tags = set(r.tags[0]) | set(r.tags[1])
        cell["tags"][name] = {t: min(r.tags[0][t], r.tags[1][t]) for t in sorted(tags)}
        for t in sorted(tags):
            if 0 < cell["tags"][name][t] < THIN_TAG:
                both = r.tag_pats[0][t] & r.tag_pats[1][t]
                if both:
                    cell["manifest"].setdefault(name, {})[t] = min(both, key=lambda p: (len(p), p))
    return cell


def write_pins(path, measured, trace_records):
    """The measured cells as python source for VARIANT_PINS /
    TRACE_VARIANT_RECORDS_FLOOR (a measurement, pasted in by a reviewed
    re-pin; never read back by this script)."""
    with open(path, "w") as fh:
        fh.write("VARIANT_PINS = {\n")
        for key in sorted(measured):
            fh.write(f"    {key!r}: {measured[key]!r},\n")
        fh.write("}\nTRACE_VARIANT_RECORDS_FLOOR = {\n")
        for v in sorted(trace_records):
            fh.write(f"    {v!r}: {trace_records[v]!r},\n")
        fh.write("}\n")


def run_variants(args, variants, bases, patterns, full_population, flag_args, tree, out_dir,
                 cc, run_full_sweep, trace_order, t0, plain_ref, plain_tree):
    """[DEC-FALLBACK] B0 item 1: the sweep once per (variant, base) cell, both
    sides built with the variant's `-D` set from `git archive` (the plain
    variant reuses the two default builds, whose CFLAGS are the Makefile's).
    Per cell: identity on every stream, the reach floors and the tally
    streams' tag floors/manifests from VARIANT_PINS. Per variant: the plumbing
    control, a self-check (first base) and, under --trace, the variant's own
    trace pair compared with trace_diff (records floor per variant)."""
    import trace_diff
    vstreams = [s for s in VARIANT_STREAMS if s in args.streams.split(",")]
    all_ok = True
    measured, trace_records = {}, {}
    fb_seen = set()
    for vname, vflags in variants:
        cf = (DEFAULT_BUILD_CFLAGS + " " + vflags).strip()
        if vflags.strip():
            vref, _ = build_from_rev(tree, args.ref, out_dir, cc, f"ref-{vname}", cflags=cf)
            vtree, _ = build_from_rev(tree, args.tree_rev, out_dir, cc, f"tree-{vname}", cflags=cf)
        else:
            vref, vtree = plain_ref, plain_tree
        print(f"\n===== VARIANT {vname} ({vflags or 'shipped limits'}): {args.ref} vs {args.tree_rev} =====")
        probs = [f"side {s}: {p}" for s, b in (("a", vref), ("b", vtree))
                 for p in variant_plumbing(b, vname, args.timeout)]
        for p in probs:
            print(f"  VARIANT PLUMBING: {p}")
        if probs:
            all_ok = False
            continue
        nwit = (sum(len(w) for w in VARIANT_WITNESSES.values()) if vname == "plain"
                else len(VARIANT_WITNESSES.get(vname, ())))
        print(f"  plumbing: {nwit} variant witness(es) read as this variant's limits predict, "
              f"both sides" + ("" if nwit else " (an ad-hoc variant: NO plumbing control)"))
        first_extra = list(ARM_BASES[bases[0]]) + flag_args
        if not args.no_self_check:
            vref2, _ = build_from_rev(tree, args.ref, out_dir, cc, f"ref2-{vname}", cflags=cf)
            res, *_ = run_full_sweep(vref, vref2, f"selfcheck-{vname}", run_extra=first_extra,
                                     streams=vstreams)
            sc_ok = True
            for r in res.values():
                ok, text = report_stream(r, identity_required=True)
                if not ok:
                    print(text)
                sc_ok = sc_ok and ok
            print(f"  self-check ({bases[0]}, {vref} vs an independent rebuild): "
                  f"{'PASSED' if sc_ok else 'FAILED'}")
            if not sc_ok:
                all_ok = False
                continue
        hashes = None
        for i, base in enumerate(bases):
            cell_streams = [s for s in vstreams if i == 0 or s not in BASELESS_STREAMS]
            extra = list(ARM_BASES[base]) + flag_args
            res, *_ = run_full_sweep(vref, vtree, f"{vname}-{base}", run_extra=extra,
                                     streams=cell_streams)
            if i == 0:
                hashes = {st: (res[st].hash_a, res[st].hash_b) for st in ARM_STREAMS if st in res}
            pins = None if flag_args else VARIANT_PINS.get((vname, base))
            print(f"-- cell {vname}/{base}" + (f" + {' '.join(flag_args)}" if flag_args else "")
                  + (" (no VARIANT_PINS cell)" if pins is None else "") + " --")
            if pins is None and not args.no_variant_floor:
                print("  NO VARIANT_PINS CELL: an unpinned variant cell is not a check "
                      "(--no-variant-floor waives, for a measurement)")
                all_ok = False
            for name, r in res.items():
                fl = None
                if name == "dumps":
                    fl = PINS["dump_surfaces_floor"]
                elif pins and full_population:
                    fl = pins["reach"].get(name)
                ok, text = report_stream(r, floor=fl, identity_required=True)
                print(text)
                all_ok = all_ok and ok
                if r.tags is not None:
                    ok, text = report_tally(r, pins, full_population)
                    print(text)
                    all_ok = all_ok and ok
            if not flag_args:
                measured[(vname, base)] = measured_cell(res)
        if args.trace:
            tcf = (TRACE_CFLAGS + " " + vflags).strip()
            tb_a, _ = build_from_rev(tree, args.ref, out_dir, cc, f"ref-trace-{vname}", cflags=tcf)
            tb_b, _ = build_from_rev(tree, args.tree_rev, out_dir, cc, f"tree-trace-{vname}", cflags=tcf)
            paths, byte_moves, _ = sweep_trace(patterns, tb_a, tb_b, args.timeout, args.jobs,
                                               out_dir, hashes or {}, extra=first_extra,
                                               tag=f"_{vname}")
            print(f"-- variant {vname}: trace ({bases[0]} base, {tcf}) --")
            for st, (ma, mb) in byte_moves.items():
                print(f"  trace build vs default build, {st}: stdout differs on {ma} / {mb} (must be 0)")
                all_ok = all_ok and not (ma or mb)
            ta, tb = trace_diff.load(paths[0]), trace_diff.load(paths[1])
            trace_records[vname] = {arm: min(sum(len(v) for k, v in ta.items() if k[1] == arm),
                                             sum(len(v) for k, v in tb.items() if k[1] == arm))
                                    for arm in ARM_STREAMS}
            floor = TRACE_VARIANT_RECORDS_FLOOR.get(vname) if full_population else 1
            if floor is None:
                print("  NO TRACE RECORDS FLOOR for this variant" +
                      (" (waived: --no-variant-floor)" if args.no_variant_floor else ""))
                all_ok = all_ok and args.no_variant_floor
                floor = 1
            declared = trace_diff.read_declared(args.trace_declared) if args.trace_declared else set()
            ok_t, text_t = trace_diff.compare(ta, tb, declared=declared, min_records=floor,
                                              unordered=not args.trace_ordered, order=trace_order)
            print(text_t)
            all_ok = all_ok and ok_t
            fb_seen |= {rec[trace_diff.FIELDS.index("site")] for recs in tb.values()
                        for rec in recs if len(rec) > trace_diff.FIELDS.index("site")}
    if args.trace and full_population:
        # [DEC-FALLBACK] B1: every fallback-trace site key prints on the
        # WORKING side of at least one variant (K35: a record that stopped
        # printing would otherwise hide inside the records floor), except the
        # two whose arrival no corpus compile makes (row_reach's declared
        # zeros; their witness is alloc_check W4/W5).
        missing = [k for k in FALLBACK_TRACE_SITES if k not in fb_seen]
        print(f"-- fallback-trace site keys reached (working, any variant): "
              f"{len(FALLBACK_TRACE_SITES) - len(missing)}/{len(FALLBACK_TRACE_SITES)}"
              + (f"; NOT REACHED: {', '.join(missing)}" if missing else ""))
        all_ok = all_ok and not missing
    with open(os.path.join(out_dir, "variant_tallies.tsv"), "w") as fh:
        fh.write("variant\tbase\tstream\tkey\tfloor\tmanifest\n")
        for (v, b), cell in sorted(measured.items()):
            for st, n in cell["reach"].items():
                fh.write(f"{v}\t{b}\t{st}\treach\t{n}\t\n")
            for st, tags in cell["tags"].items():
                for t, n in tags.items():
                    man = cell["manifest"].get(st, {}).get(t)
                    fh.write(f"{v}\t{b}\t{st}\t{t}\t{n}\t{encode_escape(man) if man else ''}\n")
    print(f"\nper-cell measurement: {os.path.join(out_dir, 'variant_tallies.tsv')}")
    if args.emit_pins:
        write_pins(args.emit_pins, measured, trace_records)
        print(f"measured pins written: {args.emit_pins}")
    if not full_population:
        print("(PARTIAL POPULATION: reach and tag floors NOT applied; identity, plumbing and "
              "manifests in the population are)")
    print(f"population: argv={len(patterns)}\nelapsed: {time.time() - t0:.1f}s")
    print("VARIANTS: " + ("CLEAN" if all_ok else "FAILED"))
    return 0 if all_ok else 1


# MEASURED per (variant, base) cell ([DEC-FALLBACK] B0 item 4: every floor in
# the instrument's OWN population -- corpus `pattern`/`pattern-esc` rows,
# `--features all`, 5,423 rows -- never decfb0's). One run, main ab583f6b
# against itself, both sides built separately from `git archive`, every cell
# identical (0 movers, 0 asymmetric), `--emit-pins`'s output pasted here:
#   python3 scripts/emit_sweep.py --ref HEAD --tree-rev HEAD --variant all \
#       --no-variant-floor --no-self-check --trace --trace-order fallback=ordered \
#       --emit-pins pins.py
# RE-MEASURED 2026-10-09 (lane decattr, abi 69: [DEC-VAR-ATTRIB]'s `no-variable`/
# `no-size-cap` tokens and [DEC-COLLAPSE-WASTE]'s shorter fallback sequences), the
# same command at 365caa6c against itself, every cell 0 movers / 0 asymmetric.
# RE-MEASURED again 2026-10-09 (lane decland, after the merge of main 5761cd03):
# K100's restart-restores-K turns lowered-cap refusals into compiles, so the
# lowsize/lowboth cells' `refused`/`refused-default` floors fell (lowsize byte
# 3270 -> 3255, stderr 487 -> 472) and their reach/`no-size-cap`/`yes-collapsed`
# counts rose; plain/lowdfa/lowthr unchanged. Same command at c0a0b76a against
# itself, every cell 0 movers / 0 asymmetric, manifests unchanged.
# RE-PINNED 2026-10-09 (lane rq3tri, session 102): R4e'.0b (abi 70, 82ff9432)
# grew each VM FUNC by +139..+184 B, which pushes `(x?)([a-z]+)+S\d(?i:s)qz\1`
# (tests/litscan/reqcube.rxt:480 and :492) over the LOWERED 30000-byte VM-code
# cap (30098 B), so it is refused on both sides: reach -2 on six lowsize/lowboth
# byte streams (c-default, c-vm, emit-ir-vm), never a mover. Reproduced with
# --ref 9c181041 --tree-rev 82ff9432 --variant lowsize --bases byte.
# Floors sit AT the measured value (the smaller side), DIFFER_PINS' stance: a
# B commit is a no-mover over one corpus, so a count below it is a corpus
# change (a reviewed re-pin) or a plumbing loss. `reach` is both_ok per
# stream; `tags` is the per-tag count of each TALLY stream; `manifest` names,
# for every tag under THIN_TAG, the shortest pattern carrying it on both
# sides. A tag absent from a cell had a measured count of 0 and has no floor.
VARIANT_PINS = {('lowboth', 'byte'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                        b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                     'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                     'no-size-cap': b'((a)+)+',
                                                     'no-variable': b'${v}x',
                                                     'yes-collapsed': b'a{500}'},
                                    'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'a{500}',
                                                                              'no-size-cap': b'((a)+)+',
                                                                              'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'a{500}',
                                                                     'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                     'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fprefilter]': {'yes-collapsed': b'(a+){2,3}'},
                                    'stderr': {'stderr-default': b'a{500}'}},
                       'reach': {'c-default': 4949, 'c-vm': 4943, 'emit-ir-vm': 4943, 'facts': 4819},
                       'tags': {'emit-ir-auto': {'no-backreference': 492,
                                                 'no-dfa-overflow': 3,
                                                 'no-linked-call': 122,
                                                 'no-nullable-collapsed': 1,
                                                 'no-nullable-exact': 105,
                                                 'no-size-cap': 68,
                                                 'no-variable': 45,
                                                 'refused': 3252,
                                                 'yes': 1308,
                                                 'yes-collapsed': 35},
                                'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 492,
                                                                          'no-dfa-overflow': 30,
                                                                          'no-linked-call': 122,
                                                                          'no-nullable-exact': 105,
                                                                          'no-size-cap': 80,
                                                                          'no-variable': 45,
                                                                          'refused': 3249,
                                                                          'yes': 1308},
                                'emit-ir-auto[-fno-prefilter]': {'no-backreference': 492,
                                                                 'no-dfa-overflow': 7,
                                                                 'no-fno-prefilter': 1410,
                                                                 'no-linked-call': 122,
                                                                 'no-nullable-collapsed': 1,
                                                                 'no-nullable-exact': 105,
                                                                 'no-variable': 45,
                                                                 'refused': 3249},
                                'emit-ir-auto[-fprefilter]': {'refused': 4007, 'yes': 1412, 'yes-collapsed': 12},
                                'stderr': {'refused-default': 480, 'refused-vm': 486, 'stderr-default': 94}}},
 ('lowboth', 'utf8'): {'manifest': {'emit-ir-auto': {'no-nullable-collapsed': b'[^c]{0,4}$',
                                                     'no-variable': b'${v}x',
                                                     'yes-collapsed': b'a{500}'},
                                    'emit-ir-auto[-fno-prefilter-collapse]': {'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fno-prefilter]': {'no-nullable-collapsed': b'[^c]{0,4}$',
                                                                     'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fprefilter]': {'yes-collapsed': b'a{2,4}+a'}},
                       'reach': {'c-default': 4888, 'c-vm': 4880, 'emit-ir-vm': 4880},
                       'tags': {'emit-ir-auto': {'no-backreference': 462,
                                                 'no-dfa-overflow': 116,
                                                 'no-linked-call': 102,
                                                 'no-nullable-collapsed': 3,
                                                 'no-nullable-exact': 109,
                                                 'no-size-cap': 272,
                                                 'no-variable': 38,
                                                 'refused': 3184,
                                                 'yes': 1126,
                                                 'yes-collapsed': 19},
                                'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 462,
                                                                          'no-dfa-overflow': 143,
                                                                          'no-linked-call': 102,
                                                                          'no-nullable-exact': 109,
                                                                          'no-size-cap': 282,
                                                                          'no-variable': 38,
                                                                          'refused': 3169,
                                                                          'yes': 1126},
                                'emit-ir-auto[-fno-prefilter]': {'no-backreference': 462,
                                                                 'no-dfa-overflow': 109,
                                                                 'no-fno-prefilter': 1440,
                                                                 'no-linked-call': 102,
                                                                 'no-nullable-collapsed': 3,
                                                                 'no-nullable-exact': 109,
                                                                 'no-variable': 38,
                                                                 'refused': 3168},
                                'emit-ir-auto[-fprefilter]': {'refused': 4211, 'yes': 1210, 'yes-collapsed': 10},
                                'stderr': {'refused-default': 543, 'refused-vm': 551, 'stderr-default': 445}}},
 ('lowdfa', 'byte'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                       b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                    'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                    'no-variable': b'${v}x',
                                                    'yes-collapsed': b'a{500}'},
                                   'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'a{500}',
                                                                             'no-variable': b'${v}x'},
                                   'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'a{500}',
                                                                    'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                    'no-variable': b'${v}x'},
                                   'stderr': {'stderr-default': b'a{500}'}},
                      'reach': {'c-default': 4980, 'c-vm': 4981, 'emit-ir-vm': 4981, 'facts': 4940},
                      'tags': {'emit-ir-auto': {'no-backreference': 500,
                                                'no-dfa-overflow': 8,
                                                'no-linked-call': 127,
                                                'no-nullable-collapsed': 1,
                                                'no-nullable-exact': 110,
                                                'no-variable': 45,
                                                'refused': 3223,
                                                'yes': 1391,
                                                'yes-collapsed': 26},
                               'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 500,
                                                                         'no-dfa-overflow': 35,
                                                                         'no-linked-call': 127,
                                                                         'no-nullable-exact': 110,
                                                                         'no-variable': 45,
                                                                         'refused': 3223,
                                                                         'yes': 1391},
                               'emit-ir-auto[-fno-prefilter]': {'no-backreference': 500,
                                                                'no-dfa-overflow': 12,
                                                                'no-fno-prefilter': 1413,
                                                                'no-linked-call': 127,
                                                                'no-nullable-collapsed': 1,
                                                                'no-nullable-exact': 110,
                                                                'no-variable': 45,
                                                                'refused': 3223},
                               'emit-ir-auto[-fprefilter]': {'refused': 3933, 'yes': 1498},
                               'stderr': {'refused-default': 451, 'refused-vm': 450, 'stderr-default': 34}}},
 ('lowdfa', 'utf8'): {'manifest': {'emit-ir-auto': {'no-nullable-collapsed': b'[^c]{0,4}$',
                                                    'no-variable': b'${v}x',
                                                    'yes-collapsed': b'a{500}'},
                                   'emit-ir-auto[-fno-prefilter-collapse]': {'no-variable': b'${v}x'},
                                   'emit-ir-auto[-fno-prefilter]': {'no-nullable-collapsed': b'[^c]{0,4}$',
                                                                    'no-variable': b'${v}x'},
                                   'stderr': {'stderr-vm': b'((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,6}(){2,3}){1,2})'
                                                           b'{2,3}'}},
                      'reach': {'c-default': 5009, 'c-vm': 5010, 'emit-ir-vm': 5010},
                      'tags': {'emit-ir-auto': {'no-backreference': 502,
                                                'no-dfa-overflow': 121,
                                                'no-linked-call': 127,
                                                'no-nullable-collapsed': 3,
                                                'no-nullable-exact': 115,
                                                'no-variable': 45,
                                                'refused': 3072,
                                                'yes': 1422,
                                                'yes-collapsed': 24},
                               'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 502,
                                                                         'no-dfa-overflow': 148,
                                                                         'no-linked-call': 127,
                                                                         'no-nullable-exact': 115,
                                                                         'no-variable': 45,
                                                                         'refused': 3072,
                                                                         'yes': 1422},
                               'emit-ir-auto[-fno-prefilter]': {'no-backreference': 502,
                                                                'no-dfa-overflow': 114,
                                                                'no-fno-prefilter': 1453,
                                                                'no-linked-call': 127,
                                                                'no-nullable-collapsed': 3,
                                                                'no-nullable-exact': 115,
                                                                'no-variable': 45,
                                                                'refused': 3072},
                               'emit-ir-auto[-fprefilter]': {'refused': 3900, 'yes': 1531},
                               'stderr': {'refused-default': 422,
                                          'refused-vm': 421,
                                          'stderr-default': 151,
                                          'stderr-vm': 1}}},
 ('lowsize', 'byte'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                        b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                     'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                     'no-size-cap': b'((a)+)+',
                                                     'no-variable': b'${v}x',
                                                     'yes-collapsed': b'(a+){2,3}'},
                                    'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'(?:ab){0,16000}',
                                                                              'no-size-cap': b'((a)+)+',
                                                                              'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?'
                                                                                        b'!f)(?!g)(?!h)(?!i)(?!j)(?!k)'
                                                                                        b'(?!l)(?!m)(?!n)(?!o)(?!p)(?!'
                                                                                        b'q)',
                                                                     'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                     'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fprefilter]': {'yes-collapsed': b'(a+){2,3}'},
                                    'stderr': {'stderr-default': b'((a)+)+'}},
                       'reach': {'c-default': 4957, 'c-vm': 4943, 'emit-ir-vm': 4943, 'facts': 4754},
                       'tags': {'emit-ir-auto': {'no-backreference': 492,
                                                 'no-dfa-overflow': 1,
                                                 'no-linked-call': 122,
                                                 'no-nullable-collapsed': 1,
                                                 'no-nullable-exact': 105,
                                                 'no-size-cap': 73,
                                                 'no-variable': 45,
                                                 'refused': 3255,
                                                 'yes': 1312,
                                                 'yes-collapsed': 25},
                                'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 492,
                                                                          'no-dfa-overflow': 3,
                                                                          'no-linked-call': 122,
                                                                          'no-nullable-exact': 105,
                                                                          'no-size-cap': 97,
                                                                          'no-variable': 45,
                                                                          'refused': 3255,
                                                                          'yes': 1312},
                                'emit-ir-auto[-fno-prefilter]': {'no-backreference': 492,
                                                                 'no-dfa-overflow': 1,
                                                                 'no-fno-prefilter': 1410,
                                                                 'no-linked-call': 122,
                                                                 'no-nullable-collapsed': 1,
                                                                 'no-nullable-exact': 105,
                                                                 'no-variable': 45,
                                                                 'refused': 3255},
                                'emit-ir-auto[-fprefilter]': {'refused': 3991, 'yes': 1416, 'yes-collapsed': 24},
                                'stderr': {'refused-default': 472, 'refused-vm': 486, 'stderr-default': 78}}},
 ('lowsize', 'utf8'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                        b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                     'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                     'no-variable': b'${v}x',
                                                     'yes-collapsed': b'a{2,4}+a'},
                                    'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'(?:ab){0,16000}',
                                                                              'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?'
                                                                                        b'!f)(?!g)(?!h)(?!i)(?!j)(?!k)'
                                                                                        b'(?!l)(?!m)(?!n)(?!o)(?!p)(?!'
                                                                                        b'q)',
                                                                     'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                     'no-variable': b'${v}x'},
                                    'emit-ir-auto[-fprefilter]': {'yes-collapsed': b'a{2,4}+a'}},
                       'reach': {'c-default': 4823, 'c-vm': 4880, 'emit-ir-vm': 4880},
                       'tags': {'emit-ir-auto': {'no-backreference': 462,
                                                 'no-dfa-overflow': 1,
                                                 'no-linked-call': 102,
                                                 'no-nullable-collapsed': 1,
                                                 'no-nullable-exact': 109,
                                                 'no-size-cap': 297,
                                                 'no-variable': 38,
                                                 'refused': 3281,
                                                 'yes': 1129,
                                                 'yes-collapsed': 11},
                                'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 462,
                                                                          'no-dfa-overflow': 4,
                                                                          'no-linked-call': 102,
                                                                          'no-nullable-exact': 109,
                                                                          'no-size-cap': 308,
                                                                          'no-variable': 38,
                                                                          'refused': 3279,
                                                                          'yes': 1129},
                                'emit-ir-auto[-fno-prefilter]': {'no-backreference': 462,
                                                                 'no-dfa-overflow': 1,
                                                                 'no-fno-prefilter': 1440,
                                                                 'no-linked-call': 102,
                                                                 'no-nullable-collapsed': 1,
                                                                 'no-nullable-exact': 109,
                                                                 'no-variable': 38,
                                                                 'refused': 3278},
                                'emit-ir-auto[-fprefilter]': {'refused': 4207, 'yes': 1213, 'yes-collapsed': 11},
                                'stderr': {'refused-default': 608, 'refused-vm': 551, 'stderr-default': 369}}},
 ('lowthr', 'byte'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                       b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                    'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                    'no-variable': b'${v}x',
                                                    'yes-collapsed': b'(1{0,30}?[^]abc][^abc]){28,30}0+|a'},
                                   'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'(?:ab){0,16000}',
                                                                             'no-variable': b'${v}x'},
                                   'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?'
                                                                                       b'!f)(?!g)(?!h)(?!i)(?!j)(?!k)'
                                                                                       b'(?!l)(?!m)(?!n)(?!o)(?!p)(?!'
                                                                                       b'q)',
                                                                    'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                    'no-variable': b'${v}x'},
                                   'stderr': {'stderr-default': b'((a)|ab){4000}c'}},
                      'reach': {'c-default': 4980, 'c-vm': 4981, 'emit-ir-vm': 4981, 'facts': 4940},
                      'tags': {'emit-ir-auto': {'no-backreference': 500,
                                                'no-dfa-overflow': 1,
                                                'no-linked-call': 127,
                                                'no-nullable-collapsed': 1,
                                                'no-nullable-exact': 110,
                                                'no-variable': 45,
                                                'refused': 3234,
                                                'yes': 1412,
                                                'yes-collapsed': 1},
                               'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 500,
                                                                         'no-dfa-overflow': 3,
                                                                         'no-linked-call': 127,
                                                                         'no-nullable-exact': 110,
                                                                         'no-variable': 45,
                                                                         'refused': 3234,
                                                                         'yes': 1412},
                               'emit-ir-auto[-fno-prefilter]': {'no-backreference': 500,
                                                                'no-dfa-overflow': 1,
                                                                'no-fno-prefilter': 1413,
                                                                'no-linked-call': 127,
                                                                'no-nullable-collapsed': 1,
                                                                'no-nullable-exact': 110,
                                                                'no-variable': 45,
                                                                'refused': 3234},
                               'emit-ir-auto[-fprefilter]': {'refused': 3909, 'yes': 1522},
                               'stderr': {'refused-default': 451, 'refused-vm': 450, 'stderr-default': 5}}},
 ('lowthr', 'utf8'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                       b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                    'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                    'no-size-cap': b'(\\p{Xwd})',
                                                    'no-variable': b'${v}x',
                                                    'yes-collapsed': b'(1{0,30}?[^]abc][^abc]){8,8}0+|a'},
                                   'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'(?:ab){0,16000}',
                                                                             'no-size-cap': b'(\\p{Xwd})',
                                                                             'no-variable': b'${v}x'},
                                   'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?'
                                                                                       b'!f)(?!g)(?!h)(?!i)(?!j)(?!k)'
                                                                                       b'(?!l)(?!m)(?!n)(?!o)(?!p)(?!'
                                                                                       b'q)',
                                                                    'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                    'no-variable': b'${v}x'},
                                   'stderr': {'stderr-default': b'\\P{C}',
                                              'stderr-vm': b'((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,6}(){2,3}){1,2})'
                                                           b'{2,3}'}},
                      'reach': {'c-default': 5009, 'c-vm': 5010, 'emit-ir-vm': 5010},
                      'tags': {'emit-ir-auto': {'no-backreference': 502,
                                                'no-dfa-overflow': 1,
                                                'no-linked-call': 127,
                                                'no-nullable-collapsed': 1,
                                                'no-nullable-exact': 115,
                                                'no-size-cap': 2,
                                                'no-variable': 45,
                                                'refused': 3187,
                                                'yes': 1449,
                                                'yes-collapsed': 2},
                               'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 502,
                                                                         'no-dfa-overflow': 4,
                                                                         'no-linked-call': 127,
                                                                         'no-nullable-exact': 115,
                                                                         'no-size-cap': 2,
                                                                         'no-variable': 45,
                                                                         'refused': 3187,
                                                                         'yes': 1449},
                               'emit-ir-auto[-fno-prefilter]': {'no-backreference': 502,
                                                                'no-dfa-overflow': 1,
                                                                'no-fno-prefilter': 1453,
                                                                'no-linked-call': 127,
                                                                'no-nullable-collapsed': 1,
                                                                'no-nullable-exact': 115,
                                                                'no-variable': 45,
                                                                'refused': 3187},
                               'emit-ir-auto[-fprefilter]': {'refused': 3867, 'yes': 1564},
                               'stderr': {'refused-default': 422,
                                          'refused-vm': 421,
                                          'stderr-default': 83,
                                          'stderr-vm': 1}}},
 ('plain', 'byte'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                      b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                   'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                   'no-variable': b'${v}x',
                                                   'yes-collapsed': b'(1{0,30}?[^]abc][^abc]){28,30}0+|a'},
                                  'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'(?:ab){0,16000}',
                                                                            'no-variable': b'${v}x'},
                                  'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?'
                                                                                      b'!f)(?!g)(?!h)(?!i)(?!j)(?!k)'
                                                                                      b'(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                                   'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                   'no-variable': b'${v}x'},
                                  'stderr': {'stderr-default': b'((a)|ab){4000}c'}},
                     'reach': {'c-default': 4980, 'c-vm': 4981, 'emit-ir-vm': 4981, 'facts': 4940},
                     'tags': {'emit-ir-auto': {'no-backreference': 500,
                                               'no-dfa-overflow': 1,
                                               'no-linked-call': 127,
                                               'no-nullable-collapsed': 1,
                                               'no-nullable-exact': 110,
                                               'no-variable': 45,
                                               'refused': 3234,
                                               'yes': 1412,
                                               'yes-collapsed': 1},
                              'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 500,
                                                                        'no-dfa-overflow': 3,
                                                                        'no-linked-call': 127,
                                                                        'no-nullable-exact': 110,
                                                                        'no-variable': 45,
                                                                        'refused': 3234,
                                                                        'yes': 1412},
                              'emit-ir-auto[-fno-prefilter]': {'no-backreference': 500,
                                                               'no-dfa-overflow': 1,
                                                               'no-fno-prefilter': 1413,
                                                               'no-linked-call': 127,
                                                               'no-nullable-collapsed': 1,
                                                               'no-nullable-exact': 110,
                                                               'no-variable': 45,
                                                               'refused': 3234},
                              'emit-ir-auto[-fprefilter]': {'refused': 3909, 'yes': 1522},
                              'stderr': {'refused-default': 451, 'refused-vm': 450, 'stderr-default': 5}}},
 ('plain', 'utf8'): {'manifest': {'emit-ir-auto': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!'
                                                                      b'i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                   'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                   'no-size-cap': b'(\\p{Xwd})',
                                                   'no-variable': b'${v}x',
                                                   'yes-collapsed': b'(1{0,30}?[^]abc][^abc]){8,8}0+|a'},
                                  'emit-ir-auto[-fno-prefilter-collapse]': {'no-dfa-overflow': b'(?:ab){0,16000}',
                                                                            'no-size-cap': b'(\\p{Xwd})',
                                                                            'no-variable': b'${v}x'},
                                  'emit-ir-auto[-fno-prefilter]': {'no-dfa-overflow': b'x(?!a)(?!b)(?!c)(?!d)(?!e)(?'
                                                                                      b'!f)(?!g)(?!h)(?!i)(?!j)(?!k)'
                                                                                      b'(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)',
                                                                   'no-nullable-collapsed': b'(?:ab){0,16000}',
                                                                   'no-variable': b'${v}x'},
                                  'stderr': {'stderr-default': b'\\P{C}',
                                             'stderr-vm': b'((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,6}(){2,3}){1,2})'
                                                          b'{2,3}'}},
                     'reach': {'c-default': 5009, 'c-vm': 5010, 'emit-ir-vm': 5010},
                     'tags': {'emit-ir-auto': {'no-backreference': 502,
                                               'no-dfa-overflow': 1,
                                               'no-linked-call': 127,
                                               'no-nullable-collapsed': 1,
                                               'no-nullable-exact': 115,
                                               'no-size-cap': 2,
                                               'no-variable': 45,
                                               'refused': 3187,
                                               'yes': 1449,
                                               'yes-collapsed': 2},
                              'emit-ir-auto[-fno-prefilter-collapse]': {'no-backreference': 502,
                                                                        'no-dfa-overflow': 4,
                                                                        'no-linked-call': 127,
                                                                        'no-nullable-exact': 115,
                                                                        'no-size-cap': 2,
                                                                        'no-variable': 45,
                                                                        'refused': 3187,
                                                                        'yes': 1449},
                              'emit-ir-auto[-fno-prefilter]': {'no-backreference': 502,
                                                               'no-dfa-overflow': 1,
                                                               'no-fno-prefilter': 1453,
                                                               'no-linked-call': 127,
                                                               'no-nullable-collapsed': 1,
                                                               'no-nullable-exact': 115,
                                                               'no-variable': 45,
                                                               'refused': 3187},
                              'emit-ir-auto[-fprefilter]': {'refused': 3867, 'yes': 1564},
                              'stderr': {'refused-default': 422,
                                         'refused-vm': 421,
                                         'stderr-default': 83,
                                         'stderr-vm': 1}}}}
# Records per arm of each variant's trace pair, RE-PINNED at [DEC-FALLBACK]
# B1 (lane decfbB1, 2026-10-08): the working side of the B1 gate run (B0
# 6794d272 vs B1, byte base), C1's records plus B1's `fallback`/`admit`/
# `gate`/`stwhy`/`attrib` slots (B0's C1-only values were 315,269/105,080
# for plain, ~20k/15k lower in every cell). Measured, no margin: the trace
# is deterministic and its population only grows with the corpus.
TRACE_VARIANT_RECORDS_FLOOR = {'lowboth': {'c-default': 362174, 'c-vm': 128390},
 'lowdfa': {'c-default': 334754, 'c-vm': 120691},
 'lowsize': {'c-default': 370103, 'c-vm': 128390},
 'lowthr': {'c-default': 355509, 'c-vm': 128419},
 'plain': {'c-default': 335067, 'c-vm': 120691}}


STREAMS_ALL = ("c-default", "c-vm", "emit-ir", "composition", "dumps", "facts",
               "emit-ir-auto", "stderr")


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
    ap.add_argument("--census-facts-keys", metavar="KIND:KEY[,...]",
                    help="with --census-ref-re: the facts stream's census. A facts "
                         "mover is explained iff the REF listing has an RX_VM_PROGRAM_BYTES line and the pattern's REF --engine=vm .c is "
                         "a census hit AND every moved listing line is one of these "
                         "kind:KEY heads (e.g. byte:RX_VM_PROGRAM_BYTES,"
                         "utf8:RX_VM_PROGRAM_BYTES)")
    ap.add_argument("--census-ref-re", metavar="FILE",
                    help="[MEMFN] R4h: file of regexes (one per line); streams 1-4 hold "
                         "movers == REF artifacts matching any of them, 0 off-diagonal")
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
    ap.add_argument("--trace-ordered", action="store_true")
    ap.add_argument("--build-cflags")
    ap.add_argument("--variant", action="append", default=[],
                    help="[DEC-FALLBACK] B0: NAME (a VARIANTS entry), `all`, or NAME=CFLAGS")
    ap.add_argument("--bases", default="byte,utf8")
    ap.add_argument("--no-variant-floor", action="store_true")
    ap.add_argument("--emit-pins")
    ap.add_argument("--trace-order", action="append", default=[])
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
    variants = []
    for v in args.variant:
        if v == "all":
            variants += [(k, c) for k, c in VARIANTS.items() if k not in dict(variants)]
        elif "=" in v:
            variants.append(tuple(v.split("=", 1)))
        elif v in VARIANTS:
            variants.append((v, VARIANTS[v]))
        else:
            ap.error(f"--variant {v}: not in VARIANTS ({','.join(VARIANTS)}) and not NAME=CFLAGS")
    if variants:
        if not (args.ref and args.tree_rev):
            ap.error("--variant builds BOTH sides with its -D set: it needs --ref and --tree-rev")
        if args.build_cflags or args.extra_base or args.arms or args.only_emit_ir_reach:
            ap.error("--variant: --build-cflags/--extra-base/--arms/--only-emit-ir-reach do not compose with it")
        if args.trace and args.trace_bin:
            ap.error("--variant --trace builds each variant's trace pair itself (no --trace-bin)")
    bases = [b for b in args.bases.split(",") if b]
    if any(b not in ARM_BASES for b in bases) or not bases:
        ap.error(f"--bases: each of {','.join(ARM_BASES)}")
    trace_order = {}
    for o in args.trace_order:
        slot, _, mode = o.partition("=")
        if not slot or mode not in ("ordered", "set"):
            ap.error(f"--trace-order wants SLOT=ordered|set, got {o!r}")
        trace_order[slot] = mode
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

    def run_full_sweep(bin_a, bin_b, label, run_extra=run_extra, streams=streams):
        res = {}
        argv_streams = [
            ("c-default", "stream 1 (.c default engine)",
             lambda b, p, t: compile_stream_c(b, p, t, engine=None, extra=run_extra)),
            ("c-vm", "stream 2 (.c --engine=vm)",
             lambda b, p, t: compile_stream_c(b, p, t, engine="vm", extra=run_extra)),
            ("emit-ir-vm", "stream 3 (--emit-ir --engine=vm)",
             lambda b, p, t: compile_stream_ir(b, p, t, extra=run_extra)),
            ("facts", "stream 6 (--emit-facts=byte,utf8)",
             lambda b, p, t: compile_stream_facts(b, p, t))]
        # [DEC-FALLBACK] B0 items 2-3: the tally streams (their tags carry the
        # token and refusal floors). emit-ir-auto runs at the base and per arm.
        tally = {}
        if "emit-ir-auto" in streams:
            for arm in IR_AUTO_ARMS:
                nm = ir_auto_stream(arm)
                argv_streams.append((nm, f"stream emit-ir-auto (--emit-ir, default engine) {arm or '<base>'}",
                                     lambda b, p, t, arm=arm: compile_stream_ir_auto(
                                         b, p, t, extra=list(run_extra) + shlex.split(arm))))
                tally[nm] = ir_auto_tags
        if "stderr" in streams:
            argv_streams.append(("stderr", "stream stderr (full stderr + rc of streams 1-2)",
                                 lambda b, p, t: compile_stream_stderr(b, p, t, extra=run_extra)))
            tally["stderr"] = stderr_tags
        # ONE pool across every stream (was: a pool per stream, waited out
        # before the next began, so each stream's slowest compile -- the
        # composition stream's most of all -- left the box at a fraction of
        # its threads). Results are tagged by stream and merged in stream
        # order, so the output is byte-identical to the per-stream form.
        mirror = same_binary(bin_a, bin_b)
        # [MEMFN] R4h (lane advtri): the facts stream's census. RX_VM_PROGRAM_BYTES
        # reports the VM program's emitted length (the quantity the entry-shape size
        # term compares) and is listed only for an artifact that carries a VM program,
        # so it moves exactly where the REF listing has that line AND the layout
        # census hits the --engine=vm artifact of that listing's encoding, and NO other fact may move.
        facts_census = {}
        if args.census_facts_keys:
            facts_census["facts"] = dict(
                census_fn=lambda b, p, t, enc: compile_stream_c(
                    b, p, t, engine="vm",
                    extra=list(run_extra) + (["-e", "utf8"] if enc == "utf8" else [])),
                declared_keys={"\t".join(k.split(":", 1)) for k in
                               args.census_facts_keys.split(",")})
        tasks = []
        comp_files_run = []
        comp_out = None
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
            comp_files_run = list(enumerate(comp_files))
            for item in comp_files_run:
                tasks.append((True, lambda item=item: composition_task(
                    item, bin_a, bin_b, comp_out, args.comp_timeout, run_extra)))
        spans = {}
        for name, title, fn in argv_streams:
            if (name if name != "emit-ir-vm" else "emit-ir") not in streams and name not in tally:
                continue
            log(f"[emit_sweep] === {label}: {title} ===")
            spans[name] = (len(tasks), len(patterns))
            for item in patterns:
                tasks.append((False, lambda item=item, fn=fn, name=name: argv_stream_task(
                    fn, item, bin_a, bin_b, mirror, args.timeout,
                    tally_fn=tally.get(name), **facts_census.get(name, {}))))
        done = run_pooled(tasks, args.jobs, args.comp_jobs)
        # merge in the old per-stream order: argv streams, composition, dumps
        for name, (lo, n) in spans.items():
            res[name] = merge_argv_stream(name, done[lo:lo + n], mirror)
        producing = artifacts = 0
        fixtures_hit = {}
        if "composition" in streams:
            res["composition"], producing, artifacts, fixtures_hit = merge_composition(
                [f for _, f in comp_files_run], done[:len(comp_files_run)])
        if "dumps" in streams:
            log(f"[emit_sweep] === {label}: stream 5 (registry dumps) ===")
            res["dumps"] = sweep_dumps(bin_a, bin_b, args.timeout)
        return res, producing, artifacts, fixtures_hit, nonlocal_flag[0]

    if variants:
        sys.exit(run_variants(args, variants, bases, patterns, full_population, flag_args,
                              tree, out_dir, cc, run_full_sweep, trace_order, t0,
                              ref_bin, tree_bin))

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
    if args.census_ref_re:
        global CENSUS_RES
        with open(args.census_ref_re) as fh:
            CENSUS_RES = [re.compile(l.rstrip("\n"), re.M) for l in fh
                          if l.strip() and not l.startswith("#")]
        log(f"[emit_sweep] census: {len(CENSUS_RES)} REF-side regexes from {args.census_ref_re}")
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
    # the tally streams' floors: the plain variant's cell at this run's base,
    # when the run's options ARE a base (no --extra flag on top)
    inv = {tuple(v): k for k, v in ARM_BASES.items()}
    base_name = inv.get(tuple(run_extra))
    cell = VARIANT_PINS.get(("plain", base_name)) if base_name else None
    for name, s in res.items():
        fl, ident = stream_checks.get(name) or stream_check(name, identity_required_default)
        if cell and name in cell["reach"] and name not in stream_checks:
            fl = cell["reach"][name] if full_population else None
        ok, text = report_stream(s, floor=fl, identity_required=ident)
        print(text)
        run_ok = run_ok and ok
        if s.tags is not None:
            ok, text = report_tally(s, cell, full_population)
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
                                                 args.jobs, out_dir, hashes, extra=run_extra)
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
        ta, tb = trace_diff.load(paths[0]), trace_diff.load(paths[1])
        floor = TRACE_RECORDS_FLOOR if full_population else 1
        ok_t, text_t = trace_diff.compare(ta, tb, declared=declared, min_records=floor,
                                          unordered=not args.trace_ordered, order=trace_order)
        print(f"  GATE ({'ordered' if args.trace_ordered else 'SET'} compare):")
        print(text_t)
        ok_d, text_d = trace_diff.compare(ta, tb, declared=declared, min_records=floor,
                                          unordered=args.trace_ordered)
        print(f"  DIAGNOSTIC, not gating ({'SET' if args.trace_ordered else 'ordered'} "
              f"compare): {'clean' if ok_d else 'DIFFERS'}")
        if not ok_d:
            print(text_d)
        if full_population:
            seen = {rec[trace_diff.FIELDS.index("site")] for recs in tb.values()
                    for rec in recs if len(rec) > trace_diff.FIELDS.index("site")}
            missing = [k for k in TRACE_SITES if k not in seen]
            print(f"  declared site keys reached (working): {len(TRACE_SITES) - len(missing)}"
                  f"/{len(TRACE_SITES)}" + (f"; NOT REACHED: {', '.join(missing)}" if missing else ""))
            if missing:
                run_ok = False
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
