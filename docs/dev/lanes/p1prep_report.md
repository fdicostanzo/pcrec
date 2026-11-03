# Lane p1prep — P1 landing preparation (timing read, the +1 identity mover, landing draft, [LANDWALK-PRES])

Lane p1prep, opus, 2026-11-01, worktree `worktrees/p1build`, branch `lane/p1build` (tip 45dd1bf99 at
start). Prep only: there are no code changes. The landing below is a DRAFT for the manager; nothing
in it was executed. Light work only: reads, single-pattern compiles, and one scratch build of the
ac4917d reference compiler (`gcc -O0`, one process). No suite, no sweep, no queue job. Scratch:
`$PCREC_TMPDIR/scratch/p1prep/`.

## Summary

- **Timing (job 712-p1build-timingr):** answers are the same on every cell. The walk wins big on 5b
  (x68.8 instructions / x45.3 cycles on acc-main) and on qnt-plus `a+b` (x5.1 / x3.2). It loses on
  one cell that is not N1, and that cell is [LANDWALK-PRES]: `[a-z]+@x` on acc-small, x0.77
  instructions / x0.83 cycles. Every other loss beyond noise is the N1 dense-landmark shape and sits
  inside the ruled N1 bound (ruling 2026-11-01 13:45). The worst is the card's wlen-2 hit cell, +23%
  cycles.
- **The +1 mover is population, not a P1 move.** It is a new `landwalk.rxt` pattern, not an existing
  pattern that P1 moved. On vm the pattern is `(?i)[a-z]+@X`: the pre-module reference emits an
  empty node for the leading `(?i)`, and main emits none. The same class is already in main's red,
  for example `(?i)ab`. P1's program region equals main's byte for byte. The brief missed a second
  +1, on the default and noprefilter arms (167 -> 168). That one is p1kind's
  `[a-z]+@x(?:(y|\G)+){0}`: dead-capture elision makes it a DFA artifact on main and on P1, where
  the reference made it a VM artifact. P1 equals main there too. Neither mover changes an answer.
- **Landing draft:** abi 95 if R-30 (94) lands first. It is 94 if P1 lands first, by the
  landing-order precedent of s3m and landtgc. Every reader is listed below. Also drafted: the FILEPIN
  re-pin to the landing merge, D184, the ledger class `major` with its line, and S1855 joining the
  arm's row list. Two merge-order risks were found: P10 also writes `docs/spec/tuning.md` §2.54, and
  p4entry and R-30 both claim 94.
- **[LANDWALK-PRES]:** recommendation: do NOT gate. Land P1 with the loss recorded. A declared-row
  fix that needs no pricing exists: apply G1's existing identity/run conjuncts to the walk's
  landmark scan instead of the blanket `whole`. It should follow the rule-list pilot's verdict
  (Monday) as a separate small lane.

## TIMING

Source: `worktrees/.boxqueue/done/20261031T082823.969134049-712-p1build-timingr/` (green, 3/3 stages,
wall 20 s, 08:28 2026-10-31, taskset -c 7). It writes `$PCREC_TMPDIR/scratch/p1build/timing/`
`{card.tsv, speed_main.txt, speed_deny.txt}`, all three timestamped inside the job's window. The
contaminated 712-p1build-timing is ignored. Numbers are the measurement's own lines (medians of 9
interleaved passes; the card: medians of 9 repeats, A/A spread = the denied twin's (max-min)/median).

**Bench cells (speed.sh; `main` = main's build/pcrec; `deny` = the lane's own `-fno-landmark-walk`):**

