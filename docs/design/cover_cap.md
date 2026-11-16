# cover_cap.md — the `cover` route's exact stretch: read from the anchored machine, bounded by that machine's own state ceiling, no budget; at stage 2 the cover ROUTE gains one per-compile width limit ([COVER-CAP])

Status: stage 1 BUILT (rev 4.1, lanes covs1/covs1f/covs1g, merge fff636eda, abi 108). Stage 2:
PROPOSED, revision 5.1 (lane `covs2e`, 2026-11-15; rev 5 by lane `covs2d`): the STAGE 2
ADDENDUM, §11, design only; the owner's build go covers both stages ("Go on all stages", 14:50).
Rev 5's critic round r13 (`docs/dev/reviews/2026-11-15-r13-covs2d.md`) is applied; the
stage-2 build waits for a short readiness re-check of rev 5.1 and the kit's reply (§11.6).
Plan row: [COVER-CAP] (set S3). Owner criteria: D198. Reviews: round covcap-r2
(`docs/dev/reviews/2026-11-15-r5-covcap-r2.md`, C-1..C-25) and round covcap-r3
(`docs/dev/reviews/2026-11-15-r6-covcap-r3.md`, R-1..R-14) and round covcap-r4
(`docs/dev/reviews/2026-11-15-r7-covcap-r4.md`, FI-1..FI-6, READY-1..READY-5), dispositions ruled by the manager.
Compiler read: worktree at main `ac91d48bb` (no `src/`, `lib/`, `cli/` change since rev 3's
`4ccd97ca7`). Every "today" number below carries its command;
`$PC` is that worktree's `build/pcrec` and `SF() { $PC -p rx --features all --emit-facts --pattern "$1" | awk -F'\t' '$1=="byte"&&$2=="span_facts"{print $7}'; }`.

**REVISION 5.1 (review r13 applied, lane covs2e; design only).** Every FIX-NOW of round r13
(`docs/dev/reviews/2026-11-15-r13-covs2d.md`, DISPOSITIONS RULED) is applied; the by-id map is
`docs/dev/lanes/covs2e_report.md`. Answer- and build-level: the proof comparison covers the
reply's whole counted range, all ones past `k`, a named error on a short range, and a plant of
the opposite error (F1, §11.1 B5, §11.6.3); pcrec's own span writers, `MF_MAX_TERM` and the
by-value class records join the reader list, the last as a fact for the kit (F2, F5); the seam
is three kit bounds and `window_bounds_check` gets its item (F3); §11.1 splits into items that
start before the kit's reply and items that wait for the combined branch (F4); the
lowered-ceiling reference builds pass the new row's `-D`, and both build-time checks are
`_Static_assert` (F14, F18). Checks: the rename's readers and their new values (F6), a kitproof
`W` letter and default-derived witnesses (F7, F13), sabotage witnesses that fail under the
right plant direction, S3223 as the bypass row and a seam-assertion row (F8, F9), mech rows that
copy rewritten code (F10), compile cost as a recorded measurement with one criterion (F11).
Measurement: land once with the measured default, 24-wide and two synthetic long cells added
(F16, F17), a first-match outcome table that agrees with the rule (F19), the noise procedure
(F20), B's axes named (F15). Rulings: the per-compile VALUED option `--window-search-width=N`
is designed (F21, manager ruling; §11.2.1) and the test-only lever dropped; the dial is live
(F22); every stale sentence of sections 0-10 now says one thing, the route-not-stretch reading
marked LEAN, OWNER QUESTION OPEN (F23, §9 Q7); D198 (e)'s amendment stated (F24); the EMITTED-2
remedy quoted and moved to an owner question (F25, §9 Q8); unit `positions`, name
`WINDOW_SEARCH` (F26); the [SIZE-KNEE] family and unlocks (F27); `--list-limits`, the `limits.md`
section 3.12 (new) anchor, the `.text` command, the PREMISE grep (F28-F31). §11.5 re-issued whole.

**REVISION 4 (round covcap-r3 applied; small).** The round held the core reading (the
stretch read from the anchored machine matched libpcre2 on every probe). It found that rev
3's new limit `PCREC_MAX_EXACT_SPAN` (4096) could never bind: the walk reads the anchored
machine, which exists only under the EXISTING ceiling `PCREC_ANCHORED_MAX_STATES` (4096
states), so `k <= 4095` first (R-1). Rev 4 DELETES that limit, rev 3's outcome 4, its
`over-max` detail, plant (e) and the `a{4097}` witness; rev 3's "no cliff" was FALSE (§9
Q2). The rest is text: the walk stops at `min(L, first accept)` (R-2), the listing's record
and where it states a stretch (R-3, R-4), the controls table (R-5), the delivery bar (R-6,
R-8..R-13). R-7 is moot; R-14 NOTED (§3.3). Rev 3 (lane `covcap4`: the anchored-machine
reading, the slice deleted) is in git; findings by id: `docs/dev/lanes/covcap5_report.md`.

**REVISION 4.1 (round covcap-r4: READY WITH LISTED TEXT FIXES; text only).** C9 reads the
rows at `k` too, with a decline witness (FI-3, the one answer-relevant item); the listing's
`k`/`exact_len` rule, loader and VALUE (FI-4, READY-2); S1131's witness (READY-1); the
`MkEnd` fill bound (READY-3); x0.py's horizon (FI-5); the `marked` guard dropped as C5's own
test (FI-6); the INTO rule (READY-5); the owner example (FI-1), a dead clause (FI-2), cites
and the grep rule (READY-4). Mapped by id: `docs/dev/lanes/covcap6_report.md`.

**R5 (owner, 2026-11-15, amends "no length bound"; D198 (g)):** "Practically, we might need
a max span length then. I don't want edge cases to ruin the concept. Something sufficiently
high that it's rarely seen but that doesn't become a memory problem." Rev 4 meets it with a
limit that already exists: `PCREC_ANCHORED_MAX_STATES` (4096 states at the default, so at most the ceiling less one: 4095
positions; §3.1). No new constant is added at stage 1. Past it there is no anchored machine, no stretch
from this reading, and the pattern runs as it does today (§3.1, §9 Q2). *(Rev 5.1, F23: the owner
answered §9 Q2 at 14:10, "2. set in limits. If it's a user setting it could be shorter then
adjusted by the user per artifact", against its "no new limit" leaning. Stage 2 adds ONE
`limits.def` row with a per-compile option (§11.2). LEAN, OWNER QUESTION OPEN (§9 Q7): it bounds
the cover ROUTE, not the stretch; past it the pattern runs as today, a cliff.)*

## 0. Goals

