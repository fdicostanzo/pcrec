# cover_cap.md — the `cover` route's exact stretch: read from the anchored machine, no length bound, no budget ([COVER-CAP])

Status: PROPOSED, revision 3 (lane `covcap4`, 2026-11-15). DESIGN ONLY: no build go.
Plan row: [COVER-CAP] (set S3). Owner criteria: D198. Review of rev 2: round covcap-r2,
`docs/dev/reviews/2026-11-15-r5-covcap-r2.md` (C-1..C-25, dispositions ruled by the manager).
Compiler read: worktree at main `4ccd97ca7`. Every "today" number below carries its command;
`$PC` is that worktree's `build/pcrec` and `SF() { $PC -p rx --features all --emit-facts --pattern "$1" | awk -F'\t' '$1=="byte"&&$2=="span_facts"{print $7}'; }`.

**REVISION 3 (critic round covcap-r2 applied; the walk choice).** Rev 2 replaced the bounded
subset-exploring walk by a straight NFA-subset walk. The round found that walk unsound or
unbuildable as written in five places (C-1 a dead line need not terminate within the bound
claimed, C-2 the kept `sw_take` cannot detect a cycle, C-3 the root rule, C-4 "branch" depends
on NFA shape, C-8 a liveness pass with no client) and three cost or outcome gaps (C-5..C-7).
Rev 3 answers the manager's design question (R4) by reading the exact stretch from the
ANCHORED MACHINE instead, with the walk the cover already runs (`kn_walk`, C7), unbounded.
That choice discharges C-1..C-8 by deletion rather than by repair (§3.1, the report's
WALK CHOICE), loses none of today's 1,852 covers (rev 2 lost 4), keeps kit_proof's Z2
ruling 1 standing, and deletes the NFA span slice (`pcrec_span_walk`, about 430 lines of
`src/facts/kset.c`) with its budget, horizon, 24-deep loop and limits row. The price is
C8's second machine: the in-build two-producer comparison goes, and its control role moves
to checks against libpcre2 and the `-fno-scan-edge` arm (§3.6 Q2). Also in rev 3: the
owner's END STATE (§1.1, C-25, D198 (d)); "branch" defined at language level (§3.2, C-22);
goals per stage with G4 as a constraint (§0, C-21, C-23); corrected facts for the owner
(§9, C-9, C-10); the kit request cut to the capability and the population fact (§4.3,
R3, C-24); the re-timing regimes (§7, R3); the delivery bar's instruments, values, plants
and outside witnesses (§5, C-13..C-20). Rev 2's text is superseded in place; §10 lists
what survives. Findings are mapped by id in `docs/dev/lanes/covcap4_report.md`.

## 0. Goals

**Constraint above the ranking (G4; D198 (c)).** The exact stretch has no length bound, no
budget and no constant of its own. Its only limits are the machine's size and the pattern's
language. No goal below may be met by re-adding one; a goal that cannot be met without it
goes, in order, to the one-pass rule (memory `pcrec-one-pass-loss-chasing`), then to the
kit (§4.3), then to an owner ruling. Form: §8 lists no pcrec-side row on the exact path
marked INHERITED or BUDGET, `src/core/limits.def` loses `PCREC_SPAN_WALK_SUBSETS`, and `KN_CAP`
is gone.

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

