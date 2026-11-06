# Review 2026-11-06 r2 — vlookbehind rev 3 (design, RE-CHECK before the stage-1 build go)

DRAFT by the coordinator (opus); dispositions are PROPOSED, for the manager's ruling.

## RULING (manager, 2026-11-06)

Verdict accepted: READY WITH LISTED TEXT FIXES; no answer bug in the §5.1 loop. Every PROPOSED FIX-NOW (F1-F7) ACCEPTED. F1's design choice (manager): the encoding-dependent bounded step comes from the ENCODING SEAM as a declared entry, like the existing advance, and DD12a(i)/K49 read their excised regions and agreement sites FROM the seam's entry list rather than from a hand-named region (general mechanism over a named exclusion; memory pcrec-general-mechanisms-not-special-cases). The entry-shape decision must not read the step's encoding-dependent length (or reads it via the seam and is stated as encoding-dependent), and the K49 comment obeys -fno-comments. If rev 4 finds DD12a cannot derive its regions from the seam without a rewrite out of proportion to stage 1, it falls back to a named DD12a region and says why. W14's byte-step arm gets a detector. Process change adopted: a critic whose findings Write is refused SendMessages the coordinator AT ONCE (critic skill §5).

## Subject
- `docs/design/vlookbehind.md` REV 3 (PROPOSED), doc commit `febde6edd2b2`, byte-identical on main
  `e20dee230` (merge of lane/vlbrev3). Build tree: main `e20dee230`, review tree `worktrees/crit-vlb3`
  built unlocked (`nice make -j2`, rc 0).
- Client in force: `docs/design/stream/arev.md` rev 1 (`b4878cb6a`, = main HEAD at freeze).
- Rulings frozen at `e20dee230` (decisions.md `0b7ee8898`, plan.md `cc7edf500`). FREEZE DRIFT at hand-back
  (main `6e01c810b`): 7 commits touch decisions.md/plan.md (D37 addendum, [FEAT-FAMILIES], [UTF-END-ASSERT],
  [M4-CALLOUTS] close, [MATCH-EVENTS]); none mentions lookbehind, [VLOOKBEHIND], [VMREC], D153 or D186.
  No drift bearing on this subject.

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| fix-induced | opus | every rev-3 addition traced to every reader, incl. the sizing passes; sibling fields | re-check of a revised design; r6's FRAMES lesson |
| soundness | opus | hand-execute §5.1 literally on F1 cells, W12-W16, stray-continuation UTF-8 cells; can each witness fail | rev 3 re-spells pseudo-code over real frames/slots |
| readiness (+goals, sibling of family, general form + unlocks) | opus | per stage-1 unit: cites, witness, separable, complete; overall verdict | last re-check before a build go |
Verifier: sonnet, all 14 items (verify.md).

