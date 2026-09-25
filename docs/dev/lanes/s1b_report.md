# Lane `s1b` — `[OPT-LITSCAN]` S1 revision 2 (option B), report

2026-09-25, opus, design only. Branch `lane/s1b` from main `4976f385`.
Charter: D122 ADDENDUM 4 ("make sure such a change is well-considered and
critiqued — it's close to the vital organs"). Deliverable:
`docs/design/litscan_s1.md` revision 2. A FULL D6 panel reviews it next.

## Summary (a fresh agent resumes from here)

- **Placement.** `prefix_k.c` publishes one fact: `PrefixKSets.run_pinned`
  / `run_o`, the smallest `o` at which the walk's singletons spell
  `Job.req_run`. It is computed before the `k0`-dependent early return, and
  it is a `bool` so that memset-safe zero means "not pinned".
- **Decision.** ONE row pair at the head of `dfa_pfs[]`:
  - rows `run-pinned-bounded` / `run-pinned`;
  - deny `PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER` (bit 32);
  - `reseeds = true`;
  - they emit `pf_tables_ofs` / `pf_block_ofs` / `pf_emit_ofs[_bounded]`;
  - predicate clauses 0-4 (§1.2).
- **One new derivation.** `OfsTest` is what the ofsskip block tests. The
  `offset-set` rows are routed through it first, at zero moves. It is read
  by the block, the verify chain, the params, the tables, the comment, the
  OFFSETS stamp and G1.
- **Program.** The emitted program is identical to revision 1's. The
  stamps are new: `RX_DFA_PREFILTER` has 9 values.
- **Census** (`docs/dev/optloop/s1/census_b*.{tsv,txt}`). The predicate
  selects exactly B ∪ B-bounded ∪ C1 (27 bench per config, 186 corpus at
  `b5c1423b`) and nothing else. Program changes are 34 bench / 513 corpus:
  the same totals, with two explained compensating corrections (+5
  B-bounded, −5 A2). The census at `4976f385` is byte-identical (§6.3).
- **Found:**
  1. The 32-bit deny plumbing (`DfaCand.deny`, `dfa_select`,
     `dfa_form_derive`'s local, `PcrecAxisCand`, `axes_dump.c`). Bit 32
     would silently not deny. Widening it is S1's first commit.
  2. The new stamp values ripple through
     `run_dfa_stamps.sh`'s text re-derivation, the form census,
     `run_offset_skip.sh`, `--list-axes` and the bench's bucketing.
  3. Revision 1's census over-counted A by 5 (G1's `p == q`), and
     mis-described C0.
  4. S1-4's `prefix_k.c` comment edit is no longer needed.
  5. Sabotage (g) has a measured answer-detectable witness,
     `/abcd[xy]/user`.
  6. Row (j)'s only natural reach candidate is bench
     `wild-secrets-github-pat`.
- **Open for the panel, then Frank:**
  - N1: the two-bit deny;
  - N2: including B-bounded;
  - N3: row (j)'s witness.

## Validation

Design-only lane: no `src/` change, no `make test`. Instruments were run on
scratch `git archive` builds (`build/s1b/`, gitignored):
- `census_b.py` over a `probe_b_patch.py` build of `b5c1423b` (its own
  corpus), and of `4976f385` (its own corpus);
- light probe compiles of the existing test witnesses and of the sabotage
  witnesses.

Not re-run, with the reason: `twin_counts.txt` and `router_c_identity.sh`.
The counted program is unchanged (R2), so their numbers carry over.
