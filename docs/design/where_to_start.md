# Where should a search start? — landmarks, reverse walks, prefilters

**STUDY / DESIGN NOTE, nothing built** (lane `startstudy`, 2026-10-06, from main
`6816f839`). Nothing under `src/`, `cli/`, `lib/` or `tests/` changes. Instruments
and committed output: `where_to_start/` (own CLAUDE.md). Rulings are Frank's; §5.4
lists the open questions, each with a recommendation.

Frank's three questions (2026-10-06):

1. "Is there a general strategy around not starting at the beginning?"
2. "If the DFA goes backwards from the middle, can it record the match start?"
3. "Does all this work as a prefilter?"

Rows read before writing (memory: grep the plan first): `[ENG-TACTICS]` (plan.md:393,
Frank's row, tactics (a)/(b)/(c) and its "no general planner, first-match tactic
rows" principle), `[OPT-REVEND]` (:340) + `docs/dev/optloop/revend_census.md`,
`[OPT-A]`, `[OPT-VMSEED]`/`[OPT-FIRSTSET]` = START-SET (`startset.md`, D148 +
addenda), `[OPT-K]` (`offset_k_skip.md`), `[OPT-REQPOS]`/`[OPT-REQBYTE]`/K82
(`litscan_k82h.md`), D124, the first-match-table memory, `[PATFACTS]`,
`decisions.md:1032`'s reverse-inner lead, and the `[ARTREV]` pilot
(`report_pilot.md` §5 #2, `generalize.md` I1).

---

## 0. Answers first

1. **Yes, and pcrec already has most of it, spelled as six separate mechanisms.**
   Every one of them answers the same question with the same four parts: a
   NECESSARY FACT (a landmark every match contains), a SCANNER that finds its
   occurrences, a MAPPING from an occurrence to candidate starts, and a VERIFIER.
   What differs is the mapping: EXACT (a start at offset 0, or a fixed offset k),
   BOUNDED (a window, or a lower bound `hit − K` for the forward scan), or
   PRESENCE-ONLY (the fact can only say "no match"). §1 tabulates them with
   file:line. The one mapping pcrec does NOT have is an EXACT start for a landmark
   behind an UNBOUNDED prefix — today such a landmark is presence-only. That is
   what a reverse walk adds.
2. **Yes, with conditions.** Split the pattern `R = P·L·S` at a necessary literal
   `L`. A reverse walk of `P` seeded at an occurrence `j` of `L` accepts exactly
   the starts `s` with `subject[s:j] ∈ L(P)`; the smallest is the leftmost start
   of any match that uses that occurrence. It is the overall leftmost start, and
   the forward engine from it gives PCRE's end and captures, **iff the split is
   unambiguous** (no later occurrence can yield an earlier start) **and `P` is
   regular-faithful** (no backreference, no atomic group or possessive
   quantifier). Measured against libpcre2 10.48 on 9,822 generated `P·L·S`
   patterns: **0 mismatches over 329,771 single searches and 57,204 find-alls**
   where the gate holds; all 6 planted mutations are detected, and the ungated
   and erased-atomic variants are shown wrong (§2.6). Without the gate the answer is wrong (19 + 1 witnesses), exactly the
   bug rust's `regex` shipped and fixed in July 2026 (§2.3).
3. **Yes — and the prefilter form is where it matters most.** The reverse walk is
   a CANDIDATE GENERATOR: it hands exact candidate starts to any anchored engine.
   Only `P` must be backref-free; `S` may hold anything. That reaches the
   backreference/linked-call population that today gets NO DFA prefilter at all
   (`select_engine.c:862`): the prefix machine is built from `P`'s own sub-tree,
   so the erasure problem that blocks the hybrid (`select_engine.c:579-611`) never
   arises. A bounded-width `P` collapses to today's offset-k / handoff; §3.

**The census (§4, K35, with controls):** over 2,096 corpus + 250 bench unanchored
patterns the reader parses, the best necessary landmark is NOT at the pattern's
start on **480 corpus / 24 bench**; 374 / 16 of those are ≥2× rarer than what the
artifact scans today. The new mapping (exact reverse walk behind an unbounded
prefix) reaches **77 corpus / 8 bench**; on the VM-only route it reaches 5 corpus /
3 bench, every one with its backreference in `S` (bench `dup-param-detect`,
`bak-1`, `bak-g-rel`; corpus the K65/K66 witness blocks, K66's own
`(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` among them). `loglines/stack-frame` (ARTREV A01, −72%) is in it.

**Recommendation (§5):** no planner. One row family — a REVERSE-WALK CANDIDATE row
— added to the existing candidate table under the existing ordering principle
(order by the mapping's information, not by a cost model), with a three-conjunct
gate taken from a measured model, a guard that hands off to the forward scan
rather than giving up, and the VM backref population as its D77 trigger.

---

## 1. (A) Inventory and unification

### 1.1 The one contract

Every start mechanism is a ROW: `(landmark, scanner, mapping, verifier)`.

- **landmark** — a necessary fact: a byte set at offset 0 (`start_set`), a byte or
  run at a fixed offset (`kset_walk`, `run_pin`), a run somewhere (`req_run` +
  `req_run_maxoff`), a byte somewhere (`req_set`, `req_byte`), the subject end
  (`end_window`).
- **scanner** — `memchr`, a pair/run compare, a 256-entry table loop, the DFA's
  own state-0 skip.
- **mapping** (what a hit says about where a match may START):
  - `EXACT` — the hit IS a candidate start (offset 0) or determines one
    (`hit − k`);
  - `WINDOW` — candidates lie in `[hit − b, hit − a]`;
  - `LOWER-BOUND` — no match starts before `hit − K`; the forward engine scans
    from there (K82 handoff);
  - `PRESENCE` — absence proves no match; the position is discarded.
- **verifier** — the forward DFA (unanchored from a position, or re-seeded), the
  reverse pass, a VM anchored attempt, the hybrid's DFA-then-VM.

### 1.2 What ships, cast as rows

| mechanism | landmark (fact) | scanner | mapping | verifier | where |
|---|---|---|---|---|---|
| anchored start (`^`, `\A`, `\G`) | `start_anchor` | none | EXACT, one position | anchored engine | `src/facts/startanch.c`; one attempt (`[OPT-ANCHOR-VM]`) |
| `run-pinned[-bounded]` | `req_run` pinned at `o` (`run_pin`) | `<p>_ofsskip` on the run's member at its offset | EXACT `hit − (o+idx)` | forward DFA, re-seeded | `emit_dfa.c:6659-6664`, predicate `:6009-6041` |
| `offset-set[-bounded]` ([OPT-K]) | `kset_walk` (offset, byte-set) pairs | memchr on the rarest offset, verify the rest | EXACT `hit − k` | forward DFA, re-seeded | `emit_dfa.c:6665-6670`, `:5970-5980` |
| `first-class` (START-SET VM hat) | `start_set` | 256-table seek | EXACT (offset 0) | VM attempt | `emit_dfa.c:6672-6674`, `:6601-6614` |
| `first-*` DFA hat (stage 3, lane ssbuild3) | `start_set`, `T = S` | memchr / table | EXACT (offset 0) | forward DFA, re-seeded | `startset.md` §2 |
| `memchr[-bounded]`, `byte-class[-bounded]` | s0's escape set `E` (`unanch_start`, `emit_dfa.c:4191`) | memchr / table | EXACT (offset 0) | forward DFA | `emit_dfa.c:6675-6682`, `:5786-5796` |
| req-byte / req-run pre-check ([OPT-REQBYTE], [OPT-REQPOS]) | `req_byte`, `req_run` | memchr / run search | PRESENCE | — | `pcrec_emit_req_byte_check`, `emit_dfa.c:1362-1407`; admission `req_admits[]` `:7014-7024` |
| K82 `set-leads` | rarest `req_set` byte | memchr | PRESENCE | — | `req_set_leads_applies`, `emit_dfa.c:7021`; emitted by `emit_req_one_byte` `:1313` |
| K65/K66 rest-of-set / whole-run | `req_set`, whole `req_run` | memchr / run | PRESENCE (the VM's only linear no-match proof) | — | `emit_req_set_rest` `:1259`, `emit_req_run_check` `:1159` |
| K82 handoff | `req_run` + `req_run_maxoff` = K | the pre-check's run search | LOWER-BOUND `max(startpos, c − K)` | forward DFA / hybrid prefilter | `emit_req_handoff` `:1116-1147`; `req_uses[]` `:7129-7134`; predicate `:7097-7114` |
| [OPT-ENDWIN] | `end_window` | arithmetic | WINDOW (start ≥ n − maxw) | forward DFA / VM | `pcrec_emit_end_window_clamp` `:935`; VM `emit_vm.c:13170` |
| reverse-pass start | the whole pattern's reverse DFA | — | EXACT, from a match END | reverse DFA | `dfa_search_starts[]` `:7659-7662` |
| hybrid prefilter | the whole pattern's DFA (exact or count-collapsed) | the DFA scan | EXACT window (exact lang.) / SUPERSET (collapsed) | VM over the window | `emit_vm.c` (`pcrec_vm_prefilter_window` `:3634`); declined for backref/call `select_engine.c:613-862` |
| [OPT-REVEND] (filed) | `\z`/`$` end pin | none | EXACT from the end, by reverse walk | reverse DFA then anchored | plan.md:340 |
| [OPT-A] multi-literal (filed) | per-alternative literals | memchr2/3, pair scan | EXACT per alternative | forward DFA | plan.md:1165 |
| [ENG-TACTICS] (a)/(b)/(c) (filed) | inner necessary literal `L` | memchr / run | (a) WINDOW, (b) EXACT by reverse walk, (c) EXACT + forward resume | VM / DFA | plan.md:393 |

### 1.3 Where these are parallel special cases of one form

Memory `pcrec-general-mechanisms-not-special-cases` asks this directly. Four
places:

1. **The same scan, two uses of its answer.** The run pre-check
   (`emit_req_run_check`, `emit_dfa.c:1159`) finds the run's leftmost window
   `c`. Under `req_uses[]` row `handoff` it is used as a LOWER BOUND; under
   `scan-from-startpos` (`:7132`) it is discarded. On the VM route with no DFA
   scan the handoff is declined by conjunct (a) (`:7103`,
   `pcrec_artifact_has_dfa_scan`) — the position is computed and thrown away,
   which is [ENG-TACTICS]'s (a) observation (plan.md:393 cites it as
   `emit_dfa.c:810-841`, `emit_vm.c:12731` at 2026-09-25; today the VM call site
   is `emit_vm.c:13189` and the decline is `emit_dfa.c:7103`).
   And K82 `set-leads` (`:7021`) memchr's a byte RARER than the run's scan
   member and uses it only to say no: the ARTREV pilot counts 12 of 17 bench /
   50 of 90 corpus I1 artifacts in exactly that state (`report_pilot.md` §5 #2).
   One scan, one fact, and the mapping chosen by which table you are in.
2. **Two tables answering "where can the scan begin".** `dfa_pfs[]` (`:6658`)
   decides how the forward machine finds its NEXT candidate; `req_uses[]`
   (`:7129`) decides where its FIRST scan begins. A LOWER-BOUND row is a
   candidate row whose candidate is "scan from here"; `litscan_k82h.md` §2.1 kept
   them separate because `dfa_pfs[]` was DFA-only and loop-internal. Since
   START-SET made `dfa_pfs[]` engine-neutral (`CAND_ROUTE_VM`, D148), the
   separation is no longer forced.
3. **Offset-0 vs offset-k vs offset-window are one mapping with three widths.**
   `memchr`/`byte-class` (offset 0), `offset-set`/`run-pinned` (offset k) and the
   handoff (window `[0, K]`, used as a lower bound) are the same arithmetic
   `start = hit − k`, `k ∈ [a, b]`, with `a = b = 0`, `a = b = k`, and `a < b`.
   They are rows of one table already (`dfa_pfs[]`) except the window case,
   which lives in `req_uses[]`.
4. **Three reverse machines over three slices of the pattern.** The reverse-pass
   start (whole pattern, from a match end), [OPT-REVEND] (whole pattern, from the
   subject end) and [ENG-TACTICS] (b) (the prefix `P`, from an inner landmark)
   are one operation — "seed a reverse machine at a known position, take the
   smallest accepting position" — differing in the seed and in the slice.
   `compile.c:1882` builds the reverse NFA over `root`; nothing structural stops
   it being built over a sub-tree (`pcrec_build_nfa` takes an `Ast *`).

None of these is a defect today: each landed as the measured mechanism of its
own row. But the next row in this family should be ONE row in the existing
table, not a seventh mechanism.

### 1.4 "Pick the best landmark" as a first-match table

The memory rule (Frank 2026-09-28) is that every selection is an ordered
predicate-row table, first passing non-denied row executes. The question is what
orders the rows.

- **Order by the mapping's INFORMATION, not by modelled cost.** This is the
  existing table's own principle (`startset.md` §2: "ordering by information is
  the existing table's own principle; it is not a cost comparison (D146)"), and
  it is the right one here: an EXACT candidate is worth more than a WINDOW, a
  WINDOW more than a LOWER-BOUND, and those more than PRESENCE, independent of
  the subject. The subject only changes HOW MUCH an exact row saves.
- **Rarity enters as an ADMISSION conjunct, not as an order.** "Use an inner
  landmark only if it is ≥F× rarer than what the offset-0 row scans" is K1's /
  I1's predicate. F is a D149 suspect constant; the census reports F = 1, 2, 8.
  A per-row admission keeps the table first-match; a cross-row argmin would turn
  it into a planner, which [ENG-TACTICS] rules out ("no general planner").
- **Predicates come from [PATFACTS] facts that already exist, plus one new
  one.** `start_set`, `kset_walk`, `run_pin`, `req_run`, `req_run_maxoff`,
  `req_set`, the byte-rate prior — all `src/facts/`. The new fact is the
  INNER-LANDMARK SPLIT: the spine index of the chosen landmark, `P`'s byte width
  `[a, b]`, and the gate's three bits (§2.4). It is a core fact (an AST walk over
  the top-level concatenation, rust's `top_concat`/`flatten`), owner
  `src/facts/` by `patfacts/design.md` §4's rule.

The table, in information order (existing rows unchanged, new rows marked):

```
row                         mapping     predicate (facts)                                      verifier hat
run-pinned[-bounded]        EXACT  k    run_pin, scan identity                                 DFA (re-seed)
offset-set[-bounded]        EXACT  k    kset_walk selection                                    DFA (re-seed)
first-* (START-SET)         EXACT  0    start_set narrows                                      DFA / VM
memchr / byte-class         EXACT  0    s0 escape set                                          DFA
NEW rev-inner-bounded       EXACT       split ∧ gate ∧ b finite ∧ admit(F)                     DFA / VM / hybrid
NEW rev-inner               EXACT       split ∧ gate ∧ admit(F)                                DFA / VM / hybrid
none                        —           always                                                 the attempt loop
---- req_uses[] (where the first scan begins) ----
handoff                     LOWER-BOUND req_run, K finite                                          DFA / hybrid
NEW handoff-rev             LOWER-BOUND split ∧ gate (the candidate loop's give-up, §2.7)          DFA / hybrid / VM
scan-from-startpos          —           always
```

Why the new rows sit BELOW the offset-0 rows: an offset-0 row that applies is
already scanning a landmark that IS a start; the new row only beats it when its
landmark is rarer (the admission). Why ABOVE `none`: on a VM-only artifact `none`
is "every position is an attempt". The `-bounded` twin carries the D11 views bound
exactly as the existing pairs do.

**Argument against the table, considered and rejected:** "the best landmark
depends on the subject, so a static first-match table cannot pick it." True, and
already true of every row above it; [FINDINGS] supplies the rate, the table stays
static. `sel_cost.md` §3's admission rule (the sign must hold in every regime)
applies to F.

---

## 2. (B) Q2: the reverse walk from an inner landmark — soundness

### 2.1 Definitions

`R = P·L·S`, a top-level concatenation (after splicing un-quantified groups), `L`
a literal byte string (or a caseless one). For an occurrence of `L` at `j`
(`subject[j:j+|L|] = L`), and a search from `lo` (`search_from`):

- `starts(j) = { s ∈ [lo, j] : some path of P matches subject[s:j] }`, each
  path's views (`\b`, `^`, `$`, lookbehind) read the REAL subject around it.
  This is what a reverse DFA of `P` seeded at `j` and run down to `lo` accepts.
- `s*(j) = min starts(j)`.
- **The walk RECORDS `s*(j)`** — the smallest accepting position, the same rule
  the shipped reverse pass uses (`dfa_search_starts[]` `"reverse-pass"`,
  `emit_dfa.c:7661`) and [OPT-REVEND] uses from the subject end. It never
  records an END: the end comes from a forward run (§2.5).

**Tactic (b), the candidate loop:** for each occurrence `j ≥ lo` of `L` in
increasing order: if `starts(j) ≠ ∅`, run the forward engine ANCHORED at `s*(j)`;
if it matches, that is the answer; otherwise continue with the next occurrence
(`j + 1`, not `j + |L|`: `L` may overlap itself).

### 2.2 Claim and preconditions

**Claim.** If (G1) `P` holds no backreference, call, atomic group or possessive
quantifier, (G2) the split is UNAMBIGUOUS — `P` has fixed byte width, or `P`
cannot consume every distinct byte of `L` — and **(G4) `S` holds no reference
into `P`'s groups** (no backreference to a group of `P`, no condition on one; and,
conservatively, no `${...}` variable) **[r2 E1]**, then tactic (b) returns exactly
libpcre2's leftmost-first match (span and captures) from `lo`. Without G4 the
sound mapping is weaker: `LOWER = s*(j₀)` for the first occurrence `j₀` whose
`starts` is non-empty, finished by the ordinary attempt loop from there (below).

Argument, in three steps:

1. *Per occurrence.* A match starting at `s` that uses occurrence `j` has
   `s ∈ starts(j)`, and conversely any `s ∈ starts(j)` with an `S`-continuation
   from `j + |L|` gives a match at `s`, PROVIDED the continuation does not depend
   on `s` — which is G4. So under G4, if any match uses `j`, the anchored forward
   run at `s*(j)` succeeds, and the leftmost start among matches using `j` is
   `s*(j)`.

   **[r2 E1] CORRECTION (lane locfin2, 2026-10-09; panel
   `../dev/reviews/2026-10-09-r-locfin-panel.md` LF-E1).** The first version of
   this step read "when it does [reference `P`], the forward verify reads the real
   captures", and concluded the same. That is UNSOUND: when `S` references a group
   of `P`, the capture `P` makes depends on `s`, so the verify at `s*(j)` can FAIL
   while a larger `s ∈ starts(j)` SUCCEEDS, and the tactic then moves to the next
   occurrence and loses the match. `(a+)X\1` on `"aaXa"`: `starts(2) = {0, 1}`,
   the verify at 0 fails (`\1` needs `aa`), libpcre2 answers (1,4), the tactic
   NOMATCH; a second witness returns a LATER match than the leftmost. Measured by
   the critic: 82 wrong of 82,903 over the 1,199 gated cases with a backreference
   in `S`; the `lowerbound` form below, 0 wrong. The study's own 0 / 129,222
   (§2.6) reproduces: its population held too few backreferences in `S` (K35's
   shape — a population nobody counted). This is exactly rev-inner's VM-route
   population (§3: `\b(\w+)=[^&]*&(?:[^&]*&)*\1=`, `(\w+) \1`), so the
   correction is not a corner case.

   **Without G4: `LOWER`, not a candidate per occurrence.** `starts(j)` depends on
   `P` alone (G1 makes it regular), so step 2's monotonicity holds whatever `S`
   is; hence no match starts below `s*(j₀)`, `j₀` the first occurrence with a
   non-empty `starts`. That is a LOWER bound, and the finisher is the ordinary
   attempt loop from `s*(j₀)` (the VM's, or the DFA body's), not one anchored
   verify per occurrence. It is still a gain wherever `s*(j₀)` is far from `lo`
   (the whole point on the VM-only population), and its give-up posture is the
   loop's, ONE_WAY (it skips only attempts below a proven lower bound).
2. *Across occurrences (the which-occurrence problem).* For `j < j'`, every
   `s' ∈ starts(j')` with `s' ≤ j` would put the whole occurrence at `j` inside
   a string `P` matches — impossible when `P` cannot consume all of `L`'s bytes
   (an overlap of two occurrences needs `P` to consume every distinct byte of `L`,
   rust's argument, §2.3), and impossible when `P` has fixed width `w` (then
   `starts(j) ⊆ {j − w}`, monotone in `j`). So `starts` is monotone in `j`, and
   the first occurrence whose verify succeeds has the leftmost start.
3. *Priority.* PCRE's leftmost-first answer is "the smallest `s` at which an
   anchored attempt succeeds, and that attempt's result". Step 2 gives the
   smallest `s`; the anchored forward run gives the result. Laziness and
   alternation order change WHICH path an attempt takes, never WHETHER one
   exists, so they do not touch `s*`.

**Why G1.** A backreference has no reverse machine (`nfa.c:918-930`, the A_BREF
arm deliberately falls into an internal error). An atomic group or possessive
quantifier changes which strings `P` matches IN CONTEXT; a reverse DFA builds the
erased language, a superset, and an `s*` from the superset can be a start the
real engine refuses while a larger start in the same `starts(j)` succeeds.
Measured (§2.6, `erase_atomic`): with the split CLEAN, walking the erased language
is wrong on 11 / 6 single searches (byte / utf8), e.g.
`(?:[aX]?+a|b?)é(?:[^X]{1,3}?|X)`. A possessive that possessify proves a no-op
(`atomic_groups_design.md`'s free discharge) is not atomic for this purpose; the
gate may read possessify's verdict rather than the spelling.

### 2.3 The which-occurrence problem, and rust's fix

The failure is not hypothetical. rust's `regex-automata` shipped reverse-inner and
reverse-suffix without G2 and returned a later match than the leftmost one:
`.bb|b` on `zabb` reported `2..3` where the answer is `1..4`, and
`(?:..acbb|b)a(?:c|d)` on `xzbacbbac` reported `2..5` where the answer is `1..9`
(rust-lang/regex issue #1354, fixed by commit `64ad0b6`, "automata: fix bug in
reverse suffix/inner optimization", 2026-07-15) [RArevinner]. The fix added
`has_no_earlier_match` (`regex-automata/src/meta/reverse_inner.rs`), which admits
the optimization only when one of three sufficient conditions holds:

- a single literal that the prefix cannot contain ("an occurrence crossing the
  prefix boundary must overlap another occurrence of that same literal. Such an
  overlap requires the prefix to consume every distinct byte in the literal");
- a fixed-length prefix;
- a "disjoint class separator" in the prefix.

This study's G2 is the first two; the third is a refinement worth adopting if the
census shows customers (§5.4 Q3). The commit message's own cost: `(.*?,){13}z`
lost reverse-suffix. Our model reproduces the failure class without G2: 19 + 1
wrong single searches over 145,598 split-ambiguous checks (byte + utf8), e.g.
`(?:\B(?:b*|aa+)|(X*[^X]{1,3}?))a(?:[ab]a)` on `Xaaaba`: truth `(0,6)`, ungated
tactic `(1,4)`. Rare (≈1 in 7,000 checks) — which is exactly why it shipped in
rust, and why the gate cannot be argued away by a sample.

### 2.4 The gate, as data

```
G1  P is regular-faithful: no A_BREF, no linked call, no atomic/possessive
    (unless possessify discharged it), and no lookaround the reverse machine
    cannot evaluate (the DFA's own views are fine; general lookaround = the
    DFA's own [ENG-LOOK] boundary)
G2  fixed_width(P)  ∨  ¬(bytes(L) ⊆ alphabet(P))          [rust's first two]
G3  the landmark is admitted: ppm(L's scan byte) ≤ ppm(today's key) / F
G4  S reads no capture state of P: no backreference / group condition naming a
    group of P (conservatively, no ${...} either) [r2 E1]; where G4 fails the
    row hands LOWER(s*(j0)) to the attempt loop instead of CAND per occurrence
```

G2's "alphabet" is the set of bytes `P` can consume (a byte-set union over `P`'s
consuming nodes; `possessify.c`'s `first_of` is the wrong tool, it is a FIRST
set). Under `-e utf8` it is the byte alphabet of `P`'s lowered automaton, and
"fixed width" means fixed BYTE width (a fixed character width is not, K49/K50).

### 2.5 End, captures, views, find-all, utf8

- **End and captures.** Tactic (b) reads them off the forward anchored run at
  `s*` — exact by construction. Tactic (c) (resume forward from `j + |L|` over
  `S` only) gives the right END under G1 ∧ G2 when `S` holds no reference into
  `P` (`c_end`: 0 / 5,380 byte, 0 / 2,572 utf8), and the WRONG end without G2
  (361 / 7,880 and 142 / 3,796). Captures in `P` still need `P`'s priority parse,
  a forward run over `[s*, j)` only: bounded by the match, never a rescan of the
  subject.
- **Views at the walk's lower boundary.** The walk must READ `subject[lo − 1]`
  for `\b`/lookbehind/`(?m)^` at a start equal to `lo`, but ACCEPT no start below
  `lo`; and `^` (non-multiline) is position 0, not `lo`. Two mutations break
  exactly this: `lo0` (accept starts below `lo`: 1,531 wrong) and `slice` (walk a
  subject sliced at `lo`, losing context: 382 wrong). This is the same obligation
  `assertions_design.md` §3.8.3.1 records for the shipped reverse pass's
  termination boundary (the N1 defect).
- **`\G`** anchors at `search_from`: the pattern is start-anchored and takes one
  attempt; the tactic does not apply (decline on `start_anchor`).
- **startpos > 0** is covered by the model's every-startpos sweep.
- **find-all.** `R` is never nullable (`L` is non-empty), so the next search
  starts at the previous match's END. Restarting at `s + 1` reports overlapping
  matches (`restart_s1`: 329 wrong find-alls). No empty-match rule is needed.
- **utf8.** A landmark that is a whole character (or an ASCII byte) is found at
  character boundaries only (UTF-8 is self-synchronizing), and the walk accepts
  only character starts. A landmark that is a NON-INITIAL byte of a multibyte
  character (a "rarest byte" pick can choose one: `reqbyte_freq_pick.md` §3's
  0xC3 hazard in reverse) needs the hit rounded to its character start before the
  walk — the same round-up the handoff already emits (`PCREC_START0_ROUNDUP`,
  `emit_dfa.c:1123`). The utf8 model run (L ∈ {`é`, `Xé`, `éa`, …}) is clean with
  the gate: 0 / 137,692 and 0 / 23,976.
- **Lookaround in `P`.** The model evaluates it in full context and finds no
  failure attributable to it (0 / 23,257 byte and 0 / 16,095 utf8 checks where the
  split is clean); the
  decline in G1 is about whether the REVERSE MACHINE can evaluate it, which is
  pcrec's DFA boundary, not a soundness fact of the tactic.

### 2.6 Edge cases and the mutation table (D148 addendum 1's bar)

Instrument: `where_to_start/rinner_model.py`. libpcre2 **10.48** (Homebrew, this
Mac's local library; NOT the 10.46 reference — §6.2), via ctypes. Generated
`R = (?:P)L(?:S)` over alphabet `{a, b, X}` (+ `é` in utf8 mode): classes,
alternation, greedy/lazy/possessive quantifiers, captures, atomic groups, `\b`
`\B` `^` `$`, lookahead/lookbehind, `(?m)` on 20%, and backreferences in `S`.
12 subjects of length 0-9 per pattern over `{a, b, X, \n}` (+ `é`); every startpos
is a single search, plus one find-all per subject. Oracle: libpcre2's own
unanchored `pcre2_match`. The model uses libpcre2 only as its two COMPONENTS
(`starts(j)` by an end-pinned anchored run of `P` alone; the verify by an anchored
run of `R`), so the start-selection logic under test shares no source with the
oracle's search loop.

**Instrument defect found and fixed before any number was taken.** The first
`starts(j)` used `pcre2_dfa_match` (the all-paths matcher). It reports only the
LONGEST end for a trailing quantifier (`a*` on `aab`: `{2}`, not `{0,1,2}`), with
or without `PCRE2_NO_AUTO_POSSESS`, so `[^X]?` lost its empty path and the gated
tactic read 16 false mismatches. Replaced by an end pin, `(?:P)(?<=\A[\s\S]{j})`,
under the backtracking matcher.

Seed 1, byte mode, 6,000 patterns (5,884 compile; gate applies 2,769). Seed 2,
utf8, 4,000 (3,938; 1,998). `checks` = single searches; `/fa` = find-alls.

| variant | what it is | byte checks / wrong | byte /fa wrong | utf8 checks / wrong | utf8 /fa wrong |
|---|---|---|---|---|---|
| **tactic** | (b), gated | 192,079 / **0** | 33,228 / **0** | 137,692 / **0** | 23,976 / **0** |
| **lowerbound** | the handoff form: `s*` of the first non-empty occurrence as the unanchored scan's startpos | 192,079 / **0** | 0 | 137,692 / **0** | 0 |
| **fallback** | candidate loop, then hand the current `s*` to the unanchored scan | 192,079 / **0** | 0 | 137,692 / **0** | 0 |
| **rust_guard** | loop + rust's reverse-limit guard, falling back to the full search | 192,079 / **0** | 0 | 137,692 / **0** | 0 |
| **c_end** | (c): end from `j+\|L\|` over `S` | 5,380 / **0** | — | 2,572 / **0** | — |
| gate_off [split-ambiguous] | (b) without G2 | 92,510 / 19 | 6 | 53,088 / 1 | 1 |
| gate_off [atomic, clean split] | real-semantics walk | 29,812 / 0 | 0 | 23,494 / 0 | 0 |
| erase_atomic | atomic `P`, clean split, ERASED walk (what a DFA builds) | 29,812 / **11** | 4 | 23,494 / **6** | 3 |
| rust_guard ungated | the guard is not a correctness device | 92,510 / 17 | 5 | 53,088 / 1 | 1 |
| c_end ungated | (c) without G2 | 7,880 / 361 | — | 3,796 / 142 | — |
| M max_start | take the LARGEST accepting start | 636 | 237 | 197 | 65 |
| M lo0 | accept starts below `search_from` | 1,531 | 51 | 680 | 17 |
| M slice | walk a subject sliced at `search_from` (context lost) | 382 | 15 | 212 | 15 |
| M noverify | trust the landmark, skip the forward run | 11,811 | 3,440 | 6,967 | 1,988 |
| M skipL | next occurrence at `j+\|L\|` (misses self-overlap) | 37 | 15 | 17 | 4 |
| M restart_s1 | find-all restarts at `s+1` | 0 | 329 | 0 | 105 |

`--selftest` asserts the bold rows are 0, every M row is detected, and the
ungated tactic is wrong at least once (the gate is shown necessary). Both runs:
PASS. Transcripts: `rinner_model_byte.txt`, `rinner_model_utf8.txt`.

### 2.7 The quadratic hazard

Two separate costs, only one of which is new:

- **Reverse walks.** Under G2's literal arm the walks are disjoint: a walk from
  `j'` reads only a suffix of some string `P` matches, which cannot contain a
  whole earlier occurrence, so it stops within `|L|` of the previous occurrence.
  Total reverse work O(n + occurrences·|L|). Under G2's fixed-width arm each walk
  is ≤ w bytes. rust still keeps a guard (`try_search_half_rev_limited(...,
  min_match_start)`, quoted in [RArevinner]) because its three arms do not all
  have this property; pcrec's two do.
- **Forward verifies.** A failed anchored verify can read far past the next
  occurrence (`S = .*Z` with no `Z`): the loop re-reads the same bytes per
  occurrence — O(occurrences·n). rust's second guard catches it:
  `if litmatch.start < min_pre_start { return Err(RetryError::Quadratic(..)) }`,
  `min_pre_start` being where the last forward verify stopped, and the meta
  engine retries with the core engine from the start. **pcrec should not start
  over.** The measured `fallback` row is the better give-up: hand the current
  `s*` to the ordinary unanchored scan as its startpos (0 wrong, §2.6). That is
  the K82 handoff's own startpos contract (`litscan_k82h.md` §1.2, Claims 1-3)
  with an exact lower bound instead of `c − K`, and it is linear.
- **On the VM route** each verify is an anchored attempt at a position the plain
  attempt loop would also have tried; the tactic tries a SUBSET of the loop's
  positions, in the same order, stopping at the same first success. VM work is
  never larger than today's; only the reverse walks are added.

---

## 3. (C) Q3: the prefilter form

**Yes.** Tactic (b)'s output is a candidate start; any anchored verifier consumes
it. Concretely:

- **P must be backref-free and regular-faithful (G1); S may hold anything** —
  but **[r2 E1]** where `S` references a group of `P` (G4 fails, which is this
  whole VM population's shape) the walk hands `LOWER(s*(j₀))` to the attempt loop,
  never a candidate per occurrence (§2.2 step 1's correction). The
  reverse machine is built from `P`'s sub-tree alone, so `S`'s backreferences,
  calls, atomics and lookarounds never enter it. This is the decisive difference
  from the hybrid prefilter, which needs the WHOLE pattern's DFA and is therefore
  declined for every backreference and linked call (`select_engine.c:579-611`'s
  measured reasons: the erasure is not a superset under assertions/atomics, and
  its span is wrong where it is). Those are today's K66 population: VM-only, no
  DFA front, the presence check their only linear proof.
- **Census of that population (§4):** VM-only unanchored, best landmark behind
  the start with an exact reverse walk available: **5 corpus / 3 bench**
  (`capability/dup-param-detect` `\b(\w+)=[^&]*&(?:[^&]*&)*\1=`, `syntax/bak-1`
  `(\w+) \1`, `syntax/bak-g-rel`), all ≥2× rarer than what the START-SET hat
  scans; 8 more corpus with a FIXED offset (offset-k for the VM, `[OPT-VMSEED]`
  stage 4's run seed). 18 corpus VM-only artifacts have NO candidate scan at all
  today, and none of them has a usable landmark (each landmark sits behind a
  backreference or call in `P`).
  K66's own witness `(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` qualifies with `L = ~#~#~#~#`:
  `[a-z]` cannot consume `~`, and the `\1` is in `S`.
- **Bounded-width P collapses to existing rows.** `P` of width `[k, k]` IS
  offset-k (`offset-set`'s arithmetic, no machine); `[a, b]` finite is a WINDOW
  (`[OPT-VMSEED]`'s seed: attempts at `hit − b … hit − a`) or a LOWER BOUND
  (`hit − b`, the K82 handoff). The reverse walk adds information only when `b`
  is unbounded, or when the window is wide and dense. The census: 59 corpus /
  2 bench DFA bests are bounded-not-fixed (47 / 1 at ≥2×), and 36 of the 88 corpus
  DFA ≥2× fixed/bounded bests are already on an offset row or the handoff.
- **The give-up surface (K65's concern).** On the VM route the tactic skips
  attempts the plain loop would run, so a call that gave up on its step budget
  may now ANSWER; never the reverse (it runs a subset of the attempts in the same
  order, §2.7). That is D148 Q6's one-way allowance word for word ("a give-up may
  turn into the unbounded answer, never the reverse"), and it is the opposite of
  the handoff's Q10 posture ("the deny flag never moves the give-up surface"),
  which was ruled for a LOWER-BOUND mapping on a count-collapsed prefilter. The
  tactic's deny flag WOULD move the give-up surface, one-way. Needs a ruling
  (§5.4 Q4). The no-match proof is unaffected: no occurrence of `L` → no match,
  O(n), and it is the same fact K65/K66 already test.
- **Count-collapsed hybrid.** Not a host: its language is a superset, so a
  reverse walk over a collapsed `P` would be G1's erasure failure. The tactic
  reads `P` exact or not at all.

---

## 4. (D) The census

Instrument: `where_to_start/census.py`. Population and facts reader imported from
the [ARTREV] generalizer (`docs/dev/optloop/artrev/gen/census.py`): 345 bench
(read-only, pcrec-bench `eb634d9d`) + 3,704 corpus patterns (deduplicated), one
`--emit-facts` call each, this lane's build of `6816f839`'s `src/`. Our own reader
flattens the top-level concatenation and lists landmarks; it parses **274 / 321
bench (85%)** and **2,448 / 3,333 corpus (73%)** of the compiled patterns
(unparsed by reason in `summary.txt`: unsupported group kinds 323, escapes 145,
`(?x)`/`\Q`/conditionals 125, `\K` 78, ...). Unparsed patterns are NOT counted in
any population below; VM-only patterns parse worst (274 of 364 corpus).

**Controls (K35, all committed):**
- **C1** reader controls: 11 hand-classified patterns, 0 failed (`selftest.txt`).
- **C2** necessity against pcrec's own `req_set` (`src/facts/req.c`, no shared
  code with the reader): 99 bench / 1,256 corpus patterns, 331 / 2,258 bytes,
  **0 violations**.
- **C3** fixed offsets against pcrec's `kset_walk`: agree 5 / 92, disagree **0 /
  0**, walk does not reach 2 / 20.

Unanchored patterns the reader parses, by route; the best landmark = the rarest
scan byte under the shipped prior (`tests/findings/default_ppm.tsv`). "≥2×" is
K1's admission: ≥2× rarer than what the artifact scans today (D149: UNMEASURED
default, 1× and 8× in `summary.txt`).

| | bench DFA | bench hybrid | bench VM-only | corpus DFA | corpus hybrid | corpus VM-only |
|---|---|---|---|---|---|---|
| unanchored, parsed | 201 | 33 | 16 | 1,172 | 770 | 154 |
| no landmark on the spine | 95 | 15 | 5 | 517 | 200 | 90 |
| top-level alternation | 12 | 0 | 0 | 97 | 21 | 1 |
| best at the START | 77 | 14 | 8 | 377 | 289 | 24 |
| best NOT at start | **17** | **4** | **3** | **181** | **260** | **39** |
| … of which ≥2× rarer | 12 | 1 | 3 | 133 | 203 | 38 |
| ≥2× by mapping: fixed | 5 | 0 | 0 | 41 | 56 | 8 |
| bounded | 1 | 1 | 0 | 47 | 88 | 0 |
| **exact-rev (new)** | **2** | 0 | **3** | **21** | **23** | **4** |
| presence only | 4 | 0 | 0 | 24 | 36 | 26 |
| fixed/bounded already on an offset row or handoff | 5 of 6 | 0 of 1 | — | 36 of 88 | 58 of 144 | 0 of 8 |

Landmark kind, NOT-at-start, all routes: bench 19 single byte / 5 run, corpus
420 / 60 (`best_kind` in `rows.tsv.gz`).

Reading it:

- **Q1's population is real and mostly ALREADY SERVED by bounded mappings.** On
  the DFA route 181 corpus bests sit behind the start, and the fixed/bounded half
  of them (88 at ≥2×) is the territory of `offset-set` and the handoff — 36 are
  already there, the rest are candidates for the existing rows' admission rules,
  not for a new mechanism.
- **The exact reverse walk's own population is small and specific:** 21 + 23 + 4
  corpus, 2 + 0 + 3 bench at ≥2× (77 corpus / 8 bench at any ratio). The bench
  members: `loglines/stack-frame` (A01, the −72% cell), `syntax/qnt-plus`, and
  the three VM backref patterns.
- **Presence-only (26 VM-only corpus at ≥2×)** is the population no landmark
  tactic can serve: the landmark sits behind a backreference or call in `P`, or
  `P` can consume the landmark (`\S+@\S+`).
- **Agreement with ARTREV K1.** K1 (DFA, landmark not in the start set, ≥2×)
  reads 17 bench / 90 corpus; this census's DFA "not at start, ≥2×" reads 12 /
  133. They differ in definition (K1 asks start-set membership; this asks the
  spine position and requires the reader to parse) and should not be added.

---

## 5. (E) Recommendation

### 5.1 The general strategy

Not a planner. **The existing candidate table, one mapping richer.** The answer to
"where should a search start" is already a first-match table in information
order (`dfa_pfs[]` + `req_uses[]`); what is missing is the EXACT mapping for a
landmark behind an unbounded prefix. Add it as one row family with:

- the INNER-LANDMARK SPLIT as a core fact (`src/facts/`, a top-level-concat walk;
  rust's `top_concat`/`flatten` is the precedent);
- the gate G1 ∧ G2 ∧ G3 as the row's predicate, each conjunct with a sabotage row
  and a witness from §2.6's table;
- a PREFIX reverse machine (`pcrec_build_nfa` over `P`'s sub-tree, reverse,
  exact; the existing minimizer and emitter), seeded at the hit;
- two hats: the DFA hat runs the anchored forward machine from `s*` (the shipped
  `anchored_match_unwrapped.md` entry); the VM hat runs one anchored attempt —
  the VM's FIRST prefilter for backref/linked-call patterns;
- a give-up that is a HANDOFF (§2.7's `fallback`): on a tripped forward-verify
  guard, the current `s*` becomes the unanchored scan's startpos. One more row in
  `req_uses[]`'s sense, not a separate fallback mechanism.

Tactic (c) (resume forward over `S` only) is a refinement of the DFA hat's
verify, sound under the same gate when `S` has no reference into `P`; it saves
the re-scan of `P` on a verify. Not worth a separate row until the DFA hat is
measured with and without it.

### 5.2 What to measure next (D77 triggers)

1. **The VM hat on the backref population** (the row's own trigger, and the
   largest expected effect): a hand twin of `capability/dup-param-detect` —
   memchr(`=`), walk back over `\w` to the `\b`, one anchored attempt — against
   the shipped artifact on the bench's subjects. That cell is already a losing
   VM cell in the gap reports. Answer-check over the model's alphabet first.
2. **A01 L1 is the DFA hat's measurement and is DONE** (−72.2%, Linux,
   `report_pilot.md` §5 #2); the residual question is the candidate loop vs the
   handoff-only form on the same cell (the twin is the loop; the handoff-only
   form changes only each call's first scan).
3. **The census at the 10.46 reference** is not needed (compile-side), but the
   model's §2.6 table should be re-run once against 10.46 over ssh (light: ~20 s
   of CPU) before a build — the Mac's 10.48 is not the reference.
4. **F (the ≥2× admission)** is unmeasured (D149). Its first measurement is the
   cell pair in item 1 at two subject densities.

### 5.3 Rows this merges, retires or re-scopes

- **[ENG-TACTICS]**: (b) and (c) become this note's row family; the "tactic
  census" its FIRST STEP asks for is §4 (VM-only: 4 exact-rev at ≥2× corpus, 3
  bench; 26 presence-only). (a) SEED is the WINDOW mapping and stays
  `[OPT-VMSEED]` stage 4. Recommend re-scoping the row to "the reverse-walk
  candidate row" and keeping it under [OPTLOOP] candidates, trigger §5.2 item 1.
  Its "superset DFA with `\N` relaxed" question is answered NO for the prefilter
  role (it is `select_engine.c:579-611`'s measured erasure failure) and made moot
  for this population: the prefix machine never sees `S`.
- **[ARTREV] I1** (generalize.md) is this row's DFA instance: MERGE into the
  re-scoped [ENG-TACTICS]; it stays a [MEMFN] request for the scan site.
- **[OPT-VMSEED] stage 4** (run seed) is the WINDOW mapping; unchanged, but its
  population is §4's VM-only "fixed" 8 corpus.
- **[OPT-REVEND]** is the same reverse machine seeded at the subject end
  (whole pattern rather than prefix): note the shared builder; no merge — its
  trigger (an `anc-tail` bench family) is independent.
- **K82 handoff / `req_uses[]`**: gains one row (`handoff-rev`) only if the
  candidate loop is built; nothing retires.
- **[OPT-A]**: a multi-literal LANDMARK (per-alternative streams) is the same
  table's landmark column widened from one literal to a set; rust's
  `has_no_earlier_match` declines multi-literal sets except by the class
  separator, so [OPT-A] keeps its own soundness argument.
- Retires nothing.

### 5.4 Open questions for Frank (each with a recommendation)

- **Q1. Re-scope [ENG-TACTICS] to "the reverse-walk candidate row" (b)+(c),
  with (a) left to [OPT-VMSEED] stage 4, and merge [ARTREV] I1 into it?**
  Recommend YES — one row, two hats (D124), the census in §4 as its first step.
- **Q2. Move it out of BOONIES?** Recommend: NOT YET. File the §5.2 item-1 hand
  twin as its D77 trigger; schedule only if the twin wins the VM cell. A01's
  −72% alone is one DFA cell on a 17-artifact population.
- **Q3. G2's third arm (rust's disjoint class separator)?** Recommend NO until
  §4's presence-only population is re-counted under it; the first two arms carry
  every member counted here.
- **Q4. The give-up surface.** The tactic's deny flag moves the VM give-up
  surface one-way (a give-up may become an answer). Recommend applying D148 Q6's
  ruled sentence unchanged, and NOT the handoff's Q10 posture (which was ruled
  for a superset prefilter, where the answer could move).
- **Q5. One table or two?** `dfa_pfs[]` (next candidate) and `req_uses[]` (first
  scan start) both answer "where can the scan be", and §1.3 item 2 shows the
  split is no longer forced. Recommend: keep two tables until the `handoff-rev`
  row exists; fold them in the `dfa_pfs[]` → `cand_rows[]` rename D148 Q2
  already schedules, as a no-mover commit.
- **Q6. Admission F.** Recommend reporting 1×/2×/8× and building with the
  K1/I1 value 2× labelled UNMEASURED (D149) until §5.2 item 4 measures it.

---

## 6. Standing questions (docs/design/CLAUDE.md)

### 6.1 The measurement regime — RELEVANT, briefly

This note takes no timing. The one performance number it cites (A01 −72.2%) is
ARTREV's, measured on Linux in throughput regime, fail-dominated subjects
(`report_pilot.md` §3). The rarity numbers are the shipped static prior
(`default_ppm.tsv`), a corpus-independent table; a different prior moves G3's
admissions, never G1/G2's soundness.

### 6.2 The independent control — RELEVANT

- The soundness model's ORACLE is libpcre2's own unanchored search; the model
  uses libpcre2 only as two components, so the tactic's start selection — the
  thing under test — is the model's own code. Its teeth: 6 mutations, every one
  detected, and the ungated tactic shown wrong. Its blind spots: the alphabet
  (`{a, b, X, \n}`, + `é`); single-literal `L` only; subjects ≤ 9 characters;
  10.48 not 10.46 (U13: they are known to differ in places; none of the
  constructs here is among them, unverified).
- The census's populations are counted by pcrec's own `--emit-facts`; its
  landmark classes by a reader that shares no code with `src/facts/`, checked
  against `req_set` (C2) and `kset_walk` (C3), both at 0 disagreements. The
  reader's coverage (85% / 73%) is reported, and unparsed rows are excluded, not
  guessed.

### 6.3 What moves when data is regenerated — RELEVANT, nothing yet

Nothing is emitted. If built: the new row moves emitted bytes on its movers (an
abi event, readers found by grep, D76/D94), adds a stamp value to
`RX_DFA_PREFILTER` / `RX_VM_START_SCAN` (D80 spec hunk), and G3 makes the movers
depend on the prior (a regenerated `default_ppm.tsv` would move admissions — the
same exposure [OPT-REQBYTE]'s pick already has).

## 7. The lenses

- **specific vs general:** general — one mapping added to the table every start
  mechanism is already a row of; K66's witness and A01 are two instances.
- **core vs derived:** the split is a core fact; the row is derived.
- **applicable vs assumption-changing:** applicable; G1 keeps every construct
  that would change an assumption (backrefs, atomics) out of the machine.
- **fits the architecture vs refactor:** fits (D124: one question, engine hats).
  The prefix reverse machine reuses `pcrec_build_nfa` on a sub-tree.
- **shared question / engine hat (D124):** yes — the same row serves the DFA and
  the VM; the VM hat is the larger customer.

---

## §7 trigger reading (2026-10-06)

Lane `revtwin`, D151 items 2 and "owed before any build". Measurement only; evidence in `where_to_start/model_1046.txt`
and `where_to_start/twin_dup_param/` (README there).

**1. The soundness model against the 10.46 reference (ubuntubudu, libpcre2 10.46-1build1, x86_64).** Same seeds and
counts as the note's run (seed 1 x 6,000 byte; seed 2 x 4,000 `--utf8`), plus `--selftest`. All 64 variant rows of both
transcripts are IDENTICAL to the 10.48 transcripts in checks and mismatches (the per-row diff is empty; the same
witnesses first). Gated wrong answers: **0** (tactic, lowerbound, rust_guard, fallback and every `/findall`: 0 of
192,079 + 33,228 byte and 137,692 + 23,976 utf8). Ungated wrong: byte `gate_off[split-ambiguous]` 19 (+6 find-all),
`gate_off[P-atomic+split-ambiguous]` 5 (+1); utf8 `gate_off[split-ambiguous]` 1 (+1), `gate_off[P-lookaround+split-ambiguous]` 5 (+1);
`erase_atomic` 11 / 6 (+4 / +3). Mutations (byte / utf8, single searches, none missed): `max_start` 636 / 197,
`lo0` 1,531 / 680, `slice` 382 / 212, `noverify` 11,811 / 6,967, `skipL` 37 / 17 (find-all arms `restart_s1` 329 / 105 as
well); `--selftest: PASS`. The 10.46 and 10.48 counts agree row for row, so the note's §2.6 table stands on the
reference.

**2. The D77 trigger twin: NOT MET.** The hand twin of `capability/dup-param-detect` (memchr `=`, walk back over `\w`,
one anchored VM attempt, find-all restart per spec) is answer-identical to the shipped artifact (hardened identity, plain
and ASan+UBSan, 14,927 cases of which 1,475 match; every give-up repair equals libpcre2) and, timed on ubuntubudu (11
interleaved rounds, null twin and orig2 NOISE everywhere, 7-pad layout control):

- the bench's **throughput cell** (t-64k/256k/1m) reads **NOISE**: 0.0371 vs 0.0370 ns/B, IQR 0.0008/0.0011, null
  deviation 0.0001. The subjects hold no `&` and no `=`; since [OPT-REQBYTE]/[OPT-FREQPICK] the shipped artifact answers
  them with one `memchr('&')` at the memchr floor, so there is nothing for a better start to save. The cycle-1 figure
  that made this cell the largest VM loss (576x, `cycle1_analysis.md:97`) predates those batches;
- the bench's **search_short cell** (75 subjects, regenerated read-only, hashes verified) reads **NOISE**: 1.8385 vs
  1.8819 ns/B (the twin 2.4% slower, inside the 0.0778 IQR); only 2 of 75 subjects pass the artifact's prechecks;
- where the artifact does run its attempt loop the twin WINS and the layout control confirms it: `waf-benign` +64%
  (21.49 -> 7.69 ns/B) and the synthetic sparse variant +76% (7.57 -> 1.79); the synthetic dense variant (a match every
  4 KiB) is NOISE (+1.9%). The bench has no dense/sparse rows for this pattern.

D151's trigger is "the twin wins the VM cell". It does not: the cell is at the floor. Q2's condition therefore is not met
and [ENG-TACTICS] stays in BOONIES. What the twin does show is the row's real customer shape: a subject that carries the
required bytes and no match (or a sparse one) costs the shipped VM an attempt at every start-set byte, and the walk
removes that. What would re-open the question is a bench subject with `&` and `=` and no match for this pattern (the
bench's to add; a pcrec-side hand-built one is the sparse variant here), or the K65/K66-population cells that do reach
the attempt loop, not a better twin of this one.
