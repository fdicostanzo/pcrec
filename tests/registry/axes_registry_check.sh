#!/usr/bin/env bash
# tests/registry/axes_registry_check.sh — [CHK-2] piece 1(a): THE REGISTRY
# CHECK for `pcrec --list-axes` — CODE (the dump) vs SPEC (docs/spec/
# tuning.md + cli/main.c), in BOTH directions, PC-3's own shape (a named
# assertion per row, a PASS/FAIL summary, never a bare count).
#
# WHY THIS IS THE INDEPENDENT SIDE (docs/dev/learnings.md §3: "a control
# must not share a source with what it controls"). `--list-axes` (src/parse/
# axes_dump.c) reads live off src/gen/emit_dfa.c's own candidate arrays for
# name/deny and off lib/pcrec.h's enum symbols for the predicate axes' bit
# VALUES — so the dump and lib/pcrec.h/emit_dfa.c share a source and cannot
# catch each other drifting. This script reads the dump against TWO OTHER
# files the dump never opens: docs/spec/tuning.md (the axis's own §2.N
# section and its own "(bit N)" heading) and cli/main.c (the flag parser).
# Both directions are checked (dump -> spec, spec -> dump), because a
# one-directional check only catches a row the dump ADDED without spec
# support; the reverse — a documented axis the dump stopped reporting — is
# the more dangerous silent loss and needs its own sweep.
#
# DIRECTION 3 (added on manager review, 2026-08-28): the charter's own
# direction (a) reads "every dumped row has its tuning.md §2.N, its §6.3
# VALUE and its CLI flag, every spec value appears in the dump" — the first
# two revisions covered the bit/flag/heading half and skipped the STAMP
# VALUE half. "§6.3" is `docs/spec/match_api.md` §6.3 ("The compile-time
# mirror: observability macros") — the D46 stamp family's own home, cited
# by name throughout `docs/spec/tuning.md` for exactly this reason. FIVE
# stamp macros have a CLEAN, closed value-set stated there (a markdown
# table for `RX_DFA_TABLE`/`RX_DFA_PREFILTER`, an unambiguous pair of
# string literals in prose/code for `RX_VM_PREFILTER`/`RX_ENGINE`, and —
# [REG-SV], 2026-08-30 — multi-line prose for `RX_UNROLL_K_WHY`, whose own
# `extract_prose_values` extraction shape is documented at that function)
# and are checked both directions with NO exception. The D46 family's NINE named
# bit constants (`PCREC_VM_RUNG_*`/`_STRAT_*`/`_PRUNE_*`) are NOT declared
# in `lib/pcrec.h` at all — match_api.md §6.3's own [ABI-NS] paragraph says
# why: they are EMITTED-ARTIFACT text, in the shared `PCREC_RX_ABI_H` block
# `src/gen/emit_dfa.c`'s `emit_rx_abi_types` writes literally (grep
# `#define PCREC_VM_(RUNG|STRAT|PRUNE)_` there) — so THAT file, not
# lib/pcrec.h, is this direction's source for them. Three of the nine
# (`_RUNG_CURSOR`/`_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`) are a NAMED,
# CITED exception to the spec->dump sweep: no `-fno-*` flag denies "use the
# cursor rung" or a specific frames sub-rung individually (`src/gen/
# CLAUDE.md`'s `[ENG-BREP]` rung-ladder section — only `-fno-revdet` and
# `-fno-counter` address a rung of their own), so no axis in this dump can
# ever carry those three as a candidate's `stamp_value`; the six directly
# controllable pairs (POSSESSIVE/BACKTRACKING, REVDET, COUNTER, CLAMPED/
# UNCLAMPED) are checked in full both directions.
# `RX_DFA_TABLE`'s exception is DISCHARGED, not merely narrowed ([REG-SV],
# 2026-08-30). `"mixed"`/`"none"` are ARTIFACT-LEVEL COMPOSITIONS of the
# forward and reverse machine's own per-machine choice (match_api.md §6.3:
# "the choice is per machine... 'mixed' the forward and reverse machines
# took different forms") and were never a candidate this dump's per-MACHINE
# `table` axis could select on its own — true when this exception was first
# written and unchanged by this pass. What changed is that "never a
# candidate" does not mean "never a ROW": `src/parse/axes_dump.c` now hand-
# states both as `kind=predicate` rows attached to axis `table` (order 3/4,
# `emit_table_composite_rows`), the same shape a predicate row already has
# everywhere else in this dump, so the check below has no exception left to
# carry for this macro either.
#
# DIRECTION 3B — THE EMITTER-SOURCE LEG (team-lead review, 2026-08-30,
# [REG-SV]). Direction 3 above is dump-vs-DOCS: both `src/parse/axes_dump.c`
# and `docs/spec/match_api.md` are HAND-WRITTEN, so a value added to the
# code that actually WRITES a stamp — `src/core/compile.c`'s
# `cx.size_term_why` chain, `src/gen/emit_dfa.c`'s `dfa_table_name` — and
# forgotten in BOTH would still pass every check above. Two more
# `check_value_set` calls close that, for the two macros whose stamp is
# hand-stated rather than read live off an emitter array (`RX_UNROLL_K_WHY`
# in full, `RX_DFA_TABLE`'s two composite values only — its two list-sourced
# values are already a live read and need no third leg): the dump against
# the DERIVATION ITSELF, using `extract_prose_values`/`extract_c_return_
# values` (own headers below) rather than the docs.
#
# Usage: bash tests/registry/axes_registry_check.sh
# Env: PCREC (default build/pcrec), TUNING (default docs/spec/tuning.md —
#   override to point at a doctored copy, e.g. for the sabotage
#   demonstration below), CLIMAIN (default cli/main.c, same override use),
#   MATCHAPI (default docs/spec/match_api.md, §6.3's own stamp-value
#   tables — same override use), EMITDFA (default src/gen/emit_dfa.c, the
#   nine D46 bit constants' own literal source — same override use),
#   KEEP=1 to keep the work directory.

