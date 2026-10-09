# Search is LOCATE × FINISH — the model, the table, the family, and [OPT-REVEND] in it

**DESIGN NOTE, PROPOSED, nothing built.** Lane `locfin`, 2026-10-09, from main
`525dec33` (abi 71). Charter: `docs/dev/decisions.md` D156 (Frank, 2026-10-09):
*"look for the general rule to expand. We have dfa prefilter then vm now. This is
the same but the prefilter is reverse."* Nothing under `src/`, `cli/`, `lib/`,
`tests/` or `docs/spec/` changes. Evidence: `../../studies/locate_finish/` (own
CLAUDE.md; a compile-side census with three controls). A FULL D6 panel reviews
this note before any `src/` change (D156); every section ends with a
**where to attack** paragraph written for it.

Read before writing: D156; `where_to_start.md` §1.1-§1.4, §2-§3, §5;
`start_table.md` rev 2.1 (refactor A is complete on main: `cand_rows[]`, the
slots, `cand_nodes[]` with the typed handoffs E1-E12, `cand_rows_selfcheck`) and
the shipped code at this pin (`src/gen/emit_dfa.c` `cand_rows` `:8160`,
`cand_nodes` `:8053`, `cand_select` `:8447`, `cand_read` `:323`, `dfa_matches`
`:7706`, `pcrec_emit_dfa_engine` `:11212`; `src/gen/emit_vm.c`'s hybrid entry
`:12703-12733`, `:13146-13426`); `revend.md` revision 2 (§R2, §0 first);
`../dev/reviews/2026-10-09-r-revend-panel.md` (X1-X13); `engine_m4.md` §6.1;
`litscan_k82h.md` (§1.1a, §1.2, the rulings); `offset_k_skip.md`;
`hyb_reseed.md` §4; `pf_know.md` §0-§3.

---

## 0. Answers first

