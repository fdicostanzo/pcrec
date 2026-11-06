# Lane vlbrev3: vlookbehind design rev 3, the cursor-rung loop

Lane vlbrev3, opus, 2026-11-06. Branch `lane/vlbrev3` from main `7feb7d641`. TEXT and PROBES only:
no edits under src/, cli/, lib/, memfn/ or tests/, and no build. Subject:
`docs/design/vlookbehind.md`, now **PROPOSED rev 3**. Applies Frank's ruling of 2026-11-06: "if
it's able to always be true then do it. if it's occasionally true then it should use a decision
table, ideally a general one for determining this sort of thing." Evidence:
`docs/dev/lanes/vlbrev3_evidence/` (README in the note's §15).

## Verdict, in plain words: ALWAYS

The cursor-rung shape (the retry frame keeps the candidate start, and one trailed value is
written per evaluation) is sound for every lookbehind body the design admits, at stage 1 and
stage 2. So it is the `range` row's only spelling, and no decision table is needed. Rev 3 grows no
[DEC-RUNG] row.

There are two refinements. Both are conditions on how the loop is SPELLED, not on which bodies it
accepts:
1. **The farthest start.** It is not "hi characters back, clamped at the subject start". Under
   UTF-8 the back-step also stops at a run it cannot validate. The loop finds the farthest start
   with rev 2's own retry (count minus one on the sentinel), run once per evaluation instead of
   once per candidate.
2. **The forward step.** The one-character step toward the nearest start must be bounded by the
   CURSOR, not the subject length. Bounded by the subject length, a stray continuation byte at the
   cursor makes the step overshoot, and the loop never ends. This is a real runaway, measured.

The checklist the brief named:

| item | result |
|---|---|
| UTF-8 | needs both refinements |
| caseless and multi-width | Kelvin-sign cells pass |
| `(?<*` (non-atomic) | retries come from outside, through the frame |
| negative | same exits |
| nested lookarounds | they write their own mark/`POS` above the frame's trail mark |
| alternation and atomic | body choice points sit above the frame |
| stage-2 backrefs | bytes and UTF cells pass |
| the 255 cap, the 65535 ceiling | unchanged |
| `\K` | refused, err 199 |
| `\G` and `^` | cells pass; review r5's F1/F2 are reverse-machine hazards, not the loop's |

## Evidence (MEASURED, libpcre2 10.46 on the dev box)

- **Exhaustive candidate-sequence check** (`candidates.py`, `candidates.out`). It uses literal
  Python ports of the emitted `back_step` and `advance` texts and covers 8,583,480 cells (every
  subject over an 8-byte UTF-8 alphabet up to length 5, a 5-byte alphabet at lengths 6-7, × every
  cursor × nine ranges).
  - The cursor shape and rev 2's counter shape try the same candidates in the same order: 0
    differences.
  - The back-step's sentinel is monotone in its count: 0 violations.
  - The check can fail. Its three wrong spellings differ on 288,168 cells (unbounded step, which
    includes runaways), 3,398,699 (sentinel → subject start) and 591,194 (sentinel → nearest
    start).
- **Model sweeps** (`sweep_cursor.py`). vlbpieces' two sweeps, re-run through a literal `cursor`
  evaluator, differ from libpcre2 on 0 of 54,579 cells. The `range` control is also 0.
- **52 hand-picked libpcre2 cells** (`cells_*.out`). They cover bytes, UTF-8, Kelvin fold, `\G`,
  stage-2 backrefs, and ill-formed subjects under `PCRE2_MATCH_INVALID_UTF`. Each is a witness or
  a control.
- **Work-charge distribution** (`workdiff.out`), cursor minus counter over the same cells:
  - 852,406 cells charge exactly 1 more (small widths only);
  - 3,138,528 charge less, by up to 9;
  - the rest are equal.

## What rev 3 changed in the note

- **§5.1, re-sketched in the cursor shape.** One trailed slot `LO_i` per `range` branch (the
  nearest start), one untrailed local `K_i` (the far count), and labels `L_far_i`, `L_try_i`,
  `L_adv_i` and `L_n_i`.
- **§5.1a, new: totality.** The argument per body class, the work corner, and the STOP RULE (not
  triggered).
- **§5.1b, rows rewritten.** Slot allocation and every reader of the `low` family. The rewrites to
  today's bytes at `lo = hi` are re-stated. The K134 checkpoint is now derived, not declared, and
  the note says exactly which bodies get one. The role texts are updated.
- **§5.1c, re-traced literally.** Eight cells with trail depths: the four F1 cells, W12, W6's
  UTF-8 retry, W13's bound and W15's clamp.
- **§5.2.** Storage no longer depends on `hi`, so a raised cap is a one-row change in storage too.
- **§5.5.**
  - Work: at most `2·hi − lo` on the common path (509 at `{1,255}`, against rev 2's 32,640). The
    corner bound is unchanged.
  - Trail: re-derived from every write, `2 + (number of range branches)`.
  - `growable`/`pt` is withdrawn, and the "alternative" paragraph is retired.
  - A `back_step_upto` seam entry is filed as a measured-trigger candidate.
- **§5.6, record mapping.**
  - No new `VmKind`.
  - Two new members inside existing closed lists: one `VmSeek` member `VSK_STEP_CHAR` and one
    `VmLocalKind` member `VL_LB_COUNT`. Plus one local-count operand on `VSK_BACKSTEP`.
  - V3's `slotx`-value arm is deleted.
  - `advance` gains a new caller, and enc.h's `@N` comment widens.
- **§6.** Gate 1 adds ill-formed UTF-8 subjects. The stage-1 trail term is updated.
- **§7.** W6, W11 and W12 are re-aimed. W13-W16 are new. W-low has no answer-level cell, so it
  becomes a codegen row. S133/S134 get one twin per site, and the fixture count is `back_step:3`.
- **§10.** No `ir_listing.md` hunk (new reason). One `limits.md` §3.1 sentence on the work charge.
  The decision-entry text is updated.
- **§11, §13, §15.**
  - §11 adds the two new controls.
  - §13: Q1 and Q2 are recorded ANSWERED, and Q4's counter line is marked superseded. Q5 and Q6
    are new; both are the manager's calls.
  - §15 adds a measured/inferred split and the evidence README.
- **§16c, new.** The disposition map, plus an 11-item pick-up list for `stream/arev.md`.

## What it deleted (the brief asked exactly which)

- `D_i` and its `SLOT_COUNTER` slot. V4's ruling no longer has an object.
- The per-candidate back-step, and its count rendered from a slot (V3's arm).
- The per-candidate `RX_CHARGE_WORK(D_i)`.
- The trail term `Σ_range (hi_i − lo_i + 1)`.
- The `growable`/`pt` ceiling proposal.
- §5.5's alternative paragraph.
- The K134 checkpoint on every `range` loop, plus the two `D_i` sites it added to the `nset`
  margin.
  - What remains: `vm_goto` places a checkpoint only where the BODY writes the trail (captures, a
    quantifier on the cursor or counter rung, atomic marks, nested lookarounds, callee parks).
  - So the K134 helpers disappear for bodies with no trailed write (literals, classes, fixed
    alternations, anchors, possessified loops), such as `(?<=(?:ab|c))x`.
  - They do NOT disappear for every capture-free body: `(?<=a{1,9})x` still writes its rung's
    `low` slot.
- **K134 consequence:** the checkpoint becomes structurally harmless. The pop before the back edge
  has already rewound the body's writes, so the trail does not grow around the loop.

Kept, per the rulings: ruling A, so `one-length` stays today's bytes; the 65535 ceiling rides
stage 1; cap 255; backrefs at stage 2. The fixed-tail hoist and the backward span count stay
HELD.

## Questions for the manager (both answer-free)

- **§13 Q5.** Does the "a new VM record kind waits for the analysis stage" ruling also cover a
  new MEMBER of an existing closed list (`VmSeek`, `VmLocalKind`)? Leaning: no. Each member is a
  one-row addition to the declared-effects table.
- **§13 Q6.** Which slot family holds `LO_i`? Leaning: the `low` family. Its contract matches
  exactly (a position, written once per entry, trailed). It needs per-slot legend and listing text,
  which §5.1b lists. The alternatives are the counter family (no reader changes, but it names a
  position as a counter) and `lookpos`.

## INFERRED (checked at build, stated in the note)

- Which rung a body quantifier inside a lookbehind takes, and so whether a body writes the trail.
- W12(b)'s exact margin.
- Row 3's W-trail cell in arev.
- G4's line counts.
- The speed rows.

## Not done / out of scope

- `stream/arev.md` was NOT edited (lane arevrev1 owned it). §16c lists what it must pick up, by
  line, against main's `0f7d79795`.
- The [VLOOKBEHIND] plan status line was left unchanged, because staging did not change.
- There is no `vlbrev3_deliver.txt`, so there is no lanecheck DELIVER block.

## STATE AT HANDOFF

- The rulings file `docs/dev/lanes/vlbrev3_rulings.md` was empty (0 bytes) at every checkpoint,
  including this one. No rulings entry was applied.
- Every commit is on `lane/vlbrev3`. Nothing was merged to main.