**Constraint above the ranking (G4; D198 (c), (g)).** The exact stretch (the walk, the record
and the listing) has no budget, no tuning constant and no limit of its own. Its one bound is the anchored machine's existing
state ceiling `PCREC_ANCHORED_MAX_STATES` (§3.1): a machine of at most 4096 states, so at
most 4095 positions, reached by no population pattern's stretch. Past it there is no
machine and no stretch from this reading (today's behaviour, not a new drop; §3.1). No goal
below may be met by adding a bound ON THE STRETCH; a goal that cannot be met otherwise goes, in
order, to the one-pass rule (memory `pcrec-one-pass-loss-chasing`), then to the kit (§11.5), then
to an owner ruling. Form: §8 lists no other pcrec-side row on the exact path; at stage 1
`src/core/limits.def` loses `PCREC_SPAN_WALK_SUBSETS` and gains nothing; `KN_CAP` is gone;
`a{4095}` states 4095 positions and `a{4096}` reads `anchored-A` (§5.3).
*(Rev 5.1, F23; owner 2026-11-15 14:10: "2. set in limits. If it's a user setting it could be
shorter then adjusted by the user per artifact." At stage 2 `limits.def` gains ONE row, the
cover ROUTE's width limit, with a per-compile option and a measured default (§11.2). LEAN,
OWNER QUESTION OPEN (§9 Q7): the limit bounds the route only; the walk, the record and the
listing still state the stretch up to the state ceiling; a pattern whose exact width is over
the limit runs as today, which is a cliff: with the limit at 32, `[0-9a-f]{32}` takes the
cover and `[0-9a-f]{33}` runs the engine for all 33 positions. The no-cliff form (prove the
first N positions, the engine finishes the rest) is [EARNED-SKIP]'s, PARKED, with its trigger.)*

Ranked; the higher goal wins a conflict.

1. **G1, answer identity (every caller), both stages.** No search, match or group answer
   moves on any corpus pattern, encoding or deny arm. Form: `make test`, `make test-axes`
   and `test-kitproof` (answers from libpcre2 10.46, §5.3): all green, 0 differences.
2. **G2, only the predicted artifacts move (reviewers), both stages.** Every artifact
   outside the predicted mover list (§5.2) is byte-identical except the `abi` stamp.
   Form: `scripts/emit_sweep.py` main-before against the candidate; predicted ⊇ observed,
   every predicted-but-unmoved item listed with its `why`.
3. **G3, no slower cell (bench users), each stage.** No mover cell is slower beyond the
   bench's A/A noise floor in any regime of §7. A loss follows the constraint's order above.
4. **G5, the long fixed shapes leave the engine (bench users with literals, hashes, ids
   and uuids).** Stage 1: `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id` faster beyond
   noise in both encodings. Stage 2: also `lit-l40`, `loglines/uuid`,
   `wild-validator-uuid-grok`. Expected size: the 24-position twins' cover/engine ratio,
   measured in §7 (UNMEASURED today).
5. **G6, size reported (reviewers, users with size budgets).** Stage 1: each mover's C
   bytes and `gcc -O2` `.text` before and after, beside its timing (R3). Stage 2: the same;
   a growth is the owner's to accept, once (§9 Q5; rev 4 cited Q4, a slip, F23).

Non-goals: the hull and its N (§3.4); the fraction case of the end state (§1.1, PARKED
rows); lookaround as a run ([REQ-LOOKAROUND]); captures in a cover body (C1);
`PCREC_PREFIX_K_MAX` itself.

## 1. The owner's model, mapped to the code

| the model (D198) | in pcrec today | rev 3, rev 4 |
|---|---|---|
| EXACT span: every position proven, the engine does not retest | two producers compared by C8: the NFA slice `span_facts` (`pcrec_span_walk`, `src/facts/kset.c`) and the anchored machine's walk `kn_walk` (`src/gen/known.c`, C7) | ONE producer: the anchored machine's walk, unbounded (§3.1). The slice is deleted |
| HULL positions: candidates only, the work thrown out | `kset_walk` (assertions passed as if they held, reach `PCREC_PREFIX_K_MAX` = 24) | unchanged, off the cover path (§3.4) |
| "a branch ends it" | no such rule; the slice proved branching prefixes exact by exploring them | the stretch ends where the next byte's set depends on which bytes came before (§3.2) |
| "no bound" (c), amended by "a max span length ... sufficiently high that it's rarely seen" (g), then "set in limits ... adjusted by the user per artifact" (14:10) | `PCREC_SPAN_WALK_SUBSETS` (512), a 48-deep horizon, a 24-deep exact loop, `KN_CAP` (32) | the stretch: no new limit, the anchored machine's existing ceiling `PCREC_ANCHORED_MAX_STATES` (4096 states, `k <= 4095`); stage 1 reads the kit's seam bounds through C15; stage 2 RE-READS C15 as the cover route's width limit, one `limits.def` row with a per-compile option (§11.2; LEAN, OWNER QUESTION OPEN, §9 Q7) |
| the kit loops over repeated positions itself | the kit renders one test per position | not asked (R3); the kit gets the span |

### 1.1 The END STATE (D198 (d); C-25), and the cover as its first case

Given a pattern, pcrec proves the exact stretch from the match start as far as it goes.
If the stretch is the whole pattern, the kit's proof finishes the match: that is the
cover. If it is a fraction, the proven part is done and an engine runs the rest. Where
the exact stretch is short (most often under UTF-8, where a multi-byte class splits on its
lead byte, §3.4), hull positions extend it to filter candidates.

On the anchored machine this is ONE walk with one rule per depth (§3.1): while every row at
a depth allows the same next-byte set, the position is EXACT; where they differ, the exact
stretch ends at that depth `L`. What follows reads the same walk's state at `L`:
- WHOLE: the rows at `L` all accept and none continues (C10): the cover. Built here.
- FRACTION: the rows at `L` are the machine states an engine resumes from. With one row,
  it is one machine state; with several, the subject's own `L` bytes pick it. Nothing in
  the walk is redone: `L`, `S_0..S_{L-1}` and the rows at `L` are its outputs. Not built
  ([EARNED-SKIP]/[MATCH-KNOWN], PARKED; trigger unchanged).
- HULL: past `L`, the same walk continues with the rows MERGED (the union of their live
  next-byte sets per depth). Liveness is the machine's own, so this hull is never wider
  than `kset_walk`'s. N is how far the merge runs. Not built (§3.4; trigger there).

Unlocks, with triggers (PLAN, for main to file under the N row): (i) N as the merge's
reach from `L` (trigger: the first FIND statement that offers the kit exact plus hull
positions); (ii) `kset_walk` retires into the merge phase on routes with an anchored
machine (trigger: (i)); (iii) the rows at `L` as the engine's resume state (trigger:
[MATCH-KNOWN] un-parked; past the state ceiling there is no machine to resume, so that
fraction case needs another producer, same trigger). The walk family ("per-depth forward walks": `kn_walk`,
`kset_walk`, and rev 2's straight walk) shrinks by one member: rev 3 adds none.

## 2. Premise and census

PREMISE (reproduced at `4ccd97ca7`): `SF 'a{48}'` prints `24:97,...` (24 positions) and
`SF 'a{49}'` prints `0`; `SF '[ab]{1000}'` and `SF 'a{500}'` print `0`. The slice's 48-deep
horizon (`kset.c` `2 * PCREC_PREFIX_K_MAX`) leaves a straight line's liveness unknown past
depth 48, and the unknown propagates to depth 0, so the whole span collapses to 0 from 49
positions on. The 512-subset budget never binds on a straight line. Rev 2's "`[ab]{1000}`
lists 24" and "a cliff near 511" were wrong (C-9).

Census (lane covcap3; population `bench_pop()` + `corpus_pop()` of
`docs/dev/optloop/artrev/gen/census.py`, each distinct pattern under both encodings,
11,738 compiles, 10,795 ok; command `python3 -I /var/tmp/pcrec-pcrec/scratch/covcap3/census.py
$PC OUT.jsonl` on a probe build, `probe.diff` beside it; counts by `an3.py`). Today 1,852
compiles take the cover route. The anchored machine's reading of a new stretch was checked
on a scratch prototype of rev 3 (lane covcap4: `kn_walk` unbounded, C8 reduced to the
machine's own exactness, diff `/var/tmp/pcrec-pcrec/scratch/covcap4/probe.diff`, run with
`COVCAP_DFA=1`; the per-compile line record is `DFALINE` under `COVCAP_PROBE=1`).

**What each reading loses or gains among today's covers** (the C-22 list):

| reading of "the stretch" | covers lost | covers gained (stage 1, k <= 32) | source |
|---|---|---|---|
| one NFA THREAD per depth (the literal reading) | 29 compiles, 16 corpus test patterns, k 1..4 (`a*?a`, `ab\|abc\|ad`, `(?:(?!a)z\|w)`, `a??(?:\b\|)a`, ...) | the long shapes only | covcap3 census |
| one NFA SUBSET per depth (rev 2) | 4 compiles, 3 patterns: `reqcube.rxt:29`/`:48` `(?:S(?i:ab)\|(?i:sab))` and its arms swapped (byte), `view_edge.rxt:2607` `(?:[a-z]{0,3}\z\|x)[0-9]{3}` (both) | the long shapes only | covcap3 census |
| the ANCHORED MACHINE (rev 3) | **0** (every cover today already passes the machine's own exactness, C7/C8; rev 3 removes only the slice's half) | the long shapes, plus 18 compiles of 10 corpus test patterns at k = 1, today `exact/producer-short` | covcap3 census `why`; covcap4 prototype |

The 18 gained compiles are context shapes the slice could not decide (liveness through an
item): `composition_d27.rxt` `\d{0,}?\B-`, `\d*(?<=a)\w`, `-{0,}?(?<!\W)-` (byte),
`[a-c]*\ba`, `\w*\b\w`, `[a-z]*\b[0-9]`, `(?:a*\b)*b`, `a*\bA`, `[A-C]*\b[a-c]`,
`\W*(?<!\W)\w` (byte). On the prototype each reads `cover`, and each answers like python
`re` on every subject of length 1..4 over `{a,0,-,A,space,b}` (1,554 subjects, search from
0, 0 differences in 31,080 cells; `python3 -I /var/tmp/pcrec-pcrec/scratch/covcap4/diff10.py
PROBE_PC SCRATCH`). The bench's one `producer-short` decline,
`capability/wild-logparse-quotedstring-noatomic` (utf8, k 2), still declines at a later
conjunct. No bench cover moves out.

*(CORRECTION 2026-11-15, lane covs1f, from the stage-1 sweep triage `docs/dev/lanes/covs1w_report.md`.
The counts above hold for THEIR population only, and two statements need it named:*
- *Census population (above): `bench_pop()` + `corpus_pop()`, 11,738 compiles, by
  `python3 -I /var/tmp/pcrec-pcrec/scratch/covcap3/census.py $PC OUT.jsonl` (a scratch script,
  not committed): 18 gained k = 1 compiles of 10 patterns, 0 covers lost.*
- *Sweep population: `emit_sweep.py`'s `enumerate_corpus`, 7,071 corpus rows = 5,516 distinct
  patterns under both encodings, by `docs/dev/lanes/covs1_evidence/job_sweep` and then
  `predict.py` (lane/covs1): 20 gained k = 1 compiles of 11 patterns (byte 11, utf8 9; the
  eleventh is `a*(?<=A)b`, outside the census list), plus 4 long-literal compiles (k 31, 32),
  24 in all; predict.py `lost=0 unexplained=0`.*
- *The baseline `why` of the gained decisions on the sweep population is `exact/producer-short`
  on 12 byte and 10 utf8 decisions, where §5.2 said "expected 0". The census table above
  already shows them non-zero (its 18 are `exact/producer-short` today); §5.2's "0" is wrong
  on both populations and is read as "every such decision is predicted INTO the cover".*
- *"0 covers lost" holds on both populations (census: §2's table; sweep: predict.py `lost=0`).*

- **Every long fixed shape is one machine row per depth to its accept** (prototype
  `DFALINE`, both encodings): `a{1000}` and `[ab]{1000}` L 1000, the uuid shape L 36,
  `a{30}(?:b{30}c|d)` L 31. Today `KN_CAP` stops the machine walk at 32 and C7 declines
  them `fixed-width` (census `why`).
- **The listing.** `span_facts` states a nonzero stretch on 1,519 compiles where the
  machine reading is not defined (VM finisher 1,127; no anchored machine 36; seeded entry
  14; no cover record 342; covcap3's `census2.jsonl`..`census4.jsonl`). No decision reads
  those values (C8 is the only reader); they leave the listing (§3.3 says where it states).

## 3. The design

### 3.1 The exact stretch: the anchored machine's product walk, unbounded

**FORM.** `kn_walk` (`known.c`) without `KN_CAP`. From the entry row `r0` (C6), it holds
the set of machine rows (virtual states: a state and its count inside a scan-edge chain,
`kn_step`) reached at each depth, keeping only LIVE rows (`kn_liveness`: exact backward
reachability to an accept in any form or through the view-gated final newline), deduplicated
by a per-(state, count) stamp (rev 3 kept today's linear dedup, quadratic in rows; R-2).
At depth `j`:
1. No rows, or a view-gated newline consumed at `j - 1`: the walk ends, `k = j`.
2. Some row accepts in any form: the walk ends, `k = j`. C9 is checked on the rows at `k`
   too: C9 checks depths 0..k inclusive, as `cc_eol` does today (FI-3); C10/C11 then read them.
3. Otherwise each row's live next-byte set is computed (`kn_step` over the bytes, plus `\n`
   through the eol view; C9 is checked here, as the walk passes the depth). If every row's
   set is the same set `S_j`, depth `j` is EXACT and the walk goes on. The first depth where
   two rows' sets differ is `L`, the end of the exact stretch, and THE WALK ENDS THERE
   (`stop = branch`, `k` not known): past `L` it decides nothing, since C8 declines whatever
   `k` is (R-2).

`exact_len` is `L` on a branch and `k` otherwise. These are rev 1's three outcomes (C-6);
the walk defines no bound of its own. On a branch the decision is C8's
`exact/machine-inexact` (C7 passes a walk that stopped at a branch; it reads `k >= 1` and
the rows at `k` only when the walk reached an accept). The `why` therefore moves from
`fixed-width` to `exact/machine-inexact` on compiles that branch before their first accept
(listing only; no route moves, §5.2).

**THE BOUND ON THE STRETCH: the anchored machine's state ceiling (R-1).** *(Rev 5.1, F23: rev
4 titled this "the bound on this route"; at stage 2 the ROUTE has a second, lower bound, the
width limit of §11.2, and this ceiling remains the stretch's only bound.)* The walk reads
`Job.adfa`, which is built only when it fits `PCREC_ANCHORED_MAX_STATES`
(`compile.c`'s `build_anchored_dfa`; where it is absent, C4 `cc_anchored` in `known.c` declines); every walked row is live and the walk ends
by the shortest path to an accept, so `k <= V - 1 <= 4095`. The row as `limits.def` has it:

    PCREC_LIMIT(PCREC_ANCHORED_MAX_STATES, 4096, "states", "compile budget", BUILD_D, "",
      "[ENG-ABS]: the optional anchored match-here machine's own DFA state ceiling, lower than the mandatory pair's", LIMITS_H)

It is LABELLED (kind `compile budget`, override `-D`). The row names its role, not its
derivation, which lives in `src/core/limits.h`'s `[ENG-ABS]` block (measured: 2.05x the
captures-on corpus maximum of 2,001 states; 4.9x below `tests/resource`'s giant repeats,
whose compile CPU and size it excludes). Proposed stage-1 `desc` text, no derivation
invented: append "; also bounds the exact stretch the cover record states, at most the ceiling less one
positions (docs/design/cover_cap.md); derivation: limits.h [ENG-ABS]" (worded so at both
stages: at stage 1 a COVER is at most 32 positions (C15) while the record states up to
4095; review r9 covs1 CONTRACT-2, 2026-11-15). (`compile.c`'s comment calling
it equal to `PCREC_MAX_DFA_STATES_TABLE` contradicts limits.h's "lower than": stale, §5.5.)

PAST THE CEILING: no anchored machine is built, C4 declines `anchored-A`, no exact stretch
comes from this reading (`exact_len` 0) and the pattern runs exactly as it does today. That
is today's behaviour, not a new drop, but it IS a step: `a{4095}` states 4095 positions,
`a{4096}` states 0 (PREMISE, the report). The ceiling counts STATES, not positions: a
straight line meets it at 4096 positions (`a{2047}b{2048}` is walked, `a{2048}b{2048}` is
not), a machine with many paths meets it sooner (`[ab]*a[ab]{12}`, 13 positions, gets no
machine; `[ab]*a[ab]{11}` does). A "fraction proven" reading
past the ceiling needs another producer (trigger [MATCH-KNOWN], §1.1 (iii)).

**Why this walk** (rev 3, R4; covcap4's report has the comparison): it is the walk the
cover already runs, which X0 checked against libpcre2 (`kit_proof.md` §6.4); liveness on a
machine is exact (no undecided case, no root or cycle rule: C-1..C-3, C-5 (i) go by
deletion); it compares byte SETS, not rows, so `-fno-altcls-*` and `-fno-scan-edge` cannot
move `L` or `k` (C-4); it loses no cover and keeps Z2 ruling 1 (§2, §9).

**TERMINATION AND COST (C-1, C-7; R-2).** Every row is live, so the shortest path from
`r0` to an accept is at most `V - 1` and the walk ends by that depth (or earlier at `L`).
`kn_walk` steps 256 BYTES per row (`known.c`), so the walk costs 256 x (rows summed over
the depths walked); with the stamp dedup each step is O(1). Bound: depth <= 4095, rows per
depth <= `V` <= 4096, so 256 x 4095 x 4096 byte steps in principle; on an acyclic machine
the rows over all depths sum to at most `V`. Measured on the emitted machine with rev 4's
stop rule (`python3 -I rowcost.py build/pcrec PATTERN`, the report's run kit):
`a{4095}` depth 4095, 1 row per depth, 1.05 M byte steps; `[ab]*a[ab]{10}-{2000}` (4,048
states, rev 3's walk 1.56 G byte steps to its first accept at 2011) stops at `L` = 11, max
1,024 rows, 0.52 M byte steps; `[ab]*a[ab]{8}-{300}` stops at 9, 0.13 M. No constructed
witness with many rows AND a long exact stretch was found (alternation families of that
shape route to the VM: no anchored machine). The compile-cost row of §5.1 carries these
witnesses. MEMORY: two row arrays (this depth, the next), grown as needed, plus 32 bytes of
set per exact depth and the rows at `k` for C10/C11: O(32 x exact_len + V), at most 128 KB of
sets. The `rows` detail of C7 retires (census count 0).

**WHAT IT DELETES (simplification, the benefit).** The NFA span slice: `pcrec_span_walk`
and its `sw_*` helpers (`kset.c` from the "THE SPAN SLICE" banner to the end of
`pcrec_span_walk`), `MkLang` (`facts.h`), the `span_facts` row of `facts.def`, its
accessor `pcrec_fact_span_stated` and the trace build's `SPANSET` record (`facts.c`),
`PCREC_SPAN_WALK_SUBSETS` (`limits.def`), `KN_CAP`, C8's slice comparison and its
`producers-disagree` / `producer-short` / `producer-unstated` details, and
`pcrec_known_derive` (no caller; it read `MkLang`; M6, C-20) with its prototype, `known.h`'s
header prose on it, `PcrecCover.lang` and `MkDerived`; `facts_derive.h`'s reader;
`PF_WHY_ERASED`/`PF_WHY_MARKED` (`facts.h`, `facts.c`, `facts_dump.c`; R-9 below). The
48-deep horizon and the 24-deep exact loop go with the slice. `PCREC_SPAN_WALK_SUBSETS`'
home is `INTERNAL_H`, not `limits.h` (R-10).

**THE SLICE'S THREE GUARDS (R-9).** The slice declined on an erased NFA (`erased-nfa`), an
island NFA and a marked accept (`end-mark`). Believed subsumed: an erased NFA widens the
language, so its finisher is not the DFA (C1); a marked accept means a tagged machine (C5);
an island machine is character-stepped. No counterexample in 72 decisions over 48 shapes
(V-10), but not shown, so rev 4 KEEPS two as lines at the top of `cc_anchored`, each
declining `anchored-A` with its own detail (`erased`, `island`). The `marked` guard is C5's
own test (`kset.c`'s guard is `dfa.c`'s `tagged`, which C5 `cc_unmarked` reads), so it is
not repeated (FI-6). The build counts each over C4's population, which is larger than the
one V-10 measured (compiles that reached C8): a count above 0 there is a `why` move from
C5-C7 into `anchored-A/erased|island`, listing-only (§5.2), not a lost cover. §5.2's INTO
list carries `exact/producer-unstated` (expected 0). Dropping the two is a later cleanup
once a count and an argument show it.

### 3.2 "A branch ends it", at language level (C-22)

A BRANCH is a position where the bytes allowed next depend on which bytes were read
before it, among the strings that can still become a match. Up to the first branch, the
set of allowed bytes at each position is one fixed set, and every combination of those sets
is the start of some match: that is the exact stretch. The NFA's alternatives and threads
are not branches unless the LANGUAGE splits. Two examples:
- `a*?a`: the only match from a start is `a` (leftmost, lazy). Two NFA threads run (the
  `a*?` loop and the final `a`), but there is one allowed byte and then a match end: no
  branch, stretch `1`, `S_0 = {a}`.
- `ab|abc|ad`: the matches are `ab` and `ad` (`ab` wins over `abc`). After `a` the next
  byte is `b` or `d`, and either way the match ends: the language is `{a} x {b,d}`, no
  branch, stretch `2`. By contrast `a[xy]c|b[xy]d` has stretch 2 (`{a,b} x {x,y}`) and
  branches at the third byte, where `c` or `d` depends on the first byte.
Which today's covers each reading loses is §2's table: the literal thread reading 29
compiles, rev 2's subset reading 4, this reading 0.

### 3.3 The cover table and the listing

- C7 `fixed-width`: on a walk that reached an accept, `k >= 1` and the rows at `k` are not
  empty; the `k <= KN_CAP - 1` term goes; a walk stopped at a branch passes to C8 (§3.1).
  Stage 1 adds C15 (§3.5).
- C8 `exact`: the walk did not stop at a branch (`exact_len = k`); otherwise
  `exact/machine-inexact`. Its kind becomes `machine`; its `span fact` reading goes. C8 keeps
  its id and its `why`. It is decision-redundant at rev 4: the rows at a branch stop never
  accept, so C10 declines whatever C8 declines; C8 names the `why` (READY-1, §5.4).
- C12 `utf8-start` reads the record's `S_0`; its kind `span fact` becomes `machine`.
- THE RECORD (R-3). `pcrec_cover`'s memo keeps, on EVERY decision it makes (cover or
  decline): `why` (conjunct and detail), `k` and `exact_len` (`uint16_t`, each with a
  known/not-known mark), `stop` (`accept`, `branch`, `empty`, `view`; `-` where no walk ran)
  and `S_0..S_{exact_len-1}` in an
  arena owned by the Job (32 bytes per depth; freed with the Job). Today the walk is a stack
  local and `MkEnd` (`uint8_t k`, `set[32][32]`) is written only when C8 holds; at stage 1
  `MkEnd` keeps its shape (C15 bounds `k <= 32`) and is filled from the record before C13
  reads it (`cc_served` -> `pcrec_cover_site` -> `cover_window`), under §3.5's bound. One compile may decide more than once (`[a-c]*\ba`: `anchored-A`,
  then a later part): the record is the compile's LAST decision per encoding.
- THE LISTING. `--emit-facts` loses the `span_facts` row. A new section `cover` (a new
  `facts_listing.md` section after its §4.4, and `cover` added to [3¶3]'s closed name set),
  columns `encoding | why | k | exact_len | sets`: one row per encoding, read from the record
  (no second walk). `sets` is `S_0..S_{exact_len-1}` comma-joined in `kset_walk`'s spelling,
  or empty. Where the memo was never asked (an earlier LOCATE row won: `ab$`, `^ab`), the
  row reads `why` `unasked`, `k` and `exact_len` `-`; the listing never runs the cover
  decision itself (no kit ask after the artifact, facts_listing.md [5¶2]). Where C1-C6
  fail: the `why`, with `k` and `exact_len` by the rule below.
- WHERE A STRETCH IS STATED (R-4). `exact_len` and `sets` are stated only where X0 can check
  them: the decision is `cover`, or the pattern's width is bounded (`width` fact
  `[wmin, wmax]`, `wmax` finite), and X0's search is given `wmax` as its horizon (a stage-1
  build item, FI-5: `x0.py`'s `stated()` gains a `wmax` column and passes `horizon=wmax` to
  `explore`, its header's row-format note says so; beside the `z2.py` re-point). Other rows,
  C1-C6 declines included, read `exact_len` `-`; 0 is listed only where it is checkable.
  `k` is listed where `stop` is `accept` or `view`, else `-` (FI-4). The build counts
  stated, checked and unstated rows over the census (K35). The definition of a stated stretch is ¶7c's, unchanged: for every `d < exact_len`
  the matches' length-`(d+1)` prefixes are exactly the product and no match ends before
  `d + 1`. The section also makes the cover `why` visible in the default build, which the
  mover prediction reads (§5.2, C-15).
- NOTED (R-14). The tree has three memoized conjunct tables (`cover_conj[]`,
  `lmwalk_conj[]`, `split_conj[]`); the general form is one decisions-why section with
  per-table columns, and the walk's output (L, k, sets, rows at L) as one record read by the
  listing, C12, `cover_window` and later [MATCH-KNOWN]. Whether the cover's why belongs in
  the existing `decisions` section is the build's first question. PLAN for main (trigger: a
  second table's why needed by a mover prediction).

### 3.4 The hull and N: not on the cover path

A cover is proven at every position; the hull adds nothing there. `kset_walk` stays the
hull producer with its reach `PCREC_PREFIX_K_MAX` (24). That limits row carries no rationale
today; the "headroom over a measured corpus maximum of 13" lives only in
`offset_k_skip.md` §3.3 (C-12). Labelling the row is PLAN (main, hull side). N is not
built: no reader takes exact plus hull positions (D77); its trigger is §1.1's (i).
UTF-8 (D198 (d) points 2-3): `[а-я]{4}` reads `L = 1` under utf8 on the prototype (the
lead bytes `d0`/`d1` take different continuation sets), while a Cyrillic literal is one
row per depth. That short-stretch case is where §1.1's hull merge would carry a filter.
It is a later row after this one.

### 3.5 Two stages (rev 1 §3.5, kept)

- **Stage 1 (pcrec only, today's seam).** §3.1-§3.3, plus C15 `statement-fits` (kind
  `seam`, read right after C7): `k <= MF_WSPAN_POS`, `k + 1 <= MF_WREACH`, `k < MF_MAX_FWD`,
  read from the kit's constants, so `cover_window` never writes past `mf_wspan.set[]` (K7).
  pcrec has no bound of its own. Named build item (R-13): `cover_window` checks the span
  length BEFORE its position writes (`window_bounds_check` first, or at its top), so a
  missing C15 is the named internal error, not an overrun of `mf_wspan.set[32..]`. Named
  build item (READY-3): the `MkEnd` fill from the record copies only for
  `k <= MF_MAX_SPAN_POS`, else the same named internal error, so plant (d) and
  `a{40}(?:b|cc)` (k = 41) never write past `MkEnd.set`.
  Cover movers: `k` 25..32, and the 18 k = 1 compiles (§2).
- **Stage 2 (after the kit's answer to §11.5; rev 5 replaces rev 4's bullet).** A counted
  seam up to 4095 positions (the state ceiling, §3.1). C15 is RE-READ, not retired: it
  becomes the cover width limit (§11.2), and the seam's THREE kit bounds (positions per span,
  reach, proof range) become one build-time assertion (§11.1 B2; rev 5.1, F3).
  `MkEnd` points at the record's sets (no copy); `cover_window` and
  `pcrec_cover_proof_diff` read counted ranges (§11.1). Movers: the long shapes the
  anchored machine holds, up to the measured default (§11.2, §11.4); past it, at the
  user's raise (`--window-search-width=N`, §11.2.1).

Each stage is one pcrec `abi` event (§4.4). The listing section (§3.3) lands at stage 1.

### 3.6 The standing questions

1. **Measurement regime: RELEVANT** for G3, G5, G6 (§7). No decision depends on a regime:
   the cover is answer-identical by proof, and the census counts compiles.
2. **Independent control: RELEVANT; this is where rev 3 pays.** Today C8 compares the
   NFA slice with the anchored machine's walk on every compile and declines on a
   difference. The two share their source (`Job.nfa`: the machine is its subset
   construction), so C8 was a control on the two READINGS, not on the language. Rev 4 has
   one reading. Its controls, each with what it shares and which plants (§5.4) it sees (R-5;
   rev 3's "none sharing its code" was false for two):

   | control | shares with the reading | sees |
   |---|---|---|
   | libpcre2 10.46: `test-kitproof` answer rows | nothing | answer-moving errors |
   | X0's per-position check, run once by the build on the listing's stated rows, census population, horizon `wmax` (§3.3; instrument `docs/design/kit_proof/z2/z2.py` `records()` re-pointed from `SPANSET` to the listing, with `x0.py stated`) | nothing (libpcre2 enumerations) | overstated sets: (c), (f) |
   | `facts` rows in `cases.tsv` (values written in full, checked against libpcre2 when written) | nothing | (a), (b), (c), each by value |
   | hull containment, trace build: `S_d ⊆ kset_walk.k[d].set` for `d < min(exact_len, 24)` in `pcrec_cover`'s trace block (rev 3 deleted `facts.c`'s ONE-WALK hull check unlisted; it is re-pointed, about 15 lines) | `Job.nfa` only, not the machine or `kn_walk` | overstatement within 24: (c), (f) |
   | the `-fno-scan-edge` arm compare, census population, listing equal row for row | `kn_walk`'s rule, liveness, C9-C11 | only the virtual-state half; none of (a)-(c) |
   | the engine route (`test-axes`, `--memfn=no-window-search`) | the emitted tables | answer-moving errors |
   | the kit's proof (C14, `pcrec_cover_proof_diff`) | the statement | the kit's text only: a wrong statement passes it |

   What is lost: a decline on every user compile where two readings disagree; it fired on 0
   compiles in the trace builds that assert it (`z2build_report.md`, "producers-disagree
   internal errors are 0"). K35: the sweeps count the whole census population, stated vs
   unstated rows counted (§3.3); the kitproof floors are in §5.3. [MECH-REACH]: §5.4.
3. **What moves on regeneration: RELEVANT.** At stage 1 `limits.def` loses `PCREC_SPAN_WALK_SUBSETS`
   (home `INTERNAL_H`) and gains nothing (stage 2 gains one row, §11.7 Q3); `PCREC_ANCHORED_MAX_STATES`' `desc` gains §3.1's
   pointer text. By grep in the same change: `--list-limits`' output, the X-macro list,
   `tests/registry/limits_check.sh`'s count (82 becomes 81) and name list,
   `limits.def`'s own home count, `src/facts/CLAUDE.md`'s bound sentence (C-13). `facts.def`
   loses a row: every reader of the facts table (`src/dump/facts_dump.c`, the listing's
   row order, any check that counts facts), by grep. Regenerated
   by the build: `tests/kitproof/answers.tsv` (`gen_answers.sh`), the start-set mover
   manifest if it moves, the recursion identity gate's pins (§4.4). Not regenerated:
   `docs/dev/artifact_size_log.tsv` (its own gate commit) and kvcensus's tables.

## 4. The seam, and the kit request

### 4.1 What pcrec needs across the seam (facts)

pcrec STATES one window span of `k` exact positions for any `k >= 1`, with one context
position before (offset -1) and one after (offset `k`). It READS the set the kit's text
tests at every offset in `[-1, k]` and checks it EQUALS the statement (C14), and it reads
the reply's `stop`. Today the proof range ends at `MF_MAX_FWD` (33) and the statement is
refused past `MF_WSPAN_POS` (32) and `MF_WREACH` (64).

### 4.2 pcrec's side (stage 2)

*(Rev 5.1, F23/READYSEAM-10: SUPERSEDED by §11.1, which a build lane reads instead. Rev 4's
sentence "C15 retires" is WRONG at stage 2: C15 is RE-READ as the cover route's width limit
(§3.5, §11.2). Its `window_bounds_check` sentence moved to §11.1 item B4.)*

### 4.3 KIT REQUEST DRAFT

*(Rev 5: rev 4's draft is SUPERSEDED by §11.5, which adds the owner's 2026-11-15 rendering
direction, the width limit's effect on the population and the EMITTED-2 fact. Rev 4's text is
in git at 61f8e9f88. Rev 5.1 re-issues §11.5 whole: three bounds, the by-value fact, true
population facts; F3, F5, F21, F30.)*

Struck from rev 2 (R3, C-24): the "compact text for repeated positions" ask and its size
fact (the observation is already in the kit's ideas log), the G2-cases ask, the list of
the kit's internal bounds, and the pre-classification of the kit's version events.

### 4.4 The `abi` events (rev 1 §4.4, kept)

Both stages are pcrec `abi` events, numbered at landing: a bump, the recursion identity
gate's re-pin, a `docs/dev/history/abi_changelog.md` entry, D94's grep of every reader of
the current number, and the suites that count (registry, codegen, rxtsource). The gate's
(B) compares whole files over every call-free corpus pattern, and §5.2's corpus movers are
in it. Stage 2 also moves kit bytes (D146/D147: a pcrec abi event in the same commit).

### 4.5 Spec (D80), in the same change (C-13)

Stage 1:
- `facts_listing.md` §4.1.2¶7c (`span_facts`) becomes a `— retired` stub (a spec number
  never disappears) and its `decline:` reasons leave §4.1.3¶3; [3¶3]'s closed name set gains
  `cover` (R-3); a new section `cover` after §4.4 defines §3.3's section: its columns, the
  `unasked` row, where a stretch is stated (§3.3 R-4), ¶7c's product definition carried
  over word for word, the `k`/`exact_len` listing rule (§3.3 FI-4), and one sentence: a
  pattern whose anchored machine is not built lists `exact_len` 0 where its width is
  bounded, `-` otherwise. §4.1¶2's sentence on the `cover` row's reading of `span_facts` is rewritten
  to the machine reading.
- `cli.md` §2.6 describes `--list-limits` generically and names no row: no hunk (the gone
  row and the `desc` text show in its output). The `kind` vocabulary is untouched (R-7 moot).
- `match_api.md` §6.3.4¶2's `"cover"` row names no bound: no hunk.
- The abi changelog entry (§4.4).
Stage 2: the abi entry, plus the per-compile width option's hunks (§11.2.1: `tuning.md`,
`limits.md` section 3.12 (new), `match_api.md` §8.2, `facts_listing.md` §4.5¶2's one word). *(Rev 5.1, F21:
rev 5 said "no spec hunk"; the option is caller-observable, D80.)*

## 5. Answer-identity plan

### 5.1 The checks (C-19)

| check | against | proves |
|---|---|---|
| `make test` (both encodings) | oracle-verified expectations | every mover answers as before |
| `make test-axes` | the engine route, `--memfn=no-window-search` (`tuning.md` §2.43¶3d) | cover against engine on every corpus subject |
| `test-kitproof` (§5.3) | libpcre2 10.46 (`answers.tsv`) | boundaries, every startoffset, find-all |
| `pcrec_cover_proof_diff` | the statement | the kit proves what pcrec states, at every `k` |
| X0 set check, one-off (§3.6 Q2) | libpcre2's per-position sets | every stated position of the listing's `cover` section |
| scan-edge arm compare, one-off | the same listing under `-fno-scan-edge` | the virtual-state reading |
| ASan, one-off: `make asan`, then `PCREC=build-asan/pcrec PCREC_HARNESS=build-asan/pcrec-harness bash tests/kitproof/run_cover.sh` (`run_cover.sh` is not in `san_scripts.txt`, so `make asan` alone does not run it; the build first checks both ASan binaries exist) | AddressSanitizer | the grown row arrays, `MkEnd`, the seam arrays |
| `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` | the clean tree | every kitproof witness still reaches its site |
| `scripts/compile_time_census.py`, old binary against new, CPU and max RSS (C-7), plus the worst-case witnesses `a{4095}`, `[ab]*a[ab]{10}-{2000}`, `[ab]*a[ab]{8}-{300}` (each `scripts/watchdog -s 60 -m 2g -c 60 -S covcost -- build/pcrec -p rx --features all --emit-main -o OUT --pattern P`, both encodings; R-2) | the old binary; §3.1's byte-step counts | §3.1's cost claim |

### 5.2 Byte identity and the mover list (G2; C-15)

`scripts/emit_sweep.py`, main-before against the candidate, over the committed population.
Its facts stream today allows only cell moves and new rows (R-6): the build adds a
DECLARED-GONE fact (`span_facts`) and a DECLARED-NEW section (`cover`), each judged both
ways as the dumps stream judges its declarations (a declared item that does not move is
red, an undeclared one is red), so every other facts row keeps its byte-identity guard.
The dumps stream declares `--list-limits`' gone row and its one `desc` cell (§3.1).
The prediction comes from the BASELINE build only, read from the trace build's `KITPROOF`
record (`PCREC_KIT_PROOF_TRACE=1` on the trace binary; `k=0` on a decline, so the width is
read from the `width` fact of the same compile): INTO the cover, every decision whose `why`
is `exact/producer-short` or `exact/producer-unstated` (not 0: 12 byte / 10 utf8 on the sweep population, see §2's 2026-11-15 correction), or
`fixed-width` with the width's LOWER bound `wmin <= 32` at stage 1 (`wmin <= 4095` at
stage 2; R-8: C7 reads the first-accept depth, so `a{32}|a{32}b` and `x{31}(?:y|yz)`,
width `[32,33]`, move; READY-5: a dead short arm puts that depth above `wmin`, as in
`a\z\W|b{32}`, width `[2,32]`, first accept 32). That is an UPPER bound: C9-C15 never ran on those decisions, so the
deliverable lists each predicted compile that does not move with the candidate's `why` (at
stage 1 the bench's `wild-logparse-quotedstring-noatomic` is one, §2). OUT of the cover:
none. A `why` that moves from `fixed-width` to `exact/machine-inexact` (§3.1), or from
C5-C7 into `anchored-A/erased|island` (§3.1 FI-6), moves no artifact (listing only). No `k >= 25` floor is claimed for gains below 25 (the 18 k = 1 compiles are in
the prediction by their `why`). The listing is not predicted (it changes form, §3.3); its
values are checked by §3.6 Q2's table instead (C-15's downgrade).

### 5.3 Witnesses (`tests/kitproof/cases.tsv`; C-16)

- `verdict`: a literal and `[0-9a-f]{n}` at 24, 25, 32, 33, 40, 100, 1000; `\b[0-9a-f]{n}\b`
  at 32, 40, 100; `\d{32}` under `u`. Stage 1: cover through 32, decline from 33
  (`statement-fits`). Stage 2 (rev 5.1, F7): on the DEFAULT arm, cover through the shipped
  default `D` and decline past it (the `why`, `width-limit`, is checked by a `facts` row, since a
  `verdict` row reads only `RX_DFA_SCAN`); on the `W` arm (§11.6.2), cover at every length the
  machine holds. `ab|abc|ad` cover;
  `(?:S(?i:ab)|(?i:sab))` cover (byte); `[a-c]*\ba` cover (a k = 1 gain);
  `a[xy]c|b[xy]d` decline `exact/machine-inexact`; `a(?:b|c)(?:$|q(?<=x))` decline
  `no-eol-view` (FI-3: its one non-identity eol view sits on the row at `k`, so a plant
  that drops depth `k` from C9 flips it; PCRE2 matches `ab\n` at (0,2)). The existing
  `(?:[a-z]{0,3}\z|x)[0-9]{3}` rows (Z2 ruling 1) are unchanged.
- `facts` (the listing's `cover` section, compared whole; the loader in `run_cover.sh`
  reads the new section, a named loader change): the 6 existing rows keep their values on
  the new section; new rows `a{40}(?:b|cc)` `41:` + 40 × `97` + `,[2]` (its `b`/`c` set;
  the build writes the literal value), `a[xy]c|b[xy]d` `2:[2],[2]`, `a{30}(?:b{30}c|d)`
  `31:` + 30 × `97` + `,[2]`, `ab|abc|ad` `2:97,[2]`, `a*?a` `1:97`, `(?:\bab|\Bac\z)` `0`
  (`entry-const/seeds`), `a(?:b|c\z\W)` `2:97,98` (plant (c)'s witness, R-11), and the
  ceiling's pair (R-1): `a{4095}` `4095:` + 4095 × `97` (generated by the build) and
  `a{4096}` `why` `anchored-A`, `0`; and `ac|bd` (S1131's witness, READY-1; `why`
  `exact/machine-inexact`, the build writes its value). The loader in `run_cover.sh` tracks
  the `#section cover` line (listing rows carry no section name) and keys each row on `$1`,
  the encoding (READY-2). A `facts` VALUE on this section is the row's `why | k | exact_len |
  sets` columns, tab-joined; the short forms above give `exact_len:sets`, and the build
  writes every value in full in `cases.tsv` (no prefixes).
- `answer`: per length `n` of the verdict rows: subjects of `n-1`, `n`, `n+1` bytes, a near
  miss at the last position, a match at the subject end, two adjacent matches, every
  startoffset; expectations from libpcre2 via `gen_answers.sh`. Answer rows at `n >= 33`
  land at stage 2 (at stage 1 they fail their REACH, which requires `cover`).
- Floors (`run_cover.sh`: verdict 24, facts 6, answer 55) rise by the rows added (facts
  by 10, to 16); no row is
  removed (rev 2's loss of four answer rows does not happen). *(Rev 5.1: at main the floors
  read verdict 48, facts 19, answer 105 after stage 1; stage 2's deltas are §11.6.2's.)*

### 5.4 Sabotage rows (mech arm `kitproof`), each with a unique witness (C-17)

| plant | breaks | unique witness | why only it flips |
|---|---|---|---|
| (a) a length bound back on the walk (`j < 32`) | G4 | `facts` `a{40}(?:b|cc)` `41:...` → `32:...` | not a cover (variable width); (b)-(d), (f) leave a one-row line's length intact |
| (b) rows compared by identity: a second row ends the stretch | §3.2 | `facts` `a[xy]c|b[xy]d` `2:[2],[2]` → `1:[2]` | the only witness with two rows of equal sets before `L` |
| (c) liveness dropped (dead rows kept) | §3.1 | `facts` `a(?:b|c\z\W)` `2:97,98` → `2:97,[2]` | (a), (b), (d) keep liveness; its `c` row is dead in the emitted table |
| (d) C15 removed (stage 1 only) | K7 | the 40-literal `verdict` compile goes red: `window_bounds_check`'s named internal error, after §3.5's R-13 reorder (before it, the red was an overrun) | nothing else states a 40-position span at stage 1 |
| (f) a byte added to a stated `S_0` | §3.6 Q2's hull containment | the trace build's hull check fires on `facts` `a*?a` | the only plant that widens a set; (c) is told apart by its value |

S1131 (C8 skipped): its `verdict` witness `ac|bd` cannot flip at rev 4 (C10 declines what
C8 declines, §3.3), so its witness becomes the `facts` row `ac|bd`, whose VALUE carries the
`why` (`exact/machine-inexact` -> `end-at-k` under the plant), with the REACH record below
(READY-1); its `SAB_AFTER` copies `w.set` by `sizeof end.set` and is re-anchored on the
record's counted copy. S1136 and S1139 anchor on `cc_eol`'s loop over retained rows, which
§3.1 removes: both re-anchor on the walk's C9 check at depths 0..k inclusive, the rows at
`k` included (R-12, FI-3). S1149 (`slice ctx passthrough`) plants into the deleted slice:
the row retires with its code (its id stays absent), its three `facts` witnesses stay as
`cover`-section rows, and the cloud tables drop it by regeneration
(`cloud_units_plan.py mech --write`: `tests/ci/cloud_mech_shards.tsv`,
`measured_mech.tsv`), or a shard FATALs on an undefined id. REACH for a facts-value plant
(`reach.sh` cannot show one on a non-cover witness): the clean run's value equals
`cases.tsv` and the planted run's differs, recorded per plant. The plant ids are the build's.

### 5.5 Witnesses outside the census population (C-18), and stale text (C-14)

At stage 1 these become covers and would go vacuous-green: `tests/codegen/run_offset_skip.sh`
(`\b[0-9a-f]{32}\b` as the offset-k DECLINE witness and the `-fno-offset-skip` identity
witness) and `tests/codegen/run_entry_shape_identity.sh` (`[0-9a-f]{32}`). The build
re-points each to a shape no stage makes a cover (a capture, which C1 declines, e.g.
`\b([0-9a-f]{32})\b`, if it still selects the same form; the build checks), and greps
every non-`.rxt` test for the moving shapes at each stage. *(Correction 2026-11-15, review r9
covs1 CHECKS-6: the vacuity premise is false for both scripts. `run_offset_skip.sh`'s
`emit()` passes `--memfn=no-window-search`, which denies the cover row, so its bare witness
never became a cover there (the re-point is harmless, kept); `run_entry_shape_identity.sh`
compiles with `--engine=vm`, so it does not go vacuous either and was rightly not re-pointed.
The sentence naming it is struck.)* Stale text the build owes: the
`facts.h` comment naming a FIND-site reader of `MkLang` that does not exist, `known.c`'s
`KN_CAP` comment, `kit_proof.md`'s sentences on C8's two producers and on `span_facts`' bound,
`ctx_span.md` §11 N-1, `compile.c`'s comment on `PCREC_ANCHORED_MAX_STATES` (§3.1), and the
readers R-10 lists: `tests/kitproof/CLAUDE.md`, `cases.tsv`'s header row, `run_cover.sh`'s
header, `kit_proof/CLAUDE.md`, `x0/CLAUDE.md`, `z2/CLAUDE.md` with `z2.py`,
`fact_consumers_inventory.md`'s two `span_facts` rows, `docs/design/memfn/window_site.md`'s
`MkLang` sentence (pcrec's design record for the kit: a pcrec edit), `docs/design/memfn/CLAUDE.md`,
`scripts/NOTES.md`, `src/facts/CLAUDE.md`'s three mentions and `emit_sweep.py`'s help text. (Rev 3's `span_runs_sheet.md` and
`patfacts/inventory.md` hold no mention: struck, V-11.) Each is found by grepping
`span_facts`, `MkLang`, `KN_CAP`, `pcrec_known_derive`, `PF_WHY_ERASED`, `PF_WHY_MARKED` and
`PCREC_SPAN_WALK_SUBSETS`, which must reach 0 outside history. HISTORY is `docs/dev/history/`,
`docs/dev/reviews/`, `docs/dev/lanes/`, the journal, `decisions.md`, `plan.md` and
`plan_completed.md`, the kit's ledgers (`memfn/docs/journal.md`, `responses.md`: pcrec cannot
edit them), study data (`studies/selflip/sweep.tsv`), the Z2 build's evidence kept as run
(`docs/design/kit_proof/conj.py`, `witnesses.txt`, `x0/results.md`, `z2/stated_built.tsv`)
and the fixture `scripts/tests/emit_sweep.py.test` (`span_facts` as an arbitrary row name;
READY-4); a LIVING design note
that mentions them (`ctx_span.md`, `span_arms.md`, `alt_normal_form.md`,
`window_contract.md`) keeps the mention with a dated "superseded by cover_cap.md rev 4" note
beside it, and the grep counts unmarked mentions.

## 6. Movers (both encodings; the sweep's count is the count of record)

| population | stage 1 | stage 2 |
|---|---|---|
| bench into the cover | `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id`: 4 × 2 | + `lit-l40`, `loglines/uuid`, `wild-validator-uuid-grok`: 7 × 2 |
| corpus into the cover | `litrun.rxt:1204` (31), `:1320` (32): 2 × 2; the 10 k = 1 patterns of §2: 18 | + `counterk.rxt:1919` (49), `spanarms.rxt:96` (60), `d27_large_counts.rxt:6` (500), `:37` (1000): 6 × 2 |
| out of the cover | none | none |
| not moving | captures (`wild-secrets-github-pat`, `(ab){300}`: C1), `uuid-near-miss` (attempt route), variable widths | same |
| outside the population | `(?i)permission is hereby granted` (28, byte); §5.5's test witnesses | + `req-<uuid>` (40) |

## 7. Re-timing plan (not run; R3)

*(Rev 5: the stage-1 night timing below is still owed; §11.4 merges it with stage 2's timing
into ONE plan (adding the dense near-miss witnesses of review r9 EMITTED-2 and the cells that
set the width limit's default). §11.4 is the plan of record; this section stays as its base.)*

Cells: §5.2's OBSERVED movers × both encodings, confirmed with the bench dev. Before and
after differ in one variable: main at the stage's base against main with the stage, same
box, pin, toolchain and night. Regimes, each mover in each:
- hit-dense subjects and near-miss subjects (a mismatch at the last position), not only
  miss-heavy throughput;
- a COLD-artifact regime: the matcher is not already warm in L1/L2 (the owner's concern,
  D198 (f): an inline form that busts the cache may lose), e.g. many matchers called in
  rotation or the cache evicted between calls, the bench dev choosing the method;
- `short-subject-search`, where a long cover's fixed cost shows first.
A/A controls: `lit-l16` and one non-mover engine cell. G5's expectation: the 24-position
twins, default against `--memfn=no-window-search`, on the before compiler. Emitted size
(C bytes, `.text`) per mover is reported beside each timing. Window: at night, cleared with
the owner, outside 20:00-01:00, after each stage lands.

## 8. The bounds on the cover path (rev 1 §1's inventory; rev 4 verdicts)

Rev 1 §1's inventory (in git at `75d365a0b`) stands for its sites. Rev 4's verdicts:
- THE BOUND THAT BINDS THE STRETCH (R-1; omitted from rev 3's inventory):
  `PCREC_ANCHORED_MAX_STATES` (4096 states, so `k <= 4095`), existing, labelled `compile
  budget`, derived in `limits.h` (§3.1). Nothing is added on the stretch. *(Rev 5.1, F23: at
  stage 2 one row is added on the cover ROUTE, §11.2; LEAN, OWNER QUESTION OPEN, §9 Q7.)*
- GONE with the slice: P1 (the 24-deep exact loop), P2 (the 48-deep horizon), P3
  (`MkLang.set[24][32]`, `uint8_t exact_len`), P4 (`PCREC_SPAN_WALK_SUBSETS`, a budget that
  never binds on a straight line; its cliff is P2's at 49, §2). GONE: M1 `KN_CAP`; M2 the
  sentinel (§3.1's outcomes); M3 the per-depth row cap (grown arrays); M6
  `pcrec_known_derive`.
- COUNTED: M4 `MkEnd` (its `k` and its sets).
- At stage 2: M5, the proof loop, reads the reply's WHOLE counted range (§11.1 B5); the
  seam's K1-K7 are the kit's call, and pcrec asserts its ceiling against the kit's three
  declared bounds at build time (§11.1 B2). Stage 1 reads them through C15; stage 2 re-reads
  C15 as the route's width limit (§11.2).
- Unchanged: P5 (256 byte values); M7-M9 (M8 is the hull's reach). Adjacent, not on this
  path: `PCREC_PREFIX_K_MAX`, `PCREC_MAX_REQ_RUN_SCAN`, `MF_MAX_BACK`.

## 9. For the owner (plain words)

**Corrections already given** (rev 3, unchanged): rev 2's "hidden limit near 511" was
wrong (today `a{48}` lists 24 positions and `a{49}` none); and keeping the cover of
`(?:[a-z]{0,3}\z|x)[0-9]{3}` is an earlier ruling (Z2 ruling 1, 2026-10-21, 0 differences
from libpcre2 in 66,243,390 cells, `docs/dev/lanes/z2build_report.md`), which rev 4 keeps.
**A new correction** of rev 3 heads question 2.

**Questions.**
1. **Reading the exact stretch from the compiled machine instead of the pattern's graph.**
   This changes what rev 2 told you. Rev 3 and rev 4 read it with the walk the cover already runs on
   the compiled matching machine, with its limit removed. It loses none of today's covers
   (rev 2 lost four), it gains 18 small test-pattern covers, the earlier ruling above
   stands, and about 430 lines of exploring code go. What it gives up: today two separate
   readings must agree before a cover is used; afterwards there is one reading, checked
   against PCRE2 and against a second form of the same machine in the test suite instead of
   on every compile. Also, the listing shows an exact span only where a PCRE2-based check can
   test it (covers and fixed-length-bounded patterns; nothing else reads those values
   today). Leaning: accept. **ANSWERED** (14:10, verbatim): "1. reading dfa for the span is
   fine. In my goal of partial span proofs that means either rebuilding the dfa on the
   remainder or editing out the proven span states." Accepted; the partial-proof routes are on
   [EARNED-SKIP]'s body (2026-11-15 owner note).
2. **The maximum span length you asked for.** First, a correction: rev 3 told you that
   past its 4096 limit "the first 4096 positions stay proven". That was false. The exact
   stretch is read from the compiled anchored matching machine, and pcrec already refuses
   to build that machine past 4096 states (an existing ceiling, measured in 2026 to keep
   compile time and artifact size in check). So rev 3's new limit could never be reached:
   a pattern of 4095 positions gets all 4095 proven, and a pattern of 4096 gets no machine
   and no proven positions at all; it runs exactly as it does today. The ceiling counts
   machine states, not positions, so a pattern with many different paths meets it sooner
   (`[ab]*a[ab]{12}`, whose matches are 13 characters long, does). Rev 4 therefore adds NO new number: the existing ceiling is the
   maximum span, about four times the longest stretch we test (1000), and a pattern past it
   is not made worse than today. Proving a FRACTION past it would need a different reading
   of the pattern, a later item. Leaning: accept the existing ceiling as the maximum, and
   no new limit. **ANSWERED AGAINST THE LEANING** (14:10, verbatim): "2. set in limits. If
   it's a user setting it could be shorter then adjusted by the user per artifact." Stage 2
   adds the limit (§11.2) with a per-compile option; how it is read is question 7.
3. **The earlier ruling** (the Z2 correction above): it stands under rev 4. Re-decide only if you
   would rather not cover that pattern. Leaning: keep it.
4. **One step or two** (from rev 1, answered by you: "leave that ordering step to you").
   Taken as two: step one changes only pcrec and covers up to 32 positions; step two needs
   the kit to accept spans up to 4095 positions. No question left.
5. **Size.** Stage 1 reports each mover's size beside its timing. If a long cover grows the
   matcher enough to lose in the cold-cache timing, the order is: one bounded try, then the
   kit, then you. Leaning: no action until the timing shows it.
6. **Build go for stage 1** (§3.1-§3.3 plus C15, §5 as the delivery bar), at opus tier,
   after the narrow readiness re-check that follows this revision.

7. **(Stage 2, rev 5.1; reply either way.) What does your span limit stop: the shortcut, or
   the proof?** You said "set in limits ... adjusted by the user per artifact". We read it as a
   limit on the SHORTCUT: a pattern whose every match is exactly N characters long, N up to the
   limit, is found by testing the N characters directly with no matching engine; a longer one
   is not shortcut at all and runs on the engine, exactly as it does today. Example, with the
   limit at 32: `[0-9a-f]{32}` (a 32-character hex id) takes the shortcut; `[0-9a-f]{33}`
   runs on the engine for all 33 characters. That is a CLIFF at the limit: one character more
   loses the whole shortcut, not one character of it. The alternative reading is a limit on the
   PROOF: the first N characters are proven and skipped, and the engine finishes the remaining
   ones. No cliff, but that is the "partial span" work you parked ([EARNED-SKIP]), so it would
   not come with stage 2. Consequences. Shortcut reading (leaning): stage 2 ships as designed;
   above the limit nothing changes from today; you raise the limit for an artifact that needs
   it (`--window-search-width=N`, §11.2.1); the no-cliff form waits for [EARNED-SKIP]'s
   trigger. Proof reading: stage 2's route limit still ships (it is what the engine-free
   shortcut needs), and [EARNED-SKIP] is un-parked to remove the cliff, which is a bigger
   build and comes after S4 by your 2026-11-11 ruling unless you move it. Leaning: the shortcut
   reading, with the cliff stated in the spec.
8. **(Asked ONLY IF the timing night's dense near-miss cells lose; §11.4.) Your class-run
   remedy, or one width for all?** The record of your remedy: "the remedy if slower is the
   class-run cover length (old exact length 24)" (journal 2026-11-15, session 132). One width
   for every shortcut would send the long LITERALS back to the engine too, though they win;
   a width only for character-class runs keeps them, but it is a special rule keyed on what
   the positions contain. Leaning: first ask the kit to render class runs so a near miss does
   not re-test the whole run (its reply to §11.5 ASK (3) is the general fix); your class-run
   width if that does not close the loss.
9. **FYI, a ruling of the manager's (2026-11-15):** the per-artifact option you asked for is
   added NOW with stage 2, not at the interface push (§11.2.1). Say if it should wait.

For main, not the owner: [DD-11.5]'s part 1 product (the span slice, Z2) is deleted by
stage 1, and its in-span `A_CTX` producer work has no remaining cover-path reader; its row
needs re-scoping. [DEC-LIMITS]'s trigger does not fire (a row is removed). The N row
(§1.1 (i)-(iii)) and the `PCREC_PREFIX_K_MAX` label row are main's to file.

## 10. What earlier revisions' parts survive

- KEPT: rev 1's bounds inventory (§8), the two stages and C15 (§3.5), the abi events
  (§4.4), the checks and sweep (§5), the re-timing (§7); rev 3's anchored-machine reading.
- REPLACED: rev 2's NFA-subset walk and rev 3's capped walk by §3.1's walk to
  `min(L, first accept)`; the C8 two-producer comparison by §3.6 Q2's controls.
- DROPPED: rev 2's kit ASK 2/ASK 3, FACT 3 and kit-bound list (C-24), "cliff near 511"
  (C-9) and four cover losses; rev 3's `PCREC_MAX_EXACT_SPAN`, outcome 4, plant (e) (R-1).
- Earlier dispositions: `docs/dev/reviews/2026-11-15-r2-covcap0.md`, `2026-11-15-r5-covcap-r2.md`,
  `2026-11-15-r6-covcap-r3.md`, `2026-11-15-r7-covcap-r4.md`.

## 11. STAGE 2 ADDENDUM (rev 5, lane covs2d; rev 5.1, lane covs2e; 2026-11-15; design only)

Owner's words this section answers (journal 2026-11-15, session 132, verbatim there): 14:10 "1.
reading dfa for the span is fine. In my goal of partial span proofs that means either rebuilding
the dfa on the remainder or editing out the proven span states. 2. set in limits. If it's a user
setting it could be shorter then adjusted by the user per artifact. 3. explain."; 14:35 the
long-span rendering direction (quoted in §11.3); 14:50 "Go on all stages"; 15:00 "I predict most
all rx will only have a short span and will inline due to being under the inline head portion of
the prover. Therefore, this issue is mostly moot". Rev 5's today-numbers carry their commands in
`docs/dev/lanes/covs2d_report.md` (TODAY NUMBERS, T-n). Rev 5.1 cites code at main `469d4205c`;
no file under `src/`, `lib/`, `cli/`, `memfn/` or `tests/` changed since review r13's build tree
(`git diff --stat b9b9e8635 main -- src lib cli memfn tests` prints nothing), so r13's line cites
hold and are re-used. `$PC51` below is main `469d4205c` built in lane scratch (`git archive main |
tar -x -C $PCREC_TMPDIR/scratch/covs2e/main`, then `nice make -j2 build/pcrec` there, rc 0).

PREMISE (held). The seam stops at 32 today: C15 `cc_fits` (`src/gen/known.c:332-337`) admits
`k <= MF_WSPAN_POS && k + 1 <= MF_WREACH && k < MF_MAX_FWD`, and `memfn/include/memfn.h` has
`MF_WSPAN_POS` = `MF_MAX_SPAN_POS` = `MF_MAX_TERM` = 32 (`:653`, `:302`, `:277`), `MF_WREACH` 64
(`:667`), `MF_MAX_FWD` 33 (`:315`) (T2). `a{32}` is `cover`, `a{33}` declines `statement-fits` at
`k` 33, `a{4095}` declines `statement-fits` at 4095, `a{4096}` reads `anchored-A` (T3). No
`limits.def` row bounds the cover ROUTE's width; the record's stretch is bounded by
`PCREC_ANCHORED_MAX_STATES` (`src/core/limits.def:186`, its `desc` says so since stage 1) (rev 5.1,
F31: rev 5's grep `grep -n COVER src/core/limits.def` was too narrow for its sentence).

### 11.1 The counted seam (what pcrec states, what changes on pcrec's side)

- **What pcrec states (facts, D157):** unchanged in kind from stage 1. One REPORT window site,
  span 0 of `k` exact positions `S_0..S_{k-1}`, `1 <= k <= 4095`, plus the context positions
  at -1 and `k` where they constrain (`cover_side_stated`). pcrec reads the per-offset proof
  over the reply's WHOLE counted range and checks it EQUALS the statement there (C14; B5 below).
  Nothing about repeats, runs or forms is stated: the kit sees repeated sets in the sets it is
  passed (D198 (b)).
- **THE SEAM IS THREE KIT BOUNDS (F3).** C15 today reads three: positions per span
  (`k <= MF_WSPAN_POS`), reach (`k + 1 <= MF_WREACH`: the after-context span sits at offset
  `k`, `known.c:594, 606`) and the proof range forward (`k < MF_MAX_FWD`: offset `k` must be
  proven). At stage 2 each must hold for `k` = 4095: positions per span >= ceiling - 1, reach
  >= ceiling, proof range forward >= ceiling, where ceiling = `PCREC_ANCHORED_MAX_STATES`
  (4096). §11.5 ASK (1) asks the kit to name all three.
- **READERS ON PCREC'S SIDE, and how the build finds them again.** Method (each is a command
  the build re-runs at its base; F2, F5, F10): `git grep -nE
  'MF_WSPAN_POS|MF_MAX_SPAN_POS|MF_WREACH|MF_MAX_FWD|MF_PROOF_LO|MF_MAX_TERM|MF_WMAX_SPAN' --
  src cli lib`; the WRITERS of `mf_wspan` fields (`git grep -nE 'w->(len|core_len|core_lo|set\[)'
  -- src`); readers of `MkEnd.k` and `mf_class` by layout (`git grep -nE '\bMkEnd\b|end\.k|e->k|mf_class\b'
  -- src`); mech rows whose plant text copies the code below (`git grep -nE
  'end\.|e->k|MF_MAX_FWD|MF_MAX_SPAN_POS' -- tests/mech/sabotages`); reference compilers that
  lower the ceiling (`git grep -n -- '-DPCREC_ANCHORED_MAX_STATES=' -- tests`). Today's hits:
  - `known.c`: `cc_fits` (`:332-337`), `cc_exact` and its copy (`:343-355`), `cover_window`
    (`:583-610`), `pcrec_cover_proof_diff` (`:649-660`), the `KITPROOF` trace `k=` (`:521`).
  - `known.h`: `MkEnd` (`uint8_t k`, `set[MF_MAX_SPAN_POS][32]`, `:22-30`); `PcrecCover.cls`
    (`mf_class` by value).
  - `memfn_sites.c` (pcrec's OWN span writers, F2): `pcrec_memfn_wspan` stores `len` and
    `core_len` as `(uint8_t)` (`:544`, `:548`), `pcrec_memfn_wspan_core` casts `lo`/`len` to
    `uint8_t` (`:553-554`), `pcrec_memfn_wpos_bits`/`_wpos_table` write `w->set[j]` with no
    bound on `j` (`:557-568`); `window_bounds_check` (`:584-602`, called from
    `pcrec_memfn_window_stated`); `MF_MAX_TERM` at `:630` (nterm bound) and `:948` (ADVANCE
    stride bound).
  - `emit_vm.c:234` `_Static_assert(MF_MAX_TERM >= VM_MAX_STRIDE, ...)`; `memfn.h:658`
    `MF_WMAX_SPAN MF_MAX_TERM` (F5: `MF_MAX_SPAN_POS` is defined AS `MF_MAX_TERM`, so a kit that
    raises the span bound by raising `MF_MAX_TERM` moves these too; a kit that decouples them
    ends the equality the PREMISE states. §11.5 asks which).
  - `emit_dfa.c`: `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS, ...)` (`:1446`); the
    proof diff's second caller, a compile FAIL (`:14495`); `scan_position + %d` from
    `cv->end.k` (`:14510`); `req_run_in_cover` (`:16278`).
  - `mf_class` held BY VALUE (F5): `CandAsked` (4 per record, `emit_dfa.c:7121`), a stack local
    (`:7157`), `CandScan.cls` (`:8443`) with 7 stack `CandScan` locals (`:8620, 8755, 9240,
    9991, 11280, 11489, 12171`), `mf_result.cls` (`memfn.h:1365`), `PcrecCover.cls`. Today a
    class is 41 x 32 = 1,312 B (`proven[MF_MAX_FWD - MF_PROOF_LO][32]`, `memfn.h:1340`); sized
    inline for 4,104 offsets it would be 131,328 B, and the compile's C stack budget is 442,368 B
    (`PCREC_COMPILE_STACK_BUDGET`, `limits.def:177`). How the kit carries the reply is the
    kit's; the fact goes to it (§11.5).
  - mech rows (F10): `S1131_cover_c8_skipped.sh:23` (SAB_AFTER writes `end.k` as `uint8_t` and
    `memcpy`s into `end.set`: rewritten to the pointer fill of A1), `S1148_cover_optional_position.sh:13`
    (anchors on `pcrec_memfn_wspan(&sp[0], 0, e->k, MF_VERIFY_YES);`, which B3 moves),
    `S1144`/`S1135` (anchor on `emit_dfa.c:14510`'s line), `S3220`/`S3223` (`REACH-WHY=
    [statement-fits]`, §11.2 readers).
  - reference compilers with a LOWERED ceiling (F14): `tests/codegen/run_anchored_match.sh:423`
    (§4b, `=6`) and `tests/endmark/run_b3_checks.sh:303` (§5, `=3`; S889's detector,
    `S889_lowered_overflow_refuses.sh:3`). No other test passes that `-D`.
- **THE ITEMS, SPLIT BY WHAT THEY WAIT FOR (F4).** `mf_class.proven` is 41 fixed rows,
  `mf_wspan.len` is `uint8_t` and `set[MF_WSPAN_POS]` is 32 rows (`memfn.h:1340`, `:671`,
  `:682`): until the kit's delivery is merged into pcrec's branch, no compile there can state a
  cover past 32, and every check past 32 is vacuous or red for the wrong reason.
  **A. Start before the kit's reply (pcrec's lane branch alone; route-identical to main at the
  default):**
  - A1. `MkEnd` stops copying: `k` becomes `uint16_t` and `set` points at the cover record's
    arena sets (§3.3), so `cc_exact`'s copy and its READY-3 internal error go
    (simplification). `req_run_in_cover` reads the same pointer. S1131's plant is rewritten to
    the pointer fill.
  - A2. The width limit's `limits.def` row, its `limits.h` wiring and range assertion, the
    registry 81 -> 82, `limits.md` section 3.12 (new), and the two lowered-ceiling reference builds' extra
    `-D` (§11.2).
  - A3. The per-compile option: field, CLI, library refusal, spec hunks (§11.2.1).
  - A4. The `why` rename `statement-fits` -> `width-limit` and its readers (§11.2).
  - A5. The kitproof loader: the `W` FLAGS letter and the `@D`/`@D1` and `width=N` forms
    (§11.6.2).
  - A6. The prediction tooling re-pointed (`docs/dev/lanes/covs1_evidence/predict.py`, read
    in place; it must read the baseline's `statement-fits` and the candidate's `width-limit`
    as the same conjunct C15).
  - A7. The sabotage rows that need no long cover: the bypass row (S3223 re-aimed) and the
    off-by-one row, both at the default (§11.6.3).
  **B. Wait for the kit's reply, on the COMBINED branch** (pcrec's lane branch with the kit's
  delivery branch merged in; the manager names it at the stage-2 build go):
  - B1. pcrec's own span writers (F2): the width type holds 4095 (the kit's carrier type), and
    `wpos_bits`/`wpos_table` check `j` against the span's length before the write (a named
    internal error), so a long statement can never truncate or overrun silently.
  - B2. The seam assertion (F3, F18): ONE `_Static_assert` (never `#if`: the ceiling is an
    `enum` at the default, `limits.h:723`, and evaluates to 0 in `#if`), beside `cc_fits` in
    `known.c`: `PCREC_ANCHORED_MAX_STATES - 1 <=` the kit's declared positions per span,
    `PCREC_ANCHORED_MAX_STATES <=` its declared reach, and `PCREC_ANCHORED_MAX_STATES <=` its
    declared proof range forward. A `-D` raise of the ceiling past the seam fails the BUILD,
    never a compile.
  - B3. `cover_window` states the counted span through the kit's new carrier; its length check
    stays FIRST (R-13), now against the kit's declared bounds, still a named internal error.
  - B4. `window_bounds_check` (F3; rev 4's §4.2 sentence, restored): a cover alternative is
    checked against the kit's new declared bounds (span length and reach, the after-context
    span at offset `k <= 4095` included), every other window site against the bounds it is
    checked against today.
  - B5. `pcrec_cover_proof_diff` compares the reply's WHOLE counted range (F1): for every
    offset `d` in it, `want` is `S_d` for `0 <= d < k`, the stated context at -1 and `k`, and
    ALL ONES everywhere else, every `d > k` included. The reply's range must reach `k + 1`
    (offset `k` included); a shorter range is a named internal error ("the kit's proof range
    ends at offset %d, before the cover's after-context at %d"), never a narrower comparison.
    Rev 5's `[MF_PROOF_LO, k + 1)` is struck: today's loop runs to `MF_MAX_FWD` and wants all
    ones past `k` (`known.c:649-660`), so a kit text that tests a byte past the after-context
    reads `under@d`/`over@d` and declines C14 (or fails the compile, `emit_dfa.c:14495`);
    rev 5's range would never look there, and a kit over-read at `k + 1` would silently drop
    matches.
  - B6. The `MF_MAX_TERM` readers and the by-value `mf_class` holders, as the kit's reply
    decides (coupled or not; inline or not).
  - B7. Every check past 32: the `n >= 33` kitproof rows, the `test-axes` arm, the compile-cost
    record, the proof-range sabotage rows (§11.6.3).
  - Unchanged: the other window sites state what they state today; the sweep proves them
    identical.
- **abi events.** ONE pcrec `abi` event (108 -> next) at the JOINT landing (§11.6.1): the kit's
  bytes move with it (D146/D147) and the identity gate re-pins (§4.4, D94's grep of every
  reader of the current number). Whether the kit's carrier change is an `MF_SITE_ABI` event is
  the kit's to say. The plan of record lands ONCE with the measured default (§11.6.1, F16); only
  the fallback (land at 32, then move the default) costs a second `abi` event (its corpus
  movers move the identity gate's (B) pins). The per-compile option adds no emitted scaffolding
  (§11.2.1) and is not an `abi` event of its own.
- **Answer identity.** The checks of §5.1, run at the stage-2 build, plus:
  - the kitproof `answer` rows at `n >= 33` that stage 1 deferred (§5.3), on the `W` arm (the
    option at the ceiling less one), so they cover whatever the default is;
  - one `test-axes` arm: the whole corpus with `--window-search-width=` at the ceiling less one
    against the default run (beside `tests/axes/run_axes.sh`'s INTERNAL_ARMS); for every `k`
    above the default the default run IS the engine route, and the existing
    `--memfn=no-window-search` axis still covers covers at or below it. The option is a
    `pcrec_options` field, and every compound part compiles with a copy of its parent's
    options (`src/core/compound.c` `part_compile`: `o = *parent`), so the arm reaches part
    covers with no threading (F12; rev 5's harness lever would not have: `.harness = NULL`,
    `compound.c:74`). The build confirms it with one trace compile of a compound whose part has
    a stretch of 33 or more (its `KITPROOF` part line reads `cover` under the option);
  - compile cost, a RECORDED measurement (F11), numbers into the build's report, no verdict
    beyond one criterion: for `a{4095}` and `[0-9a-f]{1000}`, both encodings, on the `W` arm
    and the default: pcrec's CPU and max RSS (`scripts/watchdog -s 120 -m 4g -c 120 -S covcost2
    -- $PC -p rx --features all --emit-main -o OUT --pattern P`; the limits are kill switches,
    not budgets), emitted C bytes against `PCREC_MAX_EMIT_BYTES` (1,000,000) and the 250,000
    warning, and `gcc -O2 -c` time, RSS and `.text` on the emitted file. Reference points,
    UNMEASURED for the kit's real form: review r13 READYSEAM-9's synthetic all-inline chain
    (4,094 terms: `gcc -O2` 2.56 s, 232 MB, `.text` 124,663 B) and today's ~151 emitted C bytes
    per position (`$PC51 -p rx --features all -o hex24.c --pattern '[0-9a-f]{24}'` 17,710 B,
    `{32}` 18,918 B), which puts `a{4095}` near 620 KB of C by linear extrapolation, above the
    warning and below the cap. CRITERION: a legal width whose compile FAILS (the size cap or a
    kill) is a finding for the kit (its form's per-position cost), listed in the report and
    filed, not a silent fallback. `req_run_in_cover`'s loop costs O(k + len^2 x 256) with
    `len <= PCREC_MAX_REQ_RUN_SCAN` (32) (`emit_dfa.c:16278-16284`: placements not containing
    `m` are skipped before the inner loops; rev 5's "k x run length x 256" was false, F11) and
    needs no witness;
  - ASan `run_cover.sh` (the counted arrays), and the REACH-only sabotage matrix.
- **The prediction (stage 1's check, re-pointed).** From the BASELINE (main before stage 2)
  listing's `cover` section, no trace build needed: INTO the cover, every row whose `why` is
  `statement-fits` with `k` <= the stage's width default (an UPPER bound: C9-C14 never ran on
  them; e.g. `a{40}(?:b|cc)` reads `statement-fits` at 41 today (T3) and will decline at
  C10). OUT: none while the default is >= 32; with a default below 32, every baseline
  `cover` row with `k` above it. Each predicted-but-unmoved row is listed with the
  candidate's `why`; LOST or UNEXPLAINED is red (`predict.py` as at stage 1, A6). At default 32
  the INTO set is empty by construction (stage 1 admits every `k <= 32`), so the prediction is
  "no artifact moves", and any move is red. Non-cover window sites: no predicted move; any
  move is red.

### 11.2 The per-artifact cover width limit

- **What it bounds (LEAN, OWNER QUESTION OPEN: §9 Q7; F23).** The cover ROUTE only: C15
  declines a cover whose `k` exceeds it, and that pattern runs on today's route (the engine),
  as `a{33}` does now. The walk, the record and the listing are not bounded by it:
  `exact_len` and the sets are still stated in the listing up to the state ceiling. THIS IS A
  CLIFF, stated plainly: with the limit at 32, `[0-9a-f]{32}` takes the cover and
  `[0-9a-f]{33}` runs the engine for all 33 positions; one position more loses the whole
  cover, not one position of it. It is NOT D198 Consequences' limit "shared by the walk, the
  cover and the seam, with no cliff: past it the first positions up to the limit are still
  stated" (that sentence was written for rev 3, whose new limit rev 4 deleted; the D198
  addendum the manager files records the change). The no-cliff form, "prove the first N
  positions, the engine finishes the rest", is [EARNED-SKIP]'s (PARKED; its trigger is
  lookaround-as-run landing and then a bench cell where the engine's finish is a measurable
  share), not a stage-2 item.
- **Where.** One `src/core/limits.def` row (F26 unit, F28, F29):

      PCREC_LIMIT(PCREC_DEFAULT_WINDOW_SEARCH_WIDTH, 32, "positions", "selection knee", FLAG_D, "3.12",
        "[COVER-CAP]: the widest fixed-width match the window search reports with no matching engine (the cover route); a wider one runs the engine; --window-search-width=N moves it per compile, -D moves the built-in default; UNMEASURED: stage 1's seam reach, kept so the stage-2 build is route-identical to main until the timing of cover_cap.md section 11.4 sets it", LIMITS_H)

  Home `LIMITS_H` with an `#ifndef` wiring block in `limits.h` (the FLAG_D shape; the six
  existing blocks follow `limits.h:723`) and its derivation block there once measured (as
  `[ENG-ABS]`'s is). Override `FLAG_D` (renders `flag+-D`): a caller-facing option moves it
  per compile, a `-D` at pcrec's own build moves the built-in default. Anchor `3.12`: a NEW
  `limits.md` section 3.12 (new) "The window search's width", caller-facing (the owner asked for a user
  setting; `limits.md` §1's scope is what pcrec promises a caller), stating the default, the
  cliff with its example, the option and the legal range; `tests/registry/limits_check.sh`
  then checks the value at that section (an anchored row) and its count 81 -> 82 and name list
  (`:182`). `--list-limits` shows the SHIPPED literal, not a `-D` build's value
  (`src/dump/limits_dump.c:113-114` prints the row's own `value` token, as for every `-D`
  row): a `-D` build is the builder's own record (F28).
- **Legal range and refusal (F14, F18).** `1 .. PCREC_ANCHORED_MAX_STATES - 1` in force in the
  build (4095 at the shipped ceiling); widths above it are unreachable (the walk ends by
  then) and are refused, never clamped (no silent default). At pcrec's build: a
  `_Static_assert(PCREC_DEFAULT_WINDOW_SEARCH_WIDTH >= 1 && PCREC_DEFAULT_WINDOW_SEARCH_WIDTH <=
  PCREC_ANCHORED_MAX_STATES - 1, "PCREC_DEFAULT_WINDOW_SEARCH_WIDTH must lie in 1 ..
  PCREC_ANCHORED_MAX_STATES - 1")` after the wiring block (an `#if` would read the `enum` as 0
  and `#error` every build). Per compile: §11.2.1. READERS THIS MAKES (F14): the two
  lowered-ceiling reference builds (`run_anchored_match.sh:423`, ceiling 6;
  `run_b3_checks.sh:303`, ceiling 3) would fail the assertion at the unchanged default 32;
  each ALSO passes `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=<ceiling - 1>` (5 and 2), and S889's
  detector keeps building. The build re-runs `git grep -n -- '-DPCREC_ANCHORED_MAX_STATES='`
  for any third.
- **Name (D174, behaviour; F26 spelling, the manager's call).** `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH`
  / `--window-search-width=N` / `pcrec_options.window_search_width`: "window search" is the
  caller's shipped word for this route (`tuning.md` §2.43¶3d, `--memfn=no-window-search`), so
  the option joins that spelling rather than adding a third noun (rev 5's "window match"; the
  working deny name `PCREC_NO_WINDOW_REPORT` is [IFACE-PUSH]'s to settle). It is not spelled
  `max_*`: the `max_*` option fields are raise-only caps (`lib/CLAUDE.md`), and this one may be
  lowered. No collision: `git grep -n -i 'window.search.width\|WINDOW_SEARCH_WIDTH' main -- src
  cli lib docs/spec memfn/include tests` prints nothing. C15 keeps its id; its name becomes
  `width-limit`, kind `limit`.
- **Readers of C15's name (F6), found by `git grep -n statement-fits -- . ':!docs/dev/history'
  ':!docs/dev/reviews' ':!docs/dev/lanes' ':!docs/dev/dev_journal.md'`:** compared VALUES:
  `tests/kitproof/cases.tsv:65` (`facts a{40}(?:b|cc)`) becomes `width-limit|41|41|...` and
  `:72` (`facts a{4095}`) becomes `width-limit|4095|4095|...` on the default arm (both rows stay
  on the default arm; their `W` twins are new rows, §11.6.2); `S3220_cover_walk_length_bound.sh:12`
  and `S3223_cover_c15_removed.sh:12` (`REACH-WHY=[statement-fits]` -> `[width-limit]`). Text:
  `cases.tsv:38-48` (notes), `known.c:349` (the error text, which A1 deletes), `:439` (comment:
  "retires like C2", stale), `:455` (the table row), `docs/design/kit_proof.md:239` (C15's row,
  "stage 1 only"), `facts_listing.md` §4.5¶2's example list (one word; the `why` vocabulary is
  advisory, no `abi` event), `docs/dev/lanes/covs1_evidence/predict.py` (A6). History
  (`abi_changelog.md`) keeps its spelling.

#### 11.2.1 The per-compile option (F21, MANAGER RULING 2026-11-15)

Added NOW, the usual way, by the path `--unroll=K` (`unroll_k`) and `--vm-entry-shape=N`
(`vm_entry_shape`) took; no flag bit is spent.

| item | `--window-search-width=N` | precedent at main |
|---|---|---|
| library field | `int window_search_width;` in `pcrec_options`, `0` = the built-in default `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH`; `pcrec_default_options` sets 0 | `unroll_k` (`lib/pcrec.h`, `PCREC_UNROLL_K_DEFAULT` = 0) |
| CLI | `--window-search-width=N`, parsed in `cli/main.c` beside `--unroll=` with `cli_int_value(a + 22, 1, PCREC_ANCHORED_MAX_STATES - 1, &v)` | `--unroll=` (`cli/main.c:1419-1427`), `--vm-entry-shape=` (`:1435-1450`) |
| refusal (CLI) | `cli_err("--window-search-width wants an integer in %d..%d (got '%s')", 1, PCREC_ANCHORED_MAX_STATES - 1, ...)`, the same exit path as `--unroll=`'s | `--unroll wants an integer in 1..4096 (got '%s')` |
| refusal (library) | a field outside `0 .. PCREC_ANCHORED_MAX_STATES - 1` is a malformed option: `pcrec_compile` returns -1 with `invalid window_search_width %d (1..%d, or 0 for the built-in default)`, never clamped | `src/core/compile.c:2074-2094` (an out-of-range `tune`, the part-layout controls) |
| override order | an explicit option (field != 0) wins; else a dial cell, if one is ever measured (none at stage 2; §11.7 unlock 1), and an explicit spelling beats the dial (`limits.md` §8b¶2's rule for `--vm-entry-shape=N`); else the `-D` build default; else the row's literal | `--vm-entry-shape=N` over the dial |
| deny | `--memfn=no-window-search` still declines the cover row at any width | `tuning.md` §2.43¶3d |
| compound parts | inherited by construction (`part_compile` copies the parent's options) | every option field |
| `.rxt` | no line (neither precedent has one); a `.rxt` `config` line is a later item if asked | — |
| stamp | NONE (MANAGER DECISION OPEN, lean none): the outcome is already stamped (`<PREFIX>_DFA_SCAN "cover"` or not, `match_api.md` §6.3.4¶2) and the listing's `cover` row names `width-limit` with `k`; the precedents stamp because their value moves a surface nothing else records (`<PREFIX>_UNROLL_K` explains `.subject_ceiling`). With no stamp the option moves no byte at the default and, at any value, only the artifacts whose route moves | `<PREFIX>_UNROLL_K`, `<PREFIX>_VM_ENTRY_SHAPE` |
| `abi` | not an event of its own (no scaffolding change); the joint landing's one event covers stage 2. A stamp, if the manager rules one, would be scaffolding on every DFA artifact and would fold into that same event and its re-pin | D76/D94 |
| `rx_info.flags` | not a bit: nothing to mask | `tuning.md` §2¶3 |
| spec (D80), same change | `tuning.md`: a new section 2.56 `--window-search-width=N` (answer-identical; the cliff; the deny; the dial rule), its row in §2¶4's table (bit —, default the row, class answer-identical, `rx_info.flags` —, stamp `<PREFIX>_DFA_SCAN`), its row in §4's field table, one pointer from §2.43¶3d; `limits.md` section 3.12 (new) (new, anchor `3.12`) and its line in the contents; `match_api.md` §8.2's `pcrec_options` listing gains the field and §6.3.4¶2's `"cover"` row gains "up to the window search's width (`tuning.md` section 2.56 (new))"; `facts_listing.md` §4.5¶2's one word; the `abi` changelog entry. `cli.md` §1.18 names the valued axes generically ("`--unroll=K`, and similar"): no hunk | `tuning.md` §2.10, §2.21, §4; `limits.md` §8a |
| limits table row | the row above, anchor `3.12`, override `FLAG_D` | `PCREC_DEFAULT_UNROLL_K` (`limits.def:170`, FLAG), the FLAG_D size rows |
| `--help` | not listed (a tuning axis, `cli.md` §1.18); `cli/CLAUDE.md` gains its per-flag line | `--unroll=K` |

**The test-only lever is DROPPED.** The option serves every check rev 5 gave the lever: the
kitproof `W` rows (§11.6.2), the `test-axes` arm (§11.1), the compile-cost record and the
timing cells (§11.4), and it reaches compound parts where the lever would not (F12). Nothing
needs a lever-fence entry: the spelling is public.

**D27 (review r13, RECOMMENDED, small):** one spec-first author for this contract once the
spec hunks exist: refusal of out-of-range values at build and at the option, the `width-limit`
`why` at `k` = default + 1, route identity at the default.

- **How the default is chosen (measured, never presumed; F16, F17, F19, F20).** Rule, one
  declared row, applied to §11.4's COUNTED cells (a cell counts only if its candidate artifact
  at the measuring setting reads `RX_DFA_SCAN "cover"`; a declined cell leaves the rule and is
  listed, it never counts as "not slower"): the default is the LONGEST counted width `w` such
  that no counted cell of width `<= w` is SLOWER (§11.4's procedure) in ANY regime. Widths
  above the longest counted cell are unmeasured and so off by default: the user raises the
  limit for them (`--window-search-width=N`). With §11.4's cells the counted widths are 24
  (the stage-1 movers' 24-position twins, added so 24 is reachable), 31, 32, 36, 40, 64 and
  500, so the rule can land at ANY of them, below 32 included: 24 if a 31 or 32 cell is
  slower and the 24 cells are not; 31 if only the 32-wide class cells lose (then untimed class
  covers of width 25..31 ride along, the case §9 Q8 is for). If a 24-wide cell is itself
  slower, NO width qualifies: the EMPTY outcome, the owner's call (§11.4 table), interim
  default 32 (rev 5.1, F17: rev 5's "it would land at 24 or below" was outside its own rule,
  which could reach only 31, 32, 36 or 40, or nothing). Size is reported beside each timing
  (G6) and is the owner's to accept once (§9 Q5); it does not enter the rule.
  - The value the build uses before §11.4 runs: 32, labelled UNMEASURED in the row (above):
    stage 1's seam reach, so the combined branch is route-identical to main. That 32 is
    today's behaviour, not a tuning claim, and the plan of record replaces it BEFORE landing
    (§11.6.1).
- **EMITTED-2 and the owner's remedy (F25).** The record, verbatim (journal 2026-11-15,
  session 132 afternoon entry; the manager's record of the owner's ruling, not his own
  words): "EMITTED-2 (x6.65 instructions for a 32-position class cover on dense near misses):
  with Frank, LAND then time; the remedy if slower is the class-run cover length (old exact
  length 24)." The width limit meets it only BLUNTLY: it is one width for every cover, so
  lowering it to 24 also sends the winning long literals (`lit-l31`, `lit-l40`: the
  instruction counts of [COVER-CAP]'s skipmeas block) back to the engine. A class-only width
  keeps them. Whether that is a special case keyed on what the positions hold (memory
  `pcrec-general-mechanisms-not-special-cases`) or the owner's measured remedy is the OWNER's
  to rule: §9 Q8, asked ONLY IF §11.4's dense near-miss cells lose. Order meanwhile: the
  one-pass rule (memory `pcrec-one-pass-loss-chasing`), then the kit, whose reply to §11.5 ASK
  (3) is the general form of the fix (a near miss need not re-test the whole run; the kit
  holds the fact, ideas log 2026-11-15), then §9 Q8. Leaning: the kit's rendering first; the
  owner's class-run width if that does not close the loss.

### 11.3 Long-span rendering is the kit's (the owner's direction, quoted)

Frank, 2026-11-15 14:35, verbatim: "we have a performance dial for pcrec. it could include some
options for the kit. Also, I would default to sub span loops (excepting the measured head
inline ) then measure if inline was faster than the other way around. Measure three: all
inline, all loops, header inline then loops. Then the speed dial option can be always inline
should it prove that is faster". This is the OWNER's direction to the kit, carried in the
request (§11.5) as his words; pcrec designs no form, states no run and names no method
(D157). It amends D198 (e) ("the kit is told facts, never asked to compact") for this request,
by the owner (F24): a later reader of D157/D198 reads §11.5's quoted direction as his, not as a
pcrec method. The measurement stays small (15:00, "mostly moot"): the long tail is the few
dozen patterns at 25+ positions among 1,852 covering compiles (§2 census, before stage 1).
Stage 1's size step, from `[0-9a-f]{24}` to `{32}`, is +208 bytes of `.text`, about 26 bytes per
position (F30; command: `$PC51 -p rx --features all -o hexN.c --pattern '[0-9a-f]{N}'`, then
`gcc -O2 -std=gnu11 -c hexN.c` and `size -A hexN.o`'s `.text`: 1,752 at 24, 1,960 at 32; review
r13 PREMISE-4 read 2,695 -> 2,903 by another emit command; the +208 delta holds on both), so an
all-inline `[0-9a-f]{1000}` would be about 26 KB of `.text` by linear extrapolation (UNMEASURED;
READYSEAM-9's synthetic chain gave ~30 B per position). The three forms' cards and their lengths
are the kit's (memory `pcrec-new-method-needs-measurement-card`).
THE DIAL IS LIVE (F22): `--tune=N` (`tuning.md` §5) ships, and its policy table (§5.4) already
carries `limits.def` selection knees as cells and states that a dial cell may set a row a caller
cannot spell (§1¶9); its λ "kit" row is the class-matcher kit (`clskit`), not the memfn search
kit. So: the width limit is a candidate §5.4 knee row once §11.4 measures a rate (§11.7 unlock
1); the owner's "speed dial option ... always inline" is a dial cell when the kit's cards show
inline faster (unlock 2), not a `--memfn=` value.

### 11.4 The timing plan: stage-1 owed + stage 2, one night

ONE night window, cleared with the owner, outside 20:00-01:00, at the box's quietest, on the
COMBINED branch before the joint landing (the plan of record, §11.6.1).
- **A. Stage 1 (owed), as a BUNDLE:** main before stage 1 (91bae2d98) against main with it
  (95 commits, abi 107 -> 108; MEASURE-6), its movers (`lit-l31`, `hex32`, `dig-exact-32`,
  `hex32-id`, both encodings), as §7. The A/A non-mover cell is timed on the same two
  binaries, so the bundle's non-cover drift shows there.
- **B. Stage 2:** the combined branch's build, each cell with `--window-search-width=` at the
  ceiling less one against the same binary's `--memfn=no-window-search` (the engine route):
  `lit-l40`, `loglines/uuid`, `wild-validator-uuid-grok`; the stage-1 movers' 24-position
  TWINS (a 24-byte literal, `[0-9a-f]{24}`, `\d{24}`; the bench dev names the cells; F17);
  two SYNTHETIC long cells, `[0-9a-f]{64}` and `a{500}` (F16: so the rule's admissible range
  reaches past 40 where the 4095 seam's population is); both encodings. These cells and A's
  set §11.2's default. B is "cover route versus the engine route INCLUDING its prefilter and
  required-run sites", not one variable (F15): declining the cover moves `RX_DFA_SCAN` (cover
  -> unanchored), `RX_DFA_START`, `RX_DFA_PREFILTER`, `RX_REQ_WHY`, `RX_REQ_HANDOFF`, adds a
  forward DFA and removes the kit's span site (review r13 MEASURE-5 on `lit-l31`: 21,993 vs
  32,965 C bytes). That is the intended A/B (the route as a whole); the axes are named so no
  win is explained by one of them alone (memory `pcrec-speed-compare-apples-to-apples`).
- **Regimes, each cell in each:** hit-dense; DENSE NEAR-MISS (review r9 EMITTED-2's
  witnesses: `dig-exact-32` on 31 digits + a letter, repeated; `hex32` on digit runs; for the
  other cells, the same shape: the pattern's `k - 1` positions then a miss); NOT-WARM (the
  matcher not in L1/L2, method the bench dev's, D198 (f)); miss-heavy throughput;
  `short-subject-search`. A/A controls: `lit-l16` and one non-mover engine cell, in every
  regime. A cell missing any regime is VOID for the rule (never "not slower").
- **Size beside each timing:** emitted C bytes and `gcc -O2` `.text` per cell, both routes.
- **The procedure (F20).** Unit: the bench's wall-clock time metric, which the rule reads;
  instructions:u (EMITTED-2's unit: 230.7 M engine vs 1,534.8 M cover) are reported beside,
  never ruled on (an instruction ratio and a time ratio can disagree on dense near misses).
  Each cell: the bench's standard launch count, at least 5 launches; statistic: the median.
  NOISE FLOOR: the largest |median ratio - 1| among the night's A/A cells, over every regime.
  SLOWER: a cell's median ratio (cover over engine) exceeds 1 + floor in some regime. One
  outlier launch is absorbed by the median. BIMODAL (the bench's report flags it, or the
  launches' spread exceeds twice the floor): the cell is VOID and re-run once; void twice reads
  SLOWER (conservative). The bench's own field names for these (its verdict and spread
  fields, e.g. `inconclusive-load`) are a bench-only question relayed to the bench dev
  (memory `pcrec-ask-bench-dev`).
- **The three rendering forms** (§11.3): the kit's cards, on the kit's harness; not part of
  this night unless the kit asks for a slot (they are kit timing, the kit's window request).
- **Outcome table (declared, FIRST MATCH; F19).** The interim default, wherever a row says
  "owner's call", is 32: route-identical to landed main, which the owner accepted as "land,
  then time".

  | # | when | then |
  |---|---|---|
  | 1 | an A/A cell reads slower than another beyond the bench's own validity verdict (`inconclusive-load` or its equal), or the floor is not computable (an A/A cell missing) | night VOID, re-run; nothing is set |
  | 2 | a rule cell is missing a regime, or is void twice (procedure) | that cell VOID; re-run it; the rule waits for it |
  | 3 | a cell's candidate artifact does not take the cover at the measuring setting | the cell leaves the rule, listed with its `why` |
  | 4 | no counted cell is slower in any regime | default = the rule's value (the longest counted width) |
  | 5 | some counted cell is slower, and the rule's set is not empty | default = the rule's value (it excludes the slower widths); size reported beside each slower cell; if a slower cell is a stage-1 class cover slower in near-miss: also §11.2's EMITTED-2 order (one-pass, kit, then §9 Q8); stage 1 stays landed meanwhile (owner: "land, then time") |
  | 6 | the rule's set is empty (a 24-wide cell is slower) | owner's call; interim default 32; stage 1 stays landed; §11.2's EMITTED-2 order runs |

  A not-warm loss has no row of its own (rev 5's row 3 conflicted with the rule): it is a
  slower cell like any other (row 5 or 6), with its size beside it for the owner's G6 call.

### 11.5 KIT REQUEST DRAFT (for the manager to file as R-n, next after R-44, after the readiness re-check; facts only)

> **R-n (DRAFT, pcrec manager) — window spans of up to 4095 positions ([COVER-CAP] stage 2)**
> - GO: the owner's build go covers stage 2 ("Go on all stages", Frank 2026-11-15); pcrec's
>   stage-2 design (cover_cap.md §11, rev 5.1) passed its critic round (r13) and a readiness
>   re-check before this request was filed.
> - FACT (statement). pcrec states one REPORT window site per cover: span 0 of `k` exact
>   positions, `1 <= k <= 4095` (4095 = pcrec's anchored-machine ceiling, 4096 states, less
>   one), with a context position at -1 and at `k` where they constrain. Today the statement
>   stops at 32 positions.
> - FACT (the three bounds pcrec relies on). Today pcrec admits a cover only where all three of
>   your bounds hold: `k <= MF_WSPAN_POS` (positions per span), `k + 1 <= MF_WREACH` (the
>   after-context span sits at offset `k`), `k < MF_MAX_FWD` (offset `k` is inside the proof
>   range). For `k` = 4095 that is: positions per span >= 4095, reach >= 4096, proof range
>   forward >= 4096. pcrec will assert its ceiling against all three at its build time.
> - FACT (how pcrec reads the proof). pcrec compares the reply's WHOLE counted proof range with
>   its statement: the stated set at each of offsets 0..k-1, the stated context at -1 and `k`,
>   and "nothing proven" (all 256 bytes) at every other offset, every offset past `k`
>   included. A reply whose range ends before offset `k` is a pcrec internal error.
> - FACT (how pcrec holds the reply). pcrec holds the reply's class record (`mf_class`) BY
>   VALUE: in its cover record, four per `CandAsked` record, in `mf_result`, and on the C stack
>   in 8 places (one local and 7 `CandScan` locals in `src/gen/emit_dfa.c`). Today the record is
>   41 offsets x 32 B = 1,312 B; at 4,104 offsets x 32 B it would be 131,328 B each, against
>   pcrec's compile stack budget of 442,368 B (`PCREC_COMPILE_STACK_BUDGET`).
> - FACT (coupling). `MF_MAX_SPAN_POS` is defined as `MF_MAX_TERM`, and pcrec reads
>   `MF_MAX_TERM` at three sites of its own (the VM stride assertion, the term-count bound, the
>   ADVANCE stride bound); pcrec needs to know whether they stay equal.
> - FACT (population, census of 11,738 compiles, both encodings, before pcrec's stage 1).
>   1,852 compiles took the cover; almost all are short. Beyond 32 today: `k` = 36 (two uuid
>   shapes), 40, 49, 60, 500, 1000, mostly runs of one byte class; the bench's are `lit-l40` and
>   two uuid shapes. pcrec states no span longer than its width limit: such a pattern runs
>   pcrec's engine route. The limit has a built-in default (32 until pcrec's stage-2 timing
>   sets it, before the joint landing) and a per-compile option up to 4095
>   (`--window-search-width=N`, `pcrec_options.window_search_width`).
> - FACT (cost, stage 1). `[0-9a-f]{24}` -> `{32}` cover: `.text` +208 bytes, about 26 per
>   position (gcc 15.2 `-O2 -std=gnu11 -c` on pcrec's default emit, `size -A`; 1,752 -> 1,960
>   by that command). Review r9 EMITTED-2: `dig-exact-32` on (31 digits + `g`) repeated,
>   instructions:u 230.7 M (engine route) vs 1,534.8 M (cover), x6.65; +14 % on `z`*n. The
>   statement gives every position's set.
> - OWNER DIRECTION (Frank 2026-11-15 14:35, verbatim; his direction to the kit, amending
>   D198 (e) for this request): "we have a performance dial for pcrec. it could include some
>   options for the kit. Also, I would default to sub span loops (excepting the measured head
>   inline ) then measure if inline was faster than the other way around. Measure three: all
>   inline, all loops, header inline then loops. Then the speed dial option can be always inline
>   should it prove that is faster". And (15:00): "I predict most all rx will only have a short
>   span and will inline due to being under the inline head portion of the prover. Therefore,
>   this issue is mostly moot". Size the measurement to that. pcrec's dial (`--tune=N`) is
>   live and can carry a kit option as a cell once your cards show one faster.
> - ASK. (1) Can the statement and the reply carry spans up to 4095 positions? Name the three
>   bounds you declare (positions per span, reach, proof range forward) and the reply's counted
>   proof range. (2) Do `MF_MAX_SPAN_POS` and `MF_MAX_TERM` stay equal? (3) The three forms'
>   cards per the owner's direction, at lengths of your choosing within the population above.
>   (4) Your reading of the dense near-miss regime above (no form asked). Reply in
>   responses.md with the form you choose before building.
> - Deliver: a kit branch for merge review, for ONE joint landing with pcrec's stage 2.

### 11.6 Staging, sabotage, and what stage 2 is not

#### 11.6.1 Order (plan of record; F16, F4)

(1) The short readiness re-check of rev 5.1; then file §11.5; the kit replies with its form.
(2) In parallel: the kit builds its branch; pcrec builds the A items (§11.1) on its lane branch,
route-identical to main at the default 32. (3) The COMBINED branch (pcrec's branch with the
kit's merged in; the manager names it): the B items, then every check past 32. (4) Code round
on both. (5) §11.4's night on the combined branch. (6) The default set by §11.2's rule: one
`limits.def` value, its `desc`'s derivation (UNMEASURED label replaced), `limits.md` section 3.12 (new)'s
number, the movers' re-pins. (7) Joint landing: ONE `abi` event, with the measured default.
FALLBACK (a manager choice, if the night cannot run before (4) clears): land at 32 UNMEASURED,
time on landed main, and move the default in a second `abi` event. No generated witness needs
re-pointing when the default moves (§11.6.2); the movers' pins do.

#### 11.6.2 The kitproof loader (F7, F13)

- FLAGS letter `W`: `--window-search-width=<ceiling - 1>`, the ceiling read from the shipped
  `build/pcrec --list-limits` (`PCREC_ANCHORED_MAX_STATES`, 4095 = 4096 - 1); `run_cover.sh`'s
  `flags()` (`tests/kitproof/run_cover.sh:40-46`) maps it and the build cache keys on it
  (`:58`). `cases.tsv`'s header names it.
- `@D` / `@D1` in a PATTERN: the loader substitutes the shipped default and default + 1, read
  from `--list-limits`' `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH` row (the shipped value is the
  test build's; F28's caveat is for `-D` builds). The at-default and past-default witnesses
  are spelled so (`[0-9a-f]{@D}`, `[0-9a-f]{@D1}`, and the literal pair as `@D`/`@D1`
  letters), so a moved default moves them with no edit. They replace the literal rows `:37`,
  `:38`, `:44`, `:45` (32 and 33).
- `width=N` as a `verdict` VALUE: expected `cover` iff `N <=` the shipped default, else
  `decline`; the other literal-width verdict rows (24, 25, 40, 100, 1000; `:35-36`, `:39-43`,
  `:46-48`) and the `\b[0-9a-f]{n}\b` and `\d{32}` rows (`:49-52`, `width=` their `k`) carry
  it, so none goes red when the default moves. Each gets a `W` twin expecting
  `cover` where the machine holds the pattern (n 33..1000: 4 literal, 4 class, `\b[0-9a-f]{n}\b`
  at 40 and 100: 10 rows).
- ROW KINDS for the why (F7): a `verdict` row reads only `RX_DFA_SCAN`
  (`run_cover.sh:79-81`), so "declines `width-limit`" is checked by a `facts` row: `a{40}(?:b|cc)`
  and `a{4095}` on the default arm (`width-limit|41|41|...`, `width-limit|4095|4095|...`, F6),
  and their `W` twins (values written by the build; review r13 READYSEAM-4 expects
  `end-at-k|41|...` and `cover|4095|...`).
- FLOORS (`run_cover.sh:141-143` at main: verdict 48, facts 19, answer 105; §5.3's "24, 6, 55"
  were rev 4's pre-stage-1 numbers): stage 2 adds verdict
  +10 (the `W` twins; the `@D`/`@D1` rows replace four literal rows, net 0), facts +2 (the `W`
  twins), answer + the `n >= 33` rows on `W` plus the two proof-range witnesses of §11.6.3 (the
  build counts and states each new floor as old + added).

#### 11.6.3 Sabotage rows (ids at build time): 4 new, 1 re-aimed (F8, F9, F1)

| plant | waits for | unique witness | control / why only it flips |
|---|---|---|---|
| BYPASS: C15 always passes. S3223 IS this row at stage 2 (same site, `S3223_cover_c15_removed.sh:17` `if (st) return true;`): re-described, `REACH-WHY=[width-limit]` | A (before the reply) | `verdict [0-9a-f]{@D1}` (default arm) reads `cover`; `facts a{4095}` loses `width-limit`. Before the kit's carrier, the same plant reddens through `cover_window`'s named internal error (READYLIMIT-7): detected either way | only the bypass admits a cover past the default on the default arm |
| OFF BY ONE: `k < limit` for `k <= limit` | A | `verdict [0-9a-f]{@D}` (expects `cover`) declines | the bypass leaves `@D` a cover; nothing else moves the comparison |
| SEAM ASSERTION REMOVED OR INVERTED (plant (d) re-aimed; F9) | B | a reference compile of the ONE translation unit holding the B2 assertion, with `-DPCREC_ANCHORED_MAX_STATES=<the kit's declared positions bound + 2>` (and a legal `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH`), must FAIL, checked BY ITS MESSAGE (the assertion's text in the log), never by a nonzero exit alone; host: `tests/codegen/run_anchored_match.sh` as a new §4c, the shape of its §4b reference build | no run-time plant touches the assertion; C15 plants leave it intact |
| PROOF RANGE LEFT AT `MF_MAX_FWD` (P1), paired with P2: the statement passed to the kit at offset 36 of `[0-9a-f]{40}` NARROWED (P2 drops `0`-`9` there; F8) | B | `answer` row `[0-9a-f]{40}` on `W` whose subject is a 40-position hit with a digit at offset 36 (`0` x 40): pcrec reports no match, libpcre2 `0:40` | CONTROL, recorded: P2 alone must decline C14 (`under@36:..`). A WIDENING P2 flips no §5.3 shape (READYSEAM-6: 0 of 6), so the plant narrows |
| PROOF RANGE CUT TO `k + 1` (P3, rev 5's formula), paired with P4: the kit's text for a cover also tests offset `k + 1` and its reply says so (F1's OPPOSITE error; a kit-tree plant on the combined branch, or the kit's row if its rules require) | B | `answer` row `a{5}`, subject `aaaaa` (the match ends at the subject end, no byte at offset 6): pcrec reports no match, libpcre2 `0:5` | CONTROL, recorded: P4 alone must decline C14 at offset 6; only a comparison that stops at `k + 1` lets P4 through |

Existing rows: plants (a)-(c), (f) unchanged; S3220's `REACH-WHY` re-pinned (§11.2); S1131,
S1148, S1144, S1135 re-anchored where A1/B3 move their anchor text (§11.1). Kit-side rows are the
kit's.

#### 11.6.4 NOT in stage 2

The hull and N (§3.4); the fraction case ([EARNED-SKIP]/[MATCH-KNOWN], PARKED); raising
`PCREC_ANCHORED_MAX_STATES`; any rendering form designed by pcrec; the kit's three-form cards'
timing (kit-side); a dial cell for the width (unlock 1, on its trigger); a `.rxt` line for the
option. NOT pre-declined (F25): a class-only width, which is §9 Q8, asked only if §11.4's
near-miss cells lose (leaning: the kit's rendering first). Moved IN since rev 5 (F21): the
per-compile option and its `pcrec_options` field (§11.2.1).

### 11.7 The standing questions (stage 2)

1. **Measurement regime: RELEVANT.** The default IS a measured selection, and the near-miss
   and not-warm regimes can flip it, so the rule takes every regime's worst (§11.2, §11.4),
   in the bench's time unit; instructions are reported, not ruled on.
2. **Independent control: RELEVANT.** §3.6 Q2's table holds; added: libpcre2 answers at
   `n >= 33` (independent), the `test-axes` width arm against the default run (shares the
   emitted tables), the build-time seam assertion (shares the kit's declared bounds only), the
   proof comparison over the reply's whole range (shares the statement; the two paired plants
   of §11.6.3 show it and the answer rows each catch what the other misses). The DEFAULT
   SELECTION's only control is the A/A pair, now with a defined floor (§11.4). K35: the
   prediction counts the whole baseline listing; the timing counts every cell, declined cells
   listed.
3. **What moves on regeneration: RELEVANT.** Re-measuring the default can move it EITHER way;
   it moves the routes of every cover with width between the old and new default: an `abi`
   event, the identity gate's re-pin, the start-set manifest if it moves, `answers.tsv`,
   `limits.md` section 3.12 (new)'s number by its dump check (D80), the row's `desc` derivation. The
   kitproof witnesses at and past the default move with it by construction (`@D`/`@D1`,
   `width=N`; §11.6.2). The registry count 81 -> 82 once.
4. **The family (F27; memory `pcrec-forest-for-trees`).** The width limit is a route knee
   between two emitted forms, a member of [SIZE-KNEE]'s family (`VM_INLINE_CHAIN_MAX_BYTES`
   with `--vm-entry-shape=N`, the closest analogue; `PCREC_DEFAULT_UNROLL_K` with `--unroll=N`;
   `PCREC_SIZE_TERM_THRESHOLD`/`_BAR`); PLAN for main: add it to [SIZE-KNEE]'s member list.
   General form: "how far a proven span stands in for the engine, per artifact", one dial row
   whose cells are measured exchange rates; the whole-or-nothing cover is its first instance
   and [EARNED-SKIP]'s proof extent is the same quantity read as a fraction. UNLOCKS (filed,
   not scheduled): (1) per-artifact adjustment through `--tune` (trigger: §11.4 measures a
   rate, a long-cover win with a size cost or a near-miss loss); (2) the owner's always-inline
   kit option as a dial cell (trigger: the kit's cards show inline faster beyond noise in some
   regime); (3) [SIZE-KNEE]'s one derived quantity covering INLINE_CHAIN and the width
   (trigger: its own, a measured miss where the two cut-overs disagree on one artifact);
   (4) prefix covers past the limit, the fraction case, which removes the cliff (trigger:
   [EARNED-SKIP]'s own; the owner's 14:10 "1." names its two candidate methods).
