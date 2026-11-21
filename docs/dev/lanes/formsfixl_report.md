# formsfixl report: review r44's fixes on the span forms' cards (r45_reply rev 13)

Lane formsfixl (kit lane, opus, 2026-11-18), branch `lane/memfn-formsfixl` cut from
`lane/memfn-forms` @ 27b18e75c. Charter: review r44's RULINGS section
(`docs/dev/reviews/2026-11-18-r44-memfn-forms7.md`, committed here with its critic texts in the
directory of the same name; index line in `docs/dev/reviews/CLAUDE.md`). Items A-L done; M is the
manager's. `docs/dev/lanes/formsfixk_rulings.md` (R2's record, FREEZE NOTE 1) is committed here
unchanged (`git add -f`: `*_rulings.md` is gitignored). Files changed: `memfn/tests/span_forms/cards.py`,
`docs/design/memfn/r45_reply.md` (rev 13, "Changes in rev 13" by r44 id), the review files, this
report, the lanes history index line. No file under `memfn/src/`, `src/`, `cli/`, `lib/` moved.

## STATE AT HANDOFF

DONE. Committed tip: the branch head (`git -C worktrees/formsfixl log -1`). Rulings file `docs/dev/lanes/formsfixl_rulings.md`: empty at every read (start, each
commit, before the report): no entry to apply. OWED: the box-queue job `kit-formsfixl-dry` (queue key; job file `420-kit-formsfixl-dry`, queued at 04:48 and running at hand-back)
(`cards.py dry` over all 1374 cells at WIDTH_FLAG=none on this branch; script
`/var/tmp/pcrec-pcrec/scratch/memfn/formsfixl/jobs/420-kit-formsfixl-dry`, output
`/var/tmp/pcrec-pcrec/scratch/memfn/formsfixl/dryjob/`, completion line `^formsfixl-dry: DONE rc=0$`;
its verdict to read: `# dry: cells 1374, built and gated 1374, failures 0;`, POOL REFUSED lines 0
under r44 C's two new clauses; the step 2b WOULD REFUSE line is the known VACUOUS case at width
none). It is the one check that exercises C's new refusal halves on REAL pools: a real pool whose
same-relative-layout pair shares its 32-B phases would now refuse (none expected: the prelude moves
each pair 16 B mod 32).

## FIXES BY ID

Fail-before lines come from `scratch/memfn/formsfixl/failbefore.py` (the PRE-FIX module, 27b18e75c,
on the new rows' inputs; log `failbefore.log`), `failbefore_j.py` (K6's gate with rev 12's fixed wins;
`failbefore_j.log`), or the row's own control switch in the selftest. Pass-after lines are from
`selftest --rev12` / `--rev11` (`st12_a.log`, `st11_a.log`, then the full selftest).

