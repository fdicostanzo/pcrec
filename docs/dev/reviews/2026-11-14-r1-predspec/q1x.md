# Q1X findings: crit-predspec

Lens: Q1 examples-and-cost (Model A context-marked triples vs Model B string sets + D196 in-context composition).

## Findings

### Q1X-1 (CONFIRMED; design/doc; effort small; blast: §11 REASONING, §13 O25) The two §11 cases cited as needing Model A do not discriminate the models
§11 REASONING: "Context-marked sets keep G3 for lone-literal programs with lookbehind (`/(?<=\$)\d+/`) and
E-JSONL's `/^${q}$/m`". In both, the context assertion sits in the program's FINAL pattern, which is SEARCHED against
the real subject (§12 preamble: "searched with PCRE semantics"); search is in-context under Model A, Model B1
(value-scoped sets) and Model B2 (context kind + D196 in-context `&`) alike, because no pattern is being used AS A SET.
E-JSONL's `q` contains no assertion (row/jstr/isodate/between/contains are context-free), so `q` is a plain string
set and in-context = isolated for every `&` inside it; the `^`/`$` belong to the outer literal.
Repro: `q.py find '(?<=\$)\d+' 'a $12 b 34 $5'` -> [(3,5,'12'),(12,13,'5')] (the program's answer under all three
models; G3 holds). The only model-sensitive form near these cases is the BOUND name used as a set:
`p := /(?<=\$)\d+/` then `(n = /\d+/) & (n: p)`: `q.py and '\d+' '(?<=\$)\d+' 'a $12 b 34 $5'` -> (3,5) in-context,
None --isolated (B1: the lookbehind can never pass inside a value). So the real argument for A is "a name means the
same everywhere" (third case), not G3.
Recommendation: restate §11's reasoning as that one argument; drop the G3 and E-JSONL claims (they hold under B).

### Q1X-2 (CONFIRMED; design; effort small; blast: Q1 itself, §11, §13 C15/C27) "Model B" is two models; Model A coincides with one of them on every `&`, condition and hole
As COMMON states it, B is underdetermined: "a pattern used as a set means the strings it matches entirely, alone"
(B1, value-scoped: `^ $ \b` and lookarounds read only the value; rev 0's "value-scoped literals", the 2026-11-13 lean
Frank accepted) vs "context assertions make a SEPARATE kind composed by D196's in-context `&`" (B2). Under A a
context-free pattern's triples are (any, s, any), i.e. its string set, and a context-bearing operand is checked against
the real context, which is exactly B2's in-context composition. So A and B2 give the SAME answer for every `&`,
label condition and pattern hole; they differ only where a context-bearing value lands in a STRING position
(literal operands, assertions, `enumerate`, `records` entries, transform outputs: Q1X-5, Q1X-6). The answer-bearing
contrast is A/B2 vs B1. Kit witnesses (in-context = A/B2, --isolated = B1):
| form | subject | A / B2 | B1 |
|---|---|---|---|
| `(?<= )\w+` & `^S\w*` (x: /^S\w*/) | `x Sab` | None | (2,5) Sab |
| `\w{3}` & `\w+\b` | `foobar` | (3,6) bar (start MOVES) | (0,3) foo |
| `\d+` & `(?<=\$)\d+` | `a $12 b 34 $5` | (3,5) 12 | None (dead) |
| `\d+` & `\d+(?=px)` | `w 12px` | (2,4) 12 | None (dead) |
| exact `\b<ipv4>\b` on [1,9) | `256.1.1.1` | False | True |
Recommendation: the round's comparison (and §11) should name THREE candidates (A, B1, B2), or rule B2 = A's answers
with a different kind system; otherwise a ruling for "B" leaves the anchor-in-a-condition answer open (that is C27).

