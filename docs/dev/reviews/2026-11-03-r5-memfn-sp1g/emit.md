# Critic lens EMIT (emitted vs replaced) -- round memfn-sp1g

Question: does any emitted byte, stamp, listing, diagnostic, exit code or
`KSRCTRACE`/`KSTRACE` stderr record differ between BASE (c0f0d543b) and
SUBJECT (efd724b4b)? Answer: NO. Across the population below, every case was
byte-identical on both sides.

## Findings

None. Nothing differed: emitted C, emitted header, stdout, stderr (incl.
every `KSRCTRACE object` and `KSTRACE` record) and exit code, in all 393
cases, on both the plain pair and the trace pair. The sampled asm was
identical too.

## PROBED-AND-HELD

Method. Scripts and fixtures are under this lens dir (scripts/mkx.py,
scripts/mkcases.py, scripts/run.sh, fx/, out/all/). Every case ran four
binaries, each in its own directory with the same relative `-o`:
bin/base/pcrec (b), bin/base-trace/pcrec (bt), the review tree's build/pcrec
(s), and bin/subj-trace/pcrec (st). For each case, `diff -r -q` compared b
with s and bt with st over x.c, x.h, the `-o DIR` artifacts, stdout, stderr
and rc. Command: `scripts/run.sh all.cases out/all` -> out/all.diff is EMPTY.

Population: 393 cases x 4 binaries = 1572 invocations, plus 12 smoke and 30
`gcc -O2 -S` = 1614 compiles (cap 1800).
- A, pattern sample (66 cases): 30 patterns covering literal, alternation,
  sets/classes, anchored ^/$, \b, (?m), (?i), counted repeats, backrefs
  (VM), lookahead and non-ASCII. Run under -e byte (27) and -e utf8 (30)
  with `--features all`, plus 6 `--engine=vm` cases. The default analysis
  applies, so this is the PRIOR_AUTHORED default (byte) and PRIOR_NONE
  (utf8) state.
- B, kit arms (98 cases): 6 patterns x all 12 `--memfn=no-NAME` deny rows
  under `-fmemfn-simd`, plus `-fmemfn-simd` byte and utf8, plus
  `-fno-memfn-simd` with two denies. Also one unknown deny and the retired
  `no-fd-r8` (both refuse identically).
- C, provenance fixtures written by scripts/mkx.py (130 cases). This is 28
  bundle shapes x {byte, utf8 dir} x 2 patterns, run as measured or
  authored blocks:
  - each fidelity token: verbatim, adapted, synthesized (synthesized reads
    PRIOR_AUTHORED per D162 add. 4), and none;
  - authored blocks with each fidelity;
  - `provenance bytes` at 0, 0042, 2^63, 2^64-1, 2^64, and 26 digits;
  - malformed values: -5, +5, 0x10, 1_000, Verbatim, measured, an empty
    fidelity, 'verbatim', two tokens, a trailing comment, trailing spaces,
    a duplicate fidelity row, adapted without adaptation, and no bytes;
  - `source synthesized`.
  Plus measured bundles named `default` with each fidelity token (12),
  `include <default>` with its own fidelity (2), a two-link
  authored-synthesized -> measured-adapted chain (4), and a compound file
  with four targets under two inline analyses, with and without CLI
  `--analysis` (2).
- E, tests/findings/e1_fixtures.py tree (36 cases): COPY, MDEF (`default`
  measured, bytes 4242, no fidelity), AUTH, INC (`include <default>`),
  CHAIN outer/inner (inner `fidelity verbatim`, bytes 555), and L1
  `l1none` (the all-dropped block: underivable-arrives, PRIOR_NONE under
  utf8, and the refusal where read). Each was run x byte/utf8 x 2 patterns.
  Also multi2.rxt two-target (byte, utf8) and 6 nothing-asked cases
  (-fno-req-byte).
- R, tests/findings/res_fixtures.py tree (44 cases): shadow, ord (A, and B
  then A), user default with include_next, withdef, byteonly, d2, lib
  fall-through, two, mixed, pickz/picka, tabq, the cyca cycle, the d1
  nine-link chain, nosuch, and prov P1/P2/P3, each x byte/utf8. Also
  fill.rxt, view.rxt, multi.rxt, s1_shadow.rxt, dup.rxt and pcrecline.rxt.
- L, listings (19 cases): --list-schema, --list-axes (incl. the memfn kit
  section), --list-limits, and --list-analysis for 13 bundles/files (incl.
  compound.rxt and view.rxt with --analysis). Also --list-source,
  --emit-facts=byte,utf8 (2), --version, and 2 -I-refused queries.
- asm: `gcc -std=gnu11 -O2 -S` of 15 artifacts on both sides (DFA, VM,
  utf8, simd, deny arms, measured/adapted/2^64-1, chain, pickz): 0 diffs.

What the trace records covered (640 `KSRCTRACE object` lines at st, each
equal to bt's line):
- SOURCE: MEASURED, PRIOR_AUTHORED, PRIOR_NONE and UNSTATED.
- ROW: measured, authored, prior-none, underivable-arrives and no-shape.
- FIDELITY column: verbatim, adapted, synthesized and `-`.
- BYTES column: 0, 7, 11, 42, 333, 444, 555, 777, 1000, 1001, 1003, 4242,
  1000000, 2^63 and 2^64-1.
72 cases refuse, and they refuse identically on both sides (same text and
rc).

Why no difference can arise, read from the code:
- The kit reads only `tag`/`present`/`payload` (memfn/src/presence.c:50-54,
  same at both revs), and mf_art_begin only stores `an`.
- BASE's stanza mapping could differ from the offer in exactly one way: it
  refused a fidelity outside {verbatim, adapted, synthesized} with an
  internal error. That input cannot reach the offer. The `closed fidelity
  ...` FORMAT clause is checked unconditionally at parse
  (src/parse/rxt_source.c closed_check, ~1563), and the probes confirmed
  it: Verbatim, measured, the quoted form and two tokens all get
  [schema-constraint]; the empty value gets [value-shape]; trailing spaces
  are trimmed to `verbatim`.
- Bytes went to the trace as `o.bytes` at both revs (unsigned long long ->
  uint64_t -> %llu: same value). Fidelity NULL prints `-` at both revs.

Pre-existing, identical on both sides, not this change (noted, not a
finding against the subject): `provenance bytes 18446744073709551616` and a
26-digit value pass the INT shape check. strtoull then saturates them
(src/parse/rxt_find.c:150) to 18446744073709551615 in the offer and trace.
