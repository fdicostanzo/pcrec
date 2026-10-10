# s4build: `[OPT-LITSCAN]` S4 C0 + C1 (lane report)

**LANDING NOTE (lane r1land, 2026-10-03):** landed on `lane/r1land` after
[OPT-HYB-RESEED-FORM] A1 (abi 56) and [OPT-VEDGE] (abi 57, bit 42, S440), so
this change is **abi 57 -> 58**, `-fno-run-overlap` is **bit 43**, its tuning
section is **§2.38**, the registry axis pin is **174 -> 177**, and its sabotage
rows are **S440 -> S442, S441 -> S443, S442 -> S444, S443 -> S445**. Every
number below is branch-time. C2's planned bit is 44. `c1_movers.py` stays the
branch-time census (abi 55 vs 56). See docs/dev/lanes/r1land_report.md.

Lane `s4build` (opus), 2026-10-03. Branch `lane/s4build` from main
`26152329` (abi 55), **NOT merged**. Round 1 of the `[OPTLOOP]` cycle under
D144. Design: `docs/design/litscan_s4.md` (+ `docs/dev/lanes/s4des_report.md`,
`docs/dev/optloop/s4/`), with the manager's rulings on its §10 (Q1 three abi
events, Q2 bits at landing order, Q3 the overlap row ships only on an alpha
win, Q5/Q6/Q8 accepted, Q9 C2 HELD, Q10 the `&&` spelling, Q4 C3 under its own
light panel, not built here).

## 0. Summary (for a resuming agent)

