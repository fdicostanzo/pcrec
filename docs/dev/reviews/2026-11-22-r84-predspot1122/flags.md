# flags findings — r84 predspot1122
(critic: APPEND below; never overwrite)

## Findings

### FLAGS-1 — CONFIRMED — design — reading (e) "same defaults" is false once `@options` is not the first item of a file
File/tag: core.md [core/holes/flags] bullet "This holds for a direct literal and for a binding alike, at any depth. A
binding of the SAME file inserted in a hole of that file has the same defaults, so nothing visible changes there (the
manager's reading (e))."; core_details.md core/holes/flags readings "(e) ... — SUPPORTED as run".
Against: library.md [lib/builtin/options] "`@options(..)` applies to the literals written after it in the same file,
from the statement on" and its own "Not ruled: the spelling, and whether it may appear more than once; whether `i` may
be set weakly insensitive only at the top of a file". Nothing requires the statement to be first, and "from the
statement on" makes position matter, so two bindings of ONE file can have different defaults.
Repro (the model's own engine, copy R/flags/model_probe.py, probe P1): program file `a := /./`, then `@options(s)`, then
the program `/x${a}y/`: WHOLE `x\ny` FAILS, while the host's own `/x.y/` HOLDS (`x.y` under the file's `s`). The
same-file binding does NOT have the host's defaults; something visible changes. The model's LEXICAL check builds exactly
this file shape (`a := /a./`, then `@options(s, m)`) but never inserts `a` into a later literal, and LIBFILE tests (e)
only with the statement at the top (`SAMEF`), so "SUPPORTED as run" covers the top-only case.
Fix: scope (e) to "a file whose options are all stated before its first binding", or rule top-of-file-only (then the
"from the statement on" wording and the LEXICAL check change). Effort: small (one bullet + one reading line).
Blast radius: core/holes/flags, core/holes/flags/in-filter (reuses "own file's defaults"), any later example that
splices a same-file binding. Modes: all three (a WHOLE / SEARCHED / FIND-ALL answer moves; P1 is WHOLE).

### FLAGS-2 — CONFIRMED — design — a bound `&` in a hole is NOT "the `&` written in the hole" once program options differ by file
File/tag: core.md [core/holes/flags/in-filter] bullet "A binding of an `&` put in a hole behaves the same: for flags and
matching a binding is its expression where it is used (...), so `C := /[a-z]+/ & /b.*/` at `/(?i)id-${C}/` is the `&`
written in the hole (a reading)."; and the place table core.md [core/model/places], row "a binding `name := X` | for
flags and matching, X where `name` is used". Both are sentences of the EARLIER (position-decides) rule.
Against: core/holes/flags statement "What is inserted in a hole starts from its own file's defaults" and its bullet "the
program options in force where it is written".
Repro (model engine, probe P11): program file opening `@options(i)`, library `C := /[a-z]+/ & /b.*/`: `/id-${C}/` WHOLE
`id-BLAH` FAILS; the same `&` written in the hole, `/id-${/[a-z]+/ & /b.*/}/`, HOLDS. The model's own FILTER check
prints this split (`P_w` False vs `P_side` True, "the same sides written in place ... take its weak `i`") and passes,
while the bullet it is cited for says the two are the same. With an explicit `(?i)` (the bullet's own example) they
agree, so the example line hides it.
Fix: re-word both to "for flags a binding is its expression where it is WRITTEN, with an explicit `i` from the hole"
(the place-table row is not in the diff: an earlier-rule sentence the fold missed). Effort: small. Blast radius: the
place table (every place row's flags reading), in-filter, the any_case body reading.

### FLAGS-3 — CONFIRMED — doc — sentences still written under the EARLIER inheritance rule (i, m, s inherited; flags by position)
Every one found, whole files (grep for inherit / hole's flags / flags in force / where it is used / m`, `s`):
1. core.md [core/model/places] the binding row "for flags and matching, X where `name` is used" (FLAGS-2).
2. core.md [core/holes/flags/in-filter] "for flags and matching a binding is its expression where it is used" (FLAGS-2).
3. core_details.md core/holes/flags readings: "\"only i\" inherited: his OBSERVATION, a possible narrowing, not ruled —
   UNTESTED." (it is now ruled in the narrower form: explicit `i` only).
4. same: "the not-inherited flags are the inserted rx's own defaults at any depth; `m`, `s` stay inherited until he
   rules the narrowing (the manager's) — UNTESTED here." (he ruled: not inherited).
5. same: "the `r` and `a`-family flags inherited (the draft's reading, P29-2) — UNTESTED here" — contradicts the base
   statement "only an explicit `i` or `-i` in force at the hole is inherited" (twice-decided: see FLAGS-6).
6. core_details.md core/holes/flags/in-filter readings: "flags-warning (d): the trigger is stated for `i`; `m` and `s`
   follow the same comparison — UNTESTED; marked a reading in the base. His lean that only `i` is inherited (...)
   would narrow it; not ruled." — the base sentence was removed by this fold (its history line says so); the reading
   line survives and says the base still carries it.
7. same: "the two sides of an `&` inside a hole start with the hole's flags (THE DRAFT'S READING REACH ...) — open in
   the draft" — "the hole's flags" is now one explicit `i`.
8. core_details.md core/patterns/flags `rulings:` keeps 2026-11-18 "a hole takes the flags in force at the hole" and
   "flags-propagate: yes" with no "revised by hole-flags" mark (core/holes/flags carries a `rejected:` line for the
   list; this entry does not).
9. core.md [core/principles/rx-owns-flags] quotes "so if one builds up an rx, they inherit the flags of the
   surrounding." — kept, then "Narrowed by hole-flags" — HELD (marked).
Held (not stale): core/patterns/flags bullets, core/holes/flags base, the warnings row (core.md:2019), library any_case.
Effort: small (delete / re-mark 6 reading lines, re-word 2 sentences). Blast radius: details only, except 1-2.

### FLAGS-4 — CONFIRMED — maintenance (evidence) — the flag engine ignores "from the statement on" for macro bodies and call arguments
File: predspot_model.py `lower_fexpr`: the parameter arm `return lower_fexpr(arg, at, files, afile, aparams, at_hole)`
passes no `upto`, so the argument's literal reads its file's options at the END of the file; the macro arm takes
`own = file_defaults(files, bfile, len(files[bfile]))` (FMACROS carry no position at all).
Subject sentence it breaks: library.md [lib/builtin/options] "`@options(..)` applies to the literals written after it in
the same file, from the statement on".
Repro (probe P3): program file `b := mac(/a.b/)`, then `@options(s)`; mac(r) := `/${r}/` (library): `b` WHOLE `a\nb`
HOLDS, while `b2 := /a.b/` in the same place FAILS. The argument literal is written BEFORE the statement and still gets
`s`. Probe P2: a library ending in `@options(s)` gives that `s` to any macro body of the file (no position modelled).
No printed line or check exercises it (every check puts options first), so 27/27 is unaffected; but the engine
encodes a rule with no sentence, and any later check with a mid-file statement and a call inherits it.
Fix: pass `upto` (the caller's j) to the parameter arm; give FMACROS entries a file position. Effort: small.

### FLAGS-5 — CONFIRMED — maintenance (evidence) — FLAGGRID: vacuous cells, mislabelled n/a cells, a constant UNDECIDED, a missing reader
File: predspot_model.py FLAGGRID (cell / expect / SG); predspot_model.out lines 457-587.
(a) PLANT (my one mutation of the arm, copy R/flags/model_probe.py): OPT["weak off"] = {} (the weak-off option
removed). All 6 weak-off cells still AGREE (6/6). The 4 "the file's option" cells write `@options(-i)`, which equals
the default, so they cannot fail; the 2 "importing" cells test only that the library's own `@options(i)` survives. The
weak-off column guards nothing about a weak-off option. (ORDER/SWAP: a switch that reverses nothing.)
(b) `@options(-i)` (and `-s` etc., `opts_of`) has no sentence: the subject says only "a file with no option is weakly
case-sensitive, `@options(i)` makes it weakly insensitive". An engine spelling with no sentence.
(c) n/a is not "no such program" for 22 cells: weak on/off x "up the hole" (8) are labelled "a weak value is never
written in a literal", but a host literal's weak value in force at a hole is the subject's own example line
(`/id-${word}/` under `@options(i)`); its answer sits in another cell, a duplicate, not n/a. "the importing file's
option" x "own text" (6, plus same-file binding 6) are labelled "no importing file": a library binding used as the
program itself, a side of a program-level `&`, or a library binding inserted in a same-LIBRARY binding are real
programs (probe P6: program `@options(s)`, library `d := /a.b/`, the program `d` and `d & /(?s:.*)/`: both FAIL on
`a\nb`, decided by "never across an import"), never run by the grid. Their cited sentence ("applies to the literals
written after it in the same file") does not state n/a.
(d) `FG["UNDECIDED"]` is never incremented anywhere: "UNDECIDED 0" is a constant, so the grid cannot report the
cells the subject leaves open (FLAGS-6); `xx`, `U`, `J` (the brief's "unchanged" flags) and `r`, `a` are absent.
(e) No reader "a provided body such as `any_case`" (EXPLICIT covers only its `(?i:`); probe P7 (program `@options(s)`,
`any_case(/a.b/)` on `A\nB`: HOLDS) agrees with "written" but is unchecked.
(f) The "deciding sentence" test is `ws(words) in ALLDOC2` (the words occur anywhere in three files): a control that
shares nothing with the cell; it cannot fail on a cell decided by the wrong sentence.
(g) The "moved from 2026-11-19's rule" column runs `@options` programs under the old inheritance: no such state ever
existed (2026-11-19 had no program options); 18 "moved" cells compare against a hybrid.
Effort: medium (re-label, add 3 readers and a real UNDECIDED arm). Blast radius: evidence only; no answer moves.

### FLAGS-6 — CONFIRMED (text) — design — DEFINITION-COMPLETENESS: no one statement decides a flag at a point; six cells undecided or twice-decided
There is no single sentence. The decision is spread over FOUR statements, each pointing at the next:
core.md [core/patterns/flags] "A literal's flags are the ones it writes (...), with PCRE's scope, over its file's
program options"; [core/holes/flags] "What is inserted in a hole starts from its own file's defaults; only an explicit
`i` or `-i` in force at the hole is inherited, replacing them; `m`, `s`, `x`, `xx`, `n`, `U` are not."; [core/holes/
flags/in-filter] (the `&` sides); library.md [lib/builtin/options] "applies to the literals written after it in the
same file, from the statement on". Composed, they decide the 78 run cells as the model says. What they leave open:
(1) TWICE-DECIDED `r` and the `a`-family: the base ("only an explicit `i`") says not inherited; core_details
core/holes/flags readings "the `r` and `a`-family flags inherited (the draft's reading, P29-2)". The option hole's legal
set (core.md [core/holes/option] "`i m s x xx n U J r a aD aS aW aP aT`") makes them writable. Also absent from the
options' "Not ruled" list ("options beyond the four (`xx`, `J`, `U`, the `&`-in-rx switch)").
(2) UNDECIDED: is an `i` made by an OPTION HOLE explicit? `/(?${o})${w}/`, o := "i", w a library binding. "EXPLICIT is
a flag written in the literal's text (`(?i)`, `(?-i)`, `(?i:..)`, `/.../i`)" lists text spellings only; the option
hole is a hole, not text. WHOLE `AB` (w := `/ab/`) HOLDS if explicit, FAILS if not.
(3) UNDECIDED: a STRING operand `"ab"` under `@options(i)` / `@options(x)`. The options apply to "the literals written
after it"; core/patterns/literals defines "An rx literal `/.../`". The engine decides (probe P5: `"ab"` on `AB` HOLDS
under weak `i`; `"a b"` under `x` keeps its space) with no sentence. The rejected "plain text" split (core_details
core/holes/flags `rejected:`) speaks of a hole, not of a file option.
(4) UNDECIDED: `pattern($x)` (library.md [lib/builtin/pattern] "the flags in force where the group is written come
along") inserted in a hole under an explicit `(?i)` that the group was not written under, e.g.
`/(?<x>[a-z]+)(?i),${pattern($x)}/` on `ab,AB`: "come along" (the group's) or "an explicit `i` ... in force at the
hole is inherited, replacing them"? Not stated which wins (a reading piece, out of the first build; low weight).
(5) UNDECIDED: several statements and turning a flag OFF (`@options(-s)` after `@options(s)`): "Not ruled ... whether
it may appear more than once", yet "from the statement on" and FLAGS-1's reading lean on position; the engine
accumulates (probe P12: `@options(i)`, a, `@options(-i)`, b: a on `A` HOLDS, b on `B` FAILS) with no sentence.
(6) DEPTH WORDING: "only an explicit `i` ... in force at the hole" + "EXPLICIT is a flag written in the literal's
text": at depth two the `i` in force at B's hole was written in A's text, not B's. The base's "down the hole, until a
nearer explicit setting" and "at any depth" decide it (inherit), so this is wording, not a gap; the model agrees
(probe P4a: `/(?i)${B}/`, B := `/x${C}/`, C := `/[a-z]/` both in a library: `XA` HOLDS; P4b, B := `/(?-i)x${C}/`:
`xA` FAILS, the nearer explicit wins). Suggest "explicit in force at the hole, written in this literal or inherited".
Fix: one statement in core/patterns/flags naming the four sources in order (own text > explicit `i` from the hole >
file options from the statement on > the file default), with (1)-(5) each ruled, marked a reading, or listed open.
Effort: small-medium. Blast radius: core/patterns/flags, core/holes/flags, core/holes/option, lib/builtin/options.

## PROBED-AND-HELD
- FLAGGRID, read cell by cell against the text (predspot_model.out 458-585): all 78 run cells answer as the four
  statements of FLAGS-6 compose (literal itself 24/24 apply; up the hole: explicit `i`/`-i` 6/6 apply, `m` `s` `n` `x`
  12/12 do not; the file's option 24/24 apply; importing file's option 12/12 do not). 0 DISAGREE reproduced in my run
  (verdict line "predspot_model: 27 checks, 0 failed", PREDSPOT_LIGHT=1, copy with probes).
- n/a cells that ARE true "no such program": explicit `i` x either option place (16): "a program option is never
  explicit"; weak x "the literal itself" (8): "a weak value is set only by a program option"; "up the hole" x own text (8).
- Sub-part 2 drills, three insertion points: OUTER CHAIN = the grid's one-deep cells (above); TWO DEEP: P4a (`XA`
  HOLDS, explicit `i` through two library holes), P4b (`xA` FAILS, a nearer `(?-i)` wins), P4c (library `@options(s)`
  kept two deep under an outer `(?i)`: `A\n` HOLDS); SHARED BINDING: P4d/P4e (library `C` used by the program directly
  and through library `B` under program `@options(i)`: `/${C}/` on `C` FAILS, `/${B}/` on `XC` FAILS, `/(?i)${B}/` on
  `XC` HOLDS, `/${C}${B}/` on `cXC` FAILS): each answers by "never across an import" and the explicit-only rule.
- "never across an import" at the top (not in a hole): P6, `d` and `d & /(?s:.*)/` FAIL on `a\nb` (held; FLAGS-5c).
- PCRE scope at the hole: P9 `/(?i:x)${w}/` on `XA` FAILS (the group's `i` ends before the hole); P10 a library `&`
  side under `(?i)` HOLDS on `AB`.
- EXAMPLES: the record's pasted line (b) reproduced; the four new core/holes/flags lines and two lib/builtin/options
  lines printed by the engine (FSWEEP 9/9, DOC 22/22).
- The `@options` statement parse in printed lines (`files_of_line`): only "a program/library file opening
  `@options(..)`", i.e. at the top; every printed line uses one statement at the top, consistent with the "Not ruled"
  list. Mid-file placement is used only by LEXICAL (FLAGS-1).
- Lint: pred_doc_lint 7034 passed, 0 failed (form only).
- Minimum witness length reached: texts of length 2-7 (`AB`, `a\nb`, `cXC`, `id-BLAH`); no "no case found" claim is made.
- Model runs used: 1 (the probe copy, which also carried my one FLAGGRID plant).

CRITIC COMPLETE flags