- **A** (variant x regime interaction; FIX-NOW small form). `text_effects` fills per-text fit stats;
  `text_interaction` runs a lack-of-fit test of the per-text fit against the (row, variant) cell
  means, launch noise from launches that repeat a variant inside one row (pooled per regime over the
  night); `rule` prints the share sI2 / (sI2 + sL2) and VOIDS the C1-C2 cells of a text above both
  lines (`INTER_SHARE` 0.5, `INTER_ALPHA` 0.01 family-wise; both labelled UNMEASURED DEFAULT). No
  per-(text, regime) fit (PLAN, trigger as ruled). New drill model "regime" (`synth_layout_effect`,
  keyed per (text, regime, variant): unlike the fit).
  - before (control `INTERACTION_VOID` off = rev 12's rule): `ok   (r44 A) control: variant x regime heads tau 3 %, no void P(h* != 64) = 0.373 over 300 nights (the drill sees the defect: accept > 0.10)`
  - after: `ok   (r44 A) layout: variant x regime, heads only, tau 2 % P(h* != 64) = 0.000 over 300 nights (accept <= 0.05); nights with an interaction void 300; nights with a first void 0.920 (RECORD ...)`; tau 3 %: `P(h* != 64) = 0.000 ... nights with an interaction void 300; nights with a first void 0.937`; every text tau 2 % (RECORD) 0.000.
  - cost (false interaction voids on models WITHOUT interaction, nights of 300): phase 5 / 3 / 0 at
    tau 1 / 2 / 3 %, heads 2 / 0 / 1, rho 0.8 2 / 3 / 6, rho 0.95 5 / 3 / 3. The nominal family rate
    is 1 %; the read is up to 1.7-2 % (the lack-of-fit statistic is approximate: 4-pass backfit,
    pooled pure error). A void keeps 64 (speed only). See FOR THE MANAGER.
- **B** (per-(cell, head) floor). `f_hI(c, h)` for H(h) vs I (wins, the confirm, E's tolerance, R2
  dial lines, R4), `f_pair(c, g, h)` for dominance; `r1` takes `fh`/`fp` (defaults = the old cell
  floor, so every no-layout drill is unchanged); the agreement gate keeps the cell max. New drill
  model "loser" (H(1) 20 % slower, layout tau 4 % on its texts only), GATED.
  - before (control `PER_HEAD_FLOOR` off = rev 12's one cell max): `ok   (r44 B) control: the same nights, one floor a cell h* = 8 in 159 of 300 nights (the drill sees the defect: accept < 270)`
  - after: `ok   (r44 B) power: one 5 % winner beside a noisy loser h* = 8 in 281 of 300 nights (rev 11's accept >= 270; ...)`
- **C** (32-B guard; distinct layouts). `pool_refusal` adds: two variants of one relative layout
  sharing their per-loop 32-B vector; fewer than POOL_SIZE distinct built layouts (a duplicate also
  shares its 32-B phases, so that clause never fires alone; its plant asserts both).
  - before: `C before: old pool_refusal(32-B-sharing pair) = None; (duplicate) = None`; the
    construction row on rev 11's order: `C 32-B construction row, PHASE_ORDER (0, 1, 2, 3): pairs not 16 B apart mod 32 = 4000 (accept 0)`
  - after: `ok   (r41 L9, r44 C) the pool refusal, each half clauses fired: moving (); one 64-B phase ('one 64-B phase each',); one relative layout ('shares one relative layout',); a 32-B-sharing pair ('share the 32-B phases',); a duplicate ('share the 32-B phases', 'distinct built layouts'); ...` and `ok   (r44 C) each alignment pair's preludes differ by 16 B mod 32 pairs (v, v + 2) over 2000 texts NOT 16 B apart mod 32: 0 (accept 0; PHASE_ORDER (0, 2, 1, 3))`
- **D** (text + salt; no fresh pool). Text: cards.py's confirm comment (was :1864) and r45_reply §3
  "Confirm by re-run" state that the confirm re-times the same 4-exe pools, is not an exe-level
  control, and the exe level rests on the per-text term. Salt and pairing: each confirm ROUND its own
  file (`confirm_name`: `results_confirm.tsv`, `results_confirm_r<K>.tsv`); `confirmed` reads the
  I row of the head's own round.
  - before: `D before: one confirm file, round 2's I replaces round 1's: h* 64 (accept 8)`; `D before: rounds 1 / 2 draws (one file name) [3, 1, 2, 1, 0] / [3, 1, 2, 1, 0]`
  - after: `ok   (r44 D) the confirm's rounds: own draws, own I row round 1 / 2 draws of one cell [3, 1, 2, 1, 0] / [0, 2, 1, 1, 1]; H(8)'s round-1 confirm against round 1's I with a 15 % faster I in round 2: h* 8 (accept 8; 14 cells owed)`
- **E** (fresh run id). `start_timing` (called by `run`): keeps the id unless `run_id.timed` names
  it (the id already timed a night), then mints a fresh one; a G2 record keyed to another id refuses
  (exit 2). Job 701's order (record, then the first `run`) is kept.
  - before: `E before: second `run` on the re-used RUNDIR refused: False; run id kept: True`
  - after: `ok   (r44 E) a re-used RUNDIR: a fresh run id, the old G2 record refused 701's pre-run record kept: True; the re-used RUNDIR's second `run` refused the old record: True; a fresh id: True; draws [2, 2, 1, 0, 2] / [2, 2, 3, 1, 0]`
- **F** (doc). cards.py's pool comment names the FIXED AXES; `rule` prints them (`rule: layout pools
  hold FIXED (r44 F): ...`); r45_reply's R2 A row and §3 "The layout pools" name them. Text only.
- **G** (doc). cards.py's (2) comment (was :142: entries NOT 16-B aligned in odd variants), the
  PHASE_ORDER comment (was :154: preludes span four classes; each relative layout two 64-B classes
  16 B apart) and r45_reply's L9 row (was :81). Text only.
- **H** (doc + print). R2 A's scope (odd pair = same stream, other padding, not what -O2 ships) in
  r45_reply; `rule` prints per text the even-pair vs odd-pair contrast and each win re-read on even
  draws only (records, never an input). Print rows: a line in every layout night's `rule` output;
  no gate (ruled as a print).
- **I** (CC in the key). `cc_ident()` (CC + `$CC --version`), `variant_key`.
  - before: the old name formula `_h(key, pre, flags)` has no compiler term (`I before: old vk = ... 3c4072e8cb1468db (one name for every compiler)`)
  - after: `ok   (r44 I) the exe cache key carries the compiler   two compilers' keys 2cd171c3ebbdc641 / f3e3b5a1940ef725`
- **J** (K6 placed). `k6_place`: each night's rows without the win (same RNG stream) read with and
  without G2 = {16}; the first hit-dense H(8) cell gets the factor that puts its ratio at the band's
  MIDPOINT (UNMEASURED DEFAULT); 16 seeds; gate: >= 12 placed, main stalled 0, control >= 80 % of
  placed. Comments (cards.py K6, r45_reply rev 12 note) corrected.
  - before (`K6_FIXED_WIN`, rev 12's fixed wins under the same rate gate): `FAIL (r39 K6, r44 J) ... [K6_FIXED_WIN 0.953] ... control (no G2 record, rev 10's rerun): stalled 6 of 16 (accept >= 80 %)`; `[K6_FIXED_WIN 0.955] ... stalled 0 of 16`
  - after: `ok   (r39 K6, r44 J) ... 16 of 16 nights placed in their own band (bands 0.0444-0.0448, ...); through the commands: stalled 0, rerun timed the rule's owed list on every pass: True, ...; control ...: stalled 16 of 16 (accept >= 80 %)`
- **K** (power line). Sigma read corrected by `SIGMA_READ_BIAS` 0.88 (MEASURED, r44 V11); the two
  bracketing RECORD rows named, power log-interpolated; above the top row an upper bound.
  - before: `K before: measured layout sigma 0.0132 -> the RECORD row at tau 1 %: one 5 % winner 170, ...`
  - after: `ok   (r44 K) the power line brackets the night's sigma at a read of 0.0132: measured layout sigma 0.0132 (read ~12 % low, r44 K: corrected 0.0150) between the RECORD rows tau 1 % (...) and tau 2 % (...), log-interpolated: ...`
- **L** (pins checked). `check(got == POWER_RECORD[tau])` at tau 1 and 2 %. It fired on its first
  run, because B moved the power:
  - before (first run after B): `FAIL (R2 D, r44 L) POWER_RECORD pin, tau 1 % the drill reads (204, 296, 179), POWER_RECORD pins (170, 299, 176)`; tau 2 %: `reads (25, 271, 18), POWER_RECORD pins (7, 260, 5)`
  - re-pinned (b0e620826); after: `ok   (R2 D, r44 L) POWER_RECORD pin, tau 1 % the drill reads (204, 296, 179), POWER_RECORD pins (204, 296, 179)`; tau 2 %: `reads (25, 271, 18), POWER_RECORD pins (25, 271, 18)` (full selftest)

## CHECKS RUN

The previous lanes' set (formsfixk report, "Validation"), all under `nice` + `timeout`:

- **selftest (full)** on b0e620826 (= HEAD's cards.py, cmp-identical copy
  `scratch/memfn/formsfixl/cards_full_b0e620826.py`, PCREC_TREE = this worktree), log
  `scratch/memfn/formsfixl/selftest_full.log`: `selftest: 217 checks, 0 failed`, rc 0 (03:42-04:47; formsfixk's tip read 205). Class drill worst arm row `(r38) noise at arm: H(8), every cell, tau 2 % P(h* != 64) = 0.017` (accept <= 0.05); F2 0.000 / 0.000; every r44 row and control as quoted in FIXES BY ID.
- **selftest --rev12** (`st12_a.log`, before the re-pin): `selftest --rev12: 28 checks, 2 failed`
  (the two L pins, above; re-pinned). **--rev11** (`st11_a.log`): `selftest --rev11: 5 checks, 0 failed`.
- **make strict** (-j4): rc 0, "strict: whole tree compiles clean with -Werror -Wshadow; the kit's
  target table check passes" (`strict.log`).
- **doc checks** `make test-claudemd-size test-spec-history test-doc-lint test-plan-lint`: rc 0 (11 /
  15 / 2 checks passed, 0 failed; `docchk.log`). `grep -rnE 'plan\.md:[0-9]'` over the review files:
  nothing; no spec cited by line.
- **0 movers**: `git diff --name-only 27b18e75c..HEAD -- memfn/src src cli lib` prints nothing (only
  cards.py and doc files changed); no measured kit code moved, so no abi event.
- **dry** over all cells: OWED, box-queue job `kit-formsfixl-dry` (STATE AT HANDOFF).
- **Deliver file**: two format edits so lanecheck can read it: `owed:` names the queue key `kit-formsfixl-dry` (the brief said to replace `none`), and the `files:` paths are now `;`-separated (lanecheck splits on `;`; the space-separated list read as one missing path). The paths themselves are unchanged.

## FOR THE MANAGER

- **A's false-void cost.** On models with no interaction the new void fires on up to 6 of 300
  nights (2 %; nominal 1 %). Each such night keeps 64 (speed only). If that cost matters, tighten
  `INTER_ALPHA` (detection margin is large: flagged texts read ratios 4-22 against lines 1.5-4).
  The share is a mean-square index, not a variance component (stated in the code).
- **B's cost on a RECORD row.** Per-head floors are lower than rev 12's cell max wherever heads
  differ, so the heads-only tau 3 % row (RECORD since R2 B) reads 0.067 (rev 12: 0.000) and tau 2 %
  0.010 (gated, accept 0.05). The power RECORD rose: 5 % winner at tau 1 % 170 -> 204, tau 2 % 7 ->
  25. B was ruled for power; the heads-only tau 3 % rise is the trade.
- **A's first-void rate** under the interaction model stays at 0.92-0.94 (the variant-aware bimodal
  test reads the regime-specific effect as a split): RECORD; the per-(text, regime) fit (PLAN) is
  what would remove it.
- **C on real pools** is unproven until 420 reads: a real pool refusing under the new clauses would
  make `dry` red. If it does, the refusal text names the pair.
- **E's marker** is a new RUNDIR file `run_id.timed`; job 701's `g2_record` before `run` still works
  (the selftest row runs that order).
- **D**: the confirm's later rounds now land in `results_confirm_r<K>.tsv`; nothing in jobs 700-704
  greps the confirm file's name.
- PLANs from the rulings to file (the manager's): per-(text, regime) fit (A), fresh confirm pool (D),
  subject-offset draw (F), pool change for the odd pair (H), shared layout-draw module (M).
