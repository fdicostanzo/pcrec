# bsu5fix report: review r79's fixes to R-47 U5 (card C6/C6c, kit-grid@8, formhash)

Lane bsu5fix (opus), branch `lane/bsu5fix` cut from `lane/bsu5`; review
`docs/dev/reviews/2026-11-22-r79-memfn-bsu5.md` (kit branch), its MANAGER
RULING: FIX FIRST. Nothing was timed.

## STATE AT HANDOFF

- Commits on `lane/bsu5fix` over `lane/bsu5`: `1b3eafd08` (F1, F16, F17,
  F18: the formhash fold), `ac807e97a` (the rest: rule file, pools, layer
  table, C6c gcc -Os, reach build, verdict drills, design hunks), and the
  commit that carries this report (it also records the rule sha in §8).
- All fixes are DONE. In-lane checks are green (IN-LANE RUNS). The identity
  sample is 356 of 356 byte-identical against base `b51fd80bd`.
- OWED: two box-queue jobs, `746-kit-bsu5fix-test` (make test) and
  `747-kit-bsu5fix-mech` (S2930, S2931, S2933, after the test). C6 and C6c
  TIMING is owed to a window main clears (U6), on each bench box that runs
  V.
- The rulings file `bsu5fix_rulings.md` was empty at every checkpoint.
- Readings made, for the manager:
  - **F4.** `c6_hexb32`'s near-miss-in now calls the span (20,695 calls).
    Its plain near-miss still calls it 0 times, as at every window site
    with k <= 32 (c6_hex17/32/33 read 0 too; the probe lands on each
    record's miss byte). It is N/A by construction and named as a cut in
    the rule.
  - **F13.** At gcc -Os, gcc's alignment-OFF variant builds the default
    layout again, so the dry refused all 9 -Os pools. The layer table
    therefore gained a fourth column, the ALIGNMENT ROW. Its -Os row is
    `ALIGN_OS_ON` (16 B; at 32 B the pool proof still refused every -Os
    pool), an UNMEASURED DEFAULT listed in §12.
  - **kit-grid.tsv** is append-only, so its `ver 8` data row is unchanged.
    Only the `ver 8` header comment was rewritten (it was born in U5 and
    never measured).

## FIXES BY ID

- **F1** (dep blind to B=16 and SIMD-off): three `span-vector` instances,
  `b16` (k 31, x86-64-v3), `b32` (k 40, x86-64-v3) and `off` (k 31, no
  level). Commit 1b3eafd08, proof below.
- **F2** (A/A cannot fail or see the pool): H64.b draws its OWN salted pool
  (`POOL_SALT`). The rule's A/A clause makes a standing A/A non-TIE cell
  HARNESS, and a rate above AA_VOID_MAX 0.05, or no readable A/A, makes the
  (card, layer) on that box VOID. `c6_decide` computes and prints the rate.
  Commit ac807e97a, proof below.
- **F3** (compiler not a declared column; the missing `align_variants_of`):
  the `LAYER` table rows are (pcrec flags, compiler, level, alignment row),
  read through `layer_flags`, `layer_simd`, `cc_of`, `opt_of` and
  `align_variants_of`. The function now exists. ac807e97a.
- **F4** (hexb32 near-miss never reaches the span): `C6_MISS` uses a space
  as the miss byte (`z` is a word byte, which made the left `\b` fail). The
  dry's reach build shows every C6/C6c cell's span calls. ac807e97a.
- **F5** (no VERDICT, WINDOW, RECORD, REPORTED or CLAIM): all are written in
  `memfn/tests/span_forms/c6_rule.md`, with 710's clauses each named.
  ac807e97a.
- **F6** (UNIT left to a later reader): UNIT is fixed in the rule (median of
  the launches; spread over the middle three of five). A floor above
  SPREAD_MAX 0.30 reads INCONCLUSIVE-NOISE. ac807e97a.
- **F7** (the re-time re-draws the same 4 layouts): the re-time builds a
  FRESH pool (`RETIME_SALT`, `pool_salt(arm, retime)`). ac807e97a.
- **F8** (nothing recorded or checkable): `rule_710.md` is committed (block
  sha `6351bff3901e3955`, computed from the file), and so is `c6_rule.md`.
  Its sha, from `git show` of the committed file, is
  **`9a2875a6bf089837`**. The RECORD clause fixes U6's `#c6` header (rule,
  rule710, form, binary, cc.<layer>, widths, run). `c6_header` and
  `c6_header_check` refuse a missing header or another rule's sha.
  ac807e97a.
