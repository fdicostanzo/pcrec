# S3440 — [ART-POSS-ARMS]/K147 (r64 F5, lane k147f2): ARM B's DEPTH-BOUND
# WIDEN READS THE ACCUMULATOR, NOT THE REFERENCE'S WIDENED ANSWER.
# (src/opt/possessify.c, first_eval's `widen:` label.)
#
# When a reference chain runs past PCREC_MAX_POSS_REF_DEPTH (64 referenced
# groups that themselves hold references), a member in progress or out of range
# widens the reference to fst_leaf's answer (every byte). The plant returns the
# members resolved so far instead (`f->acc`: here nothing), which is a NARROWER
# set: the quantifier before the reference then looks disjoint from it and is
# possessified, and the match changes answer. The witness is a chain of 65
# groups, `(x)(\1)...(\64)x+\65`, on x^67: libpcre2 10.46 and python3 `re`
# match (0, 67); the planted compiler answers NOMATCH. No corpus cell reached
# this edge before the two B-depth BOUND cells (K=64, the control; K=65, the witness) this row's witness
# lives in.
SAB_ID="S3440-poss-b-depth-widen-reads-acc"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm B'\''s depth-bound widen returns the members resolved so far, not the reference'\''s widened (all-bytes) answer: `(x)(\1)...(\64)x+\65` on x^67 turns NOMATCH'
SAB_DOC_FIGURE="Validated by plant at lane k147f2 (r64 F5): the K=65 cell goes NOMATCH; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3440."
SAB_REACH='P=$(python3 -c "print('\''(x)'\''+'\'''\''.join('\''(\\\\%d)'\''%i for i in range(1,65))+'\''x+\\\\65'\'')") && "$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "$P" && grep -q "^#define RX_VM_POSS_ARMS 0x0u$" "$REACH_TMP/o.c" && echo REACH-S3440'
SAB_REACH_EXPECT="REACH-S3440"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(x\)\(\\1\)\(\\2\).*\(\\64\)x\+\\65$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    v = fst_leaf(q, f->a);'
SAB_AFTER='    v = f->acc;   /* SABOTAGE S3440: the depth-bound widen reads the accumulator */'
