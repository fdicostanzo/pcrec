# Predicate-language manager: wake-up brief

Rewritten 2026-11-22 (box clock, afternoon), fifth predicate-manager session, IN FLIGHT (the owner: "do your
followups and we can continue this conversation later"). Committed docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`). DELIVERED as P-20 (tip = the commit carrying P-20): every
  owner ruling through 2026-11-22 is folded AND reviewed: r77 (filed 2026-11-21) and r82 (filed 2026-11-22, RULED,
  applied by lane predfix82). Lanes predbound, predref, predcall, predfix82 are merged and stopped. Main merges at
  its convenience (P-19 = 399ef98f4 was the previous delivery).
- IN FLIGHT (after P-20, which main has merged and pushed): critic round **r83** (coordinator
  `crit-preddef1122`, opus; round dir `$PCREC_TMPDIR/scratch/crit-preddef1122/`; subject frozen at 3e58abe9e, diff
  from 30ca2520d): the fold of **default-export: protected** and **export-list: yes** by lane preddef (MERGED).
  The subject stays FROZEN until the draft: record only. THEN: rule every disposition (record entry "MANAGER —
  review r83"); ONE opus fix lane (it files the review as docs/dev/reviews/2026-11-22-r83-preddef1122.md, and
  ALSO adds the name table piece and restates the hide-label warning and parked label-hygiene: see the journal's
  last entry); merge; lint; P-21 `done:`; SendMessage main. No cron.
- Lint `python3 -I scripts/pred_doc_lint.py`: 6,645 / 0 at the preddef merge (RUN IT BEFORE NAMING A TIP). The newest evidence
  model is `docs/dev/lanes/predfix82_evidence/predfix82_model.py` (22 checks; it carries the fixed engine: `_x`
  part labels close, a later `&` operand lowered once, uses counted in the definition's text; its SUCCESSOR check
  declares every older model's red). Known limit: a nullable loop body past the minimum is not modelled.
- NEXT: the question queue below, one per turn; a single ruling is folded by hand (record + piece + details +
  lint + the predfix82 model re-run); several, or anything touching labels' sources, by an opus lane and a critic
  round (ask main for the number first).

## READ, IN THIS ORDER

1. The skill, section 2. 2. `core.md`, `library.md` whole, `parked.md` scanned (they changed a great deal today:
the label-reference sweep re-spelled most examples). 3. The record from "2026-11-22 MANAGER — review r77" to the
end (about 20 entries). 4. `journal.md` from "2026-11-22 (about 12:30 EST)". 5. `owner.md`. 6. The reports
`docs/dev/lanes/predbound_report.md`, `predref_report.md`, `predcall_report.md` (readings tested, questions left).

## Ruled 2026-11-22 (all in the record)

- array-in-piece (b): "because B is bound first, its internal references refer only to what can be seen at that
  point"; written in place (SEQ or `&`) it sees the rest of its definition. Folded (predfix77), delivered.
- bound-condition (b): `A := (x: blah)` and `A := /x/ & (y: blah)` are compile errors ("illegal meaning a compiler
  error"); a computed label bound alone goes with them; macro variables `A(x:) := (x: < 2100)` and macro types
  `B(d & isodate) := (year: < 2100)` under construction; `c := (0: 5)` LEFT OPEN by him. Folded (predbound).
- count-in-set (b): a value may stand left of `:` in a condition, in place. Values allowed in the joint form too
  (my reading withdrawn at his question). Folded (predbound).
- binding-prefix: a binding's name is a label prefix (`chars.ch`); a group question through it reads every use;
  a plain read with the binding used more than once is a compile error saying to label the part. Folded.
- label-reference: REQUIRED (a label not written in the referencing definition's own text carries its source;
  the plain idiom included: `isodate & (isodate.year: < 2100)`); "we can relax it later ... although i'm not
  inclined to". His unqualified-after-definition idea: parked by him. Swept (predref): no answer changed.
- helper-captures: "occurences et al should only set labels not captures unless they are so declared"; his
  `(?<:x>...)` is a PROPOSAL (the label-only group is now under construction). Folded (predref).
- call-prefix case 1: the macro's name qualifies a label of its body (`hits.hit`). In predcall.
- record-in-some: CLOSED BY ME on his words of 2026-11-21 (told to him; he did not object).
- closed-argument (a): the caller's `A.d` is legal exactly where `d` is visible through the call (this settles
  call-prefix case 2). My readings from r82, marked as mine in the documents: a path to an invisible label is a
  compile error; a value entry inside a group question is refused for now; the index through a prefix across `&`
  is refused for now; nested paths compose; a set reading a label, bound alone, is the bound-condition error.
- NOT rulings: "[ c = B(A) ] does not allow
  c.A" (his statement); declaring a binding's labels (his idea, parked); "critical is the @assert macros" (his
  priority; two gaps noted: what a search reports, a label's value on a subject).

## The question queue (one per turn; grep the record AND read the same-day later entries first)

1. **two-sources** (from r82; an open piece core/labels/paths/two-sources with the run lines for `7-3` and
   `1,7`), then **idiom-confirm** (open piece core/labels/paths/one-use-read; his 2026-11-17 point 4 made the
   one-use `A.h` an error; I took the isodate idiom on his silence). closed-argument is RULED (a).
2. **zero-condition-binding** (`c := (0: 5)` bound alone; left open by him: do not push; ask when an example needs
   it), **zero-in-loop** WITH the occurrences-argument reading (three candidates part: predfix77 OCCZERO).
3. Macro variables / macro types / declared labels as ONE design (his alternatives; restriction (i) intersection
   or (ii) a promise checked at the call; under label-reference the body names `d.year`); how a helper "declares"
   a capture; the capture add-on's form.
4. count-several; capture-loop-value; group-truth; every-pass-spelling; number-in-loop; caller-ambiguous (helper
   labels no longer reach the caller); not-test; condition-group; `\k<x>` to a label-only group; a label and a
   binding of one name under a prefix.
5. Older: tuple-parts, default-imports, export-choice, call-forms, any-case-body (held by me). THE SPELLINGS
   REVIEW (one sitting; new today: `(?<:x>...)`, `A(x:)`, `B(d & isodate)`, a value left of `:`, the prefix forms).
For a pcre2-reader, not him: the members of `(?i)k` in libpcre2 per mode.

## Lessons (cases; rule-shaped ones go to main as proposed skill edits)

- I leaned (a) on bound-condition and (b) on closed-argument from "the piece owns nothing / the caller owns A";
  both times his scope rule ("bindings define scope"; "what would A.d mean if d no longer was visible?") was the
  consistent read. When a leaning needs an EXCEPTION to a rule he ruled the day before, say so in the leaning.
- I told him two spellings were "the same label" without a run; he found the case (B defines its own `d`) in one
  line. A sentence of the form "X and Y are the same" is a claim about matches: run the parting case first.
- His examples can be legal and still not mean their gloss (`hits(/\d+/ & (0: <5))`: the inner test chooses the
  hits). check-his-regex paid twice today; show the table, he answers "right".
- Rulings arrived faster than lanes ran: R-n files worked for predfix77 (3) and predbound (3); predref finished
  before its R-1 was written, so R-1 became a fresh small lane (predcall). Write the R-n the same minute as the
  record entry, and check the lane has not already delivered.
- After a lane merge the lint count grows with the record: name the count from a run on the merged branch.
- A lane's late idle notifications repeat its delivery: no action.
