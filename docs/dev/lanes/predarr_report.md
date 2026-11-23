# Lane predarr — array-vs-passes (a) and joint-in-some folded into the predicate documents

Design-document revision only ([COND-FAMILY]); nothing under src/ cli/ lib/ memfn/ tests/ scripts/ touched. Tier opus.
Branch lane/predarr, cut from lane/pred-rev28 at 96f25d7a0. Not the planned full restructuring.

## STATE AT HANDOFF

- STATE: delivered. Tip: the commit carrying this report (on top of 5b83eee2f and b8719544f, the WIP folds).
- Lint: `python3 -I scripts/pred_doc_lint.py` → `pred_doc_lint: checks passed 5514, failed 0` (the one soft WARN,
  parked.md over its 16 KB soft cap, as at the start).
- Rulings file `docs/dev/lanes/predarr_rulings.md`: rulings file empty (re-read before each commit and before this
  report).
- PREMISE: (1) the lint at the starting tip ended `checks passed 5459, failed 0` (as the brief expected). (2)
  predscope's model re-ran byte-identical against its committed `.out` (no diff), before and after this fold.
  Observed, not a premise: three OLDER models were already red at the starting tip, from folds before this lane
  (preddoc4 R2, `longest_first` with no library piece; preddoc3c DOC, three library lines since changed; predfix61 DOC,
  the bare-nested-scope and class-hole-order lines since changed). After this fold each fails the same check and
  nothing else; preddoc4's printout differs only in echoing the new `defined:` text of some / count / occurs. No
  earlier model asserts the pass reading in a check this fold turns red, so no `evidence:` citation was marked
  superseded by design; lib/counting/some's details note that preddoc4 PART SO's "every pass" wording is superseded
  while its line's answers stand.
- OWED: none

## RULINGS FOLDED

R-A, array-vs-passes (record: "2026-11-21 OWNER RULING — array-vs-passes: a (the group questions and the index read
the array of settings)"), his words whole: "array-vs-passes: in your example, the user chose to set the labels the
same. if they wanted the out-the-loop setting to be separately labeled they could have done so. also, if they wanted
the h5,m3 condition to be held at the same time they could have specified (h,m): (5,3) but they did not. they chose to
use the same labels and therefore that has to have a meaning. for simplicity, and due to the fact that the other
interpretations can be otherwise spelled, i think option "a"". Folded: core/labels/labels-vs-captures/array-vs-passes
(open → ruled 2026-11-21; the three "Settings" lines kept, the three "Passes" lines to rejected in details);
core/labels/labels-vs-captures (the array bullet; a rulings item); lib/counting/some, lib/counting/count,
lib/counting/occurs (statements and `defined:` lines revised from passes to the array; rulings items; ruled
2026-11-21); core/model/places/outermost-view (its reading bullet replaced; the outer-pass-forms reading marked
REPLACED in details); core/model/table/group-truth and lib/counting/every-pass (re-put, still open). His reasons are
quoted in the array piece's details.

R-B, joint-in-some (record: "2026-11-21 OWNER RULING — joint-in-some: agree (a joint entry inside a group question is
refused for now; "same item" is written on the item)"), his words whole: "join-in-some: agree and elegant. that said,
no one would know to write it." Folded as the manager's leaning (c): a joint entry inside a group question is a compile
error for now; "same item" is the on-item label, then a group question on it. In the array piece (a slug
joint-in-some, a rulings item, the line "Same item, on the item"), lib/counting/some, core/values/tuples (a bullet;
rulings items; ruled 2026-11-16 → 2026-11-21), and a pointer in core/diagnostics/looped-compare. "no one would know to
write it" is quoted as an OBSERVATION, not a ruling: the idiom is item 30 of the user-documentation list
(parked/ideas/user-doc-traps, its details entry, with a rulings item). That the refusal's message names the on-item
form is stated in the base as the manager's call. No shorthand is parked.

## MANAGER READINGS TESTED

From the array-vs-passes entry:

- (a) a record of two entries inside a group question is the product of its entries, each over its own array —
  SUPPORTED by the record's run and by his words, WITH A CONFLICT. The model (RECORD) gives `5:1,2:3,` HOLDS under the
  product and FAILS under the passes, as the record printed ("passes WHOLE `5:1,2:3,` FAILS, settings HOLDS"); the
  product against an independent hand regex `(?=(?:\d:\d,)*5:\d,)(?=(?:\d:\d,)*\d:3,)(?:\d:\d,)+`: 0 / 0 / 0 of 5,461
  texts. Line: A record of two entries: WHOLE `5:1,2:3,` HOLDS, `5:3,` HOLDS, `2:1,` FAILS / SEARCHED `2:1, 5:1,2:3,` `5:1,2:3,`@5 / FIND-ALL `5:1,2:3, 2:1, 5:3,` [`5:1,2:3,`@0, `5:3,`@14] (`/(?:(?<h>\d):(?<m>\d),)+/ & some((h: "5", m: "3"))`)
  THE CONFLICT: record-is-product ("record-is-product: absolutely. This is precisely the sort of simplifying
  semantics I'm looking for.", 2026-11-16) makes `(h: A, m: B)` = `((h, m): (A, B))`; inside a group question the
  joint form is now refused (R-B) while the record is legal and means something else. So under (a) record-is-product
  no longer holds inside a group question. His own sentence ("if they wanted the h5,m3 condition to be held at the
  same time they could have specified (h,m): (5,3)") already parts the two spellings. Asked below as record-in-some.
- (b) `count(c)` and `occurs` on a one-entry condition count SETTINGS — SUPPORTED (CHANGED, EMPTY); on several
  entries what is counted is not stated — SUPPORTED (no record line; the model refuses to compute it, QUESTIONS).
  Asked below as count-several.
- (c) the group questions are false / zero on an EMPTY array, replacing "false where the loop made no pass" —
  SUPPORTED as a reading (EMPTY). It moves an answer only for a negated condition, where a pass sets nothing:
  An empty array: WHOLE `,` FAILS, `7,` FAILS, `1,` HOLDS / SEARCHED `7, ,` FAILS / FIND-ALL `, 7, 1,` [`1,`@5] (`/(?:(?<d>\d)?,)+/ & some(NOT (d: "7"))`) against the pass reading Passes: WHOLE `,` HOLDS, `7,` FAILS, `1,` HOLDS / SEARCHED `7, ,` `,`@1 / FIND-ALL `, 7, 1,` [`,`@0, `,`@3, `1,`@5] (`/(?:(?<d>\d)?,)+/ & some(NOT (d: "7"))`)
- (d) group-truth with arrays: `NOT some(c)` = `occurs.none(c)` — SUPPORTED, by definition (TRUTH: 0 / 0 / 0 of 364
  texts over `17,`). The record's wording "`NOT some(c)` against `occurs.none(NOT c)` now part on settings, not
  passes" — NOT SUPPORTED as worded: those two part under BOTH readings (28 / 216 / 244 on the array); what moves is
  `occurs.none(NOT c)` itself (array against passes 17 / 237 / 245), because a pass that sets nothing is no longer
  judged. The piece's question ("each pass judged with its own labels") does not survive as asked: the lane PROPOSES
  closing it for one-entry conditions, the several-entry residue asked as record-in-some and count-several. Its status
  is left open (the owner's or the manager's call).
- (e) "same item" without a joint entry is spelled on the item — SUPPORTED (IDIOM): `([ok = item & ((h, m): ("5",
  "3"))] | item)+ & some((ok: anything))`, item := `/(?<h>\d)(?::(?<m>\d))?,/`, against the by-item reading of the
  joint 0 / 0 / 0 and against a hand regex `(?:\d(?::\d)?,)*5:3,(?:\d(?::\d)?,)*` 0 / 0 / 0, of 5,461 texts over
  `53:,`. On the record's four subjects: Same item, on the item: WHOLE `5:3,` HOLDS, `5:1,2:3,` FAILS, `5,2:3,` FAILS, `2:3,5,` FAILS / SEARCHED `x5,2:3,` FAILS / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0] (`([ok = item & ((h, m): ("5", "3"))] | item)+ & some((ok: anything))`, item := `/(?<h>\d)(?::(?<m>\d))?,/`)
  The same four under the rejected pairings: by index By index: WHOLE `5:3,` HOLDS, `5:1,2:3,` FAILS, `5,2:3,` HOLDS, `2:3,5,` FAILS / SEARCHED `x5,2:3,` `5,2:3,`@1 / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0, `5,2:3,`@5] (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/ & some(((h, m): ("5", "3")))`) and by item By item: WHOLE `5:3,` HOLDS, `5:1,2:3,` FAILS, `5,2:3,` FAILS, `2:3,5,` FAILS / SEARCHED `x5,2:3,` FAILS / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0] (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/ & some(((h, m): ("5", "3")))`)

From the joint-in-some entry:

- (a) the refusal's message names the on-item form — UNTESTABLE as a rule (a diagnostic's wording, the manager's
  call); stated so in the base; the model's error text names `[ok = item & ((h, m): (..))]` (REFUSE).