| the model (D198) | in pcrec today | rev 3 |
|---|---|---|
| EXACT span: every position proven, the engine does not retest | two producers compared by C8: the NFA slice `span_facts` (`pcrec_span_walk`, `src/facts/kset.c`) and the anchored machine's walk `kn_walk` (`src/gen/known.c`, C7) | ONE producer: the anchored machine's walk, unbounded (§3.1). The slice is deleted |
| HULL positions: candidates only, the work thrown out | `kset_walk` (assertions passed as if they held, reach `PCREC_PREFIX_K_MAX` = 24) | unchanged, off the cover path (§3.4) |
| "a branch ends it" | no such rule; the slice proved branching prefixes exact by exploring them | the stretch ends where the next byte's set depends on which bytes came before (§3.2) |
| "no bound" (c) | `PCREC_SPAN_WALK_SUBSETS` (512), a 48-deep horizon, a 24-deep exact loop, `KN_CAP` (32) | none on the exact path; stage 1 reads the kit's seam bound (C15), stage 2 removes it |
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
[MATCH-KNOWN] un-parked). The walk family ("per-depth forward walks": `kn_walk`,
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
  machine reading is not defined (the finisher is the VM: 1,127; no anchored machine: 36;
  seeded entry: 14; no cover record: 342). Counted on covcap3's probe builds (budget
  raised, so an upper bound for today): `census2.jsonl`..`census4.jsonl` filtered on
  `span_facts > 0` and those `why`s, the same 1,519 on each. No decision reads those values (C8 is the only
  reader, `known.c` `cc_exact`); they leave the listing (§3.3).

## 3. The design

### 3.1 The exact stretch: the anchored machine's product walk, unbounded

**FORM.** `kn_walk` (`known.c`) as it is, without `KN_CAP`. From the entry row `r0` (C6),
it holds the set of machine rows (virtual states: a state and its count inside a scan-edge
chain, `kn_step`) reached at each depth, keeping only LIVE rows (`kn_liveness`: exact
backward reachability to an accept in any form or through the view-gated final newline).
At depth `j`:
1. No rows, or a view-gated newline consumed at `j - 1`: the walk ends, `k = j`.
2. Some row accepts in any form: the walk ends, `k = j` (C10/C11 then read the rows at `k`).
3. Otherwise each row's live next-byte set is computed (`kn_step` over the byte classes,
   plus `\n` through the eol view). If every row's set is the same set `S_j`, depth `j` is
   EXACT. The first depth where two rows' sets differ is `L`, the end of the exact stretch;
   the walk records `exact = false` there and goes on to find `k` (C7 still needs the
   width), keeping only the sets, never the rows, past `L`.

`exact_len` is `min(L, k)`. These are rev 1's three outcomes (C-6) without the fourth
("the loop ends at `H`"), since there is no `H`.

