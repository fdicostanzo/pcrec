# S994 — [WINDOW-E1] THE OBJECT IS BUILT ONCE PER PROCESS
# (src/gen/memfn_sites.c, `pcrec_memfn_analysis_build`): a static cache
# hands every later compile in the process the FIRST compile's object, so a
# second target under a different analysis, or a retry attempt, offers the
# kit data it does not compile under (window_contract.md §3.3 rule 3: one
# object per compile ATTEMPT).
#
# Detector: run_findings_tests.sh §14 C-E1-4's two-target fixture
# (`multi2.rxt`: t_web under weblog, then t_def under none) and the ordering
# assertion (an attempt with no object record after its resolve record).
SAB_ID="S994-object-once-per-process"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="findings"
SAB_DESC='pcrec_memfn_analysis_build caches the first object in a static and returns it to every later compile in the process'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §14 (C-E1-1 ordering; C-E1-4 multi2: the second target'\''s attempt builds no object).'
SAB_REACH='python3 "$TREE/tests/findings/e1_fixtures.py" "$TREE" "$REACH_TMP/fx" && mkdir -p "$REACH_TMP/o" && "$PCREC" -o "$REACH_TMP/o" "$REACH_TMP/fx/multi2.rxt" && grep -q "_FINDINGS \"byte-rate=weblog:" "$REACH_TMP/o/t_web.c" && grep -q "_FINDINGS \"byte-rate=default:" "$REACH_TMP/o/t_def.c" && echo REACH-E1-TWO-TARGETS'
SAB_REACH_EXPECT="REACH-E1-TWO-TARGETS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    while (pcrec_find_query(n)) n++;'
SAB_AFTER='    static const mf_analysis *once;   /* SABOTAGE S994: once per process */
    if (once) { cx->job->analysis = once; return; }
    while (pcrec_find_query(n)) n++;'
SAB_FILE2="src/gen/memfn_sites.c"
SAB_BEFORE2='    cx->job->analysis = an;
}'
SAB_AFTER2='    cx->job->analysis = an;
    once = an;
}'
SAB_COUNT2=1
