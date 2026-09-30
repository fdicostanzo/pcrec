# S391 ([CLS-TREE] S4, lane s4build) -- THE ONE-CHARACTER DECODE ACCEPTS A
# SURROGATE.
#
# S390's claim, the other exclusion: U+D800-U+DFFF have no UTF-8 encoding and
# the lowered automaton has no path through `ED A0 80`. The plant drops the
# surrogate test, so the decoder yields U+D800, a member of every complemented
# class (`[^a]`, `\P{L}`, `.` -- cpset complements within [0, max_cp], the
# design's "Surrogates" paragraph), and the kit route matches where the
# automaton does not. The design's own named sabotage (§6, S4 row).
SAB_ID="S391-decode-accepts-surrogate"
SAB_FILE="src/enc/enc_utf8.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8/wclass_illformed.rxt"
SAB_DESC="the utf8 backend's one-character decode (\$_decode) loses its surrogate exclusion, so ED A0 80 decodes to U+D800, which every complemented wide class contains"
SAB_DOC_FIGURE="MEASURED solo 2026-09-30 at the s4build tip: corpus:16fail/728pass DETECTED -- the engine-vm blocks' surrogate cells; the default-engine blocks green."
SAB_REACH='"$PCREC" -e utf8 --engine=vm -p rx -o - --pattern "x[^a]y"'
SAB_REACH_EXPECT='rx_decode(subject, subject_length, scan_position'
SAB_REACH_POP='tests/utf8/wclass_illformed.rxt|xed.xa0.x80|8'
SAB_COUNT=1
SAB_BEFORE='"    if (v < floor || v > 0x10FFFFu || (v >= 0xD800u && v <= 0xDFFFu)) return 0;\n"'
SAB_AFTER='"    if (v < floor || v > 0x10FFFFu) return 0;\n"'
