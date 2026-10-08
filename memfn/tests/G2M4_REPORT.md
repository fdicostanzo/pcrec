# G2M4 — G2 brought to MF_SITE_ABI 6 (lane g2m4, D27-blinded)

Lane g2m4, 2026-10-08, Linux dev box, in the cell `worktrees/g2u-cell/`. Serves
the kit's request R-7 (M4). Written from `memfn/include/memfn.h`,
`docs/design/memfn/integration.md` (Q-R7-1/2/3 and section 14) and the cell's
own G2 files; the kit's source was not read.

## Headline

`memfn/tests/run_g2.sh --quick --rows`, final tree, seed 20261005, gcc 15.2
(no clang on this box, so the ASan+UBSan leg did not run, as in the baseline):

| | passed | failed | wall |
|---|---|---|---|
| before (baseline reproduced here) | 45,210,391 | 19,294 | not timed |
| after, final tree | **47,436,029** | **0** | **134 s** (126-136 s over five runs) |
| after, `--seed 7` | 47,535,635 | 0 | about the same |

Exit 0. The before-run's reds reproduce exactly as the brief says: the `base`
family reads-below FINDs and rows check (b) "rows never chosen:
arms/pf_memchr_back".

**`arms/pf_memchr_back` chosen: 4,566** (summed over the nine kit-selecting
processes of the tier: the generator and the eight W2 mutation generators; the
unmutated generator alone chooses it 1,011 times). The manager pins its
`g2_floor` from these. Per-process the count differs by mutation, so the
tier-summed figure moves only if the generated space does.

The rows section (all 14 rows chosen at least once, floor 14):

```
row-chosen arms generic 218676        row-chosen runcmp bytes 18882
row-chosen arms ofsskip 25757          row-chosen runcmp memcmp 41420
row-chosen arms pf_memchr 4211         row-chosen runcmp overlap 9234
row-chosen arms pf_memchr_back 4566    row-chosen runcmp words 17642
row-chosen arms pf_memchr_bounded 3619
row-chosen arms pf_walk 4692
row-chosen arms pf_walk_bounded 4291
row-chosen arms precheck 2629
row-chosen arms precheck_assign 2856
row-chosen arms runcmp 22350
PASS (a) REACH_DROPPED 0; PASS (b) every row >= 1 (+ its control); PASS (c) 14 >= 14; PASS (d) (+ its control)
```

## Commands

```
cd /home/pcrec/projects/pcrec/worktrees/g2u-cell
TMPDIR=$PWD/.scratch/tmp taskset -c 12-15 gnutimeout 1500 memfn/tests/run_g2.sh --quick --rows
```
Run in the background, log polled. Nothing else was run at higher parallelism;
no full tier, no `make`. Sabotage runs used `--keep` in scratch copies under
`.scratch/sab/` (below).

## Charter checklist

| # | item | artifact |
|---|---|---|
| 1 | Q-R7-1 read-bounded range, the reference's split from the contract's definition | `g2/g2_ref.c` `g2_ref_readsbelow` + `g2_ref_range` (the one statement of the range; the reference, the driver's `admit()`, its planting windows and the PF positive test call it). Generator: `gen_reads_below` + render() (own statement of the same rule, used only to keep the site's other facts true). Driver: plants hits AT c == n, `lo` at the planted hit's edge; census line `G2 read-bounded range`. W1 defect 4 (the OLD range) |
| 2 | Q-R7-2 AT_N: driver establishes lo <= n, non-NULL subject; AT_N on ADVANCE refuses; a family | `G2_EMPTY_AT_N` (g2.h); `admit()` skips lo > n (counted) and `call_on()` aborts the run if an AT_N site is ever called with lo > n or a NULL subject; refusal case `ADVANCE-empty-AT_N`; family `mline` (`gen_fam_mline`); semantic field `empty` class 3 on every non-ADVANCE seed; refusal case for the value past AT_N |
| 3 | Q-R7-3 LOOP_EXIT: its own class; generic-only sites refuse naming `on_miss`; driver-owned loop | enforced class `loop-exit` (`G2_PEND_LOOPX`); `wrap_loopx` (g2_gen.c) owns the loop; seven `LCASE` refusal-table shapes; the generic-row guard; W2 mutation 8 |
| 4 | FLOOR_ROWS 13 -> 14 | `run_g2.sh` |
| 5 | MF_SITE_ABI + 1 refusal | `abi-mismatch` uses `MF_SITE_ABI + 1`, no 6/7 hardcoded; PASS in the generator results |

