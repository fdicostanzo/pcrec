# src/parse — PCRE pattern parser

Base-tier PCRE parser for literals, '.', character classes, quantifiers, alternation, anchors, groups, and metachar escapes. Constructs outside the base tier are routed through module lookup tables that yield precise "requires module" diagnostics instead of miscompiles; future drop-in modules will register handlers in these tables.

## Files

- **parse.c** — base-tier PCRE parser; module hook points for escapes and (?X...) constructs; produces AST

## Conventions

The parser builds an expression AST using recursive descent. Split edges in the AST preserve choice order for greedy/lazy and alternation preference. Module lookups are statically defined: add new entries to esc_modules and atom_modules arrays when a module registers. Unsupported syntax routes through lookup to produce an actionable error.

Maintenance: update this file when files are added/removed or their roles change.
