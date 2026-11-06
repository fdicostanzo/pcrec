# vlbrev1 — [VLOOKBEHIND] design rev 1 (lane report)

**Lane:** vlbrev1, opus, 2026-11-05. Branch `lane/vlbrev1`, from main `2056360d7`.

**Brief:** write rev 1 of `docs/design/vlookbehind.md`, applying the RULED review
`docs/dev/reviews/2026-11-05-r3-vlookbehind.md`.

**Constraints:** text only. No build go, and nothing under src/ cli/ lib/ memfn/src/ tests/ was
touched.

## What changed

The note is `docs/design/vlookbehind.md`, now PROPOSED rev 1. Corrections are marked inline as
`[r3 Fn]`. A REVISION 1 block at the top summarizes them, and §16 maps each finding to the section
that answers it.

- **F1, §5.1 re-sketched.**
  - The guard tests `lo` first. The retry frame is pushed BEFORE the back-step and saves the CURSOR.
  - Each candidate re-steps `D_i` back from that restored cursor, so every exit to the next branch
    leaves `scan_position` at the cursor.
  - §5.1c hand-executes the sketch literally on four cells, saying what each frame saves and
    restores:
    - the three F1 cells: `(?<=a{1,2}|b)x`/`bx` [1-2], `(?<=a{2,3}|b)x`/`bx` [1-2],
      `(?<=a{1,2}|bc)x`/`bcx` [2-3];
    - W5's gap cell, `(?<*(a|aaa))c\1`/`aaaca` [3-5,2-3].
  - All four equal libpcre2. The cells also go into §2, as witness W11 in §7, and as a gate-1 axis.
