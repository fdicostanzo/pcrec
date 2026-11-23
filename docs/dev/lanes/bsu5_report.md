# bsu5 report: R-47 U5, card C6 + kit-grid@8 + the formhash SPAN shape (no timing)

Lane bsu5 (sonnet), branch lane/bsu5 cut from lane/memfn-k1108 @ b51fd80bd. Design of record: `docs/design/memfn/block_span.md` §8, §14 (U5), §10.2 "At U5". Build go: D201, "build with simd layer" (covers the formhash shape, renderer and entry; nothing else under `memfn/src/`).

## STATE AT HANDOFF

- Committed on lane/bsu5 (see `git log`): card C6 and its clang sibling C6c in `memfn/tests/span_forms/cards.py`, `kit-grid@8` row, the formhash SPAN shape, its renderer and the `span-vector` entry, `mf_form_entry.k`, the finder check's expectations, S2930 re-aimed, the CLAUDE.md/PROVENANCE hunks. No timing run of any kind was made.
- Rulings file `docs/dev/lanes/bsu5_rulings.md`: re-read at every checkpoint (before the first edit, at the WIP commit, before this report); it is EMPTY, so the last entry applied is NONE.
- U5 moves no emitted byte and needs no abi event (IDENTITY below: 356 of 356 compiles byte-identical). No stamp moved.
- Sabotage ids S3546-S3549: none taken. No D/K/R/abi number used.
- OWED: two box-queue jobs, `kit-bsu5-test` and `kit-bsu5-mech` (OWED RUNS). C6's and C6c's TIMING is owed to a window main clears (U6), on each bench box that runs V; nothing here has been timed.
- Stopped short of nothing the brief asked; three readings I made are flagged for the manager under CARD C6 ("OPEN POINTS").

## CARD C6

Where: `memfn/tests/span_forms/cards.py` (`CARDS`, `C6_*`, `check_c6`, `C6_RULE`); the row `kit span_vector 8 ...` in `memfn/data/cards/kit-grid.tsv`, header paragraph `ver 8`.

Declared as §8 states, in the shape of C1-C5 (a `CARDS` tuple of card, patterns, arms, regimes, layers, kind; the same cell, pool, gate and dry machinery):

- **One binary, two arms.** `V` = the default compile (`build/pcrec`, the shipped binary, not the harness: C6 times what ships), `H64` = `--memfn=no-span-vector` (H64@on at `-fmemfn-simd=x86-64-v3`). `deny changes wrapper, body and TU together; C6 times that combination on purpose` (§8).
- **A/A arm.** `H64.b`: the deny exe timed as both arms on each C6 pattern (one text, one layout pool: `arm_base` maps `H64.b` to `H64`, the same convention as the lit16 `aa`/`aa.b` pair).
- **Patterns, each width stated** (`C6_WIDTH`, `C6_SITE`, k = tested positions, `{n}` is k = n - 1):

