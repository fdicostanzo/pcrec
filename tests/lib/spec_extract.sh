# tests/lib/spec_extract.sh — ONE implementation of the four hand-written-set
# extractors (docs/spec/match_api.md §6.3's value sets, and a C function's
# `return "..."` literals). Sourced, never executed. Moved here VERBATIM from
# tests/registry/axes_registry_check.sh (decfbB0b, 2026-10-08) so that
# tests/registry/axes_registry_check.sh (the dump-vs-docs/code legs) and
# tests/codegen/run_fallback_table.sh (the observed-stamp leg) read the
# spec's sets through the SAME code: no copy to drift. Defines functions only.

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
# legs above compare the DUMP (src/dump/axes_dump.c's hand-stated rows)
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
