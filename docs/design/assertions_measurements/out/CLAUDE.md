# docs/design/assertions_measurements/out — archived probe output

Verbatim output of `../probes/`. **Every file here is written by
`../probes/archive.sh`**, so the provenance header cannot drift between them:
probe path and args, the commit the probe was last changed at, the commit and
branch the run was made from, whether the working tree was clean at run time,
the date, and the python3, libpcre2 and gcc versions. Same intent as
`scripts/measure.sh` / `docs/measurements/` (D35), scoped to this lane.

**Evidence for the [M6.1] panel, never an oracle.** No check in `make test`
reads anything here; re-run the probe to re-measure.

## Files

- `ncls_refine_realistic.txt` — `probe_ncls_refine.py` over the 40-pattern
  realistic set. Headline: the word-set alphabet refinement costs at most **+1**
  equivalence class (n = 38 measured, 2 skipped).
- `ncls_refine_rxt.txt` — the same probe over 574 of the 609 patterns harvested
  from the `.rxt` corpus (the adversarial denominator). Headline: word at most
  **+2**, newline at most **+1**, both at most **+3**; largest
  `states × ncls` after both refinements **48,012** against
  `PCREC_MAX_TABLE_ENTRIES` = 2,000,000.
- `wordctx_states_realistic.txt` — `probe_wordctx_states.py` with
  `--calibrate`. Headline: minimised state ratio for `\bPAT\b` vs `PAT` is
  **1.00x / 1.11x / 4.75x** (min/median/max, n = 35); the prototype reproduces
  pcrec's own state count on **29 of 33** assertion-free arms and the four
  disagreements are listed, in both directions.
- `acc_by_class.txt` — `probe_acc_by_class.sh`. Headline: the `states × ncls`
  accept table a next-byte-sensitive assertion forces is **not slower** —
  197.5/197.3/197.3 MB/s against 202.5/202.4/202.4, identical `matches=54424`
  both arms (the variant is answer-preserving by construction, which is what
  makes the timing attributable to the lookup).
- `d475_scope.txt` — `probe_d475_scope.py`. Headline: **2 of 5 cells
  MISCOMPILE** under the shipped D47.5 gate design — `(?m:[^c]{1,3}$)` and
  `(?m)[^c]{1,3}$(?-m)` on `"a\nc"` are `(0,1)` correct and **no match**
  possessified. Two of the five cells are libpcre2-only: python3 `re` rejects
  a bare `(?-m)` and rejects a trailing `(?m)`.
- `z_oracle.txt` — `probe_z_oracle.py`. Headline: **1 of 7 cells disagree**
  between libpcre2 and python3 `re`, and it is a `\Z` cell — python's `\Z` is
  PCRE2's `\z`, so python is the wrong oracle for `\Z`.
- `dollar_multiline_rerun.txt` — the re-run of
  `../../eng_brep_measurements/probes/probe_dollar_multiline_pcre2.py`.
  Headline: on the greedy population the exemption covers, **0 of 168**
  diverging with multiline off and **12 of 168** with it on, both oracles
  agreeing — the qualitative result `eng_brep_design.md` §2.5 states, at
  different absolute numbers than it cites (see `../../assertions_design.md`
  §8.4).

Maintenance: update this file when outputs are added/removed.