- **F12, the fold is now a declared selection (§5.1b).**
  - A two-row emission table, `one-length` (`lo == hi`, today's bytes) and `range`, is selected by
    the stored width fact.
  - Each row states its guard, slot, retry frame (target and saved position), work per candidate,
    back-step count, negative end-check action and `L_adv` block.
  - The `one-length` row is shown to be the `range` row after four rewrites that the emitter does
    not perform in general. That is why it is a selection and not a fold.
  - Work per candidate is its back-step's character count: `k`, or `D_i`.
  - Slots: one per VARYING branch only, so artifacts without one keep their numbering.
  - Owner question 1 is re-asked (§13).
- **F4, two lookbehind ceilings (the note's §5.2).**
  - The 65535-character absolute branch ceiling (err 187) and the 255 variable cap (err 200) each get
    a `limits.def` row.
  - Both are stated as POLICY. Correctness needs no cap: `D_i` is clamped and strictly decreasing.
  - The ceiling rides stage 1 as G1's exception to G2. §13 Q2 confirms this.
- **F2, F3, F5, stage 2 rewritten (§6).**
  - Both width ends come from the referenced group, and the range must be exact wherever it decides
    the cap or the emission row.
  - DD-14.LB's deferral widens to cover backreferences, with a per-group width memo.
  - Refusals: a by-name duplicate, any `(?|`, an unbounded group, a recursive group, and
    self-reference.
  - An 18-row acceptance table from the ruling lens: 15 rows re-run by this lane, and all match the
    rule.
  - The fixed-group half needs none of stage 1's loop.
  - The mrl.c comment fix rides the stage-2 build.
- **F7.** Gate 1 names D142's UTF startpos class. Those cells stay in the population, compared to
  D142's rule and counted separately.
- **F6.** §10 spec hunks completed:
  - `pattern_language.md` §9¶2 (both clauses), §7.11¶3, §7.3¶5/¶6 and shape 7;
  - the cap, ceiling and unbounded sentences;
  - `limits.md` §3, in a new subsection numbered 3.11;
  - `match_api.md` §4¶6 (the stale `pcrec_maxw`) and §9.4¶8;
  - the readers of the refusal text.
- **F8-F10.**
  - W6's cell is replaced by `(?<=(é{1,2}))x` on `éx` (UTF) [2-3,0-2]. Its sabotage is re-derived
    for the clamp as rev 1 spells it.
  - S136's re-aim is spelled as "the stored pair becomes K+1 at both ends".
  - W3b `(?<=a{1,2})a`/`aaa` [1-2][2-3] is added, and W9b covers the ceiling boundaries.
- **F11.** Noted at WD6.
- **F13.**
  - The UTF-8 clamp uses the EXISTING `$_back_step` entry with a run-time count. Its C signature
    already takes `size_t k`. So no new seam entry and no D58 change are owed, and the [M5-SEAM]
    count is unchanged.
  - The [VMREC] overlap is stated (§5.6). `D_i` is a record field (the `VK_SEEK` `slotx` operand),
    and the host row now says `VK_SET`, not `VK_LSET`.
- **F14.** G1 is scoped to implemented constructs and stated as false today. G2's dependency on Q1
  is recorded. G4 states a constant and "one loop frame". The population and callout text is fixed.
- **F15.** R03's `VK_CONSUME_BACK` is cited as the in-body precedent.
- **F16.** §4 names the LOCATE × FINISH family and the K-back sibling. §5.4 names [ENG-LOOK]'s
  existence form.
- **Plan.**
  - [VLOOKBEHIND]'s status and next lines are updated.
  - A HELD Boonies row, [LB-EXIST], is filed: the automaton existence filter plus unbounded
    lookbehind. Trigger: a real pattern from the [UTF-RW] harvest or a user.
  - The tag was grepped first; there is no collision. `scripts/plan_lint.sh` gives 300 rows,
    0 violations.
- **Index files.** `docs/design/CLAUDE.md` (the note's status) and the lane history index have new
  entries.

## Validation (text lane)

- **Premise test.** F1 reproduced with libpcre2 10.46 used as a library. The three cells match in
  libpcre2 ([1-2], [1-2], [2-3]), so rev 0's sketch was wrong exactly as the review says. Evidence:
  `docs/dev/lanes/vlbrev1_evidence/premise.out`.
- **Every cell rev 1 adds or quotes anew** was re-run: 19 match cells (byte), 4 UTF cells, and 28
  compile cells. They cover the ceiling, the cap, the stage-2 accepts and refusals, and the D142
  cell. Evidence: `vlbrev1_evidence/cells.out`. The probe source is `vlbrev1_evidence/probe.c`.
  Every answer equals the one the note states.
- **Checks.**
  - The pre-commit spec-cite check passed. It first flagged two "limits ... §N" phrasings as dangling
    `limits.md` cites; both were reworded.
  - `scripts/plan_lint.sh`: 0 violations.
- **Not run (by design).** No build, no make, no suites.

## The re-asked owner question, in plain words

**Should today's fixed-width lookbehinds keep their exact code?**

The earlier "yes" assumed the new loop turns into today's code by itself when a branch has only one
possible length. The review showed it does not: the compiler has to choose the old code when it
sees "this branch has one length". So there are two honest options.

- **(A) Keep today's code and write the choice down as a two-line table** ("one length → today's
  code, a range → the loop").
  - Cost: one declared choice, read off a fact the compiler already stores, with both lines tested
    by the same witnesses.
  - Nothing that compiles today changes, and no abi event is owed.
- **(B) Use the loop everywhere and take an abi event.**
  - Every lookbehind artifact changes: about 826 lookbehind lines in 40 `.rxt` files feed the
    identity gate.
  - Each gets a slot that renumbers later slots, one more frame on the last branch, and about 4-5
    more C lines per fixed branch.
  - The negative hard error stays tied to "one length" unless it is retired too, which would be a
    further contract change.
  - Speed: unmeasured, expected negligible.

**Leaning: (A).** Stability outranks textual unity, and the choice is declared and answer-free.
Under Frank's open "VM base" frame it is an admission row (used as a lens only).

There is also a smaller confirmation, Q2: the 65535 ceiling rides stage 1. The leaning is yes.

## Standing questions (summary; the note's §11 has the detail)

1. **Measurement regime.** Stage 1: a bound only. No number selects anything, and gate 4 measures the
   give-up subject size. Stage 3: relevant (per-regime row evidence).
2. **Independent control.** libpcre2 10.46, plus a NEW classification control (gate 3): pcrec's
   one-length judgment against libpcre2's accept at `max_varlookbehind = 0`. The generator counts its
   population and its D142 subset (K35). Every witness was re-derived so that it can fail.
3. **What moves on regeneration.** Mostly not relevant. Two `limits.def` rows move the limits
   listing's readers, and the refusal-text readers move in the same change. Under Q1 (B), every
   lookbehind artifact moves.

## Decisions owed

None minted. One candidate: a D-next recording the emission-table ruling (one-length vs range
selected by the width fact), once Frank answers Q1.

## STATE AT HANDOFF

STATE: delivered (text). The note is at PROPOSED rev 1 on `lane/vlbrev1`.

- The rulings file `docs/dev/lanes/vlbrev1_rulings.md` was empty at every checkpoint. No ruling was
  applied beyond the brief.
- Next: the re-check critic round (fix-induced on F1/F12, plus readiness), then Frank's answers to
  §13 Q1/Q2 and a build go.
- Validation is complete for a text lane: probes re-run and plan lint clean. Nothing is owed.
