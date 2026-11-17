# formsfixk report: layout pools replace the layout twins (review r41, RULED L9, L5, L6, L8): STOPPED

STATE: stopped (the brief's stop rule: drill and power rows miss their accept lines; see STATE AT HANDOFF)

Lane formsfixk (opus, 2026-11-17), branch `lane/memfn-formsfixk` from `lane/memfn-forms` @ 42fd4b33e.
Charter: review r41's RULED section (`docs/dev/reviews/2026-11-17-r41-memfn-forms6.md`, committed
here). Rulings file `docs/dev/lanes/formsfixk_rulings.md`: R1 applied (the Summary's last sentence).

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
(strict arguments, the keyed G2 record) and L8 (S3320/S3321 doc lines) are done. The rule's drill
rows under the four layout models the ruling names do NOT all hold, nor do two power rows at
layout τ 1 %: the lane STOPPED and sent the kit manager four questions (below, STATE AT HANDOFF).
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
- **L3.** The power rows at layout τ 0 and 1 % are gated with rev 11's accept lines, RECORD at
  2 %; r45_reply rev 12 states the numbers.
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

## Validation

All under `nice`, `gnutimeout`; never more than 8 drill processes (one stray over the limit for
~1 min while a dry and two drills overlapped; the baseline selftest was stopped by `safekill`
to keep within it).

- **selftest (full, HEAD's cards.py):** OWED at the time of writing; log
  `/var/tmp/pcrec-pcrec/scratch/memfn/formsfixk/selftest_final.log`, completion line
  `selftest: N checks, M failed` then `rc=`. Expected: every rev 11 earlier row as before plus
  13 FAILs, all in the (r41 L9) layout / void rows and the two (r41 L3) τ 1 % power rows below.
  A WIP run of the same earlier drills (`selftest_wip1_partial.log`, 105 lines, stopped early
  to free the box) passed every earlier row it reached, controls included: G2 0.177, F3 control
  48/50, G3 0.397, fast-split control 27/100, H1 0.663, H2 0.403 (accept > 0.15 or as stated).
- **selftest --rev12** (`selftest_rev12.log`, 30 checks, 13 failed):

  | layout model | τ 1 % | τ 2 % | τ 3 % |
  |---|---|---|---|
  | phase (fixed function of text, 64-B phase) | 0.000, voids 0.023 | 0.000, voids **0.310** | 0.010, voids **0.490** |
  | heads only | 0.000, voids 0.040 | **0.057**, voids **0.943** | 0.007, voids **1.000** |
  | rho 0.8 | 0.017, voids 0.003 | **0.247**, voids 0.040 | **0.350**, voids **0.210** |
  | rho 0.95 | **0.117**, voids 0.000 | **0.603**, voids 0.003 | **0.630**, voids 0.013 |

  P(h\* != 64) over 300 nights (accept <= 0.05); voids = nights with a first void (accept <= 0.05).
  Power (300 nights), layout τ 0 / 1 % / 2 % (RECORD): one 5 % winner 281 / **192** / 26 (accept
  >= 270), one 10 % winner 300 / 299 / 259 (accept >= 270), every head <= 16 5 % faster 279 /
  **184** / 30 (accept >= 255). GAP_K false-split rate per arm (1e5 arms): 0, 0, 3.5e-4, 9.1e-4 at
  τ 0/1/2/3 %. The pool refusal per half: ok. L6: ok (6 refusals, both `--g2` spellings, record,
  moved file, second list, another run's record).
- **Measured for the questions (scratch, not in the selftest):** GAP_K table
  (`gapk_table.txt`): K 4.5 / 5.0 / 5.5 / 6.0 -> false voids a night at τ 2 % 0.29 / 0.10 / 0.02
  / 0.00, τ 3 % 1.20 / 0.38 / 0.10 / 0.05; the F3 control arm (2 of 5 launches 8 % slow, σ 1 %)
  flagged 0.94 / 0.88 / 0.76 / 0.61 (its selftest row needs >= 45/50). Power at layout τ 1 % with
  more launches (`power_L7.log`, `power_L9.log`): LAUNCHES 7: 263 / 240; LAUNCHES 9: 277 / 273
  (pure noise 0.000, no voids, median f 0.050 / 0.043).
- **dry** (WIDTH_FLAG=none): `--quick` (`dry5.log`) and FULL subject (`dryfull.log`, cold rundir,
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
- **make strict:** rc 0 ("whole tree compiles clean with -Werror -Wshadow").
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
- If question D is ruled as more launches: LAUNCHES 9 doubles roughly step 1's timed part (0.11
  -> ~0.18 h by the plan's formula), 701's cap +~1.5 ks, past the fixed 3 h total: not possible
  without moving another job's cap.

## STATE AT HANDOFF

STOPPED by the brief's stop rule (a drill or power row misses its accept line). Committed tip:
the branch head (`git -C worktrees/formsfixk log -1`); last rulings entry applied: R1. Sent to the
kit manager at about 17:05 (SendMessage), with my leaning on each:

- **A. Correlated layout (rho rows).** A layout share common to every variant of a text is, by
  construction, that text's own speed; no within-text pool averages it (0.117 at rho 0.95, τ 1 %;
  0.60-0.63 at 2-3 %). Leaning: those rows RECORD (the rule measures layout-averaged speed),
  print the night's measured share, and optionally widen the draw with a data-section prelude
  (.rodata/.data placement is the one layout input the pools do not move today).
- **B. Heads-only layout.** The floor's estimators (A/A, I's pools) read only I's and aa's
  texts, so a head text more layout-sensitive than I is unseen (0.057 at τ 2 %, voids 0.94).
  Leaning: a per-TEXT layout term from each text's own launches grouped by the recorded variant
  (df = its launches over regimes), floor per comparison = max(current, the head's own term).
- **C. The bimodal test under layout mixture.** Voids 0.31 / 0.49 a night at τ 2 / 3 %; no GAP_K
  keeps both F3's control (needs ~4.5) and the void rate (needs >= 5.5). Leaning: a
  variant-aware test (the gap after removing the text's per-variant effect, same machinery as B),
  GAP_K kept at 4.5.
- **D. Power at layout τ 1 %.** 192 / 184 of 300 (accept 270 / 255); LAUNCHES 9 restores it
  (277 / 273) but breaks the 3 h cap. Leaning: power rows RECORD at τ >= 1 % and the night prints
  power as a function of its measured layout sigma (L3's own form).

What remains for the morning lane (once A-D are ruled): build B and C if ruled (in `analyse`,
`launch_sigmas`/`bimodal`, with drill rows), re-run `selftest` whole and `--rev12`, `dry`, `plan`,
then a sized round 7. OWED now: the final full selftest's quote (log path and completion line
above); if it shows any FAIL outside the 13 listed, that is a regression to chase first.
`lanecheck` is run with `STATE: stopped` (rc 2 is the honest stop).

OWED: the full selftest verdict (`/var/tmp/pcrec-pcrec/scratch/memfn/formsfixk/selftest_final.log`, line `selftest: N checks, M failed`); rulings A-D.
