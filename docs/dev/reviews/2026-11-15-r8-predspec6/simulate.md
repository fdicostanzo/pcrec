## Findings

### SIM-1 CONFIRMED (answer) — `contains(/^err/)` is NOT `$m ~ /^err/`: L17 and the `!~` sugar give the wrong meaning
Location: §0.1 L17 (line 103), §2.6 (line 347-348), §8 `contains(s) := /.*${s}.*/` (line 934), §11 (lines 1027, 1052-1054).
Repro: §8 defines `contains(s) := /.*${s}.*/`. Apply to `/^err/`: the argument lands in a HOLE, and §11 says a hole's set is a
FILTER whose `^`/`$` are "the START and END OF THE SPAN BEING FILTERED" (line 1027) — the hole's span, which sits after `.*`.
So `contains(/^err/)` = `/.*err.*/` (err anywhere). `$m ~ /^err/` (§2.6: `^` = the value's start) = m STARTS with err.
L17 says SAME, citing "`^` is the value's start in both". §2.6 defines `$x !~ rx` as `(x: !contains(rx))` "with ^/$ the
value's ends in both": on m = `xerr`, `$m ~ /^err/` is false (so `!~` should hold) but `contains(/^err/)` accepts `xerr`,
so the sugar REJECTS. Two G0 look-alikes disagree silently, on an ordinary subject.
Effort S. Blast: L16-L17, §2.6 `!~`, O12. Fix: state that `contains`'s argument is a set position whose ^/$ are the
VALUE's ends (a library-level rule, not the hole rule), or define `contains` as a primitive, or drop L17's SAME / `!~` sugar.

### SIM-2 CONFIRMED (doc) — L9 writes `(n = /\d+/)`: a one-entry `=` record in value position, an error under §5.4
Location: §0.1 L9 (line 95).
Repro: `(n = /\d+/) & (n: p)`. The left `&` operand is `( e )` WITH a label mark `=`, so §5.4's GROUPING row ("no comma,
no label mark", line 738) does not apply; it is a record in value position, which line 745 makes the error "a record is
not a value; for any one of the entries write `[ ... ]`" (L43). It is not a `label: S` condition either (O45 exception).
So under rev 6 the row's left form fails with the record error before reaching the edge-assertion error the row claims.
This is the rev 5 map-literal shape (one entry) that rev 6 withdrew; it was not respelled.
Effort S. Blast: L9 only. Fix: write `[n = /\d+/] & (n: p)`.

### SIM-3 CONFIRMED (doc) — L36 and C28 write `occurs.all(x: S)`, the withdrawn labelled-argument spelling
Location: §0.1 L36 (line 122), §13 C28 (line 1409).
Repro: in a CALL record `:` has no place: §5.4's `:` row admits `label: S` only as an entry of a CONDITION record or `p: T`
in a definition head, "Elsewhere an error" (line 740); a call's labelled entries use `=` (line 739), and `occurs.all` has
no parameter `x` anyway. §12.9 (line 1236-1237) and C31 say this spelling "is not used"; §4.3 writes the ruled form
`occurs.some((x: S))`. So L36's right-hand form is ill-formed; the row compares a legal form to an error.
Effort S. Blast: L36, C28. Fix: `occurs.all((x: S))`.

### SIM-4 CONFIRMED (doc) — `each_group(&, rx, (x: d2))` passes a bare operator as an argument
Location: §3.4 (line 465).
Repro: the only operator-as-macro form is the SECTION `(& B)` (§5.2 line 679-682; "Sections START with `&`", C33); §5.4
lists `(& f)` as the operator section. A bare `&` as a call entry is no value kind (§2.1: rx or macro), no section and no
name; nothing in §2.1-§5.4 admits it. The example is ill-formed as written (and `(x: d2)` then passes a condition macro
as a separate argument, so even reading `&` as "the `&` macro" gives a two-operand operator, which §5.2 never defines).
Effort S. Blast: §3.4 only. Fix: respell (e.g. `each_group((& (x: d2)), rx)`) or mark it pre-rev-4 placeholder.

### SIM-5 CONFIRMED (doc) — `;` as a statement separator in L2 and L42; undefined, and a withdrawn spelling
Location: §0.1 L2 (line 88), L42 (line 128).
Repro: `m := ...; m & T` and `n := count((name: S)); headers & (n: ==1)`. §5.1 (line 629-631) defines a program as
bindings/expressions/statements with newlines as layout; no `;` exists in §5.4's mark table, and §2.7 STATUS (line 394)
lists "the `->` / `;` stage ideas" as SUPERSEDED. A literal reader sees an undefined token, or the withdrawn stage operator.
Effort S. Blast: L2, L42. Fix: write the two statements on two lines (or define `;` as layout).

### SIM-6 CONFIRMED (design) — the stated reason for withdrawing `lex_ge([major, minor, patch], [1, 4, 0])` also rejects every `join([...])` in §12
Location: §8 TUPLE (line 954-956), §13 C25 (line 1396-1399); vs §3.4 (line 463-464), §12 re-check (line 1098-1099).
Repro: §8 says a `[ ]` "is an alternation (any one entry, so its order is not part of the value)". But §3.4 says
STRUCTURAL operations read the spelling (`/a|b/` vs `/b|a/` differ under `[1]`), and the rev 6 re-check admits
`[ ]` "passed to a structural macro that reads its entries in order (`join`)". `join([octet, octet, octet, octet],
sep = ".")`, `join([year = ..., month = ..., day = ...])`, `date_sep`, `textdate`, `pair` all rely on the order of a
`[ ]` argument. Applied literally, one rule cannot both forbid `lex_ge([1, 4, 0], ...)` (order lost) and accept
`join([...])` (order kept): `[1, 4, 0]` passed to a library macro reading entries in order is exactly the join case,
not a tuple VALUE. What actually makes the rev 5 form ill-formed is the bare label names `major, minor, patch` used as
values (§4.1: values are `$x`; C13), which the text does not name.
Effort S. Blast: §8, C25, O47 (the variadic need follows from the wrong premise), §12.2/12.3/12.6/12.7/12.10 by
implication. Fix: give the real reason (bare names / labels-as-values), and state that a `[ ]` argument to a
structural macro carries its order (§3.4), so `lex_ge([$major, $minor, $patch], [1, 4, 0])` is join-like and legal,
or say why not.

### SIM-7 CONFIRMED (answer) — E-RFC `month := $mname.index`: two parses with different values
Location: §12.6 (line 1181); rules §4.1 (line 491: `$x` = the value captured, a one-string set, context-free), §3.1
(line 409: `.index` = which top-level alternative/accept-state branch), O2 (line 1421: precedence of `.` vs `$` unstated).
Repro: parse A `$(mname.index)` = the value of the metadata path mname.index = 11 for `Nov` (the meaning claimed:
"1-based index = month number"). Parse B `($mname).index`: `$mname` = {"Nov"}, a context-free one-string rx; its array
view has ONE entry, so `.index` = 1 for every match (or undefined). Both parses are defined by the rules; nothing picks A.
Compare `$rest.year` (only parse A is defined, a one-string set has no labels) and `(wname.index: ==wd)` (no `$`), so the
draft writes "read the metadata of a label" two ways. E-RFC's answer (`Sat, 14 Nov 2026` -> match) needs A.
Effort S. Blast: §12.6, §4.4 (`month_numbered` family note), O19. Fix: state that `$` applies to a whole label path
(`$a.b.c` = `$(a.b.c)`), in §5.4 or O2.

### SIM-8 CONFIRMED (doc) — E-CAL `(day: padded(<=dim))` reads a computed label bare; C13 names only E-RFC
Location: §12.5 (line 1164); rule §4.1 (line 492: "`$x` is ALWAYS a value used (operand ...)"); C13 (line 1376-1378).
Repro: `dim := days_in($year, $month)` is a computed label (§4.4). `<=dim` uses it as an OPERAND; under §4.1 that must
be `<=$dim` (as `(b: >$a)` in §4.6). C13 leaves bare-vs-`$` OPEN and cites only `==wd` (E-RFC); E-CAL's spelling rests on
the same open item, yet line 1096-1100 says all twelve cases are well-formed and "two open items touch cases" (O46,
O45) without C13. Under the lean OWN-11 recorded in C13 (`==$wd`), E-CAL must change to `<=$dim`.
Effort S. Blast: §12.5, §12.6, the rev 6 re-check sentence. Fix: list C13 among the open items touching cases (E-CAL,
E-RFC), or respell both with `$`.

### SIM-9 CONFIRMED (doc) — `balanced := /\((?:[^()]|(?&balanced))*\)/` crosses from rx to expression without `${}`
Location: §7 first bullet (line 854-855); rules §11 (line 1012-1013: "rx -> expression only by `${...}`"; line 1017: "A
literal is its OWN SCOPE").
Repro: inside the literal, `(?&balanced)` is PCRE's subroutine call to a GROUP named `balanced`; the literal has no such
group (its own scope), and the binding name `balanced` is an expression-language name, reachable from rx text only by a
hole. Literally: a PCRE compile error ("reference to non-existent subpattern"), not the claimed recursion through the
binding. Writing `${balanced}` instead would be a self-referencing parameterless binding, which §7's same bullet admits
only "as in PCRE"; the rules give no spelling that means what the example says.
Effort S. Blast: §7, §14 non-goal 1. Fix: write the PCRE form with its own group (`/(?<balanced>\((?:[^()]|(?&balanced))*\))/`)
or state that a binding name is visible to `(?&name)` inside its own literal (a stated crossing).

### SIM-10 SUSPECTED (doc) — `($x + $y) & <50` has the shape §4.1 calls an error; no legal position is shown
Location: §2.5 (line 325); rule §4.1 (line 493: "`$x & ...` used AS A CONDITION is an ERROR"), §0.1 L28.
Repro: the example is offered as how subject numbers are "added and filtered". As an `&` operand of a pattern it is a
value test used as a condition: L28's error. Its only legal readings are a hole guard (`${($x + $y) & <50}`, empty set
kills the match) or a computed label (`s := $x + $y` then `P & (s: <50)`). Which one the text means is not stated.
Confirm by: the owner/manager naming the position. Effort S. Blast: §2.5. Fix: respell as `s := $x + $y` ... `(s: <50)`.

### SIM-11 SUSPECTED (doc) — `m(p: pure)` gives `:` in a definition head a second meaning
Location: §5.2 (line 695); §5.4 `:` row (line 740: `p: T` in a head constrains the parameter by a SET T).
Repro: `pure` is not a set of strings (§2.1 kinds: rx or macro); it is a purity marker ("match-dependent argument an
error"). So `p: T` narrows by a set while `p: pure` declares a binding-time property: one mark, two meanings in one
position, against the owner's "operators that always mean the same thing" (CF:846).
Confirm by: whether `pure` is meant as a set. Effort S. Blast: §5.2. Fix: give purity its own mark or a call form.

### SIM-12 CONFIRMED (doc) — §5.4's `( )` table row, read alone, rejects E-HTTP, L46 and `[(x: <200), ...]`
Location: §5.4 table (line 737) vs line 745-747 and §5.2 (line 670-672).
Repro: the row says a RECORD is "NEVER A VALUE: it cannot be bound, stored or returned", positions (a)-(c) only. Literally,
`occurs.exactly(1, (name: ...))` (E-HTTP; a record inside a call record = L45's error), `c := (year: 2000)` (L46, bound) and
`[(x: <200), (y: >55)]` (L23, stored in an array) are all errors by the row. They survive only by the O45 exception two
lines below the table. Since §5.4 is "the ONE place these marks are defined", the table should carry the exception;
and with it, position (b) "in a condition" is no position at all: a `label: S` record is legal anywhere a value is, so
what the bracket means depends on which entry marks it holds (`:` -> a value; `=`/positional -> never a value).
Effort S. Blast: §5.4, L23, L45, L46, E-HTTP. Fix: add an exception row ("( label: S, ... ) in value position = its
condition, a macro") to the table, and say (b) is "anywhere, when every entry is `label: S`".

## PROBED-AND-HELD
Rules checklist written from the text: simulate/checklist.md (R1-R17).

(a) §12 acceptance cases, token by token (12 cases, ~55 expressions):
- CLEAN (9): E-JSONL, E-WEEKDAY, E-IPV4, E-LUHN, E-NEAR, E-FILE, E-SEP, E-DEPTH (head `value_depth(0)` disclosed O21),
  E-CTX (all 7 lines + the agreeing look-alike). Every comma sits in a call record, a `[ ]` array or rx text; every
  `[ ]` is an alternation or a join argument; every `&` has an rx on the subject side; no record bound/returned; no
  unapplied macro where an rx is needed (`!startsWith("#")`, `!""` stand in the filter role of a chain).
- CONDITIONAL (3): E-CAL (bare `dim`, SIM-8), E-RFC (`$mname.index` parse, SIM-7; bare `wd`, C13), E-HTTP (needs the O45
  exception, SIM-12; otherwise clean).
(b) Other code: §0.1 table, 47 rows (~95 forms): 43 rows clean as claimed; ill-formed or wrong meaning: L9 (SIM-2),
  L17 (SIM-1), L36 (SIM-3); undefined token L2/L42 (SIM-5). Intended-error rows checked to error by the rule they cite:
  L4, L5, L28, L38, L40, L43, L45, L47 (8/8). §2-§11 and §13 code spans: ~70 checked, 64 clean; ill-formed/ambiguous:
  §3.4 each_group (SIM-4), §7 balanced (SIM-9), §2.5 (SIM-10), §5.2 `p: pure` (SIM-11), §2.6 `!~` (SIM-1), §8 tuple reason
  (SIM-6).
Priority probes (CF:874-878):
- `(x)` grouping vs one-entry record: HELD. §5.4 line 738 decides by position and marks; `f((x))` = `f(x)` (grouping in a
  call entry), `(x: S)` a condition, `(x) := r` design-only; no example has two parses. (L44 clean; the one stray
  one-entry `=` record is L9, SIM-2.)
- tuple example: the rewrite `version & lex_ge(1, 4, 0)` parses under R2/R12 (call record + subject by `&`); the
  semver respelling `semver & ((major: >=2) | (major: 1, minor: >=4))` parses (outer parens grouping, two condition
  macros under `|`). The REASON given for the withdrawal does not hold (SIM-6).
- `[x = /foo/, y = /bar/]`: HELD; reads as `(?<x>foo)|(?<y>bar)` by R7/§5.4 `=` row; §4.2's `[x = /\d/, y = /[a-z]/] &
  (x: /[0-5]/)` = `[0-5]` follows.
- withdrawn map literal `(x = /foo/ | y = /bar/)`: HELD as an error (entry `x = (/foo/ | y = /bar/)`, label inside a
  value; also a record in value position); nothing in the draft still uses it except L9's one-entry shape (SIM-2).