set -u
export LC_ALL=C   # K35 — see tests/harness/run.sh's own header for why

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/table.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"   # [K37] resolves TIMEOUT_BIN for this file's own bare compiler call below

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
TUNING="${TUNING:-$ROOT_DIR/docs/spec/tuning.md}"
CLIMAIN="${CLIMAIN:-$ROOT_DIR/cli/main.c}"
MATCHAPI="${MATCHAPI:-$ROOT_DIR/docs/spec/match_api.md}"
EMITDFA="${EMITDFA:-$ROOT_DIR/src/gen/emit_dfa.c}"
COMPILEC="${COMPILEC:-$ROOT_DIR/src/core/compile.c}"   # [REG-SV] the size-term derivation's own source — see the emitter-source leg below
KEEP="${KEEP:-0}"

if [ ! -x "$PCREC" ]; then
    echo "axes_registry: $PCREC not built — run 'make' first" >&2
    exit 1
fi
if [ ! -f "$TUNING" ]; then
    echo "axes_registry: FATAL: $TUNING not found" >&2
    exit 1
fi
if [ ! -f "$CLIMAIN" ]; then
    echo "axes_registry: FATAL: $CLIMAIN not found" >&2
    exit 1
fi
if [ ! -f "$MATCHAPI" ]; then
    echo "axes_registry: FATAL: $MATCHAPI not found" >&2
    exit 1
fi
if [ ! -f "$EMITDFA" ]; then
    echo "axes_registry: FATAL: $EMITDFA not found" >&2
    exit 1
fi
if [ ! -f "$COMPILEC" ]; then
    echo "axes_registry: FATAL: $COMPILEC not found" >&2
    exit 1
