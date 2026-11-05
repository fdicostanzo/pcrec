# sp1d — span_pick stage 1, unit 1d: the planning core (lane sp1d, opus)

Branch `lane/memfn-sp1d`, cut from main `daf6f002b` (units 1a, 1f, 1g, 1b, 1c landed). Design of record:
docs/design/memfn/span_pick.md rev 5.2 (§Staging, the 1d row and its test row; §What stage 1 deletes U1/N1,
U10/N6; dispositions R4/R8, C1, C2, C7; D186 + addenda, D187). Build go: Frank's conditional approval of
2026-11-02, confirmed by main's stage-1 GO.

**No-mover, as stage 1 requires.** No pcrec abi change. No `docs/spec/` hunk: nothing caller-visible moves.
Proof by grep: no `docs/spec/`, `lib/` or `memfn/include/` file names `kit_pick`, `run_pos_sat`, `cands`,
`mass_domain`, `run_cmp_sat`, `kit_run_member` or the new trace record. `git diff daf6f002b..HEAD --
memfn/include lib docs/spec src cli` is empty. **MF_SITE_ABI 23** and **MF_CLASS_V 7** are unchanged (MF_VOCAB
4): no seam struct changes its layout or meaning. Every new type and function is kit-internal (`kit.h`).

## What changed

By file:

- **memfn/src/window.c**
  - **THE CANDIDATE LIST, one builder `cands`.** It runs C-meet (`merge`), then gives each present position:
    - its meet's SUM mass;
    - `stop_ok`: core and not the full set (A-mass's domain);
    - `stretch`: the T_MASS_STRETCH / T_MASS_SET choice.

    It also gives:
    - the walked offsets (`wf_walk`), with their spans' OWN sets' CAP masses in LISTED order and `scan`
      (`scan_ok`);
    - F0 and its CAP mass;
    - the any_empty, any_stop and any_scan summaries.

    `decide` calls `cands` where it called `merge`. Every Table A row reads the list:
    - A-empty, A-model and A-mass hold on the summaries;
    - `a_model_choose` iterates the walked list (its private enumeration and its `mass[]` pricing are gone);
    - `a_mass_choose` iterates the `stop_ok` positions (its `mass_domain` copy and its per-row `kit_mass` are
      gone).

    `mass_domain` is DELETED. `f0_of`, `walked`, `scan_ok` and `in_stretch` moved into the builder's section,
    and only the builder calls them.
  - **THE PICK's ONE before-relation, `kit_pick_takes` (with the `kit_pick` best-so-far).** It reads "a lesser
    value, or an equal one the TIE row sends its way". All five argmin members ask it:
    - A-mass;
    - A-model;
    - `kit_run_member`, both its pick and its `after` filter (the filter asks the relation with the roles
      swapped, so the walk and the pick share one before-relation);
    - presence's set pick;
    - presence's run window.
  - **T-VERIFY as a step list.**
    - The run member is the list's first applied step, `C-member` (apply `run_member`); `c_plan` no longer
      calls it directly.
    - `C-bound` is an applied step after C-floor and C-yes: it drops each added position whose step set is the
      full set (the verify-YES meet when there is a stop, else the meet the plan reads).
    - C-floor and C-yes now add every present / verify-YES position, and C-bound filters them, where before the
      bound was "applied inside" both.
    - translate's grouping stays a named member (R8): census row `translate:grouping`, unchanged.
  - **The trace (no price).** `trace_cands` writes one `MFTRACE WCAND` per candidate on a define's decision (a
    query writes none).
- **memfn/src/kit.h:** declares `kit_pick`, `KIT_PICK_NONE`, `kit_pick_takes`, `gate_cand`, `gate_trace_cand`
  (with a no-op inline when MF_TRACE is off) and `run_pos_sat`. The TIE comment says every pick asks through
  `kit_pick_takes`. The `run_cmp_sat` comment names the normal form's one spelling and its three askers.
- **memfn/src/presence.c:** P3's set pick and run window ask `kit_pick_takes` (the `best`/`lo` and `wl`/`at`
  pairs are gone).
- **memfn/src/gate.c (F12):** `cl_run`'s CL_UNSAT asks `run_cmp_sat` (its own loop is gone). Adds
  `gate_trace_cand`, the WCAND writer.
