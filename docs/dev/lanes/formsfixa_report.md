# formsfixa report — review r35's cards-rule, script and doc fixes (R-45 plan A)

Lane formsfixa (opus), 2026-11-17, branch `lane/memfn-formsfixa` from `lane/memfn-forms` @ 7506bca30.
Input: review r35 with the kit manager's RULED section (now `docs/dev/reviews/2026-11-17-r35-memfn-forms.md`).
Sibling lane formsfixb holds F12-F17, F20, F23, F29 (G2, checks, cli/main.c, window.c); this lane touched none of
its files.

## Summary

- **F22 first:** `lane/memfn-r45` (69acf5376) merged in ALONE (17d3dbb8f). Its diff against the merge base
  ea83fbc01 is 28 paths, every one under `docs/` (two `.c` files are review artifacts under
  `docs/dev/reviews/`), so docs-only. Two append-only index conflicts were resolved keep-every-line. Six
  `docs/dev/reviews/CLAUDE.md` index lines (r12, r20, r21, r22, r23, r25) moved to that directory's NOTES.md,
  because the merged file was 13,675 B, over the 12 KB limit.
- **The rule (F2), mechanism in one line:** f = max(the largest A/A ratio, exp(z(0.05 / N) x σ_up) - 1).
  - σ is the A/A cells' RMS log ratio, raised to its 95 % upper bound (χ², Wilson-Hilferty).
  - N is the head-against-I comparisons the rule makes, so the floor is a Bonferroni bound over the
    comparisons actually taken.
  - A head whose emitted text equals I's in a cell reads I's median there (one text, one binary).
- **The F2 noise drill,** 108 C1-C2 cells x 9 heads, 300 nights through the whole rule:
  - P(h* != 64) = **0.033** under normal launch noise and **0.027** under t(5). The acceptance is <= 0.05.
  - Under rev 6's floor, with every other change kept, the same drill gives 0.487.
  - Power: a true 10 % win picks h* = 8 in 59 of 60 nights.
- **The F3 bimodality test:** an arm is bimodal when its 5 launches split into two groups of two or more,
  with a gap of more than 4.5 launch σ between them. The launch σ is pooled per (regime, layer) as a median.
  - Unimodal drill (t(5) launches, 300 nights): **2.0 %** of nights void any cell. That is 0.017 % of cells.
  - Control: a truly bimodal arm voids in 48 of 50 nights.
- **The rule's other fixes (cards.py and design rev 7 alike):**
  - C3 is timed at the picked h* in a step 2b (`cards.py c3`).
  - A gate failure is R0 for its head, in any card and C3 included. Gate failures of I or A/A make the night
    DEFECTIVE.
  - Step (5) ships the largest R0-surviving head, or "no form ships".
  - `rerun` is a step: R1 waits for it, and the results are merged.
  - The kit's NOT-WARM / short-subject approximations are void by method.
  - The identity check reads its census from the sweep's corpus through the cover facts. It covers both
    encodings, requires FROZEN, and refuses at H < 64 with no movers file.
  - The labels are the record. DERIVED is defined.
  - NOT-WARM is calibrated on calls, and `plan` prints the expected wall time.
- **Docs:**
  - F1: the deny's refusal past ~3,300 wide positions, in registry §6¶8a and tuning §2.43¶3d.
  - F21: ¶3d now reads "UNMEASURED DEFAULT: CHOSEN, the cards' grid top; the form cards will replace it".
  - F24: the force overrides the lever. `cards.py` is added to cli/CLAUDE.md's spellings list.
  - F19, F25, F27, F28 are in rev 7.
  - The review is filed as **2026-11-17-r35-memfn-forms.md**, with its critic texts.
- **Cards stay in kit-grid@7, not kit-synthetic (the lane-ask ruling):** kit-synthetic's cards are the
  synthetic sets' and are "never measured" (its header). These are measured method cards. The kit-grid@7
  header records the same.

## Fixes