fi

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-axesreg.XXXXXX")"
cleanup() { [ "$KEEP" = "1" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

TSV="$WORKDIR/axes.tsv"
"$TIMEOUT_BIN" 60 "$PCREC" --list-axes > "$TSV" || { echo "axes_registry: FATAL: $PCREC --list-axes failed" >&2; exit 1; }   # [K37] bounded, tests/reject/run_reject_tests.sh's own --list-syntax precedent

npass=0
nfail=0
ok()   { npass=$((npass + 1)); echo "PASS: $1"; }
bad()  { nfail=$((nfail + 1)); echo "FAIL: $1" >&2; }

# ============================================================================
# HEADER TRUTHFULNESS (table_contract.md) — every row's field count agrees
# with the header's own declared count, before anything below trusts a
# column index the header claims to have.
# ============================================================================
if table_check_truthfulness "$TSV" >"$WORKDIR/trutherr" 2>&1; then
    ok "table_check_truthfulness: every row of --list-axes' TSV matches its header's declared field count"
else
    bad "table_check_truthfulness: $(cat "$WORKDIR/trutherr")"
fi

MAP="$(table_awk_map "$TSV" axis order candidate kind stamp_macro stamp_value \
        deny_macro deny_bit force_macro force_bit cli_flag applies)" || {
    echo "axes_registry: FATAL: could not resolve --list-axes' own columns by name" >&2
    exit 1
}

nrows="$(grep -vc '^#' "$TSV")"
if [ "$nrows" -lt 1 ]; then
    echo "axes_registry: FATAL: --list-axes produced ZERO data rows — extraction is broken (docs/dev/learnings.md §3: hard-fail on empty, never silently measure nothing)" >&2
    exit 1
fi
ok "non-vacuity: --list-axes produced $nrows data row(s)"

# ============================================================================
# lib/pcrec.h's OWN registry, derived the same proven way run_axes.sh
# derives it (tests/axes/run_axes.sh's own header comment) — never
# hand-copied. This is a SECOND, independent read of lib/pcrec.h: the dump
# itself was built from the SAME header's enum symbols (src/parse/
# axes_dump.c's V() macro), but that is dump-vs-header agreement BY
# CONSTRUCTION for the predicate axes' bit numbers; what this script adds is
# dump-vs-header agreement checked FROM OUTSIDE the compiled binary, over a
# plain-text re-read, which catches the case a stale BUILT binary would hide
# (a header edit with no rebuild).
declare -A HDR_BIT=()   # macro -> bit
while IFS=$'\t' read -r macro bit; do
    [ -n "$macro" ] || continue
    HDR_BIT[$macro]="$bit"
done < <(grep -oE 'PCREC_(NO|FORCE)_[A-Z_]+ *= *1u << [0-9]+' "$ROOT_DIR/lib/pcrec.h" \
          | sed -E 's/^(PCREC_(NO|FORCE)_[A-Z_]+) *= *1u << ([0-9]+)$/\1\t\3/')
if [ "${#HDR_BIT[@]}" -eq 0 ]; then
    echo "axes_registry: FATAL: derived ZERO PCREC_(NO|FORCE)_* bit constants from lib/pcrec.h" >&2
    exit 1
fi

# cli/main.c's own flag<->macro pairing, the identical awk run_axes.sh uses
# (tests/axes/run_axes.sh's own header comment: "remembers the most
# recently seen `strcmp(a, "-...")` literal, and pairs it with the next
# `opt.flags |= MACRO` line").
declare -A CLI_MACRO=()   # cli flag text -> macro
while IFS=$'\t' read -r macro flagtext; do
    [ -n "$macro" ] && CLI_MACRO["$flagtext"]="$macro"
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
' "$CLIMAIN")

# tuning.md §2's own "(bit N)" headings, restricted to the THIRTEEN-AXES
# section exactly as run_axes.sh restricts it.
# THE ANCHOR IS THE SECTION NUMBER, NEVER THE COUNT WORD. It read
# `/^## 2\. The thirteen axes/`; [OPT-K] added an axis, correctly renamed the
# heading, and this range then matched NOTHING -- so `doc_bits_raw` came back
# empty and DIRECTION 2's first arm compared against an empty documented
# column. tuning.md's heading no longer carries a count at all.
doc_bits_raw="$(sed -n '/^## 2\./,/^## 3\./p' "$TUNING" \
    | grep -oE '\(bit [0-9]+\)' | grep -oE '[0-9]+')"

# ============================================================================
# DIRECTION 1: DUMP -> SOURCES. Every dumped row with a deny/force macro
# must (a) exist in lib/pcrec.h at the SAME bit the dump printed, (b) if it
# carries a cli_flag, that flag must be one cli/main.c's parser actually
# accepts AND pairs with the SAME macro, (c) tuning.md must document that
# bit with a "(bit N)" heading.
# ============================================================================
check_macro_bit() {
    local macro="$1" dumped_bit="$2" axis="$3" cand="$4"
    if [ -z "${HDR_BIT[$macro]:-}" ]; then
        bad "[$axis/$cand] dumped deny/force macro '$macro' is not defined in lib/pcrec.h at all"
        return
    fi
    if [ "${HDR_BIT[$macro]}" != "$dumped_bit" ]; then
        bad "[$axis/$cand] dumped bit $dumped_bit for '$macro' disagrees with lib/pcrec.h's own bit ${HDR_BIT[$macro]}"
        return
    fi
    ok "[$axis/$cand] '$macro' (bit $dumped_bit) matches lib/pcrec.h"
}

check_cli_flag() {
    local flagtext="$1" macro="$2" axis="$3" cand="$4"
    if [ -z "${CLI_MACRO[$flagtext]:-}" ]; then
        bad "[$axis/$cand] cli_flag '$flagtext' is not a spelling cli/main.c's parser accepts (or the awk pairing missed it)"
        return
    fi
    if [ "${CLI_MACRO[$flagtext]}" != "$macro" ]; then
        bad "[$axis/$cand] cli_flag '$flagtext' pairs with '${CLI_MACRO[$flagtext]}' in cli/main.c, not the dumped '$macro'"
        return
    fi
    ok "[$axis/$cand] cli_flag '$flagtext' pairs with '$macro' in cli/main.c"
}

check_tuning_bit_documented() {
    local bit="$1" axis="$2" cand="$3"
    if ! grep -qE "\(bit $bit\)" "$TUNING"; then
        bad "[$axis/$cand] bit $bit has no '(bit $bit)' heading anywhere in $TUNING"
        return
    fi
    ok "[$axis/$cand] bit $bit is documented in $TUNING"
}

seen_dumped_bits=""   # accumulates "N" per bit this dump names, for direction 2

while IFS=$'\x01' read -r axis order candidate kind stamp_macro stamp_value \
                        deny_macro deny_bit force_macro force_bit cli_flag applies; do
    [ -n "$axis" ] || continue
    if [ -n "$deny_macro" ]; then
        check_macro_bit "$deny_macro" "$deny_bit" "$axis" "$candidate"
        seen_dumped_bits="$seen_dumped_bits $deny_bit"
    fi
    if [ -n "$force_macro" ]; then
        check_macro_bit "$force_macro" "$force_bit" "$axis" "$candidate"
        seen_dumped_bits="$seen_dumped_bits $force_bit"
    fi
    if [ -n "$cli_flag" ]; then
        # vm-prefilter's one row carries TWO flags ("-fno-prefilter /
        # -fprefilter") pairing with its deny and force macro respectively —
        # split on " / " and check each half against its own macro.
        case "$cli_flag" in
            *" / "*)
                f1="${cli_flag%% / *}"; f2="${cli_flag##* / }"
                [ -n "$deny_macro" ]  && check_cli_flag "$f1" "$deny_macro" "$axis" "$candidate"
                [ -n "$force_macro" ] && check_cli_flag "$f2" "$force_macro" "$axis" "$candidate"
                ;;
            "--engine="*)
                # the coarse axis: not through pcrec_options.flags at all,
                # so there is no macro to pair it with — just confirm
                # cli/main.c's parser recognises the spelling's PREFIX.
                if ! grep -qF '"--engine="' "$CLIMAIN" && ! grep -qF "\"--engine=\"" "$CLIMAIN"; then
                    bad "[$axis/$candidate] cli_flag '$cli_flag' but cli/main.c has no --engine= parsing site"
                else
                    ok "[$axis/$candidate] cli_flag '$cli_flag' — cli/main.c parses --engine="
                fi
                ;;
            *)
                mac="${deny_macro:-$force_macro}"
                if [ -n "$mac" ]; then
                    check_cli_flag "$cli_flag" "$mac" "$axis" "$candidate"
                fi
                ;;
        esac
    fi
    if [ -n "$deny_bit" ]; then
        check_tuning_bit_documented "$deny_bit" "$axis" "$candidate"
    fi
    if [ -n "$force_bit" ]; then
        check_tuning_bit_documented "$force_bit" "$axis" "$candidate"
    fi
