#!/usr/bin/env bash
# tests/registry/axes_registry_check.sh — [CHK-2] piece 1(a): THE REGISTRY
# CHECK for `pcrec --list-axes` — CODE (the dump) vs SPEC (docs/spec/
# tuning.md + cli/main.c), in BOTH directions, PC-3's own shape (a named
# assertion per row, a PASS/FAIL summary, never a bare count).
#
# WHY THIS IS THE INDEPENDENT SIDE (docs/dev/learnings.md §3: "a control
# must not share a source with what it controls"). `--list-axes` (src/dump/
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
# candidate" does not mean "never a ROW": `src/dump/axes_dump.c` now hand-
# states both as `kind=predicate` rows attached to axis `table` (order 3/4,
# `emit_table_composite_rows`), the same shape a predicate row already has
# everywhere else in this dump, so the check below has no exception left to
# carry for this macro either.
#
# DIRECTION 3B — THE EMITTER-SOURCE LEG (team-lead review, 2026-08-30,
# [REG-SV]). Direction 3 above is dump-vs-DOCS: both `src/dump/axes_dump.c`
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
# [DEC-FALLBACK] B5 RETIRED `RX_UNROLL_K_WHY`'s leg and `RX_ENGINE_SEL`'s
# ([OPT-4.1]'s, the same shape): both tokens became table cells, and
# tests/codegen/run_fallback_table.sh (b)'s witnesses are their emitter
# half (see each retirement note at its old site). `RX_DFA_TABLE`'s stays.
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
. "$ROOT_DIR/tests/lib/assoc.sh"   # [MACPORT] HDR_BIT below is string-keyed (C macro names) — bash 3.2 (this box) has no declare -A at all

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

# [MEMFN] R4a: `--list-axes` is a MULTI-SECTION stream — pcrec's anonymous
# axis table, then the kit's `memfn` section (docs/spec/registry.md §6). Every
# check below reads pcrec's table, SELECTED as the leading anonymous table
# (table_main; table_contract.md consumer rule 5), so a kit row can never be
# read as a pcrec axis; the `memfn` section is read by name in its own block.
RAW="$WORKDIR/axes.raw.tsv"
TSV="$WORKDIR/axes.tsv"
"$TIMEOUT_BIN" 60 "$PCREC" --list-axes > "$RAW" || { echo "axes_registry: FATAL: $PCREC --list-axes failed" >&2; exit 1; }   # [K37] bounded, tests/reject/run_reject_tests.sh's own --list-syntax precedent
table_main "$RAW" > "$TSV" || { echo "axes_registry: FATAL: could not select --list-axes' main table" >&2; exit 1; }

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
# [MEMFN] R4a: THE KIT'S `memfn` SECTION (integration.md §R4.4.1). Its rows
# are the kit's option registry (memfn/src/options.def, through
# mf_options()); pcrec names none. Present, header-truthful, its columns
# resolvable by name. Its INDEPENDENT control is a member-count FLOOR pinned
# as a literal in docs/spec/registry.md §6 ("memfn section floor: N"), which
# shares no source with options.def: born with the first row (R4d). Until
# then the registry is empty and the floor arm is UNREACHED (K35) — printed
# as such, never counted as a pass. A row that lands WITHOUT its floor fails.
# ============================================================================
REGMD="$ROOT_DIR/docs/spec/registry.md"
if ! grep -q '^#section memfn$' "$RAW"; then
    bad "[memfn] --list-axes has no '#section memfn' (the kit's option registry is not listed)"
elif ! table_check_truthfulness "$RAW" memfn >"$WORKDIR/mferr" 2>&1; then
    bad "[memfn] header truthfulness: $(cat "$WORKDIR/mferr")"
elif ! table_awk_map -s memfn "$RAW" name kind budget layer spelling doc >/dev/null 2>"$WORKDIR/mferr"; then
    bad "[memfn] the section's columns do not resolve by name: $(cat "$WORKDIR/mferr")"
