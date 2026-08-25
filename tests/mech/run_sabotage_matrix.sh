#!/usr/bin/env bash
# tests/mech/run_sabotage_matrix.sh — GENERATE the sabotage detection tables
# instead of hand-writing them ([MECH-1], subsumes [MECH-2]).
#
# WHY THIS EXISTS. Every "disabling X fails N cases" figure that used to live
# by hand in tests/*/CLAUDE.md goes stale silently, and every attempt to
# maintain such a figure by hand in this project has failed at least once —
# including twice in the same review (see tests/reject/CLAUDE.md). One prior
# figure was contaminated because a hand-rolled copy+sed+`git checkout` loop
# reverted a sabotage with `|| true` inside a tarball copy that is not a git
# repo, so a second sabotage landed on top of the first without anyone
# noticing ([MECH-2]'s lesson). This script owns the sabotage edits, applies
# each to a FRESH tree copied straight from `git archive HEAD` (one tree per
# sabotage, never reused, never reverted), VERIFIES the edit actually landed
# before trusting the tree, builds it, runs the suites the sabotage's own
# documentation says are relevant, and prints a diffable matrix. Docs should
# cite this script's OUTPUT, not a copied number — re-running it is how drift
# gets caught.
#
# Every sabotage is a small file under tests/mech/sabotages/S<NN>_*.sh that
# sets SAB_ID, SAB_FILE, SAB_SUITES, SAB_DESC, SAB_BEFORE, SAB_AFTER (and
# SAB_COUNT, default 1, and SAB_HARNESS_TARGET for corpus-suite sabotages).
# tests/mech/lib/replace.py is the ONLY thing that edits a sabotaged file: it
# refuses to run unless the BEFORE text appears in the target file EXACTLY
# SAB_COUNT times, and refuses to trust the result unless AFTER text is found
# in it afterward. That is the MECH-2 lesson applied per-file rather than
# trusted to a revert.
#
# Usage:
#   bash tests/mech/run_sabotage_matrix.sh              # run every sabotage
#   bash tests/mech/run_sabotage_matrix.sh S13           # run just S13 (id
#                                                         # prefix match)
#   bash tests/mech/run_sabotage_matrix.sh --help        # the field list
#   KEEP=1 bash tests/mech/run_sabotage_matrix.sh        # keep scratch trees
#
# [MECH-REACH, 2026-08-25] A ROW WHOSE WITNESS IS A CONSTRUCT DECLARES ITS
# REACH. Three optional fields, and the verdict they can produce.
#
#   SAB_REACH         a command, run on the CLEAN tree BEFORE the sabotage is
#                     applied, whose stdout+stderr must contain the literal
#                     SAB_REACH_EXPECT. `$PCREC` is the clean tree's binary,
#                     `$TREE` its root, `$REACH_TMP` a scratch dir which is
#                     also the cwd (so a probe that writes an output file
#                     cannot write into the shared clean tree).
#   SAB_REACH_EXPECT  ONE REQUIRED LITERAL SUBSTRING PER LINE, all of which
#                     must appear. Typically the EXACT diagnostic each witness
#                     produces AT THE SABOTAGED SITE -- that is what makes the
#                     check about reach rather than about the construct being
#                     refused somehow, somewhere. Several lines because a
#                     row's detector is usually several witnesses at one site,
#                     and asserting one of them leaves the rest free to expire.
#   SAB_REACH_POP     zero or more `FILE|EREGEX|MIN` lines: the file must hold
#                     at least MIN lines matching EREGEX at HEAD. The count is
#                     PRINTED whether it passes or fails. The regex is
#                     everything between the FIRST and the LAST `|`, so an
#                     ERE alternation inside it needs no escaping.
#   SAB_REQUIRE       space-separated instrument requirements; the vocabulary
#                     is CLOSED and today holds exactly `asan`.
#
# A row failing SAB_REACH/SAB_REACH_POP is **UNREACHED**: a THIRD verdict
# beside DETECTED/UNDETECTED/ANOMALY, counted in the trailer, RED in the
# headline, and its sabotaged tree is never built. A row may declare
# `SAB_EXPECT=UNREACHED` with a mandatory `SAB_EXPECT_REASON`, and the
# reverse direction is checked too (`NOW REACHED`), on the same argument
# `SAB_EXPECT`'s `NOW DETECTED` rests on.
#
# A row declaring SAB_REQUIRE the run cannot satisfy is **ANOMALY**, never
# UNDETECTED (Frank's ruling 2026-08-25): an absent instrument is the absence
# of a measurement, and reporting it as "the guards missed it" is a claim
# about the CODE and a false one.
#
# WHY (docs/dev/plan.md [MECH-REACH]; D69 addendum). S70's four escape
# witnesses were retired ONE PER WAVE as module `assertions` implemented the
# constructs they probed, and after [M6.5.2] retired the last one not a single
# row in the tree still reached `UNBUILT(at, "\%c", c)` -- the only text S70
# deletes. The row went on scoring for two milestones and certified nothing;
# a full 180-row matrix eventually read UNDETECTED. The "expired claim"
# doctrine watches only UNDETECTED->DETECTED, so the DETECTED->certifies-
# nothing direction had no checker at all. S155 is the same shape through a
# different door: a witness FILE whose relevant population went to zero.
#
# Env:
#   CC              C compiler for the sabotaged trees' own `make all`
#                   (default: gcc)
#   MECH_SCRATCH    scratch root for tree copies (default: a mktemp dir under
#                   $TMPDIR, or /tmp)
#   KEEP=1          do not delete scratch trees on exit (prints their paths)
#   JOBS            parallel make jobs per tree build (default: nproc,
#                   divided by PROCS when PROCS > 1 so concurrent tree builds
#                   do not oversubscribe the box)
#   PROCS           run N SABOTAGES concurrently (default 1 — serial,
#                   unchanged). Each run_one already works in its own
#                   $MECH_SCRATCH/$SAB_ID tree; in parallel mode each writes
#                   its matrix row to its own file and the rows are merged in
#                   sabotages/ listing order, so the matrix stays diffable.
#                   In BOTH modes the row count is now guarded against the
#                   number of sabotage definitions requested: a run that
#                   produces no row (e.g. a definition failing validation) is
#                   a loud FATAL, not a silently smaller denominator.
#                   [TT-8 FIX] PROCS ALSO DERIVES INNER_PROCS, a per-row
#                   shard-width budget for the two suite arms (`reject`,
#                   `harness`) that read PROCS from their OWN environment to
#                   pick their internal worker count (tests/reject/
#                   run_reject_tests.sh's REJECT_SHARD dispatch,
#                   tests/harness/run.sh's per-file dispatch). Computed the
#                   same way JOBS already is (nproc/PROCS, min 1) and passed
#                   EXPLICITLY on each inner invocation's command line —
#                   never left to the environment. Before this fix, PROCS
#                   (an env var, once set by the caller, keeps bash's export
#                   attribute through this script's own `PROCS="${PROCS:-1}"`
#                   reassignment) reached those two scripts UNDIVIDED: at
#                   `PROCS=4` (this repo's `make mech` default, Makefile's
#                   `PROCS=${PROCS:-$(nproc)}`), up to 4 concurrently-running
#                   ROWS each additionally sharded 4-way internally the
#                   moment they hit `reject` or `harness` — up to 16-way
#                   fan-out on top of the row-level concurrency the box was
#                   actually sized for. Measured directly (ps-sampled during
#                   a single-row `PROCS=4` run of S15: `run_reject_tests.sh`
#                   spawned 4 `REJECT_SHARD_TOTAL=4` workers from a run
#                   requesting exactly ONE sabotage — the leak does not need
#                   PROCS>1 at the ROW scheduler to fire, since a lone row
#                   still inherits the unwidened PROCS from its own
#                   environment). docs/dev/chain_profile.md "(b) mech
#                   per-row scoping" named this risk from reading the
#                   dispatch code; this is the confirming measurement and
#                   fix. At outer PROCS=1 (a lone row, whether from the
#                   default or an explicit `PROCS=1`) INNER_PROCS is
#                   `ncpu/1 = ncpu`, same precedent as JOBS already sets for
#                   the build step at PROCS=1 — the one running row is
#                   entitled to the whole box for its own internal work.
#                   That is a REAL change from pre-fix PROCS=1 (which left
#                   the inner suites serial, since nothing was in the
#                   environment to leak): validated to produce the SAME
#                   fail/pass figures per row as the old serial path, which
#                   is reject's/harness's own established contract for their
#                   PROCS mechanisms ("Summary line format is identical in
#                   both modes") — see docs/testing.md and tests/mech/
#                   tt8_mech.md for the measurement.
#
# SUITE VOCABULARY (the words that may appear in a sabotage's SAB_SUITES):
#   codegen  trie  reject  harness   — the original four
#   registry  pc3  cli                — added 2026-08-12 (MOD-0.8c slice 1)
#   vmidentity  vm                     — added 2026-08-15 ([M4.5b])
#   endvaridentity  assertions         — added 2026-08-19 ([M6.2] wave A)
#   wordctxidentity                    — added 2026-08-19 ([M6.2] wave B)
#   mlinectxidentity  mlinediff       — added 2026-08-19 ([M6.2] wave C)
#   gstartidentity  gstartdiff        — added 2026-08-19 ([M6.2] wave D)
#   kresetdiff                         — added 2026-08-19 ([M6.2] wave E)
#   irlisting                          — added 2026-08-15 ([M4.5c])
#   gentimeout                         — added 2026-08-15 ([M4.5c fix], D45)
#   possdiff                           — added 2026-08-16 ([ENG-BREP])
#   rungdiff                           — added 2026-08-16 ([ENG-BREP] rung-select)
#   counterkdiff                       — added 2026-08-17 ([ENG-BREP] counter-K)
#   mrldiff  mrl                       — added 2026-08-17 ([M4.6d] MRL pruning)
#   prefilter                          — added 2026-08-17 ([M4.6f] D46 prefilter close-out)
#   altdiff  altcls                    — added 2026-08-17 ([OPT-ALTCLS] alternation->class normalization)
#   atomicdiff  atomicidentity         — added 2026-08-22 ([M6.4.2] module atomic-groups)
#   brefdiff  dupnamesdiff  brefidentity — added 2026-08-22 ([M6.5.2] module backrefs)
#   recursion — added 2026-08-24 ([DD-14] wave B+C); like `lookaround` below
#     it is wired at the wave that builds it rather than at the module's
#     close, because two of that wave's rows are unscoreable without it: S158
#     lives on the `--no-captures` axis, for which NO `.rxt` directive exists
#     anywhere in this tree, and S154's halved trail charge changes no answer
#     until a capacity is crossed, which a fixed-length corpus cell cannot
#     reach on purpose.
#   framebuffer  stackdepth        — added 2026-08-25 ([DD-14.FB], D71 item 2);
#     registered BEFORE the six rows that need them, per the R31 C11 lesson two
#     paragraphs down. `framebuffer` runs tests/recursion/run_frame_buffer.sh
#     (the NULL-equivalence spread and the mmap'd reservation) and `stackdepth`
#     runs tests/thread/run_stackdepth_tests.sh (the 128 KB thread). Neither is
#     foldable into `harness`, and the reason is the one `vmidentity` gives for
#     itself: what they guard — that a CALLER-SUPPLIED capacity is the one the
#     matcher uses, and that the working storage is off the entry's stack frame
#     — is orthogonal to every answer-checking cell in the corpus, and a
#     sabotage of one must not be reported as coverage by the other. Note that
#     `stackdepth`'s script prints a KNOWN: line on a green run (K33, pinned by
#     D73) and the scrape below reads only its `checks passed:`/`checks failed:`
#     totals, which exclude it — so a pinned row can never be mistaken for
#     detection.
#     **`framebuffer` IS RUN WITH `REQUIRE_ASAN=1`** ([srMech 2026-08-25],
#     Frank's ruling on S155). Its SS2 is the only instrument in this tree that
#     reads an out-of-bounds WRITE rather than an ANSWER, and S155 is a row
#     that changes a write and no answer at all. On a box where the overrun
#     lands in slack the allocator owns, SS2's two `one-short` arms read
#     1/-3/-3 and PASS -- and S155 would score `UNDETECTED`, which is a claim
#     about the CODE and a false one. The flag makes the script exit 3 on a
#     failed preflight, this
#     arm records `framebuf:UNMEASURED-no-asan`, and the verdict block turns
#     that into an ANOMALY. This is SKIP-IS-NOT-A-PASS applied to an
#     INSTRUMENT instead of an ORACLE -- the same rule `pc3` has had since
#     MOD-0.8c: a net that was not in the water caught nothing for a reason
#     that is not about the fish. MEASURED, because the first version of this
#     paragraph asserted the opposite and was wrong: on THIS box a sabotaged
#     S155 build fails SS2 with OR without the sanitizer (the overrun corrupts
#     the heap and glibc aborts, exit 134). Detection-by-abort is a property of
#     the ALLOCATOR, not of the test, so the flag stays as the guard for a box
#     where the write lands in slack and nothing notices.
#   lookaround — added 2026-08-23 ([M6.6.2] wave B+C, R33 C2-7); the design put
#     it at wave F, and two of wave B+C's own rows (S131's atomicity flag and
#     S122's cut) cannot be scored without its DISAGREEMENT assertion
#   laexpand   — added 2026-08-24 ([M6.6.2] wave E2, R33 C2-7 / design §11);
#     the SUBSTITUTION DRIVER. It is a different KIND of net from `lookaround`
#     above and the difference decides which rows it can score: `lookaround`
#     runs the module's OWN corpus, ~175 hand-shaped blocks; `laexpand` runs
#     8,260 libpcre2-verified cells belonging to a module that already ships,
#     re-expressed as lookarounds — DEPTH on one body shape (a class or a
#     literal) where the other is BREADTH. It is also the SECOND arm here that
#     can decline for want of an oracle, which is why the verdict block below
#     no longer names `pc3` as the only one
#
# THE THREE NEWEST WORDS WERE REGISTERED FIRST, DELIBERATELY, which is the
# lesson R31 C11 left one module earlier: this vocabulary is CLOSED, so a
# sabotage naming a word that does not exist yet is scored UNKNOWN-SUITE and
# cannot be scored AT ALL. Fifteen of [M6.5.2]'s NINETEEN rows (S102-S120)
# depend on `brefdiff` or `dupnamesdiff`, so the registration precedes the
# measurement rather than following it. `brefidentity` is REGISTERED AND
# RESERVED with ZERO rows as of the merge (2026-08-22): the one-shot identity
# gate is not a per-sabotage suite today; the lane's own candidate for it is
# S103 (publish-at-open perturbs A_CAP emission, which backref-FREE patterns
# share) — on the [M6.5] close's residual list, not wired by a merge-time guess.
#
# THE TWO NEWEST WORDS WERE A BLOCKER, NOT A DETAIL (R31 C11). This vocabulary
# is CLOSED — the `*)` arm below scores an unrecognised word as UNKNOWN-SUITE —
# so four of [M6.4.2]'s thirteen rows (S91, S92, S96, S97) could not have been
# SCORED AT ALL until `atomicdiff` existed, and the design's slice ordering
# says the registration must PRECEDE the sabotage measurement rather than
# follow it.
#
# COST, measured before the three new arms were wired rather than asserted
# after (docs/dev/plan_completed.md's [MOD-0.8c] row forbids claiming a cost): one scratch
# archive tree at 11352be on a 12-core box, `git archive HEAD` 0.04s + `make
# all -j12` 0.75s, then per suite, build AND run —
#   registry  0.60s  (0.38 build + 0.14 run + 0.08 compliance_section.py x2)
#   pc3       4.36s  (1.05 build + 3.31 run)
#   cli       5.46s
#   reject   54.75s  <- the arm S15-S19 already paid, for scale
# So all three new arms together cost about a fifth of the one arm those rows
# already ran. PC-4 (run_pc4.sh, 2.50s) is deliberately NOT an arm, for the
# reason `make bench` is not one: no sabotage's only signal is a semantic
# differential today. Add it the day one is, with the sabotage that needs it.
#
# What this does NOT do: it does not run `make` in the real repository (every
# build happens inside a scratch copy), it does not edit any file outside
# tests/mech/ or the scratch trees, and it does not commit anything.
#
# Completion: a successful run ends with a grep-able trailer line,
# `== mech run COMPLETE: ...` (row count, undetected/anomaly counts, SHA).
# Poll a run's log for that trailer (or FATAL) to know whether it finished;
# never poll with `pgrep -f` — see the comment at the trailer for why that
# check lies.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
PROCS="${PROCS:-1}"
case "$PROCS" in (''|*[!0-9]*) echo "FATAL: PROCS must be a positive integer, got '$PROCS'" >&2; exit 2;; esac
[ "$PROCS" -ge 1 ] || { echo "FATAL: PROCS must be >= 1, got '$PROCS'" >&2; exit 2; }
ncpu="$(nproc 2>/dev/null || echo 2)"
if [ -z "${JOBS:-}" ]; then
    JOBS=$(( ncpu / PROCS )); [ "$JOBS" -ge 1 ] || JOBS=1