## Which lens caught what
- The DD12a(i) / one-splice break: all three lenses independently (fixind, ready, sound).
- The encoding-dependent entry-shape knee: fixind only.
- The K49 comment under `-fno-comments`: ready (fixind noted it as a side fact).
- The W-low answer-level witness (the design's "no cell found" is false): sound only, by literal execution.
- The local's missing sizing pass: fixind and ready.
- Sabotage anchors (S123/S133), W-low plant spelling: fixind. S-U4 re-aim, gate-1 harness, legend vs
  `vm_slot_name`, stale 160-byte claim, [VMREC] list home, W12(a) mechanism: ready.

## Answer-level verdict
No answer bug in rev 3's loop. The soundness critic's literal interpreter of §5.1 (frames, trail, POS,
`$_back_step` ported line for line, bounded `advance`) equals libpcre2 on rev 3's 52 cells, 33,000 byte
fuzz cells, 15,000 UTF-8, ~12.8k ill-formed (residual diffs are start-position semantics outside §5.1
or its own step budget), 70 hand adversarial cells incl. stray continuation bytes at and before the
cursor, and §5.1c's 8 cells. Every finding below is text the build owes or a gate the build must
extend; none changes the mechanism. No speed-level finding.

## Findings and PROPOSED dispositions

### F1 — the bounded step is a second encoding splice inside the VM body (FIXIND-1, READY-1, SOUND-1, SOUND-2; verify 1, 2, 3) — maintenance/design
DD12a(i) (`tests/codegen/run_encoding_checks.sh` l.329-380) compares byte vs utf8 artifacts with a CLOSED
region list; region (2) is "the one splice DD-12 (7) admits", found only by `GUARD_RE` (l.491). A
`VSK_STEP_CHAR` renders `scan_position++;` vs the utf8 skip loop + K49 comment in the matcher body: no
region excises it, so every flipped ASCII `range` pattern turns DD12a(i) red on a correct build. §5.6
l.1275-1278 ("unaffected ... a range fixture gives it a second site") and §7 l.1534-1536 ("W14's
byte-step detector") are false: the K49 agreement check extracts only the `a*` retry loop (l.2128-2142),
so W14's byte-step arm has NO detector (SOUND-2). Two further readers: (a) the body's byte length,
comments included, feeds the entry-shape decision (`pcrec_vm_stmt_program_bytes` -> `pcrec_sb_len_decide`
vs `VM_INLINE_CHAIN_MAX_BYTES`), so near the knee the entry rung would differ by encoding — the
encoding-dependent emitter decision DD-12 (7) exists to exclude; (b) the utf8 `advance` text's five-line
K49 comment ("an unanchored search may only ever try LATER CHARACTER BOUNDARIES as match starts") is
emitted even under `-fno-comments` (measured: `a*`, `-e utf8 -fno-comments`, a.c l.309) and is false at
the lookbehind site; G4's "two more lines" is about eight.
**PROPOSED: FIX-NOW (text, before the build go).** §5.6/§6/§7 name: DD12a(i) region (6) for the
lookbehind step with counter, floor, asymmetry rule and a forced `range` witness, plant re-validation;
a real detector for W14's byte-step arm (a second K49 extraction anchored on the step's own text, or a
residlb per-site count of the step); the step's text kept out of the entry-shape length (as SIMD/layout
text already is) or rendered comment-free; the `advance` field split into its D112 doc/code pair (or
the comment moved to the retry-loop caller); and every "one splice" sentence that becomes false
(DD12a header (2), emit_vm.c's K49 comment ~l.13340, enc.h's `advance` contract ~l.355-360 and l.614-616,
src/gen/CLAUDE.md l.27). An alternative the manager may prefer: a dedicated seam entry for the bounded
step (§5.5 already files `back_step_upto` as a measured-trigger candidate) — this would make the step
an entry DD12a(i) already excises (region 1), at the cost of a new entry; the coordinator leans to the
named region (smaller; no new seam vocabulary) but notes the entry form removes three of the five owed
texts. Design call, not answer-bearing.

### F2 — W-low's "none at answer level" is false; the witness CAN fail at answer level (SOUND-4; verify 11) — test/doc
`(?:(?*.*(?<*a?))b)*$` on `bc`: libpcre2 `[2-2]` (both oracles); literal §5.1 with `LO_i` trailed `[2-2]`;
with `LO_i` untrailed GIVEUP (re-evaluation from a backtracked `.*` leaves `LO` stale; `@P++` overruns
`POS`). Sound's lowmin: 652/2,904 cells move. §7 W-low (l.1484) says no cell was found and re-aims it as a
codegen row only. **PROPOSED: FIX-NOW (text):** W-low gets this answer-level cell (and states what a real
artifact does on overrun: give-up/frames, or an out-of-bounds read — the build must confirm the
former), keeping the codegen row as the second detector.

### F3 — `VL_LB_COUNT`'s declaration has no sizing pass or frame field (FIXIND-2, READY-5; verify 8) — maintenance
§5.6 l.1249 "declared by the frame as the `rv` locals are"; `VmFrame` (vm_stmt.h l.304-318) has no such
field, locals are declared per family from frame fields; `<n>`'s meaning and the `VmLocal` field that
carries it are unstated; three reads of the local are opaque strings built in emit_vm.c, which cannot
call the static `vm_local_name` (the declaration/use split [M6-READ] records as a past break).
Both critics note `K_i` is dead before the first push and its window is straight-line, so ONE
artifact-wide local suffices. **PROPOSED: FIX-NOW (text):** name the `VmFrame` field (leaning: a single
shared local, a `bool` like `span_cursor`, no `<n>`), its producer, and the name's single source.