### Q1X-3 (CONFIRMED; design, owner criterion 1; effort medium; blast: §11, §4.1, §8 filters) Neither model is look-alike-clean; the divergence is confined to assertions at a value's EDGE, which is statically decidable
A/B2 break pairs that look alike: (i) `x: /^S\w*/` vs `x: startsWith("S")` (= `/S.*/`, §8): on `x Sab` the first fails,
the second passes (row 1 of Q1X-2); §11's own sentence "keys starting with S are `/S.*/`" invites the `^` spelling.
(ii) `\w{3} & /\w+\b/` silently MOVES the reported match (foo -> bar), the owner's "context silently making a
predicate fail". B1 breaks other pairs: (iii) `p := /(?<=\$)\d+/` searched finds `12`, yet `n: p` can never pass
(rows 3-4); (iv) `/a${num}/` with `num := /\b\d+\b/` vs the pasted text `/a\b\d+\b/`: on `a12` the pasted form
fails (`q.py find 'a\b\d+\b' 'a12'` -> []) while a value-scoped hole (§11: "every hole denotes a SET OF STRINGS")
passes (`exact '\b\d+\b' a12 1 3 --isolated` -> True); (v) `"256.1.1.1" & contains(ipv4b)` with
`ipv4b := /\b${ipv4}\b/`: B1 erases the boundary at the hole edge and finds `56.1.1.1` (row 5).
Every divergence needs an assertion that can read OUTSIDE the value: `^`/`\b`/lookbehind reachable from the value's
start with an empty prefix, or `$`/`\b`/lookahead reachable before its end. Assertions strictly inside agree under all
models. That property is decidable on the pattern (nullable-prefix/suffix reachability of the assertion node).
Recommendation (fits criterion 1: look-alikes either agree or one is REFUSED): adopt B with an EDGE-ASSERTION ERROR: in
a set position (operand of `&`, label condition, hole, filter body), an assertion that can read outside the value is a
compile error ("`^` in the condition on x reads text outside x: write `startsWith(\"S\")` for the value, or move `^`
into the pattern that places x"), with an explicit named in-context form (a library call, no keyword) if a measured
need appears. Under A the nearest mitigation is a `label.context` WARNING plus the dead-condition error (Q1X-8 shows
pcrec already detects the always-dead case: `[a-z]+ (?<=\$)\d+` compiles to no DFA tables); the PARTIAL case (fails
for some subjects only) stays silent under A.

### Q1X-4 (CONFIRMED underdetermination; design/answer; effort small; blast: §11, §4.1) Model A's "context inside the match" has two readings that give different answers
§11: "a label condition's value is the label's span WITH its context inside the match, so a lookbehind in a condition's
set sees the text before the label". A1: the context is the whole SUBJECT (what D196's in-context oracle does); A2: the
context is the MATCH text only. Witness: `(n = /\d+/) & (n: /\d+(?=px)/)` on `w 12px`, match = `12`: A1 match
(`q.py and '\d+' '\d+(?=px)' 'w 12px'` -> (2,4)), A2 none (the `px` is outside the match). Same for a lookbehind on a
label that starts the match: `n: /(?<=\$)\d+/` on `a $12`: A1 match, A2 none. A2 also breaks a look-alike INSIDE A:
the top-level `/\d+/ & /\d+(?=px)/` (a set `&`, subject context) and the label-condition spelling of the same thing
differ. Cost differs too: A1 lets a right-context obligation run PAST the reported end (deferred acceptance plus
memory of where the span ended, Q1X-8); A2 closes every obligation at the match end.
Recommendation: if A is kept, rule A1 and delete "inside the match" from §11.

### Q1X-5 (CONFIRMED by construction + kit; answer/design; effort small; blast: §5.6 assertions, §2.1 literals, §12.3/12.5 `@assert`) Under A, a string literal `&` a context-bearing pattern is EXISTENTIAL over contexts
§2.1: `"5"` = {"5"}; under A that is the triples (any, "5", any). So `dollar := /(?<=\$)\d+/`,
`@assert.none("5" & dollar)` FAILS (the triple with left context `$` exists) although the subject `5` never matches
(`q.py exact '(?<=\$)\d+' 5 0 1` -> False) and `$5` does (`exact ... '$5' 1 2` -> True). Likewise
`@assert.some("Sab" & /(?<=Q)S\w*/)` passes. A user reads `"5" & p` as "does p accept the text 5"; under A it is "is
there SOME surrounding text in which it would". Under B1 the assertion tests the value alone (passes); under B2 a
string mixed with the context kind has no context at all: an error or a rule the spec must add. No model lets an
assertion state SEARCH behaviour: E-IPV4's documented `256.1.1.1` -> `56.1.1.1` (`q.py find <ipv4> 256.1.1.1` ->
[(1,9,'56.1.1.1')], CONFIRMED) and its `\b` fix (`find \b<ipv4>\b '256.1.1.1 and 10.0.0.1'` -> only `10.0.0.1`) can
only be asserted through `contains`, which brings back Q1X-3 (v).
Recommendation: whichever model, define literal-vs-context `&` explicitly (B: refuse it, per the edge-assertion rule);
consider a library search assertion (`@assert.finds(p, "256.1.1.1", none)`-shaped, a name not a keyword).