fi
# [TT-8 FIX] the per-row budget for the two suite arms that read PROCS from
# THEIR OWN environment to pick an internal worker count (`reject`,
# `harness` — see the header comment above). Computed exactly like JOBS,
# and always passed EXPLICITLY on those two arms' command lines below —
# never left for the environment to supply, which is what let the outer
# row-concurrency PROCS leak into inner suite sharding undivided (measured:
# a single-row `PROCS=4` run spawned 4 REJECT_SHARD workers instead of the
# whole-box share a lone row should have gotten).
INNER_PROCS=$(( ncpu / PROCS )); [ "$INNER_PROCS" -ge 1 ] || INNER_PROCS=1
ONLY="${1:-}"

# `--help` prints the ROW FIELD LIST rather than only the invocation forms,
# because the thing a reader opens this script for is almost always "what may
# a sabotage definition set". [MECH-REACH] added three fields and a verdict,
# and a mechanism nobody can find is a mechanism nobody uses.
case "$ONLY" in
-h|--help|help)
    cat <<'USAGE'
usage: bash tests/mech/run_sabotage_matrix.sh [S<id>]

  no argument   run every sabotage under tests/mech/sabotages/
  S<id>         run just that row (matched at the id boundary: S10 selects
                S10_*.sh and never S100_*.sh)

env: CC, KEEP=1 (keep scratch trees + logs), MECH_SCRATCH, JOBS, PROCS

A sabotage definition (tests/mech/sabotages/S<NN>_*.sh) sets:

  REQUIRED
    SAB_ID SAB_FILE SAB_SUITES SAB_DESC SAB_BEFORE SAB_AFTER

  OPTIONAL
    SAB_COUNT            occurrences SAB_BEFORE must have (default 1)
    SAB_FILE2 SAB_BEFORE2 SAB_AFTER2 SAB_COUNT2
                         a second coordinated site (a one-hunk mutation
                         cannot falsify a defence-in-depth pair)
    SAB_HARNESS_TARGET   scope the `harness` arm to one .rxt file or dir
    SAB_DOC_FIGURE       the row's own record of what it measured
    SAB_EXPECT           DETECTED (default) | UNDETECTED | UNREACHED --
                         checked in BOTH directions, a mismatch exits 1
    SAB_EXPECT_REASON    REQUIRED when SAB_EXPECT=UNREACHED

  [MECH-REACH] THE WITNESS'S REACH -- a row whose detector is a construct
  declares that the construct still reaches the sabotaged site AT HEAD:
    SAB_REACH            a command run on the CLEAN tree BEFORE the sabotage.
                         $PCREC = clean binary, $TREE = clean root,
                         $REACH_TMP = its cwd and scratch dir.
    SAB_REACH_EXPECT     one required literal substring PER LINE; all must
                         appear in the probe's output. Normally the EXACT
                         diagnostic each witness produces at the sabotaged
                         site. REQUIRED with SAB_REACH.
    SAB_REACH_POP        `FILE|EREGEX|MIN` lines (one per line): FILE must
                         hold >= MIN lines matching EREGEX. The count is
                         printed on pass and on fail. The regex is everything
                         between the first and last `|`, so an ERE
                         alternation inside it needs no escaping.
    SAB_REQUIRE          instrument requirements, closed vocabulary: `asan`.
                         Unsatisfiable => ANOMALY, never UNDETECTED.

  Failing a reach check is the verdict UNREACHED: the row does NOT build or
  run its sabotaged tree, the headline counts it, and it is RED unless the
  row declares SAB_EXPECT=UNREACHED with a reason.
USAGE
    exit 0
    ;;
esac

MADE_SCRATCH=0
if [ -z "${MECH_SCRATCH:-}" ]; then
    MECH_SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-mech-sabotage.XXXXXX")"
    MADE_SCRATCH=1
fi
mkdir -p "$MECH_SCRATCH"

# ---- identify the tree we are about to measure -----------------------

if ! SHA="$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null)"; then
    echo "FATAL: $ROOT_DIR is not a git repository (git archive HEAD needs one)" >&2
    exit 2
fi
DIRTY_NOTE=""
if ! git -C "$ROOT_DIR" diff --quiet -- 2>/dev/null || \
   ! git -C "$ROOT_DIR" diff --cached --quiet -- 2>/dev/null; then
    DIRTY_NOTE=" (working tree has UNCOMMITTED changes not reflected below — this matrix measures committed HEAD only, per MECH-2: sabotage trees are 'git archive HEAD', never a copy of a dirty working tree)"
fi

echo "== pcrec sabotage detection matrix (MECH-1) =="
echo "tree SHA measured: $SHA$DIRTY_NOTE"
echo "scratch root: $MECH_SCRATCH"
echo

# ---- collect the sabotages to run -------------------------------------

# THE SELECTOR MATCHES AT THE ID BOUNDARY, not by bare prefix, and [M6.4.2] is
# why. The old rule was `[[ "$base" != "$ONLY"* ]]` — a plain prefix match on
# the basename — which is exactly the hazard R31 C4 named when it caught a
# proposed `S87` colliding with the shipped `S87_kreset_trail_uncharged.sh`:
# "the driver's ID-prefix match would have selected two `S87-` rows".
#
# [M6.4.2] took the numbering past two digits and made the same hazard REAL for
# the first time: with `S100_lift_accepts_nullable.sh` on disk,
# `run_sabotage_matrix.sh S10` selected BOTH it and
# `S10_casefold_one_direction.sh` — two unrelated rows, one intended, and a
# figure attributed to whichever finished last. Measured on this tree before
# the fix.
#
# A basename is `S<id>_<name>.sh`, so the boundary is the underscore. `S10` now
# selects `S10_*` and nothing else; `S1` selects nothing, which is right — it
# is not an id. A prefix selecting a RANGE was never a supported thing to want.
sab_files=()
for f in "$SCRIPT_DIR"/sabotages/S*.sh; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    if [ -n "$ONLY" ] && [[ "$base" != "$ONLY"_* && "$base" != "$ONLY" ]]; then
        continue
    fi
    sab_files+=("$f")
done

