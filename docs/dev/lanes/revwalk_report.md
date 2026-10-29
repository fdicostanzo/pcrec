# Lane revwalk — the reverse-walk start-recovery family: design note + census

Lane revwalk (opus), 2026-10-29, branch `lane/revwalk` from `ec87afbca`. Design and measurement only:
nothing under `src/`, `cli/`, `lib/` or `memfn/` was edited. Instruments and outputs:
`docs/dev/lanes/revwalk_evidence/` (its CLAUDE.md says how to re-run them). Rulings applied: R1-R4 of
`revwalk_rulings.md` (all 2026-10-29).

## Summary

- **Premise test: confirmed.** The kit's window site states every span at a FIXED signed offset from the
  candidate, inside `[-MF_MAX_BACK, MF_WREACH)` = `[-8, 64)` (`memfn/include/memfn.h`, "THE WINDOW SITE",
  `mf_wspan.start`; D172). The old D161 fields `window_stated/move_back/overshoot` and their reserved
  `MF_MOVE_UNBOUNDED` were deleted at D172 S2 commit 6 (`memfn/include/CLAUDE.md`, MF_SITE_ABI 20). So
  the window contract has no unbounded move-back. The ONE place an unbounded backward walk already
  exists in the kit is the ADVANCE contract: `PcrecAdvance` (`src/gen/memfn_sites.h`) carries
  `reverse` and a span cap that may be `MF_SPAN_UNBOUNDED`, and the EDGE / STAY / VMSPAN sites use it
  for one set (R2).
