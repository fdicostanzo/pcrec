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
# reverse). Every one of the bit-flag axes (the COUNT is derived from
# lib/pcrec.h below and is deliberately not restated here -- it has grown at
# nearly every wave, and this line read "twelve" at twenty-four) is
# DENY-ONLY or FORCE-PAIR
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
# [OPT-DIAL] THE DIAL, AS A FIFTH KIND OF AXIS (docs/spec/tuning.md §5.5;
# docs/design/opt_dial_design.md §6.1). Four non-default `--tune=` positions
# (`-2`/`-1`/`1`/`2` — position `0`, `balanced`, is a structural no-op and
# needs no arm here) join the identical RXTFLAGS/RXTDUMP mechanism every
# other axis in this file uses. `lost_ok` is 0 on all four — the dial's own
# rule (tuning.md §5.5) is that NO position may refuse a pattern position 0
# compiles, so unlike `--engine=dfa`'s legitimate do-or-die refusals, any
# REFUSED case here is a real failure and this file carries no
# REFUSAL_PATTERN entry for any `--tune=` flag. That per-axis rule is
# necessary but not sufficient: **DIAL-S3**, a separate arm after the main
# job loop, compares the dial's REFUSED-key SETS across all five positions
# in both directions — a count-only comparison is the one shape that could
# miss two of this design's hazards (a lost answer, a gained one) moving
# past each other at once. See the job-list build and DIAL-S3's own header
# below for the full design citation.
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
#               empty (default) runs every bit-flag axis derived from
#               lib/pcrec.h (bits 4..31) plus both
#               engine directions plus the [OPT-DIAL] `--tune=` positions
#               (matched by the substring "--tune", same shape "--engine"/
#               "--vm-entry-shape" already use). For a QUICK check, not the
#               delivered run.
#   PCREC/CC/GENCFLAGS   forwarded to tests/harness/run.sh verbatim.
#   PROCS       forwarded to tests/harness/run.sh (default: tests/lib/
#               procs_default.sh's count — [CORPUS-PCAP] — matching
#               test-corpus's own default).
#   HARNESS_BATCH   ([TT-4M] STEP 2c/axbatch lane, 2026-09-10) forwarded to
#               EVERY tests/harness/run.sh invocation this script makes
#               (baseline AND every axis run) verbatim — default 0, today's
#               unbatched per-pattern path, byte-for-byte unchanged (the
#               same house rule this file's every other forwarded var
#               follows). Set to a positive N (2d's recommended N=64,
#               docs/dev/tt4m_step2a_parallel_sizing.md) to batch this
#               sweep's own corpus-compile pass too — INHERITED rather than
#               defaulted to 64 here, deliberately: this script does not
#               decide the axes stage's own batching policy, it only has to
#               carry whatever value the caller (a developer's quick check,
#               or scripts/battery.sh's axes stage) sets, same as PCREC/CC/
#               GENCFLAGS above. Baseline and axis dumps are compiled under
#               the IDENTICAL value (never split — an axis compiled batched
#               against an unbatched baseline would be comparing two
#               different compile shapes, not one optimization axis), so
#               there is exactly one place this is read.
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
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
. "$ROOT_DIR/tests/lib/procs_default.sh"   # [CORPUS-PCAP] perf-core count on darwin, else NCPU
PROCS="${PROCS:-$PROCS_DEFAULT}"
KEEP="${KEEP:-0}"
SKIP_ORACLE="${SKIP_ORACLE:-0}"
AXES="${AXES:-}"
# [TT-4M] STEP 2c / axbatch — see the header comment above for why this is
# INHERITED (default 0) rather than given its own axes-stage default here.
HARNESS_BATCH="${HARNESS_BATCH:-0}"

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
# are unrelated `PCREC_BIT(N)` constants in the same header (PCREC_CASELESS
# and friends) and must never be swept in, while the top of the deny/force
# family simply moves every time an axis is added. It was written as `4..15`
# — the family's extent on the day it was written — and [OPT-K]'s bit 16 was
# therefore DERIVED AWAY SILENTLY: the new axis would have been absent from
# the sweep with no failure, which is exactly the "an axis shipped without its
# five things" gap [CHK-2] exists to close, arriving through [CHK-2]'s own
# instrument. 63 is the width of the `uint64_t` `pcrec_options.flags` has always
# been, and since [OPT-REQPOS] widened the enum's spelling to `1ull << N`
# (itself since respelled `PCREC_BIT(N)` at [b2fix], 2026-09-23) it is also
# the width the CONSTANTS can name — so the bound needs no maintenance; the
# cross-check below catches a bit that has a constant and no doc heading either
# way. (It read 31 until 2026-09-22, when `PCREC_NO_REQ_RUN` took the last
# `1u <<` bit and the enum had to widen.)
declare -A bit_macro=()
while IFS=$'\t' read -r macro bit; do
    [ -n "$macro" ] || continue
    if [ "$bit" -ge 4 ] && [ "$bit" -le 63 ]; then
        bit_macro[$bit]="$macro"
    fi
# `PCREC_BIT(N)`: the flags enum is spelled through this macro since
# [b2fix] (2026-09-23), respelling [OPT-REQPOS]'s (2026-09-22) bare
# `1ull << N` — itself a widening from `1u << N`, because bit 31 is the
# last bit an `unsigned` constant can name. This extraction hard-fails on
# deriving ZERO bits below, which is what makes reading only the current
# spelling safe rather than sloppy — a tree still on the bare `1ull << N`
# or `1u << N` spelling fails LOUD here, not silently.
#
# TWO SHAPES: `NAME = PCREC_BIT(N)` (an enum member, bits 0-30) and
# `#define NAME PCREC_BIT(N)` (bit 31 on — PCREC_NO_REQ_RUN's own value
# numerically exceeds INT_MAX, which -Wpedantic refuses as an enumerator
# before C23, so [b2fix] pulled it out of the enum; every future bit will
# need the same #define shape for the identical reason). Both are read so
# this extraction keeps deriving every bit as that population grows.
done < <(grep -oE '(PCREC_(NO|FORCE)_[A-Z_]+ *= *PCREC_BIT\([0-9]+\))|(#define PCREC_(NO|FORCE)_[A-Z_]+ +PCREC_BIT\([0-9]+\))' "$ROOT_DIR/lib/pcrec.h" \
          | sed -E 's/^#define +//; s/ *= */ /' \
          | sed -E 's/^(PCREC_(NO|FORCE)_[A-Z_]+) +PCREC_BIT\(([0-9]+)\)$/\1\t\3/')