if [ "${#sab_files[@]}" -eq 0 ]; then
    echo "FATAL: no sabotage definitions matched '${ONLY:-*}' under $SCRIPT_DIR/sabotages/" >&2
    exit 2
fi

# ---- [MECH-REACH] the CLEAN REFERENCE TREE, built at most once per run ----
#
# The reach check must ask its question of the tree WITHOUT the sabotage, and
# it must ask it of the SAME tree the rows measure -- committed HEAD via
# `git archive`, never the working tree (the [MECH-2] rule, and the reason a
# dirty working tree gets the banner above rather than a measurement).
#
# ONE tree for the whole run, extracted and built before any row forks, then
# read-only for every row including in PROCS>1 mode. Rows never write into it:
# a witness probe runs with its cwd in its OWN scratch dir and reaches the tree
# through `$TREE`/`$PCREC`, so a probe that emits an output file cannot touch
# it. Cost, measured by this file's own header on a 12-core box: `git archive`
# 0.04s + `make all -j12` 0.75s, i.e. one build against a matrix that measures
# in the tens of minutes.
#
# NOTE THE ONE ASYMMETRY WITH THE ROWS, deliberately: run_one re-reads `git
# archive HEAD` per row (see the header's "A SWEEP OVER N COMMITS MEASURES N
# TREES"), while this is read ONCE at the start. Under the standing rule for
# this script -- commit before you start, commit nothing during the run --
# they are the same tree; under a violation of it the reach check reports the
# tree the run BEGAN on, which is the honest half of a run that is already
# unsound.
#
# LAZY: built only when some SELECTED row actually declares a reach field, so
# a run of rows that declare none is byte-for-byte the run it was before this
# mechanism existed.
CLEAN_TREE=""
needs_clean=0
for f in "${sab_files[@]}"; do
    if ( SAB_REACH=""; SAB_REACH_POP=""
         # shellcheck disable=SC1090
         source "$f" >/dev/null 2>&1
         [ -n "${SAB_REACH}${SAB_REACH_POP//[[:space:]]/}" ] ); then
        needs_clean=1
        break
    fi
done
if [ "$needs_clean" -eq 1 ]; then
    CLEAN_TREE="$MECH_SCRATCH/_clean/tree"
    rm -rf "$MECH_SCRATCH/_clean"
    mkdir -p "$CLEAN_TREE"
    if ! git -C "$ROOT_DIR" archive HEAD | tar -x -C "$CLEAN_TREE" \
            2>"$MECH_SCRATCH/_clean/archive.log"; then
        echo "FATAL: could not extract the clean reference tree for the reach checks (see $MECH_SCRATCH/_clean/archive.log)" >&2
        exit 2
    fi
    # A CLEAN TREE THAT DOES NOT BUILD IS A FATAL FOR THE WHOLE RUN, not a
    # per-row anomaly: every verdict below is stated relative to it, and if
    # HEAD does not build there is nothing for any row to mean.
    if ! make -C "$CLEAN_TREE" -j"$ncpu" all CC="$CC" \
            > "$MECH_SCRATCH/_clean/build.log" 2>&1; then
        echo "FATAL: the CLEAN reference tree does not build at $SHA (see $MECH_SCRATCH/_clean/build.log)" >&2
        exit 2
    fi
    echo "reach reference: clean tree built at $SHA ($CLEAN_TREE)"
    echo
fi

# ---- run one sabotage: fresh tree, verify-apply, build, run suites ----

