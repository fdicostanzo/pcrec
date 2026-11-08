# [POSTFACT] row body (long notes)

## 2026-10-27 — spelling and scope (Frank + manager)

- **Spelling** (Frank: "that is a good idea"): a language tag in the embedded-code family, ``(?C`rx: $1 < 256`)`` (`rx` is a placeholder name). Declined alternatives:
  - restricting `(?(...))`: PCRE2's conditional condition slot already has six meanings;
  - silently converting the C spelling when possible: unpredictable, and it means matching C's semantics;
  - `(?[...])`: taken by PCRE2's extended character classes (module extended-classes).
- **Guarantee:** an `rx:` predicate is lowered into the pattern or REFUSED at compile time with a reason ("not regular: use a `c:` callout"). There is never a silent fallback to a call.
- **Value semantics** (leading zeros, sign, overflow) are pcrec's own, not C's: part of the design.
- **Regular predicates over a captured span** (lowerable):
  - numbers (dec/hex/oct/bin readings): comparisons, ranges, sets, `% m`, and/or/not;
  - checksums as mod automata: Luhn (~20 states), ISBN-10/13, IBAN mod 97;
  - length and bounded character counts (password policies);
  - finite string sets, case-insensitive sets, lexicographic order, `starts_with`/`ends_with`/`contains`;
  - regex algebra `$1 ~ /re/`, `$1 !~ /re/` (intersection/difference; e.g. identifier-but-not-keyword);
  - bounded relations between captures (date validity incl. leap years, start<end time ranges), priced against the size ladder.
- **Not regular** (refused, use `c:`): unbounded two-capture comparisons, balanced counts, palindromes and reversals, unbounded arithmetic.
- **Leaning for v1:** numeric forms, length, sets, `~`/`!~`. Then named functions built on the same machinery (`luhn($1)`, `valid_date(y,m,d)`). After [INLINE-C] stage 2 (reuses the tag parser). No build without Frank's go.

## 2026-10-27 — security (Frank: "it would not have the same security implications as embedded C")

- An `rx:` predicate is lowered into the pattern; no user code runs and nothing is linked. Its trust class is a PATTERN FEATURE, not code:
  - an ordinary feature module (GRANT `any`), allowed in feature families and in `all`;
  - allowed in included and library files without sha256 pins;
  - no `--allow-code`, no `<PREFIX>_CODE_LANGS` entry.
- This holds ONLY because of the lowered-or-refused rule: an `rx:` predicate never falls back to a call. A fallback to a `c:` callout, or a named function implemented as C at run time, would bring it back under the code gate. Named functions (`luhn`, `valid_date`) are pcrec-built automata, not shipped C.
- What remains is a pattern's own risk class: compile-time size and time. A predicate whose product automaton is too big is refused by the size ladder, like any pattern. A wrong lowering is a miscompile, tested by the oracle like any module.

## 2026-11-08 — Frank: the "where" operator (idea preserved; details TBD)

Frank's words: "a special kind of inline code expression that can be translated to dfa rx. A restriction is that it can only refer to a single \"capture group\" within a predicate- it can't compare two values. I presume that means two capture groups can't really interact at all eg addition. A second point is that the intent is dfa rx which capture groups disallow. The idea: a new operator called the \"where\" operator. Example syntax \"rx ## predicate expression\"."

Examples (Frank):
- `\d+ ## $ < 256`
- `(?:\d+## $ <=255)\.` (scope limited by the group)

Frank 2026-11-08 clarification: "The syntax is only an example. I was thinking to the match thus far within scope." So the predicate's value is the text matched SO FAR WITHIN THE ENCLOSING SCOPE (from the start of the enclosing group, or of the whole match at top level, up to the operator), and the spelling `##`/`$` is a placeholder. That also settles precedence: scope is the group, not an operand.

As first stated: `$` names the text matched by the operand on the left (no capture group, so the DFA keeps its speed); the predicate refers to that ONE value only (no two-value relations, so no arithmetic between groups); the result lowers into the automaton (tier 1 above: one-variable predicates over a digit span are regular). Details TBD.

Manager notes for the design, not ruled:
- Spelling is a placeholder (Frank). Whatever is chosen must survive `(?x)`, where `#` starts a comment.
- (settled by the clarification) the value is the in-scope match so far; an alternation inside the scope means each alternative's text so far.
- Supersedes the `int($1)<=255` spelling in this row's title, which needs a capture; the where form needs none.

