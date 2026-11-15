# census findings

## Findings

### CENSUS-1 — `[ ]` means "any one entry" (alternation) AND "the ordered list of all entries" (join's sequence) [CONFIRMED]
- Severity: design. Effort: M. Blast radius: §3.1, §3.4, §5.3, §5.4 table row `[ ]`, §8 tuple text, §12.2/12.3/12.5/12.6/12.7/12.9/12.10 (every `join([...])`).
- Location: §5.4 L736 ("ARRAY: ANY ONE entry"); §3.1 L407-408; §5.3 L714; §8 L954-956; §12 re-check L1098-1099.
- Repro: `ipv4 := join([octet, octet, octet, octet], sep = ".")` (L1138). Under §5.4/CF:863, `[octet, octet, octet, octet]` = `octet|octet|octet|octet` = ANY ONE octet; join reads it as FOUR parts IN ORDER, ALL together (the record's "all entries together" meaning, CF:863). §8 L955-956 rejects `lex_ge([major, minor, patch], [1, 4, 0])` because "a `[ ]` is an alternation (any one entry, so its order is not part of the value)" — yet join's whole meaning rests on the order (and count) of exactly such a `[ ]`. The rev 6 re-check (L1098-1099) names the second meaning ("passed to a structural macro that reads its entries in order") instead of removing it. The owner's criterion ("operators that always mean the same thing", CF:846) moved the two-logics problem from the comma to the bracket: `[ ]` = OR under `& | !`, = ordered AND under `join`/`each`/`[i]`.
- Also internally contradictory: §8 L955 ("order is not part of the value") vs §3.4 L462-464 and §7 L886 (order IS part of the rx: PCRE priority, `[1]`) vs §5.5 (enumerate's order is the point).
- Fix direction: give the ordered-all-entries meaning to `( )` (a call record), e.g. join takes its parts as its own call record (needs O47's variadic record), or state `[ ]` = "ordered entries" and derive any-one only under extensional operators — and fix L955's reason.

### CENSUS-2 — `[a, b]` vs `a | b`: claimed equal, structurally different (an unlisted look-alike) [CONFIRMED]
- Severity: design (G0). Effort: S. Blast radius: §3.1 L408, §3.3, §3.5 L473, §0.1 (missing row beside L24), every `join([... x ...])` where an entry has alternatives (§12.6 `mname = month_abbrevs`).
- Location: §3.1 L408 ("`[1, 3, 5]` = `1|3|5`"); §3.3 L452-454 (`|` CONCATENATES arrays, each operand contributes its top-level alternatives); §3.5 L473 (`t & [f, g]` = `(t & f) | (t & g)`).
- Repro: E-RFC L1180 `join([day = /\d{1,2}/, mname = month_abbrevs, year = /\d{4}/], sep = " ")` only works if the 12-entry `month_abbrevs` is ONE entry of the `[ ]` (comma = entry boundary, like a hole/group). Then with `x := /a|b|c/`: `[x, /d/]` has 2 entries but `x | /d/` has 4 (§3.3). So the comma inside `[ ]` and the `|` operator — both glossed "any one" — differ under `[i]`, `.index`, `join`, `each`; the draft states the identity `[1, 3, 5]` = `1|3|5` without the qualifier, and §0.1 has no row (L24 covers holes only).
- Fix direction: state "`[e1, e2]` = `(?:e1)|(?:e2)` (each entry ONE entry, like a group/hole)" in §5.4 and add a §0.1 row `[x, /d/]` vs `x | /d/` (DIFFERENT, `array.hole`-family diagnostic).

### CENSUS-3 — `( e )` in value position has FOUR meanings, chosen by its content [CONFIRMED]
- Severity: design. Effort: M. Blast radius: §5.4 table rows `( , )`/`( e )` and L745-747, §2.1, §4.1 L509-511, §5.2 L671-672, §0.1 L43-L46, O41, O45.
- Location: §5.4 L737-738, L745-747; §5.2 L680; §0.1 L44, L46.
- Repro (all in value position, one pair of parentheses): `(x)` = GROUPING (L738, L44 SAME as `x`); `(& isodate)` = SECTION, a macro (L680, L747 "Other marks"); `(year: 2000)` = CONDITION, a macro value (L746 "except a record of `label: S` entries", L46 `c := (year: 2000)`); `(x = /a/, y = /b/)` / `(1, 2)` = ERROR "a record is not a value" (L43, L45). The table row says `( )` is "ONLY laid against something with fields ... NEVER A VALUE" (L737), and then L745-747 makes its most frequent use (a condition passed, bound or put in an array: `occurs.exactly(1, (name: S))`, `c := (year: 2000)`, `[(x: <200), (y: >55)]`) an exception that IS a value. "A record is never a value" (CF:866 (4)) and "a condition is a macro, a value" (CF:858 (1)) meet in the same spelling; the reader decides which by scanning for `:`, `=`, `&` or a comma.
- Fix direction: either say plainly that a record of `:` entries IS the written form of a macro value (drop "never a value" for that case and the exception clause), or give conditions a spelling that is not a record.

### CENSUS-4 — `:` means "narrow silently" in a condition and "check containment, error otherwise" in a definition head [CONFIRMED]
- Severity: design (G0). Effort: S. Blast radius: §5.2 L688-694, §5.4 `:` row L740, §4.1, O44.
- Location: §5.2 L688-692; §5.4 L740.
- Repro: `m(x: T)` — "the POSITIONAL argument must lie WITHIN T; a broader or partly overlapping argument is an error showing a dropped witness" (L689-690); `isodate & (year: <2000)` — "never gets that check: it always NARROWS ... silently drops `5`" (L691-692). Same mark, same `label: S` shape, opposite treatment of a value outside S (error vs silent drop). §5.4 glosses both as "CONSTRAINS a label that EXISTS", hiding the split. Also the "exists" half fails in a head: `m(x: T)` constrains a parameter the same `( )` is DECLARING, not one that exists.
- Fix direction: one meaning for `:` (narrow, with the dead-branch / empty-intersection diagnostics at narrowing sites, which §5.2 already lists typed parameters among), or a different mark for the containment check.

### CENSUS-5 — §5.4's axis for `=` vs `:` ("gives a label" vs "constrains a label that EXISTS") is violated by both marks [CONFIRMED]
- Severity: doc/design. Effort: S. Blast radius: §5.4 rows `=`/`:`, §4.1 L520-521, CF:863 restatement.
- Location: §5.4 L739-740; §4.1 L520-521.
- Repro: in a call, `sep = "."` / `between(low = 1, high = 12)` — `=` addresses a parameter that already EXISTS (declared in the head); in `[year = /\d{4}/]` `=` CREATES a new group label. In a head `m(x: T)` `:` addresses a parameter being DECLARED (new). So `=` is "create a label" (array) and "select an existing label" (call), and the existing-vs-new axis does not separate `=` from `:`. The axis that does separate them in every census occurrence (71 `=`-bearing spans, 216 `:`-bearing): `=` FILLS/DEFINES an entry's content (`sep = "."`, `year = /\d{4}/`, `index =`), `:` NARROWS it (`year: 2000`, `x: T`). CF:706's own words were "`=` sets a parameter vs `:` filters".
- Fix direction: restate §5.4 as `=` = this entry IS e (fill/define), `:` = this entry is narrowed to S; drop "exists".

### CENSUS-6 — §0.1 L9 still writes a labelled `( )` in value position: `(n = /\d+/)` [CONFIRMED]
- Severity: doc (an ill-formed example in the acceptance table). Effort: S. Blast radius: §0.1 L9.
- Location: §0.1 L95.
- Repro: `(n = /\d+/) & (n: p)`. By §5.4 L738 `( e )` is grouping only with "no label mark"; a labelled one-entry `( )` in value position is a record used as a value, the L43 error ("a record is not a value; for any one of the entries write `[ ... ]`"). The row's subject (the EDGE-ASSERTION error) is therefore masked by an earlier error. Same family as the withdrawn map literal (§3.1 L414-415).
- Fix direction: `[n = /\d+/] & (n: p)`.

### CENSUS-7 — §3.4 passes a bare operator as a call entry: `each_group(&, rx, (x: d2))` [CONFIRMED]
- Severity: doc/design. Effort: S. Blast radius: §3.4 L465.
- Location: §3.4 L465.
- Repro: the first entry `&` is neither an rx, a macro value, nor a section: §5.2 L679-684 says a section is `(& B)` with B given, sections are "the one way to leave a hole", and there is no partial application in phase 1 (C33, C34). A bare `&` is an operator with BOTH operands open — a fourth meaning of `&` (operator-as-value) the census found nowhere else (281 `&`-bearing spans: intersection, subject-fill, pointwise macro AND, section head, rx-text guard; this one only).
- Fix direction: respell with a section or a named macro (`each_group((& (x: d2)), rx)`-shaped), or drop the example.

### CENSUS-8 — `occurs.all(x: S)` (L36, C28) uses `:` directly in a call record, which §5.4 makes an error [CONFIRMED]
- Severity: doc. Effort: S. Blast radius: §0.1 L36, §13 C28.
- Location: L122, L1409.
- Repro: §5.4 L740: `:` only "as an entry of a condition record ... or in a definition head ... Elsewhere an error"; L1237 says the labelled-argument spelling `occurs.exactly(1, name: ...)` is not used (C31). L36 and C28 still write `occurs.all(x: S)`.
- Fix direction: `occurs.all((x: S))`.

### CENSUS-9 — the section `(& B)` is a LIFT (rx -> macro) when B is an rx and an IDENTITY when B is already a subject-open macro [CONFIRMED]
- Severity: design. Effort: S. Blast radius: §2.1 L211-213, §2.3 L289-291, §3.5 L475-476, §5.2 L679-681, §5.3 L711-713, §0.1 L6.
- Location: §2.1 L211-213 (a CONDITION and `(& B)` are BOTH "a macro with only the subject open"); §0.1 L92 / §2.3 L291 (`each((& (a: d)), x)`).
- Repro: `(& isodate)` turns an rx into a subject-open macro (needed: mixed arrays L475-476 "write the rx entry as a section, `(& /x/)`"). `(& (a: d))` wraps a CONDITION, which by §2.1 is already exactly that kind (subject open, no parameters), so `(& (a: d))` and `(a: d)` denote the same macro — yet L6/§2.3 make the wrapper mandatory under `each`, and §5.3 L711 says `each`'s f is "a MACRO whose parameters the entry fills, OR a FILTER passed as an operator SECTION" (a condition has no parameters, so `each((a: d), x)` falls between the two). Two meanings for one mark; no §0.1 row for `(& (a: d))` vs `(a: d)`.
- Fix direction: say `(& M)` = M for a subject-open macro M (so `each((a: d), x)` is legal and SAME), keeping the section as the rx->macro lift; add the row.

### CENSUS-10 — `${M}` with a subject-open macro M: a GUARD (§5.1) or the unapplied-macro ERROR (§2.2, L21)? [CONFIRMED]
- Severity: answer (a program is legal under one section and an error under another). Effort: S. Blast radius: §5.1 L634-635, §2.2 L253-254, §0.1 L21, §11 L1052-1057, O26.
- Location: §5.1 L634-635: "a macro with only its subject open (a condition, a section) is a guard (§11)" in a hole; §2.2 L253-254: "A standalone `!B` where an rx is needed (`${!B}`, ...) is the unapplied-macro error" (and `!B` IS a macro with only its subject open, L252-253); L21: `${!<200}` the unapplied-macro error; §11 L1055-1057: a guard needs an explicit `&` before the hole (C4) and the example guard `${ <256 }` holds a full rx, not a macro.
- Repro: `/(?<n>\d+)${!<200}/` — guard (by §5.1) or error (by §2.2/L21)? `${(n: <5)}` likewise. `${ }` carries two meanings for one operand kind.
- Fix direction: delete the guard clause from §5.1 (C4's guard is `&` + an rx hole), leaving macro-in-hole = the unapplied-macro error everywhere.

### CENSUS-11 — `~` returns an rx (occurrence set) but `!~` returns a condition; `$x` is a value under `~` and the constrained label under `!~` [CONFIRMED]
- Severity: design (G0). Effort: S. Blast radius: §2.6 L336-348, §4.1 L491-493, §0.1 L16, L17, L28, O12.
- Location: §2.6 L336 ("A SEARCH RETURNS AN RX", CF:873) vs L347-348 ("`$x !~ rx` is a TEST, sugar for the condition `(x: !contains(rx))`"); §4.1 L491-493 ("`$x` is ALWAYS a value used ... `$x & ...` used AS A CONDITION is an ERROR"); L16/L17 mark `$m ~ /^err/` SAME as `m: startsWith("err")` / `m: contains(/^err/)`.
- Repro: `!~` is not the complement of `~` (an rx vs a macro: different kinds); L16/L17 compare an rx (the occurrence set) with a condition entry and call them SAME, which the two-kind rule (CF:858) makes a category error; and `$x !~ rx` is a condition whose constrained side is spelled `$x`, the exact shape L28 refuses for `&` ("did you mean `x: ...`?"). The census found `$` in 111 spans: value read (most), rx end anchor, hole opener, reserved `$&`/`$_`, and this one constrained-side use.
- Fix direction: drop `!~` (O12's second reading) and respell L16/L17 as `(m: contains(...))` vs `(m: startsWith(...))`, keeping `~` = search returning an rx only.

### CENSUS-12 — `^` in `contains(/^err/)`: the HOLE's start (by §8's definition + §11) or the value's start (L17)? [CONFIRMED]
- Severity: answer. Effort: S. Blast radius: §0.1 L17, §8 L934 (`contains`), §11 L1023-1028, L1052-1054.
- Location: §8 L934 `contains(s) := /.*${s}.*/`; §11 L1023-1025 (a hole's set is a set position, a FILTER applied to a SPAN) and L1027-1028 (in a filter `^`/`$` = the filtered span's ends); §0.1 L17 (`m: contains(/^err/)` SAME as `$m ~ /^err/`, "`^` is the value's start in both").
- Repro: expanding the library definition, `contains(/^err/)` = `/.*${/^err/}.*/`; the hole's span is the inserted substring, so `^` = its own start: the filter accepts any m CONTAINING `err` (e.g. `xerr`). L17 says it accepts only m STARTING with `err`. `^` carries "span start" by §11 and "value start" by L17 for the same token. Same issue for `endsWith`/`startsWith` if passed rx with anchors.
- Fix direction: either L17 is DIFFERENT (`contains(/^err/)` = `contains("err")`), or `contains` is not definable as a hole macro and becomes a built-in with stated anchoring.

### CENSUS-13 — `X[i]` indexes four different things: alternatives, PCRE group 0, joined (sequence) parts, occurrences [CONFIRMED for the first three]
- Severity: design. Effort: M. Blast radius: §3.2 tool 1 (L431-435), §5.3 L715, §2.6 L346, §4.3 L555-556.
- Location: §3.2 L431-434; §5.3 L714-715; §3.1 L403-404.
- Repro: (a) `X[1]` = the first TOP-LEVEL ALTERNATIVE (array view, §3.1: "`/abc/` is an array of one"). (b) `X[0]` = "the whole rx (PCRE group 0)" (L434): a GROUP number, the map-view numbering, where a PCRE reader then expects `X[1]` = group 1 — not alternative 1. (c) `join(...)` yields ONE alternative (a concatenation), so by (a) `c[1]` = c itself; §5.3 L715 says `c[1]` is the first JOINED PART (a sequence position). (d) `s[i]` on a search = the i-th occurrence (consistent with (a) only because §2.6 defines the occurrence set's array view that way). Census: 29 distinct index-bracket spans; one each carries (b) `[0]` (L434, written bare), (c) `c[1]` (L715), (d) `s[i]` (L346); `alt.x[1]`/`alt.repeated[1]` (same-name groups in group order) are a fifth reading; the rest are (a) or the C5 multi-index.
- Fix direction: drop `[0]` (whole rx is X itself) and either drop `c[1]` from §5.3 or define join's result so its array view is its parts (which collides with (a)); this is CENSUS-1's split surfacing in the index tool.

### CENSUS-14 — `(` and `[` are postfix (call / index) AND statement openers, while newlines are layout [CONFIRMED by construction]
- Severity: design (a parse ambiguity). Effort: S. Blast radius: §5.1 L629-633, §2.5 L328-329, §2.6 L341, O41, every program ending in an array or condition expression.
- Location: §5.1 L630 ("whitespace and newlines are free between expression tokens"); §2.5 L328-329 ("with no juxtaposition, a name after an expression always starts a binding (one-token look-ahead)"); `(x, y) := ...` (L341, L633), final expressions like `[a, b]`.
- Repro: `d := $m ~ /x/` NEWLINE `(x, y) := $m ~ /y/` lexes as `d := $m ~ /x/(x, y) := ...` (a call on an rx literal, the "patterns take no arguments" error); `t := foo` NEWLINE `[a, b]` (a final array) lexes as `foo[a, b]` (an index). The one-token look-ahead argument covers a NAME after an expression only; `(` and `[` after an expression are always postfix. The ruled design keeps `(x, y) :=` (CF:866 (c)), so the collision is in the design even if out of phase 1.
- Fix direction: state that a statement never starts with `(`/`[` (destructuring gets a leading mark), or make newline significant before `(`/`[`.

### CENSUS-15 — KEY WORD "section" names two kinds: `(& B)` (a macro) and `<256`/`==5` (a full rx) — and contradicts "sections start with `&` only" [CONFIRMED]
- Severity: doc/design. Effort: S. Blast radius: §2.4 title + L297-309, §5.2 L679-682, §5.4 L747, §0.2 L155, §0.1 L20, L22, O38, C33.
- Location: §2.4 L297 ("Comparisons are UNARY SECTIONS"), L302 ("an integer section"), L309; §5.4 L747 ("`==` is the equality section"); vs §5.2 L681-682 ("Sections START with `&` only; sections of other operators come on need (C33)") and §2.1 L211-213 (a section = a macro with the subject open) vs L217 (`<200` "is a full rx").
- Repro: `<200` is called a section of `<` and is in phase 1, while §0.2 L155 says phase 1 has sections of `&` only; and the two "sections" are different value kinds (rx vs macro). 
- Fix direction: call the comparisons "comparison sets" (they are rx), keep "section" for `(& B)`.

### CENSUS-16 — KEY WORD "subject" names the run-time TEXT and the compile-time OPERAND rx filling a macro's slot [CONFIRMED]
- Severity: doc (reader confusion on the very point the owner ruled). Effort: S. Blast radius: §2.1 L209-214, §2.3, §2.7 L363-366, §5.2 L668, §5.6, §12 header.
- Location: §2.1 L209-210 ("`&` fills its one SUBJECT slot with the rx on the other side"); §2.3 L285 ("THE SUBJECT IS NEVER AN ARGUMENT"); §2.7 L365-366 ("THE TRANSFORM TRANSFORMS THE FILTER, NOT THE SUBJECT: the subject is never modified; the modified filter reads it differently") ; §12 L1090 ("expected behaviour on a few subjects"); §5.2 L694 ("the assertion's own subject").
- Repro: in `month & padded(between(1, 12))`, "the subject" is `month` (an rx, §2.1) in one sentence and the string `"05"` being matched (§2.7, §12) in the next; L1291's `subject foobar` is text. Of 86 occurrences, both senses recur in §2.x. CF:860's "subject slot" is the operand sense; the owner's transform quote (§2.7 REASONING) is the text sense.
- Fix direction: "operand"/"target" (the term §2.3 L283 already uses: "has no target") for the slot; "subject" for the text only.

### CENSUS-17 — KEY WORD "transform" names the filter->filter macro AND the subject->image map t [CONFIRMED]
- Severity: doc (re-opens the owner's naming point). Effort: S. Blast radius: §2.7, §11 L1046, L1081.
- Location: §2.7 L363 ("A TRANSFORM is a macro FILTER -> FILTER"), L365 ("THE TRANSFORM TRANSFORMS THE FILTER, NOT THE SUBJECT"); L367-368 ("the pullback of S under a finite transducer ... t"); §11 L1046 and L1081 ("transform images (what a modified filter reads)").
- Repro: "transform image" = t(subject), i.e. the transform acting on the SUBJECT — precisely the reading the owner rejected ("Trim or unpad imply they are doing something to the subject. But they are not", §2.7 REASONING). 
- Fix direction: "transform" = the modifier only; call t the modifier's "reading" and its output "what the modified filter reads".

### CENSUS-18 — KEY WORDS "filter" and "condition": "filter" is ruled a ROLE but still used as a TYPE and for `where`; "condition" names the entry, the record and any filter [CONFIRMED]
- Severity: doc/design. Effort: S. Blast radius: §2.1, §2.2, §2.3, §3.2, §4.1, §8, §10, O26.
- Location: ROLE: §2.1 L216 (CF:858). TYPE uses: L1455 ("prefix `!` is always a filter"), L607 ("a FILTER is never called with them ... `leap($year)`" — `leap` is an rx), L934 ("Standard filters: `between` ... `startsWith`" as a category), L919 ("a label-free value filter is a full rx"). A DIFFERENT OPERATION: §3.2 L438 `where(p, X)` = "filter by a compile-time STRUCTURAL property" (keeps entries by spelling; not the `&` role at all). "condition": the ENTRY `x: S` (L490: "`x: S` ... (a condition, a macro ...)", though L507 says `x: S` outside a record is an error, so the entry alone is no macro); the RECORD `(x: S, y: T)` (§4.1 L496); ANY filter (§10 L997 "`x & eval($fmt)` is a CONDITION"; §8 L935 `when(c, p)`'s c; L283 calls `x: digit` a "filter").
- Repro: two words name one thing (a subject-open macro = "filter" = "condition") and each word also names something else (filter: a structural selection; condition: a non-value entry).
- Fix direction: "condition" = the `( label: S, ... )` record's macro only; "filter role" only for `&`'s side; `where` "selects".

### CENSUS-19 — KEY WORD "binding" names `:=` AND the C22 parse attachment ("the condition binding", "binds tighter") [CONFIRMED]
- Severity: doc. Effort: S. Blast radius: §4.1 L499, L512, L518-519, L527, O43, changelog L12/L27.
- Location: "binding" = `name := e` (§5.1, 70 uses mostly this); "the C22 binding"/"the condition binding"/"The binding reads the same at top level and after a label" (L499, L512, L518, L1537) = how far `label:` reaches (precedence).
- Repro: §4.1 discusses "a binding" (`c := (year: 2000)`, L510) and "the binding" (precedence, L512) two lines apart; "match-dependent binding" (§4.4) is a third, the `:=` sense with a label read.
- Fix direction: call the C22 rule "entry extent" (the term §5.4 L743 already uses).

### CENSUS-20 — KEY WORDS "value", "kind", "type": "value" = any rx/macro AND a captured substring (vs a "pattern"); "kind" is both the two value kinds and value-vs-pattern; "type" = kind AND an rx used as a constraint [CONFIRMED]
- Severity: design/doc. Effort: S. Blast radius: §2.1, §4.1, §4.3, §4.5, §4.6, §5.1 L633-635, §11 L1052, L1071, C29.
- Location: "value" as kind-level: §2.1 L203 ("Every value is one of TWO KINDS"). "value" as a match string OPPOSED to "pattern": §11 L1052 ("a value inserts LITERAL TEXT ... a pattern inserts a sub-pattern"), L1071 ("The KIND of a hole decides its insertion"), C29 L1412 ("a VALUE ... or the map-view PATTERN"), §4.6 "value macros" L606. "type": L554 ("static TYPE of a duplicate label" = an rx), §5.2 L688 (`m(x: T)`: T an rx), L594 ("Library types" = library patterns), L309 ("declared types"), §9 L986 ("value types"); vs the owner's "few types" (CF:846) = the kinds.
- Repro: under two kinds a captured `$x` and a pattern are the SAME kind (rx, a one-string set vs a set), so L1071's "KIND of a hole" names a distinction the kind system no longer has; the census found no rule that tells the compiler whether a hole operand is a "value" or a "pattern" other than its set (both insert the same set, §5.1 L634).
- Fix direction: "kind" only for rx/macro; "value" only for the kind-level term (use "captured string" for `$x`); "type" retired in favour of "constraint set" (or "kind").

### CENSUS-21 — KEY WORD "macro" covers a value kind, non-value `@` "effect macros", and the operators themselves [CONFIRMED]
- Severity: design. Effort: S. Blast radius: §2.1 L203, L223, §5.1 L644-646, §5.2 L679, C18, C19.
- Location: §2.1 L203 (macro = one of the two VALUE kinds); L223 ("`@` statements ... are statements, not values") vs §5.1 L644-646 ("compile-time EFFECT macros", "effect macros cannot drop" `@`); §5.2 L679 ("Operators are macros").
- Repro: (a) an effect macro is a macro that is not a value, against "every value is rx or macro / a macro is a value"; C18's dead end (a named assertion can be no binding because an assertion is neither kind, L1389) follows from this. (b) If `&` is a macro, its operands arrive by a call or by `&` (the one input rule, CF:860) — the rule becomes circular for `&` itself, and `each_group(&, ...)` (CENSUS-7) is what "operators are macros" licenses.
- Fix direction: call `@` forms "effects" (not macros); drop "operators are macros" and say a SECTION is a macro.

### CENSUS-22 — KEY WORD "label" names a group name, a parameter name, a module binding and a metadata member; "field" umbrellas three of them [CONFIRMED]
- Severity: doc/design. Effort: S. Blast radius: §5.4 `=` row L739, §4.1 L521, §7 L872, §3.1, O31.
- Location: §5.4 L739 ("gives the entry its LABEL: a group name in an array ..., a parameter name in a call"); §7 L872 ("every module label whose NAME is in the rx"); §3.1 L409 (`.index` "the accept-state label"); §4.4 computed labels (bindings); §3.1 L413 "fields" = parameters, labels, groups.
- Repro: since parameter names are "labels" (L739) and `:` "constrains a label that exists" (L740), `between(low: 1, high: 12)` reads as legal by the table's own words, yet is an error ("Elsewhere an error"); a module label (an exported binding) can be a macro, while a pattern label is always an rx.
- Fix direction: "label" = pattern group names (incl. computed labels); "parameter" for macro fields; "member" for module names.

### CENSUS-23 — KEY WORDS "record" and "entry": `records(text, rx)` returns an ARRAY of file records whose entries are "maps"; "entry" = alternative, sequence part, record field, module export [CONFIRMED]
- Severity: doc. Effort: S. Blast radius: §7 L856-864, §8 L1442-1444 (O20), §5.4, §3.1, O44, O46.
- Location: §7 L856-857 ("`records(text, rx)` = each compile-time match ... is an entry; named groups make entries maps"); L858 "record rx"; O44 (2) already notes the name `records` (L1548). "entry": array entry = top-level alternative (§3.1), join entry = sequence part (§5.3), record entry = field (§5.4), module "every entry is an rx" (L870).
- Repro: "named groups make entries maps" (L857) calls an rx a map (the withdrawn value form) in the same section that says a record (the written map) is never a value (L871); O44's rename covers the function name but not "record rx" (L858, L863, L1048) or "maps".
- Fix direction: extend O44's rename to "record rx" (-> "item pattern") and replace "make entries maps" with "entries keep their labels (map view)".

### CENSUS-24 — `.` carries four meanings: map-view navigation (an rx op), module member (name resolution, if O46's lean holds), metadata (`.index`/`.label`), and a path under `$` [CONFIRMED; partly known as O31 / RUL-F5]
- Severity: design. Effort: M. Blast radius: §3.2 tool 4, §2.6 L340, §4.4, §7 L868-872, §12.6, O31, O46, C13, C29.
- Location: §3.2 L440 (one tool for `A.Saturday`, `alt.repeated[1]` AND `json.row`); §7 L871-872 (lean: a module is a NAMESPACE, not a value) — so `json.row` stops being navigation on a value; §12.6 L1181 `$mname.index` (metadata read through `$`, on what §4.1 calls a one-string set, which has no branch) vs L1184 `wname.index` (the same metadata on a label path, no `$`).
- Repro: O46's lean turns the module case into a different operation while §3.2 lists it as the same tool; `$rest.year` (L1183, a path under `$`) and `$mname.index` (metadata under `$`) put two of the dot's meanings behind the same `$x.y` shape. O31 covers only metadata-vs-label.
- Fix direction: widen O31 to the whole dot family (map view / module / metadata / `$`-path) and decide it once.

### CENSUS-25 — SIBLING OF A FAMILY: the brackets are the THIRD spelling of any/all, and `=`/`:=`/`(?<x>)`/head parameters are four ways to introduce a name [CONFIRMED]
- Severity: design (unification candidate). Effort: M. Blast radius: §2.2, §3.1, §3.5, §4.1, §4.3, §5.1, §5.2, §5.4, §8 (`occurs`), §2.6 (`some`/`all`).
- ANY ONE: `a | b` (§2.2), `[a, b]` (§5.4), `some(s)` / `occurs.some(c)` (§2.6, §8), `X[1|3|5]` = `X[1, 3, 5]` (C5). ALL TOGETHER: `a & b` (§2.2), `(x: a, y: b)` (§4.1; L3 says SAME as `(x: a) & (y: b)`), `x: S` on a repeated label = all iterations (§4.3), `occurs.all` / `all(s)` (C28). CF:863 made the bracket a third member of the `|`/`&` family and the `some`/`all` family (RUL-F2) without folding either; L3's SAME verdict and §3.5's `t & [f, g]` = `(t & f) | (t & g)` are the fold identities.
- NAMING a thing: `name := e` (§5.1), `[x = e]` (§3.1, = `(?<x>e)` inside rx), PCRE `(?<x>...)`, a head parameter `m(x)` / destructuring `(x, y) :=` (§2.6), computed labels via `:=` (§4.4). `[x = /foo/]` and `/(?<x>foo)/` are two spellings of one group label (§3.1 L407-408).
- Fix direction: list each family in one §13 FAMILIES line (beside RUL-F2) and decide whether the bracket is DEFINED as a fold of `|`/`&` (then say so in §5.4) or is a separate mechanism.

### CENSUS-26 — GENERAL FORM + UNLOCKS: an ENTRY LIST whose bracket is a fold and whose entry marks are fill (`=`) vs narrow (`:`) [SUSPECTED as a design direction; each unlock names its trigger]
- Severity: design. Effort: L. Blast radius: §5.4 (the whole table), §5.2, §5.3, §8 tuples, O21, O41-O47, C25.
- The general form that appears when CENSUS-1/3/4/5/9 are removed: (1) one ENTRY LIST `e1, e2, ...`; the BRACKET names the combiner: `[ ]` = keep the entries, any one (alternation, entries atomic as in CENSUS-2), `( )` = keep the entries, all together, IN ORDER (a record). (2) Each entry is positional, `name = e` (this field IS e: fill/define) or `name: S` (this field is narrowed to S). (3) A record is laid against fields (parameters, labels, groups); a condition is the record-of-`:` laid against the operand's labels, i.e. the macro (no exception clause needed, CENSUS-3). (4) An rx in macro position IS its section, `(& rx)` (CENSUS-9).
- UNLOCKS: (a) `join`'s ordered parts move to `( )` — `join(year = /\d{4}/, month = ..., sep = "-")`-shaped — so `[ ]` keeps one meaning (CENSUS-1, CENSUS-13's `c[1]`); TRIGGER: the same variadic call record O47 needs for `lex_ge`, i.e. one mechanism settles C25, O47 and CENSUS-1 together (cost: a rest-parameter rule to keep group labels apart from settings like `sep`). (b) Piecewise definitions (O21's `value_depth(0)` / `value_depth(k)`) become head entries narrowed by `:` (`value_depth(k: 0)`), no new form; TRIGGER: O21 being decided, or a second recursive library. (c) `m(x: T)` and `(x: T)` share one narrowing meaning, the containment check becoming the existing dead-branch/empty-intersection diagnostic (CENSUS-4); TRIGGER: any build of typed parameters. (d) Mixed rx/macro arrays and `each(isodate, dates)` without a wrapper (§3.5's mixed-array error disappears); TRIGGER: a worked example with a mixed table, or C33's "other sections on need".
- Fix direction: carry this as one §13 item (a unification candidate), not a rewrite in rev 7.

## PROBED-AND-HELD

Census tool: `census/tool/census.py` + `comma.py` (python3 -I) over the draft at aa9348f3d: 1,639 code spans (1,554 inline, 85 code-block lines). Spans containing each mark (expression text, `/.../` and `"..."` masked): `&` 281, `( )` 483, `.` 255, `:` 216, `,` 200, `$` 111, `[ ]` 109, `:=` 107, `!` 76, `=` 71, `@` 70, `|` 57, `(& f)` 17, `==` 14, `~` 14, `/.../` 174.
- `,` HELD: every comma in an expression sits inside a bracket — call records 123, `[ ]` arrays 69, index brackets 14 (all the C5 multi-index), definition heads 5, `( )` records 23 (conditions, the withdrawn/erroneous forms the draft cites as errors, destructuring, the `(1, 40)` boundary examples). The 41 bracket-less commas are prose fragments, subject text (`Sat, 14 Nov 2026`, CSV rows, JSON subjects), the multi-line E-WEEKDAY block, or unwrapped rx text (`\d{1,3}`, L731/L1545). No comma carries AND/OR/dimension: CF:863 is met for the comma itself.
- All twelve §12 cases' commas classify as call record / condition record / array / rx text, as the rev 6 re-check says (L1097-1099); what that check does not catch is the `[ ]` second meaning (CENSUS-1, CENSUS-2).
- `==` (14 spans): one meaning (the equality comparison set). `@` (70): one meaning (effect statement prefix). `/.../` (174): only the rx delimiter — the expression language has no `/` operator (arithmetic is `+ - * %`), so no clash; the `^`/`$` split inside is CENSUS-12. `|` (57): union with the documented structural concatenation (§3.3, L24), set union inside an entry, index sets — one operation, held (its contrast with `[ , ]` is CENSUS-2). `!` (76): prefix complement macro / PCRE literal inside rx (documented, §2.2) — held except the `!~` token (CENSUS-11). `:=` (107): bind / macro head / destructure / piecewise heads — the last is O21, already open; not re-filed.
- `&` (281): intersection, subject fill, pointwise macro AND and rx-text guard reduce to one lifted intersection (L1-L3 hold under it); the one outlier is `each_group(&, ...)` (CENSUS-7).
- Known and not re-filed: metadata dot (O31), `==wd` vs `$a` (C13), `occurs.all` vs sequence rule (C28), multi-index (C5), name `records` (O44 (2)), module kind (O46).
- Key words probed with no second meaning found: "view" (34 uses: array/map view, plus "manager's view" = opinion in prose only), "set" (as string set/rx; the verb "sets a parameter" is CF:706's quoted wording).