| cell | subject (matches) | instr walk/base | x (instr) | cycles x, vs main | cycles x, vs deny |
|---|---|---|---|---|---|
| 5b email | acc-main (80,123) | 79.57M / 5,477.6M | **x68.84** | x45.32 | x43.57 |
| 5b email | acc-small (830) | 0.838M / 59.4M | **x70.89** | x62.72 | x52.50 |
| 5b email | fz-me, N1 (7,946) | 101.35M / 97.58M | x0.96 | x0.98 | x0.98 |
| 5b email | qs-200k (0) | 1.969M / 1.969M | x1.00 | x0.98 | x1.02 |
| qnt-plus `a+b` | t-1m (1,505) | 0.990M / 5.070M | **x5.12** | x3.19 | x3.21 |
| qnt-plus `a+b` | t-256k (377) | 0.248M / 1.274M | **x5.15** | x3.26 | x3.26 |
| `[a-z]+@x` | acc-small (0) | 0.556M / 0.426M | **x0.77** | x0.83 | x0.84 |

`answers=same` on all 7 cells in both runs. The deny column's instructions equal main's to within
3 instructions on every cell, so the lane's deny artifact is main's artifact (as p1build recorded
for 5b).

**Noise floor.** Instructions:u are deterministic: the two runs agree to within 5 instructions on
every cell. Cycles are the timing. The card's A/A spread is 1.0-6.4% (column `aa_spread`). Across
the two speed runs the same artifact's cycles moved up to x1.85 on the smallest cell (5b qs-200k:
1.32M vs 2.45M cycles). Within a run, the walk/base ratio held to about 2-4%. So on cells under
about 3M cycles, a cycles ratio is good to about ±4% and no better. Instructions are the stable
reading there.

**Card (card_lwalk.sh --timed, `[a-z]+@x` against its denied twin; ns/B, one forward DFA step
u = 1.1292 ns/B):**

| row | wlen | arm | walk | denied | walk vs denied | A/A spread |
|---|---|---|---|---|---|---|
| lwhit | 2 | miss | 1.268 | 1.839 | walk x1.45 faster | 1.0% |
| lwhit | 8 | miss | 1.161 | 1.450 | walk x1.25 faster | 1.5% |
| lwhit | 32 | miss | 1.276 | 1.237 | walk +3.2% | 1.6% |
| lwhit | 2 | hit | 2.566 | 2.085 | **walk +23.1%** | 2.8% |
| lwhit | 8 | hit | 1.925 | 1.781 | walk +8.1% | 6.2% |
| lwhit | 32 | hit | 1.586 | 1.511 | walk +5.0% (inside noise) | 6.4% |
| lwcall | - | 5-byte call | 7.968 ns/call | 8.523 ns/call | walk x1.07 faster | 1.6% |
| lwfit | - | miss / hit | a=2.80 b=1.144 / a=8.76 b=1.262 walkbytes | | | |

