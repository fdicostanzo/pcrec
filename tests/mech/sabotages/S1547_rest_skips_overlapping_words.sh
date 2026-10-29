# S1547 (lane r30b, 2026-10-29; [MEMFN] R-30, memfn/docs/requests.md): THE REST SKIPS TOO MUCH. After the lead, the rest drops every word that merely
# OVERLAPS the lead, not only one inside it, so bytes of the whole run outside the
# window are never compared (a weaker pre-check: answer-neutral, the matcher verifies).
# Section D's pinned led compare differs.
SAB_ID="S1547-rest-skips-overlapping-words"
SAB_FILE="memfn/src/runcmp.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the led compare's rest skips every word overlapping the lead, so whole-run bytes outside the window are never compared"
SAB_DOC_FIGURE="OWED: read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1547."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (at >= lo && at + w <= hi) continue;      /* inside the lead (R-30) */'
SAB_AFTER='        if (at + w > lo && at < hi) continue;      /* SABOTAGE S1547 */'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a)(b)(c)(d)(e)(f)(g)(h)(i)\\9" && grep -qF "if (!memcmp(subject + cand + 1, \"bcdefghi\", 8) && rx_w8(subject + cand) == rx_w8(\"abcdefgh\")) return cand;" "$REACH_TMP/o.c" && echo REACH-R30-LED-COMPARE'
SAB_REACH_EXPECT="REACH-R30-LED-COMPARE"