n_bits=${#bit_macro[@]}
if [ "$n_bits" -eq 0 ]; then
    echo "run_axes.sh: FATAL: derived ZERO deny/force bit constants from lib/pcrec.h — extraction is broken (docs/dev/learnings.md §3: hard-fail on empty, never silently measure nothing)" >&2
    exit 1
fi

# macro -> CLI flag spelling.
#
# [REVW.4] wave 4 (D111), 2026-09-19: THE AWK SCRAPER THAT STOOD HERE IS
# DELETED, not re-aimed. It rebuilt the pairing out of `cli/main.c`'s TEXT
# ("remember the most recently seen `strcmp(a, "-...")` literal, pair it with
# the next `opt.flags |= MACRO` line") and carried a fatal guard for the day
# "cli/main.c's loop shape changed" — which this wave IS: that loop no longer
# has twenty-two arms to scrape. `tests/registry/axes_registry_check.sh`
# carried an independent re-implementation of the identical pass and it is
# deleted there too.
#
# [MEMFN] R4a: pcrec's axis table is `--list-axes`' leading anonymous table;
# the kit's `memfn` section after it is not pcrec flags (its rows are
# `--memfn=` options), so the pipe SELECTS the main table (table_main,
# table_contract.md §4¶6) before reading any row.
# The pairing now comes off `pcrec --list-axes`, whose deny/force macro and
# `cli_flag` columns are rendered from `src/core/axes.def` — the same row
# `cli_axis_apply` parses. One derivation, read by the sweep instead of two
# hand-typed ones reconciled by awk.
#
# WHY READING THE DUMP IS NOT THIS CHECK SHARING A SOURCE WITH WHAT IT
# CHECKS. What this sweep asserts is ANSWER IDENTITY across axes: compile the
# corpus with a flag and without, and require the same answers. The flag
# spelling is how it ADDRESSES an axis, never what it measures — so taking
# the spelling from the same table the parser uses makes the sweep reach the
# axis it names, which is exactly the property the old guard below was
# protecting. What the dump cannot tell it is whether the parser ACCEPTS the
# spelling; that is driven live by axes_registry_check.sh's own
# `check_cli_flag_accepted`.
declare -A macro_flag=()
while IFS=$'\t' read -r macro flagtext; do
    [ -n "$macro" ] && [ -n "$flagtext" ] && macro_flag[$macro]="$flagtext"
done < <("$TIMEOUT_BIN" 60 "$PCREC" --list-axes \
          | bash "$ROOT_DIR/tests/lib/table.sh" table-main - \
          | grep -v '^#' \
          | awk -F'\t' 'NF > 10 {
                split($11, f, " / ")
                # [OPT-LITSCAN] S1: a multi-bit deny cell is `|`-joined in
                # lockstep across the macro and flag columns (the run-pinned
                # rows carry two bits) -- pair each half with its own flag.
                if ($7  != "" && f[1] != "" && f[1] !~ /^--/) {
                    nm = split($7, dm, "|"); nf = split(f[1], df, "|")
                    for (i = 1; i <= nm && i <= nf; i++) print dm[i] "\t" df[i]
                }
                if ($9  != "" && f[2] != "") print $9 "\t" f[2]
                else if ($9 != "" && $7 == "" && f[1] != "") print $9 "\t" f[1]
            }')

if [ "${#macro_flag[@]}" -eq 0 ]; then
    echo "run_axes.sh: FATAL: derived ZERO macro->flag pairs from --list-axes -- the dump's deny/force/cli_flag columns moved, or the dump failed (docs/dev/learnings.md §3: hard-fail on empty, never silently measure nothing)" >&2
    exit 1
fi

# Sanity: every derived bit macro must have a derived CLI spelling, or the
# dump names a bit it gives no way to address -- a silent empty flag would
# compile the DEFAULT pattern under every "axis", comparing default against
# default and reporting perfect agreement on every one, the exact "measures
# nothing" failure mode this family's own suites (run_possdiff.sh et al.)
# guard against. KEPT, and it is the arm that now watches the SEAM between
# lib/pcrec.h's bits and axes.def's rows: a macro declared in the header and
# absent from the table reaches this loop with no spelling.
for bit in "${!bit_macro[@]}"; do
    macro="${bit_macro[$bit]}"
    if [ -z "${macro_flag[$macro]:-}" ]; then
        echo "run_axes.sh: FATAL: $macro (bit $bit) is declared in lib/pcrec.h but --list-axes reports no CLI spelling for it — it has no src/core/axes.def row, or no candidate row carries its bit; a wrong sweep would silently compare default against default" >&2
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
    echo "  derived    (lib/pcrec.h PCREC_BIT(N), bits 4-63): $(echo "$reg_bits" | tr '\n' ' ')" >&2
    echo "  a bit in one column and not the other means a new axis shipped with no" >&2
    echo "  doc heading, or a heading survived its axis's removal" >&2
    exit 1
fi
echo "axes: registry derived — $n_bits bit-flag axes (bits ${reg_bits//$'\n'/,}), matching tuning.md §2's own $(echo "$doc_bits" | wc -l) documented bit mentions"

# which bit is the one DO-OR-DIE member (tuning.md §2.5: PCREC_FORCE_PREFILTER
# refuses on a pure-DFA-selected pattern), so that ITS refusals are a
# documented population rather than a failure.
#
# [EMIT-VERB] 2026-09-19 — NARROWED FROM A NAME-PREFIX SWEEP, and the old
# comment's claim that "a second FORCE_ member added later is picked up the
# same way without an edit here" was the defect rather than the feature.
# DO-OR-DIE IS A PROPERTY OF THE AXIS, NOT OF THE `FORCE_` SPELLING:
# `-fprefilter` refuses; `-fprefilter-collapse` explicitly does NOT
# (src/core/axes.def states why — the collapsed language of a pattern with
# nothing to collapse IS its exact language), and `-fcomments` cannot refuse
# anything at all. The loop assigned the LAST match in bash's associative
# iteration order, which is not sorted, so with two FORCE_ macros it was
# already picking one of two arbitrarily and a third made the coin three-
# sided. The failure is silent in both directions: bit 9's genuine documented
# refusals would FAIL the sweep, and whichever bit won the toss would get an
# exemption it never needs.
#
# Named, with its reason, and asserted present so a rename is loud.
force_bit=""
for bit in "${!bit_macro[@]}"; do
    [ "${bit_macro[$bit]}" = "PCREC_FORCE_PREFILTER" ] && force_bit="$bit"
done
if [ -z "$force_bit" ]; then
    echo "run_axes.sh: FATAL: PCREC_FORCE_PREFILTER is not among the derived bits — the ONE do-or-die axis (tuning.md §2.5) has been renamed or removed, and without it that axis's documented refusals would be reported as failures" >&2
    exit 1
fi

# ============================================================================
# THE DOCUMENTED-REFUSAL LOOKUP (manager's classification rule, 2026-08-26,
# from the first full-corpus sweep's own findings). A REFUSED case (pcrec
# itself declined to compile the pattern under this axis) is counted as
# REFUSED-DOCUMENTED — a population, floored (K35), never a failure — ONLY
# when its diagnostic TEXT contains the axis's own documented limit
# substring, verified live against the shipped diagnostics below (never
# hand-guessed): src/gen/emit_vm.c's replication-cap pcrec_ctx_fail
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
REFUSAL_DELIM=$'\x1f'   # joins multiple documented substrings per axis; an
                        # axis can have more than one distinct diagnostic
                        # [MACPORT] \x1f (US), not \x01 (SOH): verified live
                        # that bash 3.2's own `read -a` (like plain `read`,
                        # see tests/registry/axes_registry_check.sh's own
                        # note) does not split on IFS=$'\x01' at all — the
                        # whole string lands in element 0 — while bash 4+/5+
                        # splits it correctly. \x1f splits identically on
                        # both versions.
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
    # SIXTH shape, [axtri] (2026-09-30, triaging the Linux final `make
    # test-axes` of main d6cb0bb4, abi 49): the forced prefilter's byte DFA
    # is charged against the emitted-BYTES cap (limits.md §8), so a
    # `engine vm` pattern that fits without it can overflow with it —
    # tests/utf8/wclass_illformed.rxt's `\p{Xwd}` cells under `-e utf8`
    # (bare 1,013,468 and captured 1,013,932 bytes against the 1,000,000
    # cap; 32 cases, that one file, the same two patterns that file's line
    # 219 comment records as refused at default when captured on the auto
    # route). It is the do-or-die posture, not a defect: §2.5/§2.17 state
    # that `-fprefilter` is never silently dropped and makes the size-ladder
    # rungs that would undo it (the D135 drop-the-prefilter rung included)
    # ineligible, so the size cap refuses with its own text. Verified live
    # with `build/pcrec -p rx -e utf8 --features all --engine=vm -fprefilter
    # --pattern 'x\p{Xwd}y'`, and against lane/pfdrop's compiler, which
    # refuses identically with and without --size-cap=refuse. The substring is
    # the emitted-C-source cap's own wording (the code-bytes cap reads
    # "bytes of emitted code", which this axis does not reach), and the
    # existing 12,000 floor is unaffected (K35: 32 cases on one file is not
    # a corpus-wide measurement).
    ["-fprefilter"]="-fprefilter requires the VM engine${REFUSAL_DELIM}cannot be honoured for a pattern containing a${REFUSAL_DELIM}cannot both be requested${REFUSAL_DELIM}pattern too complex for the DFA engine${REFUSAL_DELIM}pattern too large (NFA exceeds${REFUSAL_DELIM}bytes of emitted C source (limit"
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
    # FOURTH shape, [axtriage] (2026-09-19, triaging adm71's own new
    # corpus file): the zero-population "third documented DFA limit"
    # named above at 2026-09-03 — src/ir/dfa.c's OWN "pattern too complex
    # for the DFA engine" state-count/subset-construction ceiling, as
    # opposed to the NFA-build cap the THIRD shape reaches through a
    # different door — now has a measured population too, through its OWN
    # door this time: tests/base/opt41_rung_nullable_decline.rxt's
    # `(?:ab){0,16000}` (adm71, e021b982) is BUILT to overflow
    # `PCREC_MAX_DFA_STATES_TABLE` (32000 states, src/core/limits.def) so
    # `--engine=auto` is offered and declines the [SEL-1] collapse rung;
    # under `auto` the overflow is a selection outcome (tuning.md
    # [SEL-1]) and answers correctly via the VM fallback, but forcing
    # `--engine=dfa` has no fallback and refuses with src/ir/dfa.c:954's
    # do-or-die diagnostic ("pattern too complex for the DFA engine (>32000
    # states; try --engine=vm)") — exactly the do-or-die posture tuning.md
    # §2.11/[SEL-1] documents ("--engine=dfa ... still refuse[s] with
    # today's diagnostic"). Verified live (`build/pcrec -p rx
    # --engine=dfa -o - -- '(?:ab){0,16000}'` prints that text) and by
    # this axis's own run: RED before this substring existed (6 undocumented
    # refusals, opt41_rung_nullable_decline.rxt:41-46, one per expectation
    # line on the single `pattern` case), green after. Substring shared
    # verbatim with -fprefilter's fourth shape above (both name the
    # generic "pattern too complex for the DFA engine" prefix, which
    # covers dfa.c's sibling subset-construction message too, by the same
    # "generic format-string prefix, not a per-site list" reasoning the
    # VM_ONLY branch above already uses). No floor raised (K35; 6 cases
    # on one file is not a corpus-wide measurement, and the existing 8000
    # floor is unaffected — it undercounts the true documented population
    # already, per the two prior additions' own notes).
    ["--engine=dfa"]="requires the VM engine${REFUSAL_DELIM}requires captures (on by default)${REFUSAL_DELIM}pattern too large (NFA exceeds${REFUSAL_DELIM}pattern too complex for the DFA engine"
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
    # `-fno-cls-kit` ([axtri], 2026-09-30): denying the class-matcher kit
    # returns every wide class on the VM to the byte alternation this
    # compiler emitted before abi 48 (tuning.md §2.33), so the K55 refusal
    # the kit retired comes back BY DESIGN on the same population: a
    # `\p{Xwd}` at `-e utf8` under `engine vm` is 576,773 bytes (captured
    # 577,122) of emitted code against the 500,000-byte code cap, and
    # `\P{Unknown}` 526,899. Measured (Linux final run of main d6cb0bb4 and
    # a local single-file run agree): 77 cases, five blocks of
    # tests/utf8/wclass_illformed.rxt (one block, the capturing `\P{Unknown}`,
    # is default-route: the VM is selected there), all with this diagnostic, the same
    # substring as `-fno-size-term`'s entry above. With the kit on those
    # artifacts are ~31 KB. Nothing rescues them: `engine vm` has no
    # prefilter for lane/pfdrop's D135 drop rung to drop (its compiler
    # refuses identically). The floor is a measured number rounded down
    # (K35), so a change that stops the byte alternation being reached is
    # caught rather than read as "fewer refusals".
    # NOT documented here, deliberately: the OTHER 32 cases of the 109
    # (`x(\p{L})y`, `x(\P{L})y` on the default route, "bytes of emitted C
    # source (limit 1000000": 1,179,060 / 1,153,832) are the size-CAP
    # ladder's, not the kit axis's. Their bytes are the hybrid prefilter's
    # byte alternation, and D135's drop-the-prefilter rung (lane/pfdrop)
    # rescues them (measured: 430,907 / 413,437 bytes, `RX_VM_PREFILTER
    # "none"`, answers unchanged) — so they clear when that lane merges and
    # a substring for them would go vacuous the same day. Until then
    # `-fno-cls-kit` reads red on exactly those 32.
    ["-fno-cls-kit"]="bytes of emitted code (limit"
    # K55 RETIRED ([CLS-TREE] S4, abi 48): `--engine=vm` carried ONE entry
    # here, "bytes of emitted code (limit", for `\P{Unknown}` under
    # `-e utf8` (tests/utf8/axis12_scripts.rxt), whose VM body was a
    # 689,367-byte byte alternation against the 500,000-byte code cap. The
    # VM now tests a wide class with one decode and a class-matcher kit
    # function (tuning.md §2.33), the artifact is ~30 KB, and the entry is
    # DELETED rather than kept: a documented-refusal substring nothing
    # reaches would read green on a regression that brought the refusal
    # back. The refusal-set move is recorded as the identity break it is in
    # docs/dev/lanes/s4build_report.md.
)
declare -A REFUSAL_FLOOR=(
    ["-fno-counter"]=180
    ["-fprefilter"]=12000
    ["--engine=dfa"]=8000
    ["-fno-cls-kit"]=60
)

