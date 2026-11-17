# condkind — a condition as its own kind, the owner's SQL model worked out (lane report)

EXPLORATION, rules nothing (owner, COND-FAMILY 2026-11-16 20:44: "Go. Purely exploration"). Deliverable:
`docs/design/condition_kind.md`. Evidence: `docs/dev/lanes/condkind_evidence/` (`condkind_model.py`, `rev22_ref.py`,
`condkind_model.out`). No edit to `predicates_draft.md` (rev 22) or to any ruling.

## STATE AT HANDOFF

- Branch `lane/condkind`, cut from main @ 5c4287266; the tip is the last commit on the branch.
- Delivered: `docs/design/condition_kind.md` (new); `docs/design/CLAUDE.md` gains its line (the line for the
  COND-FAMILY files was shortened to stay under the 12,288-byte limit: `scripts/check_claudemd_size.sh --all` clean,
  12,284 bytes); `docs/dev/lanes/condkind_evidence/` (two scripts, the forward output, a CLAUDE.md); this report and
  its history-index line in `docs/dev/history/claude_md/docs__dev__lanes.md`.
- PREMISE TEST passed: `grep -c "OWNER GO — definition-lane" docs/design/plan_row_bodies/COND-FAMILY.md` = 1; `timeout
  300 python3 -I docs/dev/lanes/predspec22_check.py` from the scratch dir printed output BYTE-IDENTICAL to the
  committed `predspec22_check.out` (`diff` empty; e.g. PART D "differ 28 of 1100", PART B "FAIL -> HOLD on 8 lists").
- Rulings file `docs/dev/lanes/condkind_rulings.md`: read before each commit and before this report: EMPTY (no R-n
  applied).
- Nothing built; `make` not run. Every evidence run is under `timeout`, from `$PCREC_TMPDIR/scratch/condkind/`.

OWED: none.

## THE DEFINITION IN BRIEF

- SOURCE row: a whole subject (S1). A statement (pattern, regex, program) returns RESULT rows per source row: one
  match (PCRE's one reading) with set-once labels as columns and the pairing loop's passes as a NESTED table (R1); a
  loop that ran zero times gives one pass of NULLs where a plain condition looks (a LEFT JOIN) and no pass where a
  group question counts.
- A CONDITION is a test of ONE result row answering TRUE / FALSE / UNKNOWN; `P & c` = `select * from (P) where c`
  keeps TRUE. Unmarked absent label = NULL -> UNKNOWN; default = COALESCE; `&` of conditions = AND, so order-free and
  monotone when every condition is one-row; record = `&` and record-is-product hold by construction.
- TWO NOTS: the condition's NOT (three-valued, inside the where-clause) and the statement's complement `!Q` (the
  source rows with no row of Q: his best guess, an anti-join). They part on UNKNOWN rows (NOT drops, `P & !(P & c)`
  keeps), on repeated labels, and per source row vs per result row. The set complement `(h: !S)` is a third thing,
  equal to NOT c on one set-once unmarked label.
- Run (`condkind_model.out` PART 1-2): R1 vs a pass-row reading R2 of the plain condition differ on 500 of 1,110 RZ
  subjects (`0;0;5`) and 10 of 43 lists; S1 vs S2 (span rows) differ on the searched complement on 9,140 of 11,110 T2
  subjects (`9:30`; 1,970 vs 11,110: review r30 K named); NOT vs the complemented pattern differ on 10 of 1,110 RZ
  (zero passes), NOT vs the set complement on 500.

## CONSTRUCTS

Every construct the brief lists is stated in the model in the note's section 3 table; each is a test of one row
EXCEPT the ruled optional mark, which reads the program's other rows (a subquery over the statement; the STOP RULE
names no construct the model cannot express, and says this one does not fit "where c" over one row). Notable:
- a missing part under DICTIONARY ORDER: ruled FAILS on `10` against `padded(>= (9, 30))` with m absent and
  unmarked, where SQL's own row comparison would say TRUE: absent-rule (2) is a choice stricter than SQL;
