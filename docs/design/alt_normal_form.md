# One alternation normal form: folds are alternations, positions are sets at the seam

**Status: PROPOSED, rev 1** (lane altrev1, 2026-11-05; design only, no build go).
Rev 0 was lane altdesign's; rev 1 applies the RULED critic round
`docs/dev/reviews/2026-11-05-r2-alt-normal-form.md` (every FIX-NOW fixed in
the text, PLAN items placed, DOC items fixed) and the owner's five rulings of
the same evening (§0.2). Changes from rev 0 are marked inline with **(r2)**;
the rev 0 decisions that held are kept unmarked. A re-check critic round
follows. Plan row: [RUN-POS-SET]; siblings [LOWERENC-SEAL], [REQ-EMPTYCAT],
[REPEAT-RUN], [REQ-LOOKAROUND], [DFA-ALPHA-MERGE], [POS-ONE-DETECTOR].
Inputs: `docs/dev/lanes/altthink_report.md`, `docs/dev/lanes/rpsurvey_report.md`
(its derived москва/αβγ numbers are wrong, corrected by altthink).
Evidence: `docs/dev/lanes/altdesign_evidence/` (rev 0) and
`docs/dev/lanes/altrev1_evidence/` (rev 1: `cmp.py`, pcrec `--emit-main` +
`gcc -O1` against libpcre2-8 10.46 by ctypes, utf8 = UTF|UCP|MATCH_INVALID_UTF;
case files `*.tsv`, outputs `*.out`). Proposed decision: **D-next** (§12).

Rulings this note builds on (Frank, 2026-11-05): case folds are set up as
alternations and handled by the alternation logic (considering alternation
concatenation); for ASCII that may just be sets, for UTF-8 tries or other
reductions; the byte-encoding result may be the same as today. The kit hand-off
stays SETS unless a case is made that something richer lets SIMD do better.
The matcher's own caseless-class code (the VM's decode-and-test) is not the
target.

## 0. Premise tests and the owner's rulings

### 0.1 Premise tests (re-run)

- Rev 0's premise (`(?i)abcdÀefgh -e utf8`: the run starts AT À, `abcd` lost)
  holds; the critic round re-ran it.
- **(r2) SND-1 reproduced** before any text was written
  (`altrev1_evidence/premise.out`): `(?:ab|a|ad)` on `ad` = (0,1) in libpcre2
  and in `build/pcrec`; the width-grouped `(?:a[bd]|a)` = (0,2) in both; the
  other slot `(?:a|a[bd])` on `ab` = (0,1) against the original's (0,2);
  `(?:for|fo|fox)`/`fox` (0,2) vs (0,3); `(?:ac|x|xc)`/`xc` (0,1);
  `(?i)(?:αb|α|αd)`/`αd` (0,2) under utf8. Rev 0's stage 2b as written moves
  answers; §3.3 is the fix.

### 0.2 Owner rulings applied (r2)

| # | ruling (Frank, 2026-11-05, "Yes to all") | where |
|---|---|---|
| O1 | Run FACTS may use covering (superset) sets wider than any one alternative; facts only, never a tree rewrite | §3.1, §4.2 |
| O2 | Stage 1 = UTF-8 lowering alone; its extra movers (VM islands, dot / negated / `\p` / `\W`) listed as PREDICTED movers with gates; stage 1 classed honestly under D186 per regime | §5 stage 1 |
| O3 | Set positions ride along with the kit-seam work ([POS-ONE-DETECTOR] / D187) | §5 stage 3, §4.7 |
| O4 | Runs continue across mixed-byte-length case letters (о, Kelvin k) in PER-LENGTH PIECES now, `ci-moskva` the witness | §3.4, §5 stage 2p |
| O5 | The note NAMES the wider general form: every fixed-width piece of a pattern has ONE description; the alternation owner is one part; the siblings come in by design, staged later | §3.5, §9 |

The STOP RULE was checked against every ruling: none contradicts a CONFIRMED
finding. O4 is sound as a FACT (§3.4) but no reader pcrec ships today can
consume it; §3.4 says so prominently and designs the nearest sound form (the
fact now, its consumer through the kit), with the question in §13.

## 1. Goals

Ranked; the higher goal wins a conflict. **(r2)** each goal now names its
comparison and margin, and the ledger behind G3 is §2.3.

| # | goal | who benefits | measurable form (comparison, margin) |
|---|---|---|---|
| G1 | No answer moves | every caller | answer identity over the corpus and the bench patterns, every encoding, every axis (`make test`, `make test-axes`); libpcre2 differential (PC-3) unchanged; margin 0 |
| G2 | D186's bar per stage, per regime | users with pinned performance | each stage declares its kind PER REGIME (r2: stage 1 is no change on byte, a unit change on utf8 except the listed pick-flip cells, which are choice cells, §5); unit: no regime slower beyond noise; choice: no regime loses beyond noise, a loss narrows the flipped row; stage 1's byte emit diff is EMPTY over the named population (§5 B0) |
| G3 | One mechanism | maintainers | one owner of tree rewrites (§3.3) and one description of fixed-width pieces for facts (§3.5); the ledger §2.3 (deleted / merged / added, file:line) is the check, not "none added" (r2) |
| G4 | Caseless UTF-8 keeps its required runs | `-e utf8 (?i)` users | of the 1454 simple fold classes, those keeping the full `abcd<X>efgh` run: 513 today, EXACTLY 766 after stage 1 (r2: one form, Gate U2), about 898 after stage 2a (766 + the 132 equal-width classes whose hull is a cube of ≤ 2 members; inferred from the critic recount, the census confirms), 1403 after stage 3 at the ruled member bound 2 (1416 at 3, 1417 at 4 or more; r2, SIM-1); the 37 mixed-width classes keep a full-width PIECE per length (§3.4) from stage 2p; `ci-greek-run` 0 → 3 positions at stage 1 (the seal's removal alone, §8 `s0`), 6 at stage 3 only at member bound 3 (§4.4) |
| G5 | Smaller caseless UTF-8 tables | object size, cache | no utf8 mover's DFA next-state table grows, compared PER MACHINE (r2: PREM-5/SIM-8); `(?i)москва` 1140 → 900 entries (−21%), `(?i)αβγ` 160 → 112, `(?i)Ελληνικά` 1430 → 1040 (r2: SIM-5's partial-merge figures) |

Non-goals: the VM's caseless class code; full case folding itself
([FULL-CASEFOLD], [SEQ-FOLD]); any statement of the kit's method (D157); any
reduction that enumerates a language (2^n words for n caseless letters); the
DFA alphabet re-merge (its own row, §10); **(r2)** a minimal or
language-canonical tree form (§3.3 "Order"); a trie produced by the owner for
the VM island (the island's trie stays A-ISL's, §3.3).

## 2. Where alternation facts come from today (inventory, checked)

### 2.1 Producers and readers

| site (file:function) | level | what it does with an alternation or class | role after this design |
|---|---|---|---|
| `src/parse/` (D23 fold) | code point | `(?i)x` becomes the class of x's simple fold set | unchanged: a class IS the one-symbol alternation |
| `src/opt/altcls.c` stage 1 (`altcls_walk_alt` merge), stage 2 (`altcls_factor_run`, `altcls_extend_prefix`) | code point, pre-callgraph | adjacent bare single-char class branches to one class; prefix factoring on ONE literal byte key over consecutive branches, a branch that IS the key left as `A_EMPTY` in its slot; **(r2: PREM-7)** stage 1 FEEDS stage 2 (`altcls_walk_alt` merges, then factors the merged list), stage 2's remainders are never re-merged | **caller of the owner** (stage 2b); both stages become owner rules (§3.3) |
| `src/opt/lower_enc.c` `lower_class_utf8` + `u8_box`/`u8_ranges` | byte, inside the new subtree | one branch per BOX (r2: a byte-range sequence, not a code point; PREM-7); boxes pairwise disjoint and prefix-free; wraps >1 branch in the `A_CAT(A_EMPTY, alt)` seal (`lower_enc.c:369-384`) | **caller of the owner** (stage 1); seal deleted |
| `src/facts/req.c` `rb_class_into` (`:549`) | byte | a class is a run position if it is one cube of ≤ `pos_set` members | the CLASS arm of the description (§3.5) |
| `src/facts/req.c` `rr_alt` (`:470`) + `rn_common_head`/`rn_common_tail`/`rn_hull_mask` (`:344`) | byte | cube hull of the common head and tail; `all = false` always | the ALT arm (stage 2a, 2p) |
| `src/facts/req.c` `rb_walk_at` `case A_EMPTY` (`:698`) → `rb_row_into` → `rb_assert_into` | byte | the empty string cuts the run like an assertion, because `kindrow.def:61` classes `A_EMPTY` as `ZERO` | the kind ROW gains the unit value (stage 2a, §3.6) |
| `src/facts/req.c` `rb_rep_into` (`:538`) | byte | a repeat keeps only the body's best; nothing joined across an iteration | the REP arm, [REPEAT-RUN] (§9) |
| `src/facts/req.c` `rb_intersect` | byte | bytes necessary in every branch | unchanged (a different question) |
| `src/facts/kset.c` `pcrec_kset_walk`, `pcrec_span_walk`, `pcrec_width_walk`; `src/facts/startset.c` `ss_walk` | NFA / lowered AST | per-offset unions, shape-blind (measured identical) | unchanged |
| `src/ir/dfa.c` `refine_by` | NFA atoms | alphabet refined from class atoms, never re-merged; shape-SENSITIVE | normal form removes most of it; [DFA-ALPHA-MERGE] removes the rest |
| `src/gen/emit_vm.c` `vm_isl_words` (`:4079`) / `vm_isl_build` | AST | enumerates a literal language into a priority-tagged trie, singleton byte edges only; descends `A_WCLASS` on EVERY axis (`:4091`) | **(r2: PREM-1)** stage 1 obligation: read a set position inside an `A_WCLASS` as its members (§5 stage 1) |
| `src/facts/endwin.c:301`, `src/gen/emit_vm.c:4093` | AST | private spellings of "the empty node is the identity" | readers of the kind row's unit value (stage 2a, §3.6) |
| `src/core/cpset.c` `pcrec_cls_cube`, `pcrec_cube_of` | class bitmap | the cube detector | D187's one derivation |