- **The family.** Every start-recovery mechanism is: a SEED (a known position: a landmark hit, the
  match end, the subject end) plus a WALK backwards over the part of the pattern between the start and
  the seed, recording the SMALLEST accepted position not below the floor. The tiers are first-match
  rows by the shape of that part `P`: **T1** fixed width (today's fixed-offset spans), **T2** one
  plain class run `B{m,M}` (the "reverse span" of D161 add. 17), **T3** a string of segments whose
  boundaries are FORCED (each segment's alphabet is disjoint from every byte that can end what precedes
  it), **T4** P's general reverse DFA (today's `reverse-pass` and rev-inner's DFA hat). G1 failures
  (backreference, call, atomic, possessive, lookaround in P) take no row.
- **"Non-overlapping", made precise** (Exactness conditions): split P from the landmark outwards at
  every point where `LAST(earlier part) ∩ ALPH(segment) = ∅`. Then a back-scan over each segment's
  alphabet stops exactly at that segment's left edge, in every parse. Any segment that can hold the
  match START (every earlier segment can be empty) must be walked exactly (plain run, a chain
  automaton, or the first segment at a fixed width). Every other segment may be back-scanned over its
  ALPHABET alone, a SUPERSET, with its content left to the anchored verify pcrec runs anyway. That is
  what admits `loglines/stack-frame` (ARTREV A01, the -72% cell): its two identifier runs are not DFA
  chains, but their boundaries are forced by `.` and ` `.
- **One finding refines D161 add. 17's exactness condition.** For a plain run `B{m,M}` the walk is
  exact **with or without** landmark exclusion: plain runs are prefix-closed, so a later landmark can
  never give an earlier start (proof in Exactness conditions). For T2, exclusion buys COST: a walk
  never re-crosses an earlier landmark, so total work is linear and the candidate stream needs no
  de-duplication. For non-plain prefixes (T3, T4) exclusion, or D151's other strong arm, is still a
  correctness condition (monotonicity), exactly as for rev-inner.
- **Census** (parse-only reader + controls; corpus 5,203 deduplicated patterns, the repo's bench
  snapshot 345 + the 5b witness): see the Census tables. Headline at the ruled F = 2 admission:
  corpus **T1 78 / T2 197 / T3 15 / T4 92**, bench **T1 4 / T2 13 / T3 3 / T4 5** (exact counts and
  the unbounded subsets in the table). The general reverse DFA (T4) holds about a quarter of the
  admitted landmark population (92 of 382). The 5b witness is T2 (excluded, unbounded, scan-shaped).
- **Model:** the segment walk + anchored libpcre2 verify against libpcre2 10.46's own search, every
  startpos: **0 wrong / 74,824 checks** on 256 admitted real patterns + 10 hand witnesses. Mutations
  max-start (761 wrong), no-context (89), no-max-count (46) are all detected.
- **R1 scan edges:** the hypothesis holds for the EXACT tiers. On all 252 corpus rows where P's minimal
  reverse DFA is a chain, the segment rule gives T2/T3 (C2: 0 violations). Today's scan edge needs a
  UNIFORM exit (`src/opt/scanedge.c` precondition (1)), which only the OUTERMOST run has. A one-state
  self-loop does not need that uniformity (there is no early-exit ambiguity), so relaxing it there
  would make every chain loop a scan, forward machines included. What a dedicated chain form adds
  beyond that: superset segments, no reverse machine for P, fixed positions checked beside the
  landmark scan, and the kit's ownership of both layers.
- **Recommendation (leaning, no build go asked):** state the family as ONE fact (`back_walk`, a
  facts.def row, direction-free) and ONE kit contract (the ADVANCE contract widened to a sequence of
  `(set, min, max)` steps in either direction, seeded at the window site's stop). Admit T2 first, with
  exclusion and LOWER where S reads P's groups. Keep T4 in pcrec's reverse DFA, and keep rev-inner
  HELD for everything outside T1-T3.

## The family

**One operation, three seeds.** where_to_start.md §1.3 item 4 already observed that the reverse pass
(whole pattern, from a match end), [OPT-REVEND] (whole pattern, from the subject end) and
[ENG-TACTICS] (b) (prefix P, from an inner landmark) are "seed a reverse machine at a known position,
take the smallest accepting position". The family names the second axis that D161 add. 17 asks for:
how the walk is DONE, by the shape of what it walks over.

| | seed = landmark hit `j` (NEW for T2/T3) | seed = forward match end `e` | seed = subject end |
|---|---|---|---|
| walked part | P (spine before the landmark) | the whole pattern R | the whole pattern R |
| today | handoff LOWER-BOUND / presence only; rev-inner HELD | RECOVER rows `pinned`, `end-minus-width`, `landing`, `reverse-pass` (`emit_dfa.c` RECOVER block; start_landing.md) | `rev-end` |
| T1 fixed | offset-set / run-pinned / window spans | `end-minus-width` | `end-minus-width` arithmetic |
| T2 one run | **reverse span** (5b) | back-scan of one run instead of the reverse DFA | same |
| T3 forced segments | **string of spans** (stack-frame) | chain walk instead of the reverse DFA | same |
| T4 general | rev-inner DFA hat (HELD) | `reverse-pass` | `rev-end` |

The RECOVER table is already ordered by "where the evidence comes from and how much" (start_landing.md
§4.1: none / bounded / unbounded). The family adds a third value of "how much": unbounded but
STRUCTURED (T2/T3), between bounded (T1) and general (T4). The landmark seed is new. The end seeds
gain value only where the reverse pass is a measurable cost. On 5b it was 0.4% (subtri_report.md), so
the end-seeded rows stay a corollary and are not the motive.

**The walk is a reverse DFA that degenerates (R1.1).** For the exact tiers, the walk IS P's minimal
reverse DFA, and that DFA is a CHAIN: every state has a self-loop set (possibly empty), one exit set
to the next state, and an accept bit. C2 checks this both ways on the corpus: 252 of 252 rows whose
reverse DFA is a chain land in T2/T3. A loop state is a back-scan over its loop set, which is what
`src/opt/scanedge.c` calls a scan edge. Today's precondition (1) asks for a UNIFORM exit (every byte
outside the set leaves to ONE target), because a multi-state counting chain may stop with the state
variable at the head rather than at the true member. A ONE-state self-loop (`*`, `+`) has no such
ambiguity: the state variable is exact when the scan stops, and the following ordinary step reads the
true row, whatever its exits. So:

- The OUTERMOST run of a walk (5b: everything outside the class dies) is scan-shaped today. Of the 197
  admitted corpus T2 rows, 114 have every loop state scan-shaped, 70 have no loop at all (bounded
  counted chains, which the multi-state scan edge handles at m >= 2), 11 are not a chain in P's
  minimal reverse DFA (a bounded run before a fixed first segment, `ab?c`, `ab{2,3}c`: the DFA
  has a skip edge, which the segment walk handles as a count), and only 2 have an unshaped loop
  (`summary.txt`, R1 lines). Bench T2 admitted: 7 of 13 scan-shaped; the unshaped ones are
  `tag-depth3-bound`, `bak-k-named` (`[^<]*` before `</`) and the WAF `sleep(` pattern, whose run's
  exit splits between the next segment and death.
- INNER runs of T3 (exit to the next segment on one set, death on the rest) are NOT scan-shaped today.
  A relaxed precondition (1) for one-state self-loops would cover them. The same relaxation applies to
  FORWARD machines: any forward self-loop state with a split exit (a run followed by a specific
  delimiter, `\d+-`) becomes a scan. Frank's "perhaps they could use a chain as well": yes, forward
  DFAs gain from this, as one predicate change in scanedge.c rather than a new mechanism. Its
  population on pcrec's own forward machines is not measured here, because the reader's automata are
  not pcrec's class-split machines. The measurement that would trigger it: count, over `--emit-facts`
  or the DFA dump, the forward states with a self-loop and a non-uniform exit.

What a dedicated chain form adds beyond scan edges, which is the reason to state it at all:
(a) SUPERSET segments: stack-frame's inner identifier runs are not a chain in any DFA of P, but a
back-scan over their alphabet is exact at the boundaries (T3 "superset"; 2 of 15 admitted corpus T3 rows and
all 3 bench T3 rows); (b) no reverse machine for P has to be built or emitted (rev-inner's DFA hat,
its tables and its size cap); (c) fixed positions are checked as spans beside the landmark scan, in
the same vector; (d) the kit owns the scan in both layers (D146/D147), SIMD included. It adds no
exactness: where the chain is exact, the DFA already is.

**Who walks (R2).** The walk is the kit's, in both directions; pcrec supplies facts (D157). The kit
already owns the single-run case both ways: `DELEG_SITE` EDGE / STAY / VMSPAN are kit ADVANCE skips
built from `PcrecAdvance` (`reverse`, `span` up to `MF_SPAN_UNBOUNDED`). VMSTRIDE is a W-position
fixed sequence. T2 is therefore an ADVANCE with `reverse` set and one set. T3 is the same contract
widened from "one set, one cap" (or "W fixed positions") to an ordered SEQUENCE of `(set, min, max)`
steps. That is a widening of an existing contract, not a new site family (Kit request draft).

**The fact (R1.2).** The landmark is already a fact (`req_byte`, `req_set_maxoff`,
`req_landmark_maxoff`, `land_char`, `span_facts`). The family needs ONE more row, proposed:

    PF_FACT(BACK_WALK, "back_walk", 2, PF_DERIVED, 0, "src/facts/backwalk.c",
            "req_set req_run req_set_maxoff req_landmark_maxoff")

- **Value:** the landmark it walks from (which req fact, the scan byte's offset in the run); the
  direction; the segments outwards from the landmark, each `(alphabet set, min, max|unbounded,
  kind ∈ {plain, fixed, chain, superset}, may-host-start)`; the context item at the start, if any
  (`\b`, `\B`, `(?m)^`, in D161 add. 16's before-origin spelling); the EXCLUSION bit (an L byte is in
  no segment's alphabet); the G4 bit (S reads a group of P).
- **Declines:** `decline:g1` (backreference, call, atomic, possessive, lookaround in P),
  `decline:view-inside`, `decline:outer-not-exact` (a segment that may host the start is neither
  plain, chain nor the first-fixed), `decline:no-landmark`, `decline:multi-branch` (until branches
  compose by D151 add. 7).
- **Epoch:** 2, beside `req_landmark_maxoff`; it is an AST walk over the sealed IR. The plain / chain
  decision is an automaton over P's own sub-tree, never the artifact's machine. PF_DERIVED because it
  reads the req facts' landmark choice.
- **Readers:** the candidate-row selector (a RECOVER-style row "landmark-walk" on `cand_rows[]`), the
  kit request (the site facts, below), the census (`--emit-facts`), and the end-seeded corollary (the
  same fact over R instead of P).
- **Used for this census:** the facts layer cannot answer the tier yet (no such row). It answers the
  controls: `start_anchor`, `req_set`, `req_set_maxoff` and the route (C3, Census).

**Direction-free (R1.3).** The fact is stated as segments outwards from a known point, with a
direction bit. The same shape describes walking FORWARD from the landmark's end over S. The meanings
differ in one way that matters: a backward walk computes a SET MINIMUM (the smallest start), which no
priority rule touches (where_to_start.md §2.2 step 3). A forward walk must reproduce PCRE's PRIORITY
choice of end, so a forward run is exact only where it is POSSESSIVE-EQUIVALENT: the next item's first
set is disjoint from the run's set. That is the same boundary disjointness T3 uses, and the same
condition possessify discharges on. So the forward column of the tier table reads "the possessify
discharge condition". The fact needs no new field for it, only the direction bit.

## Tier table

First match wins. Every row also needs the conditions of the next section (G1, a non-empty P, the
floor and context rules); the "admission" column is the row's own predicate. "Forward" is R1.3's note:
what the same row means walking forward from the landmark's end. It is a note, not a design.

| row | admission (P's shape) | the walk (cost per landmark hit) | facts pcrec states | today's home | landmark exclusion is | forward (from the landmark's end) |
|---|---|---|---|---|---|---|
| T0 | P empty | none: the hit is the start | — | offset-0 rows (memchr, byte-class, first-*) | — | the window spans after the origin (D161, KIT-VERIFY `consumable_len`) |
| T1 | P has fixed byte width k | none: start = hit − k; P's positions verified as spans at fixed offsets | spans at offsets −k..−1 (the window site as today, k ≤ `MF_MAX_BACK` = 8; a longer P is a walk step with `min = max`) | offset-set, run-pinned, window spans, `end-minus-width` | not needed (fixed width is its own arm, D151 G2) | fixed spans after the landmark (today's `consumable_len`) |
| T2 | exactly one variable segment, and it is PLAIN `B{m,M}` (M may be unbounded); the other segments fixed; ASCII-only under utf8 | one back-scan over B (≤ M), the fixed segments as spans | `back_walk` (one plain segment + fixed ones), context item, floor | none (presence / handoff LOWER today); rev-inner HELD | a COST condition: linear walks, no repeated candidates | a forward scan over B to the run's end: exact iff the run is possessive-equivalent |
| T3 | forced boundaries (`LAST(earlier) ∩ ALPH(seg) = ∅` at every cut); every segment that may host the start is plain, a chain, or the first and fixed; any other segment may be SUPERSET (alphabet only) | one back-scan per segment over its alphabet, the count rule per segment; accepts only in may-host-start segments | `back_walk` (segments with kinds), context, floor; EXACT or SUPERSET mark (D161 add. 16) | none; rev-inner HELD | a CORRECTNESS condition (strong arm: disj or factor-free, D151 add. 5) | a chain of forward runs: exact iff every cut is possessive-equivalent |
| T4 | anything else regular-faithful (G1 holds) | P's reverse DFA from the hit, byte by byte (one-state loops become scan edges where shaped) | none to the kit: pcrec's own machine (D161 add. 5: automata stay pcrec's) | `reverse-pass` (end seed), rev-inner DFA hat (HELD) | correctness, D151 G2 three arms + add. 7 composition | the forward DFA (today) |
| — | G1 fails | no walk | — | presence-only / VM attempt loop; [OPT-VMSEED] LOWER | — | — |

T1 deliberately keeps today's form: a fixed-width P needs no walk, and is the degenerate chain whose
every segment has `min = max`. The kit already receives it as spans. T2 is T3's degenerate case (one
variable segment). T3's exact-chain kind is T4's degenerate case (a DFA that is a chain). One
mechanism, read at four widths, as where_to_start.md §1.3 item 3 read offset-0 / offset-k / window.

## Exactness conditions

Notation: `R = P·L·S` at the top level (after splicing un-quantified groups and peeling a mandatory
first iteration, rincensus's `flatten(peel)`). L is a literal run (a byte, or a caseless pair per
position). `j` is an occurrence of L, `lo` = `search_from`.
`starts(j) = { s ∈ [lo, j] : subject[s:j] ∈ L(P) }`, with views evaluated in the real subject.
The walk returns `s*(j) = min starts(j)`.

1. **G1 (unchanged):** P holds no backreference, call, atomic group or possessive quantifier (unless
   possessify discharged it), and no lookaround. A reverse walk builds the erased language, and
   where_to_start.md §2.6's `erase_atomic` row is wrong 11 / 6 times. Census: 374 corpus / 15 bench
   landmark rows stop here.

2. **Segments and forced boundaries ("non-overlapping", precisely).** Split P into segments
   `Q_1 … Q_r` (forward order), cutting before item i iff `LAST(P[:i]) ∩ ALPH(segment from i) = ∅`.
   LAST is the set of bytes that can END a non-empty string of the earlier part; it unions through
   nullable items, so OPTIONAL runs and `min = 0` counts are covered. ALPH is every byte the segment
   can consume. The finest such split is taken from the right (`tiers.py segments()`). Then, in every
   parse of `subject[s:j]`, segment k occupies exactly `[b_k, b_{k+1})`, where `b_k` is where a
   back-scan over `ALPH(Q_k)` from `b_{k+1}` stops. The one exception is the segment holding the
   start, which may begin inside its scanned extent. Proof: the byte before `b_k` is either the last
   byte of the earlier part (in LAST, hence not in ALPH(Q_k)) or outside the match. A nullable segment
   whose extent is non-empty cannot be empty in a parse, because those bytes cannot belong to an
   earlier segment.
   - "Adjacent classes disjoint" in the brief is the special case where each segment is one class
     run and LAST of the previous one is its class.
   - `[a-c][a-z]+@` is NOT forced: `[a-c] ⊂ [a-z]`, so the first segment can start inside the run.
     It is decided by rule 3.

3. **May-host-start segments are walked exactly.** Segment k can hold the match start iff every
   earlier segment is nullable (always for `Q_1`). Such a segment must be one of:
   - PLAIN `B{m,M}`, decided on its automaton: one set B, every live state sends all of B, and only
     B, to one successor. Its starts are `[max(b, e−M), e−m]`, the minimum taken, subject to the
     context item.
   - an EXACT CHAIN: its own reverse DFA is a chain, and accepts are recorded as it walks its extent.
   - FIXED and first (`Q_1` at width w: start `e − w`).

   Any other segment may be a SUPERSET: back-scanned over its alphabet, content left to the anchored
   verify. This is exact because a non-hosting segment's extent is forced at both ends, so a failed
   content check means `starts(j)` is truly empty for this j (no smaller extent exists). The model's
   segment walk implements exactly this rule (0 wrong). The population this rule turns away is "T4
   outer": 99 corpus / 9 bench rows (`kv-quoted`'s `\b[a-z_][a-z0-9_]{0,31}`, `ipv4`, `email/orig`).
   Unlock (filed, not designed): a context item can narrow a non-plain outer segment to one start
   (`\b` before a `\w`-subset run forces the run start). That is kv-quoted's shape.

4. **Counts.** An inner plain segment whose scanned extent exceeds M, or falls short of m, ends the
   walk (no parse continues through it). The may-host-start rule above clamps at `e − M`. The model's
   `no_max` mutation (ignore M) is wrong 46 times, so the max count is load-bearing.

5. **Leftmost across landmark hits (which-occurrence, D151 G2).**
   - **Plain runs need no exclusion for CORRECTNESS.** Let `s' ∈ starts(j')`, `j < j'`, `s' < j`. Then
     `subject[s':j']` is all in B with length in `[m, M]`, so `subject[s':j]` is all in B with length
     `< M`. If `s' < s*(j)` its length also exceeds `j − s*(j) ≥ m`, so `s' ∈ starts(j)`, a
     contradiction. Hence `starts` is monotone in j. The context item depends on s only, so it does
     not change this. `\S+@\S+` (bench `syntax/cls-s-uc`, `@ ∈ \S`) is therefore exact as a T2 walk.
     What it lacks is linearity: every `@` re-scans the run. The model's ungated plain/chain rows agree
     (43 rows, 5,579 checks, 0 wrong; reported, not gated).
   - **Exclusion buys COST for T2.** If an L byte is outside B, a back-scan stops at the previous
     occurrence by itself. Walks never overlap (total O(n + hits)), the floor-at-previous-hit device
     is never needed, and the stream is ascending with no repeats (D161 add. 7) without
     de-duplication. Without exclusion the same exactness at linear cost needs a kit-side run memo
     (the start of the B-run containing the hit, kept between hits, D161 add. 2's stateful form). That
     is a method, so it is the kit's choice once the fact says "plain, not excluded".
   - **Non-plain prefixes (T3, T4) need a strong arm for correctness:** `disj`
     (`bytes(L) ⊄ alphabet(P)`) or factor-free (D151 add. 5), and branches compose only all-strong
     or all-fixed-same-width (D151 add. 7). The census counts T2/T3 with `disj` as the exclusion. The
     factor-free arm adds 0 corpus / 2 bench rows.

6. **G4: S reads a group of P → LOWER, not one verify per hit** (where_to_start.md §2.2 step 1
   correction, LF-E1). The first hit with a non-empty walk gives a lower bound; the ordinary search
   runs from it. The model does exactly this for the `srefs` rows; without it, `(x?)(?i:abcdefghijkl)\1`
   was wrong 63 times in the first model run. 36 of the 197 admitted corpus T2 rows (and 6 of 13 bench, the
   `bak-*` and `dup-param-detect` VM cells) are LOWER rows. G4 stays the closed predicate of LR-S5
   (DUPNAMES: every member of `refs[]`).

7. **Context at the start.** A leading `\b`, `\B` or `(?m)^` is evaluated at each accepted position,
   reading `subject[s−1]` even when `s == lo`, never below the subject start (where_to_start.md §2.5
   `lo0`/`slice` rows). It is D161 add. 16's context span before the origin, with its absent-byte bit.
   The model's `no_ctx` mutation is wrong 89 times. A view anywhere else in P sends P to T4 (90 corpus
   rows).

8. **The floor.** No start below `search_from`; reads below it only for context. In find-all, the
   next search starts at the previous match END (R is non-nullable, since L is non-empty).
   `restart_s1` stays a mutation (where_to_start.md §2.6).

9. **utf8.** A plain run is byte-exact only if its set is ASCII-only. A non-ASCII class reaches the
   walk as lead and continuation bytes, a SUPERSET (D161 add. 10/16). Such a segment is admitted only
   where it cannot hold the start (superset kind); where it can, the row declines to T4. An ASCII
   landmark is a character start, and a walk that stops on a non-member byte lands on an ASCII byte or
   after a complete character, so no round-up is needed. A landmark that is a non-initial byte keeps
   the handoff's `PCREC_START0_ROUNDUP` obligation (where_to_start.md §2.5).

10. **Forward verify cost** (where_to_start.md §2.7) is unchanged. A failed anchored verify can re-read
    far past the next hit. The `fallback` give-up (hand the current `s*` to the ordinary scan as its
    startpos, 0 wrong) applies to every tier.

## Census

**Instrument.** `revwalk_evidence/tiers.py` is a parse-only reader: rincensus's Reader, flatten,
landmarks, NFA and arms, plus this lane's segment, plain, chain and scan-edge decisions on automata.
No pattern is compiled for the tiers. pcrec runs only as `--list-source`.

**Populations.**
- CORPUS: every `pattern` / `pattern-esc` line of every `tests/**/*.rxt` in the worktree, deduplicated
  by (pattern, encoding, flags): 5,203.
- BENCH: the bench list this repo holds, `docs/design/startset/census.tsv`'s 345 bench rows (an
  OLDER export of `bench/*/patterns/*.rx`; flags are not recorded there, so `icase` is false). To
  these is added `subtri/5b-mask-email~`: the bench file is not in the repo, so its leading class and
  `@` come from subtri_report.md and the suffix is an approximation. The tier reads only P and L.
- Not counted: unparsed (660 corpus / 17 bench), patterns with an item the reader approximates
  (`\X`, `\p`, `\C`; 273 / 17), anchored (470 / 25), no landmark (1,539 / 93), no common landmark
  across branches (248 / 45), landmark at the start (P empty, 1,050 / 84).

"Best landmark" is the rarest scan byte under the shipped prior (`tests/findings/default_ppm.tsv`),
admissible tiers first. "Admitted at F = 2" is D149's unmeasured default: the landmark is >= 2x rarer
than the pattern's whole first-byte set.

**Corpus** (5,203 patterns; 3,800 unanchored and parsed; 963 with an inner landmark):

| tier | all | composes (D151 add. 7) | + exclusion (T2/T3) / strong arm (T1, T4) | admitted at F = 2 | of those, unbounded | of those, S reads P's groups (LOWER) |
|---|---|---|---|---|---|---|
| T1 fixed | 105 | 105 | 91 | **78** | 0 | 1 |
| T2 one plain run | 256 | 256 | 217 | **197** | 116 | 36 |
| T3 forced segments | 39 | 39 | 37 | **15** | 4 | 2 |
| T4 reverse DFA | 189 | 189 | 114 | **92** | 4 | 6 |
| G1 decline | 374 | 367 | 208 | 197 | 0 | 10 |

**Bench** (346 patterns; 287 unanchored and parsed; 65 with an inner landmark):

| tier | all | composes | + exclusion / strong arm | admitted at F = 2 | unbounded | LOWER |
|---|---|---|---|---|---|---|
| T1 | 14 | 14 | 10 | **4** | 0 | 0 |
| T2 | 21 | 21 | 19 | **13** | 10 | 6 |
| T3 | 6 | 6 | 4 | **3** | 1 | 0 |
| T4 | 9 | 9 | 5 | **5** | 2 | 1 |
| G1 | 15 | 15 | 7 | 7 | 0 | 0 |

Reading the tables:
- **Falls to the general reverse DFA:** T4 is 92 corpus / 5 bench admitted rows. 99 of the 189 corpus
  T4 rows are there because the start may lie in a non-plain segment ("outer"), the other 90 because
  P holds a view. All 9 bench T4 rows are "outer".
- **Chain without a strong arm:** 41 corpus / 2 bench rows are T2/T3-shaped but have neither
  exclusion nor the factor-free arm. For T2 rows among them, exactness still holds (rule 5); only the
  linear-cost argument is missing. The factor-free arm alone adds 0 corpus / 2 bench rows.
- **SUPERSET segments:** 2 of the 15 admitted corpus T3 rows and all 3 bench T3 rows
  (`loglines/stack-frame`, `utf8/cls-s-nbsp`, `utf8/cls-s-ucp`) need the superset rule.
- **Unbounded:** 116 of the 197 admitted corpus T2 rows have an unbounded run (the D161 add. 17
  case proper); the other 81 are bounded counts (`{0,32}`, `?`) that today's fixed-offset spans
  cannot state either when the bound exceeds `MF_MAX_BACK = 8`.

**Examples** (`summary.txt` lists more; bench ids are `docs/design/startset/census.tsv`'s):
- T1: `loglines/iso-ts` and `loglines/uuid` (L = `-`), `wild-secrets-slack-webhook-url` (L = `/B`).
- T2: `subtri/5b-mask-email~` (`[%+\-.0-9A-Za-z_]+@`, L = `@`, excluded, scan-shaped);
  `bounded/csv5` (L = `,`, `[^,\n]{0,32}`), `bounded/dotted4` (L = `.`), `loglines/ipv6` (L = `:`),
  `wild-waf-crs-942160-sleep-benchmark` (L = `(`, two branches, both T2), `syntax/bak-1`
  `(\w+) \1` (L = space, LOWER), `capability/dup-param-detect` (L = `=`, LOWER).
- T3: `loglines/stack-frame` (L = `(`, five segments, two of them superset), `utf8/cls-s-nbsp`
  `a\sb` (the non-ASCII `\s` segment is superset), corpus `tests/classes/multi_chain.rxt:33`
  `[a-c]{2,4}x[0-9]{2,4}y[A-C]{2,4}z...` (five exact plain segments).
- T4: `loglines/kv-quoted` (`\b[a-z_][a-z0-9_]{0,31}="`, outer `[a-z_]` ⊂ the run's class),
  `loglines/ipv4` (alternation of fixed widths in the hosting segment), `capability/tag-pair-match`
  (outer `<` + optional attribute run), `email/orig` (alternation of runs).
- G1: patterns whose prefix holds a backreference or atomic group (`(?>...)`, possessive `++`).

**Controls (K35).**
- **C1** (`selftest.txt`): 20 hand rows, positives and negatives per tier, including stack-frame (T3),
  `[a-c][a-z]+@` and `x*[A-Z][A-Z0-9]*@` (T4 outer), `[a-z]+xy` (T2 not strong), `\w+\b-x` (T4 view):
  20/20. With `--sabotage chain` (every non-fixed P called T2) it FAILS, 11/20.
- **C2** (independent method, same reader): P's minimal reverse DFA is a chain ⇒ the segment rule
  admits T2/T3: 252 corpus / 19 bench chain rows, **0 violations**.
- **C3** (`facts_control.txt`, pcrec's own `--emit-facts`, no shared code with the reader; 954 corpus
  / 62 bench landmark rows compiled, the rest refused):
  - `start_anchor` is `unanchored` on every row: 0 disagreements.
  - Landmark bytes in `req_set`: 922 agree, 30 `req_set` absent, **2 violate**:
    `possessify.rxt:4327/4354`, `a+\b\x{e9}` caseless under utf8. The reader folds only ASCII, so it
    called `\xA9` necessary where `É` makes it optional. A real reader limit. Both rows are T4/G1, so
    no admitted count moves.
  - Unbounded move-back matches `req_set_maxoff` for the excluded byte: 244 / 19 agree, 0 disagree.
- **Model** (`model.txt`): see Summary; 0 wrong / 74,824 checks; all three mutations detected.

**Route split of the admitted rows** (C3, from the `RX_ENGINE` stamp): corpus T1 dfa 46 / vm 28,
**T2 dfa 88 / vm 109**, T3 dfa 7 / vm 8, T4 dfa 47 / vm 45, G1 dfa 56 / vm 138; bench T1 3 / 1, T2 7 / 6,
T3 3 / 0, T4 3 / 2. About half of every exact tier compiles to the VM, where the walk's reader is the
VM's attempt loop (the [REQRUN-VM] handoff site), not the DFA's RECOVER table.

**The end-seeded corollary** (the whole pattern's tier, as the reverse pass from a match end would
walk it, unanchored parsed rows): corpus T1 573 / T2 569 / T3 110 / T4 296 / multi-branch 283 / views or G1 1,969;
bench T1 82 / T2 39 / T3 15 / T4 41 / multi-branch 48 / views or G1 62. `end-minus-width` already serves the T1 column.
T2/T3 would replace the reverse DFA with back-scans; worth it only where the reverse pass is measured
as a cost.

**The three standing questions (docs/design/CLAUDE.md).**
- *Measurement regime:* relevant only for the admission threshold F (D149, unmeasured, reported at
  F = 2 with the raw ratio in `rows.tsv.gz`). The tier decision is structural and has no clock. Any
  build is judged by D161 add. 17's own measured cell (5b: x75 instructions) and a second twin.
- *Independent control:* C3 (pcrec's facts layer vs the reader) and the model (libpcre2's search loop
  vs the walk). C2 shares the reader with what it controls, which is why C3 and the model exist.
- *What moves when data is regenerated:* only the F = 2 admission (the byte-rate prior). The tiers
  themselves are pattern facts.

## Fit with existing mechanisms

- **D161 and its addenda.**
  - Add. 3 (the window search subsumes the other searches) and add. 9 (pcrec chooses the ORIGIN): the
    landmark's window search stays as it is. The walk is a second, SEEDED operation on its
    candidates, which is why it fits the ADVANCE contract rather than the window site (R2).
  - Add. 4 (pcrec hands a sub-problem): pcrec states the walk only where T1-T3 hold and keeps T4 (add.
    5: automata stay pcrec's).
  - Add. 5 said "unbounded is automata and outside memfn"; add. 17 reverses that for STRUCTURED
    unbounded walks only. The tier table is the line: T2/T3 are a chain of simple searches, which is
    add. 5's own phrase, and T4 is the automaton.
  - Add. 7: the stream obligations (complete, ascending, no repeats) hold under exclusion by
    construction. Without it they need the run memo.
  - Add. 10/16: SUPERSET segments are exactly the "inexact prefix" add. 16 describes. A T3-superset
    candidate carries no proof past the first superset segment.
  - Add. 16's context spans before the origin are the start's context item.
- **window_search_game.md §7, "the unbounded move-back".** Reading (b) ("back over class C, at most
  until the previous stop") is T2 with exclusion. The "previous stop" bound is automatic, because an L
  byte stops the scan.
- **[ENG-TACTICS] rev-inner, the "house of cards" (D151 add. 5-7; LF-E1).** Does the string-of-spans
  tier avoid each recorded unsoundness? Plainly:
  - *Which-occurrence / G2* (rust #1354): AVOIDED for T2 by the monotonicity proof (rule 5); exclusion
    is not needed for correctness there. NOT avoided for T3/T4: they inherit G2's strong arm.
  - *The floor* (add. 5: `[a-z]+xy` on `abxcdxy`, a floored walk reports 3, truth 0): AVOIDED by
    construction. The chain walk never floors at a previous hit. With exclusion it stops there by
    itself, and without it (plain only) it walks to the true run start.
  - *Per-branch P_i differ* (add. 6 F1): NOT avoided. Branches verify at each branch's own `s*_i`; the
    census admits multi-branch rows only under add. 7's composition rule.
  - *Composition* (add. 7: a fixed branch beside a strong one): inherited unchanged. Fixed is a weak
    arm, so mixing T1 with T2 branches needs every branch strong.
  - *LF-E1* (S reads P's groups): inherited. Those rows take LOWER (rule 6).
  - *Erased atomic / G1*: inherited unchanged (decline).
  - *DUPNAMES G4 (LR-S5)*: inherited unchanged.
  - *Quadratic forward verifies* (§2.7): inherited, with the same `fallback` give-up.
  - *Views at the lower boundary* (`lo0`, `slice`): inherited as rule 7/8.

  So the tier does not escape the house of cards. It removes two of its floors (which-occurrence for
  plain runs, the floor device) and keeps the rest as declared conjuncts. rev-inner stays HELD outside
  the admitted tiers, as ruled.
- **[MATCH-SPLIT] / [COMPOUND] (D163).** The walk is a LOCATE part. A landmark-seeded row with a T4
  fallback is compound client 3's shape (per-branch locators, P finishes) and needs no compound to
  start: one RECOVER-style `cand_rows[]` row ("landmark-walk", hands START, takes EXISTS) sits beside
  `landing`. The compound is the home only if a T4 reverse machine of P is a separate part.
- **where_to_start.md.** §1.4's table already reserved rows `rev-inner-bounded` / `rev-inner` (EXACT)
  and `handoff-rev` (LOWER). The family fills them: rev-inner-bounded = T1 + bounded T2, rev-inner =
  unbounded T2/T3 (+ T4 behind the HOLD), handoff-rev = rule 6's LOWER. Its §4 census (77 corpus / 8
  bench exact-rev at any ratio) used literal-only G2. This census's T2 + T3 at F = 2 is the same
  question, with the segment rule and on today's larger corpus.
- **[SCANEDGE-SET] / scan edges (R1.1):** see The family. A one-state relaxation of precondition (1)
  is the cheap pcrec-side half and helps forward machines too. The kit chain is the general form for
  landmark seeds.
- **PATFACTS (R1.2):** the `back_walk` row above.
- **The VM's span scans (R3).** The VM already runs its class repeats as kit ADVANCE scans:
  `vm_emit_span_scan` (`src/gen/emit_vm.c`) emits ONE ADVANCE site, `DELEG_SITE` VMSPAN at stride 1
  and VMSTRIDE above, for the possessive and greedy arms and the lazy arm's rmin prefix. It runs
  FORWARD only, one repeat per site. So `C1+C2+` emits two scans today, with the dispatch, the cursor
  store and the rung test between them. A widened ADVANCE (a sequence of `(set, min, max)` steps)
  would let the VM hand both as ONE site: the forward column of the tier table, on the engine that
  already uses the contract. The VM routes hold 109 of the 197 admitted corpus T2 rows and 8 of the
  15 T3 rows (C3 route split), so the VM is the larger reader of the chain form, not a side case.
- **One disjointness fact, three readers (R3).** The "non-overlapping" condition is a boundary
  disjointness between adjacent items, and three places compute a form of it today:
  - **possessify** (`src/opt/possessify.c`): FIRST(X) ∩ FOLLOW(Q) = ∅, looking FORWARD from a
    quantifier;
  - **scan edges** (`src/opt/scanedge.c`): the uniform exit of a DFA state, which is the same fact
    read off the machine rather than the AST;
  - **this family**: LAST(earlier part) ∩ ALPH(segment) = ∅, looking BACKWARD.

  They are mirror images of one relation: at each cut between adjacent items, which bytes can END
  the left side and which can be CONSUMED by the right side. For a single-class run, ALPH = FIRST =
  LAST = its set, so `C1+C2+` with C1 ∩ C2 = ∅ satisfies both directions at once. My leaning: ONE
  fact, a per-cut disjointness record over the flattened spine (each cut: forward-disjoint,
  backward-disjoint), computed once on the sealed IR and read by all three. Each reader keeps its
  OWN extra conjuncts on top. possessify keeps (U1) unique iteration, (U2) prefix-free and the lazy
  conjunct: those carry its priority obligation, and a reverse walk does not need them because it
  takes a set minimum. The walk keeps the may-host-start rule. scanedge keeps its machine-level test,
  because its machines are class-split and minimised and can be uniform where the AST cut is not.
  Merging the three is a simplification, not a precondition of the family. I filed no row for it
  (no IDs in this lane); it belongs with the `back_walk` fact if that is ruled.

## Kit request draft

(Draft only: no R number, not filed. Text in the ledger's own shape.)

> **R-?? (pcrec manager) — the ADVANCE contract widened to a WALK: a sequence of `(set, min, max)`
> steps in either direction, seeded at a window site's candidates**
>
> **Customer:** D161 addendum 17 (Frank, 2026-10-29: the move-back may be unbounded; the family
> first), lane revwalk's tier table (docs/dev/lanes/revwalk_report.md). Trigger cell: bench O-109
> case 5b mask-email (subtri: an `@`-driven twin, x75 instructions).
>
> **Facts pcrec will state, per walk site:**
>
> | fact | meaning |
> |---|---|
> | seed | the window site whose candidates seed the walk, and the landmark's offset from that candidate (the walk starts at the landmark's first byte, moving away from it) |
> | direction | BACKWARD (recover a start) or FORWARD (reserved; no site states it until a forward row is ruled) |
> | steps | an ordered list outwards from the seed; each: a 256-bit byte set, `min`, `max` (or `MF_SPAN_UNBOUNDED`), and HOSTS (1: the walk's result may lie in this step; 0: it may not) |
> | the boundary fact | for every step, no byte that can end the steps beyond it is in its set (pcrec asserts it; the kit may check it against the sets and refuse) |
> | exactness | per step EXACT (every byte string the step's count rule accepts is in P's language there) or SUPERSET (a filter: pcrec verifies the candidate) |
> | context | at most one context item on the result position, as D161 add. 16's span before the origin with its absent-byte bit |
> | floor | the result is never below the floor expression (`search_from`); reads below it only for the context item, never below the subject start |
> | monotone | 1 iff results are ascending across seed hits without de-duplication (pcrec states it where the landmark is excluded from every step's set). Always stated, never presumed |
>
> **Producer obligations pcrec asserts:**
> - steps are in walk order;
> - a HOSTS step is EXACT;
> - `min <= max`;
> - a step with HOSTS 0 is never the outermost;
> - G1 holds for the walked part;
> - pcrec states no walk where S reads a group of the walked part unless it consumes the result as a
>   LOWER bound (its own business, stated in the frame).
>
> **What pcrec needs back:** a stream of results, one per seed hit whose walk accepts: the SMALLEST
> accepted position not below the floor, with the seed hit it came from. The stream is ascending
> with no repeats; EMPTY means no match. Also: whether any SUPERSET step was taken (so pcrec keeps its
> verify), and, as today, the proof class for the positions the kit proved.
>
> **Not asked:** any method: how a step is scanned, whether a run is memoised, SIMD, or whether the
> kit fuses the walk with the seed's scan (D157).
>
> **Sabotage ids:** none requested at filing; the build's own range from main's ledger.

## Questions for Frank

1. **Where should the one-run case land first: pcrec's reverse machine with scan edges, or the kit's
   widened ADVANCE?** Both reach 5b: 114 of the 197 admitted corpus T2 rows already have scan-shaped loops in
   P's reverse DFA, so a rev-inner DFA hat would scan them today. The kit form also covers the
   superset segments (stack-frame), builds no reverse machine for P, and is yours-ruled to be the
   kit's (R2). My leaning is the kit form, with the scan-edge one-state relaxation as a separate small
   pcrec row because it helps forward machines too. I would like to hear whether you see the two as
   competing or as two halves.

2. **Should the walk be allowed over the "superset" segments, whose content is checked only by the
   verify?** This is what admits stack-frame's identifier runs: exact at the boundaries, a filter in
   between. It costs a verify on candidates the walk cannot rule out, which pcrec runs anyway. Leaning
   yes, labelled SUPERSET per D161 add. 16 so no proof is claimed past it.

3. **Landmark exclusion for plain runs is about cost, not correctness. Do we use that?** `\S+@\S+`
   (`@` inside `\S`) is exact as a T2 walk but re-scans the run at every `@` unless the kit remembers
   where the current run started. D151's Q3 ruled that pattern "K7, not rev-inner". My leaning: build
   with exclusion first (217 of the 256 corpus T2-shaped rows have it; the 39 without it are
   shapes like `([a-z]+)x` and `.*=`) and file the non-excluded plain
   rows as an unlock whose trigger is a measured `\S+@\S+`-shaped cell. Is there a reason to want
   them in the first build?

4. **What should be measured next, before any design pass beyond T2?** 5b is the T2 trigger. For
   T3, `loglines/stack-frame` already has a measurement: where_to_start.md's A01 L1 (the DFA-hat
   twin, -72.2% on Linux). So T3's open question is narrower: does a kit chain walk with superset
   segments beat the DFA hat on that same cell, or only match it? For the VM route,
   where_to_start.md's item 1 (a hand twin of `dup-param-detect`: memchr `=`, walk back over `\w`,
   one anchored attempt) is the trigger, and it is a T2 LOWER row here. My leaning: measure the
   dup-param twin first. It is a losing VM cell today and exercises the half of the population (VM
   routes) that the DFA hat cannot serve.

## STATE AT HANDOFF

STATE: delivered. Committed on `lane/revwalk`: this report, `revwalk_evidence/` (tiers.py, model.py,
facts_control.py, outputs, CLAUDE.md), the history-index line. Rulings file read through R4 (last
entry applied: R4: no box load after 19:00; the census finished well before). Nothing under src/ cli/ lib/ memfn/ touched; no build, no suite run owed. Runs
were made: one `make -j16` (to get `build/pcrec` for `--list-source` / `--emit-facts`), the census
(~7 min, parse-only), the facts control under `scripts/boxlock run --label revwalk-facts`, the model
(~10 min, libpcre2 ctypes). Open for a follow-up: the forward self-loop census for the scan-edge
relaxation (R1.1) on pcrec's own machines; the reader's non-ASCII caseless fold (C3's 2 rows); the
context-narrowed outer segment unlock (kv-quoted).
