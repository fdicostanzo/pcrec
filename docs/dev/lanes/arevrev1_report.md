# Lane arevrev1 — A-REV design rev 1 (review 2026-11-05 r5 applied)

Lane arevrev1, opus, 2026-11-05/06. Branch `lane/arevrev1` from main `fd1a32021`. TEXT ONLY: no
edits under src/, cli/, lib/, memfn/ or tests/. Subject: `docs/design/stream/arev.md`, now
**PROPOSED rev 1**, and the matching A-REV area of `docs/design/stream/roadmap.md` (its §1 row and
`### A-REV`). Applies the RULED review `docs/dev/reviews/2026-11-05-r5-arev.md` (every disposition
ACCEPTED, the manager's RULING block, the OWNER ADDENDUM of 2026-11-06), read in full with every
critic text and `verify.md` in its directory. Evidence: `docs/dev/lanes/arevrev1_evidence/`
(`premise.out`, `cells.txt`).

## Premise test (the brief's)

- **F1's cell reproduces** with libpcre2 10.46 as a library (vlbrev1's `probe.c`):
  `(?<=\Ga{1,2})b` on `aab` gives (2,3) from offsets 0 and 1 and nomatch from 2;
  `(?<!\Ga{1,2})b` gives nomatch, nomatch, (2,3). On `caab` from 1: (3,4) / nomatch.
- **The four walks' anchors were re-grepped at fd1a32021** and did not move from the review's
  freeze: `unanch_scan` :13495 (four callers), `emit_scan_loop` :13244, `emit_reverse_block` :13409
  (three callers :13625, :14317, :14489), the direct `emit_scan_loop` reverse sites :14054 / :14116,
  `emit_rev_end` :14229, `emit_landmark_walk` :14398, the five `static const DfaDir` objects
  :9340-:9460 and the run-time copy in `pcrec_emit_dfa_retry` :14700, `dir_rev_bound_accept` :9297,
  `dir_rev_skip` :9249, `dfa_form_derive` :12962, `Rev` emit_vm.c:5500, `vm_rev_emit` :5521,
  `vm_revdet_rep` :5705, `pcrec_nfa_has_bot` nfa.c:1342, `revend_build_one` compile.c:454,
  `fit_rungs[]` :1309. One correction to the review's text: the `CT_*` masks are in
  src/gen/emit_dfa.c (:9882), not `internal.h`.
- **Other cells measured** (premise.out): F2's `(?<=^a{1,2})b` (2,3); F3's `(?<!a{1,2}|b)x` / `bx`
  nomatch and `(?<=a{1,2}|b)x` (1,2); a variable-branch atomic counter-example
  `(?<=(?>ab|a)b{1,2})x` on `abx` nomatch (non-atomic twin (2,3)); the right context at the cursor
  (`(?<=a{1,2}\b)x` / `aax` nomatch, `(?<=a{1,2}\b)-` / `aa-` (2,3), `(?<=a{1,2}$)` / `aa` (2,2));
  branch order with varying branches `(?<=(a{1,2})|(aa{1,2}))c` / `aaac` [3-4, 1-3]; the
  non-atomic retry `(?<*(a{1,2}))b\1c` / `aabac` [2-5, 1-2]; the restore cell
  `(?<=(?>ab|a)b{1,2}|ab)x` / `abx` (2,3); UTF-8 `(?<=(é{1,2}))x` / `aééx` g1 = (1,5). The `(?m)^`
  cell needs a newline in the subject, which the line-based probe cannot carry: NOT RUN, owed by
  the build's harness.

## What changed (by finding; the note's §11 is the full map)

- **The owner's ruling.** §3.1 is now the lookbehind HAND-OFF as a stream PROOF step: per-branch
  rows `reverse-dfa` existence (`AUTO EXISTS` when `lang = same` and the branch has no group) and
  `reverse-dfa` candidates (`AUTO ENUM`, each confirmed by the forward body run and range's
  end-check), one D186 choice row against `range` with the exit decided by a fact (F29). No speed
  trigger (F25); the gate is "no answer moves, nothing slower" over vlookbehind §5.4's four
  regimes. Rev 0's `gate` row is a later option; rev 0's HELD `commit` row is gone (it IS the
  hand-off).
- **F1, F2.** The admission gains `!pcrec_nfa_has_bot` on the branch's reverse NFA, tested BEFORE
  the subset construction (§2.5): `\G` makes the reverse machine a subset; `^`/`\A`/`(?m)^` make
  the build a longjmp refusal. Witnesses WD-G and WD-A.
- **F3.** A branch's NO_ACCEPT sends the next branch from the cursor; only ACCEPT answers (§2.2,
  §3.1, WD-B).
- **F4.** "Exact" is replaced by one fact read after the build, `lang = same | superset`; the build
  request names `collapse` and `prune` (§2.4, §2.5); the word avoids the VM stamp's "exact".