**Why this walk, against the NFA-subset walk of rev 2** (R4; the full comparison is the
report's WALK CHOICE):
- It is the walk the cover already runs and X0 already checked against libpcre2
  (`kit_proof.md` §6.4 X0 RE-RUN). Nothing new is built on the exact path.
- Liveness is exact on a machine (one backward pass over its edges): no undecided case,
  no POSSIBLY/SURELY passes, no root rule (C-3: a context-dependent start is C6's
  `entry-const/seeds` decline), no cycle rule (C-1, C-2: termination below), no opaque
  ends (C-5 (i): `\G` is C3's decline).
- It compares byte SETS, never row identity, so it reads the language, not the NFA's or
  the machine's shape (C-4): `-fno-altcls-*` and `-fno-scan-edge` cannot move `L` or `k`.
- It loses no cover today (§2) and keeps `(?:[a-z]{0,3}\z|x)[0-9]{3}` (Z2 ruling 1, §9).

**TERMINATION AND COST (C-1, C-7).** Let `V` be the machine's virtual-state count (states
plus the counts inside scan-edge chains: the machine's own size). Every row on the walk is
live, so from each row some accept is at most `V - 1` bytes away, and the walk follows
every live successor; so some row accepts, and the walk ends, by depth `V`. Rows per depth
are at most `V` (deduplicated). Each depth costs `rows x classes` steps, so the walk is
O(k x rows x classes), bounded by the machine. MEMORY: today `kn_walk` allocates
`KN_CAP + 1` row arrays of `4n + 8` entries eagerly; rev 3 keeps two row arrays (this
depth, the next), grown as needed, plus 32 bytes of set per depth and the rows at `k`
for C10/C11, so memory is O(k x 32 + V). C9 (no eol view at any depth) is checked as the
walk passes each depth instead of from retained rows. The `rows` detail of C7 (a depth
over the scratch) retires: census count 0 (`why` = `fixed-width/rows` on no compile).
UNMEASURED as a comparison: §5.1's compile-cost row reads CPU and max RSS, old against new.

**WHAT IT DELETES (simplification, the benefit).** The NFA span slice: `pcrec_span_walk`
and its `sw_*` helpers (`kset.c` from the "THE SPAN SLICE" banner to the end of
`pcrec_span_walk`), `MkLang` (`facts.h`), the `span_facts` row of `facts.def`, its
accessor `pcrec_fact_span_stated` and the trace build's `SPANSET` record (`facts.c`),
`PCREC_SPAN_WALK_SUBSETS` (`limits.def`), `KN_CAP`, C8's slice comparison and its
`producers-disagree` / `producer-short` / `producer-unstated` details, and
`pcrec_known_derive` (no caller; it read `MkLang`; M6, C-20). The 48-deep horizon and the
24-deep exact loop go with the slice.

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

- C7 `fixed-width`: `k >= 1` and the rows at `k` are not empty; the `k <= KN_CAP - 1` term
  goes. Stage 1 adds C15 (§3.5).
- C8 `exact`: `exact_len >= k`, i.e. no depth below `k` where the rows' sets differ (today's
  `exact/machine-inexact`). Its kind becomes `machine`; its `span fact` reading goes. C8 keeps
  its id and its `why` `exact/machine-inexact`.
- C12 `utf8-start` reads `MkEnd`'s `S_0`; its kind `span fact` becomes `machine`.
- THE LISTING. `--emit-facts` loses the `span_facts` row. A new listing section `cover`
  (a new section of `facts_listing.md` after its §4.4) states, per encoding, the cover decision's `why` (`cover`
  or the first failing row), `k`, `exact_len` and `S_0..S_{exact_len-1}` in `kset_walk`'s
  spelling, read from the decision's own record (`pcrec_cover`'s memo; no second walk).
  Where C1-C6 fail the row states the `why` and `exact_len` 0. The definition of a stated
  stretch is ¶7c's, unchanged: for every `d < exact_len` the matches' length-`(d+1)`
  prefixes are exactly the product and no match ends before `d + 1`. This section also
  makes the cover `why` visible in the default build, which the mover prediction reads
  (§5.2, C-15).

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
  pcrec has no bound of its own. Cover movers: `k` 25..32, and the 18 k = 1 compiles (§2).
- **Stage 2 (after the kit's answer to §4.3).** A counted seam; C15 retired like C2 (id
  kept, absent). `cover_window` and `pcrec_cover_proof_diff` read counted ranges. Movers:
  every long shape.

Each stage is one pcrec `abi` event (§4.4). The listing section (§3.3) lands at stage 1.

### 3.6 The standing questions

1. **Measurement regime: RELEVANT** for G3, G5, G6 (§7). No decision depends on a regime:
   the cover is answer-identical by proof, and the census counts compiles.
2. **Independent control: RELEVANT; this is where rev 3 pays.** Today C8 compares the
   NFA slice with the anchored machine's walk on every compile and declines on a
   difference (the trace build asserts). The two share their source (`Job.nfa`: the
   machine is its subset construction), so C8 was never a control on the NFA's language;
   it was a control on the two READINGS. Rev 3 has one reading. Its controls, none sharing
   its code:
   - libpcre2 10.46: `test-kitproof` answer rows (standing), and X0's per-position set
     check (`x0.py stated`, `docs/design/kit_proof/x0/`) run ONCE by the build on the
     listing's `cover` section over the census population, every stated position, both
     stages (the instrument read `SPANSET`; it is re-pointed to the listing);
   - the `-fno-scan-edge` arm, which reads plain states where the default reads virtual
     ones (the reading's other half, `known.c`'s header): the build compares the listing's
     `cover` rows on both arms over the census population, equal row for row;
   - the engine route of the same compiler (`test-axes`, `--memfn=no-window-search`):
     the engine runs the emitted tables, not `kn_walk`;
   - the kit's proof (C14, `pcrec_cover_proof_diff`): the kit's text against the statement.
   What is lost: a decline on every user compile where two readings disagree. Today that
   decline has fired on 0 compiles in the trace builds that assert it (`z2build_report.md`,
   "producers-disagree internal errors are 0"). K35: the sweeps count the whole census
   population; the kitproof floors are stated in §5.3. [MECH-REACH]: §5.4.
