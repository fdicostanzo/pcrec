# S235 — [K50] SITE 2: `ENG_ATTEMPT`'s START LOOP STEPS ONE BYTE AGAIN.
#
# The emitted `for (start = search_from; start <= start_max; start++)` gains a
# boundary `continue` under an encoding that restricts positions. Delete it
# and that engine offers attempts at mid-character offsets again.
#
# THIS ROW EXISTS BECAUSE THE CHARTER DID NOT HAVE IT. K50's site list names
# this loop as *"the loop utf8_design.md 5.5 and ASK 5 are about"* and files
# NO witness for it — 5.5 asserts such starts merely waste attempts, and
# Frank's ASK 5 ruling ("leave it alone") was given that claim. It is false:
# `(?m)^a|\B` over `61 CE B1` at `startpos = 1`, a real character boundary,
# reported `(2,2)` where libpcre2 10.46 under `PCRE2_UTF` answers `(3,3)`.
#
# THE WITNESS SHAPE IS THE FRAGILE PART and is why `SAB_REACH` checks it. The
# pattern needs a BOT-family branch (to route it to this engine at all) AND a
# nullable second branch (to keep an interior start state live, so `start_max`
# is the subject length rather than 0 or `search_from`). A pure `(?m)^` or
# `\G` pattern is SELF-GATING and detects nothing — which is precisely why
# this site went unwitnessed for a milestone, and why a future change that
# routed the witness to the other engine must make this row read UNREACHED
# rather than quietly green.
#
# WHAT SEES IT: `tests/utf8/run_startbnd_diff.sh` §5's `attempt-startloop`
# cell and nothing else — MEASURED at the landing, exactly 1 of 7 cells, the
# other six staying green because they exercise the other two mechanisms.
# That discrimination is the row's value: a matrix in which S234 and S235 fire
# the same cells would not be telling two mechanisms apart.
SAB_ID="S235-attempt-loop-ungated"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="startbnd harness"
SAB_HARNESS_TARGET="tests/utf8/axis11_startpos_boundary.rxt"
SAB_DESC="ENG_ATTEMPT's emitted start loop loses its character-boundary continue, so an attempt engine under -e utf8 tries starts inside a character again — K50 site 2, which the charter's own site list had no witness for"
SAB_DOC_FIGURE="docs/dev/known_issues.md K50's SITE LIST item 2 and its FIXED block's site-2 table; docs/design/utf8_design.md 5.5"
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx -e utf8 --features assertions,modifiers -o - -- "(?m)^a|\\B" | grep -o "start_max = subject_length" | head -1'
SAB_REACH_EXPECT='start_max = subject_length'
SAB_BEFORE='                "        if (start > search_from && !(%s)) continue;\n", sbnd);'
SAB_AFTER='                "        (void)search_from; /* SABOTAGE S235 */%s\n", "");'
