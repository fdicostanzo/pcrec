# verify.md — crit-covs2code, INLINE verification by the coordinator (skill §6.2: every item a one-call repro, a quote or a grep)

Box clock 22:58-23:00, subject build ad6f4cb56 (worktrees/crit-covs2code), round trace builds.

## CODE-CAP (EMIT-1, CONTRACT-1, SEAM-1) — HOLDS
- `build/pcrec -p rx --window-search-width=4095 -o c.c --pattern '[0-9a-f]{3400}'` -> rc 1, "pattern too large: 510342 bytes of emitted code (limit 500000) ... A repeat's body is replicated ...". Same with `--size-cap=degrade`: rc 1. Default width: rc 0, `RX_DFA_SCAN "unanchored"`.
- limits.md section 3.12¶4 (subject) says "... also runs the engine, through the size-cap ladder (§8.4) ...; the compile does not fail." False at this width.
- cover_cap.md (subject) header lines ~50-55 already list it OPEN (review r27 READ-3, "being worked by lane covs2c"); commit 3ec992759's subject says "READ-3 reproduced and stopped (not local)". New here: it binds from k ~ 3,330 for a 16-byte class / ~1,900 for `\w`, degrade does not rescue it, and the cap that binds is PCREC_MAX_VM_EMIT_CODE_BYTES.

## NEAR-MISS (EMIT-2, CONTRACT-2) — HOLDS
- `[0-9a-f]{1000}`, subject ("a" x 999 + "g") x 1000 (1 MB, no match), CONTRACT's tdrv.c find-all, gcc -O2, `taskset -c 7 perf stat -e instructions:u`, 3 repeats each:
  cover (`--window-search-width=4095`): 1,952,412,013 / 1,952,411,981 / 1,952,411,978 instructions:u (0.070 s);
  engine (default, `unanchored`): 9,240,934 / 9,240,933 / 9,240,932 (0.000 s). Ratio ~211x.

## SEAM-3 — HOLDS
- `git grep -n MF_RANK_MAX -- src cli lib` in the review tree: no hits. memfn/include/memfn.h:296 "pcrec asserts MF_RANK_MAX >= that bound where it fills the ranking". BASE emit_dfa.c:1446 had `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS, ...)` (then 32).

## SEAM-5 — HOLDS
- decisions.md at e1f6a8349, D198 (e) is the owner's question ("does pcrec need to tell kit to 'compact' its code?"); the sentence "The kit is told facts (D157), never asked to compact." is in D198 Consequences. cover_cap.md:1401 quotes it as D198 (e) without "(D157)".

## SEAM-6 — PARTLY
- Subject trace: `MFWSTMT COVER ? site ...` and `MFROUTED COVER ? -` for `[0-9a-f]{32}`. BASE trace build: `MFROUTED COVER ? -` too. So `routed_kind_name[]` lacking MF_SK_REPORT is PRE-EXISTING (MFROUTED); the subject's NEW MFWSTMT record inherits it.

## CHECKSAB-2 — HOLDS
- tests/mech/run_sabotage_matrix.sh ~1805-1812: on `make all` failure with SAB_EXPECT=BUILD-REFUSED, prints DETECTED without reading build.log text.

## CHECKHAR-1 — HOLDS
- cases.tsv by kind x arm: verdict 48 default / 1 N / 11 W; facts 19 / 2 W; answers (answers.tsv) 108 / 32 W. run_cover.sh:179-181 floor totals only (60/21/140).

Not re-verified (critic evidence judged sufficient: read-only structural claims with file:line, maintenance/doc tier): EMIT-3..6, CONTRACT-3/4, SEAM-2/4, CHECKSAB-1/3/4/5/6, CHECKHAR-2..6.

VERIFY COMPLETE
