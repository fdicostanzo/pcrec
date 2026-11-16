# predspec13 report: predicate spec rev 13

Lane predspec13 (opus), 2026-11-15. Design only; no build go. Touched: `docs/design/predicates_draft.md`, this
report, `docs/dev/lanes/predspec13_anchor.py` / `.out`, and one history-index line
(`docs/dev/history/claude_md/docs__dev__lanes.md`, N-1 / D149). Nothing under src/, cli/, lib/, memfn/, tests/,
docs/spec/; not COND-FAMILY.md, plan.md or docs/dev/reviews/.

## STATE AT HANDOFF

OWED: none

- DONE. `docs/design/predicates_draft.md` is rev 13 on `lane/predspec13` (changelog entry "rev 13").
- Premise test: the draft's changelog named rev 12 the latest; `git show main:...COND-FAMILY.md | tail -n 60` showed
  the three entries (~20:40, ~20:55, ~21:20); the review draft existed. All held.
- Rulings file `docs/dev/lanes/predspec13_rulings.md`: empty at the first read; R-1 (manager, 20:33) present at the
  second read (before the second WIP commit) and applied in full: (a) per-call hit label name, O55 (i) RESOLVED;
  (b) no count warning, O63 CLOSED, L66 GAP -> BY DESIGN; (c) the owner's hole example as an acceptance row with its
  near row, oracled. Re-read before the final commit and before this report: LAST R-n APPLIED: R-1.
- STOP RULE: not triggered. The ~21:20 entry corrects part (a) of the ~20:55 one; "later wins on the same point"
  resolves it (exact ends ruled; the "filter role" wording not ruled).
- Oracle: `timeout 300 python3 -I docs/dev/lanes/predspec13_anchor.py` (libpcre2-8 10.46 by ctypes and Python 3.14
  `re`): 47 rows, "engines disagree on 0 rows", rc 0. It EMULATES the ruled rule (each operand matched as plain PCRE
  with its span as the subject; a hole opens no scope); it is not pcrec.
