# Lane sar1fix report: review 2026-11-09 r5 fixes on lane/sar1 (span arms R1)

Lane sar1fix (opus), 2026-11-09, worktree `worktrees/sar1`, branch
`lane/sar1`. The brief: merge lane/sae1, then apply the ruled review
`docs/dev/reviews/2026-11-09-r5-sar1.md`, with the rulings in
`docs/dev/lanes/sar1fix_rulings.md` (R1, R-IDENT, R-CHAIN). main was not
merged. No abi number moves and no emitted scaffolding moved.

Commits: f7809e83a (merge), fe5712ccb, 001c0faf5, e72f044ab, 011ea8d58,
1b8e10239, and the report commit.

## Merge of lane/sae1

- `git merge lane/sae1` ran on its own, at f7809e83a. It had four conflicts:
  - `docs/dev/history/claude_md/docs__dev__lanes.md`: kept both lines.
  - `docs/spec/facts_listing.md` ¶4a: sae1fix's text plus R1's `rep` arm.
  - `docs/spec/tuning.md` §2.28¶3: R1's text plus sae1's width-0 clause.
  - `src/facts/CLAUDE.md`: the anchor list now has S1909 and S1910 too.
- `make strict` was clean after the merge.
- Brief check: a split part that holds a counted repeat restores under
  `--harness=restore=rep`. Witness `^a|xy(?:ab){2}zw$`: RX__Q_REQ_RUN is
  `7879616261627a77@6` by default and `7a77@0` under the `rep` arm (at merge
  time the arm gave `6162@1`; the tie rule below moved it). This is pinned in
  `[facts-arm]`.

## Tie fix and measurements

**The fix (EMIT-1 + EMIT-2 cause 1, one fix).**
- `rn_better` (`src/facts/req.c`) is now a declared first-match table,
  `rn_choice_rows`. In order:
  1. more information;
  2. the rarer scan member: lower mass of the member
     `pcrec_find_run_scan_index` picks, by `pcrec_find_seq_mass` over the
     same byte-rate the pick reads;
  3. the nearer offset bound;
  4. content order: shorter, then lower bytes, then wider mask, then the
     untruncated run.
- No row reads argument order or spelling.
- The rate reaches the walk as one `ReqWalkParams.rate` field, set in
  `pf_derive_req_walk` from `pcrec_find_byte_rate`.
- Under NONE (`-e utf8`) row 2 answers 0 for every pair, so rows 3-4 decide.
  The rate pointer is not tested anywhere (S1 rule).
- The walk `w` is threaded into `rr_cat`, `rr_pow`, `rr_rep_exact`,
  `rr_rep_split`, `rb_gap_into`, `rb_assert_into`, `rb_row_into` and
  `rb_rep_split_val`.
- `req_whole_run`'s why is now the rate rule (`rate:builtin-prior` or
  `rate:none(utf8)->rightmost`) when a run exists, through the now non-static
  `pcrec_req_rate_why`.

**Rulings R1 (applied): the relabel.**
- `REQ_WHOLE_RUN` is `PF_DERIVED` in `facts.def`, and the kind comment says
  why.
- The patfacts design was updated with no exception clause: item 3, the table
  row at its old line 185, and the readers table input.
- The `req.c` header comments and `src/facts/CLAUDE.md` were updated.

