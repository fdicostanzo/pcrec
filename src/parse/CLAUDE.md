# src/parse — PCRE pattern parser

Base-tier PCRE parser for literals, '.', character classes, quantifiers, alternation, anchors, groups, and metachar escapes. Constructs outside the base tier are routed through module lookup tables that yield precise "requires module" diagnostics instead of miscompiles; future drop-in modules will register handlers in these tables.

## Files

- **parse.c** — base-tier PCRE parser; module hook points for escapes and (?X...) constructs; produces AST
- **registry.c** — the syntax construct registry (D24/SR-1): every non-base
  construct as one `static const` row. Not yet consumed by parse.c — SR-2
  routes the four doorways through it and must emit byte-identical output

## The construct registry (registry.c, D24)

One declarative home per non-base construct, replacing knowledge that lived in
up to five places at once. `\v` shipped decoding as vertical tab because
`esc_modules[]` and `esc_char_value`'s switch disagreed ten lines apart with
nothing enforcing agreement; a construct with two homes will drift.

Everything non-base enters through exactly **four doorways** — after `\`, after
`(?`, after `(*`, after `[` inside a class. The base tier reaches exactly one
of them, once, for `(?:`, which is why "the common path is fast" holds by
construction rather than by optimisation (SR-5 will guard it with an
instrumented build).

Four axes stay apart on purpose: **flavour** (which construct a byte MEANS) /
**option** (what it DENOTES) / **enablement** (is it available) / **engine**
(can it LOWER). A flavour change rebinds a row; it cannot reach inside another
construct's handler. One flavour exists today, by design.

Rules when touching it:

- **Add a row here and nowhere else.** `syntax` must be a pattern that really
  reaches that doorway — tests/registry/ uses it as the probe, so a new row
  covers itself with no test edit.
- **`RS_MODULE` with no handler is a complete outcome**, not a stub: the
  construct is named, cleanly rejected and queryable.
- **The `engines` column is design intent, not measurement.** Nothing consumes
  it until SR-8/M4; do not build on its values without checking them.
- **Two "requires module" diagnostics deliberately stay in parse.c**: `\x{...}`
  (a sub-case of the base `\x` handler) and the possessive `+` suffix (a
  quantifier suffix, not an atom). Neither is a doorway, and giving them one
  would cost the base tier a lookup.

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
