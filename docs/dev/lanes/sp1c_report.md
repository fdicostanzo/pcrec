# sp1c — span_pick stage 1, unit 1c (kit-only spellings, U2) with D187's set-only step

Lane sp1c (opus) for the memfn kit manager. Branch `lane/memfn-sp1c`, cut from main 7b671bc2c (units 1a, 1f, 1g,
1b landed). Design of record: `docs/design/memfn/span_pick.md` rev 5.2 (§Staging's 1c row, §What stage 1 deletes
U2/U5, dispositions R4/R8 and C7, the Ratchet text); D186 + addenda 1-2; D187. Build go: the owner's conditional
approval of 2026-11-02, confirmed by main's GO for stage 1; D187's set-only step scheduled into 1c by the owner
(review 2026-11-04 r1, rulings on R7/R8). Scope: 1c and the D187 step only; nothing from 1d/1e.

## What changed

- **U2, ONE run member** (`memfn/src/window.c`, declared in `memfn/src/kit.h`): `kit_run_member(rate, at, src, n,
  exact, after)` returns `{pos, mass}`: the least-mass position (KIT_MASS_SUM over the position's set alone), ties
  per `T_MASS_STRETCH` through `kit_tie_takes` (the higher position). The positions are read one at a time through
  a `kit_pos_at` reader that returns position j as a byte set, so a run stated as sets (window.c's spans and plan)
  and a RUN term (presence) are asked alike. `exact` keeps one-member positions only (window.c's verify-NO member).
  `after` admits only positions the member order ranks strictly after it.
  - window.c's `run_member` asks it for R's member and keeps only the stretch. Its own argmin loop is gone.
  - **P3's run scan asks it** (presence.c). Its own `c < sm` loop is gone. P4 reads the member's mass (`sc.mass`)
    instead of recomputing the scan position's mass.
  - **translate's run ranking is DERIVED from it** (the -2 form): each answer is asked again from the last, so the
    ranking is the member order. Its insertion sort (`rank_pos[j] = (uint16_t)i`) and its `cube[]` rebuild are
    gone. `rank_pos[0]` IS the run member by construction, so there is no separate assertion to keep. Its
    positions are the plan's own sets (`w->set` from the term's first plan position); the term's run/mask are the
    cube derived from those sets (`run_bytes`, unchanged).
  - **Why -2 and not -1**: it is byte-identical. Both orders are the strict total order (mass ascending, then the
    higher position first). The rank went from 22 lines to 7, and the `after` argument is one condition in the
    member function. The cost is O(n^2) mass evaluations over n <= MF_RANK_MAX = 32 positions (memfn.h: pcrec's
    run analysis truncates at 32), at most 32 x 32 x 256 bit tests per ranking. That is compile time only, and
    negligible. U6 is NOT touched (the landmark shadow, a named member; R25 kept).
- **D187, set-only (byte-identical)**:
  1. `kit_mass(rate, set, n, cap)` now takes `n` consecutive 256-bit sets. `kit_pos` with its cube fields `t`/`mask`
     and the cube enumeration path is DELETED. This removes review R7's zero-value hazard: no field can be omitted.
     It also removes R10's repeated `&(const kit_pos){ .set = X }` call shape: every one-position call is now
     `kit_mass(rate, X, 1, cap)`. So **no wrapper was added** (R10). The one-byte cube spelled three ways is gone
     too. A member span is priced as its own one-member `term[0].set`.
  2. `kit_run_set(t, j, set)` (presence.c) is **the ONE run-position-to-set conversion**: {x : (x & mask[j]) ==
     run[j]}, the vocabulary's formula (memfn.h `mf_term.run`). Its readers:
     - presence's run window (`win[][32]`);
     - the landmark admission (its inline 256-loop rebuild is retired: HOUSE-1);
     - the run member's presence reader `run_at`;
     - compose.c's `term_prove` (its identical inline loop is retired).
  3. **NORMAL FORM, a checked fact at the input boundary**: `kit_presence_check` (compose.c) refuses a RUN presence
     span with a byte outside its mask. The text is "a RUN presence span states a run byte outside its mask
     (`run[j] & ~mask[j]`: the span would never hold, Q-G2-13; D187, MF_SITE_ABI 23)". The check reuses `run_cmp_sat`, the existing
     normal-form detector beside gate.c's `cl_run` (CL_UNSAT). It adds no second detector. It is documented where
     kit input refusals are documented, in memfn.h:
     - the pspans paragraph: "every byte inside its mask: a byte outside it is refused, D187";
     - `mf_term.run`'s Q-G2-13 note: "On a presence span (mf_site.pspans) it is REFUSED".
     The refusal is on presence spans only. A rendered term keeps Q-G2-13's ruling (in the vocabulary, never
     holds).
  4. **The KITMASS counter is RETIRED**: the trace-only `km_count`/`km_print` (presence.c), reach_equal.py's sum
     (the file is byte-identical to its pre-sp1bfix form) and trace_format.md's entry (now a one-paragraph
     retirement note). The refusal covers the only cube source that reached `kit_mass` (presence runs). The other
     source, translate, now prices sets, so no path is left uncovered.
  5. No cube detector was added. The one cube derivation that remains is `run_bytes`/`shape`, which predates 1c. It
     builds the RUN term's run/mask from the plan's sets for the renderer. D187 names `pcrec_cube_of` as the one
     detector at the kit split; that step is not built.