Hit counts agree between the walk and the twin on every lwhit arm (the card's own check).

**Wins:** 5b on match-bearing logs (x68.8 / x70.9 instructions; x45 / x63 cycles), qnt-plus `a+b`
(x5.1 instructions / x3.2 cycles), the sparse-landmark card arms (miss wlen 2 and 8: x1.45 / x1.25),
and the per-call term (lwcall, 7% faster). The latter meets design G4: no admitted cell loses beyond
`lwcall`'s bound.

**Losses beyond noise, each with its pattern and subject:**

| loss | pattern | subject | size | class |
|---|---|---|---|---|
| L1 | `[a-z]+@x` | acc-small (830 `@`, no `@x`, no match) | x0.77 instr / x0.83 cycles | **[LANDWALK-PRES]** (below) |
| L2 | 5b email | fz-me (one `@` per ~10 B) | +3.9% instr / cycles x0.98 | N1, inside the bound (ruled) |
| L3 | `[a-z]+@x` | card lwhit wlen 2 hit (`ab@x ` repeated: one landmark and one match per 5 B) | +23.1% cycles | N1, inside the bound, the worst cell (ruled) |
| L4 | `[a-z]+@x` | card lwhit wlen 8 hit | +8.1% cycles | N1, inside the bound (ruled) |
| L5 | `[a-z]+@x` | card lwhit wlen 32 miss | +3.2% cycles | N1, inside the bound (ruled) |

The wlen 32 hit cell (+5.0%) is inside its 6.4% spread. By the manager's ruling (2026-11-01 13:45),
L2-L5 are NOT new: each is the N1 dense-landmark shape (p1dsg3 "Non-goals", ruled by Frank) and
sits inside its bound (x1.25 instr / x1.28 cycles). So the STOP RULE's "a loss beyond noise other
than [LANDWALK-PRES]" did not fire.

Design acceptance cell 1 (5b on acc-main within ±1% of 77.76M instructions) reads 79.57M, +2.3%.
That is the scan-edge cost p1build recorded and filed into [LANDWALK-EDGEPRICE]; it is unchanged
here. The `lwfit` intercept (hit a = 8.76 walkbytes) is the first measured source for `k_hit`
(LMWALK_K_HIT_UNMEASURED = 10). Per p1build's landing note it goes to a [MEASURE-SET] row, not a
constant edit.

## MOVER

**Inputs.** P1 is job 762, `worktrees/.boxqueue/failed/20261031T164323.704737382-762-p1mech-ident/job.log`.
The main-side counts come from 745-vmrecm-test, `failed/20261031T043504.365036529-745-vmrecm-test/job.log.ident`
(vmrec on main d30f5bb78). The landing checks 695-lands3, 696-landic3 and 698-recida (2026-10-29)
all read the same counts: (A) default 167, vm 382, noprefilter 167, nocaptures 111. These are the
known [RECID-A] numbers in the full-suite ledger.

| arm | main (A) same / differing | P1 (A) same / differing | population | buckets that moved |
|---|---|---|---|---|
| default | 2565 / 167 | 2589 / **168** | +25 | ctx-node 462 -> 463 |
| vm | 2077 / 382 | 2099 / **383** | +23 | ctx-node 455 -> 456, island 76 -> 77, litrun 310 -> 311 |
| noprefilter | 2566 / 167 | 2590 / **168** | +25 | ctx-node 462 -> 463 |
| nocaptures | 2715 / 111 | 2740 / 111 | +25 | none |

(B) is 0 differing on every arm in 762 (vs 8aedc62ee) and in 709-p1tri-test (vs 379b84fac). So the
(A) gate list is the only place a mover can show. The brief named only the vm +1. The default and
noprefilter arms carry a +1 too.

**Method.** The job log prints only the first 10 REGION DIFFERS lines, and both runs print the same
ones. The full list is a temp file that the gate deletes, so the movers were found by population.
P1's corpus adds 29 unique pattern lines, all from `tests/landwalk/landwalk.rxt`; no line was removed
(merge base 5796317e9 vs HEAD). 27 of them are call-free; the two DEFINE ones are call-bearing, as
507 vs 505 in the gate's positive control shows. The ac4917d reference compiler was built in scratch
the gate's own way (`git archive ac4917d src lib cli`, `gcc -O0`). The gate's own `stamp_strip`,
`prog_region_raw`, `adv_layout_canon` and `trail_check_canon` (copied from
run_recursion_identity.sh) then compared the program region of each new pattern: the subject compiler
with `-fcomments`, the reference without, per the gate (`$PCREC_TMPDIR/scratch/p1prep/newcmp.sh`,
`cmp_vm.txt`, `cmp_default.txt`).

| arm | new patterns whose region differs from ac4917d | bucket that explains it | P1 region == main region |
|---|---|---|---|
| vm | `(?:ab\|cd)+@x` | island (+1) | yes |
| vm | `a.*b@c` | litrun (+1) | yes |
| vm | `[a-z]+(?<=a)@x` | ctx-node (+1) | yes |
| vm | **`(?i)[a-z]+@X`** | **none: the +1** (it stamps `RX_VM_CLS_FOLDS 1`, but `-fno-cls-fold` does not restore the pin) | **yes** |
| default, noprefilter | `[a-z]+(?<=a)@x` | ctx-node (+1) | yes |
| default, noprefilter | **`[a-z]+@x(?:(y\|\G)+){0}`** (p1kind's D family) | **none: the +1** | **yes** |

**The vm mover, `(?i)[a-z]+@X`.** The reference's region carries a `// empty` node and an extra
label for the leading `(?i)` (`rx_L0: goto rx_L2;`). Main's and P1's regions do not. Main stopped
emitting that empty node after the pin. With the fold denied, only that label shift remains, so the
fold bucket cannot excuse the pattern and it lands in the unexplained list. The same shape is already
in main's red: the existing corpus patterns `(?i)a*`, `(?i)ab`, `(?i)abc`, `(?i)cat`,
`(?i)a(?-i)b` and three more all read main != ref on vm. `(?i)ab`'s diff shows the identical
`// empty` + label shift. P1's whole file for `(?i)[a-z]+@X --engine=vm` differs from main's only
in the abi digits and the `#include` name. It entered at p1build (709-p1tri-sec already read 383).

**The default/noprefilter mover, `[a-z]+@x(?:(y|\G)+){0}`.** The capture inside the `{0}` body is
erased by the dead-capture elision (`A_REP{0,0}` emits nothing), so main and P1 both select the DFA
(empty program region). The reference selected the VM. The gate's elision bucket admits only its 4
NAMED patterns, so a new pattern of the same kind is counted as differing. It entered with p1kind's
six D-family blocks (709-p1tri-sec read 167; 709-p1tri-test, after p1kind, read 168).

**Verdict: an expected, explainable change, not a finding.** Both movers are NEW corpus patterns
whose emitted program is byte-identical to main's. They differ from the August pin for two reasons
main already carries in its [RECID-A] red. No answer moves, and no existing pattern moves. At the
landing, the known [RECID-A] counts become **168 / 383 / 168 / 111** (from 167 / 382 / 167 / 111).
The ledger's recidentity note should carry the new numbers with this reason.

## LANDING DRAFT

Written, not executed. Order: merge main into the lane, re-validate, then merge to main. Main is
53 commits past the lane's base 5796317e9, including lane/vmrec (D182, a byte-identical emitter
rewrite), axtri and file1101. The two sides share these files outside docs: Makefile,
`tests/lib/san_excluded.txt`, `tests/mech/run_sabotage_matrix.sh`, `tests/memfn/site_manifest.tsv`,
plus the CLAUDE.md/NOTES.md files under `src/gen/` and `tests/codegen/`.

### 1. The abi number

- **95 if the kit's R-30 lands first** (lane/memfn-r30b already carries `PCREC_ARTIFACT_ABI 94`; its
  r30b2 mech jobs 779-781 are in the queue today). **94 if P1 lands first.** By the landing-order
  precedent, the number is main's number + 1 at the merge. s3m renumbered 84/85 to 92 "in landing
  order", even though 85 had been held reserved. landtgc numbered trailgc's provisional 93 as
  92 -> 93. `docs/dev/history/abi_changelog.md` records both. A reservation that skips a number
  (main 93 -> 95 with 94 still unlanded) leaves the later lander BELOW main. That lander would then
  renumber anyway.
