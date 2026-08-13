# S17 — \s's registry row gets a `syntax` probe string that does not reach
# its own doorway ("zz" instead of "\s") (tests/reject/CLAUDE.md's SR-4
# table, row 2). Documented result: 0 hand-written fail, 1 iterated fail (the
# --list-syntax iteration probes "zz" and finds it does NOT produce the
# promised "requires module 'classes'" diagnostic, because "zz" is two
# ordinary literal characters that compile fine).
#
# RETAGGED 2026-08-12 (MOD-0.8c slice 1) with `registry` and `pc3`. A row whose
# `syntax` no longer reaches its own doorway is precisely what both suites use
# as their PROBE: tests/registry/CLAUDE.md's assertion 2 compiles "every row's
# `syntax` for real" and demands the diagnostic match the row, and PC-3's part
# 1 puts the same string in front of libpcre2 ("a row whose syntax will not
# compile and has no wrapper is a FAILURE, never a skip"). Both should fire,
# and for DIFFERENT reasons — the probe stops reaching pcrec's doorway, and it
# stops being a construct libpcre2 can be asked about.
SAB_ID="S17-syntax-mismatch"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject registry pc3"
SAB_DESC="ESC('s', ...) syntax probe changed from '\\\\s' to 'zz' (a syntax field that never reaches its doorway)"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 0 hand-written, 1 iterated fail"
SAB_COUNT=1
SAB_BEFORE="ESC_SET('s', \"\\\\s\", classes, ANY_ENGINE, \"any whitespace character\", QF_YES, \"set 6\", pcrec_cls_space_esc, 0),"
SAB_AFTER="ESC_SET('s', \"zz\", classes, ANY_ENGINE, \"any whitespace character\", QF_YES, \"set 6\", pcrec_cls_space_esc, 0),"
