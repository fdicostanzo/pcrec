# src/parse — PCRE pattern parser

Base-tier PCRE parser for literals, '.', character classes, quantifiers, alternation, anchors, groups, and metachar escapes. Constructs outside the base tier are routed through module lookup tables that yield precise "requires module" diagnostics instead of miscompiles; future drop-in modules will register handlers in these tables.

## Files

- **parse.c** — base-tier PCRE parser; module hook points for escapes and (?X...) constructs; produces AST

## Case folding (OS-1 / D23)

`options.caseless` (CLI `-i`) is handled entirely here: `cls_casefold` adds
each ASCII letter's other case to a class bitmap, so the automaton is built
case-blind and nothing downstream — NFA, DFA, minimizer, emitter — knows the
option exists. Measured result: `-i 'aBc'` emits byte-identical C to
`'[aA][bB][cC]'`, so caselessness is not an engine axis (D18's case 1).

Two rules that are easy to break and hard to detect:

- **Fold the POSITIVE set, then negate.** `[^a]` caseless means "neither a nor
  A". Folding the complement instead yields every byte. Both results are
  case-closed, so no downstream stage, invariant or equivalence check can tell
  them apart — only behaviour can. Pinned by tests/base/caseless.rxt and by a
  shape check requiring `-i '[^a]'` == `'[^aA]'` and != `'[^A]'`.
- **Every site that builds an A_CLASS must fold.** There are three: char_node,
  p_class, and `.` (which needs nothing — "every byte but \n" is already
  case-closed). A post-parse AST walk would catch future sites automatically
  and is deliberately not used: AST depth is unbounded in pattern length, so it
  would add exactly the recursion DD-10/TS-4 exists to remove. A new
  class-producing construct calls `cls_casefold` itself.

ASCII only — bytes >= 0x80 have no case in the C locale, and Unicode folding
stays with DD-1/M5.

## Conventions

The parser builds an expression AST using recursive descent. Split edges in the AST preserve choice order for greedy/lazy and alternation preference. Module lookups are statically defined: add new entries to esc_modules and atom_modules arrays when a module registers. Unsupported syntax routes through lookup to produce an actionable error.

Maintenance: update this file when files are added/removed or their roles change.