1. **The model (§1).** A LOCATOR is a DFA walk named by its seed(s), its
   direction, the slice of the pattern its machine covers and that machine's
   LANGUAGE (exact, or a superset by erasure). It hands a TYPED result from a
   closed set of six: `SPAN` (start and priority end), `ENDSET` (start exact, end
   one of a known small set, priority undecided), `CAND` (a start worth one
   anchored try; nothing starts below it), `LOWER` (nothing starts below it),
   `UPPER` (nothing starts above it; with `LOWER` this is D156's "window"), and
   `NOMATCH`. A locator over a SUPERSET language can hand at most `CAND`
   (type degradation, §1.2). A FINISHER computes what the type leaves open, given
   the engine the pattern needs: return the span; one anchored forward DFA run;
   one anchored VM attempt with the span as ceiling; a VM search from a bound;
   or hand a `LOWER` to another locator. Every (type × finisher) pair carries a
   written set of exactness obligations O1-O10 (§1.4), and the give-up posture is
   DERIVED from the pair, not declared per row (§1.5).
2. **The table (§2).** Two new slots of the ONE `cand_rows[]` (D151 add. 3 Q2):
   `LOCATE`, first, asked by every DFA-shaped body and by the VM-only entry; and
   `FINISH`, last, walked once per type its locator can hand, keyed by (type,
   route). FINISH is the "separate first-match table" D156 asks for, as a slot
   block, which is what every start "table" already is. Today's eight slots are
   the INSIDE of the shipped forward+reverse locator and stay as they are.
   `revend.md`'s E13 (WINDOW → CALLER) is withdrawn: REVEND becomes a LOCATE row
   and its edge is the generic LOCATE → FINISH. Two of its four predicate
   conjuncts dissolve into table structure (R2 into the route mask, R4 into
   row order), and the third, R3, turns out to be exactly stage 2's switch.
3. **The family (§3).** Every shipped start mechanism casts as (seed, direction,
   language) → one of the six types; the census puts every compiled artifact in
   exactly one of eleven (locator, finisher) pairs (bench 343, corpus 5,012).
   FINISH already has SEVEN shipped members spread over `fit.chosen` tests (32
   code lines, §3.3), the VM entry's `prefn` arms and `dfa_matches[]` (which is
   REVEND's tie table, rows T2/T3, already written). The ≥3 rule fires; §2.3
   proposes the unified table. **No shipped mechanism falls outside the six
   types, so D156's revisit trigger does not fire**, with one wording amendment:
   D156's list omits `CAND`, which every NEXT row and the VM hat hand today and
   which the finisher must tell apart from `LOWER` (one try then re-locate,
   versus an attempt loop).
4. **REVEND (§4).** `rev-end` is one LOCATE row (route `CR_DFA`, predicate
   `end_pin`, deny `-fno-rev-end`); its tie arms are FINISH rows (`anchored` =
   T2, `relocate` = T3), and whether a tie can arise at all (`nl_last`, T1) is a
   property of the row's hand set. **Stage 2 (captures) is the same row with the
   VM finisher, and its give-up posture is NEUTRAL, not `revend.md` §3.9's
   ONE_WAY**: on an exact hybrid the walk hands the VM the same (start, ceiling)
   on every call the shipped prefilter does (§4.3: a STRUCTURAL step plus
   `revend.md` §6.1's measured 0 / 1,393,750). It needs one more PRESENCE row (the
   VM entry's O(n) pre-check runs before the prefilter and would eat the win).
   **Census: stage 2 reaches 0 bench / 13 corpus artifacts (11 already
   W1-bounded), so it stays FILED (D77)**; stage 1 reaches the 12 bench patterns
   `revend.md` names and 121 distinct corpus. The backreference relaxed-reverse
   locator is sound as specified in §4.5 (it is NOT the erasure
   `select_engine.c:877` measured unsound), hands `LOWER`, is ONE_WAY, and
   reaches 7 distinct corpus / 0 bench: FILED. `rev-inner` is a LOCATE row
   (not a NEXT row as `start_table.md` §4.1 placed it): its verifier is the
   anchored finisher, not NEXT's.
5. **Build (§5).** L0, a no-mover adding the two slots and one derivation
   `cand_finish_of(cx)` that ten scattered tests read; L1 = `revend.md` S0+S1
   unchanged; L2 = REVEND stage 1 as a LOCATE row, the abi 71 → 72 event, with
   D-2's ruled `attempt-start` batched into it; L3 = stage 2, FILED; L4 relaxed
   reverse, FILED; L5 rev-inner, FILED (D151). New sabotage ids: L0 5, L2 17,
   L3 4.
6. **Questions (§7):** where FINISH lives, L0's size, the stamp rule (no new
   stamp: `RX_DFA_SCAN` already IS the locator's projection), stage 2's
   trigger, the posture derivation, and the relaxed locator's deny.

---

## 1. The model (D156 item (a))

### 1.1 LOCATE

A locator is a DFA walk with four parameters:

| parameter | values today and proposed |
|---|---|
| **seed** | `search_from` with every start state live (the unanchored forward scan); a candidate position (a NEXT row's hit, `hit − k`, the predecessor byte + 1); the END of a match (RECOVER); the subject end `n` and `n − 1` (REVEND); a landmark hit `j` (rev-inner) |
| **direction** | forward; reverse |
| **slice** | the whole pattern; the prefix `P` of `P·L·S` (rev-inner) |
| **language** | EXACT (the capture-erased pattern, D31: the same machine, `engine_m4.md` §6.1) or a SUPERSET (lookaround → ε, atomic transparent, count collapse, and §4.5's backreference relaxation; `pf_know.md` §0: `L(P) ⊆ L(erase(P))` for every erasure `src/ir/nfa.c` performs) |

A locator may be a COMPOSITE: the shipped forward+reverse locator is the chain
WINDOW → PRESENCE → FIRST → NEXT → (the forward machine) → RECOVER, every link
of which already hands one of the types below (`start_table.md` §1.6). That
chain stays as it is; this note names its OUTPUT.

### 1.2 The typed results

Six types, each with the obligation the handing locator owes (`lo` is the
locator's accepted lower bound, `search_from` or a raised one):

| type | bit | meaning | the locator's obligation |
|---|---|---|---|
| `SPAN` | `CT_START` (+ the END) | `[s, e)` is the leftmost-first match from `lo` | `s` is the smallest start ≥ `lo` of any match; `e` is the PRIORITY end at `s` (PCRE2's, not the longest) |
| `ENDSET` | `CT_ENDSET` (new) | `s` is the leftmost start; every match at `s` ends in `D`, `\|D\| ≤ 2` today | as `SPAN` for `s`; `D` holds every possible end at `s`; priority among `D` NOT claimed |
| `CAND` | `CT_CAND` | a match MAY start at `s` | no match starts in `[lo, s)`; `s ≥ lo` (start_table S-N1(d)) |
| `LOWER` | `CT_LOWER` | no match starts below `s` | no match starts in `[lo, s)` |
| `UPPER` | `CT_UPPER` | no match starts above `t` | every match start ≤ `t` |
| `NOMATCH` | `CT_VERDICT` | no match from `lo` | NOMATCH only where none exists |

`LOWER` ∧ `UPPER` is D156's "window" (start ∈ `[s, t]`); today BOUND hands the
`UPPER` half to the loop header separately (E9), and no shipped locator hands
both at once (filed: `[OPT-VMSEED]` stage 4's seed window would).

**Type degradation (the rule that makes "inexact" a type, not a flag).** A
locator whose machine accepts a SUPERSET `L' ⊇ L` hands at most `CAND`: the
leftmost `L'` start is ≤ the leftmost `L` start (every `L` match is an `L'`
match with the same span), so "nothing starts below `s`" holds, but an `L`
match at `s` is not proved, and the `L'` end is no bound on the `L` end
(`atomic_groups_design.md`'s 122 refuting cells; the `mrl_win` gate,
`emit_vm.c:3643`). `pf_know.md` §0 measured the same split: the START is a sound
lower bound on every hybrid, the span exact only under `Vm.mrl_win`.

**HIT and START are not locator outputs.** `CT_HIT` is the PRESENCE gate's
leftmost landmark, handed to FIRST inside the composite (E3); `CT_START` is the
bit `SPAN` is carried in. Neither leaves a locator, so neither is a seventh type.

### 1.3 FINISH

A finisher consumes one type and returns the answer, or hands a `LOWER` to a
locator. The engine the PATTERN needs (D156's "capture need": the VM is needed
for captures or a VM-only construct, i.e. `fit.chosen == ENGM_VM`) selects which
finishers exist; the TYPE selects among them.

| finisher | consumes | what it does | engine | shipped today as |
|---|---|---|---|---|
| **report** | `SPAN` | returns `(s, e)` | none | every DFA artifact's return (E10) |
| **nomatch** | `NOMATCH` | returns 0 | none | PRESENCE/WIDTH verdicts, the empty engine |
| **anchored** | `ENDSET`, `CAND` | runs the anchored forward machine from `s`; the end is `s` + its length; on `CAND`, failure re-enters the locator | DFA | ENG_ATTEMPT's per-candidate run; the `unwrapped` match-here entry (`dfa_matches[0]`) |
| **relocate** | `ENDSET`, `LOWER` | raises `lo` to `s` and runs the NEXT locator (the composite) | DFA | the `search-filter` match-here entry (`dfa_matches[1]`); REVEND T3 (proposed) |
| **vm-window** | `SPAN` | one anchored VM attempt at `s`, `e` as the MRL ceiling where the artifact clamps | VM | the exact hybrid (E6 under `mrl_win`) |
| **vm-search** | `CAND`, `LOWER`, `ENDSET` (unclamped) | VM attempts from `s`; on a failure the RETRY slot steps or re-locates | VM | the inexact hybrid (E6+E7), the VM hat (E8), the VM-only loop |

The anchored DFA run and the VM over the span are D156's finishers 2 and 3;
`vm-search` is D156's "VM search from a lower bound"; `relocate` is the one D156
does not name, and the shipped tree already has it twice (the K82 handoff's
`LOWER` feeding NEXT inside the composite, and `search-filter`).

### 1.4 The exactness obligations, per pair

D156 asks for the obligation each (locator type × finisher) pair carries. Ten
obligations, then the matrix.

- **O1 leftmost-first start.** The `s` a locator hands is the smallest start ≥
  `lo` of any match of ITS language; it is the answer's start iff that language
  is `L` (§1.2). PCRE2 takes the smallest start with any match; priority acts
  only among ends at that start (`revend.md` §3.1, panel-upheld).
- **O2 end priority.** An end handed in `SPAN` is the priority end. A locator
  that cannot see priority (a reverse walk) hands `ENDSET` whenever more than one
  end is possible, and the finisher that resolves it must see priority: the
  anchored DFA machine (built priority-aware, K17/K18 fixed), the composite's
  forward pass (`relocate`), or the VM.
- **O3 captures equal PCRE2's.** Only a VM finisher writes groups ≥ 1; it does
  so from its own anchored attempt, never from a locator's positions (D44.6:
  `fit.chosen == ENGM_DFA` implies `NCAPS 1`; the DFA finisher's dead-group fill
  `emit_dfa.c:1650` is the one exception and it is a FINISH read, §3.3).
- **O4 give-up surface (D148 Q6 / K65 / K82 Q10).** The VM finisher's sequence of
  (attempt start, ceiling) must EQUAL the deny arm's (posture NEUTRAL) or be a
  SUBSEQUENCE of it in the same order with no ceiling looser (ONE_WAY: a give-up
  may become an answer, never the reverse). Anything else is forbidden. A looser
  ceiling is the trap: the MRL prune cuts less, steps rise, and an answer can
  turn into `PCREC_ERR_STEPS` (§4.3).
- **O5 `search_from` and find-all.** A locator accepts no start below `lo` and
  READS `subject[lo − 1]` for left context (the N1 defect,
  `assertions_design.md` §3.8.3.1; `where_to_start.md` §2.5's `lo0`/`slice`
  mutations). Find-all re-enters at E1 with the returned end; the empty-match
  advance is the caller's (`match_api.md` §3.1).
- **O6 utf8 boundaries.** Every `s` a locator hands, and every re-entry `LOWER`,
  is a character start; the position-domain layer (K49 advance, K50 guard, K73
  offset-0 rule, K75 alignment, `start_table.md` §2.5) applies to it unchanged.
  A reverse walk over a byte machine satisfies this by accepting only after whole
  characters (`revend.md` §3.6).
- **O7 views and `\G`/`\K` at the span edge.** Left context at `s − 1` and right
  context at `e` are read from the real subject by locator and finisher alike;
  `\G` reads `search_from`, never `s` (`litscan_k82h.md` Claim 2′); a `\K`
  pattern's REPORTED start is the VM's, not the locator's `s` (`\K` is VM-forced,
  `emit_dfa.c:7831`; the hybrid hands the attempt start, which is what the
  stage-2 members `a\Kb\z` etc. need).
- **O8 seeded walks.** Every SPECULATIVE seed (one nothing proved a match ends or
  starts at: REVEND's `n`/`n − 1`, rev-inner's landmark hits) may be DEAD and is
  tested before the first view lookup (X1). Seeds must be sound for the walk's
  OWN language: under an erasure, every `L'` match must end at a seed
  (end_pin(P) ⇒ end_pin(erase(P)), §4.4).
- **O9 progress.** Every re-entry edge strictly advances (`start_table.md` §1.6's
  per-row PROGRESS obligation): E5, E7, E8, E10, E11, E12 and the two new ones,
  `anchored`-on-`CAND` failure (the K49 advance) and `relocate` (into a different
  locator, which itself advances).
- **O10 cost (not soundness).** A locator must not cost more than the deny arm's
  locator on any subject, up to a constant. For REVEND: the walk's depth from `n`
  is ≤ `n − lo`, the forward scan's length.

| locator type ↓ / finisher → | report | anchored | relocate | vm-window | vm-search |
|---|---|---|---|---|---|
| `SPAN` | O1 O2 O5 O6 O7 | — | — | O1-O7; window = the deny arm's (O4 NEUTRAL) | — |
| `ENDSET` | — | O1 O2 O5-O8 | O1 O5-O9 | — | unclamped only: O1 O3-O8 (the ceiling is unread) |
| `CAND` | — | O1 O5-O9 (fail ⇒ re-enter) | — | — | O1 O3-O9, ONE_WAY (O4) |
| `LOWER` | — | — | O5 O6 O9 | — | O3-O7, ONE_WAY (O4) |
| `NOMATCH` | (nomatch) | — | — | — | — |

A dash is a pair the FINISH table never forms (§2.3's rows are total over the
types each route's locators hand). O8 binds every pair whose locator seeds
speculatively, which today is none and after L2 is `rev-end`.

### 1.5 The give-up posture is a property of the PAIR

`start_table.md` §1.5 made the posture a column every row fills by hand. Two
observations from this frame:

- **It is a function of the locator, its finisher and its deny arm, not of the
  row alone.** The same `rev-end` row is NEUTRAL with the DFA finisher (no VM
  runs), NEUTRAL with the VM finisher on an exact hybrid (window identity,
  §4.3), and would be ONE_WAY on a superset hybrid if its `CAND` differed from
  the deny arm's (it does not, §4.3). So posture belongs on the LOCATE row and is
  checked against O4, not declared.
- **One shipped cell is wrong by §1.5's own definition (finding F-1).** W1
  `window` (`emit_dfa.c:8163`) carries no `.giveup`, so it reads `CG_NEUTRAL`
  (K84's zero-value rule), but on `CAND_ROUTE_VM` its clamp skips VM attempts the
  `-fno-end-window` arm runs: a budget-limited call can answer where the deny
  arm gives up, which is ONE_WAY. No check reads the column (grep `giveup`:
  the field and seven initializers), so nothing failed. The PRESENCE rows on
  the VM route have the same shape (they skip every attempt when the landmark
  is absent) and §1.5 calls them NEUTRAL. The posture rule proposed here
  (O4, derived per pair) classifies both ONE_WAY; that is a doc/data correction,
  not an answer change, and it is L0's (§5).

**Where to attack §1.** (a) The type set: find a shipped or filed locator whose
output is not one of the six (D156's revisit trigger). (b) Type degradation: a
superset locator whose `s` is ABOVE the true start (it would need an `L` match
that is not an `L'` match). (c) O2: a reverse walk that hands `SPAN` where two
ends are possible (the `nl_last` derivation, §4.2). (d) O4's "subsequence with
no looser ceiling": is it sufficient for ONE_WAY under every meter (steps, work,
frames, trail, `_in` buffers — D148 Q-R3)? (e) F-1: is W1's VM-route posture
really ONE_WAY, and does any spec sentence promise otherwise?

---

## 2. Mapping onto the start table (D156 item (b))

### 2.1 What the eight slots are in this frame

They are the INSIDE of the shipped forward+reverse locator: WINDOW (`LOWER`),
PRESENCE (`NOMATCH` or pass), WIDTH (`NOMATCH`), FIRST (`LOWER`), NEXT (`CAND`),
RECOVER (`SPAN` from an end), BOUND (`UPPER`) and RETRY (the VM finisher's
re-entry). None moves. What the table lacks is (i) a place to choose BETWEEN
locators, which REVEND is the first to need, and (ii) the finisher choice, which
today is not a selection anywhere: it is a consequence of the route class, spelled
as `fit.chosen` tests (§3.3).

### 2.2 Two new slots, in the one array

**FINISH is a slot of `cand_rows[]`, not a separate array** (D151 addendum 3,
Q2, Frank: "otherwise logic is spread around"). D156's "separate first-match
FINISH table" is read as a separate SLOT BLOCK, which is how every former start
table already lives in `cand_rows[]`. **LOCATE is a slot too.** Both are walked
by `cand_select`; the selection DAG and the handoff graph read them like any
other slot.

| slot | the question | asked at | routes | accepts / hands |
|---|---|---|---|---|
| `LOCATE` (first) | which walk produces the result? | each DFA-shaped body, once (the entry body AND the hybrid's inlined `<p>_prefilter`, since both come through `pcrec_emit_dfa_engine`); the VM-only entry, once | `CR_DFA`, `CR_ATTEMPT`, `CR_VM` | accepts `LOWER` (E1); hands the row's declared type set to FINISH, or `LOWER` to WINDOW where the row is the composite |
| `FINISH` (last) | what computes what the result leaves open? | the caller-facing entry, once PER TYPE the artifact's locator can hand | `CR_DFA`, `CR_ATTEMPT` (DFA finishers), `CR_VM` (VM finishers) | accepts the six types; hands `START`/`VERDICT` to CALLER, `LOWER` to LOCATE (relocate), a failed `CAND` to RETRY |

`CandSel` gains one field, `hand` (the CT bit being finished), and FINISH's rows
declare which bits they `take`; the walk filters on `take & s->hand` exactly as it
filters on the route mask. That is the "(handoff type, capture need, route)" key:
the type is `hand`, the capture need is the route (a DFA route has DFA
finishers, `CR_VM` has VM finishers), and machine availability (an anchored
machine, a clamp) is a predicate.

### 2.3 The FINISH table, first match per (type, route)

| # | row | takes | routes | predicate | does | posture |
|---|---|---|---|---|---|---|
| F1 | `nomatch` | `VERDICT` | all | always | `return 0` | — |
| F2 | `report` | `SPAN` | DFA, ATTEMPT | always | return `(s, e)` | — |
| F3 | `anchored` | `ENDSET`, `CAND` | DFA, ATTEMPT | reads `dfa_matches[]`'s selection: `unwrapped` | `e = s + <p>_match(s)`; a `CAND` failure re-enters | — |
| F4 | `relocate` | `ENDSET`, `LOWER` | DFA, ATTEMPT | always | `search_from = s`; the composite locator | — |
| F5 | `vm-window` | `SPAN` | VM | always | one VM attempt at `s`, ceiling `e` (where clamped) | — |
| F6 | `vm-relocate` | `ENDSET` | VM | `v->nclamp > 0` | the inlined composite from `s`, then F5 | — |
| F7 | `vm-search` | `CAND`, `LOWER`, `ENDSET` | VM | always | VM attempts from `s`; RETRY on failure | — |

FINISH rows carry no posture and no deny: posture is the LOCATE row's (§1.5), and
every FINISH choice is already forced by an existing axis or is a consequence of
correctness — F3 vs F4 by `-fno-anchored-dfa` (`dfa_matches[]`'s deny, read, not
restated), F5 vs F7 by the locator's type (an exact or a superset machine,
itself forced by `-fprefilter-collapse` and the module mix), F6 by the clamp. So
FINISH adds no `--list-axes` axis and no deny bit (D46's forceability holds
through the existing ones). Totality: for every (route, type) that some LOCATE row
on that route can hand, the last FINISH row taking it is undeniable and
`cand_always` — F1, F2, F4, F5, F7 — the self-check's existing totality test
extended to the `hand` axis.

### 2.4 The LOCATE table

| # | row | routes | deny | predicate | hands | posture |
|---|---|---|---|---|---|---|
| A1 | `empty` | DFA, ATTEMPT | — | `dfa_engine_is_empty` | `NOMATCH` | NEUTRAL |
| A2 | `rev-end` (L2) | DFA | `PCREC_NO_REV_END` | `end_pin ≠ NONE` (∧ the stage-1 conjunct, §4.3) | `SPAN`, `NOMATCH`, `ENDSET` iff `nl_last` | NEUTRAL (§4.3) |
| — | `rev-inner[-bounded]` (filed, §4.6) | DFA, VM | its own | G1 ∧ G2 ∧ G3 | `CAND` | ONE_WAY |
| A3 | `fwd-rev` | DFA | — | always | the composite (`LOWER` to WINDOW; RECOVER hands `SPAN`, or `CAND` on a superset machine) | NEUTRAL |
| A4 | `cand-loop` | ATTEMPT | — | always | the composite with the ATTEMPT verifier fused (`CAND` → F3 per candidate) | NEUTRAL |
| — | `rev-end-relaxed` (filed, §4.5) | VM | its own | §4.5's gate | `LOWER`, `NOMATCH` | ONE_WAY |
| A5 | `trivial` | VM | — | always | `LOWER` = `search_from` (raised by W1, H1, the hat) | NEUTRAL |

**The route is NOT a projection of LOCATE.** The route (`cand_route_of`,
`job->engine`) says which MACHINES the compile built (ENG_UNANCH forward and
reverse, ENG_ATTEMPT forward, none); LOCATE says which WALK over them the search
uses. Today each route has exactly one walk (A3, A4, A5; A1 is a special case
on two), which is why no table was needed; `rev-end` is the first second walk on
a route.

### 2.5 What changes in the handoff graph

- `cand_nodes[RECOVER].succ`: CALLER → FINISH. `cand_nodes[PRESENCE/WIDTH].succ`
  keep CALLER for `VERDICT` (F1 is CALLER's spelling, kept as a node so the
  existing edges do not move).
- New edges: **E-LF** LOCATE → FINISH (typed by the LOCATE row's hand set);
  **E-FL** FINISH F4/F6 → LOCATE (relocate, `LOWER`; progress: the next locator
  in table order, which never re-selects the one that handed, O9); **E-FR**
  FINISH F7 → RETRY (the failed `CAND`; today's E7/E8, renamed, unchanged).
- **`revend.md`'s E13 (WINDOW → CALLER) is withdrawn**: REVEND's result travels
  E-LF to FINISH and FINISH's `report`/`anchored` to CALLER. `cand_nodes[WINDOW]`
  keeps its successor set; X2's `table-hands-unaccepted` question no longer arises
  because WINDOW keeps handing `LOWER` only.
- E6 (the hybrid's prefilter → the VM loop) becomes E-LF on an inlined body:
  LOCATE (A3/A2 on `CR_DFA`) → FINISH (F5/F6/F7 on `CR_VM`). It is the same edge
  as the DFA-only artifact's, with a different finisher; that sameness is D156's
  sentence "REVEND with captures is reverse-from-end × the same finisher".
- One declared type changes: the inlined body's RECOVER row hands `CAND`, not
  `START`, when the prefilter's language is a superset (`!Vm.mrl_win`). Today
  `cand_rows[]` declares `CT_START` on both RECOVER rows unconditionally, so the
  graph says "the reported match's start" on 621 corpus / 22 bench artifacts
  (§3.1 T1, `P-fwdrev × F-vm-cand`) where it is only a candidate (finding F-3;
  the VM's retry exists because of exactly this). L0 corrects the declaration
  (data, no byte).

### 2.6 Routes, X4, and the hybrid

X4 required the REVEND row to be route-independent because WINDOW is an ENTRY
slot whose choice must not depend on the asking route (`cand_hit_every`). As a
LOCATE row the question changes: LOCATE is a BODY slot, asked once per body on
that body's route, and `rev-end`'s route mask is `CR_DFA` because only an
ENG_UNANCH body has a reverse machine. Its predicate still reads no `s->route`
and no `fit.chosen` (bar the stage-1 conjunct), so **the inlined prefilter of a
hybrid ASKS LOCATE on `CR_DFA` exactly as a DFA-only body does**, and the row
admits it wherever its prefilter carries reverse tables (`RX_DFA_START
"reverse-pass"` with `RX_DFA_SCAN "unanchored"`; census T2: 39 bench / 1,192
corpus hybrids, control C1 0 disagreements). What decides whether the walk's
result reaches the caller or the VM is FINISH, on the entry's route.

**Where to attack §2.** (a) FINISH as a slot vs a separate array: does
`cand_select`'s first-match-per-(slot, route) extend cleanly to (slot, route,
hand), or is the `hand` filter a second walk in disguise? (b) LOCATE asked on the
inlined body: the hybrid's inlined `<p>_prefilter` is called from three places
(the entry, the RETRY recompute, the adaptive re-seed, `emit_vm.c:13261-13327`,
`:13396`); a walk there must give the same answer at every call (§4.3). (c) F-3:
is any reader of RECOVER's declared `hands` relying on `CT_START` on a superset
prefilter? (d) Totality over `hand`: a LOCATE row added later with a type no
FINISH row on its route takes (the self-check must fail, not abort at run time).
(e) Is the composite A3 really one row, given that the eight slots inside it are
asked at different emission points?

---

## 3. The family survey (D156 item (c))

### 3.1 Today's pairs, measured (`studies/locate_finish/results/summary.txt`)

Population: every bench export (367; 343 compile) and every `.rxt` pattern block
(5,431; 5,012 compile, 4,191 distinct), main `525dec33`, each compiled as its
own testee/block does. Three controls, each sharing no source with what it checks
(§6.2): C1 the reverse-machine stamp vs the emitted text (0 / 5,355 disagree),
C2 the hybrid stamp vs the text (0 / 5,355), C3 the borrowed end-pin probe vs the
shipped `end_window` fact (0 / 400).

| today's pair (T1) | bench | corpus (distinct) |
|---|---:|---:|
| `fwd-rev` × report | 233 | 2,192 (1,768) |
| `pinned` (RECOVER S1) × report | 15 | 231 (192) |
| `cand-loop` × anchored (ENG_ATTEMPT) | 20 | 308 (237) |
| `empty` × nomatch | 0 | 53 (47) |
| `trivial` × vm-search (VM-only) | 19 | 791 (668) |
| hybrid `fwd-rev` × vm-window (exact) | 17 | 571 (497) |
| hybrid `fwd-rev` × vm-search (superset) | 22 | 621 (585) |
| hybrid `cand-loop` × vm-window | 14 | 145 (115) |
| hybrid `cand-loop` × vm-search | 3 | 82 (66) |
| hybrid `empty` × vm-window / vm-search | 0 / 0 | 12 / 6 |
| hybrid `pinned` (either) | 0 | 0 |

Every compiled artifact is in exactly one row (the classifier is total by
construction, `census.py classify`). Two shipped finishers appear that D156's
list does not name explicitly: `anchored` on 20 bench / 308 corpus ENG_ATTEMPT
artifacts, and `vm-search` on `CAND` (the superset hybrids, 22 / 621).

### 3.2 Every shipped start mechanism as (seed, direction, language) → type

| mechanism | seed | dir. | language / slice | hands | a row today? | in this design |
|---|---|---|---|---|---|---|
| the forward+reverse pass (ENG_UNANCH) | `search_from`, all starts live | fwd, then rev from the end | exact, whole | `SPAN` | the route + RECOVER S2 | LOCATE A3 |
| `pinned` ([OPT-5]) | `search_from` | fwd | exact, whole | `SPAN` (start = `search_from`) | RECOVER S1 | inside A3 |
| ENG_ATTEMPT | each candidate ≤ `start_max` | fwd, anchored | exact, whole | `CAND`, finished per candidate | the route + N12/B1/B2 | LOCATE A4 (+F3 fused) |
| the empty engine | — | — | — | `NOMATCH` | `dfa_engine_is_empty` (inline) | LOCATE A1 |
| hybrid prefilter, exact | as A3/A4 | as A3/A4 | capture-erased = `L` | `SPAN` | route class HYB-* | A3/A4 × F5 |
| hybrid prefilter, superset (lookaround, atomic, count-collapsed) | as A3/A4 | as A3/A4 | `L' ⊋ L` | `CAND` (degraded) | route class + `mrl_win` | A3/A4 × F7 |
| K82 handoff | the gate's leftmost run hit `c` | arithmetic | — | `LOWER` = `max(lo, c − K)` | FIRST F1 | inside A3/A4 |
| offset-k / run-pinned | the rarest offset's hit | arithmetic | — | `CAND` = `hit − k` | NEXT N1-N4 | inside A3 |
| START-SET DFA hat | a byte in `S` | — | — | `CAND` + re-seed | NEXT N5/N6 | inside A3 |
| START-SET VM hat | a byte in `S` | — | — | `CAND` | NEXT N7 | inside A5 × F7 |
| memchr / byte-class | `s0`'s escape set | — | — | `CAND` | NEXT N8-N11 | inside A3 |
| pred-memchr (ATTEMPT) | the predecessor byte | — | — | `CAND` = hit + 1 | NEXT N12 | inside A4 |
| W1 end window | `n` | arithmetic | — | `LOWER` = `n − maxw − eps` | WINDOW W1 | inside A3/A4/A5 |
| H1 width ceiling | — | — | — | `NOMATCH` | WIDTH H1 | inside A5 |
| PRESENCE pre-checks, K65/K66 | the landmark scan | fwd | — | `NOMATCH` / pass (+`HIT`) | PRESENCE P1-P5 + payload | inside A3/A4/A5 |
| BOUND | — | — | — | `UPPER` | BOUND B1-B5 | inside A4/A5 |
| RECOVER reverse pass | the forward pass's end | rev | exact, whole | `SPAN` given the end | RECOVER S2 | inside A3 |
| RETRY | the failed attempt + K49 | — | — | `LOWER` (re-locate) or `CAND` (step) | RETRY R1-R6 | F7's re-entry |
| the match-here entry | the caller's start | fwd | exact, whole | `CAND` from the caller | `dfa_matches[]` (axis G) | FINISH F3 / F4 |
| [OPT-REVEND] (L2) | `n`, `n − 1` | rev | exact, whole | `SPAN`/`ENDSET`/`NOMATCH` | — | LOCATE A2 |
| rev-inner (filed) | landmark hits `j` | rev | exact, prefix `P` | `CAND` per `j` | — | LOCATE (§4.6) |
| relaxed reverse (filed) | `n`, `n − 1` | rev | `L' ⊇ L` (§4.5) | `LOWER` | — | LOCATE (§4.5) |

**Which are rows already:** everything inside A3/A4/A5 (37 rows, refactor A),
and `dfa_matches[]` (two rows of its own axis G table). **Which would become
rows:** the locator choice (A1, A3, A4, A5: today the body dispatch
`pcrec_emit_dfa_engine` `:11212` plus `dfa_engine_is_empty` readers) and the
finisher choice (F1-F7: today the ten `fit.chosen` reads of §3.3, the VM entry's
`prefn` arms and the ATTEMPT body's fused verify). **Which output is not a typed
result: none** (D156's trigger does not fire; §0 item 3's wording amendment
adds `CAND` to D156's list).

### 3.3 Where the FINISH decision is spelled today

`studies/locate_finish/finish_sites.sh` lists every CODE line under `src/gen/`
that tests `fit.chosen`, `fit.prefilter` or `prefn`: 32 lines. Dispositioned:

| class | lines | what they decide |
|---|---|---|
| **FINISH reads** (is this body's result returned to the caller, or handed to the VM?) | `emit_dfa.c:1650` (the dead-group fill: the DFA finisher writes groups ≥ 1), `:1728` (the startpos guard on the caller-facing body), `:3145` (`rx_info.match_form`: who wrote `_match`), `:9768`, `:9769`, `:9784` (`emit_unanchored`'s entry gate: req-run blocks, trace, W/P/F), `:10068`, `:10070`, `:10083` (`emit_attempt`'s), `:10707` (the orientation block) | 10 lines, 6 decisions, one question: "is the finisher a DFA finisher on this entry?" |
| route-class reads inside predicates (start_table §2.3 sound-n4's third axis: VM-only vs hybrid) | `:6847` (N7), `:7155`, `:7159` (P2), `:7360` (F1's (d′)) | stay (filed there; not FINISH) |
| "does a DFA body exist" | `:439` (`pcrec_artifact_has_dfa_scan`), `:10922` | LOCATE's existence (any row on `CR_DFA`/`CR_ATTEMPT`) |
| the VM finisher's locator calls and exactness | `emit_vm.c:3645` (`mrl_win`: the locator's type), `:11071`, `:11182`, `:11218` (stamps, RETRY plan), `:12703-12733` (emit the inlined locator), `:13261-13327` (RETRY's re-locate), `:13393-13404` (the entry's locate call, E6) | 16 lines that ARE the F5/F7 implementation |

So the finisher choice is one question asked at six decisions in two emitters,
and the hybrid-vs-DFA-only distinction is spelled ten times. L0 gives it one
derivation, `cand_finish_of(cx)` (the `cand_route_of` precedent, start_table
§2.3 item 3), read by all ten.

### 3.4 The ≥3 rule and the unified table

FINISH has seven shipped members (report, nomatch, anchored, relocate via
`search-filter`, vm-window, vm-search on `CAND`, vm-search on `LOWER`), all
dispersed. The house rule (memory `pcrec-forest-for-trees`) asks for the unified
table at three; §2.3 IS that table, and `dfa_matches[]` is its existing DFA half
(it already chooses `anchored` vs `relocate` for the match-here entry; FINISH
reads it rather than restating it, `start_table.md` §1.3's "slots read each other
only through the walk"). A small adjacent finding (F-2): `dfa_match_is_unwrapped`
(`emit_dfa.c:7727`) compares the selected row's POINTER to `&dfa_matches[0]`, the
shape `start_table.md` sound-m2 removed from RECOVER (`u.recover.pinned`); F3's
read should test a property field. L0 item.

**Where to attack §3.** (a) T1's classifier (`census.py classify`) decides
exactness from `RX_VM_PREFILTER_LANG` plus the `kinds` fact's `atomic` and
`lookaround` bits, mirroring `pcrec_vm_prefilter_window` (`emit_vm.c:3643`); a
hybrid with a fourth erasure would be misclassed. (b) The survey's claim that
every mechanism hands one of six types: K65/K66's payload and the K82 gate's
`HIT` are the candidates for a counterexample. (c) §3.3's dispositions are by
hand over a grep list; a FINISH read the grep pattern misses (a test of
`emitted_prefilter`, `v->cx->job->fit` spelled differently) would escape L0's edit
set. (d) Is `dfa_matches[]` really FINISH (the match-here entry has no locator),
or a second table L0 should leave alone?

---

## 4. REVEND in this frame (D156 item (d))

### 4.1 The locator row

```
{ .c = { "rev-end", PCREC_NO_REV_END, cand_rev_end_applies },
  .slot = CAND_SLOT_LOCATE, .routes = CR_DFA, .tok = "rev-end",
  .map = CM_EXACTREV, .hands = CT_START | CT_VERDICT | CT_ENDSET /* ENDSET iff nl_last */,
  .list = { [CAND_ROUTE_DFA] = { "locate", 1, "rev-end", PCREC_NO_REV_END } },
  .desc = "...end_pin...", .u.locate = { .walk = CAND_WALK_REV_END } }

static bool cand_rev_end_applies(const CandSel *s)
{
    if (pcrec_fact_end_pin(s->cx) == PCREC_EPIN_NONE) return false;  /* R1 */
    return s->cx->job->fit.chosen == ENGM_DFA;                        /* the stage-1 conjunct */
}
```

`revend.md` §2.3's four conjuncts, in this frame:

| `revend.md` | here | why |
|---|---|---|
| R1 `end_pin ≠ NONE` | the predicate | the one admission fact |
| R2 `cand_route_of == CAND_ROUTE_DFA` | the row's route mask `CR_DFA` | a reverse machine exists only on ENG_UNANCH; the walk filters routes before predicates |
| R4 `!dfa_engine_is_empty` (X11) | row order: `empty` (A1) precedes `rev-end` | `[^\x00-\xff]$` selects A1 and never reaches A2 |
| R3 `fit.chosen == ENGM_DFA` | the ONE remaining conjunct, and it is exactly stage 2's switch | removing it admits the hybrid's inlined body (§4.3) |
| X3's assertion (RECOVER never `pinned`) | kept, at the walk's emission | `end_pin ∧ pinned = ∅` is now MEASURED too: census T4, 0 / 5,012 |

The emitted walk is `revend.md` §5.1's text unchanged; the helper is §8's
(`emit_scan_loop`'s reverse arm parameterized; a seed may be DEAD, X1; it reports
which seed(s) reached the minimum).

### 4.2 The tie table is FINISH

`revend.md` §2.4's three rows map one-to-one:

| `revend.md` | here |
|---|---|
| T1 `no-tie` (`\z`, or `nl_last` false) | the row's HAND SET omits `ENDSET`, so FINISH is never walked for it and no tie code is emitted |
| T2 `anchored` (`DFA_MATCH "unwrapped"`) | FINISH F3, which reads `dfa_matches[]`'s selection |
| T3 `body` (`"search-filter"`) | FINISH F4 `relocate`: `search_from = s*`, the composite A3 |

`nl_last` stays as `revend.md` defines it (computed on the BUILT reverse machine
at emission: the seed state after the end view steps to dead on `'\n'`'s class).
It decides the hand set, so it is a LOCATE-row property and its sabotage row
(revend §9.2 row 10) is unchanged.

### 4.3 Stage 2: the same locator with the VM finisher

**What it is.** Drop the stage-1 conjunct. The hybrid's inlined `<p>_prefilter`
is emitted by `pcrec_emit_dfa_engine` (`emit_vm.c:12725`), so it asks LOCATE on
`CR_DFA` and selects `rev-end` exactly where a DFA-only body would; the VM entry
asks FINISH on `CR_VM` and gets F5 (`SPAN`), F6 (`ENDSET` on a clamped artifact)
or F7 (`ENDSET` unclamped, `CAND`). The reverse tables it needs are already in
every such artifact (census T2: the 39 bench / 1,192 corpus `P-fwdrev` hybrids
carry them; C1 confirms by text).

**Its posture is NEUTRAL, and this corrects `revend.md` §3.9.** The VM sees
`attempt_position = window[0][0]` and, where it clamps, `window_end =
window[0][1]` (`emit_vm.c:13396-13410`), at the entry and at every RETRY
re-locate (`:13261`, `:13329`). For an exact hybrid:
- *STRUCTURAL:* `<p>_prefilter` is the DFA emitter's output for the capture-erased
  pattern (`engine_m4.md` §6.1, D31), so today's window on every call is that
  pattern's DFA span from `lo`;
- *MEASURED:* the walk's span equals the DFA artifact's span on every call:
  `revend.md` §6.1, form C, 0 / 1,393,750 cells over 74 patterns at every
  `search_from` in `[0, n+1]`, ties included (T2 and, on `-fno-anchored-dfa`
  artifacts, T3);
- so the walk hands the VM the SAME `(start, ceiling)` sequence (O4 equality),
  PROVIDED a tie on a clamped hybrid goes to F6 (the composite's priority end)
  and not to F5 with `max(D)`: a ceiling of `n` where the priority end is `n − 1`
  prunes less, and a budget-limited call could then give up where today it
  answers (§1.4 O4's trap). Unclamped, the ceiling is unread and F7 is exact.

On a SUPERSET hybrid (1 corpus member, `\w{1,2}(?:(?=)|)$`) the walk's `s*` is the
leftmost `L'` start, which is what today's superset prefilter returns too, so the
`CAND` sequence is again equal; the residual obligation is O8's
end_pin(P) ⇒ end_pin(erase(P)), argued per erasure in §4.4.

**The one new mechanism it needs: PRESENCE must defer to the walk.** On the
hybrid the VM entry runs W1, then the PRESENCE pre-check, then FIRST, then calls
the prefilter (`emit_vm.c:13146`, `:13165`, `:13396`). A pre-check is an O(n)
`memchr` over the whole window, which is exactly X7's finding for the DFA-only
artifact (there the walk replaces the entry body, so PRESENCE is never asked).
On the hybrid PRESENCE IS asked, so it needs a row, first in the slot:
`locate-decides` (verdict NONE, hands pass), whose predicate READS LOCATE on the
inlined body through `cand_read` (a new selection-DAG edge PRESENCE → LOCATE) and
applies where the selected locator declares that it answers presence itself
(`.u.locate.whole = true` on `rev-end`). P3 `dominated` is the same shape ("the
scan already tests it"). FIRST's handoff then declines through its existing
PRESENCE read (F1 reads PRESENCE, `req_handoff_applies` `emit_dfa.c:7352`). W1 and H1 stay: both are
O(1) arithmetic and can only raise `lo`.

**Is it cheap enough to build with stage 1?** The mechanism is: delete one
conjunct, add one PRESENCE row and one DAG edge, give F6 its arm, and a
window-identity twin (`revend_twin/`'s `check.c` comparing `window[0]` from the
walk-rewritten and the shipped `<p>_prefilter`, every `lo`, plus the find-all).
That is small, and NOT building it is the special case (a conjunct that exists
only to keep a route-independent locator off one route). **But the census says
the population is 0 bench / 13 corpus** (T5: 12 exact, 1 superset; 11 of the 13
already width-bounded, where W1 at the VM entry already clamps; the 2 unbounded
are `(a\z)+` and `(a+)$`, both correctness witnesses). The 15 bench / 192
corpus end-pinned hybrids that do exist are ENG_ATTEMPT (`^...$` validators:
`cand-loop`, one attempt at 0, nothing to locate). **Leaning: keep it FILED**
with `revend.md`'s trigger (a captures-bearing end-pinned bench cell, e.g.
`(\d+)$`), and say so in L2's commit as the reason the stage-1 conjunct exists.
§7 Q3 asks Frank.

### 4.4 O8 for superset languages: does an erasure keep the end pin?

The walk seeds only at `n`/`n − 1`, which is sound for `L'` only if every `L'`
match ends there. `end_pin` is computed on the lowered AST (`endwin.c`'s
`ew_walk`); each erasure `src/ir/nfa.c` applies when it BUILDS the prefilter must
map a pinned tree to a pinned language:
- lookaround → ε: `ew_walk` returns no pin from a lookaround's interior (a
  trailing `(?=\z)` reads `none`, the probe's `look_tail` class), and `A_CAT`
  treats a zero-width factor as transparent, so the factor erased to ε
  contributed nothing to the pin (`\d+$(?=\n)` is pinned by its `$`);
- atomic → transparent: the body's view is the view;
- count collapse `X{m,n}` → `X{min(m,1),}`: `A_REP` pins only for `rmin ≥ 1`
  (revend sabotage row 4), and `min(m,1) ≥ 1` iff `m ≥ 1`;
- §4.5's backreference relaxation and a recursive call's Σ*: an `A_BREF` or
  `A_CALL` at the END of an alternative is not pinned by `ew_walk` in the first
  place (its width is subject-bounded, not a view).

This is an argument, not a measurement; the L3 build's window-identity twin is
the measurement (the walk vs the shipped superset prefilter over the same `L'`).

### 4.5 The backreference relaxed-reverse locator

**Where its reverse machine comes from.** A new erasure arm, used for the
REVERSE machine only: `A_BREF(N)` lowers to `relax(G_N)` = the referenced
group's sub-tree with its views and lookarounds erased to ε, atomicity
transparent, every class closed under the pattern's case fold where the
REFERENCE is caseless (`backrefs_design.md`: the caseless compare's fold is
exactly `cls_casefold`'s set in byte mode; 10.46 folds 1:1 per code point under
utf8, `utf8_design.md`), applied recursively to backreferences and calls inside
`G_N` while the reference graph is acyclic, and Σ* (any whole character, `[\s\S]*`
in the encoding's automaton) where it is cyclic (a reference inside its own group;
`subroutines_design.md` §8.3's construction for a recursive call is the same
rule). `src/ir/nfa.c`'s `A_BREF` arm keeps its internal error in every OTHER mode,
so `select_engine.c`'s `backref` prefilter decline (T2's row,
`select_engine.c:667`) is untouched: this machine is never a forward prefilter.

**Soundness of the relaxation: `L(P) ⊆ L(relax(P))`.** The bytes a
backreference matches are (a per-code-point case variant of) the bytes `G_N`
matched in its own context. That path through `G_N` is a path of `relax(G_N)`:
erasing a view to ε admits every path the view admitted, a transparent atomic
admits every path the atomic admitted, and the fold closure admits every case
variant. An unset group makes the backreference FAIL (PCRE2's default), which
removes strings, never adds them. A group in a loop is referenced at its last
iteration's capture, still a string `G_N` matched. **This is not the erasure
`select_engine.c:877-886` measured unsound**: that one replaced `\N` by a COPY of
`G_N` with its assertions KEPT, so `(\ba)\1` became `(\ba)\ba`, which matches
nothing on `"aa"` (12 / 18 false negatives, all from assertions or atomics in the
referenced group's closure). Erasing them in the copy is exactly the repair, and
the measured span error there (`(["'])[^"']*\1`: (0,2) vs (1,3)) is irrelevant to
a `LOWER` locator, which promises only a lower bound (type degradation, §1.2).
`where_to_start.md` §5.3 answered "superset DFA with `\N` relaxed" NO for the
PREFILTER role on that measurement; the answer here is for a different
construction and a different role (a lower bound, not a window).

**Type and finisher.** It hands `LOWER = s*'` (the leftmost `L'` start, ≤ the
true one) or `NOMATCH`, to F7 `vm-search`: the shipped VM-only attempt loop from
`s*'`, its START-SET hat and BOUND unchanged. Not `CAND` with a re-walk per
failed attempt: a reverse walk enumerates accepting positions from the RIGHT, so
the next candidate above a failed one costs another walk from `n` (O(n − lo) per
retry, quadratic over a dense `R`).

**The give-up surface: ONE_WAY.** Attempts below `s*'` are skipped (each fails:
`L ⊆ L'`), attempts from `s*'` on are the deny arm's in the same order (O4
subsequence), so a budget-limited call may answer where `-fno-…` gives up, never
the reverse: D148 Q6's sentence applies unchanged, not K82's Q10 posture (no
count-collapsed prefilter is involved).

**Cost (O10).** An end-pinned match must reach `n − 1` at least, so the VM's
successful attempt at the true start `s` consumes ≥ `n − 1 − s` bytes, and the
loop makes ≥ 1 step per failing start in `[lo, s)`; the walk reads ≤ `n − lo`
bytes. So the walk is bounded by the VM's own work, up to the per-byte cost
ratio. Where the relaxation contains Σ* the walk does not die and `s*'` is `lo`:
the walk is pure overhead (bounded, not free), so the gate excludes a cyclic
reference, which is when Σ* appears.

**Population (census T6):** 275 end-pinned VM-only corpus artifacts, 255 of them
start-anchored (one attempt; nothing to locate); start-unanchored 13 distinct, of
which 7 distinct carry a backreference and are unbounded, all corpus correctness
witnesses (`(?=(a|ab))\1$` in six spellings, `(?i)(\xe9)(?:x|\1)$`); bench 0.
**FILED (D77)**; trigger: a bench or real-world end-pinned backreference cell
that pays the VM's attempt loop.

### 4.6 `[ENG-TACTICS]` reverse-inner: the next locator, row shape only

- **Slot LOCATE, not NEXT** (correcting `start_table.md` §4.1's placement). A NEXT
  row hands `CAND` to NEXT's VERIFIER, the unanchored forward machine re-seeded,
  after which RECOVER walks back for the start. rev-inner already HAS the start
  (`s*(j)`) and needs the END and a verdict: its DFA hat is FINISH F3 (the
  anchored machine from `s*`), its VM hat F7 (one anchored attempt), and a failed
  verify re-enters the LOCATOR at the next occurrence. That is a locator with its
  own finisher pairing, not a candidate feeding the composite.
- **Row:** `rev-inner-bounded` then `rev-inner` (`views` first, the house
  order), routes `CR_DFA` and `CR_VM`, after `rev-end` and before `fwd-rev`/
  `trivial`; predicate G1 ∧ G2 ∧ G3 (`where_to_start.md` §2.4), each conjunct its
  own line and sabotage row from §2.6's mutation table; seed = each landmark hit
  `j` (FIND resuming at `j + 1`, self-overlap); direction reverse over the PREFIX
  machine (`pcrec_build_nfa` over `P`'s sub-tree; the family helper of
  `revend.md` §8 with "a seed may be dead": a landmark seed is speculative);
  hands `CAND` per occurrence.
- **Give-up hand-off:** where the forward-verify guard trips (`where_to_start.md`
  §2.7), F4 `relocate` hands `s*` as `LOWER` to the composite (the measured
  `fallback`); `start_table.md`'s FIRST-slot `handoff-rev` row is not needed,
  because relocate IS the FIRST hand-off (E-FL then A3's FIRST row F2 scans from
  the raised `lo`). E11's progress rule (resume past `h`) binds the re-entry.
- **Posture** ONE_WAY on the VM (D151 Q4, ruled). Not built: D151 item 2's
  trigger (the `dup-param-detect` twin) is NOT MET (`where_to_start.md` §7).

**Where to attack §4.** (a) §4.3's window identity rests on (STRUCTURAL) the
prefilter being the erased pattern's DFA body and (MEASURED) `revend.md`'s twin
on DFA artifacts; is any difference between `<p>_prefilter` and a DFA-only
`<p>_search` (no W1/PRESENCE inside, the K73 seek at `lo`, `\G`'s
`search_from`) on the walk's path? (b) The F6-not-F5 rule on clamped ties: no stage-2
corpus member is both clamped and tie-capable (`(a$){1,3}` declares
`window_end` but cannot end on `'\n'`; `([^c]{1,3})$` can tie but declares no
clamp), so F6's population is constructed: `(\s+){2}$` and `(\s$){1,3}` are both
(this build: `size_t window_end;` emitted, `VM_PRUNE_CEILING
"prefilter-window"`). Check whether `max(D)` would actually move a step count
on them. (c) §4.4 per erasure: a fifth erasure,
or an `ew_walk` arm that pins through a lookaround. (d) §4.5's relaxation: a
backreference whose matched bytes are NOT a path of `relax(G_N)` (a `\K`
inside the group? a branch-reset group? `(?|...)`, DUPNAMES `(?J)`: a name
naming several groups needs the UNION of their relaxations); and the claim that
a cyclic reference is the only source of Σ*. (e) Whether `locate-decides` is a
general PRESENCE row (any whole-answer locator) or a special case.

---

## 5. Build sequencing (D156 item (e))

No ids are taken here (counts only). Every count below is a COUNT of new rows
for the build lane to number from the range its brief names (BOILERPLATE: the
highest id on main is `S703` at `525dec33`; the kit's reserved ranges are not
free).

### L0 — the two slots, no mover

- **What:** `CAND_SLOT_LOCATE`/`CAND_SLOT_FINISH` in `CandSlot` (core/internal.h)
  and `cand_nodes[]`; the rows A1, A3, A4, A5 and F1-F7 reproducing today's
  choice; `CandSel.hand`; `cand_finish_of(cx)` read by the ten FINISH reads of
  §3.3 (`emit_dfa.c:1650`, `:1728`, `:3145`, `:9768-9784`, `:10068-10083`,
  `:10707`); LOCATE's selection read by `pcrec_emit_dfa_engine` (`:11212`) in
  place of its `if/else`; RECOVER's succ → FINISH; the inlined RECOVER's declared
  type `CAND` on a superset prefilter (F-3); `dfa_match_is_unwrapped` reads a
  property (F-2); W1's `giveup` and the PRESENCE rows' on `CR_VM` per §1.5
  (F-1, data only). The route-class predicates (`:6847`, `:7155-7159`, `:7360`)
  are NOT touched (start_table's filed third axis).
- **abi:** none. No emitted byte, no stamp, no listing byte moves (LOCATE/FINISH
  get no `--list-axes` projection until L2's declared listing change).
- **Checks:** `scripts/emit_sweep.py` at 0 movers on every arm (the six streams,
  `-e utf8`, `-i`, the deny arms incl. `-fno-anchored-dfa`,
  `-fprefilter-collapse`); the C1 trace's SET compare (`trace_diff.py
  --unordered`) with the new slots' records; `cand_rows_selfcheck` extended
  (totality over `hand`; every LOCATE row's hand set taken on its routes; RECOVER
  → FINISH; the posture derivation of §1.5 as a declared-vs-derived compare);
  `tests/codegen/run_cand_rows.sh`, `run_cand_oracle.sh` (a witness per new row:
  `[^\x00-\xff]` A1, `a` A3, `^a` A4, `(\w+)\1` A5; F3/F6 have no producer until
  L2/L3 and ship `UNREACHED`, S219's precedent); `start_table/call_graph.py` +
  `inventory_check.py` re-derived (every new decision site dispositioned).
- **New sabotage ids: 5.** LOCATE order swap (`empty` after `fwd-rev`: the empty
  engine emits a scan); `cand_finish_of` misderives a hybrid as the entry (the
  inlined body emits W/P/F twice); RECOVER's succ reverted to CALLER (self-check);
  a LOCATE hand type with no total FINISH row (self-check); a declared posture
  that the derivation contradicts (self-check). **Re-aims:** 0 by the grep at
  this pin (the rows anchored on finish-adjacent lines, S476 `:7360`, S493
  `:6847`, S494 `:439`, sit on lines L0 leaves alone); re-runs derived by
  `start_table/sabotage_anchors.py`'s `rerun_at` against L0's edit set.
- **Spec:** none (no caller-observable change). `start_table.md` §1.2/§1.6 gain
  the two slots and E-LF/E-FL/E-FR (the manager's merge, as E13 would have been).
- **Deny/force:** none new.

### L1 — `revend.md` S0 and S1, unchanged

The `end_pin` fact split (W1's `end_window` becomes its reader; no mover) and the
parameterized reverse-block helper with the dead-seed skip and the which-seed
report (no mover, byte-identical for RECOVER). Checks, sabotage and spec as
`revend.md` §9.1 items 1-2.

### L2 — `rev-end` (stage 1, DFA finishers): the abi event

- **What:** LOCATE row A2 with the stage-1 conjunct; `nl_last`; FINISH F3/F4 gain
  their `ENDSET` producer; the walk emission (`revend.md` §5.1) at the head of the
  body, the composite not emitted under T1/T2 and emitted for F4 only where the
  hand set holds `ENDSET` and `dfa_matches[]` says `search-filter`; `-fno-rev-end`
  (one new bit, the manager's allocation); the `locate` listing axis (A2 order 1,
  A3 order 2); the stamps by §5.1's rule below; and **D-2's `attempt-start`**
  (`start_table.md` §6 Q5, ruled "a later LOW-priority row, batched with the NEXT
  abi event"): it is the same rule as REVEND's downstream stamps (a slot not on
  the locator's path stamps its absence), so it rides this event.
- **abi:** 71 → 72. Readers BY GREP at build time (D76/D94): (a) the abi NUMBER
  (`revend.md` §5.3 (a)'s list is current at this pin: abi is still 71 at
  `525dec33`; this lane's grep finds the same files plus `memfn/docs/*` prose,
  which are history, not readers); (b) the byte-count readers (§5.3 (b));
  (c) the `END_WINDOW` value readers (§5.3 (c)), which under this design do NOT
  gain a value (§5.1); (d) the `DFA_SCAN` value readers (33 files, 6 sabotage
  rows, `revend.md` §5.3 (d)) and the `DFA_START` value readers (19 files, 5
  rows) for D-2; then the counting suites (registry, codegen, rxtsource) whether
  or not they cite the number (D94 addendum).
- **Movers:** census T4: 12 bench (the 5 tail patterns, `letters-bounded-tail-z`,
  the 6 class-B cells incl. `wild-semdiv-dollar-trailing-newline-pcre2` in two
  sets), corpus 171 rows / 121 distinct (41 distinct unbounded, 80 bounded); plus
  D-2's population (census T8: every artifact stamping `"reverse-pass"` on an
  ATTEMPT or empty locator, hybrids included: 37 bench / 606 corpus rows, 481
  distinct). The
  build's `emit_sweep` default vs `-fno-rev-end` census must equal the set whose
  text carries `revend_seed` (`revend.md` §5.4).
- **Checks:** `revend.md` §9.1 item 3's list, with E13 replaced by E-LF and the
  W1-vs-REVEND order question gone (they are in different slots: A2 pre-empts
  the composite, W1 is inside it). The answer net `tests/assertions/rev_end.rxt`
  (§9.3), the codegen structural check (`"rev-end"` ⇔ `revend_seed` emitted;
  `nl_last` false ⇔ no tie text; a declining pattern byte-identical under
  `-fno-rev-end`), the test-axes floor arm (X13), the refusal-set check, C17 and
  the memfn stamps (§4.3).
- **New sabotage ids: 17.** `revend.md` §9.2's 16, recast: rows 1-10 unchanged;
  11 (R2) becomes "the route mask widened to `CR_ATTEMPT`" (same witnesses);
  12 (R3) "the stage-1 conjunct dropped" (a hybrid selects the walk with no
  PRESENCE deference: the codegen check sees a pre-check emitted before a walk);
  13 (R4) "`empty` after `rev-end`"; 14 the deny unplumbed; 15 F4 made
  unconditional; 16 the stamp forked from the selection (now `DFA_SCAN`); plus
  1 for D-2 (`DFA_START` forked from RECOVER's absence). Re-aims: S264 (X8,
  its probe to `(abc)$`), S693 (the abi constant), and every `DFA_SCAN`/
  `DFA_START`/§5.3 (d) row whose witness is a mover (the movers census names
  them).
- **Spec (D80):** `tuning.md` §2.x `-fno-rev-end`; `match_api.md`: `DFA_SCAN`
  gains `"rev-end"`, `DFA_START` gains `"attempt-start"` (and its
  `:4686-4703` contradiction is fixed), the downstream stamps' absence values on
  movers, `rx_info.search_form`, the abi sentence and TU-guard example;
  `registry.md` axis counts and the new `locate` axis; `facts_listing.md`
  `end_pin`; `cli.md` where it lists axes.
- **Deny/force:** `-fno-rev-end` (deny only; nothing branches on it, the walk
  skips the row).

### L3 — stage 2 (VM finishers): FILED

Drop the stage-1 conjunct; PRESENCE `locate-decides` + the DAG edge; F6's arm;
the window-identity twin and the answer net's captures cells (`(\d+)$`, `(a+)$`,
`a\Kb$`, the unclamped tie `([^c]{1,3})$`, the constructed clamped ties
`(\s+){2}$` and `(\s$){1,3}`, the superset witness). abi 72 → 73 (or
folded into L2 if Frank rules so, §7 Q3). Movers: 0 bench / 13 corpus (T5).
**New sabotage ids: 4** (the deference dropped: a pre-check emitted ahead of an
inlined walk, codegen check; a clamped tie sent to F5 (`max(D)` as the ceiling:
the window-identity twin, which compares `window[0][1]`, goes red); a superset
walk declared `SPAN` (the retry text dropped: answer net on a constructed
superset witness whose leftmost `L'` start fails in `L`); the inlined LOCATE ask
read on `CR_VM` instead of `CR_DFA`). Spec: `match_api.md`'s hybrid stamps.
Trigger: `revend.md`'s, unchanged.

### L4, L5 — FILED

L4 `rev-end-relaxed` (§4.5): its own erasure mode in `src/ir/nfa.c`, a LOCATE row
on `CR_VM`, its own deny (§7 Q6), ONE_WAY with D148 Q6's spec sentence. L5
rev-inner (§4.6): D151's trigger.

### 5.1 The stamp rule (no new stamp)

`RX_DFA_SCAN` already IS LOCATE's projection: its three values today
(`unanchored`, `attempt`, `empty`) are exactly A3, A4, A1 (census T1 classifies on
it, control C1 holds it against the text). So `rev-end` is a fourth VALUE of
`RX_DFA_SCAN`, not a new `RX_LOCATE` stamp, which would put new bytes on every
artifact and move every byte-count reader for no new information. `RX_END_WINDOW`
keeps its vocabulary (a number or `"none"`): on a `rev-end` artifact W1 is not on
the path, so it reads `"none"` like every artifact whose window the search does
not use; `revend.md` X10's one-spelling rule holds (`"rev-end"`, the row's listed
name, now on `DFA_SCAN`). `RX_DFA_START` keeps `"reverse-pass"` on `rev-end`
artifacts, which is TRUE there (the start is found by walking the reverse
machine), and gains `"attempt-start"` where no reverse machine exists (D-2). The
other slot stamps (`DFA_PREFILTER`, `_OFFSETS`, `REQ_*`) read their existing
absence value. The general rule, for the spec: **a slot that is not on the
selected locator's path stamps its absence value, and the locator is named once,
on `RX_DFA_SCAN`.** Spellings are the manager's call (memory
`pcrec-dd13b-syntax-is-managers`); the rule is the proposal.

**Where to attack §5.** (a) L0's "no mover": the ten FINISH reads include the
dead-group fill and `rx_info.match_form`; a `cand_finish_of` that disagrees with
`fit.chosen` on one artifact class (an EMPTY hybrid, `P-empty`, 18 corpus) moves
bytes. (b) The sabotage counts: is any obligation of §1.4 left without a row?
(O6 and O7 ride the answer net, not a plant.) (c) §5.1: does any reader treat
`RX_DFA_SCAN` as "the forward scan's form" in a way `"rev-end"` breaks (memfn's
site manifest, `scanedge`'s precondition (8), the axes floors)? (d) Batching D-2
into L2: the ruling says "batched with the next abi event"; is a stamp-vocabulary
change on 37 bench / 606 corpus artifacts (T8) acceptable inside a feature's
abi event, or should D-2 ride its own small event?

---

## 6. Standing questions (`docs/design/CLAUDE.md`)

### 6.1 The measurement regime — RELEVANT, briefly

This note takes no timing. Every number it reads is either compile-side (the
census: counts from stamps, facts and emitted text, regime-free) or `revend.md`'s
scratch-tier Linux timing (7700X, warm repeated calls, cited for REVEND only, with
its own regime section §12.1). The one decision a regime could flip is stage 2's
value, which is FILED on a population of 0 bench cells, not on a timing. The
census reads one corpus and one bench pin; a grown corpus moves the counts, not
the design.

### 6.2 The independent control — RELEVANT

- **The census.** C1 holds the reverse-machine stamp against the emitted text
  (the stamp writer reads the selection; the grep reads the bytes), C2 the hybrid
  stamp against the text, C3 the borrowed end-pin probe (a copy of `ew_walk`)
  against the shipped fact (`src/facts/endwin.c`). `analyze.py` refuses to print a
  table if any disagrees, and C1 earned it: the first marker read 146 false
  disagreements (the uniform-fold representation has no next-state accessor),
  recorded in the study's CLAUDE.md. The population is counted by the borrowed
  `bench_pop`/`corpus_pop`, the same rows `revend_census.md` counted (K35: who
  counts is named).
- **The design's checks.** The extended `cand_rows_selfcheck` is a CONSISTENCY
  check: it shares its source with the table. The controls are elsewhere: the
  emit sweep (bytes, not selections) for L0; libpcre2 10.46 on the answer net
  and `-fno-rev-end` for L2 (`revend.md` §12.2); for L3, the window-identity
  twin compares the walk against the SHIPPED prefilter, which shares the reverse
  block but not the seeding, the seed record or the forward pass.
- **Witness reach ([MECH-REACH]).** F3 and F6 have no producer before L2/L3 and
  ship `UNREACHED` with the argument; the L0 rows each get a constructed witness.

### 6.3 What moves when data is regenerated — RELEVANT

- L0 moves nothing (no abi event).
- L2: the abi number and the `DFA_SCAN`/`DFA_START` values on movers (§5); no
  calibration or data file is read (`end_pin`, `nl_last` are derived per
  compile; `nl_last` from the built reverse machine).
- L4's relaxed machine reads no data. rev-inner's G3 reads the byte-rate prior
  (`default_ppm.tsv`), the [OPT-REQBYTE] exposure.
- The census outputs (`rows.tsv.gz`, `summary.txt`, `finish_sites.txt`) move with
  the tree; no check reads them.

---

## 7. Questions for Frank (discussion)

**Q1. Where FINISH lives.** *Problem:* D156 says "a separate first-match FINISH
table"; D151 addendum 3 says one `cand_rows[]` with a slot field, "otherwise logic
is spread around". *Forces:* the FINISH walk has a third key (`hand`) the other
slots do not; a separate array would make that key local, but would put the
LOCATE → FINISH edge across two tables, and the typed-handoff self-check reads one
array. *Leaning:* a slot block in `cand_rows[]` (§2.2), the `hand` key as a
`CandSel` field filtered like the route. I read your "separate table" as "its own
first-match block", which is what every former start table already is. Is that
your intent, or did you mean a table outside the start family?

**Q2. Do L0 before REVEND, or land LOCATE/FINISH inside REVEND's abi event?**
*Problem:* REVEND needs a home; LOCATE is that home, FINISH is the general part.
*Forces:* D153 (remodel first) and the start table's own precedent (a no-mover
fold, then the movers) favour L0 first; L0 is ten read sites and two slots, small
next to refactor A. Against: L0 alone delivers nothing measurable, and the panel
must review a refactor whose only immediate customer is one row. *Leaning:* L0
first, kept to the §5 list (no route-class work, no posture enforcement beyond
the self-check), then L1/L2. If you would rather fold it, L2 grows by L0's checks
and the "no mover" proof becomes "movers = REVEND's set exactly".

**Q3. Stage 2 with stage 1?** *Problem:* the stage-1 conjunct is the one place
this design keeps a route-independent locator off a route. *Forces:* the
mechanism is small (§4.3), NEUTRAL, and not building it is the special case; but
the measured population is 0 bench / 13 corpus, 11 of them already clamped by W1,
and D77 says wait for a measured need. *Leaning:* FILED with `revend.md`'s
trigger, the conjunct commented as stage 2's switch. If you see the generality
argument as outweighing D77 here, it folds into L2 for one PRESENCE row and one
twin.

**Q4. The stamp rule.** *Problem:* `revend.md` Q2 asked how downstream stamps
read on an admitted artifact; D-2 is the same question on ATTEMPT artifacts.
*Forces:* a new `RX_LOCATE` stamp is the most explicit but moves every artifact's
bytes; `RX_DFA_SCAN` already carries exactly the locator choice. *Leaning:*
§5.1's rule (the locator on `DFA_SCAN`, absence values elsewhere, D-2 batched
into L2). The spellings are the manager's to settle; the rule is the question for
you.

**Q5. Posture derived from the pair.** *Problem:* §1.5 found W1's VM-route cell
(and the PRESENCE rows') declared NEUTRAL where the definition says ONE_WAY; no
check reads the column. *Forces:* deriving it (O4) makes it checkable and makes
REVEND's stage-2 NEUTRAL a provable property instead of a sentence; it also forces
a spec sentence for W1 and the pre-checks (a give-up may become an answer under
`-fno-end-window`/`-fno-req-byte`'s complements), which nobody has asked for.
*Leaning:* derive it in L0's self-check, correct the two cells as data, and add
the one-way sentence to `tuning.md` §2.26 / §2.27 only if you agree they are
ONE_WAY (I believe they are; they skip only failing attempts).

**Q6. The relaxed-reverse locator's deny.** *Problem:* it is the same walk as
`rev-end` over a different (relaxed) machine. *Forces:* one deny keeps the family
one switch; but its posture (ONE_WAY) and its erasure mode differ, and
`test-axes` can only isolate what has its own bit. *Leaning:* its own bit when it
is built (filed today); noted now so the L2 bit is not later overloaded.

---

## 8. The lenses

- **specific vs general:** general. Six types and seven finishers cover every
  shipped mechanism; REVEND's E13, its tie table, its R2/R4 conjuncts and its
  stage 2 all become instances (an edge, FINISH rows, table structure, a
  conjunct) rather than special cases.
- **core vs derived:** the tables are derived; `end_pin`, `nl_last` and the
  relaxed machine are core facts or machine properties.
- **applicable vs assumption-changing:** applicable. No contract changes; one
  declared type (F-3) and one posture cell (F-1) are corrected as data.
- **fits the architecture vs refactor:** L0 is a small refactor in refactor A's
  shape; L2 fits.
- **shared question / engine hat (D124):** this is D124 split along its other
  axis: the start table asked "where can a match start" with the engine as a
  route; FINISH asks "what does the engine still have to compute", with the
  locator's type as the key.
- **sibling of a family:** §3; `dfa_matches[]` is FINISH's existing member.

---

## 9. Findings for the record

- **F-1** W1 `window` and the PRESENCE rows on `CAND_ROUTE_VM` declare (by the
  zero value) a NEUTRAL give-up posture where §1.5's own definition makes them
  ONE_WAY; the column has no reader. §1.5, Q5.
- **F-2** `dfa_match_is_unwrapped` (`emit_dfa.c:7727`) compares a selected row's
  POINTER, the shape sound-m2 removed from RECOVER. §3.4.
- **F-3** RECOVER's rows declare `CT_START` unconditionally; on the 22 bench / 621
  corpus superset-prefilter hybrids the inlined body's result is a `CAND`. §2.5.
- **F-4** `revend.md` §3.9's stage-2 posture (ONE_WAY) is NEUTRAL given the F6
  rule. §4.3.
- **F-5** `start_table.md` §4.1 places rev-inner in NEXT; its verifier is the
  anchored finisher, so it is a LOCATE row and `handoff-rev` is F4. §4.6.
- **F-6** D156's type list omits `CAND`. §0 item 3.
