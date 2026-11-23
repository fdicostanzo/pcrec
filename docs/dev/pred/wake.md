# Predicate-language manager: wake-up brief

Rewritten 2026-11-22 (box clock, late night), at the owner's `/close` ("Let's discuss these pain points next
time."), fifth predicate-manager session. Committed docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`). DELIVERED to main: P-19 (r77), P-20 (r82), P-21 (r83:
  default-export, export-list, the name table); main had merged P-20 and was to merge P-21 (tip 75d2318bd) after a
  kit change landed: check `git log --oneline -5 main` and from_main.md.
- ON THE BRANCH, MERGED, UNDER REVIEW: lane predspot's fold of FIVE rulings (tip e6e95a2c5): argument-default (an
  error; the principle piece "a label names a spot"), wrapper-export, transform-export (the convention; his `hide`
  / `identity` pair), program-options, hole-flags. Lint 7,034 / 0; its model
  `docs/dev/lanes/predspot_evidence/predspot_model.py` 27 / 0 (several minutes to run; NAME-GRID 144 cells and
  FLAG-GRID 128 cells, no disagreement).
- REVIEW **r84** (number from main; design mode): coordinator `crit-predspot1122`, round dir
  `$PCREC_TMPDIR/scratch/crit-predspot1122/` (`review.md` when drafted; critic texts in `review/`; `.coord/
  process.md`). See the LAST journal entry for whether the draft had arrived at close; it is NOT RULED.
- IN THE RECORD ONLY, NOT FOLDED (ruled after the r84 freeze): **capture-export** (a named group in a part of a
  composed program is NOT a capture by default; the program-level `capture(path)` asks for one; explicit captures
  returned from the artifact against implicit ones the language needs); **zero-condition-binding** (`c := (0: 5)`
  bound alone: an error, to be reconsidered later; his reasons recorded). And SPELLING notes, not rulings: his
  reading of `[a = A]` (the brackets are the array / grouping; `a = A` the label set of the expression language;
  `[a = A | b = B]`); my four precedence points (the label set looser than SEQ and `&`, tighter than `|`; written
  only inside `[ ]` or directly in a hole, so `${=rx}`; never bare in `( )`): my syntax reading; `[ab = B | A]`
  (six places in core.md) must become `[ab = (B | A)]`; the comma form `[a, b, c]` kept "for now" as `a | b | c`;
  the third small form `A(rx) := /${=rx}/` (`A.rx`, `A.rx.g`) beside hide / identity.
