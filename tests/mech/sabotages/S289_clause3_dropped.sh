# S289 — [OPT-LITSCAN] S1 CLAUSE 3 DROPPED (a C2 ARTIFACT TAKES THE RUN ROW)
# (src/gen/emit_dfa.c, `pf_run_applies_common`): clause 3, IDENTITY -- "the
# scan is the same byte at the same offset it is today" -- is deleted, so
# the run-pinned row's predicate no longer checks that the MODEL's own
# candidate-start scan actually lands on the run's own scan member. A class
# C2 pattern, whose model scans a DIFFERENT byte at a different offset than
# the run's pick, now wrongly takes the run-pinned row. litscan_s1.md §7.1
# row (f).
#
# STRUCTURAL: the witness must stamp the OFFSET-SET form with its model
# OFFSETS, and reads run-pinned with a wrong OFFSETS list under the plant.
SAB_ID="S289-clause3-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks offsetskip"
SAB_DESC="pf_run_applies_common drops clause 3 (IDENTITY: the model's own scan is the run's own scan member), so a class-C2 pattern whose model scans a different byte at a different offset than the run's pick (\\Bfoo\\B: the model scans 'o' at offset 1, not the pick 'f') is wrongly admitted to the run-pinned row instead of staying offset-set-bounded"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S289."
# [MECH-REACH] the witness stays offset-set-bounded (never run-pinned) on
# the clean tree.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\Bfoo\\B" && grep -q "^#define RX_DFA_PREFILTER \"offset-set-bounded\"" "$REACH_TMP/o.c" && echo REACH-C2-STAYS-OFFSET-SET'
SAB_REACH_EXPECT="REACH-C2-STAYS-OFFSET-SET"
SAB_COUNT=1
SAB_BEFORE='    if (o->nsel > 0) {
        if (o->k[o->sel[o->scan]].k != sp) return false;
    } else if (!(sp == 0 && u->kind == DFA_PF_MEMCHR &&
                 u->cand.byte == r->bytes[r->idx])) {
        return false;
    }'
SAB_AFTER='    /* SABOTAGE S289: clause 3 (IDENTITY) dropped -- the run row is
     * taken whatever the model scans. */'