- **memfn/src/runcmp.c (F12):** `run_pos_sat(t, j)` is the per-position normal form, and `run_cmp_sat` loops
  over it.
- **memfn/src/generic.c (F12):** the per-byte RUN chain asks `run_pos_sat`.
- **memfn/src/compose.c:** fixes the stale comment "no row reads it before B3a". It now names
  `kit_byte_rate`'s readers.
- **memfn/docs/trace_format.md:** documents the WCAND record, and that T-VERIFY steps write none.
- **tests/memfn/arm_fixtures.c: THE PURITY HARNESS.** `--purity` and `--purity-control` (described below).
- **tests/memfn/run_finder.sh:** the `purity` part, with its floor (287), the plant (RED) and the control
  (reached).
- **tests/memfn/decider_census.tsv/.py:**
  - `cands` and `kit_pick_takes` are in, plus the kit.h prototype as excluded;
  - `mass_domain` is out;
  - the presence parts are re-anchored;
  - BACKSTOP gains `pick_takes(`;
  - the three plants are re-aimed at the pick lines;
  - MEMBER_COUNT 50 -> 52. HIT_FLOOR stays 30 (hits 37).
- **tests/mech/sabotages/S1095, S1096:** re-anchored onto the `kit_pick_takes` lines with the same mutants,
  each hand-measured DETECTED (see Validation).
- **memfn/src/CLAUDE.md, tests/memfn/CLAUDE.md:** updated, and within their size limits.
- **memfn/docs/journal.md:** one entry.

### The purity harness (tests/memfn/arm_fixtures.c)

- **Sites.** Five window sites, each stated as FUNC/RETURN FIND sites:
  - NONE (A-mass, a set position among one-byte ones; the plan pins);
  - PARKED (A-parked);
  - RESEED (A-model / C-model, F0 + 3 walked);
  - PARKED+RESEED (the MARGIN);
  - NONE with a 4-position verify-YES run (the run member).
- **Rate tables.** Each check runs under the NONE table and under a skewed rate table that has ties (g/h,
  b/d).
- **Replies.** Each site's `mf_wdecide` reply on a FRESH art is compared field by field with its reply on one
  art at every point between interleaved `mf_define`s. Three define orders are used: in order, reversed, and
  repeated (each site twice). The header says WHY the defines are interleaved: `nsites`' one writer is
  `mf_define`, and the plan face takes a `const mf_art *`.
- **The sticky-err case.** After a refused define (two NONE alternatives), every later plan call must answer
  -1. That asserts breaker (a) is FENCED.
- **The plant.** `run_finder.sh` builds a copy of memfn/src with one line changed (awk, exact-line match): A-mass
  holds only when `!x->d->art->nsites`. The planted `--purity` goes RED (80 checks failed).
- **The control.** The planted `--purity-control` print (each reply after ONE define of the next site) differs
  from this build's, so the plant is REACHED on the unharnessed fixture.
- **Not reached by the harness sites:** A-empty, and A-floor's floor-only path. The base G2 family and the
  corpus reach them.

### Folded items

- **F12, the normal-form predicate.** It now has ONE spelling: `run_pos_sat` / `run_cmp_sat` in runcmp.c.
  - gate.c `cl_run` asks it; its own loop is gone, and it keeps only the MASKED scan, which is a different
    question.
  - generic.c asks the position form.
  - D187 does not make this moot: D187 refuses a non-normal presence run at `kit_presence_check`, but the
    VMRUN compare and the generic RUN chain still classify arbitrary RUN terms.
- **F13, one home for the kit-wide position primitives.** NOT MOVED, OWED. `kit_mass`, `kit_run_set`,
  `kit_run_member`, `kit_tie_takes`, `wf_ties` and now `kit_pick_takes` stay where they are.
  - window.c still mixes the planning face (phase 1) with the emitting face (phase 2).
  - 1d's builder is window.c-internal, so it is not the natural home. Moving the primitives there would tie
    presence.c to the window family's file.
  - The natural home is the planning face's own file, made at the kit split (manifesto, principle 9).
  - Owner: the kit session. Trigger: the kit's planner/back-end split, or T-PICK (stage 2), whichever comes
    first.
