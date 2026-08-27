#!/usr/bin/env bash
# tests/axes/run_axes.sh — [CHK-2] piece 2: THE ANSWER-IDENTITY SWEEP.
#
# docs/spec/tuning.md §2 documents THIRTEEN axes, and for eleven of the
# twelve BIT-FLAG members of the deny/force family (bits 4-15 of
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

# bit -> macro name, e.g. bits[4]=PCREC_NO_POSSESSIFY. Scoped to 4..15 (the
# deny/force family's own range — tuning.md §2's own bound) so a future
# unrelated `1u << N` in the header (there are several below bit 4, for
# PCREC_CASELESS etc.) is never swept in by accident.
declare -A bit_macro=()
while IFS=$'\t' read -r macro bit; do
    [ -n "$macro" ] || continue
    if [ "$bit" -ge 4 ] && [ "$bit" -le 15 ]; then
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
doc_bits="$(sed -n '/^## 2\. The thirteen axes/,/^## 3\./p' "$TUNING" \
    | grep -oE '\(bit [0-9]+\)' | grep -oE '[0-9]+' | LC_ALL=C sort -n -u)"
reg_bits="$(printf '%s\n' "${!bit_macro[@]}" | LC_ALL=C sort -n -u)"
if [ "$doc_bits" != "$reg_bits" ]; then
    echo "run_axes.sh: FATAL: tuning.md §2's documented bits and lib/pcrec.h's derived bits DISAGREE" >&2
    echo "  documented (tuning.md \"(bit N)\" mentions): $(echo "$doc_bits" | tr '\n' ' ')" >&2
    echo "  derived    (lib/pcrec.h 1u << N, bits 4-15): $(echo "$reg_bits" | tr '\n' ' ')" >&2
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
    local dump="$WORKDIR/axis_$(echo "$label" | tr -c 'A-Za-z0-9' '_').tsv"
    echo
    echo "axes: axis $label (RXTFLAGS=\"$flags\")..."
    local t0 t1
    t0=$(date +%s)
    "$ROOT_DIR/scripts/watchdog" -l "axes-$label" -S axes -s 3600 -- \
        env RXTFLAGS="$flags" RXTDUMP="$dump" PCREC="$PCREC" CC="$CC" \
            GENCFLAGS="$GENCFLAGS" PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" \
            bash "$ROOT_DIR/tests/harness/run.sh" "$@" > "$WORKDIR/axis.out" 2>"$WORKDIR/axis.err"
    local axis_rc=$?
    t1=$(date +%s)
    if [ ! -f "$dump" ]; then
        echo "AXIS FAIL: $label: run.sh produced NO dump at all (rc=$axis_rc) — see $WORKDIR/axis.err" >&2
        cat "$WORKDIR/axis.err" >&2
        fail=1
        axis_results+=("$label|FAIL|no-dump|$((t1 - t0))s")
        return
    fi
    local diffline
    diffline="$(awk -v BASEFILE="$BASE_DUMP" -f "$SCRIPT_DIR/dump_diff.awk" "$dump" 2>"$WORKDIR/diff.err")"
    cat "$WORKDIR/diff.err" >&2
    echo "  $diffline"
    local mismatches lost gained keys_base_n keys_axis_n
    mismatches="$(echo "$diffline" | grep -oE 'mismatches=[0-9]+' | cut -d= -f2)"
    lost="$(echo "$diffline" | grep -oE 'lost=[0-9]+' | cut -d= -f2)"
    gained="$(echo "$diffline" | grep -oE 'gained=[0-9]+' | cut -d= -f2)"
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
        echo "---- $WORKDIR/axis.out ----" >&2
        cat "$WORKDIR/axis.out" >&2
        echo "---- $WORKDIR/axis.err ----" >&2
        cat "$WORKDIR/axis.err" >&2
        echo "---- end harness output ----" >&2
        fail=1
        axis_results+=("$label|FAIL|harness-level:$diffline|$((t1 - t0))s")
        [ "$KEEP" = "1" ] || rm -f "$dump"
        return
    fi
    local verdict="OK"
    if [ "$mismatches" -gt 0 ] || [ "$gained" -gt 0 ] || { [ "$lost" -gt 0 ] && [ "$lost_is_ok" != "1" ]; }; then
        verdict="FAIL"
        fail=1
        echo "AXIS FAIL: $label: $mismatches mismatch(es), $lost lost ($([ "$lost_is_ok" = "1" ] && echo "documented refusal population, not counted against it" || echo "UNEXPECTED — not documented as do-or-die")), $gained gained" >&2
    elif [ "$lost" -gt 0 ]; then
        echo "  ($lost case(s) refused under this axis — documented do-or-die population, not a failure)"
    fi
    axis_results+=("$label|$verdict|$diffline|$((t1 - t0))s")
    [ "$KEEP" = "1" ] || rm -f "$dump"
}

for bit in $(printf '%s\n' "${!bit_macro[@]}" | LC_ALL=C sort -n); do
    macro="${bit_macro[$bit]}"
    flagtext="${macro_flag[$macro]}"
    label="$flagtext ($macro, bit $bit)"
    if [ -n "$AXES" ]; then
        case " $AXES " in (*" $flagtext "*) ;; (*) continue ;; esac
    fi
    lost_ok=0
    [ "$bit" = "$force_bit" ] && lost_ok=1
    run_one_axis "$label" "$flagtext" "$lost_ok" "$@"
done

# ============================================================================
# THE COARSE AXIS — §2.11, --engine=vm / --engine=dfa
# ============================================================================

if [ -z "$AXES" ] || printf '%s' "$AXES" | grep -q -- '--engine'; then
    run_one_axis "--engine=vm (§2.11)" "--engine=vm" "1" "$@"
    run_one_axis "--engine=dfa (§2.11)" "--engine=dfa" "1" "$@"
fi

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
echo "total wall time: $((t_end - t_start))s"
if [ "$fail" -ne 0 ]; then
    echo "run_axes.sh: FAILED — see AXIS FAIL lines above" >&2
    exit 1
fi
echo "run_axes.sh: all axes answer-identical to default (documented refusal populations excepted); oracle cross-check $oracle_verdict"
exit 0
