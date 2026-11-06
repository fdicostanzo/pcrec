# Review 2026-11-06 r1 — arev rev 1 (design, RE-CHECK)

**Subject.** `docs/design/stream/arev.md` rev 1, last commit `b4878cb6a` (merged on main by `0f7d79795`),
and `docs/design/stream/roadmap.md`'s A-REV area at `de551e514`. Mode: design, a RE-CHECK of the
revision that applied review `2026-11-05-r5-arev` (its RULING and OWNER ADDENDUM). Build commit
(review tree, built unlocked with `nice make -j2`): main `e20dee230`. Client in force at the freeze:
`docs/design/vlookbehind.md` **rev 3** (`febde6edd`, merged `e20dee230`, after arev rev 1), with its
§16c 11-item pick-up list for arev. Rulings frozen at `e20dee230` (decisions.md `cc7edf500`, plan.md
`0b7ee8898`). No code moved between arev's anchor commit `fd1a32021` and `e20dee230` (empty
`git diff --stat` over src/cli/lib/tests/scripts, checked by three critics).

**FREEZE DRIFT** (main at hand-back `cca7ff00b`): decisions.md D37 addendum ([FEAT-FAMILIES], not
this subject); plan.md gained **[UTF-END-ASSERT]** (K74: end-of-subject assertions at an ill-formed
UTF-8 end diverge from libpcre2, filed UNSCHEDULED 2026-11-06). That touches this subject: rows 2-3's
gate (and vlookbehind rev 3 gate 1) add ill-formed UTF-8 subjects, and A3 below adds `$`/`\z` cells at
`from`. A `$`/`\z`-at-the-cursor cell on an ill-formed subject end would meet K74 regardless of the
row; the gate should state K74 as a named class beside D142's (see A3).

**Verdict (readiness lens, verified):** NOT READY. S1 and S1M are ready WITH TEXT FIXES; S3 (the
proof step) is not ready: one answer-level hole (A1), one optimization-added refusal (A2), an owner
document that contradicts it (D1), and its gate's units unowned (R-group). Every item is a text fix
plus four manager rulings (listed at the end). No finding argues against the hand-off's direction.

## RULING (manager, 2026-11-06)

