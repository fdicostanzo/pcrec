# [COND-FAMILY] spelling survey: `&` `&!` `|` against prior art

Lane synsurv, 2026-11-13. Input for the owner's ruling, not a ruling. Tests the leaning recorded in
`docs/design/plan_row_bodies/COND-FAMILY.md` ("SPELLING LEANING") and D196 (asymmetric intersection, tightest
first: concatenation, intersection, alternation).

**Evidence status, read first.** The lane's web-fetch helpers returned no readable pages (their reports never
reached the lane), so NO row below was re-read against its URL in this session. Every fact is from the
author's recall of the cited public source; the URL names where to confirm it. Rows marked (?) are the ones
recalled least firmly; confirm them before they carry weight. Nothing here was run against pcrec or PCRE2.

## SUMMARY

- The leaning holds on meaning and on tier order. Three independent systems already spell the family the same
  way for the same reason: Perl's `(?[ ])` regex sets (`&` intersect, `|`/`+` union, `-` subtract, `!`
  complement, `&` tighter than union), Lucene/dk.brics `RegExp` (`|` union, `&` intersection, `~` complement,
  concatenation > `&` > `|`, difference written `a&~b`), and Python's own set operators (`&` tighter than `|`).
  Lucene's `&~` is the closest ancestor of `&!`.
- It does NOT hold as an always-on spelling. In PCRE2 an unescaped `&` is a literal today (`R&D`, `AT&T`,
  `a=1&b=2`, `&amp;`), so enabling it by default silently turns each of those into a pattern that matches
  nothing. The only mainstream engine that made `&` default-on in a pattern language (Lucene/Elasticsearch
  `RegExp`) gates it behind flags; every other system confines the operators to a bracket class or to a
  delimiter that was previously illegal (Perl `(?[`) or a version flag (Python `regex` `(?V1)`).
- Doubling (`&&`) buys no safety: `&&` is common in the text people match (shell lines) and in Java/Rust means a
  class-only intersection.
- Real clashes to settle: Ragel puts `|` `&` `-` on ONE precedence level (left-assoc), against D196; PEG's
  `&e`/`!e` are lookahead, so a PEG reader parses `A &!B` as "A not followed by B"; `x =~ rx & y` has an
  operand-extent ambiguity unless the pattern after `=~` is delimited.
- Thin evidence: the span-reporting rule ("left chooses") has no prior art in any automaton-based system
  (they report sets, not a chosen end); Raku's `&` is the one place to look (not confirmed here). Complement
  relative to a declared type (`year &! leap`) has no prior art in regex syntax.

## PRIOR ART

Columns: INT intersection, DIF difference, CMP complement, UNI union, PREC precedence (tightest first), OPT-IN
how the syntax is reached. "class" = only inside `[...]` and over character sets. Confidence: F firm, ? check.

