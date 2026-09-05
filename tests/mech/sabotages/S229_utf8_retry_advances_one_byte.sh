# S229 — [K49] THE UNANCHORED RETRY ADVANCE STEPS ONE BYTE UNDER utf8.
#
# This is K49 itself, planted: the `utf8` backend's `advance` text loses its
# continuation-byte skip and becomes the `byte` backend's step. It is the exact
# state the tree shipped in between [M5.0] stage 2 and 2026-09-05, so the row
# is a regression pin on a defect that really happened rather than a
# hypothetical.
#
# WHY THIS IS THE EDIT WORTH PLANTING. The advance is INLINE TEXT rather than a
# call to `<prefix>_next_pos`, because DD-12 (7), the [M5-SEAM] codegen check
# and sabotage row S68 all forbid an engine body calling that entry — so the
# boundary rule is spelled TWICE per backend and the two spellings can drift.
# This sabotage is that drift in the direction it would actually happen: a
# backend author writes the entry, and forgets that the advance says the same
# thing somewhere else.
#
# WHAT ACTUALLY HAPPENS, and it is the reason a positive pattern's corpus
# cannot see it: a mid-character start "has no path" under UTF-8, so for any
# POSITIVE pattern the extra retries are wasted attempts and every answer is
# unchanged. The inversion is on a NEGATIVE assertion, which succeeds exactly
# where its body has no path — so `(?<!.)` over `CE B1 CE B2` at startpos 2
# retries at offset 3, the lookbehind's own back_step reports BACK_STEP_NONE on
# the truncated leading character, the assertion SUCCEEDS, and the artifact
# reports a match at a byte offset inside a character.
#
# TWO DETECTORS, and they are independent instruments rather than one twice.
# The `harness` arm is the D27-blinded corpus cell that FOUND K49
# (tests/utf8/axis09_nextpos_findall.rxt's "midstart-row3-boundary"), which is
# an ANSWER. The advance-agreement section of
# tests/codegen/run_encoding_checks.sh is a STRUCTURAL check that extracts the
# advance from an emitted artifact and compares it against that same artifact's
# own `next_pos` — it goes red on this row too, and it would still be red if
# the corpus had no such cell. That suite is not wired into this matrix's
# dispatch today (there is no `encoding` suite token in
# run_sabotage_matrix.sh), so it is named here rather than claimed as a scored
# arm.
#
# THE BYTE PATH IS UNTOUCHED by this row, which is the point of putting the
# advance on the backend at all: `SAB_FILE` is the utf8 backend's own file, so
# every `byte` artifact in the tree is byte-identical under the sabotage and
# every byte-identity gate stays green.
SAB_ID="S229-utf8-retry-advances-one-byte"
SAB_FILE="src/gen/enc/enc_utf8.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8/axis09_nextpos_findall.rxt"
SAB_DESC="the utf8 backend's unanchored RETRY ADVANCE loses its continuation-byte skip and becomes the byte backend's pos++, so an unanchored search under -e utf8 retries at offsets inside a character. Invisible on every positive pattern (a mid-character start has no path); on a leading negative assertion it REPORTS a match at a mid-character offset. This is K49 as it shipped"
SAB_DOC_FIGURE="docs/dev/known_issues.md K49 (FIXED marker); src/gen/enc/enc.h's \`advance\` field comment; docs/design/utf8_design.md §5.5's refutation box"
SAB_COUNT=1
SAB_BEFORE='"@P++;\n"
"while (@P < @N\n"
"       && (@S[@P] & 0xC0) == 0x80) @P++;\n";'
SAB_AFTER='/* SABOTAGE S229: the advance is the byte backend'"'"'s step, so a retry
 * lands on the next BYTE rather than the next character boundary. */
"@P++;\n";'