### Q1X-6 (SUSPECTED gap, confirmable by reading §§2.7/5.5/7; design; effort medium; blast: §2.7, §5.5, §7 records, §12.8) Model A needs three unstated context-STRIPPING rules, each a value scope inside A
(a) `records` entries (§7, E-FILE): the record rx `lines := /^[^\r\n]*$/m` matches in the FILE's context; if an entry
kept its triple (left context = the preceding file lines), `alts | heavy` would match `foo` in a subject only after
`# words\n`. E-FILE's expected answer requires entries to be context-free strings; A must say so. Under B it is the
default (an entry is a string). (b) `enumerate` (§5.5) "re-joining preserves which match is reported": for
`enumerate(/(?<=a)[bc]/)` the array ["b","c"] re-joined is `b|c`, NOT the original; under A enumerate must either refuse
a context-bearing rx or carry contexts (infinite); under B2 it is a kind error for free. (c) Transforms (§2.7): the
pullback's image is not subject text, so `x & unpad & /^5/` has no context to read; A must value-scope `^` there,
giving `^` two meanings in look-alike chains (`x & /^5/` in-context vs `x & unpad & /^5/` value-scoped), against
criterion 1. Recommendation: list these three as §13 items for A, or count them as evidence for B with the edge rule
(Q1X-3), under which all three are the same refusal.

