# FINDINGS — D27 \Q...\E quoting corpus

Per the D27 method requirement: log any cell where `man pcre2pattern`'s
prose and the libpcre2-8 oracle disagreed. This file is not a template
default; it reflects what actually happened while building the corpus.

## Result: no documentation/oracle divergence found

Every expectation in this corpus — all 95 oracle-checked cells across 52
pattern blocks — matches both the `pcre2pattern(3)` prose (BACKSLASH
section's `\Q...\E` paragraphs) and libpcre2-8 10.46's actual behavior,
with no disagreement between the two anywhere `checker.py` exercised.
This includes reproducing all five worked examples from the man page's own
table verbatim (`basics.rxt`, the five `\Q\\E` / `\Qabc$xyz\E` /
`\Qabc\$xyz\E` / `\Qabc\E\$\Qxyz\E` / `\QA\B\E` blocks) and its `{\Q1\E,2}`
quantifier-defeat example (`quantifier_after.rxt`).

## Places the prose was correct but under-specified, resolved by the oracle

Not a divergence (the two never conflicted), but worth recording since D27's
whole premise is that a corpus derived purely from the promise can find gaps
an implementation-derived one wouldn't think to ask about. Two behaviors
`pcre2pattern(3)` does not state directly, confirmed empirically:

1. **What a quantifier immediately after `\Q...\E` repeats.** The doc says
   `\Q...\E` characters are literals and separately that a quantifier
   *inside* what looks like `\Q...\E` defeats quantifier recognition — but
   it never states what `\Qab\E+` itself repeats. Verified against the
   oracle: it is exactly the LAST quoted character (`\Qab\E+` on `"aabb"`
   matches `[1,4)`, i.e. `a(b+)`, not `(ab)+`) — consistent with `\Q...\E`
   lowering to a sequence of individually-escaped atoms rather than one
   atom. `quantifier_after.rxt`.

2. **Whether an EMPTY `\Q\E` blocks a following quantifier from reaching the
   real atom before it.** It does not: `a\Q\E+` matches `"aaa"` in full,
   confirming the empty quoted run is transparent to quantifier attachment.
   Contrast: `\Q\E+` with truly nothing before it (pattern-initial) is a
   hard compile error ("quantifier does not follow a repeatable item").
   Both in `quantifier_after.rxt`.

## Error codes recorded (provenance only, per D26 — not a wording promise)

| pattern | libpcre2-8 10.46 code | message |
|---|---|---|
| `[a\Qbc` | 106 | missing terminating ] for character class |
| `[a\Qbc\E` | 106 | missing terminating ] for character class |
| `\Q\E+` | 109 | quantifier does not follow a repeatable item |

Both are general PCRE2 error surfaces (106 also fires for any unterminated
class; 109 for any quantifier with nothing to its left) reached here
specifically *through* `\Q...\E` constructs, per pcre2pattern(3)'s own
statement that an unterminated `\Q` inside a class is an error "because the
character class is then not terminated by a closing square bracket."

## Scope note on what was NOT exercised

- `startpos` values greater than the subject length were deliberately
  avoided (see `oracle_probe.c`'s header): libpcre2 raises its own
  `PCRE2_ERROR_BADOFFSET` there, a startpos-clamping question that belongs
  to the base search-entry corpus, not to `\Q...\E`'s own semantics.
- No case here embeds a NUL byte in a subject or pattern; `oracle_probe`
  passes both through `argv` via C strings, which cannot carry `\0`. Not a
  gap specific to quoting — no `\Q...\E` behavior is byte-value-dependent.