| System | INT | DIF | CMP | UNI | PREC | OPT-IN | Conf | Source |
|---|---|---|---|---|---|---|---|---|
| Java / Kotlin(JVM) class | `[a-z&&[aeiou]]` | `[a-z&&[^aeiou]]` (via `[^]`) | `[^...]` | juxtaposition / nested `[..[..]]` | range, union, then `&&` (lowest) in the Pattern javadoc table | none: always on, class only; `&&` outside a class is literal | F | docs.oracle.com `java.util.regex.Pattern`, "Character classes" |
| .NET | none | `[a-z-[aeiou]]` | `[^...]` | juxtaposition | n/a (subtraction must be the LAST item in the class) | none: always on, class only | F | learn.microsoft.com "Character classes in .NET regular expressions", "Character class subtraction" |
| Python `regex` (mrab) | `&&` | `--` | `~~` is symmetric difference; `[^]` complement | `\|\|` | not recalled (?) | `regex.V1` / `(?V1)` flag; V0 default keeps `re` behaviour; class only | F/? | pypi.org/project/regex, "Set operations" |
| Python stdlib `re` | none | none | `[^]` | none | n/a | `[[`, `&&`, `\|\|`, `--`, `~~` in a class emit FutureWarning: reserved for future set operations | F | docs.python.org `re`, "Regular Expression Syntax" |
| Rust `regex` / `regex-syntax` | `[a&&b]` | `[a--b]` | `~~` symmetric diff; `[^]` | nesting `[a[b]]` | one level among the binary ops, left to right (?) | none: always on, class only | F/? | docs.rs/regex, "Character classes" |
| Ruby (Onigmo/Oniguruma) | `[a-w&&[^c-g]]` | via `[^]` | `[^]`; `(?~X)` is "absent" operator | juxtaposition | n/a | none, class only | F | github.com/k-takata/Onigmo doc/RE |
| ICU regex | `[\p{L}&&\p{ASCII}]` | `[\p{L}--\p{Lu}]` | `[^]` | juxtaposition | n/a | none, class only | F | unicode-org.github.io/icu/userguide/strings/regexp.html |
| ICU UnicodeSet | `[[a-z]&[aeiou]]` | `[[a-z]-[aeiou]]` | `[^...]` | implicit | n/a (?) | its own bracket syntax, a distinct language | F | unicode-org.github.io/icu/userguide/strings/unicodeset.html |
| UTS #18 RL1.3 | required capability: intersection | required: difference | `[^]` | required | spelling NOT mandated; examples use `&&`, `--`, `\|\|`, `~~` | feature level (RL1.3) | F/? | unicode.org/reports/tr18/ |
| Perl regex sets `(?[ ])` | `&` | `-` | `!` | `+` or `\|` | `!`, then `&`, then `+ \| - ^` equal, left-assoc | the group `(?[ ... ])`, a form that was a syntax error before 5.18; experimental until its warning was dropped (5.36) (?) | F/? | perldoc.perl.org/perlrecharclass "Extended Bracketed Character Classes" |
| Ragel | `&` | `-`, strong `--` | `!` (language), `^` (one character) | `\|` | `\|` `&` `-` `--` share ONE level, left-assoc; concatenation binds tighter (?) | always on: a different (machine) language | F/? | colm.net Ragel guide, "Operator Precedence" |
| Lucene `RegExp` / dk.brics.automaton / Elasticsearch regexp | `&` | `a&~b` | `~` | `\|` | concatenation, then `&`, then `\|`; `~` unary on the next atom | flag bits (INTERSECTION, COMPLEMENT, ANYSTRING, INTERVAL, ALL, NONE); Lucene's `RegExp(s)` default enables all of them, Elasticsearch documents "optional operators" and says `&` then needs escaping | F | lucene.apache.org core `org.apache.lucene.util.automaton.RegExp`; brics.dk/automaton |
| re2c | none | `\` on character classes only | `[^]` | `\|` | n/a | always on | F | re2c.org manual, "Regular expressions" |
| flex | none | `{-}` on classes | `[^]` | `{+}` on classes, `\|` | n/a | always on | ? | westes.github.io/flex/manual/Patterns.html |
| ocamllex | none | `#` on classes | `[^]` | `\|` | n/a | always on | F | ocaml.org manual, "Lexer and parser generators" |
| JFlex | class `&&` | class `--`; none at pattern level | `!a` on whole patterns | `\|` | not recalled | always on | ? | jflex.de/manual.html |
| Brzozowski / Owens-Reppy-Turon derivatives | `And` | via `And`+`Not` | `Not` | `Or` | constructors, no surface syntax | library API (OCaml/Haskell/Scala/Racket derivative libraries) | F | "Regular-expression derivatives re-examined", JFP 19(2), 2009; Brzozowski, JACM 11(4), 1964 |
| `greenery` (Python) | API `&` on patterns (?) | API `-` (?) | `.everythingbut()` | API `\|` | Python operator precedence | library API; its regex STRING parser takes no `&` (?) | ? | github.com/qntm/greenery README |
| PEG | none | none (`!A B` approximates) | none | `/` ordered choice | prefix `&`, `!` bind tighter than sequence | always on; `&e` AND-predicate, `!e` NOT-predicate: LOOKAHEAD | F | Ford, "Parsing Expression Grammars", POPL 2004; bford.info/pub/lang/peg |
| Perl `=~` `!~` | n/a | n/a | `!~` negates the match test | n/a | above `*` `/`, below unary `!` `~`; right operand is a delimited pattern or an expression | always on | F | perldoc.perl.org/perlop |
| Raku | `&` all branches match at the same start; `&&` ordered, short-circuit | none | `<!...>` negative assertion, `!` | `\|` (longest-token), `\|\|` ordered | not recalled | always on (new language) | ? | docs.raku.org/language/regexes, "Conjunction" |
| Set-algebra notations (TLA+, Z, Python `set`, SQL) | `\cap`, `∩`, `&`, INTERSECT | `\`, `-`, EXCEPT | overbar, `~` | `\cup`, `∪`, `\|`, UNION | Python: `-` tighter than `&` tighter than `^` tighter than `\|` | n/a | F | language references |

Notes.

1. Two families. CLASS-LEVEL operators (Java, .NET, Rust, Python `regex`, ICU, Onigmo, UTS #18, flex, re2c) work
   on sets of characters, are always on, and are safe because `[` already opens a new context. WHOLE-PATTERN
   operators (Perl sets only for characters; Ragel, Lucene/brics, derivative libraries, Raku) are the
   leaning's family. The only PCRE-style engine with one at pattern level is Perl, and only over character
   sets.
2. Perl `(?[ ])` is the nearest precedent for "a PCRE-family syntax acquires Boolean operators without breaking
   old patterns": it claims a bracket form that was an error. Its `&`-above-`|` order and `!` complement
   agree with the leaning; its `-` for difference does not.
3. Lucene shows the same family on whole patterns with the leaning's exact tiers (concatenation, `&`, `|`) and
   spells difference as intersection with a complement. It is also the cautionary tale: default-on `&`
   forced users to escape literal `&` (a standing Elasticsearch support topic, recalled, not cited).
4. Python's `re` reserving `&&`, `||`, `--`, `~~` and `[[` in classes (FutureWarning) is a direct record that
   the language owners considered unescaped operator characters a compatibility hazard.
5. `--` for difference and `||`, `&&` are the UTS #18 / Rust / Python `regex` consensus for CLASSES. The
   leaning's single `&` has no class-level precedent except ICU UnicodeSet and Perl sets.
6. Ragel's `--` (strong difference: remove strings that CONTAIN a word of the second language) is a different
   operator from `-`; the leaning's `&!` is plain difference (`X & ~Y`).
7. No surveyed system defines which end a Boolean combination reports when several ends are admissible: the
   automaton systems answer a membership or longest question. D196's "left chooses" is new ground, except
   possibly Raku (unconfirmed).

## CONFLICTS

Each item gives the clash and a concrete case. "Today" means PCRE2 as pcrec reads it; the registry
(`pcrec --list-syntax`) is authority and was not consulted by this lane.

1. **Literal `&` in existing patterns (severe, silent).** Today `R&D`, `AT&T`, `\w+&\w+`, `a=1&b=2`,
   `&amp;`, `foo&&bar` match those literal characters. With `&` always an operator, `R&D` is `R ∩ D`: it never
   matches, and the pattern is still accepted. Mitigation: opt-in; escaping `\&` already works, so a
   rewriter is possible, but it does not help patterns already deployed.
2. **Literal `!` and `&!`.** `a&!b` (a C-ish `a &!b` in source text), `wow!` are literal today. `!` alone is
   benign (nothing in the leaning uses bare `!`), but `&!` as one token changes `x&!y` from three literals
   to a difference. Same cure as item 1.
3. **`(?!`, `(?&name)`, `(?<!`.** No token-level clash: `(?!` and `(?&` begin with `(?`, and the operators
   would be infix, between operands. Concrete hazard is lexical: in `(?&x)&(?&y)` the first `&` is a name
   introducer, the second an operator; a lexer must key on the preceding `(?`. `a(?!b)&c` is fine (`&`
   after `)`).
4. **Doubled operators do not make it safe.** `cmd1 && cmd2` as a literal pattern is as plausible as `R&D`;
   in Java and Rust `[a&&b]` means class intersection while in PCRE2 it is the set {a,&,b} today. A portable
   pattern `[a-z&&[^aeiou]]` is therefore already two different programs across engines; pcrec should keep
   PCRE2's reading of class contents and put Boolean operators OUTSIDE classes (a class-level intersection
   is expressible as `[a-z] & [^aeiou]`).
5. **PEG reader expectation.** In PEG, `&e` and `!e` are prefix lookaheads, so the text `A &!B` reads as
   "A, then (lookahead that B does not match)", i.e. "A not followed by B". In the leaning it is `A` minus `B`
   (the whole span of A must not be in B). The two parse differently (infix vs prefix), so the grammar is
   unambiguous, but a PEG-trained reader will misread `year &! leap`. The PCRE2 spelling of the PEG meaning
   is `year(?!leap)`, so the two stay distinguishable in the same pattern.
6. **`&` vs `&&` reader expectation.** C-family readers expect `&&` for Boolean AND and `&` for bitwise AND.
   Predicate `x > 0 & x < 9` reads as bitwise to them. It is semantically AND, and because predicates are
   pure (COND-FAMILY base requirements) short-circuit versus not is unobservable, so no behavioural trap,
   only a reading one. Java already uses `&` for non-short-circuit Boolean AND, a precedent.
7. **Precedence.** (a) Tier order concatenation > `&` > `|` agrees with Perl sets, Lucene, Java classes and
   Python sets but DISAGREES with Ragel, where `a | b & c` is `(a | b) & c`. Example: `x | y & z` is
   `x | (y & z)` under D196 and `(x | y) & z` in a Ragel reader's head. (b) Predicate comparisons bound
   between concatenation and `&` follows C (`==` tighter than `&`), which is the opposite of Python
   (`a & b == c` is `(a&b)==c`). Example: `x % 4 == 0 & y` is `(x%4==0) & y` here. Either choice is
   defensible; the survey finds no system that has both pattern operators and C-style comparison operators
   in one expression.
8. **`=~` binding and operand extent.** Perl's `=~` takes a delimited pattern on the right (`/.../`), so
   `$x =~ /a/ && $y` is unambiguous. With no delimiter in pcrec, `x =~ a & b` is either `(x =~ a) & b` (a
   Boolean `&` pattern-or-predicate mix) or `x =~ (a & b)`. The leaning's tier rule (comparison tighter than
   `&`) picks the first, which then requires `b` to be a predicate, while `a & b` as a pattern is the
   second reading. Cure: delimit the right operand, or give `=~` a rule that its right operand is a primary
   (a name, a group or a literal).
9. **Overloaded `&`.** The same character is intersection of patterns (`isodate & leap_day`), a
   membership test of a value against a pattern (`x & rx`) and conjunction of predicates (`p & q`).
   `year &! leap` mixes a type pattern with a predicate macro. The survey finds no prior art for one
   operator across these three object kinds; Lucene and Perl sets have only the first. It is coherent only
   because COND-FAMILY makes a predicate denote a pattern; a type-checking rule must say what `&` does with a
   (value, pattern) pair.
10. **`!~` and `&!`.** `x !~ rx` (negated search) and `x &! rx` (negated whole-text membership) are both
    needed under the leaning and differ only in scope (search versus anchored); that is an inherited Perl
    habit, not a clash, but a documented pair.

## RECOMMENDATION

The leaning holds as a SEMANTIC and PRECEDENCE choice. Adjustments the prior art suggests:

1. **Opt-in, not default.** Reach `&`, `&!` and the predicate language only inside a form PCRE2 currently
   rejects, so existing patterns keep their meaning. Two precedent shapes: a delimited group (Perl's
   `(?[ ... ])`, claimed from the error space) or a scoped inline flag (Python `regex` `(?V1)`; Lucene's flag
   bits). A scoped flag composes (`(?B: a & b)`-style, spelling a placeholder) and is stackable with
   existing `(?i)`; a delimited group makes the extent of the new grammar obvious to a reader. Which
   introducer characters are free in PCRE2 10.46 is a registry question this lane did not answer.
2. **Do not double the operators and do not touch class contents.** Evidence: conflict items 1 and 4. Keep
   `[...]` exactly PCRE2; class intersection stays the pattern-level `[..] & [..]`.
3. **Keep `&` `&!` `|` and the tier order** concatenation, `&`, `|` (Perl sets, Lucene, Java, Python agree).
   State the Ragel difference in the spec's notes as a known divergence. `&!` matches Lucene's `&~` shape;
   the alternative `-`/`--` has wider class-level use (UTS #18, Rust, Perl) but `-` already means range and
   `--` is a decrement-looking token, so the survey does not argue for changing.
4. **Document PEG's reading.** One spec sentence: `&e`/`!e` are NOT the lookahead predicates here; the
   pcrec lookaheads are `(?=` and `(?!`.
5. **Pin `=~`'s right operand** to a primary (delimited pattern, name or parenthesised group) so
   `x =~ rx & p` has one reading; keep `x & rx` (whole-text) and `x =~ rx` (search) as the two spellings.
6. **Write the typing rule for overloaded `&`** (conflict 9) before the spelling is adopted: it is the
   actual semantic risk, not the glyph.
7. **Complement:** the survey has Lucene `~`, Ragel `!`, Perl sets `!`. The leaning's choice to expose
   only `&!` (relative to the left operand's type) is safe and loses nothing the surveyed systems need
   except De Morgan forms; no surveyed system defines complement relative to a declared type, so that part
   is a new design, not a spelling choice.

Where the evidence is thin: (a) every row above needs a confirming re-read (see the status note); the (?) rows
most (Python `regex` precedence, Rust binary-op precedence, Ragel precedence, Raku conjunction span and
precedence, JFlex, flex `{+}`, greenery's string syntax). (b) No prior art for the asymmetric "left chooses"
reporting rule. (c) No prior art for one `&` across pattern, value and predicate. (d) The freedom of
introducer characters in PCRE2 was not checked against the registry.
