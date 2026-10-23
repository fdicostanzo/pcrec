# Style

Lean on purpose. The code-level style rules live in `coding.md`; this file
names them and adds the cross-cutting ones.

## Naming
A caller-facing name (a flag, an `rx_info` field or value, a CLI option, a
stamp, a spec sentence) says what the caller sees or turns off. Never kit,
memfn, proof, family letters or row ids. Not retroactive: shipped spellings
(e.g. `--memfn=`) stay. **Why:** outside pcrec's developers architecture names
mean nothing. **Source:** D174 (Frank 2026-10-22).
Emitters' short locals stay as they are: `coding.md` §1.7.

## Comments and headers
Home: `coding.md` §4.2 (invariants and why-not-the-alternative in code, history
in docs with a pointer; every function gets a header whose first sentence says
what it does in plain words, [HDR-1]/[HDR-2]). Comment density follows the
surrounding file; do not add or strip to a quota.

## The spec travels with the change
Anything a caller can observe (an entry, a flag, a stamp, a limit, a diagnostic
tier, a module's behaviour) carries its `docs/spec/` hunk in the same change.
**Source:** D80; `coding.md` §3.6. Diagnostic wording for unimplemented
constructs is not worth effort: D26.

## Emitted text
Any emitted byte is an abi event; comment escaping; anchor columns. See
`coding.md` §3.