### F4 — legend text for `LO_i` vs `vm_slot_name`'s no-parallel-list rule (READY-6; verify 6) — design (house rule)
§5.1b l.749-751's "one owner record per `low` index" is the parallel list `vm_slot_name`'s header
(emit_vm.c l.1004-1010) forbids. Ruling 8's per-slot text is deliverable arithmetically: lookbehind lows
as a sub-block after the span lows (`base_low + nspanlow_total + i`), counted apart, both sub-totals
agreeing. **PROPOSED: FIX-NOW (text):** §5.1b spells the arithmetic sub-block.

### F5 — sabotage rows: anchors, plants and mechanisms (FIXIND-3, FIXIND-4, READY-3, READY-9; verify 4, 9, 10, 13) — test/doc
- S133's anchor is the exact builder line `pcrec_vm_b_seek(v->sb, VSK_BACKSTEP, NULL, k);` (`SAB_COUNT=1`);
  widening the builder for the local operand breaks it, a new site in the same spelling makes it 2. S123
  (anchor: vm_look's `VSK_RESTORE, sl, 0`, count 1) is not named by §7 although `range` adds two
  `VSK_RESTORE` sites. The operand's "absent" spelling and the builder shape are unstated.
- W-low's plant "`LO_i` written untrailed (`VK_LSET`)" cannot be built: `VK_LSET` targets only a
  `VmLocal`, never a slot (vm_stmt.h l.139-141). Plantable form: `LO_i` held in an untrailed local.
- S-U4's re-aim cell `(?<=a)x` is a T3 context node, built before any width rule (mod_lookaround.c
  l.524-533; no lookbehind in its listing): re-aim on `(?<=ab)x`.
- W12(a)'s red under its sabotage rests on K134's compaction trigger stopping after one round
  (emit_vm.c ~l.12650-12711; hand reasoning, ~70 % confidence); a trigger change could turn it green.
**PROPOSED: FIX-NOW (text)** for the first three (§7 lines); **DOC** for W12(a): state the mechanism or
choose a sabotage whose extra entries are distinct slots, and confirm red at build.

### F6 — gate 1's named harness cannot run its UTF-8 or ill-formed cells (READY-4; verify 5) — design/doc
`tests/lookaround/run_lookaround_diff.sh` and `tests/backrefs/bref_oracle.py` have no encoding or
INVALID_UTF option. Instruments that can exist (`tests/lib/p2probe.c`, `tests/utf8/run_startbnd_diff.sh`).
**PROPOSED: FIX-NOW (text):** gate 1 names the instrument for its UTF-8 and ill-formed cells and counts
the population per mode (K35).