| id | fix | commit |
|---|---|---|
| F1 | One sentence in registry §6¶8a and tuning §2.43¶3d: past ~3,300 wide positions the deny, and a lever head that high, can exceed `PCREC_MAX_VM_EMIT_CODE_BYTES` and is refused where the default (and the force) compile. "Answer-identical in every state" becomes "... that compiles". Rev 7 corrects plan B's cap citation (the binding cap is 500,000, not `PCREC_MAX_EMIT_BYTES`), and the C4 row names the VM cap. The main-side PLAN half (limits.md on covs2b, the fit rung) is main's | 35231f062, 8ba79b895 |
| F2 | The count-sized floor (`count_floor`) and the I-text substitution. Rev 7's "The floor `f`" gives the mechanism and one paragraph of why. Noise drill (xv) in selftest | d696ef198, 8ba79b895 |
| F3 | The gap bimodality test (`bimodal`, `launch_sigmas`). Results keep every launch. Rev 7 defines "bimodal". Unimodal drill (xvi) plus a control | d696ef198, 8ba79b895 |
| F4 | `run` times C1, C2, C5 and A/A. `c3 RUNDIR H` times C3 (and records C4's sizes) at the picked h*. Until then `rule` prints "R2(C3)/R5 NOT COMPUTED at h* = N" and exits 3. Night step 2b is added in rev 7 | d696ef198, 8ba79b895 |
| F5 | `GateFail` rows are status `gatefail`, never void, and are R0 for their head (C3 included). A gate failure of I or A/A makes the night DEFECTIVE. Step (5)'s head is the largest R0-surviving head, or "no form ships". A C3 void is re-run, then recorded, and is never dropped. Drill (xii'), plus the C3 gate-fail case (h* 32, exit 3, not a clean tie) | d696ef198, 8ba79b895 |
| F6 | `r1` with no surviving head returns "no form ships" (drill (viii)'s last case, in selftest) | d696ef198 |
| F7 | `rerun RUNDIR` re-times every arm of each cell void once and merges the rows over the first reading. `rule` refuses step (5) while a cell has been attempted once (exit 3, "NEXT cards.py rerun"). Three selftest cases | d696ef198, 8ba79b895 |
| F8 | Approximated regimes are VOID BY METHOD (counted as void twice, never re-run) and are not floor inputs. `run` skips them unless `--with-approx` (a record only) | d696ef198, 8ba79b895 |
| F9 | `identity` reads the census from the sweep's corpus (`emit_sweep.enumerate_corpus` plus the frozen pcrec's `cover` facts, K35 floor at zero). It compiles both encodings and both layers. It refuses an unset FROZEN, FROZEN == REBUILT, and H < 64 with no movers file | d696ef198, aa37029ce, 8ba79b895 |
| F10 | MEASURED names its kit-grid@7 card rows and the count of cells read. DERIVED when R3 tracks (each class's own pick = the surviving grid head nearest its E[D]). The "slower" grid-top label takes a colon (drill (v)) | d696ef198, 8ba79b895 |
| F11 | NOT-WARM is calibrated on calls (one pass of n/4096 chunk calls). `plan` prints each step's expected wall from named UNMEASURED per-launch costs | d696ef198, 8ba79b895 |
| F19 | Rev 7 strikes the formhash force-instance bullet: NOT BUILT, with no reader (D77). TRIGGER: a card naming `kit:form.span-*` | 8ba79b895 |
| F21 | ¶3d reads "UNMEASURED DEFAULT: CHOSEN, the cards' grid top; the form cards will replace it". Rev 7 "Scope" records the h = 64 interim, quoting forms_report.md's Summary line and the kit journal's 2026-11-17 03:00 line, and states how it differs from "built but OFF". The decisions/plan record is main's | 35231f062, 8ba79b895 |
| F22 | `lane/memfn-r45` merged (docs-only, checked path by path) | 17d3dbb8f |
| F24 | The force also overrides the lever (registry §6¶8a, tuning ¶3d). cli/CLAUDE.md's spellings list names `memfn/tests/span_forms/cards.py` | 35231f062 |
| F25 | Rev 7 quotes the owner's sentences in full (including the 15:00 "will only have a short span and ... of the prover"). It spells out near-miss-fix-later's polarity and quotes the rulings' in-tree record: requests.md R-45 "RULINGS ON THE REPLY", and main's dev_journal at b1bcee85b. The decisions row is main's | 8ba79b895 |
| F27 | Rev 7 "Named witnesses": `\w{32}\B` does not move at h* <= 32 in this build, because the E-find probe's offset splits the run. The predictor stays a superset | 8ba79b895 |
| F28 | Rev 7 "The forms": the minimum of two entries is DERIVED (a one-entry loop is a lone test plus overhead, and gcc unrolls two trips). The `wf_loop_len` comment is in window.c, which is formsfixb's file, so that comment is NOT added here | 8ba79b895 |
| review | Filed as `docs/dev/reviews/2026-11-17-r35-memfn-forms.md` (+ dir of the 7 critic texts), RULED section included, with the reviews CLAUDE.md line. r35 was re-checked free on main, lane/covs2b and every `lane/*` branch. Three cites of a limits.md section only lane/covs2b has (3.12) were respelled in words, because the tree's cite check reads this tree's limits.md | a6c6254be |

Notes for the merge with formsfixb:
- F15 asks "cards.py asserts that arm I has zero loops". It is formsfixb's finding, but it lands in cards.py,
  which this lane rewrote. Apply it on top of a6c6254be (an assertion in `dry`/`run` over arm I's artifacts).
- F28's `wf_loop_len` comment is owed in window.c (formsfixb's file). The derivation text to cite is rev 7
  §3 "The forms".

Choices this lane made inside the ruled scope, for the kit manager to see:
- F2's mechanism, with α 0.05 and a 95 % σ bound. The alternatives were weighed in rev 7.
- GAP_K = 4.5, chosen from a 2e7-sample simulation in scratch (`kcal.py`).
- R3's "tracks" means "the nearest surviving grid head, the larger on a tie".
- `run` skips the void-by-method regimes by default.
- Bench-only census patterns reach `identity` through main's movers file. The bench's pattern list is not
  read from pcrec-bench.

## Validation

All runs are local and `nice` under `gnutimeout`. No timing, no queue jobs, no cloud.
- `python3 -I memfn/tests/span_forms/cards.py selftest`: **37 checks, 0 failed** (22 s). The ruled lines:
  - `(F2) noise drill, normal launches sigma 1 %  P(h* != 64) = 0.033 over 300 trials (accept <= 0.05); median f 0.0434`
  - `(F2) noise drill, t(5) launches sigma 1 %  P(h* != 64) = 0.027 over 300 trials (accept <= 0.05); median f 0.0371`
  - `(F3) unimodal drill, t(5) launches  void rate 0.020 of nights, 0.00017 of cells over 300 nights (accept <= 0.05)`
  - `(F3) control: a bimodal arm voids  ... voided in 48 of 50 (accept >= 45)`
  - All 23 design drills hold, including (viii)'s all-fail case and (xii'). The C3 gate-fail case gives
    h* 32 and exit 3, not a clean tie.
  - Control on the drill itself: rev 6's floor, swapped in (`scratch/.../oldfloor.py`), gives P = 0.487.
