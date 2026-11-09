# Lane sae1: span arms unit E1 (width-0 repeats) and the walk-parameter table

Lane sae1 (opus), 2026-11-09. Branch lane/sae1 in worktrees/sae1, based on lane/u3mech 404cff6ea (the joint U2+U3
landing branch, abi 98). Main is NOT merged in (the brief leaves the tests/ci/shards.tsv conflict to the manager).
Design: docs/design/span_arms.md rev 2.2 §8 row E1, T2 row 1 (§6), T3 E-2/E-3 (§4.1), the restored-arms row of
§3.7's walk-parameter table, and D191.

## Summary

- **T2 row 1 is built as a declared first-match table** in `src/facts/req.c` (`rb_rep_rows`). A repeat whose body
  is width 0 (`maxw == 0`, any m and n) is now CAT's unit at `m = 0`. At `m >= 1` it is the body's value. `all`
  is true in both cases. The table's other two rows are today's arms, unchanged: `m >= 1` keeps the best-only
  copy (`rb_rep_into`), and anything else is the gap. Each row carries the walk arm that restores the old form,
  so later units (R1 `rep`, E2 `zero`, L1 `look`) add their rows to the same table.
- **The walk-parameter table (§3.7, T7)**: `ReqWalkParams {pos_set, max_pieces, restored}` (`facts_derive.h`) is
  filled once at the one walk entry (`pf_derive_req_walk`) and handed to `pcrec_req_walk`. The restored arms come
  from a new X-macro table, `src/facts/walk_arms.def`. Each row gives the arm's name and the walk facts it can
  change. E1 adds one row, `empty`.
- **Restore lever (test builds only)**: `--harness=restore=ARM[+ARM]`, in build/pcrec-harness only (sixth
  harness lever, `PcrecHarnessOptions.walk_arms`). Its listing token is `harness:<arm>` in `--emit-facts`'s why
  column. The token takes precedence over deny/decline/rate (facts_listing.md §4.1.3¶1 and the new ¶4a). It sits
  on req_whole_run and req_pieces. Every fact derived from those inherits it through `pf_ask`
  (`PatFacts.arms_seen`).
- **No abi number, no emitted scaffolding change.** Artifacts move only through the stamp values of the req
  facts they already list (`RX_REQ_RUN`, `RX_REQ_BYTE`).
- **One design inconsistency, flagged (not resolved here).** T2 row 1 (span_arms.md line 940) sets `all` true
  "any m, n", and W-R4's designed failure needs that. As a result, `(?:\b)+` and `(?:^)+` (§4.1 E-4, the
  m >= 1 can-fail body, assigned to E2) also move under E1: the run joins across them. The answers are
  unchanged and libpcre2-checked (`abcd(?:\b)+efgh` in spanarms.rxt). If E-4's m >= 1 half should stay E2's,
  the narrowing is one table row (`maxw == 0 && rmin >= 1 && body is a cut` -> BEST). Question for the manager
  below.
- Gates owed as box-queue jobs (keys below). The census and the identity diff were built and smoke-tested but
  run only in the queue.

## Census and movers

The census is a measurement record, not a build gate (D191). Its instrument is
`docs/dev/lanes/sae1_evidence/census_e1.py`.

- **Model (independent of the compiler)**: a PCRE text scanner finds every QUANTIFIED item whose every path is
  0 bytes wide: anchors, `\b`-class escapes, lookarounds, empty groups, option settings, comments, `{0}`
  repeats, and groups made only of those. It deletes those items from the pattern text (the SPELLING: the unit
  matches the empty string) and asks TODAY's compiler (the branch-point build) for the spelling's run.
  - A PREDICTED mover is a pattern whose spelling's reference run differs from its own reference run, in either
    encoding.
  - When the model does not know a construct, it treats it as consuming, so it predicts no move.
  - A candidate whose deletion would renumber a capture, or that sits in a `(?x)` pattern, is ABSTAINED and
    listed.
- **Observation**: every `--emit-facts=byte,utf8` row of the branch-point build vs the lane build. Any differing
  row makes the pattern an OBSERVED mover.
- **Two-sided compare**: observed-not-predicted, predicted-not-observed, and, for every mover, the value check
  "the lane's run of P equals the reference run of P's spelling".