**Reader survey, done before the relabel.**
- The fact kind is read by exactly one reader: `src/dump/facts_dump.c` (the
  listing's note column, which makes no wording promise).
- `pr11_front.py` reads the status column. `reqcube_check`, `emit_dfa` and
  `run_prechecks.sh` read values.
- No reader keys or caches `req_whole_run` as prior-independent, and no check
  compares it across analyses.
- So no reader needs it prior-independent, and no STOP was needed.

**The NONE count is OWED.** Job `main-sar1-tiecensus` gives it as "NONE (utf8)
req_whole_run equal to the tree before the fix: N of M". On the
`spanarms.rxt` smoke it was 15 of 19. The 4 that moved are deliberate:
- `xy(?:ab){1,2}zw` and `xy(?:ab){1,3}zw`: `abzw` becomes `xyab` (row 3,
  nearer).
- `ab(?:c?){2}de` and `ab(?:cd){0,2}ef`: `de`/`ef` becomes `ab` (row 3).

**Facts after the fix.**
- `Q(?:ab){20}Z` lists `b(ab)^15Z`, `req_byte` 90 (Z). This is the same as
  its unrolled literal: repeat and literal now agree, as EMIT-1 asked.
- `A{33}x` lists `A^31x`, `req_byte` 120, the literal's run.
- `x(?:a[bc]){2,3}y` lists `x·abab` (`7861626162/fffffefffe`), so the rare `x`
  is kept. Same for `x(?i:ab){2,3}y`.
- §3.4 tie cells, re-checked:
  - `xy(?:ab){2,3}zw` lists `ababzw`. The head `xyabab` and the tail `ababzw`
    tie on information. Row 2: scan members `x` 997 ppm vs `z` 498 ppm, so `z`
    is rarer and the tail wins.
  - `xy(?:ab)+zw` lists `abzw`.
  - Under utf8 (NONE), `xy(?:ab){2,3}zw` lists `xyabab` (row 3, the nearer
    offset).

**Measurements.**
- Setup: `perf stat -e instructions:u`, `taskset -c 7`, a 20-scan loop,
  3 repeats each (the repeats agree within ±25 instructions).
- BASE = lane/u3mech 404cff6ea; NEW = this lane after the fix.
- Texts:
  - text_eng: the review's English text;
  - text_ab: dense `ab` text;
  - text_prior: text drawn from the built-in prior.

| witness | eng BASE | eng NEW | ab BASE | ab NEW | prior BASE | prior NEW |
|---|---|---|---|---|---|---|
| `Q(?:ab){20}Z` | 3,886,364 | 3,883,298 | 2,126,703 | 2,126,641 | 4,057,892 | 4,003,244 |
| `x(?:a[bc]){2,3}y` | 8,596,985 | 7,333,399 | 2,126,863 | 2,126,562 | 7,635,054 | 6,640,245 |
| `x(?i:ab){2,3}y` | 8,596,099 | 7,333,398 | 2,126,861 | 2,126,563 | 7,638,754 | 6,640,242 |
| `x(?i:ab)+y` | 8,596,083 | 7,345,239 | 2,126,863 | 2,126,561 | 7,638,752 | 6,670,644 |
| `A{33}x` | **3,892,282** | **7,231,099** | 2,126,522 | 2,126,622 | 15,743,693 | 6,559,464 |
| `A{33}xyz` | 5,432,364 | 5,409,678 | 2,126,602 | 2,126,621 | 5,240,572 | 5,220,902 |
| `qA{40}` | 6,909,205 | 6,096,839 | 2,126,861 | 2,126,821 | 6,370,856 | 5,707,082 |
| `xy(?:ab){2,3}zw` | 36,591,211 | 5,455,038 | 2,126,542 | 2,126,582 | 30,229,360 | 5,260,263 |
| `xy(?:ab)+zw` | 36,591,215 | 6,094,658 | 2,126,541 | 2,126,701 | 30,229,361 | 5,816,665 |
| `q(?:ab){2,3}z` | 35,647,454 | 5,409,618 | 2,126,541 | 2,126,562 | 29,581,841 | 5,220,842 |
| `xy(?:ab){16}zw` | 36,591,154 | 5,409,698 | 2,126,523 | 2,126,641 | 30,229,301 | 5,220,923 |

- On text_eng and text_prior, every witness is at or below BASE except
  **`A{33}x` on the English text, +86%**.
- On text_ab, NEW is up to +160 instructions in 2.13M (0.008%) on six cells,
  so it is strictly above BASE there. I read that as noise; the cause was not
  investigated.
- What the `A{33}x` loss is:
  - It is not a tie left unbroken. NEW's `A{33}x` costs exactly what the
    unrolled literal `A`×33`x` costs on BASE (7,231,102), so the repeat now
    does what its literal does, which EMIT-1 required.
  - BASE listed no whole run for `A{33}x` at all.
  - The English text has few `x` and a dense `A` run. The run's handoff on
    the rare `x` loses to BASE's plain memchr locator.
  - That is EMIT-2 cause (2), run-locator pricing: the pick reader does not
    price a run's handoff against a memchr locator. It is PLAN'd by the
    review, not in this fix.
  - On prior-distributed text the same pattern runs 2.4x faster.
- I did not try to fix it in the walk: that would mean choosing by the text,
  which is the pricing row's job. Reported, not hidden.

## Other fixes

- **SLOT-1:**
  - Piece widths saturate: `pd_cat_group` uses `pcrec_sat_add`.
  - `pd_pow` uses `pcrec_sat_mul`/`pcrec_sat_add`.
  - A saturated width is a wall: `pd_norm` returns none.
  - Nested `{65535}` pieces now list `not-fixed-width` instead of a negative
    width.
  - Spec: facts_listing ¶8c, "a length too large to count, 2^40 bytes or
    more, reads as no fixed length".
- **SLOT-2:**
  - `pd_pow` returns the unit at once for one width-0 group.
  - `rr_rep_exact` keeps `all` when `b.maxw == 0`.
  - The two false comments are corrected.
  - `ab(?:c{0}){3}de` under `restore=empty` now lists the whole run.
- **SLOT-4:**
  - The five `rb_rep_*_into` builders became value builders
    (`rb_rep_unit_val`, `_exact_val`, `_split_val`, `_best_val`, `_gap_val`)
    behind one `rb_rep_val` switch.
  - The repeat arm does one `rb_cat_into`.
- **CONTRACT-1:** tuning §2.28¶3 states `X{0}`/`X{0,0}` (`xy(?:ab){0}zw`
  reports `xyzw`).
- **CONTRACT-2:**
  - `pd_dropped` is order-free: a wall on either side wins.
  - Spec: facts_listing ¶8c, with `(?:a|bc){10}x*` and its ten copies written
    out alike.
- **CHECK-1:**
  - `[facts-rep]` cell `xy(?:ab){1,2}zw`: `61627a77` by default, `7a77` under
    the `rep` arm.
  - Mech row S1922 drops the arm from T2 row 3. Planted: DETECTED by
    `[facts-arm]` and `[facts-rep]`.
- **CHECK-2:**
  - `handoff_vm.rxt` gains a `vm`-route block for the entry-only witness
    `(ab)c?userpass` (subjects `abcuserpass`, `userpass abcuserpass`). It was
    generated by `gen_handoff_vm.py` against libpcre2 10.46 (0 mismatches),
    with the match at 0..11.
  - The rxtsource census was re-pinned to 318/6433/76372 and C3 to
    22810/25213. Both comments say which file moved and why.
- **CHECK-3:** S1919's REACH also reads the DFA twin `(?:a.){10}.?xyz`
  (engine dfa, K 21).
- **CHECK-4, condition met:**
  - `(?:ab[0-9]cd){3}` lists `cdab` (the join of two copies), where one copy
    gives `ab`. It is now a `[facts-rep]` cell.
  - Mech row S1923 (`rr_pow_count` 2 becomes 1). Planted: DETECTED.
  - The `c == m` clause of `rr_rep_exact` has no separating cell. With the
    clause removed, the facts checks, the prechecks, `x(?:ab){20}y`,
    `Q(?:ab){20}Z` and `(?:abc){20}d` list the same: the 32-position store is
    full when `c < m`, so a truncated run never joins again. Marked NOTED, as
    the condition says. No row was added for it.
- **Re-pins forced by the tie rule.** Each is a cell where two equal-information
  runs tie; the rarer one is now chosen.
  - `[facts-arm]` and `[facts-rep]` values and whys.
  - `run_prechecks.sh` 5.11 `cat\s+sat`: the cell becomes `cat\s+sate`, since
    `cat`/`sat` tie and the rarer `cat` is taken. The row is kept with a
    longer tail.
  - The R1-owed prechecks reds that were already red at f7809e83a (7 cells in
    3.1, 4.1, 4.7, 5.12a), each re-derived.
- **Re-aims and re-anchors.**
  - REACH re-aimed: S470 (K5 becomes K3), S1907, S1909, S1917, S1921.
  - Re-anchored to the threaded helpers: S1653, S1915, S1916, S1917.
  - S474 now plants its bounded preference before the `rn_choice_rows` loop.
  - S1920 re-anchored. S446 and S807 re-aimed at the live min-0 site.
- **Not done in this lane:** DOC SLOT-3 and the PLAN items (SLOT-5, EMIT-2
  cause 2) are the manager's.

## Checks run

- `make strict`: clean at 011ea8d58.
- `run_facts_checks.sh`: 12 passed, 0 failed.
- `run_prechecks.sh`: 395 passed, 0 failed.
- `make test-rxtsource`: GREEN after the re-pin.
- Harness, with expectations from libpcre2 or oracles: `spanarms.rxt`
  142/142, `handoff.rxt` 4908/4908, `handoff_vm.rxt` 831/831, `reqcube.rxt`
  287/287.
- libpcre2 differential (crit-sar1's `cmp1.sh`): 15 witnesses × {byte, utf8}
  × 10 subjects, all SAME.
- Facts listing vs f7809e83a, 114 patterns × 4 arms × 2 engines: only the 6
  expected SLOT/CONTRACT diffs (before the tie fix).
- Plants, each on its own detector, then restored with `git checkout`:
  - S1922: DETECTED (facts).
  - S1923: DETECTED (facts).
  - S446: DETECTED (`reqcube.rxt`, 16 cases).
  - S807: DETECTED (prechecks).
  - S474: DETECTED (prechecks).
  - S1915: DETECTED (`spanarms.rxt`, 23 cases).
- REACH probes OK: S463, S265, S465, S474, S807, S446, S1905-S1910, S1915-S1923.
- Anchor check over every `src/facts/` row: all found exactly once.
- `tiecensus.py` smoke on `spanarms.rxt`: COMPLETE, 0 information movers.

## STATE AT HANDOFF

- Branch `lane/sar1`, tip = the report commit (code tip 1b8e10239). Worktree
  clean.
- Last rulings entry applied: **R-CHAIN**. Each job's `--ready` waits on a
  RESULT FILE, never on a key: tiecensus and ident-2 wait on
  `scratch/sar1fix/census/summary.txt`; the rest wait on the evening hold
  only. Before that, R1 and R-IDENT (the ident job uses the sae1tri wording).
- **OWED queue keys** (scripts in `/var/tmp/pcrec-pcrec/scratch/sar1fix/jobs/`;
  output under `/var/tmp/pcrec-pcrec/scratch/sar1fix/`):

| key | what it runs | refs and expected result |
|---|---|---|
| `main-sar1-census-2` | census_r1 | REF = lane/sae1 tip 69aed3360, built at `scratch/sar1fix/ref1` |
| `main-sar1-tiecensus` | every fact of f7809e83a vs the fix | the NONE count; 0 unexplained R1 census differences |
| `main-sar1-ident-2` | emit_sweep | ref1 vs tip; ident_check on census-2 |
| `main-sar1-maketest-2` | make strict + make test | |
| `main-sar1-mech-2` | 17 rows | S1915-S1923, S463, S446, S807, S474, S470, S1653, S1907, S1909 |
| `main-sar1-reach-2` | REACH_ONLY | all 1213 rows |
| `main-sar1-axes` | `AXES=--harness=restore=rep make test-axes` | |

- Read census-2 together with tiecensus. census_r1's REF has the old tie
  order, so tie-moved texts that are not repeats show as OBS-NOT-PRED. The
  tiecensus reconcile line must say 0 unexplained.
- Open for the manager:
  - `A{33}x` on English text (EMIT-2 cause 2, the run-locator pricing PLAN
    row).
  - The `c == m` clause is NOTED.
