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
# by name throughout `docs/spec/tuning.md` for exactly this reason. Four
# stamp macros have a CLEAN, closed value-set stated there (a markdown
# table for `RX_DFA_TABLE`/`RX_DFA_PREFILTER`, an unambiguous pair of
# string literals in prose/code for `RX_VM_PREFILTER`/`RX_ENGINE`) and are
# checked both directions with NO exception. The D46 family's NINE named
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
# `RX_DFA_TABLE`'s own spec table also has a real, cited exception:
# `"mixed"`/`"none"` are ARTIFACT-LEVEL COMPOSITIONS of the forward and
# reverse machine's own per-machine choice (match_api.md §6.3: "the choice
# is per machine... 'mixed' the forward and reverse machines took different
# forms"), never a candidate this dump's per-MACHINE `table` axis could
# select on its own — so only `"premultiplied"`/`"indexed"` are expected
# back from the dump, and are.
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

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
TUNING="${TUNING:-$ROOT_DIR/docs/spec/tuning.md}"
CLIMAIN="${CLIMAIN:-$ROOT_DIR/cli/main.c}"
MATCHAPI="${MATCHAPI:-$ROOT_DIR/docs/spec/match_api.md}"
EMITDFA="${EMITDFA:-$ROOT_DIR/src/gen/emit_dfa.c}"
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

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-axesreg.XXXXXX")"
cleanup() { [ "$KEEP" = "1" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

TSV="$WORKDIR/axes.tsv"
"$PCREC" --list-axes > "$TSV" || { echo "axes_registry: FATAL: $PCREC --list-axes failed" >&2; exit 1; }

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
doc_bits_raw="$(sed -n '/^## 2\. The thirteen axes/,/^## 3\./p' "$TUNING" \
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
# lib/pcrec.h defines in the deny/force family's own 4..15 range, must
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

hdr_bits_45_15=""
for macro in "${!HDR_BIT[@]}"; do
    b="${HDR_BIT[$macro]}"
    if [ "$b" -ge 4 ] 2>/dev/null && [ "$b" -le 15 ] 2>/dev/null; then
        hdr_bits_45_15="$hdr_bits_45_15 $b"
    fi
done
hdr_bits_sorted="$(printf '%s\n' $hdr_bits_45_15 | sort -n -u)"
missing_from_dump2=""
for b in $hdr_bits_sorted; do
    if ! grep -qxF "$b" <<< "$dumped_bits_sorted"; then
        missing_from_dump2="$missing_from_dump2 $b"
    fi
done
if [ -n "$missing_from_dump2" ]; then
    bad "lib/pcrec.h defines PCREC_NO_*/FORCE_* bit(s)$missing_from_dump2 (range 4-15) that --list-axes names on no row (an axis landed in the header with no dump coverage — e.g. a new axis's list not yet reached by src/parse/axes_dump.c's predicate table)"
else
    ok "every PCREC_NO_*/PCREC_FORCE_* bit lib/pcrec.h defines in range 4-15 ($( printf '%s' "$hdr_bits_sorted" | tr '\n' ' ' )) appears in --list-axes' output"
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
extract_line_values() {
    local file="$1" pattern="$2"
    grep -E "$pattern" "$file" | grep -oE '"[a-z]+"' | tr -d '"' | sort -u
}

# check_value_set MACRO SPEC_VALS DUMP_VALS EXCEPT — both directions for one
# macro. EXCEPT (space-separated, may be empty) names spec values that are
# NEVER expected back from the dump (a cited, structural exception — see
# this script's header), so they are excluded from the spec->dump sweep
# only, never from the dump->spec one (a value the dump prints that isn't
# in the exception list must still be a real spec value).
check_value_set() {
    local macro="$1" spec_vals="$2" dump_vals="$3" except="$4"
    local v miss=""
    for v in $dump_vals; do
        if ! grep -qxF "$v" <<< "$spec_vals"; then
            bad "[$macro] dump stamps value '$v' that docs/spec/match_api.md §6.3's own value-set table for $macro does not list"
            miss=1
        fi
    done
    [ -z "$miss" ] && ok "[$macro] every dumped stamp_value ($( printf '%s' "$dump_vals" | tr '\n' ' ' )) is in match_api.md §6.3's own value-set table"

    miss=""
    for v in $spec_vals; do
        grep -qxF "$v" <<< "$except" && continue
        if ! grep -qxF "$v" <<< "$dump_vals"; then
            bad "[$macro] match_api.md §6.3 documents value '$v' for $macro that --list-axes names on no row"
            miss=1
        fi
    done
    local except_disp="no exceptions"
    [ -n "$except" ] && except_disp="$(printf '%s' "$except" | tr '\n' ',' | sed 's/,$//')"
    [ -z "$miss" ] && ok "[$macro] every match_api.md §6.3 value for $macro (exceptions: $except_disp) appears in --list-axes' output"
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
    "mixed
none"

check_value_set "RX_DFA_PREFILTER" \
    "$(extract_md_table_values "$MATCHAPI" "its five values are the whole set")" \
    "$(dump_stamp_vals RX_DFA_PREFILTER)" \
    ""

check_value_set "RX_VM_PREFILTER" \
    "$(extract_line_values "$MATCHAPI" 'RX_VM_PREFILTER')" \
    "$(dump_stamp_vals RX_VM_PREFILTER)" \
    ""

check_value_set "RX_ENGINE" \
    "$(extract_line_values "$MATCHAPI" '\<RX_ENGINE\>')" \
    "$(dump_stamp_vals RX_ENGINE)" \
    ""

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
