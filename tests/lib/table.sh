# tests/lib/table.sh — [SR-11] ONE implementation of docs/spec/table_contract.md,
# the shape gen_timeout.sh already established (D45's single, sourced
# implementation of a cross-cutting rule; this is the same pattern applied to
# the dump FORMAT rather than the compile budget).
#
# WHY THIS FILE EXISTS. D65 appended a 16th column (`built`) to
# `pcrec --list-syntax` and two consumers broke: tests/reject/'s row iterator
# and tests/cli/'s case10 both hard-coded `NF != 15`, because each had
# hand-rolled its own copy of "resolve this dump's shape" rather than sharing
# one. docs/spec/table_contract.md is the RULED contract (comment lines,
# header-names-columns, append-only, consumers resolve by name); this file is
# its one implementation, so the NEXT appended column is a non-event here
# rather than a third site to fix by hand. Every function below implements a
# rule from that document by name in its own comment — read the contract
# first if a rule's "why" is not obvious from here.
#
# WHO USES THIS. Shell/awk consumers of a `pcrec` TSV dump: source this file
# and call `table_col_index`/`table_awk_map`/`table_check_truthfulness`
# instead of hand-rolling `cut -fN`, a literal `NF != N`, or a positional
# `awk '{print $N}'`. tests/reject/run_reject_tests.sh, tests/cli/
# run_cli_tests.sh's case10, and tests/spec_mod0/check09_every_feature_
# toggles.sh all route through it. (compliance_section.py is python, not
# shell, and cannot source this file — it implements the SAME contract rules
# directly; see its own header for the cross-reference.
# tests/spec_mod0/spec_common.h is the C exemplar the contract itself names
# and is intentionally untouched — see table_contract.md's consumer rule 1.)
#
# TABLE_LIB_ROOT — computed once, same reason gen_timeout.sh computes
# GEN_LIB_ROOT once: every call site that used to compute it again nearby was
# one more place for the two copies to drift.
TABLE_LIB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"

# ---------------------------------------------------------------- sections
#
# table_contract.md's Sections rule: `#section NAME` announces a section; the
# LAST `#` line before that section's first data row is ITS header (rule 3,
# applied per section); a file with no `#section` line is one anonymous
# section, byte-for-byte today's `--list-syntax`/`--list-verbs` shape (rule
# 2); and a consumer reading a multi-section file WITHOUT naming a section
# must fail loudly rather than silently parse rows across a boundary that was
# never its own (rule 4) — so table__header_line refuses to guess when a
# multi-section file is read with no `section` argument, rather than
# returning whichever header happened to be last.
#
# table__header_line FILE [SECTION] — prints the raw header line (with its
# leading `#`) for FILE, or for SECTION within FILE if given. Internal:
# callers use table_header_ncols / table_col_index below, not this directly.
table__header_line() {
    local file="$1" section="${2:-}"
    local has_sections=0
    if grep -q '^#section ' "$file" 2>/dev/null; then has_sections=1; fi
    if [ "$has_sections" -eq 1 ] && [ -z "$section" ]; then
        echo "table: '$file' has multiple #section blocks; a consumer must" >&2
        echo "       name the section it wants (table_contract.md, Sections" >&2
        echo "       rule 4) rather than parse whichever header came last" >&2
        return 1
    fi
    local active=1 found_section=0 hdr=""
    [ "$has_sections" -eq 1 ] && active=0
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
            '#section '*)
                local name="${line#\#section }"
                if [ "$name" = "$section" ]; then active=1; found_section=1; hdr=""
                else active=0
                fi
                continue
                ;;
        esac
        [ "$active" -eq 1 ] || continue
        case "$line" in
            '#'*) hdr="$line" ;;
            '') continue ;;
            *) break ;;   # first data row: this section's header is fixed
        esac
    done < "$file"
    if [ -z "$hdr" ]; then
        if [ "$has_sections" -eq 1 ] && [ "$found_section" -eq 0 ]; then
            echo "table: '$file' has no #section '$section'" >&2
        else
            echo "table: '$file'${section:+ section '$section'} has no header line" >&2
        fi
        return 1
    fi
    printf '%s\n' "$hdr"
}

# table__header_fields FILE [SECTION] — internal: the header's column names,
# in order, one per line (the leading `#` stripped, split on TAB — never on
# IFS whitespace, which is why this is not a bash `read -a` on the raw line:
# tests/reject's own CLAUDE.md records what that collapse did the first time
# this dump was hand-parsed with `IFS=$'\t' read -r`).
table__header_fields() {
    local hdr
    hdr="$(table__header_line "$1" "${2:-}")" || return 1
    awk -F'\t' '{ sub(/^#/, "", $1); for (i = 1; i <= NF; i++) print $i }' <<< "$hdr"
}