# ============================================================================
# GIVEUP1_ALLOWANCE — [chkgaps] 2026-09-25's check-design close-out
# (docs/dev/learnings.md §3: "count answer->give-up TRANSITIONS as their own
# population"; K64's own check-gap note, docs/dev/lanes/k64fix_report.md
# §"Check gaps"). A GIVEUP1 case (dump_diff.awk: exactly one side gives up
# or times out, the other reports a real answer) is a FAILURE unless this
# axis names the EXACT case here, keyed "<flags>|<file:line>" — a COUNT
# ceiling would disarm itself the moment a different case moved into it
# (K35, the REFUSAL_PATTERN/REFUSAL_FLOOR precedent two tables up), so this
# is a manifest, never a number.
#
# POPULATED 2026-09-26 (lane giveupallow), the first real population this
# manifest has ever held: the four groups the 27a63314 full-corpus run's own
# triage (/tmp/pcrec_axestriage/verdict.md) ruled (b) "documented
# budget-boundary effect" — 52 cases total, 0 wrong answers among them. Every
# key below is a LIVE MEASUREMENT (2026-09-26, single-file/single-axis
# `tests/harness/run.sh` + `dump_diff.awk` re-runs), never a guess from the
# verdict's own capped log sample. `keys_base=N keys_axis=N ... giveup1=M`
# matched the triage's stated count on all four groups (45/2/3/2).
#
# THE KEY IS $ROOT_DIR-RELATIVE, same day, same lane, same-branch fix. The
# first landing of this manifest keyed on the RAW value of `$key`
# (dump_diff.awk's `$1:$2`), which on a full-corpus run is
# `$ROOT_DIR`-ABSOLUTE (`tests/harness/run.sh` discovers files via `find
# "$ROOT_DIR/tests" ...`) — tying every entry to THIS checkout's own
# absolute path. `run_one_axis`'s lookup now strips `"$ROOT_DIR"/` off
# `$key` before indexing (the identical no-op-when-already-relative idiom
# `tests/harness/run.sh`'s own `SIZELOG` row key already uses), and every
# entry below is written relative (`tests/base/...`), so the manifest
# survives a different checkout root unchanged.
#
declare -A GIVEUP1_ALLOWANCE=(
# GROUP A — bit 7, `-fno-length-prune` (PCREC_NO_LENGTH_PRUNE), 45 cases, all
# tests/base/d27_k23_ambiguous_decomposition.rxt (the D27 blinded corpus for
# `(a{1,3}){65}`). Direction: DEFAULT answers a real match (MRL pruning
# intact), denied axis gives up (steps). MRL pruning IS the K23 fix
# (tuning.md §2.4: "Denies MINIMUM-REMAINING-LENGTH (MRL) pruning ... a
# denied artifact is claimed byte-for-byte the emitter's own pre-MRL
# output"). k23_design.md §9.1 is the step-count curve this denial reopens —
# "the bound is measured to the SUBJECT END", pruning's own break-even is a
# MEASURED 16-byte trailing suffix past which the UNPRUNED step count grows
# combinatorially (1 step pruned vs. 1,153,352 unpruned at t=16 on the
# note's own exemplar) — exactly the ambiguous-decomposition band this
# file's own header says it exists to hit. §14.5 names THIS FILE as K23's
# own independent D27 blinded corpus (89/89 against the MRL build). A
# one-sided give-up denying MRL on this band is the documented
# budget-boundary effect the mechanism exists to have, not a regression —
# tests/mrl/run_mrldiff.sh's own 22-cell answer-more asymmetry exemption is
# this same shape one axis over (deny MRL entirely vs. deny it on one
# engine). Verified live 2026-09-26 (single-file baseline vs.
# `RXTFLAGS="-fno-length-prune"`, this file alone): keys_base=89 keys_
# axis=89 agree=44 budget=0 giveup1=45 mismatches=0 — the exact count and
# shape (0 mismatches, 0 lost, 0 gained) the triage measured; the 45 keys
# below are dump_diff.awk's own ROWSFILE for that run, not a re-derivation.
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:22"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:23"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:24"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:25"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:26"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:27"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:28"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:29"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:30"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:31"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:32"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:33"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:34"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:35"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:36"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:37"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:38"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:39"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:40"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:41"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:42"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:43"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:44"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:45"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:46"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:47"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:48"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:49"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:50"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:51"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:52"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:53"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:54"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:55"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:56"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:57"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:60"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:61"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:62"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:63"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:64"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:65"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:90"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:105"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"
    ["-fno-length-prune|tests/base/d27_k23_ambiguous_decomposition.rxt:118"]="K23/MRL band (tuning.md §2.4, k23_design.md §9.1/§14.5): default matches with MRL pruning intact, -fno-length-prune reverts to the pre-MRL emitter and gives up (steps) inside the documented ambiguous-decomposition band"

# GROUP B — bit 8, `-fno-prefilter` (PCREC_NO_PREFILTER), 2 cases, the SAME
# file's lines 90 and 98. Direction: DEFAULT (hybrid DFA prefilter ahead of
# the VM) answers a real match, denied axis gives up (steps): losing the
# sharp reverse-window start. tuning.md §2.5's own witness is the identical
# mechanism, one pattern over: "((a)|bc){0,4000}d over 1 MB of `a` is `no
# match` with the hybrid's DFA prefilter and PCREC_ERR_WORK without it. A
# sweep that compares answers across this axis must classify a give-up on
# either side as budget-bound..., not as a disagreement" — GIVEUP1 is
# exactly that classification, now split from BUDGET because only ONE side
# gives up here. §2.17's "fourth cost" names THIS FILE's OWN PATTERN as its
# worked example, verbatim: "`(a{1,3}){65}` on a long run of `a`s answers
# `0,100 90,100` in 0.00 s with the exact prefilter and returns
# PCREC_ERR_STEPS after 13.34 s with the collapsed one. Answer identity is
# preserved in D46's unbounded sense — and `make test-axes` is right to keep
# passing — but the step budget is a documented caller-visible bound
# (DD-2/D22)." `-fno-prefilter` denies the SAME sharp start the collapsed
# language in §2.17 loses a cheaper way; both land on these same two lines.
# Verified live 2026-09-26 (this file alone, RXTFLAGS="-fno-prefilter"):
# keys_base=89 keys_axis=89 agree=87 budget=0 giveup1=2 mismatches=0 —
# exactly the triage's count; both keys below are default=match/axis=steps.
    ["-fno-prefilter|tests/base/d27_k23_ambiguous_decomposition.rxt:90"]="tuning.md §2.5/§2.17 (the fourth cost's own worked example is this file's pattern): losing the sharp prefilter-window start turns a 0.00s match into a step give-up — default matches, -fno-prefilter gives up (steps)"
    ["-fno-prefilter|tests/base/d27_k23_ambiguous_decomposition.rxt:98"]="tuning.md §2.5/§2.17 (the fourth cost's own worked example is this file's pattern): losing the sharp prefilter-window start turns a 0.00s match into a step give-up — default matches, -fno-prefilter gives up (steps)"

# GROUP C — bit 9, `-fprefilter` (PCREC_FORCE_PREFILTER), 3 cases,
# REVERSED direction: DEFAULT gives up (steps/frames), the FORCED axis
# answers a real nomatch — forcing the hybrid prefilter proves no-match
# before the VM's own catastrophic-backtracking cost is ever paid.
# tests/harness/giveup.rxt:52 (`(a*)*[bc]`, `gu steps`) and :57
# (`((a)|b)*[cd]`, `gu frames`) are this suite's own dedicated give-up
# witnesses (chosen so `-freq-byte` — [OPT-REQBYTE] — declines for the WHOLE
# pattern regardless of axis flags, per that file's own header, so the
# prefilter axis is what is actually on trial here); tests/base/
# k64_precheck_forced_vm.rxt:39 is K64's own `gu steps` CONTROL cell,
# `^([a-zA-Z0-9._%+-]+)+@` on a run with no terminating `@` — built so the
# budget genuinely reaches the VM's exponential backtrack. tuning.md §2.5:
# "Identity is modulo WHICH BUDGET BINDS. The prefilter changes how much
# WORK a search does before it answers, never the answer — but a give-up
# is a bound on work, so on a subject that sits near a budget the two
# builds can differ by a GIVE-UP CODE where neither is wrong" — the same
# rule as Group B, opposite direction, because forcing the prefilter ON
# where the default did not build one buys the same work reduction Group
# B's denial takes away. Verified live 2026-09-26 (giveup.rxt +
# k64_precheck_forced_vm.rxt together, RXTFLAGS="-fprefilter"):
# keys_base=11 keys_axis=11 agree=8 budget=0 giveup1=3 mismatches=0 —
# exactly the triage's count; all three keys below are
# default=steps|frames/axis=nomatch.
    ["-fprefilter|tests/harness/giveup.rxt:52"]="tuning.md §2.5, reversed direction: forcing the hybrid prefilter proves no-match before the VM's catastrophic-backtracking cost is paid — default gives up (steps), -fprefilter answers nomatch"
    ["-fprefilter|tests/harness/giveup.rxt:57"]="tuning.md §2.5, reversed direction: forcing the hybrid prefilter proves no-match before the VM's catastrophic-backtracking cost is paid — default gives up (frames), -fprefilter answers nomatch"
    ["-fprefilter|tests/base/k64_precheck_forced_vm.rxt:39"]="tuning.md §2.5, reversed direction: forcing the hybrid prefilter proves no-match before the VM's catastrophic-backtracking cost is paid (K64's own gu-steps control cell) — default gives up (steps), -fprefilter answers nomatch"

# GROUP D — bit 20, `-fprefilter-collapse` (PCREC_FORCE_PREFILTER_COLLAPSE),
# 2 cases, the SAME file/lines as Group B (90, 98), SAME direction (default
# matches, axis gives up (steps)). tuning.md §2.5 for the give-up/budget
# rule (identical citation to Group B); §2.17 is this flag's OWN section,
# and its "fourth cost" paragraph is this exact file's exact pattern quoted
# above verbatim under Group B — forcing the count-collapsed prefilter
# LANGUAGE on `(a{1,3}){65}` reaches the identical lost-ceiling mechanism
# `-fno-prefilter` reaches by removing the prefilter outright: "the lost
# prefilter-window ceiling does not only make matching slower: it changes
# which patterns fit inside a step budget... `(a{1,3}){65}` on a long run
# of `a`s answers `0,100 90,100` in 0.00 s with the exact prefilter and
# returns PCREC_ERR_STEPS after 13.34 s with the collapsed one." Verified
# live 2026-09-26 (this file alone, RXTFLAGS="-fprefilter-collapse"):
# keys_base=89 keys_axis=89 agree=87 budget=0 giveup1=2 mismatches=0 —
# exactly the triage's count; both keys below are default=match/axis=steps.
    ["-fprefilter-collapse|tests/base/d27_k23_ambiguous_decomposition.rxt:90"]="tuning.md §2.5/§2.17 (the fourth cost's own worked example is this file's pattern): the count-collapsed prefilter language loses the same sharp ceiling as no prefilter at all — default matches, -fprefilter-collapse gives up (steps)"
    ["-fprefilter-collapse|tests/base/d27_k23_ambiguous_decomposition.rxt:98"]="tuning.md §2.5/§2.17 (the fourth cost's own worked example is this file's pattern): the count-collapsed prefilter language loses the same sharp ceiling as no prefilter at all — default matches, -fprefilter-collapse gives up (steps)"

# GROUP E — bit 30, `-fno-req-byte` (PCREC_NO_REQ_BYTE), 45 cases across
# FOUR witness files/mechanisms, not just the two the flag's own name
# suggests. tuning.md §2.30¶3: "`-fno-req-run` and `-fno-req-byte` remove the
# run itself, so nothing is pinned under either" — denying req-byte removes
# BOTH the byte pre-check AND the run pre-check it carries, so it reaches
# every mechanism either one alone can reach. Verified live 2026-09-26
# (single-axis `tests/axes/run_axes.sh` re-runs, scoped per sub-group below,
# KEEP=1 rowsfiles read directly for the exact key list — the capped
# stderr detail in the original full-corpus run only ever showed 20 of
# these per bucket, tests/axes/dump_diff.awk's own documented cap, which is
# why a first pass at this manifest from that capped log alone would have
# missed 25 of the 45): 18+12+4+11 = 45, matching the full-corpus
# giveup1-unallowed=45 exactly. E5 (19, below) added 2026-10-07: 64.
#
# E1 (18 cases) — tests/base/k65_precheck_whole_set.rxt, K65 (tuning.md
# §2.29, known_issues.md K65). `(x?)([a-z]+)+Z.@\1` / `(x?)([a-z]+)+
# eeeeeeee~#~#~#~#\1` (backrefs): on the no-DFA-scan VM route the emitted
# pre-check tests the WHOLE necessary set, the call's only linear no-match
# proof; -fno-req-byte reads RX_REQ_BYTE "none" and removes it, and the
# same subject exhausts the file's own `budget steps=10000` ceiling —
# default proves nomatch via one `memchr`, axis gives up (steps). Repro
# verified live: default RX_REQ_WHY "emitted", nomatch; -fno-req-byte
# RX_REQ_BYTE "none", exit 3 "steps", same subject
# ("aaaaaaaaaaaaaaaaZb"). Live re-run (this file alone,
# RXTFLAGS="-fno-req-byte"): keys_base=40 giveup1=18 (of the file's 30
# total — the other 12 are k66's own cells, sharing this file's pattern
# family, see E2) — the 18 keys below are that run's own ROWSFILE, not a
# re-derivation from the capped log.
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:35"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:36"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:37"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:38"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:39"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:40"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:48"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:49"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:50"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:51"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:52"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:53"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:61"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:62"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:63"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:64"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:65"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k65_precheck_whole_set.rxt:66"]="K65 (tuning.md §2.29, known_issues.md K65): the whole-necessary-set pre-check is the VM route's only linear no-match proof; -fno-req-byte removes it (RX_REQ_BYTE none) and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"