- **Conflict to rule:** 94 is claimed twice. lane/memfn-r30b sets it in code. p1tri's report says
  "94 reserved for p4entry" (lane/p4entry is still at 93 in code). p10build carries 96.
- **Readers of the number on lane/p1build** (grep `(abi|ABI).{0,12}9[3-6]` over src, tests, docs/spec,
  lib, cli, memfn, examples; then `` `95` `` in docs/spec). Each one moves if the number changes:

| reader | site | today |
|---|---|---|
| the `.abi` stamp, the banner, the `PCREC_RX_ABI_H` guard (all three from one macro) | `src/gen/emit_dfa.c` `#define PCREC_ARTIFACT_ABI` | 95 |
| the test expectation | `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=` | 95 |
| the spec's guard snippet (three lines: the `!=` test, the `#error` text, the `#define`) | `docs/spec/match_api.md` §1 | 95 |
| the spec's `rx_info` table, row 1 (`abi`) | `docs/spec/match_api.md` §6 | `95` |
| the spec's sentence "It is `95` on every artifact pcrec emits today" | `docs/spec/match_api.md` §6¶17 | 95 |
| the bump-omitted sabotage | `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE` (95) / `SAB_AFTER` (main's number, 93) + its RE-AIMED comment | 95 / 93 |
| the change-log entry (top of list) | `docs/dev/history/abi_changelog.md` "is `95` ... (93 -> 95 PROVISIONAL)"; the prior entry becomes "was `93`" | 95 |
| the identity gate's (B) pin + its SELF-PIN comment | `tests/codegen/run_recursion_identity.sh` `FILEPIN=` (see 2) | 379b84fac |
| comments citing the number (history, not readers; leave) | `run_facts_checks.sh` "(abi 95)"; `run_cpset_structure.sh` "RE-RECORDED ... abi 95" | — |

  If R-30 lands first, its own 94 entry in the change log, S693's AFTER and FILEPIN all conflict with
  P1's. Resolve them as "P1 is 94 -> 95, prior entry R-30's 94" and set S693 `SAB_AFTER` to 94. Then
  run the D94 suites that count: registry, codegen (`make test-codegen`), rxtsource.

### 2. The FILEPIN re-pin (after the merge commit exists)

`tests/codegen/run_recursion_identity.sh`: `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-<landing merge sha>}"`.
The provenance text, prepended to the chain:

> `<sha>`, lane/p1build merge commit (landing <date>): abi 9N, [LANDWALK] stage 1 landmark-walk
> LOCATE row, re-pinned from the lane self-pin 379b84fac; (B) 0 differing at 379b84fac (job 709),
> and the later src commits e766f6b15 (p1kind) and d6e03a594 (p1mech) byte-identical (job 762, 0
> differing vs 8aedc62ee); before it ebcc10aa1, ...

The landing gate is `make test-recursion-identity-locked` at the new pin. Its expected reading:
(B) 0 differing on all four arms, and (A) the known [RECID-A] at 168 / 383 / 168 / 111 (MOVER).

### 3. The D entry: D184 (next free; main and every worktree top out at D183)

> **## D184 — the landmark walk: a LOCATE row that seeds a reverse machine at each landmark hit; RECOVER's asker is derived (lane p1build, 2026-10-29; Frank's build go; landed <date>)**
>
> **Decision.** One DFA-route LOCATE row, `landmark-walk` (order `empty, rev-end, cover,
> landmark-walk, composite`), searches a one-branch pattern P·L·R from each occurrence of a byte
> class L that P can never consume. Each hit walks the reverse machine of P·L back to its leftmost
> accepting start s* (floored at `search_from`), and one inline anchored run of the finisher decides
> the match there. A hit the last run already read past relocates to `composite` from s* (the reach
> guard, linear). Admission is a declared first-match conjunct table (`lmwalk_conj[]`, ten rows).
> Rarity is priced against NEXT's counterfactual start set (the `NEXT_cf` memo) with an UNMEASURED
> `k_hit` default. The row is a public deny, `-fno-landmark-walk` (bit 57), because the walk CAN be
> slower on a caller's input (dense landmarks, N1, a ruled non-goal). It is also a size-cap rung
> (`drop-landmark-walk`, before `drop-anchored`).
>
> **Why it would surprise a reader.** (1) The walk's code runs no RECOVER block, yet RECOVER is asked
> on its path. RECOVER's ASKER is a derivation (`cand_recover_asker`): the LOCATE row whose walk
> runs the RECOVER block, the relocate target where FINISH relocates. The walk row carries no
> `.recover` field, because that field would be a declaration false of its row (review r7 FIX-1).
> An admitted selection with a NULL slot is refused at compile time. (2) The walk declares
> `whole`, so PRESENCE reads `dominated` and drops the whole-window pre-check. That costs a
> no-match subject carrying L often and the required run rarely ([LANDWALK-PRES], x0.77
> instructions on `[a-z]+@x`). It was landed with the loss recorded, and the fix follows the
> pricing rule-list pilot's verdict. (3) A's availability is admission row 2's alone. The
> predicate's own re-read of `anchored_ok` was removed as a second mechanism for one fact (p1mech,
> S1824). Row 1 (`finisher-dfa`) is implied by row 2 today; S1822 is retired UNREACHED and the
> [cand-ma-dfa-only] tripwire re-arms it.
>
> **Measured.** 5b email x68.8 instructions / x45 cycles on acc-main; qnt-plus `a+b` x5.1 / x3.2;
> N1 (fz-me) +3.9% instructions, inside its bound; answers identical (a libpcre2 differential of
> 1.3M subject-answers, 0 wrong; the libpcre2-generated answer net, 181 cases under four
> configurations and 207 at default after p1kind's blocks).
>
> **Refs.** docs/dev/lanes/p1dsg3_report.md, p1build_report.md, p1tri/p1pin/p1kind/p1mech/p1prep
> reports; review docs/dev/reviews/2026-10-29-r7-landwalk3.md; `docs/spec/tuning.md` §2.54,
> `docs/spec/match_api.md` §6.3.4, `docs/spec/limits.md` §8.4; plan [LANDWALK], [LANDWALK-PRES],
> [LANDWALK-EDGEPRICE], [SEL-WORLD].

### 4. The full-suite ledger (D177): class **major** (new capability, abi event, new engine path)

Under "### major", at the top:

> - <date> <merge sha> major — merge lane/p1build: [LANDWALK] stage 1, the `landmark-walk` LOCATE row
>   (D184; reverse machine of P·L from each landmark hit, inline anchored verify, reach guard to
>   composite; RECOVER's asker derived; the `drop-landmark-walk` size rung; public deny
>   `-fno-landmark-walk`, bit 57), abi 93 -> 9N (artifacts it does not take move in the abi digits
>   only). Validated on the branch: 709-p1tri-test make test, 706-p1pin-startset, 713/761 mech (S1824
>   DETECTED, S811 DETECTED, S1822 retired UNREACHED, S1855 DETECTED), 762 identity (B) 0 on all arms,
>   (A) = the known [RECID-A] at 168/383/168/111 (+1 each from two NEW landwalk.rxt patterns
>   identical to main; p1prep_report.md MOVER); 712 timing (p1prep_report.md TIMING). Known loss
>   recorded: [LANDWALK-PRES]. Owed: the next full suite.

In the Runs notes:

> Landing <date> <sha>: lane/p1build ([LANDWALK] stage 1, D184; class major: a new capability, an abi
> event, a new search path); full-suite triggers per D177: major +1; recidentity's known (A) moves
> to 168/383/168/111 (population, not a move).

### 5. The sabotage-id list (S1855 joins)

- The landing's mech re-run list (the 20 ids of 713-p1build-mechb, which already carried S1855):
  `S1820 S1821 S1822 S1823 S1824 S1825 S1826 S1827 S1828 S1829 S238 S693 S738 S741 S744 S770 S777 S811
  S844 S1855`. Expected: S1822 UNREACHED as declared. The rest are DETECTED.
- `tests/mech/run_sabotage_matrix.sh`, the `landwalk` arm's comment ("Rows: S1820-S1829.") becomes
  "Rows: S1820-S1829 (S1822 retired UNREACHED; re-arm tripwire `cand_rows_check.py`
  [cand-ma-dfa-only]) and S1855 (lane p1kind, g1 reads nested \G/\K)". This file is also touched on
  main since the base, so merge it with care.
