# A-REV: one automaton-run record, one walk behaviour, hostable in a VM body

**Status: PROPOSED rev 2** (lane arevrev2, opus, 2026-11-06; plan row [STREAM], roadmap area
A-REV). Rev 0 was lane arevdesign's (2026-11-05), rev 1 lane arevrev1's (applying review
`docs/dev/reviews/2026-11-05-r5-arev.md` and its OWNER ADDENDUM). Rev 2 applies the RULED re-check
`docs/dev/reviews/2026-11-06-r1-arev-recheck.md` (every disposition ACCEPTED, four manager rulings
of 2026-11-06). Design only: no build go, no step built. Anchors are at **main 6e01c810b**; no code
moved since rev 1's fd1a32021 (the review's three critics checked the empty `git diff --stat` up to
e20dee230, and nothing under src/ has landed since). Anchors move with code: re-grep the symbol.
The manifesto is not edited by this note; `roadmap.md`'s A-REV section is the area plan and points
here. Client documents in force: `docs/design/vlookbehind.md` **rev 3** (the cursor-rung loop) and
`docs/design/vlookbehind_pieces.md` **rev 0** `[r5 F5]` `[r1-1106 D6]`.

## REVISION 2 (re-check 2026-11-06 r1) — read first

Corrections are marked inline as `[r1-1106 <id>]` (the review's consolidated ids A1-A3, D1-D6,
R1-R8, N1-N7). Rev 1's refuted text is recorded where it stood. Evidence:
`docs/dev/lanes/arevrev2_evidence/` (the probe, its outputs, the sweep model with A1's rule). In
summary:

- **A1, answer level.** On the non-atomic form `(?<*`, the existence row now pushes the next
  branch's frame before it reports success, exactly as the `one-length` row does; without it a later
  capturing branch was never tried (`(?<*a{1,2}|(a))b\1` on `aaba` is [2-4,1-2] in libpcre2). The
  review's 552,900-cell sweep, re-run through this rule: **0 differences** (§3.1).
- **A2, answer level.** A new first conjunct (c0) bounds the branch's NFA size on the AST before any
  NFA is built, so the NFA-state cap can never refuse a compile that `range` alone accepts
  (`(?<=\p{L}{1,255})b` under UTF-8; D158). No build on the admission path is mandatory (§2.5).
- **A3.** The part's read set is clipped at both edges and includes `subject_length`; `from`
  selects the machine's base, end-of-line or end view by position; WD8 (now `HO-8`) gains the cells that
  separate the byte at `from` from its position (§2.3, §2.5).
- **Ownership (ruling 1).** `vlookbehind.md` owns lookbehind's admission rows, the `reverse-dfa`
  candidate source included; this note owns the automaton kind, its exits, the record and the host.
  §3.1's rows are now a LIST OF PROPOSALS for vlookbehind's revision when the proof step is designed
  for build, with their own witness ids (`HO-*`), so they no longer clash with vlookbehind's WD ids
  `[r1-1106 D1]`.
- **The host as members, not a kind (ruling 2).** The in-body call is spelled with new MEMBERS of
  existing closed lists (a local, a seek form, a piece) and the code-segment declaration slot is the
  part's slot. Only the part's declared EFFECT SET waits for [VMREC] stage (c), shared with kit
  windows and code segments (§2.3) `[r1-1106 D5]`.
- **[ROWCONJ] first (ruling 3)** and **a `--harness=` lever (ruling 4)**: both in S3's
  prerequisites and gate (§4.1) `[r1-1106 R2, R3]`.
- **The record closed (D2), S1M's swap as a role (D3), stems per instance (D4)**, rev 3's eleven
  pick-ups applied (D6), the oracle per `lang` (R1), unit ownership of the round trip and oracle
  (R4), stage 1's witnesses pinned to the deny build (R5), the recorded per-branch row (R6), the
  rung's readers (R7), ratchet recipe words (R8), and the doc items N1-N7.
- **§12** maps every id of the re-check to its section.

## REVISION 1 (review 2026-11-05 r5)

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
build, every construct that NARROWS a reverse machine is declined before it (§2.5), no build on the
admission path can refuse the compile (§2.5's (c0)), and on the non-atomic form the existence row
keeps the frame that reaches the later branches (§3.1); the STOP RULE does not fire (§3.1)
`[r1-1106 A1, A2]`. The rows themselves are vlookbehind's to adopt (ruling 1, §3.1).

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
   `floor`, `dead` and `names` were C text, which is the manifesto's F2 falsifier `[r5 F14]`). The
   grep is a cell of S1's and S3's gates `[r1-1106 R4]`.
3. **G3 = F3 Division of labour (the manager dividing lanes).** The walk part can be validated
   alone. Checkable: a record-in / text-out golden check for the part renderer, and an oracle for
   the part's answer that runs without the VM, stated per `lang` (§3.1 "Per-part oracle"): on
   `lang = same` the part's answer EQUALS the smallest `s ≥ bound` at which libpcre2 has a match of
   `B` from `s` ending at `from` (any end, found by forcing backtracking, not only the priority
   end); on `lang = superset` the true starts are a SUBSET of the part's accepts `[r1-1106 R1]`.
   Neither exists today: every witness is an end-to-end matcher cell. S1 owns the record's text
   writer and reader; S3 owns the golden-check hook and the part oracle (§4.1) `[r1-1106 R4]`.
4. **F4 constraint, no blindness.** The language fact that admits a row, the hand a walk returns
   and the facts that flow back (the tag encoding and tie bit, the empty-at-n probe, the landmark
   walk's reach) are declared fields, not conventions (§2.1, §2.2). Checkable by the seam
   round trip (manifesto principle 9): the record written as text and read back renders the same
   bytes; the round trip is a cell of S1's and S3's gates `[r1-1106 R4]`. A caller-visible listing of the record (rev 0's "every instance prints its operands in
   `--emit-ir` / the trace") is NOT claimed: `--emit-ir` and `--trace` are VM-only, so it would be
   an interface change (D80) and waits for [IFACE-PUSH] `[r5 F24]`.

**Non-goals.** A reverse VM (owner, 2026-11-05). Tagged-capture DFA tables (TDFA) for revdet's
groups (§5). Unbounded lookbehind ([LB-EXIST], HELD). A speed CASE for any step: speed is the gate
(manifesto). Choosing between the open "VM base" frame and today's two-engine reading (§6 uses it
as a lens only).

## 1. Today, at main fd1a32021 `[r5 F6-F13: restated]` (unchanged at 6e01c810b)

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
  `bind`, `tbl_hdr` and `acc_meaning` `[r5 F12]`. `[r1-1106 D2]` The floor is spelled in FIVE
  strings, not two: besides the two printers, each reverse object's `seed_cond`
  (`match_end_position < subject_length`), `at_bound` (`rewind_position <= search_from`) and
  `scan_more` (`rewind_position > search_from`). And `dfa_dir_lmverify` differs from
  `dfa_dir_anchored` in `ind`, `bind`, `range_guard` (NULL vs a guard), `dead_entry` (`break;` vs
  `return -1;`) and `tbl_hdr`; the retry copy overwrites `tbl_hdr` and `acc_meaning`.
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
then a pure function of the record (roadmap §0a) `[r5 F15]`, EXCEPT for the two kit replies named
below, which keep rendering impure until the kit seam returns them at plan time `[r1-1106 D2]`.

| field | type (no C text) | W1 | W2 | W3 | W4 | L (lookbehind branch) |
|---|---|---|---|---|---|---|
| `machine` | id of a machine-table entry (§2.4); the entry owns direction, tables and accessors | R | R (the lowered set after the swap is R; §2.4) | ML | the reversed body (structural entry) | one per varying branch |
| `rendering` | a row name of the rendering table: `table` or `structural` (renamed from rev 0's `repr`, which collided with `DfaForm.repr`, the layout axis) `[r5 F18]` | table | table | table | structural | table |
| `form` | the selected row names (`dfa_reprs`, `dfa_views`, `dfa_seeds`, `dfa_accs`), skip and scan-edge state lists, folds, entry facts | derived | derived per `revend_forms[]` row | derived | — | derived |
| `from` | a position REFERENCE: `FWD_ACCEPT`, `SUBJECT_END`, `HIT(stream)`, `SLOT(n)`, `CURSOR`, or a compile-time seed STATE id; for the forward walks S1 also moves, `SEARCH_FROM`, `REQ_HANDOFF` (the position the req-byte pre-check hands on, today the C name `pcrec_emit_req_byte_check` returns after printing) and `LMWALK_START` `[r1-1106 D2]` | `FWD_ACCEPT` | per form: a seed list {`SUBJECT_END`, `SUBJECT_END − 1` if the last byte is `\n`} combined MIN-with-tie, or STATE chosen by the last byte | `HIT(lmhit) + 1` | the cursor local | `SLOT(POS)` (the lookbehind's cursor); the reference also selects the machine's base, end-of-line or end view by POSITION (§2.5) `[r1-1106 A3]` |
| `bound` | a position REFERENCE: `SEARCH_FROM`, `ZERO`, `SLOT(n)`, `CANDIDATE + 1` | `SEARCH_FROM` | `SEARCH_FROM` | `SEARCH_FROM` | `SLOT(entry)` | `ZERO`, then `CANDIDATE + 1` |
| `hands` | a map from the walk's three outcomes {`DEAD_ENTRY`, `NO_ACCEPT`, `ACCEPT(pos[, tag])`} to host hands (§2.2) | NO_ACCEPT → `return 0;`'s hand (rev 0 wrote NULL: wrong `[r5 F14]`), ACCEPT → SPAN | per form | DEAD/NO → next hit; ACCEPT → verify or LOWER | → the fail label / the step's landing | §3.1 |
| `tag` | `none`, or `distance` = a ≤ 7-bit set, end = lowest set bit, tie = popcount > 1; the forward and anchored walks of the tagged form carry `distance` too (today `forward_dist`, `anchored_dist`) `[r1-1106 D2]` | none `[r5 F8]` | tagged form: `distance` | none | `groups` (writes the artifact-scope sinks) | none |
| `instance` | an id, DISTINCT per walk within one host function; a declared instance → stem row gives today's stems `[r1-1106 D4]` | `reverse` | `revend` (and, on its relocate arm, a second walk: W1's `reverse` in the same function) | `landmark` | the loop's index | (site, branch) |
| `placement` | `inline` or `part` (§2.3) | inline | inline | inline | inline (records) | part |
| `container` | `search function` or `VM body` `[r5 F21]` | search fn | search fn | search fn | VM body | VM body |

**What left the record** `[r5 F14, F21]`: rev 0's `seed`/`floor`/`dead`/`names` as C strings, its
`exit` (one behaviour, §2.2), its `charge` (a `VK_WORK` record beside the call where one is owed,
§3.1), and the `rv<i>` group sinks (an artifact-scope resource of the structural rendering,
declared once, shared by every structural walk) `[r5 F10]`.

**Two stems, two owners** `[r5 F14]`. Table and accessor names belong to the machine-table ENTRY
and are emitted once per (machine, direction): today `emit_rev_end`'s relocate arm walks one set of
tables twice (`DfaForm rel = *rev;`). Label stems belong to the walk `instance`.

`[r1-1106 D4]` Rev 1 gave W1 and W2 the same (machine R, instance 0) and derived stems from
(entry, instance). That yields ONE stem, but `emit_rev_end` renders two walks over R in one
function: the two-seed walk with stem `revend` (`emit_reverse_block(c, &rev, "revend", …)`), then,
on its relocate arm, RECOVER's pass through `unanch_scan` with stem `reverse`; the tagged form does
the same. One stem would print duplicate C labels (a gcc error) or move one walk's labels (bytes
move against S1's 0 movers). So an instance is distinct per walk within one host function, and the
stem is read from a declared row, instance → stem, whose rows reproduce today's `revend`,
`reverse` and `landmark` (and the forward walks' stems).

**Fields rev 1 did not state** `[r1-1106 D2]`. `DfaForm` (emit_dfa.c:5861) and `DfaDir` (:5787)
carry more than §2.1's table, and the seam round trip is reachable only once each has a named
field and an owner:

| today's field or override | in the record as | owner |
|---|---|---|
| `cx`, `p` (artifact prefix) | not fields: the renderer's context | the renderer |
| the host function name (`pf_stem = "%s_pf"` of it, :13690, :14280, :14449) | `host`: the host function's id | the walk |
| `ind`, `bind` (indent) | the CONTAINER's nesting depth, not a direction fact | the container |
| `us` (UnanchStart, borrowed by pointer through render), `views`/`viewsel`/`src`, the start-analysis override `rus.eol = rus.endv = rus.viewsel = rus.views = false` (:14265) | the start-analysis facts as a RECORDED plan output (the form's input, frozen with it) | the plan |
| `pf` (NEXT row, chosen only where `d == &cx->job->dfa`), `cand`, `ofs` | form rows (already `form`); the identity test becomes a ROLE test (§2.4) | the plan |
| `pf_find` (written at render, `f->pf_find = find_define(…)` :7178) and `ofs_site` (`ofs_site_define`, :7650), each read later by the table emitters | a declared BACK-FLOWING field: the kit's define reply (F4). Until the kit seam returns it at plan time these two keep render impure; the record names them so the impurity is visible, not hidden (D157: the reply is facts, never the kit's method) | the kit seam |
| `tbl_hdr`, `acc_meaning` (comment prose) | the machine-table ENTRY's prose | the entry |
| `range_guard`, `dead_entry` | hands in the hand set (`DEAD_ENTRY`'s host hand; the guard as the walk's entry check) | the walk |
| `landing`, `accv` | `tag` (above) and the hand map | the walk |
| `fwd.from = pcrec_emit_req_byte_check(…)` (:13723), `av.from = "lmwalk_start"` (:14439) | `from` references `REQ_HANDOFF`, `LMWALK_START` (above); the pre-check is its own preceding record | the walk |

The floor is in the five strings §1 names; S1 moves all five into the record's `bound` (and
`from`), not only the two printers `[r1-1106 D2]`.

**The seam round trip.** Written as text, the record is: an entry id, row names, two position
references, a hand map, a tag kind, an instance id, two placement words, and (rev 2) the host id,
the container depth, the recorded start-analysis facts and the kit's back-flowing replies
`[r1-1106 D2]`. S1 owns the text writer and reader and the round trip (§4.1). Every field is either a
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
level (src/gen/emit_comb.c:576, :580), not from the body `[r5 F19]`. Rev 1, as corrected by rev 2:

- **The walk is a PART.** A file-scope function with its own stem. Its declared signature:
  `ptrdiff_t <part>(subject, subject_length, from, bound)`, returning the accept nearest `bound`
  or −1 for NO_ACCEPT (DEAD_ENTRY is folded into −1: the call has no other caller-visible
  outcome). Its declared EFFECTS `[r1-1106 A3]`: reads `subject[max(bound, 1) − 1 ..
  min(from + 1, n) − 1]` (the context byte below the bound only when `bound > 0`, S74's rule, the
  absent context otherwise; the walked bytes; the byte AT `from` only when `from < n`, the right
  context) and `subject_length` (`from` is compared with it to select the view, §2.5); writes
  nothing but its result; transfers no control; never touches frames, slots or the trail. Rev 1's
  `subject[bound − 1 .. from]` named `subject[-1]` at `bound = 0` and `subject[n]` at `from = n`,
  reads today's code GUARDS rather than makes (`dir_rev_bound_accept`'s `search_from ? … : …`, the
  reverse `seed_cond`), and omitted the length.
- **The part's SLOT is the code-segment declaration slot** `[r1-1106 D5(b)]`. Rev 1 put the part
  "in its own slot BEFORE the matcher function, the way the combinator emits the hybrid's DFA
  part". The closer precedent is called FROM the body: [INLINE-C]'s code segments, whose prototype
  and binding `pcrec_emit_code_protos` (emit_code.c:142) prints "before the function whose call
  sites name them" (emit_vm.c:14187), with the definitions in the segment block at the end of the
  `.c`, and the site calling `<binding>.fn(&ctx)` ("gcc sees the definition, so the call is direct
  and inlinable"). The part uses that slot, widened from "code segments" to "units called from the
  body" (a member list), not a new stream-level slot. Artifacts with no called unit print nothing
  there today and still print nothing.
- **The call is MEMBERS of existing closed lists, not a new kind** `[r1-1106 D5(a); manager ruling
  2, 2026-11-06]`. The call has no control of its own (vm_stmt.h:7-11: the only free text is a
  VALUE fragment), so it composes from existing kinds:

  | statement | kind | new member |
  |---|---|---|
  | `t = <part>(subject, subject_length, from, bound)` | `VK_LSET` `VLO_ASSIGN` | a `VmLocalKind` member for the result local (untrailed, as rev 3's `VL_LB_COUNT`); the call itself a `VmPieceKind` member `VP_AUTO` beside `VP_KIT`, printing the part's name and the operands as VALUES (`(size_t)slot_values[<n>]`, never the index: vlookbehind rev 3 §5.6's rule) |
  | `if (t < 0) goto …` | `VK_BRANCH` | none |
  | `scan_position = t` | `VK_SEEK` | a `VmSeekKind` member, cursor ← local (today's five are slot-restore, advance, back-step, span commit, and [VLOOKBEHIND]'s one-character step); so the cursor write stays `VK_SEEK`'s, which rev 1's `VK_AUTO` writing `scan_position` would have overlapped |
  | row 3's charge, one per non-empty candidate | `VK_WORK` | a typed operand member (1 iff the cursor is below a slot) in place of the C text `scan_position < POS`, which (c) would otherwise have to analyse as free text `[r1-1106 N5]` |

  Under the members ruling none of these waits for [VMREC]. Rev 1's `VK_AUTO` was a new KIND, and
  r5's ruling ("the step adding a VM record kind waits for the remodel's analysis stage") bound S3
  to it; with no new kind, that ruling has no object here. `VK_AUTO` survives only as the name of
  this four-record composition in the text.
- **What genuinely waits for [VMREC] stage (c): the part's DECLARED EFFECT SET, and only that**
  `[r1-1106 D5; manager ruling 2]`. vm_stmt.h:24-26 reserves read sets for stage (c) ("Records carry
  no verdicts, no read sets and no statement ids; stage (c) adds those"). The effect set above (the
  bytes and the length it reads, nothing written but the result) is such a read set. It is ONE
  declaration shape shared by the three members of "an in-body call to a separately emitted unit":
  kit windows (`VP_KIT`, opaque with declared effects, [VMREC] (c)'s r9 rule), code segments and
  callouts (`VK_CALLOUT`, vm_stmt.c:710), and the part (`VP_AUTO`). This is the third member, so
  the family unifies at (c): one effect-set declaration for the three, not a field of a part-only
  record. S3 does not wait for it: the call ships as members, exactly as `VP_KIT` shipped before
  its effect set; (c)'s scope gains `VP_AUTO` (and `VK_CALLOUT`) beside `VP_KIT`.
- **The work charge is not a field** `[r5 F21, F9]`. Where a charge is owed it is a `VK_WORK`
  record beside the call (vlookbehind rev 3 §5.6's spelling, unchanged from rev 2) `[r1-1106 D6:
  pickup 7]`. There is no precedent for a per-walk run-time charge (revdet's walk has none), so
  §3.1 argues the lookbehind's from scratch.

gcc inlines a one-caller `static` function, so no speed claim rests on the call; placement is a
fact of the host (a VM body cannot hold a table walk inline without a new tiling rule), not a
priced choice.

**The finisher contract.** The kind hands a typed position; the finisher is the host's, chosen by a
FINISH row (D156), never by the kind: report (W1), `verify-at` with the anchored machine (W3, W2 on
a tie), `search-from` relocate (W2, W3), the VM body continuing (W4), and the new one: a forward
body run from the candidate with its end required at the cursor (L). `[r1-1106 D6: pickup 3]` The
finisher's operand is a POSITION carried by the retry frame (`L_try_i`'s push), not a count, and
row 3 SHARES vlookbehind rev 3 §5.1's `L_try_i`, `L_body_i` and `L_end_i` (not only their shape),
once its charge sits before the jumps into `L_try_i` (§3.1). That last finisher is the "VM forward run for captures" of the owner's example. A
fact that flows BACK from a finisher to the next walk is a declared field of the host loop's state,
never a convention: today the landmark walk's `lmwalk_reach` (the verify's farthest read byte) is
such a fact, and S1 declares it `[r5 F14]`.

### 2.4 The machine per site `[r5 F4, F7, F20, F22]`

**One table for every machine, H-FLAGS's shape.** H-FLAGS already declares the owner of machine
building ("one builder") and its interim shape ("a new machine is requested by a row and built by
the one builder"). A table holding only the optional reverse machines would leave the forward and
mandatory ones as `Job` fields, two identity mechanisms that W3 alone reads both of `[r5 F20]`. So:
the lookbehind's per-branch need is argued here as H-FLAGS's TRIGGER (its machine half), and the
step that builds the table (S1M, §4) moves EVERY walked machine (`dfa`, `rdfa`, `adfa`, the lowered
set, `lmdfa`, `nedfa` `[r1-1106 D3]`, and later the lookbehind's) into one per-artifact table, with
`dfa_member_machines` and every other reader reading it through roles (below).

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
- **"Adds, never swaps" holds only through a ROLE** `[r1-1106 D3]`. `revend_choose_form`
  (compile.c:568-592) swaps FIVE pairs by value, NFAs included (`nfa`/`xnfa`, `rnfa`/`xrnfa`,
  `dfa`/`xdfa`, `rdfa`/`xrdfa`, and `adfa`/`xadfa` under `anchored_ok`), and readers depend on what
  sits in the plain slot: two ADDRESS tests, `if (d == &cx->job->dfa)` (emit_dfa.c:12996, the NEXT
  prefilter row versus the fallback) and `.forward = d == &cx->job->dfa` (:9179), and two memos keyed
  on the slots' contents (`lm_key_holds`, lmwalk.c:318-324; `cover_key_holds`, known.c:395-399). A
  lowered machine held as a separate entry fails both address tests on every tagged artifact (the
  NEXT row is lost, bytes move) and the memos key on the wrong machine. So S1M re-expresses the swap,
  it does not remove it: "the live forward / reverse / anchored machine" is a ROLE of the table,
  resolved once from the lowering fact, and EVERY reader goes through the role. The two address
  tests become role tests; the two memos re-key on the role's entry. The reader set is a grep
  recipe, not a list: `grep -rP 'job->(nfa|dfa|rdfa|rnfa|adfa|lmdfa|lmnfa|xnfa|xdfa|xrdfa|xrnfa|xadfa|nedfa|xprio)\b' src`
  (160 sites at 6e01c810b: `dfa` 45, `nfa` 25, `adfa` 24, `rdfa` 19, `xnfa` 11, `nedfa` 9, `lmdfa`
  8, `xrdfa` 7, `xprio` 7, `lmnfa` 6, `xrnfa` 6, `rnfa` 5, `xdfa` 4, `xadfa` 4).
- **Two machines rev 1 missed** `[r1-1106 D3]`. `Job.nedfa`, the MANDATORY [FINDALL-NEXT] retry
  machine (built compile.c:438-446, walked by `pcrec_emit_dfa_retry`, whose run-time `DfaDir` copy
  S1 folds): IN, an entry with the role "find-all retry". `Job.xprio`, `mark_prio`'s probe
  (compile.c:514-526): OUT. It is built only to read `prio_seen` and is never walked or emitted; its
  one output is a FACT of the lowered entry (recorded there), and the probe stays a driver-local
  build.
- **Tables are the entry's**, emitted once per (machine, direction) (§2.1).
- **Size.** Each optional machine has its own build cap (an overflow is the row's DECLINE).
  `[r1-1106 N1]` The shape is the CALLERS', not `revend_build_one`'s: that function saves and
  restores only `dfa_overflowed`/`dfa_overflow_why`, while the subset budget is saved and restored
  by its callers (`lmwalk_build`'s `subset_before`, `revend_build_marked`'s). A lookbehind build that
  copied `revend_build_one` alone would charge every per-branch build to K7's per-compile budget
  (dfa.c:1316-1321, a comment itself stale against those two callers), and a MANDATORY machine built
  after it (the VM hybrid's prefilter DFA) could then refuse a pattern that compiles today. So the
  lookbehind's machines are built AFTER the mandatory ones, with `lmwalk_build`'s caller-side
  restore. The lookbehind's machines also get a size-cap RUNG in `fit_rungs[]`, in H-LADDER's
  declared append shape, as every shipped optional reverse machine has (`drop-end-mark`,
  `drop-landmark-walk`): without one, an artifact that `range` alone would fit under the emitted-size
  caps is refused because of an optimization (D158) `[r5 F22]`. The rung's drop flag uses the
  existing `FitSets` + `*_dropped` spelling, so R11 does not rise; H-LADDER's R13 counts the hub,
  not its rows.
- **The rung, completed** `[r1-1106 R7]`. One `fit_fired` bit makes it all-or-nothing per artifact:
  when it fires, every lookbehind branch of the artifact falls to `range` (acceptable: `range` is
  total, and the answers are the same). It is built in ONE unit, S3 (the machines exist only there;
  S1M declares nothing for it). Its readers outside H-LADDER's own shape (`fit_rungs[]`, `FitAct`,
  `fit_seq_legal[]`, `COMPILE_MAX_ATTEMPTS`, the driver case, the note), each owed a hunk or a row
  in S3: `docs/spec/limits.md` §8.4's rung table (its last column names each rung's public flag;
  this rung's entry is "none: the test-only `--harness=` arm", ruling 4); `docs/spec/tuning.md`'s
  two rung-order sentences (§2.15¶4, §2.54¶5); `tests/codegen/run_fallback_table.sh` (its
  `fseq`/`frec` rows under the `trlowsize` build); `tests/mech/sabotages/S238_size_drop_unstamped.sh`
  (it enumerates the rungs that stamp `size-cap-retry`) plus a twin of
  `S1826_lmwalk_rung_unattributed.sh`; `src/dump/axes_dump.c` (it lists `fit_rungs`). Its witness:
  a `trlowsize` cell where the lookbehind's tables push the artifact over the cap and the rung
  drops them to `range` (answer = libpcre2's; plant: the rung removed, giving a size refusal). The
  concrete pattern is the build's (INFERRED: a wide UTF-8 class body is the likely shape).

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
as F-13). A lane reading rev 0's "exact" in the stamp's sense would have admitted WD1's machine (now `HO-1`)
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
the order is the fix for F2, not only the conjunct, and no NFA or DFA build on the admission path is
mandatory (below) `[r1-1106 A2]`. `\K` would be a third (a report shift), but it is refused inside
every lookaround by both libraries (err 199).

**The right context at `from`: position, then byte** `[r1-1106 A3]`. `(?m)$`, `$`, `\Z`, `\z` and
`\b` at the cursor are RIGHT-context rows (nfa.c's header to `pcrec_nfa_has_bot`: "`(?m)$` does NOT
join"), and they hold or fail at the walk's START, `from`. Rev 1 said they are "read from the byte
at `from`". That decides only two of the five:
- `(?m)$` holds iff `from == n` or `subject[from] == '\n'`; `\b` reads the word class of
  `subject[from]` (absent at `from == n`). These are byte-keyed.
- `$` and `\Z` hold iff `from == n`, or `from == n − 1` and `subject[from] == '\n'`; `\z` holds iff
  `from == n` and reads no byte. These are POSITION-keyed: they need `from` compared with
  `subject_length`.

The DFA already realizes this choice twice: the forward machine's base, end-of-line and end
position views (dfa.c:1430-1432) with the emitter's view selection, and, for a REVERSE machine,
`rev-end`'s seeds (the two-seed form's seed list {n, n − 1 before a final newline}; the one-seed
form's start state chosen by the last byte), which is where a right-context row at a reverse walk's
start is decided. So the record states the rule, as the part's START STATE choice: the `from` reference selects the
view by POSITION (end at `from == n`; end-of-line at `from == n − 1` with a final newline; base
otherwise), and the base view then reads the byte. This is why §2.3's read set includes
`subject_length`. Cells (libpcre2 10.46, `arevrev2_evidence/premise.out`): `(?<=a{1,2}$)\nb` on
`aa\nb` nomatch (a byte-only reading says `$` holds at 2: [2-4]); `(?<=a{1,2}\z)\n` on `aa\n`
nomatch; controls `(?<=a{1,2}$)\n` and `(?<=a{1,2}\Z)\n` on `aa\n` [2-3], and the byte-keyed
`(?<=(?m)a{1,2}$)\nb` on `aa\nb` [2-4]. They join WD8 (§3.1, `HO-8`). An end-assertion cell on an
ILL-FORMED UTF-8 subject end meets K74 ([UTF-END-ASSERT], filed 2026-11-06: `$`, `\Z`, `\z`,
`(?m)$` and `\B` at an ill-formed end diverge from libpcre2 today, whatever the row), so the gate
states K74 as a named class beside D142's for such cells.

**No build on the admission path can refuse: conjunct (c0)** `[r1-1106 A2]`. Conjunct (c) needs the
branch's reverse NFA BUILT, and `pcrec_build_nfa` has no optional mode: its state allocator `nst`
(src/ir/nfa.c:146-156) calls `pcrec_ctx_fail` at the per-compile NFA-state cap
(`PCREC_MAX_NFA_STATES`, 131072, raise-only through `--max-nfa-states`), which longjmps to the
compile's one `setjmp`: a refusal. Only the DFA builder has `d->optional`. Today's whole-pattern NFA
erases a lookbehind body to one row (nfa.c:759), so no NFA ever sized a body until this row. Cell:
`\p{L}{255}b` under `-e utf8` refuses today ("NFA exceeds 131072 states", at 6e01c810b, premise.out)
while `(?<=\p{L}{255})b` compiles, and libpcre2 accepts the varying `(?<=\p{L}{1,255})b` (255 is its
variable-lookbehind ceiling; `{1,256}` is err 200). Once `range` ships, a row that built that
branch's NFA would turn the pattern into a refusal: an optimization-added refusal (D158), which the
gate's "no answer moves" forbids, and which no retry rung catches (`dfa_overflowed` is not set on
this path).

So the admission gains a conjunct BEFORE (c), on the AST, before any NFA is built:
- **(c0): the branch's NFA-state BOUND is within the effective cap.** The bound is an upper bound on
  the states `pcrec_build_nfa` would allocate for the branch, computed structurally from the branch
  AST with the builder's own per-arm costs: a class node counted by the SAME UTF-8 range splitter the
  builder calls (the one arm that expands: under `-e utf8` one `\p{L}` character costs between 3,543 and 3,641 states, so `\p{L}{k}b` passes the cap at k = 36 and fails it at k = 37, premise.out), a
  counted repeat as `hi` copies of its body plus the builder's per-copy states, alternation and
  concatenation as sums, an erased lookaround as its one row. Above the cap (the same effective cap
  `nst` reads, the caller's raise included) the branch DECLINES to `range`. A bound that over-counts
  declines more bodies, never a wrong answer (`range` is total).
- **Its control** is the builder's real count: the build lane adds a check that on every branch
  (c0) admits, the built reverse NFA's `n` is at most the bound (a codegen-section assertion over the
  lookbehind corpus, the population counted, K35). A bound that ever under-counts is then a red
  check, not a refusal in the field. The build lane may instead realize the bound as a counting
  pass OF the builder (one source of the per-arm costs) if the builder's arms allow it; the
  conjunct and its control are the same either way.
- **Why not an optional NFA build or a retry rung** (the review's other two options). An optional
  mode needs a failure return threaded through every recursive arm of the builder (its cap's only
  exit today is the longjmp), or a second `setjmp`, which the compiler avoids by design
  (select_engine.c: "exactly one `setjmp` … feeding the result back means running the pass again
  with one more input bit"). A retry rung on the NFA cap costs a whole extra attempt and needs an
  arrival label telling this branch's cap from the pattern's own. The bound is cheaper than both
  and leaves the builder unchanged.
- **The DFA half** stays (d): the per-branch DFA is built `optional`, so its cap overflow is
  recorded and declines, with the caller-side subset restore of §2.4. The rung of §2.4 covers the
  emitted-size caps. With (c0), (d) and the rung, every cap on the row's path declines.

Witness `HO-N` (§3.1): `(?<=\p{L}{1,255})b` under `-e utf8` compiles and matches as `range` does;
plant: (c0) dropped (the compile refuses with the NFA-state diagnostic). The `HO-N` id and its
twin at a raised cap are the build's to pin.

### 2.6 The generalizations, against vlookbehind §4's checklist (rev 2's, unchanged in rev 3) `[r1-1106 D6]`

| vlookbehind item | where it lands here | status |
|---|---|---|
| G1 machine per site | §2.4, one table for every machine (H-FLAGS's machine half) | proposed (S1M) |
| G2 floor and seed as operands | §2.1 `from`, `bound` as typed references | proposed (S1) |
| G3 names per instance | §2.1: label stems per `instance`, table stems per entry | proposed (S1) |
| G4 the exits | §2.2: one behaviour, the exits as hands and host loops | proposed |
| G5 hosting in a VM body | §2.3: a part in the code-segment slot, the call as four members (rev 1's `VK_AUTO` kind withdrawn `[r1-1106 D5]`) | proposed (S3) |
| G6 the finisher on the VM route | §2.3's finisher contract; built by vlookbehind stage 1 | proposed |
| (new) the build request and `lang` | §2.4, §2.5 | proposed |
| (new) rendering | `table` / `structural`, a declared row table's OUTPUT, recorded as a selection; D161 add. 17's prefix-shape tiers are NOT rendering rows (they fold under the scaffolding) `[r5 F18]` | proposed |
| (new) tags | `distance` and `groups`: two tag kinds of one hand, noted, not unified (two members) | noted |
| (new) the context at the bound and at `from` | S74's rule at the bound; at `from`, the POSITION selects the view, then the byte (§2.5) `[r1-1106 A3]` | proposed, read from code |

## 3. Clients, in order

### 3.1 First client, the proof step: the lookbehind HAND-OFF `[r5 F1-F5, OWNER ADDENDUM]` `[r1-1106]`

**What Frank ruled** (2026-11-06): the first cross-engine piece is the hand-off form. The reverse DFA
finds the start, existence when the machine has the branch's own language, otherwise the
candidates farthest first, and the forward VM run confirms each and captures. It is built as a
stream PROOF step judged on F1-F3 with the gate "no answer moves, nothing slower", not waiting on a
speed trigger ("seems strange to go all that way and then stop early"). The order is unchanged:
after vlookbehind stage 1 (§4.1 has the full prerequisite list).

**Who owns what** `[r1-1106 D1; manager ruling 1, 2026-11-06]`. `docs/design/vlookbehind.md` owns
lookbehind's ADMISSION ROWS, the `reverse-dfa` candidate source included: their conjuncts, exits
as rows, prerequisites, trigger and witnesses. This note owns the automaton KIND, its exits as
hands, the record and the host (§2). Rev 1 said it "adopts" vlookbehind's row and carried five
PROPOSALS back; vlookbehind rev 3 (written later) adopted only the loop's spelling, so two
documents stated one row differently, and the owner document's text, followed alone, builds r5's
F1/F2 (a `\G` subset machine; a `^` internal-error refusal). Under the ruling the rows below are a
LIST OF PROPOSALS, adopted into vlookbehind by a revision of that note when the proof step is
designed for build (not now: this lane does not edit it). Until that revision lands, vlookbehind
rev 3 §5.4, §6 "Stage 3 (HELD)" and §7 "Stage 3's witnesses" are its text, and S3 is not
buildable from either document alone: the adopting revision is an S3 prerequisite (§4.1).

**The proposals, for vlookbehind's adopting revision** (each with the section of this note that
argues it):

| # | proposal | replaces in vlookbehind rev 3 | here |
|---|---|---|---|
| P1 | conjunct (c) `!pcrec_nfa_has_bot` on the branch's reverse NFA, tested BEFORE the subset construction | nothing (rev 3 has no `has_bot`) | §2.5 |
| P2 | conjunct (c0), the branch's NFA-state bound within the cap, BEFORE (c) | nothing | §2.5 `[r1-1106 A2]` |
| P3 | the language fact `lang = same \| superset`, read after the build | §5.4 "Exactness is read from `Nfa.erased == 0`" | §2.5 |
| P4 | each walk answers for ONE branch; a branch's NO_ACCEPT sends the next branch from the cursor | §5.4's exit wording | below |
| P5 | on `(?<*`, the existence row pushes the next branch's frame before `L_ok` | nothing | below `[r1-1106 A1]` |
| P6 | existence has no early stop (one walk behaviour, `farthest`) | §4 G4 "may stop at the first accept" | §2.2 |
| P7 | prerequisites: no [LANDWALK-VM] and no P-d (the part of §2.3 is the general form [LANDWALK-VM] will use; S1/S1M remove the "third hand-written reverse walk"); no D77 trigger (a proof, Frank 2026-11-06); not HELD | §5.4 prerequisites and trigger, §4 "Why not now", §6 "Stage 3 (HELD)" | below, §4.1 |
| P8 | the selection key is the RECORDED per-branch row, not the width predicate | §5.1b "one predicate on the stored pair" | below `[r1-1106 R6]` |
| P9 | the lever is a `--harness=` internal arm; no public flag and no stamp unless a regime is slower after narrowing | §5.4 "a public deny flag"; §10's stage-3 stamp | below `[r1-1106 R2, N5]` |
| P10 | stage 1's witnesses and `range` fixtures run with the lever DENIED in S3's gate, plus a reach control | nothing | below `[r1-1106 R5]` |
| P11 | the witness list `HO-*` (one id space), replacing §7's stage-3 WD1-WD6 | §7 "Stage 3's witnesses" | below `[r1-1106 D1]` |

**Per-branch selection** (one recorded row per branch; first match; vlookbehind rev 3 §5.1b's table
gains two rows in front of `range`):

| order | row | applies when (conjuncts tested in this order) | exit | finisher |
|---|---|---|---|---|
| 1 | `one-length` | `lo_i == hi_i` | — | today's bytes (ruled (A)) |
| 2 | `reverse-dfa`, existence | (a) `lo_i < hi_i`; (b) no backreference, variable, call, callout or other side-effecting construct in the branch (the AST, before any build); (c0) the branch's NFA-state bound is within the effective cap (the AST, before any build) `[r1-1106 A2]`; (c) `!pcrec_nfa_has_bot` on the branch's REVERSE NFA (before the subset construction); (d) the reverse DFA builds `optional` under its own cap and the rung has not fired; (e) the host is a VM body; then, read after the build, `lang = same` and the branch has no capturing group | `AUTO EXISTS` | none: ACCEPT → the branch holds (on `(?<*`, with the next branch's frame pushed); NO_ACCEPT → the next branch from the cursor |
| 3 | `reverse-dfa`, candidates | (a)-(e) as row 2, `lang ∈ {same, superset}` | `AUTO ENUM` | each candidate confirmed by the forward body run and the end-check |
| 4 | `range` | `lo_i < hi_i` | — | vlookbehind rev 3 §5.1, the total fallback and the reference `[r1-1106 D6: pickup 2]` |

**Rows 2 and 3 are ONE D186 choice row with two exits decided by a fact** `[r5 F29]`. The choice is
`reverse-dfa` versus `range` (one evidence set, one lever); the exit is selected by the recorded
`lang` fact and the group test, not by a regime. A bound over the cap, a has_bot hit, a DFA cap
overflow or the rung is the row's decline to `range`, never a refusal. The conjunct list is a
[ROWCONJ] list (ruling 3, §4.1): [ROWCONJ] lands first, so the list is an instance of its one
conjunct type and R19 does not rise `[r1-1106 R3]`.

**The key is the recorded ROW, read by every pass** `[r1-1106 R6]`. vlookbehind rev 3 §5.1b keys its
table on "one predicate on the stored pair" (`lo_i < hi_i`), read by `vm_count_slots_look`,
`vm_cost_look`, `vm_look_behind_branch` and the role texts. Under that key a row-2/3 branch would
still get range's `LO_i` slot (every family above `low` would shift), range's labels and range's
trail term, and the reader table below would be false. So the key becomes the per-branch row
SELECTED by the table above and recorded once (`one-length`, `range`, `exists`, `enum`), read by the
same four passes plus label allocation. Its ordering constraint: conjuncts (d) and `lang` are read
after a machine build, so the per-branch builds (and the selection) run BEFORE
`vm_count_slots_look`/`vm_cost_look`, after the mandatory machines (§2.4).

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
(`HO-5`). The context byte below an accept is read as on every reverse walk (S74). A
count-collapsed machine would need the width bound back (its lengths are unbounded) and a
character-distance check under UTF-8; it is not proposed.

**The records** (the cursor-rung spelling, RULED by Frank 2026-11-06 and adopted by vlookbehind
rev 3 §5.1) `[r1-1106 D6: pickups 1, 3; client-5]`. Row 3, per branch `i`, inside today's `vm_look`
wiring. It SHARES rev 3's `L_try_i`, `L_body_i` and `L_end_i`: its charge sits before each jump into
`L_try_i`, as range's step charge does, so `L_try_i` is exactly range's (rev 1's sketch charged
after the push, which made `L_try_i` row 3's own):

```
L_b_i:    if (scan_position < lo_i) goto L_b_(i+1)       // guard, as range (bytes >= characters)
          t_i = <part_i>(subject, subject_length, POS, 0) // VK_LSET + VP_AUTO: farthest start or -1
          if (t_i < 0) goto L_b_(i+1)                     // VK_BRANCH: NO_ACCEPT, nothing moved
          scan_position = t_i                             // VK_SEEK, cursor <- local
          RX_CHARGE_WORK(scan_position < POS)             // VK_WORK, typed operand: 1 per non-empty
L_try_i:  RX_PUSH(&&L_adv_i, scan_position)               // rev 3's: the frame saves the CANDIDATE
          goto L_body_i
L_body_i: <B_i forward, vm_emit unchanged>  -> L_end_i    // rev 3's
L_end_i:  if (scan_position != (size_t)slot_values[POS]) goto rx_fail   // rev 3's end-check
          goto L_ok
L_adv_i:  // reached ONLY by popping L_try_i's frame: scan_position = that candidate
          t_i = <part_i>(subject, subject_length, POS, scan_position + 1)   // the next farthest
          if (t_i < 0) { scan_position = POS; goto L_b_(i+1) }  // VSK_RESTORE; the LAST branch:
                                                                 //   `goto rx_fail` alone
          scan_position = t_i
          RX_CHARGE_WORK(scan_position < POS)
          goto L_try_i
```

Row 2, per branch `i` `[r1-1106 A1]`:

```
L_b_i:    if (scan_position < lo_i) goto L_b_(i+1)
          t_i = <part_i>(subject, subject_length, POS, 0)
          if (t_i < 0) goto L_b_(i+1)                     // the branch fails; nothing moved
          RX_PUSH(&&L_b_(i+1), scan_position)             // (?<* ONLY, and not on the last branch:
                                                          //   the one-length row's own frame
          goto L_ok
```

Rev 1's row 2 ("the guard, the call with `bound = 0`, `t < 0 → L_b_(i+1)`, else `goto L_ok`") pushed
no frame on any form. In today's wiring the only path from branch `i` to branch `i + 1` after branch
`i`'s guard is a frame branch `i` pushes (the emitted C of `(?<*ab|(c))x\1`: branch 2's label has
exactly two referrers, the guard skip and `RX_PUSH`; the review's verifier read it). So on `(?<*` a
failing follow popped below the assertion and every later branch was lost:
`(?<*a{1,2}|(a))b\1` on `aaba` is [2-4,1-2] in libpcre2 and was nomatch under rev 1;
`(?<*a{1,2}|(a{1,2}))b\1` on `aabaa` is [2-5,0-2] and was nomatch. The push is the `one-length`
row's frame exactly: pushed at the cursor, not on the last branch (whose continuation is `rx_fail`,
vlookbehind rev 3 §5.1b's rewrite 4), and only on `(?<*` (on `(?<=` and `(?<!` `L_ok` cuts it at
once, so it is not emitted). Pushed after the walk, not before it, so NO_ACCEPT leaves no frame.

**The sweep, re-run through this rule** (STOP RULE check). The review's literal model
(`sound/model.py`, a copy in `docs/dev/lanes/arevrev2_evidence/`, with this rule as
`model_a1.diff`) over its 552,900 cells (1-3 branches from 19 bodies × 3 forms × 8 follows × 49
subjects) against libpcre2 10.46: **0 differences** (rev 1's literal rows: 1,702, all `(?<*`; the
rev 3 `range` control: 0) (`sweep.summary`). One correction to the review's cell list: its third
cell, `(?<*a{1,2}|(b))x\1` on `abxb`, does not reach the hole (branch 1's walk has no accept at
cursor 2, so the next branch runs from the NO_ACCEPT path); the unpatched model already answers
[2-4,1-2] there. The first two cells do.

*Rev 1's paragraph "Under rev 2's spelling, if the cursor-rung spelling is NOT adopted" is HISTORY*
`[r1-1106 D6: pickup 1]`: the owner ruled the cursor rung (vlookbehind rev 3), so the trailed
per-candidate position slot it priced is not designed. (Its sentence that "no existing family's
contract fits" a PER-CANDIDATE slot stays true; rev 3's `LO_i`, written once per entry, is a
different slot and does fit the `low` family, pickup 11.)

**The per-row reader table** (vlookbehind rev 3 §5.1b's second table, extended; one column per pass
that reads it) `[r1-1106 D6: pickup 5, client-6; A1]`:

| row | loop slot | matcher locals | push sites (`npush`) | trail entries per evaluation (`vm_cost_look`) | labels (`vm_look_behind`) | trail checkpoint (`vm_goto`, K134) | seam sites ([M5-SEAM]) | role texts |
|---|---|---|---|---|---|---|---|---|
| 2 existence | none | the result local `t_i` (untrailed) | 1 on `(?<*` if not the last branch, else 0 | 0 | `bl` only (no `bodl`, `endl`, `L_try_i`, `L_adv_i`) | none (no backward jump) | 0 back-steps, no `advance` | its own: "branch %d, width %d..%d: reverse DFA, existence" |
| 3 candidates | none (no `LO_i`) | `t_i` | 1 (`L_try_i`), the last branch included | 0 | `bl`, `bodl`, `endl`, `L_try_i`, `L_adv_i` (no `L_far_i`, `L_n_i`) | only where the body itself writes the trail (rev 3 §5.1b's list: a capture, a cursor or counter rung's `SET`, an atomic mark, a nested lookaround's mark and `POS`, a callee's park) | 0 back-steps, no `advance` | range's texts with "candidates from the reverse DFA" |

The trail term is per ROW (exact form): range 1 per branch (`LO_i`), rows 2-3 0. A shared
`2 + (number of varying branches)` would over-charge a row-2/3 branch by one, which is safe, but
the recorded row (above) makes the exact form free. Rev 1's parenthetical "its back edge closes a
trail cycle only where the body itself writes the trail (captures)" was narrower than rev 3's list;
the K134 column now cites the list.

**Composition with `vm_look`: every continuation of every frame** `[r1-1106 A1; the critic skill's
new soundness rule]`. Rev 1 argued only about the retries the row removes. The rule adopted by the
manager with this review: when a design removes a frame push, list every path that frame's pop
reaches. Range's frames in branch `i` and where their pops lead, against rows 2-3:
- **Branch `i`'s other candidates** (range's `L_adv_i` frame). Row 3 keeps the ones its machine
  accepts, in the same order, and skips only starts no confirm can pass. Row 2 drops them all: each
  would end at the same cursor with the same groups (row 2's branch has no capturing group and no
  side effect, conjunct (b)), so the follow sees an identical state and fails again. Unobservable
  except in frames, steps and work (the one-way change below).
- **The body's own choice points.** Row 3 keeps them (the body runs as range's). Row 2 has none; the
  same argument: every alternative path ends at `POS` with the same groups.
- **The later branches** (range reaches `L_b_(i+1)` through `L_adv_i` → exhaustion → `L_n_i`'s
  restore). Row 3: the same path (`L_adv_i`'s restore on NO_ACCEPT). Row 2 on `(?<*`: its pushed
  frame, at the cursor, the trail rewound. Row 2 on `(?<=`/`(?<!`: `L_ok` cuts every frame of the
  evaluation in both rows and range, so no later branch is reachable from the follow in either. On
  NO_ACCEPT (both rows) no candidate of branch `i` could succeed, so range's own path also ends at
  `L_b_(i+1)` with the cursor restored and nothing written.
- **Below the assertion** (the frames pushed before it). Untouched by every row.

**Soundness of row 3**, by construction against `range` `[r1-1106 D6: client-6, pickup 9]`. Range
tries every start that `$_back_step` reaches within `hi_i` characters of the cursor and at least
`lo_i` characters back, farthest first (under UTF-8 the farthest start is the farthest position
`$_back_step` reaches: an ill-formed run stops it, vlookbehind rev 3 §5.1a; rev 1's
"`[lo_i, min(hi_i, cursor)]`" was the byte reading), confirming each by the body run and the
end-check. Row 3 tries the subset of those starts that the machine accepts, in the same order
(ascending position = farthest first; the moving bound gives exactly the next one). A start the
machine does not accept cannot pass the confirm: `lang` is same or superset, so the truth is inside
the machine's language. A skipped candidate leaves no state behind in range either: a failed
confirm backtracks to the frame, which restores the position and every trailed write. So the first
confirmed candidate, every group it writes and, on the non-atomic form, the order of every later
retry are range's. Branch order is kept by per-branch machines (`HO-2`). Under UTF-8 the byte
machine accepts only at character boundaries of VALID input (pcrec's byte machine is strict: the
review measured surrogate and overlong cells equal to libpcre2), and every such start is one
`$_back_step` reaches; candidates replace both of range's position mechanisms, so the
`$_back_step` calls, their sentinel and far retry, and the bounded one-character step
(`VSK_STEP_CHAR`, the encoding's `advance`) are not used by rows 2-3.

**Work and give-ups** `[r5 F9, F21]` `[r1-1106 D6: pickup 4, client-4]`. Range charges, per
evaluation of a branch (vlookbehind rev 3 §5.5): `lo_i` for the nearest step, `K_i` per far try,
then 1 per step to the next candidate; at most `2·hi_i − lo_i` on the common path, plus the far
retry's `(hi_i − lo_i)(hi_i − lo_i + 1)/2` only in the UTF-8 corner. Row 3 charges ONE per
candidate it hands to the confirm that starts below the cursor, nothing for the walks; row 2
charges nothing. The comparison holds PER CANDIDATE, as a prefix inequality: before each candidate's
body runs, row 3's charge so far is at most range's charge so far before the same candidate
(attribute range's `lo + ΣK` to its farthest candidate and each step's 1 to the candidate it
reaches; row 3's candidates are a subset of range's in the same order). The review's client critic
checked it on vlookbehind rev 3's candidate cells (8,583,480 cells, bytes and UTF-8, ill-formed
included, the far retry included, every range candidate taken as accepted, row 3's worst case): 0
violations. The prefix form also covers early success, which a totals statement does not. Rev 1's
parenthetical "the empty candidate at `lo_i = 0` charges nothing, as range's `d = 0` candidate
does" is false under rev 3 (range reaches the empty candidate by `L_adv_i`'s step, charged 1, unless
it is the only candidate); the conclusion stands. Steps: one pop per failed candidate, and row 3's
are a subset; row 2's `(?<*` frame pops once where range pops at least once. Frames: at most one
loop frame live per branch in every row. Trail: range 1 per branch, rows 2-3 0. So every budget
counter of rows 2-3 is at most range's in every evaluation: they never give up where range
answers, and may answer where range gives up. That is a ONE-WAY give-up change, which
[GIVEUP-DIFF] (direction-checked GIVEUP1) must cover before the row ships. The walks are bounded
without a charge: each is at most `4·hi_i` bytes (UTF-8's widest character), and at most
`hi_i − lo_i + 1` walks run per evaluation, each reached through charged VM steps.

**[GIVEUP-DIFF] for a row that is not a LOCATE row** `[r1-1106 R2]`. GIVEUP1 compares the corpus
"default vs each DENY", and `make test-axes` already runs test-only `--harness=` arms in the same
job loop (`tests/axes/run_axes.sh`'s `INTERNAL_ARMS`, `--harness=no-compound` and
`--harness=pres-window`). So the row's lever, a `--harness=` arm (ruling 4; P9), is compared by
GIVEUP1 with no new mechanism. What [GIVEUP-DIFF] lacks: its direction rule reads a LOCATE row's
`.giveup` classification and its trigger names locate_finish L3-L5 and [LANDWALK-VM]. The proposal
(a PLAN item for the manager's [GIVEUP-DIFF] row): its trigger and scope name this row; the row's
ONE_WAY classification ("default answers, deny gives up" admitted) is declared on the arm's job
entry beside `INTERNAL_ARMS`, since the row has no `.giveup` column; and its constructed ONE_WAY
witness `HO-V`: a work-budget cell where `range` gives up and row 2 answers (shape:
`(?<=a{1,255})x` after a long run of `a`, under a `--work-budget` below range's `2·hi − lo = 509`
per evaluation; row 2 charges 0). The budget value is the build's to pin (INFERRED).

**The STOP RULE does not fire.** The hand-off is sound on every body the row admits: a widening
erasure (atomic, possessive, nested lookaround) only adds candidates that the confirm rejects; the
narrowings (`\G`, `^`, `\A`, `(?m)^`) are declined before the build; backreferences have no machine
(`compile_ast`'s A_BREF arm) and decline; callouts, verbs and `\K` are refused inside a lookbehind
today and stay declined by conjunct (b) on the day they are admitted. `[r1-1106]` Rev 1 also needed
two facts it did not have, and both are fixed rather than restricted: on `(?<*` the existence row
keeps the frame that reaches the later branches (A1: the sweep's 1,702 cells agree), and no build on
the admission path can refuse (A2: (c0)). The atomic counter-example: `(?<=(?>ab|a)b{1,2})x` on
`abx` is nomatch in libpcre2 while the erased machine accepts at 0; row 2 declines
(`lang = superset`) and row 3's confirm rejects the candidate, so the answer is range's.

**The gate** (manifesto §5, Frank's "no answer moves, nothing slower") `[r1-1106 R2, R4, R5, N5,
D6]`:
- **Answers.** `tests/lookaround/run_lookaround_diff.sh` (vlookbehind rev 3 gate 1's harness, its
  variable-lookbehind section, which lands with stage 1) over the generated cell set, with the row
  on (the default) and with its `--harness=` arm denying it: 0 differing answers against libpcre2
  10.46 outside two NAMED classes, each on its own line: D142's stated UTF class, and K74's
  ([UTF-END-ASSERT]: an end assertion at an ill-formed UTF-8 subject end, whatever the row). The
  cell set includes ill-formed UTF-8 subjects under `PCRE2_MATCH_INVALID_UTF` for rows 2-3 (rev 3
  gate 1's own addition; `HO-U`'s cells). The zero-width-repeat divergence (rev 3's V6 cell
  `(?<=(?:)*a{1,2})x`) is on its own line; it reaches ROW 2, not row 3 as rev 1 said (it varies,
  has no group, and an empty star sets no `NFA_ERASED_*` bit: read from the builder, confirmed at
  build) `[r1-1106 N6]`. Plus the corpus answer identity, default versus the arm.
- **Stage 1's own witnesses stay on `range`** `[r1-1106 R5]` (P10). With rows 2-3 on by default,
  most of vlookbehind rev 3 §7's cells leave `range`: row 2 takes W2, W3b, W4, W7, W11(a) branch 0,
  W11(b), W12(a), W12(b), W13's second cell and W16's first; row 3 takes W1, W5, W6, W13's first
  cell, W15 and W14's Kelvin cell (counts INFERRED, the row is unbuilt). The `residlbrange` codegen
  fixture's back-step count would drop from 3 to 1 (branch 0 takes row 2), reddening
  `run_codegen_tests.sh` at S3's landing, and the S133/S134 `range` twins' anchors would not be
  emitted for it. So S3's gate runs stage 1's witness rows, the `range` fixtures and S133/S134 with
  the row's arm DENYING it, and adds a reach control per row ([MECH-REACH]): each stage-1 plant
  still reached in the deny build, each `HO-*` plant reached in the default build.
- **Bytes.** Every artifact without a varying lookbehind branch is byte-identical under
  `scripts/emit_sweep.py`, the one comparator (vlookbehind's gate 2 uses
  `tests/codegen/run_recursion_identity.sh` for its own step; S3 uses the corpus sweep) `[r1-1106
  N5(d)]`. Artifacts that take rows 2-3 are new emission: an abi event at the landing number,
  readers by grep (D76/D94).
- **Spec hunks** `[r1-1106 N5(e)]`. A `tuning.md` section for the row and its rung, naming the lever
  as test-only the way the kit's `pres-window` arm is listed; `limits.md` §8.4's rung row (§2.4). NO
  stamp: vlookbehind rev 3 §10 owes "a `tuning.md` §2 section for the row and its stamp", and P9
  proposes the stamp only with a public flag, which rides [IFACE-PUSH] if a regime is ever slower
  after narrowing (flag follows caller effect).
- **Nothing slower.** vlookbehind rev 3 §5.4's evidence requirement, all four regimes: (a) short
  bodies, (b) the bench's `negation-scope-lookbehind-var` on its own subjects (BLOCKED on pcrec
  until stage 1 ships and the bench lifts its `lookbehind-variable` declaration: an inbox entry the
  manager owes then), (c) a wide body whose candidates do not fail at the first byte
  (`(?<=\w{1,64}x)y`), (d) a random-like subject. A regime slower beyond noise NARROWS the row's
  admission (a minimum width, a body shape), never adds a parallel path.
- **F1-F4 checks** `[r1-1106 R4]`: G2's grep (no C text in the record), F4's round trip, the
  golden check and the part oracle (below), each a cell.

**Witnesses** `HO-*` (each a libpcre2 10.46 cell, `arevrev1_evidence/premise.out` and
`arevrev2_evidence/premise.out`; P11) `[r1-1106 D1, N2]`. In the DEFAULT build each is red under its
named plant where the row admits. In the row's DENY build each runs `range` and either names the
stage-1 plant that reaches it there or is marked **row-only (deny build: control)**: a
reverse-machine hazard that `range` cannot have, green by construction there. Rev 1's "every cell
can fail in both builds" was false for six cells (the review modelled six stage-1 plants over 18
cells). The vlookbehind rev 3 §7 id each one replaces is given (one id space after the adoption):

| id (rev 1) | intent and plant (default build) | cells | deny build |
|---|---|---|---|
| `HO-1` (WD1; replaces vlb WD1) | the `lang` conjunct dropped (a superset machine taken as existence) | `(?<=(?>ab\|a)b{1,2})x` on `abx` nomatch, `(?<!(?>ab\|a)b{1,2})x` (2,3); `(?<=(?>a\|ab)b)x` / `(?<!…)` on `abbx` nomatch / (3,4) | rev 0's `abbx` pair: W2; the `abx` pair: row-only (control) |
| `HO-G` (WD-G) | conjunct (c) dropped | `(?<=\Ga{1,2})b` on `aab` from 0, 1, 2: (2,3), (2,3), nomatch; `(?<!\Ga{1,2})b`: nomatch, nomatch, (2,3); on `caab` from 1: (3,4) / nomatch; controls `(?<=\Ga{1,3})b` / `(?<!…)` on `caab` from 0: nomatch / (3,4) | W14 (its own cell) |
| `HO-A` (WD-A) | (c) tested after the build (the cell becomes a compile refusal) | `(?<=^a{1,2})b` on `aab` (2,3), `(?<!^a{1,2})b` nomatch, `(?<=\Aa{1,2})b` (2,3); `(?<=(?m)^a{1,2})b` on `c\naab` [4-5], `(?<!(?m)^a{1,2})b` nomatch, `(?<=(?m)^a{1,2})b` on `caab` nomatch (rev 1 said this cell was owed by the build's harness; the probe's `x` mode runs it today) `[r1-1106 N7]` | the negative cell: W4 (by hand trace); the rest row-only (control) |
| `HO-B` (WD-B) | a branch's NO_ACCEPT taken as the lookbehind's | `(?<!a{1,2}\|b)x` on `bx` nomatch, `(?<=a{1,2}\|b)x` on `bx` (1,2), also from offset 1; control `(?<!a{1,2}\|b)x` on `cx` (1,2) | W11(a); the `cx` control row-only |
| `HO-NA` (new) `[r1-1106 A1]` | row 2 on `(?<*` with no next-branch frame | `(?<*a{1,2}\|(a))b\1` on `aaba` [2-4,1-2]; `(?<*a{1,2}\|(a{1,2}))b\1` on `aabaa` [2-5,0-2] | W11(a) (by hand trace: without the restore, branch 2 starts from the nearest candidate and its end-check fails) |
| `HO-2` (WD2; replaces vlb WD2) | one machine for the whole lookbehind, confirmed by the whole alternation | `(?<=(a{1,2})\|(aa{1,2}))c` on `aaac` [3-4, 1-3, g2 unset]; vlb WD2's W10 cell `(?<=(a)\|(aa))c` on `aac` g1 = (1,2) | W1; W10 |
| `HO-3` (WD3; replaces vlb WD3) | the nearest candidate first | `(?<=(a{1,2}))b` on `aab` [2-3, 0-2]; vlb WD3's W1 cell | W1 |
| `HO-4` (WD4; replaces vlb WD4) | no `L_adv_i` re-walk (only the farthest candidate) | `(?<*(a{1,2}))b\1c` on `aabac` [2-5, 1-2]; vlb WD4's W5 gap cell `(?<*(a\|aaa))c\1` on `aaaca` (3,5) g1 = (2,3) | W2, W5, W16 |
| `HO-5` (WD5; replaces vlb WD5) | the bound at `search_from`, not 0 | `(?<=a{1,2})b` on `aab` from 2: (2,3) | W7 |
| `HO-6` (WD6; replaces vlb WD6) | the context below an accept ignored | `(?<=\ba{1,2})x` on `baax` nomatch; control ` aax` (3,4) (only `baax` discriminates; keep the pair) | row-only (control) |
| `HO-8` (WD8) `[r1-1106 A3]` | the part ignores `from`'s right context: (a) the byte; (b) the POSITION (reads only `s[from]`, no length compare) | (a) `(?<=a{1,2}\b)x` on `aax` nomatch, `(?<=a{1,2}\b)-` on `aa-` (2,3); (b) `(?<=a{1,2}$)\nb` on `aa\nb` nomatch, `(?<=a{1,2}\z)\n` on `aa\n` nomatch; controls `(?<=a{1,2}$)` on `aa` (2,2), `(?<=a{1,2}$)\n` and `(?<=a{1,2}\Z)\n` on `aa\n` [2-3], `(?<=(?m)a{1,2}$)\nb` on `aa\nb` [2-4] | the `$`-on-`aa` control: W2; the rest row-only (control) |
| `HO-R` (W-restore) | no `VSK_RESTORE` before `L_b_(i+1)` on row 3's exhaustion | `(?<=(?>ab\|a)b{1,2}\|ab)x` on `abx` (2,3) | W11(a) |
| `HO-U` (W-UTF) `[r1-1106 N2, D6]` | the part accepting mid-character (a reverse machine whose accept is not filtered to character boundaries), which no other cell plants | `-e utf8`: `(?<=é{1,2})x` on `aééx` (5,6), `(?<!é{1,2})x` nomatch, `(?<=(é{1,2}))x` g1 = (1,5); under `PCRE2_MATCH_INVALID_UTF`: `(?<=é{1,2})x` on `A9 C3 A9 x` [3-4], `(?<=(é{1,2}))x` on `FF C3 A9 C3 A9 x` [5-6, 1-5], `(?<!é{1,2})x` on `C3 C3 A9 x` nomatch | row-only (control); range's own UTF cells are W6, W13, W15 |
| `HO-N` (new) `[r1-1106 A2]` | (c0) dropped | `(?<=\p{L}{1,255})b` under `-e utf8` compiles and answers as `range` | row-only (control: `range` compiles it by construction) |
| `HO-T` (W-trail) `[r1-1106 D6: pickup 10]` | a trailed write per candidate (a per-candidate position slot) | `(?<*(a{1,5}))bz` on `aaaaab`: nomatch (five candidates, each confirmed with a group write, the follow fails; INFERRED: a per-candidate trailed write overflows the bounded trail, `PCREC_ERR_FRAMES`, capacity checked at build) | W12(a) |
| `HO-V` (new) `[r1-1106 R2]` | the ONE_WAY witness: the row's give-up direction | the budget cell above (`range` gives up, row 2 answers) | it IS the deny-build give-up |

**Per-part oracle (G3/F3)** `[r1-1106 R1]`. Rev 1 defined the part's answer at (`from`, `bound`) as
"the smallest `s ≥ bound` such that `B` matches anchored at `s` ending exactly at `from` …, the end
tested by a callout or by comparing `ovector[1]`". Both halves were wrong for some part:
- **Per `lang`.** On `lang = superset` the part legitimately accepts starts libpcre2 rejects: the
  erased machine of `(?>ab|a)b{1,2}` accepts at 0 on `abx`, where no match of the body exists. An
  equality oracle fails a correct part by design. The contract is ONE-SIDED: every true start is
  among the part's accepts (enumerated by moving the bound), so the part's answer is at most the
  smallest true start at or above the bound. On `lang = same` the contract is EQUALITY.
- **Every end, not the priority end.** "Comparing `ovector[1]`" sees only the priority end: for the
  branch `a|ab`, `s = 0`, `from = 2`, libpcre2's match is [0-1], while `ab` does end at 2 and a
  correct part answers 0. The oracle is the callout form only: compile `(?:B)(?C1)` and match
  ANCHORED at `s` on the whole subject (so the context on both sides is real); the callout returns 0
  iff the current position is `from`, else 1, forcing backtracking through every end.

S3 owns the oracle and the record-in / text-out golden-check hook (a test-only hook under `tests/`,
no caller surface) `[r1-1106 R4]`; INFERRED, not built.

**The D27 author** `[r1-1106 N5(c)]`. S3's spec-first author works from an extract cut, at S3's
design-for-build time, from vlookbehind's adopting revision (the rows) plus this note's §2.3 contract
and the oracle above (a `*_d27_extract.md` beside it, docs/design/CLAUDE.md's rule: re-cut, never
edited).

**One tagged machine instead of per-branch machines** stays a later rendering (vlookbehind rev 3
§5.4). **The filter row** (rev 0's `gate`: the reverse DFA as a yes/no filter in front of range's
own loop) is a later option beside rows 2-3, HELD with no trigger of its own: it is rows 2-3 with
the candidate hand-off removed, which nothing needs.

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
  `[r1-1106 D2, D4]` The floor leaves all FIVE strings (the two printers and each reverse object's
  `seed_cond`, `at_bound`, `scan_more`), not two; the fields of §2.1's "fields rev 1 did not state"
  table get their owners; label stems come from the declared instance → stem row (`revend`,
  `reverse`, `landmark`, the forward stems), distinct per walk in one host function. S1 also owns
  the record's text writer and reader and the seam round trip `[r1-1106 R4]`.
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
- **S1's sabotage reader set is wider than its five re-aims** `[r1-1106 N4]`: 183 sabotages anchor
  `src/gen/emit_dfa.c`, and 36 of them name a token S1 touches (e.g. S72's anchor spans
  `stay_advance(f, K, f->dir->scan_more)`; S82's is the floor literal `gseed ? "search_from" :
  "0"`; S73). So S1's gate is "the sabotage matrix's anchor check: 0 missing anchors; the five named
  rows also DETECTED", not five re-aims alone.

## 4. Steps `[r5 F23, F26, F28; OWNER ADDENDUM]`

### 4.1 The step list

| step | what | bytes | prerequisites (at 6e01c810b) | gate | trigger | ratchet (§4.3) | cost (F28) |
|---|---|---|---|---|---|---|---|
| S0 | this note (rev 2 after the re-check r1-1106); the manager's roadmap §5 restatement (R28', R03', R10' rows); the D-next entry | none | none | a readiness re-read | now | recipes proposed (§4.3) | text |
| S1 | the record (`DfaForm` made into it, form rows as plan outputs, the fields of §2.1's rev-2 table with owners) for every DFA walk; the `DfaDir` copies and the five floor strings folded; stems by instance; the record's text writer/reader; S74 re-aimed (§3.3) | 0 movers | p1build MERGED; the manager's roadmap §5 restatement of R28' (its gate counts against it) `[r1-1106 R8]` | `emit_sweep.py` identity over the corpus, movers 0; `make test`; `make test-codegen`; the sabotage matrix's anchor check, 0 missing anchors, with S74, S1825, S1827, S759, S760 re-aimed and DETECTED `[r1-1106 N4]`; the two floor cells; G2's grep (no C-text field) and F4's round trip `[r1-1106 R4]` | ride-along: the first change that opens a DFA walk ([REVBLOCK-VIEW] likeliest; [LANDWALK-ALLACC], [LANDWALK-WINDOW], rev-inner (D151)), or the proof step's own build | R28' 5 → 0 | M: a corpus sweep (box lock, a heavy job), a full `make test` (~11 min), codegen, the anchor check, five sabotage re-aims, the writer/reader; one CODE critic round |
| S1M | the machine table: every walked machine an entry (`nedfa` in, `xprio` out, §2.4); the lowering a table fact; the swap re-expressed as ROLES every reader uses (two address tests, two memos re-keyed) `[r1-1106 D3]` | 0 movers | S1 | as S1; the reader grep recipe of §2.4 read empty of slot-identity readers | rides the proof step (lands just before it); H-FLAGS's machine trigger | R14 (H-FLAGS) 1 → 0 if the hub's owner and shape are written with it | L (restated from M `[r1-1106 D3]`): 160 reader sites by the grep recipe, the role layer, a corpus sweep with tagged artifacts in it, `make test`; one CODE critic round. The rung is NOT S1M's (it is S3's, §2.4) `[r1-1106 R7]` |
| S2 | revdet's STEP onto the record (§3.2) | 0 movers | S1 | identity; `make test`; S50-S52, S94, S160 DETECTED | a change opening `vm_revdet_rep` (a revdet widening); also a ride-along [VMREC] (b)/(c) MAY carry (named in [VMREC]'s row as such) `[r5 F26]` | none falls: the step was never a ratchet member; R03' is the LOOP (§4.3) | S: identity sweep on the VM corpus, `make test`, five re-aims |
| **S3, the PROOF step** | the part in the code-segment slot, the call as four MEMBERS (§2.3); the lookbehind's rows 2 and 3 (§3.1) with their recorded per-branch row; the size-cap rung and its readers (§2.4); the `--harness=` lever; the part oracle and the golden-check hook | moves only artifacts with a varying lookbehind branch (abi event) | vlookbehind stage 1 (`range`) SHIPPED; **vlookbehind's adopting revision** of §3.1's proposals P1-P11 (ruling 1) `[r1-1106 D1]`; **[ROWCONJ]** built (its three byte-identical migrations), so rows 2-3's conjuncts are an instance of its one type (ruling 3) `[r1-1106 R3]`; S1, S1M; **[GIVEUP-DIFF]** with its trigger and scope widened to this row, the arm's ONE_WAY classification and `HO-V` (§3.1) `[r1-1106 R2]`; a D27 spec-first author with its extract (§3.1). NOT [VMREC]: the call is members (ruling 2); only the part's EFFECT SET waits for (c), and S3 does not wait for it (§2.3) `[r1-1106 D5]` | §3.1's gate: answers (`run_lookaround_diff.sh`, the row on and the arm denying it; D142's and K74's classes named), stage 1's witnesses and fixtures on the deny arm with a reach control, bytes (`emit_sweep.py`), the spec hunks, the four regimes; F1-F4 by §0's checkable forms (diff classification, G2's grep, the round trip, the golden check, the per-part oracle) | NONE: scheduled as a proof (Frank, 2026-11-06) once its prerequisites land | R28', R03', R10' do not rise (an instance and the kind's first host loop); R12, R11, R13 do not rise (`CT_*` hands, the existing `FitSets` spelling); R19 does not rise because [ROWCONJ] lands first (no fifth private conjunct struct, no R19 +1 exception); re-counted at its head | L: the D27 author, the build, `make test`, the lookaround differential in both builds, `test-axes` (the arm rides `INTERNAL_ARMS`), a CODE critic round, a timing window for the four regimes (cleared with Frank, never 20:00-01:00) |
| S4 | the landmark walk's body as records (P-d) | 0 movers | P-b (not started; waits on P-c); [VMREC] (b) | P-d's: identity, one renderer body | P-b landed and a change opening the walk ([LANDWALK-VM], [LANDWALK-FWD], [LANDWALK-ALLACC]) | R10' 1 → 0 | M |
| S5 | the moving-seed host loop: W2's seed list, W3's hits and W4's walk as instances of the kind's one host loop, beside S3's moving-bound loop | 0 movers | S1, S2, S3 (the host loop's first instance) | identity; the walks' witnesses | the third member's next change, or [LANDWALK-WINDOW] | R03' 3 → 0 | M |

Rev 0's S5 (the `commit` row, HELD) is GONE: it is the proof step's row 3 `[OWNER ADDENDUM]`. Rev 0's
"S1 and S2 cost nothing on the box" was untrue `[r5 F28]`.

**S3's real wait, written out** `[r1-1106 N3, D5; manager rulings 2 and 3, 2026-11-06]`. Rev 1 made
S3 wait for "[VMREC]'s ANALYSIS stage (c)", under r5's ruling that a step adding a VM record KIND
waits for it. Rev 1 also understated that wait: plan.md orders [VMREC] (b) (the analysis-free R
stage), then a soundness round on its lexer section, then (c)'s own D27 spec-first author, then (c).
Under ruling 2 the hand-off adds no kind (§2.3), so that chain is no longer S3's: the effect-set
declaration rides (c) for all three in-body-call members whenever (c) lands. S3's chain is
instead: vlookbehind stage 1 shipped → vlookbehind's adopting revision → [ROWCONJ] → S1 → S1M →
[GIVEUP-DIFF] (widened) and the D27 author (both separable test-side lanes, in parallel with the
build once the lever's name and the record's field list freeze) → S3. The rung, the oracle and the
golden check are separable lanes once S3's machines and the part signature exist.

**Why the proof step needs no speed trigger.** Rev 0 §4.2 made it wait for "pcrec slower than
libpcre2 with the lookbehind as cause", a cell vlookbehind §3 (rev 2, unchanged in rev 3) predicts will not show `[r5
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

**Recipe words, rev 2** `[r1-1106 R8]`. The review recounted all three at e20dee230 and agreed (R28'
5, R03' 3, R10' 1; no code has moved since), and found the WORDS fragile:
- **R10'** counted `while (`, which also matches the `do { … } while (0)` scaffold (:14504) that is
  not a loop, and "lines of its body" falls to 0 if the loop-printing lines move into a helper (a
  rename, not P-d). Restated: the LOOP CONSTRUCTS the registered emitter prints, in its own body AND
  its static callees: `for (`, a `while (` not closing a `do` block, and a backward `goto`. Shared renderers the kind already owns (`emit_scan_loop`, `emit_reverse_block`) are NOT counted (manager 2026-11-06, lane ratchet3: counting them over-reads by at least 3). 1 at
  6e01c810b.
- **R28' (i)** said "objects", but the tree also carries a forward declaration
  (`static const DfaDir dfa_dir_forward;`, :7106), so a line grep reads 6. Restated: DEFINITIONS
  (initialized `DfaDir`s, plus run-time copies with fields overwritten), minus the number of rows of
  the record's DIRECTION table, not a literal 3, so a legitimate new direction (rev-inner's, D151)
  does not raise the count. Before S1 builds that table the subtrahend is today's three directions.
- **R28' (ii)** would fall to 0 if `emit_rev_end_one_seed`/`_tagged` were routed through
  `emit_reverse_block` with a flag while their seed code stayed. Restated: reverse walk renderings
  whose SEED code lies outside the record's renderer, wherever they are called from.
- The rows do not exist in roadmap §5 yet (it stops at R27; R03 and R10 keep their old recipes). The
  manager's restatement is a PREREQUISITE of S1's gate (S0, §4.1), and a PLAN item, not this note's
  edit.

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
  IS that unification `[r5 F29]`. The lookbehind's member is ROW 3's moving `bound`
  (`ZERO`, then `CANDIDATE + 1`), not range's: under vlookbehind rev 3 range's floor is a FIXED
  nearest start `LO_i` with a one-character step toward it `[r1-1106 D6: pickup 8]`.
- **In-body calls to a separately emitted unit, three members** `[r1-1106 D5(b)]`: kit windows
  (`VP_KIT`), code segments and callouts (`VK_CALLOUT`, their declaration slot
  `pcrec_emit_code_protos`), and the part (`VP_AUTO`). Past the unify-at-the-third threshold: one
  declaration slot (§2.3 reuses the code-segment slot) and one effect-set declaration at [VMREC]
  (c). Unlock: one call record for the three; trigger: (c)'s analysis needs the third member's
  effects, which holds the day S3 lands.
- **Automata built per site and run inside a VM body, three members** `[r1-1106 D5]`: revdet's
  reversed AST (structural), [ENG-ISL]'s trie (`vm_isl_build`, roadmap A-ISL), and the lookbehind's
  table machines. Noted; the machine table (S1M) is where their entries meet.
- **The machine-language fact, four readers** `[r1-1106 D5]`: `lang` (new), the
  `RX_VM_PREFILTER_LANG` stamp (exact / count-collapsed), `RX_VM_RESEED`'s exact/superset
  (locate_finish C10's classifier), and the landmark walk's `lmnfa.erased == 0` gate
  (compile.c:554). A-FACTS' "superset record" is the family's home; `lang` should be read from it
  when A-FACTS builds it, not re-derived per reader.
- **First-match rows whose exit is a recorded fact, three members** `[r1-1106 D5]`:
  `revend_forms[]` (form by fact), the landmark walk's AT/LOWER finisher by erasure, and rows 2-3's
  exit by `lang`. Noted for [ROWCONJ]'s `form` column (its `RowConj` carries a form).
- **The general form of the proof step** (the review's readiness critic, Standing Q2): a CONTRACTED
  PART CALLED FROM A HOST PROGRAM: a compiled component with typed position inputs, typed hands
  out and a declared effect set, called by a record in the host's stream, with an oracle of its own
  contract. Unlocks with triggers: lookahead-as-check (a forward `AUTO EXISTS` on capture-free
  regular lookaheads, roadmap §4 row 12; trigger: a corpus or bench cell where such a body's VM run
  dominates an evaluation); the anchored verify as a forward part ([LANDWALK-VM]; its own measured
  cell); per-part oracles for every contracted part (trigger: a second contracted part lands, or a
  part bug found only end-to-end); [LB-EXIST]'s unbounded lookbehind through the same call (its
  plan row's trigger).
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
   count their own cells (K35). Reach `[r1-1106 N2, R5]`: each `HO-*` cell names the stage-1 plant
   that reaches it in the deny build or is marked row-only (a control there); stage 1's own
   witnesses run on the deny arm in S3's gate so `range` stays checked, each with a reach control
   ([MECH-REACH]). (c0)'s bound is controlled by the builder's real count, not by itself (§2.5).
   The per-part oracle is libpcre2's callout form, per `lang` (§3.1).
3. **What moves when data is regenerated.** MOSTLY NOT RELEVANT: no table, calibration or measured
   set. Machines are generated per artifact from the pattern. S3's new emission is an abi event
   (readers by grep) and a `tuning.md` hunk (D80); a future price card for rows 2-3 would move
   selections, never answers. A raised `--max-nfa-states` moves (c0)'s decisions (more branches
   admitted), selections only.

## 8. Questions for Frank (plain words; leanings are not rulings) `[r5 F27]`

1. ~~Spell the lookbehind loop the cursor-rung way?~~ ANSWERED: Frank ruled the cursor-rung shape
   on 2026-11-06, adopted by vlookbehind rev 3 for `range` and by this note for the hand-off
   `[r1-1106 D6: client-6]`.
2. **Move every machine into one table before the hand-off, or only the lookbehind's?** One table
   for all of them is the hub's own end state and keeps one way of naming a machine; it is a medium,
   byte-identical step just before the hand-off. Only the lookbehind's would be smaller now and leave
   two ways side by side. Leaning: all of them, in its own step.
3. **The ratchet counts I restated go UP before anything is built** (the revdet row from 1 to 3, the
   direction-copies row to 5), because they now count what the code does rather than names. That is
   the manager's to record; you may want to know the totals rise on paper. No ruling needed unless
   you object.

Rev 2 adds no question for Frank: the re-check's four questions were the manager's and are ruled
(ownership, members, [ROWCONJ] first, the harness lever).

## 9. What this note does not decide

- The C names (`AutoRun`, the part header, the new members `VP_AUTO`, the result local, the seek
  form and the work operand) and field layout: the build lane's.
- The lookbehind's admission rows as text of record: vlookbehind's, at its adopting revision
  (ruling 1); §3.1 proposes them.
- Whether (c0)'s bound is a function beside the NFA builder or a counting pass of it (§2.5): the
  build lane's, under the same control.
- When [VMREC] (c) declares the one effect set for the in-body-call family (§2.3): [VMREC]'s.
- Whether `dfa_form_derive` moves files when the form becomes a plan output (H-HEADER / A-PLAN).
- The early-stop exit, the filter row, one tagged machine for many branches, TDFA tags for W4,
  unbounded lookbehind: HELD.
- P-b's order relative to P-c (roadmap §6).
- Any change to the manifesto (none is needed) or to APPROACH.md.

## 10. Measured vs inferred

- MEASURED (rev 2, lane arevrev2; `arevrev2_evidence/`): A1's cells and the 552,900-cell sweep
  through the corrected row-2 rule (0 differences, the review's model with `model_a1.diff`); A2's
  libpcre2 cells (`c u`) and pcrec's NFA-cap refusals at 6e01c810b, with the threshold (`\p{L}{36}b`
  passes the cap, `{37}` fails); A3's `$`/`\Z`/`\z`/`(?m)$` cells; `HO-A`'s `(?m)^` cells; `HO-T`'s
  cell; `HO-U`'s ill-formed cells under `PCRE2_MATCH_INVALID_UTF`. Read from the review's critic
  texts, not re-run: the 8,583,480-cell prefix-inequality check (client), the reach model over 18
  cells (ready), the reader counts (re-grepped: 160 sites).
- MEASURED (rev 1, libpcre2 10.46 as a library, rev 1's `probe.c`): every cell of §3.1 and the
  F1/F2/F3 cells (premise.out, cells.txt). Rev 0's floor cells (`a+b`, `[ab]+[bc]` from offset 1)
  are rev 0's measurements, not re-run.
- READ from code at fd1a32021 (re-grepped, not executed): §1, §2.3's placements, §2.5's two
  narrowings and `pcrec_nfa_has_bot`, the ratchet counts of §4.3.
- INFERRED: every byte-identity expectation (proved only by each step's comparator); the hand-off's
  soundness argument (by construction against `range`; the gate's differential is the check); the
  work and trail figures; the per-part oracle; W-trail's concrete cell. Rev 2: (c0)'s bound (a
  design, its control owed by the build); `HO-T`'s trail capacity arithmetic; `HO-V`'s budget
  value; the counts of stage-1 witnesses that leave `range` (R5); `HO-NA`'s deny-build reach by
  W11(a) (a hand trace); N6's row-2 reach (read from the builder's erasure bits).

## 11. Disposition table (review 2026-11-05 r5)

Ids and sections as of rev 1; rev 2 renamed the witnesses `WD*`/`W-*` to `HO-*` (§3.1's table gives
each one's rev-1 id).

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
| vlbrev2 pickups 1-10 (vlookbehind REV 2's numbering; rev 3's eleven are in §12) | applied | 1 §2.3, §3.1 (trail); 2 §3.1 (no slot, or a new one under rev 2); 3 §3.1 (K134); 4 §2.3; 5 §3.1 (the end-check is range's); 6 §3.1 reader table; 7 §3.1 composition; 8 §3.1 reader table; 9 §3.1 gate; 10 moot: Frank ruled (A), today's bytes stay |

## 12. Disposition table (re-check 2026-11-06 r1) `[r1-1106]`

Every PROPOSED disposition was ACCEPTED by the manager's RULING of 2026-11-06, with four rulings:
(1) vlookbehind owns the admission rows, this note the kind; (2) members do not wait, only a new
effect set waits for [VMREC] (c); (3) [ROWCONJ] first, the ratchet must not rise; (4) the lever is a
`--harness=` arm.

| id | disposition | where |
|---|---|---|
| A1 (sound-1) | FIX-NOW: the push on `(?<*`, not the capture-free restriction; the sweep re-run: 0 of 552,900 differ; `HO-NA`; the composition paragraph restated as every frame's continuations; the review's third cell does not reach the hole (noted) | §3.1 (records, sweep, reader table, composition, STOP RULE), REVISION 2 |
| A2 (FIX-1) | FIX-NOW: conjunct (c0), an AST bound before any NFA build, controlled by the builder's real count; optional build and retry rung argued against; `HO-N` | §2.5, §3.1 (table, P2), §4.1 |
| A3 (sound-2, FIX-4, READY-13a) | FIX-NOW: the read set clipped plus `subject_length`; `from` selects the view by position; WD8's cells; K74 named beside D142 | §2.1 (`from`), §2.3, §2.5, §3.1 (`HO-8`, gate) |
| D1 (client-1, READY-1) | FIX-NOW + ruling 1: §3.1's rows are proposals P1-P11 for vlookbehind's adopting revision; one id space `HO-*` with the vlb WD mapping; the adopting revision is an S3 prerequisite | §3.1, §4.1 |
| D2 (FIX-2) | FIX-NOW: the fields table with owners; the kit replies as a back-flowing field keeping render impure until the kit seam carries them; forward `from`/`tag`; five floor strings | §1, §2.1, §3.3 |
| D3 (FIX-5, READY-7) | FIX-NOW: the swap as a ROLE every reader uses; address tests and memos; `nedfa` in, `xprio` out; the grep recipe (160 sites); S1M cost L | §2.4, §4.1 |
| D4 (FIX-6) | FIX-NOW: instances distinct per walk in one host function; the instance → stem row | §2.1, §3.3 |
| D5 (FIX-3, READY-14) | FIX-NOW + ruling 2: the call as four members; the code-segment slot; only the effect set waits for (c), shared by three members; S3 does not wait for [VMREC] | §2.3, §4.1, §5 |
| D6 (READY-2, client-4/5/6) | FIX-NOW: rev 3's pick-ups applied (checklist below) | throughout |
| R1 (READY-5) | FIX-NOW: the oracle per `lang`; the callout form; `ovector[1]` dropped | §0 G3, §3.1 |
| R2 (READY-4) | FIX-NOW + ruling 4 + PLAN: the `--harness=` arm; GIVEUP1 already compares internal arms; [GIVEUP-DIFF]'s trigger/scope widened (PLAN, the manager's row), ONE_WAY declared on the arm's job; `HO-V` | §3.1, §4.1 |
| R3 (READY-3) | FIX-NOW + ruling 3: [ROWCONJ] an S3 prerequisite; R19 does not rise | §3.1, §4.1 |
| R4 (READY-10) | FIX-NOW: S1 owns the writer/reader and the round trip, S3 the oracle and golden hook; G2's grep and F4's round trip in both gates | §0, §2.1, §3.1, §3.3, §4.1 |
| R5 (client-2) | FIX-NOW: stage 1's witnesses and `range` fixtures on the deny arm in S3's gate, with a reach control | §3.1 (gate, P10), §7 |
| R6 (client-3) | FIX-NOW: the recorded per-branch row as the key; machine builds before the count passes | §3.1 (P8) |
| R7 (READY-6) | FIX-NOW: the rung's readers, all-or-nothing stated, a `trlowsize` witness, the rung in S3 only | §2.4, §4.1 |
| R8 (FIX-7, READY-11) | FIX-NOW (recipe words) + PLAN (roadmap §5 restatement, an S1 gate prerequisite) | §4.3, §4.1 (S0, S1) |
| N1 (FIX-8) | DOC: the caller-side restore; machines built after the mandatory ones | §2.4 |
| N2 (READY-8) | DOC: per cell, the deny-build plant or row-only; `HO-U`'s plant | §3.1 (witness table), §7 |
| N3 (READY-9) | DOC: the [VMREC] chain written; under ruling 2 it is no longer S3's | §4.1 ("S3's real wait") |
| N4 (READY-12) | DOC: S1's gate is the matrix's anchor check plus the five rows | §3.3, §4.1 |
| N5 (READY-13 b-e) | DOC: the `VK_WORK` typed operand (a member); the D27 extract; `emit_sweep.py` as the one comparator; no stamp while the lever is test-only | §2.3, §3.1 |
| N6 (client-7) | NOTED → read: `(?:)*` sets no erasure bit, so the cell reaches row 2; confirm at build | §3.1 (gate) |
| N7 | DOC: the `(?m)^` cells run today, in `HO-A` | §3.1 |

**Vlookbehind rev 3 §16c's pick-ups and the client critic's additions, as applied:**

| pick-up | applied |
|---|---|
| 1 "NOT YET RULED"; rev 2's spelling paragraph; the bracketed rev-2 entries | RULED; the paragraph is a history line; brackets gone (§3.1) |
| 2 row 4 cites rev 2 §5.1 | rev 3 §5.1 (§3.1 table) |
| 3 the finisher's operand; row 3 shares `L_try_i`/`L_body_i`/`L_end_i` | §2.3 finisher contract; §3.1 records, with the charge moved before the jumps into `L_try_i` (client-5) |
| 4 work restated | as a PER-CANDIDATE prefix inequality (client-4, which also covers early success); the false empty-candidate parenthetical removed (§3.1) |
| 5 the trail column | row 3: 0; the term per row through the recorded row (§3.1) |
| 6 V3's rule | cited as rev 3 §5.6 (§2.3) |
| 7 `VK_WORK` beside the call | citation moved to rev 3 (§2.3) |
| 8 the moving-floor member | row 3's `bound`, not range's (§5) |
| 9 soundness of row 3 | `VSK_STEP_CHAR` and the far retry named as unused; the replacing fact stated; the `$_back_step` reading of the farthest start (§3.1) |
| 10 W-trail's cell | `HO-T`: `(?<*(a{1,5}))bz` on `aaaaab` (§3.1) |
| 11 the rejected slot vs `LO_i` | stated in the history line (§3.1) |
| client-6 header, citations, §8 Q1, rev-2 pickup numbering, ill-formed UTF-8 gate cells, the trail-cycle parenthetical, the two missing reader-table columns | header (rev 3); citations moved; Q1 ANSWERED (§8); §11's last row names rev 2's numbering; `HO-U`'s ill-formed cells and the gate line; the K134 column cites rev 3's list; "matcher locals" and "seam sites" columns added (§3.1) |