# ------------------------------------------------------------- the contract
#
# table_header_ncols FILE [SECTION] — the header's DECLARED column count.
# The base quantity every "header truthfulness" comparison (table_contract.md
# "The checks") is stated against — never a literal number, per the
# consumer contract's rule 3.
table_header_ncols() {
    # NOT `table__header_fields ... | wc -l`: piping loses
    # table__header_fields's exit status (the pipeline's status is `wc`'s,
    # which is always 0), so a multi-section file read with no `section`
    # argument would silently report "0 columns" instead of failing loudly
    # — measured live while validating this file's own sabotage controls.
    local fields
    fields="$(table__header_fields "$1" "${2:-}")" || return 1
    awk 'END { print NR }' <<< "$fields"
}

# table_col_index FILE COL [SECTION] — 1-based index of column COL in FILE's
# header, resolved BY NAME (consumer contract rule 1). Fails loudly, naming
# the column and the header actually seen, rather than returning 0 or an
# empty string a caller might silently splice into `$0`.
table_col_index() {
    local file="$1" col="$2" section="${3:-}"
    local i=1 f
    local fields
    fields="$(table__header_fields "$file" "$section")" || return 1
    while IFS= read -r f; do
        if [ "$f" = "$col" ]; then
            printf '%s\n' "$i"
            return 0
        fi
        i=$((i + 1))
    done <<< "$fields"
    echo "table: column '$col' not in '$file'${section:+ section '$section'}'s header (have: $(printf '%s' "$fields" | tr '\n' ' '))" >&2
    return 1
}

# table_awk_map [-s SECTION] FILE COL [COL...] — the awk-ready index map: one
# `-v name=N` per requested column, space-joined, meant to be spliced
# unquoted into an `awk -F'\t' $(table_awk_map ...) '...'` invocation so the
# awk PROGRAM can read `$module`/`$status`/... by name instead of a bare `$4`
# a reader has to cross-reference against the header by hand. This is the
# "awk consumer builds a name->index map from the header row" the contract's
# consumer rule 1 requires, in reusable form — one implementation instead of
# tests/reject and tests/cli each writing their own map-building loop.
table_awk_map() {
    local section=""
    if [ "$1" = "-s" ]; then section="$2"; shift 2; fi
    local file="$1"; shift
    local col idx out=""
    for col in "$@"; do
        idx="$(table_col_index "$file" "$col" "$section")" || return 1
        out="$out -v $col=$idx"
    done
    printf '%s\n' "$out"
}

# ------------------------------------------------------- reading the rows
#
# [DD-8] THE READING HALF OF THE SECTIONS MECHANISM, added when `--emit-ir`
# became the contract's first MULTI-SECTION producer whose consumers live
# outside this file. `table_col_index` resolves a column by name; these three
# resolve the ROWS, so a consumer never writes a positional `cut -fN` or a
# fixed-position `grep` against a section's remembered shape again — which is
# the failure D106 records for `run_ir_listing.sh`'s own extractors ("fixed-
# position greps went stale once; declaration-based parsing is the durable
# fix").
#
# EVERY ONE OF THEM FAILS LOUDLY ON AN ABSENT SECTION, COLUMN OR KEY, and
# that is not defensiveness: an extractor that returns nothing when its
# section has been renamed reads exactly like a population that legitimately
# has no rows, which is the vacuity shape docs/dev/learnings.md §3 names and
# the one `run_ir_listing.sh`'s SLOTS block already guards by hand.

# table_section_rows FILE SECTION — the DATA rows of SECTION, raw, one per
# line (comments, the section's own header and blank lines dropped). Rows
# from other sections are never returned: contract consumer rule 4.
table_section_rows() {
    local file="$1" section="$2"
    if ! grep -q "^#section $section\$" "$file" 2>/dev/null; then
        echo "table: '$file' has no #section '$section'" >&2
        return 1
    fi
    awk -v want="$section" '
        /^#section / { cur = substr($0, 10); next }
        /^#/         { next }
        /^[ \t]*$/   { next }
        cur == want  { print }
    ' "$file"
}