| id | pattern | width | site | k |
|---|---|---|---|---|
| c6_hex32 | `[0-9a-f]{32}` | 32 | window (real: bounded/hex32) | 31 |
| c6_hexb32 | `\b[0-9a-f]{32}\b` | 32 | window (real: loglines/hex32-id) | 31 |
| c6_dig32 | `\d{32}` | 32 | scan (real: bounded/dig-exact-32) | 31 |
| c6_hex17 | `[0-9a-f]{17}` | 32 | window | 16 |
| c6_hex33 | `[0-9a-f]{33}` | 4095 | window | 32 |
| c6_hex1001 | `[0-9a-f]{1001}` | 4095 | window | 1000 |
| c6_dig25 | `\d{25}` | 32 | scan | 24 |
| c6_dig65 | `\d{65}` | 4095 | scan | 64 |

  The "window k 31 at width 32" bound cell is the real hex32 site (one text, one cell, not duplicated). The outside-bound cells (window k 15, 1001; scan k 23, 65) are CUT (both arms render today's bytes: A/A by construction), recorded in `plan`'s output. F2 DIFFERS patterns at width 4095: `C6_F2_DIFFERS = []`, because F2 (bsu3 report, "F2 AND THE GUARDED BOUND") matched 82 of 82 routed cells; a later DIFFERS adds its pattern there. `\b...\b` needs a hit-dense separator (`C6_SEP`, a space after a match; every other pattern appends nothing, so C1-C5's subjects are unchanged).
- **Regimes.** The six (`REGIMES`) plus `near-miss-in` at the window sites with k + 1 <= 255 (`regimes_of`): c6_hex32, c6_hexb32, c6_hex17, c6_hex33. The subject is 710's definition ported into `subject()`: runs of g members, g uniform in [ceil((k_tested)/2), k_tested], each followed by one non-member; answers gated against python `re` like every cell.
- **Counts.** `cards.py plan`: C6 156 cells (8 patterns x 3 arms x 6 regimes + 4 x 3 near-miss-in; 108 timed, 48 in the two approx regimes void by method as in C1-C5), C6c 60 cells (42 timed). Whole plan: 1590 cells (was 1374: AA 24, C1 480, C2 600, C3 144, C4 48, C5 78, C6 156, C6c 60), 289 distinct pcrec compiles. Expected wall (UNMEASURED constants): C6 0.02 h, C6c 0.01 h.
- **The rule (`C6_RULE`, printed by `plan`).** Sha recorded: 6351bff3901e3955 (job 710's rule, the DECISION_RULE text's own sha; `run-20261120T212920/meta.json` `rule_sha`; first line of `$PCREC_TMPDIR/scratch/memfn/blockconfirm/decision_rule.md`). APPLIES unchanged: the cell rule (FLOOR = max(0.15, spread(A), spread(B)); WIN / LOSS / TIE), the re-time, the N/A rule, the CPU-quiet control. DROPPED: the CONTROL clause (Hspk), the S (busy) clause and the verdict population built on it. REPLACED: the A/A line by the A/A arm (its repeated-LOSS-or-WIN rate printed beside the verdict).
- **Deny check in `dry`** (`check_c6`; the existing loop check reads arm I, which C6 has none of): per (pattern, layer) V and H64 render different text; H64 carries no V text (`__body`, selector, `__w32`); V carries the wrapper, and the `w32` level at the SIMD layer only. 11 pairs read, 0 failures. `dry` also gained `--cards C6,C6c` (a PARTIAL dry that names the C1-C5 checks it skips).
- **No timing command.** Nothing in `run` reads C6 (`C6_CARDS` is outside `STEP1`). The command that times C6 and the reader of its verdict (cell rule, re-time, N/A, quiet control, A/A rate) are U6's, owed with the window; `time_cells` is generic and would run the cells unchanged.
- **CANDIDATE and UNMEASURED:** the kit-grid@8 header says so; V stays CANDIDATE until C6 has run on each bench box that runs it (Zen 4 here; Zen 1 via main), a repeated LOSS on any box blocks the level (D155 item 2), a re-measure may raise a lower bound, never below 16.

OPEN POINTS (readings I made where §8 and 710's rule meet; each is a labelled UNMEASURED DEFAULT in `C6_RULE`, for U6's reader to rule):
1. **N/A needs call counts; §8 declares no profile arm.** 710 read them from a profile arm. I wrote: U6's reader takes them from an untimed instrumented build of the same cell, never a timed arm.
2. **710 re-timed a WIN only in an S cell; S is dropped.** I wrote: every WIN is re-timed too (wins are reported, never gated, so this costs launches, not the verdict).
3. **710's unit of an arm is three per-variant readings; cards.py's is LAUNCHES over a pool of 4 variants.** I wrote that LAUNCHES stand for them; `spread` is read over the launches.

## CLANG ARMS

**Built, as a sibling card `C6c`, declared by C6; it fits the "small declared column" test, so I did not stop.** The shape: one declared column and one function pair, read by `artifact` and `build_cell` only.

- `LAYER_FLAGS = LAYERS + {"off-clang": []}`, `CLANG` (env, default `clang`), `cc_of(layer)`; `LAYERS` (which the C1-C5 rule, drills and identity check iterate) is untouched, so no earlier card or drill sees the axis. `cc_ident(cc)` and `variant_key(.., cc)` carry the compiler into the exe cache key (r44 I's rule, now per compiler).
- C6c = the 3 real sites (§0.1), layer `off-clang` (the SIMD-off layer, clang 21 -O2 via the existing `build_cell` flags), arms V / H64 / H64.b, six regimes plus near-miss-in at the two window sites (60 cells). It says whether the V wrapper's text costs anything under clang, the thing the census found differing (§2.2.1 `wrap-clang`, D201 add. 5). Same one kit-grid@8 row: its `layer` dim carries `off-clang`.
- The pool's alignment variant is gcc-specific (`-mtune-ctrl`, loop/jump/label switches); clang gets its own odd variant `CLANG_ALIGN_OFF` = `-fno-align-functions -mllvm -x86-experimental-pref-innermost-loop-alignment=0` (labelled UNMEASURED DEFAULT in place). `dry` accepted every C6c pool (the r44 C refusal: each pool holds POOL_SIZE distinct layouts and at least 2 relative layouts: min 2, max 3; 0 pools refused), so the variant moves the code as the gcc one does.
- The unmeasured part: C6c has never been timed; clang's layout-variant flag is a default I chose, and U6's window owes its timing (it is a SIMD-off, compiler-axis run, on the box that has clang 21).
- Plan row [BSPAN-CLANG-DIFF] says this rides U5's C6 card: it does, as C6c. Main may want the follow-up item D201 add. 5 asked for to name C6c and the U6 timing.

## FORMHASH SHAPE

- **New shape `MF_FH_SPAN`** (kit.h, appended last: `mf_form_shape_id`), word `window-span`: a WINDOW REPORT site whose one span is ONE STRETCH of the entry's set, `k + 1` positions, every position core and verify-YES, the long_rows shape of `g2/g2_win_gen.c` and `g2_vspan_gen.c`; the heap lists are the span's own storage (R-28: no frame growth; `make test-memfn-link` passes). The art's byte-rate analysis states the set common (60,000 ppm; others 50), which is what routes the site to D-hors/T-vwin. The analysis object names no `digest` (finder check L bars kit sources naming it): left 0, the hash is identical to the run that set it.
- **New entry column `mf_form_entry.k`** (uint16, last): SPAN's k; 0 elsewhere. All 16 existing rows gained a trailing `0` (positional initializers under `-Wextra`).
- **Renderer:** one new `case MF_FH_SPAN` in `fh_render` (the one renderer path every instance uses); it checks the MEMFN_FORMS token the rendering reached equals the entry's `row`, else -1 (an instance that reaches another row is refused, never hashed as the id).
- **ONE entry:** `{ "span-vector", "-", canon 1, MF_FH_SPAN, row "span-vector@w32", set "0123456789abcdef", ..., target "x86-64-v3", k 40 }`. Hash a9efa02907d0645b. Its text shows `__body`, the `__w32` loop (`for (; i + 32 < 40; ...)`) and the selector, so a later text change moves the hash and stales the row.
- **`deps`:** `kit:form.span-vector` on the kit-grid@8 row. Readers moved with it: `tests/memfn/finder_check.py` (`FORM_IDS` + `span-vector`; `CARD_FORMDEP_COUNT` 20 to 21, printed "21 cards with a kit:form. dep"), `tests/memfn/arm_fixtures.c` (hash id list, a one-instruction edit row `i += 32` -> `i += 31`, `f_find_shape` includes SPAN so `--facts` states the site's lo/result/miss), docs: `memfn/src/CLAUDE.md`, `memfn/PROVENANCE.md`, `memfn/data/cards/CLAUDE.md`, `memfn/tests/CLAUDE.md`.
- **Hash/stamp/abi:** no emitted byte, stamp or `.abi` moved (IDENTITY): no abi event. `mf_form_hash` is a measurement identity, never in an artifact.

## IDENTITY

U5 moves no emitted byte. Base = this tree at b51fd80bd built before any edit (`base_pcrec`); mine = this tree at the commit. Each compile run with both binaries, `-p rxa --features all`, `-o X.c --pattern P` (which also writes X.h), at both layers (default and `-fmemfn-simd=x86-64-v3`): `.c`, `.h`, exit code and stdout/stderr byte-compared.

| population | compiles per binary | byte-identical |
|---|---|---|
| the 3 real sites (§0.1) x widths 32, 4095 x 2 layers | 12 | 12 |
| SPAN-SEED's 41 patterns (`tests/memfn/span_seed.rxt`) x widths 32, 4095 x 2 layers | 164 | 164 |
| 90 corpus patterns (the first 8 of each of counterk.rxt, spanarms.rxt and 12 other tests/*/*.rxt) x 2 layers, width 32 | 180 | 180 |
| **total** | **356 pairs (712 compiles)** | **356, 0 differ** |

(`.rxt` files are libraries of definitions, so the patterns were taken from their `pattern` lines and compiled by `--pattern`; script `$PCREC_TMPDIR/scratch/bsu5/ident.py`, output `ident.out`.)

## RE-CHECKS

The §10.2 "At U5" note: **S2930 and S2933 are re-aimed and REACH re-proved only if the entry struct gains a field or the hash dispatch changes.**
- **S2930: the entry struct DID gain a field (`k`)**, so every row ends `..., NULL, NULL, 0 },`. Its SAB_BEFORE and SAB_AFTER now carry the `, 0` (re-aimed; header note added). Anchor present once. `VALIDATE_ONLY=1 run_sabotage_matrix.sh S2930 S2933 S2931`: fields OK for all three. REACH re-proved by hand: the plant applied in the worktree (formhash.c backed up and restored byte for byte), `tests/memfn/run_finder.sh` goes red with 4 failures ("instance pair reached row pf_walk, the design's PAIR"; "form instances hash one text: walk - = pair -"; the edit and fold-edit rows), the unplanted tree green (28,926 / 0). The queue job `kit-bsu5-mech` re-runs it through the matrix.
- **S2933: NOT re-aimed.** The hash dispatch (`mf_form_hash`'s fold loop, its anchor `if (strcmp(entries[i].id, form_id)) continue;`) did not change, and the entry struct's new field does not touch that line. Its detector (the fold of the instances, multi-instance ids `settest` and `rc-words`) is unchanged; anchor present once. Re-run in `kit-bsu5-mech` as a re-check.
- **S2931** (the §10.2 R71-7 (b) re-check): `kit-grid.tsv` gained an appended row and header text; its anchor `kit<TAB>verify_cmp<TAB>3<TAB>form;cls;pass<TAB>` is unchanged (one match); fields OK.

## IN-LANE RUNS

All on this tree (worktree bsu5; `TMPDIR=$PCREC_TMPDIR/scratch/bsu5/tmp`; heavy ones under `scripts/boxlock`; box free on every start).
- `python3 -I memfn/tests/span_forms/cards.py plan`: green before the edit (premise test: ran green on today's cards, `kit-grid.tsv`'s last row was @7), green after (1590 cells).
- `cards.py dry RUNDIR --quick` (the whole plan, all cards, boxlock run): **rc 0; 1590 cells built and gated, 0 failures; 289 distinct compiles; 163 timed texts x 4 variants = 652 exes, 0 pools refused; deny check C1-C5 unchanged (42 arm-I loop-free, reach 124), C6 deny check 11 pairs 0 failures**. `--quick` is the 64 KiB subject (the gate sizes the cell, not the timing). A `--cards C6,C6c` partial dry: 216 cells, 0 failures.
- `bash tests/memfn/run_finder.sh` (`make test-memfn-finder`'s runner): 28,926 passed / 0 failed (was 1 failed on the first build: `digest` named in formhash.c, fixed).
- `make strict`: clean (`-Werror -Wshadow`). `make test-memfn-arch`: 32 / 0. `make test-memfn-link` (R-28 frame bar): 12 / 0. `scripts/check_claudemd_size.sh --all`: 426 within limits.
- `cards.py selftest` (C1-C5's rule drills; C6 touches none of its paths, `LAYERS`/`STEP1` unchanged): STARTED under `boxlock run` (label bsu5-selftest), still running at handoff; OWED, log `$PCREC_TMPDIR/scratch/bsu5/selftest.log`, completion line `rc=N` appended (rc=0 = green; its own output ends with the drill summary). It holds the box lock, so the queued jobs wait behind it.
- Not run in-lane: `make test`, the mech rows (the two OWED jobs), any timing.

## OWED RUNS

Queue jobs (non-timing), per `docs/dev/lanes/RUNS.md`, key = name suffix:
- `744-kit-bsu5-test`: `make test` on this tree (`scripts/perfrun`, `TMPDIR` set), key `kit-bsu5-test`.
- `745-kit-bsu5-mech`: S2930, S2933, S2931 (readiness `after kit-bsu5-test`), key `kit-bsu5-mech`. S2931 is the re-check the note names; no row was moved besides S2930's anchor.
- Timing (U6, main's window, on each bench box that runs V): C6 (108 timed cells) and C6c (42), one `cards.py` command to be written with the rule's reader; not queued by this lane.

## CHARTER VS COMMITTED

| charter item | committed |
|---|---|
| Card C6 `span_vector` in cards.py, exactly as §8 | YES: arms V / H64@on (`--memfn=no-span-vector`), patterns and widths, cut outside-bound cells, six regimes + near-miss-in at window sites, rule clauses applied / dropped, A/A arm, rule sha 6351bff3901e3955; open points 1-3 flagged |
| Row `kit span_vector 8 ...` in kit-grid.tsv, visibly UNMEASURED | YES (header `ver 8` says UNMEASURED and CANDIDATE) |
| `deps`: new formhash SHAPE, renderer, ONE entry (hex set, K 40, x86-64-v3) | YES: `MF_FH_SPAN`, `case MF_FH_SPAN` in `fh_render`, entry `span-vector` hash a9efa02907d0645b; `kit:form.span-vector` on the row |
| Clang arms for the 3 real sites (§0.1): SIMD-off layer under clang -O2, V wrapper vs deny, UNMEASURED | YES: sibling card C6c on a declared compiler column; no parallel mechanism; unmeasured; clang alignment variant is an UNMEASURED DEFAULT |
| `cards.py plan` and `dry` green, no timing | YES (plan; full dry 1590 cells 0 failures); no timing of any kind |
| §10.2 "At U5" re-check: S2930, S2933 | S2930 re-aimed (struct gained a field), REACH re-proved by hand; S2933 not re-aimed (dispatch unchanged); S2931 re-check; mech job owed |
| U5 moves no emitted byte / no abi event | YES: 356 of 356 compiles byte-identical |
| CLAUDE.md updates | YES (memfn/src, memfn/tests, memfn/data/cards CLAUDE.md, PROVENANCE.md) |
| In-lane checks green: formhash tests, make test-memfn-arch, make strict, any mech row moved | YES (selftest: see IN-LANE RUNS); mech S2930 hand-proved, matrix owed |
| Two queue jobs `kit-bsu5-test`, `kit-bsu5-mech` | YES: 744-kit-bsu5-test, 745-kit-bsu5-mech (queued; selftest also owed) |
| lanecheck DONE rc=0, report committed, SendMessage to team-lead | see the handback |