### 2.2 Special cases this design deletes or merges (r2: corrected)

- **(1) `rr_alt`'s `o.all = false` is NOT a deleted special case** (r2: OWN-2,
  PREM-7). Its comment (`req.c:464-469`) calls `all = false` the GENERAL fact
  ("these bytes are common") and declines the same-literal `all` as a special
  case with an unmeasured population (D77). Rev 0 read it inverted. Stage 2a
  REPLACES it with a declared row (§6, rr_alt rows 1/1b/2) whose general form is
  the ALT arm of §3.5, and stage 2a is re-argued against D77 in §5: its
  population is measured BEFORE the build go.
- (2) The `A_CAT(A_EMPTY, alt)` seal in `lower_class_utf8`: a real deletion
  (two nodes and the comment). Its own comment calls it redundant since K123,
  and the abi event its comment names is real (§4.7, r2).
- (3) `A_EMPTY` walked as an assertion: **(r2: SLOT-2)** not deleted but
  re-classified at its owner, the kind row (§3.6), and two private spellings
  (`endwin.c:301`, `emit_vm.c:4093`) become readers of that row.
- (4) `rb_class_into`'s and `rn_common_head`/`tail`'s two spellings of "a
  position" become one set-position constructor (stage 3, D187).
- (5) **(r2: OWN-1)** altcls's two stages become owner RULES (§3.3): its
  adjacent-class merge is the owner's sibling merge at width 1, its one-byte
  prefix key generalizes to a fixed-width key. That is a real merge only
  because rev 1's owner has a factoring rule; rev 0's did not.
- Generalized, not deleted: (6) `u8_box`'s contiguous-only boxing; (7)
  `vm_isl_single`'s singleton edges (stage 1's set-edge reading, §5); (8)
  [RUN-POS-SET]'s k/s first-byte handling, which is `rr_alt`'s existing common
  head/tail rule read over sets (r2: SLOT-4, OWN-7: §4.5, not "§6").

### 2.3 The ledger (r2: OWN-2; G3's check)

| change | where (file:line, base 7ffbd4deb) | kind |
|---|---|---|
| the seal | `src/opt/lower_enc.c:369-384` | DELETED (stage 1) |
| altcls stage 1 adjacent-class merge | `src/opt/altcls.c:312` `altcls_walk_alt` | MERGED into the owner (stage 2b) |
| altcls stage 2 one-byte key | `src/opt/altcls.c:180` `altcls_branch_peel`, `:210`, `:260` | MERGED into the owner, key widened (stage 2b) |
| "empty is the identity", three spellings | `req.c:698`, `endwin.c:301`, `emit_vm.c:4093` | MERGED into one kind-row value (stage 2a) |
| two position spellings | `req.c:549` `rb_class_into`, `req.c:344` `rn_hull_mask` | MERGED (stage 3) |
| `o.all = false` | `req.c:470` `rr_alt` | REPLACED by a three-row table (stage 2a) |
| the owner (sibling merge, prefix/suffix factoring, the adjacency test) | new, `src/opt/altnf.c` (name at build) | ADDED (stage 1 merge only; 2b the rest) |
| per-length pieces in the run walk | `req.c` (the ALT and CAT arms) | ADDED (stage 2p) |
| the island's set-edge reading | `emit_vm.c:4099-4110` | ADDED (stage 1) |
| the `info(S)` rounding, the member bound | `req.c` ranking; `limits.def:411` | ADDED / RE-RULED (stage 3) |
| R2 census obligation, R3 second core fact | §4.4 | ADDED (R3 only on its trigger) |

Rev 0's "the special cases named deleted, none added" was false. The
simplification the owner is offered is the merge column: one rewrite owner
instead of altcls's two stages, one unit value instead of three spellings, one
position constructor instead of two, the seal gone.

## 3. The general form and its owners

### 3.1 The form (kept, sharpened)

A class is an alternation of one-symbol strings. An alternation of
capture-free, fixed-position branches (each position a SET over the level's
alphabet: code points above lowering, bytes inside it) is reduced
POSITIONALLY, never by enumerating its language. Two products come out of it,
with different obligations (O1):

- a **tree rewrite** must be EXACT and must keep leftmost-first preference
  (§3.2, §3.3); it is owned by the rewrite owner;
