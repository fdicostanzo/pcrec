# predref — the label-reference sweep, the flat-read statements, helper-captures folded

Lane predref (opus), branch lane/predref cut from lane/pred-rev28 at 915b47e64. Design only; docs only; no build
go. Not the planned full restructuring.

## STATE AT HANDOFF

OWED: none

- Commits: da1550f72 (WIP: the sweep, the statements, the fold, the new pieces) and the final commit (the
  evidence, the on-item and hit lines, this report, the history line).
- Rulings file `docs/dev/lanes/predref_rulings.md`: empty at every checkpoint (last read before the final commit);
  no R-n applied.
- Premise test: (a) `python3 -I scripts/pred_doc_lint.py` at the worktree root: "checks passed 6088, failed 0";
  (b) `timeout 120 python3 -I docs/dev/lanes/predbound_evidence/predbound_model.py | tail -1`: "predbound_model:
  21 checks, 0 failed"; (c) the record's last entry begins "2026-11-22 OWNER RULING — helper-captures". All held.
- Final tree: the lint prints "pred_doc_lint: checks passed 6183, failed 0"; `make -s test-plan-lint` is clean;
  the model prints "predref_model: 8 checks, 0 failed".
- predbound's own model now has one red check: "predbound_model: 21 checks, 1 failed (DOC)". Its DOC looks for the
  old metadata line `/${days}/ & (w.index: >= 2)`, which this lane re-spelled. My RESPELL check covers that line
  (old bare answers = new answers). predfix77's model already stopped at load before this lane (predbound's
  report).
