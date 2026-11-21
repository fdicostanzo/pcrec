# u2land report — the kit's R-47 U2+U2b landed on main at abi 110 (2026-11-21, sonnet)

(This file name was used once before, by the [UCP] U2 landing of 2026-09-29; that report is kept
verbatim at the end, under "Earlier lane of the same name".)

## STATE AT HANDOFF

Landed on main, NOT pushed, commits by named paths only: merge `2d8beeb2a` (lane/memfn-k1108), abi
re-pin `1feeb3fe1` (111 -> 110, the last src commit), FILEPIN commit, then the ledger/plan/report
commit. `make -s strict` clean; `python3 scripts/plan_lint.py` 0 violations. RULINGS FILE
`docs/dev/lanes/u2land_rulings.md` exists and is EMPTY: last R-n applied: none. The three suites
(test-codegen, test-registry, test-rxtsource) are QUEUED behind other jobs in the box lock and had not
started when this lane handed back: OWED RUNS below. Cloud runs: see OWED RUNS.

OWED: none (the local suites and both cloud runs have since read green; see OWED RUNS).

## MERGE

`git merge --no-ff lane/memfn-k1108` (tip 2cdff1794 = the manager-ruled 994de281c plus one
memfn/docs/journal.md commit, three journal lines; the kit's validation was on 994de281c): clean, no
conflicts (47 files, +1876/-171). The kit's branch is not pruned (the kit's).

## PINS AND LEDGER

Every reader of the number was found by grepping `-w 111` unfiltered over src tests docs/spec
docs/testing.md memfn scripts and over the merge diff, and moved 111 -> 110 (seven readers):
`src/gen/emit_dfa.c` PCREC_ARTIFACT_ABI; `tests/codegen/run_codegen_tests.sh` ABI_EXPECT and the
failure message's 109->110 clause; `tests/mech/sabotages/S693_abi_not_bumped.sh` SAB_BEFORE (AFTER stays
109) and its re-aim note; `docs/spec/match_api.md` (the `#if`/`#error`/`#define PCREC_RX_ABI_H` block,
the rx_info table row, the §6 sentence: four lines of text, five spellings); `docs/dev/history/
abi_changelog.md` entry; the identity gate's (B) `FILEPIN` in `tests/codegen/run_recursion_identity.sh`
(re-pinned to `1feeb3fe1`, the re-pin commit, which is the last src-touching commit; ABASEPIN
unchanged, the kit reported (A) 0 differing). The plan.md [REQ-LOOKAROUND] reservation NOTE now reads
110 = U2/U2b (landed), 111 = L3. Left as is on purpose: the kit's own journal, responses, wake and the
bsu2/r75 review texts, which are records of what the kit stamped (they say 111 and say it was to be
re-pinned); `tests/memfn/pins/arms.tsv` and `docs/testing.md`'s "111" are unrelated numbers.
No emitted byte moved beyond the abi spelling.

Ledger: `docs/dev/full_suite_ledger.md` has a `major` line (kit byte move + abi event). D177
triggers: row 3 (a refactor or new engine path lands) FIRES; row 4 (2-3 majors since the last green
full suite) counts 2 (the L3 remodels and this); row 2 not applicable; row 1 discharged long ago.

## PLAN ROWS

[COVER-WIDTH-SIMD]'s status line no longer says the block span is absent from main; a NOTE on
[BSPAN-SCALAR-RISK] records the landing; [BSPAN-SCALAR-RISK] and [BSPAN-CLANG-DIFF] stay open. The
[MEMFN] umbrella's status line is at its 300-character cap (PL10), so the landing is recorded in the
ledger, the NOTE and the history index instead.

## PRUNE

None (the kit's branch is the kit's).

## OWED RUNS

VERDICTS (read after handback): local `make test-codegen test-registry test-rxtsource` EXIT 0, no `*** [...test-X] Error` lines; cloud u2land-test and u2land-recid GREEN (per main); main pushed at 68521b3ad. Nothing is owed. The text below is the state at handback.

