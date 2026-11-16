# Lane absimpact: what the candidate absent-label rule R does to every other statement

Lane absimpact, 2026-11-16, opus, DESIGN ONLY (no build go; nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`;
no edit to `predicates_draft.md`, `joint_condition.md`, the rulings record or `predicates_future.md`; no file under
`docs/design/`). Branch `lane/absimpact` (cut from `lane/absent`, main merged). The owner's question (2026-11-16,
verbatim): "absent-rule: I agree with your lean but before we lock it in, what is the impact across other statements.
What was the statement where absence matches made sense?" R is the manager's lean and is NOT ruled: this report
writes "under R" throughout. Every sentence not quoted or cited is the lane's.

EVIDENCE. `docs/dev/lanes/absimpact_check.py` / `.out`, run from the worktree root as
`timeout 120 python3 -I docs/dev/lanes/absimpact_check.py` (0.4 s; libpcre2-8 10.46, Python 3.14.4). Every count
below is from that output unless another command is named. Kinds of result, marked on every example:

- RUN: every subject is a whole match of its pattern in libpcre2-8 AND Python `re`; the parse facts the answers rest
  on are read from PCRE2 (a loop run zero times, an alternative not taken: probe groups; the hits of `occurrences`:
  an unrolled form of its body, compared hit for hit with find-all, 0 disagreements).
- COMPUTED: the answers under "today" (T: the ruled line read per pass, lane absent's T-pass) and under R, from ONE
  declared table (`part()` in the script; table (RT) below), on the subject split by string code.
- ENGINE-RUN: for the list, `occurrences`, record, zero-pass-record, `when` and labelled-alternation populations, R's
  answer is also built as a regex from R stated over sets and run against the computed answer: 27,487 engine cases,
  0 differ, 0 engine disagreements (41,148 whole-matches and probes).
- SABOTAGE: `ABSIMPACT_SABOTAGE=1 timeout 120 python3 -I docs/dev/lanes/absimpact_check.py` flips R's zero-pass
  entry back to today's: 4,858 engine cases differ, so the check can fail.
- DERIVED: read off the rule table by hand, not run (marked so where used).
- REUSED: lane absent's 28 spelling rows (`absent_check.py`'s list, exec'd; kinds re-probed here).

## STATE AT HANDOFF

- STATE: done. Commits on `lane/absimpact`: the evidence script and its output (WIP commits), this report, the
  history-index line.
- OWED: none.
- Rulings file `docs/dev/lanes/absimpact_rulings.md`: empty at the start; R1 (14:15, the owner's R-kinds variant)
  found at the first re-read, applied as section SUB-CHOICES THE RULE LEAVES, "R-KINDS BESIDE R-INTENT", and
  summarised in FOR THE OWNER. Re-read before every commit and before this report. Last entry applied: R1.
- Nothing ruled was edited. No file under `docs/design/` added or changed.
- Names used: R as briefed is called R-INTENT only where R1's variant R-KINDS stands beside it; elsewhere "R".
- Standing questions (docs/design/CLAUDE.md): this report is a decision aid, not a design note. (1) Measurement
  regime: not relevant, no timing or size is measured. (2) Independent control: relevant to the evidence only; the R
  answers are checked against regexes built from R stated over sets (ENGINE-RUN), the parse facts against PCRE2's
  own capture state, the hits against find-all; the sabotage shows the check fails when R's zero-pass entry is wrong.
  (3) What moves on regeneration: not relevant, no table or pin.
- Deviations: none from the brief. One addition: a population with an optional label INSIDE a hit, (OG), because the
  sub-choice on the mark inside `some(...)` / `count(...)` has no answer without one.

## THE RULE AS TESTED

Table (RT), what an absent part contributes (from `part()`; printed as the first block of the `.out`). Kinds: Z a
loop reached and run zero times (the empty list; zero hits); U never reached (an optional skipped, an alternative not
taken, a loop skipped by an optional or alternative around it); P missing in ONE pass of the pairing loop.

| kind | today, nothing written | today, `= v` | R, nothing written | R, `h?` (the mark) | R, `h = v` |
|---|---|---|---|---|---|
| a value | tested | tested, v unread | tested | tested | tested, v unread |
| Z (zero passes) | holds: one label vacuously, a record or joint condition tests the other labels (projection) | v NOT read | FAILS | some value of the group would do (projection) | v read |
| U (never reached) | FAILS | v read | FAILS | projection | v read |
| P (missing in a pass) | FAILS | v read | FAILS | projection | v read |

The sentences implemented:

1. `(h: S)` holds when h has a text in EVERY pass of its pairing loop (for a set-once label: its one text), there is
   at least one pass, and every text is in S. Any absence (Z, U, P) fails it.
2. A record or joint condition is tested per pass of the pairing loop (J7); a pass whose tuple has an absent part
   fails; on zero passes the looped labels are absent, so it fails; outside labels are still read.
3. `h?`: when h has no text in a pass (or no pass), that part ranges over the strings of h's group and the tuple
   holds if SOME of them puts it in the set (lane absent's U5 label mark).
4. `h = v`: v's text stands in on every kind of absence, the empty list included.
5. `some(c)`, `count(c)`, `occurs.*(…, c)` count the passes on which c holds; nothing in them changes.
6. `!c` is the plain complement of c.
7. `h? = v` (both) is not answered by R: the script refuses it (`ValueError`); SUB-CHOICES (d).

Record = product, `(a: S, b: T)` = `(a: S) & (b: T)`: 0 of 259 differ on the record population (OP) and 0 of 1,110
on the zero-pass-record population (RZ) under R (RUN; table "record vs `&`").

## IMPACT BY STATEMENT KIND

Populations (all RUN as matches; answers COMPUTED and, where marked, ENGINE-RUN):
(SP) lane absent's 28 spelling rows; (LI) `/(?:(?<n>\d),)*/`, 1,111 lists of 0-3 digits; (OC) `occurrences(r)`,
`r := /ab(?<g>[xy])/`, 5,461 spans over {a,b,x,y} of length 0-6; (OG) the same with `r2 := /ab(?<g>[xy])?/` (a
hit may lack g); (OP) `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/`, 259 lists; (RZ) `/(?<k>\d)(?:;(?<h>\d))*/`, 1,110
subjects; (ZE) `/(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/`, 11,100; (AL) `[x = /\d/, y = /[a-z]/]`, 36; (T2)
`/(?<h>\d{1,2})(?::(?<m>\d\d))?/`, 11,110.

Table (IM). "moves" = answers that differ between today and R for the same program.

| # | statement kind | verdict under R | moves (smallest example) | how |
|---|---|---|---|---|
| IM1 | plain condition, set-once label (optional, alternative) | SAME | (SP) 0 of the 22 rows that are not Z; (T2) 0 of 11,110 | RUN |
| IM2 | plain condition, looped label, ZERO passes | MOVES | (LI) 1 of 1,111: `''` today HOLDS, R FAILS; (SP) 6 of 28 rows (every Z row: `/(?<n>\d)*x/` on `x`); (OC) 4,839 of 5,461 for `(m: occurrences(r) & (g: "x"))` (every zero-hit span without `aby`; smallest `''`) | RUN, ENGINE-RUN |
| IM2' | the same, to KEEP today's meaning | NEEDS A MARK OR DEFAULT | `(n?: <5)` = today on 1,111 (0 differ); `(n = 0: <5)` 0 differ; `!some((n: !<5))` 0 differ; `(g?: "x")` = today on 5,461 (0 differ) | RUN, ENGINE-RUN |
| IM3 | plain condition, label missing in ONE pass | SAME | (SP) the P rows: today FAILS, R FAILS | RUN |
| IM4 | record `(a: S, b: T)` | MOVES on zero passes only | (OP) 1 of 259 (`''`); (RZ) 5 of 1,110 (`3`: zero passes, k in 3..7; today HOLDS, R FAILS); record = `&`: 0 differ under R on both | RUN, ENGINE-RUN |
| IM4' | the record, to keep today's meaning | NEEDS A MARK, or an alternative | (RZ) `(h?: <5, k: 3..7)` = today on 1,110 (0 differ). (OP), both labels looped, m optional per item: NO mark or default reproduces today: `(h?, m?)` moves 11 (an item without minutes now passes), `m = 0` moves 1 (`''` still fails: h has no text); today's answer needs `(h: <10, m: <30) \| occurs.none((h: /(?s).*/))`, an anything-set (DERIVED) | RUN; the alternative DERIVED |
| IM5 | joint condition `((h, m): R)` | SAME for set-once labels, MOVES as IM4 for looped ones | (T2) `>= (9, 30)`: 0 of 11,110; `m = 0`: 0; lane absent's F column (= R unmarked): (ZJ) 22 of 5,550, (ZN) 69 of 2,526, all zero passes | RUN; (ZJ)/(ZN) from `absent_check.out` |
| IM6 | `!` of a condition; §4.2's "its `!` true"; the guard `!(m: /[\s\S]*/)` | MOVES on zero passes | `!(n: <5)` (LI) 1 (`''`: today FAILS, R HOLDS); `!(h: <10, m: <30)` (OP) 1; `!(g: "x")` over hits (OC) 4,839. The guard: true on EVERY absence under R, zero passes included (LI 1 move), and still not "m has no value at all" inside a loop (a pass missing m makes it true: lane absent's `3:45,3,`) | RUN, ENGINE-RUN |
| IM7 | `all((h: S))` | MOVES as IM2 (sub-choice A1), or SAME as today (A2) | (LI) A1 1, A2 0; (OC) A1 vs A2 4,839 | RUN |
| IM8 | `some(c)`, `count(c)`, `occurs.exactly/at_least/at_most/none` | SAME | (LI) 0 of 1,111 for each of six forms; (OC) `occurs.none((g: "y"))` 0, `some((g: "x"))` 0 | RUN |
| IM9 | `occurrences(x, min = 0)` + a plain condition on a hit's label | MOVES (zero hits now fail) | IM2's 4,839; `min = 0` and `min = 1` under a plain condition now give the same answers (L55: 0 of 5,461 under R, 4,839 today) | RUN |
| IM9' | `occurrences` bare, `contains`, `contains(r & (g: S))`, a hit lacking its label | SAME | L16's bare form 0; `contains(r) & (g: "x")` 0; L61's inner form 0; (OG) a hit without g fails `(g: "x")` both days (the 3,976 moves there are the zero-hit spans only) | RUN |
| IM10 | `list_of` parts (E-HTTP's `name`, E-CTX-7) | SAME on every stated subject; UNDEFINED IN THE DRAFT for an empty block | the draft never states whether `list_of` admits zero items (`grep -n "list_of" docs/design/predicates_draft.md`: no body); if it does, `headers & (name: S)` on an empty block moves (today match, R no match). Counts (E-HTTP) do not move | DERIVED |
| IM11 | arrays of filters; the labelled alternation `[x = ..., y = ...] & (x: S)` ("the alternative lacking x drops") | SAME | (AL) 0 of 36 (R = `[0-5]`, ENGINE-RUN); with the mark, `(x?: /[0-5]/)` keeps the y entries: `[0-5] \| [a-z]`, 26 of 36 differ from the unmarked form | RUN, ENGINE-RUN |
| IM11' | an array of conditions `[(h: <5), (k: 3..7)]` over a looped h (L23's shape) | MOVES on zero passes | (RZ) 5 of 1,110 (`0`: today HOLDS by vacuous h, R FAILS: only k can carry it) | RUN |
| IM12 | `enumerate`, `.index`, `each`, `join` | SAME | no condition reads an absent label in them | DERIVED |
| IM13 | computed labels from a count (`n := count(c)`, `length`'s `nchars`) | SAME | a count is always a value (0 on zero passes): (LI) `c := count((n: <5))`, `(c: ==0)` 0 moves | RUN |
| IM13' | a computed label that READS an absent label (`mnum := $mname.index`, `wd := weekday_of(...)` with an absent input) | UNDEFINED UNDER R | R speaks of conditions on labels; whether the computed label is itself absent is not said (today §4.4 is silent too; joint_condition.md §4B.1's lane reading: absent) | SUB-CHOICES (h) |
| IM14 | `$h` and `${...}` of an absent label; a bound read from one (`(b: >$a)`, a absent) | UNDEFINED UNDER R (and today) | `$` gives no entry (§5.4 `$` row); what a hole or a comparison set built on no entry means is unstated in both | SUB-CHOICES (h) |
| IM15 | bindings and macros: a bound condition (`c := (year: 2000)`), a set macro (`office_hours`), a macro whose body writes the condition (`is_late(f) := (f: >17)`) | SAME / SAME / NEEDS A MARK IN THE BODY | a binding is its expansion (L2, L46); a set carries no label, so the author marks at the label (`((h, m?): office_hours)`); a body that writes `(f: ...)` owns the label's mark for every caller (the field reference that would carry it is paused) | DERIVED |
| IM16 | `padded` and the lift | SAME | the mark ranges over the group's strings through the set as written; a default is compared as written (joint_condition.md §4B.1 `padded` row unchanged) | DERIVED |
| IM17 | defaults `(h = v: S)` | MOVES on zero passes (item 7 becomes the rule) | (LI) `(n = 9: <5)` 1 (`''`: today HOLDS, default unread; R reads 9, FAILS); (RZ) `(h = 9: <5, k: 3..7)` 5; `n = 0` / `h = 0`: 0 | RUN, ENGINE-RUN |
| IM17' | `default.unused` | MOVES SIDE on a label whose only absence is zero passes | (DU) today: `n = 0` and `n = 9` both never change an answer (warn); R: `n = 0` changes `''` (used), `n = 9` changes nothing (warns, clause (b)) | RUN |
| IM18 | the label-twice error, `compare.looped`, the `occurrences` refusals, the default-`$x`-absent error, `empty.search` | SAME | none reads the absent-label rule | DERIVED |
| IM19 | `label.unset` | MOVES (wider) | fires wherever a label can have no text, `*`, `{0,n}` and `occurrences` at `min = 0` included; its text names three fixes (`h = v`, `h?`, an alternative); count in SUB-CHOICES (g) | DERIVED |
| IM20 | `when(c, p)` (= `(x & c & p) \| (x & !c)`) | MOVES through `!c` | (RZ) `P & when((h: <5), (k: 3))` 9 of 1,110 (`0`: today FAILS, c vacuous so p needed; R HOLDS, `!c` true) | RUN, ENGINE-RUN |
| IM21 | `@assert.some/none(X)` | SAME on every draft assertion | none puts a condition on a looped label (`grep -n "@assert" docs/design/predicates_draft.md`) | DERIVED |

THE SPELLING TEST under R (table (SP), RUN): equal spellings that split, of 11 groups: today 5, R 0, R with `n?` 0.

## LOOK-ALIKE ROWS THAT MOVE

All 81 rows L1-L81 (L66 stands after L67 in the table) were read for a label that can be absent in either
form. Rows that MOVE (table (LK)):

| row | forms (abridged) | today | under R | evidence |
|---|---|---|---|---|
| L36 | `(x: S)` vs `all((x: S))` on a repeated label | SAME, "on ZERO iterations both HOLD" | SAME with A1 (both FAIL on zero); DIFFERENT with A2 (`all` holds on zero, plain fails: (LI) 1, (OC) 4,839) | RUN; sub-choice (a) |
| L55 | `(m: occurrences(r) & (g: S))` vs `(m: occurrences(r, min = 1) & (g: S))`, span with NO hit | DIFFERENT: BY DESIGN (first accepts `xyz`) | SAME: 0 of 5,461 differ (today 4,839); both reject `xyz` | RUN |
| L56 | `/(?<n>\d)?x/` vs `/(?<n>\d)*x/` under `(n: <5)` on `x` | DIFFERENT: WARNING | SAME: both FAIL; with `n?` both HOLD | RUN ((SP)) |
| L65 | `/x\|(?<n>\d)+/` vs `/(?<n>\d)*x/` under `(n: <5)` on `x` | DIFFERENT: WARNING | SAME: both FAIL; with `n?` both HOLD | RUN ((SP), A row and Z row) |
| L52 | `(m: occurrences(r) & (g: "x"))` vs `... & some((g: "x"))` | DIFFERENT: BY DESIGN, 4,841 of 5,461 differ (zero-hit spans + `abxaby`) | DIFFERENT: BY DESIGN, 2 of 5,461 (`abxaby`, `abyabx`: "all hits" vs "some hit" only); on zero hits both fail | RUN |
| L30 | `!(x: S)` vs `(x: !S)` on a repeated, optional or zero-iteration label | DIFFERENT: GAP; on zero iterations `!(x: S)` FAILS, `(x: !S)` HOLDS; on an unset x §4.2's two sentences disagree (O28) | DIFFERENT: GAP; on zero iterations `!(x: S)` HOLDS, `(x: !S)` FAILS (the pair flips); O28's unset half is ANSWERED (`(x: !<5)` fails: it needs a text; `!(x: <5)` holds). 801 of 1,111 differ under both | RUN ((LI) L30 rows) |
| L23 | `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]` | DIFFERENT: BY DESIGN | DIFFERENT: BY DESIGN; answers move when the looped label has zero passes ((RZ) 5 of 1,110) | RUN |
| L16 | `(m: occurrences(/^err/))` vs `(m: contains(/^err/))` | DIFFERENT: BY DESIGN | verdict unchanged (no question reads the hits); its reason clause "filters nothing until a question is asked (`some(...)`, `count(...)`, a plain condition)" moves: a plain condition now also requires a hit, so with one `occurrences` = `contains` | DERIVED (IM9) |
| L50 | a record on the left over `occurrences` (OPEN) | OPEN | still OPEN; its x, y would be repeated labels, so on zero hits a condition on them fails under R | DERIVED |

Rows UNCHANGED (verdict and stated answer): L1-L15, L17-L22, L24-L29, L31-L35, L37-L49, L51, L53, L54, L57-L64,
L66-L81. Why, per class: no label in either form can be absent (L1-L5, L7-L15, L17-L22, L24-L29, L32-L35, L37-L49,
L59, L60, L63, L66-L81, every set-once or anchoring row); the forms are group questions or counts, which R does not
touch (L31, L42, L54, L57); the forms are refusals (L51, L53, L62); L58 and L61 compare forms that both need a hit
((OC) L61: 2 of 5,461 differ both days); L64's "out of range = the iteration is absent and a test on it is false"
(CF:62) is already R's reading; L6 (`each` errors on an entry lacking the label, `&` drops it) is the unset case,
unchanged.

## LIBRARY BODIES AND ACCEPTANCE CASES

Table (LB). "survives" = the stated answer is the same under R as written.

| body / case | conditions on labels that can be absent | survives? | smallest edit if not; effect on other callers |
|---|---|---|---|
| `startsWith`, `endsWith`, `anchored`, `padded`, `any_case`, `quoted` | none | yes | — |
| `occurrences(x, min = 0)`, `contains(x) := occurrences(x, min = 1)` | none in the bodies; callers' plain conditions on hit labels | bodies yes; §2.6's ZERO HITS text and hand-check sentence ("a plain `(g: "x")` HOLDS at `min = 0`" on `xyz`) no | none in the body; the TEXT changes: under R `min` decides acceptance only for a bare `occurrences`, counts and marked labels ((OC): `min` 0 vs 1 differ 0 times under a plain condition) |
| `length(S) := chars & (nchars: S)`, `nchars := count((ch: /(?s:.)/))` | `nchars` is a count, always a value | yes (`length(==0)` on `''`: count 0, holds both days; (LI) count rows 0 moves) | — |
| `month_numbered(S) := months & (mnum: S)`, `mnum := $mname.index` | mname is set in every match of `months` | yes | — (an absent mname would be IM13') |
| the group questions (`some`, `all`, `count`, `occurs.*`) | the plain/`all` rows' "HOLDS on zero iterations" | `some`/`count`/`occurs` yes; plain and `all` no | `all`: sub-choice (a) |
| `when(c, p)` | `!c` | answers move on zero passes ((RZ) 9) | none in the body; a caller wanting today's answer marks c's label (`when((h?: <5), ...)`); the body's meaning for other callers is unchanged |
| tuple compares `lex_ge2` / `lex_le2` / `lex_between2` and the size-3 family (the sigil they use is paused) | `(s[k]: ...)` on a compared field | set-once fields yes; a LOOPED field (`compare.looped`) on zero passes no | a mark cannot be written through `^h` today (no spelling); under the joint condition the author writes `((h, m?): lo_hi_set)` at the label |
| E-JSONL (`contains("timeout")`), E-IPV4, E-LUHN, E-SEP, E-DEPTH | no condition on a label | yes | — |
| E-WEEKDAY, E-CAL, E-RFC, E-NEAR (c) | labels and computed labels always set | yes | — |
| E-FILE `rows & (w: >100)` | w set in every record | yes | — |
| E-HTTP (counts over `name`) | counts only | yes (an empty block fails `occurs.exactly(1, ...)` both days) | — |
| E-CTX-1 (`x` always set), E-CTX-7 (`headers & (name: ...)`) | E-CTX-7: a plain condition on a `list_of` part | yes on both stated subjects (each has a header) | if `list_of` admits zero items, an empty block moves (IM10); edit `name?` |
| joint_condition.md §4B examples (`t2`, `t3`, `semver2` with defaults) | set-once | yes ((T2) `m = 0`: 0 of 11,110) | — |
| joint_condition.md §4B.1 LOOPED row, `list & ((h, m = 0): R)` on the empty list | h looped, no default | no: today HOLDS, R FAILS (h has no text; DERIVED from (RT); (OP)'s `m = 0` row moves `''` likewise, RUN) | `h?` or `h = v`; a local edit |

§12 (twelve cases): 0 stated answers move (`sed -n '3214,3600p' docs/design/predicates_draft.md` read case by case;
the only condition on a looped label is E-CTX-7's, whose two subjects each have a header). No library BODY needs an
edit; the text that moves is the draft's own statements of the zero-pass rule (next section's count).

## WHERE ABSENCE-HOLDS WAS THE POINT

Table (AH). The statements for which "a condition holds over none" was chosen, with the words then.

| # | where | words (verbatim) | the example | the alternative then, and why it went | under R the author writes | RUN |
|---|---|---|---|---|---|---|
| AH1 | CF:180 (2026-11-13 late), the MANAGER'S leaning on label types | "a comparison on an unset label is false (and `!` of it true), `some` over no occurrences is false, `all` is true, plus a warning when a plain reference can be unset" | an optional group that may be unset | none offered; this is where "`all` is true over none" enters, as the manager's lean, not the owner's words | `all` per sub-choice (a); `(h?: S)` | — |
| AH2 | CF:933 (2026-11-15), the owner on "every hit" with zero hits | "2. this is subtle tricksy question. What's missing is the + or * control. Perhaps search needs a min max with defaults." | `(m: search(r) & (g: "x"))` on a value with no hit (`xyz`, §2.6's hand checks) | rev 8's lean (O28: "a condition holds when EVERY occurrence is in the set AND there is at least one (zero iterations = unset = fail)", the vacuous reading written `!some((g: !S))`; review r1 OWN-4's proposal). R IS that lean plus the mark. It went in rev 9 on the RECORD's reading of his words (CF:937-940: "a plain condition on the hits stays 'all hits' and is true over zero hits when zero hits are allowed"), which review r10 FIXB-8 found too thin to rule | `(m: occurrences(r) & (g?: "x"))`: 0 of 5,461 differ from today; or `occurs.none((g: !"x"))` / `!some((g: !"x"))` | (OC) |
| AH3 | CF:997-1000 (2026-11-15), the per-match boundary | "Agree with lean" (the lean: "a loop that was REACHED and ran zero times satisfies a plain condition (`/x\|(?<n>\d)+/ & (n: <5)` on `x` fails, like the set-once form; `(?:(?<n>\d),)*` on an empty value holds)") | `/(?:(?<n>\d),)*/ & (n: <5)` on the empty span | rev 9's statement by the label's own quantifier, under which `/x\|(?<n>\d)+/` on `x` held (review r10 FIXB-2); "fail" was not on the table that day | `(n?: <5)`: 0 of 1,111 differ from today; or `(n = 0: <5)`: 0 | (LI) |
| AH4 | 2026-11-16 12:45, zero-pass-record (CF:1544-1558) and `predicates_future.md` item 6 | "zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from themselves' category"; on an author-written empty member: "The author's contribution is the * form so they know they are providing a possibly empty set." | `/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3..7)` on `9` FAILS (the outside label is tested); the manager's wording kept "a plain single-label condition still HOLDS on zero passes" | the per-pass rule read literally (`9` holds vacuously) went; R keeps `9` failing. His second quote is the one place his own words give the reason for absence-holds: the `*` IS the author's statement that the list may be empty | `(h?: <5, k: 3..7)`: 0 of 1,110 differ from today. Under R the `*` alone no longer says "empty is fine for my conditions"; the mark says it | (RZ) |

How often the draft's own text needs the old meaning. Command: `grep -nE "(zero (passes|iterations|hits|times)|empty
(list|span)|the empty)" docs/design/predicates_draft.md docs/design/joint_condition.md | grep -E "HOLDS|holds|HOLD\b"`
(11 lines in the draft, 16 in the note), classified by hand into distinct statements whose stated answer moves under
R: in the draft 8 (§2.6 ZERO HITS and its `xyz` hand-check sentence, the §4.2 witness on the empty span, the §4.3
table's plain and `all` rows, L36's zero clause, L55, L56, L65); in joint_condition.md 7 (J7's quoted wording, §4B.1's
LOOPED row and its nested `5` example, §4D row D9, (ZD)'s all-looped list, (Z1), (ZJ)'s empty-set row, the
zero-pass-empty example `0-3`). §12: 0. Each is restored by one mark on the looped label, except the all-looped
record with an optional field per item (IM4'), which needs an alternative.

## SUB-CHOICES THE RULE LEAVES

Each with both answers run; the smaller-surprise one is named as THE LANE'S, not the manager's.

(a) `all((h: S))` on zero values. A1: the same as the plain condition (FAILS). A2: "every, possibly none" (HOLDS), so
`all((h: S))` is the spelled-out mark for a one-label condition. (OC) A1 vs A2: 4,839 of 5,461; (LI) 1 of 1,111.
Lane's pick: A2. Reason: today's text defines `all` as the plain condition, and under R the only behaviour that keeps
`all` a separate word is the vacuous one, which is also the word's ordinary English reading ("all of none"); A1
leaves `all` a synonym. Cost: L36 becomes DIFFERENT (BY DESIGN).

(b) `!` of a condition on a MARKED absent label. B1: the plain complement (`(n?: <5)` holds on absent, so `!(n?: <5)`
FAILS). B2: the mark stays outside the `!` (absent acceptable, HOLDS). (LI) 1 of 1,111 differ (`''`). B1 equals
today's `!(n: <5)` on all 1,111 (0 differ). Lane's pick: B1 (one meaning of `!`, §6 of THE RULE AS TESTED).

(c) A mark on a label that can never be absent. (T2) `((h?, m): ...)` vs `((h, m): ...)`, h required: 0 of 11,110
differ. Answers: a WARNING like `default.unused` (a), or an error. Lane's pick: the warning, for the reason
joint_condition.md §4B.1 gives for the default (a library condition laid over several patterns, the field optional in
some).

(d) A mark AND a default on one label, `m? = 0`. D1: an error (two answers to one question; lane absent's reading).
D2: the default wins (= `m = 0`). D3: the mark wins (= `m?`). (T2) D2 vs D3: 1 of 11,110 (`9`: D2 FAILS, D3 HOLDS).
Lane's pick: D1. Under R-KINDS (below) the combination is the ONE way to cover both kinds, so it cannot be an error
there.

(e) The mark inside `some(...)` / `count(...)`, on a hit that lacks the label ((OG), `r2 := /ab(?<g>[xy])?/`). E1: a
hit without g counts as meeting `(g?: "x")` (the projection, per hit). E2: it does not (the group question counts
values). `some((g?: "x"))` E1 vs E2: 885 of 5,461 (`ab`: E2 FAILS, E1 HOLDS); `occurs.exactly(1, (g?: "x"))`: 848.
Lane's pick: E2 with a warning, or an error: a count of "values in S" that counts absences is the surprise.

(f) Zero-pass-empty for a MARKED label (the joint set empty for every value). (ZE) `(h?: <$a, k: 3)` on `0-3` (a = 0,
zero passes): F1 (projection: no h is <0, FAILS) vs F2 (absent acceptable outright, HOLDS): 1 of 11,100. Unmarked
labels under R: no corner (absent fails, 10 of 11,100 differ from F2: every zero-pass `k = 3` subject). Lane's pick:
F1 (the mark has one meaning, "some value would do", and the corner is then the plain consequence that no value
would); the corner survives only for marked labels.

(g) How noisy `label.unset` becomes. Command: the backtick-span census in
`$PCREC_TMPDIR/scratch/absimpact/proto.py` (spans holding a loop or `occurrences` and a condition; 18 in the draft, 10
in joint_condition.md), classified by hand: programs with a plain, record or joint condition on a label that can
have zero passes: the draft 7 (`(m: occurrences(r) & (g: "x"))`, `(m: occurrences(r) & (g: S))`, `occurrences(r) &
(g: S)`, `(m: occurrences(/(?<g>a)?b/) & (g: "a"))`, `/(?<n>\d)*x/ & (n: <5)`, `/(?:(?<n>\d),)*/ & (n: <5)`, E-CTX-7
if `list_of` admits zero), joint_condition.md 8 (the list and nested programs; the sibling-loop program is a compile error and the repeated
`(n: <5)` is the draft's, both left out; the two spellings of k's set in the zero-pass-record example counted
apart). Today the warning fires on 1 of those 15 (g optional inside a hit); under R it fires on all 15.
Every condition over a `*` loop draws it unless the label is marked or defaulted.

(h) UNDEFINED UNDER R (R does not say; both answers named, none chosen):
- a computed label reading an absent label (IM13'): (i) the computed label is absent, its conditions fail unless
  marked or defaulted (joint_condition.md §4B.1's lane reading, table (DC)); (ii) a compile error, since §4.4 asks a
  mapping to be "total on its pattern".
- `$h`, `${$h}` and a bound `>$a` with the label absent (IM14): (i) no entry, so the hole or the comparison set is
  empty and the condition fails ("a condition needs a text" applied to the value side); (ii) a compile error where the
  label can be absent (the existing "the default `$x` can itself be absent" error, widened).
- a mark passed through a macro's label parameter (IM15): the field reference is paused, so there is no spelling to
  decide.
- `list_of`'s minimum (IM10): a gap in the draft, not in R.

### R-KINDS BESIDE R-INTENT (rulings R1)

The owner's words (14:15): "What if the mark ? only meant tested but didn't exist. Like x*. Then the default = is
never tested, alternation. Together they are never tested or tested and empty is this default." THE MANAGER'S reading
(R1, stated as his): two absence kinds, each with its own control. REACHED-EMPTY (a quantifier reached and run zero
times: `x*`, and by his 13:29 remark "Even /x?/ is a loop from 0 to 1", `x?` skipped) is accepted only by `h?`;
NEVER-REACHED (an alternative not taken) only by `h = v`; `h? = v` reads v on either; nothing written: FAILS. R as
briefed (R-INTENT): `h?` and `h = v` are intents over every kind.

Table (RK) (COMPUTED from `part_kinds()`; `.out` block (RK)):

| kind | nothing | `h?` | `h = v` | `h? = v` |
|---|---|---|---|---|
| R-kinds, reached-empty (`x*` zero times, `x?` skipped, missing in a pass by a skipped `?`) | FAILS | some value would do | FAILS | v read |
| R-kinds, never-reached (an alternative not taken, in the match or in a pass) | FAILS | FAILS | v read | v read |
| R-intent, any kind | FAILS | some value would do | v read | sub-choice (d) |

A loop NEVER REACHED because an optional around it was skipped (`(?:(?<n>\d)+)?x` on `x`): K1, by the optional (the
`?` ran zero times: reached-empty, `n?`); K2, by the label's own loop (never reached: `n = v`). R-intent: one class,
nothing to decide.

THE SPELLING TEST, `(n: <5)` with v = 3, over lane absent's 11 groups of equal spellings (RUN kinds; split = rows of
one group answer differently):

| written | R-kinds K1 | R-kinds K2 | R-intent |
|---|---|---|---|
| nothing | 0 | 0 | 0 |
| `n?` | 9 | 8 | 0 |
| `n = 3` | 9 | 8 | 0 |
| `n? = 3` | 0 | 0 | 0 |

Which control each spelling needs under R-kinds (from the `.out`): `(?<n>\d)?x`, `(?<n>\d){0,1}x`, `(?<n>\d)??x`,
`(?<n>\d)*x`, `(?<n>\d){0,2}x` need `n?`; `(?:(?<n>\d)|)x` and `(?:(?<n>\d)+|)x` need `n = v`; the greedy/lazy pair
`(?:(?<n>\d)*)?x` (PCRE enters the optional: reached-empty, `n?`) and `(?:(?<n>\d)*)??x` (PCRE skips it: `n?` under K1,
`n = v` under K2), so under K2 greedy vs lazy again changes which control works. Under R-intent every row takes either.

The time example, `((h, m ...): >= (9, 30))`, minutes absent, on `9` / `10` (COMPUTED):

| spelling of the optional part | goal | R-kinds writes | R-intent writes |
|---|---|---|---|
| `(?::(?<m>\d\d))?` (reached-empty) | "absent means 0" (`9` out, `10` in) | `m? = 0` (`m = 0` alone is never read: `10` FAILS) | `m = 0` |
| the same | "does not matter" (both in) | `m?` | `m?` |
| `(?::(?<m>\d\d)\| o'clock)` (never-reached) | "absent means 0" | `m = 0` (or `m? = 0`) | `m = 0` |
| the same | "does not matter" | CANNOT (`m?` FAILS both: no projection for a not-taken alternative) | `m?` |

The labelled alternation with a list-valued entry, `[x = /(?:(?<n>\d),)*/, y = /[a-z]+/]`, "an x record whose list
may be empty, but not a y record" (RUN parse, 7 subjects): R-kinds `(n?: <5)` gives the intended answer on all 7 (the
empty x list is reached-empty, a y record is never-reached); R-intent `(n?: <5)` also admits `a` and `bc` (2 wrong);
R-intent needs a condition that x has a text, `(n?: <5, x: /(?s).*/)`, right on all 7 (an anything-set, item 8's snag).

What R-kinds cannot say: accept a not-taken alternative without naming a value (the o'clock row); a joint set where no
one default fits the never-reached case ("does not matter" by projection: joint_condition.md §4B.4's date case, table
(DD): every default day misses one of three months; DERIVED); and the kind of an absence is read from the pattern's
spelling, so the same intent needs a different control after a refactor between equal spellings (9 or 8 split groups
with one control written). What R-intent cannot say in one mark: "absent in this kind only" (the x/y example).

## FOR THE OWNER

You asked two things: what the rule (a condition needs a text; the mark `h?` and the default `h = v` are the author's
controls) does to everything else, and where "absence matches" made sense.

**(a) Where absence-holds was the point.** Three places, and in each the author can get the old answer with one mark:

- The hits of a search with zero hits. Your words (2026-11-15): "this is subtle tricksy question. What's missing is
  the + or * control. Perhaps search needs a min max with defaults." Example: "every hit has g = x" on a text with no
  hit. Before that, the draft's lean was "every hit, and at least one" (the same as this rule); it was withdrawn on the
  record's reading of your words, not on your words. Under the rule: `(g?: "x")`, the same answers on all 5,461 texts
  tried.
- The empty list. You agreed (2026-11-15) with "a loop that was reached and ran zero times satisfies a plain
  condition", example `/(?:(?<n>\d),)*/ & (n: <5)` on the empty text. Under the rule: `(n?: <5)` or `(n = 0: <5)`,
  the same answers on all 1,111 lists tried.
- The `*` as the author's statement. Your words on an author-written "empty" value (2026-11-16): "The author's
  contribution is the * form so they know they are providing a possibly empty set." This is the one place your own
  words give the reason. Under the rule the `*` no longer says "empty is fine for my conditions"; the mark says it:
  `(h?: <5, k: 3..7)` gives today's answers on all 1,110 texts. Your zero-pass answer (`9` fails) is kept.

**(b) What changes for an author, largest first.**

- Every condition on a label inside `*`, `{0,n}` or a search with no minimum now fails on the empty case: the empty
  list (1 of 1,111 lists tried), and every text with no hit for a search (4,839 of 5,461). The draft states this old answer in
  15 places (8 in the draft, 7 in the joint note), none in the twelve worked examples.
- `!` of such a condition, and `when(c, p)`, flip there too (`when`: 9 of 1,110).
- A default is read on the empty list as well (`(n = 9: <5)` now fails on it); a default inside the set is how
  "empty is fine" is also written.
- The "label may be unset" warning fires on every condition over a `*` loop (15 programs in the two documents, 1
  today), unless the label is marked.
- One shape has no one-mark spelling: a record over a list whose items have an optional field, where the empty list
  should pass but an item without the field should not. It needs an extra alternative.
- Four look-alike pairs become the same: `?` vs `*` (and an alternative vs `*`) under a condition, a search with
  minimum 0 vs 1 under a condition, and one pair turns over (`!(x: S)` vs `(x: !S)` on the empty case). The 11
  groups of equal patterns: 5 split today, none under the rule.

**(c) What stays the same.** Optional fields and alternatives (they already fail); a field missing in one item;
counts, `some`, `occurs`; records equal to `&` of their parts; joint conditions on fields that appear once;
dropping an alternative that lacks the label; `padded`; every library body; all twelve worked examples.

**(d) Choices the rule leaves.**

- `all(...)` on an empty list: fails like a plain condition, or holds (then `all` is the spelled-out mark).
- `!` of a marked condition on a missing field: false (plain negation), or true.
- A mark on a field that is never missing: a warning, or an error.
- A mark and a default on one field: an error, or one of them wins.
- A mark inside `some`/`count` on an item missing the field: counted, or not.
- A computed value read from a missing field: missing itself, or a compile error.
- Your 14:15 variant (the mark for "ran but empty", the default for "alternative not taken"): it expresses "an x
  record whose list may be empty, but not a y record" with one mark, which this rule needs two conditions for; it
  cannot accept a not-taken alternative without naming a value, and which control works depends on how the pattern
  is spelled (8 or 9 of the 11 equal-pattern groups split when one control is written; 0 under this rule).

---
What the evidence favours on each of his two stated criteria (the lane's, not a recommendation):
- Simplifying semantics: under the rule as briefed one absence state and two controls, no equal-pattern group splits;
  the variant brings back a pattern-dependent split for each single control.
- Saving people from themselves: the rule passes nothing that has no text unless the author marks it, at the cost of
  failing every unmarked empty list, which `label.unset` then names.