- Validation in the worktree: `make test-spec-history`: 11 passed, 0 failed. `make test-plan-lint`: FAILS on two
  violations, neither in a file this lane touched: PL14 for `docs/dev/lanes/land1115c_report.md` (pre-existing on
  main, as rev 12's report said) and PL14 for `docs/dev/lanes/predspec12_report.md` line 26, which QUOTES that
  lint message and so itself cites a plan line (inherited from lane/predspec12; it will go red at merge unless the
  manager rewords it). selftest 45 plants, 0 failures. No suite owed (design only; the owner's evening hold).

## WHAT REV 13 CHANGES

Rulings folded (COND-FAMILY.md on main):
- `search` -> `occurrences` (CF:1026-1031): every definition, row, case and example outside quotations and
  history; §2.6 retitled; O61 CLOSED; the label `hit` kept (its name not ruled).
- `anchored` has EXACT ends (CF:1048-1053, correcting CF:1033-1040 (a)): `anchored(rx) := /\A(?:${rx})\z/`; O62
  CLOSED; L68 DIFFERENT -> SAME; E-HTTP's final pattern written `anchored(block)` (the same text).
- rx-text `&` under ON is the operator exactly where `|` means alternation; a literal is `\&` or `[&]`
  (CF:1041-1046); O60 (d) CLOSED; §11, §5.4 `&` row, §0 G3 and §0.2 respelled; rev 11 withdrew only the rewrite.
- both `&` operands are filter roles, and an explicit anchor in an operand draws a warning (CF:1054-1062):
  §11 THE ONE ANCHORING RULE restated; the warning named `anchor.operand` (§7.1; name, text, reach LEAN); the
  owner's condition met by §11 THE AMPERSAND RULE TESTED BY POSITION (below).
- R-1 (CF:1068-1081): a call may name its hit label (`occurrences(x, label = "foo")`, his placeholder spelling;
  `label` is reserved metadata since rev 9, so the setting's name is a spelling-step item); no count warning
  (O63 CLOSED, L66 BY DESIGN); `999${/\d+/ & <100}999` an acceptance row.

Review r14 (draft dispositions as proposed):
- F2: the general form, "a scoped match is opened by the PROGRAM and by every FILTER ROLE wherever it stands; a
  hole never opens one; an anchor reads the innermost" (§11 bullet, §0.3 "scoped match"); ONE SPAN PER FILTER ROLE
  and the HOLES sentence narrowed to "outside any filter role written inside the hole"; STRING SETS names four SET
  POSITIONS and three FILTER ROLES (a hole's set is not one).
- F1: folded by the ruling (both operands filter roles); L39's reason; new L70 (`P` vs `P & /(?s).*/`), L71 (the
  same inside a hole), both DIFFERENT: WARNING.
- CENSUS-1: rev 11's paragraph in §0.1 marked superseded, its L63 clause struck.
- CENSUS-3: the library family is "gap-bodied" in lower case; GAP is only the verdict class.
- CENSUS-4: `$` without `(?m)` is "the span's end or just before a final newline" (§11 MULTILINE, §13 C35).
- CENSUS-6: §2.7's "or what it reads" marked LEAN (from `length`, CF:722); §2.7 retitled "Filter modifiers: the
  pullback kind of transform".
- CENSUS-7: O61 now carries the whole name audit in the draft; `capture` classed a structural tool (lean name
  `labelled` if the owner reads the rule as covering it).
- DOC: CENSUS-2 ("span" in the draft's voice), CENSUS-8 ("searched" for the mode at the three places), `\Z` in the
  list of ends.
- New in §13: O64 (`anchored` inside a hole), O65 (the warning's reach); OWNER QUESTIONS AFTER REV 13; DECIDED BY
  THIS LANE (22)-(29).

`anchored` wording check (CF:1050-1053: usable only if no case differs from `\A(?:P)\z`). Read as "P whole on the
INNERMOST scoped match", it agrees in every case tested (final pattern, `$` in P, an alternation at P's top,
`(?m)` inside P, inside a filter, a `label:` condition, a hole). Read as "P in filter role on the span it takes", it
DIFFERS in a hole (`/x${anchored(/a/)}/` on `xa`: `\A`/`\z` no match, that reading 0-2). The wording carries both
readings, so the definition is the `\A`/`\z` text and the hole case is owner question 1 below.

## THE AMPERSAND RULE TESTED BY POSITION

The rule: both sides of `&` must match the SAME stretch of text from end to end, and a `^`/`$` written in a side
means that stretch's start/end. Verdict: SENSIBLE IN EVERY POSITION an `&` can stand. The one thing that has no
sensible meaning confined to the stretch is `\b` or a lookaround at its edge, which already is a compile error
(unchanged). Answers: `docs/dev/lanes/predspec13_anchor.out` (libpcre2 10.46 and Python `re` agree on every row).
`<256` / `<100` are "a number below 256 / 100".

| position | the stretch both sides must match (what an anchor in a side means) | example, text: answer | sensible? | warning fires? |
|---|---|---|---|---|
| (i) the whole program, searched in the text | each stretch the search tries; the one reported is the first both sides accept | `/^\d+$/ & <256` in `x300 12`: finds `30` (the same as `/\d+/ & <256`); `/^\d+$/` alone finds nothing | yes: "a number below 256 somewhere"; the anchors add nothing | yes |
| (ii) the whole program inside `anchored(...)` | the whole text, exact ends | `anchored(/^\d+$/ & <256)`: `200` matches; `x300 12` and `200` + newline do not | yes: the anchors coincide with the text's ends | yes (they add nothing) |
| (iii) inside a hole `${...}` | the text the hole takes | YOUR ROW: `999${/\d+/ & <100}999` matches `99945999` (the stretch is `45`); `99912345999`: no match. `port=${/^\d+$/ & <256}` matches `port=80`; on `port=300` it matches `port=30` (nothing after the hole stops the number; add `\b` after the hole to forbid that) | yes: the hole's text is the only stretch both sides can share; reading `^` as the start of the whole text would make the hole impossible | yes |
| (iv) an `&` inside a hole that is itself inside a side of another `&` | the innermost: the inner hole's text | `/\w+/ & /a${/^\d$/ & <5}b/` matches `a3b` | yes: each `&` has its own stretch; an anchor reads the nearest | yes |
| (v) a `label:` condition (`P & (x: /^S\w*/)`) | the text of label x in this match | matches `a Sab`; not `a xSab` | yes (unchanged since rev 11) | not by your words (the anchor is in a condition, not directly in a side of `&`): question 2 |
| (vi) a side that is itself an `&` chain | the same stretch for every side (grouping changes nothing) | `(/^\d+/ & /\d+$/) & <256` in `x300 12`: `30`, the same as the other grouping | yes | yes |
| (vii) a side with `\b` or a lookaround at its edge | the stretch, but `\b`/lookaround would look at the character before or after it | `/\w+/ & /\bfoo/`: compile ERROR (unchanged); read loosely it would find `foo` inside `xfoo`, where the plain pattern finds nothing | NO for `\b`/lookarounds, which is why they are an error; anchors are fine (they look at no outside character) | no (the error instead) |
| (viii) `&` written inside regex text (switch ON) | each side is the whole run of its alternative, so the stretch is what that alternative takes; anchors OUTSIDE a group around the `&` read the whole text | `/^\d+&${<256}$/` in `x300 12`: `30` (both anchors sit inside the sides); `/^(?:\d+&${<256})$/`: no match there, `200` matches | yes by the same rule, and the MOST surprising one: whoever writes `^...$` around a whole pattern means the whole text; the warning names the grouped fix | yes |

The look-alike the rule creates (review r14 F1): `/^foo/` finds nothing in `xfoo`, but `/^foo/ & /(?s).*/` (`&`
with "anything") finds `foo`; in a hole, `/x${/^a/}/` never matches `xa` while `/x${/^a/ & /(?s).*/}/` does. The
warning fires on the second form of each (draft rows L70, L71).

The warning (`anchor.operand`, text in §11): "`^` in this side of `&` is the start of the text both sides must
match whole (here: ...), not of the subject, so it always holds and adds nothing; to pin the subject's start, write
the final pattern as `anchored(...)` (in regex text: `/^(?:...&...)$/`)". It does not fire on `contains(/^err/)`
(there `^` follows the library's gap: the documented "starts with") nor on `anchored(...)`.

## QUESTIONS FOR THE OWNER

Rev 12's two carried questions were answered tonight (rulings R-1): two `occurrences`/`contains` calls exposing the
same hit label is an error fixed by naming one call's label; no warning for a count in a searched program. Rev 13
raises two:

1. `anchored(...)` inside a hole. With the exact ends you ruled, `anchored(P)` is `\A(?:P)\z`, and a hole has no
   ends of its own, so inside a hole `anchored` means the ends of the WHOLE text: `x${anchored(/a/)}` can never
   match (`xa`: no match). The other reading ("P matched whole on the hole's own text") would match `xa`, but that
   is already spelled `x${/a/ & /(?s).*/}`, or just `x${/a/}`. Lean: keep the definition, and make an `anchored`
   hole that provably cannot reach the text's ends a compile error ("anchored is for the whole pattern").
2. Does the anchor warning reach every place a pattern must match its whole stretch? Your ruling names a `^`/`$`
   in a side of `&`. The same anchor adds nothing, for the same reason, in a label condition (`P & (x: /^S\w*/)`),
   a modifier's argument (`padded(/^5/)`) and a warning-name set (`@warn.off(/^dead\./)`). If the warning stops at
   `&`, then `x & /^S\w*/` warns while `(x: /^S\w*/)` is silent although the `^` means the same thing in both.
   Lean: YES, one warning for every such place (one rule for one fact).

## CONSISTENCY SWEEP

Every §0.1 row and §12 case re-applied under rev 13's rulings, each in its real mode (on the span unless the row
says SEARCHED).

| rows | result | reason |
|---|---|---|
| L68 | ANSWER MOVES: DIFFERENT -> SAME | `anchored` is the `\A`/`\z` text; both find nothing in `foo\n` |
| L11, L41 | CLASS MOVES: BY DESIGN -> WARNING (answers unchanged) | the anchor is in an `&` operand (L11 inside the complement `!/^#.*/`): `anchor.operand` |
| L66 | CLASS MOVES: GAP -> BY DESIGN | the owner ruled no count warning (CF:1073-1081 on main) |
| L70, L71 | NEW, DIFFERENT: WARNING | the look-alikes the ruling creates (oracle rows) |
| L7, L13, L15 | unchanged (BY DESIGN); WARNING if question 2 is answered yes | the anchor sits in a condition, a modifier argument, a name set |
| L39 | unchanged (SAME); reason now the ruling | both operands filter roles keeps `&` symmetric |
| L69 | unchanged answers | the warning fires on its written-anchor forms, not on `anchored(r)` |
| L17 | unchanged (SAME), no warning | the `^` sits in `contains`'s hole after its gap |
| L63 | unchanged (DIFFERENT: BY DESIGN) | `$` stays PCRE's in a filter role |
| L16, L31, L50-L53, L55, L57, L58, L61, L62 | unchanged answers; respelled `occurrences` | the same transform |
| L67 | unchanged | its `&` stands where `\|` would alternate |
| every other row | unchanged | no anchor in an `&` operand, no `anchored`, no renamed name |

| §12 case | result |
|---|---|
| E-HTTP | code line `/\A${block}\z/` -> `anchored(block)` (the same text); answers unchanged |
| E-JSONL | unchanged (`contains` = `occurrences(x, min = 1)`; anchors in the final pattern) |
| E-CTX-1, E-CTX-5, E-CTX-7 | unchanged answers; would draw the warning only under question 2 |
| E-CTX-2, 3, 4, 6 | unchanged (compile errors) |
| E-WEEKDAY, E-IPV4, E-LUHN, E-CAL, E-RFC, E-NEAR, E-FILE, E-SEP, E-DEPTH, agreeing look-alike | unchanged: no anchor in an `&` operand, no rx-text `&`, no `search` by name |

Words swept: every `search` (code renamed by script over §0.1-§14, quotations of the owner and record, the
changelog and §15 kept; prose uses read one by one: transform -> `occurrences`, mode -> "searched", rev 7/8 "search
result" history kept), "GAP" (library sense lower-cased), "value" in the rev 12 voice lines (-> "span"), `[&]` (->
"`\&` or `[&]`" wherever it was the literal), `O60`, `O61`, `O62`, `O63`, `L66`, `L68`.

What a confirming critic round should look at: the warning's firing rule ("an anchor in an operand's own rx text,
not in a hole of a macro body") against every library body; O64's lean (an error for an unreachable `anchored`
hole); whether (viii) (rx-text `&` with `^...$` around a whole pattern) deserves more than a warning.
