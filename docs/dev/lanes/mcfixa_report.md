# mcfixa — review 2026-11-15 r5 (memfn-mfindcomb) groups (A)-(C), as ruled

Lane mcfixa (opus), branch `lane/memfn-mcfixa` (cut from 9cb091199), 2026-11-15. This lane changed only the
harness, cards and docs. Nothing under memfn/src/, src/, cli/ or lib/ changed, so no emitted byte moved and
there is no abi event. Review draft: `$PCREC_TMPDIR/scratch/crit-memfn-mfindcomb/review.md`.

## Summary

- **The timed shape is now inline, as pcrec emits it (FIDELITY-1).** Each site TU is compiled twice from one
  text. The timed object holds only `_time`. The gate object holds `_gate`: it is built from the same file with
  `-DSLOT_GATE_TU` and linked after every arm. A new check, `link: TIMED-SHAPE`, refuses any `_time` that calls a
  function its own object defines (that would mean the finder site was emitted out of line). I showed the check
  RED on the old shape first: `a2_time calls mf_fn__w16`. It is now GREEN on dry JMB and dry JMH, where every
  timed object holds exactly one function.
- **The estimator now enforces the inputs it was trusting (group B).**
  - Every job that ran has its manifest checked, and `cell_text` and `placement` are pinned (FIDELITY-2).
  - A duplicate cell is refused, and so is a duplicate cell_text line (FIDELITY-5, DRAFTSETS-2).
  - The ISA level of a draft set now comes from the kit's own `--target-facts` (DRAFTSETS-3). The mixed-level
    guard reads the needs that link.py recorded (DRAFTSETS-1).
  - Base cells and ctl cells are filed with their rows' sets (FIDELITY-3).
  - The unit row is repeated in every ver-6 set, so every draft set loads with the tree's loader (contract-2).
    The self-test now loads each draft with `build/pcrec --measures=`.
- **D197 has a declared decision rule, one verdict per ISA level, per the kit manager's R1 (FIDELITY-4).** The
  rule is `slot/d197_rule.tsv`, read by `slot/d197_rule.py`. It was written before any number existed.
  - Main's YES came with three changes (R3), all applied:
    - A loss resting on one or two of a level's 36 comparisons must reproduce in ONE confirming re-run. Three or
      more losses count at once.
    - A second INCONCLUSIVE is recorded as NOT-WIN, never LOSS.
    - A header line says why the scan cost never decides. The scan result is printed per level with its libc
      ratio.
  - The confirming re-run is plan.py's new job `JMHC`, built from `SLOT_CONFIRM_CELLS`, with record.py window
    `mfconfirm`. Staged job 610 runs it.
  - The drill is 22/22.
  - Frank receives the rule as information and may amend it before 01:00.
- **record.py now records which memchr variant each process actually bound** (`memchr=evex|avx2|sse2`).
  - **FINDING:** on this box's glibc 2.43, the prepared tunable `glibc.cpu.hwcaps=-AVX512F` STILL binds the EVEX
    memchr (ymm16). Only `-AVX512VL` (or `-AVX512BW`) selects the AVX2 variant.
  - The re-staged jobs use `-AVX512VL`.
  - The rule refuses an AVX2 record that bound anything else.
- **The emitted size is now reported next to the timing, but never decides (EMITTED-1).** cell_text gained a
  9th column, `text_bytes`, and `est.py rows` prints one `size` line per kit row.
- **Docs (DRAFTSETS-4, contract-3):** span_cards.md §2.7 now states the one-level-per-set rule and the
  kit-grid@6 owed list, and the card comment points at both.
- **Timing jobs 600-609 are re-staged but NOT queued.** They have a declared time gate plus the evening hold.

## Fixes by id