else
    ok "[memfn] --list-axes carries the kit's section, header-truthful, columns name/kind/budget/layer/spelling/doc"
    mfrows="$(table_section_rows "$RAW" memfn | grep -c . || true)"
    mffloor="$(sed -n 's/.*`memfn` section floor: \([0-9][0-9]*\).*/\1/p' "$REGMD" | head -1)"
    if [ -z "$mffloor" ] && [ "$mfrows" -eq 0 ]; then
        echo "UNREACHED: [memfn floor] the kit's registry is empty ($mfrows rows) and no floor is pinned in docs/spec/registry.md §6 -- the floor is born with the first row ([MEMFN] R4d); nothing to check until then (K35)"
    elif [ -z "$mffloor" ]; then
        bad "[memfn floor] the section has $mfrows row(s) but docs/spec/registry.md §6 pins no '\`memfn\` section floor: N' -- a kit row landed without raising its floor (integration.md §R4.4.1)"
    elif [ "$mfrows" -lt "$mffloor" ]; then
        bad "[memfn floor] the section has $mfrows row(s), under the floor $mffloor pinned in docs/spec/registry.md §6 -- a stale or truncated kit registry"
    else
        ok "[memfn floor] $mfrows row(s), floor $mffloor (docs/spec/registry.md §6)"
    fi
fi

# ============================================================================
# lib/pcrec.h's OWN registry, derived the same proven way run_axes.sh
# derives it (tests/axes/run_axes.sh's own header comment) — never
# hand-copied. This is a SECOND, independent read of lib/pcrec.h: the dump
# itself was built from the SAME header's enum symbols (src/dump/
# axes_dump.c's V() macro), but that is dump-vs-header agreement BY
# CONSTRUCTION for the predicate axes' bit numbers; what this script adds is
# dump-vs-header agreement checked FROM OUTSIDE the compiled binary, over a
# plain-text re-read, which catches the case a stale BUILT binary would hide
# (a header edit with no rebuild).
assoc_new HDR_BIT   # macro -> bit
while IFS=$'\t' read -r macro bit; do
    [ -n "$macro" ] || continue
    assoc_set HDR_BIT "$macro" "$bit"
# THE SPELLING IS `PCREC_BIT(N)` SINCE [b2fix] (2026-09-23) — every member
# respelled from a bare `1ull << N` (itself the [OPT-REQPOS] (2026-09-22)
# widening from `1u << N`; the bit after 31 cannot be spelled `1u <<` at
# all, `1u << 32` being undefined behaviour) through the PUBLIC
# `#define PCREC_BIT(n) (1ull << (n))` macro declared just above the enum
# in lib/pcrec.h. No value moved either time; only the SPELLING did.
#
# TWO SHAPES, because bit 31 is not an enum member: `PCREC_NO_REQ_RUN =
# PCREC_BIT(31)` would numerically exceed INT_MAX and trip `-Wpedantic`'s
# "ISO C restricts enumerator values to range of 'int' before C23" (a
# GNU extension `make strict` does not require but a stricter downstream
# build might), so that one member alone is a `#define PCREC_NO_REQ_RUN
# PCREC_BIT(31)` line, matching PCREC_ENGINE_DFA/VM's existing `#define`
# precedent for an unrelated reason. Every future bit from 32 to 63 will
# need the SAME `#define` shape for the identical reason (named at its
# own site in lib/pcrec.h) — this extraction reads both shapes so it
# keeps deriving every bit as that population grows.
done < <(grep -oE '(PCREC_(NO|FORCE)_[A-Z_]+ *= *PCREC_BIT\([0-9]+\))|(#define PCREC_(NO|FORCE)_[A-Z_]+ +PCREC_BIT\([0-9]+\))' "$ROOT_DIR/lib/pcrec.h" \
          | sed -E 's/^#define +//; s/ *= */ /' \
          | sed -E 's/^(PCREC_(NO|FORCE)_[A-Z_]+) +PCREC_BIT\(([0-9]+)\)$/\1\t\3/')
if [ "$(assoc_count HDR_BIT)" -eq 0 ]; then
    echo "axes_registry: FATAL: derived ZERO PCREC_(NO|FORCE)_* bit constants from lib/pcrec.h" >&2
    exit 1
fi

