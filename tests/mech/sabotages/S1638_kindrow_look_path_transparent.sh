#!/usr/bin/env bash
# S1638 (S-IC21; [INLINE-C] stage 1a, lane ic1a, 2026-10-26; docs/design/inline_c.md §1.8, docs/dev/lanes/ic1a_report.md) -- the PER-KIND ROW's PATH column for the lookaround flips GATE -> TRANSPARENT: possessify's next-character readers (`fst_row` in first_of, `gk_row` in gk_build) model a lookaround as ABSENT, so `a*(?=a(?!a))` reads its follower as empty-then-end, the star is possessified, and the matches that needed the star to give back are lost. The path family's row read ([ART-POSS-ARMS] rev 2.1 N1 is the same hazard spelled per arm).
# Detector: the corpus harness on tests/possessify/composition_d27.rxt. MEASURED by plant at landing: 18 of 9002 cases fail.
SAB_ID='S1638-kindrow-look-path-transparent'
SAB_FILE='src/core/kindrow.def'
SAB_SUITES='harness'
SAB_DESC='the lookaround row reads PATH TRANSPARENT: possessify treats a lookaround follower as absent and possessifies a quantifier whose giveback the lookaround needs'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ic1a_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1638.'
SAB_HARNESS_TARGET='tests/possessify/composition_d27.rxt'
SAB_REACH='"$PCREC" --features all --engine=vm --emit-ir -p rx --pattern "a*(?=a(?!a))" | grep -qP "^possessify\t0/1\t" && echo REACH-LOOK-FOLLOWER-DECLINED'
SAB_REACH_EXPECT='REACH-LOOK-FOLLOWER-DECLINED'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='KIND_ROW(A_LOOK,    ZERO, GATE,        NONE,   NFA_ERASED_LOOK)'
SAB_AFTER='KIND_ROW(A_LOOK,    ZERO, TRANSPARENT, NONE,   NFA_ERASED_LOOK)   /* SABOTAGE S1638 */'