## What the three contract changes look like in G2

**Q-R7-1.** A FIND (not ON_CAND) whose every term has offset + len <= 0 (a SET
term's len is 1; E the largest) takes candidates c in [lo, n] with c + d <= n,
d = max(0, end_back + E); empty iff lo + d > n (lo > n included). Every other
site keeps [lo, n - end_back). The reference computes this from the contract's
words. The driver was taught that c == n is a candidate (its planting window
stopped at n - 1), and puts `lo` at the planted hit's edge, because a site
whose floor is lo has lo + 1 as its first valid candidate. The generator makes
the contract's other clauses true of such a site, deterministically (no RNG
draw, so no older site moved): `miss` must be a value no hit can take, and `n`
(and `n - 1` at end_back 1) is a hit here, so those modes become `-1` / `n + 5`;
no span fact is stated (a span bounds hi - lo and hi is not n - end_back here).
Populations (quick, hard sites that ran): 458 reads-below FIND sites, 1,669,322
checks, 304,535 with the hit planted at n, 124,723 answers that ARE a hit at n
(RETURN/ASSIGN, where the result shows it). "A family at offset -1 with the
target byte at s[n-1] must find n" is every `mline` RETURN-shaped check at
c == n.

**Q-R7-2.** The wrapper-level promise is kept by the driver (`admit()` plus a
`call_on()` backstop). The reference needs no new branch: the empty-scan outcome
is MISS's. `mline` base cell: STMT / FIND / ASSIGN, ONE REQUIRED one-byte SET at
-1, end_back 0, empty AT_N, `floor` the same text as `lo` (`floor_lo`; the driver
passes fl == lo), a leaving `on_miss` (goto / return, `on_miss_leaves` 1), no
`miss`, no result_decl, no note. It makes `arms/pf_memchr_back` chosen. Fourteen
one-thing-changed variants (`MLV_*`: stated miss, offset -2, end_back 1, reverse,
no floor, result_decl, note, on_miss_leaves 0, multi-member set, a 2-byte run at
-2, the three other empty outcomes) are hard sites rendered by whatever row
serves them. 454 AT_N sites ran, 1,648,697 checks, 67,376 with lo == n (the
zero-byte scan the proof is about); 9,468 instances were refused as lo > n (they
come from semantic variants of the lo-past-n PF seeds).

**Q-R7-3.** `on_miss` exactly `break;` is `g2_site.loopx` and the enforced class
`loop-exit`. The wrapper runs the rendered site inside a `for (;;)` THE WRAPPER
owns and falls through to `g2_fell = 1; break;`; `missed` is `!g2_fell`. A
`break;` the kit pasted inside a loop or switch of its own leaves THAT one, the
statements after it run, `g2_fell` reads 1 on a miss, and the reference (a miss
expected) fails the call. The result is reported only on the fall-through
(`on_miss_leaves` 1 leaves it unspecified). Outcome per site: rendered by a
non-generic row and answer-checked, or refused naming `on_miss`; the GENERIC row
rendering one is a failure. Measured: 130 sites rendered (all `pf_memchr`, the
row family `pf_memchr_back` belongs to: `LOOPX forms=pf_memchr:130`), 24 refused
naming `on_miss` (the `mline` variants with a non-AT_N empty outcome, which the
back row does not serve), plus the seven refusal-table shapes, all refused
naming `on_miss` ("no row serves this site: `on_miss` (R2: stated as LOOP_EXIT,
not served)"). 466,830 checks, 25,941 took the break, 440,889 fell through.