# [REVW.4] wave 4 (D111), 2026-09-19: THE AWK SCRAPER THAT STOOD HERE IS
# DELETED, not re-aimed. It rebuilt `cli/main.c`'s flag-text-to-bit pairing
# out of that file's TEXT — "remember the most recently seen `strcmp(a,
# "-...")` literal, pair it with the next `opt.flags |= MACRO` line" — so
# that `check_cli_flag` could reconcile the parser's spellings against the
# dump's `cli_flag` column. `tests/axes/run_axes.sh` carried an independent
# re-implementation of the identical pass, with its own fatal guard for the
# day "cli/main.c's loop shape changed".
#
# Both facts now come off ONE row of `src/core/axes.def`: `cli_axis_apply`
# (cli/main.c) and `axis_cli_flag` (src/dump/axes_dump.c) read the same
# table, so there are no longer two independently-typed spellings for a check
# to reconcile. A3's usual direction inverts — the extraction DELETES two
# checks rather than needing a new one.
#
# WHAT IS KEPT, because the shared table does not make it true: that the
# shipped BINARY actually ACCEPTS the spelling this dump advertises.
# `check_cli_flag_accepted` below runs it. A table cannot guarantee that —
# the grammar arm could stop being reached (a mis-ordered chain, a
# `no_more_opts` guard, an empty spelling cell) and the dump would go on
# advertising a flag nobody can pass. That is behaviour, measured through a
# different mechanism from the text it checks.

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
    if ! assoc_has HDR_BIT "$macro"; then
        bad "[$axis/$cand] dumped deny/force macro '$macro' is not defined in lib/pcrec.h at all"
        return
    fi
    if [ "$(assoc_get HDR_BIT "$macro")" != "$dumped_bit" ]; then
        bad "[$axis/$cand] dumped bit $dumped_bit for '$macro' disagrees with lib/pcrec.h's own bit $(assoc_get HDR_BIT "$macro")"
        return
    fi
    ok "[$axis/$cand] '$macro' (bit $dumped_bit) matches lib/pcrec.h"
}

