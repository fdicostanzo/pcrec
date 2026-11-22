# Predicate-language manager: wake-up brief

Rewritten 2026-11-21 (box clock, about 19:15 EST; the record's entries are dated 2026-11-21), at the owner's
"lets close the session now", fourth predicate-manager session. Committed docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`); main was merged in at wake (clean). Main has everything
  through P-14 (74f70152e). ON THE BRANCH ONLY, not delivered: the three hand folds of 2026-11-19
  (flags-in-filter, its confirmation, flags-warning) and ALL of this session's rulings (below). P-17 is the pause
  notice and says so.
- REVIEW **r77 predfold1121** (design mode; number from main) is DRAFTED, NOT RULED: draft
  `$PCREC_TMPDIR/scratch/crit-predfold1121/review.md` (critic texts and `verify.md` in `review/`, process notes in
  `.coord/process.md`). VERDICT: NOT READY. Five opus lenses (ruling, examples, general, modes, fixind) and an opus
  verifier: 57 raw findings; 13 verified HOLD, 4 PARTLY, none refuted. Answer-level, by the coordinator's ids: A1
  (+A2) TWO OWNER RULINGS COLLIDE: array-scope ("the scope of the entire rx") against bare-nested-scope case 2 (own
  value only): a group question inside a used piece has two answers (WHOLE `7` HOLDS against FAILS): an OWNER
  QUESTION, not a rewording; A3 the ruled nested-scope statement read literally refuses 7 printed bound conditions
  and computed labels (the exemption is my reading; bound-condition is unanswered and no piece carries its slug);
  A4 a condition passed into a macro hole FAILS under the restated bare-condition statement while the "An
  argument" line prints HOLDS (`when` / `peek` become a compile error); A5 `0` in an `&` used as a sequence operand
  breaks the ruled `A & B` = `A & (0: B)`; A7 any_case has a third parting; A8 for a duplicated name PCRE2 uses the
  FIRST set group; A9 record-is-product against the joint refusal; A12 loop against two uses (dissolved once my
  withdrawal of reading (c) is folded). Proposed FIX-NOW: A1+A2 as the owner question, A3, A4, A5, A7, A8, A9, A12,
  D1-D12. FREEZE DRIFT: four owner entries landed mid-round, none a ruling, hand-mapped in the draft. Process:
  three of four evidence scripts were RED at the freeze while their committed outputs read 0 failed: after ANY
  direct fold of mine, re-run the lanes' DOC checks and mark superseded citations.
- NEXT, in order: (1) read `review.md` + `process.md`, RULE every disposition (record entry "MANAGER — review
  r77"); (2) ONE opus fix lane on a worktree cut from this branch (it also files the review as
  `docs/dev/reviews/2026-11-2x-r77-predfold1121.md` + directory + index line; denylist rule: no line-numbered
  plan.md or spec cites); (3) merge, lint, `make -s test-plan-lint`; (4) `done:` line in to_main.md (P-18) with the
  [COND-FAMILY] status line; SendMessage main.
- Lint `python3 -I scripts/pred_doc_lint.py`: 5,569 / 0 at close (RUN IT BEFORE NAMING A TIP). Lanes predscope
  and predarr are merged and stopped; their worktrees (`worktrees/predscope`, `worktrees/predarr`) are for main to
  prune (in P-17). No cron. Nothing in the box queue (never ours).

## READ, IN THIS ORDER

1. The skill, section 2. 2. `core.md`, `library.md` whole, `parked.md` scanned. 3. The record from "2026-11-20
OWNER, to main (relayed as M-2)" to the end (this whole session; about 60 entries; the late ones matter most).
4. `journal.md` from "2026-11-21 (16:30) — fourth predicate-manager session: wake-up". 5. `owner.md`. 6. The round
dir of r77. 7. `docs/dev/lanes/predscope_report.md`, `predarr_report.md` (readings tested, owner questions left).

## Ruled this session (all in the record; all in the pieces unless marked)

- class-value: "ascending codepoints everywhere"; any other order is the user's, by a sort.
- flat-read-outside: (a) a flat read outside a binding follows the inside rules; the path says which part.
- pure-label: "captures are explicitly written either in literal form or using a macro like capture()"; `[x = A]`
  is a label and no capture; export statement 5 narrowed to captures; `_` labels never export as captures. A
  label-to-capture ADD-ON is REQUIRED by him, form and spelling open (under-construction piece
  lib/structural/capture/add-on; his two methods: a wrapper, or after the fact for a library's label).
- zero-in-definition: (a) `0` is the match so far of the definition it is written in. CONFIRMED by his two
  examples at close: a bare condition's `0` is the rx it sits in; in `${A & (0: S)}` "the 0: is bound to A only".
- class-hole-order: (a) written order under a lift (the example program corrected at his catch: `/${/[${c}]/ +
  1}/`).
- array-vs-passes: (a) `some`, `count`, `occurs`, `h[k]` read the ARRAY OF SETTINGS (lib/counting revised).
- joint-in-some: a joint entry inside a group question is refused for now; "same item" is written on the item
  (`[ok = item & ((h, m): ..)]`, then `some((ok: anything))`); his "no one would know to write it".
- bare-nested-scope: case 1 "compile error at inner" (a piece may not NAME a label it does not hold); case 2 "i
  meant b" (a piece reads its OWN value only), ruled with the two-spellings pair shown first: compose-equals-
  literal now holds for what a piece's USER reads. His three examples (C sees d through B(A); B's body may not
  name d; B may label its parameter) are in the piece verbatim. His later statement: "bindings define scope. if
  they must refer to each other then construct in predicate with labels or create them in the same literal."
- NOT rulings: his LEAN that only `i` will be inherited at a hole (today's ruled list is `i`, `m`, `s`); the
  label variable (parked; pass the condition or the set today); my frame (finished rx, shaping / matching holes);
  `list_of_stuff` (his sketch; my worked form passes a set-making macro: needs a named macro as an argument).
- M-2 (his remark to main: rx and graph manipulation for intersection and subtraction) recorded as a LEAN.

## The question queue (one per turn; grep the record AND read the same-day later entries first)

0. **array-in-piece** (NEW, from r77 A1; ask FIRST, with the review's witness run): inside a separately defined piece, does a group question / the array of a name read "the scope of the entire rx" (array-scope, 2026-11-19) or the piece's own settings (bare-nested-scope case 2)?
1. **bound-condition** (ASKED twice, not answered; his two examples did not reach it): a condition under its own
   name (`c := (0: 5)`, then `/\d${c}/`; `late := (h: >5)`): does it read its labels and `0` where it is USED?
   Five printed definitions depend on it (pass-start-read's `c`, `sum`, `n := count(..)`, `nchars`, `mnum`). My
   leaning (a): yes. r77 has findings on this carve-out: read them first.
2. From the lanes: record-in-some (inside `some`, a two-entry record is "some h is 5 and some m is 3", parting
   from the joint form there); count-several (my lean: refused for now); capture-loop-value; group-truth re-put
   (close for one entry?); every-pass-spelling re-put (a named form would now mean every setting).
3. To confirm (his statement, my withdrawal of reading (c)): a piece looped by its USER does not see its own
   previous pass; a predecessor test belongs to the definition that writes the loop.
4. Older: number-in-loop, zero-in-loop, caller-ambiguous, not-test, condition-group, tuple-parts,
   default-imports, export-choice, call-forms, any-case-body (held by me). `scripts/entry -g . -p predicates --state
   open` lists 12 open pieces. Still owed: THE SPELLINGS REVIEW (one sitting; new today: `[=year]`, `.` as the
   sequence mark, the capture add-on's two forms); warning names (my call).
For a pcre2-reader, not him: the members of `(?i)k` in libpcre2 per mode (class-value reading (a)).

## Lessons (cases; the rule-shaped ones are proposed to main in P-17)

- I told him "That is the closed answer for labels" from three examples that covered a PARAMETER's labels only; the
  lane refuted it against the 17 printed definitions. A rule I induce from his examples is tested against every
  printed example BEFORE it is said, or said as "fits these three, untested".
- His answer letter can be a typo ("no, c" for b) and his REASON can be wrong while the answer stands (the loop
  case did not part (a) from (b): the reset rule). Check the reason by a run, show the ONE witness pair, ask again;
  he answers in one turn.
- I recorded a FIND-ALL line before reading the run's output (`55`@6 for ` 5`@5). The record is written FROM the
  output, pasted, never from what I expect it to print. Corrected by an appended entry.
- A rewrite I offered as equivalent was not (`inner($h)` consumes; the original tested). Run both sides of any
  "write it this way instead" before offering it.
- A printed program can be illegal predicate language and pass lane, review and lint (`/${[${c}] + 1}/`); he
  caught it. Briefs now say: inside `${...}` an rx is written `/.../`.
- "condition-argument" should not have been asked: `when`'s ruled condition test already answered it. Grep the
  LIBRARY's ruled bodies too, not only the record, before asking.
- When he asks for an EXERCISE, do it mechanically and report where the rules pinched; it moved the discussion
  more than three rounds of framing did.
- Two sequential opus fold lanes on overlapping pieces worked (second cut after the first merged); a single-piece
  ruling folded by hand between them merged clean.
- The lint's ruling-line parser takes the record title up to the LAST `")` on the line: nothing quoted in
  parentheses after the `(record: "...")` cite.