3. **What moves on regeneration: RELEVANT.** `limits.def` loses a row, so by grep in the
   same change: `--list-limits`' output, the X-macro list in `src/core/limits.h`,
   `tests/registry/limits_check.sh`'s count (82 to 81, its two lines) and name list,
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

> **R-n (DRAFT, pcrec manager) — a window span of any length ([COVER-CAP] rev 3)**
> - GO: none yet; the kit-side build waits on the owner's go for stage 2 (§9 Q4).
> - FACT (population). pcrec will state the cover's REPORT window site with span 0 of `k`
>   exact positions, where `k` has no upper bound on pcrec's side. Today's population
>   (census, both encodings): `k` = 36..500 and 1000 beyond the current 32 (31-32: four bench
>   shapes and two corpus literals, already inside today's bound; 36: two uuids; 40;
>   49; 60; 500; 1000), mostly long runs of one byte class. Each has one context position
>   at -1 and, where stated, one at offset `k`. pcrec reads the per-offset proof at every
>   offset in `[-1, k]` and checks it equals the statement.
> - ASK. Can the statement and the reply carry a span of any length? Reply in responses.md
>   with the form you choose.
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
  never disappears) and its `decline:` reasons leave §4.1.3¶3; a new section `cover` after §4.4 defines the section of §3.3 with ¶7c's product definition
  carried over word for word, and §4.1¶2's sentence on the `cover` row's reading of
  `span_facts` is rewritten to the machine reading.
- `cli.md` §2.6 describes `--list-limits` generically and names no row: no hunk.
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
| `scripts/compile_time_census.py`, old binary against new, CPU and max RSS (C-7) | the old binary | §3.1's cost claim |

### 5.2 Byte identity and the mover list (G2; C-15)