run_one() {
    local sab_path="$1"
    (
        # subshell: SAB_* variables from this sabotage never leak to the next
        SAB_COUNT=1
        SAB_HARNESS_TARGET=""
        SAB_DOC_FIGURE=""
        # [DD-14 wave B+C] THE EXPECTATION, CHECKED. Absent means DETECTED --
        # the overwhelmingly common case, and the one a new row should have to
        # do nothing to get. A row that sets UNDETECTED is claiming its
        # sabotage is real and its population cannot see it yet; see this
        # directory's CLAUDE.md, "SAB_EXPECT".
        SAB_EXPECT=""
        # [M6.5.2-FIX] THE OPTIONAL SECOND SITE. Reset here with the rest, so
        # a two-site row cannot leak its extra site into the next row's
        # subshell -- the same reason SAB_COUNT is reset rather than defaulted.
        SAB_FILE2=""
        SAB_BEFORE2=""
        SAB_AFTER2=""
        SAB_COUNT2=1
        # [MECH-REACH 2026-08-25] THE WITNESS'S OWN REACH. See the header
        # block "SAB_REACH / SAB_REACH_POP / SAB_REQUIRE" for the doctrine;
        # reset here with the rest so one row's reach claim cannot leak into
        # the next row's subshell.
        SAB_REACH=""
        SAB_REACH_EXPECT=""
        SAB_REACH_POP=""
        SAB_REQUIRE=""
        SAB_EXPECT_REASON=""
        # shellcheck disable=SC1090
        source "$sab_path"
        for v in SAB_ID SAB_FILE SAB_SUITES SAB_DESC SAB_BEFORE SAB_AFTER; do
            if [ -z "${!v+x}" ]; then
                echo "FATAL[$(basename "$sab_path")]: $v not set" >&2
                exit 2
            fi
        done
        # A TYPO MUST NOT READ AS "DETECTED". `SAB_EXPECT=UNDETECED` silently
        # falling back to the default would turn a checked claim back into an
        # unchecked one -- which is the exact failure this field exists to fix.
        case "${SAB_EXPECT:-DETECTED}" in
            DETECTED|UNDETECTED|UNREACHED) ;;
            *)  echo "FATAL[$(basename "$sab_path")]: SAB_EXPECT must be" \
                     "DETECTED, UNDETECTED or UNREACHED (got '$SAB_EXPECT')" >&2
                exit 2 ;;
        esac
        # ---- [MECH-REACH] THE REACH FIELDS, VALIDATED BEFORE ANYTHING RUNS --
        # Same rule the suite vocabulary and SAB_EXPECT already hold: a field
        # that is half-written must be a FATAL, never a silent fall-back,
        # because falling back turns a checked claim into an unchecked one.
        if [ -n "$SAB_REACH" ] && [ -z "${SAB_REACH_EXPECT//[[:space:]]/}" ]; then
            echo "FATAL[$(basename "$sab_path")]: SAB_REACH set with a blank" \
                 "SAB_REACH_EXPECT -- a reach probe that asserts nothing is" \
                 "not a reach check (tests/reject's blank-expectation rule)" >&2
            exit 2
        fi
        if [ -z "$SAB_REACH" ] && [ -n "$SAB_REACH_EXPECT" ]; then
            echo "FATAL[$(basename "$sab_path")]: SAB_REACH_EXPECT set with no" \
                 "SAB_REACH to produce it" >&2
            exit 2
        fi
        while IFS= read -r popline; do
            [ -n "${popline//[[:space:]]/}" ] || continue
            case "$popline" in
                *"|"*"|"*) ;;
                *)  echo "FATAL[$(basename "$sab_path")]: SAB_REACH_POP entry" \
                         "'$popline' is not FILE|EREGEX|MIN" >&2; exit 2 ;;
            esac
            popmin="${popline##*|}"
            case "$popmin" in
                ''|*[!0-9]*) echo "FATAL[$(basename "$sab_path")]:" \
                    "SAB_REACH_POP entry '$popline' has a non-numeric MIN" >&2
                    exit 2 ;;
            esac
        done <<< "$SAB_REACH_POP"
        # THE INSTRUMENT VOCABULARY IS CLOSED, for the reason the SUITE
        # vocabulary is (R31 C11): a row naming an instrument this driver does
        # not know would be scored as if it had declared nothing, which is the
        # silent version of the thing the field exists to make loud.
        for req in $SAB_REQUIRE; do
            case "$req" in
                asan) ;;
                *)  echo "FATAL[$(basename "$sab_path")]: SAB_REQUIRE names" \
                         "an unknown instrument '$req' (known: asan)" >&2
                    exit 2 ;;
            esac
        done
        if [ "${SAB_EXPECT:-DETECTED}" = "UNREACHED" ]; then
            if [ -z "${SAB_EXPECT_REASON//[[:space:]]/}" ]; then
                echo "FATAL[$(basename "$sab_path")]: SAB_EXPECT=UNREACHED" \
                     "requires a non-blank SAB_EXPECT_REASON -- an expected" \
                     "UNREACHED is a claim, and an unexplained one is the" \
                     "parking space this field exists to refuse" >&2
                exit 2
            fi
            if [ -z "$SAB_REACH" ] && [ -z "${SAB_REACH_POP//[[:space:]]/}" ]; then
                echo "FATAL[$(basename "$sab_path")]: SAB_EXPECT=UNREACHED" \
                     "with no SAB_REACH/SAB_REACH_POP -- nothing in this row" \
                     "can produce that verdict, so the expectation could" \
                     "never be checked" >&2
                exit 2
            fi
        fi

        work="$MECH_SCRATCH/$SAB_ID"
        rm -rf "$work"
        mkdir -p "$work"
        tree="$work/tree"
        mkdir -p "$tree"

        # ===== [MECH-REACH] BEFORE THE SABOTAGE: DOES THE WITNESS REACH? =====
        #
        # Everything in this block runs on the CLEAN tree and BEFORE the
        # sabotage exists, which is the whole point: a row's detector is a
        # WITNESS reaching the sabotaged site, and a witness that stopped
        # reaching it certifies nothing while still scoring `DETECTED` or
        # `UNDETECTED` as if it had measured something. S70 is the worked
        # case -- four escape witnesses expired by BEING IMPLEMENTED and the
        # row went blind from [M6.5.2] until a full matrix scored it
        # UNDETECTED two milestones later, because the "expired claim"
        # doctrine only ever watched UNDETECTED->DETECTED.
        #
        # A row that fails here does NOT build or run its sabotaged tree: the
        # verdict is already known and the minutes are not worth spending on a
        # measurement whose instrument is absent.
        reach_bits=()
        reach_ok=1
        reach_why=""

        # (i) THE INSTRUMENT REQUIREMENT, first, because an unsatisfiable
        # instrument makes the reach question moot: nothing measurable follows
        # either way. Frank's ruling 2026-08-25 -- when the run cannot satisfy
        # a declared instrument the verdict is ANOMALY, never UNDETECTED,
        # which would be a claim about the CODE and a false one.
        for req in $SAB_REQUIRE; do
            case "$req" in
            asan)
                printf 'int main(void){return 0;}\n' > "$work/asan_probe.c"
                if "$CC" -O0 -fsanitize=address,undefined \
                        -o "$work/asan_probe" "$work/asan_probe.c" \
                        > "$work/asan_probe.log" 2>&1 \
                   && "$work/asan_probe" >> "$work/asan_probe.log" 2>&1; then
                    reach_bits+=("require:asan-ok")
                else
                    printf '%s\t%s\t%s\tNOT-RUN (instrument absent)\trequire:asan-UNAVAILABLE\tANOMALY (this row DECLARES SAB_REQUIRE=asan and %s cannot build or run -fsanitize=address,undefined -- an absent instrument is the absence of a measurement, never UNDETECTED; see %s)\n' \
                        "$SAB_ID" "$SAB_FILE" "$SAB_DESC" "$CC" "$work/asan_probe.log"
                    [ "$KEEP" = "1" ] || rm -rf "$work"
                    exit 0
                fi
                ;;
            esac
        done

        # (ii) THE POPULATION FLOOR. "the target file still holds >= N cells
        # matching REGEX", counted on the CLEAN tree and PRINTED whether it
        # passes or fails (learnings.md SS3: every population-deriving check
        # prints its population count). S155's shape: SAB_HARNESS_TARGET
        # pointed at leftrec.rxt, which had held ZERO `gu` cells since
        # [DD-14.EMPTY] -- a witness FILE whose relevant population went to
        # zero, with nothing anywhere saying so.
        while IFS= read -r popline; do
            [ -n "${popline//[[:space:]]/}" ] || continue
            popmin="${popline##*|}"
            poprest="${popline%|*}"
            popfile="${poprest%%|*}"
            popre="${poprest#*|}"
            if [ ! -f "$CLEAN_TREE/$popfile" ]; then
                reach_bits+=("pop:$popfile=NOFILE(want>=$popmin)")
                reach_ok=0
                reach_why="$reach_why; SAB_REACH_POP names $popfile, which does not exist at HEAD"
                continue
            fi
            popn="$(grep -cE -- "$popre" "$CLEAN_TREE/$popfile" || true)"
            reach_bits+=("pop:$popfile=$popn(want>=$popmin)")
            if [ "$popn" -lt "$popmin" ]; then
                reach_ok=0
                reach_why="$reach_why; $popfile holds $popn cell(s) matching /$popre/, below the floor of $popmin this row's detector needs"
            fi
        done <<< "$SAB_REACH_POP"

        # (iii) THE WITNESS PROBE. Run in a per-row TEMP DIRECTORY with the
        # clean tree exported as $TREE and its binary as $PCREC, so a probe
        # that writes an output file (`-o out.c`, the reject rows' own shape)
        # cannot write into the shared clean tree -- enforcement by
        # construction rather than by a rule in a comment. stdout AND stderr
        # are captured: every diagnostic in this compiler goes to stderr.
        if [ -n "$SAB_REACH" ]; then
            mkdir -p "$work/reach"
            (
                cd "$work/reach" || exit 97
                TREE="$CLEAN_TREE" PCREC="$CLEAN_TREE/build/pcrec" \
                REACH_TMP="$work/reach" CC="$CC" \
                    bash -c "$SAB_REACH"
            ) > "$work/reach.log" 2>&1
            reach_rc=$?
            # ONE REQUIRED SUBSTRING PER LINE, and ALL of them must appear.
            # A row's detector is often several witnesses at ONE site (S70:
            # `\Q` and `\R` both reach the escape doorway's epilogue), and
            # asserting one of them would leave the others free to expire
            # exactly the way the four this row started with did.
            reach_want=0
            reach_missing=0
            reach_first_missing=""
            while IFS= read -r wantline; do
                [ -n "${wantline//[[:space:]]/}" ] || continue
                reach_want=$((reach_want + 1))
                if ! grep -qF -- "$wantline" "$work/reach.log"; then
                    reach_missing=$((reach_missing + 1))
                    [ -n "$reach_first_missing" ] || reach_first_missing="$wantline"
                fi
            done <<< "$SAB_REACH_EXPECT"
            if [ "$reach_missing" -eq 0 ]; then
                reach_bits+=("reach:ok($reach_want/$reach_want)")
            else
                reach_bits+=("reach:MISSING($reach_missing/$reach_want)")
                reach_ok=0
                reach_why="$reach_why; the witness probe exited $reach_rc and $reach_missing of its $reach_want expected strings are absent from its output, the first being '$reach_first_missing' -- see $work/reach.log"
            fi
        fi

        # THE SCORING, in both directions, exactly as SAB_EXPECT scores
        # DETECTED/UNDETECTED: an expectation a human maintains in prose is a
        # claim, one the runner checks is a contract. A row that DECLARES its
        # witness dead and is then found to reach is `NOW REACHED` -- the
        # expiry doctrine pointing the other way.
        reach_joined="$(IFS=,; echo "${reach_bits[*]}")"
        if [ "$reach_ok" -eq 0 ]; then
            if [ "${SAB_EXPECT:-DETECTED}" = "UNREACHED" ]; then
                rverdict="UNREACHED (EXPECTED -- $SAB_EXPECT_REASON)"
            else
                rverdict="UNREACHED -- this row's witness no longer reaches the sabotaged site, so it certifies NOTHING until it is re-pointed${reach_why} ***UNEXPECTED***"
            fi
            printf '%s\t%s\t%s\tNOT-RUN (unreached)\t%s\t%s\n' \
                "$SAB_ID" "$SAB_FILE" "$SAB_DESC" "$reach_joined" "$rverdict"
            [ "$KEEP" = "1" ] || rm -rf "$work"
            exit 0
        fi
        if [ "${SAB_EXPECT:-DETECTED}" = "UNREACHED" ]; then
            printf '%s\t%s\t%s\tNOT-RUN (reach re-measured)\t%s\tNOW REACHED -- the witness this row declares dead is live again; re-measure and flip SAB_EXPECT ***UNEXPECTED***\n' \
                "$SAB_ID" "$SAB_FILE" "$SAB_DESC" "$reach_joined"
            [ "$KEEP" = "1" ] || rm -rf "$work"
            exit 0
        fi
        # ===================== end of the reach block ========================

        if ! git -C "$ROOT_DIR" archive HEAD | tar -x -C "$tree" 2>"$work/archive.log"; then
            printf '%s\tFATAL\t%s\tgit archive failed, see %s\tNONE\tANOMALY\n' \
                "$SAB_ID" "$SAB_FILE" "$work/archive.log"
            exit 3
        fi

        printf '%s' "$SAB_BEFORE" > "$work/before.txt"
        printf '%s' "$SAB_AFTER"  > "$work/after.txt"
        if ! python3 "$SCRIPT_DIR/lib/replace.py" \
                "$tree/$SAB_FILE" "$work/before.txt" "$work/after.txt" "$SAB_COUNT" \
                > "$work/apply.log" 2>&1; then
            printf '%s\t%s\tAPPLY-FAILED\t-\t-\tANOMALY (anchor drifted from HEAD -- see %s)\n' \
                "$SAB_ID" "$SAB_FILE" "$work/apply.log"
            [ "$KEEP" = "1" ] || rm -rf "$work"
            exit 0
        fi

        # [M6.5.2-FIX] THE OPTIONAL SECOND SITE, and it exists because a
        # ONE-HUNK MUTATION CANNOT FALSIFY A DEFENCE-IN-DEPTH PAIR. S108 is the
        # case that forced it: `rd_shape` declining a backreference body and
        # `pcrec_uniq_iteration`'s Glushkov model declining the same body are
        # INDEPENDENT gates on the same input, so removing either one changes
        # no emitted byte and the row scored UNDETECTED against correct code.
        # Removing BOTH reaches the wall the row was written to test.
        #
        # OPTIONAL BY CONSTRUCTION: 117 of 118 rows set no SAB_FILE2 and take
        # the branch below zero times, so this cannot change what a one-site
        # row means. It is deliberately not a general N-site list -- a row
        # needing three coordinated edits is describing a refactor, not a
        # plausible mistake, and should be several rows or none.
        #
        # SAME APPLIER, SAME LOUDNESS: the second site goes through replace.py
        # like the first, so a drifted second anchor is an ANOMALY rather than
        # a silent no-op, and scripts/m6read_check_sab_anchors.py checks BOTH
        # sites (it reports SITES as well as rows, so a second site that no
        # instrument reads is impossible by construction).
        if [ -n "$SAB_FILE2" ]; then
            for v in SAB_BEFORE2 SAB_AFTER2; do
                if [ -z "${!v}" ]; then
                    printf '%s\t%s\tAPPLY-FAILED\t-\t-\tANOMALY (SAB_FILE2 set but %s empty)\n' \
                        "$SAB_ID" "$SAB_FILE2" "$v"
                    [ "$KEEP" = "1" ] || rm -rf "$work"
                    exit 0
                fi
            done
            printf '%s' "$SAB_BEFORE2" > "$work/before2.txt"
            printf '%s' "$SAB_AFTER2"  > "$work/after2.txt"
            if ! python3 "$SCRIPT_DIR/lib/replace.py" \
                    "$tree/$SAB_FILE2" "$work/before2.txt" "$work/after2.txt" \
                    "$SAB_COUNT2" > "$work/apply2.log" 2>&1; then
                printf '%s\t%s\tAPPLY-FAILED\t-\t-\tANOMALY (second-site anchor drifted from HEAD -- see %s)\n' \
                    "$SAB_ID" "$SAB_FILE2" "$work/apply2.log"
                [ "$KEEP" = "1" ] || rm -rf "$work"
                exit 0
            fi
        fi

        if ! make -C "$tree" -j"$JOBS" all CC="$CC" > "$work/build.log" 2>&1; then
            printf '%s\t%s\t%s\tBUILD-FAILED\t-\tANOMALY (see %s)\n' \
                "$SAB_ID" "$SAB_FILE" "$SAB_DESC" "$work/build.log"
            [ "$KEEP" = "1" ] || rm -rf "$work"
            exit 0
        fi

        pcrec="$tree/build/pcrec"
        lib="$tree/build/libpcrec.a"
        # [MECH-REACH] THE REACH LINE RIDES THE RESULTS CELL. A retrofitted
        # row prints what its witness proved on EVERY run, not only on the
        # run where it fails -- a population count nobody reads on the green
        # runs is how S155's zero went unnoticed for a whole milestone.
        suite_bits=()
        if [ "${#reach_bits[@]}" -gt 0 ]; then
            suite_bits=("${reach_bits[@]}")
        fi
        any_fail=0
        any_ran=0
        any_skip=0      # an assigned suite could not run for want of an ORACLE
        skipped_arms=() # ...and WHICH ones, so the verdict can name them
        any_anom=0      # a check binary would not build in the sabotaged tree
        # [srMech 2026-08-25, Frank's ruling on S155] AN ARM THAT COULD NOT
        # PERFORM ITS MEASUREMENT, as distinct from one that measured and saw
        # nothing. `any_skip` above is the ORACLE version of this (libpcre2
        # absent); this is the INSTRUMENT version, and it exists because
        # S155's only detector is an ASan build. Where an arm sets this, "zero
        # checks failed" is the ABSENCE of a result and must never be printed
        # as `UNDETECTED` -- which would be a claim about the CODE, and a
        # false one. Set by an arm, read once in the verdict block below;
        # nothing else in this file sets it today, so no existing row's
        # verdict moves.
        any_unmeasured=0
        unmeasured_arms=()  # ...and WHICH, so the verdict can name them

        for suite in $SAB_SUITES; do
            case "$suite" in
            codegen)
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_codegen_tests.sh" \
                    > "$work/codegen.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/codegen.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/codegen.log" | grep -oE '[0-9]+')"
                suite_bits+=("codegen:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            trie)
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_trie_identity.sh" \
                    > "$work/trie.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/trie.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/trie.log" | grep -oE '[0-9]+')"
                suite_bits+=("trie:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            vmidentity)
                # [M4.5b] the §5.4 zero-regression gate. A separate arm from
                # `codegen` on purpose: the property it guards (a capture-free
                # pattern's emitted bytes do not move) is orthogonal to every
                # optimization-present check in that script, and a sabotage of
                # one should not be reported as coverage by the other.
                PCREC="$pcrec" bash "$tree/tests/codegen/run_vm_identity.sh" \
                    > "$work/vmidentity.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/vmidentity.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/vmidentity.log" | grep -oE '[0-9]+')"
                suite_bits+=("vmid:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            endvaridentity)
                # [M6.2 wave A] the `\z`-free byte-identity gate. Its own arm
                # rather than `codegen` or `trie`, for the reason vmidentity is
                # its own: what it guards — that adding a THIRD closure view
                # moved no byte of any pattern that does not use it — is
                # orthogonal to every optimization-present check in
                # run_codegen_tests.sh and to the trie's own equivalence, and a
                # sabotage of one must not be reported as coverage by another.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_endvar_identity.sh" \
                    > "$work/endvaridentity.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/endvaridentity.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/endvaridentity.log" | grep -oE '[0-9]+')"
                suite_bits+=("endvarid:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            wordctxidentity)
                # [M6.2 wave B] the `\b`-free byte-identity gate. Its own arm
                # rather than `endvaridentity`, for exactly the reason that one
                # is not `codegen`: the two guard DIFFERENT constructions (a
                # third POSITION view against `\z`, a CLASS view plus an
                # alphabet refinement plus three start states against `\b`),
                # they use different reference knobs, and a sabotage of one
                # must not be reported as coverage by the other.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_wordctx_identity.sh" \
                    > "$work/wordctxidentity.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/wordctxidentity.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/wordctxidentity.log" | grep -oE '[0-9]+')"
                suite_bits+=("wordctxid:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            mlinectxidentity)
                # [M6.2 wave C] the `(?m)`-free byte-identity gate. Its own arm
                # rather than `wordctxidentity`, on the same rule those two
                # apply to each other: they guard DIFFERENT constructions
                # against DIFFERENT reference knobs, and wave C's is the one
                # that has to survive a mechanical refactor of every site that
                # read wave B's `waccept`/`wlist`/`s1w`. A sabotage of one must
                # not be reported as coverage by the other.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_mlinectx_identity.sh" \
                    > "$work/mlinectxidentity.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/mlinectxidentity.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/mlinectxidentity.log" | grep -oE '[0-9]+')"
                suite_bits+=("mlinectxid:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            mlinediff)
                # [M6.2 wave C] the `(?m)$`-family differential against
                # libpcre2 and python3 `re`. Its own arm because it is the only
                # instrument in the tree that sweeps a generated subject space
                # over patterns with a LIVE prefilter and LIVE skip states —
                # the population §3.6.1 names as the one the scan-avoidance
                # cure can actually break, and the one D11's own 53-divergence
                # history is about. A `.rxt` corpus pins chosen cells; this
                # sweeps.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/assertions/run_mline_diff.sh" \
                    > "$work/mlinediff.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/mlinediff.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/mlinediff.log" | grep -oE '[0-9]+')"
                suite_bits+=("mlinediff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            gstartidentity)
                # [M6.2 wave D] the `\G`-free byte-identity gate. Its own arm
                # rather than any of the three above, on the rule those three
                # already apply to each other: they guard DIFFERENT
                # constructions against DIFFERENT reference knobs. Wave D's is
                # the one that has to survive a FOURTH branch being inserted
                # ahead of the ENG_ATTEMPT start dispatch's existing three, and
                # a sabotage of one must not be reported as coverage by
                # another.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_gstart_identity.sh" \
                    > "$work/gstartidentity.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/gstartidentity.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/gstartidentity.log" | grep -oE '[0-9]+')"
                suite_bits+=("gstartid:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            gstartdiff)
                # [M6.2 wave D] `\G`'s behavioural instrument. Its own arm
                # because it is the only one in the tree that drives
                # docs/spec/match_api.md §3.1's FIND-ALL LOOP against libpcre2
                # driven through the same loop, and the only one that compares
                # the two ENTRIES of one artifact — neither of which any `.rxt`
                # corpus or byte-identity gate can express.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/assertions/run_gstart_diff.sh" \
                    > "$work/gstartdiff.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/gstartdiff.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/gstartdiff.log" | grep -oE '[0-9]+')"
                suite_bits+=("gstartdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            atomicdiff)
                # [M6.4.2] module `atomic-groups`' behavioural instrument, and
                # the ONLY arm that can score four of the module's rows. Three
                # of its four sections exist because nothing else in the tree
                # asks their question: the ENGINE differential (default hybrid
                # vs `--engine=vm`) is where §4's ceiling hazard lives — 114
                # cells of silent match loss were measured on the emitted
                # prefilter — the `-fno-possessify` arm is the only place S92
                # can be red, and the DISCHARGE differential is the only thing
                # that checks "changes no answer" for a rewrite that changes
                # which ENGINE a pattern gets.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/atomic_groups/run_atomic_diff.sh" \
                    > "$work/atomicdiff.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/atomicdiff.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/atomicdiff.log" | grep -oE '[0-9]+')"
                suite_bits+=("atomicdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            atomicidentity)
                # [M6.4.2] the byte-identity gate, and the one arm in this
                # matrix whose reference is a PINNED COMMIT rather than a `-D`
                # knob on this tree's own sources. That matters HERE more than
                # anywhere: tests/mech/CLAUDE.md's own finding is that a
                # knob-built reference is sabotaged TOO, so an edit outside the
                # knob's gated region CANCELS and the sweep reports 100%
                # identical under a live sabotage. This reference is built from
                # `git archive` of a pre-module commit, so no sabotage of this
                # tree can reach it.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_atomic_identity.sh" \
                    > "$work/atomicidentity.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/atomicidentity.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/atomicidentity.log" | grep -oE '[0-9]+')"
                suite_bits+=("atomicidentity:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            brefdiff)
                # [M6.5.2] module `backrefs`' behavioural instrument, and the
                # only arm that can score most of that module's rows. Three of
                # its eight sections exist because nothing else in the tree
                # asks their question: the RE-ENTRY arm is where
                # publish-at-close is observable AND NOWHERE ELSE (R32 E1's
                # 5,808-cell sweep found a backref-FREE control population 0/0
                # in BOTH publication disciplines, so no other suite can see
                # the difference); the `--no-captures` arm is the only place
                # §6.3's "keeps internal slots, reports none" ruling is
                # exercised; and the SPAN-DIVERGENCE section exists for exactly
                # one sabotage, because a prefilter planted on a backref
                # pattern is invisible on any subject where the true span and
                # the erased one agree.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/backrefs/run_backref_diff.sh" \
                    > "$work/brefdiff.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/brefdiff.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/brefdiff.log" | grep -oE '[0-9]+')"
                suite_bits+=("brefdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            dupnamesdiff)
                # [M6.5.2] §8.3's RESOLUTION RULE, swept rather than sampled.
                # Its own arm rather than `brefdiff`'s because it asks a
                # different KIND of question: it carries an INDEPENDENTLY
                # WRITTEN model of the rule and checks that model against
                # libpcre2 as well as checking pcrec against libpcre2, so a
                # sabotage of the rule and a sabotage of the emitted chain
                # score differently here — which is the whole reason S114 and
                # S115 are separate rows.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/backrefs/run_dupnames_diff.sh" \
                    > "$work/dupnamesdiff.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/dupnamesdiff.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/dupnamesdiff.log" | grep -oE '[0-9]+')"
                suite_bits+=("dupnamesdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            brefidentity)
                # [M6.5.2] the byte-identity gate, pinned-commit reference like
                # `atomicidentity`'s and for that arm's reason. Its THIRD axis
                # is this module's own: under `--no-captures` the parser now
                # builds an `A_CAP` for every numbered group and deletes the
                # unreferenced ones at end of parse, so "a backref-free
                # pattern's tree is what it always was" is a claim about a
                # DELETION rather than about code that never ran.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_backref_identity.sh" \
                    > "$work/brefidentity.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/brefidentity.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/brefidentity.log" | grep -oE '[0-9]+')"
                suite_bits+=("brefidentity:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            lookaround)
                # [M6.6.2 wave B+C] module `lookaround`'s behavioural
                # instrument, and it is wired HERE rather than at wave F where
                # the design first placed it (R33 C2-7) because two of this
                # wave's own rows cannot be scored without it.
                #
                # S131 (`.atomic` ignored) is observable ONLY through
                # `nonatomic_ahead.rxt`'s cells, and this arm's §2 sees it in
                # a way no corpus file can: it asserts the EXACT NUMBER of
                # cells on which `(?=` and `(?*` DISAGREE, so a compiler that
                # cut both spellings — or neither — reports agreement where 13
                # disagreements are required. An arm that only checked each
                # spelling against libpcre2 would go green on both S122 and
                # S131, which is the shape this whole directory exists to
                # find. §1 additionally re-drives every `# pcre2-only` cell in
                # the corpus against libpcre2, which is the only oracle those
                # cells have (python has no `(?*` at all).
                #
                # SKIP-IS-NOT-A-PASS is exercised in the failing direction, as
                # `pc3` was: the script prints `SKIP:` lines and `checks
                # passed: 0 / checks failed: 0` when libpcre2 is absent, so
                # the scrape below reports `0fail/0pass` and `any_fail` stays
                # clear — a skipped arm contributes no evidence rather than
                # false evidence. Validated by pointing the oracle import at a
                # nonexistent module: the row's cell reads
                # `laround:0fail/0pass` and the verdict is carried by whatever
                # else ran, never by this.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/lookaround/run_lookaround_diff.sh" \
                    > "$work/lookaround.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/lookaround.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/lookaround.log" | grep -oE '[0-9]+')"
                suite_bits+=("laround:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            recursion)
                # [DD-14] wave B+C: module `recursion`'s behavioural
                # instrument, `tests/recursion/run_recursion_diff.sh`, and it
                # is wired at THIS wave rather than at the module's close for
                # the reason the `lookaround` arm above was: two of this wave's
                # own rows cannot be scored without it.
                #
                # S158 (`pcrec_bref_mark` stops marking `u.call.target`) is
                # observable ONLY on the `--no-captures` axis, and **there is
                # no `.rxt` directive for that flag anywhere in this tree** —
                # the corpus is structurally blind to it, which the corpus's
                # own CLAUDE.md records as an owed gap. This arm's §1 compiles
                # under the flag and reads the ARTIFACT (the slot legend) as
                # well as the answer, because the answer alone can be right by
                # accident on a subject the callee's own text happens to match.
                #
                # S154 (a halved `2*|W|` trail charge) changes NO ANSWER until
                # the trail is exhausted, and a corpus cell has to pick a
                # subject LENGTH in advance. §2 BISECTS for the artifact's own
                # ceiling instead and asserts that one step past it the answer
                # is a TYPED GIVE-UP rather than a wrong `nomatch` — a property
                # that holds at whatever the ceiling is.
                #
                # SKIP-IS-NOT-A-PASS, AND THIS ARM SKIPS ONLY PARTLY, which is
                # a different shape from `laexpand`'s and is why the scrape
                # below does not need `laexpand`'s SKIP-banner special case.
                # §3 (the libpcre2 subject sweep) needs the oracle; §1, §2 and
                # §4 do not and RUN regardless, so on a box with no libpcre2
                # the script still prints a real `checks passed:` count and a
                # real `checks failed:` — never `0/0`, which is the reading
                # that would let a row be called UNDETECTED by an arm that
                # never ran. Validated by pointing the oracle import at a
                # nonexistent module: the cell reads `recdiff:0fail/Npass` with
                # N > 0 and the SKIP line names §3 by number.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/recursion/run_recursion_diff.sh" \
                    > "$work/recursion.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/recursion.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/recursion.log" | grep -oE '[0-9]+')"
                suite_bits+=("recdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            framebuffer)
                # [DD-14.FB] tests/recursion/run_frame_buffer.sh — the caller
                # buffer's two instruments that a corpus cell cannot be: the
                # NULL descriptor compared BYTE FOR BYTE against the un-suffixed
                # entry over a 12-pattern spread, and spec §10.6's mmap'd
                # MAP_NORESERVE reservation driven to its ceiling.
                #
                # SKIP-IS-NOT-A-PASS: section 2 declines (NOTE, not a check) on
                # a machine that will not give it a 2 x 64 MB MAP_NORESERVE
                # reservation, and section 1 runs regardless — so the script
                # still prints a real non-zero `checks passed:` and this cell
                # can never read as 0fail/0pass, which is the reading that would
                # let a row be called UNDETECTED by an arm that never ran.
                # REQUIRE_ASAN=1 -- [srMech 2026-08-25, Frank's ruling on
                # S155] SKIP-IS-NOT-A-PASS APPLIED TO AN INSTRUMENT RATHER
                # THAN AN ORACLE. §2's exact-fit driver is the only thing in
                # this tree that can see an out-of-bounds WRITE, and S155 is
                # a row that changes a write and no answer.
                #
                # MEASURED, NOT ASSUMED -- and the first version of this
                # comment assumed and was WRONG. On this box a sabotaged S155
                # build fails §2 WITHOUT the sanitizer too: the one-frame
                # overrun corrupts the heap and glibc aborts the driver
                # ("double free or corruption (!prev)", exit 134), which §2's
                # own `exact_rc -ne 0` branch scores as a failure. But
                # detection-by-abort is a property of the ALLOCATOR, not of
                # the test -- a write one element past a heap region is UB,
                # and on a box where it lands in slack the three verdicts read
                # 1/-3/-3 and §2 PASSES. This flag is the guard for exactly
                # that box: the script exits 3 on a failed preflight and the
                # row then reads ANOMALY (not measured) rather than
                # UNDETECTED. The opt-in `make test-frame-buffer` route passes
                # no such flag and is unchanged.
                PCREC="$pcrec" CC="$CC" REQUIRE_ASAN=1 \
                    bash "$tree/tests/recursion/run_frame_buffer.sh" \
                    > "$work/framebuffer.log" 2>&1
                fb_rc=$?
                p="$(grep -m1 '^checks passed:' "$work/framebuffer.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/framebuffer.log" | grep -oE '[0-9]+')"
                # THE TOTALS ARE READ FIRST AND THE EXIT STATUS SECOND, on
                # purpose: a red §1 or §3 is a real catch and must stay one
                # even on a box with no sanitizer. Only `exit 3` with nothing
                # failing means "the instrument was missing".
                if [ "${f:-1}" -gt 0 ] 2>/dev/null; then
                    suite_bits+=("framebuf:${f:-ERR}fail/${p:-?}pass")
                    any_fail=1
                    any_ran=1
                elif [ "$fb_rc" -eq 3 ]; then
                    suite_bits+=("framebuf:UNMEASURED-no-asan")
                    any_unmeasured=1
                    unmeasured_arms+=("framebuffer")
                else
                    suite_bits+=("framebuf:${f:-ERR}fail/${p:-?}pass")
                    any_ran=1
                fi
                ;;
            stackdepth)
                # [DD-14.FB]/[TS-4] tests/thread/run_stackdepth_tests.sh — the
                # emitted matcher on a musl-default 128 KB thread stack. Its own
                # arm rather than `harness`, for the reason `vmidentity` is not
                # `codegen`: what it guards is whether one call FITS, which no
                # answer-checking cell anywhere in the tree asks.
                #
                # ITS `KNOWN:` LINE IS NOT SCRAPED, deliberately. Arm A
                # reproduces K33 and is a PINNED state rather than a pass; the
                # totals below count only real checks, so a row cannot be
                # credited with detection by a pin, nor excused by one.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/thread/run_stackdepth_tests.sh" \
                    > "$work/stackdepth.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/stackdepth.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/stackdepth.log" | grep -oE '[0-9]+')"
                suite_bits+=("stackdep:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            laexpand)
                # [M6.6.2 wave E2] THE SUBSTITUTION DRIVER (design §6.3),
                # `tests/lookaround/run_expansion_diff.sh`. A DIFFERENT KIND OF
                # NET from the `lookaround` arm above, and the difference is
                # what decides which rows it is assigned to: that one runs the
                # module's own ~175-block corpus, and this one runs 8,260
                # libpcre2-verified cells that belong to a module which already
                # ships (`tests/assertions/`), textually re-expressed as
                # lookarounds. BREADTH there, DEPTH here — over exactly the
                # body shapes the assertion family uses, which is one class or
                # one literal.
                #
                # SO IT SEES A NARROWER SET OF ROWS THAN ITS POPULATION SIZE
                # SUGGESTS, and the rows it is NOT assigned to are as much a
                # result as the ones it is. Every expansion in §6.1's table is
                # an ATOMIC lookaround with a FIXED-WIDTH body, so a sabotage
                # of the non-atomic flag (S131) or of the width rule (S136) is
                # INVISIBLE here however many cells run — those two are scored
                # by the `lookaround` and `harness` arms, on the module corpus
                # that contains `(?*` and the variable-width refusals. Assigning
                # this arm to them would have bought a bigger denominator and no
                # evidence. The per-row measurement is in tests/mech/CLAUDE.md.
                #
                # SKIP-IS-NOT-A-PASS, exercised in the failing direction as
                # `pc3` was. The script prints `SKIP:` and `checks passed: 0 /
                # checks failed: 0` when libpcre2 is absent, and a bare scrape
                # of those two numbers reads `0fail/0pass` — which the verdict
                # block would then be free to call UNDETECTED, i.e. a FINDING,
                # from an arm that never ran. So the `SKIP:` banner is detected
                # FIRST and the row is marked skipped instead. Validated by
                # pointing the oracle import at a nonexistent module: the cell
                # reads `laexpand:SKIPPED-no-oracle` and the verdict carries
                # `(laexpand SKIPPED -- no oracle)` — see tests/mech/CLAUDE.md.
                #
                # PROCS is passed EXPLICITLY (the [TT-8 FIX] rule): this script
                # reads PROCS from its own environment to pick a worker count,
                # so the outer row-concurrency PROCS would otherwise leak in
                # undivided.
                PCREC="$pcrec" CC="$CC" PROCS="$INNER_PROCS" \
                    bash "$tree/tests/lookaround/run_expansion_diff.sh" \
                    > "$work/laexpand.log" 2>&1
                if grep -q '^SKIP:' "$work/laexpand.log"; then
                    suite_bits+=("laexpand:SKIPPED-no-oracle")
                    any_skip=1
                    skipped_arms+=("laexpand")
                else
                    p="$(grep -m1 '^checks passed:' "$work/laexpand.log" | grep -oE '[0-9]+')"
                    f="$(grep -m1 '^checks failed:' "$work/laexpand.log" | grep -oE '[0-9]+')"
                    suite_bits+=("laexpand:${f:-ERR}fail/${p:-?}pass")
                    [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                    any_ran=1
                fi
                ;;
            kresetdiff)
                # [M6.2 wave E] `\K`'s behavioural instrument. Its own arm for
                # the reason every sibling above has one, plus a wave-E
                # specific: it is the only instrument in the tree that asks
                # libpcre2 the MATCH-HERE question (through `\G(?:pat)` at the
                # same startpos), so it is the only thing that can see the two
                # halves of assertions_design.md §6.3 rule 3 — the filter and
                # the consumed-length return. Wave E ships NO byte-identity
                # gate of its own, deliberately, so this arm and `codegen`
                # carry that wave's whole failing-direction load between them.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/assertions/run_kreset_diff.sh" \
                    > "$work/kresetdiff.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/kresetdiff.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/kresetdiff.log" | grep -oE '[0-9]+')"
                suite_bits+=("kresetdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            assertions)
                # [M6.2 wave A] module `assertions`' own structural checks:
                # the libpcre2 re-verification of its corpus, the module
                # gate's two refusals, and the D47.5 exemption read off the
                # artifact's STRATS stamp in both directions.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/assertions/run_assertions_tests.sh" \
                    > "$work/assertions.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/assertions.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/assertions.log" | grep -oE '[0-9]+')"
                suite_bits+=("asrt:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            gentimeout)
                # [M4.5c fix] D45's own checks. Its own arm because what it
                # guards is a property of the TEST INFRASTRUCTURE, which no
                # other arm can see.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/lib/run_gen_timeout_tests.sh" \
                    > "$work/gentimeout.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/gentimeout.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/gentimeout.log" | grep -oE '[0-9]+')"
                suite_bits+=("gentmo:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            irlisting)
                # [M4.5c] DD-8's program listing held to the artifact it
                # describes. Its own arm rather than `codegen`, for the same
                # reason vmidentity is: the property is orthogonal to every
                # optimization-present check in that script, and a sabotage of
                # one must not be reported as coverage by the other.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/codegen/run_ir_listing.sh" \
                    > "$work/irlisting.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/irlisting.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/irlisting.log" | grep -oE '[0-9]+')"
                suite_bits+=("irlist:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            vm)
                # [M4.5b] the VM engine section: the two bounds, the stamps,
                # and the oracle+differential sweep. The sweep dominates the
                # runtime, which is why this arm is assigned only to sabotages
                # whose signal is a WRONG SPAN — a bounds sabotage gets the
                # arm too, but the arm is never assigned "just in case".
                PCREC="$pcrec" CC="$CC" JOBS="${JOBS:-4}" \
                    bash "$tree/tests/vm/run_vm_tests.sh" > "$work/vm.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/vm.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/vm.log" | grep -oE '[0-9]+')"
                suite_bits+=("vm:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            possdiff)
                # [ENG-BREP] the possessification differential. The arm exists
                # because it is the ONLY suite that can see a wrong
                # possessification verdict: a quantifier the analysis admits
                # unsoundly still matches correctly on most subjects, so the
                # signal is a divergence between the possessified build and
                # the `-fno-possessify` one, not a corpus failure.
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/possessify/run_possdiff.sh" \
                    > "$work/possdiff.log" 2>&1
                p="$(grep -m1 '^possdiff: [0-9]* patterns agreed' "$work/possdiff.log" | grep -oE '[0-9]+' | head -1)"
                f="$(grep -m1 '^possdiff: [0-9]* patterns agreed' "$work/possdiff.log" | grep -oE '[0-9]+' | sed -n 2p)"
                suite_bits+=("possdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            rungdiff)
                # [ENG-BREP] the REVERSE-DETERMINISTIC rung's differential, and
                # the arm exists for the same reason possdiff's does, one rung
                # down: a rung selected on an unsound condition still matches
                # correctly on most subjects, so the signal is a divergence
                # between the rung build and the `-fno-revdet` (replication,
                # i.e. ground truth) one rather than a corpus failure.
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/rungselect/run_rungdiff.sh" \
                    > "$work/rungdiff.log" 2>&1
                p="$(grep -m1 '^rungdiff: [0-9]* patterns agreed' "$work/rungdiff.log" | grep -oE '[0-9]+' | head -1)"
                f="$(grep -m1 '^rungdiff: [0-9]* patterns agreed' "$work/rungdiff.log" | grep -oE '[0-9]+' | sed -n 2p)"
                suite_bits+=("rungdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            counterkdiff)
                # [ENG-BREP] the COUNTER rung's differential, the third arm of
                # the same shape and for the same reason: a rung whose boundary
                # arithmetic is off still matches correctly on most subjects, so
                # the signal is a divergence against the `-fno-counter`
                # (replication = ground truth) build rather than a corpus
                # failure. Its population carries RESIDUE and STRIDE axes,
                # without which a sabotage like S54 (residue tail deleted) is
                # invisible at every count that happens to be a multiple of K.
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/counterk/run_counterkdiff.sh" \
                    > "$work/counterkdiff.log" 2>&1
                p="$(grep -m1 '^counterkdiff: [0-9]* patterns agreed' "$work/counterkdiff.log" | grep -oE '[0-9]+' | head -1)"
                f="$(grep -m1 '^counterkdiff: [0-9]* patterns agreed' "$work/counterkdiff.log" | grep -oE '[0-9]+' | sed -n 2p)"
                suite_bits+=("counterkdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            mrldiff)
                # [M4.6d] MRL pruning's differential, the fourth arm of the
                # same shape. The signal for a WRONG BOUND is a divergence
                # against the `-fno-length-prune` build, not a corpus failure:
                # an over-estimating bound still matches correctly on every
                # subject with slack, and only a subject at or near the
                # pattern's own minimum can tell. Its population carries the
                # STRIDE axis R26 E1 proved a differential is blind without,
                # and it sweeps BOTH ceilings.
                #
                # IT CANNOT SEE AN UNDER-ESTIMATE, and that is a property of
                # the mechanism rather than of this arm: under-estimating
                # prunes LESS, so both arms answer identically and the sweep
                # is silent by construction. S58 is the row that measures
                # that, and the `mrl` arm below is what catches it.
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/mrl/run_mrldiff.sh" \
                    > "$work/mrldiff.log" 2>&1
                p="$(grep -m1 '^mrldiff: [0-9]* pattern-engine pairs agreed' "$work/mrldiff.log" | grep -oE '[0-9]+' | head -1)"
                f="$(grep -m1 '^mrldiff: [0-9]* pattern-engine pairs agreed' "$work/mrldiff.log" | grep -oE '[0-9]+' | sed -n 2p)"
                suite_bits+=("mrldiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            mrl)
                # [M4.6d] MRL's STRUCTURAL checks and acceptance cells. This
                # arm exists because the differential above is structurally
                # blind to the direction that makes the fix a fix: a bound
                # that vanishes, or under-reports, changes NO answer and is
                # invisible to any pcrec-vs-pcrec comparison. What it changes
                # is the STEP COUNT, and the acceptance cells are what read
                # that (the K23 exemplar inside eight steps, the counter
                # rung's own cell, the suffix residual, D51 ruling 2's three
                # obligations against the emitted C).
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/mrl/run_mrl_tests.sh" \
                    > "$work/mrl.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/mrl.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/mrl.log" | grep -oE '[0-9]+')"
                suite_bits+=("mrl:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            prefilter)
                # [M4.6f] the D46 close-out for the PREFILTER axis: the stamp
                # (RX_VM_PREFILTER) and the -fprefilter/-fno-prefilter force
                # pair. Its own arm rather than riding `vm` or `mrl`, for the
                # reason every other structural-check arm here is separate:
                # what it guards (the stamp agreeing with the actual emitted
                # _prefilter() machinery, the do-or-die refusal, the
                # rx_info.flags mask) is orthogonal to what those arms check,
                # and a sabotage of one must not be reported as coverage by
                # another.
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/prefilter/run_prefilter_tests.sh" \
                    > "$work/prefilter.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/prefilter.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/prefilter.log" | grep -oE '[0-9]+')"
                suite_bits+=("prefilter:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            altdiff)
                # [OPT-ALTCLS] the pass's PRIMARY validation instrument: the
                # merged/factored build against `-fno-altcls-merge
                # -fno-altcls-factor` (the unmerged/unfactored ground truth),
                # linked via the SHARED tests/possessify/possdiff_driver.c and
                # swept for span/capture/failure-surface agreement. Its own
                # arm rather than riding `possdiff`, for the reason every
                # other differential arm here is separate: a sabotage of one
                # pass's rewrite must not be reported as coverage by another.
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/altcls/run_altdiff.sh" \
                    > "$work/altdiff.log" 2>&1
                p="$(grep -m1 '^altdiff: [0-9]* patterns agreed' "$work/altdiff.log" | grep -oE '[0-9]+' | head -1)"
                f="$(grep -m1 '^altdiff: [0-9]* patterns agreed' "$work/altdiff.log" | grep -oE '[0-9]+' | sed -n 2p)"
                suite_bits+=("altdiff:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            altcls)
                # [OPT-ALTCLS] the pass's STRUCTURAL checks: the D46 stamp
                # matches what actually merged/factored, denial leaves no
                # trace (0/0, and unchanged rx_info.flags), the two stages
                # are independently controllable, and a verdict-free pattern
                # is byte-identical with the pass on and off.
                PCREC="$pcrec" CC="$CC" \
                    bash "$tree/tests/altcls/run_altcls_tests.sh" \
                    > "$work/altcls.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/altcls.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/altcls.log" | grep -oE '[0-9]+')"
                suite_bits+=("altcls:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            reject)
                # [TT-8 FIX] PROCS explicit, never inherited: see INNER_PROCS
                # above. run_reject_tests.sh reads PROCS itself to size its
                # REJECT_SHARD_TOTAL dispatch.
                PCREC="$pcrec" PROCS="$INNER_PROCS" \
                    bash "$tree/tests/reject/run_reject_tests.sh" \
                    > "$work/reject.log" 2>&1
                p="$(grep -m1 '^checks passed:' "$work/reject.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^checks failed:' "$work/reject.log" | grep -oE '[0-9]+')"
                suite_bits+=("reject:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            harness)
                local target_arg=()
                [ -n "$SAB_HARNESS_TARGET" ] && target_arg=("$tree/$SAB_HARNESS_TARGET")
                # [TT-8 FIX] PROCS explicit, never inherited: see INNER_PROCS
                # above. run.sh reads PROCS itself to size its per-file
                # worker dispatch.
                PCREC="$pcrec" CC="$CC" PROCS="$INNER_PROCS" \
                    bash "$tree/tests/harness/run.sh" "${target_arg[@]}" \
                    > "$work/harness.log" 2>&1
                p="$(grep -m1 '^cases passed:' "$work/harness.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^cases failed:' "$work/harness.log" | grep -oE '[0-9]+')"
                suite_bits+=("corpus:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            registry)
                # tests/registry/ MINUS its libpcre2 half: registry_check.c
                # (the table against the parser, in one process) plus the two
                # compliance_section.py checks (the table against
                # docs/pcre2_compliance.md, via `--list-syntax`). This is the
                # pcrec-reading-pcrec net; `pc3` below is the external one, and
                # they are separate arms because a sabotage's interesting
                # answer is usually WHICH of the two sees it. Neither arm runs
                # run_registry_tests.sh itself: that wrapper's coverage guards
                # fire on a changed PASS COUNT, so a sabotage that made a check
                # legitimately fail would also trip "coverage changed" and the
                # cell could not distinguish detection from a count moving.
                if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
                        -I"$tree/lib" -I"$tree/src" -o "$work/registry_check" \
                        "$tree/tests/registry/registry_check.c" "$lib" \
                        > "$work/registry_build.log" 2>&1; then
                    suite_bits+=("registry:CHECK-BUILD-FAILED")
                    any_anom=1
                else
                    "$work/registry_check" > "$work/registry.log" 2>&1
                    p="$(grep -m1 '^checks passed:' "$work/registry.log" | grep -oE '[0-9]+')"
                    f="$(grep -m1 '^checks failed:' "$work/registry.log" | grep -oE '[0-9]+')"
                    cf=0
                    PCREC="$pcrec" python3 "$tree/tests/registry/compliance_section.py" --check \
                        >> "$work/registry.log" 2>&1 || cf=1
                    PCREC="$pcrec" python3 "$tree/tests/registry/compliance_section.py" --names \
                        >> "$work/registry.log" 2>&1 || cf=1
                    if [ "$cf" = "1" ]; then
                        suite_bits+=("registry:${f:-ERR}fail/${p:-?}pass+compliance-FAIL")
                        any_fail=1
                    else
                        suite_bits+=("registry:${f:-ERR}fail/${p:-?}pass")
                    fi
                    [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                    any_ran=1
                fi
                ;;
            pc3)
                # The EXTERNAL check: the same table against libpcre2. It
                # dlopens the oracle at run time and SKIPS LOUDLY when it is
                # absent, and this arm reproduces that skip AS A VISIBLE CELL
                # rather than as a pass. A row whose only assigned net skipped
                # has measured nothing, and "0 failures because the oracle was
                # missing" is the exact shape of a green run that means nothing
                # — see the verdict block below, which refuses to call that
                # UNDETECTED.
                if ! "$CC" -O2 -g -Wall -Wextra -std=gnu11 \
                        -I"$tree/lib" -I"$tree/src" -o "$work/pcre2_check" \
                        "$tree/tests/registry/pcre2_check.c" "$lib" -ldl \
                        > "$work/pc3_build.log" 2>&1; then
                    suite_bits+=("pc3:CHECK-BUILD-FAILED")
                    any_anom=1
                else
                    "$work/pcre2_check" > "$work/pc3.log" 2>&1
                    if grep -q '^SKIP:' "$work/pc3.log"; then
                        suite_bits+=("pc3:SKIPPED-no-oracle")
                        any_skip=1
                        skipped_arms+=("pc3")
                    else
                        p="$(grep -m1 '^checks passed:' "$work/pc3.log" | grep -oE '[0-9]+')"
                        f="$(grep -m1 '^checks failed:' "$work/pc3.log" | grep -oE '[0-9]+')"
                        suite_bits+=("pc3:${f:-ERR}fail/${p:-?}pass")
                        [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                        any_ran=1
                    fi
                fi
                ;;
            cli)
                # tests/cli/run_cli_tests.sh — the CLI surface and library API.
                # NOTE the scrape: this script counts `cases`, not `checks`,
                # like the corpus harness and unlike every other arm here.
                PCREC="$pcrec" CC="$CC" bash "$tree/tests/cli/run_cli_tests.sh" \
                    > "$work/cli.log" 2>&1
                p="$(grep -m1 '^cases passed:' "$work/cli.log" | grep -oE '[0-9]+')"
                f="$(grep -m1 '^cases failed:' "$work/cli.log" | grep -oE '[0-9]+')"
                suite_bits+=("cli:${f:-ERR}fail/${p:-?}pass")
                [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1
                any_ran=1
                ;;
            *)
                suite_bits+=("UNKNOWN-SUITE:$suite")
                ;;
            esac
        done

        # THE SKIP MUST NEVER READ AS A PASS. TWO arms can decline to run —
        # `pc3` and, since [M6.6.2] wave E2, `laexpand`; both need libpcre2 —
        # and a skipped oracle contributes no evidence in either direction. So a row whose ONLY nets skipped is
        # INCONCLUSIVE, never UNDETECTED (which is a finding, and would be a
        # false one), and a row that did run something still carries the skip
        # visibly in its verdict, because "caught by nothing" means something
        # different when one of the nets was not in the water.
        verdict="DETECTED"
        if [ "$any_ran" -eq 0 ] && [ "$any_skip" -eq 1 ]; then
            verdict="INCONCLUSIVE -- every assigned suite SKIPPED (no libpcre2 oracle: $(IFS=' '; echo "${skipped_arms[*]}"))"
        elif [ "$any_ran" -eq 0 ] && [ "$any_anom" -eq 1 ]; then
            verdict="ANOMALY (every assigned check binary failed to build)"
        elif [ "$any_ran" -eq 0 ]; then
            verdict="ANOMALY (no suite ran)"
        elif [ "$any_fail" -eq 0 ] && [ "$any_unmeasured" -eq 1 ]; then
            # [srMech 2026-08-25, Frank's ruling on S155] AN INSTRUMENT THE
            # ROW DEPENDS ON DID NOT RUN, so ZERO CHECKS FAILED is the absence
            # of a measurement rather than a finding -- exactly the reading
            # the `any_skip` branch above refuses for a missing ORACLE, and
            # refused here for a missing SANITIZER. Placed BEFORE the
            # UNDETECTED branch and AFTER nothing else, so a row whose other
            # arms DID catch the edit still reads DETECTED: `any_fail`
            # outranks this, which is why it is the guard on this branch.
            verdict="ANOMALY (an assigned arm could not perform its measurement: $(IFS=' '; echo "${unmeasured_arms[*]}") -- see its log)"
        elif [ "$any_fail" -eq 0 ]; then
            verdict="**UNDETECTED -- ZERO CHECKS FAILED**"
        fi
        # ---- SCORE THE VERDICT AGAINST THE ROW'S EXPECTATION ----
        # [DD-14 wave B+C] S19's lesson applied as a MECHANISM. The finding is
        # no longer "this row was caught by nothing" -- which is only a finding
        # when nobody expected it -- but "this row did not do what its
        # definition SAYS it does". The two directions are both findings and
        # both fail the run:
        #
        #   expect DETECTED, got UNDETECTED -- a guard regressed, or the row's
        #       population was never adequate. The original finding, unchanged.
        #   expect UNDETECTED, got DETECTED -- the row's claim has EXPIRED: a
        #       later wave grew the population that closes it. The expectation
        #       is now a lie and must be re-measured and flipped. This is the
        #       known_fail ratchet's "now passing" shape, and it is why an
        #       expected-UNDETECTED row is not a place to park a dead sabotage.
        #
        # INCONCLUSIVE and ANOMALY are scored against NEITHER: they are the
        # absence of a measurement, and an absent measurement must never
        # satisfy an expectation (the same reason a SKIP is not a PASS above).
        expect="${SAB_EXPECT:-DETECTED}"
        case "$verdict" in
            DETECTED)              actual="DETECTED"   ;;
            \*\*UNDETECTED*)        actual="UNDETECTED" ;;
            *)                     actual="OTHER"      ;;
        esac
        if [ "$actual" = "UNDETECTED" ] && [ "$expect" = "UNDETECTED" ]; then
            verdict="UNDETECTED (EXPECTED -- see this row's SAB_DOC_FIGURE for what would close it)"
        elif [ "$actual" = "DETECTED" ] && [ "$expect" = "UNDETECTED" ]; then
            verdict="NOW DETECTED -- re-measure and flip the expectation ***UNEXPECTED***"
        elif [ "$actual" = "UNDETECTED" ] && [ "$expect" = "DETECTED" ]; then
            verdict="$verdict ***UNEXPECTED***"
        fi

        # The suffix NAMES the arms that skipped rather than assuming `pc3`:
        # with one skipped arm it renders exactly as it always did.
        [ "$any_ran" -gt 0 ] && [ "$any_skip" -eq 1 ] && \
            verdict="$verdict ($(IFS=' '; echo "${skipped_arms[*]}") SKIPPED -- no oracle)"
        [ "$any_ran" -gt 0 ] && [ "$any_anom" -eq 1 ] && \
            verdict="$verdict + ANOMALY (a check binary failed to build)"

        bits_joined="$(IFS=,; echo "${suite_bits[*]}")"
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
            "$SAB_ID" "$SAB_FILE" "$SAB_DESC" "$SAB_SUITES" "$bits_joined" "$verdict"

        if [ "$KEEP" = "1" ]; then
            echo "KEEP=1: $SAB_ID tree + logs kept at $work" >&2
        else
            rm -rf "$work"
        fi
    )
}

# ---- run all requested sabotages ------------------------------------------
#
# Serial by default (PROCS=1): a correct, diffable matrix first. PROCS>1 runs
# sabotages concurrently — safe because run_one is already fully isolated per
# sabotage — with rows merged in sabotages/ listing order so the matrix output
# is byte-identical to a serial run's.

results_file="$(mktemp "$MECH_SCRATCH/results.XXXXXX")"
: > "$results_file"

if [ "$PROCS" -gt 1 ] && [ "${#sab_files[@]}" -gt 1 ]; then
    rowdir="$(mktemp -d "$MECH_SCRATCH/rows.XXXXXX")"
    running=0
    for f in "${sab_files[@]}"; do
        echo "-- running $(basename "$f") --" >&2
        run_one "$f" > "$rowdir/$(basename "$f").row" &
        running=$((running + 1))
        if [ "$running" -ge "$PROCS" ]; then
            wait -n || true
            running=$((running - 1))
        fi
    done
    wait
    for f in "${sab_files[@]}"; do
        cat "$rowdir/$(basename "$f").row" >> "$results_file" 2>/dev/null || true
    done
    cat "$results_file" >&2
else
    for f in "${sab_files[@]}"; do
        echo "-- running $(basename "$f") --" >&2
        run_one "$f" | tee -a "$results_file" >&2
    done
fi
# run_one's stdout IS the tsv row; tee above sent it to stderr for a progress
# view too, so re-extract just the tab-separated rows for the table below
grep -P '^\S+\t' "$results_file" > "$results_file.rows" || true

echo
echo "== detection matrix =="
{
    printf 'id\tfile\tedit\tsuites run\tresults\tverdict\n'
    cat "$results_file.rows"
} | column -t -s "$(printf '\t')"

echo
unexpected="$(grep -c 'UNEXPECTED' "$results_file.rows" || true)"
undetected="$(grep -c 'UNDETECTED' "$results_file.rows" || true)"
anomalies="$(grep -c 'ANOMALY\|APPLY-FAILED\|BUILD-FAILED\|FATAL' "$results_file.rows" || true)"
oracle_skipped="$(grep -c 'SKIPPED-no-oracle' "$results_file.rows" || true)"
# [MECH-REACH] counted BESIDE undetected/anomalies rather than folded into
# either: an UNREACHED row is neither "the guards saw it" nor "the guards
# missed it" -- it is "the witness was not there to look", which is a third
# thing and the one this mechanism exists to make countable.
unreached="$(grep -c 'UNREACHED\|NOW REACHED' "$results_file.rows" || true)"
total="$(wc -l < "$results_file.rows" | tr -d ' ')"

# The denominator guard: `total` above is derived from the rows that ARRIVED,
# which is the same source as the numerators — a sabotage that produced no row
# (a definition failing validation, or a lost parallel worker) would silently
# shrink the matrix and 19/19 would read as 20/20. Count the DEMAND side from
# the sabotages/ listing instead and refuse the mismatch loudly.
if [ "$total" -ne "${#sab_files[@]}" ]; then
    echo "*** FATAL: ${#sab_files[@]} sabotage(s) requested but only $total row(s) arrived. ***"
    echo "*** A sabotage that vanishes is a lost measurement, never a smaller matrix. ***"
    for f in "${sab_files[@]}"; do
        id="$(basename "$f" | sed -E 's/^(S[0-9]+)[-_].*/\1/')"
        grep -q "^$id	" "$results_file.rows" || echo "    - missing: $(basename "$f")"
    done
    rm -f "$results_file" "$results_file.rows"
    exit 2
fi

if [ "${unexpected:-0}" -gt 0 ]; then
    echo "*** $unexpected of $total sabotage(s) did NOT match the expectation their definition states. ***"
    echo "*** That is not a bug in this script -- it is the finding it exists to surface. ***"
    echo "*** A row reading 'NOW DETECTED' has an EXPIRED claim: some later wave grew the      ***"
    echo "*** population that closes it. Re-MEASURE it, then flip its SAB_EXPECT -- do not     ***"
    echo "*** simply delete the row, and do not leave the stale expectation standing.          ***"
    grep 'UNEXPECTED' "$results_file.rows" | cut -f1,6 | sed 's/^/    - /'
fi
if [ "${anomalies:-0}" -gt 0 ]; then
    echo "*** $anomalies sabotage(s) hit an ANOMALY (anchor drift, build failure, or archive failure) and were NOT measured. ***"
    grep 'ANOMALY\|APPLY-FAILED\|BUILD-FAILED\|FATAL' "$results_file.rows" | cut -f1 | sed 's/^/    - /'
fi
if [ "${unreached:-0}" -gt 0 ]; then
    echo "*** $unreached row(s) reported UNREACHED: the row's own WITNESS does not reach the      ***"
    echo "*** sabotaged site on the CLEAN tree, so the row certifies nothing. It was NOT built    ***"
    echo "*** or run. Re-POINT the witness at a live one (and say so in the row's header) --      ***"
    echo "*** do not delete the row, and do not read a DETECTED/UNDETECTED verdict off a row      ***"
    echo "*** whose witness has expired. 'NOW REACHED' is the other direction: a row that         ***"
    echo "*** DECLARES its witness dead and was found live. Re-measure, then flip SAB_EXPECT.     ***"
    grep 'UNREACHED\|NOW REACHED' "$results_file.rows" | cut -f1,5,6 | sed 's/^/    - /'
fi
if [ "${oracle_skipped:-0}" -gt 0 ]; then
    echo "*** $oracle_skipped row(s) ran with an ORACLE-DEPENDENT arm SKIPPED (pc3 and/or       ***"
    echo "*** laexpand): libpcre2-8-0 is absent, so the EXTERNAL oracle contributed nothing to   ***"
    echo "*** those verdicts. Read them accordingly — for the rows whose only external answer is ***"
    echo "*** one of those two, this run did not measure them. The row cell names which arm.     ***"
    grep 'SKIPPED-no-oracle' "$results_file.rows" | cut -f1 | sed 's/^/    - /'
fi

rm -f "$results_file" "$results_file.rows"
if [ "$KEEP" != "1" ]; then
    [ -n "${rowdir:-}" ] && rm -rf "$rowdir"
    [ -n "$CLEAN_TREE" ] && rm -rf "$MECH_SCRATCH/_clean"
    # remove the scratch root only if this run created it (and it is empty)
    [ "$MADE_SCRATCH" = "1" ] && rmdir "$MECH_SCRATCH" 2>/dev/null
fi

# COMPLETION TRAILER. The one line a watcher may poll for. Never check
# whether this script is still running with `pgrep -f "make mech"` (or any
# pattern naming this script): the session harness wraps every polling
# command in a shell whose OWN command line contains that pattern, so the
# poll matches itself and answers RUNNING forever — a control sharing a
# source with its subject, measured 2026-08-12: a finished run was reported
# alive 51 minutes after completion, twice. Completion is a fact about the
# LOG, not about a process listing: grep the log for this trailer (or for
# FATAL, the only early exit that skips it).
#
# AND READ THE THIRD OUTCOME: a run with NO TRAILER AND NO `FATAL` WAS
# KILLED, NOT FAILED — treat its output as damage rather than data. The
# MECH-2 row-count guard below cannot see that case and is not meant to: it
# counts arrived rows INSIDE this script, so a SIGTERM'd run never reaches
# it, and the log simply stops. Measured 2026-08-19 ([M6.2] wave C), when a
# `pkill -f run_sabotage_matrix` aimed at a duplicate run took out a live
# sibling's child — the pattern is over the whole command line, so two
# legitimate concurrent runs are indistinguishable under it. Kill a run by
# its PROCESS GROUP or its recorded PID, never by a name pattern; it is the
# same root as the no-`pgrep -f` rule above, which is that a command line is
# not an identity.
echo
echo "== mech run COMPLETE: $total rows (unexpected: ${unexpected:-0}, undetected: ${undetected:-0}, unreached: ${unreached:-0}, anomalies: ${anomalies:-0}, oracle-skipped: ${oracle_skipped:-0}) at $SHA =="

# A MISMATCHED EXPECTATION FAILS THE RUN. Before this field the script exited
# 0 with the finding printed, because an UNDETECTED row was a fact to read
# rather than a contract to enforce; now that every row STATES its outcome,
# a row that disagrees with its own definition is a broken contract and the
# caller must see it in the exit status, not only in the log.
[ "${unexpected:-0}" -gt 0 ] && exit 1

exit 0