Every PROPOSED disposition is ACCEPTED (FIX-NOW A1, A2, A3, D1-D6, R1, R3-R7, and R2/R8 text). Verdict accepted: NOT READY; S1 and S1M ready with text fixes, S3 (the hand-off proof step) not. The four asked rulings, all manager's: (1) OWNERSHIP: docs/design/vlookbehind.md owns lookbehind's admission rows (the reverse-dfa candidate source included); arev.md owns the automaton kind, its exits, record and host. arev's row proposals are adopted into vlookbehind when the proof step is designed for build (a vlookbehind revision at that time), not now. (2) VK_AUTO is spelled as new MEMBERS of existing closed lists where it can be (manager ruling 2026-11-06: members do not wait); only a genuinely new effect set waits for [VMREC]'s stage (c). (3) [ROWCONJ] goes first rather than R19 +1: the ratchet must not rise. (4) The lever is a --harness arm (memory pcrec-flag-follows-caller-effect: wrongness risk gets a test-only lever). Process change adopted: when a design removes a frame push, the soundness lens lists every path that frame's pop reaches (later branches, the next row), not only the removed piece's own retries (critic skill §4).

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| fix-induced (`fix`) | opus | Each piece rev 1 ADDED (DfaForm-made record, `VK_AUTO`, S1M table, rung, `has_bot` order, ratchet R28'/R03'/R10'): what read/hand/row/slot/storage does it add, does it hold in today's code? + seam round trip | a RE-CHECK of a revised design (skill §4) |
| soundness (`sound`) | opus | Apply rows 2-3 LITERALLY, composed with today's `vm_look` and rev 3's cursor-rung `range`, over multi-branch witnesses on all three forms: does any answer move vs libpcre2? | a claim of answer identity by proof; pseudo-code over real primitives |
| premise / client in force (`client`) | opus | Does every client-dependent sentence hold under vlookbehind REV 3 (the 11 pick-ups and the ones §16c missed); anchors at the build tree; evidence re-run | r5 lesson: the client moved after the subject was written |
| readiness (`ready`) + ruling check + owner criteria + standing questions (sibling of a family; general form + unlocks) | opus | Per build unit of S1, S1M, S3: cites, can-fail witnesses (both builds), separability, completeness; overall verdict | the proof step is ruled by the owner; next is a build go |

Verifier: one opus agent over every CONFIRMED finding that would change the design (16 ids): 14
HOLDS, 1 PARTLY (READY-4), 0 REFUTED; client-3's pass-order consequence not verified.

## Which lens caught what

- `sound` alone caught the answer-level hole (A1), by a 552,900-cell sweep of a literal model
  (1,702 diffs, all `(?<*`; the rev 3 `cursor` control 0). The coordinator had recorded the same
  suspicion while profiling (`.coord/suspicions.md`, `(?<*b{1,2}|(ab))(?(1)y|z)` on `aby`), kept out
  of every brief; the critic found it blind.
- `fix` alone caught the NFA-cap refusal (A2), the record's missing fields and render-time writes
  (D2), the swap's identity readers (D3), the label-stem collision (D4) and the kind-vs-members
  reading of `VK_AUTO` (D5).
- `client` and `ready` both caught the two-owner-documents problem (D1) and the unapplied pick-ups
  (D6); `client` alone the stage-1 witness reach loss (R5) and the predicate-vs-row key (R6).
- `ready` alone caught the gate units (oracle, lever, GIVEUP-DIFF, ROWCONJ, golden check) and the
  VK_CALLOUT precedent (D5).
- `sound`, `fix` and `ready` each caught the part's read-set edges (A3).

## Findings (consolidated; every lens that found it named)

### Answer level

**A1 — row 2 (`AUTO EXISTS`) on the NON-ATOMIC form drops every later branch** (sound-1; verified
HOLDS). arev §3.1 "Row 2, per branch i: the guard, the call with bound = 0, t < 0 → L_b_(i+1), else
goto L_ok" pushes no frame; in today's wiring the ONLY path from branch i to branch i+1 after branch
i's guard is the frame branch i pushes (emitted C of `(?<*ab|(c))x\1`: `rx_L7` has exactly two
references, the guard skip and `RX_PUSH(&&rx_L7, …)`). So on `(?<*`, a later capturing branch is
never tried after a failing follow. Cells (libpcre2 10.46 vs the literal design):
`(?<*a{1,2}|(a))b\1` on `aaba` [2-4,1-2] vs nomatch; `(?<*a{1,2}|(a{1,2}))b\1` on `aabaa` [2-5,0-2] vs
nomatch; `(?<*a{1,2}|(b))x\1` on `abxb` [2-4,1-2] vs nomatch. The "Composition with `vm_look`"
sentence ("every retry ends at the same cursor with the same groups") is true for the row-2 branch's
own retries only; the cited vlookbehind_pieces §3 evidence is capture-free for the WHOLE lookbehind.
The STOP RULE paragraph inherits it. Atomic/negative forms and row 3 are unaffected (0 diffs).
- **PROPOSED FIX-NOW.** Row 2 on `(?<*` pushes `RX_PUSH(&&L_b_(i+1))` before `goto L_ok` (the
  one-length row's own frame; frames +1, trail 0; the sweep with this fix agrees on all 1,702), OR
  admits row 2 on `(?<*` only when every later branch is capture-free. Leaning: the push (one rule,
  no new conjunct; the reader table's row-2 push count becomes "1 on `(?<*`"). Add witness WD-NA
  (the first cell; plant: row 2 with no frame). Restate the composition paragraph.

**A2 — the per-branch reverse NFA build can REFUSE the compile where `range` alone compiles**
(FIX-1; verified HOLDS). Conjunct (c) needs the branch's reverse NFA BUILT, and `pcrec_build_nfa` has
no optional mode: `nst` (src/ir/nfa.c:146-156) calls `pcrec_ctx_fail` at `PCREC_MAX_NFA_STATES` =
131072 (limits.def:160); only the DFA has `d->optional`. Today's NFA erases the lookbehind body
(nfa.c:759), so no NFA ever sized it. `\p{L}{255}b` under `-e utf8` refuses ("NFA exceeds 131072
states") while `(?<=\p{L}{255})b` compiles; libpcre2 accepts `(?<=\p{L}{1,255})b` (255 is its
variable-lookbehind ceiling). Once `range` ships, the row's admission turns that pattern into a
refusal: an optimization-added refusal (D158), which the gate's "no answer moves" forbids.
`dfa_overflowed` is not set on this path, so no retry rung catches it.
- **PROPOSED FIX-NOW.** A conjunct (c0) before (c): an NFA-size precheck on the AST, or an optional
  NFA build that records instead of failing; its decline goes to `range`. Witness: the cell above,
  plant = the precheck dropped (a refusal). §2.5's "the order is the fix for F2" sentence gains
  "and no NFA build is mandatory".

**A3 — the part's declared effects and its right-context reading are wrong at the edges**
(sound-2, FIX-4, READY-13a; verified HOLDS as a doc/witness gap). §2.3 "reads
`subject[bound − 1 .. from]`" names `subject[-1]` at row 2's `bound = 0` and `subject[n]` at
`from == n` (today both reads are guarded, emit_dfa.c:9318-9332 and the reverse `seed_cond`), and
omits `subject_length`. §2.5 "`$`, `\Z`, `\z` … at the cursor are RIGHT-context rows, read from the
byte at `from`" does not decide `$`/`\Z` (need `from == n` or `from == n − 1` with `s[from] == '\n'`)
or `\z` (no byte). Cell for a byte-keyed part: `(?<=a{1,2}$)\nb` on `aa\nb` libpcre2 nomatch; a
"`s[from]` is `\n`" reading says yes. WD8's three cells cannot fail under that plant. The DFA already
has the eol/end position views (dfa.c:1430-1432); the record does not name the choice.
- **PROPOSED FIX-NOW** (text + two cells). Clip the read set (`subject[max(bound,1)−1 ..
  min(from+1,n)−1]` plus `subject_length`), state that `from` selects the base/eol/end view by
  position, add `(?<=a{1,2}$)\nb`/`aa\nb` and `(?<=a{1,2}\z)\n`/`aa\n` to WD8. Name K74
  ([UTF-END-ASSERT], FREEZE DRIFT) as a stated class beside D142's in the gate for any end-assertion
  cell on an ill-formed subject end.

### Design level (S3's client and host)

**D1 — two owner documents state the hand-off row differently; rev 3 adopted none of arev's five
proposals** (client-1, READY-1; verified HOLDS). arev §3.1 calls its differences "PROPOSALS to the
client's owner document". vlookbehind rev 3 §5.4 still reads "Exactness is read from `Nfa.erased ==
0`" (no `has_bot`, no `lang` anywhere in rev 3), lists [LANDWALK-VM] as a prerequisite, keeps the
D77 trigger and "Stage 3 (HELD)", and its §7 "Stage 3's witnesses" WD1-WD6 reuse arev's ids for
DIFFERENT cells. §16c's pick-up list runs one way only. A lane given "build S3" that opens the owner
document gets r5's F1/F2 back (a `\G` subset machine; a `^` internal-error refusal).
- **PROPOSED FIX-NOW + a manager ruling: which document owns the row** (admission, witnesses,
  prerequisites, trigger). Leaning: arev §3.1 owns the hand-off row (the owner ruled it the stream
  proof step); vlookbehind's next revision replaces its §5.4/§6 stage 3/§7 stage-3 witness list by a
  pointer, and one witness id space (arev's). Until then arev states that §3.1 supersedes vlb §5.4
  for the hand-off.

**D2 — the record is not closed, and rendering is not pure today** (FIX-2; verified HOLDS).
`DfaForm` (emit_dfa.c:5861) carries fields §2.1 does not state: `cx`, `p`, `pf` (chosen only when
`d == &cx->job->dfa`), `us` (borrowed by pointer through render), `views`/`viewsel`/`src`, `cand`,
`ofs`, `ofs_site`, `pf_find`, `pf_stem`, `landing`, `accv`. Two are WRITTEN during rendering (`f->
pf_find = find_define(…)` :7178, `f->ofs_site = ofs_site_define(…)` :7650) and read later
(:7527, :7976). Caller overrides §2.1 cannot express: `fwd.from = pcrec_emit_req_byte_check(…)`
(:13723, a C string returned after printing), `av.from = "lmwalk_start"` (:14439), `pf_stem =
"%s_pf"` of the host function (:13690, :14280, :14449), FORWARD/ANCHORED tags `forward_dist`
(:14158) / `anchored_dist` (:14658) though §2.1 has no forward column while S1 covers forward walks,
and the start-analysis input override (:14265). `DfaDir` objects differ in indent, `range_guard`,
`dead_entry` and prose, and the floor is also spelled in `seed_cond`/`at_bound`/`scan_more`, not only
in the two printers §1/§3.3 name. The seam round trip is therefore NOT reachable from §2.1 as listed.
- **PROPOSED FIX-NOW** (design text, S1's unit). Extend §2.1 with: host name; nesting/indent (the
  container's); the start-analysis facts as a recorded plan output (or `us`); the kit's define
  replies as a declared BACK-FLOWING field (F4); per-entry prose (the machine entry's);
  forward/anchored `tag`; forward `from` references (`SEARCH_FROM`, the req-byte hand-off,
  `LMWALK_START`); `range_guard`/`dead_entry` as hands. State which of them keep render impure until
  the kit seam carries them (D157: facts, not methods), and list all five floor strings for S1.

**D3 — S1M's "a form decision ADDS entries, never swaps" moves bytes unless the swap becomes a ROLE
every reader uses; two machines are missing** (FIX-5, READY-7; verified HOLDS). `revend_choose_form`
(compile.c:568-592) swaps five pairs, NFAs included. Readers keyed on the SLOT: `if (d ==
&cx->job->dfa)` (emit_dfa.c:12996, NEXT prefilter row vs fallback) and `.forward = d ==
&cx->job->dfa` (:9179); memos keyed on the plain slots' contents (lmwalk.c:318-324, known.c:395-399).
As separate entries, the lowered forward machine fails both identity tests on tagged artifacts.
Reader sites: `job->dfa` 45, `->nfa` 25, `->adfa` 24, `->rdfa` 19, `->rnfa` 5. §2.4's list also
omits `Job.nedfa` (the mandatory [FINDALL-NEXT] retry machine) and `Job.xprio` (`mark_prio`'s probe).
- **PROPOSED FIX-NOW** (S1M text). "The live forward machine" is a ROLE lookup through which every
  reader goes (the swap re-expressed, not removed); the two identity tests become role tests; the
  memos re-key; `nedfa`/`xprio` in or out with the reason; the reader set given as a grep recipe.
  S1M's cost likely above "M": restate.

**D4 — W1 and W2 share (machine R, instance 0) but emit two label stems in ONE function** (FIX-6;
verified HOLDS). `emit_rev_end` renders "revend" (:14317; tagged :14090-14091) and then, on the
relocate arm, RECOVER's "reverse" on the same form (:14364 → :13625). §2.1 derives stems from
(entry, instance), which yields one. Either duplicate labels (a gcc error) or a moved stem (S1's 0
movers broken).
- **PROPOSED FIX-NOW** (S1 text). Instances are distinct per walk within one host function; a
  declared instance → stem row reproduces today's "revend"/"reverse"/"landmark".

**D5 — `VK_AUTO` as a new KIND is a choice, not a necessity; and the in-body call to a file-scope
function already has a precedent and a slot** (FIX-3, READY-14; verified HOLDS on the facts).
(a) The call has no control of its own (vm_stmt.h:7-11: free text is a VALUE fragment), so it
composes from existing kinds: `VK_LSET` `VLO_ASSIGN` into a new `VmLocalKind` member, `VK_BRANCH` on
`t < 0`, a cursor write through a new `VmSeekKind` member ("`scan_position = <local>`"; the verifier
found this one, today's four members are slot-restore, advance, back-step, span commit), and the call
as a `VP_AUTO` piece beside `VP_KIT`. Under the manager's 2026-11-06 ruling (new MEMBERS do not
wait), S3's VM half would not wait for [VMREC] (c); only the declared effect set does
(vm_stmt.h:24-26 reserves read sets for (c)). §2.3's `VK_AUTO` writing `scan_position` also
overlaps `VK_SEEK`'s one-writer ownership. (b) `VK_CALLOUT` (vm_stmt.c:710) already calls a
file-scope function from the body, and `pcrec_emit_code_protos` (emit_code.c:142, called at
emit_vm.c:14187 "before the function whose call sites name them") is its slot. With kit windows
(opaque, declared effects), callouts/code segments and the part, this is the THIRD member of "an
in-body call to a separately emitted unit": past the unify-at-the-third threshold.
- **PROPOSED FIX-NOW + a manager ruling.** §2.3 states the composition (LSET + BRANCH + SEEK over a
  `VP_AUTO` piece, three new members) or argues why a kind is needed; the part reuses the
  code-protos slot mechanism or argues why not; one effect-set declaration shared by the three
  members, waiting for (c). Ruling asked: under the members ruling, does S3's [VMREC] prerequisite
  shrink to "(c) for the effect set only", or does the manager keep S3 behind (c) as a whole?
  Note READY-9 either way: plan.md orders [VMREC] (b), a soundness round and (c)'s own D27 author
  before (c), so "(c)" understates S3's real wait; write the chain.

**D6 — rev 3's 11 pick-ups are not applied, plus rev-2 dependencies §16c missed** (READY-2,
client pick-up table, client-4, client-5, client-6; doc). `client` classified all 11 against rev 3's
body: 1, 9, 10 need wording; 2, 6, 7 citation only; 3 holds for `L_body_i`/`L_end_i` but "exactly
row 3's" `L_try_i` is false until row 3's `VK_WORK` moves before the jumps into `L_try_i`
(client-5); 4's arithmetic HOLDS (a prefix-inequality model over 8,583,480 cells, 0 violations: the
argument CAN stay per candidate, restated as a prefix inequality, which also covers early success),
but "the empty candidate charges nothing, as range's `d = 0` candidate does" is false under rev 3
(range's step charges 1, client-4); 5, 8, 11 hold. Missed by §16c: the header's "client in force rev
2"; every "rev 2 §…" citation; §8 Q1 (answered); rev 2's pickup numbering; line 452's "[lo_i,
min(hi_i, cursor)]" (refuted under UTF-8 by rev 3 §5.1a; conclusion unaffected); no ill-formed UTF-8
cells for rows 2-3 in the gate; the trail-cycle parenthetical narrower than rev 3 §5.1b; the reader
table lacks rev 3's "matcher locals" and "seam sites" columns.
- **PROPOSED FIX-NOW** (arev rev 2: apply all, with `client`'s table as the checklist).

### Readiness of the proof step's units

**R1 — the per-part oracle is wrong for every `superset` part and partial for `same`** (READY-5;
HOLDS). For `superset` the part legitimately returns a start libpcre2 rejects (the note's own
`(?>ab|a)b{1,2}` example accepts at 0); the contract is one-sided (true starts ⊆ the part's accepts).
"Comparing `ovector[1]`" sees only the priority end (`a|ab` on `ab` → [0-1], while a correct part
answers 0 for `from = 2`). **PROPOSED FIX-NOW:** the oracle per `lang` (`same`: equality via the
callout form; `superset`: containment); drop `ovector[1]`.

**R2 — the lever and [GIVEUP-DIFF]'s coverage** (READY-4; PARTLY). REFUTED part: a test-only lever
mechanism exists and rides `make test-axes` (tests/axes/run_axes.sh:1682 `INTERNAL_ARMS=("--harness=
no-compound" "--harness=pres-window")`, the `PcrecHarnessOptions` levers in cli/CLAUDE.md). HOLDS
part: [GIVEUP-DIFF]'s direction rule reads a LOCATE row's `.giveup` classification and its trigger
names locate_finish L3-L5 / [LANDWALK-VM]; the lookbehind row is not a LOCATE row and no ONE_WAY
witness is named. **PROPOSED FIX-NOW + PLAN:** spell the lever as a `--harness=` internal arm (or
argue a public flag), add the row to [GIVEUP-DIFF]'s trigger and scope, declare its ONE_WAY
classification's home, name the budget witness (range gives up, row 3 answers; e.g. W12(a)'s shape
under `--work-budget`).

**R3 — "R19 does not rise ([ROWCONJ]'s conjunct type)": the type does not exist** (READY-3; HOLDS).
[ROWCONJ] is `STATE:not-started`; `grep RowConj src` is empty; R19 counts private conjunct structs
(3). Rows 2-3's five conjuncts would be a fourth. **PROPOSED FIX-NOW + a manager ruling:** [ROWCONJ]
as an S3 prerequisite, or R19 +1 with its named deletion.

**R4 — no unit owns the record's text form, the golden check or the oracle; the gates omit two of
§0's checks** (READY-10). **PROPOSED FIX-NOW:** S1 owns the record writer/reader and the round
trip, S3 the part oracle and the golden-check hook; S1's and S3's gate cells add G2's grep and F4's
round trip.

**R5 — S3 takes stage 1's own `range` witnesses and its codegen fixture off `range`** (client-2;
HOLDS, counts inferred). With rows 2-3 default-on, W2, W3b, W4, W7, W11, W12(a/b), W13, W16 (row 2)
and W1, W5, W6, W13, W15, W14's Kelvin cell (row 3) leave `range`; the `residlbrange` fixture's
back-step count drops to 1, so `run_codegen_tests.sh` is red at S3's landing and S133/S134's anchors
are not emitted. **PROPOSED FIX-NOW:** S3's gate runs stage 1's witness rows and `range` fixtures with
the row's lever DENIED (or re-aims them to declined bodies), plus a reach control per row
([MECH-REACH]).

**R6 — rev 3's "one predicate on the stored pair, read by every pass" must become the recorded
per-branch ROW** (client-3; text HOLDS, pass order not verified). Otherwise a row-2/3 branch gets an
unused `LO_i` slot and labels, and families above `low` shift. Conjuncts (d) and `lang` are read after
a machine build, so the per-branch build must precede `vm_count_slots_look`/`vm_cost_look`.
**PROPOSED FIX-NOW** (text: the key change and the ordering constraint).

**R7 — the size-cap rung's readers and witness** (READY-6). Readers outside H-LADDER's shape:
`docs/spec/limits.md` §8.4's rung table (public-flag column), `docs/spec/tuning.md`'s rung-order
sentences, `tests/codegen/run_fallback_table.sh`, `S238_size_drop_unstamped.sh` (+ an S1826 twin),
`src/dump/axes_dump.c`. One `fit_fired` bit makes the rung all-or-nothing per artifact (`fix`
PROBED: acceptable, should be stated). **PROPOSED FIX-NOW:** list the readers, a `trlowsize` witness,
the rung in ONE unit (S1M or S3, not both).

**R8 — ratchet recipes: right counts, fragile words; the rows do not exist yet** (FIX-7, READY-11).
Recount at `e20dee230` agrees: R28' 5, R03' 3, R10' 1. Fragility: R10''s `while (` matches the
`do { } while (0)` scaffold (:14504) and "lines of its body" zeroes on a helper extraction; R28' (i)
says "objects" while a forward declaration (:7106) makes a line grep read 6, and its literal "− 3"
rises on a legitimate new direction; R28' (ii) zeroes if the two direct sites route through
`emit_reverse_block` with a flag. roadmap §5 has no R28 and R03/R10 keep old recipes. **PROPOSED
FIX-NOW** (recipe words: loop constructs in the registered emitter AND its static callees;
"definitions"; directions counted from the direction table) **+ PLAN** (the manager's roadmap §5
restatement is a prerequisite of S1's gate).

### Doc level

- **N1 FIX-8** (DOC): the subset-budget restore is `lmwalk_build`'s/`revend_build_marked`'s (callers),
  not `revend_build_one`'s; §2.4 names the caller-side restore and builds the lookbehind machines
  AFTER the mandatory ones (dfa.c:1316-1321; that comment is itself stale against the two callers).
- **N2 READY-8** (DOC): "every cell can fail in both builds" is false for WD1 rev 1's pair, WD-A
  positive, the WD-B control, both WD6 cells and WD8's `\b` cells (no stage-1 plant reaches them;
  they are reverse-machine hazards); W-UTF names no plant. Per cell: name the deny-build plant or
  mark "row-only (deny build: control)"; give W-UTF a plant (the part accepting mid-character).
- **N3 READY-9** (DOC): the [VMREC] chain (b) → soundness round → D27 → (c) written out (see D5).
- **N4 READY-12** (DOC): S1's gate phrased as "the sabotage matrix's anchor check: 0 missing anchors;
  the five named rows also DETECTED" (36 emit_dfa.c sabotages name an S1-touched token).
- **N5 READY-13 b-e** (DOC): `VK_WORK`'s operand is C text, a typed operand is a new MEMBER (unlisted);
  no D27 extract named for S3; the byte comparator instrument unnamed (emit_sweep.py vs
  run_recursion_identity.sh); stamp vs lever hunk (vlookbehind §10 owes a stamp).
- **N6 client-7** (NOTED, SUSPECTED): `(?<=(?:)*a{1,2})x` is capture-free, so by the table it reaches
  row 2, not row 3 as §3.1's gate says; confirm at build.
- **N7 WD-A's `(?m)^` cell** (sound PROBED): runnable today through the probe's `x` mode
  (`(?<=(?m)^a{1,2})b` on `c\naab` [4-5]); "owed by the build's harness" can be replaced by the cell.

## PROBED-AND-HELD (summary; full lists in each critic file)

- `sound`: 552,900 cells literal rows 2/3: every `(?<=` and `(?<!` cell = libpcre2 (row mixes,
  erased atomic and lookahead branches, `\b` both ends, lazy, nested `(?<=b)`); F1, F2 (declined
  before the build, so dfa.c:1583 unreachable), F3/WD-B, WD1, WD2-WD5, W-restore all hold; no
  narrowing outside `pcrec_nfa_has_bot` found; UTF-8 and MATCH_INVALID_UTF shapes hold (pcrec's
  byte machine strict, = libpcre2 on surrogate/overlong cells); row 3's work ≤ range's.
- `fix`: 24 cited lines hold; `pcrec_nfa_has_bot` callable on a per-branch NFA; conjunct (b) screens
  the AST arms that longjmp; storage: rows 2-3 add no frame/trail sizing beyond stage 1's (row 2
  over-counted safely by range's charge; changes with A1's push, still ≤ range); `fit_rungs[]`
  append shape exists; `dfa_member_machines` 3 readers; ratchet counts recount exactly.
