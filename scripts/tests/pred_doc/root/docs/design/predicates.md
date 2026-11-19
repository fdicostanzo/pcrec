# Predicates (sample base file, core)

## Principles   [core/principles]

### Regex default   [core/principles/regex-default]   ruled 2026-11-01
A bare slash form is a regex unless the owner says otherwise.
WHOLE: /a/ matches; SEARCHED: /a/ finds; FIND-ALL: /a/g iterates.

## Holes   [core/holes]

### Class   [core/holes/class]   reading 2026-11-02
A hole stands for one pattern fragment of the named class.
needs: core/principles/regex-default
by: core/principles/regex-default
Definition sentence.
modes: n/a (a hole is not matched on its own)

### Name   [core/holes/name]   ?  2026-11-03
