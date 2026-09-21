# S249 ([OPT-DIAL] design §6.1a, candidate SAB-D1) — THE POLICY TABLE'S TWO
# SIZE-LEANING COLUMNS ARE SWAPPED, AND EVERY ANSWER CHECK IN THE TREE STAYS
# GREEN.
#
# `src/core/tune.c`'s `TUNE_TABLE` is DATA: one row per `--tune=N` position,
# each a tuple of (bar, threshold, vm-entry-term, deny-mask). This plant
# swaps the VALUE TUPLES of the `−2` (`min-size`) and `−1` (`size`) rows
# while leaving their `pos`/`token` fields alone — the shape a real transcription
# error takes (a column reordered while copying a table), not an invented
# defect. `−2` therefore reads `−1`'s values (bar 85, threshold 80,000, no
# premul denial) and `−1` reads `−2`'s (bar 95, threshold 40,000,
# `PCREC_NO_PREMUL_TABLE` denied).
#
# WHY EVERY ANSWER CHECK STAYS GREEN. Every axis the table moves is
# ANSWER-IDENTITY-preserving by the allowlist's own construction
# (docs/spec/tuning.md §5.4's four ratified cells are all D47.3-family
# switches or the [ART-SIZE] ladder's own parameters, none of which the
# axis-identity sweep or the corpus can distinguish from a correctly-wired
# table): `--tune=min-size` still emits SOME artifact, it matches the same
# subjects, and `make test`/`make test-axes` cannot tell "the −2 artifact
# denies premul-table" from "the −2 artifact denies nothing, because the
# table swapped its cell in from −1". THAT is the whole reason
# `tests/codegen/run_tune_dial.sh` (design §6.1a's MECHANISM-STATE
# CROSS-CHECK) had to be written: it recovers each moving mechanism's ACTUAL
# state from the artifact's EMITTED TEXT and compares the recovered set
# against docs/spec/tuning.md §5's promised cell set for that position — the
# expectation side is the SPEC table, never `src/core/tune.c`'s own copy
# (docs/dev/learnings.md §3: a check must not share a source with what it
# controls).
#
# THIS ROW IS THE ONE DESIGN §6.1a NAMES AS PROVING THE CROSS-CHECK IS NOT
# VACUOUS. It must fire on the `−2` witness's PREMULTIPLIED-TABLE state
# (recovered per §6.1a's table: "whether the transition table's entries are
# multiplied by the row stride") AND on BOTH ladder parameters at `−2` — three
# independent recoveries, all wrong at once, from one two-hunk data edit.
#
# ============ VERIFIED 2026-09-17, lane dialimpl (the shipped compiler, current tree) ============
# Two compound probes, each run at `--tune=min-size` (the row's target
# position) AND at `--tune=balanced` (the control), confirm the CURRENT
# (unsabotaged) tree produces the values this row's swap would corrupt:
#
#   premul witness `a(b|c)+d` (--no-captures, so the pattern stays a DFA
#   artifact and RX_DFA_TABLE is meaningful):
#     --tune=min-size  ->  RX_DFA_TABLE "indexed"        (premul DENIED, correct)
#     --tune=balanced  ->  RX_DFA_TABLE "premultiplied"  (premul allowed, correct)
#
#   ladder witness `(a{10,20}){10,50}` (--engine=vm, forced through the
#   [ART-SIZE] size term):
#     --tune=min-size  ->  RX_UNROLL_K_WHY "size-model"  (threshold 40,000 CROSSED)
#     --tune=balanced  ->  RX_UNROLL_K_WHY "default"     (threshold 120,000 NOT crossed)
#
# Under S249's swap, `--tune=min-size` would instead read `−1`'s cell set —
# RX_DFA_TABLE "premultiplied" (premul no longer denied) and, because the
# ladder witness's own size sits below 80,000, RX_UNROLL_K_WHY "default"
# (the ladder stays inert instead of engaging) — flipping BOTH witnesses
# simultaneously, which is what "swap, don't perturb one cell" is for.
SAB_ID="S249-tune-columns-swapped"
SAB_FILE="src/core/tune.c"
SAB_SUITES="tunedial"
SAB_DESC="the dial's policy table has its -2 (min-size) and -1 (size) rows' value tuples swapped -- a transcription-shaped defect, not an invented one -- so --tune=min-size gets -1's bar/threshold/premul-denial and --tune=size gets -2's. Every answer check stays green (the axis is answer-identity-preserving by the allowlist's own construction); only the mechanism-state cross-check (run_tune_dial.sh), which recovers each moving mechanism's ACTUAL state from the emitted text and compares it against docs/spec/tuning.md's promised cell set, can see it. This is design section 6.1a's candidate SAB-D1, the row that proves the cross-check is not vacuous: it must fire on the -2 witness's premultiplied-table state AND on both ladder parameters at once"
SAB_DOC_FIGURE="Reach probes verified 2026-09-17 against the shipped compiler in this worktree (both directions, min-size vs balanced, on two independent witnesses -- see header). CANONICAL SOLO RUN 2026-09-17 (bash tests/mech/run_sabotage_matrix.sh S249, tree 5f2d757d): the edit APPLIES, the sabotaged tree BUILDS cleanly, reach:ok(4/4) against the clean reference tree, tunedial:8fail/9pass -- DETECTED, unexpected: 0. Those counts are exactly what the same plant measured by hand against a 17/0 baseline before the row was written (run_tune_dial.sh's own VALIDATION header, plant 1), which is what makes this a VERIFIED detector rather than a merely wired one. THE RED ARMS LOCALISE RATHER THAN GOING UNIFORMLY RED, and that is the point of the row: section 3a fires in BOTH DIRECTIONS AT ONCE (-2 recovers allow where the contract says deny AND -1 recovers deny where it says allow, which a one-directional arm would have half-missed), 3b fires on both ladder parameters, 4 fires on the nesting AND on its own non-vacuity guard, and sections 1 and 2 STAY GREEN because the plant moves neither the stamp nor position 0. THE CORPUS ARM IS GREEN BY CONSTRUCTION: every switch the dial moves is independently answer-preserving, so a miswired policy table changes no answer anywhere in the tree at any position -- if a row on this arm ever DOES move the corpus, the dial has stopped being answer-identical and that is a larger finding than this row was written for. AN EARLIER RUN AT THE PARENT COMMIT SCORED DETECTED WITH tunedial:ERRfail/?pass AND IS SUPERSEDED: the suite script was uncommitted, so the arm found no log and its own default treated the absence as a failure -- a FALSE detected, recorded in dialimpl_report.md section 3.2 as a pre-existing property of every mech arm. [FIGURE ADDENDUM, manager at the mechfix merge 2026-09-17: at post-k59rung HEADs the same solo run reads tunedial:11fail/9pass -- the +3 is the K59 ladder machinery's own sub-checks failing under the plant, A/B-verified identical through the PRE-mechfix scorer at the same HEAD (mechfix_report.md), so the growth is suite growth, not the scorer change; the 8fail/9pass above remains correct at its recorded pin 5f2d757d.]"
SAB_REACH='"$PCREC" -p rx --no-captures --tune=min-size -o "$REACH_TMP/premul_ms.c" --pattern "a(b|c)+d" && grep -h "RX_DFA_TABLE" "$REACH_TMP/premul_ms.c" && "$PCREC" -p rx --no-captures --tune=balanced -o "$REACH_TMP/premul_bal.c" --pattern "a(b|c)+d" && grep -h "RX_DFA_TABLE" "$REACH_TMP/premul_bal.c" && "$PCREC" -p rx --engine=vm --tune=min-size -o "$REACH_TMP/ladder_ms.c" --pattern "(a{10,20}){10,50}" && grep -h "RX_UNROLL_K_WHY" "$REACH_TMP/ladder_ms.c" && "$PCREC" -p rx --engine=vm --tune=balanced -o "$REACH_TMP/ladder_bal.c" --pattern "(a{10,20}){10,50}" && grep -h "RX_UNROLL_K_WHY" "$REACH_TMP/ladder_bal.c"'
SAB_REACH_EXPECT="#define RX_DFA_TABLE \"indexed\"
#define RX_DFA_TABLE \"premultiplied\"
#define RX_UNROLL_K_WHY \"size-model\"
#define RX_UNROLL_K_WHY \"default\""
SAB_COUNT=1
SAB_BEFORE='    { PCREC_TUNE_MIN_SIZE,  "min-size",  95,  40000, 0,
      PCREC_NO_PREMUL_TABLE },'
SAB_AFTER='    { PCREC_TUNE_MIN_SIZE,  "min-size",  85,  80000, 0, 0 },   /* SABOTAGE S249 hunk 1: swapped in the size row tuple */'
SAB_FILE2="src/core/tune.c"
SAB_COUNT2=1
SAB_BEFORE2='    { PCREC_TUNE_SIZE,      "size",      85,  80000, 0, 0 },'
SAB_AFTER2='    { PCREC_TUNE_SIZE,      "size",      95,  40000, 0,
      PCREC_NO_PREMUL_TABLE },   /* SABOTAGE S249 hunk 2: swapped in the min-size row tuple */'