# E2 (12 cases) — tests/base/k66_precheck_whole_run.rxt, K66 (tuning.md
# §2.29, known_issues.md K66). Same pattern family, necessary RUN longer
# than its 8-byte window: §2.638 ("`-fno-req-run` and `-fno-req-byte`
# remove the run itself, so nothing is pinned under either") is why denying
# req-byte alone reaches every one of K66's own cells too, not only K65's.
# Live re-run (this file alone, RXTFLAGS="-fno-req-byte"): keys_base=16
# giveup1=12 — all 12 of the file's own cells, exact match to the
# dedicated -fno-req-run re-run below (F).
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:38"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:39"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:40"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:41"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:42"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:43"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:51"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:52"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:53"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:54"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:55"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k66_precheck_whole_run.rxt:56"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-byte removes the run pre-check along with the byte one it rides on — default proves nomatch, axis gives up (steps)"

# E3 (4 cases) — tests/base/k64_precheck_forced_vm.rxt, K64 (tuning.md
# §2.29 G2, known_issues.md K64). `^([a-zA-Z0-9._%+-]+)+@`, forced
# --engine=vm, framed/unguarded (RX_VM_PREFILTER "none"): the emitted
# pre-check is this one-attempt VM route's ONLY linear no-match proof, per
# G2's own linearity condition; -fno-req-byte removes it and the same
# subject (repro: "aaaaaaaaaaaaaaaa") exhausts the file's own `budget
# steps=10000`. Repro verified live: default nomatch after one memchr,
# -fno-req-byte exit 3 "steps". Live re-run (this file alone,
# RXTFLAGS="-fno-req-byte"): keys_base=11 giveup1=4 (the `gu steps`
# control cell at line 39 is unaffected — both sides already give up
# there, K64's own proof the budget genuinely reaches the VM).
    ["-fno-req-byte|tests/base/k64_precheck_forced_vm.rxt:34"]="K64 (tuning.md §2.29 G2, known_issues.md K64): the emitted pre-check is the forced-VM one-attempt route's only linear no-match proof; -fno-req-byte removes it and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k64_precheck_forced_vm.rxt:35"]="K64 (tuning.md §2.29 G2, known_issues.md K64): the emitted pre-check is the forced-VM one-attempt route's only linear no-match proof; -fno-req-byte removes it and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k64_precheck_forced_vm.rxt:36"]="K64 (tuning.md §2.29 G2, known_issues.md K64): the emitted pre-check is the forced-VM one-attempt route's only linear no-match proof; -fno-req-byte removes it and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"
    ["-fno-req-byte|tests/base/k64_precheck_forced_vm.rxt:37"]="K64 (tuning.md §2.29 G2, known_issues.md K64): the emitted pre-check is the forced-VM one-attempt route's only linear no-match proof; -fno-req-byte removes it and the subject exhausts the file's own step budget — default proves nomatch, axis gives up (steps)"

# E4 (11 cases) — tests/recursion/d27/sr_depth.rxt, K34 (known_issues.md
# K34, CLOSED [OPTLOOP.1.impl] batch 2) — a DIFFERENT known issue than
# K64/K65/K66 but the SAME general mechanism (§2.29's necessary-run
# pre-check, [OPT-REQPOS] tier 2b), applied to LEFT-RECURSION rather than
# backreferences: this file's own header/inline comments say so directly
# — "pcrec used to GIVE UP (frames) on every nomatch case below instead of
# concluding. It concludes now via the necessary-run precheck ([OPT-REQPOS]
# tier 2b)". `-fno-req-byte` removes that precheck and REOPENS K34's own
# give-up shape on the left-recursive `(a|(?1)a)` / `(a|(?1)a)b` /
# `(a|(?1)a)c` nomatch cells — default proves nomatch, axis gives up
# (frames), not steps (the recursion module's own give-up code, distinct
# from K64/65/66's backref-route `steps`). Found by a targeted re-run after
# E1-E3's 34 fell 11 short of the full-corpus giveup1=45; the population is
# NOT limited to the three K64/65/66 files by the flag's own name — always
# derive from a live re-run, never assume a mechanism's file list is
# closed (docs/dev/learnings.md §3). Live re-run (this file +3 other
# `gu`-bearing recursion files ruled out as unaffected, RXTFLAGS="-fno-req-byte"):
# keys_base=109 giveup1=11, all in sr_depth.rxt.
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:83"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:157"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:158"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:159"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:160"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:161"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:179"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:180"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:181"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:182"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"
    ["-fno-req-byte|tests/recursion/d27/sr_depth.rxt:183"]="K34 (known_issues.md K34, CLOSED via the same §2.29 necessary-run precheck [OPT-REQPOS] tier 2b): -fno-req-byte removes it and reopens K34's own give-up on this left-recursive nomatch cell — default proves nomatch, axis gives up (frames)"

