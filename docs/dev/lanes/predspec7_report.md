# predspec7 report: predicates_draft.md rev 7, review r8's ruled fixes applied (design only)

## STATE AT HANDOFF

STATE: done. Branch `lane/predspec7`, from main 45b7aae3d. Deliverables: `docs/design/predicates_draft.md` rev 7
(changelog entry first); the r8 critic texts and the coordinator's process log copied to
`docs/dev/reviews/2026-11-15-r8-predspec6/` (COMMON, census, drift, owner, rulings, simulate, verify, process),
listed in `docs/dev/reviews/CLAUDE.md`; the census lens row in `.claude/skills/pcrec-critic/SKILL.md` §4 (inserted
after the simulate row, the brief's text verbatim; nothing else in the skill changed); this report. Design text only:
nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/` or `docs/spec/` touched; COND-FAMILY.md and plan.md not
edited. Rulings file `docs/dev/lanes/predspec7_rulings.md`: empty at every commit and at this report; last R-n
applied: none. Validation: `make test-plan-lint` in the worktree (checks passed: 2, failed: 0); pre-commit staged
checks passed on every commit (52 passed, 0 failed). Nothing OWED (no suites by brief).

Premise test held: the review file has a "DISPOSITIONS RULED" section (its last section); the draft's changelog said
rev 6. "CF:n" = line n of COND-FAMILY.md at 45b7aae3d (887 lines; `wc -l`). The owner's note is CF:880-887; the
filtered-span confirmation cited for P6-5 is CF:761-773; the macro-in-a-hole words CF:362.

Size: `wc -lc docs/design/predicates_draft.md` = 1,978 lines / 189.3 KB (rev 6: 1,624 / 146.6 KB). Growth: §0.3
words, the §0 marks table, §2.1 kind table, §5.4 mark table, §12 two-way census, §13 O48-O52.

Counts quoted in the draft and their commands:
- "no case uses search (`~`: 0 uses)" and the TWO-WAY CENSUS's "none" rows: §12's code lines with comments stripped,
  `awk '/^## 12\./,/^## 13\./' docs/design/predicates_draft.md | grep '^    ' | sed 's/#.*//' > c12.txt`, then
  `grep -cF -- TOKEN c12.txt` per token: ` ~ ` 0, `!~` 0, `(&` 0, `where` 0, `each_group` 0, `when(` 0, `pure` 0,
  `pattern(` 0, `eval` 0, `@export` 0, `@warn` 0, `.label` 0, ` * ` 0, ` % ` 0, `count(` 0 (code; E-HTTP prose
  only), `) :=` 4 (all definition heads, no record on the left); positional `X[...]` 0 (`grep -nE
  '[A-Za-z_)]\['` minus rx text: no hit).
- "`join([...])` in six §12 cases": `awk '/^### 12\.[0-9]+/{c=$2} /^## 13\./{exit} /^    .*join\(\[/{print c}'
  docs/design/predicates_draft.md | sort -u` = 12.2, 12.3, 12.6, 12.7, 12.9, 12.10.
- "grouping: no case": the same c12.txt, a `(` not after a name, `)`, `]`, `&`, `/`, `\` or `?`: only conditions.

Per-case re-check (rev 7): all twelve §12 cases unchanged token for token. Touched only through open items: E-CAL
(`<=dim` bare, C13), E-RFC (`==wd` bare, C13; `$mname.index` now one parse; `.index`/`$rest.year` the dot family,
O31), E-HTTP (condition argument, now §5.4's row; O45), E-JSONL/E-IPV4/E-HTTP/E-DEPTH (`import`, O46), E-NEAR (b)
(`param`, O46). None uses `~`.

## FINDINGS FIXED

| finding | disposition | what changed, where |
|---|---|---|
| P6-1 hole-as-guard vs unapplied-macro error | FIX-NOW | §5.1's "a macro with only its subject open ... is a guard" deleted; a macro in a hole is the unapplied-macro error (RULED, CF:362), stated in §2.3, §5.1, §11 HOLES and §5.4's `${ }` row; the guard is `&` + an rx hole (C4) |
| P6-2 false tuple reason; `[ ]`'s one meaning | FIX-NOW | §5.4 `[ ]` row: ORDERED ENTRIES, any one under `& \| !`, in order under structural tools, each entry ONE entry; §8 tuple paragraph: defect = bare label names (C13), rev 6's "forbids/order not part of the value" withdrawn as false; §13 C25 back to OPEN between (A) structural macro over arrays and (B) `version & lex_ge(1, 4, 0)`, no lean; O47 re-argued (needed only under C25 (B) or O52 (a)); §3.2 `X[0]` dropped; §5.3 `c[1]` on a join = c itself, parts by label |
| P6-3 `( label: S, ... )` in value position | FIX-NOW | §5.4 new row: in value position it IS a condition (a macro), not a record; own row for the section `(& f)`; O45 points at the row |
| P6-4 `:` narrows vs checks; `p: pure` | PLAN + text | §0.1 L49 (BY DESIGN, O48); §5.2 states the split and marks `pure`'s spelling OPEN; §5.4 `:` row names both; §13 O48 with readings A (narrow in both), B (own spelling for the check), C (typed parameters out of phase 1); lean A |
| P6-5 `contains(/^err/)` vs `$m ~ /^err/` | FIX-NOW (manager: as the GENERAL rule) | §11 new ONE SPAN PER FILTER ROLE: the span is fixed by the filter role; an argument or a hole inside a filter reads the enclosing span (CF:761-768 applied to arguments), so `contains(/^err/)` = `startsWith("err")`; how it agrees with §2.7's "argument's own ends" stated in §2.7 and §11 (a modifier's argument reads the span as the modifier reads it); §8 `contains` line; §0.1 L17 rewritten (now condition vs condition, SAME); `!~` restated in §2.6; marked LEAN, §13 O49 for the owner's confirmation |
| P6-6 `$mname.index` two parses | FIX-NOW | §5.4 `$` row: `$a.b.c` = `$(a.b.c)`; O2 lists `$`; §12 preamble notes E-RFC's one parse |
| P6-7 the search result after CF:880 | PLAN + text | CF:880-887 folded (§2.6 rule + status: "array of all results" RULED in his words, was LEAN; changelog; §15 row); the owner's example as §2.6's structure-vs-language illustration, recorded as the behaviour any answer must give; §3.4 SPELLED vs MATCH-TIME arrays stated once; G4 restated to spelled things; L16 rewritten (value vs condition, BY DESIGN, filter role OPEN), L17 rewritten; C29's premise corrected; L50 (destructuring, two readings of one spelling) and L51 (`!($m ~ r)` vs `$m !~ r`, GAP) added; `some`/`all` over search results listed OPEN; §8 `occurs`/`count` second population noted; §13 O50 with parts (a)-(e) and readings; no §12 case invented (search listed in the census, phase 1 the owner's, §0.2) |
| P6-8 kinds in practice; typing of `& \| !` | FIX-NOW | §2.1 KIND TABLE (rx, macro, computed label, record, namespace, run-time parameter, effect; value / bound / passed / §12 case / status), the two value kinds unchanged; the typing sentence for `& \| !`; a computed label is a macro whose operand is the pattern it reads (also §4.4); `(& M)` = M, so `each((a: d), x)` is legal (§2.1, §5.3); §3.4 `each_group((& (x: d2)), rx)`; map-view tools return an rx (§2.1, §3.2, §5.3); `@` forms are "effects", "a section is a macro" replaces "operators are macros" (§5.1, §5.2); O46 carries the namespace/parameter question with readings, lean B |
| P6-9 the 11-15 criterion as a goal | FIX-NOW (kept small) | G0b row (criterion quoted, check = MARK TABLE + KIND COUNT, each naming its §12 case); G0's acceptance = every DIFFERENT row carries exactly one class (ERROR / WARNING / BY DESIGN / GAP), applied to all 28 DIFFERENT rows + L48-L51; the ranking written as it operates (G2 wins at the default level; the order question stays O38); §12 TWO-WAY CENSUS table; missing cases LISTED (§0.2, §12), none invented |
| P6-10 RULED marks past the owner's words | FIX-NOW | §0 marks legend + a table naming, per type-picture point, the owner's own sentence and what rests only on "I'm liking your ideas" (CF:851) (RUL-3); §3.1 "no third view" re-marked (RUL-2; one-way RULED in his words CF:853-854); §0.2 destructuring line (RUL-4); §14 tuple/boolean (RUL-6); C19 `@` statements LEAN CF:619 (RUL-10); §0.1 STATUS L43 error RULED vs withdrawal LEAN (RUL-11); §5.1 STATUS one kind RULED (RUL-13) |
| P6-11 ill-formed examples | FIX-NOW | L9 `[n = /\d+/]`; L36 and C28 `occurs.all((x: S))`; L2 and L42 without `;`; E-CAL lists C13 (`<=dim`) beside E-RFC (§12 preamble, §12.5, C13, L37); §7 `balanced`: the `(?&name)` self-recursion crossing stated (CF:113) in §7 and §11's crossings; §7 `records`: each item is the item rx narrowed to one match, labels by the map view; §2.5 respelled `s := $x + $y` then `P & (s: <50)` |
| P6-12 the dot family | PLAN + text | §5.4 `.` row (one meaning lean: field of the map view of the thing on the left; which uses are instances); §3.2 tool 4 points at it; §13 O31 WIDENED to the four resolutions with readings, lean A for labels/paths, B for metadata, members per O46 |
| P6-13 statements starting with `(`/`[` | PLAN | §5.1 sentence + §13 O51 (readings A no such statement start, B significant newline; lean A) |
| P6-14 `[x, /d/]` vs `x \| /d/` | FIX-NOW | §5.4 `[ ]` row: each entry is ONE entry; §0.1 L48 (BY DESIGN) |
| P6-15 key words with two meanings | DOC | §0.3 WORDS table (subject/operand, kind, value, captured string, constraint set, filter role, condition, section/comparison set, transform/reading, binding/entry extent, label/parameter/member/metadata, entry/part, record/item, effect), applied through §§0-14: "subject slot" -> operand, "the subject is never an argument" glossed as CF:749's word for the operand, comparisons are "comparison sets" (§2.4 title), "the C22 binding" -> entry extent (§4.1, O43), "record rx" -> item rx (§7, §11, E-FILE, O20, O44), "transform images" -> what a modified filter reads (§11), `where` "selects", "effect macros" -> effects, `eval` a filter not a condition (§10), "type" -> constraint set where it meant an rx (§4.3, §5.2) |
| P6-16 families and the general form | PLAN | §13 O52 FAMILIES: the any-one / all-together / name-introduction families, the entry-list general form, four unlocks each with its trigger; lean: decide each at its trigger (D77) |
| P6-17 freeze drift | NOTED | folded via P6-7 |
| P6-18 refuted sub-claims | REJECTED | nothing to apply |

Also from the brief: the owner's note CF:880-887 folded and his example added (§2.6, O50); the review directory copy
and the skill row (above).

## OWNER QUESTIONS

Plain words, each with one example and a lean (the manager carries these to owner.md).

1. What does `:` mean when it appears in a macro's definition head? Today, in a condition, `isodate & (year: <2000)`
   quietly keeps only the dates before 2000; but in a head, `m(x: T)`, calling `m` with something partly outside T is
   an error. One mark, two behaviours. Should `:` narrow in both places (the check becomes the usual dead-branch
   warning), should the check get its own spelling, or should typed parameters wait until after phase 1 (no example
   uses them)? Lean: narrow in both.

2. What is a search result while the match runs? You said it is the array of all the results. Your example: on `abx
   aby abx`, `d := <subject> ~ /ab(?<g>[xy])/` gives `count(d)` = 3 and `d & (g: x)` keeps results 1 and 3. Every array
   tool in the draft today works on arrays written in the program, at compile time; this array exists only per match.
   Four smaller questions follow: which array tools work on it; what `d.g` means when there are several results (all
   their g values as one set, or one per result); whether `$m ~ r` can be used as a test directly or only through a
   condition like `(m: contains(r))`; and whether `(x, y) := ...` names the fields of each result or the first two
   results. Lean: count it like a repeated group (one rule for `count` and `occurs`), keep `&` selecting results with
   their positions as in your example, `d.g` one entry per result, test through the condition form.

3. What is a module (and a run-time parameter) under the two kinds? `json := import("json")` names something that
   holds macros, so it is not a pattern, and a record is never a value. Likewise `anchor := param(isodate)` names a
   string the caller supplies per match. Lean: a parameter is a pattern whose text the caller fixes; a module is a
   namespace you can name but not pass around.

4. Should the dot mean one thing? Today `d.year` (a group of a pattern), `json.row` (a module member), `x.index`
   (which alternative matched) and `$rest.year` (a captured text through a path) all use the dot. Lean: the dot means
   "a field of the thing on the left" for groups and paths; `index`/`label` become call-style built-ins
   (`index(x)`), so a group named `index` can never clash.

5. Confirm the filtered-span rule for arguments. With `^` meaning the start of what is being filtered (your 11-15
   rule), rev 7 reads `contains(/^err/)` as "starts with err", the same as searching the value for `/^err/`. The
   alternative reads the `^` as the start of wherever `contains` places its argument, which makes it match anywhere.
   Lean: confirm rev 7's reading.

## OPEN ITEMS

- Rev 7 decides none of the PLAN items: O48 (`:` in a head), O49 (confirm the one-span rule), O50 (the search result
  at match time, parts a-e), O31 widened (the dot family), O46 (namespace and parameter), O51 (statement starts), O52
  (families), C25 (tuple spelling, back to OPEN, no lean).
- STOP RULE: no ruled fix contradicted another or a RULED owner item. One tension recorded, not picked: under P6-5's
  general rule `^` in a hole reads the enclosing filter's span, while `\b` at a hole's edge stays the edge-assertion
  error (L8, CF:713). Both are kept as written (CF:761 supersedes CF:713 only for `^`/`$`); the asymmetry is stated in
  O49 for the owner.
- The owner's example and reading (D) of O50: the drift critic's lean (a search result as a repeated label) would read
  `d & (g: x)` as "every result has g = x" under the sequence rule, not as selecting results 1 and 3. O50 records this
  and the combined lean; whoever answers O50 must re-run the example.
- G0b's mark table cites §12 cases per mark from a reading of the cases, not from a tokenizer run; a census lens in
  the next design round (the new skill row) is the independent check.
- No §12 case was added (ruled). Constructs with no case are listed in §12's TWO-WAY CENSUS and §0.2 for the owner.
- `records` and "item rx" are still placeholders (O44); the long lines of rev 6's tables were left as they were.
