# Lane sae2: span arms unit E2 (zero-width items stop cutting the run)

Lane sae2 (opus), 2026-11-09. Branch lane/sae2 in worktrees/sae2, based on lane/sae1 (E1, 0f6d25aac). Main is
NOT merged in. Design: docs/design/span_arms.md rev 2.2 §4.1 (T3), §6, §8 row E2, §12, §3.7; D191; rulings R1,
R2, R3 and R-AXES (docs/dev/lanes/sae2_rulings.md).

## Summary

- **T3 is built as a declared first-match table**, `rb_zero_rows` in `src/facts/req.c`. Every node whose kind
  row's TEXT is ZERO now goes through it (`rb_row_into` -> `rb_zero_into`). The rows, in order:
  - E-1 `A_EMPTY`: the unit, under arm `empty`. The next row is its restored form, the old cut.
  - E-5, a positive lookaround in either lowering (`A_LOOK` not negated, or `A_CTX` whose function is
    ctxfn.def's NEXT or PREV row): the plain unit, under arm `zero`. L1 adds the item here.
  - E-4, every other zero-width node (`\b`, `\B`, `$`, `^`, `\A`, `\z`, `\G`, `\K`, a check callout, a
    negative lookaround of either lowering): the unit, under arm `zero`.
  - Last row: the old cut. Every restored row falls through to it.
- **The unit's value** (`rb_zero_unit_into`): for the run it is `rr_unit()` (no byte, `all`, width 0), so the
  bytes on the two sides join. For the description it is `pcrec_pd_unit()` for `A_EMPTY`, and for a node that
  can fail it is a new `pcrec_pd_zero()`: a width-0 group that is not exact (§4.2).
  - `pcrec_pd_cat`'s identity shortcut now applies only to an EXACT width-0 group, so a zero group's
    inexactness reaches every group built through it.
  - No reader of `exact` exists outside desc.c today, and the listing does not show it. L1's item reads it.
- **The set is unchanged.** A zero-width node adds no byte and no offset.
- **Lowering-independent.** A one-character lookaround lowered to `A_CTX` and the same lookaround as `A_LOOK`
  give the same run under E2 (both are the unit).
- **R1 applied: E-1 moved here from alt_normal_form stage 2a.** `abcd()efgh` and `abcd(?:|)efgh` now state
  `abcdefgh`. E-1 restores under the existing arm `empty`. Record for the design note: E-1 is E2's, not 2a's.
- **R2 applied:** at E2 the `zero` arm restores BOTH E-4 and E-5 to the old cut. L1 re-splits E-5 when `look`
  exists.
- **R3 applied: the run's definition moved from L2 to E2.**
  - match_api §6.3.7¶6 and tuning §2.28¶1 now say the run is one every successful ATTEMPT must contain, and
    cover `\K` (`ab\Kcd`: run `abcd`, match (2,4)). This is the final wording.
  - L2's hunk only adds its clause that the run may extend past the attempt's consumed end.
  - Record for the design note: ownership of that paragraph moved from L2 to E2.
- **Walk-parameter table**: `src/facts/walk_arms.def` gains the row `zero` (facts `req_whole_run`, `req_pieces`).
  It is kept in its own block below `empty`, for sar1's `rep` row.
- **No abi number.** No emitted scaffolding moves, only req fact VALUES (`RX_REQ_RUN`, `RX_REQ_BYTE`,
  `RX_REQ_WHY`, `RX_REQ_HANDOFF`). The identity job checks this.
- **Open point for the manager (reply either way):** match_api §6.3.7¶4 (`<PREFIX>_REQ_BYTE`, "a byte every
  match must contain") has the same `\K` gap R3 closed for the run.
  - It was already true before E2 (`abc\Kd`). E2 adds patterns: `ab\Kcd`'s byte can now be `a` or `b`, which
    lie before the reported match.
  - R3 named only ¶6 and §2.28¶1, so ¶4 is untouched. It also touches D191's wording of the byte ("a byte
    every match consumes"), which is the owner's.
- **Gates OWED** as queue jobs (below). Per R-AXES, the axes job is NOT queued; the manager queues it after
  sae1fix.

## Census and movers

The census is the unit's measurement record, not a build gate (D191). Its instrument is
`docs/dev/lanes/sae2_evidence/census_e2.py`, and `mk_rtrace.sh` builds the R-span trace.

- **Model (independent of the compiler's T3)**: the walk facts of P under E2 equal the reference (E1) compiler's
  walk facts of P's SPELLING.
  - The spelling replaces every zero-width assertion item (with its quantifier) by `(?:)?`, and inserts
    `(?:)?` into every empty branch.
  - `(?:)?` is E1's unit: T2 row 1, `m = 0`.
  - Replacing instead of deleting never creates an `A_EMPTY` (the reference's cut) and never moves a capture
    number.
  - The scanner is census_e1.py's (imported), plus the item classes.
  - Abstained and listed: `(?x)`, callouts, verbs, conditionals, recursion and subroutine calls.
- **Two-sided compare**, as E1's:
  - observed movers are any differing facts row, byte and utf8;
  - predicted movers are those whose spelling moves the walk facts;
  - the value check is: work walk facts of P == ref walk facts of the spelling.
- **Per producer kind**: for each predicted mover, the spelling is restricted to one kind:
  - kinds: `empty`, `wordb`, `anchor`, `gstart`, `kreset`, and the four lookaround forms;
  - each lookaround form is split by lowering, `:ctx` or `:look`, read from the reference `kinds` fact on the
    item compiled alone;
  - a move that needs several kinds together is `joint:`.
- **R-span movers** (r1 F11): scratch builds of both revisions carry one stderr trace line in `pf_window_of`
  (`RSPAN off len positions`). A mover whose set of traced R spans differs, in byte or utf8, is an R-span
  mover. The patch exists only in the scratch builds; nothing is committed with it.
- **Measured so far (by hand, under the sweep cap)**: a 7-pattern smoke population.
  - 6 movers, all predicted. 0 two-sided differences. 0 value mismatches.
  - 4 of them are R-span movers. Example: `xyz(?<=yz)abc`'s R span goes from `RSPAN 3 3 abc` to
    `RSPAN 0 6 xyzabc`.
  - Producers: `look-behind-pos:look`, `look-ahead-pos:ctx`, `look-ahead-neg:look`, `empty` (2), and
    `joint:anchor+wordb` (`(?:^|\s)foo\b`, which moves `req_pieces` only).
  - Every witness in spanarms.rxt moves as T3 says (the premise test's patterns: `xyz(?<=yz)abc` goes from
    `616263` to `78797a616263`, and `foo\bbar` from `626172` to `666f6f626172`).
- **Bench, text side (no compiles)**:
  - 106 of 392 bench patterns hold a zero-width item: anchor 55, wordb 37, lookbehind-neg 9,
    lookahead-neg 6, lookbehind-pos 5, lookahead-pos 3, empty/gstart/kreset 1 each.
  - 45 are abstained: 12 callouts, 8 verbs, 8 subroutine calls, 8 `(?x)`, 3 conditionals, 2 recursion, 4 heads
    the scanner does not know.
  - A by-hand sample of the first 20 candidates' `req_whole_run` found NO bench mover: most anchors and `\b` sit
    at a pattern edge.
  - Whether a bench cell moves (D77's trigger) is the census job's answer.
- **Stop rule**: corpus movers exist (every witness block), so D191's "no mover anywhere" stop does not fire.
- **The full census is OWED** (job `main-sae2-census`). Its output is
  `$PCREC_TMPDIR/scratch/sae2/census/summary.txt` (movers per producer kind, R-span count, BENCH-MOVER lines,
  two-sided lists) and `census.tsv`.

## Identity

- **The B0 identity diff is OWED** (job `main-sae2-ident`).
- **How it runs**: `scripts/emit_sweep.py --ref-bin <E1 build> --bin <lane build>` with every stream, over the
  corpus and sae1's bench patterns file.
- **The verdict** is sae1's `ident_check.py` against `census_e2.py`'s census.tsv (same column layout):
  - every argv-stream mover is a census mover;
  - a composition mover's source holds one;
  - no dumps mover and no asymmetric row;
  - the facts stream's movers equal the census's.
- **Expected**: only the movers' req stamps move. Any scaffolding move is a STOP (the brief).

## Witnesses and sabotage

`tests/litscan/spanarms.rxt` gains 23 blocks, each on both engines. Every expectation is libpcre2-8 10.46's
(`tests/lib/p2probe.c`, this lane). Under the harness it reads 202/0.

- **The witnesses:**
  - S-L in two forms, both sabotage detectors for S1925:
    - E2's own site, `xyz(?<=yz)abc`: the plant claims `xyzyzabc`;
    - the design's `(?<=foo)bar` with `ms 3 "foobar" 3 6`: the plant claims `foobar@3`, stamped `"emitted"`
      under the plant, so the search from 3 finds no attempt.
  - W-E3 `xy(?<!ab)cd`.
  - S-g at E2's site, `(ab)x\1y`.
  - E-4 rows for each kind: `\b`, `\B`, `$`, multiline `$` and `^` (A_CTX), `\K`, `\G`, `\A`, `\z`, a negative
    lookahead, and the one-character lookarounds lowered to A_CTX NEXT, PREV, NOT_NEXT and NOT_PREV.
  - E-5 with `A_LOOK` (`xy(?=ab)abzw`) and two negatives in a row.
  - E-1: `abcd()efgh` (with its group), `abcd(?:|)efgh`, and `ab(?:|x)cd` (no move).
- **Sabotage rows S1925-S1929** (S1930-S1934 unused). All five were planted by hand and detected, and each REACH
  probe prints its token on the clean tree. Plant script: `$PCREC_TMPDIR/scratch/sae2/plant.sh`.

| row | the plant | detector | detection (manual plant) |
|---|---|---|---|
| S1925 | a positive `A_LOOK`'s body walked as CONSUMED at T3 (S-L's plant) | harness spanarms.rxt | 11 cases fail, S-L's `ms 3` among them |
| S1926 | a negative `A_LOOK`'s body walked as consumed (W-E3's plant) | harness spanarms.rxt | 12 fail |
| S1927 | TEXT ANY sent to T3: a backreference becomes the unit (S-g at E2's site) | harness spanarms.rxt | 8 fail |
| S1928 | the E-4 row ignores the `zero` arm | run_facts_checks [facts-arm] | FAIL (restore=zero lists the joined run) |
| S1929 | the E-1 row ignores the `empty` arm (R1) | run_facts_checks [facts-arm] | FAIL |

- **[facts-arm]** now carries three witnesses:
  - `abcd(?:\b)*efgh` under `empty` (E1's);
  - `abcd()efgh` under `empty` (E-1): the default lists `6162636465666768`, the lever lists `65666768` with
    `harness:empty`;
  - `xyz(?<=yz)ab\Bcd` under `zero` (E-4 and E-5 in one pattern): the default lists `78797a61626364`, the lever
    lists `78797a`/`78797a@2` with `harness:zero`. `req_byte` and `req_pieces` carry the token; `req_set`
    does not.
- **Lever fence**: `tests/compound/run_lever_fence.sh` allows S1928/S1929 (their reach probes name the lever).
- **test-axes**: `INTERNAL_ARMS` gains `--harness=restore=zero`. The run is held per R-AXES.

## Spec and listing hunks

- **`docs/spec/facts_listing.md` §4.1.3¶4a**: the `harness:` token sits on `req_whole_run`/`req_pieces` for the
  arms `empty` and `zero`. It now also states the `zero` arm's meaning (a node that consumes nothing but can
  fail, in its old form, a cut).
- **`docs/spec/match_api.md` §6.3.7¶6 (R3)**: the run is "a literal run every successful attempt must contain".
  The paragraph now defines an attempt and shows the `\K` case (`ab\Kcd` states `abcd` with its match at
  (2,4)). Where no `\K` moves the start, the attempt's span is the match's.
- **`docs/spec/tuning.md` §2.28¶1 (R3)**: "every successful attempt must contain", pointing to match_api
  §6.3.7¶6 for `\K`.
- **Not changed**: match_api §6.3.7¶4 (`<PREFIX>_REQ_BYTE`). This is the open point in the Summary.
- **CLAUDE.md** updated in: src/facts (req.c's T3, walk_arms.def's arms, desc's `zero`, the S1925-S1928
  anchors), tests/litscan (spanarms.rxt's E2 blocks). The size check passes.
- History-index line added (docs/dev/history/claude_md/docs__dev__lanes.md).

## Checks run

By hand, on the lane build:

- `make -j4` clean.
- `make strict`: clean ("whole tree compiles clean with -Werror -Wshadow").
- `tests/harness/run.sh tests/litscan/spanarms.rxt`: 202 passed, 0 failed.
- `tests/codegen/run_facts_checks.sh`: 11/0 ([facts-arm] and [facts-pieces] included).
- `tests/compound/run_lever_fence.sh`: PASS.
- `tests/spec_history/run_spec_history.sh`: 11/0.
- `scripts/check_claudemd_size.sh --all`: OK.
- Mech: `VALIDATE_ONLY` 5/5. All five plants were detected by hand (table above) and all five reach probes print
  their tokens.
- census_e2.py was smoke-tested on 7 patterns: 0 two-sided differences.

## STATE AT HANDOFF

- **Branch lane/sae2**, base lane/sae1 0f6d25aac. Commits:
  - bd8505abf: T3, the `zero` arm, witnesses, S1925-S1928;
  - 2edfb484e: axes arm, lever fence, ¶4a, census tooling;
  - 82ce62470: R1, E-1 and S1929;
  - ffbec75e3: R3 spec;
  - f09db070d: census E-1;
  - this report's commit.
- **Rulings file**: entries R1, R2, R3 and R-AXES. The last entry applied is R-AXES.
- **OWED: queue jobs, chained, each hold-aware** (no start 19:00-01:00), queued behind main-sae1-mech:
  - `main-sae2-census` (205): census_e2.py. Output in `scratch/sae2/census/`.
  - `main-sae2-ident` (206): emit_sweep every stream, then ident_check. Output in `scratch/sae2/ident/`.
  - `main-sae2-reach` (207): `REACH_ONLY=1` over the whole sabotage matrix (the delivery bar: the pre-check
    fires in new places). Log `scratch/sae2/reach.log`. A moved witness is re-aimed by the follow-up agent.
  - `main-sae2-maketest` (208): `make strict` + `make test` via perfrun (PC-3 included). Logs
    `scratch/sae2/maketest.log` and `strict.log`.
  - `main-sae2-mech` (211): S1925-S1929. Log `scratch/sae2/mech.log`.
  - NOT queued, per R-AXES: test-axes with `AXES="--harness=restore=empty --harness=restore=zero"`. Its job
    script is ready at `scratch/sae2/jobs/axes.sh`; it was cancelled from the queue as 209, and 210 mech was
    re-queued as 211 after maketest.
- Job scripts are in `$PCREC_TMPDIR/scratch/sae2/jobs/`. The reference binaries (E1) are in `scratch/sae2/ref/`,
  and the R-span trace builds are in `scratch/sae2/rtrace_{ref,work}/`.
- **Open (reply either way)**: match_api §6.3.7¶4 (`REQ_BYTE` under `\K`). See the Summary.
- **For sar1's merge**: walk_arms.def's `zero` row sits in its own block. req.c's T3 is a separate table placed
  after `rb_walk`, and does not touch `rb_rep_rows`.
- No kit facts to relay. No memfn/ edits.