# Does the SHIPPED PARSER accept this spelling? `--count-groups` is the probe
# because it takes a pattern, writes no file and exits 0 — the option loop
# runs in full and nothing downstream of it does. An unknown `-f...` falls
# through to the unknown-option diagnostic and exits 1, which is the failing
# direction this arm is driven in.
check_cli_flag_accepted() {
    local flagtext="$1" axis="$2" cand="$3"
    if "$TIMEOUT_BIN" 30 "$PCREC" "$flagtext" --count-groups --pattern 'a(b)' >/dev/null 2>&1; then
        ok "[$axis/$cand] cli_flag '$flagtext' is accepted by the shipped parser"
    else
        bad "[$axis/$cand] cli_flag '$flagtext' is advertised by --list-axes but the shipped parser REFUSES it — src/core/axes.def's row and cli_axis_apply have come apart, or the arm is no longer reached"
    fi
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

while IFS=$'\x1f' read -r axis order candidate kind stamp_macro stamp_value \
                        deny_macro deny_bit force_macro force_bit cli_flag applies; do
    [ -n "$axis" ] || continue
    # [OPT-LITSCAN] S1: a candidate removed by EITHER of two bits (the
    # run-pinned prefilter rows) carries all three deny cells `|`-joined in
    # the same order (docs/spec/registry.md) — split them in lockstep and
    # check each (macro, bit, flag) triple exactly as a one-bit row is
    # checked, so a pair whose halves disagree fails on the half that does.
    if [ -n "$deny_macro" ] && [ "${deny_macro#*|}" != "$deny_macro" ]; then
        IFS='|' read -r -a dm_parts <<< "$deny_macro"
        IFS='|' read -r -a db_parts <<< "$deny_bit"
        IFS='|' read -r -a df_parts <<< "$cli_flag"
        if [ "${#dm_parts[@]}" != "${#db_parts[@]}" ] || [ "${#dm_parts[@]}" != "${#df_parts[@]}" ]; then
            bad "[$axis/$candidate] multi-bit deny cells disagree in length: macro '$deny_macro', bit '$deny_bit', flag '$cli_flag'"
        fi
        for i in "${!dm_parts[@]}"; do
            check_macro_bit "${dm_parts[$i]}" "${db_parts[$i]:-}" "$axis" "$candidate"
            seen_dumped_bits="$seen_dumped_bits ${db_parts[$i]:-}"
            [ -n "${df_parts[$i]:-}" ] && check_cli_flag_accepted "${df_parts[$i]}" "$axis" "$candidate"
            [ -n "${db_parts[$i]:-}" ] && check_tuning_bit_documented "${db_parts[$i]}" "$axis" "$candidate"
        done
        continue
    fi
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
                [ -n "$deny_macro" ]  && check_cli_flag_accepted "$f1" "$axis" "$candidate"
                [ -n "$force_macro" ] && check_cli_flag_accepted "$f2" "$axis" "$candidate"
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
                if [ -n "${deny_macro:-$force_macro}" ]; then
                    check_cli_flag_accepted "$cli_flag" "$axis" "$candidate"
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
# Field separator here is \037 (US, ASCII Unit Separator), NOT \t: bash's
# `IFS=$'\t' read` treats tab as IFS WHITESPACE regardless of what IFS is
# set to, so runs of empty tab-delimited fields (every row with an unset
# deny/force column) silently COLLAPSE and every field after the first
# empty one shifts left — reproduced live while writing this check, and
# the exact bug tests/lib/table.sh's own header comment names ("never on
# IFS whitespace, which is why this is not a bash `read -a` on the raw
# line"). [MACPORT] NOT \001 (SOH) either, despite also being outside the
# whitespace class: verified live that bash 3.2's own `read` builtin does
# not split fields on IFS=$'\x01' at all (the whole line lands in the
# first variable, every other variable empty) while bash 4+/5+ splits it
# correctly — a narrow, previously-undiscovered bash 3.2 `read`/IFS bug
# specific to that one byte. \037 was verified to split identically on
# both bash versions, on both `read` and `awk -F`. \037 is not
# in bash's whitespace class, so empty fields survive.
done < <(awk -F'\t' $MAP '!/^#/ {
    print $axis"\037"$order"\037"$candidate"\037"$kind"\037"$stamp_macro"\037"$stamp_value"\037"$deny_macro"\037"$deny_bit"\037"$force_macro"\037"$force_bit"\037"$cli_flag"\037"$applies
}' "$TSV")

# Every "list"/"both" axis's candidates must have an authored applies() —
# the dump's own placeholder text names an unauthored one, so grep for it
# rather than re-parsing: a candidate the accessor sees but no text
# describes is a FINDING (a lane added a candidate without its text),
# never silently accepted. The text lives in axes_dump.c's AXIS_DESC table
# for the machine-form axes and, since [START-TABLE] C6, beside each row of
# cand_rows[] for the start axes, which print the same placeholder for a
# row without one (sabotage S610).
if grep -qF 'no description authored for this candidate yet' "$TSV"; then
    while IFS=$'\t' read -r axis _ candidate _; do
        [ -n "$axis" ] || continue
        bad "[$axis/$candidate] has NO authored description: src/dump/axes_dump.c's AXIS_DESC table for a machine-form axis, or, for a start axis, the row's desc beside it in src/gen/emit_dfa.c's cand_rows[] (a candidate landed with no text)"
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
# are unrelated `PCREC_BIT(N)` constants in the same header (PCREC_CASELESS
# and friends) and must never be swept in -- while the top of the deny/force
# family moves every time an axis is added. It was `-le 15`, the family's
# extent on the day this was written, and [OPT-K]'s bit 16 was therefore
# FILTERED OUT BEFORE THE COMPARISON: `-fno-offset-skip` could have been
# absent from --list-axes entirely and this arm would have printed `ok`,
# naming bits 4-15. That is this check's own claim failing at the one thing
# it exists to assert, silently. `tests/axes/run_axes.sh` had the identical
# defect and was caught only because its PROSE anchor broke loudly first.
hdr_bits_family=""
while IFS= read -r macro; do
    [ -n "$macro" ] || continue
    b="$(assoc_get HDR_BIT "$macro")"
    if [ "$b" -ge 4 ] 2>/dev/null; then
        hdr_bits_family="$hdr_bits_family $b"
    fi
done < <(assoc_keys HDR_BIT)
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
    bad "lib/pcrec.h defines PCREC_NO_*/FORCE_* bit(s)$missing_from_dump2 (of bits $hdr_bits_lo-$hdr_bits_hi found in the header) that --list-axes names on no row (an axis landed in the header with no dump coverage — e.g. a new axis's list not yet reached by src/dump/axes_dump.c's predicate table)"
else
    ok "every PCREC_NO_*/PCREC_FORCE_* bit lib/pcrec.h defines at or above bit 4 ($( printf '%s' "$hdr_bits_sorted" | tr '\n' ' ' )) appears in --list-axes' output"
fi

# ============================================================================
# DIRECTION 3: STAMP VALUES, both ways (docs/spec/match_api.md §6.3 — see
# this script's own header for which macros have a closed value set there
# and the two named/cited exceptions).
# ============================================================================

# extract_md_table_values / extract_line_values / extract_prose_values /
# extract_c_return_values live in tests/lib/spec_extract.sh (decfbB0b: one
# implementation, shared with tests/codegen/run_fallback_table.sh); their
# comments moved with them.
. "$ROOT_DIR/tests/lib/spec_extract.sh"
# Every anchor below is a `<!-- value-set: RX_NAME -->` marker line placed
# directly above that macro's value table in match_api.md (lane specclean,
# 2026-10-09). The per-macro anchor notes further down describe the phrase
# anchors those markers replaced; the lesson they record (anchor on nothing a
# new value or a rewording can change) is what the markers implement.


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
    awk -F'\037' -v m="$macro" '$5 == m && $6 != "" {print $6}' <<< "$axes_rows_dump"
}

