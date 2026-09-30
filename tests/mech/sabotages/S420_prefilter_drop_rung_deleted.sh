# S420 — [PF-DROP] (D135) THE PREFILTER-DROP RUNG NEVER FIRES.
#
# The size-cap ladder's LAST row (`fit_rungs[]`, `src/core/compile.c`)
# drops the VM hybrid's prefilter when an emitted-size cap has refused an
# artifact that still carries one. Make its predicate constantly false and
# the rung stops existing: `(\p{Xwd})` under `-e utf8` — a hybrid whose
# byte-DFA prefilter alone puts it over the total cap — goes back to being
# REFUSED at default axes, the state before D135.
#
# A REFUSAL, S237's own reasoning: nothing that compares ANSWERS can see it,
# because a pattern that does not compile has no answers. WHAT SEES IT:
# `tests/uprops/size_ladder_prefilter_drop.rxt`, whose one block becomes a
# pattern-compile failure (every case in it fails), and the resource
# section's [PF-DROP] cells.
SAB_ID="S420-prefilter-drop-rung-deleted"
SAB_FILE="src/core/compile.c"
SAB_SUITES="harness resource"
SAB_HARNESS_TARGET="tests/uprops/size_ladder_prefilter_drop.rxt"
SAB_DESC="the size-cap ladder's prefilter-drop row never applies, so a VM hybrid whose prefilter alone is over an emitted-size cap is refused again — (\\p{Xwd}) under -e utf8, D135's witness"
SAB_DOC_FIGURE="PREDICTED (lane pfdrop, 2026-09-30): harness corpus:19fail/0pass on the target file (its one block no longer compiles); resource [PF-DROP] cells red. docs/spec/limits.md §8's size-cap ladder; docs/dev/decisions.md D135"
SAB_COUNT=1
# REACH: does the witness still take this rung? Read as the stamp only this
# rung writes. If `(\p{Xwd})` ever fits unaided, this row certifies nothing.
SAB_REACH='"$PCREC" -e utf8 -p rx -o - --pattern "(\p{Xwd})" 2>/dev/null | grep -o "size cap retry, hybrid" | head -1'
SAB_REACH_EXPECT='size cap retry, hybrid'
SAB_BEFORE='    return s->size_drop_rung < SDR_NO_PREFILTER && !s->dfa_disabled &&'
SAB_AFTER='    return false && s->size_drop_rung < SDR_NO_PREFILTER && !s->dfa_disabled &&   /* SABOTAGE S420 */'