- **F5.** The client in force is vlookbehind rev 2 (+ vlookbehind_pieces rev 0). Rev 1 adopts
  rev 2 §5.4's one row, its exits, its "no side-effecting construct" conjunct and its floor 0 (the
  `max(0, cursor − W)` refinement is unnecessary because the row never requests `collapse`, so
  every admitted machine's lengths are in `[lo_i, hi_i]`). Each difference is a proposal to the
  client (§3.1 list: has_bot and its order; `lang`; the verdict wording; the cursor-rung spelling;
  [LANDWALK-VM] and P-d read as not prerequisites, with the reason). [LB-EXIST] is recorded as filed.
- **F6-F13 (today's code).** §1 rewritten at fd1a32021: W1 is `unanch_scan` with four callers and
  no tag of its own (the `accv` set is the forward form's); W2 is `revend_forms[]`'s forms, two of
  which bypass `emit_reverse_block`; W2 never reads `xrdfa` (the driver swaps); the literal
  `search_from`/`rewind_position` in two printers (S74 is re-aimed in S1); W4's step vs its loop;
  `vm_charge` is the compile-time node cap and revdet's walk has no run-time charge.
- **F14-F16 (the record).** One direction-neutral record, `DfaForm` made into it (not a third
  descriptor): typed position references for `from`/`bound`, a hand map over {DEAD_ENTRY,
  NO_ACCEPT, ACCEPT(pos[, tag])}, tables owned by the machine-table entry, label stems by
  `instance`, the form's selected rows recorded as plan outputs (the review's leaning), back-flowing
  facts (tag encoding, tie, empty-at-n, `lmwalk_reach`) declared (§2.1, §2.3).
- **F11.** ONE walk behaviour, `farthest` above a bound. Existence = "an accept exists";
  enumeration = re-walk with `bound = CANDIDATE + 1`. Rev 0's `first` needed new loop emission and
  is dropped (an early stop is HELD).
- **F17.** The exits are roadmap §4's suffixes (`AUTO COMMIT/ENUM/EXISTS/GATE/TAGGED`), which are
  ruled the home; the hands are spelled in the existing `CT_*` masks (R12 does not rise); `exist`
  is `AUTO EXISTS` tied to row 12; `seed` now has no second meaning (`from` is the start).
- **F18.** `repr` renamed `rendering`, the output of a declared row table; the prefix-shape tiers
  are not rendering rows.
- **F19, F21.** The walk is a file-scope PART emitted by the plan in its own slot; `VK_AUTO` is an
  in-body CALL record (part id, `from`/`bound` references rendered as values, result destination,
  hand map, declared effects). `host` is split into `placement` and `container`; `charge` is
  dropped in favour of a `VK_WORK` record.
- **F20, F22.** One machine table for EVERY machine (H-FLAGS's machine half), the lookbehind's
  per-branch need argued as H-FLAGS's trigger, built as its own byte-identical step S1M; the
  lowering is a table fact (no swap, entries immutable); the part header is named (not
  `internal.h`); the lookbehind's machines get a `fit_rungs[]` rung in H-LADDER's append shape.
- **F23.** Recipes restated by what they count (§4.3): R28' = 5, R03' = 3, R10' = 1 at fd1a32021.
- **F24.** §0 rewritten against F1 > F2 > F3 with F4 as a constraint and the gate apart; each with
  a checkable form; the record-in/text-out golden check and a per-part oracle (libpcre2 anchored at
  `s` with its end at `from`) are named as owed (neither exists); G4's caller-visible listing is
  NOT claimed (an interface change, [IFACE-PUSH]).
- **F26.** S3 waits for [VMREC] (c) (manager ruling); S2 named as a ride-along [VMREC] may carry.
- **F27, F28.** Questions for Frank in the note (§8); a COST column on every step.
- **vlbrev2's ten §5.1 pickups**: all applied (§11's last row). The decisive one for the hand-off is
  pickup 1-3: under rev 2's spelling the hand-off needs a trailed candidate-position slot that no
  existing family describes, plus a trail term and a K134 checkpoint per branch; under the
  cursor-rung spelling it needs NO slot and adds nothing to the trail term.

**What changes if the cursor-rung spelling is adopted** (vlookbehind_pieces' recommendation, NOT
YET RULED): §3.1 is written in that spelling and states rev 2's alternative beside it. Adopted: the
hand-off rows have no slot, trail term unchanged, a K134 checkpoint only where the body writes the
trail, exhaustion restores the cursor by one `VSK_RESTORE` (witness W-restore), and W-trail is the
check. Not adopted: a trailed position slot per row-3 branch (a new family or a stretched
contract), the trail term `2 + Σ (hi_i − lo_i + 1)`, a checkpoint on every row-3 branch.

## The STOP RULE

Did NOT fire. The hand-off is sound on every class the row admits: widening erasures (atomic,
possessive, nested lookaround) add only candidates the confirm rejects; the narrowing class (`\G`,
`^`, `\A`, `(?m)^`) is declined before the build; backreferences have no machine; callouts, verbs
and `\K` are refused inside a lookbehind today and stay declined by conjunct (b). The one class
NOT admitted that would need its own argument is a count-COLLAPSED machine (unbounded lengths:
it needs the width bound back and a character-distance check under UTF-8); the row never requests
it.

## The three standing questions (answered in the note, §7)

1. **Measurement regime:** relevant only to S3 (the proof step's speed gate): vlookbehind §5.4's
   regimes (a)-(d), dev box, both VM entries, both kit layers; regime (c) can flip the row, which
   narrows its admission. Every other step is byte-identical.
2. **Independent control:** relevant. libpcre2 10.46 for answers and for the per-part oracle; the
   previous commit's output for bytes; the ratchet recipes are written by this note, so the
   re-check and the manager are their independent reading; population counted by the D27 author
   and gate 1's generator; each witness names the plant that reaches it in the deny build.
3. **What moves on regeneration:** mostly not relevant; S3's new emission is an abi event and a
   `tuning.md` hunk.

## D-next decision entry (draft; the manager assigns the number)

> **D-next — A-REV: one automaton-run record; the lookbehind hand-off is the first cross-engine
> piece, built as a proof step** (owner, 2026-11-06, review 2026-11-05 r5 addendum; lane
> arevrev1). Every DFA walk, forward and reverse, is described by ONE direction-neutral record
> (`DfaForm` made into it): a machine-table entry, the rendering and the form's selected rows as plan
> outputs, `from`/`bound` as typed position references, a hand map in `CT_*` terms, a tag kind, an
> instance id, placement and container; no C text crosses it. There is one walk behaviour,
> `farthest` above a bound; the automaton exits of roadmap §4 are hands and host loops. Machines
> live in one per-artifact table (H-FLAGS's machine half). A VM body runs a table walk through a
> file-scope part called by an in-body `VK_AUTO` record with declared effects. A machine's
> language fact is read after the build (`lang = same | superset`), and every construct that
> NARROWS a reverse machine (`\G`, the absent-previous context rows) is declined BEFORE the build
> (`pcrec_nfa_has_bot`). The first client is the lookbehind hand-off: existence on `lang = same`
> with no group, otherwise candidates farthest first confirmed by the forward body run; one D186
> choice row against `range`, gated on answer identity and no regime slower; it waits for
> vlookbehind stage 1 and [VMREC]'s analysis stage, not for a speed trigger. Consequences: the
> filter-only form is a later option; revdet's step is a rendering and its loop a member of the
> loop-over-walk-results family; R28', R03' and R10' are counted by what they do.

## Questions for Frank (plain words; leanings are not rulings; also the note's §8)

1. **Spell the lookbehind loop the cursor-rung way?** The candidate loop can keep the candidate in
   its retry frame, or keep the cursor there and carry the candidate in a saved slot. Same answers.
   For the hand-off the first needs no slot and no extra saved entries; the second needs a new kind
   of saved slot plus a checkpoint on every such loop. Leaning: the cursor-rung way, ruled once for
   both the plain loop and the hand-off.
2. **Move every machine into one table before the hand-off, or only the lookbehind's?** One table is
   the hub's own end state and keeps one way of naming a machine; it is a medium byte-identical step
   just before the hand-off. Leaning: all of them, in its own step.
3. **The restated ratchet counts go up on paper before anything is built** (the revdet row 1 → 3,
   the direction-copies row to 5), because they now count what the code does rather than names.
   The manager's to record; no ruling needed unless you object.

## Manifesto text proposed (owner-only file, not edited)

None needed. Optionally, after the five exits in §2's "automaton records" sentence: "(one walk;
the exits differ in what the consumer does with its result)".

## For the manager

- Roadmap §5 is yours to restate: rev 1's recipes R28' (5), R03' (3), R10' (1) are in arev.md §4.3;
  the A-REV section cites them and says the baseline rises by re-definition.
- [VMREC]'s row may name S2 (revdet's step onto the record) as a ride-along it may carry (F26).
- The [STREAM] status line already carries the 2026-11-06 ruling; not edited.
- The review recommends a D27 spec-first author for the hand-off's exits when S3 is chartered
  (cells: `\G`, `^`, multi-branch, atomic, both polarities, start offsets), shareable with
  vlookbehind's.

## Validation (text lane)

- `scripts/plan_lint.sh`: 299 rows parsed, 0 violations (plan.md not edited).
- The pre-commit spec checks passed on each commit (52 passed, 0 failed).
- `scripts/check_claudemd_size.sh --staged` at the final commit (below).
- Probes: libpcre2 10.46 as a library, 39 match cells (premise.out). No pcrec build: pcrec refuses
  variable lookbehind today, so no pcrec cell is meaningful, and no `make` was run.
- No suite run. None is owed (text only).

## STATE AT HANDOFF

STATE: delivered. Branch `lane/arevrev1` is committed: arev.md rev 1, the roadmap A-REV row and
section, `docs/design/stream/CLAUDE.md` and `docs/design/CLAUDE.md` (status lines), the evidence
directory, the lanes history index line, and this report. The rulings file
`docs/dev/lanes/arevrev1_rulings.md` was EMPTY at every checkpoint, so no entry was applied. Next,
per the review: a short re-check round (fix-induced on F1/F4/F14/F16, plus readiness), then the
owner's answer to §8 question 1 (shared with vlookbehind_pieces' question 1).
