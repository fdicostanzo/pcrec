# One instruction stream, grown from today (lane stream-today, round 1)

Author: lane `stream-today` (opus), 2026-11-01. Read-only on the repository (main `c967685c9`,
plus `lane/p1build` for the landmark walk). Runs: `build/pcrec` on the ten worked patterns, outputs
in `runs/` beside this file. No build, no suite.

**The claim in one paragraph.** pcrec already has the two halves of one instruction stream and
keeps them apart. The **outer half** is the start table's handoff graph: `cand_nodes[]` with its
typed hands (`CT_LOWER`, `CT_START`, `CT_ENDSET`, ...), `src/gen/emit_dfa.c:9789-9930`. The
**inner half** is the VM's typed record body (D182, `vm_kind_rows[]`, `src/gen/vm_stmt.c:682`).
Between and inside them sit three ad-hoc families of DFA pieces: the hybrid's prefilter pair,
the VM's own deterministic rungs, and the landmark walk's four machines. Each is wired by its own
protocol. The end state puts all of them in **one program of typed instructions**, in three
families:

- **M**: backtracking control, today's VM kinds.
- **D**: deterministic segments. Each is a DFA run in one direction with a declared EXIT
  PROTOCOL.
- **K**: kit leaves, keyed by operation and never by engine.

The program has **one seam type**, today's hands extended down into the match body, and **one
soundness rule with four strengths** (commit, enumerate, guided, bound). Each strength is applied
per REGION, not per artifact. "DFA artifact" and "VM artifact" become two degenerate streams. All
of a DFA artifact's instructions are D and K; a VM artifact without prefilter is all M and K.
Today's hybrid is one D segment ahead of an M body.

---

## 0. What today's artifact ALREADY mixes (inventory, file:line on main unless noted)

### 0.1 Mixing sites: one artifact, more than one kind

| # | site | where | kinds mixed | what crosses the seam |
|---|---|---|---|---|
| X1 | VM hybrid's embedded prefilter: the capture-erased forward+reverse DFA pair, emitted by **the DFA emitter** under a private name | `emit_vm.c:13005-13033` (`PCREC_ENTRY_PREFILTER` via `emit_comb.c:569` locate-then-finish); rule H3 `emit_vm.c:10366-10441` | D ahead of M | a window `[s,e)`. Start = LOWER always. End = SPAN only where the language is exact (`v->mrl_win = pcrec_cand_lang_exact`, `emit_vm.c:10442`); else the ceiling is dropped. Patterns 3, 4, 6, 8 take this today. |
| X2 | VM span-loop cursor rung: a class run consumed by a kit SKIP with retreat-by-stride as the resume | `emit_vm.c:4890` `vm_cursor_rep`, `4839` `vm_emit_span_scan` → `DELEG_VMSPAN`/`DELEG_VMSTRIDE` (`4844`); analysis `vm_det_seq` `1883`, `vm_cursor_fits` `2042` | K inside M; a one-state DFA with an ENUMERATE exit | cursor position; retreat positions are iteration boundaries (D44.1); captures DERIVED from the cursor (`vm_cap_offsets` `1971`) |
| X3 | VM reverse-deterministic rung (`revdet`): backward walk of a quantifier body's REVERSED AST, to recover the previous iteration boundary on retreat | `src/opt/revdet.c:1-50` (U1/U2 forward+reverse unique iteration), `emit_vm.c:5705` `vm_revdet_rep`, `5521` `vm_rev_emit` | a reverse deterministic walk inside M | a boundary position |
| X4 | VM alternation island (ENG-ISL): a byte trie over literal branches, with each node's accept chain in ORIGINAL BRANCH ORDER | `emit_vm.c:4298` `vm_isl_build`, `4582` `vm_isl_emit`, `4503` `vm_isl_cands` | a DFA (trie) with an ordered-exit list inside M | the ordered candidate ends (preference order, not position order) |
| X5 | VM literal-run compares | `emit_vm.c:4538` `vm_run_site` → `DELEG_VMRUN` | K inside M | bool |
| X6 | VM backreference compare | `emit_vm.c:8744` `vm_bref`; the kit site `DELEG_N7` `memfn_sites.c:881`, `emit_dfa.c:3571` | K inside M | a position or a miss |
| X7 | DFA scan edges: a scan-shaped state chain runs as a kit SKIP | analysis `src/opt/scanedge.c:1-50`; emission `emit_dfa.c:12571-12587` (`DELEG_EDGE`) | K inside D | position |
| X8 | DFA stay/skip states | `emit_dfa.c:9148` `stay_advance`, `9171`/`9202` fwd/rev skip → `DELEG_STAY` (`9187`, `9216`) | K inside D, both directions | position |
| X9 | Start search (NEXT rows): kit FIND/memchr/byte-class/offset-set ahead of the DFA, and the **VM's** start search, emitted by `emit_dfa.c` | `cand_rows[]` NEXT `emit_dfa.c:10327-10426`; VM hat `pf_vm_start_applies` `8026`, `pcrec_emit_vm_start_seek` `8183` | K ahead of D or M | `CT_CAND` / `CT_LOWER` |
| X10 | Pre-checks and handoff (PRESENCE, FIRST): the all-present kit site, then re-entry at `c-K` | `emit_dfa.c:1531` `req_site_define` (`DELEG_PRE`), `7733` `pf_emit_handoff`, `7787` `pcrec_emit_req_attempt_reentry`; the VM reuses "the same text" (`emit_vm.c:13259`, `13502`) | K ahead of D or M | `CT_HIT` / `CT_LOWER` |
| X11 | LOCATE→RECOVER→FINISH: forward DFA to the end, then the REVERSE DFA to the start (`reverse-pass`), or `rev-end` from the subject end, or `cover` (proof covers everything) | rows `emit_dfa.c:10166` empty, `10186` rev-end, `10208` cover, `10217` composite; RECOVER `10542-10561`; FINISH `10589-10620`; emitters `emit_rev_end` `13900`, `emit_cover` `13860`, `unanch_scan` `13167` | D→D(rev)→D or M | `SPAN`/`ENDSET`/`WINDOW`/`EXISTS` (`CAND_HAND_*`, `emit_dfa.c:9805-9819`) |
| X12 | **Landmark walk** (lane/p1build): kit FIND of L → reverse DFA ML of P·L seeded at the hit, carrying scan edges → reach guard → one anchored DFA run → relocate to the composite | `lane/p1build:src/gen/lmwalk.c:1-24` (the admission table `lmwalk_conj[]`); `lane/p1build:src/gen/emit_dfa.c:14382-14514` `emit_landmark_walk` | K→D(rev, with K inside)→D(fwd), plus a controller loop, glued by raw `pcrec_sb_puts` | `AT s*` to `verify-at`, `LOWER s*` to `search-from`, `NOMATCH`. Row 1 `finisher-dfa` (`lmwalk.c` `lc_finisher`) **refuses a VM finisher** |
| X13 | Compound controller: parts compiled separately, composed by `first-nonzero` | `src/core/compound.c:248-265` (`split_conj`, `compound_rows`); entries `src/gen/entries.c:255`, `emit_comb.c:569-582`; part layout `part_layout.c:204/313/357` | whole artifact over whole artifact | return codes and one captures array (D163 add. 3) |
| X14 | Kit site KIND keyed by ENGINE CONTEXT | `emit_dfa.c:1417-1425` (`MF_SK_DFA_HAT`, `HYB_PF`, `VM_ATTEMPT`, `DFA_ATTEMPT`, `DFA_SCAN`) | the engine leaks into the kit's facts | n/a |