- NEXT, in order: (1) read r84's `review.md` + `process.md`; RULE every disposition (record entry "MANAGER —
  review r84"). (2) ONE opus fix lane cut from this branch (it files the review as
  `docs/dev/reviews/2026-11-22-r84-predspot1122.md` + directory + NOTES index line; ALSO the spelling notes
  above; brief pattern: the predfix83 brief = BOILERPLATE first, every BRIEF_TEMPLATE field, deliver + empty
  rulings file written into the worktree BEFORE launch, `scripts/lanewatch --follow NAME` in the background).
  (3) merge ALONE, lint, `make -s test-plan-lint`, TaskStop; P-22 `done:` in to_main.md (status line; worktrees
  predspot + the fix lane; r84's process notes as proposed skill edits); SendMessage main. (4) ONE opus fold lane
  for capture-export + zero-condition-binding (export statement 5, labels-vs-captures, lib/structural/capture and
  its add-on, caller-ambiguous, the name table's four cells, the zero-binding piece), then its own critic round:
  ASK MAIN FOR THE NUMBER first.
- No cron. Nothing in the box queue (never ours). Worktrees for main to prune: listed in P-20 and P-21; add
  predspot and the r84 fix lane in P-22.

## READ, IN THIS ORDER

1. The skill, section 2. 2. `core.md`, `library.md` whole, `parked.md` scanned (they changed a great deal on
2026-11-22: label-reference re-spelled every example; default-export; the export convention; the flag pieces).
3. The record from "2026-11-22 OWNER, an analogy to validate" to the end (about 35 entries; the LAST TWO are the
JSONL exercise he wants to discuss). 4. `journal.md` from "2026-11-22 (late night) — default-export RULED". 5.
`owner.md`. 6. r84's round dir. 7. `docs/dev/lanes/predspot_report.md`, `predfix83_report.md`.

## FIRST WITH HIM NEXT TIME: the JSONL exercise's pain points (his words at close)

The record entry "2026-11-22 MANAGER — the JSONL capture exercise he asked for" has the library, the search, the
run and seven findings. He wants to discuss them. Mine to bring as questions, in the order of how much each
improves the example (one per turn; grep the record first; a run before any claim):
1. **label-name-hole**: a label named by an ARGUMENT (`row(k, v)` naming its value label for the key): the
   group-name hole exists for rx text; the label-only group is under construction; the label set `[${k} = v]`
   has no name-hole rule.
2. **ambiguity-per-name**: "called more than once" is per MACRO in my call-prefix reading; four calls of
   `json.row` export four different names and `row.ts` is refused. Should the plain-read error be per NAME (a
   name more than one use holds)? It would also relax binding-prefix part 2 for bindings (HIS ruling (a) there
   was on my wording: read it before asking).
3. **capture details**: where `capture(path)` stands in a program; the caller's name for it (the last step; a
   rename); an unset label giving an unset capture.
4. Smaller: exporting from inside an argument (bind first: by design; is the three-definition chain acceptable);
   an optional member (`(row(..) | anything)`: a provided `maybe_row` or a stated idiom); a label inside the
   quotes (`quoted` offers none); duplicate keys (the last member wins by PCRE's order: state it).

## Ruled 2026-11-22 (all in the record; folded unless marked)

array-in-piece (b) · bound-condition (b; "illegal meaning a compiler error") · count-in-set (b: a value left of
`:`; values in the joint form too) · binding-prefix (a group question through a binding's prefix reads every use;
a plain read with several uses is an error) · label-reference: REQUIRED · helper-captures (library helpers set
labels, not captures; `(?<:x>...)` his PROPOSAL) · call-prefix case 1 (the macro's name qualifies its labels) ·
closed-argument (a) · default-export: PROTECTED (a part used alone is available inside its binding, not
exported; reverses hole-export; his C++ analogy) · export-list (`[(=year) = isodate]`; one form, two targets; his
caveat that a binding scopes a label) · program-options (file-scoped `m s n x`, never across an import) ·
hole-flags (weak per-file `i` not propagated; only an explicit `i` inherited at a hole; `m`, `s` no longer
inherited) · argument-default: an ERROR (his principle: "The label is not to the regex abstractly, it's to the
spot in the pattern where the regex is being inserted") · wrapper-export (a) · transform-export: yes ·
capture-export (NOT FOLDED) · zero-condition-binding: an error for now (NOT FOLDED).
Closed by me on the record, told to him, no objection: record-in-some (his words of 2026-11-21); idiom-confirm
(the statement he ruled default-export on was "available locally as `A.h`").
AGREED framing, not rulings: two kinds of name (label, binding) with properties; "captures can have no label".
My corrections recorded: the binding-prefix Class sentence (his 2026-11-17 point 4 named a ONE-use program);
default-export also narrows label-flow (b) and bare-nested-scope case 2 for a binding's user.

## The question queue after the pain points

two-sources' second shape (a name written in a definition that a used part also holds: mostly dissolved by
default-export: confirm with a run, then close or ask); whether `hide` / `identity` are provided names;
`@options(..)`: its spelling, whether it may repeat, weak `i` only at the top; macro variables / macro types /
declared labels as ONE design (the body names `d.year` under label-reference); how a helper "declares" a
capture and the wrapper `capture(name, x)` (the EARLY forms his truths argued against); capture-loop-value;
count-several; zero-in-loop with the occurrences-argument reading; group-truth; every-pass-spelling;
number-in-loop (mostly emptied by `n`); not-test; condition-group; `\k<x>` to a label-only group; older:
tuple-parts, default-imports, export-choice, call-forms, any-case-body. THE SPELLINGS REVIEW (one sitting; new
this session: `(?<:x>...)`, `A(x:)`, `B(d & isodate)`, a value left of `:`, the prefix forms, the export list,
the label set and `${=rx}`, `@options(..)`, `capture(path)`).
For a pcre2-reader, not him: the members of `(?i)k` in libpcre2 per mode.

## Lessons (cases; the rule-shaped ones went to main in P-20 / P-21 as proposed skill edits)

- Three times my leaning needed an EXCEPTION to a rule he had just ruled (bound-condition (a), closed-argument
  (b), weak-meets-weak (a)); each time his consistent read won in one message. Say "this leaning is an exception
  to <ruling>" in the leaning itself; usually that sentence is enough to drop it.
- "X and Y are the same" about two spellings is a claim about matches: run the parting case first (`A.d`
  against `c.d`; he found it in one line).
- His examples can be legal and not mean their gloss (`hits(/\d+/ & (0: <5))`): check-his-regex, show the table.
- An EXERCISE he asks for, done mechanically with a run, produced seven concrete findings in one turn: more than
  a critic round on the same pieces. Offer one when a cluster of rulings has just landed.
- Rulings arrived faster than lanes: R-n files worked while a lane was early; a lane near its end (predref,
  predfix83, predspot) does not see them: check `lanewatch NAME` before writing an R-n, else queue a fresh lane.
- A lane can sit idle on its own background run (predspot, 25 minutes): the watcher exits with rc=10 QUIET; ONE
  nudge by SendMessage ("check the run's output now; reply either way") was enough.
- The NAME-GRID and FLAG-GRID checks (r83 P1) found every answer-level defect no printed-line check reached:
  keep a grid lens in every round on names or flags.
- After every lane merge: run the lint and the newest model on the MERGED branch and name those counts (the
  record grows; a lane's own count is stale by the merge).
- A late idle notification from a stopped lane or coordinator repeats its delivery: no action.