# Field separator here is \001 (SOH), NOT \t: bash's `IFS=$'\t' read`
# treats tab as IFS WHITESPACE regardless of what IFS is set to, so runs of
# empty tab-delimited fields (every row with an unset deny/force column)
# silently COLLAPSE and every field after the first empty one shifts left —
# reproduced live while writing this check, and the exact bug
# tests/lib/table.sh's own header comment names ("never on IFS whitespace,
# which is why this is not a bash `read -a` on the raw line"). \001 is not
# in bash's whitespace class, so empty fields survive.
done < <(awk -F'\t' $MAP '!/^#/ {
    print $axis"\001"$order"\001"$candidate"\001"$kind"\001"$stamp_macro"\001"$stamp_value"\001"$deny_macro"\001"$deny_bit"\001"$force_macro"\001"$force_bit"\001"$cli_flag"\001"$applies
}' "$TSV")

# Every "list"/"both" axis's candidates must have an authored applies() —
# the dump's own placeholder text names an unauthored one, so grep for it
# rather than re-parsing: a candidate the accessor sees but this file's
# AXIS_DESC table does not is a FINDING (a lane added a candidate without
# telling axes_dump.c about it), never silently accepted.
if grep -qF 'no description authored for this candidate yet' "$TSV"; then
    while IFS=$'\t' read -r axis _ candidate _; do
        [ -n "$axis" ] || continue
        bad "[$axis/$candidate] has NO authored description in src/parse/axes_dump.c's AXIS_DESC table (a candidate landed with no edit there)"
    done < <(awk -F'\t' $MAP '!/^#/ && $applies ~ /no description authored/ {print $axis"\t"$order"\t"$candidate"\t"$kind}' "$TSV")
else
    ok "every list/both-axis candidate has an authored one-line description"
fi

# ============================================================================
# DIRECTION 2: SOURCES -> DUMP. Every bit tuning.md documents, and every bit
# lib/pcrec.h defines at or above the deny/force family's low bound of 4, must
# appear in the dump somewhere (as a deny_bit or a force_bit on some row) —
# the reverse loss: an axis quietly dropped from the dump.
# ============================================================================
dumped_bits_sorted="$(printf '%s\n' $seen_dumped_bits | sort -n -u)"
doc_bits_sorted="$(printf '%s\n' $doc_bits_raw | sort -n -u)"

missing_from_dump=""
for b in $doc_bits_sorted; do
    if ! grep -qxF "$b" <<< "$dumped_bits_sorted"; then
        missing_from_dump="$missing_from_dump $b"
    fi
done
if [ -n "$missing_from_dump" ]; then
    bad "tuning.md documents bit(s)$missing_from_dump with a '(bit N)' heading, but --list-axes names none of them (an axis dropped from the dump)"
else
    ok "every '(bit N)' heading tuning.md's §2 documents ($( printf '%s' "$doc_bits_sorted" | tr '\n' ' ' )) appears in --list-axes' output"
fi

# NO UPPER BOUND. The LOW bound is the one doing real work -- bits below 4
# are unrelated `1u << N` constants in the same header (PCREC_CASELESS and
# friends) and must never be swept in -- while the top of the deny/force
# family moves every time an axis is added. It was `-le 15`, the family's
# extent on the day this was written, and [OPT-K]'s bit 16 was therefore
# FILTERED OUT BEFORE THE COMPARISON: `-fno-offset-skip` could have been
# absent from --list-axes entirely and this arm would have printed `ok`,
# naming bits 4-15. That is this check's own claim failing at the one thing
# it exists to assert, silently. `tests/axes/run_axes.sh` had the identical
# defect and was caught only because its PROSE anchor broke loudly first.
hdr_bits_family=""
for macro in "${!HDR_BIT[@]}"; do
    b="${HDR_BIT[$macro]}"
    if [ "$b" -ge 4 ] 2>/dev/null; then
        hdr_bits_family="$hdr_bits_family $b"
    fi
done
hdr_bits_sorted="$(printf '%s\n' $hdr_bits_family | sort -n -u)"
hdr_bits_lo="$(printf '%s' "$hdr_bits_sorted" | head -1)"
hdr_bits_hi="$(printf '%s' "$hdr_bits_sorted" | tail -1)"
missing_from_dump2=""
for b in $hdr_bits_sorted; do
    if ! grep -qxF "$b" <<< "$dumped_bits_sorted"; then
        missing_from_dump2="$missing_from_dump2 $b"
    fi