# E5 (19 cases) — tests/litscan/reqcube.rxt, the [OPT-LITSCAN] S4 C3 /
# [K82] S2b and S2c blocks (landed 2026-10-03/04, AFTER this manifest was
# populated — the full AXES_FULL=1 HARNESS_BATCH=64 run at 041e450a was the
# first to reach them; lane axtri, docs/dev/lanes/axtri_report.md). E1's
# mechanism EXACTLY: `(x?)([a-z]+)+S\d(?i:select)\1` and
# `(x?)([a-z]+)+S\d(?i:s)qz\1` are K65's backref family, and those blocks'
# own comments say the n cells exist to turn into step give-ups when K65's
# whole-set memchr of 'S' is lost (S451/S452). -fno-req-byte loses it the
# blunt way (RX_REQ_BYTE/RX_REQ_RUN/RX_REQ_WHY all "none"). Measured live
# (axtri, --emit-main, the select pattern): default answers nomatch at
# --step-budget=10, i.e. by the pre-check alone; the axis needs > 10,000
# and <= 100,000 steps on the 16-a subject and > 100,000 on the 18-a one,
# and answers nomatch at 1,000,000 — the SAME answer once the budget
# covers it, so a budget transition, not a wrong answer. Four blocks
# (byte/utf8 x default/vm engine) x three n cells for S2b, two blocks for
# S2c, plus line 509 — the `# pcre2-only` L=30 review witness with no
# budget directive, which exhausts the DEFAULT step budget under the axis
# (2.9 s, `steps`) where the default memchr answers in ~0.
    ["-fno-req-byte|tests/litscan/reqcube.rxt:438"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:439"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:440"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:450"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:451"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:452"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:461"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:462"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:463"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:473"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:474"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:475"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:484"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:485"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:486"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:497"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:498"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:499"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"
    ["-fno-req-byte|tests/litscan/reqcube.rxt:509"]="K65 shape ([OPT-LITSCAN] S4 C3 / [K82] S2b-S2c witness, tuning.md §2.29): -fno-req-byte removes the whole-necessary-set memchr of 'S' (RX_REQ_BYTE none), the block's only linear no-match proof — default proves nomatch, axis gives up (steps); same nomatch once the budget covers it"

# GROUP F — bit 31, `-fno-req-run` (PCREC_NO_REQ_RUN), 12 cases, all
# tests/base/k66_precheck_whole_run.rxt (K66, tuning.md §2.29, known_
# issues.md K66) — the NARROWER flag: unlike Group E, this one leaves the
# byte pre-check standing (tuning.md §2.28¶2: "Denying `-fno-req-run` alone
# leaves the one-byte check standing"), so it reaches ONLY the cells whose
# no-match proof depends on the whole-RUN compare specifically, none of
# K65's or K64's or K34's. Verified live 2026-09-26 (this file alone,
# RXTFLAGS="-fno-req-run"): keys_base=16 giveup1=12 — exact match to the
# full-corpus giveup1-unallowed=12; the 12 keys below are that run's own
# ROWSFILE, identical set to Group E2 above (same file, same direction,
# different flag).
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:38"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:39"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:40"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:41"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:42"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:43"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:51"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:52"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:53"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:54"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:55"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"
    ["-fno-req-run|tests/base/k66_precheck_whole_run.rxt:56"]="K66 (tuning.md §2.29 & §2.28¶2, known_issues.md K66): -fno-req-run removes the whole-run compare and leaves only the byte pick, which this subject's window does not cover — default proves nomatch, axis gives up (steps)"

# GROUP F2 — bit 44, `-fno-req-run-fold` (PCREC_NO_REQ_RUN_FOLD, [OPT-LITSCAN]
# S4 C3, litscan_s4.md §4 r2 R2-C6): the cells where denying the caseless
# necessary run takes a masked run's no-match proof away and the axis gives
# up where the default answers NOMATCH (K66's shape, one fold narrower).
# EMPTY, and measured rather than assumed: lane c3build (2026-10-03) ran
# SKIP_ORACLE=1 AXES="-fno-req-run-fold" over the 17 .rxt files that carry
# one of the C3 mover manifest's 29 corpus patterns (the only files the
# axis can move; docs/dev/optloop/s4/c3_movers.log) -- keys_base=2434
# agree=2434 giveup1=0 lost=0 mismatches=0. The structural reason: the
# denied walk keeps every EXACT byte of the run as a necessary-set member,
# and on the no-DFA-scan route K65's whole-set half then memchrs each of
# them, so the proof the masked run adds is never the only one left on the
# corpus's hostile cells (the S2b witness's `S` is exactly such a member).
# The full-corpus axes run at landing confirms or populates this group.
# GROUP F3 — bit 45, `-fno-req-set-lead` (PCREC_NO_REQ_SET_LEAD, [K82] (A),
# tuning.md §2.40): EMPTY by structure, not yet by measurement. The denied
# row removes a leading one-byte memchr of a NECESSARY-SET member; on a
# DFA-scan route the scan bounds the call either way, and on the no-DFA-scan
# VM route K65's whole-set half memchrs that same member when the lead is
# denied (run_prechecks.sh §5.8/§5.9's deny rows), so no no-match proof is
# lost. Lane k82fix's AXES="-fno-req-run-fold -fno-req-set-lead" run
# (docs/dev/lanes/k82fix_report.md §6) confirms or populates this group.
# GROUP F4 — bit 46, `-fno-req-handoff` (PCREC_NO_REQ_HANDOFF, [K82] (B),
# tuning.md §2.41): EMPTY by construction, the design's §4.2 item 1 stated on
# the F3 precedent. The handoff only moves where a scan BEGINS, past positions
# a necessary run proves cannot begin a match; its budget-bound population is
# the count-collapsed hybrid movers (the one prefilter language whose answers
# can sit below c - K, so the VM's attempts could differ), and Frank's Q10
# ruling DECLINES the handoff there, so the deny moves no give-up anywhere.
# Measured: every hybrid mover of the corpus and the bench reads
# RX_VM_PREFILTER_LANG "exact" (docs/dev/optloop/s4/k82hbuild/
# k82h_movers.log), and the corpus's 35 budget/gu blocks are 0 movers
# (litscan_k82h.md §3.1a). Lane k82hbuild's AXES run over the widened subset
# (docs/dev/lanes/k82hbuild_report.md) confirms or populates this group.
# GROUP F5 — bit 47, `-fno-start-set` (PCREC_NO_START_SET, [START-SET] stage
# 2, tuning.md §2.42, match_api.md §3.1's give-up sentence): the VM hat skips
# only attempts that fail, so a deny-arm GIVE-UP may become the hat's answer,
# never the reverse (D148 Q6/Q-R3). The population is the capacity witness
# `tests/startset/giveup.rxt` (`(?=(?:a|b|x)*c)x`, `budget frames=8`): the
# deny arm's attempt at a non-S byte exhausts the frames inside the lookahead.
# Derived from a live run, not assumed (lane ssbuild2, RXTFLAGS=
# "-fno-start-set" over that file: GAVE UP at exactly these 22 lines; the
# design's 11 corpus budget/gu movers read 0 here — their give-ups start on S
# bytes). Keyed by the bare flag; a multi-flag job (the product arm's
# `--engine=vm -fno-start-set`) inherits each component flag's entries.
# Since stage 3 the flag ALSO removes the DFA hat (`first-memchr-bounded`/
# `first-class-bounded`, tuning.md §2.42): a skip, so answer- and
# give-up-identical by construction (the conditional re-seed restores the
# state a search started at the landing would have), and no entry above is
# the DFA hat's. Its movers ride this plain job at AUTO (`--engine=vm` has no
# DFA scan), and the DFA-hat arm below the job loop counts and floors them
# (the ss3 D6 panel's checks-M3).
    ["-fno-start-set|tests/startset/giveup.rxt:21"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:22"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:23"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:24"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:25"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:26"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:27"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:28"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:29"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:30"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:31"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:32"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:33"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:34"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:35"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:36"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:37"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:38"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:39"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:40"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:41"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
    ["-fno-start-set|tests/startset/giveup.rxt:56"]="[START-SET] Q-R3 (tuning.md §2.42, match_api.md §3.1): the deny arm's attempt at a non-S byte exhausts budget frames=8 inside the lookahead and gives up; the hat skips that attempt and answers (libpcre2's unbounded answer). One direction only."
# GROUP G — §2.11 `--engine=vm`, 10 cases, TWO mechanisms.
#
# G1 (2 cases) — tests/base/d27_k23_ambiguous_decomposition.rxt:90,98, the
# SAME two cells as Groups B/D above (-fno-prefilter/-fprefilter-collapse),
# reached a THIRD way: tuning.md §2.11 states "`--engine=vm` additionally
# disables the DFA prefilter (D44/R21 E-6)" — forcing VM loses the identical
# sharp reverse-window start Group B's denial removes directly. Verified
# live 2026-09-26 (this file alone, RXTFLAGS="--engine=vm"): keys_base=113
# giveup1=10 (2 here + 8 in G2 below) — exact match to the full-corpus
# giveup1-unallowed=10.
    ["--engine=vm|tests/base/d27_k23_ambiguous_decomposition.rxt:90"]="tuning.md §2.11 (\"--engine=vm additionally disables the DFA prefilter\") + §2.5/§2.17: forcing VM loses the same sharp prefilter-window start Group B's -fno-prefilter denial removes directly — default matches, --engine=vm gives up (steps)"
    ["--engine=vm|tests/base/d27_k23_ambiguous_decomposition.rxt:98"]="tuning.md §2.11 (\"--engine=vm additionally disables the DFA prefilter\") + §2.5/§2.17: forcing VM loses the same sharp prefilter-window start Group B's -fno-prefilter denial removes directly — default matches, --engine=vm gives up (steps)"

# G2 (8 cases) — tests/base/k18_deep_nesting.rxt:51,52,56,57,61,62,66,67, the
# "a"/"aa" cells of the file's 66/70/74/78-level-nesting `(?:...*)*`
# patterns (never the "" cells — matching empty needs no backtracking
# frame). Repro verified live: default RX_ENGINE "dfa" matches "a" in one
# step; --engine=vm forces RX_ENGINE "vm" and the SAME one-byte subject
# exhausts the fixed VM resume-stack/trail budget (limits.md §4: ~2 frames
# + ~9 trail entries per nesting level, independent of subject length) —
# exit 3 "frames". This mechanism had NO citing sentence before this lane
# (§2.11 named only the prefilter loss, G1 above); the one-sentence
# addition naming it is in the same commit (docs/spec/tuning.md §2.11, D80).
# known_issues.md's K18 entry already names this file as the deliberate
# resource guard for exactly this nesting-depth cost. Verified live
# 2026-09-26 (this file + d27_k23 together, RXTFLAGS="--engine=vm"):
# keys_base=113 giveup1=10 total, 8 of them these keys.
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:51"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:52"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:56"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:57"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:61"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:62"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:66"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
    ["--engine=vm|tests/base/k18_deep_nesting.rxt:67"]="tuning.md §2.11 (this lane's addition, K18): auto selects the DFA (no per-nesting-level frame cost) and matches instantly; forcing --engine=vm makes the fixed VM resume-stack/trail budget (limits.md §4) the binding constraint at this nesting depth — default matches, --engine=vm gives up (frames)"
)

# ============================================================================
# THE BASELINE
# ============================================================================

BASE_DUMP="$WORKDIR/base.tsv"
echo
if [ "$HARNESS_BATCH" -ge 1 ]; then
    echo "axes: HARNESS_BATCH=$HARNESS_BATCH — baseline AND every axis run below compile the corpus through the batched dispatch path (docs/testing.md's \"HARNESS_BATCH\" section); unset/0 is the unbatched per-pattern path this sweep has always used"
else
    echo "axes: HARNESS_BATCH unset (0) — unbatched per-pattern compile, this sweep's historical shape"
fi
echo "axes: baseline run (no extra flags)..."
t0=$(date +%s)
"$ROOT_DIR/scripts/watchdog" -l axes-baseline -S axes -s 3600 -- \
    env RXTDUMP="$BASE_DUMP" PCREC="$PCREC" CC="$CC" GENCFLAGS="$GENCFLAGS" \
        PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" HARNESS_BATCH="$HARNESS_BATCH" \
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
    # run_one_axis <label> <extra-flags-string> <force-population-not-failure> <save-dump-path>
    local label="$1" flags="$2" lost_is_ok="$3" save_dump="$4"
    # $lost_is_ok's original job (blanket-accept a nonzero LOST count for
    # the one documented do-or-die bit-flag and the coarse engine axis) is
    # SUPERSEDED by REFUSAL_PATTERN/REFUSAL_FLOOR below (2026-08-26,
    # manager's classification rule): a REFUSED case is now reclassified
    # by its own diagnostic TEXT, per axis, never by a blanket per-axis
    # flag — kept as a parameter (call sites still pass it, harmlessly)
    # rather than touched, since it is no longer read for the verdict.
    shift 4   # THE BUG (found 2026-08-26, live full-corpus run): without this,
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
    # [OPT-DIAL] the count moved from 3 to 4 with `save_dump`'s own
    # addition above — the shift count is the number of THIS FUNCTION's own
    # positional parameters, so it moves in lockstep with that list rather
    # than being a magic number to remember to bump.
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
            HARNESS_BATCH="$HARNESS_BATCH" \
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
    # [OPT-DIAL] SAVE THE RAW DUMP FOR DIAL-S3, before anything below can
    # delete it. Only the dial's four jobs pass a non-empty $save_dump (see
    # the job-list build above); every other axis's $save_dump is empty and
    # this is a no-op for it. Copied unconditionally on dump existence,
    # BEFORE this axis's own pass/fail verdict is computed — DIAL-S3 reads
    # the raw REFUSED rows directly and does its own independent population
    # check, so it must not be starved of a dump merely because this axis's
    # ORDINARY answer-identity verdict (a different question) came back RED.
    if [ -n "$save_dump" ]; then
        cp "$dump" "$save_dump"
    fi
    local rowsfile="$WORKDIR/rows_$slug.tsv"
    : > "$rowsfile"
    local diffe="$WORKDIR/diff_$slug.err"
    local diffline
    diffline="$(awk -v BASEFILE="$BASE_DUMP" -v ROWSFILE="$rowsfile" -f "$SCRIPT_DIR/dump_diff.awk" "$dump" 2>"$diffe")"
    cat "$diffe" >&2
    echo "  $diffline"
    local mismatches budget giveup1 refused lost gained agree_n keys_base_n keys_axis_n
    mismatches="$(echo "$diffline" | grep -oE 'mismatches=[0-9]+' | cut -d= -f2)"
    budget="$(echo "$diffline" | grep -oE 'budget=[0-9]+' | cut -d= -f2)"
    giveup1="$(echo "$diffline" | grep -oE 'giveup1=[0-9]+' | cut -d= -f2)"
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
    # [START-SET] A MULTI-FLAG JOB INHERITS EACH COMPONENT FLAG'S DOCUMENTED
    # POPULATIONS (the product arm's `--engine=vm -fno-start-set`): its
    # refusals are `--engine=vm`'s and its give-ups `-fno-start-set`'s, and
    # restating either list under the joined spelling would be a second copy.
    local pattern_list="${REFUSAL_PATTERN[$flags]:-}" _comp
    if [ "$flags" != "${flags%% *}" ]; then
        for _comp in $flags; do
            [ -n "${REFUSAL_PATTERN[$_comp]:-}" ] && \
                pattern_list="$pattern_list${pattern_list:+$REFUSAL_DELIM}${REFUSAL_PATTERN[$_comp]}"
        done
    fi
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
    # THE GIVEUP1 RECLASSIFICATION ([chkgaps] 2026-09-25, docs/dev/
    # learnings.md §3's own filed candidate: "count answer->give-up
    # TRANSITIONS as their own population"). dump_diff.awk's GIVEUP1
    # bucket is a case where EXACTLY ONE side gives up/times out and the
    # other reports a real answer -- distinct from BUDGET (both sides give
    # up; tuning.md §2.5 licenses that boundary moving) and previously
    # folded into it wholesale, which is exactly how the K64 admission
    # defect's own forced-VM give-up would have read here: "budget-bound,
    # never a failure" on a case that used to answer correctly.
    #
    # EVERY GIVEUP1 CASE IS A FAILURE UNLESS THIS AXIS NAMES IT, BY EXACT
    # KEY, IN GIVEUP1_ALLOWANCE below -- "derive, never blanket-excuse"
    # (the brief's own wording), K35's "a manifest naming irreplaceable
    # rows" rule one table up from REFUSAL_PATTERN's own precedent. A
    # COUNT-ONLY allowance (e.g. "up to N giveup1 cases on this axis") would
    # disarm itself the moment a DIFFERENT case moved into the count under
    # its ceiling -- exactly the failure mode K35 exists to name -- so the
    # manifest is per (axis, file:line) pair, never a number.
    #
    # THE KEY IS $ROOT_DIR-RELATIVE, on BOTH sides of this comparison --
    # `$key` itself (dump_diff.awk's `$1:$2`, which is `$cur_file:$line`)
    # is `$ROOT_DIR`-ABSOLUTE on a full-corpus run (`tests/harness/run.sh`
    # discovers files via `find "$ROOT_DIR/tests" ...`), so a manifest keyed
    # on the raw value would be tied to THIS checkout's own absolute path
    # (giveupallow's own first landing did exactly that and was corrected
    # here, same day). `${key#"$ROOT_DIR"/}` is the identical no-op-when-
    # already-relative idiom `tests/harness/run.sh` itself already uses for
    # `SIZELOG`'s row key (that file's own comment: "no-ops ... when it does
    # not already start with `$ROOT_DIR/`") -- so a `RXTFLAGS`/file-argument
    # invocation whose `$key` is ALREADY relative (e.g. a single-file
    # `AXES=... bash tests/axes/run_axes.sh tests/base/foo.rxt` check) is
    # unaffected, and the manifest below is written relative throughout.
    local giveup1_allowed=0 giveup1_unallowed=0
    if [ "$giveup1" -gt 0 ]; then
        while IFS=$'\t' read -r cls key btrc bout atrc aout; do
            [ "$cls" = "GIVEUP1" ] || continue
            # two statements: one `local` expands every word before it
            # assigns any, so `$relkey` would be unset in its own line
            local relkey="${key#"$ROOT_DIR"/}" _c
            local _allowed="${GIVEUP1_ALLOWANCE[$flags|$relkey]:-}"
            if [ -z "$_allowed" ] && [ "$flags" != "${flags%% *}" ]; then
                for _c in $flags; do
                    [ -n "${GIVEUP1_ALLOWANCE[$_c|$relkey]:-}" ] && _allowed=1
                done
            fi
            if [ -n "$_allowed" ]; then
                giveup1_allowed=$((giveup1_allowed + 1))
            else
                giveup1_unallowed=$((giveup1_unallowed + 1))
                if [ "$giveup1_unallowed" -le 20 ]; then
                    echo "AXIS FAIL: $label: UNALLOWED one-sided give-up at $key: default={trc=$btrc out=$bout} axis={trc=$atrc out=$aout} (not in GIVEUP1_ALLOWANCE — an answer<->give-up transition, not a moving budget boundary)" >&2
                fi
            fi
        done < "$rowsfile"
    fi
    local total_mismatches=$((mismatches + refused_undocumented + giveup1_unallowed))
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
    echo "  agree=$agree_n budget-bound=$budget giveup1-allowed=$giveup1_allowed giveup1-unallowed=$giveup1_unallowed refused-documented=$refused_documented (floor $([ -n "$floor" ] && echo "$floor" || echo "none")) lost-other=$lost mismatches=$total_mismatches gained=$gained"
    local verdict="OK"
    if [ "$total_mismatches" -gt 0 ] || [ "$gained" -gt 0 ] || [ "$lost" -gt 0 ] || [ "$floor_breach" -eq 1 ]; then
        verdict="FAIL"
        fail=1
        echo "AXIS FAIL: $label: $total_mismatches mismatch(es) (incl. $refused_undocumented undocumented refusal(s), $giveup1_unallowed unallowed one-sided give-up(s)), $lost lost-other, $gained gained$([ "$floor_breach" -eq 1 ] && echo ", refused-documented floor breached")" >&2
    fi
    if [ "$budget" -gt 0 ]; then
        echo "  ($budget case(s) budget-bound — BOTH sides give up/time out, only the boundary moved, never a failure)"
    fi
    # [ART-POSS-ARMS] §8.6: the FOURTH transition class, GIVEUP(code1) ->
    # GIVEUP(code2) — both sides give up (driver exit 3) but with DIFFERENT
    # give-up words, read off the rows stream's BUDGET rows (run_ksweep.sh's
    # R6 reads the same rows the same way; the row class stays BUDGET so that
    # reader does not go vacuous). Possessification can turn a STEPS or
    # FRAMES give-up into a WORK one (tuning.md §2.1; doubled-word's move),
    # so the class is REPORTED as its own population, never a failure: what a
    # code change means is the axis's own spec section's to say.
    local gu2
    gu2=$(awk -F'\t' '$1=="BUDGET" && $3=="3" && $5=="3" && $4!=$6 {n++} END{print n+0}' "$rowsfile")
    if [ "$gu2" -gt 0 ]; then
        echo "  ($gu2 of those give up with a DIFFERENT CODE on the two sides — the GIVEUP(code)->GIVEUP(code) class, reported, not a failure)"
    fi
    if [ "$giveup1_allowed" -gt 0 ]; then
        echo "  ($giveup1_allowed case(s) one-sided give-up, named in GIVEUP1_ALLOWANCE — a measured population, not a failure)"
    fi
    if [ "$refused_documented" -gt 0 ]; then
        echo "  ($refused_documented case(s) refused with this axis's own documented limit — a population, not a failure)"
    fi
    axis_results+=("$label|$verdict|$diffline refused_doc=$refused_documented refused_undoc=$refused_undocumented giveup1_allowed=$giveup1_allowed giveup1_unallowed=$giveup1_unallowed|$((t1 - t0))s")
    [ "$KEEP" = "1" ] || rm -f "$dump" "$rowsfile" "$outlog" "$errlog" "$diffe"
}

