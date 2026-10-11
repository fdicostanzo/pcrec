# r16b — R-16: KB (the second vrun filter position) at w32 only

Lane r16b, build lane for the memfn kit manager, 2026-10-11. Branch
`lane/r16b` off the kit branch `lane/memfn-r16` (afc74283). Request R-16
(memfn/docs/requests.md), Frank's Q-R14-1 ruling, D147 addendum 16.
Sabotage ids S815-S819 (all five used; next free S820).

## 1. What changed

- **memfn/src/vrun.c.** The form's per-level table `ops_of[]` (already the
  one home of the level's intrinsic spellings, indexed by the levels.def
  id) gains `npos`, the filter positions the level reads: 1 at
  `LV_X86_W16`, 2 at `LV_X86_W32`. `vrun_kb(x, v)` returns no KB where
  `v->npos < 2`, before the deny test (kept on its own line, so S753's
  anchor did not move). The renderer passes its own level's ops, so the
  w16 helper reads KA alone wherever it renders: standalone (`vrun-w16`)
  and as `vrun-w32`'s rung. No magic constant and no second mechanism:
  the level decides, through the same table the level's text comes from.
  `--memfn=no-vrun-kb` is unchanged: no KB at any level.
  - Knock-on, by construction: the trim's proven list follows the filter
    (`vrun_proven(x, k2, ...)`), so the w16 verify compares KB's position
    again. The padded word and the words compare move with it (the diff
    in §3 shows it).
- **Module comment:** SECOND FILTER POSITION (HOW MANY is now per level,
  RULED, with the slot21 figures and the rung case), DISTANCE (the level,
  not the distance, decides), the over-read bullet (`{KA, KB}` → `{KA}` at
  w16), the D149 table's KB row (RULED, D147 add. 16, no longer an
  UNMEASURED DEFAULT), the guarded-bytes comment.
- **Re-pins.** These are measured by G2's SIMD family, §4.
  - `VRUN_W16_GUARDED_MAX` and `tests/memfn/simd_bounds.tsv`'s `vrun-w16`
    go from 2,700 to 2,400. The w16 alone worst is 2,383, exactly R-13's
    KA-only figure. The file's rule is the measured maximum rounded up to
    the next 100. w32 stays at 2,800 (2,721 measured).
  - The same number in `docs/spec/limits.md` §8.3¶3 (a caller-visible
    bound) moves to 2,400. integration.md's batch-1 note gets the matching
    clause.
  - `RX_SIMD_GUARDED_BYTES` moves at `-fmemfn-simd` only, on every vrun
    artifact. Example: (?i)cat goes from 0xe48 to 0xd73. It reads 0 at
    SIMD-off.
  - G2 `VSHAPE_FLOOR['none']` goes from 19 to 8, because the measured
    count fell from 24 to 10. A w16 helper no longer covers a two-byte run
    whole, so it now verifies. The other verify-shape measurements moved
    slightly and their floors hold. The comments carry the new figures.
- **G2's SIMD family (memfn/tests/run_g2_simd.py)**: the filter rule is
  per level (`KB_LEVELS = {'w32'}`, a literal from the ruling); the final
  block's mask is now held to the rule as well as the whole block's; new
  per-level K35 populations `KBLVL_FLOOR` (§4).
- **tests/cli/run_cli_tests.sh** (?i)cat case: default w32 mask 2 loads,
  w16 mask 1; deny 1 and 1.
- **tests/memfn/simd_accept.tsv**: `vrun-kb`'s two w16 lines are removed.
  The file's rule is "their lines are the levels they move", and the deny
  no longer moves w16.