- **The standing question, the five-member argmin family.** Unified on their ONE before-relation,
  `kit_pick_takes`: all five ask it, and so does kit_run_member's `after` filter. Each member keeps its own
  loop, because each enumerates a different candidate source with its own value:
  - A-model: walked offsets, greedy plan cost;
  - A-mass: stop positions, meet SUM mass;
  - the run member: run positions read through `kit_pos_at`, the exact filter, the `after` walk;
  - the set pick: pspans, keyed by member order;
  - the run window: 3-position windows, SUM mass.

  One shared enumerator would need a candidate-reader callback, a new mechanism with no measured need (D77).
  T-PICK's row 1 (stage 2) is where the candidate sources meet. Not in the family: P2/P4, which compare with no
  TIE row, and C-model's exchange sort, which is an ordering, not a pick.
- **R10, a one-position `kit_mass` wrapper.** NOT ADDED. There are 12 one-position calls. A wrapper would drop
  only the literal `1,`; the cap argument (SUM vs CAP) is a real per-call choice, and the call already spells
  it.

## Readers

Found by grep over the tree, excluding `worktrees/`, `build*/`, `docs/dev/lanes/` and `.git`:

| function / text | change | readers (code, tests, mech) | action |
|---|---|---|---|
| `mass_domain` | DELETED | census tsv row; docs/design units_inventory :89, span_pick :364, roadmap R21; reviews (historical) | census row removed; R21 restatement proposed (below); design/review text is historical line cites, left |
| `f0_of`, `walked`, `scan_ok`, `in_stretch` | moved (window.c-internal; only `cands` calls them) | census tsv rows (fn, by name: still found) | none needed |
| `a_model_choose`, `a_mass_choose` | read the list | census rows; `wf_arows[]` | census `retires` text updated |
| `kit_run_member` | body asks `kit_pick_takes` | window.c `run_member`, translate's ranking; presence.c P3 scan; mech S1095 | S1095 re-anchored, hand-measured |
| presence run window / set pick | ask `kit_pick_takes` | census parts; mech S1096 | parts re-anchored; S1096 re-anchored, hand-measured |
| `run_cmp_sat` | loops over `run_pos_sat` | gate.c `cl_run`, compose.c `kit_presence_check`, mass_check.c | none needed |
| gate.c `cl_run` / generic.c RUN chain | respelled | mech S919 (gate.c; UNREACHED, unchanged), generic.c rows S214 S616 S618 S619 S676 S677 S1225 (anchors resolve) | in gate jobs |
| `c_plan`'s direct `run_member` call; C-bound "applied inside" | now steps | `wf_crows[]` only | comment updated |
| compose.c :882 comment | rewritten | none | — |
| `MFTRACE` readers | new kind WCAND | rows_check.py, finder_check.py, reach_equal.py, arm_fixtures.c: each filters by kind | none (finder 2266/0 and reach smoke 0 differ confirm) |

`python3 -I scripts/m6read_check_sab_anchors.py`: `sabotages checked: 1102 (1143 anchor sites)`, `all anchors
resolve`. Before the re-anchor, S1095 and S1096 were stale. They were re-anchored with the same mutants:
- S1095: a tie to the leftmost position, a strict compare;
- S1096: `<=`, a tie to the rightmost window.

## Ratchet

These are roadmap §5's R20-R27 recipes as written. The script is
`/var/tmp/pcrec-pcrec/scratch/memfn/sp1d/ratchet.sh`, sp1c's, with a restated R21 added:

```
BASE daf6f002b:
R20=3 R21=1 R22=0 R23=0 R24=0 R25=1 R26=0 R27=0 total=5
R24-restated=0 (kit_run_member 1, rank-loop 0, p3-scan 0, run_member-own-mass 0)
R21-restated=1 (a_model_choose 1, a_mass_choose 1, cands 0)
HEAD:
R20=3 R21=1 R22=0 R23=0 R24=0 R25=1 R26=0 R27=0 total=5
R24-restated=0 (kit_run_member 1, rank-loop 0, p3-scan 0, run_member-own-mass 0)
R21-restated=0 (a_model_choose 0, a_mass_choose 0, cands 1)
```