- `scripts/boxlock run -- make test-codegen test-registry test-rxtsource`, queued 15:40 on 2026-11-21 and
  waiting behind other holders. Log: `/var/tmp/pcrec-pcrec/scratch/u2land/suites.log`; completion
  line `EXIT <rc>` at its end; verdict by `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` (none = green).
  Red: report the failing section; patch no pins beyond the number move.
- Cloud: `scripts/cloudrun --kind test` and `--kind recidentity` on the final landed sha (names
  `u2land-test`, `u2land-recid`), LAUNCHED on 9c93cfdac (cloud/main/test/u2land-test, cloud/main/recidentity/u2land-recid; proved by git ls-remote).

---

# Earlier lane of the same name (2026-09-29, [UCP] U2) — verbatim

## u2land report — [UCP] U2 landed onto current main (2026-09-29, sonnet)

Branch `lane/u2land`, from `lane/ucpu3` (9220d01e), merged with main
(31979ed3: [CLS-TREE] S1 + clstri + s1tri, clsid). Merge commit `aab32f9b`.
Not merged to main.

## Merge (four conflicts, resolved by hand)

- `tests/rxtsource/run_rxtsource_tests.sh` C3 pins, combined BY MECHANISM.
  clstri's re-pin (+318 census lines: litscan, offsetskip, recursion/k69,
  the [VAR] vars corpus, utf8 restrict) and U2's +230 SKIP (tests/ucp
  ctxnode.rxt +200 own-oracle, refusals.rxt -2 own-oracle, utf8/
  axis13_ctx_illformed.rxt +32 pcre2-only) touch disjoint populations, so:
  SKIP 16975 -> 17205, PCRE2ONLY 2966 -> 2998, OWNORACLE 12002 -> 12200
  (net +198), C3_VERIFIABLE 15881 unmoved (U2 moves no PASS/INFO/nopython/
  perr-accept cell). The Mac re-derivation confirms it: invariant tier
  holds on py3.9, PASS 12921 (identical to clstri's recorded Mac value),
  reconciliation 12921+7+18180+89 = 31197. CENSUS 254/4233/31197 matched
  without change. The py3.14 split tier (C3_PASS 13903, NOPYTHON 1964,
  PERRACCEPT 14, INFO 0) is U2-independent by the same argument and is
  owed to the Linux run's verdict (only a red there means it moved).
- `tests/mech/run_sabotage_matrix.sh`: both new arms kept (`ctxnode`
  from U2, `clskit` from S1), vocabulary entries and case bodies, with the
  `;;` between them restored. S337-S343 vs S360-S364: no id collision.
- `docs/dev/plan.md`: ucpu3's [UCP] row (the newer state) over main's older
  U2 sentence. `docs/dev/lanes/CLAUDE.md`: both entries kept.
- No conflict markers remain (grep over tracked files); `make` and
  `make strict` clean.

## Validation

- test-rxtsource (Mac, PROCS=2): 270 passed / 0 failed; one RECORD line
  (py3.9 split tier, the known darwin note).
- Mac targeted sections: `make -k PROCS=2 test-registry test-codegen
  test-anchored-match test-premul-table test-clskit test-cpset-structure`,
  log `/tmp/u2land_sec.log` (MAKE_RC= trailer). Verdict = `*** [test-X]
  Error` lines. STATUS AT HANDBACK: see the handback message.
- Linux: full `make test` on ubuntubudu at aab32f9b, launched detached,
  log `/home/duxevents/pcrec/worktrees/u2land-lx/u2land_test.log`, trailer
  `MAKE_RC=`. OWED. Verdict is the `*** [test-X] Error` lines; any red is
  diagnosed, not re-pinned blindly (a C3 split-tier red is the expected
  place to look, and means re-pinning from the Linux numbers with the
  mechanism stated).

## Cleanup (Linux)

    git -C ~/pcrec worktree remove --force worktrees/u2land-lx
    git -C ~/pcrec branch -D lane/u2land-lx
    rm ~/pcrec/worktrees/u2land-lx.bundle
