# Lane lastpass — last-pass-default: a looped label read after its loop, every pass (T) or the regex default (R) (2026-11-17)

DESIGN EVIDENCE ONLY. Nothing here rules and `docs/design/predicates_draft.md` is not edited. Both defaults are run
side by side; no recommendation is made. Every number is printed by `lastpass_evidence/lastpass_model.py` (output
`lastpass_evidence/lastpass_model.out`); `[id]` names its catalogue line, PART n its section.

## STATE AT HANDOFF

- OWED: none
- Rulings file `lastpass_rulings.md`: EMPTY at every check (before each commit and before this report); no R-n applied.
- Premise test: PASS. (1) Lane rxmodel's harness re-ran byte-identical to its committed `rxmodel.out` (about 1 minute,
  `diff` empty). (2) libpcre2-8 10.46: `(?:(\d);)*` then a callout reads group 1 = `3` on `7;3;` and unset on the empty
  text; also `7` on `7;;` with the optional loop `(?:(\d)?;)*` (PART A, five rows, all OK).
- Validation: 122 draft lines (plus 3 witness lines) run in WHOLE, SEARCHED and FIND-ALL. Control: T3 (the draft's
  own text: Kleene logic, hits committed) reproduces every printed answer of the catalogue, 0 mismatches. R equals
  libpcre2 on all 29 programs with a callout model, 0 differences over their text sets in all three modes (PART D).
  Sabotage (`LASTPASS_SABOTAGE=1`, R reads the FIRST pass): 28 of the 29 differ from libpcre2, 155 output lines move.
  Switch (`LASTPASS_DEFAULT=T`): MOVED 0; 26 of 29 then differ from libpcre2 (T is not what PCRE computes).
- Standing questions: measurement regime NOT RELEVANT (no timing). Independent control RELEVANT: R is checked against
  libpcre2 (an independent engine), T against the draft's printed answers; the sabotage switch shows the libpcre2
  check can fail. Data regeneration NOT RELEVANT (no table or pin).

## THE TWO DEFAULTS

(T) TODAY'S READING (rev 23.2, R.1.2, R.1.5, §4.3's sequence rule; run two-valued per absent-under-not).
1. A label set inside a loop is a list of values, one per pass; each pass has only the values it set itself.
2. A plain condition on it holds when it holds on EVERY pass, and there must be a pass: no pass reads as one pass
   with the label missing, which fails unless the test writes a default.
3. A joint or record over looped labels pairs the values of the SAME pass (the pairing rule); a label outside the
   loop is tested with each pass.
ENGINE: the path's history is cut into passes at each loop-pass marker of the pairing loop (the deepest loop enclosing
the label); the test runs on every pass row (a null row when there is none) and the answers are ANDed; a missing value
fails (two-valued). Under branch-scope (ii) a failing condition sends the pattern back to fewer passes.

(R) THE REGEX DEFAULT.
1. A label set inside a loop is read as PCRE reads it after the match: ONE value, the one the last pass that SET it
   gave; a later pass that did not set it leaves that value in place.
2. A plain condition tests that one value, exactly as for a label set once; no pass that set it = missing = fails.
3. Every-pass questions are asked by name (the named every-pass request); `some`, `count`, `occurs.*` are already such.
ENGINE: the test reads the path's capture state (the last setting of each group), as a set-once label. Validated:
the regex with ONE callout after it, run on libpcre2 10.46, equals the engine on all 29 such programs in all three
modes (PART D), including the carried value (`(?:(\d)?;)*` on `7;;` reads `7`, PART A).

## LINES THAT MOVE

HOW THE DRAFT WAS SEARCHED: (1) `scan_looped.py` lists every `/.../` literal with a named group under a repeat of
upper bound 2+ (19 patterns, line numbers in `scan_looped.out`); (2) grep for `KH`, `list :=`, `occurrences(`,
`contains(`, `hit`, `some(`, `count(`, `occurs.`, `7;;`, `3;;`; (3) a read of §R.1-§R.8, §0.1's rows L16-L104, §2.6,
§2.7 `length`, §4.3, §8 (4) and the `when` paragraph, §12.9, §13's REV 23 blocks. Excluded as history: §16, the
Changelog, and §13 entries marked CLOSED/RETIRED (e.g. the `h?` line under zero-pass-empty).

