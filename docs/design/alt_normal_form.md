# One alternation normal form: folds are alternations, positions are sets at the seam

**Status: PROPOSED, rev 0** (lane altdesign, 2026-11-05; design only, no build go).
A critic round follows (the manager runs it). Plan row: [RUN-POS-SET] (restated
by this lane), plus the sibling row [DFA-ALPHA-MERGE] filed with it.
Inputs: `docs/dev/lanes/altthink_report.md` (the thought lane; its §6 questions
are this note's agenda) and `docs/dev/lanes/rpsurvey_report.md` (the survey;
its derived москва/αβγ numbers are wrong, corrected by altthink and re-measured
here in §8). Evidence: `docs/dev/lanes/altdesign_evidence/`.
Proposed decision: **D-next** (the manager numbers it at ruling), stated in §11.

Rulings this note builds on (Frank, 2026-11-05): case folds are set up as
alternations and handled by the alternation logic (considering alternation
concatenation); for ASCII that may just be sets, for UTF-8 tries or other
reductions; the byte-encoding result may be the same as today. The kit hand-off
stays SETS unless a case is made that something richer lets SIMD do better.
The matcher's own caseless-class code (the VM's decode-and-test) is not the
target.

## 0. Premise test (re-run)

`altthink_evidence/f.sh` (path re-pointed at this worktree's build) on
`(?i)abcdÀefgh -e utf8`: `req_whole_run c38045464748/ffdfdfdfdfdf`, i.e. a run
of 6 positions STARTING AT À (`c3 [80 a0] e f g h`); `abcd` is lost on the left
and the run is not carried through À. CONFIRMED. Every other point this note
rests on was re-read in the code (§2's inventory) and agrees with altthink's
report, with one sharpening it did not state (§4.2): the run's `all` flag
already means "fixed width, every byte inside its position", not "exactly one
literal", since [OPT-LITSCAN] S4 C3; only its comment still says the latter.

## 1. Goals

Ranked; the higher goal wins a conflict.

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | No answer moves | every caller | answer identity over the corpus and the bench patterns, every encoding, every axis (`make test`, `make test-axes`); libpcre2 differential (PC-3) unchanged |
| G2 | D186's bar per stage | users with pinned performance | each stage meets its declared kind's bar: no regime slower beyond noise on any predicted mover; stage 1 moves ZERO byte-encoding artifacts (emit diff empty) |
| G3 | One mechanism | maintainers | one owner of the normal form (§3), every other site a reader; the special cases named in §2.2 deleted, none added |
| G4 | Caseless UTF-8 keeps its required runs | `-e utf8 (?i)` users | of the 1454 simple fold classes, the count that keeps an `abcd<X>efgh` run: 513 today, at least 766 after stage 1, at least 1417 after stage 3 (same-length classes); `ci-greek-run` 0 → 6 positions |
| G5 | Smaller caseless UTF-8 tables | object size, cache | no utf8 mover's DFA next-state table grows; `(?i)москва` 1140 → 900 entries (−21%) |

Non-goals: the VM's caseless class code; full case folding itself
([FULL-CASEFOLD], [SEQ-FOLD]); any statement of the kit's method (D157); any
reduction that enumerates a language (2^n words for n caseless letters); the
DFA alphabet re-merge (its own row, §10).

## 2. Where alternation facts come from today (inventory, checked)

### 2.1 Producers and readers

| site (file:function) | level | what it does with an alternation or class | role after this design |
|---|---|---|---|
| `src/parse/` (D23 fold) | code point | `(?i)x` becomes the class of x's simple fold set | unchanged: a class IS the one-symbol alternation |
| `src/opt/altcls.c` stage 1 (merge), stage 2 (`altcls_factor_run`, `altcls_extend_prefix`) | code point, pre-callgraph | adjacent single-char branches to one class; prefix factoring on ONE literal byte key; the two stages do not feed each other | **caller of the owner** (stage 2b) |
| `src/opt/lower_enc.c` `lower_class_utf8` + `u8_box`/`u8_ranges` | byte, inside the new subtree | builds one branch per box (contiguous code points only), wraps >1 branch in the `A_CAT(A_EMPTY, alt)` seal | **caller of the owner** (stage 1); seal deleted |
| `src/facts/req.c` `rb_class_into` | byte | a class is a run position if it is one cube of ≤ `pos_set` members | reader: the one-byte-branch case of the alternation rule |
| `src/facts/req.c` `rr_alt` + `rn_common_head`/`rn_common_tail`/`rn_hull_mask` | byte | cube hull of the common head and tail; `all = false` always | reader: the hull rule over equal-width branches (stage 2) |
| `src/facts/req.c` `rb_walk_at` `A_EMPTY` arm → `rb_row_into` → `rb_assert_into` | byte | the empty string cuts the run like an assertion | deleted: `A_EMPTY` is `rr_unit` (stage 2) |
| `src/facts/req.c` `rb_intersect` | byte | bytes necessary in every branch | unchanged (a different question) |
| `src/facts/kset.c` `pcrec_kset_walk`, `pcrec_span_walk`, `pcrec_width_walk`; `src/facts/startset.c` `ss_walk` | NFA / lowered AST | per-offset unions, shape-blind (measured identical) | unchanged |
| `src/ir/dfa.c` `refine_by` | NFA atoms | alphabet refined from class atoms, never re-merged; shape-SENSITIVE | normal form removes most of it; [DFA-ALPHA-MERGE] removes the rest |
| `src/gen/emit_vm.c` `vm_isl_words`/`vm_isl_build` | AST | enumerates a literal language into a trie (singleton edges only) | reader (unlock U4) |
| `src/core/cpset.c` `pcrec_cls_cube`, `pcrec_cube_of` | class bitmap | the cube detector | D187's one derivation |

### 2.2 Special cases this design deletes or merges

Deleted: (1) `rr_alt`'s unconditional `o.all = false` (its own comment calls
the general case an unmeasured "same-literal special case"); (2) the
`A_CAT(A_EMPTY, alt)` seal in `lower_class_utf8` (its comment calls it
redundant since K123; under [CLS-TREE] S3 the `A_WCLASS` wrapper already keeps
a bare alternation out of a lookbehind's branch spine); (3) `A_EMPTY` walked as
an assertion in `req.c`. Merged: (4) `rb_class_into`'s and
`rn_common_head`/`tail`'s two spellings of "a position" become one set-position
constructor (stage 3, D187); (5) altcls's two stages become one fixpoint over
the owner's output (stage 2b). Generalized, not deleted: (6) `u8_box`'s
contiguous-only boxing; (7) `vm_isl_single`'s singleton edges; (8)
[RUN-POS-SET]'s k/s first-byte handling, which falls out of §6's affix facts
instead of being its own mechanism.

## 3. The general form and its one owner

**The form.** A class is an alternation of one-symbol strings. An alternation
of capture-free, fixed-position literal branches (each position a SET over the
level's alphabet: code points above lowering, bytes inside it) is reduced
POSITIONALLY, never by enumerating its language:
- **width groups**: branches are grouped by width; unequal widths never share a
  position product;
- **sibling merge** inside a group: two branches identical except at ONE
  position become one branch whose set there is the union. That rewrite is
  EXACT by construction (the merged branch's language is exactly the union of
  the two), so it may rewrite the matcher. Run to a fixpoint, it collapses an
  exact product (`ab|Ab|aB|AB` → `[aA][bB]`; `c3 80|c3 a0` → `c3 [80 a0]`)
  and partly reduces a non-product (`ce 92|ce b2|cf 90` → `ce [92 b2]|cf 90`);
- **the hull** of a group: per position the union of the branches' sets. It is
  a SUPERSET of the group's language unless the group collapsed to one branch.
  A superset is sound for FACTS (a necessary run, a start set) and never used
  to REWRITE.

**The owner.** One module, proposed `src/opt/altnf.c` (name at build): a pure
function from a branch list (fixed-position set sequences + an `exact`
obligation) to the normal form (width groups, each a list of merged branches,
plus each group's hull). It reads no option and no prior, allocates only new
nodes, and knows no encoding (the alphabet is a parameter). Every other site is
a caller or a reader:

| site | relation |
|---|---|
| `lower_class_utf8` | caller, byte level, over `u8_box`'s branches (stage 1) |
| `altcls` | caller, code-point level, over adjacent capture-free fixed-width literal branches (stage 2b); replaces its merge stage and its single-byte prefix key |
| `req.c` `rr_alt` | reader of the SAME hull definition at the facts level: a position-wise union over equal-width `all` branches (stage 2); the hull operation is one function in the set-position primitive (`cpset`), called by both |
| VM island, string-set fact | readers of the owner's trie output (unlocks U3/U4) |
| kset, startset, NFA/DFA | shape-blind; nothing to change |

**Determinism.** The fixpoint scans pairs in ascending branch order and merges
the first applicable pair; the result is exact whatever the order, and the
order makes it reproducible.

**Preference.** In lowering every branch is a distinct code point, so the
branches are pairwise disjoint and order cannot matter (lowering's own
existing argument). At code-point level (altcls) the merge stays inside a
maximal ADJACENT run of branches, altcls's existing soundness boundary; suffix
factoring `AC|BC ≡ (?:A|B)C` holds for leftmost-first as prefix factoring does.

## 4. The seven questions, decided

### 4.1 Where the normal form lives (Q1)

**Decision: one owner (§3), two callers, staged: lowering first, altcls
second.** A single post-lowering pass over USER alternations is ruled out: it
would rebuild nodes that contain group roots, and `pcrec_callgraph_build`
caches `u.call.body` pointers into the tree; `pcrec_lower_enc` is legal below
the call graph only because it SPLICES IN PLACE (a leaf class is replaced by a
new subtree; `src/core/compile.c`'s comment above the call, utf8s1 report §4).
So the byte-level call sits inside `lower_class_utf8` (new nodes only, the
invariant holds) and the code-point-level call sits in `altcls`, which already
runs before the call graph and already rebuilds. Lowering-only would leave user
alternations on the old path (the 4 → 6 byte case of §8 stays cut), which is
the parallel mechanism Frank asked to remove; hence both callers, but in two
stages with different kinds (§5).

### 4.2 Exact vs superset, and what `all` means (Q2)

**Decision: superset hulls ARE allowed into `all` (facts only); exactness is
required only for rewriting.** This is not a new soundness statement:
- the run is already a product of position sets, not a literal. `rr_pos` sets
  `all = true` for a cube position, and `rn_common_head`'s hull of `[aA]` and
  `a` is `[aA]`, a position holding a byte one branch never has (req.c header,
  "fr[ae]"). The soundness statement every reader relies on is: *every match
  contains, at contiguous offsets, a substring whose i-th byte is in position
  i's set; the run begins at most `off` bytes into the match*.
- `all` (internal to `req.c`) therefore already means "every match of this
  subtree is exactly `head.n` bytes and its i-th byte lies in `head` position
  i". Stage 2 corrects the comment and extends it to alternations: `all` holds
  for an alternation iff every branch is `all`, every branch stores the same
  untruncated width, and every hull position stays in the position domain.

**Reader audit** (every reader of `ReqRun`/`RbRun`, file:function, and what it
assumes):

| reader | reads | exactness assumed? |
|---|---|---|
| `src/facts/facts.c` `pf_derive_req_walk` | bit count vs `PCREC_MIN_REQ_RUN_BITS` | no (information only) |
| `src/facts/req.c` `pcrec_req_window` → `src/core/findings.c` `pcrec_find_run_scan_index`, `pcrec_find_run_window_start` | rate over (byte, mask) via `cube_mass` | no (mass of the position's members) |
| `src/facts/req.c` `pcrec_req_pick` | the scan member only if `mask == 0xFF` | no (exact positions only) |
| `src/facts/kset.c` `pcrec_run_pin` | exact positions only (`mask == 0xFF`) | no |
| `src/facts/facts.c` landmark / `req_landmark_maxoff`; `src/gen/emit_dfa.c` `req_handoff_applies`, `req_handoff_entry_applies`, `req_handoff_k` | `maxoff`/`whole_maxoff` bounds | no (offset bound only; computed from `maxw`, unchanged by the rule) |
| `src/gen/emit_dfa.c` `req_run_tests`/`ofs_test_run`, `req_pres_spans`, `req_site_define`, `emit_req_handoff_rest` | emitted masked compare `(s & K) == T` / kit presence spans | no (membership) |
| `src/gen/memfn_sites.c` `pcrec_memfn_wpos_cube` | expands (T, K) to a 256-bit set for the kit | no (membership; already a set at the seam) |
| `src/gen/emit_dfa.c` `ofs_test_verifies_run` | per position, the offset test's members ⊆ the cube | no (membership) |
| `src/gen/emit_dfa.c` `req_whole_holds_byte`, `req_parts_in_whole`, `req_set_leads_own`, `req_rest_own_sig` | exact positions only | no |
| `src/gen/emit_dfa.c` `req_landmark_hit_ppm` | product of position masses | no (a superset position only raises the mass: conservative) |
| `src/gen/emit_dfa.c` `pf_window_of`, `pf_run_applies_common`, `ofs_test_of`, `req_byte_dominated_by`, `req_none_applies`, `req_set_leads_applies`, `req_pick_shadow`, `emit_orientation_block`; `src/facts/facts.c` stamps (`pf_hex`) | length, index, pin, rendering | no |

No reader treats the run as the literal the pattern matches. Stages 1 and 2
stay in the cube domain, so no reader changes. Stage 3 changes the position
REPRESENTATION (sets), and every membership reader above moves with it; that
is [POS-ONE-DETECTOR]'s scope (§4.7).

### 4.3 Cube domain first, or wait for D187 set positions (Q3)

**Decision: do not wait.** Stage 1's rewrite is a property of the tree, not of
the run representation: the same lowering output gains more when positions
become sets, with no second change to lowering. Cube domain first gives +253
classes (513 → 766, altthink's shape count) with no `req.c` change; set
positions are stage 3 and add +253 exact and, with the hull, +398 superset
classes. The bench's `ci-*` cells mostly need stage 3 (§8), so stage 1 is
justified by G3/G5 and its own movers, not by the bench.

### 4.4 The information of a set position, and the floor (Q4)

**Decision: `info(S) = 8 − ⌈log2 |S|⌉`, an integer; the floor stays 16 bits.**
It equals `popcount(K)` for every cube, so every run representable today ranks
exactly as today (stage 3 is unit-pure on today's runs). It never overstates a
position (a 3-member set counts 6 bits, like a 4-member cube). Effect on the
floor: a two-position run with a 3-member position is 8 + 6 = 14 < 16 and does
not ship. An exact `log2` in fixed point would rank 3-sets above 4-cubes;
choosing it is a CHOICE row with evidence (a cell where the rounding changes
the picked run), not a default.

**Ranking risk** (a long superset run outranking a shorter exact one). The run
walk is a core fact and reads no prior, so it cannot weigh real byte rates; a
hull of Cyrillic positions all carrying `d0` scores 6-8 bits each but is
common in Russian text. Declared handling:

| row | condition | action |
|---|---|---|
| R1 | today's runs (no non-cube position) | today's `rn_better`: higher info, `a` on a tie |
| R2 | a candidate carries a set (non-cube) or superset-hull position | same ranking, AND the stage census lists every compile whose picked run changed from an all-exact run to one with such a position |
| R3 | R2's census shows a regime where the flipped pick loses beyond noise | narrow (D186): the walk carries the best all-exact run beside the best run as a second core fact, and the rate-aware derived pick (`src/core/findings.c`) chooses between them; built only then (D77) |

### 4.5 Mixed widths (Q5)

**Decision: the normal form carries length groups now; the FACTS read only
one affix position on each side until [SEQ-FOLD] needs more.** For a mixed
letter (k/K/K, s/S/ſ, ß/ẞ, о/О/ᲂ: 37 classes, and every 1:n fold of
[SEQ-FOLD]) no position product exists across groups. Facts at stage 3m: the
union of the groups' FIRST positions ends the run on the left (`{4B,6B,E2}`
for k), the union of their LAST positions begins the run on the right
(`{4B,6B,AA}`). Per-group runs and the bounded string set are length-group
facts that the owner's output already represents; they are built when
[SEQ-FOLD]'s design note names a cell that needs them (ß ↔ ss is a 2-group
alternation whose `ss` group is itself an exact product at code-point level,
and splits into byte widths 2/3/4 under UTF-8 because ſ is two bytes).

### 4.6 The string-set fact for the kit (Q6)

**Decision: the hand-off stays SETS.** For an exact product the per-position
sets lose nothing. A "one of these N strings" fact carries strictly more only
for non-product languages (user keyword alternations such as
`\b(true|false|null)\b`, and mixed-width folds), by the CORRELATION between
positions. Stated as a fact (D157): "every match contains (or begins with) one
of these N strings"; the kit's method is not presumed.

The evidence that would make the case, all three required, none assumed:
1. on at least one bench cell, the hull window's candidate rate exceeds the
   string set's own rate on the cell's text, by enough that the excess verify
   work is a measurable share of the cell's time (measured per cell, both
   rates from the same text);
2. a kit kernel of the F10 class (`docs/design/memfn/requirements.md` F10)
   consuming the string set beats the sets-based kit + verify on that cell,
   scalar and SIMD layers each against their own bar (D144 add. 4, C9);
3. the gain survives a random-like regime (D186 add. 2).
Folds alone never make the case. The cap N is set by that kernel's request,
not here (no silent default).

### 4.7 Sequencing and the abi question (Q7)

**Decisions.**
- **After span_pick unit 1e lands** (D153 remodel first): no shared source, but
  any change to `req_run` content moves the run positions handed to the kit
  (`pcrec_memfn_wpos_cube`), its arms and witnesses, and would contaminate 1e's
  REACH EQUALITY.
- **Stages 1, 2 and 2b do not wait for [POS-ONE-DETECTOR]**; stage 3 (set
  positions) rides WITH it, since both change what a position means across the
  seam (manifesto principle 4, ride-along).
- **Removing the seal is NOT an abi event.** `abi` versions the emitted
  SCAFFOLDING (`match_api.md` §6¶17, D76); the seal changes NFA-derived
  program content (states, tables) of UTF-8 artifacts with a multi-branch
  class, exactly as stage 1's merge does, and emits no declaration, comment or
  layout. The lowering comment that calls it "an abi event" is corrected in
  the same change. The build lane still runs D94's grep (every pinned
  whole-file fixture and identity gate) and re-pins any utf8 wide-class
  fixture under the stage's movers manifest; if a gate's pin turns out to be
  the abi number's, the critic round reopens this point.

## 5. Staging (each stage: kind, change, gates, predicted movers, sabotage witness, deletions)

All stages: no edits until Frank's build go; each stage is its own branch and
landing; `make test`, `make strict`, `make test-axes` (answer identity on every
axis, including `-fno-cls-kit` where the VM reads the lowered byte child), and
REACH for every new mech row.

### Stage 1 — UTF-8 lowering calls the owner (byte: UNIT change; utf8: predicted movers, D186 unit bar)

- **Change.** `lower_class_utf8` hands `u8_box`'s branches to the owner (sibling
  merge to a fixpoint, width groups) and returns the merged form; the seal is
  deleted. `req.c` is untouched. The owner is born here with only its byte
  caller.
- **Gate B0 (zero byte movers, REQUIRED).** An emit diff over every corpus and
  bench pattern compiled `-e byte`, base commit vs stage commit: empty. The
  control is independent: the base compiler does not contain the owner, and
  `lower_class_byte` never reaches it (`lower_ops[]` dispatches per encoding).
  Also empty for every `-e utf8` compile whose classes are all ≤ 0x7F
  (`lower_class_utf8` returns NULL before the owner is called).
- **Gate U1 (utf8 movers inside the predicted set).** The predicted set,
  computed on the BASE compiler before the build: utf8 compiles with a
  non-ASCII class whose lowering has more than one branch (case folds, and also
  non-fold classes such as `[^é]`, `\w` under UCP, ranges with holes; their
  boxes merge too). Observed movers ⊆ predicted; a mover outside is a finding.
- **Gate U2 (the fold census, independent control).** `rpsurvey_evidence/
  foldsweep.py` on the stage build: classes keeping the `abcd<X>efgh` run =
  766 exactly (predicted from CaseFolding.txt alone by
  `altthink_evidence/shapes2.py`: 24 + 489 + 253; the prediction shares no code
  with the compiler).
- **Gate U3 (no table growth).** Every utf8 mover's next-state entry count ≤
  base; growth is a finding to explain, not a pin to move.
- **Gate U4 (speed, D186 unit bar).** Per-regime bench on the utf8 movers
  (bench/utf8 `ci-*`, `cls-*`, `prp-*` that moved): no regime slower beyond
  noise. Cells whose scan pick flips (predicted: `ci-greek-run`
  offset-set → handoff) are listed with their per-regime numbers.
- **Predicted movers** (measured on byte spellings of the stage-1 tree,
  §8): run gains `(?i)abcdÀefgh` 6 → 10, `(?i)Ελληνικά` 0 → 10,
  `(?i)привет мир` 0 → 7, `(?i)naïve café` 8 → 12, `(?i)αβγ` 0 → 3; tables
  `(?i)москва` 1140 → 900, `(?i)Ελληνικά` 1430 → 1170, `(?i)αβγ` 160 → 128,
  `(?i)é` 12 → 9. Bench/utf8 cells: `ci-greek-run` (run and pick),
  `ci-moskva`, `ci-strasse`, `ci-e-acute`, `ci-ucp-invariance` (tables only),
  `ci-kelvin`/`ci-long-s` (k/K and s/S branches merge; direction not
  predicted, see §8 caveat), `ci-neg-fold` and multi-box `cls-*`/`prp-*`
  (possible), `ci-sigma` (no move predicted).
- **Sabotage witnesses.** S-a: the merge accepts pairs differing in TWO
  positions. Witness `(?i)β` (`ce 92|ce b2|cf 90`) against subject `ΐ`
  (U+0390, `ce 90`): NOMATCH expected; the sabotaged merge builds
  `[ce cf][92 b2 90]` and matches. S-b: the merge ignores width groups (pads
  or aligns branches of unequal width). Witness `(?i)k` against `K` alone:
  MATCH expected, and against `\xe2\x84`: NOMATCH. The K123 witness
  `(?<=[a\x{3b1}])x` (a lookbehind over a multi-branch class) keeps compiling
  and matching `αx` with the seal gone. S-ids from the range the build brief
  names.
- **Deletes.** The seal (two nodes and its comment).

### Stage 2 — `rr_alt` reads the hull; `A_EMPTY` is the identity (CHOICE change, byte and utf8)

- **Change.** In `req.c`: `rr_alt` sets `all` per §4.2 and, when it holds, the
  head, tail and best are the hull; the `A_EMPTY` arm returns `rr_unit`
  (assertions keep `rr_none(0)`; the D77 decline for them is untouched). Cube
  domain (`pos_set` 2).
- **Why a choice change.** It moves byte artifacts: `abcd()efgh` run 4 → 8
  (the capture's empty body), `abcd(?:|)efgh` 4 → 8, `abcd(?:ab|ab)efgh` 6 → 10
  (altcls's factoring leaves an alternation of two empties that cuts today),
  `(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)` 4 → 6. Measured today values:
  `altdesign_evidence/stage2_byte_probes.txt`; the after values are the
  run of the same language spelled without the cut (measured) or derived from
  the rule.
- **Gates.** A census of every corpus and bench compile, both encodings:
  moved runs listed with old/new (the population is NOT yet measured; it is
  this stage's first deliverable); §4.4's R2 census of exact→non-exact run
  flips; per-regime bench evidence on every cell whose pick moved (D186 choice
  bar: no regime loses; a losing regime narrows the row).
- **Sabotage witness.** S-c: `all` is set without the equal-width test.
  Witness `xy(?:ab|cde)zw` against `xycdezw`: MATCH expected; the sabotaged
  walk claims `xy[ac][bd]zw`-shaped contiguity across a 3-byte branch and the
  pre-check rejects the subject (NOMATCH).
- **Deletes.** `o.all = false`; `A_EMPTY` in the assertion arm.

### Stage 2b — altcls calls the owner (CHOICE change, byte and utf8)

- **Change.** altcls's merge stage and its single-byte-key prefix factoring
  become one fixpoint over the owner's output at code-point level: sibling
  merge within adjacent runs, prefix AND suffix factoring, any identical
  capture-free factor as the key. Fixes the measured non-composition
  `(?:ab|aB)xy` (run 3) vs `a(?:b|B)xy` (run 4).
- **Gates.** Answer identity; the altcls corpus (`tests/altcls/`) and its
  stamps; a VM island census (altcls already collided with the island once:
  `w-256` got 11 islands, 3.0% larger) with per-regime VM evidence; DFA table
  census.
- **Sabotage witness.** S-d: the merge crosses a non-adjacent branch.
  Witness `ab|a.c|aB` style preference cases where an intervening branch
  overlaps (exact witness chosen by the build lane against libpcre2,
  capture-bearing so the span differs).
- **Deletes/merges.** altcls stage 1 as its own mechanism; the single-byte key.

### Stage 3 — set positions in the run (CHOICE change; rides with [POS-ONE-DETECTOR])

- **Change.** `RbRun` positions become 256-bit sets (D187); cubes are derived
  by `pcrec_cube_of` where a reader wants one; `info` per §4.4; `pos_set` is
  replaced by a member-count bound on the set (its value a declared row with
  evidence, not a carried constant). The two spellings of "a position" in
  `req.c` merge.
- **Predicted movers.** Fold classes keeping the run 766 → 1417 (+253 exact
  non-cube, +398 superset hull); `ci-greek-run` 0 → 6 (`(?i)αβγ`, β's tail
  `{92,b2,90}`).
- **Gates.** Every §4.2 membership reader moves to sets in the same change
  (one detector); the R2 census; per-regime evidence, including a regime of
  real Cyrillic/Greek text (the lead-byte rate risk).
- **Sabotage witness.** S-e: the hull drops a member. Witness `(?i)xβy` under
  utf8 against `xϐy` (`cf 90`): MATCH expected; a hull missing `cf` or `90`
  rejects it in the pre-check.

### Stage 3m — one affix position each side of a mixed-width letter (CHOICE change)

- Facts per §4.5. Predicted: `ci-strasse` 3 → 5, `ci-moskva` 0 → 4,
  `(?i)select` 5 → 6, `(?i)information_schema` 12 → 13. Witness S-f: the
  affix set misses the long member's first byte: `(?i)xk` against
  `xK` (`78 e2 84 aa`): MATCH expected.

## 6. Decisions as declared tables

The stages add rows, never branches in code:
- the owner's reduction is one table of rewrite rules, first match per pair:
  (1) widths differ → no merge; (2) differ at exactly one position → merge
  (exact); (3) otherwise → keep both (the hull records them);
- `rr_alt`'s outcome table: (1) every branch `all`, equal untruncated width,
  hull in domain → `all`, run = hull; (2) otherwise → common head and tail
  (today's rule);
- the ranking table of §4.4 (R1-R3).

## 7. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** Run lengths, table entries and artifact
   bytes in §8 are compile-time facts of this box's compiler (gcc 15.2, Zen 4);
   they do not depend on a timing regime. Every speed claim is owed per stage,
   per regime (bench/utf8 strata, a random-like regime, and real
   Cyrillic/Greek text for stage 3); a different regime can flip a run pick
   (§4.4), which is why R2's census exists.
2. **Independent control: RELEVANT.** Stage 1: base-vs-stage emit diff (the
   base compiler cannot contain the owner); the fold-class keep count
   predicted from CaseFolding.txt by a script that shares no code with pcrec;
   answer identity against libpcre2 (PC-3). Stage 2-3: the moved-run census is
   counted by the census script over every compile (K35: the population is
   the corpus + bench list, counted, not sampled); each sabotage witness
   reaches its site (REACH run per row).
3. **What moves when data is regenerated: RELEVANT.** CaseFolding.txt (a
   `third_party/ucd-*` regeneration) changes fold classes and therefore the
   owner's input; the owner holds no table of its own. A UCD bump moves utf8
   caseless artifacts and the census numbers (1454/766/1417 are UCD 16.0.0's);
   no abi event (program content, §4.7), and no spec change (no caller-visible
   surface moves; `--emit-facts` values move as they do for any fact change).

## 8. Measured and inferred numbers

`altdesign_evidence/stage_pred.tsv` (`pred.py`, rerunnable: `python3 -I
pred.py third_party/ucd-16.0.0/CaseFolding.txt build/pcrec TEXT...`). Columns:
`today` = MEASURED `-e utf8 (?i)TEXT`; `s0` = MEASURED control, today's
lowering spelled as a byte pattern (no seal, altcls denied); `s1` = MEASURED,
the stage-1 tree spelled as a byte pattern; `s2c`/`s3`/`s3m` = INFERRED from
the rules (positions, info per §4.4, floor 16).

| pattern | today | s0 (no seal) | s1 | s3 | s3m | entries today → s1 |
|---|---|---|---|---|---|---|
| `abcdÀefgh` | 6 | 6 | 10 | 10 | 10 | 132 → 121 |
| `москва` | 0 | 0 | 0 | 0 | 4 | 1140 → 900 |
| `αβγ` | 0 | 3 | 3 | 6 | 6 | 160 → 128 |
| `straße` | 3 | 3 | 3 | 3 | 5 | 462 → 429 |
| `é` | 0 | 0 | 0 | 0 | 0 | 12 → 9 |
| `σ` | 0 | 0 | 0 | 0 | 0 | 40 → 40 |
| `select` | 5 | 5 | 5 | 5 | 6 | 216 → 192 |
| `information_schema` | 12 | 12 | 12 | 12 | 13 | 1020 → 960 |
| `Ελληνικά` | 0 | 4 | 10 | 10 | 11 | 1430 → 1170 |
| `привет мир` | 0 | 4 | 7 | 7 | 8 | 1620 → 1296 |
| `naïve café` | 8 | 10 | 12 | 12 | 12 | 169 → 143 |

Readings: the `s0` column isolates the seal (αβγ, Ελληνικά, привет мир, naïve
café gain from its removal alone); `s1` adds the merge. The s1 spelling leaves
non-product groups unmerged, so it UNDER-states stage 1 on partial merges
(`ce [92 b2]|cf 90` for β). Caveat: the byte spelling of `(?i)k`/`(?i)s`
emits 60-72 entries where the utf8 compile of the same lowering emits 48
(cause not traced), so k/s table predictions are omitted; every other row's
control equals today exactly. Byte user alternations (stage 2):
`stage2_byte_probes.txt`. The bench cell `ci-moskva` gets no run before stage
3m (о, с, в are mixed-width: U+1C82, U+1C83, U+1C80), as altthink corrected.

## 9. Unlocks (each with its trigger)

| id | unlock | trigger |
|---|---|---|
| U1 | [RUN-POS-SET] subsumed (stages 1-3m) | already fired (rpsurvey); build waits for span_pick 1e and Frank's go |
| U2 | [SEQ-FOLD]'s 1:n folds become length-group alternations the owner already represents | [SEQ-FOLD]'s design note (its first child [FULL-CASEFOLD]) |
| U3 | the string-set fact for the kit ([OPT-A]'s keyword cells, F10) | §4.6's three-part evidence on a bench cell |
| U4 | caseless VM islands: the island trie with set edges, read from the owner (`(?i)(?:select|union|insert)x` gets no island today, measured by altthink) | a VM cell with a caseless keyword alternation in the bench or a user report |
| U5 | [DFA-ALPHA-MERGE]: merge bytes whose transition columns are identical in every state after minimization; makes table size shape-blind for every pattern, not only normalized ones | an object-size or cache-pressure cell on a caseless utf8 or wide-alternation pattern, or this note's stage 1 landing |

## 10. What this note does NOT decide

- Any build go, or the order of the stages against other work beyond §4.7.
- The owner's file name and API spelling (the build lane, against
  `docs/dev/guide/coding.md`).
- The member-count bound that replaces `pos_set` in stage 3 (a declared row
  with evidence).
- The string-set fact's form and cap (U3's own design, when triggered).
- [SEQ-FOLD]'s per-group facts, offsets and captures across a fold image.
- The DFA alphabet re-merge (its own row; context atoms and the word set must
  stay distinct there).
- Whether the deny flags of the new rows are public (memory: a public deny
  only if the row can be slower; a test-only lever otherwise) — per stage, at
  build.

## 11. Proposed decision (D-next)

**Alternations have one normal form, produced by one owner; a class is the
one-symbol case; folds are alternations.** The owner reduces positionally
(width groups, exact sibling merge, the hull as a facts-only superset) and is
called above the call graph (altcls, code points) and inside the lowering's new
subtree (bytes); every other site reads it. Facts may use superset hulls;
rewrites use only exact merges. Positions cross the kit seam as sets (D187);
the hand-off stays sets until the string-set evidence of §4.6 exists. Staged
as §5, each stage with its D186 kind and bar.

## 12. Open questions for Frank (plain words)

1. **Should the required-run fact be allowed to use "covering" byte sets that
   are wider than any one alternative?** Example: for `(?i)β` the run could
   say "this position is one of 92, b2 or 90" although no single spelling has
   all three. It is safe (it only makes the scan test a little looser) and the
   code already does a small version of it today. Leaning: yes, for facts
   only, never for rewriting the matcher.
2. **Stage order: is it right to start with the UTF-8 lowering alone (no
   change at all to byte patterns), and do user-written alternations as a
   later, separately judged step?** Leaning: yes; the first step is provably
   byte-identical for the byte encoding, the second moves byte patterns and
   needs its own evidence.
3. **Set positions in the run (the step that gets `(?i)αβγ` its full run):
   ride along with the kit-seam position cleanup ([POS-ONE-DETECTOR]) rather
   than go first?** Leaning: ride along, since both change what a position
   means on the same readers.
