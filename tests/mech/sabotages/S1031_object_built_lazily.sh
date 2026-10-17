# S1031 — [WINDOW-E1] THE OBJECT IS BUILT LAZILY, ON THE FIRST KIT CALL
# (src/core/compile.c / src/gen/memfn_sites.c): the eager build after
# `pcrec_find_resolve` moves into `pcrec_memfn_art`, so the build point
# depends on which kit call comes first, and an attempt that reaches no kit
# call builds nothing (window_contract.md rev 3.1 M5, §3.3 rule 3).
#
# Detector: run_findings_tests.sh §14 C-E1-1's ordering assertion (each
# attempt's object records come immediately after its resolve record).
SAB_ID="S1031-object-built-lazily"
SAB_FILE="src/core/compile.c"
SAB_SUITES="findings"
SAB_DESC='the analysis object is built inside pcrec_memfn_art at the first kit call instead of in compile_driver right after the chain resolves'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §14 (C-E1-1 ordering: object records after the readers'\'' or missing).'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern abc && echo REACH-E1-ANY-COMPILE'
SAB_REACH_EXPECT="REACH-E1-ANY-COMPILE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_memfn_analysis_build(&cx);
'
SAB_AFTER='        /* SABOTAGE S1031: the eager build removed (built lazily in pcrec_memfn_art) */
'
SAB_FILE2="src/gen/memfn_sites.c"
SAB_BEFORE2='        const mf_measures *ms = cx->emit_in && cx->emit_in->harness'
SAB_AFTER2='        pcrec_memfn_analysis_build(cx);   /* SABOTAGE S1031: lazily */
        const mf_measures *ms = cx->emit_in && cx->emit_in->harness'
SAB_COUNT2=1
