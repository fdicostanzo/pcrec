# docs/design/poss_arms_measurements — [ART-POSS-ARMS]'s probes and evidence

This directory is the evidence for `../poss_arms.md` (lane `possarms`,
2026-10-07). Nothing here is built or run by `make`.

The scratch prototype these numbers come from is a census instrument, NOT the
implementation. It is committed as a patch only so the counts can be
reproduced.

## Files

- **`eqcheck.py`**: the oracle-only equivalence checker. Each input row pairs
  a greedy pattern with its possessive spelling. Both are run through
  `pcre2test` over one subject sweep, and every subject whose span, captures
  or after-text differs is counted. It never runs pcrec.
  - The greedy side carries `no_auto_possess`, so PCRE2's own
    auto-possessification cannot hide a difference.
  - The subject sweep is every string of length ≤ `ML` plus `NR` random ones.
  - `PCRE2TEST` overrides the binary.
- **`gen_a.py`**: arm A's family (bodies × quantifiers × follows × wrappers ×
  modes). It prints TSV rows for `eqcheck.py`. The CLAIM column is the note's
  §2.3 predicate, computed from class membership asked of libpcre2 itself
  (`^(?:C)$` per character per mode), never from pcrec.
- **`gen_b.py`**: arm B's family. It prints a cross product plus hand cells.
  The CLAIM column is §3.1's rule. A `|naive-...` suffix names a narrower
  rule that would claim the cell, so each such cell is a refutation witness.
- **`armA_sweep.out.gz`, `armA_sweep.summary`**: 22,680 pairs at `ML=2 NR=150`.
- **`armA_claims_deep.out.gz`, `armA_claims_deep.summary`**: the 3,294
  claimed pairs at `ML=3 NR=300`. 0 diverge.
- **`armB_sweep.out`, `armB_sweep.summary`**: 660 pairs at `ML=5 NR=300`.
- **`real_gates.tsv`**: the lookaround-born gate cases (A0), including lazy
  and `m=0` rows.
- **`witnesses.pcre2test`, `witnesses_10.46.out`**: every witness the note
  cites, as pcre2test input and the transcript from libpcre2 **10.46** on
  ubuntubudu (one light ssh session). This includes §1's call-target
  miscompile cells and the `(?R)` auto-possess cell.
- **`proto_census_instrument.patch`**: a diff of the scratch prototype of
  both arms against `src/opt/possessify.c` at bcb7b128.
  - Environment-switched: `PROTO_ARM_A`, `PROTO_ARM_B`, plus three
    sabotage switches (`PROTO_SAB_M0`, `PROTO_SAB_NOFOLD`,
    `PROTO_SAB_FIRSTMEM`) used for the reach test in §8.
  - It uses a file-static and `getenv`. NOT house code, NOT for merge.
- **`poss_census.py`, `census.tsv.gz`, `census_firing.tsv`**: the K35
  census.
  - It imports `../../dev/optloop/artrev/gen/census.py`'s population
    loaders. Run it with `python3 -B` so no `__pycache__` lands in the tree.
  - It compares possessify marks and emitted push sites per pattern under
    no arm, A, B and A+B.
- **`possdiff_armpats.txt`, `possdiff_sabpats.txt`, `possdiff_runs.txt`**:
  `tests/possessify/run_possdiff.sh` runs through a `--features all` shim
  with the prototype armed. The runs file records the designed family, the
  real firing set, and the three sabotage plants (S563's fold plant is
  MISSED).
- **`minwb.sh`, `workbudget.tsv`**: the minimum `--work-budget` bisection
  behind §6. These are deterministic counts, not timings.
