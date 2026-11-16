# predspec16 — predicates_draft.md rev 15 -> rev 16 (lane predspec16, opus, 2026-11-15)

Design only, no build go. Branch `lane/predspec16`, cut from local main at b8cfd3d6a. Rulings: COND-FAMILY.md on
main through CF:1208 (the 21:50 and 21:54 entries on the branch; the 21:58 and 21:59 entries arrived during the lane as
rulings R-1 to R-3).

## STATE AT HANDOFF

- STATE: done. Rev 16 of `docs/design/predicates_draft.md` committed on `lane/predspec16`; two plan rows in
  `docs/dev/plan.md`; the evidence script `docs/dev/lanes/predspec16_anchor.py` and its output
  `predspec16_anchor.out` (the predspec15 script continued, its engine helpers copied); this report; one index line in
  `docs/dev/history/claude_md/docs__dev__lanes.md`.
- Rulings file `docs/dev/lanes/predspec16_rulings.md`: last entry applied **R-3** (R-1, R-2, R-3 all applied; read
  before each commit and before this report). R-1 asked for a second plan row; R-2 corrected it (the idea already
  lived in COND-FAMILY.md, guarantees taken from that record); R-3 added `enumerate` as a third route (sketched and
  tested) and the reconciliation with the 2026-11-14 tuple record (`lex_ge`, CF:648) as the first naming candidate.
- Premise test passed: the changelog said rev 15 was latest; COND-FAMILY.md's tail held "tuple-compare: agree" and
  "cut-json-quoted: agree"; `make test-plan-lint` GREEN before the first edit.
- STOP RULE: no two ruled owner statements contradict. The 21:50 entry's "Why is json.quoted?" is a question,
  answered by the 21:54 cut.
- Validation in the worktree (owner's evening hold: no suites, no queue jobs): `make test-plan-lint` GREEN (2 passed,
  0 failed; plan_lint 360 rows, 0 violations); `make test-spec-history` GREEN (11 passed, 0 failed). Evidence:
  `timeout 300 python3 -I docs/dev/lanes/predspec16_anchor.py` (run from `$PCREC_TMPDIR/scratch/predspec16`) ->
  `predspec16_anchor.out`, rc 0, **engine disagreements 0** (libpcre2-8 10.46 via ctypes vs Python 3.14.4 `re`).
- Owed: none.

## WHAT REV 16 CHANGES

