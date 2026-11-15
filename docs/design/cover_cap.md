# cover_cap.md — the `cover` route's exact stretch: read from the anchored machine, bounded by that machine's own state ceiling, no budget ([COVER-CAP])

Status: PROPOSED, revision 4.1 (lane `covcap6`, 2026-11-15). DESIGN ONLY: no build go.
Plan row: [COVER-CAP] (set S3). Owner criteria: D198. Reviews: round covcap-r2
(`docs/dev/reviews/2026-11-15-r5-covcap-r2.md`, C-1..C-25) and round covcap-r3
(`docs/dev/reviews/2026-11-15-r6-covcap-r3.md`, R-1..R-14) and round covcap-r4
(`docs/dev/reviews/2026-11-15-r7-covcap-r4.md`, FI-1..FI-6, READY-1..READY-5), dispositions ruled by the manager.
Compiler read: worktree at main `ac91d48bb` (no `src/`, `lib/`, `cli/` change since rev 3's
`4ccd97ca7`). Every "today" number below carries its command;
`$PC` is that worktree's `build/pcrec` and `SF() { $PC -p rx --features all --emit-facts --pattern "$1" | awk -F'\t' '$1=="byte"&&$2=="span_facts"{print $7}'; }`.

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
limit that already exists: `PCREC_ANCHORED_MAX_STATES` (4096 states, so at most 4095
positions; §3.1). No new constant is added. Past it there is no anchored machine, no stretch
from this reading, and the pattern runs as it does today (§3.1, §9 Q2).

## 0. Goals

