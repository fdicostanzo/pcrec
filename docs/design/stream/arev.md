# A-REV: one automaton-run record, one walk behaviour, hostable in a VM body

**Status: PROPOSED rev 1** (lane arevrev1, opus, 2026-11-06; plan row [STREAM], roadmap area
A-REV). Rev 0 was lane arevdesign's (2026-11-05). Rev 1 applies the RULED review
`docs/dev/reviews/2026-11-05-r5-arev.md` (every disposition ACCEPTED; its OWNER ADDENDUM of
2026-11-06). Design only: no build go, no step built. Anchors are at **main fd1a32021**, re-grepped
by this lane (`docs/dev/lanes/arevrev1_evidence/premise.out`); they did not move from the review's
freeze. Anchors move with code: re-grep the symbol. The manifesto is not edited by this note;
`roadmap.md`'s A-REV section is the area plan and points here. Client documents in force:
`docs/design/vlookbehind.md` **rev 2** and `docs/design/vlookbehind_pieces.md` **rev 0** (both
merged on main fd1a32021) `[r5 F5]`.

## REVISION 1 (review 2026-11-05 r5) — read first

Corrections are marked inline as `[r5 Fn]`. Rev 0's refuted claims are recorded where they stood.
In summary:

- **The first client is the lookbehind HAND-OFF** (Frank, 2026-11-06): the reverse DFA finds where
  a branch can start, existence when the machine has the branch's own language, otherwise the
  candidates farthest first, each confirmed by the forward VM run, which also fills the captures.
  It is a stream PROOF step judged on F1-F3 with the gate "no answer moves, nothing slower", not
  waiting on a speed trigger (§3.1, §4). Rev 0's `gate` row (a yes/no filter in front of today's
  loop) is a later option, not the first piece. Its `commit` row is no longer HELD: it is the
  hand-off itself.
- **Answer level (F1-F4).** The admission gains `!pcrec_nfa_has_bot` on the branch's reverse NFA,
  tested BEFORE the subset construction: `\G` makes the reverse machine a SUBSET, and `^`/`\A`/
  `(?m)^` make the build an internal-error refusal (§2.5). A branch's "no" sends the next branch
  from the cursor; only "yes" is the lookbehind's answer (§3.1). "Exact" is replaced by one fact
  read after the build, `lang = same | superset`, named so that it does not clash with the VM
  stamp's "exact" (§2.5).
- **The record carries facts, not C text (F14-F16).** One direction-neutral record: `DfaForm`
  made into it, not a third descriptor. Positions are typed references, the dead/no-accept hands
  are a declared hand set, tables belong to the machine-table entry, and the form's selected rows
  are recorded as plan outputs (§2.1).
- **One walk behaviour (F11).** Every walk the clients need is `farthest` (the smallest accepting
  position above a bound). Existence is "an accept exists", enumeration is the host re-walking with
  a moving bound. Rev 0's `first` exit needs new loop emission and is dropped (§2.2).
- **The host is a part plus a call record (F19, F21).** The walk is a file-scope PART emitted in
  its own slot by the plan; `VK_AUTO` is an in-body CALL record naming the part, its argument
  references, its result hands and its effect set (§2.3).
- **Today's code restated (F6-F13)**, the steps re-placed with a COST column (F28), the ratchet
  recipes restated by what they count (F23), the goals rewritten against F1 > F2 > F3 (F24), and
  the questions for Frank carried in the note (F27, §8).
- **§11** maps every finding to its section.

**The decision, in one paragraph.** Four reverse walks exist on main. Three render a `DfaForm`
through `emit_scan_loop`: RECOVER's pass and two of `rev-end`'s forms through
`emit_reverse_block`, `rev-end`'s one-seed and tagged forms by calling `emit_scan_loop` directly,
and the landmark walk through `emit_reverse_block` again `[r5 F6]`. The fourth, revdet, renders one
backward STEP over a reversed AST as VM records, and its WALK loop is a separate host loop
`[r5 F10]`. What none of them has is a DESCRIPTION a second process could read: the machine is a
`Job` field, the floor and names are C strings frozen into `static const DfaDir` copies, and the
form is chosen by `dfa_form_derive` from inputs the walk does not name. The kind this note
proposes is one direction-neutral AUTOMATON-RUN RECORD (`DfaForm` made into it), one walk
behaviour (`farthest` above a bound), a declared hand set, machines from one per-artifact table,
and one new host: a file-scope part called by an in-body record. Its first client, built as a
stream proof step, is the lookbehind hand-off: the reverse DFA of each varying branch finds the
candidate starts, existence when `lang = same` and the branch has no group, otherwise the
candidates farthest first, each confirmed by the forward body run that fills the captures. The
hand-off is sound on every admitted body because the machine's language fact is read after the
build and every construct that NARROWS a reverse machine is declined before it (§2.5); the STOP
RULE does not fire (§3.1).

## 0. Goals `[r5 F24: rewritten against the owner's criteria]`

Ranked by the manifesto's own order: F1 over F2 over F3; F4 is a constraint on how they are met.
The gate binds every step and is not a goal to trade.

