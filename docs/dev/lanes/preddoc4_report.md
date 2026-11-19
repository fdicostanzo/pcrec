# Lane preddoc4 — review r59's design-bearing findings applied to the predicate documents

Lane preddoc4 (opus), 2026-11-19, branch `lane/preddoc4`, documents only. Brief: apply r59 sections C and D and the
RULING-n status/statement findings (docs/dev/reviews/2026-11-19-r59-preddoc3.md), with the manager's dispositions
and ruling R-1 (docs/dev/lanes/preddoc4_rulings.md). Sections A/B and the appendices belong to the other lane.

## STATE AT HANDOFF

- Tip: the commit that adds this report (above 79729024c). Commits: c3752d738 (G1), 0d6526ac4 (G1b, R-1 restore),
  d096fefb1 (G2, R-1 moves and `defined:`), 79729024c (G3, everything else), then the report commit.
- Rulings file read before each commit and before this report; the last entry is **R-1** (no later R-n).
- `scripts/pred_doc_lint.py`: **checks passed 4573, failed 0** (baseline 4062 at the brief).
- `make -s test-plan-lint`: checks passed 2, failed 0.
- `docs/dev/pred/doc_ratchet.tsv`: unchanged (no diff on the branch).
- Evidence model: 16 checks, 0 failed; 16 of 16 sabotages caught.
- R-1's record title ("2026-11-19 OWNER, refining where provided names live ...") is on lane/pred-rev28, not in this
  worktree; NO piece here cites it, so the lint has no failure on it. A `rulings:` item citing it can be added after
  the merge into pred-rev28 (core/operators/statements and the lib/builtin entries are the natural homes).
- `git reset --hard HEAD~1` (to drop the PLACE-1 commit after R-1) was refused by the permission layer; the PLACE-1
  move was reversed FORWARD instead (0d6526ac4), so c3752d738 stays in history. Net effect on the files is R-1's.

## FINDINGS APPLIED

