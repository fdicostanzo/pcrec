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
SAB_BEFORE='            r = kit_run_decide(d->rate, ro, sets_at, w->set[hint_at], n, k ? &r : NULL);'
SAB_AFTER='            { kit_member m0 = { r.scan, kit_mass(d->rate, w->set[hint_at + r.scan], 1, KIT_MASS_SUM) }, m = kit_run_member(d->rate, sets_at, w->set[hint_at], n, 0, k ? &m0 : NULL, T_MASS_STRETCH); r = (kit_run_reply){ m.pos >= 0, (uint8_t)m.pos, 0, (uint8_t)n }; }   /* SABOTAGE S3006 */'
# RE-PLANTED (lane k382cm, 2026-11-12), the same plant: K38-2's reply is mf_run_reply's four fields
# (has_scan, scan, ver_lo, ver_len; no mass), so the previous answer's mass is read from its set as
# kit_run_decide does, and the reply is built from four fields (scan the member, the whole run verified,
# as the decision's `after` answer). The old 5-field AFTER did not compile (cloud run 43239936557
# shard 7: BUILD-FAILED, ANOMALY).
# RE-ANCHORED (lane d27fix, 2026-11-13), the same plant: the ranking's options are now `ro` (the art's
# tie, or a pinned R's member tie; d27fix F1), and the call is one line.
