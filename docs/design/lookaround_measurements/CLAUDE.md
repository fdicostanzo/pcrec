# docs/design/lookaround_measurements — the [M6.6.1] lane's instruments

Probes and archived output for `../lookaround_design.md`, the module
`lookaround` design gate. Same shape as `../backrefs_measurements/` and
`../atomic_groups_measurements/`, and it borrows rather than copies: the
oracle helper `probes/la_oracle.py` loads `../backrefs_measurements/probes/
br_oracle.py`, which loads `../eng_brep_measurements/probes/pcre2_ctypes.py`.
Two levels of borrowing, no second binding — a lane that re-implements the
binding it is checking cannot detect that the original moved.

**NO INSTRUMENT HERE READS A LOOKAROUND THROUGH pcrec, because pcrec cannot
compile one.** Every in-pcrec arm therefore measures a SEPARATE AXIS on
patterns pcrec CAN compile — the refusals and registry rows themselves (§1),
the ERASURE that would become the prefilter (§5), the assertions module's
already-shipped `\b` and `(?m)^` artifacts (§6) — which is what makes those
arms exact rather than modelled. The design marks each claim MEASURED /
STRUCTURAL / ARGUED accordingly.

## Files

- `probes/la_oracle.py` — the lane's oracle helper. Re-exports br_oracle's
  surface and adds three things no earlier lane needed: the
  `max_varlookbehind` compile-context setter (PCRE2 >= 10.43, without which
  the length rule cannot be measured at all), `PCRE2_INFO_MAXLOOKBEHIND` and
  `PCRE2_INFO_CAPTURECOUNT` (both indices DERIVED BY SWEEP — see `out/`'s
  defect list), and a python `re` arm in the same vocabulary and the same
  padded shape, so the two oracles sit in one row. `SELFCHECK` is behavioural
  and runs at import.
- `probes/probe_premises.sh` — §1, against this worktree's `build/pcrec`.
- `probes/probe_spellings.py` — §2 axis A.
- `probes/probe_lookbehind_length.py` — §2 axis B, the length rule.
- `probes/probe_captures.py` — §2 axis C, the capture and budget cells.
- `probes/probe_prefilter_hazard.py` — §5, H1/H2/H3 with its own `erase()`
  (fixture-tested at import) and two vacuity guards.
- `probes/probe_d66_subset.py` — §5/§6, the positive control, the `(?m)^`
  self-oracle and the ceiling-coexistence sweep.
- `probes/archive.sh` — the ONLY writer of `out/`.
- `out/` — archived output; see its own CLAUDE.md, which carries the SEVEN
  instrument defects this lane found by running its own probes.