THE COUNT: 122 draft lines (one program on one text). 104 read a looped label with a bare condition; 18 are controls
(group questions, the hit list, a condition inside an argument, set-once labels). MOVED: 16 of the 104 (WHOLE 8,
SEARCHED 8, FIND-ALL 13); 88 of the 104 do NOT move on the text the draft printed; the 18 controls move 0. Most
printed texts were chosen where the readings coincide; over the text sets the same programs differ widely (below).

Lines that move (T then R; WHOLE / SEARCHED; FIND-ALL on the family's several-match subject):

| id | site | program on text | T | R |
|---|---|---|---|---|
| R3.3;;.0 | §R.3 table | `REP & (h: <5)` on `3;;` (REP := `/(?:(?<h>\d)?;)*/`) | FAILS / `3;`@0 | HOLDS / `3;;`@0 (h carries `3`) |
| R3.3;;.1 | §R.3 table | `REP & NOT (h: <5)` on `3;;` | HOLDS / `3;;`@0 | FAILS / ``@0 |
| R3.3;;.3 | §R.3 table | `REP & !(REP & (h: <5))` on `3;;` | HOLDS / `3;;`@0 | FAILS / ``@0 |
| R3.3;7;.2 | §R.3 table | `REP & (h: !<5)` on `3;7;` | FAILS / `7;`@2 | HOLDS / `3;7;`@0 |
| R3.7;;.2 | §R.3, R.8 item 2 | `REP & (h: !<5)` on `7;;` | FAILS / `7;`@0 | HOLDS / `7;;`@0 |
| R3.{empty,3;,3;;}.2 | §R.3 table | `REP & (h: !<5)` | same W / S | FIND-ALL on `3;7; 7;; 3;`: T [`7;`@2, `7;`@5], R [`3;7;`@0, `7;;`@5] |
| R2.b | §R.2 empty S | `REP & (h: !<0)` on `3;;` | FAILS / `3;`@0 | HOLDS / `3;;`@0 |
| O13.1,7,.2 | §13 REV 23 block | `NLO & (n: !<5)` on `1,7,` (NLO := `/(?:(?<n>\d)?,)*/`) | FAILS / `7,`@2 | HOLDS / `1,7,`@0 |
| O13.7,,.2 | §13 REV 23 block | `NLO & (n: !<5)` on `7,,` | FAILS / `7,`@0 | HOLDS / `7,,`@0 |
| O13.empty.2 | §13 REV 23 block | the same on `` | FAILS / FAILS | FAILS / FAILS; FIND-ALL [`7,`@2, `7,`@5] vs [`1,7,`@0, `7,,`@5] |
| NS.a-d | §0.1 L56, L65 | `/(?<n>\d)*x/` and `/x\|(?<n>\d)+/` with `(n: <5)` / `(n = 0: <5)` on `x` | unchanged on `x` | FIND-ALL on `x 73x`: T `3x`@3 / `3`@3, R `73x`@2 / `73`@2 |

ZERO PASSES AND EMPTY PASSES: on `` both readings answer alike on every catalogued line (no pass sets the label: T's
null pass row and R's unset capture both fail; a default stands in for both). The empty-pass texts (`3;;`, `7;;`,
`7,,`) are where R parts from T without any value differing: R carries the earlier pass's value over the empty pass.

Counts over the text sets (PART C; WHOLE holds T vs R, texts that differ WHOLE / SEARCHED report / FIND-ALL, first):

| program | set | holds T / R | differ | first |
|---|---|---|---|---|
| `REP & (h: <5)` | {3,7,;} to 5 (364) | 2 / 18 | 16 / 54 / 54 | `3;;` |
| `REP & NOT (h: <5)` (and the difference `REP & !(REP & c)`, identical) | 364 | 40 / 24 | 16 / 36 / 57 | `3;;` |
| `REP & (h: !<5)` | 364 | 2 / 18 | 16 / 54 / 54 | `7;;` |
| `REP & (h: !<0)` | 364 | 6 / 36 | 30 / 94 / 94 | `3;;` |
| `REP & (h = 0: <5)` | 364 | 20 / 24 | 4 / 6 / 8 | `7;3;` |
| `/(?:(?<h>\d);)*/ & (h: <5)` | 364 | 2 / 3 | 1 / 7 / 7 | `7;3;` |
| `KH & (h: <5, k: between(3, 7))` (§4.3 pairing) | KH texts (1,110) | 150 / 275 | 125 / 125 / 125 | `3;5;0` |
| `when` body and filter form, c = `(h: <5)` | 1,110 | 960 / 835 | 125 / 125 / 125 | `0;5;0` |
| `PAIR & ((h, m): padded(>= (9, 30)))` | lists of 4 times (85) | 14 / 42 | 28 / 36 / 36 | `9:15,10:00,` |
| `TML & ((h, m): R)` (§8 (4) TM2-L) | lists of 5 items (156) | 14 / 94 | 80 / 95 / 95 | `9,9:45,` |
| `TWOF & (a: <5, b: between(3, 7))` | 156 | 3 / 74 | 71 / 80 / 80 | `3-6,-6,` |
| `/x\|(?<n>\d)+/ & (n: <5)` | {3,7,x} to 4 (121) | 4 / 15 | 11 / 32 / 33 | `73` |
| every group question line (`some`, `count`, `occurs.*`) | their sets | equal | 0 / 0 / 0 | none |
| every `occurrences` hit line (H2, regex-settles) | 85, 127, 156 | equal | 0 / 0 / 0 | none |

The closing example (§4.3, 1,111 lists, WHOLE differences from intents I1 / I2a / I2b; holds): `((h, m): R)` T 1 / 37 /
12 (3), R 135 / 139 / 130 (137); `((h = 0, m = 0): R)` ("every pass, possibly none") T 11 / 25 / 0 (15, EXACT on
I2b), R 141 / 131 / 130 (145); every `occurs.none(...)` spelling is identical under T and R. R pairs STALE values:
`CLOSE & ((h, m): R)` on `3:15,3,` HOLDS under R (h = `3` from item 2, m = `15` carried from item 1), FAILS under T.

Moved by OTHER rulings, not by this question (T3 vs T, shown in PART B, not counted above): two-valued NOT
(absent-under-not) turns `NOT (h: <5)` on `` to HOLDS and makes `NOT (h: <0)` constant TRUE; the joint NOT
`occurs.none(NOT ((h, m): R))` becomes I1-exact (0 / 36 / 11) instead of I2a; and every `occurrences` line moves under
regex-settles (4) (below, hit-list).

## WHAT EACH OPEN LOOP QUESTION BECOMES

- **pass-table**: DISSOLVES for the bare label (a bare looped label is one value, the capture; no nested table is
  read); MOVES INTO THE NAMED REQUEST'S DEFINITION (its passes are the pass table, each with its own values).
  Witness `REP & (h: !<5)` on `7;;`: T FAILS / `7;`@0, R HOLDS / `7;;`@0.
- **pass-and**: DISSOLVES under either default, by absent-under-not: two-valued, "Kleene AND" and "a missing pass
  makes it UNKNOWN" both reduce to "every pass TRUE". Under R the bare label has one value, so there is no AND at all.
- **group-truth**: UNCHANGED by this question (and settled two-valued by absent-under-not): `some`/`count`/`occurs.*`
  are already named per-pass forms; 0 lines and 0 texts move (`NOT some((h: <5))` on `;` HOLDS / `;`@0 both; L102
  0 / 0 both).
- **loop-condition (pathimpact E2)**: DISSOLVES for the bare label: one judge, the callout after the loop, equal to
  libpcre2 (PART D). `/(?:(?<h>\d);)*/ & (h: <5)` on `7;3;`: T FAILS / `3;`@2, R HOLDS / `7;3;`@0. MOVES INTO THE
  NAMED REQUEST: where the every-pass test is judged. For "every pass, possibly none" it does not matter (after the
  loop vs a piece in each pass, `(?:[0-4];)*`: 0 / 0 of 364, PART E); for "at least one pass" it does (pathimpact E2,
  L1 vs L2: 1 / 324 / 364, only on zero passes and empty passes).
- **repeated-means**: UNCHANGED as a definition; its reach shrinks: under R "repeated" no longer changes what a bare
  condition means (`/(?:(?<h>\d);)+/ & /\d;/` vs `/(?<h>\d);/` under `(h: <5)`: 0 differ over 364, both defaults); it
  decides only what the named request may take and the bare `$x` level (§4.3).
- **the retired `all`** (all-question, 23:18): he was shown, on `/(?:(?<h>\d);)*/`, "the plain condition fails on the
  empty list; `(h = 0: <5)` holds; `all` read as every pass passes, none needed, holds". Under R all three answers on
  the empty list are unchanged ([W.E], [W.E0]); what changes is that `(h = d: S)` no longer spells "every pass,
  possibly none" (on `7;3;` `(h = 0: <5)` T FAILS, R HOLDS). `all`'s meaning MOVES INTO THE NAMED REQUEST (it is the
  named every-pass test itself; today's group questions already spell it two-valued as `occurs.none(NOT c)`).
- **hit-list**: UNCHANGED for a condition inside the argument (`occurrences(/(?<n>\d+)/ & (n: <100), min = 2)`: 0 of
  121 differ). A FINDING ACROSS BOTH DEFAULTS: under regex-settles (4) (one pattern, re-entered) the lazy gaps can
  swallow any hit, so the bare `(g: "x")` on hits means "some hit is `abx`" under T AND R (PART F, 0 of 85 against
  `/[\s\S]*abx[\s\S]*/`), and `occurs.none((g: "y"))` holds on every text (0 of 85 against `/[\s\S]*/`); every hit line
  answers alike under T and R (0 texts). Every-hit questions exist only over COMMITTED hits (H1, the global search):
  there T and R part on 3 of the 21 hit lines ([HIT.0] `(g: "x")` on `abxabyabx`: T FAILS / `abxab`@0, R HOLDS;
  [HIT.4]; [HIT.own] `(g: "a")` on `abb`: T FAILS, R HOLDS, g carried from hit 1). So the hit list MOVES INTO THE NAMED
  REQUEST'S DEFINITION: the named all-hits request must commit the hits.

## WHAT THE NAMED REQUEST MUST COVER

What the draft can say today about every pass that R's bare label cannot, so the minimum the named every-pass request
offers (REGULAR = an automaton with no stored values; how, in one sentence):

| what | draft section | regular? |
|---|---|---|
| every pass, at least one (today's plain condition) | §4.3 sequence rule, R.1.5 | yes: the loop body restricted per pass, `+`: `(?:[0-4];)+` (PART F, 0 of 364); spelled today as `some(c) & occurs.none(NOT c)` (0 / 0 of 364, PART E) |
| every pass, possibly none (today `(h = d: S)`) | R.1.7, L36 | yes: `(?:[0-4];)*` = `occurs.none(NOT c)` (0 of 364) |
| zero passes fine, a pass lacking the label not (sentinel) | R.1.7, §2.6 | already a group question; unchanged |
| a joint or record per pass of the pairing loop; a label outside the loop with each pass | §4.3 pairing rule, §8 (4), joint-loops | yes: a product per pass (finite sets of each part) |
| not every pass; every pass in !S; the pattern difference over every pass | §R.3, L30 | yes: complements and restrictions of the per-pass product |
| some / count / occurs.exactly, at_least, at_most, none; same pass by record | R.1.7, §4.3, L31 | yes: a flag or a capped counter (n+2 states); `occurs.exactly(2, ...)` as a regex 0 of 364 |
| one pass by literal index, `(x[2]: S)` | §4.3 (LEAN) | yes: a countdown (~k states) |
| reading a pass's value: `$x[2]`, `$m.hit[2].g`, the list `$x`, selecting passes `$m.hit[(g: "x")]` | §2.6, §4.3 | NO: stored values, the captures level (11-15 ruling (1)) |
| a pass compared with another pass or a label outside (`$a`, sorted, distinct) | §4.6 | yes over finite value sets (priced by class count); stored values otherwise |
| order and commitment of hits: leftmost, non-overlapping, the global search's hits | R.1.9, §2.6 | for `ab[xy]` yes (PART F H1 forms, 0 of 85); for any rx UNPROVEN (rxmodel, WHERE NO REGEX MODEL EXISTS 2) |

So the minimum: the per-pass tests (every, with and without "at least one"; per-pass joint/record), the counts that
exist today, a literal-index test, and for hits a COMMITTED list; reading values out stays at the captures level.

THE REVERSE: what R's bare label says that T cannot, without rewriting the pattern: "the last value h took is in S"
(`REP & (h: <5)` under R = `/(?:\d?;)*[0-4];;*/`, regular, PART F); one meaning with PCRE's own `\k<h>` and a callout
(§4.3 already gives `\k<x>` in rx text the last iteration); and, for a joint, "the last hour and the last minute seen"
(stale pairing: `3:15,3,`), which is NOT "the last item". T says "the last item" only by rewriting the regex with
the last item in its own group. The draft's §4.3 REASONING ("the last-iteration rule would need captures inside a
loop") holds for READING the value, not for TESTING it: R's tests are regular (PART F).

Rulings an answer of R touches (quoted for him, not re-decided): 2026-11-14 Q4 "repeated labels by the sequence rule
at default (`x:` = all iterations ...) SUPERSEDES `$x` = last iteration"; 2026-11-15 search record (2) "a plain
condition = ALL hits"; absent-rule (2) "over several values it holds when every value is in the set and there is at
least one"; joint-loops (per pass, for bare conditions); the L88 looped warning's premise.

## THE QUESTION FOR THE OWNER

**last-pass-default.** A label set inside a loop, read by a condition written after the loop.

TODAY: the condition must hold on EVERY pass of the loop, and the loop must have run (a default stands in for a
missing value). REGEX: the condition reads what regex keeps after a loop, the value from the LAST pass that set the
label (nothing if none did); "every pass" is asked for by name, like `some` and `count` today.

Example, `/(?:(?<h>\d);)*/ & (h: <5)`:

| | today (every pass) | regex (last pass) |
|---|---|---|
| whole value `7;3;` | FAILS (7 is not under 5) | HOLDS (h = 3) |
| searched in `7;3;` | reports `3;` at 2 | reports `7;3;` at 0 |
| every match in `7;3; 3;7;` | `3;` at 2, `3;` at 5 | `7;3;` at 0, `3;` at 5 |
| empty text | FAILS (no pass) | FAILS (no value) |

With a pass that sets nothing (`/(?:(?<h>\d)?;)*/` on `3;;`): today FAILS (pass 2 has no h); regex HOLDS (h stays 3).

WHAT EACH ANSWER DOES. Regex: 16 of the 104 draft lines that read a looped label move (§R.3's table, §R.2, §13's
REV 23 block, L56/L65 find-all), and many more texts over the sets (e.g. the pairing example 125 of 1,110, the TM2-L
table 80 of 156); pass-table, pass-and and loop-condition dissolve for the bare label; `all`'s meaning comes back as
the named every-pass form; group questions and the hit list do not move; the joint over a loop pairs the last values
seen (stale minutes); the rulings listed above are reversed for bare conditions. Today's reading: nothing moves;
pass-table and loop-condition stay open; it stays the one place where a bare condition does not mean what regex means
(rxmodel's "tension" item). Separately, either way: under the one-pattern `occurrences` every every-hit question needs
the hits committed (above).

## COMMANDS

W = /home/pcrec/projects/pcrec/worktrees/lastpass; run from `/var/tmp/pcrec-pcrec/scratch/lastpass`. Python 3.14,
standard library, the installed libpcre2-8 10.46.

    timeout 900 python3 -I W/docs/dev/lanes/rxmodel_evidence/rxmodel.py > rx.out         # premise (1), ~1 min
    diff rx.out W/docs/dev/lanes/rxmodel_evidence/rxmodel.out                              # prints nothing
    timeout 900 python3 -I W/docs/dev/lanes/lastpass_evidence/lastpass_model.py > lp.out  # ~20 s
    diff lp.out W/docs/dev/lanes/lastpass_evidence/lastpass_model.out                      # prints nothing
    grep 'PART A\|A0' lp.out                                    # premise (2): five rows OK
    grep 'PART B DRAFT\|PART B BARE\|by mode\|CONTROL' lp.out   # 122; 104 bare, 16 move; W 8 S 8 F 13; 0 mismatches
    grep 'PART B (H1) SUMMARY\|PART D SUMMARY' lp.out           # 3 hit lines; 29 programs, 0 differ
    LASTPASS_DEFAULT=T timeout 900 python3 -I W/.../lastpass_model.py > sw.out           # THE SWITCH
    grep 'MOVED LINES\|PART B DRAFT' sw.out                     # MOVED 0
    LASTPASS_SABOTAGE=1 timeout 900 python3 -I W/.../lastpass_model.py > sab.out
    grep 'PART D SUMMARY' sab.out                               # 28 of 29 differ from libpcre2
    diff lp.out sab.out | grep -c '^<'                          # 155
    python3 -I W/docs/dev/lanes/lastpass_evidence/scan_looped.py W/docs/design/predicates_draft.md   # = scan_looped.out
