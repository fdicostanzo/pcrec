# docs/design/poss_arms_measurements/rev21 — [ART-POSS-ARMS] revision 2.1's evidence

This is the evidence for `../../poss_arms.md` REVISION 2.1 (lane `possarms21`,
2026-10-07, from main `abb3db6c`). It discharges the re-check of revision 2
(`../../../dev/reviews/2026-10-07-r-poss-arms-panel.md`, "Re-check of rev 2":
N1, N2, R-3(b), R-4..R-8). Nothing here is built or run by `make`.

**The prototype is a measurement instrument, NOT the implementation.** It
reads its configuration from `getenv` into one file static. Every
per-compile fact (arm B's capture table, A1's continuation summaries) lives
on `Ctx`/`Pss`/the continuation nodes.

## Reproducing

1. Copy main into a scratch directory.
2. Run `patch -p1 < proto_rev21.patch` and `make CC=gcc-16`.
3. Set `TMPDIR` to a scratch directory.
4. Run `run_all.sh` with `PROTO` (that build), `PROTO2` (a build of
   `../rev2/proto_rev2.patch`, for the rev 2 → 2.1 delta) and `OUT`.

The libpcre2 sweeps use the local `pcre2test` (10.48). Every witness the note
cites was confirmed on 10.46 (`witnesses_r21_10.46.out`, and rev 1/rev 2's
transcripts).

## Files

**The prototype**

- **`proto_rev21.patch`**: against main `abb3db6c`'s `src/opt/possessify.c`
  and `src/core/internal.h`. `internal.h` gains one `Ctx` field, the capture
  table's pointer for the duration of one walk. Over rev 2's patch:
  - N1's `text_first`: a zero-width kind is (∅, nullable);
  - R-4's capture fact: an index by group number, memoized, where in
    progress means widen;
  - R-4's A1 half: the Q-independent continuation summary (`PSum`/`PGate`,
    `ps_chain`/`ps_eval`);
  - R-5's check (`PROTO_CHECK_FOLLOW=1` prints `R5\t<bytes>\t<end>` per
    verdict and `R4SUM-MISMATCH` if the summary and the fold disagree);
  - the atomic-body end sentinel.

  Switches added over rev 2: `PROTO_SAB_TEXTPOS` (the N1 plant: arm B reads
  `first_of`, the rev-2 behaviour) and `PROTO_NOMEMO` (both memos off, for the
  before/after timing). `PROTO_SAB_NORECGUARD` now means that an in-progress
  group is recomputed.

**The frozen predicates (R-3(b): their sha1s are recorded in the note's
§8.3a; an edit after the freeze is a rule-level event, see there)**

- **`gen_a21.py`**: arm A's family, plus:
  - the bypass follows `(?:\b|)` / `(?:\B|)`;
  - the bounded lazy quantifiers `{1,3}?` / `{2,}?`;
  - the R block (a follow inside a REFERENCED group, valued by its text);
  - N2's hand rows;
  - column 9 `src`.
- **`gen_a021.py`**: the A0 family, plus:
  - the bypass follows `(?:(?=C)|)` / `(?:(?!C)|)` (with the wrapper's
    may_end modelled);
  - `{2,4}?`;
  - the R block (a lookahead gate inside a referenced group; tag `textpos`).
- **`gen_b21.py`**: arm B's family, plus:
  - N1's gate-inside-group GROUPS, each with its TEXT and POSITION models;
  - the tails `(?:\b|)`, `(?=x)`, `(?:(?=x)|)`;
  - `x{1,3}?`;
  - N1's three hand witnesses;
  - the tags `textpos` and `lazy`.

  The depth-2 row is now a claim (R-4).

**The checks**

- **`r21_claimmark.py`**: CLAIM-vs-MARK. It reads per-quantifier marks from
  `--emit-ir`'s strategies section (R-7):
  - rows are keyed by ordinal;
  - the target is found by the base build on the possessive spelling;
  - `extra` and `anomaly` are counted.

  It runs ten configurations, reports `computed` and `hand` rows separately,
  and pins `UCP_PIN`.
- **`r21_census.py`**: the census re-run. It records base / AB (rev 2.1) /
  AB (rev 2) marks, the R-5/R4SUM outcome counts and the default-route
  engine.
- **`subjects_exh.py`, `possdiff_exh.sh`, `possdiff_plants.sh`,
  `pd_*.txt`, `pd_reach.tsv`**: rev 2's exhaustive possdiff, carried over.
  The population gains rev 2.1's rows, REACH gains N1/N2's witnesses, and the
  plants gain `SAB_TEXTPOS`. `SAB_LAZY` is now a row.
- **`run_all.sh`**: the whole battery in order, writing `$OUT/STAGES`.
- **`run_composition.sh`**: R-3(a)'s hook for the blinded corpus (note
  §8.8).
- **`witnesses_r21.pcre2test`, `witnesses_r21_10.46.out`**: rev 2.1's
  witnesses, greedy against possessive, on libpcre2 **10.46** (ubuntubudu,
  one light ssh session).

**Results** (written by `run_all.sh`; see the note for the read)

- `results/`: the eqcheck outputs, `claimmark.out`, `census_r21.tsv`,
  `pdx_verdicts.txt` and `pdx/`, `timing.out` (R-4) and `STAGES`.
