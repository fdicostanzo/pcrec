# predspec12 report: predicate spec rev 12

Lane predspec12 (opus), 2026-11-15. Design only; no build go; nothing under src/, cli/, lib/, memfn/, tests/,
docs/spec/, COND-FAMILY.md or plan.md touched. Base 61f8e9f88 (premise checked: the draft's changelog said rev 11
was the latest; the last entry of COND-FAMILY.md is the 2026-11-15 anchoring ruling, CF:1001-1024).

## STATE AT HANDOFF

OWED: none

- DONE. `docs/design/predicates_draft.md` is rev 12 on branch `lane/predspec12`: the owner's ONE ANCHORING RULE,
  `anchored()` and the naming ruling (CF:1001-1024) folded everywhere the draft spoke of anchoring; `search` marked
  OPEN (name under review) at its definition (§2.6, §8) and in §13 (O61); the open small owner questions carried
  into §13 (OWNER QUESTIONS AFTER REV 12; O60 (d), O55, new O61-O63); changelog entry for rev 12.
- Oracle: `docs/dev/lanes/predspec12_anchor.py` (libpcre2-8 10.46 through its public API by ctypes, and Python 3.14
  `re` as a second engine) with its output `predspec12_anchor.out`; run with
  `timeout 60 python3 -I docs/dev/lanes/predspec12_anchor.py`. Every PCRE statement rev 12 adds cites it.
- History index: the report's entry appended to `docs/dev/history/claude_md/docs__dev__lanes.md` (N-1 / D149).
- Rulings file `docs/dev/lanes/predspec12_rulings.md`: empty at every read (before the WIP commit, before the final
  commit and before this report); last R-n applied: none.