- a **fact** may be a SUPERSET (a covering set wider than any one branch:
  `(?i)β`'s second byte `{92,b2,90}`); it is owned by the facts walk, as the
  description of §3.5, never by the rewrite owner (r2: SLOT-3, the owner's
  hull output is dropped; it had no reader).

### 3.2 Preference: when moving a branch is safe (r2: SND-1, SND-2)

Leftmost-first answers `min{ i : branch i matches here and the continuation
succeeds }`. Two branches matching at one start consume either the SAME span
or spans where the SHORTER is a proper prefix of the LONGER (both start at one
offset of one subject). So moving branch j up past an intervening branch m
changes an answer only if m and j can match at one start with different
lengths. Hence the one adjacency test every rewrite uses:

> **Adjacency test.** Branches i < j may be combined (merged, or factored
> together) only if, for every m with i < m < j, no string of m is a proper
> prefix or a proper extension of a string of i or of j. Capture-free branches
> of EQUAL width always pass (same span, nothing observable differs); a branch
> whose language the owner cannot decide (not a fixed-position set sequence)
> FAILS the test.

It is the boundary rev 0 lacked: "a maximal adjacent run" let width grouping
move `ad` past `a` (SND-1). In lowering the test is satisfied for every pair
by construction (UTF-8 boxes are pairwise disjoint and prefix-free), which is
why stage 1 held 3112 soundness checks; in altcls it is computed.

Factoring rules and the condition each needs (r2: SND-2, C2 in §8a):
- **prefix factoring** `K X1 | ... | K Xn → K(?:X1|...|Xn)` over CONSECUTIVE
  branches: K must be capture-free and FIXED-WIDTH (every way of matching K
  consumes the same span, so the original's order "every way of K with X1,
  then with X2" and the factored order agree on the first success). A branch
  that is exactly K stays as an EMPTY branch IN ITS SLOT (`(?:ab|a|ad)` →
  `a(?:b||d)`, measured equal on every probe, `premise.out`). The rests are
  arbitrary (`frank|fr(?:x*)ed` stays in the domain). A variable-width key
  moves answers: `(?:a|ab)c|(?:a|ab)b`/`abc` (0,3) vs factored (0,2).
- **suffix factoring** `A C | B C → (?:A|B) C` over ADJACENT branches holds
  for any A, B, C (right distributivity keeps priority order; the soundness
  critic's argument, held).
- **sibling merge** (two branches of equal width identical except at one
  position become one branch with the union there) is prefix factoring on the
  fixed-width head, suffix factoring on the tail, and "a one-symbol
  alternation is a class" in the middle. It needs the adjacency test between
  the two branches; it is no longer a separate grouping step.

### 3.3 The rewrite owner (r2: OWN-1, OWN-4, SLOT-3, SIM-2)

One module, proposed `src/opt/altnf.c` (name at build): a pure function from a
branch list (each branch a node, with its fixed-position set sequence where it
has one) to a rewritten list, applying §6's rule table: sibling merge,
prefix factoring on a fixed-width key, suffix factoring, each under §3.2's
adjacency test. It reads no option and no prior, allocates only new nodes, and
knows no encoding (the alphabet is a parameter).

| site | relation |
|---|---|
| `lower_class_utf8` | caller, byte level, over `u8_box`'s boxes; sibling merge only (stage 1); the adjacency test is true by construction |
| `altcls` | caller, code-point level, over every alternation spine it walks today (stage 2b); its two stages become the owner's merge and factoring rules, its one-byte key a fixed-width key |
| `req.c` | NOT a reader of the owner. Facts come from the description (§3.5); the owner's output is a tree like any other |
| VM island | NOT a reader of the owner (r2: SLOT-3). The island's priority-tagged trie stays `vm_isl_build`'s until A-ISL (roadmap R04, HELD) replaces it; stage 1 only teaches it to read a set position inside a lowered class (§5) |
| kset, startset | shape-blind; nothing to change |
| NFA/DFA tables | (r2: PREM-4) shape-SENSITIVE: table size follows the spelling; the owner shrinks them as a side effect, [DFA-ALPHA-MERGE] is the general fix |

**Tries (criterion 2).** Prefix factoring applied recursively IS a trie with
set edges (`fr(?:ank|ed)`, `a(?:b||d)`), so the owner produces trie-shaped
TREES for user alternations at stage 2b; for UTF-8 classes it produces the
"other reduction" (sibling merge, prefix sharing being already implicit in
`u8_box`). No separate trie OUTPUT is promised to any reader (r2: OWN-4).

**Order (r2: SIM-2).** The fixpoint is EXACT whatever the merge order, but not
confluent: the critic's drill found grids whose final branch count depends on
the order (`\p{Lu}`: 76 vs 66 boxes). Decision: the owner is called **a
reproducible reduction, not a canonical form**, with ONE declared strategy:
*position-major, last position first*: for p from the last position to the
first, group the branches that are identical except at p (and pass the
adjacency test pairwise), union each group at p; repeat the sweep until no
group merges. Its cost is O(passes · n · w) with hashing on the
all-but-p key (the critic's 13M pair compares for `\p{L}` are the pair scan's,
which this replaces); the build lane states the measured worst case over the
widest UCP class. In lowering the input is itself a function of the class's
code-point SET (normalized intervals → ordered boxes), so the output is a
function of the set: canonical PER SET, which is all G5 and Gate U3 need.
Last-first matches the measured partial merges (β → `ce [92 b2] | cf 90`).
At code-point level (2b) the input order is the user's priority order and no
canonicalization is possible or wanted.

### 3.4 Concatenation and per-length pieces (r2: OWN-3, ruling O4)

**What the owner does with concatenation: nothing, by design.** The byte-level
owner sees one class at a time (§4.1's splice argument forbids neighbours), and
the code-point owner one alternation. Concatenation is composed in the FACTS,
by the description's CAT arm (§3.5), which is where "considering alternation
concatenation" is answered: `(?i)αβγ`, `(?i)abcdÀefgh` and every fold beside
literals become one run because the CAT arm joins the ALT arms' exact or hull
positions. Tables (G5) get no cross-alternation rewrite; [DFA-ALPHA-MERGE] is
the general answer for them.

**Concatenation through a mixed-width alternation (O4).** A mixed letter
(`(?i)о` = `d0 be | d0 9e | e1 b2 82`; Kelvin `(?i)k` = `6b | 4b | e2 84 aa`;
37 simple-fold classes) has WIDTH GROUPS (per byte length) and no position
product across them. Distributing the neighbours into the groups gives one
fixed-width PIECE per total length:

    X (G2 | G3) Y   =   X G2 Y  |  X G3 Y

The CAT arm therefore carries, per subtree, a small set of width groups, each a
position-set sequence (a hull per width: a superset, O1); CAT is the product
(widths add, sequences concatenate, groups of one total width hull-merge),
ALT the union (same-width groups hull-merge). `(?i)москва` (о, с, в mixed:
U+1C82, U+1C83, U+1C80) gives four pieces, widths 12 to 15; the width-12 piece
is `d0[9c bc] d0[9e be] [d0 d1][81 a1] d0[9a ba] d0[92 b2] d0[90 b0]`, which
the run walk ALREADY reports as a 12-position run when the piece is spelled as
a byte pattern (`req_whole_run d09cd09ed081d09ad092d090/ffdfffdffedfffdfffdfffdf`,
measured, cube domain, no stage 3 needed). Kelvin in `(?i)xyzkabc` gives a
7-byte and a 9-byte piece.

**The soundness statement of a piece set**: every match contains, at
contiguous offsets, a substring in ONE of the pieces' position products. A
single-run reader cannot use it (no one piece is in every match); it keeps
reading the single run, derived as today (the common head and tail across the
groups, `off` from `maxw`).

**PROMINENT (stop-rule check on O4).** The piece set is sound and computable
now, but **no consumer that pcrec ships can use it**: every pcrec run reader
needs ONE run in every match, and searching for "one of these runs" is a scan
FORM, which is the kit's choice (D157). The nearest sound form, adopted:
stage 2p computes and states the piece set as a core fact (the description's
CAT/ALT arms), shows it in `--emit-facts`, and the manager files a request to
the kit asking whether a form exists that consumes it; the fact crosses the
seam inertly (D157's own precedent: zero movers until a kit row consumes it).
`ci-moskva`'s witness at stage 2p is therefore a FACT witness (§5 S-p), and
its speed witness arrives with the consumer. If Frank wants pcrec's own
derived pick to consume pieces before the kit does, that is a new pcrec-side
scan form and a question (§13 q1).

**Bound.** The group count is bounded by a declared limits row whose value the
stage 2p census sets (no silent default: the census reports the distribution
over corpus and bench; `ci-moskva` needs 4). Over the bound a subtree's groups
collapse to today's common head/tail (sound, today's answer).

### 3.5 The wider general form: one description per fixed-width piece (r2: SLOT-6, ruling O5)

Every fixed-width, capture-free piece of a pattern has ONE description: a small
set of width groups, each a sequence of position SETS with an `exact` bit,
built bottom-up over the lowered tree. The arms:

| node | description | stage / row |
|---|---|---|
| CLASS | one group, width 1, one position (the set) | today (`rb_class_into`); sets at stage 3 |
| EMPTY | one group, width 0: the UNIT of CAT | stage 2a ([REQ-EMPTYCAT] direct half), owned by the kind row (§3.6) |
| CAT | product: widths add, sequences concatenate, same-width groups hull-merge | today for one group (`rr_cat`); several groups at stage 2p |
| ALT | union: equal-width groups hull-merge (`all` survives iff every branch exact and the union exact); this note's normal form is ALT's REWRITE side | stage 2a (one width), 2p (several) |
| REP{n,n} | power: the body's description n times (truncated at the run storage bound) | [REPEAT-RUN] (later) |
| REP{m,n}, m < n | head = body^m and tail = body^m as affixes, nothing exact across | [REPEAT-RUN] (later) |
| positive LOOKAROUND | a NON-CONSUMING piece at an offset: a lookahead's fixed prefix at offset 0, a lookbehind's fixed suffix at offset −width; it INTERSECTS position-wise with the consumed pieces it overlaps and extends the run where it reaches past them | [REQ-LOOKAROUND] (later) |
| negative lookaround, backref, variable, call | walls (no description) | unchanged |
| a variable-width subtree | no description; its fixed head and tail affixes are descriptions at its edges (`rr_alt`'s common head/tail rule) | today |

Readers: the required run (the best stretch of a group; one run when one
group; the piece set when several), the VM island (a small exact description
is a word list: A-ISL's decision), altcls/the owner (the `exact` bit and the
fixed-position sequence decide whether a rewrite is legal). The note's rewrite
owner is the ALT arm's rewrite side; the facts walk (`req.c`'s `RbRuns`,
generalized) is the description's home. Neither API is frozen ALT-only: the
stage 2a/2p build lands the description with its group list even though only
CLASS/EMPTY/CAT/ALT fill it.

### 3.6 The unit's owner is the kind row (r2: SLOT-2)

`kindrow.def:61` classes `A_EMPTY` as TEXT `ZERO` ("no bytes, ever (an
assertion, `\K`, a lookaround)"). Stage 2a adds a TEXT value, proposed `UNIT`
("no bytes and no test: the identity of concatenation"), for `A_EMPTY` alone.
`req.c`'s row reader maps `UNIT` to `rr_unit`; `endwin.c:301` and
`vm_isl_words`'s `A_EMPTY` arm read the row instead of their private tests;
every other `ZERO` reader (`nfa.c:598`, `mrl.c:487`, `possessify.c:446/501/924`,
`startset.c:83`) treats `UNIT` exactly as `ZERO` and its brief line says so.
The row is `-Wswitch`-complete, so a missed reader is a compile error.
Assertions stay `ZERO` (cut): treating a zero-width test as the unit is sound
for the run (consumed bytes stay contiguous) but its population is unmeasured
(D77), so it stays a decline with its own census question in [REQ-EMPTYCAT].

## 4. The seven questions, decided

### 4.1 Where the normal form lives (Q1) — kept

**Decision: one owner (§3.3), two callers, staged: lowering first, altcls
second.** A single post-lowering pass over USER alternations is ruled out: it
would rebuild nodes that contain group roots, and `pcrec_callgraph_build`
caches `u.call.body` pointers into the tree; `pcrec_lower_enc` is legal below
the call graph only because it SPLICES IN PLACE. So the byte-level call sits
inside `lower_class_utf8` (new nodes only) and the code-point-level call sits
in `altcls`, which already runs before the call graph and already rebuilds.
Lowering-only would leave user alternations on the old path, the parallel
mechanism Frank asked to remove; hence both callers, in two stages with
different kinds (§5).

### 4.2 Exact vs superset, and what `all` means (Q2) — kept, ruled (O1)

**Decision: superset hulls ARE allowed into facts; exactness is required only
for rewriting.** The run is already a product of position sets (`rr_pos` sets
`all` for a cube; `frank|fred` reports `fr[ae]`, measured). The statement every
reader relies on: *every match contains, at contiguous offsets, a substring
whose i-th byte is in position i's set; the run begins at most `off` bytes into
the match*. `all` (internal to `req.c`) means "every match of this subtree is
exactly `head.n` bytes and its i-th byte lies in `head` position i". Stage 2a
corrects the stale `RbRuns` comment ("EXACTLY the one literal string") and
extends `all` to alternations per §6.

**(r2: SND-6)** A cube-wanting reader of a non-cube set position (stage 3)
takes the cube HULL (the closure `K' = Ka & Kb & ~(Ta ^ Tb)` over the members,
a superset, sound) or declines the position; it never uses
`pcrec_cube_of`'s `false` as "no constraint" and never ANDs members without the
hull mask.

**Reader audit** (every reader of `ReqRun`/`RbRun`; r2: PREM-6 adds the rows
marked +):

| reader | reads | exactness assumed? |
|---|---|---|
| `src/facts/facts.c` `pf_derive_req_walk` | bit count vs `PCREC_MIN_REQ_RUN_BITS` | no |
| + `src/facts/facts.c` `pcrec_fact_stamp_req_run`, `pcrec_fact_stamp_req_byte` | rendering; the byte stamp exact positions only | no |
| `src/facts/req.c` `pcrec_req_window` → `src/core/findings.c` `pcrec_find_run_scan_index`, `pcrec_find_run_window_start` | rate over (byte, mask) via `cube_mass` | no |
| `src/facts/req.c` `pcrec_req_pick` | the scan member only if `mask == 0xFF` | no |
| `src/facts/kset.c` `pcrec_run_pin` | exact positions only | no |
| `src/facts/facts.c` landmark / `req_landmark_maxoff`; `src/gen/emit_dfa.c` `req_handoff_applies`, `req_handoff_entry_applies`, `req_handoff_k`, + `req_handoff_attempts_applies` | `maxoff`/`whole_maxoff` bounds | no |
| `src/gen/emit_dfa.c` `req_run_tests`/`ofs_test_run`, `req_pres_spans`, `req_site_define`, `emit_req_handoff_rest`, + `req_part_window`, + `req_run_member` | masked compare / kit presence spans / position cubes to the kit | no |
| `src/gen/memfn_sites.c` `pcrec_memfn_wpos_cube` | (T, K) to a 256-bit set | no |
| `src/gen/emit_dfa.c` `ofs_test_verifies_run`, + `walk_proves` | members ⊆ cube | no |
| `src/gen/emit_dfa.c` `req_whole_holds_byte`, `req_parts_in_whole`, `req_set_leads_own`, `req_rest_own_sig` | exact positions only | no |
| `src/gen/emit_dfa.c` `req_landmark_hit_ppm` | product of position masses | no (conservative) |
| `src/gen/emit_dfa.c` `pf_window_of`, `pf_run_applies_common`, `ofs_test_of`, `req_byte_dominated_by`, `req_none_applies`, `req_set_leads_applies`, `req_pick_shadow`, `emit_orientation_block`, + `req_note_run`, + `pcrec_emit_prologue` (stamps) | length, index, pin, rendering | no |

NOTED (r2: PREM-6, SUSPECTED, unreached in 6 probes): `ofs_test_of` builds the
C-pin run term with `run_mask` NULL, so `ofs_test_at` renders a walk-proven
masked position as the exact byte T in the `<PREFIX>_DFA_PREFILTER_OFFSETS`
stamp/comment (answers unaffected: T is a member). Stages 1-3 create more
masked positions beside exact stretches; the stage 1 build lane re-probes it.

### 4.3 Cube domain first, or wait for D187 set positions (Q3) — kept, ruled (O3)

**Decision: do not wait for stage 1; stage 3 rides with [POS-ONE-DETECTOR].**
Stage 1's rewrite is a property of the tree: cube domain first gives 513 → 766
(exactly, Gate U2) with no `req.c` change; set positions are stage 3 (+253
exact non-cube, +398 superset hull at an unbounded member count; 1403 at the
ruled bound 2, 1416 at 3, 1417 at 4: r2, SIM-1).

### 4.4 The information of a set position, the floor, and the member bound (Q4)

**Decision: `info(S) = 8 − ⌈log2 |S|⌉`; the floor stays 16 bits.** It equals
`popcount(K)` for every cube, so every run representable today ranks exactly
as today; it never overstates a position.

**(r2: SIM-1) The member bound.** `PCREC_MAX_REQ_RUN_POS_SET` = 2 is RULED
(`limits.def:411`): "every position must be a scan candidate and the emitted
scan has two arms". Stage 3 keeps 2 as its starting value and states every
figure at 2 (1403). It proposes, as a CHOICE row with evidence, to decouple
the FACT bound from the SCAN bound once positions cross the seam as sets
(D187): the ruled reason is about scan candidates, and after [POS-ONE-DETECTOR]
which positions are scanned is the kit's choice (D157); a 3-member position
can be a verify-only position. The evidence that moves it: stage 3's census at
bounds 2, 3 and unbounded, and a bench cell whose pick changes because of a
wider position, under the per-regime bar. Until then 1416/1417 are not
promised.

**Ranking risk**, declared table:

| row | condition | action |
|---|---|---|
| R1 | today's runs (no non-cube position) | today's `rn_better`: higher info, `a` on a tie |
| R2 | a candidate carries a set (non-cube) or superset-hull position | same ranking, AND the stage census LISTS every compile whose picked run changed from all-exact to one with such a position (r2: SIM-7: a listing, no pass/fail of its own) |
| R3 | R2's listing shows a regime where the flipped pick loses beyond noise | narrow (D186): the walk carries the best all-exact run beside the best run as a second core fact, and the rate-aware derived pick chooses; built only then (D77) |

**(r2: SIM-7)** The real-text regime (Cyrillic and Greek prose) is a REQUIRED
regime of stage 3's D186 evidence BEFORE it lands, not a later R3 trigger:
lead-byte-heavy text is exactly where a long superset run (5 caseless betas,
65 bits) outranks a shorter exact one.

### 4.5 Mixed widths (Q5) — revised (r2: SLOT-4, OWN-3, O4)

**Decision: two mechanisms, both existing rules read over more input, none
new.** (a) The single run's affix across a mixed letter is `rr_alt`'s existing
common head/tail rule read over set positions (stage 3); rev 0's separate stage
3m duplicated it and capped it at one position (SLOT-4: today
`abcd(?:ab|Abyz)` already keeps two affix positions across widths 2/4), so 3m
is folded into stage 3. For о the rule gives head `{d0,e1}{9e,b2,be}` and tail
`{d0,b2}{82,9e,be}` at a member bound ≥ 3; at bound 2 head 1 position, tail
none. (b) The full-width run per length group is the piece set (§3.4,
stage 2p, O4). [SEQ-FOLD]'s 1:n folds are later inputs to the same width
groups (ß ↔ ss is a two-group alternation); they are no longer the trigger for
the simple-fold mixed letters (r2: OWN-3).

### 4.6 The string-set fact for the kit (Q6) — revised (r2: OWN-5)

**Decision: the hand-off stays SETS.** For an exact product the per-position
sets lose nothing. A "one of these N strings" fact carries strictly more only
for non-product languages (user keyword alternations, and mixed-width folds:
the correlation between positions). Stated as a fact (D157): "every match
contains (or begins with) one of these N strings"; nothing about how it is
consumed. Stage 2p's piece set is the bounded-width case of exactly this fact
(one position-set sequence per length instead of one string per branch).

The case for it, pcrec-side and measurable, then a question to the kit:
1. on a bench cell, the hull window's candidate rate exceeds the string set's
   own rate on the cell's text by enough that the excess verify work is a
   measurable share of the cell's time (both rates from the same text,
   computed by pcrec from the facts; no kernel needed);
2. the manager files a REQUEST to the kit with that measurement, asking
   whether a form consuming the fact does better; the kit answers (its scalar
   or its SIMD layer alone may make the case, D144 add. 4: a SIMD-only win
   qualifies, as criterion 4 says);
3. the gain survives a random-like regime (D186 add. 2).
Mixed-width folds are a candidate population for item 1 (`ci-moskva`), not
excluded (r2: rev 0's "folds alone never make the case" and its named kernel
family are dropped). The cap N is the kit's request, not set here.

### 4.7 Sequencing and the abi question (Q7) — abi call REVERSED (r2: PREM-2, SLOT-1)

- **After span_pick unit 1e lands** (D153 remodel first): any change to
  `req_run` content moves the run positions handed to the kit
  (`pcrec_memfn_wpos_cube`), its arms and witnesses, and would contaminate
  1e's REACH EQUALITY. Every stage builds after 1e.
- **Stages 1, 2a, 2p and 2b do not wait for [POS-ONE-DETECTOR]**; stage 3 rides
  WITH it (O3; manifesto principle 4).
- **Every stage that moves emitted bytes is an abi event.** `match_api.md`
  §6¶19 fixes the emitted output byte-exact, whole-file, within one `abi`;
  §6¶18 lists a moved table among bump causes; the ruled reading (D168 add. 3)
  keys the abi on emitted text; the precedents are [OPT-REQRUN-ENC] (37 → 38,
  a utf8-only `REQ_RUN` value and `memchr` target move) and R-30 (93 → 94,
  program text alone). Stage 1 moves `RX_REQ_RUN` values and tables on utf8
  artifacts and, under `-fno-cls-kit`, the VM's `empty` label the seal emits
  (`(x)(?i)À`: `L2 label empty`, `RX_VM_PROGRAM_BYTES 1502ULL`). Rev 0's "NOT
  an abi event" is withdrawn; the lowering comment and [LOWERENC-SEAL]'s row
  were right. Each stage brief carries, as REQUIRED steps: the bump to the next
  number at landing, the abi changelog entry, the D94 grep of every reader of
  the number (the `.abi` stamp, test expectations, every spec sentence, the
  identity gate's (B) pin), re-pins in the same change, `make test-codegen`
  and the suites that count (registry, codegen, rxtsource). The (B) identity
  population compiles at `byte`, so stage 1 turns neither pin red; the
  obligation is the contract, not the gate. Stages may land under one bump if
  they land together.

## 5. Staging (each stage: kind per regime, change, gates, predicted movers, sabotage witnesses, deletions)

All stages: no edits until Frank's build go; each stage is its own branch and
landing (2a and 2p may share one); `make test`, `make strict`,
`make test-axes` (answer identity on every axis, including `-fno-cls-kit`),
REACH for every new mech row, and the abi ritual of §4.7. **(r2: lesson 1)**
Every sabotage witness below states why it can FAIL: for an answer witness on a
tree rewrite, the sabotaged rewrite spelled as a pattern and run against
libpcre2 (no floor applies: the rewritten tree IS the matcher); for a fact
witness, the run it targets clears the 16-bit floor and the position domain in
BOTH the correct and the sabotaged build, and the tested window covers the
position (a REACH line per position).

### Stage 1 — UTF-8 lowering calls the owner (r2: kinds per regime, O2)

- **Kind.** Byte: NO change (B0). Utf8: a UNIT change (the same language,
  smaller tables, longer runs) except on the cells whose derived scan pick
  FLIPS, which are CHOICE cells under D186 (r2: OWN-6): predicted
  `ci-greek-run` (offset-set → handoff); others listed by Gate U4's census. On
  a loss in such a cell the narrowing applies to the pick row that flipped
  (its condition gains the regime fact), never to the lowering. Deny lever:
  per "flag follows caller effect", a public deny because the pick can be
  slower (decided at build, §11).
- **Change.** `lower_class_utf8` hands `u8_box`'s boxes to the owner (sibling
  merge, position-major last-first, §3.3) and returns the merged form; the seal
  is deleted; `req.c` is untouched. **(r2: PREM-1)** `vm_isl_words` reads a set
  position INSIDE an `A_WCLASS` as its members (a set edge becomes its member
  edges, under the island's existing word cap), so the island's word list is
  today's word list; outside an `A_WCLASS` it still declines a class, so byte
  artifacts cannot move (no `A_WCLASS` under `-e byte`). Closes
  [LOWERENC-SEAL] with the bump.
- **Gate B0 (zero byte movers, REQUIRED).** (r2: OWN-6, K35) Population:
  `scripts/emit_sweep.py --ref BASE --bases byte` (its pinned streams: corpus
  argv at the default engine and at `--engine=vm`, `--emit-ir`, the
  `--source` composition stream over every `.rxt`/`.rxtin`, `--emit-facts`;
  `--features all`, the options source being the corpus argv files and each
  `.rxt`'s own directives, its floors the counted population) plus every
  `pcrec-bench/bench/*/patterns/*.rx` compiled `-e byte`. Empty emit diff; a
  pattern refused under byte (e.g. `(*UTF)`) must be refused identically and
  is counted, not dropped. Also empty for every `-e utf8` compile whose
  classes are all ≤ 0x7F (narrow under utf8: `.`, negated classes, `\D\W\S`
  and `(?i)k`/`(?i)s` all reach above 0x7F, PREM's note).
- **Gate U1 (movers predicted from an independent model, two-sided).** (r2:
  SIM-3) The predicate is computed by a script that shares no code with the
  compiler: it splits each class's code-point set into UTF-8 boxes, runs the
  §3.3 strategy, and predicts "moves" iff the class has more than one box
  (the seal goes) or a merge fires. Populations with an exact prediction:
  the 1454 fold classes in `abcd<X>efgh` and the 76 `bench/utf8` patterns
  (classes extracted by the script; a pattern it cannot parse is listed as
  UNPREDICTED and reported, K35). Gate: observed movers = predicted movers on
  those populations (a predicted mover that does not move is a finding too).
  The corpus beyond them: movers listed with the class predicate, gated
  one-sided only through B0's ASCII clause.
- **Gate U2 (the fold census, independent control).** `foldsweep.py` on the
  stage build: classes keeping the `abcd<X>efgh` run = 766 EXACTLY (24 + 489
  + 253, predicted from CaseFolding.txt by `shapes2.py`).
- **Gate U3 (no table growth, per machine).** (r2: PREM-5, SIM-8) Every utf8
  mover's next-state entry count ≤ base, compared machine by machine
  (forward, reverse, anchored); a whole-pattern class's machine SET can change
  (the `landing` start needs `land_char`, which a byte spelling cannot have), so
  totals are not compared. Growth is a finding to explain.
- **Gate U4 (speed, per regime).** Bench on every utf8 mover: no regime slower
  beyond noise (unit cells); no regime loses beyond noise (the pick-flip choice
  cells, listed with per-regime numbers and the row each would narrow).
  (r2: PREM-1) Plus a VM island census: `RX_VM_ALT_ISLANDS` equal base vs stage
  on every utf8 corpus and bench compile, default and `-fno-cls-kit` axes,
  `--engine=vm` and auto.
- **Predicted movers** (r2: O2, SIM-4, SIM-5; byte spellings of the stage-1
  tree, §8): runs `(?i)abcdÀefgh` 6 → 10, `(?i)Ελληνικά` 0 → 10,
  `(?i)привет мир` 0 → 7, `(?i)naïve café` 8 → 12, `(?i)αβγ` 0 → 3; tables
  `(?i)москва` 1140 → 900, `(?i)Ελληνικά` 1430 → 1040, `(?i)αβγ` 160 → 112,
  `(?i)é` 12 → 9. CERTAIN movers beyond the folds: every utf8 compile with
  `.`, a negated class, `\p{..}`, `\W`, `\D`, `\S` or another multi-box wide
  class (dot's 3-byte bands differ at one position: byte-spelled `x.y`
  480 → 448, `.*foo` 495 → 462; directions only, the byte control is not exact
  for dot); 20 of 76 bench/utf8 patterns (`cls-dot*`, `cls-neg-*`, `prp-*`,
  `qnt-dot-bounded`, `lit-mixed-ascii`, `ci-neg-fold`). Bench/utf8 cells:
  `ci-greek-run` (run and pick), `ci-moskva`, `ci-strasse`, `ci-e-acute`,
  `ci-ucp-invariance` (tables), `ci-kelvin`/`ci-long-s` (tables, compared per
  machine), `ci-sigma` (none predicted). Any pinned utf8 whole-file fixture
  holding one of these re-pins under the abi bump.
- **Sabotage witnesses.**
  - S-a (merge accepts pairs differing in TWO positions): `(?i)β`
    (`ce 92|ce b2|cf 90`) against `ΐ` (`ce 90`): NOMATCH expected; the
    sabotaged `[ce cf][92 b2 90]` matches. Answer witness; held by the critic
    round.
  - S-b (the merge aligns branches of unequal width, (r2: SND-5) subjects
    widened): `(?i)k` against `K`, `k`, the Kelvin sign `e2 84 aa` (expected
    (0,3), measured; a truncating `[4b 6b e2]` sabotage gives (0,1)) and the
    truncated `e2 84` (NOMATCH, measured).
  - S-i (r2: new, PREM-1; the island's set-edge reading enumerates only the
    lowest member): `x(?:[éà]1|q2|r3)y` under `--engine=vm -e utf8` against
    `xé1y`: (0,5) expected (measured today, island count 1 today); the
    sabotaged island has no `é` word. REACH: `RX_VM_ALT_ISLANDS 1` in both
    builds.
  - K123: `(?<=[a\x{3b1}])x` keeps compiling and matching `αx` with the seal
    gone (the `A_WCLASS` wrapper is load-bearing, keep it).
  S-ids from the range the build brief names.
- **Deletes.** The seal (two nodes and its comment).

### Stage 2a — the ALT and EMPTY arms: `rr_alt` reads the hull, `A_EMPTY` is the unit (CHOICE, byte and utf8)

- **Why now, against D77** (r2: OWN-2, OWN-6): the population is MEASURED
  BEFORE the build go, as the stage's first deliverable and its trigger: an
  independent model (the description's arms re-implemented in a script, run
  over byte spellings of the lowered trees, the method of `pred.py`) over the
  corpus and bench, both encodings, listing every compile whose run moves.
  The trigger is a bench cell among them. The fold population it should find
  is the 132 equal-width classes whose hull is a cube of ≤ 2 members (766 →
  about 898, G4); `ci-greek-run` is NOT among its movers (β's second-byte
  hull `{92,b2,90}` is out of the cube domain, so its 3-position run comes
  from stage 1 and its 6 from stage 3 at bound 3). If the census lists no
  bench cell, stage 2a waits (D77) and 2p goes alone.
- **Change.** `rr_alt` per §6's table (rows 1, 2; 1b if adopted); the kind
  row's `UNIT` value (§3.6) with `req.c` reading it as `rr_unit`. Cube domain
  (`pos_set` 2).
- **Predicted movers** (r2: SIM-6/SLOT-7 moves the flagship here): `abcd()efgh`
  4 → 8, `abcd(?:|)efgh` 4 → 8, `abcd(?:ab|ab)efgh` 6 → 10,
  `(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)` 4 → 6, `(?:ab|aB)xy` 3 → 4 (altcls leaves
  `a(?:b|B)xy`; row 1 reads `a[bB]xy`), plus the census list.
- **Gates.** The census (observed movers = the model's list, two-sided); R2's
  listing; per-regime bench on every cell whose pick moved (choice bar).
- **Sabotage witnesses.**
  - S-c (r2: PREM-3, SND-5; `all` set without the equal-width test):
    `xy(?:ab|abc)zw` against `xyabczw` (expected (0,7), measured) and against
    `xyabzw` ((0,6), measured; catches the form that takes the LONGER width).
    Correct run `xyab` (32 bits, measured today); sabotaged `xyabzw` (48
    bits); all exact bytes, so both clear the floor and the domain; the
    sabotaged pre-check rejects `xyabczw`. Rev 0's `xy(?:ab|cde)zw` could not
    fail (`[bd]` is out of the cube domain).
  - S-g (r2: new, SND-5; the row reader's `UNIT` arm widened to a consuming
    kind, the `ANY` value): `(ab)x\1y` against `abxaby` (expected (0,6),
    measured). Correct run `abx` (24 bits, measured today); sabotaged `abxy`
    (32 bits); the subject has no `abxy`, so the sabotaged pre-check answers
    NOMATCH.
- **Deletes.** `o.all = false` (replaced by the row table); the three private
  "empty is the identity" spellings (one row value).

### Stage 2p — per-length pieces (r2: new, O4; CHOICE when a consumer exists, a fact until then)

- **Change.** The description's CAT and ALT arms carry width groups (§3.4);
  the piece set is a core fact in `--emit-facts` (name at build); the single
  run is derived exactly as before, so no pcrec artifact moves. The manager
  files the kit request (§3.4).
- **Kind.** A new FACT with zero pcrec emitted-byte movers (no abi event while
  inert; `--emit-facts` names are advisory, `facts_listing.md`); it becomes a
  choice change, with its own bar and witness, when a consumer row lands.
- **Gate.** The piece lists over the 37 mixed-width fold classes in
  `abcd<X>efgh` and over `bench/utf8` equal an independent model's (from
  CaseFolding.txt, no compiler code); `ci-moskva`: 4 pieces, widths 12 to 15,
  the width-12 piece the 12-position run of §3.4 (measured by spelling).
- **Sabotage witness S-p** (a CAT product that keeps only the shortest group):
  `(?i)москва`'s piece list loses widths 13 to 15 and differs from the model.
  It is a FACT witness and cannot move an answer while the fact is inert
  (lesson 1, stated); the answer witness ships with the consumer.

### Stage 2b — altcls calls the owner (CHOICE, byte and utf8)

- **Change.** altcls's merge and its one-byte-key factoring become the owner's
  rules over its alternation spines (§3.2, §3.3): sibling merge under the
  adjacency test, prefix factoring on a fixed-width capture-free key over
  consecutive branches (a branch equal to the key stays as EMPTY in its slot,
  today's behaviour generalized), suffix factoring over adjacent branches.
- **Predicted movers** (r2: SIM-6/SLOT-7): TREE-level, not runs: VM program
  bytes, DFA table entries, the VM island census (altcls collided with the
  island once: `w-256` got 11 islands, 3.0% larger); multi-byte keys
  (`(?:abx|aby|abz)q` → `ab[xyz]q`), suffix factoring (`(?:xing|ying)` →
  `[xy]ing`). The census is the stage's first deliverable.
- **Overlap** (r2: slots): A-ISL (roadmap R04, HELD) — 2b changes the tree
  `vm_isl_words` enumerates; listed in the D153 remodel-overlap column.
- **Gates.** Answer identity; `tests/altcls/` and its stamps; the census;
  per-regime VM evidence.
- **Sabotage witnesses** (r2: SND-4; measured against libpcre2, `premise.out`):
  - S-d (a merge crossing an unequal-width sibling): `(?:ab|a|ad)` against
    `ad`: (0,1) expected; the correct owner gives `a(?:b||d)` ((0,1),
    measured); the sabotaged `(?:a[bd]|a)` gives (0,2). Also `(?:for|fo|fox)`
    / `fox` (0,2) vs (0,3); the suffix form `(?:ac|x|xc)` / `xc` (0,1) vs (0,2).
    These reach altcls today (`RX_ALTCLS_FACTORED 1` on all three).
  - S-k (a variable-width prefix key admitted): `(?:a|ab)c|(?:a|ab)b` against
    `abc`: (0,3) expected; the sabotaged `(?:a|ab)(?:c|b)` gives (0,2).
- **Deletes/merges.** altcls stage 1 and stage 2 as their own mechanisms; the
  single-byte key.

### Stage 3 — set positions in the run (CHOICE; rides with [POS-ONE-DETECTOR], O3); 3m folded in (r2: SLOT-4)

- **Change.** `RbRun` positions become 256-bit sets (D187); a cube is derived
  by `pcrec_cube_of` where a reader wants one, and a non-cube position is
  read by its hull or declined (§4.2); `info` per §4.4; the member bound per
  §4.4 (2 unless its evidence moves it). `rr_alt`'s common head/tail rule over
  sets IS the mixed-letter affix (rev 0's 3m). The two spellings of "a
  position" in `req.c` merge; the hull's home (`cpset` or the kit's side) is
  left to the kit-split ruling (r2: SLOT-8; until stage 3 there is one hull in
  the facts, `req.c`'s cube closure, since the owner no longer has one).
- **Predicted movers** (at bound 2): fold classes keeping the run about 898 → 1403 (1416 at bound 3);
  `ci-greek-run`: at bound 2 the run stays the 3 positions `ce[91 b1][ce cf]`
  (22 bits) that stage 1 already gives; 0 → 6 needs bound 3 (β's
  tail `{92,b2,90}`); `ci-strasse`, `(?i)select`, `(?i)information_schema` affixes per the
  re-derived model (r2: SLOT-4: `pred.py`'s s3 column modelled a cut, its s3m
  one position; the stage census re-derives both with today's head/tail rule).
- **Gates.** Every §4.2 membership reader moves to sets in the same change
  (one detector); the R2 listing; per-regime evidence INCLUDING real
  Cyrillic/Greek text before landing (§4.4).
- **Sabotage witnesses.**
  - S-e (r2: SND-5; the hull drops a member): `(?i)xyzβw` against `xyzϐw`
    (`78 79 7a cf 90 77`, (0,6) measured). Correct run at bound 3:
    `[xX][yY][zZ]{ce,cf}{90,92,b2}[wW]` (41 bits); sabotaged without `cf`
    (42); both ship; the 6-byte run lies inside the 8-byte emitted window, and
    REACH shows position 3 tested. At bound 2 the run is `[xX][yY][zZ]` either
    way and S-e cannot fail: S-e is a bound-3 witness, stated.
  - S-f (r2: SND-3; the mixed-letter affix misses the long member's first
    byte): `(?i)xyzk` against `78 79 7a e2 84 aa` ((0,6) measured). Today's run
    `[xX][yY][zZ]` (21 bits, measured). At bound 3 the correct affix
    `{4b,6b,e2}` gives 27 bits, the sabotaged `{4b,6b}` 28: both ship, the
    sabotaged one rejects the Kelvin subject. At bound 2 the correct build
    keeps 21 bits (the 3-member affix is out of bound) while the sabotaged
    2-cube is IN bound (28 bits): S-f fails the sabotage at either bound.
    Rev 0's `(?i)xk` was under the floor in both builds.

## 6. Decisions as declared tables

The stages add rows, never branches in code:
- **(r2)** the rewrite owner's rule table, first match per candidate pair or
  consecutive run: (1) the adjacency test fails → keep; (2) consecutive
  branches share a fixed-width capture-free prefix key → prefix-factor (a
  branch equal to the key stays as EMPTY in its slot); (3) adjacent branches
  share a suffix → suffix-factor; (4) equal width, differ at exactly one
  position → merge (exact); (5) otherwise → keep both.
- `rr_alt`'s outcome table: (1) every branch `all`, equal untruncated width,
  hull in domain at every position → `all`, run = hull; **(1b, r2: SLOT-5,
  named later piece)** equal width, every branch `all`, hull out of domain
  somewhere → best = the best in-domain hull stretch at its offset, `all`
  false (`(?:xabcy|qabcw)` → `abc` at 1); adopted only if stage 2a's census
  lists a bench cell it moves; (2) otherwise → common head and tail (today's
  rule).
- the description's group table (stage 2p): one width → today's arms; several
  widths ≤ the bound → per-width hull groups; over the bound → common
  head/tail only.
- the ranking table of §4.4 (R1-R3).

## 7. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** Run lengths, table entries and artifact
   bytes in §8 are compile-time facts of this box's compiler (gcc 15.2, Zen 4).
   Every speed claim is owed per stage, per regime (bench/utf8 strata, a
   random-like regime, and real Cyrillic/Greek text for stage 3, before
   landing); a different regime can flip a run pick (§4.4). Table sizes are
   compared per machine (r2).
2. **Independent control: RELEVANT.** Stage 1: base-vs-stage emit diff over
   `emit_sweep.py`'s pinned byte populations plus the bench (the base compiler
   cannot contain the owner); U1's mover prediction and U2's keep count from
   scripts that share no code with pcrec; PC-3. Stages 2a/2p/3: the census and
   the piece lists against an independent re-implementation of the arms
   (K35: the population is the corpus + bench list, counted). Every sabotage
   witness states why it can fail in both builds (§5 preamble) and reaches its
   site (REACH per row, per position for run witnesses).
3. **What moves when data is regenerated: RELEVANT.** CaseFolding.txt (a
   `third_party/ucd-*` regeneration) changes fold classes and so the owner's
   input; the owner holds no table. A UCD bump moves utf8 caseless artifacts
   and the census numbers (1454/766/1403 are UCD 16.0.0's). **(r2)** That move
   IS an abi event by §6¶19 (emitted bytes move), carrying the D94 grep; no
   spec change beyond the abi entry (no caller-visible surface moves;
   `--emit-facts` values move as for any fact change).

## 8. Measured and inferred numbers

`altdesign_evidence/stage_pred.tsv` (`pred.py`). Columns: `today` = MEASURED
`-e utf8 (?i)TEXT`; `s0` = MEASURED control, today's lowering spelled as a
byte pattern (no seal, altcls denied); `s1` = MEASURED, the stage-1 tree
spelled; `s3` = INFERRED. **(r2)** The `s1` column spells partial merges
unmerged and so under-states stage 1 on β-like letters: the corrected
entries (SIM-5, spelled with the owner's real output) are in the last column;
`s3` is inferred at NO member bound and models mixed letters as cuts, so it is
superseded by stage 3's census (SLOT-4, SIM-1); rev 0's `s3m` column is
withdrawn with stage 3m.

| pattern | today | s0 | s1 | s3 (unbounded, cut model) | entries today → s1 (r2 corrected) |
|---|---|---|---|---|---|
| `abcdÀefgh` | 6 | 6 | 10 | 10 | 132 → 121 |
| `москва` | 0 | 0 | 0 | 0 (pieces: 4, width-12 piece 12 positions, §3.4) | 1140 → 900 |
| `αβγ` | 0 | 3 | 3 | 6 | 160 → **112** |
| `straße` | 3 | 3 | 3 | 3 | 462 → 429 |
| `é` | 0 | 0 | 0 | 0 | 12 → 9 |
| `σ` | 0 | 0 | 0 | 0 | 40 → 40 |
| `select` | 5 | 5 | 5 | 5 | 216 → 192 |
| `information_schema` | 12 | 12 | 12 | 12 | 1020 → 960 |
| `Ελληνικά` | 0 | 4 | 10 | 10 | 1430 → **1040** |
| `привет мир` | 0 | 4 | 7 | 7 | 1620 → 1296 |
| `naïve café` | 8 | 10 | 12 | 12 | 169 → 143 |

Readings: `s0` isolates the seal (αβγ, Ελληνικά, привет мир, naïve café gain
from its removal alone); `s1` adds the merge. **(r2: PREM-5/SIM-8, the k/s
caveat traced)** the byte spelling of a WHOLE-PATTERN `(?i)k`/`(?i)s` emits
72 entries against utf8's 48 because the utf8 compile takes the `landing`
start (the `land_char` fact: every one-character path ends dead or
accepting), which the byte spelling cannot (the one-byte path through `e2` is
neither), so it adds a reverse machine; per-machine tables are identical, and
an embedded class (`xk`, `kx`) controls exactly. The same artefact can hit any
prediction whose first character is non-ASCII whenever the utf8 compile takes
`landing`; the rows above match today because theirs did not.

## 8a. The owner's candidate solutions C1-C4, vetted (r2: OWNER ADDENDUM)

Probes: `altrev1_evidence/premise.tsv`, `c4.tsv`, `c4b.tsv` (outputs `.out`),
pcrec against libpcre2-8 10.46; capture vectors from libpcre2.

| id | candidate | verdict | evidence and condition | adopted as |
|---|---|---|---|---|
| C1 | facts are order-free: a run/set fact describes the string SET, not which branch wins, so stages 1, 2, 3 cannot meet SND-1 | **SOUND** | a fact is a necessary condition on every match; which branch wins changes the match, never the set of strings a match is drawn from (each match's matched text belongs to the alternation's language). The critic round's stage-2 and hull probes found no pattern whose real match the run rejects; SND-1/SND-2 reproduce only on tree rewrites | §3.1 (rewrite vs fact), O1; SND-1 confined to stage 2b |
| C2 | tree rewrites exact-only: prefix factoring on a FIXED-WIDTH key keeps a shorter branch as EMPTY in its slot (`(?:ab|a|ad)` → `a(?:b||d)`); merge only adjacent branches with no sibling between them matching a prefix or extension of either | **SOUND-UNDER-CONDITION**: the key capture-free as well as fixed-width; factoring over CONSECUTIVE branches; the "between" test decided on fixed-position set sequences and FAILED for any branch it cannot decide | `a(?:b||d)` = original on `ad` (0,1), `ab` (0,2), with continuation `adc` (0,3), with a following capture `(d?)` (0,2) both; `fo(?:r||x)x`/`foxx` (0,3) both; equal-width intervening sibling `(?:ab|xy|ad)z` → `(?:a[bd]|xy)z` equal. The prefix/extension test is complete: two matches at one start differ only by one being a prefix of the other. altcls stage 2 is already C2 with a one-byte key | §3.2 (adjacency test), §6 rows 1-4, stage 2b |
| C3 | priority-sensitive tries stay in the matcher: the VM island's sorted trie with priority-tagged accepts answers the lowest original branch index | **SOUND, already built** for singleton edges (`emit_vm.c` `vm_isl_build`: each end node's accepts tried in ascending ORIGINAL index, the continuation backtracking into the next; `alt_dispatch_study.md` §3.2). **SOUND-UNDER-CONDITION for set edges**: sibling edges must stay disjoint so the walk is one path (the emitted candidate list is a compile-time constant per node); overlapping set edges need a refinement into disjoint member sets first | stage 1 reads a lowered class's set edge as its members (disjoint singletons), so today's island is unchanged; caseless set edges for user words are U4, riding A-ISL | §3.3 (island not an owner reader), stage 1 S-i, U4 |
| C4 | a zero-width lookahead after the shorter branch | **UNSOUND** in its local form; the exact form is sound but buys no rewrite | local `a(?!d)`: `(?:ab|a(?!d)|ad)` on `ad` = (0,2) vs the original's (0,1); with a continuation `(?:x|dy)` on `ady` it loses the match entirely (NOMATCH vs (0,3)); with a capture `(d?)` the group moves (1,2) → (2,2). Exact form `a(?=X)`, X the WHOLE continuation: `(?:ab|a(?=X)|ad)X` equals the original on every probe, but it does not license the merge: `(?:a[bd]|a(?=X))X` with `X = (?:d|ddd)` on `addd` = (0,3) vs (0,2), because `ad·X` still runs before `a·X`. Guarding the merged branch with the negated continuation `(?:a(?!X)[bd]|a)X` is wrong for the `b` member: `X = (?:x|b)` on `abx` gives (0,2) vs (0,3). A correct guard needs a per-member guard holding the continuation, i.e. the continuation spelled again per branch: no reduction | not adopted; recorded here |

## 9. Unlocks and the general form's siblings (each with its trigger; r2: O5)

| id | unlock / sibling | stage and decision points | witness / trigger |
|---|---|---|---|
| U1 | [RUN-POS-SET] subsumed (stages 1, 2a, 2p, 2b, 3) | §5 | fired (rpsurvey); build waits for span_pick 1e and Frank's go |
| S1 | **[LOWERENC-SEAL]** — absorbed fully | stage 1 deletes the seal with the abi bump; nothing else to decide | stage 1's gates; the row closes with stage 1 |
| S2 | **[REQ-EMPTYCAT]** — the direct half is stage 2a (an empty node directly in a CAT or ALT: `abcd()efgh`, `abcd(?:|)efgh`, altcls's two-empties residue, derive's pruned nodes); the QUANTIFIED half is later | later follow-up decides: (1) DECIDED here: the unit lives in the kind row (§3.6); (2) whether a REP whose body is a width-0 `all` description is the unit for every {m,n} (`(?:)*`, `(?:){3}`; [REPEAT-RUN]'s rule at width 0); (3) whether a zero-width ASSERTION under a repeat (`(?:\b)+`, `pcrec_wrap_bare_anchor`'s `<anchor EMPTY>`) stays a D77 decline or gets its census; (4) the producer census over corpus and bench; (5) whether the row closes into stage 2a or stays open for the REP half. The row's FLAG-SPELL symptom (`a(?i)bc`) is already gone | trigger: stage 2a's census listing REP-cut runs on bench cells, or [REPEAT-RUN]'s census; witness: `abcd(?:)*efgh` 4 → 8 |
| S3 | **[REPEAT-RUN]** — the REP arm (power) | later follow-up decides: (1) REP as the description's power arm (this note's position) vs a `req.c`-local rule; (2) the iteration-boundary join's soundness and its sabotage witness (reqpos_2b.md §2.4 declined it for want of one); (3) a declared size bound on n (run storage truncation, `head.trunc`), no silent default; (4) the VM half (counter loop vs one memcmp) as a separate CHOICE row with per-regime evidence and its A-ISL overlap; (5) the prefilter's count collapse (`NFA_ERASED_COUNT`) is unaffected, the run being AST-derived; (6) the population census (D77) | trigger: the row's census (`A{4}` none vs `AAAA` 4; `abcd(?:ab|Ab){2}efgh` 4 vs 6 spelled out); witness: `xy(?:ab){2}zw` 2 → 8 |
| S4 | **[REQ-LOOKAROUND]** — the positive-lookaround arm (O5) | later follow-up decides: (1) the non-consuming piece's offset, its INTERSECTION with the consumed pieces it overlaps (`a(?=b)[bc]` narrows `[bc]` to `b`; `a(?=bc)bc` keeps `abc`) and its EXTENSION past them (`a(?=bc)` → `abc` as a search condition; `bar(?=baz)` → `barbaz`, the piece `baz` at offset 3); (2) the fixed part of a VARIABLE lookaround adjacent to the cursor (the lookbehind body's fixed-width suffix, the lookahead's fixed-width prefix: `(?<=fo+)bar` → `obar` at −1); (3) every reader that assumes the run lies INSIDE the match (the landmark handoff, `req_whole_holds_byte`, the span verify) gets a flag or a separate fact: a lookahead run can end past the match, a lookbehind run begin before it; (4) the window: the scan may start before the start offset by up to the lookbehind width (PCRE2 lets a lookbehind read there; D172's negative span offsets); `req.c`'s header names this exact reason for not descending today; (5) negative lookarounds stay walls; (6) the span check (D172 spans to the kit) reads the same pieces | trigger: the row (filed and scheduled 2026-11-05); witness: `(?<=foo)bar` run `bar` → `foobar` at −3, and a subject where `bar` sits at the start offset with `foo` before it (`search_from` = 3 on `foobar`): MATCH expected, a window not widened back loses it |
| U2 | [SEQ-FOLD]'s 1:n folds become width-group inputs to the same description | §4.5 | [SEQ-FOLD]'s design note |
| U3 | the string-set / piece-set fact consumed by the kit | §4.6, §3.4 | §4.6's item 1 on a bench cell, then the kit's answer to the request |
| U4 | caseless VM islands for user words (set edges read from the description) | rides A-ISL (roadmap R04, HELD); C3's disjoint-edge condition | a VM cell with a caseless keyword alternation in the bench or a user report |
| U5 | [DFA-ALPHA-MERGE] | its row | an object-size or cache-pressure cell, or stage 1 landing |

## 10. What this note does NOT decide

- Any build go, or the order of the stages against other work beyond §4.7.
- The owner's file name and API spelling (the build lane, against
  `docs/dev/guide/coding.md`); only that the description is not ALT-only.
- The member bound's move above 2 (stage 3's choice row with evidence, §4.4).
- The piece-group bound's value (stage 2p's census) and the piece fact's name.
- The string-set / piece-set fact's consumer (the kit's answer, §4.6).
- [SEQ-FOLD]'s per-group offsets and captures across a fold image.
- The DFA alphabet re-merge (its own row).
- The hull primitive's home after stage 3 (the kit-split ruling, SLOT-8).
- Whether each stage's deny lever is public (memory: a public deny only if the
  row can be slower; a test-only lever otherwise): per stage, at build.
- The follow-up notes of [REQ-EMPTYCAT]'s quantified half, [REPEAT-RUN] and
  [REQ-LOOKAROUND] (their decision points are listed in §9, not decided).

## 11. Deny levers

Stage 1 can make a pick slower (a choice cell), so it gets a public deny; 2a,
2b and 3 likewise; 2p has none while inert. Spelled at build.

## 12. Proposed decision (D-next)

**Alternations have one rewrite owner and fixed-width pieces have one
description.** The owner rewrites exactly (sibling merge, prefix factoring on a
fixed-width capture-free key, suffix factoring), every move of a branch past a
sibling gated by one adjacency test; it is called above the call graph
(altcls, code points) and inside the lowering's new subtree (bytes). Facts come
from the description (CLASS = position, EMPTY = unit, CAT = product, ALT =
union with per-width hulls, later REP = power and a positive lookaround = a
non-consuming piece), which may use superset sets and never rewrites. Positions
cross the kit seam as sets (D187); the hand-off stays sets until §4.6's case
exists; mixed-width letters give per-length pieces, stated as a fact. Every
stage that moves emitted bytes is an abi event. Staged as §5, each stage with
its D186 kind per regime.

## 13. Open questions for Frank (plain words)

1. **Per-length pieces have no reader yet.** For `(?i)москва` pcrec can now
   say "every match contains one of these four byte patterns" (one per total
   length; the all-two-byte one is 12 bytes long). None of pcrec's own search
   code can use a "one of these" fact today; searching for one of several
   patterns is a search method, which is the kit's choice. Leaning: compute
   and state the fact now (as you ruled), ask the kit whether it can use it,
   and do NOT build a pcrec-side "search for one of several" form. The cost of
   the leaning: `ci-moskva` gets faster only when the kit answers yes.
2. **Wider sets per position after stage 3.** Today a run position may hold at
   most two byte values, because the old scan had two arms. Once positions go
   to the kit as sets, that reason is the kit's, not the run's. Should stage 3
   be allowed to propose three or more (it gets `(?i)αβγ` its full run, and 13
   more fold letters keep theirs), judged on its own measurements? Leaning: yes, as a
   measured choice, starting from two.
3. **Stage 2a only if the count shows a bench cell.** The change that lets an
   alternation of equal-width words keep its run (and the empty node stop
   cutting runs) has never been counted. Leaning: count first (a small
   measurement lane, no build), and build it only if a bench cell moves;
   about 132 more fold letters keep their runs by it, but which bench cells
   move is not yet known.

## 14. Disposition table (r2; every finding of review 2026-11-05-r2)

| id | disposition | where changed |
|---|---|---|
| SND-1 | FIX-NOW: adjacency test replaces width grouping; witnesses | §0.1, §3.2, §6, stage 2b S-d |
| SND-2 | FIX-NOW: prefix key fixed-width capture-free; suffix any | §3.2, §6, stage 2b S-k |
| SND-3 | FIX-NOW: S-f replaced (`(?i)xyzk`), fails at either bound | stage 3 S-f |
| SND-4 | FIX-NOW: S-d given SND-1's shapes, measured | stage 2b S-d |
| SND-5 | FIX-NOW: S-b subjects widened; S-c second subject; S-e reach per position; S-g for the unit arm | stage 1 S-b, stage 2a S-c/S-g, stage 3 S-e |
| SND-6 | DOC: cube reader of a non-cube position takes the hull or declines | §4.2 |
| PREM-1 | FIX-NOW: island reads set edges inside `A_WCLASS`; island census gate; S-i | §2.1, stage 1 change/U4/S-i |
| PREM-2 = SLOT-1 | FIX-NOW: abi call reversed; ritual required per stage; UCD bump too | §4.7, §7 q3, §2.2 (2) |
| PREM-3 | FIX-NOW: S-c replaced | stage 2a S-c |
| PREM-4 | DOC: NFA/DFA shape-sensitive | §3.3 table |
| PREM-5 = SIM-8 | DOC: k/s caveat traced; per-machine comparison | §8, Gate U3, G5 |
| PREM-6 | DOC: audit rows added; `ofs_test_of` NOTED | §4.2 |
| PREM-7 | DOC: boxes not code points; altcls stage 1 feeds stage 2; comment reading | §2.1, §2.2 (1) |
| SIM-1 | FIX-NOW: figures per bound (1403 at 2); one form of 766 | G4, §4.3, §4.4, stage 3 |
| SIM-2 | PLAN: decided here: "reproducible reduction", position-major last-first strategy, its cost; canonical per set in lowering | §3.3 "Order" |
| SIM-3 | FIX-NOW: U1 computable from an independent box model, two-sided on named populations | stage 1 U1 |
| SIM-4 | FIX-NOW: dot / negated / `\p` / `\W` certain movers, 20 of 76 cells | stage 1 predicted movers, O2 |
| SIM-5 | DOC: partial-merge figures corrected | G5, stage 1, §8 |
| SIM-6 = SLOT-7 | DOC: `(?:ab|aB)xy` moved to stage 2a; 2b's own tree-level movers | stages 2a, 2b |
| SIM-7 | DOC: R2 is a listing; real-text regime before stage 3 lands | §4.4 |
| SLOT-2 | FIX-NOW: the unit lives in the kind row | §3.6, stage 2a |
| SLOT-3 (+ OWN-4) | FIX-NOW: owner's hull and trie outputs dropped; island stays A-ISL's | §3.1, §3.3, U4 |
| SLOT-4 | FIX-NOW: 3m folded into stage 3; s3 re-derived by the census | §4.5, stage 3, §8 |
| SLOT-5 | PLAN: rr_alt row 1b, named later piece, census-gated | §6 |
| SLOT-6 | PLAN + ruling O5: the general form named, arms staged | §3.5, §9 |
| SLOT-8 | DOC: one hull until stage 3; home left to the kit split | stage 3 |
| OWN-1 (+ OWN-4, SLOT-3) | FIX-NOW: factoring is an owner rule; altcls's two stages merge into it | §2.2 (5), §2.3, §3.2, §3.3, §6 |
| OWN-2 | FIX-NOW: §2.2 (1) corrected; G3 ledger; stage 2a re-argued against D77 | §1 G3, §2.2, §2.3, stage 2a |
| OWN-3 | FIX-NOW (text) + ruling O4: concatenation paragraph; per-length pieces designed | §3.4, §4.5, stage 2p |
| OWN-5 | FIX-NOW (text): evidence bar pcrec-side + a request; F10 and "folds never" dropped; SIMD-only qualifies | §4.6 |
| OWN-6 | FIX-NOW (text): stage 1 kinds per regime; B0 population named; stage 2a predicted movers via census; G5 per machine | §1 G2/G5, stage 1, stage 2a |
| OWN-7 | DOC: cite §4.5 | §2.2 (8) |
| SIM-2 lesson / lesson 1 / lesson 3 | applied | §3.3, §5 preamble, §4.7 |
| [LOWERENC-SEAL] / [REQ-EMPTYCAT] / [REPEAT-RUN] / [REQ-LOOKAROUND] | siblings: stage, decision points, witness | §9 S1-S4 |
| C1-C4 | vetted | §8a |