`scripts/emit_sweep.py`, main-before against the candidate, over the committed population.
The prediction comes from the BASELINE build only, read from the trace build's `KITPROOF`
record (`PCREC_KIT_PROOF_TRACE=1` on the trace binary; `k=0` on a decline, so `k` is read
from the `width` fact of the same compile): INTO the cover, every decision whose `why` is
`exact/producer-short`, or `fixed-width` with `width` `[w,w]`, `25 <= w <= 32` at stage 1
(any `w` at stage 2). That is an UPPER bound: C9-C15 never ran on those decisions, so the
deliverable lists each predicted compile that does not move with the candidate's `why`
(at stage 1 the bench's `wild-logparse-quotedstring-noatomic` is one, §2). OUT of the cover:
none. No `k >= 25` floor is claimed for gains below 25 (the 18 k = 1 compiles are in the
prediction by their `why`). The listing is not predicted (it changes form, §3.3); its
values are checked by X0 and the scan-edge compare instead (C-15's downgrade of the listing
half to "observed, checked against libpcre2").

### 5.3 Witnesses (`tests/kitproof/cases.tsv`; C-16)

- `verdict`: a literal and `[0-9a-f]{n}` at 24, 25, 32, 33, 40, 100, 1000; `\b[0-9a-f]{n}\b`
  at 32, 40, 100; `\d{32}` under `u`. Stage 1: cover through 32, decline from 33
  (`statement-fits`). Stage 2: cover at every length. `ab|abc|ad` cover;
  `(?:S(?i:ab)|(?i:sab))` cover (byte); `[a-c]*\ba` cover (a k = 1 gain);
  `a[xy]c|b[xy]d` decline `exact/machine-inexact`. The existing
  `(?:[a-z]{0,3}\z|x)[0-9]{3}` rows (Z2 ruling 1) are unchanged.
- `facts` (the listing's `cover` section, compared whole; the loader in `run_cover.sh`
  reads the new section, a named loader change): the 6 existing rows keep their values on
  the new section; new rows `a{40}(?:b|cc)` `41:` + 40 × `97` + `,[2]` (its `b`/`c` set;
  the build writes the literal value), `a[xy]c|b[xy]d` `2:[2],[2]`, `a{30}(?:b{30}c|d)`
  `31:` + 30 × `97` + `,[2]`, `ab|abc|ad` `2:97,[2]`, `a*?a` `1:97`, `(?:\bab|\Bac\z)` `0`
  (`entry-const/seeds`). Every value is written in full in `cases.tsv` (no prefixes).
- `answer`: per length `n` of the verdict rows: subjects of `n-1`, `n`, `n+1` bytes, a near
  miss at the last position, a match at the subject end, two adjacent matches, every
  startoffset; expectations from libpcre2 via `gen_answers.sh`. Answer rows at `n >= 33`
  land at stage 2 (at stage 1 they fail their REACH, which requires `cover`).
- Floors (`run_cover.sh`: verdict 24, facts 6, answer 55) rise by the rows added; no row is
  removed (rev 2's loss of four answer rows does not happen).

### 5.4 Sabotage rows (mech arm `kitproof`), each with a unique witness (C-17)

| plant | breaks | unique witness | why only it flips |
|---|---|---|---|
| (a) a length bound back on the walk (`j < 32`) | G4 | `facts` `a{40}(?:b|cc)` `41:...` → `32:...` | not a cover (variable width), so (e) never reaches it; (b)-(d) leave a one-row line intact |
| (b) rows compared by identity: a second row ends the stretch | §3.2 | `facts` `a[xy]c|b[xy]d` `2:[2],[2]` → `1:[2]` | the only witness with two rows of equal sets before `L` |
| (c) liveness dropped (dead rows kept) | §3.1 | `facts` `a(?:b|c\z\W)` `2:97,98` → `2:97,[2]` | (a), (b), (d) keep liveness |
| (d) C15 removed (stage 1 only) | K7 | the 40-literal `verdict` compile goes red (`window_bounds_check`'s internal error) | nothing else states a 40-position span at stage 1 |

S1131 (C8 skipped) keeps its witness `ac|bd`: the plant now skips the machine's exactness.
S1149 (`slice ctx passthrough`) plants into the deleted slice: the row retires with its
code (its ids stay absent), and its three `facts` witnesses stay as `cover`-section rows.
The plant ids are the build's to take.

### 5.5 Witnesses outside the census population (C-18), and stale text (C-14)

At stage 1 these become covers and would go vacuous-green: `tests/codegen/run_offset_skip.sh`
(`\b[0-9a-f]{32}\b` as the offset-k DECLINE witness and the `-fno-offset-skip` identity
witness) and `tests/codegen/run_entry_shape_identity.sh` (`[0-9a-f]{32}`). The build
re-points each to a shape no stage makes a cover (a capture, which C1 declines, e.g.
`\b([0-9a-f]{32})\b`, if it still selects the same form; the build checks), and greps
every non-`.rxt` test for the moving shapes at each stage. Stale text the build owes: the
`facts.h` comment naming a FIND-site reader of `MkLang` that does not exist, `known.c`'s
`KN_CAP` comment, `kit_proof.md`'s sentences on C8's two producers and on `span_facts`'
bound, `ctx_span.md` §11 N-1, `span_runs_sheet.md`'s bound line, and
`patfacts/inventory.md`'s `span_facts` row (each found by grepping `span_facts`,
`MkLang`, `KN_CAP` and `PCREC_SPAN_WALK_SUBSETS`, which must reach 0 outside history).

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

## 8. The bounds on the cover path (rev 1 §1's inventory; rev 3 verdicts)

Rev 1 §1's inventory (in git at `75d365a0b`) stands for its sites. Rev 3's verdicts:
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

**Two corrections to what rev 2 told you.**
1. *The hidden limit.* Rev 2 said today's code had a hidden length limit "near 511". It
   does not. Today the exact span is worked out to at most 24 positions, and a pattern of
   49 positions or more gets no exact span at all: `a{48}` lists 24 positions and `a{49}`
   lists none. Either way the fix is the same: the new reading has no limit.
2. *An earlier ruling.* Rev 2 would have dropped the cover for
   `(?:[a-z]{0,3}\z|x)[0-9]{3}` without saying that keeping it was a decision. On
   2026-10-21 the manager ruled, in the Z2 build lane's rulings file (ruling 1), that this
   pattern reads `cover` with 4 positions, after an earlier check left 175 test cells
   inconclusive; the build then compared it with libpcre2 on every subject up to 8 bytes
   over a 7-letter alphabet, every start offset and find-all: 0 differences in 66,243,390
   cells, both encodings (`docs/dev/lanes/z2build_report.md`). Rev 2 would have reversed
   that and turned 6 existing test rows red. Rev 3 keeps it: the new reading covers it.

**Questions.**
1. **Reading the exact stretch from the compiled machine instead of the pattern's graph.**
   This changes what rev 2 told you. Rev 3 reads it with the walk the cover already runs on
   the compiled matching machine, with its limit removed. It loses none of today's covers
   (rev 2 lost four), it gains 18 small test-pattern covers, the earlier ruling above
   stands, and about 430 lines of exploring code go. What it gives up: today two separate
   readings must agree before a cover is used; afterwards there is one reading, checked
   against PCRE2 and against a second form of the same machine in the test suite instead of
   on every compile. Also, the listing stops showing an exact span for patterns the cover
   cannot use (nothing reads those values today). Leaning: accept.
2. **The earlier ruling** (correction 2): it stands under rev 3. Re-decide only if you
   would rather not cover that pattern. Leaning: keep it.
3. **One step or two** (from rev 1, answered by you: "leave that ordering step to you").
   Taken as two: step one changes only pcrec and covers up to 32 positions; step two needs
   the kit to accept any length. No question left.
4. **Size.** Stage 1 reports each mover's size beside its timing. If a long cover grows the
   matcher enough to lose in the cold-cache timing, the order is: one bounded try, then the
   kit, then you. Leaning: no action until the timing shows it.
5. **Build go for stage 1** (§3.1-§3.3 plus C15, §5 as the delivery bar), at opus tier,
   after the narrow readiness re-check that follows this revision.

For main, not the owner: [DD-11.5]'s part 1 product (the span slice, Z2) is deleted by
stage 1, and its in-span `A_CTX` producer work has no remaining cover-path reader; its row
needs re-scoping. [DEC-LIMITS]'s trigger does not fire (a row is removed). The N row
(§1.1 (i)-(iii)) and the `PCREC_PREFIX_K_MAX` label row are main's to file.

## 10. What earlier revisions' parts survive

- KEPT: rev 1's bounds inventory (§8), the two stages and C15 (§3.5), the abi events
  (§4.4), the checks and sweep (§5, re-instrumented), the re-timing (§7, with R3's regimes).
- REPLACED: rev 2 §3.1 (the NFA-subset straight walk, its liveness passes, cycle and root
  rules) by §3.1 (the anchored machine's walk); rev 2 §3.2 (the machine walk bounded by the
  slice's length) by §3.1's single walk; the C8 two-producer comparison by §3.6 Q2's
  controls.
- DROPPED: rev 2's kit ASK 2/ASK 3, FACT 3 and the kit-bound list (R3, C-24); rev 2's §2
  "cliff near 511" (C-9); rev 2's four cover losses and owner Q1 (none lost).
- Rev 0's and rev 2's dispositions stand as recorded in
  `docs/dev/reviews/2026-11-15-r2-covcap0.md` and `2026-11-15-r5-covcap-r2.md`.