**R21 needs a restatement (main's to file).** The written recipe counts the DEFINITIONS of `a_model_choose`
and `a_mass_choose`. 1d keeps both choosers, which now read the one list, so the recipe still reads 1 and
cannot see the private copies go. Proposed recipe: "among the Table A choosers `a_model_choose`,
`a_mass_choose` and the candidate builder `cands` in `memfn/src/window.c`, those whose BODY tests a position's
domain itself (a `scan_ok(`, `mass_domain(` or `full(` call), minus 1". That reads 1 at daf6f002b and 0 at
HEAD, the design's "R21 -1". With the restatement, the stage-1 kit-row total is 5 -> 4.

## Validation

All runs are light, on this box, niced, with no box lock: job 300, main's full suite, holds the box.

| check | result |
|---|---|
| `make` | clean, no warnings |
| `make strict` | `strict: whole tree compiles clean with -Werror -Wshadow` |
| `make test-memfn-rows` | rows `checks passed: 213, failed: 0`; decider census `checks passed: 59, failed: 0` (backstop hits 37 >= floor 30, 0 outside a member; the three plants each turn it red; the prototype plant red) |
| `tests/memfn/run_finder.sh` | `checks passed: 2266`, `checks failed: 0`, including `mass 41 >= floor 41` and `purity: 287 checks passed >= floor 287`; `purity plant: RED (80 checks failed)`; `purity control: the plant is reached` |
| purity harness | green 287/0; plant RED; control reached (rows above) |
| mass_check | 41/0 (inside run_finder) |
| G2 window family (`memfn/tests/run_g2_win.sh`, on the first code commit) | `checks passed: 10444`, `checks failed: 0` (ASan+UBSan driver 5200/0; W1 ref-defects 2-5 red) |
| `make test-memfn-finder`, `-arms`, `-g2` (once, after the last code commit) | all on e27421362, the last code commit: `test-memfn-finder` rc 0 (115 s; `checks passed: 2266`, `failed: 0`); `test-memfn-arms` rc 0 (`checks passed: 374`, `failed: 0`); `test-memfn-g2` rc 0 (467 s under job 300's load; `checks passed: 70358652`, `checks failed: 0`) |
| byte identity, single patterns (`spot.py`: rc, stderr, .c, .h) | 298 patterns (bench 250 of 392 + job 588's 24 + zzzzzzz~J + sp1c's 23 extra) x 6 arms (default, `-e utf8`, `--engine=vm`, `-fmemfn-simd`, `--analysis weblog`, `-e utf8 --analysis weblog`): `cases=1788 same=1788 differ=0 (both-refused 62)` |
| byte identity, multi-target files (`multi.py`: one invocation per .rxt source of 5 targets; rc, stderr, every output file) | the 405 patterns that HEAD compiles alone, in 81 files x 5 arms (default, utf8, vm, simd, `--analysis weblog`): `same=405 differ=0 (both-refused 7)` |
| REACH equality smoke (`reach_equal.py --limit 300`, base MF_TRACE vs HEAD MF_TRACE) | 5 arms (default, utf8, vm, simd, `no-pres-set-lead`): every arm `rows base 30 head 30, patterns differing 0`; `reach_equal: LIMITED rc=0 keys=150 differ=0` (a smoke, not the verdict) |
| trace streams | 200 patterns: every MFTRACE record except WCAND equal base vs HEAD (200/200); 1,133 WCAND lines at HEAD |
| hand-measured mech | S1095 `candoracle:31fail/151pass` DETECTED; S1096 `candoracle:5fail/177pass` DETECTED; clean `0fail/182pass` (git archive of 9eb7d7837, the row's own replace.py, run_cand_oracle.sh) |
| anchor checker | `all anchors resolve` |
| mech fields | `VALIDATE_ONLY=1` over the 64 gate rows: `64 definition(s) valid, 0 rows measured` (fields only, not a mech run) |

The spot checks total about 3.8k compile pairs, a little over the brief's ~3k. They ran niced at -j4 beside
job 300.

My first spot attempt used `emit_sweep.py --limit 150`. emit_sweep re-execs under the box lock above its cap,
so it sat WAITING on job 300. I killed it by PID with `scripts/safekill` (it had measured nothing) and replaced
it with direct compiles. The ident gate jobs below are the real sweep.

## Gate jobs

The jobs are prepared in `/var/tmp/pcrec-pcrec/scratch/memfn/sp1d/jobs/`, copied from sp1cfix's.
- Keys are `kit-sp1d-*`, TREE is worktrees/sp1d, and BASE is daf6f002b.
- The frozen base builds are under my scratch: `ref/build/pcrec` and `ref-mftrace/pcrec` (a git archive of
  daf6f002b).
- No not-before lines remain.
- Every `--dry-run` exits 0.
- All ten were accepted by a SCRATCH queue (`PCREC_BOXQUEUE_DIR=.../sp1d/bqtest boxqueue add --no-start`) and
  sit in `bqtest/pending`. **None is queued for real.**

| job | what | chain |
|---|---|---|
| 400-kit-sp1d-strict | make strict | first |
| 401-kit-sp1d-memfn | test-memfn-rows, -finder (incl. purity), -link, -g2, -arms, -stamps, -deleg, -manifest, test-findings, test-registry | after 400 |
| 402-kit-sp1d-reach | REACH EQUALITY, 18 arms (default, vm, simd, utf8, 12 kit denies, `--analysis weblog` alone and under utf8); no declared gone set (1d deletes no table row) | after 401 |
| 403/404/405-kit-sp1d-ident1..3 | byte identity: the 67 declared ident arms at daf6f002b + 2 analysis arms, in 3 shards of 23 | 402 -> 403 -> 404 -> 405 |
| 406-kit-sp1d-test | make test via scripts/perfrun | after 405 |
| 407/408/409-kit-sp1d-mech..3 | 64 mech rows, 22/21/21; shard 1 declares `unreached: 2` (S917, S919) | after 406, in order |

How the mech rows were derived:

- **(A) every row whose `SAB_FILE` is a file 1d edits:**
  - window.c 6;
  - presence.c 10;
  - gate.c 1;
  - runcmp.c 7;
  - generic.c 7;
  - compose.c 19 (a comment-only edit, kept for sp1c's memfn.h precedent);
  - kit.h none.
- **(B) every row of the `memfnfinder` arm** (it runs run_finder.sh, which 1d changes): 31.

The union is 64, listed in `mech.sh`'s header.

UNREACHED, declared:
- **S917 and S919** (SAB_EXPECT=UNREACHED, LOCKDOWN, unchanged).
- **The memfnarms rows outside the union are NOT added.** 1d adds two modes to arm_fixtures.c and changes none
  of the modes `run_arm_pins.sh` runs; its section `test-memfn-arms` is in job 401.
- **The census and trace_format edits** feed no mech arm.

## Seam notes

This is the state that would NOT survive a text round trip between the planning face (`mf_wdecide`, phase 1)
and the emitting face (`wf_prepare`, phase 2):

- **The emitting face does not read the planning face's reply. It re-decides.** `wf_prepare` runs `decide`
  again (non-quiet) over the same site and art. `mf_wreply` is all values (alt, stop, stop_set, plan offsets,
  plan_term, run member and stretch, path), and it WOULD round-trip. But nothing consumes it across the seam
  today, so the round trip is not exercised.
- **Pointers inside the decision (`wf_dec`):**
  - `const mf_art *art`;
  - each alternative's `const mf_walt *alt`, which is the site's own;
  - `const uint32_t *rate`, the handed rates' payload;
  - the site's span arrays that `plan_term` indexes;
  - kit_run_member's `src`/`at` reader.

  A text plan would carry offsets and span indices instead. The candidate list's picks already leave as offsets
  (`kit_pick.key`), not list indices.
- **`art->nsites + 1`,** the site label the trace and the routing see (breaker (b)): a define-time count, not a
  site fact.
- **First-use-wins text:**
  - helpers declared once per art (runcmp's word-width helpers, `run_cmp_prepare`);
  - the offset-skip function and table names, emitted on first use;
  - `mf_flush_helpers`' pending list.

  The second site that needs one gets a reference, not a definition. That depends on emission ORDER, not on the
  plan.
- **The sticky `art->err`** (breaker (a), FENCED): a refused define changes every later plan answer to -1.
- **Process-global reach counters** (breaker (c), trace builds only; quiet asks count no reach).
- **`art->consulted`** (breaker (d), future).

## Design deviations

1. **A-model's domain is not "candidates after C-meet".** The design's one builder prices candidates after
   C-meet. A-model reads the walked spans' OWN sets, in LISTED order, at CAP mass. That is byte-identical only
   because the builder carries the walked list beside the meet positions.
   - G2's reference (`g2_win_ref.c` `g2w_decide`, checked field by field) reads own sets in listing order.
   - G2's FAM_PAIR and FAM_RANDOM families generate R spans that overlap walked offsets, plus unordered and
     duplicated one-position spans, so meet sets and the exchange sort's order would move G2-visible decisions.
   - On pcrec's population, merged == own on 470/470 walked spans, but G2's space is wider.

   The ONE builder holds both lists. Making A-model read the meet is a G2-reference change and a ruled event,
   not a stage-1 step.
2. **The T-VERIFY trace.** "The trace" (every candidate, the rows walked, the incumbent, the deciding row) is
   met for KEY: WCAND, plus wfA/wfM's existing SEL/ROW/END records. The T-VERIFY steps write no record of
   their own, because every holding step applies and the plan's shape is WPATH's `path`. A per-step record is
   cheap if the kit wants it.
3. **F13 is not done.** It is OWED, with owner and trigger above.
4. **`kit_pick_takes` lives in window.c** beside `kit_tie_takes` (the TIE table's file), not in a T-PICK file.
   T-PICK does not exist as a file yet; this follows the same trigger as F13.
5. **The spot check ran about 3.8k compile pairs**, against the brief's "≤ ~3k".

## Charter vs committed

| promise | artifact |
|---|---|
| ONE candidate builder | window.c `cands`; census row `cands` |
| KEY/M/TIE as the default | Table A rows read `cands`; M unchanged; TIE via `kit_tie_takes` inside `kit_pick_takes` |
| T-VERIFY as a step list with C-bound and the run member | `wf_crows[]`: C-member (apply `run_member`), C-bound (apply `c_bound`); `c_plan` walks the list only |
| translate's grouping a named member (R8) | census `translate:grouping`, unchanged |
| trace without prices (U1 two KEY rows, U10 Table C + ofsskip's legacy plan, N1, N6) | A-model and A-mass stay two KEY rows (wfA); WCAND; trace_format.md; Table C + translate unchanged in shape; no price traced |
| PURITY per the breaker table; (a) FENCED, code unchanged | purity harness sticky-err case; compose.c's `art->err` untouched |
| delete `a_model_choose`'s private enumeration and `mass_domain`'s copy (R21 -1) | window.c; ratchet R21-restated 1 -> 0; R21 restatement OWED to main (manager files it in roadmap §5) |
| compose.c stale comment | compose.c `mf_art_begin` |
| REACH EQUALITY | smoke 0 differ; full: gate job 402 (OWED: main queues it after job 300's verdict) |
| PURITY HARNESS: interleaved, in order/reversed/repeated, plant RED, control reached, sticky-err -1 | arm_fixtures.c `--purity`/`--purity-control`; run_finder.sh `purity` part |
| F12 | runcmp.c `run_pos_sat`; gate.c, generic.c |
| F13 | OWED: kit session, at the planner/back-end split or T-PICK |
| standing question (five-member argmin) | `kit_pick_takes`, asked by all five; members left and why: "Folded items" |
| R10 | not added (counted: 12 calls, no repetition removed) |
| Seam notes | section above |
| readers by grep, mech anchors, anchor checker clean | "Readers"; S1095/S1096 re-anchored and hand-measured |
| CLAUDE.md files, kit journal, census map/ratchet | memfn/src/CLAUDE.md, tests/memfn/CLAUDE.md, memfn/docs/journal.md, decider_census.*; ratchet output above |
| validation (light) | "Validation" |
| gate jobs prepared, scratch queue only | "Gate jobs" |
| byte-identity on every arm in the gates (ident x3, mech, make test) | OWED: main queues jobs 400-409 after job 300's verdict |

## STATE AT HANDOFF

- `lane/memfn-sp1d` at the tip named in the handback. The tree is clean apart from the dirty-ok paths.
- Nothing is running. Nothing is queued for real. The scratch queue `sp1d/bqtest` holds the ten verified jobs
  (pending, never started).
- Scratch: `/var/tmp/pcrec-pcrec/scratch/memfn/sp1d/` holds:
  - the frozen base builds, `ref/` and `ref-mftrace/`, which the gate jobs read: keep them until the gates are
    read;
  - `head-mftrace/`;
  - `hm/` (hand-measure trees);
  - `spot/`, `multi/`;
  - `jobs/`, `bqtest/`.