- STOP RULE: not triggered. The one place the ruling meets an earlier ruled statement on the same point
  (CF:992-994: "`contains` and `search` remove that anchoring") is resolved by "later ruling wins" (CF:1018: "No
  primitive carries an anchoring special case"); the answers coincide except `$` (below).
- Validation (in the worktree): `make test-spec-history` 11 passed, 0 failed. `make test-plan-lint` FAILS on a
  PRE-EXISTING violation that is on main at the base and not in any file this lane touches: `PL14:
  docs/dev/plan.md (line elided): docs/dev/lanes/land1115c_report.md (line elided) cites a plan line number` (plan_lint: 357 rows, 1
  violation; its selftest passes, 45 plants). `git diff 61f8e9f88 -- docs/dev/plan.md
  docs/dev/lanes/land1115c_report.md` is empty on this branch; the fix belongs to the manager (main's
  land1115c report). No suites owed (design only; the box is in the owner's evening hold).

## WHAT REV 12 CHANGES

The ruling (CF:1011-1022, the manager's advice the owner agreed to at CF:1006, "Ok I agree"): (1) ONE rule, a FILTER
(the filter side of `&`, a `label:` condition) matches the WHOLE value, everywhere else an rx is unanchored as in
PCRE; `^`/`$` are the ends of the SCOPED match, plain PCRE with the value as the subject; (2) `anchored(rx) :=
/^${rx}$/` added; (3) library definitions are plain gaps, no primitive carries an anchoring special case, the fold of
`startsWith`/`endsWith` into `search` withdrawn; (4) the explicit-anchor switch rejected; (5) the naming rule over
every provided transform.

Where the draft now says it:
- §0 status marks: a new table for CF:1001-1024 (what rests on the owner's words vs the record); the CF:991-996 row
  annotated "restated by CF:1011-1019". §0 naming-rule sentence widened (CF:1020-1022), `search` flagged.
- §0.3 words: new "scoped match" row; "transform" row (gap transforms, no transform changes anchoring); "filter
  modifier" row (the naming rule now binds every provided transform).
- §11: THE FILTERED SPAN replaced by THE ONE ANCHORING RULE (the rule in five bullets, the rejected alternative,
  compile-time sets read as filters over whole strings); ONE SPAN PER FILTER ROLE restated as a CONSEQUENCE (a hole
  has no scoped match of its own); the edge-assertion error kept and said not to be an anchoring rule; HOLES, the
  in-span search sentence, REASONING and STATUS updated.
- §2.6: `search` no longer "removes" anchoring; ANCHORS IN THE ARGUMENT replaces THE ANCHORED ARGUMENT; the name
  `search` OPEN (O61) in the RULE and on the definition line; STATUS.
- §2.7: the NAMING RULE now covers every provided transform, with the owner's words; a modifier's argument is a
  filter under the one rule; STATUS.
- §8: the gap transforms written as a block with the record's text beside each, `anchored` ADDED, the record-vs-draft
  differences listed, the FAMILIES fold WITHDRAWN; `search` bullet marked OPEN; STATUS.
- §1: `endsWith`, `anchored` listed among the library filters.
- §12: a REV 12 paragraph (every case re-applied, unchanged); E-CTX intro cites the rule.
- §13: O49 restated; FIXB-9 (2) WITHDRAWN; O38 notes L63/L68/L69; O55 rev 12 note; new O61 (a name for `search`),
  O62 (`anchored`'s ends), O63 (the count warning); OWNER QUESTIONS AFTER REV 12; DECIDED BY THIS LANE (18)-(21).
- §15: a rev 12 provenance row.

ROWS AND EXAMPLES WHOSE STATED RESULT CHANGES (the brief's list):

| row / case | rev 11 | rev 12 | why |
|---|---|---|---|
| L63 `contains(/err$/)` vs `endsWith("err")` on `err\n` | SAME (both reject) | DIFFERENT: BY DESIGN: `contains(/err$/)` ACCEPTS, `endsWith` rejects | rev 10-11 read `$` in a filter as the exact end (review r10 SIM-5), an extra rule; "plain PCRE ... no extra rule" (CF:1013-1014) gives PCRE's `$` (end or before a final newline). Oracle: `(?:(?s:.*?)(?<hit>(?:err$))){1,}(?s:.*)` whole on `err\n` matches (0,4) in libpcre2 and `re`; `(?s:.*?)(?:err)` does not; `\z` gives the exact end (`contains(/err\z/)` rejects). The withdrawal is THIS LANE'S READING (LEAN) |
| L68 (NEW) `anchored(x)` final vs `/\A${x}\z/` on `foo\n` | (no row) | DIFFERENT: BY DESIGN: `anchored(/foo/)` finds `foo` (0,3), `\A(?:foo)\z` finds nothing | the owner's text uses `^`/`$`; the record's "`anchored(block)` instead of `\A...\z`" holds except on a final newline. §13 O62 |
| L69 (NEW) `x & anchored(r)` vs `x & r` vs `x & /^(?:r)$/`; `/^5/` vs `/5/` | (no row) | SAME | the record's "identity in filter position"; an explicit anchor never switches the implicit rule off (`^5` rejects `57`) |

No other row and no §12 case changes its stated result. Reasons respelled without an answer change: L7, L11, L13,
L15, L41 (now under the one rule), L17 ("falls out of PCRE", CF:1018), E-CTX-1/5/7 (cite the rule).

COND-FAMILY vs the draft (the brief: COND-FAMILY wins; differences listed):
1. CF:992-994 vs CF:1018: "contains/search remove anchoring" vs "no primitive carries an anchoring special case". The
   later ruling wins; the draft now says no transform changes anchoring (§2.6, §11). Same answers except `$` (L63).
2. The record's bodies `contains(rx) := /.*${rx}.*/` and `endsWith(rx) := /.*${rx}/` vs the draft's `contains :=
   search(x, min = 1)` and lazy `endsWith`. KEPT (LEAN, this document) and listed in §8 and §13 (20): the same SETS,
   no anchors either way (the record's point); the draft's forms decide how the ARGUMENT's labels read under the one
   reading (rev 9-10; a greedy `.*` lead brings back rev 8's rightmost reading, L58). If the owner meant the greedy
   bodies literally, L58/L61 change; a critic should confirm the reading.
3. The record's "`anchored(block)` instead of `\A...\z`" is not exact under PCRE's `$` (L68). The draft writes the
   owner's text and keeps E-HTTP's `\A...\z`; O62 asks.
4. The record lists filter positions as "the filter side of `&`, a `label:` condition"; the draft also reads a
   modifier's argument and the compile-time sets (an `enumerate`/`@assert` argument, a name set) as filters over
   whole strings (§11, LEAN), the only reading that keeps them finite/meaningful (an unanchored `enumerate(/a/)`
   would be every string containing `a`).

## TRANSFORM NAME AUDIT

The rule (CF:1020-1022, accepted at CF:1006): a PROVIDED transform is named for how it changes the FILTER / which
values the changed filter accepts (`padded`, `anchored`), never for an action on the subject. "Transform" = a macro
filter -> filter (§0.3). Every provided name in the draft:

| name | a transform? | passes the rule? | note |
|---|---|---|---|
| `padded(S)` | yes (modifier) | PASSES | the owner's example of a good name |
| `unpadded(n, S)` | yes (modifier) | passes | adjective; this document's name (O37) |
| `any_case(S)` | yes (modifier) | passes | |
| `quoted(S)`, `json.quoted(S)` | yes (modifier) | passes | |
| `length(S)` | yes (modifier) | passes | a noun for what the changed filter reads |
| `month_numbered(S)` | yes (modifier) | passes | |
| `left`/`right`/`mid` (string positions) | yes (modifier) | passes | nouns for the part read, like `length` |
| `anchored(rx)` | yes (gap transform) | PASSES | the owner's own name (CF:1009) |
| `startsWith`, `endsWith`, `contains` | yes (gap transforms) | pass | predicates on the value ("the value starts with"), not actions; the record: "likely stay" (CF:1024) |
| `search(x, min)` | yes (gap transform, adds `hit`) | FAILS | a verb acting on the subject (the record, CF:1023). OPEN, spelling kept (O61) |
| `json.row(k, v)` | yes (v a filter) | passes | a noun for the accepted values |
| `when(c, p)` | yes (two filters -> filter) | passes | a conjunction: when c holds, p filters |
| `some(c)`, `all(c)` | yes (condition -> filter) | pass | quantifiers over iterations, describing values |
| `occurs.exactly/at_least/at_most/none(n, c)` | yes (condition -> filter) | pass | "c occurs exactly n times" describes values |
| `count(c)` | no: returns a number | n/a | not a transform; a noun here |
| `between`, `within` | no: set builders, no filter parameter | n/a | |
| `capture(x)` | no: places an rx under a group name (§5.3), its argument is never tested as a filter | n/a, BORDERLINE | a verb; if the owner reads the rule as covering every provided macro, it fails too (candidates: `labelled(x)`, `captured(x)`, `exposed(x)`; lean `labelled`, it says what changes: the rx gains a caller-visible label). Not marked OPEN in the draft: it is not a transform by §0.3 |
| `each`, `join`, `where`, `where_group`, `each_group`, `list_of`, `records`, `enumerate`, `sort`, `unique`, `concat` | no: structural, compile-time | n/a | |

`search`, candidates (3-5 asked; five given, one line for and against each; §13 O61 carries the same):

| candidate | for | against |
|---|---|---|
| `occurrences(x)` | a noun for what the changed filter reads, as `length(S)` names the value's length; reads well with the group questions: `(m: occurrences(r) & some((g: "x")))` | close to the `occurs` module's name: two words of one family with different jobs |
| `hits(x)` | short; names the label it adds (`hit`) | jargon; says nothing of which values pass (all, at `min = 0`); the draft binds `hits := search(r)` as an example name |
| `marked(x)` | a participle like `padded`/`anchored`: the filter changed so each occurrence is marked | reads as marking the SUBJECT, the reading the rule forbids |
| `each_occurrence(x)` | says a plain condition reads EVERY occurrence | reuses `each`, the structural macro's name (one word, two meanings, G0b) |
| `containing(x)` | the participle of `contains`, the family's kept name; `containing(x, min = 1)` = `contains(x)` | at `min = 0` it accepts values containing NO x: the name misstates which values pass |

LEAN: `occurrences(x)`, with the label `hit` renamed to match at the spelling step (O55). No other provided
transform fails the rule.

## QUESTIONS FOR THE OWNER

Plain words, one example each. Question (3) of the last round (folding `startsWith`/`endsWith` into `search`) is
withdrawn by tonight's ruling.

1. The `&` switch inside a regex. When the switch that makes `&` mean "and also matches" inside regex text is ON,
   should PCRE's own constructs that contain an ampersand keep their PCRE meaning, so that `&` is the operator only
   where it stands alone? Example: in `/(?<w>\w+)(?&w)&${<256}/` the `&` inside `(?&w)` stays PCRE's "call the group
   w" and only the second `&` means "and also". A plain ampersand character is then written `[&]`. Most ampersands
   in real PCRE patterns are such calls (154 of 165 corpus lines). Lean: YES.
2. Two searches in one chain. `search` and `contains` each give their matches the label `hit`. If one condition
   chain uses two of them, a question about `hit` cannot tell which one is meant. Example: `(m: contains("a") &
   contains("b") & some((hit: ...)))`. Should that be a compile error naming both, fixed by giving one search its own
   hit name (`search(r, hit_name = "h")`-shaped)? Lean: YES.
3. (Withdrawn.)
4. A count in a program that searches. A program whose last pattern is searched in the subject may report a SHORTER
   stretch than the whole block, and a count can pass on the shorter stretch. Example: "exactly one Host header"
   searched in `Host: a` + newline + `host: b` reports `Host: a` alone, which passes. Should the compiler warn when
   a count sits in such a program? The question still makes sense under the one anchoring rule: the count itself
   matches the whole stretch it is given; the search picks the stretch. Tonight's ruling gives the fix a name: wrap
   the last pattern in `anchored(...)` (or `\A...\z`). Lean: NO warning (counting inside found stretches is a
   legitimate program; the fix is documented with counts).
5. A name for `search`. Your naming rule says a provided transform is named for how it changes the filter, and
   `search` is a verb acting on the text. What it does to the filter: the new filter accepts every value and reads
   each occurrence of the argument as one `hit`. Example: `(m: search(/ab(?<g>[xy])/) & some((g: "x")))` would read
   `(m: occurrences(/ab(?<g>[xy])/) & some((g: "x")))`. Candidates: `occurrences`, `hits`, `marked`,
   `each_occurrence`, `containing` (for/against in the audit above). Lean: `occurrences`, by analogy with `length`
   (a noun for what the filter reads).
6. `anchored` and a final newline. Your definition `anchored(rx) := /^${rx}$/` uses PCRE's `$`, which also matches
   just before a newline at the very end. Example: as the last pattern, `anchored(/foo/)` finds `foo` in `foo` +
   newline, while `\Afoo\z` finds nothing. Inside a filter both are the same as no anchors at all. Should `anchored`
   use the exact ends (`\A`, `\z`), so that it means "the whole text, nothing after"? Lean: YES (the record says
   `anchored(block)` replaces `\A...\z`, which is then exact).

Told, not asked (a consequence, LEAN): under "plain PCRE, no extra rule" a `$` inside `contains` or `search` also
matches before a final newline, so `contains(/err$/)` accepts `err` + newline while `endsWith("err")` does not (L63);
write `\z` for the exact end. Rev 10-11 had an extra rule that made them agree.

## CONSISTENCY SWEEP

Every §0.1 row and every §12 case re-applied under the one rule (each in its real mode: on the value unless the row
says SEARCHED). Witnesses: `docs/dev/lanes/predspec12_anchor.out`.

| rows | result | reason |
|---|---|---|
| L1-L6, L8-L10, L12, L14, L18-L40, L42-L62, L64-L67 | unchanged | no `^`/`$`/`\A`/`\z` in a filter or a filter's hole, or only in a FINAL pattern (L8, L9, L18, L19: searched, as before); errors unchanged (the edge-assertion error is not an anchoring rule, §11) |
| L7, L11, L41 | unchanged verdict (DIFFERENT: BY DESIGN) | a filter matches the whole value, a `^` in it adds nothing; now cited to CF:1011 |
| L13 | unchanged verdict | a modifier's argument is a filter over the reading (LEAN) |
| L15 | unchanged verdict | a name set is read as a filter over whole names (LEAN) |
| L16 | unchanged | `^` in `search`'s argument: only an empty lead gap reaches it, at most one hit |
| L17 | unchanged (SAME) | "falls out of PCRE" (CF:1018); oracle: `err x` accepted, `x err` rejected, both forms |
| L63 | MOVED: SAME -> DIFFERENT: BY DESIGN | PCRE's `$` (above) |
| L68, L69 | NEW | above |

| §12 case | result |
|---|---|
| E-JSONL | unchanged: `^`/`$` (with `m`) sit in the FINAL pattern, searched line by line; `contains("timeout")` has no anchor |
| E-WEEKDAY, E-CAL, E-RFC, E-NEAR, E-SEP, E-DEPTH | unchanged: no anchor in a filter |
| E-IPV4 | unchanged: `/\b${ipv4}\b/` is a final pattern |
| E-LUHN | unchanged: `startsWith("4")` is a gap body |
| E-FILE | unchanged: the item rx is searched in the file text (an "everywhere else" position); `!startsWith("#")` a gap body |
| E-HTTP | unchanged: `\A`/`\z` in the final pattern are the exact ends; kept rather than `anchored(block)` (L68, O62) |
| E-CTX-1, 5, 7 | unchanged answers; reason now the one rule |
| E-CTX-2, 3, 4, 6 | unchanged (compile errors) |
| agreeing look-alike | unchanged |

Sections 2, 7, 8, 11, 12 swept for every `^`, `$`, `\A`, `\z`, "loosen", "remove ... anchoring" and "exact end"
(grep in the lane's working notes); the remaining hits are the rev 11 history paragraphs (§0.1 "SAME ROWS RE-APPLIED
UNDER THE ANCHORING RULING", §12 "REV 11 RE-APPLIED"), kept as the record of rev 11, and the O32 hole-flags example
(a final pattern, unchanged).

What a short confirming critic round should look at:
1. The `$` withdrawal (L63, §11, decision (18)): is "no extra rule" the right reading, or did the owner's "^ $ refer
   to the scoped match" leave the exact-end reading standing? Check every place a gap or atom can follow a `$` in a
   filter's hole.
2. The record-vs-draft body differences (§8, decision (20)): whether keeping `contains := search(x, min = 1)` and the
   lazy `endsWith` honours "plain gaps" (sets equal; label readings differ from a literal greedy `/.*${rx}.*/`).
3. Compile-time sets read as filters (decision (19)): the ruling names two filter positions; is the extension forced
   (finiteness of `enumerate`) or a new rule?
4. `anchored` (L68, L69, O62): identity in filter position holds for every rx, including `(?m)` inside the hole and
   a top-level alternation (the hole is an atom with its own flags)?
5. The name audit: whether `capture` falls under the rule; whether `contains`/`startsWith`/`endsWith` pass on the
   owner's reading; the five `search` candidates against the rule's own words.