**The gate (every step).** No answer moves: no match, group or give-up class changes except where
a row's evidence names the change (the hand-off's one-way give-up, §3.1). Nothing is slower: a
byte-moving step shows no regime slower beyond noise (D186's choice bar); a byte-identical step
shows movers = 0 under `scripts/emit_sweep.py`.

1. **G1 = F1 Focus (whoever changes pcrec next).** A reverse or forward walk is changed in ONE
   place, its record and the one renderer per rendering. Checkable: the proof step's diff,
   classified by roadmap §7 item 5, has its row part (the lookbehind rows), its declared crossings
   (the new record kind, the part slot, the machine-table entry) and NO undeclared crossing; a new
   walk instance after S1 adds a record, not a `DfaDir`, a renderer or a host loop (ratchet R28',
   R03', R10' do not rise, §4.3).
2. **G2 = F2 Flexibility (a future target).** The record carries no target text. Checkable: the
   record's fields are row names, typed position references, hand names and ids (§2.1); a grep of
   the record type for `const char *` fields that hold C finds none after S1 (rev 0's `seed`,
   `floor`, `dead` and `names` were C text, which is the manifesto's F2 falsifier `[r5 F14]`).
3. **G3 = F3 Division of labour (the manager dividing lanes).** The walk part can be validated
   alone. Checkable: a record-in / text-out golden check for the part renderer, and an oracle for
   the part's answer that runs without the VM: for a branch `B`, a `from` and a `bound`, the
   smallest `s ≥ bound` such that libpcre2 matches `B` anchored at `s` with its end at `from`
   (§3.1 "Per-part oracle"). Neither exists today: every witness is an end-to-end matcher cell.
4. **F4 constraint, no blindness.** The language fact that admits a row, the hand a walk returns
   and the facts that flow back (the tag encoding and tie bit, the empty-at-n probe, the landmark
   walk's reach) are declared fields, not conventions (§2.1, §2.2). Checkable by the seam
   round trip (manifesto principle 9): the record written as text and read back renders the same
   bytes. A caller-visible listing of the record (rev 0's "every instance prints its operands in
   `--emit-ir` / the trace") is NOT claimed: `--emit-ir` and `--trace` are VM-only, so it would be
   an interface change (D80) and waits for [IFACE-PUSH] `[r5 F24]`.

**Non-goals.** A reverse VM (owner, 2026-11-05). Tagged-capture DFA tables (TDFA) for revdet's
groups (§5). Unbounded lookbehind ([LB-EXIST], HELD). A speed CASE for any step: speed is the gate
(manifesto). Choosing between the open "VM base" frame and today's two-engine reading (§6 uses it
as a lens only).

## 1. Today, at main fd1a32021 `[r5 F6-F13: restated]`

**Premise test (this lane).** Every symbol below was re-grepped at fd1a32021 (premise.out). F1's
cell reproduces with libpcre2 10.46 as a library: `(?<=\Ga{1,2})b` on `aab` gives (2,3) from offsets
0 and 1 and nomatch from 2; `(?<!\Ga{1,2})b` gives nomatch, nomatch, (2,3).

| walk | machine (built by) | where it starts | lowest position, context | what it records | finisher | host |
|---|---|---|---|---|---|---|
| W1 RECOVER's reverse pass: `unanch_scan` (src/gen/emit_dfa.c:13495), four callers (`emit_unanchored`, both `rev-end` relocates, the landmark walk's LOWER relocate) `[r5 F12]` | `Job.rdfa`, mandatory | the forward accept | `search_from`; the byte below it is read (S74) | the smallest accepting position; NO tag of its own: the distance set `accv` is the FORWARD form's (`fwd->accv`, :13629) `[r5 F8]` | report SPAN | inline |
| W2 `rev-end` (`emit_rev_end` :14229) | `Job.rdfa`; on `tagged` the driver SWAPS the lowered set into the plain slots (`revend_choose_form`, src/core/compile.c:568), so the emitter never reads `xrdfa` `[r5 F7]` | per FORM, chosen by the declared `revend_forms[]` table (five rows: denied, one-seed, tagged, two-seed, overflow): the two-seed form loops seeds {n, n − 1 before a final newline}, keeps the min and a tie bit; the one-seed form starts at a COMPILE-TIME seed state chosen by the last byte and probes empty-at-n after the walk; the tagged form adds `revend_dist` `[r5 F6]` | `search_from` | per seed, the smallest accept; tagged: plus a ≤ 7-bit distance set, tie = popcount > 1 | FINISH: report, or `verify-at` / `search-from` (via W1) on a tie | inline |
| W3 the landmark walk (`emit_landmark_walk` :14398) | `Job.lmdfa` from the cut P·L (`lmwalk_build`, compile.c:547; own cap; built only where `lmnfa.erased == 0`) | `landmark_position + 1` per LMHIT hit | `search_from` (`dfa_dir_landmark`, the reverse strings under another name) | the smallest accept; dead → next hit | anchored A inline (`dfa_dir_lmverify`, the FORWARD twin), or LOWER: relocate via W1; the verify writes `lmwalk_reach`, which the NEXT walk reads `[r5 F14]` | inline |
| W4 revdet: the STEP `vm_rev_emit` (emit_vm.c:5521, record `Rev` :5500); the WALK loop in `vm_revdet_rep` (:5705) `[r5 F10]` | the reversed body AST (`Ast.u.rep.revbody`, set by `revdet.c`) | the committed boundary (the walk's cursor local) | the loop's entry slot | the step: one predecessor boundary (unique by the reverse check), group positions written mid-step into ONE per-artifact pair of sink arrays shared by every revdet walk (`VL_GROUP_SPAN`/`VL_GROUP_SEEN`, vm_stmt.c:482-483) | the loop: re-seed from each landing, stop when all groups are seen or at the floor, keep the first step's landing for the greedy retreat (`VPOS_REVDET_PREV`) | INSIDE the VM body, as records |

**What they share.** W1-W3 render a `DfaForm` through ONE body, `emit_scan_loop` (:13244), which is
also every FORWARD walk's body (forward scan, anchored, lmverify, retry). `emit_reverse_block`
(:13409) is a thin wrapper that sets the form's `lbl` and `dead`; it has three callers (:13625
RECOVER, :14317 rev-end two-seed, :14489 landmark), and `rev-end`'s one-seed and tagged forms
bypass it (:14054, :14116) with their own seed code `[r5 F6]`. It dates from fddd803ac
([OPT-REVEND]) `[r5 F12]`. The optional machines are built by `revend_build_one` (compile.c:454),
which builds optional machines of BOTH directions (not the mandatory `rdfa`) `[r5 F12]`; each has
its own size-cap rung in `fit_rungs[]` (`drop-end-mark` :1360, `drop-landmark-walk` :1402)
`[r5 F22]`.

**What they do not share (the parallel parts).**
- **Machine identity is a `Job` field per client** (`rdfa`, `lmdfa`, the swapped lowered set) and
  `dfa_member_machines`' fixed `out[4]` (F, R, A, ML; :4916). A lookbehind needs one machine per
  varying branch per site.
- **The floor and names are C literals in five places**: the five `static const DfaDir` objects
  (forward, reverse, anchored, landmark, lmverify; :9340-:9460), one run-time copy
  (`pcrec_emit_dfa_retry`, `DfaDir dir = dfa_dir_anchored;` :14700, overwriting the names), AND two
  function members that print literals rather than the object's strings: `dir_rev_bound_accept`
  (:9297) prints `search_from`, which is S74's anchor, and `dir_rev_skip` (:9249) prints
  `rewind_position` `[r5 F13]`. `dfa_dir_landmark` also differs from `dfa_dir_reverse` in `ind`,
  `bind`, `tbl_hdr` and `acc_meaning` `[r5 F12]`.
- **The form is chosen where the walk is rendered.** `dfa_form_derive` (:12962) makes four
  `DFA_SELECT` choices (repr, view, seed, acc) from the deny flags, the route and the start-set
  fact, and callers override fields afterwards (`if (formw) rev.seed = &dfa_seeds[1];`). A process
  holding only a description of the walk cannot reproduce its bytes `[r5 F15]`.
- **The hands flow back by convention**: the distance bit set and its popcount tie, the one-seed
  form's empty-at-n patch, and `lmwalk_reach` `[r5 F14]`.
- **W4's record `Rev`** has two dead fields (`ga`, `ns`, read only in a comment) and takes no exit
  operand; its sinks are artifact-scope, not per instance `[r5 F10]`. Its run-time work charge is
  NONE: `vm_charge` (:932) is the compile-time node cap `[r5 F9]`.

## 2. The kind

### 2.1 The record (`AutoRun`, a name for the review, not a ruling) `[r5 F14, F15, F16, F18]`

**One descriptor, not a third.** `DfaForm` already holds machine, form rows, start (`from`), label
stem, dead hand and tag for every DFA walk, forward and backward. The record IS `DfaForm` made
direction-neutral and textless: its walk-describing fields become the typed fields below, its
choice pointers (`repr`, `view`, `seed`, `acc`) become recorded row NAMES, and every pointer the
renderer needs is resolved from those names by table lookup inside the renderer, a pure function
`[r5 F16]`. `Rev`'s live fields become the structural rendering's operands. The type lives in its
own part header (a name for the build lane, e.g. `src/gen/autorun.h`), not in `internal.h`
`[r5 F20, H-HEADER]`.

**The form is a plan output** (the review's leaning, adopted): `dfa_form_derive`'s four selections,
the skip and scan-edge state lists, the two folds and the entry facts are computed BEFORE
rendering and recorded; callers' overrides become writes to the record before it is frozen. Emit is
then a pure function of the record (roadmap §0a) `[r5 F15]`.

| field | type (no C text) | W1 | W2 | W3 | W4 | L (lookbehind branch) |
|---|---|---|---|---|---|---|
| `machine` | id of a machine-table entry (§2.4); the entry owns direction, tables and accessors | R | R (the lowered set after the swap is R; §2.4) | ML | the reversed body (structural entry) | one per varying branch |
| `rendering` | a row name of the rendering table: `table` or `structural` (renamed from rev 0's `repr`, which collided with `DfaForm.repr`, the layout axis) `[r5 F18]` | table | table | table | structural | table |
| `form` | the selected row names (`dfa_reprs`, `dfa_views`, `dfa_seeds`, `dfa_accs`), skip and scan-edge state lists, folds, entry facts | derived | derived per `revend_forms[]` row | derived | — | derived |
| `from` | a position REFERENCE: `FWD_ACCEPT`, `SUBJECT_END`, `HIT(stream)`, `SLOT(n)`, `CURSOR`, or a compile-time seed STATE id | `FWD_ACCEPT` | per form: a seed list {`SUBJECT_END`, `SUBJECT_END − 1` if the last byte is `\n`} combined MIN-with-tie, or STATE chosen by the last byte | `HIT(lmhit) + 1` | the cursor local | `SLOT(POS)` (the lookbehind's cursor) |
| `bound` | a position REFERENCE: `SEARCH_FROM`, `ZERO`, `SLOT(n)`, `CANDIDATE + 1` | `SEARCH_FROM` | `SEARCH_FROM` | `SEARCH_FROM` | `SLOT(entry)` | `ZERO`, then `CANDIDATE + 1` |
| `hands` | a map from the walk's three outcomes {`DEAD_ENTRY`, `NO_ACCEPT`, `ACCEPT(pos[, tag])`} to host hands (§2.2) | NO_ACCEPT → `return 0;`'s hand (rev 0 wrote NULL: wrong `[r5 F14]`), ACCEPT → SPAN | per form | DEAD/NO → next hit; ACCEPT → verify or LOWER | → the fail label / the step's landing | §3.1 |
| `tag` | `none`, or `distance` = a ≤ 7-bit set, end = lowest set bit, tie = popcount > 1 | none `[r5 F8]` | tagged form: `distance` | none | `groups` (writes the artifact-scope sinks) | none |
| `instance` | an id; the renderer derives label stems per target from (entry, instance) | 0 | 0 | 0 | the loop's index | (site, branch) |
| `placement` | `inline` or `part` (§2.3) | inline | inline | inline | inline (records) | part |
| `container` | `search function` or `VM body` `[r5 F21]` | search fn | search fn | search fn | VM body | VM body |

**What left the record** `[r5 F14, F21]`: rev 0's `seed`/`floor`/`dead`/`names` as C strings, its
`exit` (one behaviour, §2.2), its `charge` (a `VK_WORK` record beside the call where one is owed,
§3.1), and the `rv<i>` group sinks (an artifact-scope resource of the structural rendering,
declared once, shared by every structural walk) `[r5 F10]`.

**Two stems, two owners** `[r5 F14]`. Table and accessor names belong to the machine-table ENTRY
and are emitted once per (machine, direction): today `emit_rev_end`'s relocate arm walks one set of
tables twice (`DfaForm rel = *rev;`). Label stems belong to the walk `instance`.

**The seam round trip.** Written as text, the record is: an entry id, row names, two position
references, a hand map, a tag kind, an instance id and two placement words. Every field is either a
name in a declared table or an id; nothing names a method of the kit (D157). Scan edges inside a
table machine stay the kit's (D161 add. 17: the reverse DFA is the scaffolding, scan edges the
optimization inside it).

### 2.2 One walk behaviour; the five exits are hands and host loops `[r5 F11, F17]`

**`farthest` is the only walk behaviour.** Run from `from` toward `bound` until the machine dies or
the bound is passed, recording the accept nearest the bound. Rev 0's `first` ("stop at the first
accept") does not exist in the table renderer: `emit_scan_loop` records each accept and continues,
and scan edges record the LAST position of an accepting run, so `first` as a position would
overshoot inside a skip `[r5 F11]`. Existence needs no early stop: "an accept exists" is
`farthest`'s result tested against `NO_ACCEPT`. An early-stop loop exit is a later rendering of the
same answer, HELD, trigger: a measured cell where a long-dying existence walk shows (D77). W4's
single step needs none either: revdet's (U2) gives at most one accept per step.

**The exits are roadmap §4's suffixes, and §4 is their home** `[r5 F17]`. The admission table spells
an automaton record's exit as `AUTO COMMIT / ENUM / GATE / EXISTS / TAGGED`; this note uses those
words and maps each to the one behaviour plus a hand and a host loop. The hands are spelled in the
existing `CT_*` claim masks (src/gen/emit_dfa.c:9882, the `CAND_HAND_*` vocabulary at :9901-9907),
so no new hand vocabulary is introduced and R12 does not rise.

| exit (roadmap §4) | the walk | the hand at the seam, in `CT_*` terms | the host loop | who needs it |
|---|---|---|---|---|
| `AUTO COMMIT` | `farthest` once | ACCEPT on `lang = same`: `AT` (`CT_LOWER | CT_UPPER`); on a superset: `LOWER` (`CT_LOWER`); NO_ACCEPT: `NOMATCH` (`CT_VERDICT`) | none | W1, W2, W3 |
| `AUTO ENUM` | `farthest`, re-run with `bound = CANDIDATE + 1` | each ACCEPT is a re-enterable candidate whose claim is `CT_LOWER` above the previous one; NO_ACCEPT ends the enumeration | the moving-bound loop (§5) | L (the hand-off), [LANDWALK-ALLACC] |
| `AUTO EXISTS` | `farthest` once, result tested | a branch VERDICT: ACCEPT = the branch holds, NO_ACCEPT = the branch fails (`CT_VERDICT` for the branch, never for the lookbehind) `[r5 F3]` | none | L on `lang = same` and no group; roadmap §4 row 12 ("captureless regular lookaround as a predicate") in a VM body |
| `AUTO GATE` | `farthest` once | NO_ACCEPT on a superset decides (`CT_VERDICT`); ACCEPT passes | the guarded host's own | rev 0's lookbehind `gate` row, now a LATER option (§3.1) |
| `AUTO TAGGED` | `farthest` with `tag` | ACCEPT(pos, distance set) | none | W2's tagged form; W4 (`groups`) |

Rev 0's `exist` collided with `CAND_HAND_EXISTS` ("an end some match has"); the exit is now
`AUTO EXISTS` tied to row 12, and its hand is a branch verdict `[r5 F17]`. `seed` has one meaning
in this note: none. The walk's start is `from` (`DfaForm.from`'s word), and `DfaSeed` stays the
form's seed-row axis `[r5 F17]`.

Rev 0 §2.2 argued that "enumerate" needs no third behaviour; that stands, and is now true of every
exit.

### 2.3 Hosting inside a VM body: a part and a call record `[r5 F19, F21]`

Two placements exist today and the kind keeps both: `inline` (W1-W3: the walk's text in the
enclosing search function; byte identity requires it) and records in the body (W4).

The new combination is a TABLE machine run from inside a VM body. Rev 0 had a `VK_AUTO` renderer
write a file-scope function as a side output; that is a second output channel beside vm_stmt.h's
one-writer tiling, and rev 0's "precedent" (`pcrec_emit_dfa_engine`) is called by the COMBINATOR
level (src/gen/emit_comb.c:576, :580), not from the body `[r5 F19]`. Rev 1:

- **The walk is a PART.** A stream-level record with its own stem, emitted by the plan in its own
  slot BEFORE the matcher function, the way the combinator emits the hybrid's DFA part. Its
  declared signature: `ptrdiff_t <part>(subject, subject_length, from, bound)`, returning the
  accept nearest `bound` or −1 for NO_ACCEPT (DEAD_ENTRY is folded into −1: the call has no other
  caller-visible outcome). Its declared EFFECTS: reads `subject[bound − 1 .. from]` (the context
  byte below the bound, S74's rule, and the byte at `from`, the seed's right context); writes
  nothing but its result; transfers no control; never touches frames, slots or the trail.
- **`VK_AUTO` is an in-body CALL record**: operands = the part's id, `from` and `bound` as
  REFERENCES rendered as values (`(size_t)slot_values[<n>]`, never the index: vlookbehind rev 2
  §5.6 V3's rule, pickup 4), the result's destination (`scan_position` or an untrailed local), and
  the hand map ({ACCEPT, NO_ACCEPT} → labels). One renderer, one output: the body buffer. The
  effect set above is a field of the record, which is [VMREC] (c)'s r9 rule for kit windows
  ("opaque with DECLARED EFFECTS") applied to a second opaque kind.
- **The work charge is not a field** `[r5 F21, F9]`. Where a charge is owed it is a `VK_WORK`
  record beside the call (vlookbehind rev 2 §5.5's own spelling). There is no precedent for a
  per-walk run-time charge (revdet's walk has none), so §3.1 argues the lookbehind's from scratch.

gcc inlines a one-caller `static` function, so no speed claim rests on the call; placement is a
fact of the host (a VM body cannot hold a table walk inline without a new tiling rule), not a
priced choice.

**The finisher contract.** The kind hands a typed position; the finisher is the host's, chosen by a
FINISH row (D156), never by the kind: report (W1), `verify-at` with the anchored machine (W3, W2 on
a tie), `search-from` relocate (W2, W3), the VM body continuing (W4), and the new one: a forward
body run from the candidate with its end required at the cursor (L; vlookbehind rev 2 §5.1's body
and end-check). That last finisher is the "VM forward run for captures" of the owner's example. A
fact that flows BACK from a finisher to the next walk is a declared field of the host loop's state,
never a convention: today the landmark walk's `lmwalk_reach` (the verify's farthest read byte) is
such a fact, and S1 declares it `[r5 F14]`.

### 2.4 The machine per site `[r5 F4, F7, F20, F22]`

**One table for every machine, H-FLAGS's shape.** H-FLAGS already declares the owner of machine
building ("one builder") and its interim shape ("a new machine is requested by a row and built by
the one builder"). A table holding only the optional reverse machines would leave the forward and
mandatory ones as `Job` fields, two identity mechanisms that W3 alone reads both of `[r5 F20]`. So:
the lookbehind's per-branch need is argued here as H-FLAGS's TRIGGER (its machine half), and the
step that builds the table (S1M, §4) moves EVERY machine (`dfa`, `rdfa`, `adfa`, the lowered set,
`lmdfa`, and the lookbehind's) into one per-artifact table, with `dfa_member_machines` reading it.

- **An entry** = (site, role, direction), its build REQUEST and its realized FACTS, immutable once
  built. The request names every input that sets the language: direction, root, `collapse`
  (`b->collapse`, src/ir/nfa.c's count-collapse arm) and `prune` (dfa.c:979-987: a pruned machine
  drops lower-priority continuations past an accept; every reverse build passes `false` today)
  `[r5 F4]`. The facts are the realized `Nfa.erased`, `has_bot` and the `lang` fact of §2.5.
- **The lowering is a table-level fact.** D164 add. 4 is "one lowering per artifact": the `tagged`
  form today SWAPS the whole lowered set into the plain slots (`revend_choose_form`). In the table,
  the lowering is one fact of the table and a form decision ADDS entries, never swaps; a walk
  references the entry it reads. That removes rev 0's "R or XR" column, which described a slot no
  emitter reads `[r5 F7]`.
- **Tables are the entry's**, emitted once per (machine, direction) (§2.1).
- **Size.** Each optional machine has its own build cap (`revend_build_one`'s shape: overflow
  record and subset budget restored; an overflow is the row's DECLINE). The lookbehind's machines
  also get a size-cap RUNG in `fit_rungs[]`, in H-LADDER's declared append shape, as every shipped
  optional reverse machine has (`drop-end-mark`, `drop-landmark-walk`): without one, an artifact
  that `range` alone would fit is refused because of an optimization (D158) `[r5 F22]`. The rung's
  drop flag uses the existing `FitSets` + `*_dropped` spelling, so R11 does not rise; H-LADDER's
  R13 counts the hub, not its rows.

### 2.5 The language fact, and what is declined before the build `[r5 F1, F2, F4]`

**One fact, read after the build:** `lang`, with two values.
- `lang = same`: `erased == 0`, the request had `prune` and `collapse` off, and the NFA has no
  BOT-family node. The machine accepts at `s` exactly when `subject[s .. from)` is in the branch's
  language with its context.
- `lang = superset`: `erased != 0` (an atomic, possessive or lookaround erasure; `NFA_ERASED_*`),
  same request. Every recorded erasure WIDENS the language, so no accept in the machine means none
  in the truth, and an accept is a candidate to confirm.

The word is deliberately not "exact": `RX_VM_PREFILTER_LANG` (emit_vm.c:11311) already stamps
"exact" for atomic- and lookaround-erased machines, meaning only "not count-collapsed" (filed there
as F-13). A lane reading rev 0's "exact" in the stamp's sense would have admitted WD1's machine
`[r5 F4]`.

**What a recorded erasure cannot see: NARROWINGS** (the review's lesson 2). Two constructs make a
reverse machine of a branch wrong in the other direction, and neither sets an `erased` bit:
- **`\G`** (`A_GSTART`: kindrow.def:64 erases nothing; nfa.c:704 lowers it to `N_GSTART`). In a
  reverse machine `\G` is met only after a byte is consumed, where `gst_ok` is false (dfa.c:1028),
  so every path through it dies: the machine is a SUBSET. F1's cell: `(?<=\Ga{1,2})b` on `aab` is
  (2,3), and an existence row would answer nomatch; the negative form flips the other way `[r5 F1]`.
- **`^`, `\A`, `(?m)^`** (N_CTX rows reading an absent previous character). The reverse build hits
  `DFA_INVARIANT` (dfa.c:1583), which calls `pcrec_ctx_fail` and longjmps: a compile REFUSAL
  ("internal error"), which `revend_build_one` cannot catch (it restores only the overflow record)
  `[r5 F2]`. `(?<=^a{1,2})b` on `aab` is (2,3) in libpcre2: a valid pattern the row would meet.

Both are exactly what the existing predicate `pcrec_nfa_has_bot` (nfa.c:1342) reports, and the
landmark walk screens the first explicitly (lmwalk.c:181, `lc_g1`'s "gstart"). So the admission
gains `!pcrec_nfa_has_bot(branch reverse NFA)`, TESTED ON THE NFA, BEFORE the subset construction:
the order is the fix for F2, not only the conjunct. `\K` would be a third (a report shift), but it
is refused inside every lookaround by both libraries (err 199); `(?m)$`, `$`, `\Z`, `\z` and `\b`
at the cursor are RIGHT-context rows, read from the byte at `from` as RECOVER's pass reads the byte
at the match end (nfa.c's header to `pcrec_nfa_has_bot`: "`(?m)$` does NOT join"), and they get a
witness (WD8).

### 2.6 The generalizations, against vlookbehind rev 2 §4's checklist

| vlookbehind item | where it lands here | status |
|---|---|---|
| G1 machine per site | §2.4, one table for every machine (H-FLAGS's machine half) | proposed (S1M) |
| G2 floor and seed as operands | §2.1 `from`, `bound` as typed references | proposed (S1) |
| G3 names per instance | §2.1: label stems per `instance`, table stems per entry | proposed (S1) |
| G4 the exits | §2.2: one behaviour, the exits as hands and host loops | proposed |
| G5 hosting in a VM body | §2.3: a part plus `VK_AUTO` | proposed (S3) |
| G6 the finisher on the VM route | §2.3's finisher contract; built by vlookbehind stage 1 | proposed |
| (new) the build request and `lang` | §2.4, §2.5 | proposed |
| (new) rendering | `table` / `structural`, a declared row table's OUTPUT, recorded as a selection; D161 add. 17's prefix-shape tiers are NOT rendering rows (they fold under the scaffolding) `[r5 F18]` | proposed |
| (new) tags | `distance` and `groups`: two tag kinds of one hand, noted, not unified (two members) | noted |
| (new) the context at the bound and at `from` | S74's rule at the bound; the byte at `from` for right-context rows (§2.5) | proposed, read from code |

## 3. Clients, in order

### 3.1 First client, the proof step: the lookbehind HAND-OFF `[r5 F1-F5, OWNER ADDENDUM]`

**What Frank ruled** (2026-11-06): the first cross-engine piece is the hand-off form. The reverse DFA
finds the start, existence when the machine has the branch's own language, otherwise the
candidates farthest first, and the forward VM run confirms each and captures. It is built as a
stream PROOF step judged on F1-F3 with the gate "no answer moves, nothing slower", not waiting on a
speed trigger ("seems strange to go all that way and then stop early"). The order is unchanged:
after vlookbehind stage 1 and [VMREC]'s analysis stage.

**This is the client's own row** `[r5 F5]`. Vlookbehind rev 2 §5.4 has ONE `reverse-dfa` row whose
exits are "Exact machine and no capture: EXISTENCE (no VM run). Otherwise candidates farthest
first, each confirmed by §5.1's step". Rev 1 adopts that row, its admission ("no side-effecting
construct" included, which rev 0 dropped), its floor (0, not rev 0's `max(0, cursor − W)`, see
below) and its prerequisites (the reverse `AUTO` kind hosted in a VM body; [GIVEUP-DIFF]). The
differences below are PROPOSALS to the client's owner document, which is vlookbehind's to change:
(1) the `!has_bot` conjunct and its order, (2) "exact" read as `lang = same`, (3) the per-branch
verdict wording, (4) the cursor-rung spelling of the candidate loop (below), (5) two of the
client's prerequisites read differently, stated here rather than dropped silently: rev 2 §5.4 cites
[LANDWALK-VM] beside G5, but the VM-hosted part of §2.3 is the general form [LANDWALK-VM] will
itself use, so the lookbehind does not wait for that row; and rev 2 §4 "Why not now" ties the row
to P-d (rev 0's S4) because building G1-G5 for it alone "would add a third hand-written reverse
walk", which S1 and S1M remove (the proof step is an instance of the record, not a hand-written
walk), so P-d is not a prerequisite either. [LB-EXIST] IS filed (rev 0 said it was not): it names "reverse-dfa's
existence exit" as its filter's reverse form, which is this row's `AUTO EXISTS` `[r5 F5]`.

**Per-branch selection** (one row per varying branch; first match; rev 2 §5.1b's table gains two
rows in front of `range`):

| order | row | applies when (conjuncts tested in this order) | exit | finisher |
|---|---|---|---|---|
| 1 | `one-length` | `lo_i == hi_i` | — | today's bytes (ruled (A)) |
| 2 | `reverse-dfa`, existence | (a) `lo_i < hi_i`; (b) no backreference, variable, call, callout or other side-effecting construct in the branch (the AST, before any build); (c) `!pcrec_nfa_has_bot` on the branch's REVERSE NFA (before the subset construction); (d) the reverse DFA builds under its own cap and its rung is not dropped; (e) the host is a VM body; then, read after the build, `lang = same` and the branch has no capturing group | `AUTO EXISTS` | none: ACCEPT → the branch holds; NO_ACCEPT → the next branch from the cursor |
| 3 | `reverse-dfa`, candidates | (a)-(e) as row 2, `lang ∈ {same, superset}` | `AUTO ENUM` | each candidate confirmed by the forward body run and the end-check |
| 4 | `range` | `lo_i < hi_i` | — | rev 2 §5.1, the total fallback and the reference |

**Rows 2 and 3 are ONE D186 choice row with two exits decided by a fact** `[r5 F29]`. The choice is
`reverse-dfa` versus `range` (one evidence set, one lever); the exit is selected by the recorded
`lang` fact and the group test, not by a regime. A cap overflow or a has_bot hit is the row's
decline to `range`, never a refusal.

**What "yes" and "no" mean** `[r5 F3]`. Every walk answers for ONE branch: ACCEPT under row 2 means
this branch holds (the positive lookbehind succeeds; the negative one fails, through today's
`L_ok` cut); NO_ACCEPT means this branch fails and branch `i + 1` starts from the cursor, which the
walk never moved. Witness: `(?<!a{1,2}|b)x` on `bx` is nomatch and `(?<=a{1,2}|b)x` on `bx` is
(1,2); read as the lookbehind's answer, branch 1's "no" flips both.

**The floor is 0, the client's** `[r5 F5]`. Rev 0 floored at `max(0, cursor − W)` and presented it as
the client's. With `collapse` off (the row never requests it) every admitted machine has a finite
language whose lengths lie in `[lo_i, hi_i]` characters: atomic and lookaround erasures do not
change a branch's width range. So the machine dies by itself within `hi_i` characters, and the
bound adds nothing. The bound is 0, not `search_from`: the body may lie before the start offset
(WD5). The context byte below an accept is read as on every reverse walk (S74). A count-collapsed
machine would need the width bound back (its lengths are unbounded) and a character-distance check
under UTF-8; it is not proposed.

**The records, in the cursor-rung spelling** (vlookbehind_pieces §6, RECOMMENDED there, NOT YET
RULED by Frank). Row 3, per branch `i`, inside today's `vm_look` wiring:

```
L_b_i:    if (scan_position < lo_i) goto L_b_(i+1)     // guard, as range (bytes >= characters)
          t = AUTO(part_i, from = POS, bound = 0)       // VK_AUTO: the farthest start, or -1
          if (t < 0) goto L_b_(i+1)                     // NO_ACCEPT: nothing moved
          scan_position = t
L_try_i:  RX_PUSH(&&L_adv_i, scan_position)             // the frame saves the CANDIDATE
          RX_CHARGE_WORK(scan_position < POS)           // VK_WORK: one per non-empty candidate
L_body_i: <B_i forward, vm_emit unchanged>
          if (scan_position != POS) goto rx_fail        // the end-check: range's, declines
          goto L_ok
L_adv_i:  // popped: scan_position = this candidate
          t = AUTO(part_i, from = POS, bound = scan_position + 1)   // the next farthest
          if (t < 0) { scan_position = POS; goto L_b_(i+1) }        // VSK_RESTORE, exhausted
          scan_position = t; goto L_try_i
```

Row 2, per branch `i`: the guard, the call with `bound = 0`, `t < 0 → L_b_(i+1)`, else `goto L_ok`.

**Under rev 2's spelling, if the cursor-rung spelling is NOT adopted.** Rev 2's frame saves the
CURSOR and carries the candidate in a trailed slot. The hand-off would then need a trailed
candidate-POSITION slot rewritten per candidate: no existing family's contract fits it
(`SLOT_COUNTER` is an iteration count; the low-water family is written once per entry), the trail
term becomes `2 + Σ (hi_i − lo_i + 1)` over row-3 branches (candidates ⊆ range's, so rev 2's bound
holds), and every row-3 branch carries a K134 checkpoint. Under the cursor-rung spelling the row
needs NO slot and adds NOTHING to the trail term; its back edge closes a trail cycle only where the
body itself writes the trail (captures). This is a second argument for the cursor-rung spelling,
on top of vlookbehind_pieces' own.

**The per-row reader table** (rev 2 §5.1b's second table, pickup 8; cursor-rung spelling first,
rev 2's spelling in brackets):

| row | slot | push sites | trail entries per evaluation | labels | K134 checkpoint | role texts |
|---|---|---|---|---|---|---|
| 2 existence | none | 0 | 0 | `bl` only (no `bodl`, `endl`, `L_try_i`, `L_adv_i`: pickup 6) | none | its own: "branch %d, width %d..%d: reverse DFA, existence" |
| 3 candidates | none [a trailed position slot] | 1 (`L_try_i`) | 0 [`hi_i − lo_i + 1`] | today's three plus `L_try_i`, `L_adv_i` | only where the body writes the trail [every row-3 branch] | range's texts with "candidates from the reverse DFA" |

**Composition with `vm_look`** (pickup 7). Row 2 pushes no frame and leaves `scan_position` at the
cursor on both outcomes, so after "yes" the frames state is the range loop's after success minus
its `L_adv_i` frame (and the body's choice points), and after "no" it is the exhausted loop's. On
the atomic and negative forms `L_ok` cuts to the mark either way. On the NON-ATOMIC positive form
`(?<*...)` the missing frames are retries that a capture-free body cannot make observable: every
retry ends at the same cursor with the same groups, so the follow fails again (vlookbehind_pieces
§3: "Yes/no is order-free", 0 differing cells over every negative and capture-free sweep cell).
The difference is frames and steps only, which is the one-way give-up change below.

**Soundness of row 3**, by construction against `range`. Range tries every start whose distance lies
in `[lo_i, min(hi_i, cursor)]`, farthest first, confirming each by the body run and the end-check.
Row 3 tries the subset of those starts that the machine accepts, in the same order (ascending
position = farthest first; the moving bound gives exactly the next one). A start the machine does
not accept cannot pass the confirm: `lang` is same or superset, so the truth is inside the
machine's language. A skipped candidate leaves no state behind in range either: a failed confirm
backtracks to the frame, which restores the position and every trailed write. So the first
confirmed candidate, every group it writes and, on the non-atomic form, the order of every later
retry are range's. Branch order is kept by per-branch machines (WD2). Under UTF-8 the byte machine
accepts only at character boundaries of valid input, and candidates replace the back-step, so the
`$_back_step` sentinel and `$_next_pos` are not used by this row.

**Work and give-ups** `[r5 F9, F21]`. Range charges, per evaluation of a branch, Σ d over the
candidates tried (rev 2) or `k + (candidates − 1)` (cursor-rung spelling). Row 3 charges ONE per
candidate it hands to the confirm that starts below the cursor (the empty candidate at `lo_i = 0`
charges nothing, as range's `d = 0` candidate does: `RX_CHARGE_WORK` charges only a positive
amount), and nothing for the walks; row 2 charges nothing. Its candidates are a subset of range's,
and every range candidate below the cursor is charged at least one, so every budget counter
(work, steps, frames) of rows 2 and 3 is at most range's in every evaluation: they never give up
where range answers, and may answer where range gives up. That is a ONE-WAY give-up change, which
[GIVEUP-DIFF] (direction-checked GIVEUP1) must cover before the row ships. The walks are bounded
without a charge: each is at most `4·hi_i` bytes (UTF-8's widest character), and at most
`hi_i − lo_i + 1` walks run per evaluation, each reached through charged VM steps.

**The STOP RULE does not fire.** The hand-off is sound on every body the row admits: a widening
erasure (atomic, possessive, nested lookaround) only adds candidates that the confirm rejects; the
narrowings (`\G`, `^`, `\A`, `(?m)^`) are declined before the build; backreferences have no machine
(`compile_ast`'s A_BREF arm) and decline; callouts, verbs and `\K` are refused inside a lookbehind
today and stay declined by conjunct (b) on the day they are admitted. The atomic counter-example:
`(?<=(?>ab|a)b{1,2})x` on `abx` is nomatch in libpcre2 while the erased machine accepts at 0; row 2
declines (`lang = superset`) and row 3's confirm rejects the candidate, so the answer is range's.

**The gate** (manifesto §5, Frank's "no answer moves, nothing slower"):
- **Answers.** `tests/lookaround/run_lookaround_diff.sh` (rev 2 gate 1's harness) over the
  generated cell set with the row forced on and with it denied: 0 differing answers against
  libpcre2 10.46 outside D142's stated UTF class, the zero-width-repeat divergence (rev 2 V6:
  `(?<=(?:)*a{1,2})x` reaches row 3, since it varies) on its own line (pickup 9); plus the corpus
  answer identity, default versus deny.
- **Bytes.** Every artifact without a varying lookbehind branch is byte-identical (the comparator);
  artifacts that take rows 2-3 are new emission: an abi event at the landing number, readers by
  grep (D76/D94), and a `tuning.md` hunk naming the lever (D80).
- **Nothing slower.** Rev 2 §5.4's evidence requirement, all four regimes: (a) short bodies, (b)
  the bench's `negation-scope-lookbehind-var` on its own subjects (BLOCKED on pcrec until stage 1
  ships and the bench lifts its `lookbehind-variable` declaration: an inbox entry the manager owes
  then), (c) a wide body whose candidates do not fail at the first byte (`(?<=\w{1,64}x)y`), (d) a
  random-like subject. A regime slower beyond noise NARROWS the row's admission (a minimum width, a
  body shape), never adds a parallel path. The lever is test-only unless a regime can be slower
  after narrowing, in which case it is public (flag follows caller effect).

**Witnesses** (each a libpcre2 10.46 cell, `premise.out`; in the default build each is red under
its plant where the row admits; in the row's deny build the same cell runs `range` and is red under
stage 1's own plants, so every cell can fail in both builds):
- WD1 (row 2 on a superset): `(?<=(?>ab|a)b{1,2})x` on `abx` nomatch, `(?<!(?>ab|a)b{1,2})x` (2,3);
  rev 0's `(?<=(?>a|ab)b)x` / `(?<!...)` on `abbx` nomatch / (3,4). Plant: the `lang` conjunct
  dropped.
- WD-G (F1, `\G`): `(?<=\Ga{1,2})b` on `aab` from 0, 1, 2: (2,3), (2,3), nomatch; `(?<!\Ga{1,2})b`:
  nomatch, nomatch, (2,3); on `caab` from 1: (3,4) / nomatch; controls `(?<=\Ga{1,3})b` /
  `(?<!...)` on `caab` from 0: nomatch / (3,4). Plant: conjunct (c) dropped.
- WD-A (F2, the order): `(?<=^a{1,2})b` on `aab` (2,3), `(?<!^a{1,2})b` nomatch, `(?<=\Aa{1,2})b`
  (2,3). Plant: (c) tested after the build (the cell becomes a compile refusal). The `(?m)^` cell
  needs a newline in the subject; it is owed by the build's harness (this lane's probe is
  line-based).
- WD-B (F3): `(?<!a{1,2}|b)x` on `bx` nomatch, `(?<=a{1,2}|b)x` on `bx` (1,2), also from offset 1;
  control `(?<!a{1,2}|b)x` on `cx` (1,2). Plant: a branch's NO_ACCEPT taken as the lookbehind's.
- WD2 (branch order): `(?<=(a{1,2})|(aa{1,2}))c` on `aaac` [3-4, 1-3, g2 unset]. Plant: one
  machine for the whole lookbehind, confirmed by the whole alternation (gives g2 = (0,3)).
- WD3 (farthest first): `(?<=(a{1,2}))b` on `aab` [2-3, 0-2]. Plant: the nearest candidate first.
- WD4 (non-atomic retry): `(?<*(a{1,2}))b\1c` on `aabac` [2-5, 1-2]. Plant: no `L_adv_i` re-walk
  (only the farthest candidate).
- WD5 (bound 0, not `search_from`): `(?<=a{1,2})b` on `aab` from 2: (2,3).
- WD6 (context below an accept): `(?<=\ba{1,2})x` on `baax` nomatch; control ` aax` (3,4).
- WD8 (new: the right context at `from`): `(?<=a{1,2}\b)x` on `aax` nomatch, `(?<=a{1,2}\b)-` on
  `aa-` (2,3), `(?<=a{1,2}$)` on `aa` (2,2). Plant: the part ignores the byte at `from`.
- W-restore (row 3's exhaustion restores the cursor): `(?<=(?>ab|a)b{1,2}|ab)x` on `abx` (2,3).
  Plant: no `VSK_RESTORE` before `L_b_(i+1)`.
- W-UTF (UTF-8 build): `(?<=é{1,2})x` on `aééx` (5,6), `(?<!é{1,2})x` nomatch,
  `(?<=(é{1,2}))x` g1 = (1,5).
- W-trail (cursor-rung spelling only): a row-3 branch with at least four failing candidates on a
  bounded-trail artifact sized at 3; a build that writes a trailed slot per candidate gives
  `PCREC_ERR_FRAMES`. The concrete cell is owed by the build (INFERRED).

**Per-part oracle (G3/F3).** The part's answer at (`from`, `bound`) is the smallest `s ≥ bound` such
that `B` matches anchored at `s` ending exactly at `from`, with the subject's bytes on both sides
as context. libpcre2 answers it without pcrec's VM (one anchored match per `s`, the end tested by a
callout or by comparing `ovector[1]`), so the part has an oracle of its own; the build writes it
(INFERRED: not built). The record-in / text-out golden check reads the record through a test-only
hook under `tests/`, no caller surface.

**One tagged machine instead of per-branch machines** stays a later rendering (rev 2 §5.4). **The
filter row** (rev 0's `gate`: the reverse DFA as a yes/no filter in front of range's own loop) is a
later option beside rows 2-3, HELD with no trigger of its own: it is rows 2-3 with the candidate
hand-off removed, which nothing needs.

### 3.2 Second: revdet's STEP (W4) `[r5 F10]`

- **The fit.** revdet's step is a deterministic reverse automaton step: `revdet.c`'s reverse check
  is the forward unique-iteration predicate on the reversed body; (U1) makes its Glushkov automaton
  deterministic and (U2) gives at most one accept per step. `vm_rev_emit` renders it one VM state
  per position: the `structural` rendering. Its hand is ACCEPT(the predecessor boundary, `groups`).
- **The loop is not the step.** The walk loop in `vm_revdet_rep` (re-seed from each landing, stop on
  "all groups seen" or the floor, keep the first step's landing for the greedy retreat) is one
  member of the loop-over-walk-results family (§5), RULED so by the manager (review r5, question 3).
  S2 moves the step; the loop moves with that family's step.
- **The step (S2).** `Rev`'s live fields become the record's structural operands (`from` = the
  cursor local, `bound` = the entry slot, the fail label in the hand map, the loop index as
  `instance`); `Rev.ga` and `Rev.ns` are deleted (dead); the group sinks are declared ONCE as an
  artifact-scope resource of the structural rendering. `vm_rev_emit` becomes the structural
  renderer, its text unchanged. `revdet.c` stays: it is the rendering row's admission.
- **Byte identity:** expected 0 movers.
- **Witnesses** (red under the plant in the base build AND the step's build, anchors re-aimed): S52
  (the first-seen guard: `((a)|b){0,4}c` on "abac"), S50 (no reverse check), S51 (no iteration
  cut), S94, S160.

### 3.3 Third: W1-W3 onto the record (S1), and the landmark walk's body as records (S4)

- **S1.** Every DFA walk (W1-W3 and the forward walks) renders from the record; `dfa_dir_landmark`,
  `dfa_dir_lmverify` and `pcrec_emit_dfa_retry`'s run-time copy fold into their direction's one
  object plus the instance's label stem; `dir_rev_bound_accept` and `dir_rev_skip` read `bound` and
  the position names from the record instead of printing `search_from` and `rewind_position`
  `[r5 F13]`; the two direct `emit_scan_loop` reverse sites (`emit_rev_end_one_seed`,
  `emit_rev_end_tagged`) take the record with their form's `from` (the compile-time seed state, the
  seed list) and `tag`; `revend_forms[]` stays the declared form choice and the record cites its
  row `[r5 F6]`; `lmwalk_reach` becomes a declared field of the landmark walk's host-loop state.
- **S4** (P-d): the landmark walk's search body as records: a FIND record (the LMHIT site), the
  reverse `AUTO COMMIT`, the anchored forward `AUTO` (verify), and the FINISH hands. The
  `pcrec_ctx_fail` asserts in `emit_landmark_walk` (the AT, LOWER, NOMATCH hands) become seam type
  checks.
- **Byte identity:** both 0 movers; S4 is P-d's falsifier.
- **Witnesses** (red in both builds): S1825 (`a+b` on "aab", (0,3) vs (1,3)), S1827 (reach guard
  removed), S74 (context below the floor; its anchor is `dir_rev_bound_accept`'s literal
  `search_from`, which S1 moves into the record: S74 IS RE-AIMED in S1 `[r5 F13]`), S759 / S760
  (rev-end seeds), and two floor cells (libpcre2 10.46, rev 0's lane): `a+b` on "aab" from offset 1
  is (1,3) (route `landmark-walk`) and `[ab]+[bc]` on "aab" from 1 is (1,3) (route `unanchored`);
  a bound one byte low gives (0,3). The floor cells are a proposed new row for S1, the sabotage
  site S1 moves from a string constant into an operand.

## 4. Steps `[r5 F23, F26, F28; OWNER ADDENDUM]`

### 4.1 The step list

| step | what | bytes | prerequisites (at fd1a32021) | gate | trigger | ratchet (§4.3) | cost (F28) |
|---|---|---|---|---|---|---|---|
| S0 | this note rev 1; the re-check round; the D-next entry | none | none | the critic re-check | now | recipes proposed | text + one critic round |
| S1 | the record (`DfaForm` made into it, form rows as plan outputs) for every DFA walk; the `DfaDir` copies and the two literal printers folded; S74 re-aimed (§3.3) | 0 movers | p1build MERGED | `emit_sweep.py` identity over the corpus, movers 0; `make test`; `make test-codegen`; S74, S1825, S1827, S759, S760 re-aimed and DETECTED; the two floor cells | ride-along: the first change that opens a DFA walk ([REVBLOCK-VIEW] likeliest; [LANDWALK-ALLACC], [LANDWALK-WINDOW], rev-inner (D151)), or the proof step's own build | R28' 5 → 0 | M: a corpus sweep (box lock, a heavy job), a full `make test` (~11 min), codegen, five sabotage re-aims; one CODE critic round |
| S1M | the machine table: every machine an entry (§2.4); the lowering a table fact (no swap); `dfa_member_machines` reads it; the lookbehind rung's append shape declared | 0 movers | S1 | as S1; `make test-axes` on the rung flags | rides the proof step (lands just before it); H-FLAGS's machine trigger | R14 (H-FLAGS) 1 → 0 if the hub's owner and shape are written with it | M: as S1, plus the axes sweep for the fit ladder |
| S2 | revdet's STEP onto the record (§3.2) | 0 movers | S1 | identity; `make test`; S50-S52, S94, S160 DETECTED | a change opening `vm_revdet_rep` (a revdet widening); also a ride-along [VMREC] (b)/(c) MAY carry (named in [VMREC]'s row as such) `[r5 F26]` | none falls: the step was never a ratchet member; R03' is the LOOP (§4.3) | S: identity sweep on the VM corpus, `make test`, five re-aims |
| **S3, the PROOF step** | the part placement + `VK_AUTO` (§2.3) + the lookbehind's rows 2 and 3 (§3.1) | moves only artifacts with a varying lookbehind branch (abi event) | vlookbehind stage 1 (`range`) SHIPPED; [VMREC]'s ANALYSIS stage (c) (D153 remodel-first, RULED: the step adding a VM record kind waits for it); S1, S1M; [GIVEUP-DIFF]; a D27 spec-first author's witnesses (the review's recommendation) | §3.1's gate: answers (`run_lookaround_diff.sh`, default and deny), bytes, the four regimes; F1-F3 judged by §0's checkable forms (diff classification, the golden check, the per-part oracle) | NONE: scheduled as a proof (Frank, 2026-11-06) once its prerequisites land | R28', R03', R10' do not rise (an instance and the kind's first host loop); R12, R11, R13, R19 do not rise (CT_* hands, existing `FitSets` spelling, [ROWCONJ]'s conjunct type for (a)-(e)); re-counted at its head | L: the D27 author, the build, `make test`, the lookaround differential in both builds, `test-axes`, a CODE critic round, a timing window for the four regimes (cleared with Frank, never 20:00-01:00) |
| S4 | the landmark walk's body as records (P-d) | 0 movers | P-b (not started; waits on P-c); [VMREC] (b) | P-d's: identity, one renderer body | P-b landed and a change opening the walk ([LANDWALK-VM], [LANDWALK-FWD], [LANDWALK-ALLACC]) | R10' 1 → 0 | M |
| S5 | the moving-seed host loop: W2's seed list, W3's hits and W4's walk as instances of the kind's one host loop, beside S3's moving-bound loop | 0 movers | S1, S2, S3 (the host loop's first instance) | identity; the walks' witnesses | the third member's next change, or [LANDWALK-WINDOW] | R03' 3 → 0 | M |

Rev 0's S5 (the `commit` row, HELD) is GONE: it is the proof step's row 3 `[OWNER ADDENDUM]`. Rev 0's
"S1 and S2 cost nothing on the box" was untrue `[r5 F28]`.

**Why the proof step needs no speed trigger.** Rev 0 §4.2 made it wait for "pcrec slower than
libpcre2 with the lookbehind as cause", a cell vlookbehind rev 2 §3 predicts will not show `[r5
F25]`. Frank ruled it a proof: what it shows is that a deterministic part can run inside a VM body
through a declared seam with facts both ways (F1, F4), that the part is target-text-free (F2) and
that it can be validated alone (F3). Speed is the gate, measured on the four regimes.

### 4.2 The measurement (the gate, not a trigger)

The four regimes of §3.1's gate, on the dev box (7700X, gcc 15.2), both VM entries (the tiered
default and `_search_in`), both kit layers, `pcrec-auto` with the row on against the row denied (the
reference), and against `libpcre2_10.46_interp` for the bench cell. The bench cell is
`negation-scope-lookbehind-var` (body `\bnot\s{1,3}(?:\w{1,12}\s{1,3}){0,3}`, widths 4..51; a
capture-free, negative branch: row 2 on `lang = same`).

### 4.3 Ratchet recipes (proposed; the manager restates roadmap §5) `[r5 F23]`

Rev 0's recipes counted NAMES (a rename zeroed each). Restated by what each member DOES, per the
review's manager action; counts read at fd1a32021 by this lane:

- **R28' "walk spellings outside the kind's one entry".** (i) `DfaDir` objects, `static const` or a
  run-time copy with fields overwritten, minus the number of directions (3: forward, reverse,
  anchored): five objects + `pcrec_emit_dfa_retry`'s copy − 3 = 3; plus (ii) walk renderings that
  call the shared body with a reverse form outside the kind's one entry (today
  `emit_reverse_block`; after S1 the record's renderer): `emit_rev_end_one_seed` and
  `emit_rev_end_tagged` = 2. **5 at fd1a32021.** `dfa_dir_lmverify` counts (the forward twin, which
  rev 0's `reverse == true` recipe could not see).
- **R03' "loops over a walk's result outside the kind's one host loop".** Functions whose own body
  emits a loop (a `for`, `while` or backward `goto`/`vm_goto`) that re-runs a reverse walk:
  `emit_rev_end`'s two-seed loop, `emit_landmark_walk`'s hit loop, `vm_revdet_rep`'s walk loop.
  **3 at fd1a32021** (no host loop exists yet, so each counts). Rev 0's R03 (`src/opt/revdet.c`
  present) could never fall, since that file is the rendering's admission, and its rev 0 restatement
  (`} Rev;` present) read 0 on a rename `[r5 F10, F23]`. The definition RAISES the baseline from 1
  to 3 by re-definition, not by a step: a found member is a row (roadmap §8 item 2), the manager's
  to record.
- **R10' "raw loop text in the landmark walk's emitter"** (P-d's criterion). The function registered
  as the `landmark-walk` LOCATE row's DFA emitter (`.u.locate.emit`, emit_dfa.c:10354), whatever its
  name: lines of its body that print C loop text (`for (`, `while (`, `goto `) present: 1, else 0.
  **1 at fd1a32021.**

The control shares a source with what it controls (this note wrote the recipes that credit its own
steps): the review's re-check and the manager's restatement are the independent reading.

## 5. Siblings and the general form

- **The general form** (the review's standing-question-2 answer, folded): a DIRECTION-NEUTRAL
  automaton-run record over H-FLAGS's one machine table, carrying `from`, `bound`, the hand map in
  `CT_*` terms, tags and placement, plus A-FACTS' three facts (language superset, start pin, report
  shift; `lang` is the first, `has_bot` the second's screen, `\K` the third's). Unlocks, each with
  its trigger: forward existence in a VM body ([LB-EXIST] / [ENG-LOOK]; trigger: a real pattern
  needing unbounded lookbehind); lookahead-as-check (D164 add. 2 client 8; trigger: that client's
  row opens); the anchored verify in a VM body ([LANDWALK-VM]; its own trigger); P-b's reverse
  AUTO; A-ISL's `AUTO ENUM` (P-g); the all-machines table (S1M; trigger: the proof step).
- **The lookbehind candidate-source family**: `range`, `reverse-dfa` (the proof step's rows),
  [ENG-LOOK]'s forward `Σ*·L` existence machine ([LB-EXIST], HELD), and vlookbehind_pieces' HELD
  **backward span count** (a fixed-stride class run counted backward from `cursor − |F_right|`):
  that last one is this kind's cheapest table-free rendering, a constant walk of the rendering
  axis below, filed under A-REV as its home.
- **LOCATE × FINISH (D156).** Every walk here is a LOCATE half handing a typed position to a FINISH
  row; the lookbehind is the same algebra inside a VM body.
- **Loops over walk results, three members, plus the proof step's** (W2's seed list, W3's LMHIT
  hits, W4's predecessor chain; the lookbehind's moving bound): the proof step builds the kind's
  FIRST host loop (moving bound), and S5 makes the three moving-seed members its instances. The
  seed stream needs two combine rules (MIN-with-tie for W2's two-seed form; CHOOSE-BY-LAST-BYTE for
  its one-seed form) and a compile-time seed STATE `[r5 F6]`. [LANDWALK-WINDOW] (`from` = the kit's
  window stream) is the next member and should be designed as one.
- **Moving floors, three members** (W1-W3's `search_from`, the lookbehind's bound, rev-inner's
  (D151)): the third member reaches §5's "unify at the third" threshold; `bound` as a typed reference
  IS that unification `[r5 F29]`.
- **Tag kinds, two members** (W2's distance sets, W4's groups): noted. A TDFA-style group tag on
  table machines would let W4 change rendering; HELD, trigger: a measurement showing a table walk
  faster than the structural one on revdet bodies.
- **Renderings** (table, structural, and [LANDWALK-FOLD]'s constant walks: `end-minus-width`,
  `offset-set`, the `pinned` rows, plus the backward span count): one axis, chosen by a declared
  row table whose output the record carries. D161 add. 17 argues for one general mechanism with
  cases folding under it; the prefix-shape tiers are admission for the scaffolding, not rendering
  rows `[r5 F18]`.
- **[LANDWALK-*].** ALLACC = `AUTO ENUM`; WINDOW = the seed stream; FWD = a forward `AUTO` replacing
  the verify; VM = the part placement of §2.3 in the VM search loop; FOLD = a constant rendering;
  CARD/CENSUS/EDGEPRICE ride the walk unchanged. Each is a ride-along trigger of S1.

## 6. The "VM base" lens (owner's open frame; NOT a rule)

- **Where it helps.** The proof step is exactly its shape: `range` is the reference, the reverse
  walk an optimization section that must be answer-identical to it, the row's deny build the
  reference matcher. It explains the two exits in one sentence: a section may remove work the
  reference would do (row 3 skips candidates), and may replace the reference's answer only where its
  language is the branch's own and nothing else is observable (row 2).
- **Where it is neutral.** W1-W3 live in artifacts with no VM; S1's byte identity is what the lens's
  condition (a) asks. `placement` and `container` keep VM-only facts (frames, charges) out of an
  inline walk.
- **Where it could hurt.** Designing the kind around the VM host would burden every pure-DFA walk;
  the part's declared effects (no frames, slots or trail) are the isolation.

## 7. The standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** RELEVANT ONLY TO S3: §4.2's four regimes, per-position cost of a
   lookbehind evaluation, hit and miss, throughput over subjects, dev box, both VM entries, both kit
   layers. Regime (c) (candidates that do not fail at the first byte) is the one most likely to flip
   the row, which is why it is required; a flip narrows the admission. S1, S1M, S2, S4 and S5 are
   byte-identical: no number decides them.
2. **Independent control.** RELEVANT. Answers: libpcre2 10.46, which shares no source with pcrec;
   every witness answer here was measured against it (premise.out). The per-part oracle (§3.1) is
   libpcre2 too. Bytes: the comparator's baseline is the previous commit's own output. The ratchet:
   its recipes are written here, before the steps, and re-read by the re-check and the manager (the
   control shares a source with what it credits). Population: the D27 author and gate 1's generator
   count their own cells (K35). Reach: a choice row's witness is unreachable in its deny build by
   design, so each cell names the plant that reaches it there (stage 1's), and `range` is checked
   by stage 1's witnesses.
3. **What moves when data is regenerated.** MOSTLY NOT RELEVANT: no table, calibration or measured
   set. Machines are generated per artifact from the pattern. S3's new emission is an abi event
   (readers by grep) and a `tuning.md` hunk (D80); a future price card for rows 2-3 would move
   selections, never answers.

## 8. Questions for Frank (plain words; leanings are not rulings) `[r5 F27]`

1. **Spell the lookbehind loop the cursor-rung way?** (vlookbehind_pieces' question 1, restated for
   the hand-off.) The candidate loop can keep the candidate in its retry frame (the cursor rung's
   way) or keep the cursor there and carry the candidate in a saved slot (rev 2's way). Same
   answers. For the hand-off, the cursor-rung way needs no slot and no extra saved entries; rev 2's
   way needs a new kind of saved slot that no existing family describes, plus a checkpoint on every
   such loop. Leaning: the cursor-rung way, ruled once for both `range` and the hand-off.
2. **Move every machine into one table before the hand-off, or only the lookbehind's?** One table
   for all of them is the hub's own end state and keeps one way of naming a machine; it is a medium,
   byte-identical step just before the hand-off. Only the lookbehind's would be smaller now and leave
   two ways side by side. Leaning: all of them, in its own step.
3. **The ratchet counts I restated go UP before anything is built** (the revdet row from 1 to 3, the
   direction-copies row to 5), because they now count what the code does rather than names. That is
   the manager's to record; you may want to know the totals rise on paper. No ruling needed unless
   you object.

## 9. What this note does not decide

- The C names (`AutoRun`, `VK_AUTO`, the part header) and field layout: the build lane's.
- Whether `dfa_form_derive` moves files when the form becomes a plan output (H-HEADER / A-PLAN).
- The early-stop exit, the filter row, one tagged machine for many branches, TDFA tags for W4,
  unbounded lookbehind: HELD.
- P-b's order relative to P-c (roadmap §6).
- Any change to the manifesto (none is needed) or to APPROACH.md.

## 10. Measured vs inferred

- MEASURED (this lane, libpcre2 10.46 as a library, rev 1's `probe.c`): every cell of §3.1 and the
  F1/F2/F3 cells (premise.out, cells.txt). Rev 0's floor cells (`a+b`, `[ab]+[bc]` from offset 1)
  are rev 0's measurements, not re-run.
- READ from code at fd1a32021 (re-grepped, not executed): §1, §2.3's placements, §2.5's two
  narrowings and `pcrec_nfa_has_bot`, the ratchet counts of §4.3.
- INFERRED: every byte-identity expectation (proved only by each step's comparator); the hand-off's
  soundness argument (by construction against `range`; the gate's differential is the check); the
  work and trail figures; the per-part oracle; W-trail's concrete cell.

## 11. Disposition table (review 2026-11-05 r5)

| id | disposition | where |
|---|---|---|
| F1 | FIX-NOW | §2.5, §3.1 (conjunct (c), WD-G) |
| F2 | FIX-NOW | §2.5 (tested before the build), §3.1 (WD-A) |
| F3 | FIX-NOW | §2.2 (`AUTO EXISTS`), §3.1 ("What yes and no mean", WD-B) |
| F4 | FIX-NOW | §2.4 (the request names collapse and prune), §2.5 (`lang`, not "exact") |
| F5 | FIX-NOW | header, §3.1 ("This is the client's own row", the floor, prerequisites, [LB-EXIST]) |
| F6 | FIX-NOW | §1, §2.1 (`from` per form), §3.3, §5 (combine rules) |
| F7 | FIX-NOW | §1, §2.4 (lowering a table fact, no swap) |
| F8 | DOC | §1, §2.1 (`tag`) |
| F9 | FIX-NOW | §1, §2.3, §3.1 ("Work and give-ups") |
| F10 | FIX-NOW | §1, §3.2, §4.3 (R03') |
| F11 | FIX-NOW | §2.2 (one behaviour; `first` dropped) |
| F12 | DOC | §1 |
| F13 | FIX-NOW | §1, §3.3 (S74 re-aimed in S1) |
| F14 | FIX-NOW | §2.1, §2.3 (back-flowing facts) |
| F15 | FIX-NOW | §2.1 (form as plan output) |
| F16 | FIX-NOW | §2.1 (one descriptor: `DfaForm` made into the record) |
| F17 | FIX-NOW | §2.2 (roadmap §4 suffixes the home, `CT_*` hands, row 12, one meaning of `from`) |
| F18 | FIX-NOW | §2.1 (`rendering`), §2.6, §5 |
| F19 | FIX-NOW | §2.3 (part + call record, signature, effects) |
| F20 | FIX-NOW | §2.1 (part header), §2.4 (one table, H-FLAGS's trigger), §4.1 S1M |
| F21 | FIX-NOW | §2.1 (`placement`/`container`), §2.3 (`VK_WORK`) |
| F22 | FIX-NOW | §2.4 (the rung), §4.1 |
| F23 | FIX-NOW | §4.3 (manager restates roadmap §5) |
| F24 | FIX-NOW | §0 |
| F25 | RULED (owner addendum) | §3.1, §4.1 |
| F26 | RULED (manager: waits for [VMREC] (c)) | §4.1 (S3 prerequisites, S2's ride-along note) |
| F27 | FIX-NOW | §8 |
| F28 | DOC | §4.1 (cost column) |
| F29 | FIX-NOW / DOC / NOTED | §3.1 (one choice row, exits by fact); D142's UTF class in §3.1's gate; §5 (third moving floor) |
| vlbrev2 pickups 1-10 | applied | 1 §2.3, §3.1 (trail); 2 §3.1 (no slot, or a new one under rev 2); 3 §3.1 (K134); 4 §2.3; 5 §3.1 (the end-check is range's); 6 §3.1 reader table; 7 §3.1 composition; 8 §3.1 reader table; 9 §3.1 gate; 10 moot: Frank ruled (A), today's bytes stay |
