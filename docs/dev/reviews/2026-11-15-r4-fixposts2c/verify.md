
## RESPELL-1
Spec tuning.md §2.28¶3: "`AKIA|AGPA|AIDA|AROA` reports `A[GIKR][ADIP]A`". Ran `$W/build/pcrec --features all --emit-main -p rx -o x.c --pattern 'AKIA|AGPA|AIDA|AROA'` -> `#define RX_REQ_RUN "41[47494b52][44494f50]41@3"` = A [G I K R] [D I O P] A (44=D 49=I 4f=O 50=P). Spec says [ADIP], compiler [DIOP]; third bytes of the branches are I,P,D,O, no A.
HOLDS

## RESPELL-2
(i) req.c:661 `RB_ROW_SCAN(i, w, rr_alt_rows, rr_alt_rows[i].row(w,&l,&r,&t));` then :662-663 calls the same row again with `&o`. rr_alt_union (618-630) -> rn_common_head (500-509) -> rb_pd_join (792-804), which does `pcrec_arena_alloc(&cx->arena, 32)` when neither set contains the other: a side effect, contradicting the macro comment (:387 "side-effect-free expression TEST"). It runs twice per accepted alternation (arena leak of the first copy; answer-neutral). Macro comment is thus inaccurate for rr_alt. (I did not check rn_put/ctx_fail.)
(ii) BASE req.c:642-646 loops with `!row(w,&l,&r,&o)` and stops at the first success: each row called once. Claim holds.
(iii) rr_alt_union writes *o only after `u.n != n` check passes (returns false before any write at 619-627), so a false return leaves *o untouched; scanning with `&o` directly is valid. rn_better double-call not re-checked beyond the line :485 TEST being a row call.
HOLDS

## SABROWS-1
Ran `$W/build/pcrec -p rx --engine=vm --features all -o s$i.c --pattern P`:
- `(?:ab){3,}?`: REQ_RUN "616261626162@5", WHY "emitted", `slot_values[2] + 6) goto rx_fail;`
- `(?:a{2,}?|x)[ab]`: REQ_RUN "none", WHY "none", `+ 2)`
- `z(?:a{3,}?|x)c?`: REQ_RUN "none", WHY "emitted", `+ 3)`
- `z(a){3,}?c?`: REQ_RUN "7a616161@0", WHY "emitted", NO `slot_values[2] +` reach line at all (stricter than the critic's "+ 3").
S711: SAB_HARNESS_TARGET=tests/base/vm_lazy_rmin_prefix.rxt; grep shows the file contains `z(a){3,}?c?` (158,167), `(?:a{2,}?|x)[ab]` (268), `z(?:a{3,}?|x)c?` (276) but NOT `(?:ab){3,}?`. The row's own comment says the detector moved to the rxt:265-282 blocks, and SAB_DESC says stride 2 is answer-invisible. So SAB_REACH witness is not a detector cell, and it is pre-check-masked (REQ_RUN emitted). The probe only proves the emitter writes the stride-2 test.
Minor correction: critic says z(a){3,}?c? gives `+ 3`; here the line is absent.
HOLDS (with that minor correction)

## AXES-1
Copied the block (run_axes.sh:1786-1794) to verify/blk.sh, CC=gcc. Unmodified walk_arms.def: `OK read=5`. A copy with the `WALK_ARM(TIE,...)` row deleted: `OK read=4` - no FATAL, the arm silently leaves the sweep. Other checks: grep of tests/, scripts/, Makefile finds no restore-name list or count floor for the arms in `make test`/run_axes.sh. One partial catch exists outside it: tests/ci/cloud_axes_check.sh (`make cloud-check`) compares the cloud shard table (tests/ci/cloud_axes_shards.tsv names `--harness=restore=tie` etc.) with the unsplit plan; a deleted arm still named in the table would read EXTRA/"selects NOTHING". It does not fire if the table row is deleted too, and is not in the per-PR tier. Also tests/mech sabotage rows S1907/S1908/S1922/S3131 reach-probe individual arms (they would go UNREACHED/red on a missing arm).
HOLDS (deleted-row blindness real; partly backstopped by cloud-check for a stale table row)

## AXES-3
memfn_arm.py:203-219 says floors "hold at their measured values: no floor lowered" (213) yet 214-217 say the floors are restated "over a different population" and "pinned from the corpus-only counts recorded above (cloud axes 43535669918: utf8 c-default 12, c-vm 13; pad 10, 12)", with the exact `--measure corpus=` re-measure "owed to boxqueue job 701". So the source is a recorded earlier cloud measurement (not a measurement in this subject), re-measure pending. Pins: kb/trim/w16/w32 12/13, pad 10/12 match those recorded numbers. Arithmetic: "old 15 == new 11 on the corpus" but pin is 12 (not 11); pad 13/14 -> 10/12: c-default drops 3 (= the 3 pad witnesses), c-vm drops 2, unexplained. Comment 226-227 ("14 -> 13 ... siblings' 15 hold") is stale. Also "no floor lowered" contradicts 15 -> 12. I did not open job logs.
PARTLY (the floors are pinned from a recorded, pre-subject cloud count, not unmeasured as such; the comment is internally inconsistent: 11 vs 12, c-vm 14->12, "no floor lowered")

VERIFY COMPLETE
