# spanarms4 report: docs/design/span_arms.md rev 2.1 (review 2026-11-08 r3 as ruled)

Lane spanarms4, sonnet, 2026-11-08. Text only (NO BUILD GO: nothing under `src/`, `cli/`, `lib/`,
`memfn/`, `tests/` touched). Base: main `9161402da`. Compiles: a handful of `--emit-facts` /
`--emit-main` runs of the main tree's `build/pcrec`; no suites.

## Summary

Rev 2.1 applies READY-1..10 of `docs/dev/reviews/2026-11-08-r3-spanarms3.md` as RULED. Touched:
L1's text only (§3.7's `look` cell and `harness:` bullet, §5.1, §5.2's EMPTY-MEET and "(others)"
rows and (g), §5.4 A12, §5.7's mechanism sentence and the W-C1/W-T1/W-S4/W-D rows, §5.8, §8's L1
gate, §9's two L1 rows, §11 point 2, the §12 D168 addendum) plus the new §R3 disposition table
and the status paragraph. L2 and L3 rows are unchanged.

Observed at the main tree (`build/pcrec`, `9161402da`):

- `a(?=b)[bc]`: default `kinds none`, `RX_DFA_SCAN "cover"`, run none; `-fno-ctx-node`: `kinds
  lookaround`, VM, run none (today's values). `ab(?<=b)[bc]d\w*e` has run `6162@1` both ways
  (the vacuous W-C1 equality). `ab[xy](?=(?<=x)y)[xy]`: run `616278@1` today both ways.
- `--memfn=no-fd-pres-pick` is accepted; on `xy[ac]{12}abcdefghijkl(?<=l)q` the emitted C has
  `rx_reqrun_whole` 5 times against 0 by default, and `RX_REQ_RUN` stays the 8-position
  window `65666768696a6b6c@5`. W-T1's pattern has run none TODAY (needs R1), so its stamps
  `6262626262626262@7` are the review's, not re-observed here.

Choices the rulings left to the text (stated in it, no L1 rule changed): a dead
`req_whole_run` is status `derived` (`pf_done_why`'s `decl` list is unchanged); W-D numbering is
W-D1..W-D7 (W-D7 = W-T1's pattern listed NOT dead, W-D5 the structural note); `harness:` sits on
`req_whole_run` and the facts derived from it at L1.

## Disposition table

| id | ruling | applied | where |
|---|---|---|---|
| READY-1 | FIX-NOW | fourth condition (window); W-T1 under `--memfn=no-fd-pres-pick`, listing row, W-D7; other L1 witnesses re-checked (all runs at most 8 positions) | §5.7, §8 |
| READY-2 | FIX-NOW | W-D5 a structural note | §5.2 (g), §5.7 |
| READY-3 | FIX-NOW | `WIT` additions written into the gate text (script untouched) | §5.7, §8 |
| READY-4 | FIX-NOW | rows where the equality can fail named | §5.1, §5.7, §8, §11 |
| READY-5 | FIX-NOW (form) | why values: `dead` > `harness:` > existing; facts carrying them | §3.7, §8, §9 |
| READY-6 | FIX-NOW (form) | addendum: members, widening, bound, non-members | §12 |
| READY-7 | FIX-NOW | A12 census, status, `dead` vs `decline:dead-start`, prototype, cli/main.c cites, harness binary | §3.7, §5.4, §9 |
| READY-8 | FIX-NOW | S-L in L1's gate | §8 |
| READY-9 | FIX-NOW (one cell) | `look` = E-5 as E2's plain unit | §3.7, §5.8 |
| READY-10 | FIX-NOW | plant per dead member; W-D1..W-D7 numbered | §5.2, §5.7 |

## STATE AT HANDOFF

- STATE: delivered. Branch `lane/spanarms4`, committed. Rulings file
  `docs/dev/lanes/spanarms4_rulings.md` was empty at every re-read (no entry applied).
- Validation: text lane, no suites owed.
- Open for the manager:
  1. W-T2 and W-T3 (L2/L3, text not touched here) have the same shape as READY-1: their
     sabotage `a^8 b^20` and the correct `a^20 b^12` agree on the first 8 positions, so at
     default flags the emitted window may not tell them apart. The parallel L2/L3 readiness
     round should check it.
  2. `cli/main.c` line cites drifted since the review's base (`pin` is now built at `:2903`,
     passed at `:3145`); §3.7 cites `9161402da`. The `:1430-1443` `PcrecHarnessOptions` cite
     was not re-checked.
  3. After the L2/L3 readiness round, L1 goes to Frank with the REP+EMPTY half (ruled).
