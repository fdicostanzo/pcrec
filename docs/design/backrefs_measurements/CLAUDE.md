# docs/design/backrefs_measurements -- the [M6.5.1] design lane's instruments

The measurements behind `../backrefs_design.md` (module `backrefs`: numeric
`\1`..`\99` with PCRE2's octal disambiguation, `\g`/`\k` spellings,
`(?P=name)`, `(?J)`/DUPNAMES). Revised after R32 (two instruments added, four
original ones had panel-found defects; every defect here was a probe producing
CONFIDENT WRONG OUTPUT, the directory's most useful content).

Nothing here reads a backreference through pcrec (pcrec cannot compile one):
in-pcrec arms measure a SEPARATE AXIS on patterns pcrec CAN compile (the
prefilter axis `--engine=vm` vs default; the caseless-fold axis `-i '[X]'` vs
the explicit pair; the expansion's OUTPUT, e.g. `aa|bb`). Hold each
instrument to that. Kept separate from `../assertions_measurements/`,
`../eng_brep_measurements/` and siblings (never confuse one lane's numbers
with another's).

## Standing rules

- Borrow, never copy, the libpcre2 binding:
  `../eng_brep_measurements/probes/pcre2_ctypes.py` through
  `probes/br_oracle.py` (a lane that re-implements the binding it depends on
  cannot detect that the original moved).
- `br_oracle.SELFCHECK` asserts every option-bit VALUE BEHAVIOURALLY at import
  (never trusted from a header this box lacks); every probe refuses to run
  if it is non-empty.
- `probes/archive.sh` is the ONLY writer of `out/` (R30 M7 inherited); a hand
  edit there is a red line; no header may be hand-written.
- Every probe needs a way to FAIL: a vacuity guard / positive control that
  makes the run REFUSE to report when the control finds nothing; print the
  denominator in every table. Dominant defect shape: a population or filter
  that does not contain the thing measured (filter never reaching a transition
  table; subjects with no positives; a "nomatch" subject that matched; an
  erasure that was not the erasure; 255 bytes reported as 256; denominator
  counting draws; stamps compared where the fact is about engines). Second
  class: no way to fail. Third: a claim with no control (E1's counterexample,
  cell S3 of `out/br_semantics.txt`, sat archived while no one ran the model
  against it).
- Adopted critic instruments (`probes/simvm.py`, R32 critic `r32eng`'s) stay
  AS WRITTEN (only a `publish` parameter added); a lane that rewrites the
  instrument that refuted it cannot detect it softened it.
- Use a real temp directory for pcrec output, never `-o /dev/null` (pcrec also
  writes `OUT.h`); use `printf` not `echo` for strings with backslashes.
- Pad the ORACLE side only when `pcre2_match` returns a truncated pair tuple;
  never adjust the model to agree.
- Maintenance: update this file when probes or outputs are added/removed or
  their roles change.

## Files

- `probes/br_oracle.py` -- ORACLE HELPER: compile-error NUMBERS,
  `PCRE2_INFO_NAMETABLE`, three option bits, behavioural `SELFCHECK`.
- `probes/probe_br_semantics.py` -- MEASURED, both oracles: 42 cells, eight
  families + a `PCRE2_MATCH_UNSET_BACKREF` arm; divergence column is the
  deliverable (10 of 42, all python refusing).
- `probes/probe_octal_rule.py` -- MEASURED, libpcre2 + in-pcrec: octal vs
  backreference, discriminator subjects; axis D drives shipped `build/pcrec`
  on the class position (FIX-3/K13 baseline).
- `probes/probe_spellings.py` -- MEASURED, both oracles: 25 spellings
  (subroutine call vs backreference `\g` carries two constructs).
- `probes/probe_dupnames.py` -- MEASURED, libpcre2 only (python has no `(?J)`
  or `\k`): name-table order (name asc, number asc), refusal matrix,
  resolution rule over four candidate rules.
- `probes/probe_caseless_fold.py` -- MEASURED, libpcre2 + in-pcrec, all 256
  bytes: the backref fold equals pcrec's own `cls_casefold`.
- `probes/probe_prefilter_cost.sh` -- MEASURED artifact benchmark (identical
  pattern and engine, differing in prefilter); positive control and
  below-resolution guard.
- `probes/probe_erasure_hazard.py` -- MEASURED, libpcre2: erasure superset
  and span; THREE controls (vacuity, positive E2/E12, transitive E15); refuses
  to report if the positive or transitive control finds nothing.
- `probes/probe_expand_cost.py` -- MEASURED in-pcrec: why the expansion is
  declined (only customer is a `--no-captures` build); bisects the DECLINE
  boundary.
- `probes/simvm.py` -- the R32 critic's simulator (not this lane's work).
- `probes/probe_publish_discipline.py` -- MEASURED, libpcre2 vs both models:
  publish-at-open vs publish-at-close, 5,808 cells, backref-free control arm,
  reversed-span count reported separately.
- `probes/archive.sh` -- the ARCHIVER (copied from
  `../assertions_measurements/probes/archive.sh`, re-scoped).
- `out/` -- archived output with provenance headers; evidence for the R32
  panel, never an oracle; see `out/CLAUDE.md`.

## Pointers

`../backrefs_design.md` (§3.2 publish-at-close, §4.4, §7.4, §16),
`docs/dev/reviews/` R32 panel, `../assertions_measurements/`, D67.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__backrefs_measurements.md