- **Census** (`tests/memfn/decider_census.tsv`, `.py`):
  - `window.c kit_run_member` is in (T-VERIFY,TIE).
  - The parts `translate:run-rank` and `kit_pres_picks:run-scan` are out.
  - MEMBER_COUNT 51 -> 50.
  - The presence.c plant is re-aimed from `c < sm` (gone) to the run-window loop's `wm < wl`, and the docstring now
    says which loop each plant copies.
  - Backstop: 37 hits, 0 outside a member; both plants and the prototype plant are red.
- **Golden test** `tests/memfn/mass_check.c`:
  - The cube positions are rewritten as sets, with the same literals.
  - New groups: RUN (kit_run_set: case-folded, two-bit-free, exact, outside-mask = EMPTY, NULL mask); MEMBER
    (ties to the higher position, NONE, `exact`, `after` walking the whole order and equal masses); NORMAL (the
    refusal fires on a hand-built non-normal presence run; controls: the same span in normal form and with a NULL
    mask are accepted).
  - `rate3` was added so that `exact` is discriminating.
  - MASS_FLOOR 25 -> 40 (run_finder.sh).
- **Mech**:
  - S1095 (the run-scan tie) is re-anchored onto `kit_run_member`'s tie line in window.c, with the same mutant (a
    tie to the lower/leftmost position: the operands swapped).
  - S1097 and S458 are re-anchored onto the new set-leads line (the same `<` planted `<=`).
  - Each carries a hand-measured DETECTED figure (Validation).
