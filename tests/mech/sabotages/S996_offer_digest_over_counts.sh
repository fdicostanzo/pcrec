# S996 — [WINDOW-E1] THE OBJECT'S DIGEST COMPUTED OVER THE COUNTS
# (src/core/findings.c, `pcrec_find_offer`): the offer digests the answering
# block's raw counts instead of the payload it hands over, so the object
# names a digest no stamp and no `rows_digest` reports. The plant site is the
# offer's own digest computation (window_contract.md §3.7.8): a copy of the
# record's `byte_rate_digest` would make the plant undetectable.
#
# Detector: run_findings_tests.sh §14 C-E1-1 (the object's digest against
# findings_ref.py's, recomputed from the fixture's rows) and C-E1-4 (object
# digest against the stamp's).
SAB_ID="S996-offer-digest-over-counts"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='pcrec_find_offer digests the answering block'\''s counts array rather than the derived ppm payload it hands the kit'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §14 C-E1-1 (every freq-answered cell'\''s digest) and C-E1-4.'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern abc && grep -q "_FINDINGS \"byte-rate=default:" "$REACH_TMP/o.c" && echo REACH-E1-ASKING-COMPILE'
SAB_REACH_EXPECT="REACH-E1-ASKING-COMPILE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    out->digest = find_queries[query].digest(payload);'
SAB_AFTER='    out->digest = find_queries[query].digest(fb->counts ? (const void *)fb->counts : payload);   /* SABOTAGE S996 */'