- `tests/landwalk/CLAUDE.md` already names "S1820-S1829 and S1855"; p1build_report.md's table stays
  as history.

### 6. Merge-order risk against R-30, P4 and P10

| lane | its abi | shared files with P1 (besides docs/dev) | risk |
|---|---|---|---|
| kit R-30 (`lane/memfn-r30b`, tip 66b1e2254) | 94 in code | abi_changelog, match_api.md, tuning.md, internal.h, emit_dfa.c, run_codegen_tests.sh, run_recursion_identity.sh, S693 | the abi readers (mechanical); R-30 changes the required-run ask, which sits next to PRESENCE's `dominated`, so re-read `req_dominated_applies`' merge by hand |
| P4 (`lane/p4entry`, tip 946f8931b) | 93 in code (94 "reserved" per p1tri) | the same eight | the abi readers only; rule the double claim on 94 |
| P10 (`lane/p10build`, tip 44d81d9a4) | 96 | the eight plus lib/pcrec.h, axes.def, cand_oracle_witnesses.tsv, run_prechecks.sh, run_registry_tests.sh, the two CLAUDE.md files | **`docs/spec/tuning.md` §2.54 is claimed by both** (P1 `-fno-landmark-walk`, P10 `-fdeferred-req-check`): the second to land renumbers to §2.55 and every citation of it. The bits do not collide (P1 57, P10 58; P10's comment already names 57). run_prechecks.sh: P1 adds `-fno-landmark-walk` to every compile, and P10 adds a one-attempt PRESENCE witness, which must also carry the walk deny if it takes the walk. axes-registry coverage pins (245 on P1) add up |

Whichever lands first, the second re-runs `make test-codegen`, registry and rxtsource, plus the
identity gate at its own new FILEPIN. Recommended order is landing order as it comes. The cost is
mechanical either way, and P1's draft above names every reader.

## LANDWALK-PRES

**The loss.** The walk row declares `.whole = true` (`src/gen/emit_dfa.c`, the `landmark-walk`
row). G1's second dominator (`req_dominated_applies`) therefore reads `dominated` and drops the
whole-window required-run pre-check on every walk artifact. On a no-match subject that holds L
often but the run rarely, the walk visits every L hit while main's pre-check answers in one
`memmem`: x0.77 instructions / x0.83 cycles on `[a-z]+@x` / acc-small (830 `@`, no `@x`).

**Reach.**
- **Timing data:** 1 of 7 bench cells, and that cell's pattern is the lane's own synthetic one, not a
  bench pattern. 0 of the 3 bench-population patterns have the shape. For 5b and `a+b` the required
  byte IS the landmark (`@`, `b`), and 5b's no-match cell qs-200k reads x1.00. cls-s-ucp declines the
  walk. The card cells end in ` @x`, so the run is always present there. They do not show this loss.
- **Corpus (stamps only, 19 single compiles, `$PCREC_TMPDIR/scratch/p1prep/pres_reach.txt`,
  `pres_runs.txt`):** every walk-admitted pattern checked moves PRESENCE `emitted` -> `dominated`.
  That is 15 landwalk.rxt patterns plus p1tri's 4 moved prechecks witnesses. The speed shape needs
  the pre-check to be stronger than the landmark scan: a required run of 2 or more bytes (`@x`,
  `aa`, `ABC`) or a different required byte. About 13 of the 19 have that shape, almost all of them
  test witnesses of the `[a-z]+@x` family. The other 6 are identity cases with no loss: 5b,
  `(?i)[a-z]+@X`, `\w+@\w+`, `x[0-9]+Q`, `[a-y]\d{0,150}:`, `[a-z]+@...x`. Whole-corpus reach is
  UNMEASURED. Measuring it means compiling every corpus pattern twice (with and without the walk deny,
  reading `RX_DFA_SCAN`, `RX_REQ_WHY`, `RX_REQ_RUN`), which is a sweep over 50 compiles. Queue it as
  a boxlock job if the manager wants the number.
- **Real-world reach is unknown.** The shape is "an email-like pattern whose literal suffix is longer
  than its landmark, searched over text with that landmark and no match". It is plausible, but no
  bench row has it today.

**Weighing.**
- **Speed x reach (Frank).** The loss is large per cell (17-23%) but has zero reach on the bench
  population and one synthetic cell. The win it travels with is x5-x70 on the bench population.
  On the product rule, P1 is a large net win.
- **One bounded effort for small losses.** That rule covers losses just above noise. This one is
  not small per cell, so it should get its fix, but the fix does not have to come before the landing.
  A caller hit by it recovers with `-fno-landmark-walk`, a public deny that exists for exactly this
  reason (N1).
- **Remodel-first (D153).** The fix site is PRESENCE's `dominated` row, which is the kit's PRES row
  P2 since R17-b' B3b (`req_pres_ask`), together with the `whole` declaration in `cand_rows[]`. That
  slot is exactly the one the owner's rule-list pilot (`lane/rulepilot:docs/design/pricing_rulepilot.md`,
  timing Monday) scores: PRESENCE is a choice slot on 46 of its 139 sites. The pilot decides whether
  `cand_rows`-style declared rules or pricing choose strategies. A priced PRESENCE rule written now
  is the change the pilot may reverse. R-30 also changes the required-run ask beside it.
