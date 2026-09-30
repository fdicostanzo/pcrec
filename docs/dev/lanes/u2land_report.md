# u2land report — [UCP] U2 landed onto current main (2026-09-29, sonnet)

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
