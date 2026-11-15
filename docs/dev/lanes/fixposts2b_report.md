# fixposts2b -- FIX-NOW findings of review 2026-11-15 r3 fixposts2

Lane fixposts2b (sonnet), continuing lane/fixposts2. Subject: `docs/dev/reviews/2026-11-15-r3-fixposts2.md` (main). Rulings file absent (no later rulings).

## STATE AT HANDOFF

All nine findings applied and committed. `make strict` clean; `make test-codegen` result below; emitted bytes unmoved (490 pairs SAME). The corpus emit_sweep proof (job 700, re-queued) and the memarm re-measure (job 701, untouched) and the cloud `make test` are OWED.

## FIXES BY ID

- **CONTRACT-1 + CONTRACT-3 (FIXED, one respell).** `src/facts/req.c`: the helper (`rb_row_scan`, `RbRowHit`, four ctx adapters, `__typeof__`, void* casts, memcpy of `arm`) is gone; one bounded STATEMENT MACRO `RB_ROW_SCAN(i, w, tab, test)` (+ `RB_ROWS`) replaces it, the loop bound being the row count and `test` a side-effect-free expression over `tab[i]`. The catch-all is STRUCTURAL: it is no longer a table row (so it carries no `arm` to be wrong and a row appended after it is impossible) but the DEFAULT after the scan (`rn_first`, `rr_alt_affix`, `RB_REP_GAP`, `RB_ZERO_CUT`), taken when `i == RB_ROWS(tab)`. A `_Static_assert` on a row's arm is not expressible in gnu11 (the critic's probe), so the structure replaces it. `rr_alt`'s test row writes only a scratch `RbRuns`; the deciding row is re-run into the result. S474 re-anchored (`SAB_BEFORE` = the scan line; plant compiles -Werror, checked in scratch); anchor check: 1299 rows resolve.
- **CONTRACT-2 (FIXED).** `rn_better` returns `c >= 0 ? a : b`; with the default row `rn_first` a 0 answer reads `a` as at BASE.
- **CHECKS-1 (FIXED).** The reference (`memfn/tests/g2/g2_win_ref.c`) now also scans without the in-run filter and records `inrun_filt` where the filter changes the stop; the generator prints `filter-decisive N`; `run_g2_win.sh --reach` prints `REACH-G2W-INRUN rendered=R decisive=F agree=M` only when R >= 100, F >= `REACH_DECISIVE_FLOOR` (38, 43 measured less ~10%) and agree == rendered. MEASURED (seed 20261022): clean `rendered=200 decisive=43 agree=200` (token printed); plant lib (S3012's edit applied to window.c, scratch) `rendered=200 decisive=43 agree=157` (no token). Recorded in S3012's SAB_DOC_FIGURE.
- **CHECKS-2/3 (FIXED).** `tests/axes/run_axes.sh`: the restore arms are read by the preprocessor (`gcc -E -P` over an X-macro include of `walk_arms.def`), and counted both ways against the comment-stripped text (`gcc -fpreprocessed -dD -E -P`, rows = `WALK_ARM` tokens outside `#` lines); a mismatch, or zero arms, is FATAL. Checked in scratch: the clean .def reads empty, zero, rep, tie, alt; an appended `  WALK_ARM (SPC, "sp-c", 0)` (spaced, hyphenated name) is FATAL rather than dropped.
- **CHECKS-4 (FIXED, pin + comment).** `tests/axes/memfn_arm.py`: the vrun utf8 floors pinned from the recorded corpus-only counts (cloud axes 43535669918, recorded in the same file and in `s2arms_report.md`): kb/trim/w16/w32 utf8 c-default 12, c-vm 13; pad 10 / 12. The false comment ("a corpus loss of up to the witness count passed") replaced by the accurate one (restating, not tightening). The exact re-measure stays job 701 (not duplicated). No plan row filed (the manager's ruling named none; job 701 and the comment carry it).
- **CHECKS-5 (FIXED).** `partd_r_by_role.rxt` says 7 (now by name only, see CHECKS-6); unmatched `)` removed from all five headers.
- **CHECKS-6 (FIXED).** The five `tests/litscan/d27/partd_*.rxt` `# arms:` lines name the arms (moving, then `inert identity control:`) and carry no counts. No case line touched.

## VALIDATION

- `make strict`: clean. `scripts/m6read_check_sab_anchors.py`: 1299 rows, all resolve. `scripts/plan_lint.sh`: 0 violations.
- Emit identity: BASE (critic's build of 3ed7d9d71) vs this tree's `pcrec-harness`, 35 patterns (the critic's patterns.txt + p2.txt) x 7 arm configs x {byte, utf8}: 490 SAME, 0 DIFF, 0 RCDIFF, 0 BOTHFAIL (scratch/fixposts2b/emit.tsv).


## OWED

- emit_sweep proof of the respell: boxqueue job `700-main-fixposts2-emit` (cancelled and re-queued after the commit; same script `docs/dev/lanes/fixposts2_emit_job`, ref 3ed7d9d71); expect byte-identity.
- memarm re-measure (job 701, unchanged): pins the exact `corpus=` counts; re-pin 58/117/99/181 and the vrun floors only where it measures different.
- mechrows cloud run for S3012/S3129-S3132/S711/S288/S474 (predecessor's, still owed): `scripts/cloudrun --owner main --kind mechrows --rows S3012,S3129,S3130,S3131,S3132,S711,S288,S474 --name fixposts2`.
- cloud `make test` on lane/fixposts2 (this lane's last act): `--name fixposts2b`.
- `make test-codegen`: rc 0, `run_group: 21/21 scripts passed`.
- cloud `make test` dispatched: `cloud/main/test/fixposts2b` at 28686de00 (verdict arrives as CLOUD-DONE via queuewatch). Job 700 re-queued after the commit.