- Not touched: plan.md, decisions.md, known_issues.md, the record, docs/dev/pred/*, reviews, skills, other
  lanes' evidence.

## RULINGS FOLDED

- label-reference, record "2026-11-22 OWNER RULING — label-reference: required (...)". His words: "label-reference:
  required. we can relax it later as you say although i'm not inclined to. (i wrote then deleted an idea that if
  you defined isodate := ... above the binding then later usages of it in the same "program" could refer to isodate
  labels without qualifications but i'm not so sure of it so i will park it)".
  - (A) The sweep: every printed program in core.md, library.md and parked.md was checked. 15 distinct program
    spans were re-spelled (table in WHAT MOVED). The plain idiom is included: `isodate & (isodate.year: ...)`.
  - (B) The flat-read statements were rewritten so that what a flat read meant is what `binding.x` means:
    - core/labels/export/flat-read-outside: the statement and the heading;
    - core/labels/export: statement 3;
    - core/holes/labels: two bullets;
    - core/holes/bare-condition/nested-scope: example 1, his quote kept whole and the new spelling beside it;
    - core/labels/paths/label-reference: its two "next lane" bullets.
  - `grep -n 'read flat\|Read flat'` over the base files finds nothing (model MARKS).
- binding-prefix (already folded by predbound): used for `pub.h`, `pair.x`, `date.v`, `time.h`, `days.w.index`,
  `year.v`, `A.d`. Twice-used `item` in the on-item line: its part is labelled `[it = item]`, as the ruling's
  part 2 requires.
- helper-captures, record "2026-11-22 OWNER RULING — helper-captures: the library's helpers set labels, not
  captures, "unless they are so declared"; a PROPOSAL of the label-only group `(?<:x>...)`; an example to validate".
  - The ruling: "occurences et al should only set labels not captures unless they are so declared."
  - The bodies of `occurrences` and `hits` now write `(?<:hit>...)`.
  - The label-only group moved out of parked into core/labels/label-only-group, under construction. His proposal
    is quoted with both record titles (the two of 2026-11-18 and this one).
  - His example is printed in lib/search/occurrences. The four pasted run lines are in lib/search/occurrences
    (two) and lib/search/hits (two). Each is reproduced by the model from the program text, with the sentence
    that a test on the hits belongs after the atomic `hits` or inside the argument.
- Re-dating rule applied (doc_format.md: "the date is the status date"; a ruling that changes a piece rewrites
  it in the same commit): a piece whose text a ruling of today changed takes the date 2026-11-22. A re-spelled
  example line counts, as a change made by label-reference, and each such ruled piece gains a `rulings:` item
  citing the ruling. A pointer-only edit keeps its date: core/spellings/placeholders stays at 2026-11-19, since
  only its table cell's tag changed.
  - Re-dated: alternation, atomic, export, flat-read-outside, caller-ambiguous, tuples, metadata, holes/labels,
    bindings, occurrences, hits, capture, capture/add-on.

## MANAGER READINGS TESTED

- (a) "known textually" (a bare name is a label written in the definition's own text; the same for `$x`):
  SUPPORTED as rule-as-code, by two checks.
  - SCAN, the textual checker, runs over 203 program spans. The written labels are the groups in a literal and
    the part labels `[x = ..]`; the reads are left of `:`, joint entries and `$`.
  - The model's lowering check (predbound's source_check) refuses every old spelling (RESPELL; sabotage s5
    caught). The sabotage s1, a planted bare read, is caught.
- (b) the conservative forms (call-prefix):
  - (1) a call is labelled: SUPPORTED (HITS: `[h = hits(/\d+/)] & (h.hit: <5)` reproduces the record; the bare
    `hits(/\d+/) & (hit: <5)` is refused).
  - (2) an argument that is a binding goes through its name: SUPPORTED (RESPELL: example 1, `C := B(A) & (A.d:
    <100)`).
  - (3) an argument written in place is the caller's text, read bare: SUPPORTED (LABELONLY: `hits(/a(?<g>x)?/) &
    (g: "x")`, its printed line).
  - (4) a parameter's label is not nameable (ruled 2026-11-21): no program needed it except his two quoted
    alternatives, which are left as written.
- (c) no answer changes, only spellings:
  - SUPPORTED for the 10 re-spelled run lines (RESPELL). The old program read bare and the new program give
    identical answers in every mode, the annotated label values included, and the old program is refused under
    the rule.
  - SUPPORTED for the four prose answers of "Every hit under 100" (HITS).
  - UNTESTABLE for the four rule-sentence spellings with no run: the three isodate forms (isodate has no body
    here) and `A & (B & (B.h: ..))`.
- (d) helper-captures covers every provided body: SUPPORTED as a census (LABELONLY).
  - library.md's provided bodies that write a group in rx text are `occurrences` and `hits` (now label-only) and
    `capture` (a hole-named group; left: capturing is its purpose, marked as a reading).
  - `list_of`, `endsWith`, `peek` and the rest write no group of their own; their examples' groups are users'
    literals and stay captures.
  - "so declared" joins lib/structural/capture/add-on.
- (e) the label-only group is a label under every rule and never a capture: SUPPORTED as run (LABELONLY).
  - `(?<:hit>...)` against the old `(?<hit>...)` body: 0 / 0 / 0 differing on four programs.
  - `hit` is no capture now (it was before), while the users' `g` and `n` stay captures. Sabotage s4 was caught.
  - `\k<x>` to it: UNTESTED (stated as a reading: a compile error for now).
- (f) caller-ambiguous: stated (the program never reads h bare across `A & B`, and helper labels are no
  captures). UNTESTED: it is a statement about which programs raise the question.

Not supported: none.

## ANSWERS CHANGED

None. Every re-spelled line gives its old printed answers in every mode (RESPELL, HITS), and no ruling was
needed to carry a move.

## WHAT MOVED

Re-spelled programs. All 15 distinct spans that the checker flags at 915b47e64 and no longer flags; the list is
the model's "re-spelled" lines:

| tag | old reference | new reference |
|---|---|---|
| core/patterns/alternation | `(B \| A) & (l: <20)` | `[ab = B \| A] & (ab.l: <20)` (run) |
| core/patterns/atomic | `atomic(B \| A) & (l: <20)` | `[ab = atomic(B \| A)] & (ab.l: <20)` (run) |
| core/labels/labels-vs-captures/array-vs-passes | `[ok = item & ((h, m): ("5", "3"))] \| item` | `[ok = [it = item] & ((it.h, it.m): ("5", "3"))] \| item` (run; `item` used twice, so labelled) |
| core/labels/export | `pub & (h: <5)` | `pub & (pub.h: <5)` (run) |
| core/labels/export/flat-read-outside | `pair & (x: <5)` | `pair & (pair.x: <5)` (run) |
| core/labels/export/flat-read-outside | `date & (v: <5)` | `date & (date.v: <5)` (run) |
| core/values/tuples | `time & ((h, m): >= (9, 30))` | `time & ((time.h, time.m): >= (9, 30))` (run) |
| core/values/metadata | `/${days}/ & (w.index: >= 2)` | `/${days}/ & (days.w.index: >= 2)` (run) |
| core/holes/labels | `/${year}-x/ & (v: >= 2000)` | `/${year}-x/ & (year.v: >= 2000)` (run) |
| core/holes/bare-condition/nested-scope | `C := B(A) & (d: <100)` (the run line) | `C := B(A) & (A.d: <100)` (run; his quote kept) |
| core/labels/paths | `A & (B & (h: ..))` | `/(?<h>\d)/ & (/(?<h>\d)/ & (h: ..))`, beside `A & (B & (B.h: ..))` (a reading, not run) |
| core/operators/bindings | `isodate & (year: ...)` | `isodate & (isodate.year: ...)` (no run) |
| core/operators/bindings | `isodate & (year: years)` | `isodate & (isodate.year: years)` (no run) |
| core/operators/bindings/macro-types | `x & isodate & (year: < 2100)` | `x & isodate & (isodate.year: < 2100)` (no run) |
| core/operators/bindings/macro-types | `d & isodate & (year: < 2100)` | `d & isodate & (isodate.year: < 2100)` (no run) |
| lib/search/hits | `hits(/\d+/) & occurs.none((hit: >= 100))` | `[h = hits(/\d+/)] & occurs.none((h.hit: >= 100))` (run, prose answers) |

(16 rows: the model's 15 re-spelled spans, plus nested-scope's run line. Its old span text is still printed in
his quote, so the scan counts that span under Q below.)

Programs left with a bare borrowed label: 29 distinct spans, the model's LEFT list. Its reasons:
- F, a fragment in a rule sentence (16): a condition or a group question shown alone, or over a placeholder `P`/`S`.
  The spans are `some((h: "5", m: "3"))` and its joint form (array-vs-passes, record-in-some), `count((chars.ch:
  anything))`, `(count((chars.ch: /(?s:.)/)): S)`, `P & x: S`, `P & (count((d: "7")): ==2)`, `P & !(P & (h:
  <5))`, `((h: <5) SEQ (h: <5))*`, `(a: "1") & P`, `P & (a: "1")`, `(count((d: "7")): ==2)` (twice),
  `(x: <200 | >900)`, `(h: >5) | (h: 5, m: >=3)`, `some((ok: anything))`, `occurs.exactly(1, (name: set))`.
- Q, the owner's words or his spelling (3): `B(A) & (d: <100)` (his example 1, quoted whole), `(x: < 2100)` (his
  macro variables), `(year: < 2100)` (his macro types; awaits call-prefix / macro types).
- R, printed as a compile error and still one (7): label-reference's "Bare" line, `$a + $b` (sum bound alone),
  `/x${(h: <5)}/` (inner), `/${rx}xx/ & (d: <100)` (his case 2), `count((d: "7"))` (n bound alone, two files),
  `(h: S)` (lt5).
- W, the worked examples' uses quoted as found (3), lib/planned/standard: `days($b) - days($a)`,
  `weekday_of($rest.year, ...)`, `days_in($year, $month)`. These are computed values bound alone, a compile
  error since bound-condition. Left for the manager, below.

Pieces:
- New: core/labels/label-only-group (under construction), moved from parked/ideas/label-only-group (its `was:`
  line; the parked piece and its details entry removed, the entry's text moved whole); core/labels/paths/call-prefix
  (`open call-prefix`, the conservative forms (1)-(4) and the candidates (a)-(c)).
- Statements and headings rewritten: flat-read-outside (heading "A part's label read from outside through its
  binding"), export statement 3 and statement 5, occurrences' statement (the body).
- Bullets: labels-vs-captures, flow, paths, label-reference, caller-ambiguous, metadata, holes/labels,
  nested-scope, bindings, macro-types; occurrences (three), hits (two), capture, capture/add-on.
- Lines added: four, in lib/search/occurrences and lib/search/hits. The spellings table's label-only row points at
  the new tag.

## DRAFT READINGS ADDED

All are marked "(a reading)" in the base:
- A lone capital in a rule sentence stands for a pattern written in place (label-reference).
- Under label-reference the flow rules judge a name read bare where the parts are written in place, or through a
  label over the composition; one part's prefix reads its own label (flow).
- A part label inside a binding is reached through the binding's name, `pair.b.x` (flat-read-outside; not run).
- The ambiguity bullet re-spelled with literals in place (paths).
- What the two rulings change for caller-ambiguous.
- Meaning (i) of macro types: the source names isodate's year, so there is no ambiguity.
- Two calls each labelled are not ambiguous (occurrences).
- `capture`'s body is left as written, its purpose being the capture (capture).
- The label-only readings (d) of the record: a label under every rule, and `\k<x>` a compile error for now.
- call-prefix's candidates (b) and (c) are the lane's list.

## OWNER QUESTIONS LEFT

- call-prefix (new open piece): the source of a label from a macro call's body, an argument, a parameter. Candidates
  (a) keep the conservative forms, (b) a once-called macro's name as a prefix, (c) the parameter's name at the call.
- macro types' head `B(d & isodate) := (year: < 2100)`: what label-reference makes of its bare `year` (call-prefix).
- How a helper declares a capture ("unless they are so declared"): joins lib/structural/capture/add-on.
- `\k<x>` to a label-only group: not stated.
- Not ruled and not applied: zero-condition-binding, the spelling `(?<:x>...)` as final, macro variables / types,
  his parked unqualified-after-definition idea, count-several, capture-loop-value, zero-in-loop.
- For the manager (reply either way):
  - lib/planned/standard prints `d := days($b) - days($a)` and its siblings, computed values bound alone, which
    bound-condition refuses. Should they be re-spelled in place, or are they kept as quoted uses?
  - predbound's DOC check is now red on the re-spelled metadata line, as covered above.

## EVIDENCE AND COMMANDS

- `(cd worktrees/predref && timeout 300 python3 -I -B docs/dev/lanes/predref_evidence/predref_model.py)` prints
  "predref_model: 8 checks, 0 failed" (predref_model.out). Its checks are CONTROL, SCAN, RESPELL, HITS, LABELONLY,
  QUOTES, MARKS and DOC.
- The counts come from that command's "== SCAN" block:
  - 203 program spans are checked now, 29 left;
  - at 915b47e64, 193 spans were checked, 44 distinct spans flagged and 15 re-spelled since;
  - "10 lines re-spelled" is RESPELL's count.
- Sabotage: `PREDREF_SABOTAGE=sN` for N in 1..10, each run alone (predref_sabotage.out). Each plant is caught by
  its target check, with no traceback.
- Lint: `(cd worktrees/predref && timeout 300 python3 -I scripts/pred_doc_lint.py | tail -1)` prints "checks passed
  6183, failed 0". `make -s test-plan-lint` is clean.
- The model loads predbound_model.py's definitions unchanged (exec up to "the checks"). It reads the old lines from
  915b47e64 by `git show` and the library bodies from library.md as it stands. Its controls are python `re` (the
  plain, `atomic` and `hits` bodies), the record's four pasted lines, and the record's words (QUOTES, 7 passages).
