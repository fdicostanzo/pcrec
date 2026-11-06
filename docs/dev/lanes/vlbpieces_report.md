# Lane vlbpieces — variable lookbehind as fixed and variable pieces (design + probes)

Lane vlbpieces, opus, 2026-11-05. Branch `lane/vlbpieces` from main `783a45ec0`. DESIGN AND PROBES
ONLY: no edits under src/, cli/, lib/, memfn/ or tests/. Deliverable: `docs/design/vlookbehind_pieces.md`
(PROPOSED rev 0). Evidence: `docs/dev/lanes/vlbpieces_evidence/`.

## In plain words (for Frank)

You suggested reading a lookbehind backward as pieces: jump straight to the fixed parts, and loop
only the variable parts, longest first, the way the VM's quantifier rungs loop.

I built a small model of three ways to run a lookbehind and checked each against libpcre2 on 54,579
generated cases:
- rev 2's loop (try each start, farthest first, run the whole body forward);
- your piece walk;
- a middle form: rev 2's loop with the fixed tail checked once up front.

The model's copy of rev 2 agrees with libpcre2 on every case, so the model can be trusted.

What I found:
- **Yes/no answers never change.** For a negative lookbehind, or any lookbehind without capture
  groups, your walk gives exactly libpcre2's answer, however many variable parts the body has.
  Atomic groups work too, as long as each piece is run forward after the jump, which the walk does.
  Only a walk that consumes characters backward breaks atomic groups. That answers your "Idk": they
  are fine.
- **Captures can change** when the body has two or more variable parts and a group sits among them.
  Example: `(?<=(a{1,2})(a{1,2}))x` on `aaax`. libpcre2 gives the first group two letters; the
  backward walk gives the last group two. In the non-atomic `(?<*` form this changes the overall
  match too.
- **Your capture rule holds.** A group that runs from a variable part into the fixed tail is right
  once the loop knows its length (0 differences on every such case).
- **The safe cases are easy to spot at compile time.** Count the variable parts, see where the
  groups are, and look at the lookbehind's form.
- **Inside the safe cases, the walk is rev 2's loop in different clothes.** With one variable part,
  "loop the variable part longest first" is exactly rev 2's "try starts farthest first", plus the
  fixed tail checked once. With two or more, it is one loop per part where rev 2 needs one in total,
  for the same answers. So it would be a second mechanism with nothing to gain yet.

What it does give: the rung ladder has two ways to write a loop. Rev 2 used the counter rung's way: a
saved counter, rewritten for every candidate. That is what made the trail grow (last round's V1).
The cursor rung's way keeps the candidate in the retry frame and saves one value per evaluation.
Same answers, and the trail no longer grows with the lookbehind's width. I recommend rev 2's loop
switch to it before the build.

Your two ideas taken literally become two held rows, each with a trigger:
- "jump to the fixed part first" (exact wherever it is allowed, but nothing in our population would
  use it today);
- "walk the repeated part backward" (a cheap candidate finder beside the held reverse DFA).

Today's fixed-width code stays as it is under every option.

## Questions for Frank (plain words, with leanings)

1. **Switch rev 2's loop to the cursor rung's way of looping, before the build go?** Same answers.
   It deletes the trail growth and the extra sizing that patched it, and makes raising the 255 cap
   cheap in storage too. It costs a short rev 3 of the lookbehind note and a re-check. Leaning: yes.
2. **Hold "check the fixed tail first" as a later row?** It is exact where it applies, but no pattern
   we have would use it. Leaning: hold it, with the trigger in the note (§7).
3. **Hold "walk the repeated part backward" as a third way to find candidates, beside the reverse
   DFA?** Leaning: yes, held, in the same home (A-REV).

## Findings by brief question (detail and cells: the note's sections)

1. **Candidate order (note §3).** MEASURED: 0 differences on yes/no and on the match end, every
   class. Captures differ in 342 of 2,794 positive cells with ≥ 2 variable pieces and a group at or
   left of the last. Overall matches differ in 136 of 4,445 non-atomic cells of that class, plus 16
   non-atomic cells with ONE variable piece, where the fixed piece's choices become the outer loop.
   The walk does not find PCRE2's farthest start first: `(?<=((?:ab)?)(b?))` on `ab`. UTF and
   caseless widths count characters (libpcre2 MEASURED, walk INFERRED).
2. **Captures (note §4).** Frank's crossing rule: 0 of 2,159 cells differ. The exact class is a
   first-match table over the form, the variable-piece count and the group positions, computed from
   the stored widths at compile time.
3. **Atomic, possessive, negative, nested, backreferences (note §5).** Forward-run pieces honour
   atomicity: 0 differing cells on nine atomic or possessive bodies. A backward-consuming walk is a
   superset and can only filter. Negative forms and nested lookarounds are exact. Backreferences and
   group conditions inside the body (libpcre2 accepts them) are excluded: a right-to-left walk reads
   the group before it is written.
4. **Fit to the ladder (note §6).** No rung hosts a backward body as it is: cursor, counter and frames
   are forward, and revdet's `VK_CONSUME_BACK` walk recovers over an already-scanned span. What
   transfers is the cursor rung's DISCIPLINE. The sizing is traced per pass: trail
   `2 + (number of range branches)` instead of `2 + Σ (hi − lo + 1)`; frames unchanged; push sites
   unchanged; work ≤ 2·hi. The deleted list is in the note. The family is [DEC-RUNG]'s
   fact-selected emission, and no row changes. No new rung is proposed, so [DEC-RUNG]'s trigger does
   not fire.
5. **Verdict (note §7).** (b), narrowed. The range loop stays the one mechanism, re-spelled; two rows
   HELD. Witnesses: W12 re-aimed (`(?<=a{1,9})x` on `bbbbbbbbbax`, libpcre2 [10-11]; UTF twin
   [19-20]), W-restore (rev 2's cells 1 and 3), W-advance ([M5-SEAM] per-site count), W-low (owed by
   the build). abi: none for existing artifacts (ruling A).

## Premise test

- `VmRungKind` (5 rungs) and `VK_CONSUME_BACK` (one producer, `vm_rev_emit`) exist where the brief
  cites them.
- The atomic cell reproduces with libpcre2 10.46 (`control_cells.out`).
- STOP RULE: did not fire. The class where the walk changes answers is detected cheaply.

## Validation

- Control: the model's `range` mode differs from libpcre2 on 0 of 54,579 sweep cells and 0 of 23
  control cells.
- Sweeps: `sweep.py` (30,099 cells, about 10 s) and `sweep_retry.py` (24,480 cells). Summaries are
  in `sweep_summary.txt` and `retry_summary.txt`; every differing cell is in `sweep_diffs.tsv` and
  `retry_diffs.tsv`.
- No build ran and no suite applies: text and evidence only.
- `plan.md` is unchanged: the verdict changes stage 1 only if Frank answers question 1 "yes", so no
  [VLOOKBEHIND] status line was added.

## STATE AT HANDOFF

STATE: done. Commits on `lane/vlbpieces`: the WIP evidence commit, then the note, this report, the
`docs/design/CLAUDE.md` line and the lanes history index entry. Rulings file
`docs/dev/lanes/vlbpieces_rulings.md` was re-read at each checkpoint and was empty, so no ruling was
applied. Next, if Frank says yes to question 1: a rev 3 lane on `docs/design/vlookbehind.md`
(§5.1, §5.1b, §5.1c, §5.5, §7 W12) taking this note's §6-§7, then the re-check round.
