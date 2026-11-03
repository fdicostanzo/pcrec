# sp1f — span_pick stage 1, unit 1f (retire R8/R1/R2, their denies, the pay rule)

Lane sp1f (opus), branch `lane/memfn-sp1f`, cut from main 761521515 (unit 1a landed). Design of
record: span_pick.md rev 5.2 §Staging unit 1f. Build go: the owner's conditional approval, confirmed
by main's GO. Scope: unit 1f only; nothing from any other unit.

## What changed

Commits on `lane/memfn-sp1f` (oldest first): 03c883736 (kit code), 7137bf321 (readers), 9fad5facf
(history, journal, CLAUDE.md/NOTES), 7958e6627 (S917's text), then this report. 22 files, +178 -548.

- **The finder rows R8, R1, R2** (`memfn/src/finder.c`): deleted, with their contracts (`ct_r8`,
  `ct_r1`, `ct_r2`) and the uses only they declared (`use_mn`, `use_mn_kind`). Also deleted, because
  only these rows read them:
  - the comparator kinds `FL_N` and `FL_E_G`, and `fd_holds`' KN_N check;
  - the facts SF_E_MEASURED and SF_TERMINAL_FAST (bits 6 and 7, reserved, never reused);
  - the `<t>` key template, with `key_expand`'s branch for it;
  - `fd_phase`, `fd_x.phase`/`terminal` and `layer_name`.

  `fd_lhs` is now `{ FL_NONE, FL_KEY }`. The FO_IN/key2 vocabulary stays. 1a's precedent is to
  delete only the comparators the deleted rows read, and S1020/S1122 anchor on that vocabulary. Ids
  are reserved and logged in `memfn/docs/finder_history.md`.
- **The residual N step and the §2.5 pay rule**:
  - Deleted: `n_interval`, the interval carving, `nforms_of`, the multi-piece merge, `FD_INF`,
    `FD_MAXPIECE`, `fd_pay`, `fd_pay_in`, `pay_fill`, the row field `pay` and the listing's pay keys.
  - Their public entry is deleted too: `mf_finder_pay`, `mf_pay_operands`, `MF_PAY_MAXPT`.
  - `fd_decision` is now one row and its pick, and `fd_decide` is one `kit_walk` plus `fd_pick_of`.
  - `fd_route` keeps `if (d.terminal >= FD_NROWS) return NULL;`, S1079's anchor.
  - The listing's `unpaid` column stays, FF_UNSTATED (`-`) on every row. This keeps S1020/S1122's
    anchors, and finder_check A now asserts the column is `-` on every row.
- **The denies `fd-r8` and `fd-ndisp`**: deleted from `memfn/src/options.def`. `--memfn=no-fd-r8` and
  `--memfn=no-fd-ndisp` are now refused as unknown options (rc 1, checked).
- **MF_SITE_ABI 20 -> 21 and MF_CLASS_V 6 -> 7** (`memfn/include/memfn.h`, with history lines; the
  CLAUDE.md in `memfn/include` was updated to match):
  - MF_SITE_ABI moves because the entry and the two options leave.
  - MF_CLASS_V moves because three rows left ahead of the PRES rows, so the `pres_row` indices move by 3.
  - No layout move.
  - Recorded in `memfn/docs/journal.md`. The responses-ledger line is the kit session's to write
    (single writer): **for the kit manager**.
- **Readers.** These are the design's list re-grepped, plus the extra readers marked "not listed":
  - `tests/memfn/arm_fixtures.c`: `--pay-grid`, `pay_mode` and their usage text.
  - `tests/memfn/finder_check.py`:
    - A: 10 rows, and no row lists an unpaid pick.
    - H (the pay grid): retired.
    - I: re-aimed. ONESHOT is accepted, the fd gate is asked, and no gate record names `body`. The
      old "a row decided" check read R1's decision, and no FIND row decides the `set10` fixture now.
    - J: `fd-r8` and `fd-ndisp` are retired denies.
    - `WITHDRAWN_ROWS` gains R8/R1/R2.
  - `tests/memfn/rows.tsv` and `row_floors.tsv`: three lines each removed, and the header note updated.
  - `tests/memfn/run_rows.sh` `ROWS_FLOOR` 33 -> 30 (not listed in the design).
  - `tests/memfn/rows_check.py`: a comment.
  - `tests/axes/memfn_arm.py`: four ASSERT_ZERO entries.
  - `scripts/emit_sweep.py`:
    - `DIFFER_PINS`, `ASSERT_ZERO` and `IDENT_MEMFN` lose `fd-r8`/`fd-ndisp`, leaving 12 memfn arms
      (67 identity arms, 69 before).
    - New `--dumps-declared-gone FLAG:KEY[,...]`: stream 5's declared REMOVED registry rows, judged
      both ways. A missing declared row, an extra removed row, or a declared row still present at
      HEAD is red. It was tested against the base: declaring both rows is green; declaring one, or
      adding a row still at HEAD, is red.
    - Declarations now apply only to the real comparison, not the ref-vs-ref self-check. The
      existing `--dumps-declared-rows` also failed its own self-check when given; this fixes that.
  - `memfn/src/CLAUDE.md`, `memfn/data/cards/CLAUDE.md`, `memfn/data/sets/CLAUDE.md`,
    `scripts/NOTES.md`.
- **Mech**:
  - S1025 (pay-tie) is RETIRED: its file is deleted, and the reason is recorded in
    `run_sabotage_matrix.sh`'s memfnfinder block. It planted in `fd_pay` and was detected through
    `mf_finder_pay`/`--pay-grid`, and both are gone.
  - S917's UNREACHED reason text names the 1f deletion. Its REACH_POP `\{ FL_KEY,` is unchanged and
    still reads 0 (declared UNREACHED).
- The kit's keys (`kit.lstar.*`, `kit.g8.*`, `kit.xover.*`, `kit.block.W64`, the pay operands) stay
  in the sets, unread.

## Caller-visible changes and spec hunks

- `--list-axes`: the `memfn` section loses the rows `fd-r8` and `fd-ndisp` (14 -> 12 rows).
- `--memfn=no-fd-r8` and `--memfn=no-fd-ndisp`: now refused as unknown options. Both were inert:
  they moved no byte on any compile.
- Spec hunks, all in `docs/spec/registry.md`:
  - §6¶8: the floor is "raised in every change that adds a kit row and lowered in the change that
    retires one".
  - §6¶8a: the `fd-r8` "layer simd" exception is removed. The retired list adds R8/R1/R2 with
    `fd-r8`/`fd-ndisp`, and names `--memfn=no-fd-r8`/`no-fd-ndisp` as unknown options. The `fd-r8`
    and `fd-ndisp` table rows are removed.
  - §6¶8b: `memfn` section floor 14 -> 12. `axes_registry_check.sh` reads "12 row(s), floor 12";
    245 checks pass.
- No hunk in `cli.md`: it names neither deny nor the count. No `match_api.md`/`tuning.md` hunk: no
  emitted byte, stamp or abi moves.

## Witness

Byte-identical by construction: no compile ever reached R8/R1/R2 (their forms were never built).
Checks run in the lane, all light:

- `make strict`: clean.
- `make test-memfn-finder`: 1924 passed, 0 failed.
- `make test-memfn-rows`: 213 + 56 passed. The census and its plants are green, with backstop hits
  35 against floor 30.
- `make test-memfn-link`: 11 passed.
- `axes_registry_check.sh`: 245 passed.
- `reach_equal.py --limit 40` (job 588's sample, 3 arms), `--gone fd:R8,fd:R1,fd:R2`:
  - The derived gone set equals the declared one: fd/R1, fd/R2, fd/R8.
  - The base counts were chosen 0 and asked 0 on every arm, so the design's SUSPECTED nonzero
    `asked` did not show in this smoke.
  - differ=0.
- emit_sweep base-arm smoke on the 25 sample patterns with `--dumps-declared-gone`: movers 0 on
  every stream, and the declared `--list-axes` delta of 2 rows was judged both ways. rc 0.
- Mech `REACH_ONLY` on the 50 rows: reached 29, unreached 0, declared-unreached 2 (S917, S919),
  now-reached 0, no-probe 19.

The verdict is the queue chain: jobs 330-339 (Queue jobs).

## Census and ratchet

- Roadmap §5 R20-R27, recipes as 1a ran them, at base 761521515 and at HEAD:
  - base: R20=3 R21=1 R22=3 R23=1 R24=2 R25=1 R26=0 R27=0, total 11;
  - HEAD: identical, total 11.
  - Deltas: none, as the design expects. No R row counts the pay rule or R8/R1/R2.
- Decider census: MEMBER_COUNT stays 50. 1f deletes no member: `fd_pay`, `pay_fill` and
  `n_interval` were never members. The map is unchanged.
- Backstop hits went 36 at base 761521515 to 35 here (measured: `decider_census.py --root` on both
  trees). The hit that left is `if (lo0 < lo)` in the deleted residual-N interval carving inside
  `fd_decide`. HIT_FLOOR 30 still holds; no re-pin.

## Kept counted names

None are kept as a thin caller for a retired mechanism.

`fd_decide` (a census member, T-FIND/T-PRES, retiring unit `-`) is kept and SIMPLIFIED: it is now one
`kit_walk` plus `fd_pick_of`, with the multi-piece residual step gone. It remains the T-FIND/T-PRES
decider that `fd_route`, `fd_find` and `fd_pres` call, so it is not a stub. `fd_route` and `fd_find`
keep their census rows, retiring at 1e.

## Queue jobs

Scripts are in `/var/tmp/pcrec-pcrec/scratch/memfn/sp1f/jobs/`. Every one was dry-run green.

- One stage per job, cap ≤ 3600, chained with `after`.
- The first job is gated `after kit-mech1a-b`.
- Every expect regex covers its labels, digits included.

| # | key | stage | est s | after |
|---|---|---|---|---|
| 330 | kit-sp1f-strict | make strict | 240 | kit-mech1a-b |
| 331 | kit-sp1f-memfn | test-memfn-{rows,finder,link,g2,arms,stamps,deleg,manifest}, test-findings, test-registry | 900 | kit-sp1f-strict |
| 332 | kit-sp1f-reach | HEAD MF_TRACE build; reach_equal.py, 16 arms (1a's 18 less the two retired denies), `--gone fd:R8,fd:R1,fd:R2`, corpus + 417 patterns | 1100 | kit-sp1f-memfn |
| 333-335 | kit-sp1f-ident1/2/3 | emit_sweep identity, 67 arms in 3 shards (23/22/22); the base arm adds `--dumps-declared-gone=--list-axes:fd-r8,--list-axes:fd-ndisp` | 2400 each | reach, ident1, ident2 |
| 336 | kit-sp1f-test | make test ALONE via `scripts/perfrun --label sp1f` | 1800 | kit-sp1f-ident3 |
| 337-339 | kit-sp1f-mech/mech2/mech3 | the 50 mech rows that plant in or read a changed file, 17/17/16 | 2400 each | test, mech, mech2 |

The 50 mech rows were found by grepping `tests/mech/sabotages/` for each changed path or basename,
excluding the matrix runner, CLAUDE.md, journal and NOTES files. Their bar is `== mech run
COMPLETE: N rows (unexpected: 0, undetected: 0, unreached: U, anomalies: 0, ...`. U is 2 in shard 3,
which holds S917 and S919, both declared UNREACHED, and 0 in the other shards. The pattern files are
the frozen bench list (392), `p588.txt` (24) and `pzzz.txt` (1), checked to total 417. The base
builds are `ref/build/pcrec` and `ref-mftrace/pcrec`, from a git archive of 761521515.

## STATE AT HANDOFF

- Queued (owed): kit-sp1f-strict, kit-sp1f-memfn, kit-sp1f-reach, kit-sp1f-ident1, kit-sp1f-ident2,
  kit-sp1f-ident3, kit-sp1f-test, kit-sp1f-mech, kit-sp1f-mech2, kit-sp1f-mech3 (jobs 330-339).
- Branch `lane/memfn-sp1f` is committed and clean, apart from untracked lane files.
- Jobs 330-339 are queued, gated after kit-mech1a-b.
- The DELIVER `owed:` line names the three mech keys.
- No known red. Open for the kit manager: the responses-ledger line (MF_SITE_ABI 21, MF_CLASS_V 7).
- Nothing from any other unit.
