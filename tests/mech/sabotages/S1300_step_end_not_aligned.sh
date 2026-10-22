# S1300 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: after a non-empty match the iterator resumes at its end, not at the aligned end (K75).
# Detector: a utf8 match ending before a stray continuation byte: the iterator answers neither libpcre2 nor the loop.
# Witness: cells.tsv's `a\x80a` / `\xc3\xa9\x80a` utf8 subjects (lane s1300, 2026-10-21): the 621 run read
# UNDETECTED because no cell put a stray right after a non-empty match; the plant's `__find` then
# starts at the stray (no caller-position guard in `__find`), where `a*`/`a|` are expected to report an empty match.
SAB_ID="S1300-step-end-not-aligned"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='after a non-empty match the iterator resumes at its end, not at the aligned end (K75)'
SAB_DOC_FIGURE='Owed: lane s1300 queued this row after adding its witness (docs/dev/lanes/s1300_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1300.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            "        it->lo = %s__next_pos(s, n, (size_t)c[0][1] - 1);   /* K75: the aligned end */\n"'
SAB_AFTER='            "        it->lo = (size_t)c[0][1]; (void)%s__next_pos;   /* SABOTAGE S1300 */\n"'