# ============================================================================
# BUILD THE ORDERED JOB LIST — SAME axes, SAME order, SAME AXES= filtering
# as the sequential form (bit-flag axes in bit order, then --engine=vm,
# then --engine=dfa) — pairing changes ONLY how the list below is executed,
# never which axes run or the order their summary rows are printed in.
# ============================================================================

declare -a job_label=() job_flags=() job_lost_ok=()
# job_savedump[idx], set ONLY for the dial's four jobs below (left unset —
# read with `:-` — for every other axis): the path run_one_axis copies its
# own RXTDUMP to before cleanup, so DIAL-S3 (after the job loop) can read
# it without recompiling. A plain array append here would misalign against
# job_label's own index the moment any OTHER job type appended after it, so
# every writer sets it by EXPLICIT INDEX instead (see the dial block below).
declare -a job_savedump=()
# [UTF-VALID] `-futf-check` IS EXCLUDED FROM THE IDENTITY SWEEP BY NAME
# (docs/spec/tuning.md §2.36): it is a CONTRACT axis whose answers differ on
# purpose on every ill-formed corpus cell, so an identity comparison would
# report each one as a disagreement. It gets its OWN ARM below
# (tests/axes/utfcheck_arm.py). The exclusion is ASSERTED PRESENT —
# `PCREC_FORCE_PREFILTER`'s idiom one section up — so a rename of the bit
# cannot silently put the axis back into (or drop it out of) both sweeps.
utfcheck_bit=""
for bit in "${!bit_macro[@]}"; do
    [ "${bit_macro[$bit]}" = "PCREC_FORCE_UTF_CHECK" ] && utfcheck_bit="$bit"
done
if [ -z "$utfcheck_bit" ] || [ "${macro_flag[PCREC_FORCE_UTF_CHECK]:-}" != "-futf-check" ]; then
    echo "run_axes.sh: FATAL: PCREC_FORCE_UTF_CHECK / -futf-check is not among the derived axes — the one axis this sweep excludes by name for its own arm has been renamed or removed, so neither sweep would cover it" >&2
    exit 1
fi
for bit in $(printf '%s\n' "${!bit_macro[@]}" | LC_ALL=C sort -n); do
    macro="${bit_macro[$bit]}"
    flagtext="${macro_flag[$macro]}"
    label="$flagtext ($macro, bit $bit)"
    [ "$bit" = "$utfcheck_bit" ] && continue    # its own arm, below
    if [ -n "$AXES" ]; then
        case " $AXES " in (*" $flagtext "*) ;; (*) continue ;; esac
    fi
    lost_ok=0
    [ "$bit" = "$force_bit" ] && lost_ok=1
    job_label+=("$label"); job_flags+=("$flagtext"); job_lost_ok+=("$lost_ok")