### 0.2 Parallel mechanisms and special cases the end state DELETES

Each row: one question today answers more than once. In the end state it is one instruction kind
or one admission row.

| question | today's mechanisms (each its own analysis, emitter and stamp) | end state |
|---|---|---|
| skip a class run | DFA `EDGE` (scanedge.c + `emit_dfa.c:12571`); DFA `STAY` fwd and rev (`9148-9217`); VM `VMSPAN`; VM `VMSTRIDE` (`emit_vm.c:4844`). Two analyses find the shape: `scanedge.c` on the DFA graph, `vm_det_seq`/`vm_cursor_fits` on the AST. | ONE kit kind `SKIP(set, dir, stride)`. Its shape is found once, on the segment's automaton. |
| walk backwards to a boundary | `rdfa` reverse-pass (RECOVER); `rev-end` (`13693`/`13752`, one seed and tagged); `lmdfa` landmark walk; VM `revdet` backwards walk over a reversed AST (`revdet.c`); `end-minus-width` (`10548`); `pinned` (`10542`) | ONE `D(rev)` segment kind seeded at a known point (the subject end, a match end, a landmark, an iteration boundary). D161 add. 17 already names this as "the scaffolding". The fixed-width rows become admission rows of that one kind. |
| deterministic dispatch over alternatives | the DFA's subset construction; the VM's ENG-ISL trie (`emit_vm.c:4298-4745`) with its own size rule and limits rows (`VM_ISL_MIN_BRANCHES*`) | ONE `D` segment with an `ENUM` exit ordered by branch priority. The trie is the special case "literal branches, no loops". |
| literal compare at a point | VM `VMRUN`; DFA states for a literal; the `cover` proof; OFS verify | `K VERIFY(run)`, or no instruction at all where the seam's proof already covers it |
| "is the language exact at this seam?" | H3's three flat conjuncts (atomic, lookaround, count-collapse; `emit_vm.c:10366-10441`); `pcrec_cand_lang_exact`; lmwalk row `g1` (erasure, `\G`, `\K`); compound A2/A4 | ONE typing rule on the seam: an edge leaving a SUPERSET segment cannot carry `SPAN`/`AT`. Erasures are recorded on the segment, not re-derived at each consumer. |
| "may this region be committed?" | possessify's `pcrec_uniq_iteration` (`possessify.c:1154`); revdet's U1+U2; the cursor rung's determinism plus fixed length; lmwalk `exclusion`; compound client 7's "unique end" (D163 add. 3) | ONE admission, R1 below. These become its rows. |
| what engine, for the whole pattern | `analyses[]` engine mask (`select_engine.c:417`: captures, registry, dfa_overflow); `--engine=`; per-artifact `RX_ENGINE` | per REGION. The artifact's "engine" is a derived summary: `dfa` iff the stream has no M instruction. |
| locate→finish glue | `emit_comb.c` locate-then-finish; the hybrid's prefilter call; `emit_landmark_walk`'s hand-written loop (raw text, four `DfaForm`s, `p1build:14420-14512`); `unanch_scan`; RETRY rows re-seeding the VM (`10449-10491`) | the C family (controller instructions) over typed hands. `cand_nodes[]` is already its graph. |
| emission discipline | VM: typed records only (D182). DFA: raw `StrBuf` text (16k lines). Controller: raw text. | records everywhere. One kind table, one renderer per kind. |
| stamps | `RX_ENGINE`, `_DFA_*` "iff the artifact contains a DFA scan" (`emit_vm.c:11399-11421`), `_VM_PREFILTER`, `_DFA_SCAN_EDGE` folded over member machines (`emit_dfa.c:4946-5010`) | per-segment facts, folded by one walk over the stream |

What is NOT a parallel mechanism and stays: the kit's own internals (D146), the encoding seam
(src/enc), the class kit (clskit), and the measurement and pricing tables.

---

## 1. The end state, high level

### 1.1 The program

An artifact is ONE program: a graph of typed instructions, built as records and rendered by one
renderer per kind. D182 is applied to the whole artifact, not only to the VM body. The program
has two altitudes, and both use the same vocabulary:

- **the controller**: what today's `cand_rows[]` slots decide (LOCATE, PRESENCE, FIRST, NEXT,
  RECOVER, RETRY, BOUND, FINISH), plus the compound combinators;