| id | state | where |
|---|---|---|
| FIDELITY-1 (the timed `_time` was not pcrec's inline shape) | FIXED: the gate is a separate object built from the same text; TIMED-SHAPE refuses an out-of-line site; plant (i1) S3188 | slot/link.py |
| FIDELITY-2 (manifests were checked for verify jobs only) | FIXED: every job that ran is checked, with `cell_text` and `placement` pinned; MANIFEST ABSENT / MISMATCH; plants (i2) S3189, (i3) S3190 | slot/est.py |
| FIDELITY-3 (base and ctl cells were filed by ver only) | FIXED: base cells go with the sets of the rows that name them (guarded by the base's recorded needs); ctl cells go with the sets holding a row of their job; plants (i7) S3194, (i8) S3195 | slot/est.py |
| FIDELITY-4 (no decision rule had been declared before the run) | RULE WRITTEN, per level (R1), with main's yes plus three changes (R3); plants (i9) S3196, (i10) S3197 | slot/d197_rule.tsv, .py; plan.py JMHC, record.py `mfconfirm` |
| FIDELITY-5 (a duplicate cell was silently kept) | FIXED: CELL TWICE refusal; plant (i4) S3191. Pinning the cells file's sha in the record is left as a PLAN row for main (it would be a new record field) | slot/est.py |
| contract-2 (the ver-6 sets did not load) | FIXED: the unit row is repeated in every set and exempt from the guard; the self-test loads every draft; plant (i6) S3193 | slot/est.py |
| DRAFTSETS-1 (the guard used labels, not recorded needs) | FIXED: the guard runs over the recorded `target_isa` plus the target's features above the floor, against the class's features; e4 re-aimed | slot/est.py |
| DRAFTSETS-2 (a duplicate cell_text line was silently kept) | FIXED: CELL-TEXT TWICE refusal; plant (i5) S3192 | slot/est.py |
| DRAFTSETS-3 (a hand-written level table) | FIXED: `Levels` derives the level from `--target-facts`, and an unknown target is refused; TARGET_SET/TARGET_LEVEL deleted; f8a/f8b re-aimed | slot/est.py |
| DRAFTSETS-4 (one level per set was not written down) | FIXED (docs): §2.7 states the one-level rule; dead `base_tg` removed from the self-test | span_cards.md |
| EMITTED-1 (size was not reported) | FIXED: `text_bytes` in cell_text, a `size` line per row; reported, never decides | slot/link.py, est.py |
| EMITTED-2 (swar vs libc is a width comparison) | SUPERSEDED by R1: under R1 the swar row DECIDES for the default level, and the `axes` column names width and every other differing axis | slot/d197_rule.tsv |
| contract-3 (the kit-grid@6 owed list) | FIXED (docs): §2.7 owed list (mfind-w64; single-piece cells only on a D197 WIN; the D149 entry cut-over default; row floors); card comment; per R2 both now say the ver-6 rows are an UNPICKED MEASURING INSTRUMENT (D197), never a pick | span_cards.md, memfn/data/cards/kit-grid.tsv |

## D197 decision rule

The file `docs/design/memfn/span_cards/slot/d197_rule.tsv` IS the rule. Its tables are first match.

**Header facts:**
- The timed shape is inline, as pcrec emits it (FIDELITY-1).
- There is one verdict per ISA level, never a global one.

**Statistic:**
- For each find_hit@6 row and each launch l, `x_l` is the per-hit cost in ppm of W.
- `gain_l = x_l(libc) - x_l(form)`, taken over the same job, launch and cell. Positive means the form is cheaper.
- `gain = med(gain_l)`.
- `floor = aa(libc) + aa(form)`.
- `trimmed` = the 7 values of gain_l, minus the one farthest from their median.
- The scan cost (find_byte@6) is reported beside the verdict and never decides. Neither does the size.

**Deciding cells:** find_hit, ver 6, landing periodic, split one, gaps 2,4,8,16,32,64,256,1024,65536, rejects
0 and 100. That is 18 cells, each compared with `fn-memchr`.

**Levels.** I confirmed each form with `build/pcrec-harness --harness=mfind`:

| level | build | form | differing axes (in full in the tsv) |
|---|---|---|---|
| generic | default (no -fmemfn-simd) | mfind-swar | width (8-byte SWAR vs 32-byte ifunc vector); inline vs a libc call; MASK vs RESTART; check inside the loop vs a memcmp after each call |
| x86-64 | -fmemfn-simd=x86-64 | mfind-w16 | width 16 vs 32; inline vs a call; MASK vs RESTART; check placement |
| x86-64-v3 | -fmemfn-simd=x86-64-v3 | mfind-w32 | encoding only vs shipped EVEX, and equal under the AVX2 tunable; inline vs a call; MASK vs RESTART; check placement |

**Why the scan cost never decides (R3 (3)).**
- Row 1 picks what the site does AT EACH CANDIDATE: the finder continues its mask past a rejected hit, while libc
  restarts a call at hit+1 and checks after it. Only the per-hit slope prices that difference.
- The miss-only per-byte rate measures search WIDTH, and width is set by the level, not by row 1.
- The scan result is still printed per level (`d197_scan`: form, libc, and the form/libc ratio, for both libc
  rows) so that a large scan deficit stays visible.

**Losses count over the level's 36 comparisons** (18 cells x 2 libc rows; R3 (1)).
- Three or more losses count at once.
- A loss on one or two comparisons triggers CONFIRM. Job 610 re-runs exactly those cells, with both libc arms
  and a new run id. The rule then runs again with `--confirm`.
- A loss that does not reproduce is scored as a tie.

**Cell table:**

| cell | when |
|---|---|
| unresolved | either row is unpriced |
| win | gain > floor, and every trimmed launch is > 0 |
| tie | a loss that did not reproduce in the confirming record |
| loss | gain < -floor |
| tie | always |

**Arm table.** There is one arm per libc row: shipped = any variant, avx2 = must have bound memchr=avx2.

| arm | when |
|---|---|
| no-verdict | the run was refused |
| no-verdict | the bound memchr variant is not this arm's |
| WIN | no loss, and more than half of the 18 cells are wins |
| not-win | always |

**Verdict table (per level):**

| verdict | when | what it triggers under D197 |
|---|---|---|
| INCONCLUSIVE | the shipped arm has no verdict | the one re-run |
| LOSS | 3 or more loss cells | settles span_pick row 1 against the finder at this level |
| CONFIRM | 1-2 loss cells not yet confirmed | the confirming re-run (610), then the rule again with `--confirm` |
| LOSS | the 1-2 loss cells reproduced | the same as LOSS above |
| WIN | both arms are WIN | the ruled split shape for this level is built under its own owner go, then re-measured |
| NOT-WIN | this is the re-run (`--second`) | no stage-2 build; the ledger never records a LOSS for this |
| INCONCLUSIVE | always | ONE re-run: the mfcard window again, in a later window Frank clears, with the same plan, a new run id, scored with `--second` |

**Provenance.** The AVX2 libc row runs under `glibc.cpu.hwcaps=-AVX512VL`. On glibc 2.43, `-AVX512F` alone still
binds the EVEX memchr. The rule refuses an AVX2 record that bound any other variant.

Drill (`d197_rule.py drill SCRATCH`): `== d197 DRILL ok: 22 cases, 0 wrong`. There are 21 constructed cases,
including:
- one run giving LOSS, INCONCLUSIVE and WIN at three different levels;
- a 1-cell loss with no confirming run yet, giving CONFIRM;
- a 1-cell loss that reproduces, giving LOSS;
- a 1-cell loss that does not reproduce, giving WIN;
- a 3-cell loss, giving LOSS at once;
- one loss against each libc row, giving CONFIRM on both cells;
- a second tie, giving NOT-WIN.

The 22nd case runs end to end on est's synthetic window: 108 of 108 cells read, with a scan ratio printed.

## Timing jobs

The jobs are in `$PCREC_TMPDIR/scratch/memfn/mcfixa/jobs/`: `600-kit-mfcard-prep` .. `609-kit-mfcard-time`,
`common.sh` and `window.vars.example`. They are staged and NOT queued. The keys are the same `kit-mfcard-*`.
Changes from slotx's set:

- `TREE` is set at the top of common.sh. Its default is `worktrees/mfind`, which is the final tree once main
  merges this branch there. `MFCARD_TREE` overrides it, for a dry run.
- Time gate:
  - Every dry run declares `boxqueue: not-before 2026-11-16T01:00`.
  - Every `--ready` checks it again, and also the evening hold (20:00-01:00 local), returning 75 while either
    applies.
  - boxqueue does not know about the evening hold, so the job enforces it.
- `LIBC_ENV=GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX512VL` (see the FINDING above).
- 609 now ends with `d197_rule.py rule RUNDIR RUNDIR.avx2libc`, tee'd to `RUNDIR/d197_verdict.txt`. A
  CONFIRM verdict prints `d197_confirm_cells GAP.REJECT..`.
- **New `610-kit-mfcard-confirm` (R3 (1)), staged and queued ONLY on a CONFIRM.**
  - It reads `CONFIRM_CELLS` from window.vars, which becomes `SLOT_CONFIRM_CELLS` for plan.py. Those cells move
    from JMH to JMHC, which has its own bases and control.
  - It runs J2 and JMHC in `RUNDIR.confirm` and `.confirm.avx2libc`, under run id `RUN_ID.confirm`, both libc
    arms. Each record is finalized as window `mfconfirm`. It then runs the rule with `--confirm`.
  - Box time, from the jobs' own est budgets (not measured): about 25 minutes for one or two cells. Per arm, that
    is J2 at 240 s plus JMHC's 4 groups at about 105 s each; add two dry runs.
  - Its dry run was checked with `CONFIRM_CELLS="65536.0 2.100"`: rc 0, JMHC planned as 4 groups (JMH drops to
    21 from 23), `--ready` 75. An unknown cell is refused (`plan: SLOT_CONFIRM_CELLS names 3.0, no find_hit@6
    cell`).
- RUNDIR is now `scratch/memfn/mcfixa/run/<RUN_ID>`.
- To run them, main writes `window.vars` (RUN_ID and FROZEN) once Frank clears the window, then queues them.

The ten window jobs' `--dry-run` calls were checked against this worktree, with FROZEN set to its HEAD: rc 0 each, and each
declares the not-before. Every `--ready` returned 75 (`waits: not-before 2026-11-16T01:00`). The temporary
window.vars was removed afterwards.

## Validation

- **est self-test:** `== est SELFTEST ok: 64 cases, 0 wrong` (it was 57 before this lane's cases). It also ran
  green as the sabotage control.
- **D197 drill:** `== d197 DRILL ok: 22 cases, 0 wrong`.
- **Dry JMB:** rc 0, with the TIMED-SHAPE check and the `text_bytes` column. It is also green as the sabotage
  control.
- **Dry JMH:** rc 0. It covers 172 cell TUs (x86-64-v3 compiled with avx,avx2,bmi,bmi2). All 7 launches pass the gate and the round check, and cell_text carries `text_bytes` (for example base.mfind-swar 329). Run against the worktree with no `SLOT_CONFIRM_CELLS` set, it plans 23 groups, the same as before.
- **Sabotage:** every new row was DETECTED, over three runs:
  - sab1 scored i2-i8, plus the re-aimed rows e3, e4, v1, f8a and f8b.
  - sab2 scored i1, with its plant corrected (`TIMED-SHAPE kit.find_byte.mfind-w16: a2_time calls mf_fn__w16`).
  - sab3 scored i9 and i10 against the R3 reader, after the plan.py change.
  - Every control was green in every run: J2, est, JMB and d197.
- **est self-test after the plan.py JMHC change:** 64 ok, 0 wrong.
- **`make strict`:** rc 0 ("whole tree compiles clean with -Werror -Wshadow; the kit's target table check
  passes").
- **Not run, per the brief:** make test, mech, axes, the full sabotage table and box jobs.
- **Draft loading:** a dry run has no record, so there are no real drafts to load. Loading is covered by the
  self-test's `mf_loads` case, which loads every synthetic draft with `build/pcrec --measures=`.

## STATE AT HANDOFF

- Rulings applied: R1 (the per-level D197 table), R2 (the UNPICKED MEASURING INSTRUMENT wording) and R3 (main's
  three changes and the provenance). R3 is the last entry in mcfixa_rulings.md.
- Frank receives the rule as information and may amend it before 01:00.
- PENDING main/Frank: a plan row for pinning the cells file's sha in the record (FIDELITY-5 remainder).
- PENDING main: merging lane/memfn-mcfixa into the mfind tree, then writing window.vars and queuing jobs 600-609
  once the window is cleared.
- OWED: none