- **docs/spec/**: registry.md §6¶8a (the `vrun-kb` and `vrun-trim` rows)
  and tuning.md §2.43¶3b now say the 32-byte row reads the second
  position and the 16-byte row reads none. limits.md §8.3¶3 carries the
  bound (above).
  - Is this caller-observable? Yes, at `-fmemfn-simd` only: the artifact's
    w16 helper text and its guarded-bytes stamp. No SIMD-off byte, no
    entry, flag, option row or diagnostic moves.
- **CLAUDE.md**: memfn/CLAUDE.md, memfn/src/CLAUDE.md (vrun.c entry),
  memfn/tests/CLAUDE.md (run_g2_simd.py entry), tests/mech/CLAUDE.md (an
  R-16 section).
- **No options.def / --list-axes change** (no row added), no levels.def
  change, no pcrec source touched, no abi event.

## 2. Where the structural check lives, and why there

The brief asked for a check that the w16 helper has exactly one filter
compare and the w32 helper two when ranked and not denied, counting
populations, with a control independent of the renderer. It lives in G2's
SIMD family's ranking check (1b), not in the form checks or the rows check:

- **Why G2 1b.**
  - It already parsed every rendered helper's mask loads and held them,
    in order, to a filter rule derived from the GENERATED ranking entries.
    That rule is written in the checker and shares no source with vrun.c.
  - It already ran in `make test` (`test-memfn-g2` → run_g2.sh section →
    run_g2_simd.py).
- **Why not the others.** tests/memfn/form_checks.py (C12-C14) scans
  pcrec's emitter sources, not kit helper bodies. rows_check.py checks
  table metadata. Neither reads a helper.
- **What changed in 1b:**
  - The rule is keyed by level (`KB_LEVELS`, a literal from D147 add. 16).
  - The final block's mask (`subject + f`) is now checked too. Before
    R-16 only the whole block's was, so a final-block-only fault was
    invisible to the structure check (S818).
  - Per-level helper populations with floors: `kb-read-w32`,
    `kb-dropped-w16`, `kb-dropped-rung` (the w16 helper of a site that
    also rendered w32, the fall-through case). A population with no floor
    entry is red.
- **The pcrec-artifact witness** is the cli (?i)cat case (one artifact,
  four helper counts).

## 3. SIMD-on: only the w16 helpers move

Diffs base (afc74283 build, `build/r16b-ref/pcrec`) vs tree, `-p rx`, seven
witnesses (`build/r16b-ref/diff/on.diff`):

| pattern | SIMD-off | SIMD-on changed lines | of which `__m256` lines |
|---|---|---|---|
| `(?i)cat` | identical | 14 | 0 |
| `(?i)union.*?select.*?from` | identical | 14 | 0 |
| `(?i)enzyme` | identical | 14 | 0 |
| `SELECT`, `(?:username\|USERNAME\|user\|USER)=`, `it\Nm`, `abcdefghijklmn` | identical | 0 (no vrun site / KA-only ranking) | 0 |

Every changed line is inside `rx_*__w16`:

- the broadcast line (`mb`/`vb` gone);
- the whole-block and final-block masks (the KB compare and its AND
  gone);
- the verify (KB's position compared again: the padded word's `pk`/`pt`,
  or the words compare);
- the `RX_SIMD_GUARDED_BYTES` stamp.

The w32 helper still loads at `i` and `i + 1` on (?i)cat.

## 4. Validation (light; this box, `taskset -c 12-15`, `-j4`, gcc 15.2)

Logs: `/home/pcrec/projects/pcrec/worktrees/r16b/build/r16b-logs/`
(gitignored). `g2s1.log` is the first G2 SIMD run, `light/` the chain
(`light/chain.log` is its summary).

### 4.1 G2 SIMD family (`run_g2_simd.py`, quick)

- **1,616 passed / 0 failed** at the final tip (`light/test-memfn-g2.log`,
  inside the G2 quick tier). The first run (`g2s1.log`, before the floor
  re-pin) was 1,615 / 1: `verify shape none 10 < floor 19`, the expected
  move, re-pinned (§5).
- Every build: 19,250,552 answer checks, 0 fails, 0 faults (x86-64,
  x86-64-v3, x86-64-v4, gpr-only, asan-x86-64-v3). Every plant RED where its
  level is live, green where compiled out.
- Filter rule (1b), now per level, whole AND final block: green on every
  rendered helper. Per-level populations: `kb-read-w32` 192,
  `kb-dropped-w16` 191, `kb-dropped-rung` 178 (floors 154 / 153 / 142).
  Filter-shape populations unchanged: 205 / 93 / 82 / 109 / 135.
- Verify shapes: none 10, gap 342, whole 34, bytes 71, words 447, padded 172.
- Guarded bytes: alone w16 2,383 (bound now 2,400), alone w32 2,721 (2,800),
  `vrun@w16` 1,683, `vrun@w32` 2,289, `vrun@w32+w16` 4,975 (bound 5,200).

### 4.2 Suites, identity sample, sabotage

Chain `build/r16b-logs/chain.sh`, summary `light/chain.log`, at 115f8c58
(the code is unchanged since; the only later commit is this report). All
runs used TMPDIR in the worktree.

| check | time (EDT) | verdict |
|---|---|---|
| `make -j4` | 13:21:37 | rc 0 |
| `make strict` | 13:21:37-13:21:48 | rc 0 |
| `make test-cli` | 13:21:48-13:22:01 | rc 0, 284 passed / 0 failed |
| `make test-memfn-rows` | -13:22:02 | rc 0, 157/0 (check F: the vrun-kb w32 lines) |
| `make test-memfn-forms` | -13:22:02 | rc 0, 5/0 (`run_form_checks.sh`) |
| `make test-memfn-arms` | -13:22:03 | rc 0, 364/0 |
| `make test-memfn-deleg` | -13:22:03 | rc 0, 5/0 |
| `make test-memfn-arch` | -13:22:11 | rc 0, 15/0 |
| `make test-memfn-stamps` | -13:22:37 | rc 0, 25/0 |
| `make test-memfn-guarded` | -13:24:00 | rc 0, 10/0 |
| `make test-memfn-simdfloor` | -13:24:46 | rc 0, 51/0 (`run_simd_floor.sh`) |
| `make test-memfn-rank` | -13:25:02 | rc 0, 11/0 |
| `make test-spec-history` | -13:25:05 | rc 0, 145/0 |
| `make test-registry` | -13:25:56 | rc 0, 79/0 |
| `make test-codegen` | -13:30:04 | rc 0, 27/0; [SABANCHOR] all 687 rows resolve |
| `make test-memfn-g2` (G2 quick, ~7 min here) | 13:30:04-13:37:16 | rc 0, 52,987,686 / 0 |

The first chain at fb77abac+G2 went red twice:

- **test-cli, 2 cases.** The r14b/r14p trim and pad cases read the w16
  helper's verify, and the w16 verify now compares KB's position. The cases
  now read the w32 helper, which keeps both filter positions, and the trim
  case asserts the w16 verify reads both A and T.
- **test-memfn-arch (C4), 5 hits.** The first S815/S816/S819 anchors quoted
  intrinsic names and `LV_X86_*`. The fix gave `npos` its own commented line
  so the anchors are arch-free. No allowlist row was added.

**Identity, light tier** (`scripts/emit_sweep.py --ref-bin <afc74283 build>
--every 8`):

- **SIMD-off** (`light/sweep_off.log`): 0 artifact movers on c-default,
  c-vm and emit-ir-vm. The streams run the whole argv population (5,621
  rows, reach 5,170 / 5,171). The 7 registry dumps also have 0 movers, so
  `--list-axes` is unchanged. Self-check passed.
- **`--extra=-fmemfn-simd`** (`light/sweep_on.log`): 44 movers on
  c-default, 43 on c-vm, 0 asymmetric. rc 1 is the expected mover verdict.
  The classifier `docs/dev/lanes/r16b_movers.py` covers every distinct
  corpus pattern (4,531), both engines (8,307 pairs); its log is
  `light/movers_full2.log`:
  - 39 movers;
  - 39 base artifacts have a w16 KB, and all of them moved;
  - every changed line is inside a `__w16(` helper (230 lines) or the
    guarded stamp (39);
  - 0 bad.
  The sweep counts more movers than the classifier because its population
  is argv rows with per-block flags.
  - The first classifier run flagged 3 movers as having no w16 KB. That was
    a classifier bug: an exact KB position broadcasts `vb` with no `mb`. The
    fixed run is the one cited above.
- **`--extra="-fmemfn-simd --memfn=no-vrun-kb"`** (`light/sweep_deny.log`):
  0 movers on both streams. The deny arm is the pre-R-16 rendering.

**Sabotage**: `PROCS=1 bash tests/mech/run_sabotage_matrix.sh SNNN`, solo,
at 115f8c58 (`light/sab_SNNN.log`). Every row's mech trailer reads
`unexpected 0, undetected 0, unreached 0, anomalies 0`.

| id | plant | arms | verdict |
|---|---|---|---|
| S815 | w16 `npos` 2: KB back at w16 | cli g2simd | DETECTED, cli 2 fail / 284 pass, g2simd 376 / 1,241 |
| S816 | w32 `npos` 1: KB at no level | cli g2simd | DETECTED, cli 3 / 284, g2simd 376 / 1,240 |
| S817 | KA alone only where vrun-w32 is denied: the w16 rung keeps KB | cli g2simd | DETECTED, cli 2 / 284, g2simd 349 / 1,267 |
| S818 | the final block's mask drops KB, the verify still trims it | g2simd | DETECTED, g2simd 196 / 1,420 |
| S819 | the trim takes the ranking's KB as proven at w16 | g2simd | DETECTED, g2simd 191 / 1,425 |
| S753 | (rankuse, re-run) the vrun-kb deny ignored: the deny-at-w32 fault | cli g2simd | DETECTED, cli 1 / 284, g2simd 22 / 1,594 |

Only the structural check (1b) can see S815 and S817. Their answers stay
right, because KB is a run position and the verify covers it. S818 and S819
are also wrong-answer faults.

## 5. Re-pins, each with its reason

| pin | was | now | why / rule |
|---|---|---|---|
| `VRUN_W16_GUARDED_MAX` (vrun.c) | 2700 | 2400 | the measured alone max at w16 is 2,383. The rule is "max over G2's SIMD family, rounded UP to the next 100" |
| simd_bounds.tsv `vrun-w16` | 2700 | 2400 | the same number. The file says the kit states the same |
| docs/spec/limits.md §8.3¶3 | 2,700 | 2,400 | the caller-visible statement of the same bound |
| G2 `VSHAPE_FLOOR['none']` | 19 | 8 | measured 24 → 10. The rule is ~80% of the measurement |
| G2 `KBLVL_FLOOR` (new) | — | 154 / 153 / 142 | measured 192 / 191 / 178. The rule is ~80% |
| simd_accept.tsv | 4 vrun-kb lines | 2 (w32) | "their lines are the levels they move" |
| cli (?i)cat case | w16 2 loads / deny 1 | w32 2, w16 1 / deny 1, 1 | the ruled rendering |

These did NOT move:

- The pcrec abi.
- Any SIMD-off byte.
- `VRUN_W32_GUARDED_MAX` (2,721 measured, bound 2,800).
- The `vrun@w32+w16` token's measured max is 4,975, inside the sum
  2,400 + 2,800.
- The --list-axes / options.def rows and the registry floor.
- The G2 filter-shape floors: their counts are the ranking's, read with
  the w32 rule, and are unchanged at 205 / 93 / 82 / 109 / 135.

## 6. Owed (the kit manager's slot, on main's GO)

1. **Full identity sweep, every arm, both layers**, against afc74283:
   - `scripts/emit_sweep.py --tree . --ref afc74283` at default, with
     `--arms start` and with `--variant all`.
   - The same at `--extra=-fmemfn-simd`: only vrun artifacts may move, and
     only their w16 helper and the guarded stamp.
   - The same at `--extra="-fmemfn-simd --memfn=no-vrun-kb"`: expected 0
     movers.
2. **G2 full** (`make test-memfn-g2-full`).
3. **mech** for S815-S819 and S753 in the full matrix, plus [SABANCHOR].
4. **`make test`** via `scripts/perfrun --label r16b`.
5. **Re-timing** (slot21's cells, w16 vs w16 + `no-vrun-kb` should now be
   identical text; w32 KB vs deny unchanged). Official verdict: the bench
   on the target hardware (D144 addendum 4).

## 7. Charter vs committed

| promise (brief) | artifact / status |
|---|---|
| KB rendered only at w32; w16 KA alone, standalone and as w32's rung | DONE. vrun.c `ops_of[].npos` keyed by the levels.def id; §3, S815/S817 |
| no magic constant, no separate mechanism | DONE. The per-level table the level's text already comes from (§1) |
| module comment: SECOND FILTER POSITION, D149 KB row RULED (D147 add. 16), reach/guard text | DONE (§1) |
| `--memfn=no-vrun-kb` keeps its meaning (no KB at any level) | DONE. Deny sweep 0 movers; S753 DETECTED |
| guarded-bytes figures re-derived, re-pinned by their rules | DONE. w16 2,700 → 2,400 in vrun.c, simd_bounds.tsv and limits.md §8.3¶3; w32 unchanged (§5) |
| `make -j4`, `make strict` | DONE, rc 0 |
| SIMD-off byte-identical, no abi event | DONE light (every-8 sample, 0 movers on 3 artifact streams + dumps). Full sweep: OWED to the kit manager's slot (§6 item 1) |
| SIMD-on: only the w16 helpers move | DONE. Seven witnesses (§3) plus the whole-corpus classifier, 0 bad (§4.2) |
| test-memfn-rows, form checks, run_simd_floor.sh | DONE, green (§4.2); no floor in them moved |
| G2 quick tier | DONE, 52,987,686 / 0 (light enough here, ~7 min); G2 `none` floor re-pinned |
| structural check counting populations, control independent of the renderer | DONE in G2 1b (`KB_LEVELS`, whole + final block, `KBLVL_FLOOR`), with the cli (?i)cat witness (§2) |
| sabotage S815-S819, as many as real faults, figures recorded | DONE, all five used, all DETECTED solo (§4.2); S753 re-run |
| no --list-axes / options.def change | DONE. None (dumps 0 movers) |
| CLAUDE.md updates (memfn, memfn/src, memfn/tests, tests/mech) | DONE |
| docs/spec only if caller-observable | DONE. Three hunks for the SIMD-on artifact text and the w16 bound (§1); nothing SIMD-off moves |
| full identity sweeps every arm, G2 full, mech, make test, re-timing | OWED: kit manager's slot on main's GO (§6) |
