# One instruction stream: synthesis of round 1 (lane stream-synth)

Author: lane stream-synth (opus), 2026-11-01. Inputs: COMMON.md and the three approach
drafts, `clean/` (clean sheet), `today/` (grown from today's code, 14 glue sites X1-X14 with
file:line), `prior/` (prior art). Read-only on the repo. Four single-pattern `build/pcrec` runs
(outputs in `runs/`) check claims the drafts lean on; they are cited where used. Nothing here
is a ruling.

Notation: **C** = clean, **T** = today, **P** = prior. "AGREE" = all three, independently
(the drafts were blinded from each other). "2/3" = two drafts. "ONLY-x" = one draft.

---

## 1. Agreement map

| element | clean (C) | today (T) | prior (P) | verdict |
|---|---|---|---|---|
| the artifact | one typed record stream, D182 widened to the whole artifact | same; `cand_nodes[]` hands graph is the existing outer half, D182 VM body the inner half | same | **AGREE** |
| "dfa" / "vm" | derived stamp: "dfa" iff no frames | derived: "dfa" iff no M instruction | derived: "dfa" iff no CHOICE reachable but the start loop's | **AGREE** |
| instruction families | control/choice, consume, automaton (`AUTO` with exit modes), thread set (`THREADS`), search/scan (kit), assertion/call | M (VM control), D (`DSEG` with exit protocol), K (kit leaves, keyed by operation), C (controller) | K kit, A automaton (`DFA(mode)`, `RDFA`, `ONEPASS`), D deterministic consumers, V backtracking control, B barriers with declared effects | **AGREE** on VM / automaton / kit as the core three; DIFFER on the extras (below) |
| automaton exit modes | FIRST, EXISTS, LIST asc/desc, STATE, TAGGED | COMMIT, ENUM, VIAB, BOUND | exact, ends, gate, locate | **AGREE** in substance: commit-one (FIRST/COMMIT/exact), enumerate-ends with one resume point (LIST/ENUM/ends), necessary-condition only (EXISTS/BOUND/gate). VIAB ONLY-T, STATE and TAGGED ONLY-C |
| separate controller family | no: the start loop is the `FIND` generator at the bottom of the one choice stack | yes: C family (`LOOP-CANDIDATES`, `RELOCATE`, `FIRST-NONZERO`) | no: the start loop is a `CHOICE` over starts that `FIND` prunes | **DIFFER** (2 vs 1) |
| seam contract fields | pos, slots, proof, stack, meters | position TYPE (AT/LOWER/UPPER/CAND/SPAN/ENDSET/NOMATCH) + typing rule, captures, proof, resume depth | pos+dir, caps, proof, reentry, effects, `exact` (the admitting row) | **AGREE** on pos, captures, proof, re-entry. Typed position + typing rule ONLY-T; `exact` field ONLY-P; meters ONLY-C; declared effects C+P (2/3, T puts them on K kinds) |
| re-entry | one choice stack; every instruction with >1 continuation pushes its own resume; deterministic ones push nothing | one backtracker (the fail label); `DSEG ENUM` pushes one ordinary resume label; nothing else re-enters a segment | `CHOICE` frames, `FIND-next`, `ENDS-next`, `START-next` | **AGREE** |
| soundness rule (statement) | F replaces S iff it delivers the same first successful (end, slots) for every entry | same, word for word in substance | same | **AGREE** (strongest single convergence of the round) |
| core admission test | possessify's unique-iteration test is rule D's single-class case | possessify `pcrec_uniq_iteration` + disjoint follow is R1(b) | auto-possessification (PCRE2, .NET, pcrec) is E1a | **AGREE** |
| who segments | a planner pass between optimization and rendering, one declared first-match table over stretches; row 7 (backtrack) always admits | a segmenter after today's passes: controller table (= `cand_rows[]`) + region table, top-down; row 6 (vm) always admits, recurses into children | a planner walking the IR with one first-match table, plus a FUSE pass | **AGREE** on the table, the always-admitting floor, recursion into backtrack regions, and "price chooses only among SOUND rows" |
| fusion / maximality | implicit (row 3 "absorbing the tail") | maximality is a HARD RULE, not a price | fuse when the price says one machine beats N; default "no V reachable: fuse everything" | **DIFFER** in name, near-AGREE in effect (§2 picks) |
| captures at seams | `SET` at a seam; "captures are not a reason for the VM" | derived SETs at seams | "captures at seams cost nothing": `SAVE` at a seam | **AGREE** |
| captures INSIDE a segment | `AUTO TAGGED` when [ENG-TDFA] exists; else THREADS or B | derived offsets only; tagged DFA is hole H1, not designed | `ONEPASS` only; "No TDFA: it is POSIX or leftmost-greedy" | **DIFFER**, and the top hole (§6 #1) |
| ambiguous regular stretch with captures | `THREADS` (Pike thread list) | `R3 GUIDED` (reverse viability pass, then a frame-free priority walk) | `MEMO` (BitState-style failure memo); Pike held under D77 | **DIFFER**: three different mechanisms for one gap |
| kit's role | instructions with declared effects; FIND is a generator; one `SPAN` site kind | K leaves keyed by OPERATION; `MF_SK_*` engine-context kinds deleted; one `SKIP` | K family, facts only (D157); `WALK` | **AGREE** (one skip/span kind; kit keyed by operation, not engine) |
| finder / bounder / finisher | FIND / AUTO or SPAN back / the rest of the stream | controller rows LOCATE/RECOVER/FINISH over typed hands | the explicit organizing frame (L1: "the seams are universal, only granularity varies") | **AGREE**; P names it |
| callouts | ε to the analysis if non-consuming, a barrier if consuming (§11.6) | zero-width item on a one-pass segment's single thread | ε for a gate via its `effects`; consume breaks it | **AGREE** |
| lookaround | `ASSERT` sub-stream planned under an atomic context; regular capture-free body = `AUTO EXISTS` | `GUARD` on a one-pass segment; non-one-pass declines to M; D164 END_MARK stays a lowering | E5: captureless regular body folded into the adjacent DFA as context at an EDGE; else `ORACLE`/gate seam | **AGREE** on "captureless regular lookaround is a predicate, not a reason for the VM"; DIFFER on where it may sit |
| atomic / possessive in source | atomic context makes D hold by definition | R1(c): REVERSES today's treatment (today it is an erasure making the prefilter a superset) | `COMMIT` in V | 2/3 explicit (C, T); T's "reversal" framing ONLY-T |
| forced to backtracking | backref into an ambiguous stretch; ambiguous recursion; non-atomic lookaround; consuming callout | M "where none holds", same list in effect | V "where no row applies"; E6 excludes the same backref/callout cases | **AGREE** |
| worked patterns with no benefit | 1, 7, 10 | 1, 7, 10 (byte-identical targets) | 1, 2, 7, 10 | **AGREE** (P also counts 2 as none) |
| first proof | byte-identical scaffolding as records | byte-identical SKIP record in both emitters; then the landmark walk as records | byte-identical DFA top level as records; then the hybrid prologue + a seam record | **AGREE**: byte-identical first |
| first benefit proof | the one-pass capture route behind a test-only lever | R1 COMMIT islands inside the VM, after a census | the deterministic finish (B1), after a `resume-points 0` census | 2/3 (C, P) on B1's route; T picks VM islands |
| the largest loss | the two engines stop being each other's check | pure-DFA properties become derived, a segmenter bug costs them | the whole-pattern DFA needs a fusion decision that can be wrong (a slowdown) | DIFFER in which loss; T and P are the same loss seen from two sides |

**What converged independently, without each draft seeing the others** (the strongest
evidence this round has): the one-sentence soundness rule; possessify's unique-iteration test as
its workhorse; captures at seams as plain stores; one choice stack where a deterministic
segment pushes nothing; the planner as a first-match table whose floor always admits; the kit
as operation-keyed instructions with one skip kind; non-consuming callouts as ε; "dfa"/"vm" as
derived stamps; patterns 1, 7, 10 as the degeneracy test; pattern 3 as the archetype of the
benefit; byte-identical proofs first.

---
## 2. The combined approach

**The artifact is one program.** It is a sequence of typed instruction records, built and
rendered the D182 way ("the record is the source"), for the WHOLE artifact: search loop,
locators, match body, captures, kit sites. No section is "the DFA" or "the VM". `RX_ENGINE`
survives as a derived stamp ("dfa" = no choice frame is ever pushed above the start
generator).

**Four families of instructions**, each kind one row of one kind table with one renderer:

| family | kinds (union of the drafts, de-duplicated) | re-entry |
|---|---|---|
| **choice** (today's VM) | `CHOICE`, `GOTO`, `FAIL`, `SET` (trailed), `CUT`, `CALL`/`RETURN`, `METER`, `ACCEPT` | the only frames |
| **automaton** (today's DFA) | `AUTO(M, dir, exit)`, exit ∈ {COMMIT (the priority-first end), ENUM (the ends in preference order, one resume point), GATE (necessary condition only: reject, never commit), EXISTS (a lookaround body)}; a state that loops on a class renders as a kit SKIP | ENUM only |
| **kit** (facts in, method the kit's) | `FIND` (the candidate generator), `SKIP(set, dir, stride)`, `VERIFY(run)`, `MISMATCH(ref)`, `PRESENT(terms)`; keyed by operation, never by engine | `FIND` only (next candidate) |
| **barrier** (declared effects) | `BREF`, `ASSERT`, `CALLOUT`, `PART` (a compound sub-artifact) | callouts may fail; `ASSERT` is atomic |

Consume kinds (`LIT`, `CLASS`, `SWITCH`) are shared by the choice and automaton families.

**Pick 1, no separate controller family (C+P over T).** The start loop is the `FIND` generator at
the bottom of the one choice stack; "advance to the next start" is a backtrack into it. That
deletes the second "next start" loop (the DFA search loop vs the VM retry advance, K49) instead
of re-housing it. T's real insight stays: today's `cand_nodes[]` hands graph IS the first draft
of the stream's top, and its `CAND_HAND_*` types become the seam's position types. Whole-artifact
composition (compound split, arch variants) stays a controller ABOVE the stream (C's migration
note); it chooses between artifacts, not between stretches.

**The seam contract** (merged; every boundary, any pair of families):

| field | content | from |
|---|---|---|
| `pos` | a TYPED position: `AT p`, `LOWER`/`UPPER p`, `CAND p`, `SPAN(s,e)`, `ENDSET` (ordered, stated by what), `NOMATCH` | T (generalizes `CAND_HAND_*`) |
| `slots` | the one capture array in the parent's numbering (D163 add. 3), trailed | all |
| `proof` | per-offset proven byte sets, `consumable_len`, context spans, END/START pins, character-boundary under UTF-8 | all; UTF-8 bit T |
| `reentry` | none / FIND-next / ENUM-next / a CHOICE frame / START-next with a FLOOR (never re-walk below the last attempt's floor) | P (floor = Rust's quadratic guard) |
| `effects` | for kit and barrier kinds: reads, writes, cursor movement, may-transfer; undeclared = may write everything | C+P (D182 (c) ruling 1) |
| `exact` | the admission row that made this seam sound, so one deny axis per row can test it | P |
| `meters` | the step and work budgets charged by the instructions that loop | C |

**Pick 2, the typing rule (ONLY-T, adopted).** A SUPERSET segment (any erasure: atomic made
transparent, lookaround made ε, a count collapsed, a backref replaced by its referent) may emit
only `LOWER`/`UPPER`/`CAND`/`NOMATCH`. That one sentence replaces H3's three flat conjuncts,
`pcrec_cand_lang_exact`, lmwalk `g1` and compound A2/A4 (T §0.2), and it is the class of defect
that has shipped as silent match loss twice. It is the best single idea in the round that only
one draft had.

**Who segments.** A planner pass, after today's optimization passes, writes the stream from the
one IR program. It reads ONE declared first-match table of rows `(form, admission conjuncts,
exit)` (§3). The floor row (choice/backtracking) always admits. In a backtracking region the
planner recurses: sub-stretches take deterministic rows where they can (C's `(.+)=(\d+);\1`).
Price chooses only among rows that ADMIT; it never decides soundness (all three).

**Pick 3, maximality as the default, departures priced (T's rule with P's pricing).** A region
takes the largest enclosing node that admits a deterministic row; a capture-free regular pattern
therefore compiles to today's one whole-pattern DFA by construction, not by a priced fuse. Any
split of a region that could be one segment (to put a SET inside, say) is a departure that must
carry a measured price (L4: Spencer's engine is what cutting everywhere costs). Gate: every
pattern today's selector routes to the DFA yields an all-automaton/kit stream, byte-identical.

**Open choice A, captures inside a segment.** C: `AUTO TAGGED` via [ENG-TDFA]; P: only
`ONEPASS` (TDFA is POSIX or leftmost-greedy); T: derived offsets only. Keep open. Its population
is the census in §7 M4; P's objection to TDFA must be checked against the [ENG-TDFA] row's own
design (a D3 priority machine with tags fixed per state is not the POSIX TDFA P cites).

**Open choice B, the ambiguous regular stretch with captures** (`(a|aa)+ab`, `(a|ab)(c|bcd)`
without a choice frame). C: `THREADS` (Pike list, O(n·m), no give-up); T: `GUIDED` (reverse
viability pass from a known end, then a frame-free priority walk; RE2/.NET's third phase,
placed per region); P: `MEMO` (failure memo, linear where E6 holds). Hold all three under D77.
Leaning: GUIDED first IF the census finds a population, because it reuses machinery that exists
(D3's exact end, the reverse DFA) and needs only a viability bitmap; THREADS and MEMO are new
engines in all but name.

**The kit.** Unchanged in principle (D146/D157: facts in, the kit's method). What changes is the
site vocabulary: one `SKIP` replaces EDGE, STAY fwd/rev, VMSPAN and VMSTRIDE; the
engine-context site kinds `MF_SK_DFA_HAT`/`HYB_PF`/`VM_ATTEMPT`/`DFA_ATTEMPT`/`DFA_SCAN`
(`emit_dfa.c:1417-1425`) are deleted, because a site's facts come from its seam. A kit byte move
is a pcrec abi event (D146), so this lands as its own step.

**The picture to hold.** Finder → bounder → finisher (P's L1) is every engine's shape; today
pcrec draws those seams per PATTERN and per ENGINE. The stream draws them per STRETCH, with one
seam type and one admission table, and lets the parts that cannot be deterministic stay
backtracking without dragging the rest of the pattern with them. Nobody in P's survey splits per
component AND keeps PCRE backtracking semantics; the rule that makes it safe is auto-possessify,
which pcrec already has.

---

## 3. Soundness: one admission table

Setting (all three, AGREE): stretch S entered at p, continuation K (through enclosing loops, to
ACCEPT). Backtracking yields S's outcomes (e₁,σ₁), (e₂,σ₂), ... in preference order; the answer is
the first from which K succeeds. A form F may replace S iff it delivers that same first outcome
for every entry and leaves the frames below untouched. Each row is a sufficient, checkable
condition. First match; the last row always admits.

| # | stretch kind (admission) | why backtracking into it cannot change the answer | precedent | drafts | status |
|---|---|---|---|---|---|
| G | **gate**: any machine for a NECESSARY condition (backref → referent, lookaround/non-consuming callout → ε) | it only removes positions that cannot match; it commits nothing | RE2/Rust prefilters, Spencer per-node DFA, Hyperscan switches, today's hybrid prefilter | C (FIND), T (R4 BOUND), P (G) | AGREE |
| 1 | **disjoint single-class repeat**: `C{m,n}` and `first(K) ∩ C = ∅` | a shorter run leaves a byte of C next, which K cannot start with | PCRE2 auto-possess, .NET auto-atomicity, pcrec possessify | C (D), T (R1b), P (E1a) | AGREE; mature (possessify) |
| 2 | **unique end**: fixed width, or a first-byte-disjoint alternation | there is only one outcome | .NET first-char switch; one-pass DFA | C (D, SWITCH), T (R1d), P (E1b) | AGREE |
| 3 | **tail / infallible K**: K is ACCEPT, or K succeeds from every end S can reach | the first outcome is the answer; D3's pruned machine computes exactly e₁ | D3 (why the DFA engine is exact at all) | C (T-rule, row 3), T (R1a), P (E1c) | AGREE |
| 4 | **source atomic / possessive** with a regular body | only w₁ is ever used, by definition | the language | C (D, atomic context), T (R1c) | 2/3; P keeps it a V `COMMIT` |
| 5 | **landmark reverse walk** with the class excluding every landmark byte | no start before one landmark pairs with a later one; FIND's ascending order is the order of starts | D161 add. 17 / lmwalk admission table | AGREE | AGREE; the table exists |
| 6 | **walk under a slot-reading K** (backref): the walk yields the EARLIEST candidate, a window of starts | the typing rule degrades `AT` to `LOWER/UPPER`; each start is still tried in order | Rust reverse-suffix + `min_match_start` guard | T (typing), P (exact=NONE + floor), C (per-start FIND) | AGREE on outcome; P's floor bound unproven (§6 #7) |
| 7 | **locate then pinned finish**: the capture-erased pattern has the same leftmost-first [s,e] | the finisher is handed `SPAN`; with an END pin, outcomes that cannot reach e are dead (MRL) | RE2/Rust/.NET 3-phase; today's hybrid "exact" | C (D END pin), T (R4 + R3), P (E3) | AGREE; P flags E3's proof burden |
| 8 | **monotone ends**: one greedy (lazy) quantifier over a deterministic fixed-stride body; ends descending (ascending), slots a function of the end | ENUM yields the same sequence; equal ends with equal slots are one continuation | APPROACH §2 A-1; today's cursor rung | C (O), T (R2a), P (E4) | AGREE; `(?:aa|a)*` is NOT admitted |
| 9 | **branch-ordered alternation**: deterministic branches, one end each, enumerated in branch order | ENUM is the preference order | today's ENG-ISL trie | T (R2b), C (LIST covers `a|ab`) | 2/3 |
| 10 | **captures at a seam** | a SET of a seam position is a pure store; it changes no outcome | TDFA tag ops on transitions as the model | AGREE | AGREE |
| 11 | **captures inside, one-pass** | at most one live thread per position, so tags are determinate | RE2/Rust/Go one-pass DFA | P (E2 ONEPASS), C (TAGGED), T (H1, open) | DIFFER: open choice A |
| 12 | **captureless regular lookaround**: a pure function of (subject, pos) | a predicate is atomic; folding it as context or a guard is the same test | re2c trailing context, RE# [VVE25], [BP24] oracle; D164 END_MARK | P (E5, at an EDGE), T (GUARD in a one-pass region), C (`ASSERT`/`AUTO EXISTS`) | AGREE on the predicate; DIFFER on placement; mid-segment unverified (§6 #5) |
| 13 | **non-consuming callout**: ε to the analysis | skipping a fire on a path that fails whatever the callee returns cannot change a pure callee's answer (§11.6) | PCRE2's start-up optimizations skip callouts | AGREE | AGREE; a consuming callout is a barrier |
| 14 | **thread set**: S·K regular to ACCEPT or an atomic boundary, captures allowed | a priority-ordered thread list IS leftmost-first with captures | RE2, Rust PikeVM; [Mos23+] | ONLY-C | UNVERIFIED for PCRE's empty-iteration rule; excludes callouts (C hole 6) |
| 15 | **guided**: S·K regular, K reads no slot, a `SPAN(s,e)` in hand | the first success is the lexicographically-first accepting path, whose end is e; the guided walk computes the lex-first path ending at e | .NET NonBacktracking / RE2 capture phase, per region | ONLY-T | UNVERIFIED: needs the argument written for lazy quantifiers, the empty-iteration rule and atomic groups inside S |
| 15′ | **guided pruning under an irregular K**: viability over a regular superset K′ ⊇ K | a non-viable branch cannot succeed; viable ones keep their frames | a per-branch gate (row G) | ONLY-T | sound by row G; cost unmeasured |
| 16 | **memo**: K's success depends only on (point, pos): no reachable backref to a group rewritten between arrivals, no callout reading slots | a failed (point, pos) fails again | RE2 BitState, [DSL21], [FH24] | ONLY-P | UNVERIFIED (P H6); answering where PCRE2 hits its limit needs a D26 ruling |
| 17 | **backref gate by referent copy** | the backref's language is a subset of its referent's | Spencer's engine [PGregex] | ONLY-P | **UNVERIFIED, and NOT as stated**: see below |
| B | **backtracking**: anything | it IS the semantics | today's VM | AGREE | always admits |

**Row 17 checked.** Today's listing for `(\w+)\s+\1` says `prefilter no-backreference: the erased
approximation is neither a sound superset nor the true span (S7); no flag changes this`
(`runs/`, main). That decline is about today's prefilter WINDOW protocol (it hands a start and
an end), not about a start-only gate; a G row that hands only `CAND` is a different, weaker
object. The referent copy as stated also fails on `(a)(?i)\1` (listed the same way today): the
backref matches `A`, which the referent's language `{a}` does not contain. The copy must take the
backref's own caselessness, and under `PCRE2_MATCH_UNSET_BACKREF` must include ε. Duplicate
names and `(?|` remain unchecked. Ask a pcre2-reader note before relying on it.

**Forced to B (AGREE):** a backreference or `(?(n)` condition reading a group set inside an
ambiguous S; recursion/subroutine with an ambiguous body; a non-atomic lookaround; a consuming
callout. Everything else is a cost question.

---
## 4. Benefit case

Grades: **STRONG** = mechanism certain and measurable now, not reachable as cheaply another way.
**MEDIUM** = real, but today's design grown reaches most of it with per-feature work, or the
population is unknown. **WEAK** = plausible, unmeasured, or mostly "tidier". Each row carries the
bird-in-the-hand test, applied both ways.

### 4.1 Reach: which pattern classes leave the all-VM path. MEDIUM

| class | today (checked on main) | stream | could today get it without the stream? |
|---|---|---|---|
| capture patterns with `resume-points 0` (pattern 3, 7 with a capture) | VM "forced by: capture group"; `(\w+)@(\w+)\.com` runs `prefilter yes ... the VM never scans`, `resume-points 0` | kit + automaton + SETs, no choice frame | partly: [ENG-TDFA] or a ONEPASS engine for whole patterns; locate×finish with a VM finisher behind the walk |
| backreference patterns | `(\w+)\s+\1`: `prefilter no-backreference`, `prune-ceiling subject-end` | FIND + SKIP + BREF, no frame (C, T, P agree) | yes, as one more per-feature start gate; today has no start-only gate protocol (the decline is the window's), so it would be a new row |
| callout patterns | VM, `no-callout` ("no prefilter yet") | FIND across a non-consuming callout | yes, per feature (purity contract, §11.6) |
| trailing / edge lookaround | `foo(?=bar)` routes VM (`(?=...) at pattern offset 3`); `(?<!x)baz` alone routes DFA (context view) | an all-automaton stream (rows 12, 3) | **yes**: D164 END_MARK is decided for exactly this; not a stream claim |
| a regular region AFTER an irregular node, below the top level | VM, plus islands one level deep; compound concat split only at top level, once | any depth (T B6, C B4b) | **no**, structurally (§4.4) |

Measurement: §7 M1-M3, compile-only. Grade MEDIUM because every row but the last is buildable in
today's design as its own special case; the stream's claim there is "one rule (G + effects +
the typing rule) instead of one prefilter row per feature", which is the simplicity benefit
again, not reach.

### 4.2 Speed: one pass instead of three for choice-free capture patterns. MEDIUM (STRONG mechanism, unknown population)

- **What (AGREE).** `(\w+)@(\w+)\.com` today: a capture-erased forward DFA (end), a reverse DFA
  (start), then a frameless VM re-walk of the window: the match is read three times. Stream:
  FIND `@`, SKIP back `\w`, SET, SKIP `\w`, SET, VERIFY `.com`. One read.
- **Bird test, today's direction.** Locate×finish grown (the landmark walk with a VM finisher, its
  row `finisher-dfa` lifted) gets to two reads: walk back, then a VM pass. P's sharp point: making
  the finish ONE deterministic pass fused with the walk is "the stream's B1 rebuilt as one
  special row". So today CAN get it, as a row; the stream gets it as the default for every
  choice-free capture program.
- **Bird test, the stream's direction.** The gain is per MATCH. On long subjects with rare
  matches, FIND dominates both designs and B1 is near zero (C, P; captures_via_dfa_survey.md
  §3.3 reached the same for one-pass).
- **Lead, not a measurement:** P cites 17 of 26 capture-forced capability patterns on the exact
  hybrid (captures_via_dfa_survey.md §0).
- **Measure:** §7 M1 (population), then T1 (timing, match-dense, both kit layers).
- A second speed claim, R3 GUIDED removing the `frames-unbounded` stamped subject ceiling (1024
  bytes on `(a+)+b`, T): **WEAK** until §7 M6 counts the population; the exact window already
  defuses the catastrophe on the pattern itself.

### 4.3 Simplicity: the parallel mechanisms deleted. STRONG over time, ZERO at first

The T inventory (`today/approach.md` §0.1) is the evidence. Each site is a pair (or more) of
kinds joined by its own protocol:

| T site | today | in the stream |
|---|---|---|
| X1 hybrid prefilter pair, emitted by the DFA emitter under a private name, `emit_vm.c:13005-13033`, H3 `10366-10441` | its own window protocol + three exactness conjuncts | `AUTO` (GATE or locate) ahead of a choice region; exactness by the typing rule |
| X2 VM span-loop cursor rung (`vm_cursor_rep` 4890, VMSPAN/VMSTRIDE) | its own analysis `vm_det_seq`/`vm_cursor_fits` | `AUTO ENUM` over a one-state machine with SKIP (row 8) |
| X3 VM revdet (`revdet.c`, `vm_revdet_rep` 5705) | its own reverse walk over a reversed AST | the one reverse `AUTO` kind, seeded at an iteration boundary |
| X4 VM alternation island ENG-ISL (`vm_isl_*` 4298-4745) | a second trie, own size rules | `AUTO ENUM` (row 9); with a capture, the DFA's own trie + seam SETs (P) |
| X5 VM literal-run `DELEG_VMRUN` | its own site | `VERIFY`, or nothing where the proof covers it |
| X6 VM backref compare `DELEG_N7` | site via the DFA emitter | `MISMATCH` |
| X7 DFA scan edges (`scanedge.c`, `DELEG_EDGE`) | its own analysis on the DFA graph | `SKIP` |
| X8 DFA stay/skip fwd+rev (`DELEG_STAY`) | a third skip site | `SKIP` |
| X9 start search NEXT rows, plus the VM's own start seek | two start searches | the one `FIND` generator |
| X10 PRESENCE/FIRST handoff, VM reuses "the same text" | text reuse | `PRESENT` + a typed seam |
| X11 LOCATE→RECOVER→FINISH (`reverse-pass`, `rev-end`, `cover`, `end-minus-width`, `pinned`) | five emitters | admission rows of one reverse `AUTO` kind |
| X12 landmark walk (p1build `emit_landmark_walk`, raw `pcrec_sb_puts`, refuses a VM finisher) | hand-written loop over four machines | `FIND`, reverse `AUTO`, forward region; `lc_finisher` becomes a seam type |
| X13 compound controller (`compound.c`) | whole artifact over whole artifact | concat split and locate/finish fold into tilings; split and arch variants stay a controller |
| X14 kit site kind keyed by ENGINE (`MF_SK_*`) | the engine leaks into the kit's facts | deleted |

Deleted parallel mechanisms (de-duplicated across drafts): engine selection as a routing verdict
(`select_engine.c`'s `analyses[]` mask); four skip sites to one; five reverse-walk forms to one;
two tries; two start loops; five exactness arguments to one typing rule (T B2: the shipped H3
defects are what the five cost); "port this to the other engine" plan rows.

- **Bird test, honestly applied.** Several of these unify WITHOUT the stream: T's own P1 (one
  SKIP record in both emitters) and the typing rule as a shared function are both doable inside
  today's two engines. What the stream adds is that they stay unified by construction (a kind
  exists once) rather than by discipline. The DECISIONS do not vanish; they move into the
  planner's table (C). `emit_dfa.c`'s 16k lines are mostly decisions and reasons (T).
- **Measure:** §7 M7 (count kind × host cells, sites, builders, deny axes, before/after).

### 4.4 New capability: backtracking across a seam. MEDIUM (structural certainty, unmeasured population)

- **What.** A pattern can go deterministic → backtracking → deterministic → backref → deterministic
  with re-entry across every seam (`(\w+)=([^;]*);(?:\1|x)+`, C B4b). A guard or a callout can sit
  on a one-pass automaton region (T B6). An ENUM segment re-entered from a failure three seams
  later is one popped frame.
- **Bird test, today's direction: it CANNOT, structurally.** The engine is a per-pattern
  partition; islands are one level deep inside one VM; the compound's concat cut needs a unique
  end (D163 add. 3 records backtracking across the cut as "not addressed"); a DFA cannot call out
  mid-scan. All three drafts reach this independently.
- **Bird test, the stream's direction.** How many real patterns need it is unknown. Measure: §7
  M5. Until then this is MEDIUM, not STRONG.
- Also stream-only and weaker: every admissible tiling is a differential test (C B4c), MEDIUM,
  but see loss 1.

### 4.5 Not benefits (AGREE)

Patterns 1, 7, 10: the same machine. One renderer discipline: tidier, worth nothing alone. The
derived `RX_ENGINE` stamp: cosmetic. "Fewer abi events": the opposite during migration. Seam
proof reuse past the cut (T B7): already pursued in today's design as `[CAND-SPAN]` (c967685c9).

---

## 5. Losses

| # | loss | drafts | mitigation |
|---|---|---|---|
| 1 | **The two engines stop being each other's check.** Today `--engine=dfa` vs `--engine=vm` is a control that does not share a source with what it controls; every tiling of a stream shares the renderers, so a `SET` or `FIND` rendering bug is in all of them | ONLY-C | keep PC-3 (libpcre2) as the independent oracle; keep ONE reference tiling (pure backtrack) whose renderers are separate code. Partial: today's engines already share parse, IR and the kit |
| 2 | **Pure-DFA properties become derived, not structural.** No stack, no budget, O(1) streaming state, bounded work: today true because the artifact IS a DFA; in the stream, a stray choice instruction silently costs them | T (and P: a wrong fusion is a slowdown) | maximality as a hard rule; the properties stamped from the fold; a gate that every pattern today routes to the DFA yields an all-automaton stream, byte-identical |
| 3 | **Seam cost.** A cursor handoff and a boundary gcc cannot optimize across; `(?:\w+\s)*` with a capture on the inner word pays two SETs and a segment change per iteration where a DFA pays nothing | T, P (L4) | maximality; every split a priced departure; measure the seam (§7 T2) |
| 4 | **Give-up surfaces move with the tiling.** Where `PCREC_ERR_STEPS`/`FRAMES` can fire is caller-observable | C, T | a spec event (D80) per row; accepted |
| 5 | **Callout fire sets move between releases** when a cut moves | C, P | allowed (§11.6); document it; accepted |
| 6 | **One render vocabulary** must hold computed-goto DFA states, table DFAs (D13) and the VM's single-indirect-jump rule in one function | T | large `AUTO` renders as its own function (C); accepted |
| 7 | **Many small machines.** The subset cap and the gcc-time budget apply per segment and in total: a new budget to state | C, T, P | probably benign for gcc time (it penalizes big functions); code size needs the artifact-size log |

---
## 6. Holes, ranked (merged, de-duplicated; the critic round attacks these first)

1. **Captures inside segments, and inside repeats.** `(\w+\.)+com` puts a group in a loop: rule
   8 needs slots to be a function of the end; row 3's first way still needs per-iteration slots.
   Without TAGGED/ONEPASS the planner SPLITS at every capture, which fragments the stream and
   pays seams (loss 3). The three drafts give three answers (open choice A); P rejects TDFA, C
   relies on it, T has not designed it. This hole sizes B1 and B4.4 on real patterns.
   (C 1, T H1, P E2/no-TDFA.)
2. **The planner's choices are unmeasured.** Maximality is a rule, but the cost of a seam
   (register handoff, a lost gcc loop, code size) has no number, and recursion into backtracking
   regions puts seams INSIDE hot VM loops. Pricing placement is itself still under study
   (rulepilot), so every speed claim inherits that open question. (C 8, T H2, P H1.)
3. **Proof burden of the new admission rows.** Rows 1 and 5 are mature (possessify, lmwalk). Rows
   3-in-context, 7 under captures, 12, 14, 15, 16 are "obviously sound" in the way Rust's
   reverse-inner was before #1354. Each needs a written argument, a D27 spec-first author and a
   deny axis; an error is a silent wrong answer. (C 2, P H2, T implicit.)
4. **No agreement on the ambiguous-regular-with-captures mechanism** (THREADS / GUIDED / MEMO,
   open choice B). Each has an unverified edge: THREADS with callouts and the empty-iteration
   rule; GUIDED with lazy quantifiers, atomic groups inside S, and O(window × states) viability
   memory; MEMO with trailed captures and answering where PCRE2 errors (a D26 ruling).
5. **Lookaround that is not at a segment edge, or not in a one-pass region.** `a*(?=a)` puts the
   body in S's own follow set: the automaton must report the preferred end at which the context
   holds, which is tag territory. These stay seams (`ASSERT`/GATE), sound but costly. How big the
   population is once D164 takes trailing lookaheads is unknown. (T H3, P H4.)
6. **Proof invalidation must be complete.** A missing INVALIDATES on one instruction is a silent
   miscompile; "undeclared = may write everything" (D182 (c) ruling 1) must be the enforced
   default, and every kit window must declare. (C 5, P `effects`.)
7. **The start loop under non-exact walks** (row 6, pattern 5). Per-start runs over a walk window
   can go quadratic on runs of the walk class; T's `LOOP c over [s*, j)` and P's floor are the same
   shape. The floor's bound needs a proof. (P H3.)
8. **The backref gate (row 17) is not sound as stated**: `(a)(?i)\1` breaks the plain referent
   copy; unset groups under MATCH_UNSET_BACKREF, duplicate names and `(?|` are unchecked. Needs a
   pcre2-reader note. (P H5, extended here.)
9. **Budgets and give-ups move** (loss 4) and run into the `CG_FIXED` contract rows: a spec event
   per row. (C 7, T H5.)
10. **Generator state for ENUM inside loops**: per-frame accept positions, bounded by the window,
    charged by the meters; today's accept-list islands have the same problem in a narrower
    place. (C 4.)
11. **UTF-8 seams**: the VM steps code points, the DFA steps bytes; the seam must carry a
    character-boundary proof (lmwalk's `utf8-l0` is the only precursor); rule 1's disjointness
    must hold on code points. (T H7, P #10.)
12. **Recursion and subroutine calls**: segments inside shared callee bodies need seams across
    CALL/RETURN and the slot snapshot; not worked through by any draft. (T H8, C §2.2.)
13. **Stamps, listing, ABI**: `RX_ENGINE`, the `_DFA_*` iff rule, `RX_VM_PREFILTER`,
    `ir_listing.md`; every artifact moves. Ritual, not a blocker. (T H6, P H9.)

---

## 7. Measurements, cheapest first

Compile-only censuses need no timing window: they are `>50`-compile sweeps, so they go through
the box queue, but not a bench slot. Each reads fields today's `--emit-ir` and stamps already
print (`engine ... forced by`, `prefilter <reason>`, `resume-points`, `prune-ceiling`, rungs).

| # | measurement | turns which claim from argued to measured | cost |
|---|---|---|---|
| M0 | the 14-site and kind × host count, by grep over the tree (no compile) | §4.3, the baseline | trivial |
| M1 | census over the .rxt corpus + pcrec-bench's capability set: VM artifacts with `resume-points 0`, split by whether D161 add. 17 admits a landmark for the capture-erased prefix | §4.2's population; P3's go/no-go | small |
| M2 | the same census by `prefilter` reason (`no-backreference`, `no-callout`, lookaround/atomic `subject-end` ceiling) | §4.1's reach rows | small (same sweep as M1) |
| M3 | VM artifacts whose ONLY forcing reason is captures at seams, or a zero-width item in a one-pass region (after D164's trailing lookaheads) | §4.1, T B6 | small, but needs a seam classifier: a few lines over the existing facts |
| M4 | patterns with a capture INSIDE a repeat or inside a would-be segment | hole 1; open choice A | small |
| M5 | patterns with a regular region after their first irregular node below the top level, and patterns with more than one VM-forcing construct | §4.4 | medium (the planner dry run, M8) |
| M6 | VM artifacts with `resume-points > 0` whose body is regular apart from captures; with the `frames-unbounded` ceiling stamp | open choice B; GUIDED/THREADS/MEMO population | small |
| M7 | after P-a: deleted builders, rows, manifest lines, deny axes | §4.3 | trivial |
| M8 | the planner as a DRY RUN: the §3 table read-only over corpus + bench, printing the tiling per pattern (C P2) | M1-M6 in one tool; sizes hole 1 | medium; read-only, no emitted change |
| T1 | timing, B1's route vs today's hybrid on an email-shaped cell, match-dense and rare, find-all, both kit layers (D147) | §4.2 | a bench window |
| T2 | seam cost: one region split into two segments vs one, on a hot-loop cell | hole 2, loss 3 | a bench window |
| T3 | adversarial give-up counts on M6's population, with and without the chosen mechanism | §4.2's second claim, open choice B | a bench window |

---

## 8. Proofs, ordered (byte-identical first, then the first benefit)

1. **P-a (byte-identical, T P1):** one `SKIP(set, dir, stride)` record used by BOTH emitters
   (VMSPAN/VMSTRIDE at `emit_vm.c:4839`; EDGE/STAY at `emit_dfa.c:9187`, `9216`, `12571-12587`);
   movers 0; the first record in `emit_dfa.c`.
2. **P-b (byte-identical, P P1, T's pattern 1):** the DFA artifact's top level (`cover`,
   `reverse-pass`, scan edge, forward match, report) rendered from `FIND`/reverse `AUTO`/`AUTO`/
   `ACCEPT` records, stamps derived from the records; falsifies the approach if it needs
   kind-specific escape hatches.
3. **P-c (byte-identical, C P1 = P P2):** the VM hybrid's prologue (forward+reverse pair, window
   handoff, retry) as records with ONE seam record carrying `pos`/`proof`/`reentry`, then the
   existing VM body.
4. **P-d (byte-identical vs lane/p1build, T P2):** the landmark walk as a record sequence; its
   three `pcrec_ctx_fail` asserts become seam type checks; `lc_finisher` a statement about the
   hand. After p1build lands.
5. **P-e (no emitted change, C P2):** the planner dry run (M8), with the typing rule checked
   against today's five exactness sites on the same corpus.
6. **P-f (first benefit, C P3 = P P3):** for M1's population only, `FIND` landmark → reverse
   SKIP → the frameless VM program run ONCE from the walked start, no forward DFA pass; a
   test-only lever (pcrec-flag-follows-caller-effect: a wrongness-risk change); its measurement
   card in the same change; answer identity over the corpus; then T1.
7. **P-g (second benefit, if M1 is thin; T P3):** R1 COMMIT automaton islands inside the VM body
   for sub-regions possessify ALREADY proves atomic, with captures only at their boundaries
   (`(\w+(?:-\w+)*)@(\w+)`), behind the same kind of lever. P's own fallback (`foo(?=bar)` as
   DFA trailing context) is NOT a stream proof: D164 already decided it inside today's design.

**Timing note for the manager (ONLY-T, worth a ruling):** D182 stage (c) (lexer, helper
registry, FL/CEN) is being designed now for the VM body only. Designing it against the stream's
record set costs nothing extra today; doing it VM-only and redoing it later is the expensive path.