done
if [ -n "$missing_from_dump2" ]; then
    bad "lib/pcrec.h defines PCREC_NO_*/FORCE_* bit(s)$missing_from_dump2 (of bits $hdr_bits_lo-$hdr_bits_hi found in the header) that --list-axes names on no row (an axis landed in the header with no dump coverage — e.g. a new axis's list not yet reached by src/parse/axes_dump.c's predicate table)"
else
    ok "every PCREC_NO_*/PCREC_FORCE_* bit lib/pcrec.h defines at or above bit 4 ($( printf '%s' "$hdr_bits_sorted" | tr '\n' ' ' )) appears in --list-axes' output"
fi

# ============================================================================
# DIRECTION 3: STAMP VALUES, both ways (docs/spec/match_api.md §6.3 — see
# this script's own header for which macros have a closed value set there
# and the two named/cited exceptions).
# ============================================================================

# extract_md_table_values FILE ANCHOR — every `"word"` inside a markdown
# table's rows, where the table is the first one found after the line
# containing ANCHOR (verbatim substring match, `index()`, no regex
# metacharacters to escape). Table rows in match_api.md are indented under
# a bullet (`  | value | meaning |`), so the row test is `^[ \t]*\|`, not
# `^\|` — the bug this script's own author hit live while writing this
# direction: an UN-indented anchor match, tested with a naive `^\|`, silently
# skipped the indented table entirely and fell through to the NEXT `^\|`
# line in the file (a different macro's table), which is a silent WRONG
# TABLE read rather than an empty one — caught only by eyeballing the first
# run's output against the file by hand. Never trust "some column
# extracted" as proof of "the right column was read" for a markdown table.
extract_md_table_values() {
    local file="$1" anchor="$2"
    awk -v anchor="$anchor" '
        index($0, anchor) { found=1; n=0; next }
        found && /^[ \t]*\|/ {
            n++
            if (match($0, /`"[a-zA-Z-]+"`/)) print substr($0, RSTART+2, RLENGTH-4)
            next
        }
        found && n>0 { found=0 }
    ' "$file"
}

# extract_line_values FILE PATTERN — every distinct lowercase `"word"` on a
# line matching PATTERN (extended regex). Used for the two macros whose
# value set is a bare pair of string literals in prose/code rather than a
# markdown table (`RX_VM_PREFILTER`, `RX_ENGINE`).
#
# PASS A WORD-BOUNDED PATTERN (`\<NAME\>`). This function harvests every
# lowercase literal on a MATCHING LINE, so a pattern that also matches a
# prefixed sibling (`RX_VM_PREFILTER_LANG`, `RX_ENGINE_WHY`, `RX_ENGINE_SEL`)
# silently imports that macro's value set into this one's. Both call sites are
# bounded; the unbounded one cost a red battery on 2026-08-29.
extract_line_values() {
    local file="$1" pattern="$2"
    grep -E "$pattern" "$file" | grep -oE '"[a-z]+"' | tr -d '"' | sort -u
}

# extract_prose_values FILE ANCHOR — every distinct lowercase (hyphens
# allowed) `"quoted"` literal from the ANCHOR's own line through the next
# blank line. [REG-SV]: `RX_UNROLL_K_WHY`'s SEVEN values
# (docs/spec/match_api.md §6.3) are neither a markdown table
# (extract_md_table_values) nor confined to one line carrying a literal
# default-prefix `RX_...` artifact excerpt (extract_line_values, which
# `RX_VM_PREFILTER`/`RX_ENGINE` both have and this macro does not —
# match_api.md spells it `<PREFIX>_UNROLL_K_WHY` throughout) — they are
# ordinary multi-line PROSE, one bullet, seven `` `"value"` `` code-spans
# spread across it. ANCHOR ON THE MACRO NAME, NEVER A COUNT WORD ("SEVEN")
# — this script's own standing lesson (see the RX_DFA_PREFILTER anchor note
# above), stated here a fourth time because an eighth value landing must
# not silently break the anchor that finds the other seven.
extract_prose_values() {
    local file="$1" anchor="$2"
    awk -v anchor="$anchor" '
        index($0, anchor) { found=1 }
        found { print }
        found && /^[ \t]*$/ { found=0 }
    ' "$file" | grep -oE '"[a-z-]+"' | tr -d '"' | sort -u
}

# extract_c_return_values FILE FUNC_SIG_ANCHOR — every distinct lowercase
# (hyphens allowed) literal appearing in a `return "value";` statement
# inside ONE C function, bounded by that function's own column-0 opening
# and closing braces (this project's own emitter style, src/gen/CLAUDE.md).
# [REG-SV] THE EMITTER-SOURCE LEG (team-lead review, 2026-08-30): the two
# legs above compare the DUMP (src/parse/axes_dump.c's hand-stated rows)
# against DOCS (match_api.md prose) — both HAND-WRITTEN, so a value added to
# the code that actually WRITES a stamp and forgotten in both the dump and
# the docs would pass every existing check. This is the third leg: the CODE
# itself, independent of both.
#
# SCOPED TO `return "..."` ON PURPOSE, not every quoted string in the
# function body. `RX_DFA_TABLE`'s own emitter (src/gen/emit_dfa.c's
# `dfa_table_name`) carries a COMMENT that quotes `"premultiplied"` as
# prose ("...let the stamp say \"premultiplied\" about an artifact...") —
# a value that function never RETURNS, since `"premultiplied"`/`"indexed"`
# come back through the variable `f`, not a literal, in this function. A
# naive whole-body grep would import that comment's word as if it were a
# fourth return value and read a spurious mismatch against the dump's real
# four-value set; scoping to the `return "..."` shape excludes it and
# extracts exactly what the function can actually produce as a literal
# (here: `mixed`/`none`, matched against the dump's two HAND-STATED
# composite rows only — `premultiplied`/`indexed` are already live-read
# from a different array by axes_dump.c itself, so they need no third leg).
extract_c_return_values() {
    local file="$1" anchor="$2"
    awk -v anchor="$anchor" '
        index($0, anchor) { infunc=1 }
        infunc && $0 == "{" { inbody=1; next }
        infunc && inbody && $0 == "}" { exit }
        infunc && inbody { print }
    ' "$file" | grep -oE 'return "[a-z-]+"' | grep -oE '"[a-z-]+"' | tr -d '"' | sort -u
}