- group questions are aggregates over the row's own nested passes (one row);
- `when(c, p)` = SQL's `case when c then p else true end` (rev 22's body, row-level "c is not true");
- `$a` NULL -> UNKNOWN (e2.2 follows); a default inside one record reaches `$a` (e2.1 follows), across `&` it does
  not (review r30 I survives: the default's scope).

## THE TWO MARKS SIDE BY SIDE

Five candidates run on the same pools (`condkind_model.out` PART 3, PART 4): one-row M1 (any text), M1t (the label's
DOMAIN: its values in matches of the REGEX that defines it, a per-label constant like a SQL column domain), M1a
("IS NULL OR"), and the ruled mark M2 with two transparency units (M2c the text's, per pass; M2r review r30 V4's).
- M2c = rev 22's own engine on all 346 programs of rev 22's pools (0 of 21,452 program-subject pairs differ), and it
  reproduces rev 22's documented counts and review r30's RULING-2 (54 of 1,210), RULING-7 (30 of 355), SIMULATE-9
  (54 of 220): the independent control.
- M1a is out on the ruled text: it stops testing a joint condition's other labels (T2 `5`, 18 subjects) and reverses
  zero-pass-empty (91 subjects).
- M1 (any text): monotone (0 of 1,585 added-condition pairs admit), no equal-behaviour or record split; but answers
  rest on texts the label never holds (`((h, m?): !late)` on `10` HOLDS via m = "x", 90 subjects; `(mnum?: >5)` on
  `-5`, 10 of 40). Against rev 22: 130 of 346 programs, 567 pairs.
- M1t (domain): monotone (0 of 1,585), order-free, record = `&` kept (RULING-7 0); keeps `10`, `-5`, zero-pass-empty
  as rev 22. Costs: domain-scope reverses (`P & (k: "b") & (h?: <5)` on `b` HOLDS), and programs on DIFFERENT regexes
  with the same rows can split (RULING-2 54, as rev 22). Against rev 22: 90 of 346 programs, 369 pairs.
- M2r: rev 22 on its pools (0), no RULING-2/-7 split, but parts from the text's unit on SIMULATE-9 (54 -> 0) and keeps
  mark-in-none's 8 moving lists and 4 non-monotone pairs of 1,585.
- One-witness (two marked conditions on one label vs one condition, 1,100 subjects): M1 54, M1t 45, M1a 0, M2 28.

## RULINGS RE-READ

The note's section 5 classifies each ruling under a one-row mark (M1t) and under the ruled mark. Under M1t: CHANGES
domain-scope (`b`) and the spelling principle's "programs" reading (holds for regexes); MOOT match-context and
mark-narrows; KEPT absent-rule (1)-(4) (with (2) a stated choice), zero-pass-empty and its corner, label-twice,
mark-in-none (its documented property disappears: 0 lists move), not-is-complement's first half; not-is-complement's
second half CHANGES IN ITS REASON (NOT on a condition has a meaning; asked as **condition-not**); FOLLOW
optional-as-loop, zero-pass-record, one-witness, default-reaches-dollar inside one condition, e2.1/e2.2/e1. Review
r30: A, B, C (RULING-6), D, E DISSOLVE under a one-row mark; F, G, H, I, L, M SURVIVE; K is decided by the source-row
choice; C/J's expressiveness (FIXIND-1) survives.

## POPULATION RUNS

From `/var/tmp/pcrec-pcrec/scratch/condkind/`, W = the worktree root:

    timeout 300 python3 -I W/docs/dev/lanes/condkind_evidence/rev22_ref.py rev22_ref.tsv
    timeout 600 python3 -I W/docs/dev/lanes/condkind_evidence/condkind_model.py rev22_ref.tsv > fwd.out
    CONDKIND_SWAP=1 timeout 600 python3 -I W/docs/dev/lanes/condkind_evidence/condkind_model.py rev22_ref.tsv > swap.out
    diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # empty: SWAP-IDENTICAL
    CONDKIND_SABOTAGE=1 (same, forward and swapped) -> the diff shows one line, SIMULATE-9 M2c "holds on 54" vs "holds on 0"

Each run takes under 4 s. Every count quoted in the note and here is from `fwd.out` (committed as
`condkind_evidence/condkind_model.out`) AFTER the swap run printed the same lines; the sabotage shows the swap check
can fail. Headline counts (the note's section 6 has the full table): over 346 rev 22 programs (21,452 pairs) M1 /
M1t / M1a / M2c / M2r differ from rev 22 on 130 / 90 / 139 / 0 / 0 programs (567 / 369 / 600 / 0 / 0 pairs); over 729
programs M1t vs M2c 231 programs (1,055 pairs), M2c vs M2r 0; adding a condition turns FAIL into HOLD in 0 / 0 / 0 /
4 / 4 of 1,585 pairs (rev 22's own engine 3 of 845, `6,`).

## QUESTIONS FOR THE OWNER

Three, each with its current definition, an example and a leaning in the note's section 7; a reply either way wanted.
- **source-row**: is a row of the source the subject or a span? `t2 & !q` searched on `9:30`: subject FAILS (1,970
  hold), span HOLDS (11,110). Leaning: the subject.
- **mark-range**: when a marked label is absent, which values could it have had: any text, its DOMAIN in the regex
  that defines it, or its values in the program (as ruled)? `(mnum?: >5)` on `-5`: HOLDS / FAILS / FAILS; `P & (k:
  "b") & (h?: <5)` on `b`: HOLDS / HOLDS / FAILS. Leaning: the domain (a test of one row; removes review r30 A-E;
  reverses domain-scope by name; 90 of 346 programs move).
- **condition-not**: does `!` on a condition mean the condition's three-valued NOT? On `x` of `/(?<h>\d)?x/`: NOT
  `(h: <5)` FAILS, `(h: !(<5))` FAILS, `P & !(P & (h: <5))` HOLDS; on `0;0;5`: NOT HOLDS, the set complement FAILS.
  Leaning: keep the error, its reason now "one spelling per question", not "no meaning".

## LEFT OPEN

- The default's scope across `&` (review r30 I, **dollar-across-and**, already filed): the model states the choice.
- One-witness persists under every one-row mark except "IS NULL OR" (45 of 1,100 under M1t).
- The exact-unknown reading of an UNMARKED test (the dictionary-order corner) vs absent-rule (2): not asked.
- R3 (every parse a result row), the domain of a non-regular regex under M1t, searched mode beyond the complement:
  not run.
- No critic round run (the manager launches it).
