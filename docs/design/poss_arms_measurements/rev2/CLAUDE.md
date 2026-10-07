# docs/design/poss_arms_measurements/rev2 — [ART-POSS-ARMS] revision 2's evidence

This is the evidence for `../../poss_arms.md` REVISION 2 (lane `possarms2`,
2026-10-07, from main `c2a0c6df`). It discharges the D6 panel's dispositions
(`../../../dev/reviews/2026-10-07-r-poss-arms-panel.md`). Nothing here is
built or run by `make`.

**The prototype is a measurement instrument, NOT the implementation.** It
uses file statics and `getenv`. It is committed as a patch only so the counts
can be reproduced.

## Reproducing

Copy the tree into a scratch directory, `patch -p1 < proto_rev2.patch`, and
build it (`make CC=gcc-16`). Point `PROTO` at that `build/pcrec`. Run
everything with `TMPDIR` set to a scratch directory. The libpcre2 sweeps use
the local `pcre2test` (10.48), and every witness they cite was confirmed on
10.46 by revision 1 (`../witnesses_10.46.out`).

## Files

**The prototype**

- **`proto_rev2.patch`**: both arms against post-K93 `src/opt/possessify.c`,
  env-switched:
  - `PROTO_ARM_A`, `PROTO_ARM_B`;
  - `PROTO_A0_ONLY` / `PROTO_A1_ONLY`, which split arm A's two rows;
  - `PROTO_A0_NULLABLE`: revision 1's prose nullability, for A-F4's delta;
  - `PROTO_A1_NOCC`: A-F1's plant, which drops the call-site join from A1's
    continuation;
  - the sabotage switches, each named in the note's §8.2: `PROTO_SAB_M0`,
    `_FIRSTPOL`, `_MIXED`, `_NOFOLD`, `_FIRSTMEM`, `_NONNULL`,
    `_NORECGUARD`, `_LAZY`, `_NOWIDEN`.

  A1's continuation is a chain with a marker at each `A_CAP` end. At a
  marker, and at the root end, the fold unions the join `cc[g]` (fix (a)).

**The census (K35, C-1, B-M4)**

- **`r2_census.py`**: the census. It uses [ARTREV]'s population loaders
  (`../../../dev/optloop/artrev/gen/census.py`; run with `python3 -B`). It
  records marks under eight arm configurations, the default-route engine
  and `RX_ENGINE_WHY` under BOTH the denied and the armed builds, push sites
  and `RX_VM_FRAMELESS`, and the refusal reason.
- **`census_r2.tsv.gz`**: its output. 4,132 patterns: 345 bench and 3,787
  corpus.
- **`census_r2_refused.tsv`**: the 393 patterns the base `--engine=vm`
  compile refuses, with the reason.
- **`routeflip_witness.sh`, `routeflip_witness.out`**: the six constructed
  route-flip witnesses, default route and `--engine=dfa`, armed and denied.

**The oracle sweeps (B-B3, B-M4)**

These are libpcre2 only, through `../eqcheck.py`.

- **`gen_a2.py`**: arm A's family, revision 2. It adds:
  - the mixed-LAST body;
  - `\B` modelled as a gate;
  - column 7 `abl`, the ablation tags;
  - column 8 `hi`, set when FIRST(X) has a member above U+00FF;
  - the `H` rows, ENCL's control.
- **`gen_b2.py`**: arm B's family, revision 2. It adds the `abl` column, the
  `\b`-behind-an-empty-reference modelling, the depth-1 rows and the `C`
  rows (arm × call).
- **`gen_a0.py`**: the A0 family sweep: lookaround-born gates in every
  position the panel named.
- **`a2_claim_ml4.out`**: the 3,294 revision-1 claims, swept at ML=4.
- **`a2_abl_ml4.out.gz`**: the ablation-tagged rows, swept at ML=4.
- **`a2_new_ml4.out`**: revision 2's new claimed and tagged rows, swept at
  ML=4.
- **`b2_ml5.out`**: all of `gen_b2.py`, swept at ML=5.
- **`a0_ml4.out.gz`**: all of `gen_a0.py`, swept at ML=4.

**CLAIM-vs-MARK (B-B2)**

- **`r2_claimmark.py`**: the check. It compares the Python claim (column 5,
  restricted by `hi`) with the prototype's mark for every claimed row,
  every tagged row, and a 1-in-10 sample of the rest. It runs under the
  arms and under each plant.
- **`claimmark.out`**: the result, after the predicate fixes.
- **`claimmark_v1.out.gz`**: the first run, BEFORE the predicate fixes. This is
  the run that found the two predicate gaps and the two over-wide hand
  claims (note §8.3). It is kept because it is what made the check worth
  having.

**The exhaustive possdiff (B-B1, B-M5)**

- **`subjects_exh.py`**: the exhaustive subject generator, with
  `--alpha` / `--reach`.
- **`possdiff_exh.sh`**: `possdiff_driver.c` with exhaustive subjects, a
  `# flags:` header and a REACH file.
- **`possdiff_plants.sh`**: the battery. It runs the arms, then each plant,
  then the route-flip witnesses on the default route.
- **`pd_arms.txt`, `pd_utf8.txt`, `pd_utf8i.txt`, `pd_ucp.txt`,
  `pd_i.txt`**: its population.
- **`pd_reach.tsv`**: the (pattern, witness) pairs that must be in the
  sweep.
- **`pdx_verdicts.txt`, `pdx/*.log`**: one tally line per run, and the
  per-pattern logs.

**The work budget (B-M3)**

- **`wb_subject.py`**: the committed subject generator. It is
  deterministic: 200 words is 809 B, sha1 `bc1608f6…`.
- **`minwb2.sh`**: the minimum-work-budget bisector. It fails loudly on a
  compile error or an unrecognised outcome.
- **`wb_runs.tsv`**: one subject, seven builds.

## Instrument defects found while measuring (recorded so they are not repeated)

1. **The first `minwb2.sh` could not fail.**
   - Its "fail loudly" `exit 2` ran inside a `$(...)`, which exits only the
     subshell.
   - Its extra-flags `"$@"` was the function's own arguments, so every
     compile was refused.
   - The bisection then read the refusals as answers and reported a
     confident minimum of 1.
   - Fixed: outcomes go through a file, and the flags are an array.
2. **An `arm × call` witness the alphabet could not spell.**
   `(a?)(x+\1)y(?2)x` needs `y`, which neither `gen_b2.py`'s alphabet nor the
   first REACH entry (`xxyxx`, length 5 > ML 4) had. The sweep said 0
   diverging. The witness became `(a?)(x+\1)b(?2)x` on `xbxx`. The REACH
   check is what caught it, which is that check's purpose.
3. **CLAIM-vs-MARK's first run disagreed on 25 rows** (`claimmark_v1.out.gz`).
   Every disagreement was in the INDEPENDENT predicate, not in pcrec (note
   §8.3). A check that agreed on its first run would have hidden that.
