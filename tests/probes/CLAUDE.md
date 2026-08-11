# tests/probes — design-measurement probe sources

Measurement programs against libpcre2 (through `../fuzz/pcre2_abi.h`), NOT
part of `make test`. These are the probes behind the extension design's
Part II / R14 / §18 measurements, committed so that the numbers quoted in
`docs/extension_design.md` and `docs/reviews/2026-08-11-r14-part2.md` are
reproducible, and so that **the SPEC-MOD0 author (a D27 writer denied the
design document) can be handed working probe code instead of prose** —
that hand-off is the reason this directory exists (plan step SPEC-MOD0).

Build any of them:

    TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe tests/probes/<file> -ldl

(`TMPDIR` matters on the project box — /tmp is a quota'd tmpfs. libpcre2 is
runtime-only here: no header, no -dev link, hence the dlopen shim.)

## Files

- `probe_qe.c` — the §13 lexical-mode evidence (`\Q\E` quantifier binding,
  class behaviour, `(?i)`/`(?x)` interactions, `(?#)` transparency), the
  62-escape class-position sweep behind §14.3's partition, and §16.1's
  endpoint doorway×side table.
- `probe_atom.c` — atom-position facts: the literal-fallback four at atom
  position, backref-vs-octal cells, the C2/F3 forward-reference
  re-verification, `\0`-never-backreferences.
- `probe_verify.c` — the author's 29-cell re-verification of the R14 panel's
  load-bearing measurements before they were applied (digit runs starting
  8/9, quantifiability, `(?#` in class, capture forms, conditional bodies,
  endpoint edges, the `(?x)`-comment count cell).
- `probe_defer.c` — the §18.1 deferred-resolution cells: `\12`'s
  octal-vs-backref decided by the RUNNING count; error precedence (every
  structural error beats err 115); conditional forward references.
- `probe_digit_sweep.c` — the generated 2,931-probe digit-model sweep
  (predictor stated in the header BEFORE the run; backref-ness read via
  `PCRE2_INFO_BACKREFMAX`, sanity-checked; zero disagreements at close).
- `probe_quant.c` — the §18.3 quantifiability determinism probes: the
  option-run form split (`a(?i)*` 109 vs `a(?i:b)*` compiles) and the
  per-VerbName split (`a(*FAIL)*` 109 vs `a(*pla:b)*` compiles).
- `probe_fix3.c` — FIX-3 (K13): the twelve escape rows' class-position
  semantics, 41 cells with the member SET verified byte-exact (all 256
  single-byte subjects per compiling cell) — octal runs, the literal-fallback
  four, tails, range endpoints, and the error-151/108 cells with their
  offsets recorded. The oracle behind
  tests/base/class_escape_fallbacks.rxt's `# pcre2-only` blocks (U7).
- `probe_class_expect.c` — MOD-0.1 slice 3: the `class_expect` column's 44
  values, measured from libpcre2 (census of `^[S]$` over all 256 bytes; takes
  a `--list-syntax` dump path and probes every esc/class-bracket row). The
  independent cross-check of tests/spec_mod0/class_expectations.inc — the two
  implementations agreed 44/44 before the column was transcribed into
  registry.c.
- `probe_endpoint_k12.c` — MOD-0.1 endpoint-rule slice (K12): the 42 cells
  the §16 five-step rule changes or deliberately leaves — char-type escapes
  both sides, both-construct pairs, the step-3-beats-step-4 cells, the
  non-certified `\p` boundary, the bracket doorway's low side, non-range
  dashes and truncations. The oracle behind the K12 pins in tests/reject/.

## The method these encode (R14's closing lesson)

State the predictor BEFORE running; generate probe sets from the claim's
FAILURE DIRECTIONS, not from the examples that produced the claim; and feed
the predictor from the oracle (libpcre2's own verdicts/introspection), never
from the row data under test. `probe_digit_sweep.c` is the template.

Maintenance: add a file per measurement campaign; keep each header's
predictor/purpose comment current; update this file when files are
added/removed.
