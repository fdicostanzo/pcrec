# docs/design/atomic_groups_measurements -- the [M6.4.1] design lane's instruments

The measurements behind `../atomic_groups_design.md` (module `atomic-groups`:
`(?>...)` and possessive spellings `*+ ++ ?+ {n,m}+`).

Every instrument here reads a compiler that CANNOT compile the construct it
measures, so every in-pcrec arm works through a PROXY: the atomicity-ERASED
twin (`(?>` -> `(?:`, the machine `src/ir/nfa.c` will build for the
prefilter) and the possessify verdict stamp (`RX_VM_STRATS` bit 0x1). Check
each entry's own tier (MEASURED / PROTOTYPE / STRUCTURAL); the directory has
none. Kept separate from `../assertions_measurements/`,
`../eng_brep_measurements/` and siblings: never confuse one lane's numbers
with another's.

## Standing rules

- An instrument can produce a correct number about the wrong population;
  every probe needs a failing-direction control and a non-vacuity/floor check
  that FAILS the run when the population cannot reach it (a zero from an
  instrument that cannot fire is worth nothing).
- Probes resolve `pcrec` from their OWN location, not the caller's cwd
  (`$PCREC` / `$1` override); a bare relative `build/pcrec` is a defect.
- R30 M7 inherited: `probes/archive.sh` is the ONLY writer of `out/`; a hand
  edit there is a red line. `archive.sh` stamps the RUN DIRECTORY.
- A corrected instrument does not correct the document that quoted it:
  re-check the design prose after fixing a probe (R31 D1/C7).
- Evidence, never an oracle: no `make test` check reads `out/`.
- Do not copy `pcre2_ctypes.py`; import
  `../../eng_brep_measurements/probes/pcre2_ctypes.py` by path (one binding).
- The `-Wswitch` question for a new `AKind`/`RegKind` is answered by
  RE-RUNNING `../assertions_measurements/probes/probe_wswitch_alarm.sh`
  (output archived as `out/wswitch_alarm_rerun.txt`), not a second instrument.
- Beware `set -e` foot-guns (assignment from a failing command; `|| true`
  swallowing a measured exit code); instruments that restore state (e.g.
  `probe_rk_alarm.sh`) restore under an EXIT trap that VERIFIES the restore
  and refuse to report zero when they compiled nothing.
- Maintenance: update this file when probes or outputs are added/removed or
  their roles change.

## Files

- `probes/probe_atomic_semantics.py` -- MEASURED, both oracles (libpcre2
  10.46 vs python3): the design's §6 interaction table, `spelling_equivalence()`.
- `probes/probe_uncut_superset.py` -- MEASURED sweep: the §4 hybrid hazard
  (rejection and START hold; END refuted); builds the uncut twin by text
  substitution; excludes possessive suffix spellings (U9).
- `probes/probe_ceiling_shape.sh` -- STRUCTURAL: `window[0][1]` fed to the VM
  as a pruning ceiling; negative arms `-fno-prefilter` and `--engine=vm`.
- `probes/cut_proto.c` + `probes/probe_cut_trail.py` -- PROTOTYPE vs libpcre2;
  builds both `-DCUT_REWINDS_TRAIL` arms and fails if either column is zero.
- `probes/probe_free_discharge.py` -- MEASURED: free discharge (§5.3), four
  controls printed every run.
- `probes/probe_possessify_under_cut.py` -- MEASURED: possessify §2.2 verdict
  soundness under cuts, four quantifier positions.
- `probes/probe_puc_targeted.py` -- MEASURED: successor of the above with
  per-position FLOORS and an ASSERTION for the empty position.
- `probes/probe_premises.sh` -- MEASURED: design §1 premise and §6.3
  error-shape tables as one re-runnable script.
- `probes/probe_cut_dispatch.sh` -- MEASURED: which emitted code cuts across
  `vm_rep`'s FIVE dispatch paths; §2b sweeps the revdet-approved /
  possessify-rejected exact-count cell.
- `probes/probe_lift_preference.py` -- MEASURED: lazy quantifiers vs the
  possessive-rung lift (control `(?>a*?b)c`).
- `probes/probe_sref_consistency.sh` -- document-internal: prints EVERY `SNN`
  citation beside the §11.4 row description (aptness is a human judgement).
- `probes/probe_registry_cost.sh` -- MEASURED SWEEP of `src/`, `cli/`, `tests/`
  (no curated list) for what a new registry row costs; classifies EXACT /
  FLOOR / kind lists / routing assertions.
- `probes/probe_rk_alarm.sh` -- MEASURED, self-restoring: a fifth `RegKind`'s
  `-Wswitch` cost (0 diagnostics).
- `probes/archive.sh` -- the ARCHIVER (sole writer of `out/`).
- `out/` -- archived probe output (provenance header: probe, last-change
  commit, run commit/branch/tree-clean, date, python3/libpcre2/gcc); see
  `out/CLAUDE.md`.

## Pointers

`../atomic_groups_design.md`, `../assertions_measurements/`,
`../eng_brep_measurements/probes/pcre2_ctypes.py`,
`docs/dev/reviews/2026-08-22-r31-atomic-groups-design.md`, D67, U9 in
`docs/dev/upstream_issues.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__atomic_groups_measurements.md
