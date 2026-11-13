#!/usr/bin/env bash
# S3006 -- R-38 K38-1 (docs/design/memfn/span_runs_sheet.md rev 1.2 §1 Goal 2, §5's K38-1 row; lane k381).
# A READER BYPASSES THE RUN DECISION: translate's RQ-2 ranking (window.c) asks kit_run_member directly,
# with today's tie row, instead of kit_run_decide. No byte moves (the two agree until a lever acts on
# kit_run_decide alone, K38-2a's `run-tie-left`), so no answer, text or reply check can see it; the
# decider census cannot either (it reads a declared map). Detector: the RUN CALLERS section of
# tests/memfn/decider_census.py (kit_run_member( called from translate, not in its exact caller map),
# run as part `census` of memfnfinder.
# R-38 K38-2a (lane k382a) RE-ANCHORED, the same plant: the ranking's call now passes the run
# decision's options (kit_run_opts_of), spelled over two lines.
SAB_ID="S3006-rank-asks-member-directly"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC="translate's ranking asks kit_run_member directly, bypassing the run decision (zero bytes; the caller check reds)"
SAB_DOC_FIGURE="HAND-MEASURED by lane k381 2026-11-10 (docs/dev/lanes/k381_report.md): the row's plant applied by hand to a git archive of the lane's tip, decider_census.py --no-plants: 3fail (run callers of kit_run_member and of kit_run_decide; translate:run-rank's anchor). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3006."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        r = kit_run_decide(rate, kit_run_opts_of(art, s, KIT_RUN_WHOLE), sets_at, sets, n,
                           k ? &r : NULL);'
SAB_AFTER='        { kit_member m0 = { r.scan, k ? kit_mass(rate, sets + 32u * r.scan, 1, KIT_MASS_SUM) : 0 }, m = kit_run_member(rate, sets_at, sets, n, KIT_CAND_FINDABLE, k ? &m0 : NULL, T_MASS_STRETCH); r = (kit_run_reply){ m.pos >= 0, (uint8_t)(m.pos >= 0 ? m.pos : 0), 0, (uint8_t)n }; }   /* SABOTAGE S3006 */'
# RE-PLANTED (lane k382cm, 2026-11-12), the same plant: K38-2's reply is mf_run_reply's four fields
# (has_scan, scan, ver_lo, ver_len; no mass), so the previous answer's mass is read from its set as
# kit_run_decide does, and the reply is built from four fields (scan the member, the whole run verified,
# as the decision's `after` answer). The old 5-field AFTER did not compile (cloud run 43239936557
# shard 7: BUILD-FAILED, ANOMALY).
# RE-ANCHORED 2026-11-13 (lane partd, R-38 Part D; part_d.md §2.1 item 3): the ranking moved into
# run_rank, ONE function shared by translate and run_part_terms; the call reads run_rank's own
# variables (rate, sets, n), and the member's candidates are named (KIT_CAND_FINDABLE, the run
# decision's column), the same plant.
