# slotxfix — the FIX-NOW items of review 2026-11-15 r1 (memfn-slotx), lane report

Kit fix lane (opus) on lane/memfn-slotx, in the existing worktree `worktrees/slotx` (no new worktree). Subject:
the slot harness's slotx pieces (`docs/design/memfn/span_cards/slot/`), plus `tests/memfn/arm_fixtures.c`'s
`--frame`. Binding ruling: the RULED section of `docs/dev/reviews/2026-11-15-r1-memfn-slotx.md`, committed
as-is first (8e8207bfa). No emitted byte moves: no `src/`, `lib/`, `cli/` or `memfn/src/` edit, no abi event.

STATE: delivered. Scratch: `/var/tmp/pcrec-pcrec/scratch/memfn/slotxfix/` (`$X` below).

## Summary

Every FIX-NOW item of the ruling is fixed: F1, F2, F3, F4, F5, F8 (interim), F9, F10 (guard). F6, F7 and F11
are not this lane's (main's rulings / filed). Each fix was reproduced red on the unfixed code first
(f13a59356's slot dir, over a symlink tree carrying the unfixed `arm_fixtures.c`: `$X/oldtree`), then shown
green, and each check fix has a plant the check must catch. Four new sabotage rows: e1 S3168 (F1), e2 S3169
(F2), e3 S3171 (F5), e4 S3172 (F8). S3168/S3169 are slotx's two unused ids; S3170 is mfind's
(S3170_simdguarded_lever_arm_drops_lever.sh), so S3171/S3172 are the next free above it (all branches grepped).
The round's top lesson was run as this lane's own check: each touched or new row, re-run with its named check
disabled, goes MISSED (table under Validation).

Open for the kit manager / main (not done here, by the ruling): F7's §7.2 sentence and the mfind-report note
(main); F8's real ruling (per-target sets, the kit's leaning, or the multi-target format), until which the
mfcard window's draft REFUSES; F6 follows F8; F10's `mf_frame_c` unification is FILED (trigger: the next
¶15 placement change or a sixth host); F11 noted. The renamed timing job scripts' queue keys are now
`kit-mfcard-JMB`, `kit-mfcard-JMH`, `kit-mfcard-JMB-avx2libc`, `kit-mfcard-JMH-avx2libc` (nothing was queued
under the old keys by this lane; the queue was not touched).

## Fixes by id

Also fixed in passing: sabotage row f1 (S2937), whose plant anchor was already stale in the subject (the
full-table run below found it). It is re-anchored with the same intent.

