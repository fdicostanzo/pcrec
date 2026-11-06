# altnf2 lens FIX (fix-induced): findings

Subject: docs/design/alt_normal_form.md rev 1 @ f7fd1a759; build tree worktrees/crit-altnf2 (main 569c57d3a).

## Findings

### FIX-1 — §3.6's "the row is -Wswitch-complete, so a missed reader is a compile error" is false for a new TEXT value; three readers are `==` tests that would silently decline (CONFIRMED, maintenance + size/speed; effort small; blast: every byte and utf8 artifact containing an A_EMPTY under possessify)

The fix for SLOT-2 adds a fourth `KindText` value `UNIT` for `A_EMPTY` and
rests its safety on the row's -Wswitch completeness. The completeness the code
has is over KINDS, not over TEXT values:
- `src/core/internal.h:2477-2492`: the `#pragma GCC diagnostic error "-Wswitch"`
  wraps ONLY `pcrec_kind_row`'s `switch (k)` over `AKind`; `kindrow.def:50-54`
  and `tests/core/kindrow_check.sh` (plants 3-6) promise "a KIND without a row
  fails to compile", nothing about a new value of the TEXT column.
- Readers of `.text` (grep `KTEXT_` over src/, complete): switches at
  `facts/req.c:581`, `facts/startset.c:82`, `ir/nfa.c:596-610`,
  `opt/mrl.c:486` (no `default:`, so plain -Wall `-Wswitch` WARNS; an error
  only under the opt-in `make strict`, Makefile:25 `WARN = -Wall -Wextra`,
  -Werror deliberately not the default per root CLAUDE.md R5-Q1) and three
  EQUALITY tests no warning catches: `opt/possessify.c:446`
  (`text == KTEXT_ZERO ? fst_empty(true) : first_of(q, a)`), `:501`
  (`fst_row`: not ZERO -> `bs_all`, nullable: widens to all bytes), `:924`
  (`gk_row`: not ZERO -> `g->ok = false`: the WHOLE Glushkov construction
  declines).
- Failure scenario: the stage 2a build adds `KTEXT_UNIT`, updates req.c and
  the four switches (strict flags them) and misses possessify's `==` lines.
  Every pattern whose possessify region contains an `A_EMPTY` (altcls's
  `a(?:b||d)` empty slots, `(?:|x)`, derive's pruned nodes) loses its
  possessification silently — no compile error, no answer change (safe
  direction), but emitted bytes move on BYTE artifacts too and a speed loss
  hides inside stage 2a's expected movers. The note's own stage 2a census
  models only the run, so it would not attribute these movers.
- The note's mitigation sentence ("every other ZERO reader treats UNIT
  exactly as ZERO and its brief line says so") lists the right sites
  (possessify 446/501/924 included), so the defect is the false safety claim,
  not the list. Fix: drop the -Wswitch sentence; either (a) add a predicate
  `pcrec_text_is_zero(row)` (ZERO or UNIT) and convert the three `==` sites,
  or (b) keep `A_EMPTY` at TEXT `ZERO` and put the unit in a separate column
  (a fifth KIND_ROW field, which the KIND_ROW macro arity DOES make a compile
  error at every row) — (b) also matches kindrow.def's own lesson that one
  reader handed another column's answer was a live miscompile (PATH vs TEXT,
  `kindrow.def:19-24`). Add a stage 2a gate: base-vs-stage emit diff over
  byte populations limited to the run's predicted movers (B0's instrument).

### FIX-2 — PREM-1's fix over-reaches: "read a set position inside an A_WCLASS as its members" also admits TODAY's multi-member boxes, so the island census moves and Gate U4's equality is red on a correct build (CONFIRMED, design + size/speed; effort small; blast: every utf8 VM compile with a contiguous non-ASCII range class inside a literal alternation)

