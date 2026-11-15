# predspec9 report: predicates_draft.md rev 9, the owner's last two 2026-11-15 entries folded (design only)

## STATE AT HANDOFF

STATE: done. Branch `lane/predspec9`, from main 5d0e75680. Deliverables: `docs/design/predicates_draft.md` rev 9
(changelog entry first), this report, the oracle script and its output (`docs/dev/lanes/predspec9_reading.py`,
`predspec9_reading.out`) and the lane's line in `docs/dev/history/claude_md/docs__dev__lanes.md`. Design text only:
nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/` or `docs/spec/` touched; COND-FAMILY.md and plan.md not
edited. Rulings file `docs/dev/lanes/predspec9_rulings.md`: empty (0 bytes, `wc -c`) at every commit and at this
report; last R-n applied: none. Validation: `make test-plan-lint` in the worktree (checks passed: 2, failed: 0);
pre-commit staged checks passed (52 passed, 0 failed). OWED: none from this lane (no suites by brief). The cost
MEASUREMENT the owner asked for is filed as draft §13 O57, deliberately not run (brief: "Do not measure anything").

Premise test held: `grep -c 'ONE reading everywhere' docs/design/plan_row_bodies/COND-FAMILY.md` = 1; the draft's
changelog said rev 8. "CF:n" = line n of COND-FAMILY.md at 5d0e75680 (961 lines, `wc -l`): entry 1 CF:927-947 (his
words CF:928-934), entry 2 CF:948-961 (his words CF:949-952).

Size: `wc -l docs/design/predicates_draft.md` = 2,539 lines (rev 8: 2,284); `git diff --stat` against main: 428
insertions, 173 deletions at the WIP commit.

## RULINGS FOLDED

(1) ONE READING (CF:950, CF:953-955; his words "I think it will help if our rx is consistent", RULED). §4.5 rewritten
as "Ambiguity: ONE READING (PCRE's)": a condition on any label, set once or in a loop, at every level, reads the parse
PCRE2 gives the pattern matched against exactly the value (anchored both ends). The 11-14 some-parse rule and its
"library patterns are checked unambiguous" guard are SUPERSEDED. What changes for a default-level program, said
plainly in §4.5 and §6.1: an UNAMBIGUOUS label costs nothing (all parses agree, the plain automaton computes it); an
AMBIGUOUS label gets PCRE's reading built as automaton code (backreference-free: a regular set, LEAN claim), its extra
states shown, and over the budget a refusal naming the higher level (`captures` if its tagged automaton follows PCRE
priority, else `vm`): marked LEAN (manager, CF:943-944). NEW and stated once: THE CONDITION FILTERS THE PARSE, IT
NEVER STEERS IT (§4.5, L59; a rejecting callout would steer PCRE into another parse and compute some-parse).
Also touched: merged-narrowing sentence (gone: one parse), `label.ambiguous` text (§4.5, §7.1: the pointer to
validation, with a sample message), §6.1 (the old "promise; only some-parse keeps it" withdrawn: "rev 8 kept the
promise by changing the answer; rev 9 keeps the answer and prices the promise"), O33 and C36 RESOLVED, C11 re-resolved,
L34 WARNING -> SAME, §0.3 glossary rows "PCRE's reading" and "set once / repeated".

(2) COST OWED (CF:949-950, CF:955-957). §13 O57: what is measured (minimal-DFA states of PCRE's reading over the
some-parse automaton, ratio + absolute, build time beside), population (the worked examples as a zero-extra control,
§4.5/§2.6/L34/L59 examples, and the `.rxt` corpus patterns the ambiguity check flags, each with a fixed condition
family), regime, independent control (libpcre2 anchored match + Python `re`; population counted twice, K35), what
moves (nothing emitted; feeds O39 and the go/no-go). §0's standing questions 1-3 updated to cover it. Not run.

(3) AMBIGUITY THE AUTHOR'S TO VALIDATE (CF:950-951, CF:957-959). §5.6 example:
`@assert.some("123" & P & (a: "12"))` / `@assert.none("123" & P & (a: "1"))` with `P := /(?<a>\d+)(?<b>\d+)/`. The
existing forms CAN express "on this witness, label a is `12`" BECAUSE of the one reading (under some-parse both
assertions passed whatever was meant), so no gap is filed and no new form proposed.

(4) A BOUND NAME HOLDS THE TRANSFORMED RX (CF:929, RULED). O54's `d :=` half RESOLVED (`hits := search(r)`, applied
as `(m: hits)`); the owner's example in §2.6 respelled with `hits`. The record-on-the-left half of O54 stays open.

(5) `search(x, min = 0)` (CF:933-934 his "perhaps", CF:960 `min` only; no `max`, CF:951-952 RULED). Library text
`/(?s)(?:.*?(?<hit>${x})){${min},}.*/`; `contains(x) := search(x, min = 1)` as ONE definition (labels allow it, and
it REMOVES a look-alike: rev 8's own `contains` body read its argument's labels at the RIGHTMOST occurrence under the
one reading; L58). A proof that `min = 1` finds the same hits as `min = 0` whenever one exists (§2.6). Zero hits: a
plain condition HOLDS when zero hits are allowed (rev 8 lean "false" withdrawn); `min = 1` rejects. §4.2 now states
the boundary once: a SET-ONCE label (incl. `?`) that is unset fails a condition; a REPEATED label with zero iterations
is not unset (L56: `(?<n>\d)?` vs `(?<n>\d)*`, WARNING via `label.unset`). Look-alike rows L55 (zero hits by `min`),
L57 (`min = 2` re-cuts hits; lean ERROR), L58. `max` filed in O58 with its confusion ("first N hits" vs "at most N",
the latter staying `occurs.at_most`).

(6) The manager's calls, each marked LEAN (manager) and collected in §13 "DECIDED BY THE MANAGER": nullable search
argument refused with `x & !""` (O53); user label `index`/`label` an error (O31, §5.4 `.` row); `(?s)` in the library
transforms (§2.6, §8); `["US" => ...]` dropped for computed labels (C7). Still OPEN as asked: one-hit access at the
captures level (O50, §2.6, LEAN); `^`/`$` in a filter's argument (O49).

Bookkeeping: changelog, §0 status marks table (a new table for the two entries: what is his words vs the record vs
the manager's), mark table (`.` and `=` rows), kind table (unchanged: no new kind), glossary, two-way census
(`search` row gains `min`), §12 REV 9 RE-CHECK paragraph, §13 (C36, O33, O54 half, O28 half RESOLVED; O57-O59 new),
§15 provenance row.

## EXAMPLES RE-CHECKED

ORACLE. `python3 -I docs/dev/lanes/predspec9_reading.py` (sha256 a8e1fb68...6203), system libpcre2-8 10.46
(`dpkg -l libpcre2-8-0`: 10.46-1ubuntu0.1) through its public API (ctypes; no PCRE2 source read), Python 3.14.4 `re`
as a second engine. Each pattern is matched against the whole value (PCRE2_ANCHORED|PCRE2_ENDANCHORED). For search,
the loop `(?:.*?(X)){min,}` is UNROLLED into nested optionals with one group per iteration, so the final match holds
every hit and nothing abandoned by backtracking is recorded (rev 8's callout oracle could not have shown the `min = 2`
re-cut). Output verbatim: `docs/dev/lanes/predspec9_reading.out`. Every row matched its hand derivation; libpcre2 and
`re` agreed on every row.

| check | min 0 | min 1 (= `contains`) |
|---|---|---|
| `abx aby abx` / `/ab(?<g>[xy])/` | `abx`@0 g=x, `aby`@4 g=y, `abx`@8 g=x; accepts | same three; accepts |
| `xyz` (no hit) | no hits; accepts (plain `(g: "x")` holds) | REJECTED |
| `aaa` / `/aa/` | `aa`@0; accepts | `aa`@0; accepts |
| `err x err` / `/^err/` | `err`@0; accepts | `err`@0; accepts |
| `x err` / `/^err/` | none; accepts | REJECTED |
| `err\nerr x\nok` / `(?m)^err` | `err`@0, `err`@4 | same |
| `aab` / `/aab\|a/` | `aab`@0 | `aab`@0 (`min = 2`: `a`@0, `a`@1, the re-cut; find-all `['aab']`) |

Set-once ambiguous label: `/(?<a>\d+)(?<b>\d+)/` on `123`: a = `12`, b = `3` (both engines), so `(a: 12)` holds and
`(a: 1)` does not. Library-body readings: `(?s).*ab(?<g>[xy]).*` on `abx aby` gives g = `y` (rev 8's `contains` body,
rightmost); `(?s).*(?<n>\d+)` on `ab123` gives n = `3`, the lazy `(?s).*?(?<n>\d+)` n = `123`. The `/a*/` row is not
re-run: the unrolled form does not stop at an empty iteration (six empty hits), so rev 8's loop run (1 hit) stands
and the argument is refused anyway.

§12 WORKED EXAMPLES against the new §4.5. Test: does any condition read an AMBIGUOUS label? None does, so NO case's
answer depended on some-parse; code lines unchanged (rev 8's command, `awk '/^## 12\./,/^## 13\./' FILE | grep '^    '
| sed 's/#.*//'`, 67 lines, `cmp` against the same extraction from main: IDENTICAL; the only §12 edits are the REV 9
RE-CHECK paragraph and the census row).

| case | verdict | why its labels are unambiguous (or no condition) |
|---|---|---|
| 12.1 E-JSONL | unchanged | no label condition; `contains("timeout")` is now `search(.., min = 1)`, the same set |
| 12.2 E-WEEKDAY | unchanged | `\d{4}`, `\d\d`, `-`: fixed widths |
| 12.3 E-IPV4 | unchanged | no label condition |
| 12.4 E-LUHN | unchanged | no label condition |
| 12.5 E-CAL | unchanged | fixed widths (isodate) |
| 12.6 E-RFC | unchanged | `\d{1,2}` ends at the space; names from fixed lists |
| 12.7 E-NEAR | unchanged | (c) two fixed-width isodates around `\s*,\s*` |
| 12.8 E-FILE | unchanged | `[^,]+` ends at `,`; `\d+` to the line end |
| 12.9 E-HTTP | unchanged | `token` has no `:`; `fvalue` has no CR/LF (predx §3.8, line 518), so iterations split one way |
| 12.10 E-SEP | unchanged | no label condition |
| 12.11 E-DEPTH | unchanged | no label condition |
| 12.12 E-CTX | unchanged | E-CTX-1/7: `\w` + one space, whole `name`; 2-6 are compile errors; the agreeing look-alike's `v` is the whole value |

§0.1 ROWS against the new §4.5 and `min`:

| rows | verdict |
|---|---|
| L1-L15, L17-L33, L35, L37-L50, L52, L54 | unchanged |
| L16 | restated: "search with its default `min = 0` never rejects"; with `min = 1`, SAME as contains |
| L34 | CHANGED: DIFFERENT: WARNING -> SAME (both levels read PCRE's parse, a = `12`; the program is false at both). The one row whose answer depended on some-parse: before, the default level (some-parse per condition) said TRUE for `(a: <5) & (b: <5)` on `123` and `vm` said FALSE; after, FALSE at both |
| L36 | restated: on zero iterations both HOLD (was: follow O28, lean fail) |
| L51 | restated: `!search(r, min = 1)` = `!contains(r)` added |
| L53 | restated: the refusal is the manager's call (LEAN) |
| L55-L59 | new (zero hits by `min`; `?` vs `*`; `min = 2` re-cut; `contains` = `search(min = 1)`; condition vs constraint in the pattern) |

Other before/after answers that moved (not §12 or §0.1 rows): `P & (a: "1")` on `123` with `P = /(?<a>\d+)(?<b>\d+)/`
TRUE -> FALSE (§4.5); a plain condition on hits over a value with no hit FALSE (rev 8 lean) -> TRUE at `min = 0`
(§2.6); `contains(/ab(?<g>[xy])/) & (g: "x")` on `abx aby`: TRUE under some-parse -> FALSE under the one reading with
either body (rightmost hit has y; with the search body, not every hit has x); `endsWith(/(?<n>\d+)/) & (n: >100)` on
`ab123`: TRUE (some-parse) -> TRUE with the lazy body, would have been FALSE with rev 8's greedy body (n = `3`).

## CONFLICTS FOUND

None left unreconciled; the STOP RULE did not fire. Tensions found and how each was reconciled:
1. The 11-14 some-parse rule (RULED, CF:583) vs the one reading (CF:950, CF:953-955): a later ruling in the owner's own
   words that names the earlier one as superseded; recorded as SUPERSEDED, not a conflict.
2. "Library patterns are checked unambiguous" (part of the same RULED Q2): it was some-parse's guard; under one reading
   it becomes the library author's own validation by assertions (§4.5 LIBRARY PATTERNS, LEAN), with the warning scope
   left open (O59).
3. §4.2 "a condition on an unset label fails" (LEAN, CF:173, cited "ruled" per O3) vs "true over zero hits when zero
   hits are allowed" (CF:937-940): reconciled by the boundary stated once in §4.2 (set once vs repeated; `?` is set
   once, LEAN), with look-alike L56.
4. FINDINGS (not conflicts with a ruling, filed with leans): `min` above 1 re-cuts hits under PCRE's reading (O58,
   L57); a library body's gaps decide its argument's label reading (O59, the `contains` rightmost and greedy
   `endsWith` cases, fixed by one definition and a lazy body, LEAN); an oracle or build that checks a condition by a
   rejecting callout would compute some-parse, not PCRE's reading (§4.5, §0 standing question 2).

## OPEN ITEMS

Questions for the owner, plain words, each with an example and a lean:

1. When PCRE's reading of an ambiguous label is expensive, what happens? Example: `/(?<a>\d+)(?<b>\d+)/ & (a: "12")`
   must answer the way PCRE splits `123` (a = `12`), which the plain automaton cannot see. Lean (the manager's): build
   it as automaton code with its cost shown; over the budget, refuse and name the level that computes it at run time.
   The cost itself is the measurement you asked for, filed, not run.
2. Reading ONE hit's text (the third hit, keeping hits 1 and 3): the captures level? Example: `$m.hit[2]` = `aby` in
   `abx aby abx`. Lean: yes, captures; your array example is the intended behaviour there; counting and "some hit"
   questions stay default.
3. `^` in a filter's argument: the start of the value being filtered? Example: `contains(/^err/)` = "starts with err".
   Lean: yes, one span per filter role.
4. Can `min` be more than 1? Example: searching `aab` for `aab|a`: one hit normally, but "at least 2" makes PCRE cut it
   into `a`, `a`. Lean: `min` is 0 or 1; "at least 2 hits" is written with the `occurs` count, which never re-cuts.
5. `contains` defined as "search with at least one hit", one definition? Example: with its old body, a condition on a
   label inside `contains(...)` read the LAST occurrence; as a search it reads every hit, leftmost first. Lean: yes,
   and `endsWith` gets a lazy gap so its argument starts as far left as it can (n = `123` in `ab123`, not `3`).
6. Optional vs repeated with nothing there. Example: `(n: <5)` on a value with no digit fails for `(?<n>\d)?` (unset,
   with a warning) but holds for `(?<n>\d)*` (zero iterations, which `*` allows). Lean: keep that difference; the
   quantifier you wrote decides.
7. The "ambiguous" warning for ambiguity a library body makes. Example: every `search` has a gap that could swallow a
   hit. Lean: warn only for ambiguity in your own pattern text; the library states and tests its own reading.
8. For your review, the manager's four calls (made, marked as the manager's): refuse a search for something that can
   match nothing (fix: add `& !""`); a label may not be named `index` or `label`; library gaps cross line breaks; the
   `["US" => ...]` lookup table is dropped for computed labels.

Not for the owner yet (filed in the draft): the cost measurement itself (O57: when the predicate front end nears a
build go; it needs an automaton construction pcrec lacks today); the record on the left of a binding (O54 second
half, L50); the hit label's name and a short "count the hits" spelling (O55); which loop a record means at mixed
depths (O56); `!(x: S)` vs `(x: !S)` on a repeated label (O28 rest, L30 GAP); the level a budget refusal names waits
on [ENG-TDFA] (O59, O6).