### F7 — [VMREC] member list has no named home (FIXIND-3, READY-8) — doc
Ruling 7's condition ("[VMREC] must list them") is unowned: no file named, no list exists at the freeze.
**PROPOSED: FIX-NOW (text):** §5.6 names the home (the [VMREC] row's refs or a `plan_row_bodies/VMREC.md`)
with the three entries and their declared effects (noting FIXIND-3's opaque-string reads of the local,
which existing `rv` locals share); §13 Q5/Q6 marked ANSWERED by rulings 7/8, §5.1b "recommended" -> "ruled".

### F8 — model.py is frame-free and byte-only; §5.1a over-claims it (SOUND-3; verify 12) — doc
`cursor_branch` (model.py l.258-276) runs the candidate sequence only (no frames, trail, POS/LO, charges),
so it cannot move under W11-W15/W-low; `cells_byte_model.out`: `(?<=\Aa{0,2})x` on `aax` cursor=nomatch vs
pcre2 `[2-3]`. §5.1a l.617-620 "all equal to libpcre2" is false for the model. **PROPOSED: DOC** —
restate as "the candidate SEQUENCE"; the literal evaluator (sound's lvm, 52/52) is the stronger evidence
and could be adopted into the evidence dir.

### F9 — stale text (READY-7; FIXIND P&H) — doc
§5.1b l.812-815 "the 160-byte `vm_rolef` limit": no such limit (`pcrec_sb_fragfv` measures then allocates);
the stale comment at emit_vm.c l.7125-7129 should be listed among texts that move. §5.1b l.666-667
describes rev 1's push-at-cursor order as current. G2's "must be closed before the build go" is closed.
**PROPOSED: DOC** (with the FIX-NOW pass).

### F10 — out of delta: `(?<!\G|é)` on ill-formed `\xc3` (sound P&H; verify 14) — answer, existing
pcrec `match 1 1`, libpcre2 (INVALID_UTF) nomatch. This is utf8_design.md §2.6.1's ACCEPTED position
("no path inverts for a negative assertion"), not rev 3's. **PROPOSED: NOTED** — confirm it is listed in
the compliance page's ill-formed caveats; if not, a one-line DOC there (no new row).

## PROBED-AND-HELD (summary; counts in the critic files)
- Trail term `2 + (range branches)` traced to every write (`LO_i` the only trailed write; `vm_cost_look`,
  the call arm's `2·|W|` via `VmSnap.low`); slot sizing via family totals; K134 checkpoint only where the
  body writes the trail (`vm_jump_closes_trail_cycle`); push count and frames bound; `$_back_step` k=0 and
  sentinel monotonicity; `advance_utf8` reads only under `@P < @N`; M5-SEAM per-site counts; deleted terms
  (`D_i`, `SLOT_COUNTER`, the old term) all marked history; low family's contract fits `LO_i`.
- Literal §5.1: answers equal libpcre2 on every population above; 22 sabotage rows MOVE; STILL rows
  explained (W11a guard control by design; W12(a) moves capacity, not answers; WLOW's forward-path cells).
- 14 new/re-aimed witness answers re-probed on libpcre2 10.46: all equal §7's figures.
- r6 RULING block vs §16b/§16c: no disposition silently reversed (V1/V3/V4 superseded openly).
- Goals: §0 still ranks G1-G5, each measurable; rev 3 serves them in order.

## Per-unit readiness (ready lens, adjusted by F1-F2)
U1 width rule/limits: READY. U2 loop + emission table: READY WITH TEXT FIXES (F4, F9). U3 record
vocabulary + seam: READY WITH TEXT FIXES (F1, F3, F7). U4 budgets/trail: READY. U5 gates + witnesses:
READY WITH TEXT FIXES (F1, F2, F5, F6). U6 spec hunks: READY. U7 [DD-14.LB] reversal + D27: READY.
**Overall: READY WITH LISTED TEXT FIXES** (F1-F7 FIX-NOW, all text; F1 also names harness work the
build owes, and its one design choice — named region vs a seam entry for the step — is the manager's).

## Standing questions (ready lens)
- Sibling of a family: the cursor-rung loop is the SECOND member of "frame-carried candidate cursor +
  once-per-entry trailed bound" (`vm_cursor_rep` first); arev row 3 would be the third — unify into one
  emitter primitive when it is built (trigger: A-REV S3). `VSK_STEP_CHAR` is the second caller of
  `advance`, a different seam channel from `$_back_step`/`next_pos` on purpose; F1 is its cost.
- General form + unlocks: "enumerate [far, near] by a frame-carried cursor against one trailed bound,
  step = the encoding's step bounded by the cursor". Unlocks: a raised/caller-set cap costs no storage
  (trigger [IFACE-PUSH]); `back_step_upto` once the UTF-8 `(hi-lo)²/2` corner is measured; stage-2
  run-time-width references (trigger: a pattern needing it); arev row 3 as a second producer (A-REV S3);
  [LB-EXIST] with `far` from an automaton filter (trigger: a real pattern).

## D27 recommendation
Unchanged from r6: a spec-first author for the stage-1 contract (§9) remains recommended; the launcher decides.

## By-id completeness
FIXIND-1 -> F1; FIXIND-2 -> F3; FIXIND-3 -> F5, F7; FIXIND-4 -> F5. READY-1 -> F1; READY-2 -> F1;
READY-3 -> F5; READY-4 -> F6; READY-5 -> F3; READY-6 -> F4; READY-7 -> F9; READY-8 -> F7; READY-9 -> F5.
SOUND-1 -> F1; SOUND-2 -> F1; SOUND-3 -> F8; SOUND-4 -> F2; sound P&H out-of-delta -> F10.
Verify: 14/14 HOLDS (item 13 by hand reasoning, ~70 %).

## Lessons for the guide
- A design that splices an existing seam TEXT into a new site must trace the text's other readers:
  identity gates that excise it by anchor, length-based decisions that count it, and the text's own
  comments. (All three lenses found the gate; only one found the length decision.)
- Literal execution found the one witness claim the evidence could not: the evidence model was
  frame-free, so a frame/trail sabotage could never move it. A witness "no cell found" must name the
  model it searched and whether that model has the mutated state.

Critic texts and verify.md: `review/` beside this file. Process notes: `.coord/process.md`.