Stage 1's change (§5) says the island's word list "is today's word list" once
`vm_isl_words` reads a set position inside an `A_WCLASS` as its members, and
U4 gates `RX_VM_ALT_ISLANDS` equal base vs stage. But `u8_box` ALREADY emits
multi-member positions for a contiguous run (the box is a byte-RANGE
sequence, PREM-7's own correction), and today's island DECLINES them through
`vm_isl_single` (`src/gen/emit_vm.c:4099`, the A_CLASS arm; `:4091` A_WCLASS
is a transparent descent, nothing marks "inside"). Measured (build tree,
`--engine=vm -fno-cls-kit -e utf8 -p rx --emit-main`, grep the stamp):
- `x(?:[éà]1|q2|r3)y` (é c3 a9, à c3 a0: two singleton boxes): `RX_VM_ALT_ISLANDS 1` (S-i's case);
- `x(?:[éè]1|q2|r3)y` (c3 a8..a9: ONE box `c3 [a8-a9]`): `RX_VM_ALT_ISLANDS 0`;
- `x(?:[\x{100}-\x{17f}]1|q2|r3)y`: `0`.
A stage-1 build implementing the sentence as written enumerates `[éè]`'s box
into 2 words and builds an island: 0 -> 1, a new mover the note does not
predict, and U4 fails on a correct build. Wider ranges (`c4 [80-bf]`, 64 words
per position) reach `VM_ISL_MAX_WORDS`/budget, so the mover set depends on the
cap. The post-merge tree cannot tell a merged set from a box range (no
marker), so "today's list" cannot be preserved without a new field. Two
honest options: (a) state the island admission of range boxes as a stage-1
PREDICTED mover (a CHOICE on the VM: islands trade size for speed, and the
note itself records altcls's island collision, `w-256` +3.0%), with U4
changed to "listed and explained" plus U1's model predicting it; or (b) keep
the island's singleton rule and accept that merged boxes LOSE islands they
have today (`[éà]` 1 -> 0) — which S-i would then catch as a decline. Either
way the sentence "so the island's word list is today's word list" is false.
The B0 half holds (see PROBED-AND-HELD).

### FIX-3 — §11's four new public deny flags cross [IFACE-PUSH]'s hard trigger and ignore the two existing altcls bits (CONFIRMED, design; effort small; blast: the public flag word)

`lib/pcrec.h` uses `PCREC_BIT(0..57)` (bit 55 is the kit's,
`pcrec.h:1196`): 58 used, 6 free. Plan row [IFACE-PUSH] (frozen 569c57d3a):
"HARD TRIGGER ... the push opens when <= 4 flag bits remain". §11 gives
stages 1, 2a, 2b and 3 each a public deny: the first two alone reach the
trigger (4 left), all four leave 2. The note names neither [IFACE-PUSH] nor
[FLAG-ACCESS] in §11/§10 (its own header lists [IFACE-PUSH] among the rows
to read). Also, stage 2b replaces altcls's two stages, which ALREADY carry
public deny bits 10/11 (`-fno-altcls-merge`, `-fno-altcls-factor`,
docs/spec/tuning.md §2.6/§2.7, whose ¶1 text defines them by "stage 1"/"stage
2" and "a literal first byte"); a third bit for the same owner is a parallel
lever, and the two existing contracts need a spec hunk (D80) remapping them
to owner rule rows (merge -> rule 4, factor -> rules 2/3?) — not stated
anywhere in §5 stage 2b or §11. tuning.md §2.6¶2 also records that the merge
deny MOVES THE REFUSAL SET (K45, size cap); stage 1's lowering merge shrinks
utf8 trees the same way, so its deny (and stage 1 itself) can move the
utf8 refusal set — G1/B0 count refusals only under byte. Fix: §11 states the
bit budget and either reuses 10/11 for 2b and folds the stage-1/2a/3 levers
into one or two bits, or schedules [IFACE-PUSH] first; add the utf8 refusal
set to U1's mover list.

### FIX-4 — Gate B0's instrument does not do what B0 needs: `--bases byte` is ignored in a plain `--ref` sweep, and stream 6 always lists utf8 facts, so B0 is red on a CORRECT stage 1 (CONFIRMED, design/gate; effort small; blast: stage 1's required gate)

The OWN-6 fix names B0's population as `scripts/emit_sweep.py --ref BASE
--bases byte` "(its pinned streams: ... `--emit-facts`)". The script's own
definitions (build tree):
- `--bases LIST  the bases each variant runs at (default byte,utf8); facts and
  dumps run at the first only.` (`emit_sweep.py:212-213`). `bases` is read
  only by `run_variants` (`:2042`, `:3400`, which requires `--variant` AND
  `--tree-rev`, `:3220-3221`) and by `run_data_census` (`:2903`). A plain
  `--ref BASE` sweep parses and IGNORES it; its argv streams run at
  `--extra-base` (default empty, i.e. byte), so the byte half is right by
  accident.
- Stream 6 is `--emit-facts=byte,utf8` "for BOTH encodings in one call"
  (`:42-46`, `compile_stream_facts` `:1073-1076`), identity-required. A
  correct stage 1 MOVES utf8 facts: measured today `(?i)abcdÀefgh` lists
  `utf8 req_whole_run c38045464748/...` and `utf8 req_run ...@0` (6
  positions); the note predicts 10 after stage 1. Every corpus caseless or
  wide-class utf8-relevant pattern moves stream 6.
- Stream 4 (composition) compiles each `.rxt` with its own directives; the
  note itself says so ("each `.rxt`'s own directives"); a `.rxt` whose
  directives select utf8 is a utf8 compile and moves under stage 1.
So "Empty emit diff" over B0's named streams is unattainable for a correct
build: either the lane relaxes B0 ad hoc (the K35 failure the fix was
written to close) or splits streams by hand. Fix: spell B0 as streams 1-3 at
the byte base plus stream 6 filtered to its `byte` rows plus stream 4
restricted to `.rxt` files compiling at byte (or name a `--variant plain
--tree-rev` form that the script actually honours, `facts ... at the first
[base] only`), with the utf8 halves going to U1.

### FIX-5 — SIM-1's `info(S)` and SND-6's "cube reader takes the HULL" disagree: a run is ranked and floor-admitted on `info(S)` but tested on a hull worth up to 3 bits less per position (CONFIRMED arithmetic, speed/design; effort small; blast: stage 3 picks, every mixed-letter affix)

§4.4: `info(S) = 8 − ⌈log2 |S|⌉`, "it never overstates a position". §4.2
(SND-6 fix): a cube-wanting reader of a non-cube position "takes the cube
HULL ... or declines". Today's floor (`limits.def:410`, RULED) is "the sum
over its positions of popcount(K)", i.e. the information of what the reader
TESTS. For the note's own mixed-letter affixes the two diverge (computed,
python, hull = AND of ~(a^b)):
- Kelvin `{4b,6b,e2}`: info(S) 6, hull popcount 4 (S-f's "27 bits" is
  21 + info(S));
- long s `{53,73,c5}` (`(?i)s`): info(S) 6, hull popcount 3;
- β `{92,b2,90}` and σ `{a3,83,82}`: 6 and 6 (no divergence).
So a run of three ſ-like positions is admitted at 18 "bits" (≥ 16) while a
hull-reading consumer (`req_run_tests`/`ofs_test_run`, `pcrec_memfn_wpos_cube`
until the kit reads sets) compares 9 bits — under the floor's ruled meaning.
And the hull of `{53,73,c5}` has 32 members: whether `PCREC_MAX_REQ_RUN_POS_SET`
(`limits.def:411`, "the largest member set one position ... may have")
bounds |S| = 3 or the hull's 32 is unstated, and the two answers give
different S-f outcomes. Fix: state info per READER (info(S) for a set
reader after D187, popcount(hull K) for a cube reader), rank and admit with
the reader's figure, and say which cardinality the member bound counts;
"never overstates" holds only for a set reader.

### FIX-6 — OWN-1's fix misdescribes altcls stage 2 as a "one-byte key" to be "widened"; today's key is already the longest common literal prefix, so the ledger row and the multi-byte-key mover are mis-attributed (CONFIRMED, doc/design; effort trivial; blast: stage 2b's census attribution)

§2.1 ("prefix factoring on ONE literal byte key"), §2.2 (5) ("its one-byte
prefix key generalizes to a fixed-width key"), §2.3 ledger ("altcls stage 2
one-byte key ... key widened"), §5 stage 2b ("its one-byte-key factoring",
"multi-byte keys (`(?:abx|aby|abz)q` -> `ab[xyz]q`)"). The code:
`src/opt/altcls.c:200-258` `altcls_extend_prefix` "Grows a group's shared
literal prefix ITERATIVELY as far as every one of the n members keeps
agreeing on the next byte"; only the GROUPING (`altcls_factor_run`, `:260`)
keys on the first byte. Measured: `(?:abx|aby|abz)q` today stamps
`RX_ALTCLS_FACTORED 1` (prefix `ab` already factored, giving
`ab(?:x|y|z)q`). What stage 2b really adds there is RE-MERGING the
remainders (PREM-7's "stage 2's remainders are never re-merged") and
set-valued keys (`[aA]b...`), not key width. A stage 2b census attributing
`(?:abx|aby|abz)q`'s move to "key widened" mis-states the rule that moved it,
and the sabotage set has no witness for the remainder re-merge. Related:
S-d's suffix form `(?:ac|x|xc)` "reaches altcls today (`RX_ALTCLS_FACTORED
1`)" only through PREFIX factoring of `x|xc`; no stamp counts suffix
factoring (match_api.md §6.3.11¶3 defines FACTORED as "alternation runs
prefix-factored"), so the suffix rule's REACH has no instrument until a
stamp/spec hunk is added (not listed in stage 2b's abi/spec steps).

### FIX-7 — SLOT-3/OWN-1 and SLOT-6/O5 fixes contradict on phase: the code-point owner (altcls, before lowering) is named a READER of a description that §3.5 builds over the LOWERED tree (CONFIRMED by pass order, design; effort small-medium; blast: stage 2b's architecture, G3's "one description")

§3.3 (SLOT-3 fix): the owner is "a pure function from a branch list (each
branch a node, with its fixed-position set sequence where it has one)",
`req.c` is "NOT a reader of the owner". §3.5 (SLOT-6/O5 fix): the
description is "built bottom-up over the lowered tree", its home "the facts
walk (`req.c`'s `RbRuns`, generalized)", and its readers include
"altcls/the owner (the `exact` bit and the fixed-position sequence decide
whether a rewrite is legal)". Pass order at the build tree:
`src/core/compile.c:2819` `pcrec_altcls` -> `:2854` `pcrec_callgraph_build`
-> `:2962` `pcrec_lower_enc`; `req.c`'s header: the walk runs "over the
LOWERED tree the E2 seal recorded after `pcrec_lower_enc`". So at stage 2b
the code-point owner runs ~140 lines before the description exists, at a
different alphabet (code points vs bytes). Either the owner computes its
own fixed-position set sequences and adjacency facts at code-point level —
a SECOND description, the parallel mechanism G3 says the design removes —
or the description must be built at two levels, which §3.5 does not state.
Fix: say the description is a pure function over a subtree parameterized by
alphabet (as §3.3 says of the owner), with two call sites (code point
before the call graph, byte in the facts walk), and record that in the §2.3
ledger as ADDED; or drop "altcls/the owner" from §3.5's reader list and
name the owner's own width/position test as a separate, smaller fact.

### FIX-8 — SND-6's hull is a second cube derivation that disagrees with the set by construction, against D187 "two shapes of one position cannot disagree" (CONFIRMED by text, design; effort small; blast: stage 3, the kit seam)

D187 (frozen decisions.md): "A cube (t, mask) is DERIVED from the set where
an optimization wants it, never carried beside it, so two shapes of one
position cannot disagree"; "the derivation reuses ONE detector,
`pcrec_cube_of`". §4.2 (SND-6 fix) adds a second derivation, the HULL
(smallest covering cube, `K' = Ka & Kb & ~(Ta ^ Tb)`), and forbids treating
`pcrec_cube_of`'s false as no constraint. A hull of a non-cube set is a
cube that DISAGREES with the set (it admits non-members): exactly the
"two shapes of one position" D187 was written to stop (its witness: a
position whose cube and set gave different masses). FIX-5 is the measured
consequence (info(S) 6 vs hull 3 for `{53,73,c5}`). Stage 3 "rides with
[POS-ONE-DETECTOR]" (O3), so the build will meet this in the same change.
Fix: state the hull as a NAMED, separate derivation ("covering cube",
lossy) beside D187's exact detector, with every reader declaring which one
it reads (and its information figure, FIX-5), and put the question to the
owner as a D187 addendum rather than leaving its home to "the kit-split
ruling" (SLOT-8).

### FIX-9 — SLOT-2's `UNIT` is a one-member row value: kindrow.def's per-KIND rule keeps it equal to `k == A_EMPTY` forever, and the general siblings §9 S2 names are per-NODE (SUSPECTED design/maintenance; effort trivial to state; blast: FIX-1's seven readers)

kindrow.def:45-48: "A row states the KIND-LEVEL answer only. An answer
that depends on the node or on context keeps its code in the reader."
§3.6 gives `UNIT` to `A_EMPTY` alone and keeps assertions `ZERO` (D77). The
unit's other members named in §9 S2 — `(?:)*`, `(?:){3}` (a REP whose body
is a width-0 `all` description) — are node-dependent, so by the file's own
rule they can never be `UNIT` rows; only moving assertions in would add a
member, and that is S2's open census. So the "three spellings MERGED into
one kind-row value" (§2.3) trades three `A_EMPTY` tests for a value with
exactly one kind, at the cost of a new enum value seven readers must learn
(FIX-1). Confirm-by: the build brief listing any second kind that would
take `UNIT`. Alternative that satisfies SLOT-2's intent with no new value:
`rr_unit` read from the description's EMPTY arm (§3.5 already owns "EMPTY =
the unit of CAT"), leaving the kind row untouched.

### FIX-10 — Gate U2 names `foldsweep.py` as its instrument, but the "keeps the run" count is not in it (CONFIRMED, gate/doc; effort trivial; blast: stage 1's U2)

`rpsurvey_evidence/foldsweep.py` writes `whole_positions` per class from
`req_whole_run`; it computes no "keeps" verdict. The threshold ("position
count vs the 8+width a cut-free run would have") lives only in
`rpsurvey_report.md` prose (line 26), and that report decomposes 513 as
"24 ASCII + 210 + 279" (by byte length) where the note writes "24 + 489"
(by shape, `shapes2.py`). The script also takes WORKTREE and builds the
binary path itself (`W/build/pcrec`), and its input `FOLD_CLASSES.tsv`
comes from a third script (`folds.py`). "766 EXACTLY" is therefore a count
from a rule nobody committed, over two decompositions that agree only in
total. Fix: the stage-1 brief commits one script (classes in, the keep rule
`whole_positions == 8 + len(utf8(X))` stated, the count out) and pins 766
against `shapes2.py`'s category sum, per learnings §3 (one derivation).

### Prior findings re-opened in a new form (cross-reference)

- PREM-1 -> FIX-2 (the island fix over-reaches: today's range boxes enter).
- OWN-6 / K35 (B0 population) -> FIX-4 (the named instrument cannot give an
  empty diff for a correct stage 1).
- SLOT-2 -> FIX-1 (safety claim false) and FIX-9 (one-member value).
- SLOT-3 / OWN-1 / SLOT-6 -> FIX-7 (a second, code-point description).
- SIM-1 + SND-6 -> FIX-5 (info(S) vs hull) and FIX-8 (D187).
- PREM-7 / OWN-1 -> FIX-6 (altcls's key is already multi-byte).
No fix contradicts another outside FIX-5/FIX-7/FIX-8.

### Ruling check (O1-O5 and the D-rows), with consequences

- O1 (covering sets in facts only): rev 1 agrees (§3.1, §4.2, C1). Consequence
  surfaced: the covering CUBE (hull) needs its own information figure
  (FIX-5) and sits uneasily with D187 (FIX-8).
- O2 (stage 1 = UTF-8 lowering alone): agrees; the extra movers are listed.
  Consequence: the island admission of range boxes is an unlisted mover
  (FIX-2); the utf8 refusal set (size cap) is unlisted (FIX-3).
- O3 (set positions ride with [POS-ONE-DETECTOR]/D187): agrees (stage 3).
- O4 (per-length pieces now): agrees and states honestly that no pcrec
  reader consumes the fact. Consequence: stage 2p builds a fact, a limits
  row (group bound), a facts.def row, an independent model and a gate
  ahead of any consumer — D77 ("build under measurement") is cited against
  stage 2a (which waits for a bench cell) but NOT against 2p. O4 is the
  owner's explicit "now", so it governs; §13 q1 should say in plain words
  that O4 overrides D77 for 2p so the owner rules knowingly. A new facts.def
  row also moves every pattern's `--emit-facts` listing (emit_sweep stream 6,
  identity-required) and the `--list-*` dump if the group bound is a limits
  row: no artifact or abi move, but the sweep needs a declared delta.
- O5 (name the wider general form, siblings staged): agrees (§3.5, §9).
  Consequence: FIX-7 (phase/alphabet of the description).
- D76/D94: agrees (per-stage abi ritual, D94 grep, §4.7). Held: the seal's
  `L2 label empty` and `RX_VM_PROGRAM_BYTES 1502ULL` reproduce.
- D77: agrees for 2a and 1b; see O4 for 2p.
- D153: agrees (every stage after span_pick 1e; A-ISL overlap listed).
- D157: agrees (facts only, the piece set and string set stated as facts,
  kit request). The kit seam crossing is an `MF_SITE_ABI` event on the kit's
  side (memfn/include/CLAUDE.md shows bumps with "no pcrec byte moved"), not
  stated in 2p.
- D186: agrees (kinds per regime). Note: stage 2a's possessify exposure
  (FIX-1) would put unpredicted byte movers into a CHOICE stage.
- D187: partly; see FIX-8.

## PROBED-AND-HELD

- Ledger cites at the build tree (§2.1/§2.3/§3.6): `altcls.c:180/210/260/312`,
  `lower_enc.c:369-384` (seal comment through close), `req.c:344`
  (`rn_hull_mask`), `:470` (`rr_alt`), `:538` (`rb_rep_into`), `:549`
  (`rb_class_into`), `:698` (`case A_EMPTY`), `endwin.c:301`,
  `emit_vm.c:4079` (`vm_isl_words`), `:4091` (A_WCLASS), `:4093` (A_EMPTY),
  `:4099` (A_CLASS arm), `kindrow.def:61`, `limits.def:411`, and the ZERO
  readers `nfa.c:598`, `mrl.c:487`, `possessify.c:446/501/924`,
  `startset.c:83`: all exact. The ZERO-reader list is COMPLETE (grep
  `KTEXT_` over src/: 7 sites + req.c:581).
- "Outside an A_WCLASS it still declines a class, so byte artifacts cannot
  move (no A_WCLASS under -e byte)": holds — `wclass_of` is reached only from
  `lower_class_utf8` ("the byte instance never reaches it"), and ASCII-only
  utf8 classes return NULL (identity), so B0's ASCII clause holds for the
  island too (`x(?:[ab]1|q2|r3)y` utf8 island 0 today, no WCLASS).
- S-i reaches: `x(?:[éà]1|q2|r3)y` `RX_VM_ALT_ISLANDS 1` today.
- S-d/S-k/2b reach: `(?:ab|a|ad)`, `(?:for|fo|fox)`, `(?:ac|x|xc)` all
  `RX_ALTCLS_FACTORED 1` (but see FIX-6 on which rule); `(?:xing|ying)` 0
  (a real 2b mover).
- `RbRuns` comment "EXACTLY the one literal string" (`req.c:148`) is stale as
  §4.2 says; `.all` has no reader outside req.c (lines 449/451/453), so
  rr_alt row 1's widened `all` meaning is contained to `rr_cat`'s joins.
- rr_alt row 1's unstated siblings: `maxw` is common (equal width), `head`,
  `tail`, `best` all = the hull run with `all` true, offsets per `rr_cat`'s
  rules: consistent with `rr_pos`'s precedent; no reader outside req.c.
- `--emit-facts` fact names are advisory (`facts_listing.md` §1¶1, "no
  `abi` number"): a new piece-set fact is not an abi event; facts.def needs
  `deny` 0 (allowed) and its `depends` field stated.
- 253 appears twice (stage 1's +253 non-contiguous exact 2-cube; stage 3's
  +253 exact non-cube): two distinct categories in `fold_shapes.txt`
  (253 + 253), not a double count; 766 = 24 + 489 + 253 and 1417 =
  766 + 253 + 398 reconcile.
- Bit budget: 58 of 64 bits used (0-57, 55 the kit's) — basis of FIX-3.
- Compiles run: about 30 single-pattern compiles, no make, no suites.

## Standing questions

**Family.** Yes: this is the third member of a "canonical set, derived
spelling" family. (1) [CLS-TREE] S3: the `A_WCLASS` holds the code-point
SET and the byte tree is a derived spelling of it; (2) D187: a position is
a SET and a cube is derived; (3) this note: an alternation's fixed-width
pieces have one description (sets per position) and the rewrite owner's
trees are derived spellings. Rev 1 departs from the family in two places:
it calls the owner a "reproducible reduction, not a canonical form" (in
lowering the canonical object already exists — the WCLASS's set — and the
byte tree is a function of it, §3.3), and it adds the hull as a second cube
derivation (FIX-8). A second, larger sibling set the note lists as
"unchanged": `kset.c` (`pcrec_kset_walk`/`span_walk`/`width_walk`),
`startset.c` and `endwin.c` already compute per-offset position SETS of the
pattern's head/tail pieces (the rpsurvey report shows kset keeping
`{4B,6B,E2}` where req.c cuts). They are descriptions of fixed-width
pieces too: the head description at offsets 0..k, offset 0, and the tail.

**General form + unlocks (beyond §3.5/§9).**
- G-1: ONE position-set description with ANCHORS (head at 0, tail at end,
  interior stretches) whose readers are the run, the start set (offset 0),
  kset (head offsets), the end window (tail) and D172's spans; kset/startset
  /endwin become readers, deleting parallel walks. Trigger: a census showing
  the description's head positions equal (or refine, via width groups)
  kset's on corpus + bench; it is the facts half of the stream manifesto's
  "cross-engine pieces".
- G-2: the island reads the WCLASS SET, not the byte tree (shape-blind word
  enumeration), which removes FIX-2's dependence on box shape. Trigger:
  stage 1's island census (U4) or A-ISL's un-hold.
- G-3: per-reader information (`info` as a property of the reader: set vs
  cube), the general form of FIX-5. Trigger: the first stage-3 R2 listing
  where a picked run's hull information is below the floor.
- G-4: the kit-row-contract seam carries the piece set as a stated-but-
  unused field only after `fields.def` declares it (row_contracts.md: "a
  field added to the contract later is DECLINED until someone declares
  it"), so 2p's "inert" holds only while the field stays out of
  `fields.def`. Trigger: the kit's answer to §3.4's request.

END OF FINDINGS
