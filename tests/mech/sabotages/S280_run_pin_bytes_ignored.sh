# S280 — [OPT-LITSCAN] S1 THE PIN IGNORES THE RUN'S BYTES
# (src/opt/prefix_k.c, `pcrec_prefix_ksets`): `run_o` becomes the first
# window of the walk that is all SINGLETONS, whatever bytes they are, instead
# of the window that spells `Job.req_run`. litscan_s1.md §7.1 row (g).
#
# The pin is an ANALYSIS fact the run rows trust. With the byte test gone,
# `/abcd[xy]/user` (run `/user` truly pinned at 6) reports a pin at 0, where
# `/abcd` sits; clause 3(b) then passes (`/` is the memchr byte at 0) and the
# row compares `/user` at offset 0 of every candidate — every match lost.
# MEASURED with the probe's walk at design time (litscan_s1.md §7.1).
SAB_ID="S280-run-pin-bytes-ignored"
SAB_FILE="src/opt/prefix_k.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/offsetskip/run_pinned.rxt"
SAB_DESC="the run pin no longer checks that the walk's singletons ARE the run's bytes, so a pattern whose run is pinned later than an earlier all-singleton window (/abcd[xy]/user) is pinned at the wrong offset, takes a run row, and compares the run where it is not: lost matches"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane s1build, single-row mech): DETECTED -- reach:ok(1/1), corpus:2fail/53pass (the two /abcd[xy]/user m cells of run_pinned.rxt), prechecks:1fail/288pass (§5.10 names the pattern stamping run-pinned). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S280."
# [MECH-REACH] the witness really is the C0 shape: a run, the memchr form, no run row.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "/abcd[xy]/user" && grep -q "^#define RX_REQ_RUN \"2f75736572@0\"" "$REACH_TMP/o.c" && grep -q "^#define RX_DFA_PREFILTER \"memchr\"" "$REACH_TMP/o.c" && echo REACH-C0-PIN-WITNESS'
SAB_REACH_EXPECT="REACH-C0-PIN-WITNESS"
SAB_COUNT=1
SAB_BEFORE='            while (i < r->len && o->k[ro + i].count == 1 &&
                   o->k[ro + i].byte == r->bytes[i])'
SAB_AFTER='            while (i < r->len && o->k[ro + i].count == 1)   /* SABOTAGE S280 */'