- `client`: 16/16 pick-up citations land on the quoted text; 69 premise anchors re-grepped,
  unchanged; 37 byte + 3 UTF cells re-probed = premise.out; roadmap A-REV agrees with arev rev 1.
- `ready`: 40 symbols, 26 line anchors, 10/10 sabotage witnesses and every cited plan row exist;
  the gate harness exists; 13 cells reach their default-build plant by hand trace; the general
  form (a CONTRACTED PART CALLED FROM A HOST PROGRAM) with five unlocks and triggers (ready.md
  PROBED, "Standing Q2").

## By-id completeness

| id | consolidated as | verify | proposed |
|---|---|---|---|
| sound-1 | A1 | HOLDS | FIX-NOW |
| sound-2 | A3 | HOLDS | FIX-NOW |
| FIX-1 | A2 | HOLDS | FIX-NOW |
| FIX-2 | D2 | HOLDS | FIX-NOW |
| FIX-3 | D5 | HOLDS (+ a VmSeekKind member) | FIX-NOW + ruling |
| FIX-4 | A3 | (under sound-2) HOLDS | FIX-NOW |
| FIX-5 | D3 | HOLDS | FIX-NOW |
| FIX-6 | D4 | HOLDS | FIX-NOW |
| FIX-7 | R8 | not sent (counts recounted by two lenses) | FIX-NOW + PLAN |
| FIX-8 | N1 | HOLDS (lines off by one) | DOC |
| client-1 | D1 | HOLDS | FIX-NOW + ruling |
| client-2 | R5 | HOLDS (counts inferred) | FIX-NOW |
| client-3 | R6 | HOLDS (text; order not verified) | FIX-NOW |
| client-4 | D6 | not sent (doc) | FIX-NOW (with D6) |
| client-5 | D6 | not sent (doc) | FIX-NOW (with D6) |
| client-6 | D6 | not sent (doc) | FIX-NOW (with D6) |
| client-7 | N6 | SUSPECTED, not sent | NOTED |
| READY-1 | D1 | HOLDS | FIX-NOW + ruling |
| READY-2 | D6 | not sent (doc) | FIX-NOW |
| READY-3 | R3 | HOLDS | FIX-NOW + ruling |
| READY-4 | R2 | PARTLY | FIX-NOW + PLAN |
| READY-5 | R1 | HOLDS | FIX-NOW |
| READY-6 | R7 | not sent (doc) | FIX-NOW |
| READY-7 | D3 | (under FIX-5) HOLDS | FIX-NOW |
| READY-8 | N2 | HOLDS | DOC |
| READY-9 | N3 / D5 | not sent (plan text quoted) | DOC |
| READY-10 | R4 | not sent (text) | FIX-NOW |
| READY-11 | R8 | not sent (roadmap text) | PLAN |
| READY-12 | N4 | SUSPECTED, not sent | DOC |
| READY-13 | A3 (a), N5 (b-e) | (a) under sound-2 | FIX-NOW (a) / DOC |
| READY-14 | D5 | HOLDS on the fact | FIX-NOW + ruling |