- (b) the idiom on the user-doc list — done: item 30 of parked/ideas/user-doc-traps (its details entry).
- (c) no shorthand parked — SUPPORTED: nothing parked beyond the list item.

The consistency check asked (the array beside the label rules): CONSISTENT. "a reset contributes nothing" and "a name
set before a loop and inside it does not survive the loop" are about the LABEL; the array keeps every setting. On
`/(?<h>\d);(?:(?<h>\d);)*/` and `7;` the label h is unset and the array is [`7`]; the separated list
`/(?<h>\d)(?:,(?<h>\d))*/` on `7` the same (OUTSIDE; the arrays are checked against python `re`'s finditer, ARRAYS).
The two lines now printed side by side in the array piece: Outside the loop: Settings: WHOLE `7;` HOLDS, `1;7;` HOLDS / SEARCHED `x7;` `7;`@1 / FIND-ALL `7; 1;7; 1;` [`7;`@0, `1;7;`@3] (`/(?<h>\d);(?:(?<h>\d);)*/ & some((h: "7"))`) and
Outside the loop, the label beside it: WHOLE `7;` FAILS, `1;7;` HOLDS / SEARCHED `x7;` FAILS / FIND-ALL `7; 1;7; 1;` [`1;7;`@3] (`/(?<h>\d);(?:(?<h>\d);)*/ & (h: "7")`)

## ANSWERS CHANGED

Every printed example in the documents using `some`, `count`, `occurs` or `h[k]`, run under the pass reading and the
settings reading (CHANGED, AVP, HITS):

- lib/counting/some's line: UNCHANGED (one setting per pass, none outside): WHOLE `1,7,` HOLDS, `1,2,` FAILS / SEARCHED `1,2, 7,` `7,`@5 / FIND-ALL `7,1, 2, 3,7,` [`7,1,`@0, `3,7,`@8] (`/(?:(?<d>\d),)+/ & some((d: "7"))`)
- lib/counting/count's `n := count((d: "7"))` line: UNCHANGED.
- lib/modifiers/length's `length(==3)` line: UNCHANGED (one setting of `ch` per character).
- lib/search/hits's "every hit under 100" list (the base prints no program; the lane ran `hits(/\d+/) &
  occurs.none((hit: >= 100))`, a reading): UNCHANGED (`1234` FAILS, `12 34` HOLDS, `12 345` FAILS, `x300 12` FAILS
  under both).
- lib/modifiers/month-numbered: no group question (`mnum := $mname.index` is metadata): nothing to move.
- core/model/places/outermost-view's line: a bare condition, not a group question: UNCHANGED; its reading bullet
  ("Pass tests ... range over the outermost loop's passes") is REPLACED (FOLLOWS from the ruling).
- the array piece's three witnesses: the "(a): Settings" answers stand (now the ruled lines, labels dropped to
  "Two depths: Settings:" etc.); the "(b): Passes" answers become rejected (FOLLOWS). E.g. "Two in a pass" WHOLE `71,`
  was FAILS under passes, is HOLDS; "Outside the loop" WHOLE `7;` was FAILS, is HOLDS; "Two depths" WHOLE `3;4;,5;,`
  was HOLDS, is FAILS.
- his earlier words where the documents state them: lib/counting/some's "at least one pass of a loop meets the
  condition c ... false where the loop made no pass" (2026-11-15) becomes "at least one setting in the array of c's
  label meets c; it is false on an empty array" (FOLLOWS; "empty array" a reading). count's "the number of passes of a
  loop that meet c" becomes "the number of settings in the array of c's label that meet c" (FOLLOWS). occurs' "counts
  a repeated label's passes" becomes "counts the settings of a label" (FOLLOWS).
- a claim that MOVES (a reading): lib/counting/every-pass's candidate "a named group question equal to `some(c) &
  occurs.none(NOT c)`" no longer says every pass: over the array the form says every SETTING, so where the label is
  optional it parts from the item form: Every setting: WHOLE `7,7,` HOLDS, `7,,` HOLDS, `7,1,` FAILS / SEARCHED `7,, 7,7,` `7,,`@0 / FIND-ALL `7,, 7,1, 7,7,` [`7,,`@0, `7,`@4, `7,7,`@9] (`/(?:(?<d>\d)?,)+/ & some((d: "7")) & occurs.none(NOT (d: "7"))`) against The item form: WHOLE `7,7,` HOLDS, `7,,` FAILS, `7,1,` FAILS / SEARCHED `7,, 7,7,` `7,`@0 / FIND-ALL `7,, 7,1, 7,7,` [`7,`@0, `7,`@4, `7,7,`@9] (`/(?:(?<d>\d)?${(d: "7")},)+/`)
- the draft's "`some(c) & occurs.none(NOT c)` equals `REP & c` on 364 texts" (cited in every-pass and occurs
  details) held under the pass reading only (EVERYPASS): marked so in details.

## WHAT MOVED

Found by grep over the base files for `pass`, `passes`, `some(`, `count(`, `occurs`, `h[`:

- core/model/table/group-truth: re-put over the array (statement, body, heading "over the array"; open, 2026-11-21).
- core/model/places/outermost-view: the reading bullet replaced; `see:` the array piece.
- core/labels/labels-vs-captures: the array bullet (the group questions and `h[k]` read this array); rulings item.
- core/labels/labels-vs-captures/array-vs-passes: ruled; rewritten (above).
- core/conditions/form: a bullet (a reading): inside a group question a record and its joint form part.
- core/values/computed-labels: the last bullet ("over a name's settings (its array)").
- core/values/tuples: a bullet, the joint entry refused inside a group question; rulings items; 2026-11-21.
- core/diagnostics/looped-compare: a pointer sentence (joint entry refused inside a group question).
- core/spellings/placeholders: the ARRAY FORM row ("the pass index" → "the k-th setting").
- lib/counting/some, count, occurs: revised (above). lib/counting/every-pass: re-put, two run lines (open, 2026-11-21).
- lib/modifiers/length: the statement ("one setting of `ch` per character"). lib/search/hits: the "every hit under
  100" bullet names its program (a reading). lib/assert/assert: "about a label's settings". lib/structural/sorted:
  "(every setting of the name, his `@x`)".
- parked/ideas/user-doc-traps: details only (item 30, a rulings item).
- UNTOUCHED, with the reason: core/model/match ("for a loop the passes it ran": the path's definition, not a group
  question); core/model/table (a label's value inside a pass); the place table row "a loop body ... each pass" (a
  place, not a group question); core/labels/one-rule (passes as branchings: the label rule; consistent, above);
  core/conditions/in-sequence and core/conditions/pass-start-read (a condition written ON the item: passes still, as
  the brief says); core/conditions/match-so-far/in-loop (`0` per pass: not a group question); core/holes/value and
  core/holes/bare-condition/labels (reads per pass); core/operators/bindings/call-forms ("a call passes": the verb);
  core/labels/export ("pass out": the verb); core/diagnostics/errors and warnings ("can never pass": the verb);
  lib/search/occurrences ("each hit one pass of the label `hit`": the loop template; no group question is defined
  there, and each hit is also one setting); lib/structural/each ("never over a loop's passes": spelled arrays, still
  true); parked/ideas/field-count and default-set (`count(^h)`, `some(...)` over a paused sigil: parked, not in the
  language; their triggers unchanged).

## DRAFT READINGS ADDED

Each is marked "a reading" in the base and listed under `readings:` in its details entry:

- false / zero on an empty array (the array piece, some, count).
- a record of several plain entries inside a group question is the product of per-entry group questions (the array
  piece, core/conditions/form), with its conflict with record-is-product named.
- `count` / `occurs` of several entries: not stated (the array piece, count, occurs).
- `NOT some(c)` and `occurs.none(c)` the same question over the array; `occurs.none(NOT c)` "every setting meets c"
  (group-truth, some, occurs).
- `some(c) & occurs.none(NOT c)` says every SETTING, not every pass (every-pass).
- "every hit under 100" written `hits(/\d+/) & occurs.none((hit: >= 100))` (hits).
- `h[k]` 1-based, as core/values/metadata (the array piece's details).

## OWNER QUESTIONS LEFT

1. **record-in-some** (proposed slug). Inside a group question, is a record of several plain entries (a) the product
   of its entries, each a group question over its own array ("some h is 5 and some m is 3"; his array-vs-passes
   words; record-is-product then holds OUTSIDE group questions only), or (b) the joint form by record-is-product,
   and so refused with the joint entry for now? Leaning (a): it is what his words and the record's run say, and (b)
   would refuse a form he wrote as meaningful. Under (a): A record of two entries: WHOLE `5:1,2:3,` HOLDS, `5:3,` HOLDS, `2:1,` FAILS / SEARCHED `2:1, 5:1,2:3,` `5:1,2:3,`@5 / FIND-ALL `5:1,2:3, 2:1, 5:3,` [`5:1,2:3,`@0, `5:3,`@14] (`/(?:(?<h>\d):(?<m>\d),)+/ & some((h: "5", m: "3"))`) Under (b): a compile error.
   On the optional-m loop under (a): The record form: WHOLE `5:3,` HOLDS, `5:1,2:3,` HOLDS, `5,2:3,` HOLDS, `2:3,5,` HOLDS / SEARCHED `x5,2:3,` `5,2:3,`@1 / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0, `5,2:3,`@5, `2:3,5,`@12, `5:1,2:3,`@19] (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/ & some((h: "5", m: "3"))`)
2. **count-several** (proposed slug). What does `count` (and `occurs`) of a condition of several entries count? (a)
   refused for now, a compile error (conservative-first; can be allowed later without changing an answer); (b) the
   arrays paired by index, which is what joint-in-some just refused for `some`; (c) left to record-in-some's answer
   (under its (a) a count of a product is not one number). Leaning (a). Under (b):
   count-several (b), the arrays paired by index: WHOLE `5:3,2:1,` HOLDS, `5:1,2:3,` FAILS / SEARCHED `5:1,2:3, 5:3,` `5:3,`@9 / FIND-ALL `5:3,2:1, 5:1,2:3, 5:3,` [`5:3,2:1,`@0, `5:3,`@18] (`/(?:(?<h>\d):(?<m>\d),)+/ & (n: ==1)`, n := `count((h: "5", m: "3"))`)
   Under (a): a compile error.
3. **group-truth** (its existing slug), re-put: close it? On the array `NOT some(c)` and `occurs.none(c)` print the
   same answers by definition and `occurs.none(NOT c)` another, on a several-match subject:
   group-truth, `NOT some(c)`: WHOLE `1,,` HOLDS, `7,1,` FAILS, `,` HOLDS / SEARCHED `7, 1,,` `,`@1 / FIND-ALL `7, 1,, 7,1, ,` [`,`@1, `1,,`@3, `,1,`@8, `,`@12] (`/(?:(?<d>\d)?,)+/ & NOT some((d: "7"))`)
   group-truth, `occurs.none(c)`: WHOLE `1,,` HOLDS, `7,1,` FAILS, `,` HOLDS / SEARCHED `7, 1,,` `,`@1 / FIND-ALL `7, 1,, 7,1, ,` [`,`@1, `1,,`@3, `,1,`@8, `,`@12] (`/(?:(?<d>\d)?,)+/ & occurs.none((d: "7"))`)
   group-truth, `occurs.none(NOT c)`: WHOLE `1,,` FAILS, `7,1,` FAILS, `,` HOLDS / SEARCHED `7, 1,,` `7,`@0 / FIND-ALL `7, 1,, 7,1, ,` [`7,`@0, `,,`@4, `7,`@7, `,`@10, `,`@12] (`/(?:(?<d>\d)?,)+/ & occurs.none(NOT (d: "7"))`)
   Candidates: (a) close, answered by array-vs-passes for one entry; (b) keep it open for the several-entry case
   (then it is record-in-some and count-several). Leaning (a). The status is the owner's or the manager's.
4. **every-pass-spelling** (existing, still open), re-put: its candidate (b) "a named group question equal to
   `some(c) & occurs.none(NOT c)`" now names every SETTING; the lines are in lib/counting/every-pass. No new leaning.
5. Not asked (the brief): a provided shorthand for the "same item" idiom; nothing parked.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predarr_evidence/predarr_model.py`: 17 checks (CONTROL, ARRAYS, OUTSIDE, AVP, RECORD, JOINT,
  REFUSE, IDIOM, EMPTY, TRUTH, EVERYPASS, CHANGED, HITS, QUESTIONS, RECLINES, QUOTES, DOC). The lowerer builds every
  regex from the program text; the matcher's log builds every array of settings and every pass mechanically; the
  library bodies `hits`, `chars`, `nchars`, `anything` are read from library.md. Controls not sharing the matcher:
  python `re` on hand regexes (CONTROL, RECORD, IDIOM, HITS), `re.finditer` for the arrays (ARRAYS), the record's
  lines (RECLINES) and his quoted words (QUOTES). Every three-mode line it formats is found verbatim in the documents,
  the four owner-question lines in this report (DOC).
- `predarr_model.out`: the clean run, `predarr_model: 17 checks, 0 failed`.
- `predarr_sabotage.out`: s1..s17, each run alone, each CAUGHT by its target check, no traceback.
- Commands (W = the worktree): `timeout 110 python3 -I -B W/docs/dev/lanes/predarr_evidence/predarr_model.py`;
  `PREDARR_SABOTAGE=sN` the same; `(cd W && python3 -I scripts/pred_doc_lint.py)`; predscope's re-run:
  `timeout 110 python3 -I -B W/docs/dev/lanes/predscope_evidence/predscope_model.py` diffed against its `.out` (no
  diff).