## Sabotage (scratch copies under `.scratch/sab/`, never left in place)

Both ran the full `--quick --rows` command on a copy of `memfn/tests` made
before the last two driver tweaks (a census counter and the AT_N backstop;
neither touches the checks sabotaged).

**(a) The Q-R7-1 range reverted to the old `[lo, n - end_back)`** (the reads-below
branch of `g2_ref_range` disabled with `if (0 && ...)`): **152,270 failed
checks**, exit 1. Failed sites by family: `base` 50 of its sites, `mline` 406 of
406. A typical failure: `FIND/EXPR/RETURN ... n=7 lo=0: WRONG: RETURN: kit 7,
want miss 12` (the kit finds n, the old range says miss). The new floors also
tripped: "answers that ARE a hit at n 0 < floor 110000". The in-suite twin is W1
defect 4, which fails 50,637 checks on every run.

**(b) The driver ignores the break** (`wrap_loopx` ends `missed = 0;` instead of
`missed = !g2_fell;`): **25,941 failed checks, all 130 LOOP_EXIT sites failed**,
exit 1, "LOOP_EXIT checks that took the break 0 < floor 23000". The second
variant, "the break leaves a loop that is not the driver's", is W2 mutation 8,
which is part of the suite: it wraps the kit's text of every LOOP_EXIT site in a
loop of its own, and **130 of 130 are killed** each run (the floor requires all
of them, and at least 115 sites).

## Findings and open questions (readings, not resolved by reading the kit)

- **Q-G2M4-1. Do OPTIONAL terms count in "every term"?** memfn.h says "every
  term". G2 reads it as every term of the predicate, REQUIRED and OPTIONAL, E
  from all of them, so the range does not depend on which subset the kit tests.
  The generated space has 4 such sites; all pass. If the kit classifies from the
  terms it TESTS, the contract should say so.