- **Population**: the corpus (`--list-source` over tests/**/*.rxt) plus every pcrec-bench pattern file
  (bench/*/patterns/*.rx, read-only, 392 patterns).
- **Measured so far (by hand, below the 50-compile sweep cap)**:
  - All E1 witnesses move as the model predicts, with equal values:
    - `abcd(?:)*efgh` and `abcd(?:\b)+efgh`: run `65666768` -> `6162636465666768`;
    - `xy(?:(?=a))*abzw`: `61627a77` -> `787961627a77`.
  - `ab(?:c?){2}de`, `a(b|c)+d` and `(?:^|\b)+foo` do not move, and the model agrees.
  - Facts that move with the run: `req_run`, `req_byte`, `req_run_maxoff`, `req_landmark_maxoff`, `run_pin`, and
    `req_pieces` when the body is unit-valued at m = 0.
- **Bench, text side**: 0 of 392 bench patterns hold an E1 candidate. 43 are abstained: 12 callouts `(?C`,
  10 `(?x)`, 8 verbs, and the rest are recursion and conditional heads. So the expectation is NO bench cell
  moves, and the census job confirms or refutes it (an abstained mover is listed with its reason).
- **The full census is OWED** (job `main-sae1-census`; output in `$PCREC_TMPDIR/scratch/sae1/census/summary.txt`
  and `census.tsv`).
  - Corpus movers do exist: the witnesses alone are 9 patterns, so the "no mover anywhere" stop rule does not
    fire.
  - Expected: the movers are the corpus patterns that hold the shape, plus 0 bench cells.

## Identity

- **The B0 identity diff is OWED** (job `main-sae1-ident`).
- **How it runs**: `scripts/emit_sweep.py --ref-bin <branch-point build> --bin <lane build>` with every stream
  (c-default, c-vm, emit-ir, stderr, dumps, facts, composition) over the corpus and the bench patterns file
  `sae1_evidence/bench_patterns.txt`.
- **New option, `--movers-out FILE`**: it writes every mover and asymmetric key per stream, where the report
  prints only five. A 19-line change in scripts/emit_sweep.py.
- **The verdict** is `sae1_evidence/ident_check.py`:
  - every argv-stream mover is a census-observed mover;
  - a composition mover's source file holds a census mover;
  - no dumps mover and no asymmetric row;
  - the facts stream's movers equal the census's (two runners, one population);
  - emit_sweep's floors and the DELIVER witness hold.
- **Smoke test** (2 patterns, by hand): `abcd(?:\b)*efgh` moves in c-default, c-vm and facts; the diff hunk is
  `RX_REQ_BYTE`/`RX_REQ_RUN` only; emit-ir does not move; `a(b|c)+d` is identical.
- **Scaffolding**: no abi event is expected. If the run shows scaffolding moving, that is a STOP per the brief.

## Witnesses and sabotage

New corpus file `tests/litscan/spanarms.rxt`: every pattern runs on both engines, with `features all`, and every
expectation is libpcre2-8 10.46-verified (p2probe). 62/0 under the harness.

- **W-R4** `ab(?:c?){2}de` (abcde (0,5), abde (0,4), abccde (0,6), abcccde none, abce none): the width-0 row must
  read the WIDEST width, not the narrowest.
- **S-g, respelled for E1's site**: `(ab)x\1*y` (abxaby, abxy, abxababy; abxa, abxaay none). The design's
  `(ab)x\1y` is 2a's (A_EMPTY arm) and reaches no E1 site. Here a repeated back reference
  has no literal run (`best.n == 0`) but consumes, so a row that reads the run instead of the width takes it
  (S1905).
- **E-2/E-3 and the anchor wrapper**: `abcd(?:)*efgh`, `abcd(?:\b)*efgh`, `abcd(?:\b)+efgh`, `abcd(?:^)*efgh`
  (the `pcrec_wrap_bare_anchor` `<anchor EMPTY>` under a quantifier), `abcd(?:$)?efgh`, `xy(?:(?=a))*abzw`,
  `ab(?:\B){3}cd`.
- **Sabotage rows** (S1905-S1908 used; S1909-S1914 unused). All four were detected by manual plants and their
  REACH probes printed their tokens.
  - **S1905**: the row tests `best.n == 0` instead of `maxw == 0`. Caught by W-R4 / S-g NOMATCH, both engines.
  - **S1906**: the row reads the min width (`pcrec_minw == 0`). Caught by W-R4 NOMATCH.
  - **S1907**: the walk ignores the restored arms (`w->restored = 0`). Caught by run_facts_checks [facts-arm]
    FAIL.
  - **S1908**: `pf_ask` stops inheriting the arm token. Caught by [facts-arm] FAIL.
- **[facts-arm]** (new section in `tests/codegen/run_facts_checks.sh`, 11/0) checks four things:
  - the default listing of `abcd(?:\b)*efgh` and its absence of tokens;
  - under `restore=empty`: the old run `65666768` on req_whole_run/req_run with `harness:empty`, the token on
    req_byte and req_pieces, and none on req_set;
  - that an unknown arm is refused.
- The lever fence (`tests/compound/run_lever_fence.sh`) allows the two new mentions. It PASSES.

## Spec and listing hunks

- `docs/spec/facts_listing.md` §4.1.3:
  - ¶1 now states the why column's first-match order: `harness:`, `deny:`, `decline:`, `rate:`.
  - New ¶4a (anchor `s4-1-3-p4a`) specifies `harness:<arm>[+<arm>...]`: test build only, which facts carry it,
    that the status is the derivation's own, and the `empty` arm's meaning. It does not spell the lever (the
    fence greps docs/spec). spec_history check 11/0.
- **No other caller-observable change.** The req facts' VALUES move, and facts_listing.md promises no fact
  values (§1: names and values are advisory).
- **CLAUDE.md** updated in: src/facts (walk_arms.def, req.c, sabotage anchors), cli (harness lever 6),
  tests/litscan (spanarms.rxt). Size check passes.

## Checks run

By hand, on the lane build:

- `make -j4`: clean.
- spanarms.rxt under the harness: 62/0.
- `run_facts_checks.sh`: 11/0 (the [facts-arm] section included).
- `run_lever_fence.sh`: PASS.
- spec_history: 11/0.
- `check_claudemd_size.sh`: OK.
- Mech: VALIDATE_ONLY 4/4. All 4 manual plants were detected and all 4 reach probes printed their tokens.
- The census model was sanity-checked on 14 hand patterns. ident_check was smoke-tested on a 2-pattern
  emit_sweep run.

OWED, queued as box-queue jobs, chained in this order, each hold-aware (no start 19:00-01:00):

- `main-sae1-census` (prio 200): census_e1.py over the corpus and the bench.
- `main-sae1-ident` (201): emit_sweep every stream plus ident_check.
- `main-sae1-maketest` (202): `make strict`, then `make test` via perfrun (PC-3 included).
- `main-sae1-axes` (203): `AXES=--harness=restore=empty make test-axes`.
- `main-sae1-mech` (204): S1905 S1906 S1907 S1908.

Job scripts are in `$PCREC_TMPDIR/scratch/sae1/jobs/`. The logs are written under `scratch/sae1/` (census/,
ident/, maketest.log, axes.log, mech.log).

## STATE AT HANDOFF

- Branch lane/sae1 holds 681f42444 (code, witnesses, sabotage, spec), 2edd3f011 (census and identity tooling,
  emit_sweep --movers-out), and this report's commit. Base: lane/u3mech 404cff6ea.
- Queue keys: `main-sae1-census`, `main-sae1-ident`, `main-sae1-maketest`, `main-sae1-axes`, `main-sae1-mech`.
  They were queued at about 10:00 behind the kit's 567-569 mech shards.
- Rulings file `docs/dev/lanes/sae1_rulings.md`: empty at every read, the last at handoff. No entry applied.
- **Open for the manager (reply either way)**: should E-4's m >= 1 half (`(?:\b)+`, `(?:^)+`) stay moved under
  E1, as T2 row 1's `all = true` gives today, or be narrowed to E2 by one row?
- Known limitation: the restore arm does not reach compound parts (`src/core/compound.c` gives each part
  `.harness = NULL`), so `test-axes`' `restore=empty` arm compares compound artifacts against themselves.
- No kit facts to relay. No memfn/ edits.