# One extra pass over the dump, keyed the same \037 way the main loop reads
# it, so this direction does not have to re-run `pcrec --list-axes` (the
# TSV in $TSV is already read once above; re-deriving it here from the same
# file keeps this direction independent of the main loop's bash variables,
# which the main loop's own `while` has already consumed).
axes_rows_dump="$(awk -F'\t' $MAP '!/^#/ {
    print $axis"\037"$order"\037"$candidate"\037"$kind"\037"$stamp_macro"\037"$stamp_value
}' "$TSV")"

check_value_set "RX_DFA_TABLE" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_DFA_TABLE -->")" \
    "$(dump_stamp_vals RX_DFA_TABLE)" \
    ""
# [REG-SV], 2026-08-30: NO MORE EXCEPTION HERE. "mixed"/"none" used to be a
# cited exclusion from the spec->dump sweep only (this script's own header,
# pre-[REG-SV] revision) — real spec values the dump could never produce as
# a row, because the per-machine `table` axis has only two candidates. The
# dump now carries them as two hand-stated composite rows (src/dump/
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
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_DFA_PREFILTER -->")" \
    "$(dump_stamp_vals RX_DFA_PREFILTER)" \
    ""

# [ENG-ABS] axis G's stamp. THE ANCHOR CARRIES NO COUNT AND NO BACKTICK — the
# first for the reason the paragraph above records, the second because these
# anchors are double-quoted bash strings and a backtick in one is a command
# substitution. "is on every DFA" is unique in match_api.md and survives a
# value being added.
check_value_set "RX_DFA_MATCH" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_DFA_MATCH -->")" \
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
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_DFA_SCAN_EDGE -->")" \
    "$(dump_stamp_vals RX_DFA_SCAN_EDGE)" \
    ""

# [OPT-5] STEP 2 axis `search-start`'s stamp. Its value set is exactly the
# two candidates the axis can select — unlike `table` and `scan-body`, whose
# stamps compose a fact ACROSS machines and therefore carry `"none"`/`"mixed"`
# composite values the per-machine list could never produce. So this call
# needs no composite sibling, and the dump needs no hand-stated outcome rows.
#
# THE ANCHOR CARRIES NO COUNT, `RX_DFA_SCAN_EDGE`'s rule one block up: a
# phrase naming a number goes stale the day a third form lands, silently, by
# harvesting a shorter list than the spec states.
check_value_set "RX_DFA_START" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_DFA_START -->")" \
    "$(dump_stamp_vals RX_DFA_START)" \
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
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_VM_PREFILTER -->")" \
    "$(dump_stamp_vals RX_VM_PREFILTER)" \
    ""