- Docs:
  - memfn.h (the refusal);
  - window_site.md §2.1 (the T_MASS_STRETCH row names `kit_run_member` and its three readers);
  - kit.h's section comments;
  - memfn/src/CLAUDE.md (the presence.c and window.c rows; the sabotage pointers);
  - tests/memfn/CLAUDE.md (mass_check.c's row; 11,966 B, under 12 KB);
  - memfn/docs/trace_format.md;
  - memfn/docs/journal.md (one entry).

Commits (oldest first):

| commit | what |
|---|---|
| f2c258718 | code, test, mech anchors |
| 439c263c8 | census, memfn.h, TIE row, CLAUDE rows |
| f2032e7f0 | journal |
| 95d3e96c7 | hand-measured figures |
| (this report's commit) | the report |

**Stage-1 statements.**

- **No emitted-byte mover**, by construction: the same sums over the same member bytes (a normal cube's
  enumeration and its `(x & mask) == run` set are the same bytes, and pcrec states only normal runs, facts_derive.h
  "CANONICAL"). The orders are the same strict total order. The spot check reads 1760/1760 identical (below).
- **MF_CLASS_V unchanged** (7): no finder row added or removed.
- **MF_SITE_ABI 22 -> 23** (RULED by the kit manager: the refusal is a meaning change; no layout move): see Design
  deviations 1.
- **No pcrec abi change.**
- **No docs/spec hunk**: `git grep` over docs/spec for `kit_mass|kit_pos|kit_run|run_member|pspans|presence span|
  kit_presence_check|KITMASS` finds nothing. docs/spec names no kit input refusal, and no caller-visible name or
  behaviour changed: pcrec never states a non-normal presence run, so the new refusal is unreachable from any
  pattern. The kit contract doc that names refusals is memfn.h, updated.

## Readers (by grep)

`git grep` at HEAD over the whole tree, excluding worktrees/, the build dirs, docs/dev/lanes/ and docs/dev/reviews/
(review evidence):

| deleted name / text | readers | disposition |
|---|---|---|
| `kit_pos` (type), `.t`/`.mask` fields, the cube path | presence.c (kit_mass, run_pos, 5 call sites), window.c (6 call sites), kit.h, tests/memfn/mass_check.c | all moved to set positions; the type is deleted; 0 hits at HEAD |
| `run_pos` (presence.c) | presence.c only | replaced by `kit_run_set` / `run_at`; 0 hits |
| `km_count`/`km_print`, `MFTRACE KITMASS`, `nonnormal-cubes` | presence.c; tests/memfn/reach_equal.py; memfn/docs/trace_format.md; jobs 372/382 (scratch) | code and sum deleted; trace_format.md carries the retirement note; the reach job no longer declares the line. memfn/docs/journal.md :3155 and responses.md :3129 are append-only history, kept |
| translate's `uint8_t cube[32]` and its insertion sort | window.c only | deleted |
| P3's `c < sm` loop, `out->run_scan = (int16_t)scan;` | presence.c; decider_census.tsv (part `run-scan`), decider_census.py (plant anchor); roadmap §5 R24's recipe | census part removed, plant re-aimed; R24 recipe is main's (Ratchet); span_pick.md :154 names it as design record, kept |
| `p->rank_ppm[j - 1] > c` / `p->rank_pos[j] = (uint16_t)i;` | window.c; decider_census.tsv (part `run-rank`); roadmap §5 R24 | census part removed; R24 main's |
| run_member's own mass loop | window.c | now asks `kit_run_member` |
| compose.c `term_prove`'s inline run-set loop | compose.c only | calls `kit_run_set` |
| mech anchors on deleted text | `python3 -I scripts/m6read_check_sab_anchors.py`: STALE 3 (S1095, S1097, S458) | re-anchored (above), now `all anchors resolve` (1102 rows, 1143 sites) |
| `run_member` (other readers) | memfn/tests/g2/g2_win_*.c (the reply field `run_member` and G2's own reference oracle), src/gen/emit_dfa.c `req_run_member` (reads the reply field) | not readers of the function: the reply field is unchanged; G2's reference is an independent oracle, kept |
| `cube_mass`, `uniform_mass` in src/core/findings.c, S461 | pcrec's own copies | KEPT (D157) |

## Ratchet

Recipes: roadmap §5 (docs/design/stream/roadmap.md) as written at 7b671bc2c, with R22/R23 restated 2026-11-04.
They are in `$PCREC_TMPDIR/scratch/memfn/sp1c/ratchet.sh`, plus a restated R24 that names the new function:

    == base 7b671bc2c
    R20=3 R21=1 R22=0 R23=0 R24=2 R25=1 R26=0 R27=0 total=7
    R24-restated=2 (kit_run_member 0, rank-loop 1, p3-scan 1, run_member-own-mass 1)
    == HEAD
    R20=3 R21=1 R22=0 R23=0 R24=0 R25=1 R26=0 R27=0 total=5
    R24-restated=0 (kit_run_member 1, rank-loop 0, p3-scan 0, run_member-own-mass 0)

- **7 -> 5**: R24 2 -> 0 (-2), the design's "-2 only if translate's rank is derived from run_member and its loop
  goes". R25 is unchanged (1). R22 stays 0 (no wrapper was added), and R23 stays 0.
- **For main**: roadmap §5's R24 recipe is blind in the same way R22's was. It greps three literal lines, so it
  cannot see `kit_run_member` or a regrown spelling under another name. The proposed restatement is the one above:
  spellings among `^kit_member kit_run_member\(` in window.c, translate's own rank line, P3's own scan line, and a
  `run_member` that prices its own positions (a `kit_mass(` inside its body), minus 1. It reads 2 at base and 0 at
  HEAD, so the delta is the same under both recipes.

## Validation

All light, in the lane, on the dev box. The box was free (no queue job ran meanwhile). The heavy loops ran under
`scripts/boxlock run` (labels sp1c-spot, -handmeasure, -reachsmoke, -g2).

| check | file / command run | result |
|---|---|---|
| build | `make -j16` | clean, no warnings |
| strict | `make strict` | rc 0 ("whole tree compiles clean with -Werror -Wshadow") |
| census | `make test-memfn-rows` (run_rows.sh + decider_census.py) | rc 0: 213/0 and 56/0; backstop 37 hits (floor 30), 0 outside a member; plants window.c 2 stray, presence.c 1 stray, prototype 1 error (all red) |
| finder + golden | `make test-memfn-finder` (tests/memfn/run_finder.sh; parts incl. `mass`, `presence`, `proof`) | rc 0: 1975 passed 0 failed; `mass checks passed: 40`, `ok mass: 40 cases passed >= floor 40`; presence 44/0 |
| link / R-28 | `make test-memfn-link` | rc 0 |
| G2 quick | `make test-memfn-g2` | see the G2 line under STATE AT HANDOFF (run last) |
| golden plants | `scratch/memfn/sp1c/plant.py`: a scratch copy of memfn/src with ONE edit each, mass_check.c built against it; the tree is never edited | cube-enumeration set (`(b & mask) == (run & mask)`): RED 2; tie to LOWER: RED 3; `after` ignored: RED 2; `exact` ignored: RED 1 (green before `rate3`, so `rate3` was added); refusal removed: RED 1; 1b's plants re-run on set-only kit_mass: set-shaped RED 6, NONE per position RED 2, cap ignored RED 4 |
| byte identity spot | `scratch/memfn/sp1c/spot.py`: frozen base build (git archive 7b671bc2c) vs HEAD's build/pcrec (code of f2c258718 = HEAD's code), 440 patterns (bench 392, job 588's 24, zzzzzzz~J, 23 sp1c extras: `(?i)abc`, `(?i)zzzzzzz~J`, `[aA][bB]cdefghijk`, multi-member sets, ...) x arms default, `-e utf8` (the NONE row), `--engine=vm`, `-fmemfn-simd`; rc + stderr + .c + .h | **1760 of 1760 identical** (103 refused identically on both sides) |
| reach smoke | `tests/memfn/reach_equal.py --limit 300`, base vs HEAD MF_TRACE builds, the four patterns files, arms default / `-e utf8` / `--engine=vm` / `-fmemfn-simd` / `--memfn=no-pres-set-lead` | `reach_equal: LIMITED rc=0 keys=150 differ=0`; no gone rows (a smoke run, not the verdict) |
| hand-measured re-anchors | `scratch/memfn/sp1c/handmeasure.sh`: git archive of 439c263c8, the row's own replace (tests/mech/lib/replace.py), build, the arm's own command | S1095 candoracle **28fail/150pass DETECTED**; S1097 candoracle **16fail/149pass DETECTED** (clean 0fail/178pass); S458 prechecks **3fail/392pass DETECTED** (clean 0fail/395pass) |
| anchors | `python3 -I scripts/m6read_check_sab_anchors.py` | `all anchors resolve` (was STALE ANCHORS: 3) |
| mech fields | `VALIDATE_ONLY=1 tests/mech/run_sabotage_matrix.sh` over the 54 gate rows | 54 definitions valid |

Not run here (owed to the gates): make test, the full identity sweep, full reach equality and mech for real.

## Gate jobs

Prepared, NOT queued, in `$PCREC_TMPDIR/scratch/memfn/sp1c/jobs/`. They were copied from sp1bfix's:

- keys `kit-sp1c-*`, `TREE=worktrees/sp1c`, `BASE=7b671bc2c`;
- the frozen base builds `scratch/memfn/sp1c/ref/build/pcrec` (plain) and `scratch/memfn/sp1c/ref-mftrace/pcrec`
  (MF_TRACE), built from `git archive 7b671bc2c`;
- the patterns: bench list, `p588.txt`, `pzzz.txt` and sp1c's `pextra.txt` (440, checked by `check_inputs`).

**Every job's `--dry-run` exits 0**, and each was ACCEPTED by `PCREC_BOXQUEUE_DIR=scratch/memfn/sp1c/bqtest
scripts/boxqueue add --no-start FILE` (a scratch queue; all 10 are in its `pending/` with their declared expects).
They chain with `after` in this order:

| job | what | est / cap |
|---|---|---|
| 380-kit-sp1c-strict | `make -j16; make strict` | 240 / 1200 s |
| 381-kit-sp1c-memfn | test-memfn-rows, -finder, -link, -g2, -arms, -stamps, -deleg, -manifest, test-findings, test-registry | 1100 / 2700 s |
| 382-kit-sp1c-reach | HEAD MF_TRACE build; reach_equal.py vs base, corpus + 4 files, 18 arms (default, vm, -fmemfn-simd, -e utf8, 12 kit denies, `--analysis weblog` alone and with -e utf8); NO `--gone`; the KITMASS `nonnormal-cubes` expect DROPPED (the counter is retired) | 1250 / 3600 s |
| 383/384/385-kit-sp1c-ident1..3 | emit_sweep's 67 declared identity arms at 7b671bc2c + 2 analysis arms (C streams only), 23 per shard, `--ref-bin` the frozen base | 2450 each, run-total 7350 / 3600 s |
| 386-kit-sp1c-test | `make test` ALONE via `scripts/perfrun --label sp1c` | 1800 / 3300 s |
| 387/388/389-kit-sp1c-mech..mech3 | 54 rows FOR REAL, 18 per shard; S917, S919 DECLARED UNREACHED (shard 1 trailer `unreached: 2`) | 1900 each, run-total 5700 / 3600 s |

**Mech row list, derived two ways.**

- (A) Every row whose `SAB_FILE` is a file 1c edits:
  - presence.c, 10 rows: S270 S286 S288 S317 S458 S1096 S1097 S1098 S1099 S1856;
  - window.c, 6 rows: S1094 S1095 S1415 S1416 S1417 S1419;
  - compose.c, 19 rows: S570 S681 S682 S688 S846 S847 S848 S921 S1018 S1081 S1083 S1084 S1089 S1106 S1107 S1109
    S1221 S1224 S1548. 1c edits `term_prove` and `kit_presence_check` there.
  - memfn.h, 1 row: S526 (a comment-only edit, included by the rule);
  - kit.h: none.
- (B) Every row of the `memfnfinder` arm, which runs run_finder.sh (changed: part `mass`, floor 40): 31 rows.

The union is 54. The edited test files (decider_census.*, mass_check.c, reach_equal.py) add no row, because no mech
arm runs the census or reach_equal. S917 and S919 are `SAB_EXPECT=UNREACHED` (LOCKDOWN, unchanged by 1c). S570
(codegen) and S688 (harness) are put in different shards. No `--list-*` row moves, so no dumps delta is declared
on any identity arm.

## Design deviations

1. (RULED, not a deviation) **MF_SITE_ABI 22 -> 23** for the new presence-span refusal: the kit manager's ruling
   (2026-11-04), on the 14/20 precedent that a refusal narrowing what the seam may state is a meaning change; the
   brief's "should not move" was a prediction. History entry in memfn.h ("a pspans RUN byte outside its mask is
   REFUSED, D187; no layout move; no MF_VOCAB/MF_CLASS_V move; no pcrec byte moved"), memfn/include/CLAUDE.md's
   carried number, and the refusal text cites `D187, MF_SITE_ABI 23` like its siblings (14, 17, 18). Readers by
   grep: the `#define` (memfn.h :39) and include/CLAUDE.md are the only readers of the CURRENT number; every other
   hit of "MF_SITE_ABI 22" (window_contract.md :533/:606, e1_object_check.py, S1856, arm_fixtures.c, finder_check.py,
   prov_check.c, run_finder.sh, the journal) cites unit 1g's own event and stays true. Code reads the symbol only
   (`s->abi = MF_SITE_ABI` in formhash.c, window.c, src/gen/memfn_sites.c; the checks in compose.c, presence.c,
   window.c), and MF_SITE_ABI reaches no emitted text (1g's 21 -> 22 was byte-identical), so no pcrec byte moves.
2. **The refusal is on presence spans only**, not every RUN term. Q-G2-13 rules that a non-normal byte on a
   rendered term is IN the vocabulary (it never holds, rendered constant false), and G2 generates such terms. The
   set-only mass reads presence runs and the window family's sets, and neither is a rendered term. So the boundary
   check sits where D187's fact is needed and leaves Q-G2-13's ruling standing.
3. **"rank_pos[0] asserted against run_member"** is held by construction rather than by a runtime assertion: the
   ranking IS the member function asked repeatedly (the -2 form). The member is over the ranked term's own
   positions. It is the same function as window.c's `run_member`, but a different position list: the plan's
   scanned RUN term, not R's span. So an equality with `d->member` was not asserted, because it is a different
   claim that would need its own witness.
4. **kit_mass's signature changed** (consecutive sets instead of a `kit_pos` array). This is the set-only form D187
   asks for, and it removes R10's repetition without a wrapper. It is kit-internal (kit.h), so no seam moves.
5. **term_prove (compose.c) joins `kit_run_set`**. The brief named run positions, the landmark and translate. This
   is the same conversion, spelled identically, and the review's contract lens proposed exactly that general form
   ("ONE position-to-member-set function that kit_mass, term_prove, the landmark and translate all read").
6. **One extra patterns file** (`pextra.txt`, 23 patterns) feeds the spot check and every gate job beside the
   design's three inputs, for coverage of case-folded and masked runs and multi-member sets.
7. The DELIVER file `docs/dev/lanes/sp1c_deliver.txt` was written BY THE LANE, as the brief authorised.

## Charter vs committed

| promise (span_pick rev 5.2 1c row, Part B, the brief) | artifact |
|---|---|
| U2: P3's `run_scan` asks `run_member` (its own spelling goes) | presence.c `kit_run_member(rate, run_at, t, n, 0, NULL)`; the `c < sm` loop deleted; S1095 re-anchored, DETECTED 28 |
| translate's run rank reads T_MASS_STRETCH | derived from `kit_run_member`, whose ties read T_MASS_STRETCH via `kit_tie_takes`; golden MEMBER cases; tie plant RED |
| `rank_pos[0]` asserted against `run_member` | by construction (Design deviations 3) |
| U6 not here; its ratchet row kept | the landmark shadow untouched except its set conversion; R25 1 -> 1 |
| R24 -1, or -2 only if derived, byte-identical and clearly simpler | -2 (Ratchet; the reasons are in What changed) |
| R25 unchanged; counter output shown | Ratchet |
| B(1) set-only kit_mass; cubes converted where built; `kit_pos` cube fields and the cube path deleted; R7 gone | presence.c/kit.h; `kit_run_set`; 0 `kit_pos` hits |
| B(2) normal form checked in `kit_presence_check`, spelled and documented like the other refusals; a test that fires on a hand-built non-normal run and never on pcrec's own | compose.c (via `run_cmp_sat`); memfn.h pspans + Q-G2-13 notes; mass_check NORMAL (3 cases, removal plant RED); "never on pcrec's": spot 1760/1760 identical rc, reach smoke equal fail sets, finder's pcrec-level presence part 44/0; **the full population is OWED** to gates 381-386 |
| B(3) retire the landmark set rebuild and translate's `cube[]`, byte-identical | both gone (`kit_run_set`, `w->set`) |
| B(4) KITMASS counter retired or kept, say which | retired (code, reach_equal sum, trace_format; job 382 drops the expect) |
| B(5) R10 one-position wrapper only if no parallel mechanism | not needed: the set signature removed the repetition |
| no second cube detector | none added (`run_cmp_sat` reused; `run_bytes` pre-existing) |
| zero movers on every arm, no pcrec abi, no spec hunk unless caller-visible | spot 1760/1760; reach smoke 0; no abi; spec grep empty; **the full witness is OWED**: jobs 382-385 |
| state MF_CLASS_V / MF_SITE_ABI | MF_CLASS_V 7 unchanged; MF_SITE_ABI 22 -> 23 as RULED (Design deviations 1), readers re-pinned by grep |
| readers by grep, incl. the mech anchor checker, with re-anchors hand-measured | Readers; S1095/S1097/S458 figures in SAB_DOC_FIGURE |
| CLAUDE.md files, kit journal, census map/ratchet | memfn/src + tests/memfn CLAUDE.md; journal entry; census 50; Ratchet |
| each new check RED under a plant then reverted | Validation, golden plants (scratch copies; the tree never edited) |
| gate jobs prepared, dry-run rc 0, accepted by boxqueue add's checks in a scratch queue, mech derivation stated | Gate jobs |
| roadmap R24 recipe restated | **OWED, main** (proposal above) |
| responses-ledger line | **OWED, kit session** (single writer) |
| the gates' verdicts | **OWED**: the kit manager's queue run of jobs 380-389 |

## STATE AT HANDOFF

STATE: delivered. The gate jobs are prepared and NOT queued. Code is complete for unit 1c and the D187 set-only step
at the branch head. Light validation is green, with numbers above. G2 quick: `make test-memfn-g2` was launched last
under `boxlock run --label sp1c-g2`, and its log is `$PCREC_TMPDIR/scratch/memfn/sp1c/sec.test-memfn-g2.log`. Its
verdict is in the handback message; if it had not finished, the gate's job 381 runs it anyway.

OWED:
- the gate run (jobs 380-389 in `scratch/memfn/sp1c/jobs/`, keys kit-sp1c-strict, -memfn, -reach, -ident1..3,
  -test, -mech..mech3), which the manager queues;
- main's restatement of roadmap §5 R24;
- the kit session's responses line.

No rulings file was named in the brief. A fresh agent resumes from the job results. All green means 1c's witness is
complete. Any byte moved on an identity arm, or any reach difference, is a STOP.
