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