# check_value_set MACRO SPEC_VALS DUMP_VALS EXCEPT — both directions for one
# macro. EXCEPT (space-separated, may be empty) names spec values that are
# NEVER expected back from the dump (a cited, structural exception — see
# this script's header), so they are excluded from the spec->dump sweep
# only, never from the dump->spec one (a value the dump prints that isn't
# in the exception list must still be a real spec value).
check_value_set() {
    local macro="$1" spec_vals="$2" dump_vals="$3" except="$4"
    # [REG-SV] a 5th, OPTIONAL arg names where spec_vals came from, for the
    # bad()/ok() prose — every pre-existing call omits it and reads exactly
    # as before (docs/spec/match_api.md §6.3's table); the new emitter-source
    # leg calls below pass the real source (a C function/derivation) so a
    # failure message never claims a doc said something the EMITTER did.
    # NOT `${5:-...text with an apostrophe...}` — bash's own parameter-
    # expansion parser re-interprets a `'` inside `${VAR:-word}` as a quote
    # START even though the whole expression sits inside double quotes at
    # the outer level (measured: "unexpected EOF while looking for matching
    # `''" from exactly this shape), so the default is set with a plain
    # if/then instead, preserving the exact pre-[REG-SV] wording byte for
    # byte (docs/testing.md:2986 quotes it verbatim as a sabotage-transcript
    # example and must not go stale).
    local src_label="${5-}"   # `${5-}` is set-u safe (unset -> empty); default set below
    [ -z "$src_label" ] && src_label="docs/spec/match_api.md §6.3's own value-set table"
    local v miss=""
    for v in $dump_vals; do
        if ! grep -qxF "$v" <<< "$spec_vals"; then
            bad "[$macro] dump stamps value '$v' that $src_label for $macro does not list"
            miss=1
        fi
    done
    [ -z "$miss" ] && ok "[$macro] every dumped stamp_value ($( printf '%s' "$dump_vals" | tr '\n' ' ' )) is in $src_label"

    miss=""
    for v in $spec_vals; do
        grep -qxF "$v" <<< "$except" && continue
        if ! grep -qxF "$v" <<< "$dump_vals"; then
            bad "[$macro] $src_label documents value '$v' for $macro that --list-axes names on no row"
            miss=1
        fi
    done
    local except_disp="no exceptions"
    [ -n "$except" ] && except_disp="$(printf '%s' "$except" | tr '\n' ',' | sed 's/,$//')"
    [ -z "$miss" ] && ok "[$macro] every $src_label value for $macro (exceptions: $except_disp) appears in --list-axes' output"
}

dump_stamp_vals() {
    local macro="$1"
    awk -F'\001' -v m="$macro" '$5 == m && $6 != "" {print $6}' <<< "$axes_rows_dump"
}

# One extra pass over the dump, keyed the same \001 way the main loop reads
# it, so this direction does not have to re-run `pcrec --list-axes` (the
# TSV in $TSV is already read once above; re-deriving it here from the same
# file keeps this direction independent of the main loop's bash variables,
# which the main loop's own `while` has already consumed).
axes_rows_dump="$(awk -F'\t' $MAP '!/^#/ {
    print $axis"\001"$order"\001"$candidate"\001"$kind"\001"$stamp_macro"\001"$stamp_value
}' "$TSV")"

check_value_set "RX_DFA_TABLE" \
    "$(extract_md_table_values "$MATCHAPI" "2026-08-26: a THIRD")" \
    "$(dump_stamp_vals RX_DFA_TABLE)" \
    ""
# [REG-SV], 2026-08-30: NO MORE EXCEPTION HERE. "mixed"/"none" used to be a
# cited exclusion from the spec->dump sweep only (this script's own header,
# pre-[REG-SV] revision) — real spec values the dump could never produce as
# a row, because the per-machine `table` axis has only two candidates. The
# dump now carries them as two hand-stated composite rows (src/parse/
# axes_dump.c's `emit_table_composite_rows`, axis `table` order 3/4), so the
# exception is DISCHARGED rather than merely documented: both directions of
# this check now cover the macro's whole four-value set with no exclusion.

