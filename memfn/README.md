# pcrec-memory-functions

Bespoke high-speed memory functions: byte search and compare code
generated for the exact question being asked, rather than picked from a
fixed library.

A fixed library answers "find this byte" or "compare these bytes". Real
callers ask compound questions — "find the first position where this
byte is followed four bytes later by one of these three, and the run
starting there matches `SELECT` caselessly" — and pay for the gap
between the two: a second pass, a stop at every false candidate, a call
per hit. This project takes the whole question (an operation over a
conjunction of byte-set and masked-run terms at offsets, with the
caller's proven span bounds and density hints) and returns C text that
answers exactly that question, in one pass where one pass is possible.

- **Every answer has a portable scalar form**, always present, kept as
  good as it can be on its own. Vector (ISA) forms are a layer on top
  that must beat the current scalar form to be chosen.
- **Text, not a runtime.** The output is self-contained C; the code that
  uses it does not link this project.
- **Measured, not assumed.** Every choice between forms rests on a
  measurement whose regime is named, and is checked against a plain
  byte-loop reference over a generated space of questions.

Its first consumer is [pcrec](../README.md), the PCRE-to-C regex
compiler, which hands every prefilter and scan site in a generated
matcher to this project and splices back the text it returns. A stand-
alone CLI and reference functions are planned for other callers.

## Status

**No code yet.** The design of record is
`docs/design/memfn/integration.md` in the pcrec tree. The first code
lands with that design's step R4a.

## Licence

[0BSD](LICENSE): use, copy, modify and distribute for any purpose, with
or without fee, with no notice required. Text this project emits into
your program is yours under the same terms. Files translated from other
projects name their source and licence in a header and in
`PROVENANCE.md`.
