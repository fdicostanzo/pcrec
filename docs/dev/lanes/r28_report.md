# r28 report: R-28, the kit's compile-time stack frames

Lane r28 (branch `lane/memfn-r28`, cut from main ce5aa67a8). Request: `memfn/docs/requests.md` "## R-28".
Bar: no kit function with a stack frame over 4 KB, the kit states its peak, dd10's stack probe stays green, the `a` baseline drops by the frames removed, ZERO emitted-byte movers.

## 1. Frames before and after (gcc 15.2 x86_64 `-O2 -fstack-usage`, read-only over memfn/src)

Every function at or over 1 KB; nothing else in the kit is.

| function | before | after | how |
|---|---|---|---|
| `pcrec_mf_form_hash` (formhash.c) | 36,368 | 3,600 | arena block table on the heap |
| `pcrec_mf_set_terms` (terms.c) | 36,256 | heap wrapper, small | two `target`s (~15 KB each) on the heap |
| `pair_facts` (terms.c, inlined into set_terms before) | (inside the 36,256) | 2,448 | 16-bit tables |
| `pcrec_mf_kit_report_exact` (compose.c) | 4,448 | 3,184 | one offset's row at a time |
| `pcrec_mf_form_hash_text` (formhash.c) | 4,352 | 2,304 | name-length table dropped |
| `define_sel` (compose.c) | 3,408 | 3,408 | untouched, under the bar |
| `fd_pres`, `fd_route`, `dfs` | 1,536 / 1,456 / 1,376 | same | untouched |

Four frames were over 4 KB (`form_hash`, `set_terms`, `kit_report_exact`, `form_hash_text`); none is now. The largest is 3,600 B.

## 2. Method (D157: the kit's)