### Q1X-7 (CONFIRMED; doc/answer; effort trivial; blast: §12.8 E-FILE, §7 empty-match text) E-FILE's trailing-newline claim is false under PCRE's `(?m)^...$`
§12.8: "Without `& !\"\"`, a trailing newline in `w.txt` gives an empty entry, the final pattern is nullable". With the
stated record rx and PCRE semantics (which A's contexts and B's search both give), a TERMINATING newline yields no
empty match (PCRE2's multiline `^` does not match after a final newline): `q.py find '(?m)^[^\r\n]*$'
'# words\nfoo\nfoobar\n'` -> [(0,7),(8,11),(12,18)], no empty entry. An INTERNAL blank line does
(`'foo\n\nbar\n'` -> (4,4,'')). Also the CRLF case: `'foo\r\nbar\n'` -> only `bar`, so the untiled bytes are the whole
`foo\r\n` (0-4), not just "the `\r` byte". Fix: say "a blank line gives an empty entry"; name the untiled range.

### Q1X-8 (CONFIRMED measurements + SUSPECTED bounds; size/design; effort: none for the spec, large for a build; blast: G2, §6.1, §7 prerequisites) Automaton cost per model; A and B2 put every edge-assertion condition on an UNBUILT lowering, B1 puts none
Measured with main's build/pcrec (`--features all --no-captures`, forward DFA states/classes; `q1x/probe.sh`):
isodate 14st; `(?<=\$)`isodate 15st (DFA); `\b`isodate`\b` 15st (DFA); ipv4 20st, ipv4 with `\b` around EACH of 4
octets 25st = with `\b` only outside (the inner `\b` collapse; a library type with `\b` used 4 times costs +25%,
not x2^4); `(?<=[$€])\d+`, `(?<!\w)\d+` 3st (DFA); `(?m)\d+$` 4st (DFA). OFF the automaton today (engine `vm`):
`(?<=USD |EUR |\$)\d+`, `(?<=\$ )\d+` (any multi-char lookbehind), `[A-Z]{3} (?<=USD )\d+` (mid-pattern), every
lookahead (`\d+(?=px)`, `\d+(?=px)[a-z]+`, isodate`(?=px)`). Without features, `\b`/`(?m)`/lookarounds are refused.
Per model, for the default level (G2):
- context-free label condition / `&` / hole / library type: identical in all models: the product |X|x|S| on the span
  (no context state; A's triples of a plain rx are (any, s, any)). Model A does NOT force context state onto every
  named rx, only onto uses whose pattern carries an edge assertion (Q1X-3), per USE (each use has its own context).
- edge LOOKBEHIND (?<=L) in a condition (A, B2): a product with min-DFA(Σ*L) running over the text before the label;
  factor <= |that DFA| (proxy: `USD |EUR |\$` = 7st, the hand-lowered `(?:USD |EUR |\$)\d+` = 8st DFA, so SIZE is
  small; the gap is that today's engine sends the lookbehind form to the VM: needs D196 add. 2's regular-lookaround
  lowering, which §7's named build prerequisites ([DFA-MIN-FAST], budget, [PRED-SPLIT]) do not list). B1: 0 (statically
  true/false at the value edge).
- edge LOOKAHEAD (?=R) / `$` / trailing `\b` (A1, B2): the forward DFA carries the SET of pending R-states (worst case
  x2^|R|; for `$`/`\b` x2), and under A1 the obligation can outlive the reported end, so the DFA accepts AFTER the span
  ends and must remember where it ended (a tag or a reverse pass; today: VM). A2 closes obligations at the match end.
  B1: 0. Model B never needs a per-span verification or reverse pass for `&` itself: X & Y on one span is one product
  DFA; span reporting reuses the existing forward/reverse/anchored tables every engine already emits.
- Which §12 example leaves automaton code: NONE under any model (no example has an assertion in a set position;
  E-JSONL's `(?m)^...$` proxy compiles to DFA). Under A/B2, every discriminating case of Q1X-2 except the one-class
  lookbehind and `\b` is VM today, so at the default level it would be the G2 compile error until the lowering exists;
  under B1 (or B + edge-assertion error) none is.

### Q1X-9 (CONFIRMED; design/test; effort small; blast: §12, G1/G2 checkable forms) The acceptance set cannot decide Q1: all 11 examples are model-neutral
Per example, A / B1 / B2: E-JSONL, E-WEEKDAY, E-IPV4, E-LUHN, E-CAL, E-RFC, E-NEAR (a, b, c), E-HTTP, E-SEP, E-DEPTH:
unchanged under all three (no assertion inside any set, hole or condition; their only anchors are in a final pattern
or a records rx). E-FILE: unchanged under B1/B2; under A only with Q1X-6 (a)'s stripping rule. Claimed PCRE behaviours
re-checked: E-IPV4 `56.1.1.1` (held); E-DEPTH `[[[[1]]]]` -> inner `[[[1]]]` at (1,8), `[[1]]` whole (held, expanded
to PCRE with scalar = `\d+`); E-WEEKDAY/E-NEAR dates (held: isoweekday 6/5/4; 13 and 30 days); E-FILE trailing newline
(FAILED, Q1X-7). Recommendation: add discriminating acceptance cases whose expected answers the owner rules:
E-CTX-1 `x: /^S\w*/` on `x Sab`; E-CTX-2 `/a${num}/`, `num := /\b\d+\b/`, on `a12`; E-CTX-3
`@assert.none("5" & /(?<=\$)\d+/)`; E-CTX-4 `\w{3} & /\w+\b/` on `foobar` (does the match move?); E-CTX-5
`x & unpad & /^5/`; E-CTX-6 `enumerate(/(?<=a)[bc]/)`. Q1X-2's table gives each one's answer per model.

## PROBED-AND-HELD

- Rules examined: §11 (context-marked sets, holes, "entirely" rule), §2.1 literals, §2.7 transforms, §4.1 conditions,
  §5.5 enumerate, §5.6 assertions, §6.1 G2 levels, §7 records/prerequisites, D196 + add. 2, COND-FAMILY 2026-11-13
  (3) value-scoped lean and 2026-11-14 Q1 notes: 14.
- Examples walked under A/B1/B2: all 11 of §12 (+ the 3 §11 citations). 10 held unchanged under all models, E-FILE
  held under B (A needs a rule), and §11's G3/E-JSONL claims for A held under B too (Q1X-1).
- Oracle (kit) cases run: 31 (find/and/exact, in-context vs --isolated). Held: lone `(?<=\$)\d+` search; E-IPV4
  `56.1.1.1` and `\b` fix; E-DEPTH nesting; internal blank line gives an empty records entry.
- Compiles with build/pcrec (timeout 60 each, under q1x/): 36. Held: `\b`, one-class lookbehind, `(?m)^/$` stay DFA
  at +0-1 state; inner-`\b` redundancy collapses (ipv4 25st either way); pcrec's never-match detection empties the
  always-dead condition proxy `[a-z]+ (?<=\$)\d+`.
- Python datetime: 5 checks held (weekdays 6/5/4, day gaps 13/30).
- FREEZE NOTE: §11 cites predx C15/S2 for the "a name means the same everywhere" argument; that text is in a denied
  report, so Q1X-1 works from §11's one-line statement of it.