**Constraint above the ranking (G4; D198 (c), (g)).** The exact stretch has no budget, no
tuning constant and no limit of its own. Its one bound is the anchored machine's existing
state ceiling `PCREC_ANCHORED_MAX_STATES` (§3.1): a machine of at most 4096 states, so at
most 4095 positions, reached by no population pattern's stretch. Past it there is no
machine and no stretch from this reading (today's behaviour, not a new drop; §3.1). No goal
below may be met by adding a bound; a goal that cannot be met otherwise goes, in order, to
the one-pass rule (memory `pcrec-one-pass-loss-chasing`), then to the kit (§4.3), then to an
owner ruling. Form: §8 lists no other pcrec-side row on the exact path; `src/core/limits.def`
loses `PCREC_SPAN_WALK_SUBSETS` and gains nothing; `KN_CAP` is gone; `a{4095}` states 4095
positions and `a{4096}` reads `anchored-A` (§5.3).

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
   a growth is the owner's to accept, once (§9 Q4).

Non-goals: the hull and its N (§3.4); the fraction case of the end state (§1.1, PARKED
rows); lookaround as a run ([REQ-LOOKAROUND]); captures in a cover body (C1);
`PCREC_PREFIX_K_MAX` itself.

## 1. The owner's model, mapped to the code

| the model (D198) | in pcrec today | rev 3, rev 4 |
|---|---|---|
| EXACT span: every position proven, the engine does not retest | two producers compared by C8: the NFA slice `span_facts` (`pcrec_span_walk`, `src/facts/kset.c`) and the anchored machine's walk `kn_walk` (`src/gen/known.c`, C7) | ONE producer: the anchored machine's walk, unbounded (§3.1). The slice is deleted |
| HULL positions: candidates only, the work thrown out | `kset_walk` (assertions passed as if they held, reach `PCREC_PREFIX_K_MAX` = 24) | unchanged, off the cover path (§3.4) |
| "a branch ends it" | no such rule; the slice proved branching prefixes exact by exploring them | the stretch ends where the next byte's set depends on which bytes came before (§3.2) |
| "no bound" (c), amended by "a max span length ... sufficiently high that it's rarely seen" (g) | `PCREC_SPAN_WALK_SUBSETS` (512), a 48-deep horizon, a 24-deep exact loop, `KN_CAP` (32) | no new limit: the anchored machine's existing ceiling `PCREC_ANCHORED_MAX_STATES` (4096 states, `k <= 4095`); stage 1 also reads the kit's seam bound (C15), stage 2 retires C15 |
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

**THE BOUND ON THIS ROUTE: the anchored machine's state ceiling (R-1).** The walk reads
`Job.adfa`, which is built only when it fits `PCREC_ANCHORED_MAX_STATES`
(`compile.c`'s `build_anchored_dfa`; where it is absent, C4 `cc_anchored` in `known.c` declines); every walked row is live and the walk ends
by the shortest path to an accept, so `k <= V - 1 <= 4095`. The row as `limits.def` has it:

    PCREC_LIMIT(PCREC_ANCHORED_MAX_STATES, 4096, "states", "compile budget", BUILD_D, "",
      "[ENG-ABS]: the optional anchored match-here machine's own DFA state ceiling, lower than the mandatory pair's", LIMITS_H)

It is LABELLED (kind `compile budget`, override `-D`). The row names its role, not its
derivation, which lives in `src/core/limits.h`'s `[ENG-ABS]` block (measured: 2.05x the
captures-on corpus maximum of 2,001 states; 4.9x below `tests/resource`'s giant repeats,
whose compile CPU and size it excludes). Proposed stage-1 `desc` text, no derivation
invented: append "; also the cover's longest exact stretch, 4095 positions
(docs/design/cover_cap.md); derivation: limits.h [ENG-ABS]". (`compile.c`'s comment calling
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
- **Stage 2 (after the kit's answer to §4.3).** A counted seam up to 4095 positions (the
  state ceiling, §3.1); C15 retired like C2 (id kept, absent). `cover_window` and
  `pcrec_cover_proof_diff` read counted ranges. Movers: every long shape the anchored
  machine holds.

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
3. **What moves on regeneration: RELEVANT.** `limits.def` loses `PCREC_SPAN_WALK_SUBSETS`
   (home `INTERNAL_H`) and gains nothing; `PCREC_ANCHORED_MAX_STATES`' `desc` gains §3.1's
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

`cover_window` states the span from `MkEnd`'s counted sets; `pcrec_cover_proof_diff`
loops over the reply's counted proof range; `window_bounds_check` mirrors the kit's new
statement check; C15 retires. The other window sites state what they state today, and
the sweep proves them byte-identical.

### 4.3 KIT REQUEST DRAFT (for main to file; facts only, D157; no build go)

> **R-n (DRAFT, pcrec manager) — a window span of up to 4095 positions ([COVER-CAP] rev 4)**
> - GO: none yet; the kit-side build waits on the owner's go for stage 2 (§9 Q4).
> - FACT (population). pcrec will state the cover's REPORT window site with span 0 of `k`
>   exact positions, `1 <= k <= 4095` (by derivation: the stretch is read from pcrec's
>   anchored machine, whose existing ceiling is 4096 states; the owner confirms before this
>   is filed). Today's population
>   (census, both encodings): `k` = 36..500 and 1000 beyond the current 32 (31-32: four bench
>   shapes and two corpus literals, already inside today's bound; 36: two uuids; 40;
>   49; 60; 500; 1000), mostly long runs of one byte class. Each has one context position
>   at -1 and, where stated, one at offset `k`. pcrec reads the per-offset proof at every
>   offset in `[-1, k]` and checks it equals the statement.
> - ASK. Can the statement and the reply carry a span of up to 4095 positions? Reply in
>   responses.md with the form you choose.
> - Deliver: a kit branch for merge review, for one landing with pcrec's stage 2.

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
Stage 2: no spec hunk beyond the abi entry (the bound was never a spec sentence).

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
is `exact/producer-short` or `exact/producer-unstated` (expected 0, §3.1 R-9), or
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
  (`statement-fits`). Stage 2: cover at every length the machine holds. `ab|abc|ad` cover;
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
  removed (rev 2's loss of four answer rows does not happen).

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
every non-`.rxt` test for the moving shapes at each stage. Stale text the build owes: the
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
- THE BOUND THAT BINDS (R-1; omitted from rev 3's inventory): `PCREC_ANCHORED_MAX_STATES`
  (4096 states, so `k <= 4095`), existing, labelled `compile budget`, derived in `limits.h`
  (§3.1). Nothing is added.
- GONE with the slice: P1 (the 24-deep exact loop), P2 (the 48-deep horizon), P3
  (`MkLang.set[24][32]`, `uint8_t exact_len`), P4 (`PCREC_SPAN_WALK_SUBSETS`, a budget that
  never binds on a straight line; its cliff is P2's at 49, §2). GONE: M1 `KN_CAP`; M2 the
  sentinel (§3.1's outcomes); M3 the per-depth row cap (grown arrays); M6
  `pcrec_known_derive`.
- COUNTED: M4 `MkEnd` (its `k` and its sets).
- At stage 2: M5, the proof loop, reads the reply's counted range; the seam's K1-K7 are the
  kit's call. Stage 1 reads them through C15.
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
   today). Leaning: accept.
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
   no new limit.
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