## Rulings asked of the manager (plain words)

1. **Which document owns the lookbehind hand-off row** (D1)? Leaning: arev §3.1, with vlookbehind's
   stage-3 text replaced by a pointer at its next revision and one witness id space.
2. **Does the hand-off's VM half still wait for [VMREC]'s analysis stage as a whole** (D5)? It can
   be spelled with three new members of existing lists (a local, a cursor-write form, a piece), which
   the 2026-11-06 members ruling lets proceed; only the declared effect set needs (c). Leaning:
   spell it as members, keep only the effect-set declaration behind (c), and write the full [VMREC]
   chain into S3's prerequisites.
3. **The conjunct list for rows 2-3** (R3): build [ROWCONJ] first, or accept R19 +1 with its
   deletion named. Leaning: whichever the [ROWCONJ] row's own schedule makes cheaper; the note must
   say which.
4. **The row's lever** (R2): a `--harness=` internal arm (exists, rides test-axes) unless a regime is
   slower after narrowing. Leaning: the harness arm, and [GIVEUP-DIFF] widened to name the row.

A D27 spec-first author for S3 is already among S3's prerequisites; keep it, and give it an extract
(N5).

## Lessons for the guide (proposed)

- **A frame the design REMOVES is a path, not only a retry** (A1). When a row elides a frame, list
  every continuation that frame's pop reaches (later branches, later candidates, the next row), not
  only the retries of the elided piece; "unobservable because capture-free" must hold for every
  continuation's body. Proposed for `docs/dev/guide/critics.md` "Lessons" and the soundness lens.
- **A conjunct that needs a build must name that build's own failure mode** (A2): an admission test
  run on an intermediate (an NFA here) inherits that builder's mandatory caps; "decline, never a
  refusal" is checked per builder, not only for the final machine.
- **Proposals to a client document need a carrier back** (D1): when a subject proposes changes to a
  client's owner document, the round checks the client's CURRENT text adopted them; a one-way pick-up
  list is a finding.