- **Recommendation: do NOT gate P1's landing.** Land with [LANDWALK-PRES] recorded: the D184 text,
  the ledger line, and the plan row as filed. Schedule its fix after the pilot's verdict, as one
  small lane on the shape the verdict picks.

**A declared-row fix that needs no pricing (it exists).** G1 already decides when a candidate scan
dominates the pre-check, with three conjuncts (`req_byte_dominated_by`; the kit's P2 states the
same proof): (1) a RUN pre-check is dominated only where the scan verifies the run; (2) IDENTITY,
the scan's byte is the pre-check's byte; (3) DENSITY, a byte-rate compare that already exists, not
new pricing. The walk's `whole` answers presence by SCANNING L, so it is a candidate scan, and
the same three conjuncts should decide it. Today a blanket `true` decides it. The general form:
the walk row stops declaring `whole` and instead states its landmark scan (L, as the start search's
proof does) on the presence site. G1's existing rule then keeps the pre-check exactly where the run
is longer than L or its byte differs. A one-field interim spelling: `whole` on a LOCATE row becomes
a declared kind, `always` (rev-end, empty, cover: one pass over the window) or `by-scan` (the walk:
dominated only under G1's identity/run conjuncts on L). Both are declared table facts, not a
priced edge.

Expected effects, to be measured by the fix lane:
- `[a-z]+@x` / acc-small returns to main's 425K instructions.
- 5b and `a+b` are unchanged (identity).
- Match-bearing subjects of the `@x` family pay main's own per-call pre-check again, about one
  `memmem` pass. That is a few percent against the walk's gain; the fix lane measures it with
  card_lwalk.sh and speed.sh.

It needs a spec hunk: `docs/spec/match_api.md` §6.3.4's `dominated` sentence for the walk. It also
needs a small mover census (walk artifacts whose `RX_REQ_WHY` returns to `emitted`). Because it
touches the kit's P2 inputs (facts only, D157), file it with the kit as a fact change.

## STATE AT HANDOFF

- STATE: done. Branch `lane/p1build`; this report and its history-index line are the only commits of
  this lane. No code, test or pin was changed.
- Rulings file `docs/dev/lanes/p1prep_rulings.md`: last entry applied: "2026-11-01 13:45 (manager):
  the losses in your interim are RULED NOT NEW ..." (TIMING records them inside the N1 bound, the
  worst cell named). Re-read before this report's commit.
- STOP RULE: the +1 movers change no answer (P1 == main byte for byte). The only loss beyond noise
  other than [LANDWALK-PRES] is the N1 family, which was reported first (interim message,
  2026-11-01) and ruled not new.
- Scratch: `$PCREC_TMPDIR/scratch/p1prep/` holds `pcrec_ac4917d` (the reference build), `newcmp.sh` +
  `fns.sh` (the gate's own region functions), `cmp_vm.txt`, `cmp_default.txt`, `pats_new` (the 29
  new patterns), `pres_reach.txt`, `pres_runs.txt`, and the files lists behind the merge-risk table.
- Open for the manager:
  - Which number P1 lands as (94 or 95, by landing order).
  - The double claim on 94 (R-30 and p4entry).
  - P10's §2.54 collision.
  - Whether to queue the whole-corpus [LANDWALK-PRES] reach sweep.
  - The [LANDWALK-PRES] fix lane after the pilot's verdict.
- Nothing is OWED by this lane.