done
if [ -z "$AXES" ] || printf '%s' "$AXES" | grep -q -- '--engine'; then
    job_label+=("--engine=vm (§2.11)");  job_flags+=("--engine=vm");  job_lost_ok+=("1")
    job_savedump[$((${#job_label[@]} - 1))]="$WORKDIR/ss_vm_base.tsv"
    job_label+=("--engine=dfa (§2.11)"); job_flags+=("--engine=dfa"); job_lost_ok+=("1")
fi
# [START-SET] THE PRODUCT ARM's two runs (docs/design/startset.md §6.2 row
# "answer identity" (1) and "engine cross-check", review r4 checks-F3 and
# sound-F8; D148 addendum 2 Q-R2). The bit-flag sweep above runs
# `-fno-start-set` at AUTO only, where the VM hat reaches the prefilter-less
# VM artifacts alone; under `--engine=vm` it reaches every unanchored
# non-nullable pattern, so the axis is ALSO run there: `--engine=vm
# -fno-start-set` is a job against the DEFAULT baseline (the engine axis with
# neither engine reading the start set, so the two still check each other),
# and its dump is compared against `--engine=vm`'s own (the product arm,
# below the job loop). Selected by the empty AXES= or by `-fno-start-set`.
if [ -z "$AXES" ] || case " $AXES " in (*" -fno-start-set "*) true ;; (*) false ;; esac; then
    if ! printf '%s' "$AXES" | grep -q -- '--engine' && [ -n "$AXES" ]; then
        job_label+=("--engine=vm (§2.11)");  job_flags+=("--engine=vm");  job_lost_ok+=("1")
        job_savedump[$((${#job_label[@]} - 1))]="$WORKDIR/ss_vm_base.tsv"
    fi
    job_label+=("--engine=vm -fno-start-set (§2.11 x §2.42)"); job_flags+=("--engine=vm -fno-start-set"); job_lost_ok+=("1")
    job_savedump[$((${#job_label[@]} - 1))]="$WORKDIR/ss_vm_deny.tsv"
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
# [FINDINGS] B2 THE FINDINGS AXIS (docs/design/findings/design.md §11.1,
# [r2 S-F1]): the corpus under EACH adversarial analysis in
# tests/findings/adversarial/ — shapes built to be wrong (uniform, inverted,
# one-hot, random) and one `fire-<reader>` per rate reader, each the table
# that moves that reader's choice most. A rate may change SPEED and never an
# answer or a give-up (§6.2a), so `lost_ok` is 0 and GIVEUP1 carries NO
# allowance for any of them: a transition is a failure, counted as its own
# population. RXTFLAGS carries `-I DIR --analysis=NAME`, which every compile
# the harness makes (a `--pattern` compile, or a file operand) resolves.
# Selected by `--analysis` in AXES (every bundle) or `--analysis=NAME` (one).
# ============================================================================
FINDINGS_ADV="$ROOT_DIR/tests/findings/adversarial"
if [ -z "$AXES" ] || printf '%s' "$AXES" | grep -q -- '--analysis'; then
    for _b in "$FINDINGS_ADV"/*.rxt; do
        _n="$(basename "$_b" .rxt)"
        if [ -n "$AXES" ] && ! printf ' %s ' "$AXES" | grep -q -- ' --analysis '; then
            case " $AXES " in (*" --analysis=$_n "*) ;; (*) continue ;; esac
        fi
        job_label+=("--analysis=$_n (FINDINGS axis, findings design §11.1)")
        job_flags+=("-I $FINDINGS_ADV --analysis=$_n")
        job_lost_ok+=("0")
    done
fi

# ============================================================================
# [OPT-DIAL] THE DIAL, AS A FIFTH KIND OF AXIS (docs/design/opt_dial_design.md
# §6.1; docs/spec/tuning.md §5.5). Four non-default positions join the job
# list the identical mechanical way `--engine=`/`--vm-entry-shape=` do:
# RXTFLAGS accepts an arbitrary extra flag, verified live that a `--tune=`
# spelling composes exactly as those two do (lands in `pflags` before the
# pattern's own `--`). Position 0 (`balanced`) needs no arm here —
# `src/core/tune.c`'s own header states it is a structural no-op, byte-
# identical to no flag at all — that is `tests/codegen/run_tune_dial.sh`
# section 1's job, not this sweep's.
#
# `lost_ok` IS 0 ON ALL FOUR, and DELIBERATELY. `docs/spec/tuning.md` §5.5
# and design §6.2 both state the dial's own rule as ONE SENTENCE: no
# position may move the refusal set, in EITHER direction — so unlike
# `--engine=dfa`'s legitimate do-or-die refusals, ANY refused case under a
# tune position is a real failure here, and this sweep carries NO
# REFUSAL_PATTERN entry for any `--tune=` flag on purpose: a documented
# exemption is exactly the K45 mechanism §6.2 rules out for this axis (right
# for an axis whose job is to exercise a flag nobody ships; wrong for a
# dial position that DOES ship). That per-axis "undocumented refusal is a
# failure" rule is necessary but not sufficient on its own, though — a
# COUNT of undocumented refusals can be equal on both sides of a comparison
# while naming two different patterns, which is exactly the shape design
# §6.2 warns both of this design's hazards (`-fno-anchored-dfa`'s and the
# emitted-size caps') could slip through AT ONCE, since they run in
# OPPOSITE directions. DIAL-S3, after the job loop below, is the SEPARATE
# keyed-set check that rules out that shape — it reuses these same runs'
# own saved RXTDUMP output rather than recompiling.
declare -A DIAL_POSITIONS=( ["-2"]="min-size" ["-1"]="size" ["1"]="speed" ["2"]="max-speed" )
declare -a DIAL_ORDER=("-2" "-1" "1" "2")
declare -A dial_dump_file=()   # position -> saved RXTDUMP path, for DIAL-S3
if [ -z "$AXES" ] || printf '%s' "$AXES" | grep -q -- '--tune'; then
    echo "axes: --tune=-1 (size) is NOT declared vacuous at first build: both [ART-SIZE] ladder parameters move (bar 0.85, threshold 80,000) and the ladder's population below 120,000 bytes is real -- 81 shapes the ladder has never run at 120,000 (opt_dial_design.md §6.1b). A measured zero-diff result on this corpus is reported as a genuine finding below, not assumed as a construction."
    for _pos in "${DIAL_ORDER[@]}"; do
        _alias="${DIAL_POSITIONS[$_pos]}"
        if [ "$_pos" = "2" ]; then
            echo "axes: --tune=2 (max-speed) is DECLARED VACUOUS against --tune=1 (speed) at first build: identical on every moving cell (tuning.md §5.4's policy table — both set the entry-chain term to 8,192 and nothing else), differing only in the RX_TUNE stamp string. It runs anyway and is swept for real (S219's precedent: a check that ships UNREACHED/vacuous ships its derivation, and its runner fires the day it stops being vacuous). Become-reachable: the day [CLS-TREE] lands (lambda's frontier point moves 64 -> 256 at this position) or the speed-notch floor s is ruled below 1.03 (opt_dial_design.md §3.6(d))."
        fi
        _slug="dial_$(echo "$_pos" | tr -c 'A-Za-z0-9' '_')"
        dial_dump_file["$_pos"]="$WORKDIR/${_slug}_saved.tsv"
        job_label+=("--tune=$_pos ($_alias, tuning.md §5.1)")
        job_flags+=("--tune=$_pos")
        job_lost_ok+=("0")
        job_savedump[$((${#job_label[@]} - 1))]="${dial_dump_file[$_pos]}"
    done
else
    echo "axes: --tune positions not run (filtered out by AXES=)"
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
            run_one_axis "${job_label[$idx]}" "${job_flags[$idx]}" "${job_lost_ok[$idx]}" "${job_savedump[$idx]:-}" "$@"
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
# DIAL-S3 — THE DIAL'S REFUSAL SET, COMPARED AS KEYS (docs/spec/tuning.md
# §5.5; docs/design/opt_dial_design.md §6.2/§6.2a). NOT the REFUSAL_PATTERN
# mechanism above, and deliberately does not touch it: that mechanism is
# right for an AXIS SWEEP (exercise a flag in both arms including arms
# nobody ships, floor a documented population) and wrong for the DIAL,
# whose rule is one sentence — no position may move the refusal set, in
# EITHER direction, because "refused" is an answer a caller can observe and
# depend on and a dial whose positions accept different LANGUAGES is not a
# tuning knob. A count-only comparison is the ONE shape that could pass
# while both of this design's hazards fired at once — `-fno-anchored-dfa`
# losing a pattern's answer and the emitted-size caps gaining one run in
# OPPOSITE directions, so equal counts on both sides can hide two different
# patterns moving past each other. So: SETS of `file:line` keys, both
# directions, named separately, never a count.
#
# MECHANISM: reuses the RXTDUMP files run_one_axis already saved above (the
# dial's own tune-axis runs, `job_savedump`) plus `$BASE_DUMP` (position 0,
# `balanced` — the sweep's own baseline, already computed). No pattern is
# recompiled a sixth time for this arm — docs/dev/optdial_size_sweep.md §0
# used this identical RXTDUMP-keyed-by-file:line mechanism for exactly this
# kind of cross-check (K35), and this arm reuses it rather than inventing a
# second one.
#
# THE EMPTY-POPULATION FAILURE MODE (W23.1's own lesson, w233_report.md
# §5): an arm deriving its population from the data it checks must FAIL
# when that population is empty, or the first thing that breaks its
# extraction turns it green. Position 0's own refused-key set is expected
# to be near-empty (the corpus's ordinary `pattern` blocks compile at
# default by construction — a `pattern` block that failed to compile at
# `balanced` would already be red in plain `make test`), so a near-zero
# diff on this arm must be told apart from an extractor reading nothing at
# all. Before reporting any refused-set diff as a real (possibly zero) one,
# this arm asserts each dump it reads is HEALTHY on its own terms — at
# least half of $base_keys total lines, the identical floor run_one_axis's
# own harness-level-failure branch uses above, applied here independently
# since this arm reads the raw dumps directly rather than trusting that
# axis's own verdict.
dial_s3_verdict="SKIPPED (no --tune positions ran under this AXES= filter)"
if [ "${#dial_dump_file[@]}" -gt 0 ]; then
    echo
    echo "axes: DIAL-S3 — the dial's refusal set, compared as KEYS across all five positions..."
    dial_s3_fail=0
    dial_s3_extractor_unhealthy=0

    base_refused="$WORKDIR/dial_refused_0.keys"
    awk -F'\t' '$5=="REFUSED"{print $1":"$2}' "$BASE_DUMP" | LC_ALL=C sort -u > "$base_refused"
    base_refused_n=$(wc -l < "$base_refused")
    base_total_lines=$(wc -l < "$BASE_DUMP")
    echo "  position 0 (balanced): $base_total_lines total dump lines, $base_refused_n refused"
    if [ "$base_total_lines" -lt "$((base_keys / 2))" ]; then
        echo "DIAL-S3 FAIL: position 0's own baseline dump has only $base_total_lines lines against a $base_keys-line baseline population — the extractor is not reading a healthy dump; a zero-diff result below would be an extraction failure wearing one, not a real zero (docs/dev/learnings.md §3, w233_report.md §5)" >&2
        dial_s3_fail=1
        dial_s3_extractor_unhealthy=1
    fi

    for _pos in "${DIAL_ORDER[@]}"; do
        _alias="${DIAL_POSITIONS[$_pos]}"
        _dump="${dial_dump_file[$_pos]}"
        if [ ! -f "$_dump" ]; then
            echo "DIAL-S3 FAIL: --tune=$_pos ($_alias): no saved RXTDUMP at $_dump — that position's own axis run above must have failed before producing one (see its AXIS FAIL lines)" >&2
            dial_s3_fail=1
            continue
        fi
        _total=$(wc -l < "$_dump")
        if [ "$_total" -lt "$((base_keys / 2))" ]; then
            echo "DIAL-S3 FAIL: --tune=$_pos ($_alias): dump has only $_total lines against a $base_keys-line baseline population — extractor unhealthy for this position, not a real population" >&2
            dial_s3_fail=1
            dial_s3_extractor_unhealthy=1
            continue
        fi
        _pslug="${_pos//-/m}"
        _refused="$WORKDIR/dial_refused_${_pslug}.keys"
        awk -F'\t' '$5=="REFUSED"{print $1":"$2}' "$_dump" | LC_ALL=C sort -u > "$_refused"
        _refused_n=$(wc -l < "$_refused")
        # BOTH DIRECTIONS, named separately (never a count): `comm` on two
        # LC_ALL=C-sorted key sets. -23 keeps column 1 alone (unique to
        # base_refused): refused at 0, NOT refused (compiles) at P — the
        # pattern GAINED an answer it did not have at balanced. -13 keeps
        # column 2 alone (unique to $_refused): not refused (compiled) at
        # 0, refused at P — the pattern LOST the answer balanced gave it.
        _gained="$WORKDIR/dial_gained_${_pslug}.keys"
        _lost="$WORKDIR/dial_lost_${_pslug}.keys"
        comm -23 "$base_refused" "$_refused" > "$_gained"
        comm -13 "$base_refused" "$_refused" > "$_lost"
        _gained_n=$(wc -l < "$_gained")
        _lost_n=$(wc -l < "$_lost")
        echo "  --tune=$_pos ($_alias): $_total total dump lines, $_refused_n refused; vs position 0: $_gained_n gained-an-answer, $_lost_n lost-an-answer"
        if [ "$_gained_n" -gt 0 ]; then
            dial_s3_fail=1
            echo "DIAL-S3 FAIL: --tune=$_pos ($_alias) now COMPILES $_gained_n pattern(s) that REFUSE at position 0 — the pattern gained an answer it did not have at balanced, a language change tuning.md §5.5 forbids:" >&2
            head -20 "$_gained" | sed 's/^/    /' >&2
        fi
        if [ "$_lost_n" -gt 0 ]; then
            dial_s3_fail=1
            echo "DIAL-S3 FAIL: --tune=$_pos ($_alias) now REFUSES $_lost_n pattern(s) that COMPILE at position 0 — the pattern lost the answer balanced gave it, the opposite forbidden direction:" >&2
            head -20 "$_lost" | sed 's/^/    /' >&2
        fi
    done

    if [ "$dial_s3_fail" -ne 0 ]; then
        if [ "$dial_s3_extractor_unhealthy" -ne 0 ]; then
            dial_s3_verdict="FAIL — extractor unhealthy on at least one position, see DIAL-S3 FAIL lines above (not a scored refusal-set diff)"
        else
            dial_s3_verdict="FAIL — the refusal set moved, see DIAL-S3 FAIL lines above"
        fi
        fail=1
    else
        dial_s3_verdict="OK — refusal set identical (as file:line keys, both directions) across all five positions; extractor health asserted independently, not assumed"
    fi
    echo "  $dial_s3_verdict"
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
# [UTF-VALID] THE `-futf-check` ARM (docs/spec/tuning.md §2.36). The same
# corpus under RXTFLAGS=-futf-check, compared against the baseline dump by
# tests/axes/utfcheck_arm.py: identical on every byte block (the flag is
# inert there), and on a utf8 block identical iff python's strict decoder
# finds the cell's checked range [startpos - LB, n) well-formed (LB from
# libpcre2), `utf <offset>` otherwise.
# ============================================================================
utfcheck_verdict="not run (filtered out by AXES=)"
if [ -z "$AXES" ] || case " $AXES " in (*" -futf-check "*) true ;; (*) false ;; esac; then
    UTF_DUMP="$WORKDIR/axis_utfcheck.tsv"
    echo
    echo "axes: -futf-check arm (RXTFLAGS=\"-futf-check\", its own oracle, not identity)..."
    "$ROOT_DIR/scripts/watchdog" -l axes-utfcheck -S axes -s 3600 -- \
        env RXTFLAGS="-futf-check" RXTDUMP="$UTF_DUMP" PCREC="$PCREC" CC="$CC" \
            GENCFLAGS="$GENCFLAGS" PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" \
            HARNESS_BATCH="$HARNESS_BATCH" \
            bash "$ROOT_DIR/tests/harness/run.sh" "$@" > "$WORKDIR/axis_utfcheck.out" 2>"$WORKDIR/axis_utfcheck.err"
    if [ ! -f "$UTF_DUMP" ]; then
        utfcheck_verdict="FAIL (no dump — see $WORKDIR/axis_utfcheck.err)"
        fail=1
    elif python3 "$SCRIPT_DIR/utfcheck_arm.py" "$BASE_DUMP" "$UTF_DUMP" "$ROOT_DIR" \
            > "$WORKDIR/utfcheck_arm.out" 2>&1; then
        utfcheck_verdict="OK — $(grep -m1 '^utfcheck arm:' "$WORKDIR/utfcheck_arm.out")"
        cat "$WORKDIR/utfcheck_arm.out"
    else
        cat "$WORKDIR/utfcheck_arm.out"
        utfcheck_verdict="FAIL — $(grep -m1 '^utfcheck arm:' "$WORKDIR/utfcheck_arm.out")"
        fail=1
    fi
    echo "  $utfcheck_verdict"
fi

# ============================================================================
# [START-SET] THE PRODUCT ARM: `--engine=vm -fno-start-set` against
# `--engine=vm`, the two job dumps saved above, compared by the same
# dump_diff.awk. Its OWN baseline is the forced-VM run, because under
# `--engine=vm` the hat reaches a population the auto sweep cannot (startset.md
# §6.2). MISMATCH, LOST, GAINED and any REFUSED fail; a GIVEUP1 is allowed only
# for a `-fno-start-set|<key>` entry (GROUP F5: the deny arm gives up, the hat
# answers). The MOVER FLOOR counts the baseline's cases whose block is in the
# forced mover manifest (tests/startset/manifests/manifest_s2_vm_forced.tsv),
# so a sweep that stopped reaching the movers fails rather than reading clean.
# ============================================================================
startset_verdict="not run (filtered out by AXES=)"
if [ -f "$WORKDIR/ss_vm_base.tsv" ] && [ -f "$WORKDIR/ss_vm_deny.tsv" ]; then
    echo
    echo "axes: [START-SET] product arm: --engine=vm -fno-start-set against --engine=vm..."
    ss_rows="$WORKDIR/rows_startset_product.tsv"; : > "$ss_rows"
    ss_line="$(awk -v BASEFILE="$WORKDIR/ss_vm_base.tsv" -v ROWSFILE="$ss_rows" \
                   -f "$SCRIPT_DIR/dump_diff.awk" "$WORKDIR/ss_vm_deny.tsv" 2>/dev/null)"
    echo "  $ss_line"
    ss_bad=0; ss_allowed=0
    for f_ in mismatches lost gained refused; do
        v_="$(echo "$ss_line" | grep -oE "$f_=[0-9]+" | cut -d= -f2)"
        [ "${v_:-1}" -gt 0 ] && { ss_bad=1; echo "AXIS FAIL: [START-SET] product arm: $f_=${v_:-?}" >&2; }
    done
    while IFS=$'\t' read -r cls key btrc bout atrc aout; do
        [ "$cls" = "GIVEUP1" ] || continue
        rk="${key#"$ROOT_DIR"/}"
        if [ -n "${GIVEUP1_ALLOWANCE[-fno-start-set|$rk]:-}" ]; then
            ss_allowed=$((ss_allowed + 1))
        else
            ss_bad=1
            echo "AXIS FAIL: [START-SET] product arm: UNALLOWED one-sided give-up at $key: vm={trc=$btrc out=$bout} vm-deny={trc=$atrc out=$aout}" >&2
        fi
    done < "$ss_rows"
    ss_movers="$(python3 "$SCRIPT_DIR/startset_arm.py" "$WORKDIR/ss_vm_base.tsv" \
                    "$ROOT_DIR/tests/startset/manifests/manifest_s2_vm_forced.tsv" "$ROOT_DIR")"
    ss_mc="$(echo "$ss_movers" | grep -oE 'mover_cases=[0-9]+' | cut -d= -f2)"
    # K35 FLOOR: half the 22,467 mover cases measured at landing (lane
    # ssbuild2, the first full run, all 2,560 forced-manifest corpus
    # blocks; it equals the static count of their case lines exactly;
    # docs/dev/lanes/ssbuild2_report.md §5b).
    SS_MOVER_FLOOR="${SS_MOVER_FLOOR:-11000}"
    echo "  $ss_movers (floor $SS_MOVER_FLOOR); giveup1-allowed=$ss_allowed"
    if [ "${ss_mc:-0}" -lt "$SS_MOVER_FLOOR" ]; then
        ss_bad=1
        echo "AXIS FAIL: [START-SET] product arm: ${ss_mc:-0} mover cases, below the floor $SS_MOVER_FLOOR" >&2
    fi
    if [ "$ss_bad" -eq 0 ]; then
        startset_verdict="OK — $ss_line; ${ss_mc} mover cases; giveup1-allowed=$ss_allowed"
    else
        startset_verdict="FAIL — $ss_line"
        fail=1
    fi
    echo "  $startset_verdict"
fi

# ============================================================================
# [START-SET] stage 3, THE DFA HAT's population under the plain `-fno-start-set`
# bit-axis job (the ss3 D6 panel's checks-M3). The product arm above counts the
# VM hat only (`--engine=vm` has no DFA scan); the DFA hat's movers are reached
# by the AUTO sweep, so its answer identity rides the plain job's comparison
# against the default baseline, and this counts how much of that comparison
# the DFA hat actually reached: the baseline's cases whose block is in the
# stage-3 mover manifest (tests/startset/manifests/manifest_s3_dfa.tsv), held
# to a floor so a sweep that stopped reaching the movers fails rather than
# reading clean. Selected with the plain job (empty AXES= or `-fno-start-set`).
# ============================================================================
dfahat_verdict="not run (filtered out by AXES=)"
if [ -z "$AXES" ] || case " $AXES " in (*" -fno-start-set "*) true ;; (*) false ;; esac; then
    dh_movers="$(python3 "$SCRIPT_DIR/startset_arm.py" "$BASE_DUMP" \
                    "$ROOT_DIR/tests/startset/manifests/manifest_s3_dfa.tsv" "$ROOT_DIR")"
    dh_mc="$(echo "$dh_movers" | grep -oE 'mover_cases=[0-9]+' | cut -d= -f2)"
    # K35 FLOOR: half the 1,378 DFA-hat mover cases at the ssfix3 panel fixes
    # (71 corpus blocks in 18 files; it equals the static count of their case
    # lines; docs/dev/lanes/ssbuild3_report.md, "Panel fixes (ssfix3)").
    DH_MOVER_FLOOR="${DH_MOVER_FLOOR:-689}"
    echo
    echo "axes: [START-SET] DFA hat under -fno-start-set: ${dh_movers#startset arm: } (floor $DH_MOVER_FLOOR)"
    if [ "${dh_mc:-0}" -lt "$DH_MOVER_FLOOR" ]; then
        dfahat_verdict="FAIL — ${dh_mc:-0} DFA-hat mover cases in the baseline, below the floor $DH_MOVER_FLOOR"
        echo "AXIS FAIL: [START-SET] $dfahat_verdict" >&2
        fail=1
    else
        dfahat_verdict="OK — ${dh_mc} DFA-hat mover cases compared by the -fno-start-set job (floor $DH_MOVER_FLOOR)"
    fi
    echo "  $dfahat_verdict"
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
echo "DIAL-S3 (tune refusal-set, keyed): $dial_s3_verdict"
echo "-futf-check arm (contract, own oracle): $utfcheck_verdict"
echo "[START-SET] product arm (--engine=vm x -fno-start-set): $startset_verdict"
echo "[START-SET] DFA hat population (-fno-start-set vs default): $dfahat_verdict"
echo "HARNESS_BATCH: $HARNESS_BATCH"
echo "total wall time: $((t_end - t_start))s"
if [ "$fail" -ne 0 ]; then
    echo "run_axes.sh: FAILED — see AXIS FAIL lines above" >&2
    exit 1
fi
# THE CLOSING SENTENCE NAMES THE TIER, because since [CC-DIFF] STEP 2 "all
# axes" is a claim whose SCOPE depends on AXES_FULL: a default run swept two
# of `--vm-entry-shape`'s four rungs, and a summary that read the same either
# way would let a two-rung result be quoted as a four-rung one. DIAL-S3's own
# verdict is named too, for the identical reason — "all axes answer-identical"
# says nothing about the refusal SET, which is a different property this
# script checks separately.
echo "run_axes.sh: all axes answer-identical to default (documented refusal populations excepted); --vm-entry-shape tier: $_shape_tier; oracle cross-check $oracle_verdict; DIAL-S3 $dial_s3_verdict; -futf-check arm $utfcheck_verdict"
exit 0