(A) TUPLE COMPARE IN THE FIRST LIBRARY (§8 TUPLE COMPARISONS; RULED CF:1166 on main). The family, for 2 and 3 fields:
a between and its two halves (at least, at most), six plain macros with rev 15's O69 bodies, every comparison padded.
Not carried (lean: only what the bodies give for free): strictly above = `fields & !lex_le2(...)`, strictly below =
`fields & !lex_ge2(...)`, equality = `lex_between2(f, sep, t, t)`. Checked against integer lexicographic order: all
six macros and the three derived forms, 15,336 cases, 0 differ (table (F)). Worked rows (table (X), 29 rows, 0 differ
from the stated answers): the time range 9:00..10:00, h:m:s 9:30:05..10:00:00, versions 1.4..1.10 (canonical-number
fields reject `1.04`; `\d+` fields accept it through `padded`), plus contrasts (a string `between("1.4", "1.10")` is
empty; a separator written as rx `/./` accepts `1x4`). Caveats stated (§8): visible helper labels `t1..t3` and the
per-call label name (O55's route, LEAN); a parameter / array entry as a comparison atom (LEAN); positional reads and a
wrong-length array (compile error, LEAN); a string in a hole is literal; non-digit fields reject; cost UNMEASURED.
Reconciled with the 2026-11-14 record (rulings R-3 (ii)): CF:648 already had "TUPLE CONDITIONS: a LIBRARY macro
(`lex_ge([major, minor, patch], [1, 4, 0])`), no syntax"; rev 16 adds: in the FIRST library, at FIXED sizes, with
bodies, and the record's defect (bare label names as values, C13) avoided. O69 CLOSED for the fixed sizes; any number
of fields stays later (trigger: a real 4+-field use, or a looping structural macro / library primitive built for
another need); O68 stays later, behind tuple compare. C25 and §14 note the fixed-size answer; O47 stays at (C).

**tuple-names** (the naming candidates; names OPEN at the definition):
- (a) LEAN: the record's stem, sized, over arrays: `lex_ge2`, `lex_le2`, `lex_between2`, `lex_ge3`, `lex_le3`,
  `lex_between3`; `lex_between2([/\d{1,2}/, /\d\d/], ":", [9, 0], [10, 0])`. For: the owner's own name; arrays keep a
  tuple's parts together; `lex` names the order. Against: `ge`/`le` abbreviations; a digit in the name.
- (b) `pair_between`/`pair_at_least`/`pair_at_most`, `triple_...`, positional (rev 15's call shape). For: words, no
  digit. Against: seven to ten positional parameters; the words stop at three.
- (c) `tuple_between2` etc. (rev 14-15's placeholder). Against: "tuple" names no order; digit suffix.

(B) `json.quoted` CUT (§9, the owner's pointer quoted as his; RULED CF:1180-1181 on main). Removed from §0.3, §1,
§2.7 (rule text, bodies table row marked CUT, status), §8 (list, status), THE ROLE TABLE row 8, O61's audit (marked
CUT). O37 CLOSED (no name of this document's choosing remains). Examples that used it: ONE, E-JSONL (§12.1), REWRITTEN,
not dropped: `quoted(...)` (the library body) for ts and level, `json.string & contains("timeout")` for msg (the raw
literal, escapes included); the module comment's `quoted` member renamed `string`. Its three stated subjects keep
their answers; a fourth added (an escaped quote in the message: match). Where the raw reading differs from the cut
decoded reading (table (J), 4 of 12 value texts): `"2024\u002d02-10"`, `"err\u006fr"`, `"time\u006fut"` (raw
rejects) and `"x\timeout"` (raw accepts); listed in §12.1. No other example or §0.1 row used it.

(C) `any_case` STAYS a primitive for now, the one provided transform without a body: stated in §2.7 (bodies table row
and the paragraph below it) and THE ROLE TABLE row 8 (its argument: a whole-match role on the case-folded reading,
marked the manager's LEAN). O67 CLOSED, not as asked, with the owner's words quoted exactly; the "one reading
primitive" proposal not adopted. NEW §13 O70 (the follow-up): what it must answer ((i) an option-setting primitive
through a hole, which options; (ii) its effect on "a hole keeps its own flags", §11 / O32; (iii) whether it reaches
decoding or that needs the callout route), three routes (option-setting primitive; blessed DFA callout; `enumerate`).
Route (c), `enumerate` (rulings R-3 (i)), SKETCHED and TESTED: `any_case(S) := each(folded, enumerate(S))`,
`folded(w) := join(each(fold, chars(w)))`, `fold(c) := c | uppers[(lowers & c).index] | lowers[(uppers & c).index]`
over a spelled ASCII table; five finite filters, 0 differ (table (E)). NOT a body in today's language: one tool is
missing, a string's characters as an array (`chars(w)`); everything else is today's (`enumerate`, `each`, `join`, a
spelled table, `X & f` with `.index`, positional `X[...]`; reading a filtered entry's `.index` as a position: LEAN).
Outside it regardless: non-finite filters (`any_case(/\w+/)`) and a `label:` condition argument. So no
**any-case-finite** question is raised (R-3: only if complete).

(D) Plan rows: below. (E) Changelog rev 16; §0 rulings table gains the rev 16 block (five rows); §0.1 EVERY ROW
RE-APPLIED UNDER REV 16: NO ROW MOVES; §12 REV 16 RE-APPLIED: only E-JSONL's code lines change, no stated answer moves;
§12 census gains a tuple row (no §12 case; §8 rows); DECIDED (44)-(48); owner questions (9), (10) ANSWERED, (12)
**tuple-names** OPEN; §15 provenance row for rev 16. Rows that moved: none in §0.1; in §12 only E-JSONL (the one user
of `json.quoted`).

## PLAN ROW FILED

Two rows (the brief's one, plus the one rulings R-1/R-2 asked for), both STATE:not-started, design only, no schedule.

`[PRED-REREAD]` (after [COUNT-TO-OCCURS], in the predicate rows): "a more fundamental basis for transforms that test
a filter against a re-reading"; body: `any_case` (a primitive for now) and `json.quoted` (cut 2026-11-15); the
owner's words (the primitive-transforms answer, the cut with his callout pointer, "What about "enumerate""); routes
(a) option-setting primitive through a hole (which options; the hole-flags rule §11 / O32; decoding?), (b) a blessed
DFA callout ([BLESSED-CALLOUTS]; neighbours [CALLOUT-GROUPS] and [MATCH-EVENTS], read with `scripts/entry`), (c)
`enumerate` for finite filters (sketched, missing a per-character split); trigger: predicates next scheduled for a
build design, or a second re-reading transform asked for.

`[BLESSED-CALLOUTS]` (after [CALLOUT-GROUPS]): "blessed callouts: a callout with stated guarantees may run on the DFA
path". WHERE THE IDEA ALREADY LIVED (R-2): COND-FAMILY.md's 2026-11-14 entries "a standard library of blessed
callouts (Frank)" (CF:461-470: PURE, BOUNDED, TOTAL, ORACLE-TESTED, DECLARES ITS REGULAR TWIN; emitted C text) and
"capability levels" (CF:472-481: `functions` = blessed callouts on DFA captures, independent of `vm`), carried in
predicates_draft.md §8 BLESSED CALLOUTS and §6.1; no plan row held it (`scripts/entry -g blessed -in 2`: 0 items).
WHAT I ADDED: the row itself, the owner's 2026-11-15 sentence ("Idea was "blessed" callouts that guaranteed certain
characteristics could be exposed to dfa"), the guarantees copied from the 2026-11-14 record (R-1's manager
candidates dropped per R-2), and its first named client ([PRED-REREAD]: `json.quoted`). Trigger: [PRED-REREAD]
scheduled, or another feature needs a callout on the DFA path. §8 BLESSED CALLOUTS now points at the row.

## QUESTIONS FOR THE OWNER

- **tuple-names**: what are the tuple compares called, and are they called with arrays? Example: the 9:00-10:00 range
  as `lex_between2([/\d{1,2}/, /\d\d/], ":", [9, 0], [10, 0])` (lean: your own `lex_` name from 2026-11-14, with the
  number of fields at the end) versus `pair_between(/\d{1,2}/, ":", /\d\d/, 9, 0, 10, 0)`. Forces: your stem and
  arrays keep the parts together; the alternative reads as words but has seven positional parameters. Lean (a).
- No other question: the `enumerate` route is not complete (one missing tool), so **any-case-finite** is not raised.
