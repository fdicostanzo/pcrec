#!/usr/bin/env bash
# tests/axes/run_axes.sh — [CHK-2] piece 2: THE ANSWER-IDENTITY SWEEP.
#
# THE COUNT IN THIS SENTENCE IS PROSE AND HAS DRIFTED BEFORE — read the job
# list at the foot of the file for what actually runs, and the "(bit N)"
# cross-check for what is required to. What the sweep covers is: every
# BIT-FLAG member of the deny/force family, the coarse `--engine=` pair, and
# (since [CC-DIFF] STEP 2) the `--vm-entry-shape=` ORDINAL — TIERED: its two
# reachable-by-default rungs (`forward`, `inline`) on every run, all four
# under `AXES_FULL=1`, which `scripts/battery.sh`'s axes stage exports. A
# default-only green run is a claim about TWO of that axis's four rungs and
# the run's own tier line says which.
#
# docs/spec/tuning.md §2 documented THIRTEEN axes when this was written, and
# for eleven of the
# BIT-FLAG members of the deny/force family (bits 4-31 of
# pcrec_options.flags) the promise is ANSWER-IDENTITY: the .rxt corpus's
# match/nomatch/span/capture/give-up answer under the axis must equal the
# default build's answer, case for case. Before this script only 4 of the
# 13 axes had ANY corpus-wide answer sweep (run_recursion_identity.sh's
# default/vm/noprefilter/nocaptures byte-identity axes, and
# run_codegen_tests.sh's three-flag loop over eight hand-picked patterns) —
# see docs/dev/plan.md [CHK-2]'s charter. This is the corpus-wide one, for
# every axis, comparing ANSWERS rather than PASS/FAIL COUNTS: two runs can
# have equal pass/fail counts while disagreeing on which specific cases
# passed (a real risk here — this project's own default run is required to
# be 0-failure against the .rxt corpus's oracle-verified expectations, so an
# axis whose OWN run is also 0-failure against those SAME fixed expectations
# has, by construction, answered every case identically to default; but that
# argument only holds while both runs share the identical case POPULATION —
# an axis that silently changes which patterns COMPILE at all would still
# read 0/0 against a shrunken population. The per-case identity check below
# catches that: a case present in one dump and missing from the other is a
# POPULATION change, visible as LOST/GAINED regardless of either run's own
# pass/fail count).
#
# THE MECHANISM: tests/harness/run.sh's RXTDUMP hook (this script's own
# addition — see that file's header comment), which appends ONE LINE per
# evaluated case — <file>\t<line>\t<kind>\t<route>\t<trc>\t<out> — in a
# format stable across PROCS values. A baseline dump (no extra flags) and an
# axis dump (RXTFLAGS=<the axis's deny/force spelling>) are compared by
# tests/axes/dump_diff.awk, keyed by <file>:<line> (unique — .rxt cases are
# one per source line): AGREE (same trc+out), MISMATCH (same key, different
# answer — the axis's answer-identity promise broken), LOST (case ran under
# default, not under the axis — the axis changed what compiles), GAINED (the
# reverse). Every one of the twelve bit-flag axes is DENY-ONLY or FORCE-PAIR
# over the DEFAULT (auto) engine selection, which tuning.md documents as
# never refusing EXCEPT `PCREC_FORCE_PREFILTER` (§2.5, bit 9) — the one
# member of the family that is DO-OR-DIE (refuses on a pattern that compiles
# to the pure DFA engine, since there is no VM artifact to attach a
# prefilter to). So: MISMATCH is a FAILURE on every axis (an answer that
# moved), and LOST is a FAILURE on every axis EXCEPT bit 9, where it is the
# axis's own documented refusal population — printed, not failed, per this
# script's own "an axis documented as NOT answer-preserving is compared
# against its documented behaviour, never silently excluded" rule. GAINED
# (a case appearing that wasn't in the default population at all) is not
# documented as possible for ANY axis and is therefore always a FAILURE.
#
# THE REGISTRY IS DERIVED, NEVER HAND-COPIED (docs/dev/learnings.md §3's
# "a REFERENCE BUILD assembled by ... hand-enumerated list drifts silently"):
# every `PCREC_NO_*`/`PCREC_FORCE_*` bit constant in lib/pcrec.h (the single
# source of the deny/force family — tuning.md §2's own citations point back
# to it) and its CLI spelling in cli/main.c's argument loop (the single
# source of the flag TEXT), cross-checked against tuning.md §2's own
# "(bit N)" mentions so a bit added to lib/pcrec.h with no doc heading, or a
# heading with no bit, is RED before either run below starts.
#
# THE COARSE AXIS (§2.11, `--engine=vm`/`--engine=dfa`) rides the identical
# mechanism — RXTFLAGS accepts an arbitrary extra flag, not only a `-f`
# spelling, verified live (`build/pcrec --engine=vm ...` compiles exactly as
# `build/pcrec -fno-possessify ...` does, both flags landing in `pflags`
# before the pattern's own `--`) — but its refusal population is NOT
# do-or-die-exceptional the way bit 9's is: tuning.md §2.11 documents BOTH
# directions as capable of refusing (`--engine=dfa` on anything needing
# backtracking machinery; `--engine=vm` in principle, though no corpus
# member is expected to exercise it), so LOST is printed, never failed, on
# EITHER engine direction — "refusals recorded, not failed" is this script's
# brief's own wording for this one axis.
#
# THE ORACLE CROSS-CHECK (K35-class control: the DEFAULT run's own answers
# come from the SAME harness an axis run does, so an axis that reproduces a
# shared bug identically to default would read AGREE on every case and this
# script alone would call it clean). tests/registry/run_pc4.sh is PC-4, the
# one instrument in this tree that compares pcrec's ANSWERS (not merely
# ACCEPTANCE, which is PC-3's narrower claim) against a LIVE libpcre2 on a
# match/nomatch/span basis. Its own pattern space (escape-class/POSIX-class
# constructs, 273 patterns, 232 accepted, 62,872 cells) is capture-free, so
# it compiles to the pure DFA engine — which makes it the RIGHT population
# for cross-checking a DFA-side axis and the WRONG one for a VM-only rung
# (possessify/revdet/counter never fire on a capture-free pattern at all).
# `-fno-premul-table` (bit 15, §2.13) is DFA-side and answer-identity, so
# this script runs PC-4 twice — once plain, once through a one-line wrapper
# that prepends `-fno-premul-table` to every pcrec invocation (a flag before
# `--` composes with anything PC-4's own args supply, verified live) — and
# asserts BOTH runs report PC-4's own pinned population (273/41/232/62872,
# 0 failures): if libpcre2 itself disagreed with a "denied" build that
# happened to agree with pcrec's own (possibly-buggy) default, this is the
# check that would still see it, because its ground truth is external.
#
# THE DETECT DEMONSTRATION (docs/dev/learnings.md §3: "ask of any new guard
# ... what would have to be true for it to fail, and who chose that input").
# Performed once, 2026-08-26, in a SCRATCH copy under the session scratchpad
# (never this worktree's own `src/` — this lane is tests+Makefile only):
# `premul_val` (src/gen/emit_dfa.c:1521) is `return pm ? st * ncls : st;` —
# the IDENTITY function on the INDEXED (non-premultiplied) form, i.e. the
# form `-fno-premul-table` selects. Changed to `return pm ? st * ncls : st + 1;`
# in the scratch copy — every emitted indexed-table transition target off by
# one, reachable ONLY through the denied build (the default premultiplied
# build never calls this branch). Rebuilt `build/pcrec` from the sabotaged
# tree in a scratch copy OUTSIDE this worktree and ran `SKIP_ORACLE=1
# AXES="-fno-premul-table" PCREC=<the sabotaged binary> bash
# tests/axes/run_axes.sh tests/base/alternation.rxt`:
#
#     axes: axis -fno-premul-table (PCREC_NO_PREMUL_TABLE, bit 15) (RXTFLAGS="-fno-premul-table")...
#     MISMATCH tests/base/alternation.rxt:4 (m): default={trc=0 out=match 0 1} axis={trc=0 out=match 0 0}
#     MISMATCH tests/base/alternation.rxt:9 (m): default={trc=0 out=match 0 3} axis={trc=0 out=nomatch}
#     MISMATCH tests/base/alternation.rxt:38 (m): default={trc=0 out=match 0 2 0 1} axis={trc=0 out=nomatch}
#     [... 17 more, capped at 20 printed ...]
#       keys_base=26 keys_axis=26 agree=4 mismatches=22 lost=0 gained=0
#     AXIS FAIL: -fno-premul-table (PCREC_NO_PREMUL_TABLE, bit 15): 22 mismatch(es), 0 lost (UNEXPECTED — not documented as do-or-die), 0 gained
#     run_axes.sh: FAILED — see AXIS FAIL lines above
#
# — named the exact axis and every diverging case (span AND capture slots,
# e.g. line 38's `0 2 0 1` -> `nomatch`), on the FIRST corpus file alone: 22
# of its 26 cases diverged. The scratch tree was deleted immediately after
# (never built inside this worktree, never committed).
#
# Usage: bash tests/axes/run_axes.sh [file-or-dir ...]
#   With no arguments, sweeps the whole tests/ tree (tests/harness/run.sh's
#   own default). A narrower argument list is for a QUICK local check only —
#   the delivered `make test-axes` runs with no arguments.
# Env:
#   AXES        space-separated list of CLI flag spellings (e.g.
#               "-fno-possessify -fno-revdet") to restrict the sweep to —
#               empty (default) runs all twelve bit-flag axes plus both
#               engine directions. For a QUICK check, not the delivered run.
#   PCREC/CC/GENCFLAGS   forwarded to tests/harness/run.sh verbatim.
#   PROCS       forwarded to tests/harness/run.sh (default: nproc, matching
#               test-corpus's own default).
#   KEEP=1      keep the per-axis RXTDUMP files (default: cleaned up).
#   SKIP_ORACLE=1   skip the PC-4 cross-check (for a quick local run; the
#               delivered `make test-axes` always runs it).