- **F9** (full dry feeds C6 to C1-C5's `check_deny`): C6_CARDS are filtered
  out of it. Plan labels the C1-C5 pools and prints each C6 layer's compiler,
  level and alignment. ac807e97a.
- **F10** (`check_c6` tests presence only): `check_c6_texts` checks, on
  comment-stripped text:
  - V and H64 differ, and H64 carries no V text;
  - there is ONE selector, and the site calls it;
  - at a SIMD layer the selector calls a defined `__w32`, whose loop K is
    C6_SITE's k at B 32 iff k >= 32;
  - elsewhere the selector calls `__body` only;
  - the site kind matches C6_SITE.

  Six selftest plants go RED, and the control is clean. ac807e97a.
- **F11** (no design hunk): `block_span.md` gained:
  - §2.2.1 ANSWERED (D201 add. 5, verbatim), with a FREEZE NOTE row and the
    header, §2.1 and §15 mentions;
  - §8's C6c paragraph, the rule pointer and sha, and the instances;
  - §12's `CLANG_ALIGN_OFF`, `ALIGN_OS_ON`, SPREAD_MAX and AA_VOID_MAX rows;
  - §14's U5 row.

  ac807e97a plus the report commit.
- **F12** (DOC): both cuts are named, with reasons, in the rule's N/A clause,
  §8 and kit-grid's header: no near-miss-in at c6_hex1001 (shift cap 255),
  and near-miss at k <= 32 is N/A. No new cell was added.
- **F13**: the gcc -Os SIMD-off leg is layer `off-os`, a row of the layer
  table, and C6c is now `off-clang` plus `off-os`. clang -O3 and `-fPIC
  -shared` are DOC gaps, named in the rule's CLAIM, §8 and kit-grid.
  ac807e97a.
- **F14** (DOC): §8 says "it stales on the WHOLE window site's text" and
  that the scan driver (R7w) is not in it.
- **F15** (PLAN): named in §8 as a PLAN item, to be filed to main by the
  kit. `mf_form_hash`'s normalization is unchanged.
- **F16**: MF_FH_SPAN is folded into MF_FH_WINDOW with a per-entry `k`
  (pair is k 0) and `ppm`; one case and one shape test are deleted. Every
  other stored hash is unchanged, pair `b866902a13e46ba1` included. S2930 is
  re-aimed to the new row shape. 1b3eafd08.
- **F17**: the `fx --facts span-vector` row now says a hit is "k + 1
  consecutive bytes of `members`", and a `k` fact row was added (WINDOW
  only). Disposition of the second-shape-list part: the SPAN member is gone
  with the fold. `f_set_shape`/`f_find_shape` remain as predicates on
  formhash's own shape enum; there is no parallel list of shapes left to
  delete. 1b3eafd08.
- **F18**: `FORM_INSTANCE_FLOOR` goes 14 to 18 (18 instances).
  `CARD_FORMDEP_COUNT` stays 21. 1b3eafd08.

## HASH COVERAGE PROOF

Each plant is one renderer branch in `memfn/src/window.c`, built from the
working tree (scratch `tools/plant.py`, `plants2.py`; record
`scratch/bsu5fix/coverage_proof.txt`). Every other id's hash was unchanged
under every plant.

| plant | b16 | b32 | off | fold |
|---|---|---|---|---|
| none | e9b77e1aab76f279 | a9efa02907d0645b | e4c1992bf087cc90 | e62da1e2d786d8c5 |
| PV16b (`vs_w32_block`, B = 16 branch) | **a6277a8b0fefbea0** | same | same | 45893fd6538e289c |
| PV32b (B = 32 branch) | same | **39a9c54c4594026a** | same | 1f5037c99db4313e |
| POFF (no-top selector branch) | same | same | **88efbdec4ee5a71a** | d2b714bf02babf16 |
| PBODY (`__body`, all branches) | fa7cbf12c5f8fd70 | 21429f6c1f0ec18e | af329c14cc226acf | 24db898e1fe355c4 |

PV16b now moves a hash; before the fix it left `a9efa02907d0645b`
unchanged. `b32` equals the old single instance's hash. The fold gate held:
every non-span-vector FORM and FORMCLS line is identical to the base's.

## A/A PROOF

