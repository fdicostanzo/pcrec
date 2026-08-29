# S190 (S-ENGABS2) — [ENG-ABS] THE DEAD-GROUP FILL'S LOOP BOUND, ONE TOKEN,
# AND EVERY `grep` PREDICATE IN THE TREE STILL PASSES.
#
# THIS ROW IS THE r41 CRITIC'S OWN PLANT, ADOPTED RATHER THAN REWRITTEN — the
# same discipline `simvm.py` was adopted under at [M6.5.2], and for the same
# reason: a lane must not soften the instrument that found its hole.
#
# WHAT IT BREAKS. Under `RX_DFA_MATCH "unwrapped"`, `<prefix>_match_caps` no
# longer calls `<prefix>_search`, so the PERMANENTLY-UNSET group slots that
# `emit_search_head` writes at entry to that function are not written by
# anybody — the anchored entry has to fill them itself
# (docs/design/anchored_match_unwrapped.md §3.9). This plant changes the
# fill's bound from `RX_NCAPS` to `1`, so the loop body never executes and
# every slot above 0 comes back to the caller EXACTLY AS THE CALLER LEFT IT.
# On `(?(DEFINE)(?<g>a))(?&g)b` over "ab" the critic measured
# `caps[1] = [57005, 48879]` — the driver's own poison, handed back as if it
# were a capture. `docs/spec/match_api.md` §3.3 says every slot is written on
# success; it is not.
#
# **WHAT STAYED GREEN IS THE WHOLE POINT OF THE ROW.** MEASURED by r41
# (2026-08-28) and re-measured at landing:
#
#   - `tests/codegen/run_anchored_match.sh` §3's FOUR `grep -q` predicates all
#     PASS. The loop is still there, still spells `PCREC_UNSET`, still sits
#     below the early return — only its BOUND moved, and a structural check
#     that reads emitted TEXT cannot see a bound.
#   - `tests/anchored/run_anchored_diff.sh` §1 stays green across all 147,986
#     of its cells, because §1 compiles BOTH arms `--no-captures` and
#     `RX_NCAPS` is 1 there — the loop it is checking is EMPTY in the correct
#     build too.
#   - The whole `.rxt` corpus stays green: no cell reads a capture slot above
#     0 on a DFA artifact.
#
# The detector is `run_anchored_diff.sh` §2, the CAPTURES-ON arm added for
# exactly this finding: eight named witnesses with `RX_NCAPS >= 2`, compared
# against the `-fno-anchored-dfa` build's delivered array. It is a RUN, not a
# grep, which is the only kind of check a bound can be wrong in front of.
SAB_ID="S190-anchored-dead-group-fill-empty"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="anchdiff anchoredmatch harness"
SAB_HARNESS_TARGET="tests/base/groups.rxt"
SAB_DESC="the unwrapped <prefix>_match_caps's dead-group fill loop is bounded at 1 instead of RX_NCAPS, so every group slot above 0 is returned to the caller UNWRITTEN — spec §3.3's 'all written on success' broken on a DFA artifact with RX_NCAPS >= 2, while all four of run_anchored_match.sh §3's grep predicates still pass and run_anchored_diff.sh §1's 147,986 --no-captures cells stay green"
SAB_DOC_FIGURE="PRE-VALIDATED (r41 critic-checks 2026-08-28, re-measured at landing): DETECTED by tests/anchored/run_anchored_diff.sh §2 ALONE. §3's greps 4/4 pass, §1 green on 147,986 cells, tests/base/groups.rxt green — a bound is invisible to every check that reads emitted text, which is why §2 is a RUN"
SAB_COUNT=1
# THE ANCHOR CARRIES THE PRECEDING LINE, and it has to: the SAME fill loop is
# emitted at TWO sites — `emit_search_head`'s (the search-and-filter form's,
# written at entry to `<prefix>_search`) and this one. Only the anchored site
# is this row's subject; the preceding `capture_spans_out[0][1] = …` line is
# what tells them apart, since the loop line itself is character-identical
# apart from C-source indentation, which is a SUBSTRING of the other site's.
SAB_BEFORE='        "        capture_spans_out[0][1] = (ptrdiff_t)ctx->pos + rx_len;\n"
        "        for (int rx_g = 1; rx_g < %s_NCAPS; rx_g++) {\n"'
SAB_AFTER='        "        capture_spans_out[0][1] = (ptrdiff_t)ctx->pos + rx_len;\n"
        "        for (int rx_g = 1; rx_g < 1; rx_g++) {   /* SABOTAGE S190 */\n"'