set -u
export LC_ALL=C   # K35 — see tests/harness/run.sh's own header for why

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # TIMEOUT_BIN, gen_run/gen_cc budgets
export WATCHDOG_SECTION="axes"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
PROCS="${PROCS:-$(nproc 2>/dev/null || echo 1)}"
KEEP="${KEEP:-0}"
SKIP_ORACLE="${SKIP_ORACLE:-0}"
AXES="${AXES:-}"

if [ ! -x "$PCREC" ]; then
    echo "run_axes.sh: $PCREC not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-axes.XXXXXX")"
cleanup() { [ "$KEEP" = "1" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

fail=0
t_start=$(date +%s)

# ============================================================================
# THE REGISTRY — derived from lib/pcrec.h and cli/main.c, never hand-copied.
# ============================================================================

# bit -> macro name, e.g. bits[4]=PCREC_NO_POSSESSIFY. Scoped to 4..31.
#
# THE LOW BOUND IS THE LOAD-BEARING ONE and the high one is not: bits below 4
# are unrelated `1u << N` constants in the same header (PCREC_CASELESS and
# friends) and must never be swept in, while the top of the deny/force family
# simply moves every time an axis is added. It was written as `4..15` — the
# family's extent on the day it was written — and [OPT-K]'s bit 16 was
# therefore DERIVED AWAY SILENTLY: the new axis would have been absent from
# the sweep with no failure, which is exactly the "an axis shipped without its
# five things" gap [CHK-2] exists to close, arriving through [CHK-2]'s own
# instrument. 31 is the width of the `unsigned` the flags live in, so it needs
# no maintenance; the cross-check below catches a bit that has a constant and
# no doc heading either way.
declare -A bit_macro=()
while IFS=$'\t' read -r macro bit; do
    [ -n "$macro" ] || continue
    if [ "$bit" -ge 4 ] && [ "$bit" -le 31 ]; then
        bit_macro[$bit]="$macro"
    fi
done < <(grep -oE 'PCREC_(NO|FORCE)_[A-Z_]+ *= *1u << [0-9]+' "$ROOT_DIR/lib/pcrec.h" \
          | sed -E 's/^(PCREC_(NO|FORCE)_[A-Z_]+) *= *1u << ([0-9]+)$/\1\t\3/')

n_bits=${#bit_macro[@]}
if [ "$n_bits" -eq 0 ]; then
    echo "run_axes.sh: FATAL: derived ZERO deny/force bit constants from lib/pcrec.h — extraction is broken (docs/dev/learnings.md §3: hard-fail on empty, never silently measure nothing)" >&2
    exit 1
fi

# macro -> CLI flag spelling, from cli/main.c's own `!strcmp(a, "...")` /
# `opt.flags |= MACRO` pairing. One awk pass over the arg-parsing loop:
# remembers the most recently seen `strcmp(a, "X")` literal, and pairs it
# with the next `opt.flags |= MACRO` line, which is exactly how the loop
# itself associates the two.
declare -A macro_flag=()
# POSIX-awk portable (RSTART/RLENGTH, no 3-arg match() — that's a gawk
# extension and D2's "a stranger's box" discipline avoids relying on one
# where a two-line rewrite avoids it): remembers the most recently seen
# `strcmp(a, "-...")` literal and pairs it with the next
# `opt.flags |= PCREC_(NO|FORCE)_...` line, exactly how the parsing loop
# itself associates the two.
while IFS=$'\t' read -r macro flagtext; do
    [ -n "$macro" ] && macro_flag[$macro]="$flagtext"
done < <(awk '
    /strcmp\(a, "-/ {
        if (match($0, /"-[^"]+"/)) pending = substr($0, RSTART + 1, RLENGTH - 2)
    }
    /opt\.flags \|= PCREC_(NO|FORCE)_[A-Z_]+;/ {
        if (pending != "" && match($0, /PCREC_(NO|FORCE)_[A-Z_]+/)) {
            print substr($0, RSTART, RLENGTH) "\t" pending
            pending = ""
        }
    }
' "$ROOT_DIR/cli/main.c")

# Sanity: every derived bit macro must have a derived CLI spelling, or the
# awk pairing above missed a site (cli/main.c's loop shape changed) — a
# silent empty flag would compile the DEFAULT pattern under every "axis",
# comparing default against default and reporting perfect agreement on
# every one, the exact "measures nothing" failure mode this family's own
# suites (run_possdiff.sh et al.) guard against.
for bit in "${!bit_macro[@]}"; do
    macro="${bit_macro[$bit]}"
    if [ -z "${macro_flag[$macro]:-}" ]; then
        echo "run_axes.sh: FATAL: $macro (bit $bit) has no derived CLI flag spelling in cli/main.c — the awk pairing missed it; a wrong sweep would silently compare default against default" >&2
        exit 1
    fi
done

# ---- cross-check against tuning.md §2's own "(bit N)" headings -----------
TUNING="$ROOT_DIR/docs/spec/tuning.md"
# THE SECTION ANCHOR DOES NOT SPELL THE COUNT IN ENGLISH. It read
# `/^## 2\. The thirteen axes/` and [OPT-K] renamed that heading to "fourteen"
# — after which the range matched NOTHING, `doc_bits` came back EMPTY, and the
# comparison below failed with a blank documented column. A heading that
# carries a number is a heading that moves; anchoring on the section NUMBER
# is what the cross-check actually means.
doc_bits="$(sed -n '/^## 2\./,/^## 3\./p' "$TUNING" \
    | grep -oE '\(bit [0-9]+\)' | grep -oE '[0-9]+' | LC_ALL=C sort -n -u)"
reg_bits="$(printf '%s\n' "${!bit_macro[@]}" | LC_ALL=C sort -n -u)"
if [ "$doc_bits" != "$reg_bits" ]; then
    echo "run_axes.sh: FATAL: tuning.md §2's documented bits and lib/pcrec.h's derived bits DISAGREE" >&2
    echo "  documented (tuning.md \"(bit N)\" mentions): $(echo "$doc_bits" | tr '\n' ' ')" >&2
    echo "  derived    (lib/pcrec.h 1u << N, bits 4-31): $(echo "$reg_bits" | tr '\n' ' ')" >&2
    echo "  a bit in one column and not the other means a new axis shipped with no" >&2
    echo "  doc heading, or a heading survived its axis's removal" >&2
    exit 1
fi
echo "axes: registry derived — $n_bits bit-flag axes (bits ${reg_bits//$'\n'/,}), matching tuning.md §2's own $(echo "$doc_bits" | wc -l) documented bit mentions"

# which bit is the one DO-OR-DIE member (tuning.md §2.5: PCREC_FORCE_PREFILTER
# refuses on a DFA-selected pattern) — derived by NAME PREFIX, not
# hand-picked, so a second FORCE_ member added later is picked up the same
# way without an edit here.
force_bit=""
for bit in "${!bit_macro[@]}"; do
    case "${bit_macro[$bit]}" in
        PCREC_FORCE_*) force_bit="$bit" ;;
    esac
done

# ============================================================================
# THE DOCUMENTED-REFUSAL LOOKUP (manager's classification rule, 2026-08-26,
# from the first full-corpus sweep's own findings). A REFUSED case (pcrec
# itself declined to compile the pattern under this axis) is counted as
# REFUSED-DOCUMENTED — a population, floored (K35), never a failure — ONLY
# when its diagnostic TEXT contains the axis's own documented limit
# substring, verified live against the shipped diagnostics below (never
# hand-guessed): src/gen/emit_vm.c's replication-cap ctx_fail
# ("would replicate its body") for -fno-counter, and
# src/opt/select_engine.c's force-prefilter refusal
# ("-fprefilter requires the VM engine") for -fprefilter. This is
# DELIBERATELY NOT a blanket per-axis exemption: an axis with NO entry here
# (every other member of the family) treats ANY REFUSED case as an
# UNDOCUMENTED refusal — promoted to a real failure — because tuning.md
# documents every other bit-flag axis as NEVER refusing under the default
# (auto) engine this sweep uses (only §2.8/§2.9's ENGINE-SELECTING pair can
# refuse at all, and only when COMBINED with `--engine=dfa`, which this
# sweep does not do). REFUSAL_FLOOR is the K35 floor for the axes that DO
# have a pattern — the count THIS SESSION measured on the full corpus,
# rounded down generously, so a later change that stops an axis refusing
# its known population is caught loudly rather than silently reading as
# "fewer refusals, must be an improvement".
REFUSAL_DELIM=$'\x01'   # joins multiple documented substrings per axis; an
                        # axis can have more than one distinct diagnostic
                        # shape, and a REFUSED case matches if it contains
                        # ANY of them (never all — they are ALTERNATIVES,
                        # not conjuncts).
declare -A REFUSAL_PATTERN=(
    # K45 (2026-09-02/03) — tests/size/size_term.rxt:34-35's nested-repeat
    # tower (`(?:(?:...(?:a|b){41}...){41}` six deep, `engine vm`-forced so
    # the pattern reaches the size term's own machinery rather than the
    # DFA/NFA build the block's header says is "a pre-existing limit that
    # has nothing to do with the size term") REFUSES under five axes, and
    # every one of the five is a REAL, documented pcrec limit — not a
    # defect — that the axis's own denial reaches by a route this sweep had
    # no entry for. `-fno-counter` has TWO distinct replication-cap
    # diagnostic shapes in src/gen/emit_vm.c (verified live 2026-08-26/
    # 2026-09-03): the single-level one this entry already matched
    # ("a bounded repeat would replicate its body"), and — reached only by
    # a NESTED bounded-repeat tower, which the pre-existing substring never
    # matched — "nested bounded repeats would replicate a body N times in
    # total (limit 131072). Repetition counts MULTIPLY through nesting" at
    # src/gen/emit_vm.c:2663-2665, same PCREC_MAX_VM_REPLICATION_PRODUCT
    # cap, different wording because the message names the tower rather
    # than one level. Measured population on this file alone: 2
    # (size_term.rxt:34-35); no full-corpus resweep performed to raise the
    # floor (K35: a floor is a measured number, and this file's count is
    # not the corpus's).
    ["-fno-counter"]="would replicate its body${REFUSAL_DELIM}nested bounded repeats would replicate a body"
    # -fprefilter's do-or-die (§2.5) has THREE distinct diagnostic shapes
    # in src/opt/select_engine.c, verified live (2026-08-26, against the
    # actual full-corpus REFUSED population — 12,537 of the first shape,
    # 446+259 of the second, 0 of the third since this sweep never passes
    # both -fprefilter and -fno-prefilter together): the DFA-selected
    # pattern refusal ("-fprefilter requires the VM engine"), the
    # capture-erasure conflict for a pattern containing a backreference OR
    # a subroutine call ("cannot be honoured for a pattern containing a"
    # — ONE substring covers both nouns, since the format string is
    # shared and only the noun varies), and the flag-conflict refusal
    # ("cannot both be requested", dormant here — this sweep never sets
    # -fno-prefilter alongside -fprefilter — kept so it is not silently
    # undocumented the day something does).
    # FOURTH shape since [SEL-1] (2026-08-28): under auto a prefilter DFA
    # that overflows a cap is DROPPED, but the FORCE form is do-or-die
    # (§2.5: "-fprefilter itself still REFUSES with today's diagnostic
    # (§2.11)"), so -fprefilter on such a pattern refuses with the DFA
    # cap's own text. Population measured on the first sweep after [SEL-1]:
    # 2 (tests/base/k18_cost_gates.rxt:67-68, the [SEL-1] witness cells).
    # FIFTH shape, K45 (2026-09-03): forcing a prefilter needs a DFA/NFA
    # built alongside the VM artifact regardless of the pattern's own
    # `engine vm` directive, so on size_term.rxt's tower this axis reaches
    # src/ir/nfa.c's construction cap ("pattern too large (NFA exceeds
    # 131072 states)") BEFORE any of the four shapes above ever get a
    # chance to fire — the same general NFA-build limit --engine=dfa hits
    # below, verified live, substring shared between the two entries on
    # purpose. Measured population on this file alone: 2. No floor raised
    # (K35; this file's count is not a corpus-wide measurement).
    ["-fprefilter"]="-fprefilter requires the VM engine${REFUSAL_DELIM}cannot be honoured for a pattern containing a${REFUSAL_DELIM}cannot both be requested${REFUSAL_DELIM}pattern too complex for the DFA engine${REFUSAL_DELIM}pattern too large (NFA exceeds"
    # --engine=dfa's own do-or-die posture (§2.11) has TWO distinct shapes
    # in select_engine.c's switch (verified live against the full-corpus
    # REFUSED population — 3,874 of the first, 5,594 of the second): the
    # generic VM_ONLY-construct refusal ("%s requires the VM engine, which
    # --engine=dfa excludes" — possessive quantifiers, \K, backreferences,
    # calls, ... all share this one format string, so the substring is
    # deliberately generic rather than a per-construct list, which would
    # silently exclude the next construct a future module adds under the
    # same refusal), and the captures-conflict branch D44.6/E-7 documents
    # by name ("this pattern requires captures (on by default)" — the
    # SEPARATE branch taken when the pattern's own capture default, not a
    # VM_ONLY construct, is what forces the VM). A third documented DFA
    # limit exists in src/ir/dfa.c ("pattern too complex for the DFA
    # engine", the state-count/subset-construction ceiling) with ZERO
    # corpus population today — not added as a pattern, since a
    # zero-population entry cannot be verified live and this axis's own
    # floor is left unset for the same reason (K35: a floor asserts a
    # MEASURED population, never a guessed one).
    # THIRD shape now populated, K45 (2026-09-03): forcing `--engine=dfa`
    # on size_term.rxt's `engine vm`-forced tower requires the SAME NFA
    # build the VM-forced form was written to skip (this block's own
    # header comment), so the axis reaches src/ir/nfa.c's construction cap
    # ("pattern too large (NFA exceeds 131072 states)") rather than either
    # of the two branches above — this is the zero-population third limit
    # this entry's earlier comment named and declined to add; it now has a
    # measured population (2, this file's two `n` cells) reached through a
    # different door (the pre-existing NFA-state cap, not the DFA
    # subset-construction one src/ir/dfa.c's own message names) than the
    # one that comment anticipated, so the substring is the NFA message's,
    # shared verbatim with -fprefilter's fifth shape above. No floor raised
    # (K35; this file's count is not a corpus-wide measurement).
    ["--engine=dfa"]="requires the VM engine${REFUSAL_DELIM}requires captures (on by default)${REFUSAL_DELIM}pattern too large (NFA exceeds"
    # K45 (2026-09-03): these two axes had NO entry at all before — every
    # REFUSED case under them was unconditionally promoted to a failure,
    # which is correct in general (tuning.md documents neither as
    # do-or-die) but wrong for size_term.rxt's tower, where BOTH reach a
    # real, pre-existing structural cap rather than any defect. Verified
    # live, 2026-09-03, against this file alone (population 2 each; no
    # floor — K35, not a corpus-wide count):
    # `-fno-altcls-merge` denies the alternation-to-class merge that keeps
    # this tower's VM node count under the emitted-node cap, so denying it
    # reaches src/gen/emit_vm.c's own cap message directly ("pattern too
    # large (VM exceeds 131072 emitted nodes)").
    ["-fno-altcls-merge"]="pattern too large (VM exceeds"
    # `-fno-size-term` denies the size term's own K-ladder (the mechanism
    # this whole file's r40 R1 witness exists to test), so on this tower
    # the emitted C reverts to its unchunked size and trips the emitted-
    # code-bytes ceiling directly ("pattern too large: N bytes of emitted
    # code (limit 500000)").
    ["-fno-size-term"]="bytes of emitted code (limit"
)
declare -A REFUSAL_FLOOR=(
    ["-fno-counter"]=180
    ["-fprefilter"]=12000
    ["--engine=dfa"]=8000
)

# ============================================================================
# THE BASELINE
# ============================================================================

BASE_DUMP="$WORKDIR/base.tsv"
echo
echo "axes: baseline run (no extra flags)..."
t0=$(date +%s)
"$ROOT_DIR/scripts/watchdog" -l axes-baseline -S axes -s 3600 -- \
    env RXTDUMP="$BASE_DUMP" PCREC="$PCREC" CC="$CC" GENCFLAGS="$GENCFLAGS" \
        PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" \
        bash "$ROOT_DIR/tests/harness/run.sh" "$@" > "$WORKDIR/base.out" 2>"$WORKDIR/base.err"
base_rc=$?
t1=$(date +%s)
tail -6 "$WORKDIR/base.out"
if [ "$base_rc" -ne 0 ]; then
    echo "run_axes.sh: FATAL: the BASELINE run itself failed (rc=$base_rc) — an axis" >&2
    echo "  cannot be compared against a default that is not itself green; see" >&2
    echo "  $WORKDIR/base.err (KEEP=1 to preserve it)" >&2
    cat "$WORKDIR/base.err" >&2
    exit 1
fi
base_keys=$(wc -l < "$BASE_DUMP")
if [ "$base_keys" -eq 0 ]; then
    echo "run_axes.sh: FATAL: baseline dump has ZERO lines — RXTDUMP produced nothing; the sweep would compare empty against empty and measure nothing (docs/dev/learnings.md §3)" >&2
    exit 1
fi
echo "axes: baseline: $base_keys cases dumped, $((t1 - t0))s"

# ============================================================================
# THE TWELVE BIT-FLAG AXES
# ============================================================================

declare -a axis_results=()
run_one_axis() {
    # run_one_axis <label> <extra-flags-string> <force-population-not-failure>
    local label="$1" flags="$2" lost_is_ok="$3"
    # $lost_is_ok's original job (blanket-accept a nonzero LOST count for
    # the one documented do-or-die bit-flag and the coarse engine axis) is
    # SUPERSEDED by REFUSAL_PATTERN/REFUSAL_FLOOR below (2026-08-26,
    # manager's classification rule): a REFUSED case is now reclassified
    # by its own diagnostic TEXT, per axis, never by a blanket per-axis
    # flag — kept as a parameter (call sites still pass it, harmlessly)
    # rather than touched, since it is no longer read for the verdict.
    shift 3   # THE BUG (found 2026-08-26, live full-corpus run): without this,
    # "$@" below still refers to THIS FUNCTION's own full positional list
    # (label, flags, lost_is_ok, ...) rather than the trailing file/dir
    # arguments the caller forwarded — so those three strings got passed to
    # tests/harness/run.sh as bogus "file" arguments on EVERY axis call. In
    # the no-args (full-corpus) case this is fatal: run.sh's own `$# -eq 0`
    # branch (scan the whole tests/ tree) never fires because $# is 3, not
    # 0, and none of the three strings is a real path, so the corpus never
    # loads at all -- "22005 lost" was every case in the BASELINE dump
    # having no counterpart, not a real per-axis effect. It was invisible
    # in this file's own two-file spot check (real file args among the
    # three bogus ones still got processed and dominated the small
    # population) and only showed up on the delivered full-corpus run.
    # [TT-12 STEP 1] per-label, not fixed, names for the harness's own
    # stdout/stderr and the diff-awk stderr: with two axes now able to run
    # CONCURRENTLY (the pairing loop below), a fixed `$WORKDIR/axis.out`/
    # `axis.err`/`diff.err` would be a race between the two subshells —
    # every AXIS FAIL/PASS decision is computed from `diffline` (an awk
    # value captured into a local var, never read back from these files) so
    # the race could not flip a verdict, but the DIAGNOSTIC TEXT a failure
    # prints ("---- axis.out ----" etc.) could show the WRONG axis's
    # output, which defeats the whole point of printing it. One `slug` per
    # label, reused everywhere a per-axis file is named (dump/rowsfile
    # already used this shape; outlog/errlog/diffe are new).
    local slug
    slug="$(echo "$label" | tr -c 'A-Za-z0-9' '_')"
    local dump="$WORKDIR/axis_$slug.tsv"
    local outlog="$WORKDIR/axis_$slug.out"
    local errlog="$WORKDIR/axis_$slug.err"
    echo
    echo "axes: axis $label (RXTFLAGS=\"$flags\")..."
    local t0 t1
    t0=$(date +%s)
    "$ROOT_DIR/scripts/watchdog" -l "axes-$label" -S axes -s 3600 -- \
        env RXTFLAGS="$flags" RXTDUMP="$dump" PCREC="$PCREC" CC="$CC" \
            GENCFLAGS="$GENCFLAGS" PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" \
            bash "$ROOT_DIR/tests/harness/run.sh" "$@" > "$outlog" 2>"$errlog"
    local axis_rc=$?
    t1=$(date +%s)
    if [ ! -f "$dump" ]; then
        echo "AXIS FAIL: $label: run.sh produced NO dump at all (rc=$axis_rc) — see $errlog" >&2
        cat "$errlog" >&2
        fail=1
        axis_results+=("$label|FAIL|no-dump|$((t1 - t0))s")
        return
    fi
    local rowsfile="$WORKDIR/rows_$slug.tsv"
    : > "$rowsfile"
    local diffe="$WORKDIR/diff_$slug.err"
    local diffline
    diffline="$(awk -v BASEFILE="$BASE_DUMP" -v ROWSFILE="$rowsfile" -f "$SCRIPT_DIR/dump_diff.awk" "$dump" 2>"$diffe")"
    cat "$diffe" >&2
    echo "  $diffline"
    local mismatches budget refused lost gained agree_n keys_base_n keys_axis_n
    mismatches="$(echo "$diffline" | grep -oE 'mismatches=[0-9]+' | cut -d= -f2)"
    budget="$(echo "$diffline" | grep -oE 'budget=[0-9]+' | cut -d= -f2)"
    refused="$(echo "$diffline" | grep -oE 'refused=[0-9]+' | cut -d= -f2)"
    lost="$(echo "$diffline" | grep -oE 'lost=[0-9]+' | cut -d= -f2)"
    gained="$(echo "$diffline" | grep -oE 'gained=[0-9]+' | cut -d= -f2)"
    agree_n="$(echo "$diffline" | grep -oE 'agree=[0-9]+' | cut -d= -f2)"
    keys_base_n="$(echo "$diffline" | grep -oE 'keys_base=[0-9]+' | cut -d= -f2)"
    keys_axis_n="$(echo "$diffline" | grep -oE 'keys_axis=[0-9]+' | cut -d= -f2)"
    # [manager finding, 2026-08-26, live full-corpus run] A 0-KEY (or
    # near-0-key) AXIS RUN IS A HARNESS-LEVEL FAILURE, NEVER MERELY A LARGE
    # "lost" POPULATION — the run_axes.sh bug that produced exactly this
    # shape (the run_one_axis "$@" shift bug above) printed nothing but
    # "22005 lost" lines and an AXIS FAIL summary, with the harness's own
    # stderr (tests/harness/run.sh's real error text) sitting unread in
    # $WORKDIR/axis.err the whole time — a check reading NOTHING and
    # calling it something (docs/dev/learnings.md §3). So: whenever the
    # axis run produced fewer than HALF of the baseline's own keys, this is
    # loud and DIFFERENT from the ordinary per-case LOST reporting above —
    # print the harness's actual stdout/stderr, not just the diff counts.
    if [ -n "$keys_base_n" ] && [ "$keys_base_n" -gt 0 ] && [ -n "$keys_axis_n" ] && \
       [ "$keys_axis_n" -lt "$((keys_base_n / 2))" ]; then
        echo "AXIS FAIL: $label: HARNESS-LEVEL FAILURE — only $keys_axis_n of $keys_base_n baseline keys were produced (a per-case LOST count would UNDER-report this: the harness itself did not run the corpus, not merely an axis population change). tests/harness/run.sh's own stdout/stderr for this axis:" >&2
        echo "---- $outlog ----" >&2
        cat "$outlog" >&2
        echo "---- $errlog ----" >&2
        cat "$errlog" >&2
        echo "---- end harness output ----" >&2
        fail=1
        axis_results+=("$label|FAIL|harness-level:$diffline|$((t1 - t0))s")
        [ "$KEEP" = "1" ] || rm -f "$dump"
        return
    fi
    # THE REFUSED-ROW RECLASSIFICATION (manager's rule, 2026-08-26).
    # dump_diff.awk cannot know which axis it is comparing — every REFUSED
    # case lands in one bucket, with the pcrec diagnostic TEXT attached.
    # This is the axis-specific half: a REFUSED case counts as
    # REFUSED-DOCUMENTED only when its text contains THIS axis's own
    # documented-limit substring (REFUSAL_PATTERN, above); anything else is
    # an UNDOCUMENTED refusal — promoted to a real failure, printed loudly,
    # and NEVER silently absorbed ("do NOT blanket-exempt an axis" — an
    # axis with no REFUSAL_PATTERN entry at all promotes every REFUSED case
    # unconditionally, which is correct: tuning.md documents every
    # bit-flag axis except the force-prefilter pair as NEVER refusing
    # under the default engine this sweep uses).
    local refused_documented=0 refused_undocumented=0
    local pattern_list="${REFUSAL_PATTERN[$flags]:-}"
    local -a patterns=()
    if [ -n "$pattern_list" ]; then
        IFS="$REFUSAL_DELIM" read -ra patterns <<< "$pattern_list"
    fi
    if [ "$refused" -gt 0 ]; then
        while IFS=$'\t' read -r cls key btrc bout atrc reason; do
            [ "$cls" = "REFUSED" ] || continue
            local matched=0 p
            for p in "${patterns[@]:-}"; do
                [ -n "$p" ] || continue
                if printf '%s' "$reason" | grep -qF -- "$p"; then
                    matched=1
                    break
                fi
            done
            if [ "$matched" = "1" ]; then
                refused_documented=$((refused_documented + 1))
            else
                refused_undocumented=$((refused_undocumented + 1))
                if [ "$refused_undocumented" -le 20 ]; then
                    echo "AXIS FAIL: $label: UNDOCUMENTED refusal at $key: \"$reason\" (does not match any of this axis's documented limits$([ "${#patterns[@]}" -eq 0 ] && echo " — this axis has NO documented refusal population at all"))" >&2
                fi
            fi
        done < "$rowsfile"
    fi
    local total_mismatches=$((mismatches + refused_undocumented))
    # K35 FLOOR: an axis with a documented refusal population must still be
    # REACHING it — a change that quietly stopped the cap/force refusal
    # from firing would otherwise read as "0 refused, cleaner!" instead of
    # "the mechanism this axis exists to test stopped happening". Its own
    # FAIL condition, kept separate from total_mismatches (a floor breach
    # is a POLICY failure — the refused population shrank — not a real
    # per-case answer disagreement, and the two must not be added together
    # where a reader would misread the count as case-level mismatches).
    local floor="${REFUSAL_FLOOR[$flags]:-}" floor_breach=0
    if [ -n "$floor" ] && [ "$refused_documented" -lt "$floor" ]; then
        echo "AXIS FAIL: $label: refused_documented=$refused_documented is BELOW its K35 floor ($floor) — the documented refusal population shrank; find out why before lowering the floor" >&2
        floor_breach=1
    fi
    echo "  agree=$agree_n budget-bound=$budget refused-documented=$refused_documented (floor $([ -n "$floor" ] && echo "$floor" || echo "none")) lost-other=$lost mismatches=$total_mismatches gained=$gained"
    local verdict="OK"
    if [ "$total_mismatches" -gt 0 ] || [ "$gained" -gt 0 ] || [ "$lost" -gt 0 ] || [ "$floor_breach" -eq 1 ]; then
        verdict="FAIL"
        fail=1
        echo "AXIS FAIL: $label: $total_mismatches mismatch(es) (incl. $refused_undocumented undocumented refusal(s)), $lost lost-other, $gained gained$([ "$floor_breach" -eq 1 ] && echo ", refused-documented floor breached")" >&2
    fi
    if [ "$budget" -gt 0 ]; then
        echo "  ($budget case(s) budget-bound — a give-up/timeout on one side, not an answer disagreement, never a failure)"
    fi
    if [ "$refused_documented" -gt 0 ]; then
        echo "  ($refused_documented case(s) refused with this axis's own documented limit — a population, not a failure)"
    fi
    axis_results+=("$label|$verdict|$diffline refused_doc=$refused_documented refused_undoc=$refused_undocumented|$((t1 - t0))s")
    [ "$KEEP" = "1" ] || rm -f "$dump" "$rowsfile" "$outlog" "$errlog" "$diffe"
}

# ============================================================================
# BUILD THE ORDERED JOB LIST — SAME axes, SAME order, SAME AXES= filtering
# as the sequential form (bit-flag axes in bit order, then --engine=vm,
# then --engine=dfa) — pairing changes ONLY how the list below is executed,
# never which axes run or the order their summary rows are printed in.
# ============================================================================

declare -a job_label=() job_flags=() job_lost_ok=()
for bit in $(printf '%s\n' "${!bit_macro[@]}" | LC_ALL=C sort -n); do
    macro="${bit_macro[$bit]}"
    flagtext="${macro_flag[$macro]}"
    label="$flagtext ($macro, bit $bit)"
    if [ -n "$AXES" ]; then
        case " $AXES " in (*" $flagtext "*) ;; (*) continue ;; esac
    fi
    lost_ok=0
    [ "$bit" = "$force_bit" ] && lost_ok=1
    job_label+=("$label"); job_flags+=("$flagtext"); job_lost_ok+=("$lost_ok")
done
if [ -z "$AXES" ] || printf '%s' "$AXES" | grep -q -- '--engine'; then
    job_label+=("--engine=vm (§2.11)");  job_flags+=("--engine=vm");  job_lost_ok+=("1")
    job_label+=("--engine=dfa (§2.11)"); job_flags+=("--engine=dfa"); job_lost_ok+=("1")
fi
# [CC-DIFF] STEP 2 THE VM ENTRY SHAPE (§2.21), the coarse axis's shape one
# option over: an ORDINAL rather than a bit, so it is appended here for the
# same reason `--engine=` is — RXTFLAGS takes an arbitrary extra flag, not
# only a `-f` spelling — and the four rungs are FOUR JOBS, because "the
# answers do not move" is a claim about each rung and not about the family.
#
# `lost_ok` IS 0 ON ALL FOUR, AND THAT IS A STRICTLY STRONGER CLAIM THAN THE
# COARSE AXIS MAKES. `--engine=dfa` is DO-OR-DIE and legitimately refuses, so
# its LOST population is documented rather than failed. This axis NEVER
# refuses: a rung the artifact cannot legally take is a SELECTION OUTCOME —
# the emitter falls to the nearest legal rung of the same body-count family
# (`docs/spec/tuning.md` §2.21) — so a LOST case here means a pattern stopped
# compiling under a flag that cannot make that happen, and it is a failure.
#
# THE FOUR RUNGS ARE TIERED, and the tiering line is the manager's ruling
# (2026-09-04) rather than this file's own economy: four permanent
# full-corpus runs is too much for the DAY's suite.
#
#   DEFAULT (`make test-axes`, two extra runs): rungs 3 `forward` and 4
#     `inline`. Rung 3 is what AUTO SELECTS below the size term, i.e. the
#     shape most artifacts in the tree are actually built at; rung 4 is the
#     ladder's max-speed end and the shape [CC-DIFF] STEP 1 shipped.
#   `AXES_FULL=1` (the BATTERY, four extra runs): adds rungs 1 `plain` and
#     2 `shared`. `scripts/battery.sh`'s axes stage exports it.
#
# THE SPLIT IS BY REACH, NOT BY IMPORTANCE, AND THE SWEEP MUST SAY WHICH IT
# SWEPT. Rungs 1 and 2 are not the cheap ones to drop — rung 2 is HALF of the
# new emitted code (the forward entries and the static empty descriptor land
# on rungs 2 AND 3, so rung 3 keeps that half covered by default, which is why
# the pair chosen is 3+4 and not 1+4). What the default sweep genuinely does
# NOT cover is rung 1's no-attribute emission and rung 2's `noinline` matcher.
# A default-only green run is therefore a claim about TWO rungs, and this
# script's summary line says so rather than letting "axes: all identical" read
# as a claim about four.
#
# [TT-12] STEP 1's pairwise execution below absorbs the jobs two at a time
# either way, so the DEFAULT costs about one run's wall time and the BATTERY
# about two.
_shape_tier="not run (filtered out by AXES=)"
if [ -z "$AXES" ] || printf '%s' "$AXES" | grep -q -- '--vm-entry-shape'; then
    _shape_rungs="3 4"
    _shape_tier="default (rungs forward,inline; AXES_FULL=1 adds plain,shared)"
    if [ "${AXES_FULL:-0}" = "1" ]; then
        _shape_rungs="1 2 3 4"
        _shape_tier="FULL (all four rungs; AXES_FULL=1)"
    fi
    echo "axes: --vm-entry-shape tier = $_shape_tier"
    for _shape in $_shape_rungs; do
        job_label+=("--vm-entry-shape=$_shape (§2.21)")
        job_flags+=("--vm-entry-shape=$_shape")
        job_lost_ok+=("0")
    done
fi

# ============================================================================
# [TT-12 STEP 1] RUN THE JOB LIST PAIRWISE — two axes concurrently, each at
# PROCS/2 (rounded up). docs/dev/tt12_step0_profile.md §4 measured why this
# should be close to additive rather than contending: a single axis's own
# wall time is bounded by ONE `.rxt` file's case count under the harness's
# per-FILE PROCS dispatch (tests/assertions/multiline.rxt at 3,065 cases,
# 56% more than the next-largest file), not by PROCS reaching nproc — the
# box already sits at roughly half load through most of one axis's own run
# for a reason unrelated to PROCS width, so a SECOND axis's independent
# file-granularity bottleneck should fill the other half rather than queue
# behind the first.
#
# THE SHIFT-3 BUG'S FIX (see run_one_axis's own header) is exactly why this
# job list is built and iterated by INDEX rather than passed straight into
# a `&`-backgrounded call inline — this file has already shipped one bug
# from positional-argument confusion and a second layer of indirection
# (background subshells around a function with a fixed positional-arg
# contract) is exactly where that class of mistake would recur silently.
#
# WHY A RESULT FILE PER JOB, NOT AXIS_RESULTS DIRECTLY: `( ... ) &` forks a
# subshell — its own `fail=1` and its own `axis_results+=(...)` are
# invisible to this process once the subshell exits, bash subshells do not
# share writable state back to their parent. Each backgrounded job writes
# its own $WORKDIR/pararesult_<slug> (axis_results line, then fail 0/1) and
# $WORKDIR/paraout_<slug> (everything run_one_axis would otherwise have
# printed live), and the parent re-absorbs both after `wait` — so the
# printed summary table and the AXIS FAIL semantics are IDENTICAL to the
# sequential form, only the moment output appears (after both of a pair
# finish, rather than streamed live) differs.
#
# `trap - EXIT` inside the subshell is not decoration: the top-level
# `trap cleanup EXIT` (which deletes the WHOLE $WORKDIR unless KEEP=1) is
# INHERITED by a forked subshell, so without this the first background job
# to finish would delete $WORKDIR — including the shared BASE_DUMP and the
# still-running sibling axis's own dump/rowsfile — out from under
# everything else still using it.
PAIR_PROCS=$(( (PROCS + 1) / 2 ))
[ "$PAIR_PROCS" -lt 1 ] && PAIR_PROCS=1
if [ "$PAIR_PROCS" -lt "$PROCS" ]; then
    echo "axes: pairing two axes at a time, PROCS=$PAIR_PROCS each (was $PROCS sequential)"
fi

n_jobs=${#job_label[@]}
i=0
while [ "$i" -lt "$n_jobs" ]; do
    pair_idx=("$i")
    [ "$((i + 1))" -lt "$n_jobs" ] && pair_idx+=("$((i + 1))")
    outfiles=(); resultfiles=(); pids=()
    for idx in "${pair_idx[@]}"; do
        jslug="$(echo "${job_label[$idx]}" | tr -c 'A-Za-z0-9' '_')"
        out="$WORKDIR/paraout_$jslug"
        res="$WORKDIR/pararesult_$jslug"
        outfiles+=("$out"); resultfiles+=("$res")
        (
            trap - EXIT
            PROCS="$PAIR_PROCS"
            run_one_axis "${job_label[$idx]}" "${job_flags[$idx]}" "${job_lost_ok[$idx]}" "$@"
            printf '%s\n' "${axis_results[-1]}" > "$res"
            echo "$fail" >> "$res"
        ) > "$out" 2>&1 &
        pids+=("$!")
    done
    for p in "${pids[@]}"; do wait "$p"; done
    for k in "${!pair_idx[@]}"; do
        cat "${outfiles[$k]}"
        idx="${pair_idx[$k]}"
        if [ -s "${resultfiles[$k]}" ]; then
            axis_results+=("$(sed -n '1p' "${resultfiles[$k]}")")
            [ "$(sed -n '2p' "${resultfiles[$k]}")" = "1" ] && fail=1
        else
            echo "AXIS FAIL: ${job_label[$idx]}: the background job produced NO result file at all — treating this as a hard failure rather than silently dropping the axis from the summary" >&2
            fail=1
            axis_results+=("${job_label[$idx]}|FAIL|no-result-file|?s")
        fi
        [ "$KEEP" = "1" ] || rm -f "${outfiles[$k]}" "${resultfiles[$k]}"
    done
    i=$((i + 2))
done

# ============================================================================
# THE ORACLE CROSS-CHECK — PC-4 (live libpcre2) under -fno-premul-table
# ============================================================================

oracle_verdict="SKIPPED"
if [ "$SKIP_ORACLE" != "1" ]; then
    echo
    echo "axes: oracle cross-check — PC-4 (live libpcre2) under -fno-premul-table (bit 15, §2.13, DFA-side and answer-identity; PC-4's own pattern space is capture-free -> pure DFA, so this is the family member it actually exercises)..."
    PLAINOUT="$WORKDIR/pc4_plain.out"
    "$ROOT_DIR/scripts/watchdog" -l axes-pc4-plain -S axes -s 900 -- \
        env PCREC="$PCREC" CC="$CC" bash "$ROOT_DIR/tests/registry/run_pc4.sh" \
        > "$PLAINOUT" 2>&1
    plain_rc=$?
    if grep -q '^SKIP:' "$PLAINOUT"; then
        oracle_verdict="SKIPPED (libpcre2 runtime absent — see PC4OUT)"
        echo "  $oracle_verdict"
    else
        # a one-line wrapper: -fno-premul-table PREPENDED, so it lands before
        # run_pc4.sh's own -p/-o/--/pattern args regardless of their order —
        # verified live (see this file's header): a `-f` flag composes with
        # anything before `--` in any position. Bounded by "$TIMEOUT_BIN"
        # ITSELF (D45/[TT-6]) on the emitted line, not merely by the
        # already-bounded pcrec_run call one level up in run_pc4.sh — K37's
        # static sweep (tests/codegen/run_codegen_tests.sh) reads THIS FILE's
        # own text, not the call graph, so the bound has to be visible right
        # here; $TIMEOUT_BIN is resolved (gen_timeout.sh, sourced above) and
        # written into the wrapper as a literal absolute path, same as $PCREC.
        WRAP="$WORKDIR/pcrec_premuldeny"
        cat > "$WRAP" <<EOF
#!/bin/sh
exec "$TIMEOUT_BIN" "$(pcrec_timeout_secs)" "$PCREC" -fno-premul-table "\$@"
EOF
        chmod +x "$WRAP"
        DENIEDOUT="$WORKDIR/pc4_denied.out"
        "$ROOT_DIR/scripts/watchdog" -l axes-pc4-denied -S axes -s 900 -- \
            env PCREC="$WRAP" CC="$CC" bash "$ROOT_DIR/tests/registry/run_pc4.sh" \
            > "$DENIEDOUT" 2>&1
        denied_rc=$?
        plain_fail="$(grep -oE 'FAIL: pc4: [0-9]+ ' "$PLAINOUT" | head -1)"
        plain_pop="$(grep -oE '[0-9]+ patterns, [0-9]+ refusals?, [0-9]+ accepted, [0-9]+ cells' "$PLAINOUT")"
        denied_pop="$(grep -oE '[0-9]+ patterns, [0-9]+ refusals?, [0-9]+ accepted, [0-9]+ cells' "$DENIEDOUT")"
        if [ "$plain_rc" -ne 0 ] || [ "$denied_rc" -ne 0 ]; then
            oracle_verdict="FAIL (plain_rc=$plain_rc denied_rc=$denied_rc — see $PLAINOUT / $DENIEDOUT)"
            fail=1
        else
            oracle_verdict="OK — both plain and -fno-premul-table PC-4 runs are 0-failure against live libpcre2"
        fi
        echo "  plain:   rc=$plain_rc"
        echo "  denied:  rc=$denied_rc"
        echo "  $oracle_verdict"
    fi
fi

# ============================================================================
# SUMMARY
# ============================================================================

t_end=$(date +%s)
echo
echo "== axes summary =="
for r in "${axis_results[@]}"; do
    echo "  $r"
done
echo "oracle cross-check: $oracle_verdict"
echo "--vm-entry-shape tier: $_shape_tier"
echo "total wall time: $((t_end - t_start))s"
if [ "$fail" -ne 0 ]; then
    echo "run_axes.sh: FAILED — see AXIS FAIL lines above" >&2
    exit 1
fi
# THE CLOSING SENTENCE NAMES THE TIER, because since [CC-DIFF] STEP 2 "all
# axes" is a claim whose SCOPE depends on AXES_FULL: a default run swept two
# of `--vm-entry-shape`'s four rungs, and a summary that read the same either
# way would let a two-rung result be quoted as a four-rung one.
echo "run_axes.sh: all axes answer-identical to default (documented refusal populations excepted); --vm-entry-shape tier: $_shape_tier; oracle cross-check $oracle_verdict"
exit 0