From `cards.py c6selftest RUNDIR`: 27 rows, 0 failed.
- **Constructed high-rate set:** 40 cells, 4 with a standing A/A non-TIE
  (rate 0.100 > 0.05). It reads `VOID (A/A FAILED: rate 0.100 > 0.050)`.
- **Below the threshold:** 1 of 40 (rate 0.025) makes that cell HARNESS,
  and the box reads NO LOSS.
- **Nothing readable:** no readable A/A reads `VOID (A/A UNREAD)`.
- **Other drills (all pass):**
  - RE-TIME (4 drills);
  - UNIT: bimodal reads NOISE; one outlier does not hide a 25 % LOSS;
  - N/A, WINDOW/TRUNCATED, RECORD accept/refuse;
  - the rule's sha and constants are parsed from the file;
  - the contrast: the old whole-range spread reads that 25 % LOSS as a TIE.
- **Own pool:** the dry's pool lines show H64.b's own variants. For example,
  `c6_hex32 on`: H64 has 64-B phases 16/36/32/52, H64.b has 32/52/48/4.
  The C6 dry went from 22 pools (88 exes) to 42 pools (168 exes), with 0
  refused.

## IDENTITY

U5's identity sample was re-run (`scratch/bsu5/ident.py`) with this tree's
`build/pcrec` against the base `b51fd80bd` binary:
- real 12/12, seed 164/164, corpus 180/180 byte-identical (`.c`, `.h`, rc,
  stdio);
- **TOTAL 356 pairs, 356 identical, 0 DIFFER.**

No emitted byte and no stamp moved.

## IN-LANE RUNS

All logs are under `/var/tmp/pcrec-pcrec/scratch/bsu5fix/`.
- **Build:** `make` rc 0.
- **`cards.py plan`:** rc 0. 1650 cells; C6 156, C6c 120.
- **`cards.py c6selftest dry1`:** 27 rows, 0 failed.
- **`cards.py dry dry1 --cards C6,C6c`:**
  - rc 0; 276 cells built and gated, 0 failures, 42 pools, 0 refused;
  - check_c6 0 failures on 14 (pattern, layer) pairs;
  - reach build: 92 cells, of which 8 are N/A, all near-miss at window
    k <= 32.
- **Full dry `--quick`** (under the box lock): see `dryfull.log`. Its result
  is in the final line of this section.
- **`make strict`:** rc 0. **`make test-memfn-arch`:** rc 0, 0 failed.
  **`make test-memfn-link`:** rc 0.
- **`make test-memfn-finder`:** rc 0. 28,938 checks passed, 0 failed
  (finder_check included).
- **Mech rows S2930, S2931, S2933** (`tests/mech/run_sabotage_matrix.sh`):
  see `mech.log`. These are the only rows whose SAB_FILE this lane changed;
  each anchor matches exactly once.
- RESULTS: full dry `--quick`: rc 0, 1650 cells built and gated, 0 failures, 185 pools x 4 = 740 exes, 0 refused; C1-C5 deny check 42 arm-I loop-free, reach 122 (U5's was 124: the two c6_hex1001 artifacts are out of it, F9). Mech: `== mech run COMPLETE: 3 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) at ac807e97a ==`; S2930 DETECTED 4 fail, S2931 DETECTED 17 fail, S2933 DETECTED 3 fail (memfnfinder).

## OWED RUNS

Queue jobs (non-timing), per `docs/dev/lanes/RUNS.md`:
- `746-kit-bsu5fix-test`, key `kit-bsu5fix-test`: make test on this tree
  via `scripts/perfrun`, with TMPDIR set.
- `747-kit-bsu5fix-mech`, key `kit-bsu5fix-mech`: S2930, S2931, S2933,
  readiness `after kit-bsu5fix-test`. No other row moved, and no row is
  new.
- **Timing** (U6, main's window, each bench box that runs V): C6's 108 timed
  cells and C6c's 84, under rule `9a2875a6bf089837`. The result writer must
  write the `#c6` header the rule's RECORD clause states.
- **Status line for main's [BSPAN-CLANG-DIFF]:** C6c covers the SIMD-off
  wrapper on the 3 real sites under clang -O2 and gcc -Os, as non-PIC
  executables. It is UNMEASURED until U6's window runs it. Named gaps:
  clang -O3 (no bench arm) and the bench's `-O2 -fPIC -shared` build.