- **Q-G2M4-2. ON_CAND.** The brief keeps `[lo, n - end_back)` for ON_CAND; the
  header names the rule only at `MF_OP_FIND`, with no handoff exception. G2
  follows the brief (the visit's own reach is `cand + reach <= n`). 11 generated
  FIND/ON_CAND sites with every term below run on the old range and pass.
- **Q-G2M4-3. Span facts and EXCLUDED on a reads-below FIND.** `span_lo/hi`
  "bound hi - lo", and EXCLUDED means lo < hi was proven; for this range hi is
  not `n - end_back`. G2 states no span on such a site and reads EXCLUDED as
  "the range, as defined, is non-empty". The contract is silent.
- **Q-G2M4-4. `miss` on a reads-below RETURN/ASSIGN.** "A value no hit can take"
  now excludes `n`, which `MF_MISS_N` names. G2 keeps its sites contract-valid
  (`-1` / `n + 5`). What a site that states `MF_MISS_N` on a reads-below FIND
  means is not said (the answers of n-as-hit and n-as-miss coincide in a RETURN
  value, so G2 could not tell a defect from a valid reading there).
- **Q-G2M4-5. NULL subjects.** AT_N proves a non-NULL subject; every G2 layout
  already passes one (a guard-page or heap pointer, even at n == 0), so G2 can
  assert the promise but cannot test a kit's response to a NULL subject at
  n == 0 on a NON-AT_N site (K27's case). Nothing in the contract says what
  that site must do, so nothing was added.
- **Q-G2M4-6. Identifying "the generic row".** The contract says the generic
  row serves no LOOP_EXIT, and `form_id` is documented as opaque. G2 compares
  the form id with the string `generic`, the name `FORM_FLOORS` already uses.
  A rename would silently make the generic-row guard vacuous. Mitigations:
  `FORM_FLOORS` fails first (generic has a floor of 5,800), and the guard is
  printed (`LOOP_EXIT rendered sites by form id`).
- **Q-G2M4-7. What is LOOP_EXIT exactly?** "Exactly `break;`." G2 tests that
  text only. `{ break; }`, `break ;`, `continue;` and `break;` with trailing
  text are not tested as LOOP_EXIT; whether they are BRACED/JUMP/OTHER and
  whether a row may paste them in a loop is the kit's lexical rule. The same
  hazard exists for a BRACED `{ break; }`.
- **Q-G2M4-8. Which sites are "only generic" candidates?** G2 cannot know and
  does not assume it. The seven refusal-table shapes and every LOOP_EXIT site
  are held to "rendered by a non-generic row and correct, or refused naming
  `on_miss`". Today all seven shapes refuse, so the refusal arm is exercised
  (floor 140 cases in the class).
- **Q-G2M4-9. Stage of the refusal.** The LOOP_EXIT refusal is raised at
  `mf_define` ("no row serves this site"); on the define+use path a use-time
  refusal naming `on_miss` is lawful and counted (`USEREFUSE`). G2 accepts a
  refusal at either stage if it names the field.
- No kit defect found: every check is green, so there is no finding against the
  kit's implementation of Q-R7-1/2/3 at this tier.

## Files changed in the cell

- `memfn/tests/g2/g2.h` (AT_N, `floor_lo`, `loopx`, family `mline`, class `loop-exit`),
  `g2_ref.h` / `g2_ref.c` (range, W1 defect 4), `g2_driver.c` (range use,
  planting at n, AT_N promise, census lines, mutants include LOOP_EXIT sites),
  `g2_gen.c` (`wrap_loopx`, `gen_reads_below`, `mline`, sem `empty` class 3, refusal
  cases, mutation 8). `g2_k1.c` unchanged.
- `memfn/tests/run_g2.sh`: `FLOOR_ROWS` 14; floors `mline:360`,
  `FLOOR_RB_*`, `FLOOR_ATN_*`, `FLOOR_LX_*`, `FLOOR_CLS_LOOPX`, `FLOOR_LOOPX_MUT`;
  W1 defect 4 and W2 mutation 8 in every witness loop (mutation 8 samples the
  pending-only batches, where LOOP_EXIT sites live); the generic-row guard.
- `memfn/tests/CLAUDE.md` (new section, role changes), this report.

New floors are measured values less about 10%: sites run `mline` 406 (floor
360), reads-below sites 458 (410), checks 1.67M (1.5M), planted hit at n 304k
(270k), hit-at-n answers 125k (110k), AT_N sites 454 (410), checks 1.65M
(1.48M), lo == n 67k (60k), LOOP_EXIT sites 130 (115), checks 467k (420k),
break path 26k (23k), fall-through 441k (390k), class cases 161 (140). The
full tier has more checks; the site counts are tier-independent. The full tier
was not run.

## Disclosure

Seen at spawn, not as inputs: the session-root `CLAUDE.md` (with the
manager's memory index and `docs/CLAUDE.md`, `docs/dev/CLAUDE.md` and
`docs/dev/lanes/CLAUDE.md`, which describe many kit lanes in prose, including
M4 and R-7 summaries; none was used to derive a check), the git status
snapshot (branch `lane/memfn-m4`, clean, five recent commit subjects), and the
environment note naming `worktrees/memfn` as the primary directory (nothing
was written there; one `rm` was blocked by the safety check, did not run, and
was not retried). Read by the brief's leave: `docs/dev/lanes/BOILERPLATE.md`,
`docs/dev/learnings.md`. Read in the cell: `memfn.h`, `integration.md` (sections
around 5470-5560 and what the greps surfaced), the cell's G2 files and prior
reports. Not read: `memfn/src/`, `src/`, `tests/`, git history. Runtime output
of the opaque binaries (`build/libpcrec*.a`) was read as it came: refusal
messages and the `MFTRACE REACH` lines the rows check consumes.
