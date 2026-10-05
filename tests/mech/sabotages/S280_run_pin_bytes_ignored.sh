# S280 — [OPT-LITSCAN] S1 THE PIN IGNORES THE RUN'S BYTES
# (src/facts/kset.c, `pcrec_run_pin` — re-anchored at [PATFACTS] step 3.4,
# which lifted the pin out of `src/opt/prefix_k.c` into the E3 fact
# `run_pin`; the plant and its intent are unchanged): the pin becomes the first
# window of the walk that is all SINGLETONS, whatever bytes they are, instead
# of the window that spells `Job.req_run`. litscan_s1.md §7.1 row (g).
#
# The pin is an ANALYSIS fact the run rows trust. With the byte test gone,
# `/abcd[xy]/user` (run `/user` truly pinned at 6) reports a pin at 0, where
# `/abcd` sits; clause 3(b) then passes (`/` is the memchr byte at 0) and the
# row compares `/user` at offset 0 of every candidate — every match lost.
# MEASURED with the probe's walk at design time (litscan_s1.md §7.1).
SAB_ID="S280-run-pin-bytes-ignored"
SAB_FILE="src/facts/kset.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/offsetskip/run_pinned.rxt"
SAB_DESC="the run pin no longer checks that the walk's singletons ARE the run's bytes, so a pattern whose run is pinned later than an earlier all-singleton window (/abcd[xy]/user) is pinned at the wrong offset, takes a run row, and compares the run where it is not: lost matches"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane s1build, single-row mech): DETECTED -- reach:ok(1/1), corpus:2fail/53pass (the two /abcd[xy]/user m cells of run_pinned.rxt), prechecks:1fail/288pass (§5.10 names the pattern stamping run-pinned). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S280."
# [MECH-REACH] the witness really is the C0 shape: a run, the memchr form, no run row.
# RE-PINNED 2026-10-05 (lane r1mtriage): S4 C3 (req-run-fold, abi 59) folds
# [xy] (one bit apart) into the run, which is now the masked hull
# /abcd[xy]/u (scan member @6, the second /) rather than /user; the probe
# read MISSING from C3's landing. The plant still reaches the pin: MEASURED
# on a4c752a2 with the plant applied, the witness flips memchr -> run-pinned
# (offsets 0*,1) and both run_pinned.rxt m cells (/abcdx/user 0 11,
# a/abcdy/user 1 12) report nomatch. /abcd[xq]/user is the C3-proof spelling
# of the original mechanism (run /user at 6, flips to run-pinned 0*,1,2,3,4
# and loses its matches under the plant) if the corpus ever moves to it.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "/abcd[xy]/user" && grep -q "^#define RX_REQ_RUN \"2f61626364782f75@6/fffffffffffeffff\"" "$REACH_TMP/o.c" && grep -q "^#define RX_DFA_PREFILTER \"memchr\"" "$REACH_TMP/o.c" && echo REACH-C0-PIN-WITNESS'
SAB_REACH_EXPECT="REACH-C0-PIN-WITNESS"
SAB_COUNT=1
SAB_BEFORE='        while (i < l && o->k[ro + i].count == 1 &&
               o->k[ro + i].byte == r->bytes[s0 + i])'
SAB_AFTER='        while (i < l && o->k[ro + i].count == 1)   /* SABOTAGE S280 */'