- **the body**: what today's VM program and DFA machines do.

A controller instruction may contain a body. A body instruction may contain a controller: a
lookaround body, a callout, a recursion call.

### 1.2 Instruction families (each kind is one row in one kind table)

| family | kinds | renders as | backtracking role |
|---|---|---|---|
| **M**: match control | `LABEL GOTO BRANCH GUARD PUSH FAIL ACCEPT SET SNAPSHOT RESTORE CUT CALL RETURN STEP WORK CONSUME BREF CALLOUT LOOK-ENTER LOOK-EXIT` (today's 29 `VK_*` minus the SPAN/SEEK family, which moves to D) | today's VM text | the only frames, and the one backtracker (the fail label) |
| **D**: deterministic segment | `DSEG(machine, dir ∈ {fwd, rev}, entry ∈ {AT, LOWER-unanchored}, exit ∈ {COMMIT, ENUM, VIAB, BOUND})`. Inside: states, transitions (table or switch, D13), and **edges that are K instructions** (a scan-shaped state renders as `SKIP`). | today's DFA text; the cursor rung and the trie as small instances | `COMMIT`/`BOUND`/`VIAB` leave no resume point. `ENUM` leaves exactly ONE resume point, whose resume yields the next exit in preference order. |
| **K**: kit leaf | `FIND(spans/sets → candidate stream)`, `SKIP(set, dir, stride)`, `VERIFY(run)`, `MISMATCH(ref)`, `PRESENT(terms)` | the kit's text (D146), opaque, with **declared effects** (D182 ruling (c)(1): reads, writes, cursor, may-transfer) | none of their own |
| **C**: controller | `LOOP-CANDIDATES(gen, body)`, `RELOCATE(lower)`, `FIRST-NONZERO(parts)`, `ENTRY(role)`, `RETURN-TO-CALLER` | today's entry and search loops | none |

The kit is keyed by OPERATION. The engine-context column (`MF_SK_*`, `emit_dfa.c:1417`) is
deleted. A kit site's facts come from the seam it sits on: the proof, the bounds, and whether it
runs in a loop (D91's budget).

### 1.3 The seam contract

Every edge between two instructions carries a **hand**: a compile-time TYPE plus run-time
VALUES. The type has four components.

1. **Position** (one of a closed set, generalizing `CAND_HAND_*`): `AT p` (a definite position);
   `LOWER p` / `UPPER p` (bounds on the match start); `CAND p` (the next position that can start
   a match); `SPAN (s,e)` (the match); `ENDSET` (more than one end, ordered by preference or by
   position, stated); `NOMATCH`. One rule is the **typing rule**: a SUPERSET segment (any erasure:
   atomic made transparent, lookaround made ε, a count collapsed, a backref replaced by its
   referent's language) may emit only `LOWER`/`UPPER`/`CAND`/`NOMATCH`. That is H1/H2/H3 in one
   sentence. H3's three flat conjuncts become the segment's erasure record, read at the edge.
2. **Captures**: the ONE slot array (D163 add. 3), in the parent's numbering. Every instruction
   declares the slots it reads and writes. A `DSEG` writes only DERIVED slots:
   - an offset from its entry or exit (U1 fixed margin; D44.1 cursor-derived);
   - later, a determinate tag per state (a tagged DFA where each state fixes the tag; hole H1).
3. **Proof**: per-offset proven byte sets around the position, `consumable_len`, and context
   spans before the origin (D161 add. 16; today `src/gen/known.c`). It is compile-time only and
   travels with the edge. A K `FIND` hands its proof forward, so a following `VERIFY` of
   proven bytes is deleted (today's `cover`).
4. **Resume depth**: whether instructions above this edge may hold resume points. An edge with
   depth 0 below a COMMIT is a **cut**: nothing before it can be re-entered. This is what lets a
   later `DSEG` run without the VM's run state, and what lets a stream that never pushes keep
   today's frameless shape (`emit_vm.c:14-26`).

**Backtracking re-entry is uniform.** There is one backtracker, the fail label: today's single
indirect jump. A `DSEG ENUM` participates by pushing one ordinary resume label, which advances
its enumerator and re-takes the continuation. This is exactly today's cursor rung ("push L8:
shorter run is the resume", `runs/p8.ir`) and the trie's candidate chain. Nothing else
re-enters a segment.

### 1.4 Who decides segmentation, and how

One pass, the **segmenter**, runs after today's optimization passes (possessify, revdet, MRL,
facts). It reads the prioritized tree and writes the stream. It is two first-match tables, both
kept in the declared-row style (`cand_rows[]`, `lmwalk_conj[]`), admission conjuncts first, price
last:

- **The controller table** is today's `cand_rows[]` with its slots unchanged. Its rows emit C
  instructions with typed hands. LOCATE rows (`landmark-walk`, `rev-end`, `cover`, `composite`)
  no longer name a finisher route. `lc_finisher` disappears, because FINISH is "the body" and the
  hand's type is all the locator needs to know.
- **The region table** is asked top-down for each node of the body: "what instruction kind runs
  this region?". The rows, first match:
  1. `cut-literal`: the seam's proof covers the region → nothing.
  2. `dseg-commit`: R1 holds (§2) and the region is regular → `DSEG … COMMIT`.
  3. `dseg-enum`: R2 holds → `DSEG … ENUM`.
  4. `dseg-guided`: R3 holds → a `DSEG rev VIAB` over the continuation, then a frame-free forward
     priority walk.
  5. `zero-width-in-segment`: a lookaround, callout or `\K` whose enclosing region is one-pass →
     a `GUARD` / `CALLOUT` / `SET` on the segment's single live thread (§2.3).
  6. `vm`: everything else → M instructions; the table recurses into the children, which may
     again take rows 1-5.

  **Maximality is a hard rule, not a price**: a region takes the largest enclosing node that
  admits a D row. A stream never splits a DSEG that could be one (see §5, the risk that today's
  whole-DFA cannot have). Price decides only among admitted rows (e.g. `dseg-enum` vs `vm` frames
  on a short fragment), from the measurement set (D166), never from a constant (D149).

Today's per-artifact `analyses[]` mask becomes the root's degenerate answer. "Captures requested
→ VM" stops being a whole-pattern verdict: a capture is a SET instruction, derived where the
region allows and on M otherwise.

---

## 2. The soundness rule

### 2.1 What must be preserved

Take a region S, entered at position p, with continuation K: everything after S up to ACCEPT,
including what the controller requires of the end. The backtracker produces S's exits as an
ordered list `E_S(p)` = [(e₁,σ₁), (e₂,σ₂), ...] in priority order: greedy/lazy, alternation
order, PCRE's empty-iteration rule. Each eᵢ is an end position and each σᵢ is the slot values
at that end. It runs K from each element in turn and takes the first success. If none succeeds,
S fails and control returns to whatever is before S.

A replacement R for S is **exact** iff, for every p and every K consistent with the pattern, the
first element of `E_R(p)` from which K succeeds is the first such element of `E_S(p)` (same e,
same σ), and R fails exactly when S does. That is the whole rule. The four strengths below are
the sufficient conditions pcrec can check statically.

### 2.2 The four strengths

**R1 COMMIT: one exit, no resume point.** Exact if any one of these holds:
- (a) **K is ACCEPT.** S is the body's tail, so the first exit is the answer, and the D3 priority
  DFA's leftmost-first end IS that exit. This is why the DFA engine is exact at all. It is the
  same rule applied to the last region of any body, including inside a VM program.
- (b) **S is atomic in context**: `S·K ≡ (?>S)·K`. This is possessify's test
  (`pcrec_uniq_iteration`, `possessify.c:1154`, plus disjoint follow), lmwalk's `exclusion`, and
  compound client 7's "unique end". The DSEG must produce S's FIRST exit in priority order, not
  its longest: an anchored D3 machine over S alone does that.
- (c) **S is an atomic group or possessive quantifier in the source**, with a regular body. This
  case REVERSES today's treatment. Today an atomic group is an ERASURE that makes the prefilter a
  superset (H3, `emit_vm.c:10377`). Under R1(c) it is the easiest case: a commit segment over
  the body's first exit.
- (d) **S has at most one exit per start**: fixed width and deterministic, or unambiguous with a
  unique end.

Captures inside a COMMIT segment are allowed where derived (§1.3). Elsewhere the region splits at
the capture.

**R2 ENUM: the full exit list, in order, through one resume point.** Exact if the segment
produces `E_S(p)` itself. Checkable today in two shapes, both already built as VM rungs:
- (a) **monotone preference**: one greedy (lazy) quantifier over a deterministic, fixed-stride
  body yields ends longest-first (shortest-first). This is today's cursor rung, and it is
  APPROACH §2's accept-list condition (amended A-1).
- (b) **branch-ordered alternation**: deterministic branches with one end each yield ends in
  branch order. This is today's ENG-ISL trie.

The general form, a DFA whose accepting states carry a priority-ranked exit enumeration, is
hole H4. Duplicate ends may be merged only where they carry equal σ, or where K reads no slot
(no backref into S).

**R3 GUIDED: frame-free exact finish for a regular tail.** If S·K is regular (K may write slots
but reads none), and the controller has handed `SPAN(s,e)`:
1. Run one reverse segment from e back to s. It records, per position, the set of NFA states from
   which ACCEPT-at-e is reachable (`VIAB`).
2. Walk forward from s through S·K. At every choice, take the first branch, in priority order,
   whose successor is viable at the current position.

Why this is exact: the backtracker's first success is the lexicographically-first accepting path
in priority order, and its end is e because D3's end is correct. So it is also the
lexicographically-first path among those ending at e, and the guided walk produces exactly that
path. No frames, no resume, linear time, and memory proportional to e−s, capped with a fall back
to M. This is the textbook backward-pass/forward-walk capture method, placed as a segment kind.
- **R3′ (pruning).** If K is NOT regular (a backref, a callout, a recursion), the same VIAB over
  a regular SUPERSET K′ ⊇ K is a necessary condition. Non-viable branches are pruned and viable
  ones keep their resume points. This is sound and does not remove backtracking.

**R4 BOUND: locator, commits nothing.** A segment over L′ ⊇ L at its seam may hand `LOWER`,
`UPPER`, `CAND`, `NOMATCH`, and `SPAN`/`AT`/`ENDSET` only where L′ = L there: the typing rule
(§1.3). A reverse segment seeded at a landmark hands `AT s*` only under lmwalk's admission
(exclusion, g1, utf8-l0). This is today's start table, unchanged in content.

**Where none holds: M.** Frames, as today. The region table still recurses into the children,
so an M region's sub-regions take R1/R2/R3′ where they can. That is where APPROACH §2's "DFA
islands inside the VM engine", planned and never built, become ordinary rows.

### 2.3 Zero-width irregular items inside a segment

A lookaround, callout or `\K` is a point on a path. Inside a region that is **one-pass** (at
most one live NFA thread at each position: the R1(b)/(d) shapes, or a DSEG whose subset states
are singletons after D3 pruning), such an item acts on that single thread. The instructions are:
- `GUARD`, which runs the lookaround's own sub-stream at the current position;
- `CALLOUT`;
- `SET slot0.start` for `\K`.

A guard failure kills the thread, and the segment fails as the backtracker would: the thread had
no alternative inside the region. A callout fires once per pass of the thread. That is the
backtracker's own sequence, because the region is not re-entered from inside (it is a cut). Outer
re-entry re-runs the segment, and the backtracker re-runs it too. Under the purity contract (D163
add. 6 Q2) the controller may still skip starts.

In a region that is NOT one-pass, a guard filters several threads at once, and determinization
would have to split states on guard outcomes. That case declines to M (hole H3). D164's
END_MARK is the special case where the guard becomes plain consumption, and it stays a lowering
ahead of the segmenter.

---

## 3. The worked patterns

Notation: `C`/`D`/`K`/`M` are the families. `→` is a seam, with its hand. "Today" is what
`build/pcrec` emits on main (`runs/pN.c`, `runs/pN.ir`).

**1. `abc`.** Today: DFA, `RX_DFA_SCAN "cover"`.
```
C ENTRY search(lo)
C LOOP gen = K FIND(run "abc", from lo)   → AT p, proof{p:a, p+1:b, p+2:c}, consumable 3 | NOMATCH
    (body: row cut-literal, the proof covers it: no instruction)
C RETURN SPAN(p, p+3)
```
Identical to today's `cover`. This is the first byte-identity target (§7).

**2. `[a-z]+@x`.** Today: DFA `reverse-pass` on main, and the landmark walk on p1build.
```
C ENTRY search(lo); reach := lo
C LOOP gen = K FIND(set{@}, from j)                    → AT j, proof{j:@}
    D DSEG rev M(P·L = [a-z]+@) from j+1, floor lo, BOUND  [R4; exclusion: [a-z] ∌ @]
         state q0 loops on [a-z] → K SKIP(rev, [a-z])      ← the scan edge, inside the segment
       → AT s*, proof{[s*, j] ∈ L(P·L)}  | none → next j
    C if j < reach → RELOCATE LOWER s* → (D fwd unanchored composite; D rev; RETURN)
    D DSEG fwd anchored M(Q = x) from j+1, COMMIT [R1a]   ← starts at the CUT, not at s*
       → SPAN(s*, j+2) → RETURN | fail → reach := j+2; next j
C RETURN NOMATCH
```
The seam from the reverse segment carries a proof that `[s*, j]` matches P·L. Exclusion makes P·L's
end unique, so the forward run starts at the cut j+1 and does not re-read P. Today's walk re-runs
the whole anchored machine A from s*. The plan's newest row, `[CAND-SPAN]` "the cut-point
condition for starting the forward verify past the proof" (c967685c9), is this seam fact. It is
being argued case by case, where in the stream it is a property of the hand.

**3. `(\w+)@(\w+)\.com`.** Today: VM, the hybrid prefilter pair (forward then reverse DFA), then the
VM re-walks the window (possessify 2/2, cursor rung). The landmark walk declines it (row
`finisher-dfa`).
```
C LOOP gen = K FIND(set{@}) → AT j
    D DSEG rev M(\w+@) from j+1, BOUND [exclusion] → AT s*, proof{[s*,j) ∈ \w+, j:@}
    M SET g1 = (s*, j); SET g2.start = j+1       (DERIVED from the seam: plain stores)
    D DSEG fwd COMMIT [R1b: \w ∌ '.'] : K SKIP(fwd, \w, ≥1) → AT e
    M SET g2.end = e
    K VERIFY(".com" at e) → SPAN(s*, e+4) → RETURN | fail → next j
```
Zero frames, every capture derived, about two passes over a candidate instead of three. Today's
design, grown with a VM finisher behind the walk, gets most of this: it re-reads `\w+` once more
and stores g1 by walking it.

**4. `(a|ab)(c|bcd)(d*)`.** Today: VM hybrid, one island, one possessive quantifier.
```
LOCATE: D fwd unanchored (D3 priority DFA) → END e; D rev BOUND → SPAN(s,e)   [exact: no erasure]
FINISH: D DSEG rev VIAB over (a|ab)(c|bcd)d* from e to s           [R3]
        M-free walk: g1 ← first viable of {a, ab}; g2 ← first viable of {c, bcd}; d* COMMIT [R1a]
```
On `abcd`: SPAN (0,4). After `a` at 1, `bcd` reaches 4, so branch `a` (priority 1) is viable and
taken. Then `c` at 1 is not viable and `bcd` is. The answer is g1=(0,1), g2=(1,4), g3=(4,4),
which is PCRE's. A leftmost-longest DFA would give (0,2)(2,3)(3,4). The D3 machine owns the end
and R3 owns the captures. No frames.

**5. `(\w+)\s+\1`.** Today: VM, **no prefilter** ("no-backreference: ... no flag changes this").
```
C LOOP gen = K FIND(set \s) → AT j
    D DSEG rev M(\w+) from j, BOUND [exclusion \w ∌ \s] → LOWER s*, UPPER j
       (typing rule: Q reads slot g1, which P writes, so AT degrades to a WINDOW of starts)
    C LOOP c over [s*, j):
        M SET g1 = (c, j)                                         (derived: proof says [c,j) ∈ \w+)
        D DSEG fwd COMMIT [R1b: \s ∉ first(\1) ⊆ \w] : K SKIP(\s, ≥1) → AT e
        K MISMATCH(subject[c..j) vs e) → SPAN(c, e+(j−c)) → RETURN | fail → next c
```
The locator becomes admissible by the typing rule alone. lmwalk's soundness sentence ("a match at a
start above s* would also match from s*") is false when Q reads P's capture. The hand type
records that, rather than a `g1` row refusing it.

**6. `foo(?=bar)|(?<!x)baz`.** Today: VM hybrid, prefilter built from the ERASED language, no
ceiling (`prune-ceiling subject-end`), no rungs.
```
(lowered first: D164 END_MARK  foo(?=bar) → foo MARK bar)
C LOOP gen = K FIND(set{f,b}) → CAND p
    D DSEG fwd unanchored COMMIT [R1a] over  foo·MARK·bar | GUARD(prev ∉ {x})·baz
       (the GUARD reads one byte before the branch start: the segment's context view, ir/dfa.c ctx_rows)
    → SPAN(s, mark-or-end) → RETURN
```
No M instruction. It is a DFA artifact in all but name. Today's design reaches the same result with
two separate lowerings: D164 for the lookahead, and a context view for a fixed one-byte
lookbehind. The stream reaches it with one row (`zero-width-in-segment`).

**7. `(?:cat|dog|…30 words…)s?`.** Today: DFA, `reverse-pass`, no scan edge.
```
C LOOP gen = K FIND(first-byte set or the kit's window) → CAND p
    D DSEG fwd unanchored COMMIT → END e; D DSEG rev BOUND → START s → RETURN SPAN
```
Identical to today. With a capture, `(cat|…)s?`: when no word is a prefix of another, the
alternation has one exit per start, so the row is R1(d) COMMIT with a derived g1. Otherwise it is
R2(b) ENUM, today's trie. Today a capture moves the whole pattern to the VM: an island plus one
frame per alternation.

**8. `(a+)+b`.** Today: VM hybrid, exact window, rungs `cursor,frames-unbounded`, possessify 0/2,
**stamped subject ceiling 1024 bytes** (`runs/p8.ir`).
```
LOCATE: composite D fwd + D rev → SPAN(s,e)      [exact]
FINISH: D DSEG rev VIAB over (a+)+b from e to s; guided forward walk [R3]
        inner a+: continue while viable; outer: another iteration not viable at the 'b' → exit
        → g1 = (s, e−1)
```
Linear, no frames, so no ceiling. And it does not depend on the window being exact: R3 needs only
`SPAN`, and where an erasure makes the window a superset, the region table takes R3′ instead.

**9. `x(?C1)y\d+`.** Today: VM, **no prefilter** ("a callout pattern has no prefilter yet").
```
C LOOP gen = K FIND(set{x}) → AT p, proof{p:x}
    M CALLOUT(1) at p+1      [zero-width-in-segment: the region x·y\d+ is one-pass]
    D DSEG fwd COMMIT [R1a]: K VERIFY("y" at p+1); K SKIP(\d, ≥1) → SPAN(p, e) → RETURN | fail → next
```
It fires once per `x` that reaches the callout. That is the backtracker's own sequence under the
start optimization the purity contract allows (D163 add. 6 Q2).

**10. `\p{Greek}+\s\d{3}` under UTF-8.** Today: DFA, `reverse-pass`, scan edge `range`.
```
C LOOP gen = K FIND(lead-byte set of Greek) → CAND p   [seam proof: p is a character start]
    D DSEG fwd unanchored COMMIT (UTF-8 byte automaton; SKIP edges on the Greek run) → END e
    D DSEG rev BOUND → START s → RETURN SPAN
```
Unchanged. The landmark rows decline: under UCP, `\s` has non-ASCII members, so lmwalk's
`utf8-l0` fails. The only new thing is that "p is a character start" becomes a declared component
of the hand's proof, instead of a row-local check.

---

## 4. Benefit case

Grades: **strong** means measurable now and not reachable as cheaply any other way. **Medium**
means real, but today's design grown could reach most of it with per-feature work. **Weak** means
plausible but unmeasured, or mostly "tidier".

| # | benefit | kind | how measured or demonstrated | patterns | grade |
|---|---|---|---|---|---|
| B1 | **The skip family is one kit kind.** EDGE, STAY (fwd, rev), VMSPAN and VMSTRIDE become `SKIP(set, dir, stride)`. One shape analysis replaces scanedge.c's on the DFA graph and `vm_det_seq`/`vm_cursor_fits` on the AST. Every kit improvement to SKIP lands on DFA scan edges and VM cursors at once, with ONE measurement card. | simplicity, plus kit speed reach | byte-identical re-expression (proof P1); count of deleted builders, rows and manifest lines; then one kit change measured on both a DFA cell and a VM cell | 2, 3, 5, 8, 9, 10 | **strong** |
| B2 | **One exactness rule at every seam.** The typing rule replaces H3's three conjuncts (`emit_vm.c:10366-10441`), `pcrec_cand_lang_exact`, lmwalk `g1`, and compound A2/A4. A new erasure is recorded once, on the segment, and every consumer is correct by type. This class of defect has already shipped as silent match loss twice (the atomic and lookaround cases H3 records). | simplicity, correctness | count of the sites deleted; a sabotage that drops one erasure record must fail every consumer at once (one control, not N) | 3, 4, 5, 6, 8 | **strong** (on the defect history) |
| B3 | **One reverse-walk kind.** It is seeded at any known point (subject end, match end, landmark, iteration boundary). It deletes `pinned`, `end-minus-width`, `reverse-pass`, `rev-end` one-seed and tagged, `lmdfa`, and VM `revdet` as separate mechanisms; they remain as ADMISSION rows. This is D161 add. 17's own direction, taken to its end. | simplicity | P2 (the walk as records, byte-identical); count of the emitters folded | 2, 3, 5, 7, 10 | medium-strong |
| B4 | **Frame-free capture finish (R3 GUIDED) for regular regions.** It removes backtracking and the `frames-unbounded` rung's stamped subject ceiling (1024 bytes on `(a+)+b`). The captures of ambiguous regular regions are found in one linear pass. | speed, reach (limits) | census: VM-routed corpus and bench patterns whose body is regular apart from captures; then the bench VM cells, steps and time, answer-identical over the corpus | 4, 7 (captured), 8 | medium (today could add a third engine for whole regular patterns; only the per-REGION use, R3′ under a backref, is stream-only) |
| B5 | **Locators for VM-only patterns by type, not by feature.** Backrefs (today none: "no flag changes this"), callouts (none: "no prefilter yet"), and lookaround windows with a ceiling. The hand degrades AT→WINDOW where Q reads P's slots. | reach | census of `RX_VM_PREFILTER "none"` artifacts by reason; the bench on log and email backref cells | 5, 6, 9 | medium (each is buildable today as its own special case) |
| B6 | **Zero-width items inside one-pass segments, and D after M at any depth.** Guards, callouts and `\K` ride a DSEG's single thread. A deterministic region can follow a backref or a lookaround inside a loop body or a branch. Today a DFA cannot call a sub-matcher mid-scan, and compound composes only at the top-level concatenation, once (client 7, DFA then VM). | new capability | census: patterns forced to the VM ONLY by zero-width items in one-pass regions (beyond D164's trailing-lookahead group), and VM-routed patterns with a regular region AFTER their first irregular node | 6, 9, `(?:\w+(?=,),)*\d+` | medium-weak until the census |
| B7 | **Seam proof reuse.** The finish starts at the cut, past the proven prefix (§3 patterns 2, 3, 5). | speed | bytes read per match on the email and log cells | 2, 3, 5 | weak as a stream claim: `[CAND-SPAN]` is already pursuing it inside today's design |
| B8 | **D182's analysis stage (c) over the whole artifact.** Slot liveness and dead stores across D/M seams (e.g. SETs that a derived capture makes redundant), and work-budget charging per segment. | simplicity, speed | none until stage (c) exists | 3, 5 | weak (speculative) |

Claims deliberately NOT made:
- "One emitter is smaller." Most of `emit_dfa.c`'s 16k lines are decisions and their reasons, and
  those move rather than vanish.
- "Fewer abi events." The opposite holds during migration.
- "Faster on pure-DFA patterns." Patterns 1, 7 and 10 are byte-identical targets. The stream's
  job there is to lose nothing.

---

## 5. Bird-in-the-hand: the two FULLY BUILT end states

**Today's design grown as far as it goes**, built fairly:
- the two engines and the compound tool (D163 add. 7: every entry a controller over parts);
- `cand_rows[]` with VM finishers behind every locator (L3), so the landmark walk serves VM
  patterns;
- D164 END_MARK for every trailing lookahead, and fixed-width lookbehind as DFA context views;
- APPROACH §2's exact and accept-list islands inside the VM;
- concatenation split (client 7);
- superset prefilters for backrefs (referent language) and callouts (purity contract);
- one shared kit SKIP;
- a third "guided" engine for whole regular capture patterns.

That is a strong design. Head to head:

| dimension | today, fully grown | stream, fully built |
|---|---|---|
| exactness rule | one admission table per crossing: prefilter H3, island A-1, compound A1-A5, lmwalk 9 rows, possessify, revdet U1/U2. Each new crossing adds a protocol plus its admission. | one rule (R1-R4) at one seam type. The old tables survive as ROWS of the region and controller tables, and a new crossing is a row. |
| granularity of mixing | engine per artifact (or per compound part); islands one level deep inside a VM; concat split at top level, once | per region, any depth, both directions (D in M in D) |
| zero-width irregular items | in the VM only (or lowered away case by case: D164, context views) | in any one-pass segment |
| atomic groups / possessives | an ERASURE for the DFA (superset), a cut for the VM | a COMMIT segment (R1c): they make regions more deterministic, not less |
| pure-DFA patterns | one tight machine, by construction | the same machine, by the maximality rule (a rule that can be broken; see "never" below) |
| VM-heavy patterns (backrefs, recursion) | the VM, with islands | the same M, with more of its sub-regions as D (R1/R2/R3′) |
| adding a module (a new construct) | decide its engine, its prefilter erasure, its island eligibility, its compound admission: four questions | declare its instruction kind's seam signature (reads, writes, width, one-pass or not) |
| kit | per-site rows, keyed partly by engine context | per-operation kinds, with facts from the seam |
| observability | `RX_ENGINE`, the `_DFA_*` and `_VM_*` families, two listings (`--emit-ir` for the VM, stamps for the DFA) | one listing of the stream (the VM listing generalized), stamps derived by one fold. `RX_ENGINE` becomes a summary. |

**What today's design can NEVER do** without becoming the stream:
1. Continue deterministically after an irregular point, below the top level. Its D and M meet
   only at artifact or part boundaries, plus one-level VM islands.
2. Put a guard or a callout inside a DFA. A DFA artifact has no call-out by definition, so the
   whole pattern pays for the VM.
3. State exactness once. Its crossings are different protocols, so each needs its own argument.
   The shipped H3 defects are what that costs.
4. Let an atomic group make the DFA side MORE exact. In a DFA artifact it can only be erased.

**What the stream can NEVER do**, or pays for:
1. **Guarantee whole-artifact properties by construction.** Today a DFA artifact has no stack,
   no budget, O(1) streaming state and bounded work because it is a DFA artifact. The stream
   DERIVES those properties from its instruction set, so a segmenter bug (one stray M
   instruction) silently costs them. The mitigations are: maximality as a hard rule; the
   properties stamped from the fold; and a gate that every pattern today's selector routes to the
   DFA yields an all-D/K stream.
2. **Never pay a seam.** Each seam is a cursor handoff and a boundary gcc cannot optimize across.
   Today's whole-DFA hot loop has none. A segmenter that fragments a pattern can be slower than
   today on patterns today handles well.
3. **Keep two simple emitters.** One render vocabulary in one function must hold computed-goto
   DFA states, table-driven DFAs (D13) and the VM's single-indirect-jump rule together. Today
   these never meet in one function, apart from the hybrid's separate prefilter function.
4. **Avoid many small machines at compile time.** K7's subset cap and the gcc-time budget then
   apply per segment and in total, which is a new budget to state.

Verdict on merit alone: the stream wins on mechanism count, exactness by construction, and the
mixed-feature reach (B2, B6). Today's design wins on the guaranteed whole-artifact properties of
pure DFAs, which the stream must protect by rule rather than by structure. Patterns 1, 7 and 10
are a tie by design. 2 and 3 are near-ties against the grown design. 4, 5, 6, 8 and 9 are where
the stream's single rule pays.

---

## 6. Holes I already see, ranked

1. **H1: Captures inside segments.** Derived offsets cover boundary captures and cursor-derived
   spans, nothing more. General captures need a tagged DFA with determinate tags, and that is not
   designed here. Without it, the region table SPLITS at captures, which fragments the stream and
   pays seams (§5, "never" 2). This is the biggest risk to B4 and B6 on real patterns.
2. **H2: The segmenter's choices are unmeasured.** Maximality is a rule. The cost of a seam
   (register handoff, a lost gcc loop, code size) has no number yet. A first-match table may
   fragment where one M region would be faster. R3's VIAB memory is O(window) and needs a cap,
   with a fall back to M.
3. **H3: Guards in segments that are not one-pass** decline to M. Whether the one-pass population
   is large once D164 has taken trailing lookaheads is unknown; the census decides B6.
4. **H4: ENUM for non-monotone fragments** (`(?:aa|a)*`, APPROACH A-1's own counterexample)
   declines to M. A general priority-ranked exit enumeration is not designed.
5. **H5: Budgets and give-up surfaces.** A DSEG's work must be charged (`VK_WORK` exists). Moving
   a region from M to D moves where `PCREC_ERR_STEPS`/`FRAMES` can fire. That is
   caller-observable and runs into the `CG_FIXED` contract rows. It is a spec event (D80) per row.
6. **H6: Stamps, the listing, the ABI.** `RX_ENGINE`'s meaning, the `_DFA_*` iff rule, and
   `docs/spec/ir_listing.md` all change, and every artifact moves. This is ritual, not a blocker
   (pcrec-abi-changes-pre-release), but it is the whole tree.
7. **H7: UTF-8 seams.** The VM steps code points and the DFA steps bytes, so the hand must carry a
   character-boundary proof. lmwalk's `utf8-l0` is the only precursor.
8. **H8: Recursion and subroutine calls.** Segments inside shared callee bodies need seams across
   CALL/RETURN and the slot snapshot. Not worked through.
9. **H9: Streaming input.** Any M instruction ends chunked matching, as today. Listed only because
   the stream makes it a derived property (§5, "never" 1).

---

## 7. Smallest proofs

Each proof is a small change, implement-then-replace (D146), with no new caller surface.

**P1 (byte-identical): the skip kind across both engines.** Build ONE record type, `SKIP(set, dir,
stride, advance-hooks)`, used by both emitters:
- the VM's `vm_emit_span_scan` (`emit_vm.c:4839`, today VMSPAN and VMSTRIDE);
- the DFA's edge and stay sites (`emit_dfa.c:9187`, `9216`, `12571-12587`, today EDGE and
  STAY).

The record still names its kit row: collapsing the four DELEG rows is a kit-side abi event, and
comes later. Evidence: the identity gate, movers 0; the builders deleted; the first record in
`emit_dfa.c`. It proves that a kit leaf is an instruction independent of the engine, and that
D182's records can enter the DFA emitter one kind at a time.

**P2 (byte-identical against `lane/p1build`): the landmark walk as a stream.** Re-express
`emit_landmark_walk` (`p1build:emit_dfa.c:14382-14514`, today raw `pcrec_sb_puts` around four
`DfaForm`s) as the record sequence of §3 pattern 2:
`C LOOP(K FIND) · D rev BOUND · C RELOCATE-guard · D fwd COMMIT · C RETURN`.
- The seams are typed from `CAND_HAND_*`.
- The emitter's three `pcrec_ctx_fail` asserts (`14408-14419`: "the seed AT is finished by a row
  that is not verify-at", ...) become seam type checks at build time.
- `lc_finisher` becomes a statement about the hand's type.

Evidence: the walk's own suite on p1build, movers 0. It proves that controller glue and
deterministic segments live in one record vocabulary with the VM body, and that the hands graph
`cand_nodes[]` IS the stream's control layer.

**P3 (benefit): R1 COMMIT islands inside the VM body.** Step 0 is a read-only CENSUS (D77, the
trigger): the VM-routed corpus and bench patterns with a sub-region that
- possessify ALREADY proves atomic in context (no new soundness argument),
- has two or more NFA states that no current rung takes (cursor, counter, island),
- and has captures only at its boundaries.

Examples: `(\d{1,3}(?:\.\d{1,3}){3})\s+\1`, `(\w+(?:-\w+)*)@(\w+)`. If the census finds a
population, emit such a region as an anchored D segment (today's anchored `DfaForm`), with
derived SETs, behind a test-only force-decline lever (memory pcrec-flag-follows-caller-effect: a
wrongness-risk change). Its measurement card goes in the measurement script (memory
pcrec-new-method-needs-measurement-card).

Evidence:
- answer identity over the corpus with the lever on and off;
- VM steps and frames per match;
- bench time on the VM-routed cells, SIMD on and off (D147).

It proves the first stream-only benefit: APPROACH's never-built islands as an ordinary row of the
region table.

---

## 8. Migration (separate; never subtracted from §5)

| step | what | identity | cost |
|---|---|---|---|
| M0 | the censuses for B4, B5, B6 and P3 (read-only) | n/a | small |
| M1 | P1: kit leaves as records in both emitters | byte-identical | small |
| M2 | DFA emission as records: the scan loop, reverse block, tables and success tail become D-family records | byte-identical | LARGE (most of `emit_dfa.c`) |
| M3 | controller instructions: each LOCATE/FINISH row's emitter becomes a C-record sequence (P2 first) | byte-identical | medium |
| M4 | the region table holding today's choices as rows: `vm`, cursor = `DSEG ENUM` over a one-state machine, trie = `DSEG ENUM`, revdet = `D rev`, the hybrid = `D BOUND` ahead of M | byte-identical | medium |
| M5 | new rows: R1 islands (P3), then R3 GUIDED, then zero-width-in-segment, each behind its lever | answer-identical; movers by design | medium per row |
| M6 | stamps, the stream listing, `RX_ENGINE` as a derived summary, spec hunks (D80), abi bump and re-pin (D76/D94) | every artifact moves | medium, the ritual |
| M7 | retire `analyses[]` as a verdict (the root's degenerate row) and the engine-context kit kinds | movers by design | small |

**Timing note:** D182's stage (c) analysis (lexer, helper registry, FL/CEN) is being designed now
for the VM body only. Designing it against the stream's record set costs nothing extra today, and
it is the cheapest point of alignment this whole migration has. Doing it VM-only and redoing it at
M2 is the expensive path. This is a recommendation for the manager's ruling, not a scope change.
