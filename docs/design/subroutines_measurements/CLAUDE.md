# docs/design/subroutines_measurements -- the [DD-14] lane's instruments

Probes, prototypes and archived output for `../subroutines_design.md`, the
module `recursion` design gate (`(?1)`, `(?&name)`, `\g<1>`, `(?R)`, `(?0)`,
`\g<0>`). Same shape as `../lookaround_measurements/` and
`../backrefs_measurements/`; it BORROWS rather than copies:
`probes/sr_oracle.py` -> `../lookaround_measurements/probes/la_oracle.py` ->
`../backrefs_measurements/probes/br_oracle.py` ->
`../eng_brep_measurements/probes/pcre2_ctypes.py` (three levels, no second
binding).

No instrument here reads a subroutine call through pcrec (pcrec cannot compile
one); in-pcrec arms measure a SEPARATE AXIS (refusals and the 26 registry
rows, the give-up code space and `ERR_FLOOR` sites, emitted primitives quoted
from `src/`, and inlined EQUIVALENTS of call-bearing patterns verified against
libpcre2 before any timing). The design marks each claim MEASURED /
STRUCTURAL / PROTOTYPE / ARGUED.

## Standing rules

- Every PCRE2 behaviour claim is PROBED, never recalled; every sweep carries a
  REACHABILITY guard that prints VACUOUS and fails when it cannot reach its
  population (ten instrument defects were found this way; see `out/CLAUDE.md`).
- `probes/archive.sh` is the ONLY writer of `out/`.
- Adopted critic prototypes (`prototype/slotproto_*.c`, the R34 C2 panel's)
  are kept UNCHANGED (only the header block is this lane's); the probe
  REBUILDS them from source. A lane that rewrites the instrument that refuted
  it cannot be trusted not to soften it.
- Probe PCRE2 recursion cells on subjects that clear the compile-time
  START-OPTIMIZE pass (too-short or required-byte-missing subjects measure the
  wrong mechanism; `PCRE2_NO_START_OPTIMIZE` is the diagnostic).
- Fetch any PCRE2 source tarball into the scratch dir, never into this tree.
- A design section that can be executed should be, by someone who did not
  write it.
- `probes/check_selfconsistency.py` must exit NONZERO on any miss
  (archive freshness; every `S-SR` id in §9.3 in a §11 bar's DETECTED list;
  every `*.rxt` in §10.2 in a §11 bar) and was validated in the failing
  direction (7 sabotages); a check keyed on id ANYWHERE in a section passes on
  prose ABOUT the id.
- Maintenance: update this file when probes or outputs are added/removed or
  their roles change.

## Files

- `probes/sr_oracle.py` -- oracle helper: `match_limits()` (RAW rc as a cell),
  `callout_trace()` (live ovector via `pcre2_set_callout`), `depth_of()`;
  behavioural `SELFCHECK` at import.
- `probes/probe_premises.sh` -- §1 against `build/pcrec` and `src/` (seven axes).
- `probes/probe_spellings.py` -- §2 call/reference spellings.
- `probes/probe_captures.py` -- §3.1/§3.4 capture state via callouts.
- `probes/probe_atomicity.py` -- §3.2 backtrackable-call evidence and retry cost.
- `probes/probe_leftrec.py` -- §3.3 left recursion, `rc -52` sweep, error 140.
- `probes/probe_recurse_loop.py` -- K34 / [DD-14.K34]: the `OP_RECURSE` loop
  guard rule read from 10.46 source; 65/65 cells.
- `probes/probe_linkage.sh` + `prototype/gen_linkage.py` -- §6 PROTOTYPE:
  SPLICE / HYBRID / CALL linkages (52-cell agreement control first).
- `probes/probe_slotfamilies.py` + `prototype/slotproto_pending.c` +
  `prototype/slotproto_cutmark.c` -- §5.3b PROTOTYPES (R34 C2 panel's).
- `probes/probe_callproto.py` + `prototype/callproto.c` -- §5.9 PROTOTYPE of
  §5's lowering, also built `-DBROKEN_ARRAY` (the rejected `call_stack[]`).
- `probes/probe_prefilter.py` -- §8.3 prefilter value on INLINED equivalents.
- `probes/probe_call_prefilter_hazard.py` -- [DD-14 wave G]: H1/H2/H3 over the
  call population, INLINE vs ERASE (ERASE is the positive control; run FAILS if
  it violates nothing).
- `probes/probe_population.py` -- §8.4 census of `tests/**/*.rxt` patterns.
- `probes/check_selfconsistency.py` -- reads the DESIGN (see rules).
- `probes/archive.sh` -- sole writer of `out/`.
- `email_specimen/` -- RFC 5322 email pattern original vs `{0}`-idiom factored
  (+ `factored_define.rx`, derived by script); README sets wave G's bar;
  `tests/recursion/run_specimen_identity.sh` runs it; `throughput/` and
  `subjects/` are gitignored regenerable filler.
- `out/` -- archived output (own CLAUDE.md).

## Pointers

`../subroutines_design.md` (§1-§11), `../sr_d27_extract.md`,
`../lookaround_measurements/`, `docs/dev/known_issues.md` K34,
`docs/dev/reviews/` (R34), `tests/recursion/`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__subroutines_measurements.md
