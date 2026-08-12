# tests/classes — module `classes` corpus (MOD-0.3c)

The first per-module test directory (the drop-in convention from the root
CLAUDE.md): oracle-verified behaviour of the constructs module `classes`
PRODUCES — the ten char-type escapes at both positions, bare `\N` at atom
position, and the POSIX named classes with both polarities — plus the
rejections that must HOLD with the module enabled (`[\N]`, `[0-\d]`,
`[[:alpha:]-z]`, `[[:<:]]`, `[[:foo:]]`, `(?[[a]])`).

## Files

- **classes.rxt** — every block carries the `features classes` directive
  (tests/harness/run.sh passes it as `--features classes`; the default
  enabled set stays empty, and the default-state refusals stay pinned in
  tests/reject/). python-verifiable blocks (\d \D \s \S \w \W and friends)
  go through verify_rxt.py as usual; `# pcre2-only` blocks' expectations
  derive from the generated-bitmap censuses (tests/probes/probe_cls_bits.c)
  and the caseless×posix cells from tests/probes/probe_ci_posix.c — PC-4 is
  the live oracle for produced sets.

## The D33 §9.3 record

This corpus is the "probe that is false the day before" for the producing
ExtWhat vocabulary: run against the slice-1 binary (vocabulary landed,
producers not wired) it fails 37 of 43 cases with 31 distinct
pattern-compile failures — measured 2026-08-12, before the wiring commit —
and the 6 that pass there are the perr regression pins, which are not §9.3
probes. Re-run that measurement against any binary suspected of losing the
wiring: `PCREC=<binary> bash tests/harness/run.sh tests/classes/classes.rxt`.

Maintenance: add blocks when the module's producing scope grows (the octal
FN port and the RF_CLASS_* retirements land in MOD-0.3 slice 3 and bring
their own cases).