| finding | done | commit |
|---|---|---|
| PADDED-BODY (READ-4) | body is `padded(rx, n) := (rx & /(?s:.){${n},}/) \| (/0*${rx}/ & /(?s:.){${n}}/)`, n through count holes; new bullet in core/holes/insert (a bare parameter in a literal is literal text); details readings/rejected rewritten; scan of every library and core body: padded was the ONLY body with an un-holed parameter. Built mechanically from its printed text (PART PD) | 79729024c |
| ZERO (READ-3, RULING-8) | match-so-far is the one deciding piece for `0`; numbers' statement points at it; the loop case is the open sub-piece core/conditions/match-so-far/in-loop (slug zero-in-loop), both candidates RUN (PART ZL); bare-condition keeps its facts, its parentheses bullet → `see: core/spellings/condition-parentheses` | 79729024c |
| NEGATION (READ-2) | new core/filters/negation (ruled 2026-11-18): one piece for `NOT`, `!` and lower-case `not`; kinds example now `!/7\d*/ & !/8\d*/`; bindings names `NOT` as the one alphabetic exception; when `needs:` negation (its body legal); peek's `NOT peek` bullet points at it; anything `& NOT X` → `& !X`; not-test stays open | 79729024c |
| PRIMITIVES-MISSING (READ-1/6/8/15, COMPB-1, PLACE-3) | new pieces: core/values/comparisons, core/values/tuples, core/values/computed-labels, core/values/metadata; lib/counting/some, lib/counting/count, lib/counting/every-pass | 79729024c |
| COMPB-2 | new section lib/assert, piece lib/assert/assert (ruled concept, native, `modes: n/a`) | 79729024c |
| COMPB-3, READ-11 | lib/builtin/pattern (reading), lib/builtin/eval (under-construction); `@options` and the assert effects on the statements list | 79729024c |
| COMPB-4 | core/modules/standard-library (reading, blessed callouts a lean bullet), core/modules/naming (ruled) | 79729024c |
| COMPB-8 (ruled label setting) | occurrences: the per-call hit name bullet + its `rulings:` item | 79729024c |
| COMPB-9 | library header: days/weekday_of/days_in/luhn are planned standard-library content; core/modules/standard-library names them | c3752d738, 0d6526ac4, 79729024c |
| PLACE-1 | REPLACED by R-1: no core/builtins; every call-form provided name in the library; enumerate (+ class-index), import (+ filter) moved core → lib/builtin with `was:` lines; core users got `see:`; `defined:` on every library piece; "primitive" out of base text | 0d6526ac4, d096fefb1 |
| PLACE-2 (a)-(d) | lib/control/atomic; the whole-text idiom to lib/search/occurrences; negated-class's second `join` definition → pointer; anchored fact → pointer | c3752d738 |
| READ-13 | unpadded, json.quoted, rx optional-loop deleted into `rejected:` with `was:` lines on padded/quoted/repeat; provenance phrases reworded | c3752d738, 0d6526ac4 |
| READ-5 | month_numbered: `months := [mname = [...]]` (no `join`); `needs:` computed-labels + metadata | 79729024c |
| READ-7 | core/values/reads' bullet replaced by the scope rule (a reading tied to bare-condition-labels) | 79729024c |
| READ-9 | holes intro no longer says "complete"; value's last bullet → sub-piece core/holes/value/other-positions; flags-in-filter → open sub-piece core/holes/flags/in-filter | 79729024c |
| READ-10, READ-16 | one numbered-warning trigger (the record's accepted proposal, "Agree. Good warning"); count hole's copies stated as `(?\|...)` in core; library repeat example writes the same | c3752d738, 79729024c |
| READ-12, READ-14 | map's TYPE-members bullet removed (history line); hole-export statement says "Outside a binding" + `needs: core/labels/export` | 79729024c |
| READ-17 | the 11 meaning-bearing `see:` lines added (modes, table, group-truth, labels-vs-captures, export, form, two-valued, in-sequence, kinds, reads, one-type, functions, class-order) plus default-set/members → peek and the new pieces' `see:` lines | 79729024c |
| READ-18 stage 1 | "his words in full" block removed from explicit-exceptions (details keeps it); class-positions' candidate runs moved to details (the base keeps the question and the candidate names); any_case's candidates shortened | 79729024c |
| RULING-1 | stated-behaviour → `reading`, statement restated as the manager's general form of padded's ruling; its second rulings item reduced to his words "i agree with your lean" | 79729024c |
| RULING-2 | exact-wording deleted; composed-at-point details carry `was:` + history | 79729024c |
| RULING-3 | caller-ambiguous narrowed to (a) vs (e) on the two cited export rulings; (b)-(d) into `rejected:` | 79729024c |
| RULING-6 | conservative-first item marked `(class: OBSERVATION)`; general-rules' class a reading | 79729024c |
| RULING-7 | nothing-outside-domain restated as arithmetic's; the wider reach a reading | 79729024c |
| RULING-8 | see ZERO | 79729024c |
| condition-group (residual) | open sub-piece core/conditions/quantified/group | 79729024c |
| PLACE-7 | partly, through its overlaps: atomic one home, NOT one home, `0` one home, some/count homed | 79729024c |

READ-18 bytes (before = at the brief; after = the tip). The stage-1 moves took about 3 KB out of core.md, but the new
pieces added more, so the base files grew:

| file | before | after |
|---|---|---|
| core.md | 93,934 | 100,556 |
| core_details.md | 131,632 | 148,018 |
| library.md | 28,209 | 38,219 |
| library_details.md | 45,555 | 61,518 |
| parked.md | 17,786 | 17,786 |
| parked_details.md | 84,664 | 84,664 |

## FINDINGS NOT APPLIED

- PLACE-5: PLAN (an owner question, below). PLACE-8, the COMPB general form, READ-18 stages 2+: PLAN, as ruled.
- PLACE-2 (e), operators as bodies: an owner question, below.
- COMPB-8 (names) / COMPB-10 leans (sort/unique, json.row, any_order, file_literals): PLAN, as the review proposes.
- EXAMPLE-1 (one-item FIND-ALL witnesses; HOLDS-only WHOLE lines): DOC (low), not in this lane's disposition list;
  every NEW example line here has at least two FIND-ALL items and a FAILS case where one exists.
- RULING-4, RULING-5 (paraphrased quotes in four `rulings:` items): quote fixes, not status or statement; left to the
  section A/B lane. (core/modules/import's item moved with its entry to lib/builtin/import unchanged.)
- PLACE-4, PLACE-6/TUPLE-PARTS: section B/A. The tuples piece points tuple-parts at core/modules/positional as open.

## PIECES ADDED AND MOVED

Moved (with `was:` lines): core/arrays/enumerate → lib/builtin/enumerate; core/arrays/class-index →
lib/builtin/enumerate/class-index; core/modules/import → lib/builtin/import; core/modules/import-filter →
lib/builtin/import/filter; the PLACE-1 move to core/builtins and back (no `was:` lines, per R-1).

Deleted into `rejected:`: lib unpadded, json.quoted, rx optional-loop (READ-13); core/principles/exact-wording
(RULING-2, `was:` on composed-at-point).

Added, core: core/values/comparisons (ruled 2026-11-18), core/values/tuples (ruled 2026-11-16),
core/values/computed-labels (reading), core/values/metadata (reading; 1-based ruled), core/filters/negation (ruled
2026-11-18), core/conditions/match-so-far/in-loop (open zero-in-loop), core/conditions/quantified/group (open
condition-group), core/holes/value/other-positions (reading), core/holes/flags/in-filter (open flags-in-filter),
core/modules/standard-library (reading), core/modules/naming (ruled 2026-11-15).

Added, library: lib/builtin section, lib/builtin/pattern (reading), lib/builtin/eval (under-construction),
lib/control/atomic (PLACE-2a), lib/counting/some (ruled 2026-11-15), lib/counting/count (ruled 2026-11-15),
lib/counting/every-pass (open every-pass-spelling), lib/assert section and lib/assert/assert (ruled 2026-11-14).

Status calls the reviewer may question:
- core/modules/standard-library is `reading`, not `ruled` as the review's COMPB-4 says ("RULED CF:38"): his words sit in
  the record's informal 2026-11-12 discussion "before the formal start", so they are quoted under `readings:`.
- comparisons' unary-only rule is quoted as the draft's RULED status; the record line is the manager's summary, so it
  is a reading in the details entry.

Bodies corrected: `padded(rx, n)` (count holes). Also changed: `months` (no `join`), the occurrences reading's body
text (`${min}`), the library repeat example's expansion (`(?|`), `atomic(X) := /(?>${X})/` written as a body.

Natives (the language's kernel list; all other 23 library pieces are `defined: language`, 8 are `defined: ?` and
every one of those is open or under-construction):

| piece | why native |
|---|---|
| lib/builtin/enumerate | lists an rx's strings; no expression walks an rx |
| lib/builtin/import | reads library files at compile time |
| lib/builtin/pattern | reads a group's written pattern |
| lib/modifiers/any-case | native for now, by his ruling (body open) |
| lib/counting/some | a question over a loop's passes |
| lib/counting/count | a count over a loop's passes |
| lib/counting/occurs | a capped counter over passes |
| lib/strings/join | walks an array's members |
| lib/strings/left | string slicing |
| lib/strings/strlen | a string's length as a value |
| lib/assert/assert | a compile-time emptiness check |
| lib/records/records | a compile-time search over a text |
| lib/records/param | supplied by the caller at run time |
| lib/records/file-text | reads a file at compile time |
| lib/structural/each | compile-time tools over spelled arrays |

Borderline kept in the core: the effects `@warn` and `@export` (an `@` statement, not a call-form name; R-1 does not
name them); group-truth (a rule about questions, not a name); core/values/functions (a rule).

## MANAGER READINGS TESTED

1. **R-1's reading** — SUPPORTED (PART R1): no core piece is a call-form name; all 46 library pieces carry `defined:`;
   15 native (table above). Sabotage s15 caught.
2. **Every name CALLED in a base example or body has a piece** — SUPPORTED with listed exceptions (PART R2, 52 names):
   bound in their own example (`pair`, `m`, `f`, `date_in`, `x`, ...); a parked idea (`cartesian`); names that appear
   only in a worked example or as rejected spellings (`days`, `weekday`, `weekday_of`, `days_in`, `luhn` — planned
   standard-library content; `lex_ge`, `all_matches`, `concat`, `unpad`, `check` — rejected or alternative
   spellings; `even` — his example of a filter on a count). Before G3 it failed on `count` and `some`. Sabotage s16
   caught.
3. **Every corrected body, built mechanically from its text, reproduces its printed example** — SUPPORTED: PART PD
   parses `padded`'s body from library.md and builds it (both call forms, three modes); PART AT does the same for
   `atomic`. Sabotage s1 (the old `{n,}` text) and s2 caught.

## OWNER QUESTIONS LEFT

- zero-in-loop: inside a loop body, does `0` start at the pass or at the rx's start? (core/conditions/match-so-far/in-loop; both run)
- caller-ambiguous: (a) vs (e) (core/labels/export/caller-ambiguous).
- every-pass-spelling: is there a name for "every pass meets c"? (lib/counting/every-pass)
- condition-group: core/conditions/quantified/group.
- flags-in-filter: core/holes/flags/in-filter (his 2026-11-19 remark is quoted; not taken as a ruling).
- PLACE-2 (e): operators as bodies over the hole: a reading for him, not a move.
- PLACE-5: consuming-test and nullable-hit are warnings keyed on library macros while macro-warning is parked, and
  its trigger has fired: un-park macro-warning, or keep the two as compiler warnings?
- (unchanged, still open: not-test, tuple-parts, class-positions, default-set members, any-case-body.)

## EVIDENCE AND COMMANDS

Files: docs/dev/lanes/preddoc4_evidence/{preddoc4_model.py, preddoc4_model.out, preddoc4_sabotage.out, CLAUDE.md}.
The model is standalone python `re`, using preddoc3c's path engine plus a body builder. PARTS: PD AT KI CM TU NE ZL
SO CO ME CL PT RP R1 R2 DOC. Every new or changed example line is that script's output, verbatim in the document
(PART DOC).

    W=/home/pcrec/projects/pcrec/worktrees/preddoc4
    (cd $W && timeout 60 python3 -I scripts/pred_doc_lint.py)          # checks passed 4573, failed 0
    (cd $W && timeout 300 make -s test-plan-lint)                       # checks passed 2, failed 0
    git -C $W diff c331717a6 -- docs/dev/pred/doc_ratchet.tsv           # empty
    (cd /var/tmp/pcrec-pcrec/scratch/preddoc4 && timeout 600 python3 -I -B \
        $W/docs/dev/lanes/preddoc4_evidence/preddoc4_model.py)          # checks 16, failed 0
    PREDDOC4_SABOTAGE=s1 .. s16 (one at a time)                        # 16 of 16 CAUGHT (preddoc4_sabotage.out)

Limits: conditions and group questions are lowered by hand per example. Python has no `(?|`, so RP runs the copies
as `(?:` (no group inside, so the answers are the same). The R2 name scan is lexical.