- `cards.py dry RUNDIR --quick` (WIDTH_FLAG=none; this tree has no width option; under `scripts/boxlock run`):
  **cells 1374, built and gated 1374, failures 0; distinct compiles 269**.
- `cards.py plan`:
  - 1,374 cells (AA 24, C1 480, C2 600, C3 144, C4 48, C5 78).
  - Expected wall, UNMEASURED: run 788 timed cells ~0.11 h (1,182 with `--with-approx`, ~0.80 h); c3 96 cells
    ~0.01 h.
- `cards.py identity`:
  - The refusals fire: FROZEN unset; FROZEN == REBUILT; H = 8 with no movers file.
  - Smoke with `--census-limit 200` (exit 4, not a verdict): the census read 200 corpus patterns, 2 covered;
    head 64: 19 patterns x 2 encodings x 2 layers, 0 differ.
  - Control at head 0 with a movers file: 20 differ.
  - The full census read: 5,516 corpus patterns, 1,075 covered.
- `make strict`: clean.
- `make test-spec-history`: 11 passed, 0 failed.
- `tests/registry/axes_registry_check.sh`: 248 passed, 0 failed.
- `tests/registry/limits_check.sh`: 42 passed, 0 failed.
- `tests/compound/run_lever_fence.sh`: PASS (3 checks, 4 controls).
- `scripts/check_claudemd_size.sh --all`: within limits.
- Logs are in `/var/tmp/pcrec-pcrec/scratch/memfn/formsfixa/`.

## STATE AT HANDOFF

STATE: done. Rulings file `docs/dev/lanes/formsfixa_rulings.md`: empty at every piece; last entry applied: none.
OWED: none.
Main-side parts relayed by the review, not this lane's:
- F1: limits.md and the fit rung.
- F21 and F25: a decisions row carrying the 2026-11-16 rulings and the h = 64 interim.