- formhash.c: `fh_arena`'s `void *blk[4096]` (32 KB) became a heap block table grown by `realloc` (64 slots doubling to the existing 4096 cap). A refused growth sets `full` like the cap did, so `mf_form_hash` returns -1 (its existing refusal). `mf_form_hash_text`'s `nlen[256]` is gone: a name's length is recovered by scanning `id_char` from its stored pointer (equal comparison, same hash).
- terms.c: the two `target` structs move to one `calloc(2, sizeof(target))` in the exported `mf_set_terms`; the search is the static `set_terms_in`. An allocation failure returns **-1**, which is not the decline 0 (kit.h's contract comment says so; `mf_set_terms` has no caller in pcrec today, so no reader of the 0/1 result changes). `pair_facts`' `unsigned` tables became `uint16_t`/`uint8_t` (every value is at most 256).
- compose.c: `kit_report_exact` compared a 41-row `req` table against `c.proven`; it now builds and compares one offset's row at a time. `term_prove` takes the row-0 offset (`base`) so both callers share it. Same comparison, same result.
- No new malloc where the kit owned scratch: the kit's arena (`mf_arena`) is the caller's and these two functions are standalone entries that already used malloc (formhash.c's own header says so).

## 3. Peak statement

Stated in `memfn/CLAUDE.md` "Compile-time stack (R-28)" and held by `tests/memfn/run_link_checks.sh` (new block "R-28", part of `make test-memfn-link`, a `make test` section): every `memfn/src` file is compiled `-O2 -fstack-usage`; any function over 4,096 B fails. Controls: a planted 5,000 B function must be the one flagged; population floor 100 functions (254 measured).

Measured kit chain on a painted 1 MB thread (scratch driver, not committed): `mf_form_hash("walk")`, `("libc")` (each renders a site through `mf_emit`) and `mf_set_terms` at K=4 over two sets, high-water **13,704 B after, 47,144 B before** (same driver against the old terms.c/formhash.c). `dfs` recurses at most `MF_SET_K` (4) deep at 1,376 B.

## 4. The dd10 probe and the `a` baseline: a finding

dd10's `compile_stack_driver.c` (copied read-only from `lane/dd10` to the scratch build dir, built against this worktree's `libpcrec.a`) on the pattern `a`, 1 MB painted thread:

- before: `hw=31668`
- after: `hw=31668`

The baseline does NOT move at main ce5aa67a8, and it is 31.7 KB, not 62 KB: `pcrec_mf_form_hash` and `pcrec_mf_set_terms` have no caller in `src/`, `cli/` or `lib/` (grep; `lane/dd10` has none either), so neither frame is on `pcrec_compile`'s path. The 36 KB frames were real (and are removed) but they were never part of the `a` floor; the 62 KB figure in R-28's facts came from reading `-fstack-usage`, and the 31.7 KB on `a` is pcrec's own frames. dd10's full `run_compile_stack.sh` was not run: lane/dd10 is unmerged and its depth cases need dd10's compiler changes. The pcrec manager should not expect R-28 to lower the compile floor; the kit-side bar (no frame over 4 KB, peak stated and guarded) is met.

## 5. Zero movers: the evidence

- Hash values: a scratch driver (`build/su/eq.c`, not committed) ran the OLD terms.c/formhash.c (from `git show HEAD:`) against the new ones over 23,004 output lines: `mf_form_hash` for `walk`, `libc` and an unknown id; `mf_form_hash_text` over 20,000 random fragment texts plus a 400-distinct-identifier text (past the 256-name table); `mf_set_terms` over 3,000 sets (small sets, runs, masked cubes, random) at K=1..4 with the full cover, node count and complement printed. `cmp` of the two outputs: IDENTICAL (1,627 covers found, 1,375 declined).
- Form-hash pins and compose.c: the kit's own pin tests below.
- Emitted text: heavy job (section 6), nine emit_sweep arms.

## 6. Checks

Light, at tip (before the report commit):

- `make strict`: clean.
- `python3 -I scripts/m6read_check_sab_anchors.py`: found 1 stale anchor after the edit (S1255, `kit_report_exact`'s `return !memcmp(...)` line). Re-anchored, intent unchanged ("compare only span 0's offsets, d >= 0"): the plant now starts the loop at `d = 0` instead of `MF_PROOF_LO`, in `tests/mech/sabotages/S1255_report_proof_not_equal.sh` AND in its twin plant text in `tests/memfn/run_proof.sh`. Result: 901 sabotages, all anchors resolve. `run_proof.sh --plant S1255`: RED (detected: "D REPORT with a two-offset SATISFIES item: the row does not apply"). The mech row S1255 itself is in the heavy job. No other sabotage row anchors in terms.c or formhash.c.
- `make test-core`, every `test-memfn-*` target except the opt-in `g2-full`, and `tests/codegen/run_codegen_tests.sh`:
- `tests/memfn/run_link_checks.sh`: 11 checks, 0 failed (the 3 new R-28 checks included).

All green at the tip (checks passed / failed 0): test-core 7; arch 17; arms 383; deleg 14; finder 2,324 (proof 0 failed); forms 5; g2 71,217,800; guarded 10; link 11; manifest 15; rank 15; reach 4; rows 236; simdfloor 51; stamps 25; `tests/codegen/run_codegen_tests.sh` 331. (Logs: `build/su/light.log` in the worktree.)

## 7. Heavy validation (DO-THEN-FINISH): OWED

Job `570-kit-r28-heavy` (script: `build/r28/570-kit-r28-heavy` in the worktree, copied into the queue by `boxqueue add`): `make -j16`; nine emit_sweep arms (plain with the dumps stream, simd, comments, utf8, vm, start, rwquest, variant, trace) against base ce5aa67a8, binary built from `git archive` into `build/r28ref`; mech S1255 (`PROCS=4`); `scripts/perfrun --label r28` for `make test`. Per-step logs under `build/r28/heavy/`.

Queued with `scripts/boxqueue add --name 570-kit-r28-heavy` (id `570-kit-r28-heavy`, cap 21600 s, idle-ok, no quiet gate). Read it with `scripts/boxqueue status` and `scripts/verdict` on its `job.log` under `worktrees/.boxqueue/{running,done,failed}/*570-kit-r28-heavy/`. Completion lines to expect: nine `emit_sweep: DONE rc=0` (the queue's declared population, `sweeps=9`), `== r28 step mech rc=0` with a `DETECTED` line for S1255, the `maketest` step's `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` empty (read beside `maketest.make.log.perfrun`), and the trailer `== r28 heavy: 0 step(s) failed`. Result: OWED, none read.

## 8. Charter vs committed

| charter item | committed |
|---|---|
| 1. every kit frame above 4 KB, listed | section 1: four frames (36,368; 36,256; 4,448; 4,352) |
| 2. large storage off the stack, kit idiom, loud refusal, static kept, MF_NS kept | heap with the existing refusal path (-1); no symbol added or renamed (`set_terms_in` is static; `pcrec_mf_set_terms` still the one export) |
| 3. peak stated + a cheap guard | `memfn/CLAUDE.md` "Compile-time stack (R-28)"; `memfn/src/CLAUDE.md` rule; frame check in `tests/memfn/run_link_checks.sh` (witness + floor) |
| 4. zero movers, hashes unchanged | section 5 (old-vs-new equality over 23,004 lines) + nine emit_sweep arms OWED in the heavy job |
| light checks | section 6 |
| stack probe before/after | section 4: 31,668 both; the frames were not on the path (finding) |
| re-anchor + solo rows | S1255 re-anchored; plant RED; the mech row runs in the heavy job (the box lock was held by a queue `make test`) |
| report, job id | this file; job id in section 7 |
| spec hunk (D80) | none: `mf_set_terms`' new -1 is internal to the kit (`kit.h`, no caller, not in `docs/spec/`) |

## 9. Live-path correction

Section 4's finding that the 36 KB kit frames were "not on the live compile path" (no caller of `pcrec_mf_set_terms`) was WRONG. Main's lane dd10b found the live chain with gdb: `emit_dfa` -> `cand_ask` -> `mf_ask` -> `find_facts` -> `set_terms`. On lane/dd10 (painted probe) `pcrec_compile` peaks at 61,616 B on the pattern `a` and 24,120 B on `abc`; the main build reads `a` at 31,668 B. The "31,668 both" before/after in section 4 therefore measured a tree where the probe did not reach the frames. R-28 moving the kit's large frames to the heap should lower the lane/dd10 numbers; the spec hunk verdict of section 8 ("no caller") should be re-read in that light.

Painted before/after: queued job `572-kit-r28-meas` (script `docs/dev/lanes/r28/r28meas-job`, copy in the queue). It builds libpcrec.a in worktrees/r28m0 (before, lane/dd10) and worktrees/r28m (after, lane/dd10 + R-28), runs `tests/thread/compile_stack_driver.c` (painted, guarded 768 KB thread, one pattern per run) for `a`, `abc`, `a(b|c)+d`, and prints pattern / before B / after B / delta. Held by `--ready` until `i2build-parity` ends. Completion line: `== r28meas COMPLETE` (three `ROW` lines before it). Result: OWED, none read.
