# wsc3 — D172 S2 commit 3: the shadow to zero (the kit manager's rulings 1-6)

Lane wsc3 (kit lane of the memfn kit manager), 2026-10-22. Worktree `worktrees/wsc3`, branch
`lane/memfn-wsc3`, cut from `lane/memfn-wsc2` @ 7b6f59a73. Build go: Frank's conditional go for D172
(critics GO, main agreed; request R-29), as for wsc1/wsc2. Design: `docs/design/memfn/window_site.md`
rev 3.2 §5.1, commit 3. No rulings file was named.

STATE AT HANDOFF:
- **Commits:** two code commits, one per path class (§1), plus this report's commit.
- **The shadow** reads 0 on EVERY column over the corpus and over G2's generated span sites (§2).
- **Light checks:** green at the lane's code tip and at the kit-only commit (§5).
- **Owed:** the heavy job `578-kit-wsc3-heavy` (emit_sweep ×4 vs 3cd809da1, then `make test`) is
  QUEUED (§7).

## 1. The commits

| # | sha | path class | what |
|---|---|---|---|
| (a) | 50ab53739 | KIT PATH (memfn/ only) | rulings 1-3 in the family and G2's reference; window facts per part (`mf_pred.nalt`/`alts`/`wfloor`); the shadow's per-part records and its declared equivalence table; plant S1410 |
| (b) | e149a2e83 | PCREC PATH (src/ only, plus the Makefile's header dependency, finding W3-1) | the parts stated (ruling 3); R as the walk-proven stretch (ruling 4); the DFA hat's T (D-2); the D11 bound on the offset-skip block (D-5) |
| (c) | this commit | docs (`docs/dev/lanes/`, the lane index, the kit journal) | this report |

Main reviews (b) separately: it touches no file under `memfn/`. The Makefile hunk is pcrec's build, not
src/. It is in (b) because (b) is what exposed it; W3-1 says why.

## 2. The shadow, by column, before and after

`memfn/tests/wshadow.py --g2` runs over the emit_sweep corpus: 5811 patterns, default engine and
`--engine=vm`, 11,622 compiles, 0 timed out. It runs as queue job `578-kit-wsc3-wshadow` under the box
lock, about 4 minutes.

| reading | sites | reseed | stop | plan | pin | group | arm | text | never-yields (stop/plan/group) | G2 |
|---|---|---|---|---|---|---|---|---|---|---|
| BEFORE (wsc2 §4, its tip) | 7087 | 0 | 35 | 558 | 0 | 558 | 45 | 45 | (no table) | 0 failed |
| interim (wsc3 tip 66afe99ad) | 8157 | 76 | 77 | 79 | 10 | 79 | 76 | 79 | 35/35/35 | 0 failed |
| **AFTER (code tip feb808eec = e149a2e83's tree)** | **8157** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | 35/35/35 | **checks failed: 0** |

**AFTER, in detail:**
- 8157 window sites, 1070 of them pre-check FUNC parts.
- Family paths: empty 35, mass 4111, mass+pin 1070 (the parts), parked 2245, parked+pin 44, reseed 523,
  reseed+pin 129. The non-part paths equal wsc2's.
- Log: the queue's `done/20261022T034835.974237181-578-kit-wsc3-wshadow/job.log`.
- Records: `worktrees/wsc3/build/wsc3/wshadow_full/` (every `mismatch_<column>.tsv` empty).

**The interim reading** (tip 66afe99ad; preserved at `build/wsc3/wshadow_r1/`) had two classes, both
fixed in (a)/(b):
1. **The F0 class: 76 records, 65 patterns.** These are offset-skip blocks once D-5 stated their D11
   bound.
   - F0's span became `{0: F0, 1: any}`. The family's `f0_of` took only a one-position span as F0, so
     A-model did not hold. The RESEED alternative went unpriced and M-parked chose PARKED.
   - Fix: F0 is the first verify-YES span starting at 0 (window_site.md §1.2's bounded PF row states
     it so).
   - `(?=b)bc` was the same class, through the PARKED+C-pin path.
2. **The window-cube class: 2 records, `aa(?i:a)`.**
   - Today's run-pinned clause 4 (`ofs_test_verifies_run`) asks whether the model tests the WHOLE
     WINDOW, its cube `[aA]@2` included. With R stated as the exact stretch only, the family saw "R
     fully tested" and did not pin.
   - Fix: pcrec states R's walk-proven cube positions too (ruling 4 allows "exact, or walk-proven"). On
     a verify-NO R, the family's pin stretch stays the exact run.

## 3. Per ruling: outcome and evidence

### Ruling 1 — a FULL-SET position is never a plan test; its only role is the bound

**Kit (window.c).** A new declared Table C row, C-bound, is applied inside two rows:
- in C-yes, over the verify-YES meet;
- in C-floor, over the meet the plan reads.

A full-set position is no A-mass stop either. A-floor's basis now reads "no core position constraining
a byte".

**The bound.** `plan_of`'s hoisted bound spans every verify-YES core position, tested or not, so a D11
`{1: any}` is the bound alone.

**`legacy_ok`** reads `end_back` from that bound:
- past the terms, the bound is `end_back` 1 (at 1 only);
- inside the terms, the core terms imply it;
- below the terms nothing expresses it, so the floor row takes the site.

**The case the ruling's wording did not name.** On a bounded RESEED alternative, F0's span `{0: F0, 1:
any}` meets walked offset 1's verify-NO set. The full meet at offset 1 is then that set, not the full
set. C-yes reads only the verify-YES meet, which is full. So offset 1 is tested only where C-model picks
it, as prefix_k does.

**G2's reference** mirrors this:
- its plan excludes full-set positions;
- its tested list carries the bound as full-set core entries;
- A-mass skips full-set positions.

**Plant S1410** (C-yes back on a full verify-YES position) is RED.

**Outcome:** the 523 bounded-PF plan/group records are gone, and so are the 45 arm/text records (they
were D-2's, ruling 5). Plan and group are 0.

### Ruling 2 — the VM hats with an EMPTY start set: a declared semantic equivalence

**The record.** `wf_shadow`'s record gains `yields=O/F`:
- O is 0 where the old site has a REQUIRED SET term with an empty set: no candidate can hold it.
- F is 0 on the family's `empty` path (A-empty).

**The table.** `wshadow.py` gains `EQUIV`, the DECLARED EQUIVALENCE table. Each row holds a name, a
predicate over the record, the columns it excuses, and its reason.
- The one row, `never-yields`, excuses `stop`, `plan` and `group` where `yields=0/0`.
- `text` is never in the table, so the rendered text must still be equal.
- Excused differences are counted by row name, never dropped.

The family is unchanged: A-empty stays as designed.

**Outcome:**
- `equivalent never-yields: stop=35 plan=35 group=35`, the 35 `\p{Cn}`-shaped VM hats.
- Their text is equal (text column 0).

### Ruling 3 — window facts PER PART (per `mf_pred`)

**Kit-path commit (a).**
- **The facts.** `mf_pred` gains `nalt`, `alts` and `wfloor`, appended last with no `MF_SITE_ABI`
  move: a pre-check FUNC part's own window facts.
- **`wf_part_site`.** It makes a part the FIND site `precheck.c` renders it as: the offset-skip
  function, FUNC/RETURN, miss `n`.
- **`wf_parts_check`.** It checks each part's statement with `wf_check`, frame included, on every art.
  It refuses facts stated on `pred`, and on any predicate that is not a FUNC part of an ALL_PRESENT
  site.
- **`wf_parts_prepare`.** On the preview it translates each part's plan into today's part shape
  (E-func's legacy translation) and replaces that part's terms. A part with no legacy translation is
  refused loudly.
- **`window_route`'s old-field test.** It now reads `pred.nterm || npred`. This fixes the refusal the
  brief named, which before read `pred.nterm` alone.
- **The shadow.** `wf_shadow` writes one record per stating part (`part=K`), decided as that part's
  FIND site, with the composite's text. The old `reseed` column is 0 there: the run search re-seeds
  nothing.

**pcrec-path commit (b).** `req_site_define` states BOTH parts, the window and [K66]'s whole run, where
they ship. Each part gets:
- one alternative, entry NONE;
- one span: the run test's positions, each exact or the cube its mask leaves;
- core all, verify YES (the part is REQUIRED);
- floor SUBJECT.

The parts are found by `fn_ref` after the predicate loops, so S460's anchor text is kept.

**Family rules that had to generalize, keyed on facts** (window.c and G2's reference alike):

| rule | was (window_site.md §2.3) | now | why |
|---|---|---|---|
| C-pin clause 4 | "the plan does not already test all of R" | tests through the OTHER spans only (a C-model pick, another verify-YES span) | today's clause asks whether the MODEL's selection tests the run; a verify-YES R tested by itself would never pin, so the stop was dropped and the run split into two compares, where the part compares it whole today |
| R's member | least-mass EXACT position | verify NO: unchanged. verify YES: the least-mass position of all of R by cube mass, ties to the higher offset | `pcrec_find_run_scan_index`'s rule: the part's scan and `@idx`; a masked part may scan a cube (fn-pair) |
| the pinned stretch | the exact run around the member | verify NO: unchanged. verify YES: R whole | a masked part is compared whole today |

On the DFA prefilter (R verify NO), every row reads as before.

**Count of two-part pre-checks.** 69 pre-check site records state two parts and 932 state one. That is
1001 pre-check sites over 11,622 compiles (both engines), 1070 part records in all.

**Outcome:** every part record reads 0 on every column (path `mass+pin`, 1070).

### Ruling 4 — soundness first: every R position is exact or walk-proven

**Proof from the code, in five steps:**
1. **The pin is proven by the walk.** `pcrec_run_pin` (src/facts/kset.c) sets `pinned` only where the
   walk's own singletons spell the exact stretch `bytes[at .. at+len)` at offsets `o ..`. The test is
   `o->k[ro + i].count == 1 && o->k[ro + i].byte == r->bytes[s0 + i]` for every `i < l`.
2. **The walk's sets are supersets.** kset.c's header gives the guarantee: "no direction in which this
   walk can refuse a start the scan would have accepted".
3. **The walk stops before any match can end.** The `if (w.accept || w.ncur == 0) break;` loop exits
   mean every walked offset is a byte every match has.
4. **So the pinned stretch is proven.** It, and any window position whose k-set at its offset lies
   inside the position's cube, is a necessary condition of a match at that offset.
5. **The rest of the window is not proven.** The `req_run` fact says only that every match contains
   the window SOMEWHERE. The pin says only that the stretch sits at `o`. Nothing ties the window's other
   positions to the pinned occurrence.

**Counterexample (`--emit-facts` on this tree):** `xy.*xy(?i:z)`.
- `req_run` = `78795a@2/ffffdf`, the window `xy[zZ]`.
- `run_pin` = `0:0+2`.
- `kset_walk` = `120,121,[255],...`.
- wsc2 stated R = `x@0 y@1 [zZ]@2`, verify NO: "every match has z/Z at offset 2". The match of
  `xyAxyz` at 0 has `A` there.

**Fix (b), `pf_window_of`.** R is now the window's WALK-PROVEN stretch:
- the pinned stretch, each byte asserted to be the walk's singleton (a loud internal error otherwise);
- widened over each adjacent window position `walk_proves` admits (the offset inside the walk, its
  k-set within the position's cube);
- each position stated as its byte or cube;
- unproven positions never stated.

Two conditions change with it. The PARKED pin fact reads "R covers offset 0 with an exact position that
is k0 = F0". The `o >= at` exclusion is gone.

**Witness S1411.** It is feasible as a wshadow witness run. It is not feasible as a G2 plant: G2 states
its own facts and cannot see pcrec's statement, and nothing in pcrec renders through the family before
commit 4.
- **The plant:** a scratch copy of the tree at HEAD (`build/wsc3/s1411`), `pf_window_of` stating the
  whole window at `o - at` again.
- **The run:** `wshadow.py --tree <copy> --pattern 'xy.*xy(?i:z)'`.
- **Planted:** plan 1, pin 1, group 1, text 1. The family no longer pins, because its member moves to
  the unproven cube. Records in `build/wsc3/s1411_out_s1411/`.
- **Clean tree:** 0 on every column (`build/wsc3/s1411_out_wsc3/`).
- **Its suite home:** a mech row, once commit 4's NEXT reads the reply. The S1411 id is reserved for
  it.

### Ruling 5 — D-2, the DFA hat: state the pattern fact

**What the code says** (emit_dfa.c, "THE DFA HAT" section and `pf_dfa_start_set`):
- The hat's rows skip to the next byte of T = S, the `start_set` fact: the bytes a match can begin
  with.
- They RE-SEED the landing state from the byte before it, where the skip moved.
- E (k0) "plays no part in soundness, only in admission and cost".

So the hat's candidate definition is T, a PATTERN fact. It is not k0.

**Fix (b).**
- `pf_window_of` takes the PARKED set and its offer from the builder. The PF site states the set its
  scan takes (`pf_site_of`'s `set`: T on the hat, k0 elsewhere), with that site's own table offered
  (`start_bytes` on the hat, `can_begin_match` elsewhere).
- The offset-skip block states k0: the offset rows sit above the hat.
- The PARKED R condition still reads E, so no R is stated in PARKED on a hat. E has 2 or more members
  there.

**Outcome:** the 45 arm/text records (the hats with T one byte, for example `\bx`, rendering pf_walk
over E) are 0.

### Ruling 6 — D-5: state the bound wherever the site has it

**Fix (b).** The offset-skip block states the D11 core `{1: any}` wherever the machine has the bound
(`f->views`, the fact the PF site reads). Its caller's text clamps to that bound, so the bound is a fact
of the candidate.

**Outcome.**
- It exposed the F0 class (§2), fixed in (a).
- Under ruling 1 it then moves no plan: the block's tested offsets reach at least 1, so the bound lies
  inside the terms and `end_back` reads 0.
- reseed, stop, plan and text read 0 over the 129 reseed+pin, 523 reseed and 44 parked+pin records.

## 4. The plants

| id | where | what | result |
|---|---|---|---|
| S1400-S1407, S1409 | `run_g2_win.sh --plants` | as wsc1/wsc2 | all RED at the code tip (§5) |
| S1408 | `tests/memfn/run_proof.sh --plant S1408` | as wsc2 | RED: `READS: a fault (guard at s + n)` |
| S1410 | `run_g2_win.sh --plant S1410` | C-yes takes a verify-YES position whose meet is every byte | RED: `FAIL: site parked#46 DECIDE: plan of 1, the reference 0` (2831 passed, 169 failed) |
| S1411 | wshadow witness run (ruling 4) | pcrec states R's whole window at `o - at`, past the walk-proven stretch | planted: plan/pin/group/text 1 each on `xy.*xy(?i:z)`; clean: 0 |

## 5. Light checks (Linux dev box, gcc 15.2; logs `build/wsc3/light_*/`)

| check | code tip (the tree of e149a2e83; `light_c`) | kit-only commit 50ab53739 (scratch copy; `light_a_kitonly`) |
|---|---|---|
| `make strict` | clean | clean |
| sabotage anchors (`scripts/m6read_check_sab_anchors.py`) | 901 rows / 932 sites, all resolve | 901 rows / 932 sites, all resolve |
| `tests/codegen/run_codegen_tests.sh` | 331 passed, 0 failed | 331 passed, 0 failed |
| `make test-core` | rc 0 | rc 0 |
| `make test-memfn-{link,manifest,stamps,arms,deleg,arch,forms,reach,rows,finder,rank,guarded,simdfloor,g2}` | each rc 0 (g2 quick: 71,217,801 passed, 0 failed) | each rc 0 (g2 quick: 71,217,801 passed, 0 failed) |
| `memfn/tests/run_g2_win.sh` | 6032 passed, 0 failed (pinned 194, reseed_bit 253) | 6032 passed, 0 failed |
| `run_g2_win.sh --plants` | 10 of 10 RED | 10 of 10 RED |
| the shadow (§2) | 0 on every column; G2 0 failed | not run: the kit commit alone reads pcrec's wsc2 statement |

The first light run at the interim tip (`light_ab`) went red on three checks. All three are fixed:
- the anchors and codegen (SABANCHOR): S460's anchor text, kept in (b);
- `test-memfn-manifest`: W3-1.

## 6. Findings and the remaining deviations

**W3-1, a Makefile dependency gap** (fixed in (b)).
- `known.c` reaches `memfn.h` through `src/gen/known.h`, but it was missing from the Makefile rule that
  rebuilds the kit header's includers.
- After `mf_pred` grew, an INCREMENTAL build left `known.o` on the old layout. Every
  `--harness=kit-proof` compile then declined `cover` (`test-memfn-manifest` rules 4 and 5 red), while a
  fresh build was green.
- This is the class of the `emit_vm.o` stack-smash the rule's comment records.
- `known.o` and `known.h` are now in that rule, and `test-memfn-manifest` is green.

**W3-2, the family-rule changes, for the kit manager's ruling.** These are deviations from
window_site.md §2.3's text:
- C-pin's clause 4;
- the member and stretch keyed on R's verify (§3, ruling 3);
- F0 as the first verify-YES span at 0.

On the DFA prefilter they read as the design does. They move PREVIEW-only plans in two places:
- **The parts:** new; they are what reads 0 now.
- **REPORT/cover sites whose span 0 is run-shaped** (a literal): span 0 is verify YES and is now pinned
  whole with the stop inside, where it was C-yes minus the stop. That is S3's form question (581's PRO).
  It is not measured here.

**W3-3, the readers of `@idx` at commit 6.** The member differs by site:
- **The PF site:** R is the walk-proven stretch, so the reply's member is its least-mass EXACT
  position, today's pin pick.
- **`REQ_RUN`'s `@idx` today:** `ReqRun.idx`, the scan index over the whole window, cube positions
  included.
- **The pre-check part:** its reply member equals `ReqRun.idx` (one rule; the part states the whole
  run).

Main's condition (a), one resolving function, should therefore read the PART's reply where a pre-check
states one.

**W3-4, the walk-proven widening is pcrec's reading of "walk-proven".** A window position counts as
proven where the walk's k-set at its offset lies inside the position's cube. That is the same test today's
`ofs_test_verifies_run` applies to a model term. The widening is what zeroed `aa(?i:a)`.

**The remaining deviations.**
- **Resolved:** D-1 (ruling 3), D-2 (ruling 5), D-3 (ruling 4), D-5 (ruling 6).
- **ACCEPTED** (the brief): D-4, D-6, D-7, D-8, D-9.
- **New ones:** W3-2 (for the kit manager), W3-3 (for commit 6).
- **Not done here:**
  - `mf_wdecide` (the phase-1 API) does not yet decide a PART: commit 4's ask.
  - `REACH_ONLY=1` was not run: no default row's reach moves, and no NEXT row reads the new facts.

**The derived sabotage list for (b).** Every anchor resolves (901 rows). The S460 anchor sits on
`req_site_define`'s loops. Its text is kept verbatim, because the parts are stated after the loops, by
`fn_ref`, so its intent is unchanged.

## 7. The heavy job (OWED)

`578-kit-wsc3-heavy` is queued at the lane's final tip.
- **Job file:** `build/wsc3/578-kit-wsc3-heavy`.
- **Queue settings:** kit band, `idle-ok`, cap 14400 s.
- **`--ready`:** first holds while main's `i2build-parity` is pending or running.

It runs, in order:
1. `make -j16`.
2. `emit_sweep --ref 3cd809da1` four times:
   - plain streams `c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr`, dumps excluded;
   - `--arms start`;
   - `--extra=-fno-run-prefilter`;
   - `--extra=-fmemfn-simd`.
3. `scripts/perfrun --label wsc3 -- build/wsc3/heavy/maketest.make.log`.

**Completion lines:**
- four `emit_sweep: DONE rc=0` (`expect sweeps=4`), each with zero movers;
- `== wsc3 heavy: 0 step(s) failed`;
- the make verdict: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/wsc3/heavy/maketest.make.log`,
  empty = green. Read it with `scripts/verdict`.

**Logs:** `worktrees/wsc3/build/wsc3/heavy/{build,sweep_plain,sweep_arms,sweep_norun,sweep_simd,maketest}.log`,
and the queue's job.log under `worktrees/.boxqueue/done/<ts>-578-kit-wsc3-heavy/`.

The tree is clean after queueing; do not edit `worktrees/wsc3` until the job has started (its dry run
needs a clean tree).

## 8. Checklist

| item | state |
|---|---|
| ruling 1: full-set position never a plan test, bound only; plant S1410 | done; plan/group 0; S1410 RED |
| ruling 2: declared equivalence row in wshadow.py, not in the family | done (`EQUIV`, `never-yields`, 35×3 excused, text compared) |
| ruling 3: kit commit per-part facts + family per part; window_route's refusal fixed; pcrec commit states both parts; two-part count | done; 69 two-part, 932 one-part sites |
| ruling 4: R only exact or walk-proven; proof from kset.c/run_pin; witness S1411 | done; proof §3; S1411 as a wshadow witness run (no G2 plant: infeasible, why given) |
| ruling 5: the hat states its pattern fact T, T's table offered | done |
| ruling 6: the bound stated wherever the site has it | done (offset-skip block) |
| shadow zero on every column, corpus and G2 | done: 0 / 0 |
| commits split by path class; pcrec commit pcrec-only | done (a) kit, (b) pcrec (+ Makefile, W3-1) |
| R-29's fact table only (D157) | yes: spans, alternatives with entry, offers, floor; no rank, pick or plan |
| light checks after each commit | green at both commits (§5) |
| heavy job `578-kit-wsc3-heavy` queued, idle-ok, main's hold line | queued; OWED |
| report, lane index entry, kit journal | this commit |
