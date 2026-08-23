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
- `probes/probe_d66_subset.py` — §5.5/§6.5/§9.2, the equivalences, the `(?m)^`
  self-oracle and the ceiling-coexistence sweep.
- `probes/probe_expansions.py` — §6.1/§6.2, the [DD-11]/D66 assertion-family
  EXPANSIONS: equivalence in libpcre2 (972 cells, 0 disagreements, with the
  `(?!\z)`-dropped vacuity control firing at 4/108), each body classified
  against the design's §2.5 width rule, python's verdict per expansion, and
  pcrec's SHIPPED FOLDED forms against libpcre2's EXPANSIONS (0 over 324
  cells) — the D66 self-oracle run on the table itself.
- `probes/probe_substitution_population.py` — §6.3, **PURE TEXT**: how much of
  `tests/assertions/` the substitution driver qualifies. Runs no compiler and
  no matcher, because the question is a property of the corpus text and
  answering it by running the driver would require the driver to exist.
- `probes/probe_englook_sizing.py` — §5.8, `[ENG-LOOK]`'s sizing inputs. Reads
  the EMITTER'S OWN ARRAY DIMENSIONS out of the emitted C
  (`len(rx_forward_is_accepting[])` for states, `next_state/states` for
  classes) after compiling each BODY ALONE — pcrec's unanchored forward DFA
  for `L` IS the `Σ*·L` recognizer a lookbehind needs, and its reverse machine
  is the `reverse(L)·Σ*` a lookahead needs, so no model sits in between.
- `probes/archive.sh` — the ONLY writer of `out/`.
- `out/` — archived output; see its own CLAUDE.md, which carries the NINE
  instrument defects this lane found by running its own probes.