- **C0 (no abi event): the byte cube moved to `src/core/`.** `pcrec_cube_of(iv,
  i, j, base, w, care, val)` in `src/core/cpset.c` is ONE definition
  parameterized by the domain; clskit's `cube_of` is a one-line caller over a
  section's own span, and `pcrec_cls_cube(cx, a, K, T)` is the absolute
  byte-domain reader the run facts will use (base 0, width 256). The fold
  agreement check gained its (b) arm (the fold's third consumer). **Zero
  movers**, proved by `scripts/emit_sweep.py` (5 streams, 4,318 argv rows x3 +
  357 composition files + 7 dumps, `movers=0` on every stream) and
  `scripts/cls_identity.py` (16,017 triples identical or both-refused, its
  instrument control red as required).
- **C1 (abi 55 -> 56): the run compare.** `src/gen/runcmp.c`'s
  `pcrec_emit_run_compare` is the one emitter of every literal-run compare in
  emitted C, both engines, through a first-match row table: `overlap` (an
  exact run of length 3, 5-7 or 9-15: two overlapping `memcpy`-loaded natural
  words, the last at `L - W`, `&&` in offset order, constants the same load of
  a string literal) then `memcmp` (P4's text byte for byte). P4
  (`pcrec_emit_exact_compare`) is retired and its three callers re-pointed.
  `-fno-run-overlap` = `PCREC_NO_RUN_OVERLAP` = **bit 42** (the next free bit
  on main at commit; no sibling had claimed it — reconcile at merge, Q11),
  masked out of `rx_info.flags`. `<PREFIX>_RUN_WORDS` on every artifact,
  emitted after the engine body.
- **Not built, by ruling or by D77:** C2 (HELD, Q9), C3 (pending its panel,
  Q4), and the masked rows `words`/`bytes` (their first caller is C3; a row
  with no caller is code no cell reaches — `PcrecRun` gains its K column with
  them). Recorded in the `[OPT-LITSCAN]`/`[WORD-FOLD]` plan rows.
- **The `overlap` row ships DEFAULT-ON behind its flag** (Q3): the manager's
  Linux alpha (`docs/dev/optloop/s4/alpha_c1.sh`) decides whether it stays on.

## 1. Commits

| commit | what |
|---|---|
| `aac5d3df` | C0: `pcrec_cube_of`/`pcrec_cls_cube`, clskit caller, fold-agreement (b), S361 re-aimed, S440 |
| `6493b1f1` | C1: `runcmp.c`, P4 retired, bit 42 + axes row + `--list-axes` rows, `RUN_WORDS`, abi 55 -> 56 (every reader by grep), spec hunks, L-sweep cells |
| `4e38640b` | C1: words loop ends the last word at L; `runcmp_check.py`; the compare-reading checks made row-aware; S267/S279/S285/S304 re-aimed; S441-S443; forced-VM L-sweep copies — **the lane's last `src/` commit (the FILEPIN)** |
| `e126298b` | FILEPIN re-pin, compare_stack keep-it-true, CLAUDE.md entries, mover census + alpha script, plan rows |
| `d4c77b56` | alpha script per D144 addendum 1; the `runcmp_check` call bounded (K37) |
| (after) | re-pins (registry 171 -> 174, rxtsource census, cpset manifest), this report |

## 2. C0 — the cube, and why it moves nothing

- clskit's call passes `base = iv[i].lo`, `w = span`: the old semantics
  exactly, so its selections are byte-identical by construction; the sweeps
  above confirm it.
- Under the ABSOLUTE domain the O(k) spill budget is exact (`csize` must equal
  `nmem` when `w = 2^nbits = 256`), so dropping the exact loop is inert there;
  the exact loop is load-bearing only for clskit's section form. That is why
  S361 (re-aimed to `cpset.c`, anchor verbatim) keeps its `clskit` detector
  and S440 is a different plant: the absolute reader handed the section form's
  base. S440 measured red by hand: `CUBE 0x01: pcrec_cls_cube gave K=0xff
  T=0x00, expected K=0xff T=0x01` on every fold set.
- Fold-agreement (b): all 256 fold sets `{c, fold[c]}` give K = 0xDF on the 52
  letters and K = 0xFF on the other 204, T = c & K; plus `{a,b}` and `{a,b,c}`
  refused and `[0-7]` = (0xF8, 0x30). Runs in `run_backref_diff.sh` §9
  (test-backrefs green on the C0 tree).
- C0 validation (detached worktree at `aac5d3df`): `make`, `make strict`,
  `test-clskit`, `test-backrefs`, `test-registry` green; `test-codegen` red on
  the one accepted darwin line only (`nm could not read arm_a.o`).

## 3. C1 — what moved (mover census vs the design's prediction)

`docs/dev/optloop/s4/c1_movers.py`, BASE = the C0 compiler, NEW = C1, the
abi digit normalized and the `RX_RUN_WORDS` line dropped; plus a DENY arm (C1
under `-fno-run-overlap` against BASE).

| population | artifact-configs | moved & RUN_WORDS>0 | moved & =0 | identical & >0 | identical & =0 | deny == BASE |
|---|---|---|---|---|---|---|
| bench (every `bench/*/patterns/*.rx`, auto+vm) | 678 (43 refused) | **151** | 0 | 0 | 484 | 634/635 |
| corpus (every distinct pattern, auto+vm) | 6,928 (747 refused) | **520** | 0 | 0 | 5,661 | 6,181/6,181 |

- **The biconditional is exact**: 0 off-diagonal in both populations.
- **Against the design's §7 prediction** (55 default-route / 92 forced-VM bench
  artifacts with a P4 compare at an overlap length): measured 56 auto / 95 vm.
  The design's census counted `memcmp` lengths in the abi-55 text; the
  difference (+1/+3) is within what main's later commits moved and was not
  chased further.
- **Stamps that moved on movers**: `RX_VM_PROGRAM_BYTES` (113 bench, 354
  corpus — the words spell longer than the `memcmp`), and one
  `RX_VM_PREFILTER_LANG_WHY`. No entry-shape, size-term or engine stamp moved.
- **The one deny-arm difference is a stamp-line effect, not a program move**:
  `wild-logparse-syslogbase-expanded` (auto) quotes the refused exact
  attempt's byte count in `RX_VM_PREFILTER_LANG_WHY`, and that count now
  includes the 23-byte `#define RX_RUN_WORDS 0` line (1,457,019 -> 1,457,042).
  Diffed in full: that line, the stamp line and the abi digits, nothing else.
  S2a recorded the same class for `VM_LIT_RUNS`.

## 4. Suites that count (D94), run by the lane

ALL ON DARWIN, gcc-16, each in the background with its log in the lane's
scratch; verdicts from make's `*** [` lines.

| suite | result |
|---|---|
| `make`, `make strict` | green |
| `make test-codegen` | first run red on `[K37]` (the new `runcmp_check.py` call unbounded) + the accepted `nm arm_a.o`; fixed (`"$TIMEOUT_BIN"`); **re-run: OWED/see §8** |
| `run_codegen_tests.sh` `[OPT-LITSCAN S4]` block | 99/99 (runcmp_check.py) |
| `make test-registry` | red on ONE pin, `axes_registry_check` coverage 171 -> 174 (the bit-42 triple); re-pinned |
| `make test-rxtsource` | red on the census (litrun.rxt +60 blocks / +1,070 lines); CENSUS/RUNSH re-pinned, C3_VERIFIABLE +1,070 (measured: `verify_rxt.py tests/litscan/litrun.rxt` PASS 1161 vs main's 91, SKIP 0), C3_PASS inferred +1,070 for 3.14 |
| `make test-cpset-structure` | red on the manifest: 12 `EMITTED_BYTES` rows, nine +23 (the stamp line), `abc`/`(a)(b)(c)` +159, `(?<=foo)bar` +271; each verified by diff against the C0 compiler; re-recorded with the record in the script |
| `make test-prechecks` | green (§4.1/§5.9 build under `-fno-run-overlap`; the overlap spelling is pinned in the new block) |
| `run_offset_skip.sh`, `run_dfa_stamps.sh` | green after the run-term expectations moved to the overlap spelling (`run_dfa_stamps.sh`'s awk marker accepts either row) |
| `tests/litscan/litrun.rxt` | 1161/0 |
| recursion identity (B) | FILEPIN re-pinned to `4e38640b`; (A) needs no new excuse axis: `-fno-lit-run` is already in every excuse build and removes every VM run compare, so the run compare cannot reach the region under it. **Run: OWED** (§8) |

The remaining sections of the batch (`test-vm`, `test-tune-dial`,
`test-island`) and the re-runs of the four re-pinned sections are in §8.

## 5. Sabotage rows (next free on main was S440)

| id | file | plant | detector (measured on the lane, by hand) |
|---|---|---|---|
| **S440** | `cpset.c` | `pcrec_cls_cube` passes the section form's base | fold-agreement (b): every fold set's T wrong |
| S361 (re-aimed) | `cpset.c` | the exact domain loop dropped (anchor moved verbatim) | `clskit` (unchanged) |
| **S441** | `runcmp.c` | the last word at `L - W + 1` (over-read) | `runcmp_check.py` 17 red; harness litrun 27 red |
| **S442** | `runcmp.c` | the last word at `L - W - 1` (last byte uncovered) | `runcmp_check.py` 17 red; harness litrun 6 red (the forced-VM last-byte flips) |
| **S443** | `runcmp.c` | the overlap row's `==` becomes `!=` | `runcmp_check.py` 72 red; harness litrun 45 red |
| S267 (re-aimed) | `runcmp.c` | the `memcmp` row's `!memcmp` -> `memcmp` | harness (every `memcmp`-length run) + `run_prechecks.sh` §4.1b (built under `-fno-run-overlap`); reach under `-fno-run-overlap` |
| S279 (re-aimed) | `emit_dfa.c` | the run term's offset +1 | reach greps the overlap words; detectors unchanged |
| S285 (re-aimed) | `emit_dfa.c` | the run term's length +1 (`PcrecRun`'s len) | as before |
| S304 (reach only) | `cpset.c` | unchanged plant | reach greps the overlap words |

All nine anchors verified to occur exactly `SAB_COUNT` times; the four
re-aimed reaches print their REACH token. Single-row mech runs: OWED to the
manager's battery.

**A finding from S442**: `tests/litscan/CLAUDE.md` and `gen_litrun.py` said
"the harness runs every file on both engines". It does not — each block runs
on the route it is written for. S442 read 811/0 until the L-sweep gained
`engine vm` copies, because on a DFA artifact the run compare is a prefilter
term the DFA re-verifies, so a compare that accepts too much is invisible
there. Both texts corrected; the S2a population may have been read under the
same misbelief.

## 6. The structural checks (design §5.4)

`tests/codegen/runcmp_check.py` decodes every `rx_w<W>(base + o) ==
rx_w<W>("...")` chain back into (offset, bytes) and holds it to the run each
witness names from its PATTERN text. Covered: the DFA run term (`/user|/users`,
`foo\b`, `[ab]/user`), the run pre-check with escape-bearing runs (`a"b`,
`*/x` — the latter puts `*/` in a C string literal, which is fine; the run
compare writes no comment), the island's chains, and the VM literal run at
every overlap length 3..15; plus the pay-for-what-you-use lengths 4, 8 and 16
(one `memcmp`, no helper), helper declaration exactly per width used and
ahead of first use, `RX_RUN_WORDS` against the text, `-Werror` compilation,
and the deny arm (no word left, each word compare restored to exactly one
`memcmp`). "No integer literal" is asserted on every artifact.

## 7. Spec, docs and the dial

- `docs/spec/tuning.md` §2.37 (new), §2.31's compare sentence, §4's mirror
  table, §5.4's policy table (a `-fno-run-overlap` row, NOT A RUNG, and the
  row counts 27 -> 28 / 23 -> 24 / 20 -> 21).
- `docs/dev/history/abi_changelog.md`: the abi-56 entry (mechanism, movers,
  invariants), the K80 block quote's digits, and §6.3's `RUN_WORDS` entry plus
  `VM_LIT_RUNS`' compare sentence.
- `docs/design/compare_stack.md` §2/§4/§5 kept true (P2 created, P4 is the
  run compare; the cursor rung and backward walk keep their form, with the
  trigger).
- `CHANGELOG.md` [Unreleased]; CLAUDE.md for `src/core`, `src/gen`,
  `tests/backrefs`, `tests/codegen`, `tests/litscan`, `docs/dev/optloop/s4`.
- Design deviations, each small: the declarations live in `core/internal.h`
  (the `pcrec_reseed_rows` precedent; `axes_dump.c` reads the table), not a
  new `runcmp.h`; the emitter takes `(base, off)` rather than one base string
  so the `memcmp` row keeps P4's `base + off` text exactly; the words loop
  writes the last word at exactly `L - W` (so S441/S442 are one-token plants).

## 8. Owed

- Re-pinned sections (registry 171->174, rxtsource census 260/4378/33622 +
  C3 15059/17056, cpset manifest 12 rows). `test-registry`'s re-run was INTERRUPTED by
  the lock switch after PC-3 passed 213/0, so a full re-run under the lock is OWED. At handback,
  `test-rxtsource`, `test-cpset-structure` and `test-codegen` (after the K37
  fix) were running SERIALLY under the Mac suite lock. Their logs are in
  `worktrees/s4build-scratch/c1v2/<section>.log`. Each one is complete at its
  `rc=` line, and its verdict comes from its make `*** [` lines. The expected
  codegen red is the darwin `nm arm_a.o` probe alone. `test-vm`,
  `test-tune-dial` and `test-island` were GREEN in the first batch
  (`worktrees/s4build-scratch/c1v/`).
- `make test-recursion-identity` with (B) at `4e38640b` (~35 min).
- The answer differential (design §5.1 item 2): `tests/findings/
  b1_mover_answers.py` over all 671 movers, BASE = C0, NEW = C1, plain and
  under `CFLAGS="-O1 -std=gnu11 -w -fsanitize=address,undefined
  -fno-builtin-memcmp -DDIFF_EXACT_SUBJECT" PREFIXES=1` (the ASan sweep, with
  S441 as its red control). Manifests: the lane scratch's
  `movers_plain.json` (s1-identity shape, built from `c1_movers.json`).
- `make test-axes AXES="-fno-run-overlap"` (multi-hour on darwin).
- The full `make test` (the manager's queue).
- **The Linux alpha** (`docs/dev/optloop/s4/alpha_c1.sh`, BASE_REV `aac5d3df`,
  NEW_REV `4e38640b`): step 0 is `[WORD-FOLD]`'s owed gcc-15/x86 instruction
  arm; `check` asserts DENY == BASE before anything is timed; `time` reports
  absolute ns/B deltas beside the floor |DENY - BASE| (D144 addendum 1), with
  the `|` twins for slack and `lit-l7` (Q10). Smoke-tested `build`/`check` on
  the Mac with the lane's binaries (all twelve cells DENY == BASE, the twins
  answer-identical).
