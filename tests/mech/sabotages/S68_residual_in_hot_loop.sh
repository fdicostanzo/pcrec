# S68 — [M5-SEAM] THE ENGINE HOT LOOP ADVANCES THROUGH THE ENCODING
# RESIDUAL.
#
# docs/dev/plan.md [DD-12] (7), ruled in as a requirement: encodings are
# SEALED BACKENDS, the per-encoding header is the RIGHT seam for the
# enumerable runtime-identity RESIDUE and the WRONG seam for the HOT PATH
# ("gcc cannot invert decode+compare back into a byte automaton; malformed-
# input handling degrades from automaton structure to runtime branches"), and
# the rule is to be "ENFORCED BY CHECK, NOT CONVENTION".
#
# This sabotage is the most plausible way to break it, which is why it is the
# one worth planting: the emitted bitmap prefilter's skip loop advances one
# BYTE at a time (`scan_position++`), and a developer who has just been handed a
# `<prefix>_next_pos` helper whose whole job is "advance one character" will
# reach for it here. Under the byte backend the two are literally the same
# value, so the edit is CORRECT — and it is exactly the derailment DD-12 (7)
# names, because the moment a UTF-8 backend lands, the hot loop's shape and
# speed change with the encoding and the automaton stops being encoding-blind.
#
# WHAT ACTUALLY HAPPENS: nothing observable. The artifact matches identically
# (rx_next_pos returns scan_position + 1), so the whole .rxt corpus, both oracles, the
# reject table, the VM differential and every byte-identity gate in the tree
# stay green — this sabotage changes no ANSWER. Only
# tests/codegen/run_codegen_tests.sh's [M5-SEAM/DD-12(7)] check reads the
# emitted engine body and sees the residual call in it. A behaviour test
# structurally cannot cover this; that is the whole reason the structural
# check exists.
SAB_ID="S68-residual-in-hot-loop"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/base/caseless.rxt"
SAB_DESC="the emitted bitmap prefilter's skip loop advances via <prefix>_next_pos instead of scan_position++, so the DFA hot path calls into the encoding residual — DD-12 (7)'s forbidden hot-path/encoding coupling, planted in the shape a developer would actually write it. It changes no match answer under the byte backend (next_pos IS scan_position + 1), so only the codegen structural check can see it"
SAB_DOC_FIGURE="docs/dev/plan.md [DD-12] (7) 'a codegen-structural check that no hot-loop label calls into the encoding header (allowlist of named residual sites)'; src/gen/enc/enc.h's seam contract; tests/codegen/CLAUDE.md"
SAB_COUNT=1
# RE-ANCHORED 2026-08-26 ([ENG-FORM]): the bitmap prefilter's skip loop is a
# REPRESENTATION OBJECT's emitter now (`pf_emit_bcls`, axis B's `byte-class`
# candidate) rather than a branch inside `emit_unanchored`, and the D11 bound
# is a SECOND object (`pf_emit_bcls_bounded`) rather than the `fbound` string
# this row used to anchor on. The unbounded form is anchored here because it
# is the one `tests/base/caseless.rxt`'s artifacts take; the bounded form's
# own skip line is a distinct string and would need its own row.
SAB_BEFORE='    sb_printf(c, "%s    while (scan_position < subject_length &&"
                 " !%s_can_begin_match[subject[scan_position]]) scan_position++;\n",
              ind, f->p);'
SAB_AFTER='    /* SABOTAGE S68: the hot loop advances through the encoding
     * residual instead of one byte. */
    sb_printf(c, "%s    while (scan_position < subject_length &&"
                 " !%s_can_begin_match[subject[scan_position]]) scan_position = %s_next_pos(subject, subject_length, scan_position);\n",
              ind, f->p, f->p);'
