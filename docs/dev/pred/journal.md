# Predicate-language manager: journal (append-only, newest at bottom)

## 2026-11-18 — the session is chartered (written by main, session 140)

- Frank, to main: "Please create a new manager skill: /pcrec-predicate-manager. Used to design and develop the
  predicate language. Managed by the pcrec manager like the kit manager is. an interface for me discuss predicate
  work." Skill `.claude/skills/pcrec-predicate-manager/`; this directory; the first wake.md written by main from
  sessions 134-140. Until today the pcrec manager ran the predicate work itself (journal: docs/dev/dev_journal.md,
  the 2026-11-14 .. 11-18 entries; the lanes predspec .. predspec271).

## 2026-11-18 evening — first predicate-manager session up

- Registered role pred; worktree `worktrees/pred` on `lane/pred-rev28` cut from main f9ee6814e. Read wake.md,
  M-1, the record from backref-label to read-is-constant, the draft's R.1.15 (11), R.1.16 ANSWERS CHANGED, R.8's
  hole-reads-capture row. No lane, no critic round alive.
- Grep of the record before asking hole-reads-capture: the 2026-11-17 ruling "what an unqualified `$x` reads"
  says "`$x` and `x:` never disagree" and predates holes holding values; so it is put to him as a confirm with
  that ruling quoted, not as a fresh question. The capture side of the example re-run under python `re`
  (`3-3;-3;` WHOLE holds; FIND-ALL on `3-3;-3; 7-7;` = [`3-3;-3;`@0, ``@7, `7-7;`@8, ``@12]), equal to the draft's row.
- owner.md written. Waiting on Frank's answer to hole-reads-capture.
- Main ACKed the hand-over (cross-session message): review number r52 is RESERVED for the rev 28 critic round;
  main's session is closing, the next one reads to_main.md at wake.
- Frank RULED hole-reads-capture: the label ("what i want is that $y works like label. however, there is a way to
  get the pcre capture value"). On the way: his discussion (label and capture separate; a labelled group need not be
  returned) and his recollection of the label-only group, CONFIRMED in POSTFACT.md 2026-11-09 (not in the predicate
  record until now); `(?<:x>foo)` and `(?':x'foo)` rejected by libpcre2 (error 162), run by ctypes; his typed
  `(<:x>foo)` a slip, corrected by him. Four record entries; predicates_future item 32. A reading of mine withdrawn
  the same hour ("the record lacks a per-group form").
- LESSON (case): his "I proposed" was true but lived in ANOTHER row body (POSTFACT.md). The record grep before
  answering covers docs/design/plan_row_bodies/, not COND-FAMILY.md alone.
- Next asked: number-domain (the record's 2026-11-15 confirmation, "numeric ranges are string sets; padding is an
  explicit transform", answers the comparison half; the arithmetic half is what is asked).
- Frank RULED number-domain: canonical. On the way: his suggestion "cant we wrap padded($y + 1)" and his idea
  `padded($y + 1, 4)` / `padded($y + 1, length = 4, pad = "0")` (both recorded, not ruled). Runs: scratch models
  `$PCREC_TMPDIR/scratch/pred/padwrap.py`, `padwidth.py` (to be re-made as evidence by the rev 28 lane; padwrap's
  `& /\d{n}/` uses a lookahead approximation, exact only for the subjects printed). numeral-width read as moot (m1).
- Next asked: padded-width (exact or minimum). Rulings gathered for rev 28 so far: hole-reads-capture,
  number-domain.
- Frank RULED padded-width: minimum (after three remarks recorded as clarification / observations; my leaning
  moved from exact to minimum on the two-case macro body, 36,119 python checks, 0 differences). Rulings gathered
  for rev 28: hole-reads-capture, number-domain, padded-width.
- Next asked: hole-flags. Pre-check run with libpcre2 (ctypes): a subroutine call to a group defined caseful
  stays caseful under a later `(?i)` (`a-A` fails), a backreference takes the options in force (`a-A` holds): PCRE's
  own two analogues agree with the draft's "as ruled for each"; what is asked is the string constant in a hole.
- Frank RULED hole-flags (a hole takes the flags in force at the hole; each regex literal has its own flags) and,
  on his own question, flags-propagate: yes (propagation with override; the draft's NO INHERITED FLAGS reversed).
  His argument (under one type `"blah"` is a regex, so without propagation the hole's flags reach nothing) refuted
  my "plain text vs pattern text" split: withdrawn in the record. Rulings gathered for rev 28: hole-reads-capture,
  number-domain, padded-width, hole-flags, flags-propagate.
- Next asked: unset-in-hole (ALGEBRA against the EMPTY readings; ALGEBRA equals PCRE on every run of rev 27.1's
  PART B).
- Frank RULED unset-in-hole: no string (I took his slug answer "i meant what you describe "no string" as. its a
  regex that matches nothing" as the ruling and told him so). His idea: a provided constant for the never-matching
  regex (sibling of "anything"; naming trap: the record's `when` ruling uses "matches nothing" for the EMPTY
  string). Rulings gathered for rev 28: hole-reads-capture, number-domain, padded-width, hole-flags,
  flags-propagate, unset-in-hole. Next asked: construction-line, part (a).
- Frank RULED construction-line: enumerate (after his clarification that "under construction" was not about
  arrays, and his two options; the enumerate line was my candidate, §5.5 "Enumerate go."). lift-order read as
  answered by consequence; under-construction-class closed as an answer-free manager's call (own class).
  Rulings gathered for rev 28 (seven): hole-reads-capture, number-domain, padded-width, hole-flags,
  flags-propagate, unset-in-hole, construction-line. Ideas recorded, not ruled: the label-only group
  `(?<:x>...)`, `padded(rx, length =, pad =)` names, the never-matching constant.
- Frank RULED value-test (the `if` was illustrative; `when` applies to `$y`; no special case: my reading of his
  slug answer, told to him). dollar-warning closed as an answer-free manager's call (the warning stays). Eight
  rulings for rev 28. Next asked: same-name-twice (libpcre2 by ctypes: without `(?J)` error 143; with it `\k<h>`
  reads the first group: `12-1` holds, `12-2` fails).
- Frank RULED same-name-twice ("i agree with your lean": error at the backreference unless `(?J)`). On his
  question the dollar-warning call was WITHDRAWN. NINE rulings.
- LAUNCHED lane predspec28 (opus; worktree worktrees/predspec28, branch lane/predspec28 from c32e93bc6): the rev
  28 fold. Deliver + empty rulings file written first; `lanewatch --follow predspec28` armed. Brief: nine rulings
  quoted; NOT RULED list; every (m) reading of the folded entries to test; premise test = predspec271 evidence
  re-runs byte-identical; not the full restructuring. wake.md rewritten in flight.