# table_field FILE SECTION COL — column COL of every data row in SECTION,
# one value per line, resolved BY HEADER NAME (consumer rule 1).
table_field() {
    local file="$1" section="$2" col="$3"
    local idx rows
    idx="$(table_col_index "$file" "$col" "$section")" || return 1
    # NOT a pipeline: a pipeline's exit status is awk's, so an absent section
    # would read as "no rows" instead of failing — the same status-loss trap
    # table_header_ncols's own comment records.
    rows="$(table_section_rows "$file" "$section")" || return 1
    awk -F'\t' -v i="$idx" '{ print $i }' <<< "$rows"
}

# table_lookup FILE SECTION KEYCOL KEY VALCOL — the VALCOL of every row in
# SECTION whose KEYCOL equals KEY. The key/value shape a `fact`/`value`
# section (`--emit-ir`'s `summary`) is read with. A key that matches NO row
# is a hard failure naming the key, never an empty line: "the fact is absent"
# and "the fact is present and empty" are different answers and a caller that
# cannot tell them apart is reading a renamed row as a legitimate blank.
table_lookup() {
    local file="$1" section="$2" keycol="$3" key="$4" valcol="$5"
    local ki vi rows
    ki="$(table_col_index "$file" "$keycol" "$section")" || return 1
    vi="$(table_col_index "$file" "$valcol" "$section")" || return 1
    rows="$(table_section_rows "$file" "$section")" || return 1
    awk -F'\t' -v ki="$ki" -v vi="$vi" -v key="$key" '
        $ki == key { print $vi; found = 1 }
        END { if (!found) exit 3 }
    ' <<< "$rows" && return 0
    echo "table: '$file' section '$section' has no row whose $keycol is '$key'" >&2
    return 1
}

# table_check_truthfulness FILE [SECTION] — HEADER TRUTHFULNESS
# (table_contract.md, "The checks"): every data row's field count equals the
# header's declared count. This is the correct final form of the old
# tests/cli case10 `NF != 16` pin — the equality is against the header's OWN
# count, never a literal, so the next appended column changes nothing here.
# Prints one line per offending row to stderr (row number + content) and
# returns nonzero if any row disagrees; silent success on stdout otherwise.
table_check_truthfulness() {
    local file="$1" section="${2:-}"
    local nhdr
    nhdr="$(table_header_ncols "$file" "$section")" || return 1
    local has_sections=0
    grep -q '^#section ' "$file" 2>/dev/null && has_sections=1
    local active=1 lineno=0 bad=0
    [ "$has_sections" -eq 1 ] && active=0
    while IFS= read -r line || [ -n "$line" ]; do
        lineno=$((lineno + 1))
        case "$line" in
            '#section '*)
                local name="${line#\#section }"
                [ "$name" = "$section" ] && active=1 || active=0
                continue
                ;;
            '#'*|'') continue ;;
        esac
        [ "$active" -eq 1 ] || continue
        local n
        n=$(awk -F'\t' '{print NF}' <<< "$line")
        if [ "$n" -ne "$nhdr" ]; then
            echo "table: $file:$lineno has $n field(s), header declares $nhdr: $line" >&2
            bad=$((bad + 1))
        fi
    done < "$file"
    if [ "$bad" -gt 0 ]; then
        echo "table: header-truthfulness FAILED: $bad row(s) of '$file'${section:+ section '$section'} disagree with the header's declared field count ($nhdr)" >&2
        return 1
    fi
    return 0
}

# Runnable as a command, same coda as gen_timeout.sh, so a caller (or a
# sabotage control) can drive this from outside a sourcing shell. Command
# words are prefixed `table-` deliberately (gen_timeout.sh's own `secs` is
# unprefixed but this file is sourced by scripts whose OWN `$1` is often a
# short word like "check" — a collision here would silently misfire):
#   bash tests/lib/table.sh table-header-ncols FILE [SECTION]
#   bash tests/lib/table.sh table-col-index FILE COL [SECTION]
#   bash tests/lib/table.sh table-awk-map [-s SECTION] FILE COL [COL...]
#   bash tests/lib/table.sh table-check FILE [SECTION]
#   bash tests/lib/table.sh table-section-rows FILE SECTION
#   bash tests/lib/table.sh table-field FILE SECTION COL
#   bash tests/lib/table.sh table-lookup FILE SECTION KEYCOL KEY VALCOL
case "${1:-}" in
    table-header-ncols) shift; table_header_ncols "$@" ;;
    table-col-index)    shift; table_col_index "$@" ;;
    table-awk-map)      shift; table_awk_map "$@" ;;
    table-check)        shift; table_check_truthfulness "$@" ;;
    table-section-rows) shift; table_section_rows "$@" ;;
    table-field)        shift; table_field "$@" ;;
    table-lookup)       shift; table_lookup "$@" ;;
esac