check_value_set "RX_ENGINE" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_ENGINE -->")" \
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
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_ENGINE_SEL -->")" \
    "$(dump_stamp_vals RX_ENGINE_SEL)" \
    ""

# [OPT-4.1] THE EMITTER-SOURCE LEG for `RX_ENGINE_SEL` (dump-vs-CODE,
# `pcrec_engine_sel_name`'s `return "..."` statements) RETIRED at
# [DEC-FALLBACK] B5 (dec_fallback.md §4.5, critB2 M7): since B5 the token is
# a table CELL read by the attribution walk and spelled by that same
# function, so the leg's code side would share its spelling with what it
# checks. The emitter half moved to WITNESSES: tests/codegen/
# run_fallback_table.sh (b), the stamps eight witnesses actually emit, held
# to match_api.md's hand-written set with a K35 floor per value (green since
# B0). `RX_VM_RESEED`'s shape below is the precedent: docs leg kept, source
# leg retired, emitter half in witnesses.

# [REG-SV], 2026-08-30: `RX_UNROLL_K_WHY`'s seven-value set, previously
# uncovered by this direction entirely (no call at all — the gap the
# comparative bench found: the dump's two `size-term` rows both stamped an
# EMPTY `stamp_value`, so there was nothing here to check against). See
# `extract_prose_values`'s own header for why this macro needs a third
# extraction shape.
check_value_set "RX_UNROLL_K_WHY" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_UNROLL_K_WHY -->")" \
    "$(dump_stamp_vals RX_UNROLL_K_WHY)" \
    ""

# [REG-SV] THE EMITTER-SOURCE LEG for `RX_UNROLL_K_WHY` (dump-vs-CODE, the
# literals of compile.c's `cx.size_term_why = ...` ternary) RETIRED at
# [DEC-FALLBACK] B5 with the ternary it read: the token is T4's cell
# (`st_whys[]`), and fbt (b)'s seven witnesses (K35 floor per value, the
# observed set equal to match_api.md's) are the emitter half, as for
# `RX_ENGINE_SEL` above.

# [OPT-HYB-RESEED] `RX_VM_RESEED`, 2026-09-30 (lane reseedfix, r1 panel chk
# F6.3): dump-vs-DOCS for the hybrid retry's row names. ONE leg, not two: the
# dump walks the RETRY rows live (`pcrec_reseed_row`; `cand_rows[]` since
# [START-TABLE] C5, `pcrec_reseed_rows` before) and the emitter stamps the
# chosen row's spelling off the SAME rows, so a dump-vs-emitter-source leg would
# be a control sharing its source with what it controls. The independent
# source is the hand-written §6.3 table; tests/codegen's [OPT-HYB-RESEED]
# witnesses stamp each of the five values once, which is the emitter half.
check_value_set "RX_VM_RESEED" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_VM_RESEED -->")" \
    "$(dump_stamp_vals RX_VM_RESEED)" \
    ""

# [UTF-VALID] the two CONTRACT stamps, dump-vs-DOCS, one leg each for
# `RX_VM_RESEED`'s reason above: the dump's rows are hand-stated in
# src/dump/axes_dump.c and the §6.3 tables are hand-written, so the two are
# independent sources; tests/utfcheck's per-config stamp asserts are the
# emitter half.
check_value_set "RX_STARTPOS_GUARD" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_STARTPOS_GUARD -->")" \
    "$(dump_stamp_vals RX_STARTPOS_GUARD)" \
    ""
check_value_set "RX_UTF_CHECK" \
    "$(extract_md_table_values "$MATCHAPI" "<!-- value-set: RX_UTF_CHECK -->")" \
    "$(dump_stamp_vals RX_UTF_CHECK)" \
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