| id | fix | red (unfixed) | green (fixed) | plant |
|---|---|---|---|---|
| F1 | `link.py` ISA_NEEDS is now a first-match table on (ENCODING, mnemonic, operands) -> features; `encoding()` reads the instruction bytes (`objdump --insn-width=16`; legacy prefixes and REX skipped as est.py's decoder does): 0x62 = EVEX -> avx512f (+avx512vl off %zmm), a `k*` mask-register row (avx512f), the high-register row `%[xy]mm16-31` (avx512f,vl); a VEX/EVEX instruction no row prices REFUSES (`ISA UNCLASSIFIED`). Every VEX `v*` instruction now needs avx (before: only with an %xmm/%k operand). | the critic's `isav4.py` on the unfixed link.py: w32 (keyed x86-64-v3) at `-march=x86-64-v4` and with `-mavx512bw -mavx512vl` -> `ok(avx,avx2,bmi,bmi2)`; swar (keyed generic) with kmovq/kandnq -> `ok(-)` (`$X/red/F1.out`) | same objects: all 6 REFUSED, w32 `needs avx512f,avx512vl (vpbroadcastd %eax,%ymm1)`, swar `needs avx512f (kmovq %rax,%k0)` (`$X/F1.green.out`); unplanted JMB dry run green, w32 `target_isa` still `avx,avx2,bmi,bmi2` | e1 S3168: the v3 region widened with `avx512f,avx512vl` -> JMB `ISA MISMATCH kit.find_byte.mfind-w32: keyed target x86-64-v3, its code needs avx512f,avx512vl` |
| F2 | rows for every feature x86-64-v3 enables (added fma, f16c, sse3, cx16, sahf, xsave); `isa_table_check(fx, floor)` (run by `build_objs`, every job and ctl) reads `--frame` of every planned arm's instance (all jobs of `plan.build()`), and each target's `--target-facts` features above the floor must be some row's, else `ISA TABLE: planned target T enables F above the floor, and no ISA_NEEDS row names it` | the critic's `isaprobe.py` on the unfixed table: `avx` deleted -> D2 `ok(-)`; `bmi2` deleted -> B6 `ok(-)`; `avx2` deleted -> w32 `target_isa` silently `avx,bmi,bmi2` (`$X/red/F2.out`) | `$X/bin/f2drill.py`: each of the 16 target-feature rows deleted in turn -> TABLE-REFUSED, naming that feature (`$X/F2.drill.out`); the full table passes every unplanted object | e2 S3169: the `fma` row deleted -> J2 `ISA TABLE: planned target x86-64-v3 enables fma above the floor` (no arm emits FMA, so only the table check can see it) |
| F3 | `sabotage.sh`: the case table is a function `row_def ROW` (PLANT=0 sets `job`/`want` and plants nothing); the control runs J2, the est self-test and every other job the selected rows name, green first, before any row. `TREE` honours `SLOT_TREE` (a copy of slot/ outside the tree, as plan.py already does) | unfixed sabotage.sh on a copy whose J6B is broken unplanted (no region at all): `control J2 dry run green`, `control est.py self-test green`, then t1 scored on the broken job (`$X/dis/red-F3-old.log`; it scored MISSED only because link's stderr tail cut gcc's line; a regression printing the want would score DETECTED, CHK-3's case) | fixed sabotage.sh on the same regression: `CONTROL red (the unplanted copy's JMB dry run)`, exit 2, no row scored (`$X/dis/fix-F3.log`) | the control is the check (its plant is the regression above) |
| F4 | v1's want is now the refusal: `selftest<TAB>\[slotx\] the draft split[^<TAB>]*<TAB>\(DRAFT-VER MISMATCH` | unfixed sabotage.sh, v1's plant plus draft_split's per-set check disabled: v1 DETECTED (`$X/dis/red-F4-old.log`) | fixed: v1 alone DETECTED on `(DRAFT-VER MISMATCH row kit.find_byte...`; with the per-set check disabled, MISSED (`$X/dis/dis-v1.log`) | v1 S3164 (re-aimed) |
| F5 | est.py self-test case `[F5] write_draft on the mfcard window`: `mf_draft` runs the REAL `write_draft` on the mfcard synth (a `cell_text.tsv` per ran job, the record's box/isa/libc/gcc, `draft_gate` stubbed for the call: the synth has no commit; the ks_ref digest runs), then reads each written set's row keys: ver 6's set is exactly the FORMS6 rows, ver 3's holds the unit and none of them, no ver-4 set | the critic's vB leak (`vrows = split.get(v, []) + (split.get("6", []) if v == "3" else [])`) in the unfixed est.py: self-test `54 cases, 0 wrong` (`$X/dis/red-F5-old/scr/control.est.out`) | self-test `56 cases, 0 wrong` | e3 S3171: the same leak -> the F5 case WRONG |
| F8 | interim: `write_draft` REFUSES the whole draft, before any file is written, when a set's rows were compiled in more than one kit target (`DRAFT-TARGET MIXED ver V's set would hold rows of targets ... under one class`; an unframed row is `generic`). Self-test case `[F8]`: the real targets (w16 x86-64, w32 x86-64-v3, others generic) -> refused, no `.v6` file | the unfixed writer writes `class x86_64/zen4` over the mixed ver-6 rows (RUL-2; the F8 case with the refusal removed is e4's plant, WRONG) | the F8 case ok | e4 S3172: the refusal removed -> the F8 case WRONG |
| F9 | jobs renamed J6B/J6H -> JMB/JMH ("JM" = the Mfind cards; plan.py says why: span_cards.md's J6 is S2g's vrun unit): plan.py, record.py WINDOWS, sabotage.sh rows t1 t2 r1 r2 k1, slot/CLAUDE.md, kit-grid.tsv's comment, slotx_report.md, the history index line; the prepared job scripts in `scratch/memfn/slotx/jobs/` (603/604/607/608 renamed `*-JMB*`/`*-JMH*`, their keys, 600/605/608 `ready_after`, 609 KEYS, 620, common.sh WJOBS). Left as dated records: the review text itself and mfind_report.md (whose J6B/J6H were mfind's own superseded jobs) | — | `git grep J6B\|J6H` outside those two and three binary .gz coincidences: 0 hits; the job dir greps clean | — |
| F10 | `arm_fixtures --frame` prints the family guard (`mf_family_c_of(t->family)->guard`, "" for the portable target) as a fourth form-feed part; `link.frame()` returns it (index 5, the old indices kept) and `framed()` writes it first in the TU, ahead of every `#include`, also for a family target with no region; the comments now say so | the unfixed JMB cell TU `arm4.c` begins `#include <stddef.h>` (no guard) | the fixed JMB dry run's `arm4.c` (w32) and w16 begin with the `#if !(defined(__x86_64__) && !defined(__ILP32__))` / `#error` guard; generic arms' TUs unchanged; cell-text hashes unchanged (FILE+BODY spans) | none (no codegen effect; the frame comment is now true) |

## Validation

All logs under `$X` = `/var/tmp/pcrec-pcrec/scratch/memfn/slotxfix/`. The box was held by a queue job
throughout; everything ran `nice`, make at `-j8`.

| what | command / log | verdict line |
|---|---|---|
| build + strict | `nice make -j8 && nice make strict -j8` (`$X/make.log`) | `BUILD+STRICT OK`; no `*** [` line |
| kit sections | `nice make -j8 test-memfn-finder test-memfn-arms test-memfn-targets` (`$X/make.log`) | `MEMFN-TESTS EXIT 0`; e.g. `finder_check checks passed: 1173 / failed: 0`, `purity checks passed: 7874`, final `checks passed: 18106, checks failed: 0`; no `*** [` line |
| sabotage anchors | `python3 -I scripts/m6read_check_sab_anchors.py` (`$X/make.log`; re-run after the f1 re-anchor) | `sabotages checked: 1299 (1353 anchor sites)`, `all anchors resolve`, rc 0 |
| est self-test | `est.py selftest` (`$X/est1.out`; also inside every sabotage control) | `== est SELFTEST ok: 56 cases, 0 wrong` (54 before + F5 + F8) |
| JMB dry run | `run.py dry JMB` (`$X/dryJMB.out`) | rc 0, every launch's gate and round check ok; cell_text w32 `x86-64-v3 avx,avx2,bmi,bmi2`; the guard heads w16/w32 TUs |
| full slot sabotage table | `slot/sabotage.sh $X/sabfull` (all 48 rows; `$X/sabfull.log`) | control green on J2 est J3 J4 plan JMB JMH; `47 DETECTED, 1 MISSED of 48 rows`: the miss was f1 PLANT FAILED, a stale anchor ALREADY in the subject (slotx moved est's gate lookup to `plan.card_of(card, key)`); re-anchored to that line with the same intent (live cards for the record's), re-run alone `$X/sabf1.log`: `f1 DETECTED`. So 48/48 |
| new and touched rows alone | `$X/sabA.log`, `$X/sabB.log` | t1 t2 v1 w1 e1 e2 e3 e4 DETECTED |
| THE LESSON: each touched/new row with its named check disabled must go MISSED | `$X/bin/disrun.sh` (patched copy of slot/, its own sabotage.sh); logs `$X/dis/dis-*.log` | t2 (isa_check returns at once) MISSED; e1 (EVEX read as VEX, the old reading) MISSED; e2 (isa_table_check returns at once) MISSED; v1 (draft_split's per-set check off) MISSED; e3 (F5 case forced ok) MISSED; e4 (F8 case forced ok) MISSED; r1 r2 (run.py's REJECT-RATE comparison off) MISSED; k1 (key_arm_mismatch blind to dim reject) MISSED. Each control green first. t1's refusal is gcc's own (no slot check to disable); v2 w1 untouched |
| red demos (unfixed code) | `$X/red/F1.out`, `$X/red/F2.out`, `$X/dis/red-F3-old.log`, `$X/dis/red-F4-old.log`, `$X/dis/red-F5-old/scr/control.est.out` | as in the Fixes table: F1 6 objects passed or needed only avx2, F2 deletions silent, F3 control green over a broken job, F4 v1 DETECTED without its check, F5 `54 cases, 0 wrong` under the leak |

Not run (outside the brief): `make test` and the full battery (no `src/`/`lib/`/`cli/`/`memfn/src/` change, no
emitted byte); no timing.