# [REG-SV] THE EMITTER-SOURCE LEG, 2026-08-30 (team-lead review): the check
# above is dump-vs-DOCS, both hand-written. This is dump-vs-CODE — the two
# composite values (`none`/`mixed`) against `dfa_table_name`'s own
# `return "..."` statements in src/gen/emit_dfa.c, the function that
# actually decides `RX_DFA_TABLE`'s value. `premultiplied`/`indexed` are
# deliberately NOT in this comparison's dump side or expected on the
# extractor's side: they are already live-read from `dfa_reprs[]` by
# `axes_dump.c` itself (never hand-typed), so a THIRD leg for them would
# just be checking a live read against itself. Only the two hand-stated
# rows need an independent source, and this is it. See
# `extract_c_return_values`'s own header for why the comment-noise trap
# (a `"premultiplied"` inside a comment two lines from a real return) is
# excluded by construction rather than by an exclusion list.
check_value_set "RX_DFA_TABLE (dfa_table_name composite values)" \
    "$(extract_c_return_values "$EMITDFA" 'static const char *dfa_table_name')" \
    "$(dump_stamp_vals RX_DFA_TABLE | grep -vxE 'premultiplied|indexed')" \
    "" \
    "src/gen/emit_dfa.c's dfa_table_name()"

# THE ANCHOR CARRIES NO COUNT. It read "its five values are the whole set";
# [OPT-K] added two values and correctly rewrote that sentence to "seven",
# after which the extractor found NO table and every one of the seven values
# — the four pre-existing ones included — was reported as undocumented. That
# is the THIRD count-in-prose pin this one change tripped (run_axes.sh's §2
# heading anchor and this file's own at line ~175 were the other two), so the
# rule is worth stating once here: anchor on the part of a sentence a new
# member does not change.
check_value_set "RX_DFA_PREFILTER" \
    "$(extract_md_table_values "$MATCHAPI" "values are the whole set")" \
    "$(dump_stamp_vals RX_DFA_PREFILTER)" \
    ""

# [ENG-ABS] axis G's stamp. THE ANCHOR CARRIES NO COUNT AND NO BACKTICK — the
# first for the reason the paragraph above records, the second because these
# anchors are double-quoted bash strings and a backtick in one is a command
# substitution. "is on every DFA" is unique in match_api.md and survives a
# value being added.
check_value_set "RX_DFA_MATCH" \
    "$(extract_md_table_values "$MATCHAPI" "is on every DFA")" \
    "$(dump_stamp_vals RX_DFA_MATCH)" \
    ""

# [OPT-5] axis `scan-edge`'s stamp. THE ANCHOR CARRIES NO COUNT — the rule two
# blocks up, restated because this macro's own spec sentence DOES name a
# number ("The four values below are…") and it was deliberately not used as
# the anchor for that reason. It also deliberately avoids the substring
# `RX_DFA_PREFILTER`'s anchor ("values are the whole set") occupies: the
# extractor takes the FIRST match, so a second paragraph containing that
# phrase would be harmless today and a silent mis-harvest the day the two
# paragraphs are reordered.
check_value_set "RX_DFA_SCAN_EDGE" \
    "$(extract_md_table_values "$MATCHAPI" "all this macro ever reads")" \
    "$(dump_stamp_vals RX_DFA_SCAN_EDGE)" \
    ""

# [OPT-4] THE PATTERN IS WORD-BOUNDED, as `RX_ENGINE`'s below always was.
# The bare `RX_VM_PREFILTER` matched `RX_VM_PREFILTER_LANG` too — a DIFFERENT
# macro with its OWN value set — and harvested its `"exact"` as one of this
# macro's, so the check reported a spec value `--list-axes` names on no row.
# The defect was in the extractor, not in the spec or the dump: `RX_ENGINE`'s
# call site was already `\<...\>` for exactly this hazard (`RX_ENGINE_WHY`),
# and this one had simply never had a prefixed sibling until 2026-08-29.
# `RX_ENGINE_SEL` landed the same day and would have done the same thing here.
check_value_set "RX_VM_PREFILTER" \
    "$(extract_line_values "$MATCHAPI" '\<RX_VM_PREFILTER\>')" \
    "$(dump_stamp_vals RX_VM_PREFILTER)" \
    ""

check_value_set "RX_ENGINE" \
    "$(extract_line_values "$MATCHAPI" '\<RX_ENGINE\>')" \
    "$(dump_stamp_vals RX_ENGINE)" \
    ""

# [OPT-4.1], 2026-08-30: `RX_ENGINE_SEL` HAD NO LEG HERE AT ALL. Its value set
# is a CLOSED vocabulary a consumer buckets on (the comparative bench's own O-8
# ask), and it was checked in exactly one place — a hardcoded `case` list in
# tests/codegen/run_prefilter_collapse.sh §7, which shares no source with the
# dump or the spec and so could not see either of them going stale. This is the
# gap [OPT-4.1] walked into while adding a sixth value; the leg is the fix, and
# it is written the way the two legs below it are, not as a special case.
#
# THE ANCHOR CARRIES NO COUNT, per this file's own thrice-learned rule: the
# paragraph above the table says "SIX VALUES" today and a seventh must not
# break the extractor. `the same decision as a TOKEN` is unique in match_api.md
# and survives a value being added.
check_value_set "RX_ENGINE_SEL" \
    "$(extract_md_table_values "$MATCHAPI" "the same decision as a TOKEN")" \
    "$(dump_stamp_vals RX_ENGINE_SEL)" \
    ""

