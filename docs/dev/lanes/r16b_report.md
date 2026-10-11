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

Logs: `build/r16b-logs/` in the worktree (gitignored). `g2s1.log` is the
G2 SIMD run, `light/` the chain (`light/chain.log` is its summary).

### 4.1 G2 SIMD family, `--quick` (`run_g2_simd.py`, g2s1.log, on fb77abac + the G2 edit, floors MEASURING)

RESULTS_G2

### 4.2 Suites, identity sample, sabotage

RESULTS_CHAIN

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

CHECKLIST
