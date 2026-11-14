#!/usr/bin/env bash
# S1700 ([REQRUN-VM], lane reqvm1) -- THE ATTEMPT LOOP KEEPS THE WINDOW'S HIT
# WITH THE WHOLE RUN'S K. `handoff-attempts` subtracts the whole run's K
# (`whole_maxoff`) from the kept part's position; the plant keeps the WINDOW's
# part (0) instead, a hit up to (window offset - whole offset) bytes later, so
# the first attempt starts past the match. Detector: tests/litscan/
# handoff_vm.rxt (bench subst case 7's pattern, whole `https://www.` at 0,
# window `s://www.` at 4, K 0).
# RE-AIMED 2026-11-11 (lane k382, R-38 K38-2; span_runs_sheet.md rev 1.3 §5's K38-2 row): pcrec no longer
# keeps a part (`keep` retired with the cut: one derived run part, ret_pred). The intent, a
# hit LATER than the run occurrence's position 0 kept while the whole run's K is subtracted,
# moves onto the kit's ASSIGNed value (memfn/src/precheck.c run_line): the run part returns
# the occurrence's position 0, and the plant assigns the scan position instead (+ the part's
# term offset + plan_pos; +7 on the witness), so the first attempt starts past the match.
# Detector: tests/litscan/handoff_vm.rxt (the harness arm); G2's oracle reads the same value.
SAB_ID='S1700-attempts-keep-window'
SAB_FILE='memfn/src/precheck.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff_vm.rxt'
SAB_DESC='the kit'"'"'s ASSIGN line keeps the run part'"'"'s scan position instead of the run occurrence'"'"'s position 0 while pcrec subtracts the whole run'"'"'s K, so the VM attempt loop'"'"'s first attempt starts past matches'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1700.'
# RE-AIMED 2026-11-13 (lane s2tri, [RUN-POS-SET] flip 2 -> 128): the run now extends through
# the host alternation's union positions (RX_REQ_RUN "68747470733a2f2f7777772e[6168][636f][6d6f][656c]@7"
# on the old probe's (acme|hooli), was "...7777772e@7"), so the pinned run read UNREACHED. The probe
# now compiles the DETECTOR's own witness (handoff_vm.rxt's bench subst case 7 pattern) and pins
# its flipped run; K 0, the kit's ASSIGN line and the attempt loop's handoff are unchanged.
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '"'"'(https://www\.(?:acme|globex|initech|umbrella|hooli)\.(com|de|fr|nl|org)/[^"?\s]*)(?:(\?(?:[^"\s]*&)?tld=)(?!\2\b)[a-z]+|(?!\?(?:[^"\s]*&)?tld=)(\?[^"\s]*)?(?="))'"'"' && grep -q '"'"'^#define RX_REQ_HANDOFF "0"'"'"' "$REACH_TMP/o.c" && grep -qF '"'"'#define RX_REQ_RUN "68747470733a2f2f7777772e[6167-6975][636c-6f][62696d6f][62656c7274]@7"'"'"' "$REACH_TMP/o.c" && grep -qF '"'"'size_t handoff_position = rx_reqrun(subject, subject_length, search_from);'"'"' "$REACH_TMP/o.c" && grep -q '"'"'attempt_position = handoff_position;'"'"' "$REACH_TMP/o.c" && echo REACH-ASSIGN-POSITION-0'
SAB_REACH_EXPECT='REACH-ASSIGN-POSITION-0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (ofs_fn_call(art, h, p, r->fns[i], o)) return -1;
        kit_out(o, ";\n%sif (%s >= %s) %s\n", ind, h->result, h->n, h->on_miss);'
SAB_AFTER='        if (ofs_fn_call(art, h, p, r->fns[i], o)) return -1;
        kit_out(o, " + %d", (int)(p->term[0].offset + p->plan_pos));   /* SABOTAGE S1700 */
        kit_out(o, ";\n%sif (%s >= %s) %s\n", ind, h->result, h->n, h->on_miss);'
