# Q1R findings: crit-predspec

Lens Q1R: per foundation rule, Model A (context-marked triples) vs Model B (string sets + D196 in-context kind); look-alike witnesses.

## Findings

Reading labels used below (where a model is UNDERDETERMINED the two readings are named):
- **A-s**: Model A, a label's context = the real SUBJECT around the label. **A-m**: Model A, context truncated to
  the enclosing MATCH (§11 "WITH its context inside the match" admits both).
- **B-c**: Model B, a context-kind pattern composed by D196 in-context `&` wherever a subject exists (match time).
- **B-x**: Model B where NO subject exists (compile-time set uses): either **B-err** (the context kind is refused,
  a kind error) or **B-iso** (evaluated on the string alone).
Kit = `python3 -I kit/q.py` (libpcre2 10.49); "ctx" = default in-context, "iso" = `--isolated`.

### Q1R-1 (design; effort S to fold; blast radius: the whole §11 Q1 choice) Per-rule table, Model A vs Model B

| rule | Model A (triples) | Model B (string sets + context kind) | same? |
|---|---|---|---|
| §2.1 two kinds | rx = triple set; still two kinds | adds a context-dependent kind (a THIRD value kind, against §2.1's "two kinds"/no third kind lean) | different |
| §2.2 `& \| !` | extensional over TRIPLES; `!` complements triples, so `!/^#.*/` CONTAINS "#x" in mid-line contexts (Q1R-5) | extensional over strings within the string kind; `&` with a context operand = D196 in-context; `!ctx` underdetermined (in-context complement = A, or a kind error) | different for `!`; same span rule (D196) |
| §2.3 unapplied macro | unchanged | unchanged | same |
| §2.4 comparisons | sections are context-free triple sets | string sets | same |
| §2.5 no concat | unchanged | unchanged | same |
| §2.6 `$x ~ rx` | UNDERDETERMINED: does rx searched "inside a value" see the subject around $x (A-s) or not? `^` mid-line fails under A-s (Q1R-6) | the value is a string, rx searched in it alone; a context-kind rx: B-err or B-iso | different / underdetermined |
| §2.7 transforms (pullback) | UNDEFINED: a transducer maps strings; the context of an IMAGE (`unquoted` strips a quote that was in L) is not given (Q1R-7) | well-defined on strings; context kind after a transform = B-err | different (A underdetermined) |
| §3.2 `X[...]`, `where`, `.name` | unchanged | unchanged | same |
| §3.2 `X & f`, "empty products drop" | emptiness over triples: an entry survives if ANY context satisfies (Q1R-5) | static on strings; context operand undecidable statically (keep, or B-err) | different |
| §3.3 holes / single entries | a pattern hole is in context (PCRE subroutine) | same (a hole inserts a sub-pattern, matched in the subject) | same |
| §3.4 extensional vs structural | "language" = triples: `/\b\d+\b/` and `/\d+/` (same strings) are DIFFERENT languages (Q1R-3) | different kinds; equality defined within a kind | different; both deviate from what users call "the language" |
| §4.1 `x:` | A-s: context = subject; A-m: = match; the two disagree (Q1R-2) | B-c = A-s | A underdetermined; B-c = A-s |
| §4.2 unset labels | unchanged | unchanged | same |
| §4.3 sequence rule | each iteration's L includes earlier iterations: `^` passes iteration 1 only (Q1R-4) | B-c: same as A | same (both silent) |
| §4.4 computed labels | UNDERDETERMINED: a non-substring value has no position, so no context (empty? any?) | the value is a string; context kind on it = B-err / B-iso | different (A underdetermined) |
| §4.5 ambiguity | context follows the span, so per-parse | same | same |
| §5.5 enumerate | UNDERDETERMINED: strings of a triple set drop the context silently (`enumerate(/^[ab]/)` re-joined = `/a\|b/`) or error (Q1R-8) | strings of a string set; context kind = B-err | different |
| §5.6 assert (some/none/same) | decided over triples: `@assert.same(/\b\d+\b/, /\d+/)` FAILS | within a kind; across kinds B-err (or B-iso: passes) | different |
| §7 records tiling | the record rx is searched in the text in context | same | same |
| §7 records entries | UNDERDETERMINED: does an entry keep its FILE context (meaningless in a run-time subject)? | strings | different (A underdetermined) |
| §7 empty-match rule | nullable = some triple with empty span: `/\b/`, `/(?=a)/`, `/^/m` nullable (correct: they yield empty finds) | string-set nullability: `/\b/` iso = EMPTY set, so B-iso MISSES it (Q1R-9); B must compute nullability on the context kind | different |
| §11 literal scope, no inherited flags | unchanged; interacts with holes (Q1R-11) | unchanged | same |
| §11 holes `${}` | in context | in context | same |
| §11 guards `(\d+)&${ <256 }` | D196 in-context `&` | D196 in-context `&` | same |

COUNT: 25 rule rows; SAME 12, DIFFERENT 7, A-UNDERDETERMINED 6 (§2.6, §2.7, §4.1 A-s/A-m, §4.4, §5.5, §7 entries).
Every A-underdetermined row is a place with NO subject position (a transform image, a computed value, a
compile-time set, a file entry) or a choice of WHICH text is the context. B is underdetermined only on what a
context kind does where no subject exists, and there B-err is a clean, diagnosable answer.

### Q1R-2 (answer/design; CONFIRMED; effort S for a diagnostic; blast radius: every label condition with `^ $ \b` or a lookaround) `x: /^S\w*/` silently never matches, and under A-m depends on the OUTER pattern

Rule: §11 (context-marked sets; label value "WITH its context inside the match"), §4.1, §13 C27.
Witness program: `P := /(?<w>\w) (?<x>\w+)/` then `P & (x: /^S\w*/)`; subject `a Sab`.
Look-alikes on the same P and subject: `P & (x: startsWith("S"))`, `P & (x: /S.*/)`, `P & (x: /^S\w*/)`.
- Kit: `exact '^S\w*' 'a Sab' 2 5` -> False (ctx), True (iso); `and '(?<= )\w+' '^S\w*' 'a Sab'` -> None,
  `and '(?<= )\w+' 'S.*' 'a Sab'` -> (2,5) 'Sab'.
- A-s and B-c: `/^S\w*/` -> NO MATCH, no diagnostic; `startsWith("S")` and `/S.*/` -> match "a Sab". The
  user's PCRE habit ("`^S` = starts with S") silently becomes "x is at the start of the subject".
- A-m (context = inside the match): P2 := `/(?<x>S\w*)/` on the same subject: the match is "Sab", L inside the
  match is empty, `^` holds -> MATCH (kit `exact '^S\w*' 'Sab' 0 3` -> True). So with the SAME label span (2,5) and
  the same condition, P2 passes and P fails: the condition's truth depends on how much text the enclosing
  pattern happens to consume before x. Worst look-alike in the set.
- B-iso: all three match (the value-scoped reading of COND-FAMILY 2026-11-13 (3), superseded).
Also (both models, D196): `/\w+/ & /^S/` on `Sab` reports `S` (kit `and '\w+' '^S' 'Sab'` -> (0,1)), while
`/\w+/ & startsWith("S")` reports `Sab`: "a set means the strings it matches ENTIRELY" makes `/^S/` = {"S"}, so
even with the context satisfied `x: /^S/` fails on x = "Sab". PCRE users will write `/^S/`.
Diagnostic that removes the silent failure (works under A-s and B-c): a `label.context` WARNING, the twin of
`label.ambiguous` (§4.5): compute the program with the condition read in context and read isolated; if they
differ, show a witness (here `a Sab`), both readings and the fix (`startsWith("S")` / `/S.*/`). If the in-context
program is EMPTY, it is an ERROR via D196 add. 2's never-match fact ("condition on x can never hold: x always
follows ' '"). Recommend: pick A-s (or B-c) explicitly and reject A-m; A-m is unpredictable by construction.

### Q1R-3 (design; CONFIRMED; effort S; blast radius: every named pattern with an assertion) Model A breaks owner criterion 3 as users read it; a binding is consistent across uses only under A

Rule: §2.2 / §3.4 ("membership depends only on the language"), COND-FAMILY 2026-11-14 "`&` is extensional",
§11 REASONING ("a name means the same everywhere").
Witness: `num := /\b\d+\b/`; uses: (i) top level `num`; (ii) hole `/x${num}/`; (iii) condition
`/x(?<n>\d+)/ & (n: num)`; (iv) `/x(?<n>\d+)/ & (n: /\d+/)`. Subject `x12`.
- Kit: `find 'x(?:\b\d+\b)' 'x12'` -> []; `exact '\b\d+\b' 'x12' 1 3` -> False (ctx), True (iso);
  `find 'x\d+' 'x12'` -> (0,3).
- A (and B-c): (ii) and (iii) both NO MATCH, (iv) matches. The binding means the same in a hole and in a
  condition (A's stated gain), BUT `num` and `/\d+/` denote the SAME STRINGS ({digit strings}, iso both accept
  exactly the digit runs) and behave differently under `&`/`:`. Under A this is "extensional over triples",
  formally sound, but the user-visible language is the string set: criterion 3 ("two spellings of one language
  behave the same") holds only if the user knows `\b` adds context. This is the owner's named defect class.
- B-iso: (iii) matches, (ii) does not: hole and condition disagree for one name (A's argument against B).
- B-err: (iii) is "a context-kind pattern used as a value set": the kind makes the difference VISIBLE.
Neither model gives all four the same answer; the honest consistency is "same answer OR a diagnostic". Remove
the silence: the Q1R-2 `label.context` warning fires on (iii) with witness `x12`; for B, the kind error.

### Q1R-4 (answer; CONFIRMED; effort M for the per-occurrence check; blast radius: every repeated label) A context condition on a REPEATED label passes iteration 1 only: works in a one-line test, fails in production, and the never-match check does not catch it

Rule: §4.3 (sequence rule: `x: S` constrains ALL iterations) x §11 (A) / D196 in-context (B-c); E-HTTP shape.
Witness: `headers := list_of(join([name = /[\w-]+/, value = /[^\r\n]*/], sep = ": "), sep = /\r\n/)`;
`headers & (name: /^[A-Z][\w-]*/)` (user intent: names start with a capital). Subjects `Host: a` and
`Host: a\r\nAccept: b`.
- Kit: `exact '^[A-Z][\w-]*' 'Host: a\r\nAccept: b' 0 4` -> True; `... 9 15` -> False (ctx), True (iso);
  `exact '(?m)^[A-Z][\w-]*' ... 9 15` -> True.
- A-s / B-c: the one-header block MATCHES, the two-header block FAILS (all-iterations rule), silently. Adding
  `m` to the condition literal flips it (`^` after `\n`): a flag inside a condition decides whether a header
  block validates. A-m: same as A-s here (iteration 2's L inside the match contains `\r\n`).
- B-iso: both match.
The program is NOT empty (one-header blocks match), so a never-match error cannot catch it; only the Q1R-2
`label.context` comparison (in-context vs isolated reading differ: witness = the two-header block) does.
Recommendation: `label.context` must run per program, not per condition-is-empty; cost = one extra product
automaton per context-bearing condition (bounded by the same budget as `label.ambiguous`).

### Q1R-5 (answer; CONFIRMED; effort S; blast radius: every `!` over a context-bearing set, incl. `!~`) Complement of a context set silently PASSES: `!/^#.*/` keeps comment lines; `$x !~ /^err/` is true mid-line

Rule: §2.2 (`!` a filter, extensional), §3.2 (empty products drop), §2.6 (`$x !~ rx` = `$x & !contains(rx)`), §8
`contains(s) := /.*${s}.*/`.
Witness 1: `alts := ["#x", "foo"]`; `alts & !startsWith("#")` vs `alts & !/^#.*/` vs `alts & !/#.*/`; subject
`a #x`.
- Kit: `exact '^#.*' 'a #x' 2 4` -> False (ctx); `exact '^#.*' '#x' 0 2` -> True; `exact '#.*' 'a #x' 2 4` -> True.
- A: `!/^#.*/` is the complement over TRIPLES, which contains ("#x", L mid-line). The product of entry "#x" with
  it is non-empty, so the entry is NOT dropped (§3.2) and the search on `a #x` REPORTS `#x` (the `^` fails at 2,
  so `!` passes). `!startsWith("#")` and `!/#.*/` drop it. A user filtering comment entries gets them back
  wherever they are not at a line start. B-c: same at match time; B-err: refused statically; B-iso: dropped.
Witness 2: `/msg=(?<m>[^ ]*)/ & ($m !~ /^err/)` (per §2.6's own definition), subject `msg=err x`.
- Kit: `exact '^err.*' 'msg=err x' 4 9` -> False (ctx), True (iso). Under A-s the `^` inside `contains` is in
  context, `contains(/^err/)` never holds for m, so `!~` is ALWAYS true: an error filter that filters nothing.
  Silent failure turns into silent acceptance under negation; this is worse than Q1R-2 (no empty program, no
  missing match to notice).
Diagnostic: `label.context` (Q1R-2) on the condition; plus for structural `&` an ERROR "entry `#x` survives
`!/^#.*/` only in some contexts; write `!startsWith("#")`" when an entry's product is context-dependent (A) — the
same fact B reports as a kind error. Side note (doc, §2.6 vs §4.1): `$x !~ rx` is DEFINED as `$x & !contains(rx)`,
and §4.1 makes `$x & ...` used as a condition an ERROR ("did you mean `x: ...`?"); the definition should read
`x: !contains(rx)` (O12 adds a consequence: the sugar's expansion is illegal).

### Q1R-6 (design; underdetermined under A; effort S to rule) `$x ~ rx` (search INSIDE a value) has two readings under A; B has one

Rule: §2.6 ("search inside a value (unanchored)"), §4.1 (`$x` = "a one-string set"), §11 (A: label values carry
context). Witness: `line := /(?<k>\w+)=(?<v>[^\n]*)/`; `line & some($v ~ /^err/)` (spelling placeholder);
subject `msg=err x`.
- Kit: `exact '^err.*' 'msg=err x' 4 9` -> False (ctx), True (iso).
- A, reading 1 (the value keeps its context, consistent with §11's label rule): `^` sees `msg=` before v, so the
  search never finds `^err` inside v: silent never-match; `v: startsWith("err")` matches. Reading 2 (`$x` is a
  one-string set, §4.1, context-free): `^` = start of the value, matches. The draft states both premises.
- B: `$v` is a string; the search runs on it alone (B-iso is the natural reading of "search inside a value").
Consequence: `$x ~ /^err/` and `x: /^err.*/` and `x: startsWith("err")` give 3 answers under A reading 1 (no,
no, yes), 2 under reading 2 (yes, no(entirely+context), yes). Recommendation: rule that `$x` (a VALUE, §4.1) is
context-free under either model (search sees only the value; `^`/`$` = the value's ends), and say so beside
§11; then `$x ~` is the documented "value-scoped" door and `x:` the in-context one, which a `label.context` warning
names in its fix text.

### Q1R-7 (design; underdetermined under A; effort S to rule) Transforms (pullbacks) have no defined action on contexts under A

Rule: §2.7 (a transform is a transducer; "pulls a set back: the strings whose t-image lies in S") x §11 (sets are
triples). Witness: `kv := /msg=(?<msg>"[^"]*")/`; `kv & (msg: (unquoted & /^timeout/))`; subject `msg="timeout"`.
- Kit (the raw span only; the image is not a subject substring, so no oracle exists for it): `exact '^timeout'
  'msg="timeout"' 5 12` -> False (ctx), True (iso).
- A: the image `timeout` has no position in the subject. Reading 1: the image inherits the label's L (`msg="` —
  is the stripped quote part of L?), `^` fails: silent never-match. Reading 2: the image is context-free, `^`
  holds. Reading 3: the triple's L is transformed too (t applied to L?): meaningless for `unpad`/`ci`. §2.7's
  "regular in, regular out" closure theorem is stated for STRING sets; over triple sets it is not stated.
- B: the pullback is over strings, well-defined; `unquoted & /^timeout/` with a context-kind operand is a kind
  error (B-err) with the fix `startsWith("timeout")`. B is the model §2.7 was written for.
Recommendation: under A, rule "a transform's output is context-free; a context assertion after a transform
stage is an ERROR" (which is B's rule restricted to transforms).

### Q1R-8 (design; underdetermined under A; effort S) Compile-time set uses (enumerate, assert, records entries, computed labels, import/export/warn name sets) have NO subject: A silently drops or keeps context, B can refuse

Rules: §5.5, §5.6, §7 (records entries, `import(names)`, `@export(names)`), §7.1 (`@warn.off(rx)`), §4.4.
Witnesses (no kit run possible: there is no subject; the strings were checked iso):
- `enumerate(/^[ab]/)`: A gives ["a","b"] (context DROPPED; then `join(enumerate(x))` re-joined = `/a|b/`, which no
  longer requires a line start: §5.5's "re-joining preserves which match is reported" fails) or an error;
  unstated. Same for `enumerate(/a(?=b)/)` (lookahead lost).
- `@assert.same(/\b\d+\b/, /\d+/)`: A over triples FAILS; B-iso PASSES; B-err refuses. The user asked "same
  digit runs?" (iso: both accept exactly digit strings).
- `@warn.off(/^dead\./)` / `@export(/^[^_]/)`: names are strings with no context; under A `/^[^_]/` = names that
  are one char and at a line start of... nothing. A must define the context of a name (empty L/R -> `^` holds,
  `/^[^_]/` = one-char names only by "entirely"). Look-alike: `@warn.off(startsWith("dead."))` (the draft's
  example) works, `@warn.off(/^dead\./)` suppresses NOTHING (entirely = `dead.` only), raising `warn.unused` at
  best.
- Computed labels (§4.4): `d: /^-?1\d$/`: the value `days($b)-days($a)` has no position; A's context undefined.
Recommendation: one rule for both models: WHERE NO SUBJECT EXISTS, a context assertion is an ERROR ("`^` has no
context in a name set; write `startsWith`"). That is B-err; under A it is an explicit exception to "every
pattern is a triple set", which shows the rule set is B-shaped.

### Q1R-9 (answer; CONFIRMED; effort S; blast radius: the empty-match ERROR, §7) Nullability must be computed WITH context; and "anchored" is ambiguous (mode vs assertion)

Rule: §7 THE EMPTY-MATCH HAZARD ("FINAL pattern is NULLABLE ... search mode"; "no diagnostic when
anchored/whole-string").
- Kit: `exact '\b' '' 0 0 --isolated` -> False and `exact '(?=a)' '' 0 0 --isolated` -> False (as STRING sets both
  are EMPTY, not nullable); `find '\b' 'ab cd'` -> 4 empty matches; `find '(?=a)' 'bab'` -> (1,1) empty.
- A: nullable = some triple with an empty span: `/\b/`, `/(?=a)/` flagged, correct (they yield empty finds).
- B-iso: the string set is EMPTY, so `/\b/` as the final program escapes the hazard rule and returns 4 empty
  finds with no diagnostic. B must compute nullability on the context kind (some context admits the empty
  span), i.e. A's definition. A point for A, stated as a requirement on B.
- Both models: `/^\d*/m` in search mode (kit `find '(?m)^\d*' 'a\nb\n12'` -> (0,0), (2,2), (4,6)) yields an empty
  match on every line without digits. Is it "anchored"? If `^` in the pattern counts as anchoring, no
  diagnostic; if only the caller's anchored/whole-string MODE counts, ERROR. Unstated. Recommend: only the MODE
  exempts; `^`/`\b`/lookarounds do not (the hazard is "an empty find", which `^...m` still produces per line).

### Q1R-10 (answer/doc; CONFIRMED; effort S; blast radius: E-FILE, §7 tiling, O20) E-FILE's stated behaviour is wrong under PCRE, and its own record rx always fails tiling

Rule: §7 records tiling; §12.8 ("Without `& !""`, a trailing newline in `w.txt` gives an empty entry").
- Kit: `find '(?m)^[^\r\n]*$' '# words\nfoo\nfoobar\n'` -> (0,7), (8,11), (12,18): NO empty entry after the
  trailing newline (PCRE2's multiline `^` does not match after a final newline at subject end). Python's `re`
  gives `[(0,1),(2,2)]` on `a\n` (an empty entry): the example's expectation follows Python, not PCRE (G3,
  "PCRE2 is the source of truth"). An empty entry DOES arise from an interior blank line (`a\n\nb` -> (2,2)).
- The `\n` bytes 7, 11, 18 belong to no record, so under the tiling rule as written E-FILE is a COMPILE ERROR
  for every multi-line file (O20 restates the gap; the consequence is that the worked example fails its own
  rule). Same in both models (records searches the text in context).
- `foo\r\nbar` -> only (5,8) `bar`: the CRLF line is not matched at all, so the tiling error names bytes 0-4,
  not "the `\r` byte" as §12.8 says.
Fix: §12.8 text: the empty entry comes from a blank line, not the trailing newline; resolve O20 before E-FILE
can be an acceptance case (e.g. `records(text, rx, sep = /\n/)` declaring the gap).

### Q1R-11 (answer; CONFIRMED; effort S; blast radius: every hole with anchors inside an `m`/`i`/`s` literal) No inherited flags makes `/${q}/m` differ from the inlined text, silently

Rule: §11 ("NO INHERITED FLAGS"; holes; E-JSONL's `/^${q}$/m`). Witness: `q := /^\{.*\}$/`; program A1
`/${q}/m` vs program A2 `/^\{.*\}$/m`; subject `{a}\n{b}`.
- Kit: `find '(?m)(?-m:^\{.*\}$)' '{a}\n{b}'` -> []; `find '(?m)^\{.*\}$' '{a}\n{b}'` -> (0,3), (4,7).
- Both models: A1 finds NOTHING (q's `^`/`$` keep single-line meaning), A2 finds both lines. Moving text into a
  binding (which §5.1 recommends: "long logic goes in `:=` definitions") silently changes it. E-JSONL avoids it
  only because its `^`/`$` stay in the outer literal.
Diagnostic: a `flag.hole` WARNING when a hole's pattern contains a flag-sensitive item (`^ $ .` case letters)
inside a literal whose flags differ from the binding's, naming the fix (`q := /.../m`).

### Q1R-12 (design; CONFIRMED; effort S; blast radius: §11 REASONING, the basis of the TENTATIVE ruling) §11's G3 argument for Model A does not discriminate between the models

Rule: §11 REASONING ("Context-marked sets keep G3 for lone-literal programs with lookbehind (`/(?<=\$)\d+/`)
and E-JSONL's `/^${q}$/m`").
- Kit: `find '(?<=\$)\d+' 'a $12 b 34 $5'` -> (3,5), (12,13); `and '\d+' '(?<=\$)\d+' ...` -> (3,5) (ctx), None (iso).
- A lone-literal program and E-JSONL's final pattern are SEARCHED IN THE SUBJECT under Model B as well (the
  final expression is a pattern, not a set used as a value), so both keep G3 under B. The models diverge only
  where a pattern with context is used as a SET: an `&`/`:` operand (B-c = A-s at match time, kit line 2) or a
  compile-time set (Q1R-8, where B-err is the clean answer and A is underdetermined). The cases that actually
  separate the models are Q1R-2..Q1R-8, all of which are look-alike or silent-failure cases under A-s / B-c, and
  none of which §12 exercises (no worked example puts a context assertion in a condition, a transform, an
  enumerate, an assert or a `!`).
Recommendation: restate the Q1 trade on the separating cases; add one acceptance case with a context
assertion in a label condition (e.g. Q1R-2's witness) so the choice is tested, not argued from G3.

### Q1R-13 (design; verdict; effort S) Which model the rule set fits, and the diagnostics that remove each silent failure

Verdict: the rule set as written is B-SHAPED. §2.1 ("a set of strings, extensional"), §2.4 ("comparisons are on
the STRING SET"), §2.7 (transducers over strings), §3.4 ("depend only on the language"), §4.1 (`$x` a one-string
set), §4.4 (non-substring values), §5.5 ("a finite rx's STRINGS"), §5.6 (language equality), §7 (name sets), and
§11's own "a pattern used as a SET is the strings it matches ENTIRELY" all presuppose string sets; all six A-
underdetermined rows (Q1R-1) are where A must invent a context that does not exist. A's one real gain is
uniform in-context behaviour of a NAME at match time (Q1R-3) and context-aware nullability (Q1R-9); B-c
delivers the first identically (D196 in-context `&`) and B can adopt A's nullability definition. Recommended
foundation: **Model B with B-c at match time and B-err where no subject exists**; it equals A wherever A is
defined and turns A's underdetermined rows into errors.
BUT neither model removes the owner's named failure (Q1R-2, Q1R-4, Q1R-5: A-s and B-c both silently fail);
only diagnostics do:
| silent failure | diagnostic |
|---|---|
| condition never holds (`x: /^S\w*/` after text) | ERROR via never-match (D196 add. 2) on the program/branch |
| condition holds in some positions only (repeated label, Q1R-4) | `label.context` WARNING: in-context vs isolated readings differ, witness shown (twin of `label.ambiguous`) |
| `!` of a context set passes silently (Q1R-5) | `label.context` on the condition; structural `&`: ERROR when an entry survives only in some contexts |
| A-m outer-pattern dependence (Q1R-2) | none possible: reject A-m |
| `/^S/` = {"S"} "entirely" vs PCRE "starts with" | `label.context` fix text suggests `startsWith`; consider a `set.anchor` warning on a bare leading `^`/trailing `$` in a set position |
| `$x ~ /^err/` (Q1R-6), transforms (Q1R-7), compile-time sets (Q1R-8) | rule: values and transform images are context-free; context assertion with no subject = ERROR |
| `/${q}/m` flags (Q1R-11) | `flag.hole` WARNING |
| `/\b/` final pattern under B-iso (Q1R-9) | nullability on the context kind (A's definition) |
`label.context` is the single general mechanism: one comparison of the two readings, reported with a witness,
exactly the shape §4.5 already uses for ambiguity; it makes the model choice OBSERVABLE to the user rather
than an obscure rule.

## PROBED-AND-HELD

- Rules examined: 25 (Q1R-1 table: §2.1-§2.7, §3.2-§3.4, §4.1-§4.5, §5.5, §5.6, §7 records tiling/entries/empty
  match, §11 literal scope/holes/guards). Held as SAME under both models: 12 (§2.3, §2.4, §2.5, §3.2 index/where/.name,
  §3.3 holes, §4.2 unset, §4.3 (same, both silent), §4.5 ambiguity, §7 tiling, §11 literal scope, §11 holes, §11 guards).
- Kit cases run: 41 oracle calls (exact/and/find, ctx vs iso), all reproduced in the findings; plus 1 Python `re`
  comparison (Q1R-10). No compiler runs needed (no size/automaton claim made).
- Held: §2.4 `/\d+/ & <256` on `1000` reports `100` at top level and `x: <256` on a label x="1000" rejects that
  parse but the search then finds x="100": consistent in both models (context-free sections).
- Held: §4.5 some-parse with a context condition: the context follows the parse's span, so the warning's witness
  rule extends unchanged.
- Held: E-JSONL `/^${q}$/m` and lone `/(?<=\$)\d+/` work under both models (Q1R-12).
- FREEZE NOTE: §11 cites predx C15/S2 for A's rationale; those live in a denied report; worked from the subject's
  text and COND-FAMILY.md only.
