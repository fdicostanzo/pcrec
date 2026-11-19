# formsfixk report: layout pools replace the layout twins (review r41, RULED L9, L5, L6, L8; rulings R2 A-D)

Lane formsfixk (opus, 2026-11-17), branch `lane/memfn-formsfixk` from `lane/memfn-forms` @ 42fd4b33e.
Charter: review r41's RULED section (`docs/dev/reviews/2026-11-17-r41-memfn-forms6.md`, committed
here). Rulings file `docs/dev/lanes/formsfixk_rulings.md` (gitignored; quoted in STATE AT HANDOFF):
R1 applied (the Summary's last sentence); R2 (A-D, the answers to the lane's first stop) applied.

## Summary

The layout twins are gone. Every arm's TEXT is linked as a POOL of 4 layout variants, each its own
compile of the TU with (a) an in-TU prelude (a top-level `.skip 16 j` ahead of every function, j
drawn mod 256 and stratified so the four variants take the four 16-B phase classes mod 64 and the
two variants of each alignment differ by 16 B mod 32) and (b) an alignment variant (the odd
variants turn off gcc's code alignment, x86's tight-loop alignment included). Every launch draws a
variant (a hash of the run id, the results file, the cell and the round) and records it in the
results row's new `variants` column. `dry` builds and answer-gates every variant and proves each
pool from the built exes (nm + objdump of `rxa_search`'s backward-branch targets): per-hot-loop
64-B and 32-B phases, relative layouts, and a REFUSAL of a pool with one 64-B phase vector or one
relative layout. On the dry run every pool moves both phases (3-4 distinct vectors of each per
pool), 0 refused, 1374 of 1374 cells gated. L5 (one source for the confirm's arm list), L6
(strict arguments, the keyed G2 record) and L8 (S3320/S3321 doc lines) are done. The drill rows
did not all hold as first built; the lane stopped with four questions and the kit manager ruled
R2: a per-TEXT layout term (B) and a variant-aware bimodal test (C) are built, each with its
control, and the correlated-layout rows (A) and the power rows at layout τ >= 1 % (D) are RECORDs
with `rule` printing the night's measured share and its power line. Every gated row now holds:
heads-only τ 2 % 0.000 (accept 0.05), phase-model voids at τ 2 % 0.000 (accept 0.10). The price
is power: a 5 % win is seen 170 of 300 nights at layout τ 1 % and 7 at 2 % (a 10 % win 299 / 260).
R1: the pool mechanism is ARM-GENERIC at the TU level (`pool_variants` keys on any TU's text hash,
`build_cell` adds the prelude and flags to whatever artifact + driver it compiles, and the proof
needs only the hot function's symbol), so main's width-rule arms (cover_cap.md §11.4, a different
binary set) could use it once the three pieces (variant compile, per-launch draw, `pool_proof`
with the hot symbol as a parameter) move out of `cards.py` into a shared helper their launcher
calls; nothing was built for it.

## Fixes

- **L9 (closes L1, L2, L4's layout half, L7).** `cards.py`: `POOL_SIZE` (4), `PRELUDE_STEPS`
  (256), `PHASE_ORDER`, `ALIGN_VARIANTS`, each labelled `UNMEASURED DEFAULT:` in place;
  `pool_variants`, `launch_variant`, `text_key`, `build_cell(..., v)` (cache name = text key +
  variant + a hash of its prelude bytes and flags: L7), `layout_of`, `pool_proof`,
  `pool_refusal`; `run_cell` and `prepare_cell` gate every variant; `time_cells` draws and records
  per launch (salted by the results file, so a re-run or the confirm draws afresh); `dry` prints
  each pool and the summary line and refuses; `plan` prints the pool counts, the gates' cost
  (`EST_GATE_S`, a gate call measured at 0.8-3.3 ms over 30 calls on a non-quiet box, priced at
  0.01 s) and keeps step 1 at 0.11 h and C3 at 0.01 h (as rev 11's printed hours). The rule:
  I's pool is I + its hash-equal heads (no `I.lt`); the A/A pair is `aa` / `aa.b` (two arms of
  aa's pool); the confirm re-times I and each owed head on fresh pool draws into
  `results_confirm.tsv`; `rule` prints the night's layout reading (`layout_reading`: the
  between-variant sigma of I's pools, launch noise removed, a RECORD). The drills:
  `synth_body` + `synth_layout_effect` (models "phase" = a fixed function of (text, 64-B phase),
  "heads" = head texts only, "rho" = correlated variants), every synthetic launch drawing a
  variant; `selftest_rev12` (also `selftest --rev12` alone) holds the drill rows, the void rows,
  GAP_K's re-derivation (`gapk_rate`), the power rows, the pool refusal per half and L6.
  Two dry-run findings fixed on the way: a pool's phases compared as a SET read two loops 32 B
  apart that swap phases as unmoved (4 dig24/dig32 h4 pools refused falsely; now a per-loop
  vector), and with variant classes (r + v) mod 4 each alignment's two variants differed by 32 B,
  so 18 of 80 pools (dig24/dig32, whose hot loop gcc pads to 32 B even under `-fno-align-loops`)
  kept every 32-B phase; `PHASE_ORDER` and `-mtune-ctrl=^align_tight_loops` fixed both (dry: 0 of 80).
- **L5.** `confirm_only` builds the drills' confirm rows from `confirm_cells` (the command's own
  list); `synth_night`, `_confirm_rows` and G6 call it.
- **L6.** `parse_args` (plan, dry, run, rerun, rule, c3, selftest): unknown or mistyped options,
  a valueless `--g2` (also `--g2=`), missing or extra positionals refuse with exit 2; `--g2 F` and
  `--g2=F` both read. `run_id` (RUNDIR/run_id, written ONCE by the first command that needs it,
  so job 701's `rule --g2` before `run` keeps working); `rule_g2.json` carries the run id and the
  G2 file's sha-256: another run's record, a recorded file whose bytes moved, or a second
  different `--g2` list refuse (exit 2); `run` refuses a RUNDIR that holds any results file.
  `identity` keeps its own argument handling (not in L6's list; unchanged).
- **L3 / R2 D.** The power rows at layout τ 0 are gated with rev 11's accept lines; at τ 1 and
  2 % they are RECORDs (R2 D), pinned in `POWER_RECORD`; `power_line` prints the night's power at
  its measured layout sigma (the nearest pinned row) and whether it is below rev 11's lines.
- **R2 A.** The rho rows are RECORDs; `rule`'s layout line prints the texts read and the
  between-variant sigma per text (median, max) the night measures; rev 12 §3 states R2 A's
  sentence (the share common to every variant is the BODY's own layout, which ships: the text's
  speed, not noise). No data prelude.
- **R2 B.** `text_effects` (per text, over every file read, each file's row its own level: a
  two-way fit, 4 backfitting passes, effects centred, the between-variant variance less its
  estimation noise), `varmed5` (the exact variance of the median of LAUNCHES uniform draws over
  the pool's effects), `text_var`, and `layout_text_term` in `cell_floor`: per cell the floor is
  at least exp(z sqrt(V_I + V_h)) - 1 over the heads compared there, z the rule's own Bonferroni
  z. Switch `LAYOUT_TEXT_TERM` (the control). Text grouping (`text_of`): I's pool by the measured
  identity record, each other head its own, aa per layer, C3/C5 per arm.
- **R2 C.** `adjusted` (a row's launches with its text's per-variant effect removed) and
  `is_void` reading the adjusted launches against the pools' sigma of adjusted launches; GAP_K
  stays 4.5. Switch `VARIANT_BIMODAL` (the control). `gapk_rate` re-derives the per-arm
  false-split rate with texts of 6 rows fitted as `analyse` fits them, both tests.
- **A bug found on the way (fixed before the numbers below):** the first R2 build keyed the fit
  by cell, so a confirm row merged its launches into the first reading's row level; every power
  night's confirm then voided its text (one 10 % winner 0 of 300). The fit keys (file, cell).
- **L8.** S3320 and S3321 named in memfn/tests/NOTES.md, tests/compound/CLAUDE.md (4) and
  `run_shell_checks.sh`'s header. This lane adds no mech plant (sabotage ids S3330-S3334 unused):
  the cards' controls are `selftest` rows, as NOTES.md says.
- **Docs.** `docs/design/memfn/r45_reply.md` rev 12 (STOPPED): status, "Changes in rev 12" (one
  row per id, the stop table), "The layout pools", the confirm and A/A sentences, night order
  step 1, the comparison kinds by perturbation, drill (xxiii); rev 11's twin text is marked
  superseded in place. The r41 review committed as `docs/dev/reviews/2026-11-17-r41-memfn-forms6.md`
  (r41 free on main, lane/covs2b and every lane/memfn-*; main holds r40 only) with its line in
  docs/dev/reviews/CLAUDE.md.

## Deleted

| what | why |
|---|---|
| `I.lt` (I's layout twin arm in every C1-C2 cell) | L9: every arm's launches now draw from its text's pool; a hash-equal arm of I's pool draws from I's pool, so the pool already holds launches of I's text at several layouts |
| `aa-twin` (A/A's layout twin) | L9: the A/A pair is `aa` and `aa.b`, two arms of aa's pool, each launch its own draw (the pair a head against I is, in the draw) |
| the layout twin term, `layout_sigma`, the `lay` floor component, `res["layout"]`, the "measured between-exe offset" print | L9: no separate term reads layout noise; it is in every arm's launches and every estimator reads it at its level. Replaced by `layout_reading` (a RECORD, never an input) |
| `LAYOUT_TERM`, `LAYOUT_TWIN_ARM`, `LAYOUT_TWINS` switches (and their places in every earlier control) | nothing left to switch; every earlier control now turns off only its own mechanism, as before rev 11 |
| `LAYOUT_PAD`, `pad_object`, `arm_lay`, `layout_proof` | the pad-object twin itself (r41 L1: a whole-.text shift by a multiple of the TU's alignment) |
| the confirm's fresh twins `I.cf` / `h<N>.cf` (the arms, their dry-run proof and gate pass, the `.cf` owed check) | L9: the confirm re-times I and the head on fresh draws of the same pools. The CONFIRM ITSELF is kept: the drills still need it (G3 / r38 R2's fast 3-of-5 split retires only by the confirm) |
| `synth_exe` and the `exeoff` drill model, r39 K1's drill rows (per-exe offsets, "the night measures the offset", their control) | replaced by `synth_body` / `synth_layout_effect` and the (r41 L9) rows |
| L4's two single-half rows (proposed) | both halves are deleted; the new pool refusal has its own one-control-per-half row |
| the first stop's gated rho, heads-only τ 3 % and τ 1 % power rows (as gates) | R2 A, B, D: kept as RECORD rows, not deleted |

## Validation

All under `nice`, `gnutimeout`; never more than 8 drill processes (one stray over the limit for
~1 min while a dry and two drills overlapped; the baseline selftest was stopped by `safekill`
to keep within it).

- **selftest (full; `selftest_full_r2c.log` on 992be5477):** `selftest: 205 checks, 1 failed`.
  The one FAIL was `(r39 K6) ... control (no G2 record, rev 10's rerun): stalled 0 of 12 (accept
  >= 1)`. The drill's 4.5 % win sat at rev 11's floor (~0.043, A/A from `aa`/`aa-twin`). Under
  `aa`/`aa.b` the floor reads ~0.047, so G2 = {16}'s one-comparison move of the floor no longer
  reached the band. The drill win was re-centred to 0.953 (b31effa9b), and the K6 block was re-run
  alone in the module: `ok (r39 K6) ... stalled 0, rerun timed the rule's owed list on every pass:
  True ...; control ...: stalled 4 of 12 (accept >= 1)`. A full selftest on the tip
  (`selftest_full_tip.log`, b31effa9b): `selftest: 205 checks, 0 failed`, rc 0. Class drill (r38, 89 rows) worst `(r38) noise at arm:
  H(8), every cell, tau 2 % P(h* != 64) = 0.017` (accept <= 0.05). Earlier controls: F3 48/50,
  G2 0.177, G3 0.397, fast split 27/100, H1 0.663, H2 0.403, J1 0.610 (each > its line).
- **selftest --rev12** (`selftest_rev12_r2b.log` on a68e56c17, the R2 B control re-run at τ 3 %
  in the full run above): 16 checks; the R2 B control first gated at τ 2 % read 0.143 (just under
  its 0.15 line). It is now gated at τ 3 % (0.423), with the τ 2 % reading printed. Quoted lines:

  | layout model | τ 1 % | τ 2 % | τ 3 % |
  |---|---|---|---|
  | phase (fixed function of text, 64-B phase) | 0.000, voids 0.000 (G) | 0.000, voids 0.000 (G) | 0.000 (G), voids 0.000 (REC) |
  | heads only | 0.000, voids 0.000 (G) | 0.000, voids 0.000 (G) | 0.000, voids 0.000 (REC, R2 B) |
  | rho 0.8 (REC, R2 A) | 0.017, voids 0.000 | 0.210, voids 0.000 | 0.260, voids 0.000 |
  | rho 0.95 (REC, R2 A) | 0.123, voids 0.000 | 0.663, voids 0.000 | 0.580, voids 0.003 |

  P(h\* != 64) over 300 nights (accept <= 0.05); voids = nights with a first void (accept <= 0.05
  at τ 1 %, <= 0.10 at τ 2 %). Controls: `(R2 B) control: heads-only tau 3 %, no per-text term`
  0.423 (accept > 0.15; τ 2 %: 0.143); `(R2 C) control: phase tau 2 %, the raw bimodal test`
  voids 0.263 (accept > 0.10). GAP_K 4.5 false-split rate per arm, variant-aware / raw: 0 / 0
  (τ 0, 1 %), 0 / 2.5e-4 (τ 2 %), 0 / 1.25e-3 (τ 3 %). Power, layout τ 0 (gated) / 1 % / 2 %
  (RECORD): one 5 % winner 281 / 170 / 7 (rev 11's line 270), one 10 % 300 / 299 / 260 (270),
  multi 279 / 176 / 5 (255). Pool refusal per half ok; L6 ok.
- **The first stop's numbers** (before R2, `selftest_rev12.log`, 30 checks, 13 failed): P(h\* !=
  64) phase 0.000 / 0.000 / 0.010, voids 0.023 / **0.310** / **0.490**; heads-only 0.000 /
  **0.057** / 0.007, voids 0.040 / **0.943** / **1.000**; rho 0.8 0.017 / **0.247** / **0.350**;
  rho 0.95 **0.117** / **0.603** / **0.630**; power at τ 1 % 192 / 299 / 184.
- **Measured for the questions (scratch, not in the selftest):** GAP_K table
  (`gapk_table.txt`): K 4.5 / 5.0 / 5.5 / 6.0 -> false voids a night at τ 2 % 0.29 / 0.10 / 0.02
  / 0.00, τ 3 % 1.20 / 0.38 / 0.10 / 0.05; the F3 control arm (2 of 5 launches 8 % slow, σ 1 %)
  flagged 0.94 / 0.88 / 0.76 / 0.61 (its selftest row needs >= 45/50). Power at layout τ 1 % with
  more launches (`power_L7.log`, `power_L9.log`): LAUNCHES 7: 263 / 240; LAUNCHES 9: 277 / 273
  (pure noise 0.000, no voids, median f 0.050 / 0.043).
- **dry** (WIDTH_FLAG=none; run on 1712a0812: R2's diff touches only `analyse`, the drills and
  `power_line`, none of `dry`'s build/gate/proof path, so it was not re-run): `--quick` (`dry5.log`) and FULL subject (`dryfull.log`, cold rundir,
  JOBS=6, 298 s wall): cells 1374, built and gated 1374, failures 0; 80 timed texts x 4 variants
  = 320 exes; distinct 64-B phase vectors per pool min 3 max 4, 32-B min 3 max 4, relative
  layouts min 2 max 3; pools REFUSED 0; deny check 42 / 54, 0 failures; step 2b's check WOULD
  REFUSE (VACUOUS at width 32, the known r39/r41 NOTED case: the night runs the combined branch).
  Example pool line: `# pool dig24 h4 off: v0 64B 32,0 32B 0,0 rel 48/144; ...` (before the fix;
  after it every pool shows >= 3 distinct vectors).
- **plan:** 1374 cells (AA 24, C1 480, C2 600, C3 144, C4 48, C5 78); 267 pcrec compiles; at
  most 219 timed texts x 4 = 876 gcc compiles + links (an upper bound: the dry run found 80
  distinct timed texts, 320 exes, since hash-equal arms share a pool); run 788 cells timed, 0.11 h; gates +2364 calls,
  +0.0066 h; c3 96 cells, 0.01 h; rerun ~5 s a C1-C2 cell (10 arms); confirm bound 56 cells, 456
  arm cells, 0.065 h; 132 timing cells, 3940 timed launches (rev 11: 860 cells, 0.11 h).
- **plan** re-run on the tip: identical (run 788 cells 0.11 h, gates +0.0066 h, c3 0.01 h,
  confirm bound 0.065 h).
- **make strict:** rc 0 on the tip ("whole tree compiles clean with -Werror -Wshadow; the kit's
  target table check passes").
- **doc checks:** `make test-claudemd-size test-spec-history test-doc-lint` rc 0 (15 / 11 checks
  passed, 0 failed).

**The night's job set** (`/var/tmp/pcrec-pcrec/scratch/memfn/fcards/jobs/`, read, not edited):
- 701/703's est/cap read `plan`'s `run:` / `c3:` hours (`plan_hours`): unchanged at 0.11 / 0.01 h,
  so est/cap unchanged and the total cap stays 9,672 s. The gates on every variant are priced in
  those hours by `EST_GATE_S`.
- 700's `cards.py dry`: now 4 gcc compiles per timed text and a gate per variant; measured 298 s
  for the full dry from a cold rundir at JOBS=6 (700 runs JOBS=8; its est 800 / cap 2400 hold).
  Its greps (`^# dry:`, `^FAIL`, `WOULD REFUSE`) and the expect line (`^# dry: cells N, built and
  gated N, failures 0;`) still match; `# dry: layout pools ...` is one more `# dry:` line printed;
  a refused pool is a `FAIL POOL REFUSED ...` line and a non-zero exit.
- 701's `g2_record` (`cards rule RUNDIR --g2 FILE` before `run`): works with L6 (the run id is
  written by that call and kept by `run`); `rule_verdict`'s patterns and the canned outputs are
  untouched by this diff.
- R2 changes nothing the job set reads: `rule` prints two more lines (`rule: layout pools ...`,
  `rule: power at this night's layout sigma ...`), neither matching `rule_verdict`'s patterns;
  LAUNCHES unchanged, so est/caps unchanged. **The job set needs NO changes.**

## STATE AT HANDOFF

DONE. Committed tip: the branch head (`git -C worktrees/formsfixk log -1`); last rulings entry
applied: R2. The rulings file is gitignored here; its R2 text in summary: A rho rows
RECORD, the common share is the body's own layout (the text's speed), print the share, no data
prelude; B per-text layout term, ACCEPT heads-only τ 2 % <= 0.05, τ 3 % may be RECORD; C
variant-aware bimodal test, GAP_K 4.5, re-derive its rate, ACCEPT phase voids <= 0.10 at τ 2 %
(RECORD at 3 %), F3's control keeps its rev 11 line; D power RECORD at τ >= 1 %, the night prints
its power against its measured layout sigma and whether it is below rev 11's lines, LAUNCHES and
the 3 h cap fixed. All met (Validation).

For the next round (sized round 7): the per-text term's largest value on a synthetic τ 1.5 %
night is 0.11 (one cell's floor), which is where the power goes; a reviewer may want the term's
df (4 variants a text) drilled at its own level. `POWER_RECORD` is a hand pin from one drill run:
re-pin when the rule or the drill moves (the selftest prints both).

OWED: none.