# [OPT-4.1] THE EMITTER-SOURCE LEG, the same shape `RX_DFA_TABLE`'s and
# `RX_UNROLL_K_WHY`'s already have: the check above is dump-vs-DOCS, both
# hand-written, so a value added to `pcrec_engine_sel_name` and forgotten in
# BOTH would pass it. This is dump-vs-CODE — the function that actually decides
# the macro's value, read through its own `return "..."` statements. Its
# `default:` arm returns `"selected"`, so the extraction covers the whole set
# including the fallback and needs no exception.
check_value_set "RX_ENGINE_SEL (pcrec_engine_sel_name)" \
    "$(extract_c_return_values "$EMITDFA" 'const char *pcrec_engine_sel_name')" \
    "$(dump_stamp_vals RX_ENGINE_SEL)" \
    "" \
    "src/gen/emit_dfa.c's pcrec_engine_sel_name()"

# [REG-SV], 2026-08-30: `RX_UNROLL_K_WHY`'s seven-value set, previously
# uncovered by this direction entirely (no call at all — the gap the
# comparative bench found: the dump's two `size-term` rows both stamped an
# EMPTY `stamp_value`, so there was nothing here to check against). See
# `extract_prose_values`'s own header for why this macro needs a third
# extraction shape.
check_value_set "RX_UNROLL_K_WHY" \
    "$(extract_prose_values "$MATCHAPI" '`<PREFIX>_UNROLL_K_WHY`')" \
    "$(dump_stamp_vals RX_UNROLL_K_WHY)" \
    ""

# [REG-SV] THE EMITTER-SOURCE LEG, 2026-08-30 (team-lead review): the check
# above is dump-vs-DOCS, both hand-written — a value added to
# src/core/compile.c's own `cx.size_term_why = ...` derivation and forgotten
# in BOTH the dump and match_api.md would still pass it. This is dump-vs-
# CODE: the seven literals of that derivation chain itself, independent of
# both. `extract_prose_values` (above) works unmodified here — the anchor
# is the assignment's own unique text, and the chain runs to the next blank
# line exactly as the match_api.md bullet does, with no comment interleaved
# to filter out (unlike RX_DFA_TABLE's leg above, this one needs no
# `return`-scoping: the whole seven-line ternary IS the seven literals).
check_value_set "RX_UNROLL_K_WHY (compile.c cx.size_term_why derivation)" \
    "$(extract_prose_values "$COMPILEC" 'cx.size_term_why =')" \
    "$(dump_stamp_vals RX_UNROLL_K_WHY)" \
    "" \
    "src/core/compile.c's cx.size_term_why derivation"

# The nine D46 bit constants: NOT in lib/pcrec.h (they are emitted-artifact
# text — match_api.md §6.3's own [ABI-NS] paragraph), so EMITDFA (the
# literal #define block emit_rx_abi_types writes) is this direction's
# source, independent of both the dump's hand-typed strings (axes_dump.c's
# stamp_value literals are NOT stringified from a real symbol the way the
# deny/force bit values are — this check is what catches THAT drift risk)
# and of lib/pcrec.h (Direction 1/2 above's source).
emitdfa_bits="$(grep -oE '#define PCREC_VM_(RUNG|STRAT|PRUNE)_[A-Z_]+ +0x[0-9a-f]+u' "$EMITDFA" \
    | awk '{print $2}')"
if [ -z "$emitdfa_bits" ]; then
    echo "axes_registry: FATAL: derived ZERO PCREC_VM_(RUNG|STRAT|PRUNE)_* constants from $EMITDFA" >&2
    exit 1
fi

dumped_bit_const_vals="$(dump_stamp_vals RX_VM_RUNGS
dump_stamp_vals RX_VM_STRATS
dump_stamp_vals RX_VM_PRUNES)"

miss=""
for v in $dumped_bit_const_vals; do
    if ! grep -qxF "$v" <<< "$emitdfa_bits"; then
        bad "[D46 bit constants] dump stamps '$v' that $EMITDFA's own emit_rx_abi_types literal block does not define"
        miss=1
    fi
done
[ -z "$miss" ] && ok "[D46 bit constants] every dumped RUNG/STRAT/PRUNE constant name ($( printf '%s' "$dumped_bit_const_vals" | tr '\n' ' ' )) is defined in $EMITDFA"

# The three ladder members with no individual deny flag — see this script's
# header for the citation. Named here by their FULL constant name so the
# exception is unambiguous rather than a bare word a future rename could
# silently stop matching.
bit_const_except="PCREC_VM_RUNG_CURSOR
PCREC_VM_RUNG_FRAMES_BOUNDED
PCREC_VM_RUNG_FRAMES_UNBOUNDED"

miss=""
for v in $emitdfa_bits; do
    grep -qxF "$v" <<< "$bit_const_except" && continue
    if ! grep -qxF "$v" <<< "$dumped_bit_const_vals"; then
        bad "[D46 bit constants] $EMITDFA defines '$v' (not in the cited no-individual-flag exception list) that --list-axes names on no row"
        miss=1
    fi
done
[ -z "$miss" ] && ok "[D46 bit constants] every $EMITDFA-defined RUNG/STRAT/PRUNE constant with its own axis (except the three ladder-fallback rungs named in this script's header) appears in --list-axes' output"

echo
echo "== Summary =="
echo "checks passed: $npass"
echo "checks failed: $nfail"
[ "$nfail" -eq 0 ]
