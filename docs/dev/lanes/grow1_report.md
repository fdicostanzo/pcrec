# grow1: the growth-sweep runner ([GROWTH-SWEEP])

Lane grow1 (sonnet), 2026-11-21, branch lane/grow1 cut from main f286a8e1a.
Last ruling applied: R-1 (do not wait for the queued run; finish with it OWED). No `src/` edit.

## Summary

The runner is built: `tests/growth/` (own CLAUDE.md), `make test-growth`
(opt-in, not in `make test`), a `docs/testing.md` section "Growth sweep", the
plan row moved to Active as STATE:started. 1,467 cells, each run uncapped and
under a four-rung memory ladder, plus a library-mode series in one ASan+LSan
process. `tests/thread`'s DEPTH_FAMILIES is gone: the one depth table is
`tests/growth/depth_families.tsv` and `make test-stackdepth` reads it through
the runner (it printed 78 checks passed, 0 failed, including the 66 depth
cells). Two new findings (NEW-1, NEW-2); K148, K150, K151 reproduce red as
listed. The full queued run (matrix family and the whole library series) was
still running at handback: its numbers are OWED (see Validation dispatched).

PREMISE TEST (K152): `make test-stackdepth` (log in the lane scratch) shows
`litcompound` (the K152 witness's compound-route nest) compiling at 250 on the
442,368-byte thread (hw=307,056 B) and refusing at 251 with "parentheses are
too deeply nested"; `capwrap` 318,032 B, `longwrap` 319,504 B (the worst,
matching limits.md §3.10¶3), `litpost` 317,744 B, all 251 twins refused by name.

## Runner shape

- `run_growth.py` (python3 -I): expands the tables to cells, writes each
  pattern to a file in the temp root, runs `scripts/watchdog -s 180 -c 180
  -m 3g -- growth_driver one CAP STACK RAISE FEATURES ENGINE PATFILE`, and
  classifies the outcome: compiled, refused (message), CRASH (signal),
  TIMEOUT (watchdog 124: a timeout is a crash), RUNAWAY (watchdog 122),
  ERROR. Jobs run in a thread pool (cpu/2).
- `growth_driver.c`: one `pcrec_compile` on a painted, 64 KB-guarded mmap'd
  thread (the stack mechanics of tests/thread/compile_stack_driver.c), under an
  optional cap; `lib` mode runs a whole series in one process and compiles a
  control before and after.
- Verdict rule (the owner's): the uncapped column PASSES only if the outcome is
  in the cell's `expect` list (`compile`, `refuse:SUBSTRING`, where the
  substring is the named limit's diagnostic); the ladder column passes on a
  compile or ANY clean refusal. A `red` cell (K148/K150/K151/NEW-n) is listed
  as KNOWN-RED when it fails; when it passes uncapped the sweep FAILS
  (FIXED-RED: remove the `red`), so the red list cannot rot. Each FAIL prints
  a repro line.
- Files: `depth_families.tsv`, `matrix_axes.tsv`, `cells.tsv` (columns
  documented in its header), `run_growth.sh` (the make body), CLAUDE.md.

## Cells

1,467 cells (`run_growth.py --list`): depth 66, matrix 1,344, spine 35,
memory 22.

- **depth (66)**: the 33 absorbed families (tests/growth/depth_families.tsv,
  its header keeps the old comment block) at 250 (must compile on the budget
  thread) and 251 (must be refused by PCREC_MAX_GROUP_DEPTH, "too deeply
  nested"). All 66 PASS.
- **matrix (1,344)**: construct kind {group, non-capturing, named, atomic,
  lookahead, negative lookahead, lookbehind, inline option} x quantifier {none,
  `*`, `+`, `*?`, `*+`, `?`, `{0,1}`} x branch position {sole, first, second,
  last} x core {literal, backreference, literal-alternation `abc|abd`...`abe`}
  = 672 nests, each at 250 (compile, or any clean refusal: some combinations,
  an unbounded lookbehind, are refused for their own reasons) and 251 (refused
  by PCREC_MAX_GROUP_DEPTH). Its first-run numbers are OWED to the queued job.
- **spine (35)**: length 16,384 and 100,000 on the budget thread, shipped caps
  raised: zero-width runs `\b`, `(?=a)`, `(?!b)`, `(?<=x)`, `(?i)(?=a)` (must
  compile, limits.md §3.10¶1; K148 red), classes, a 100,000-byte literal,
  alternations, groups, anchors, `(?:)`, inline options, Unicode classes
  (compile), and the cells sized past their limit that must refuse by name:
  `(a)` x100,000 (PCREC_MAX_VM_NODES), `({i}x)|` x100,000 and
  `(?:ab){2,5}` (PCREC_MAX_NFA_STATES), `\b` x400,000 (NFA states).
- **memory (22)**: main stack, shipped size caps: `(?:a|b)` x1,000..4,000,
  `[ab]`, `(?:a|b)(?:c|d)` (compile), K150's witness `(?:a|b)(?:c|d)` x4,000
  (red), their x8,000 twins (refuse by PCREC_MAX_VM_EMIT_CODE_BYTES), the
  call chain `(?<g_i>a(?&g_i+1)?)` x20/80/160 (refuse by emitted-code limit),
  x320/1,000 (K151, red: runaway), `(?:` nest x60 `{2,3}`, 1,000,000 `a`
  and 300,000 `(?:a|b)` (NFA states), 100,000 `(a)` (VM nodes), a 500,000-way
  alternation (emitted-code limit), and the 1,000,000-way one (NEW-1, red).

## Memory ladder

RLIMIT_DATA (heap plus private writable mappings, set in the driver after
startup) of 2, 8, 32 and 128 MB. Why those: measured on this tree, a trivial
compile needs about 4 MB (1 to 3 MB refuse "out of memory", 5 MB compiles);
the worst depth family (longwrap, 250) peaks at 36 MB resident; the
quadratic/runaway families start at 766 MB. So 2 MB makes every cell refuse,
8 MB sits inside the trivial-pattern range, 32 MB straddles the worst depth
family, 128 MB is above every depth family and below the runaway ones.
RLIMIT_DATA and not RLIMIT_AS (AddressSanitizer cannot start under an AS cap).
Result on the families run so far: no ladder-only failure; every capped
non-red cell compiled or refused "out of memory compiling this pattern". The
only capped failures are K148's stack crashes (they crash with or without a
cap).

## Library mode

`run_growth.py --lib`: ONE process compiles the whole series (each non-red
cell uncapped and under each rung; a red cell's uncapped run is skipped, it is
a known runaway), then a control pattern again. PASS = exit 0, no sanitizer
report, every cell answered (`rc` 0, -1 or -9), the control compiled after the
series byte-identical to the one before it, and its generated C (compiled with
gcc, run on `ababcdef` and `ababcdx`) answers correctly. Compiles run on the
main thread, because ASan inflates frames past the 442,368-byte budget (the
budget is the CLI stage's question). Two stages, `run_growth.sh`:
plain build with RLIMIT_DATA caps set in the process (the brief's
setrlimit), and the ASan+LSan build (`build-asan/`, `make asan`'s flags),
where the cap is a live-heap budget via `-Wl,--wrap=malloc` (`GROWTH_HEAPCAP`
in the driver), because the ASan runtime cannot start its shadow mappings
under RLIMIT_DATA (measured: `failed to allocate ... (errno 12)` at 66 cells).

Result (depth + memory families, 436 compiles, one process): plain build PASS
(no crash, control identical and correct). ASan+LSan build: LeakSanitizer
reports a leak, NEW-2 below. Full series: OWED.

## First run

CLI stage, families run so far (`--only depth,spine,memory`, 1,458 runs after
the cell edits of this lane: 595 passed, 19 known-red, 1 FIXED-RED which was
a mis-set `red` and was corrected):

| family | passed | failed | known-red |
|---|---|---|---|
| depth | 330 | 0 | 0 |
| spine | 159 | 0 | 15 (all K148: `\b`, `(?=a)`, `(?!b)`, `(?<=x)`, `(?i)(?=a)` runs on the budget thread die by SIGSEGV; `(?<=x)` passes at 16,384) |
| memory | 106 | 0 | 4 (K150 `(?:a|b)(?:c|d)` x4,000 RUNAWAY; K151 x320 and x1,000 RUNAWAY; NEW-1) |
| matrix | OWED | | |

## Findings

K148, K150, K151 are the expected red cells (not findings). New:

- **NEW-1**: a 1,000,000-way alternation of literals (a 6.9 MB pattern) at the
  shipped size caps spends over 3 GB (the watchdog's RSS kill) before any
  refusal; the emitted-code limit (PCREC_MAX_VM_EMIT_CODE_BYTES) only fires at
  the end of the work. Memory is linear, about 5.5 KB per alternative
  (150,000 alternatives: 831 MB; 300,000: 1.7 GB; 500,000: 2.8 GB, then
  refused "pattern too large: 3904591 bytes of emitted code (limit 500000)"),
  so the cost is bounded only by the pattern's size. Repro: cell
  `memory/alt_1m@1000000` (`python3 -I tests/growth/run_growth.py --only memory
  --keep`, then its `.pat` file in the printed work dir) or
  `python3 -c "print('|'.join('%dx'%i for i in range(1000000)),end='')" > P`
  and `growth_driver one 0 0 0 all 0 P` under `scripts/watchdog -m 3g`.
  Same family as K150/K151: refuse before the work (a size estimate on entry).
- **NEW-2**: a leak on the out-of-memory refusal path in the library:
  `src/gen/memfn_stamps.c:363`, `target_headers_render`, builds its pass-2
  buffer `StrBuf nb` (malloc-backed via `sb_grow`, not the arena) and an
  allocation failure on a later append leaves the compile through the error
  path without freeing `nb.p` (LeakSanitizer: "Direct leak of 32768 byte(s)",
  `sb_grow` src/core/sb.c:33 under `pcrec_sb_printf` under
  `target_headers_render` under `pcrec_memfn_stamps_render`
  src/core/compile.c:3427). A caller that compiles many patterns in one
  process under memory pressure loses 32 KB per refused compile. Repro: the
  `depth/longwrap@250` pattern (depth cell, the 319 KB-stack worst) with
  features all, shipped caps raised, under a 32,000,000-byte live-heap cap in
  library mode on the ASan build:
  `GROWTH_CFLAGS="-O1 -g -fsanitize=address,leak -DGROWTH_HEAPCAP -Wl,--wrap=malloc -Wl,--wrap=calloc -Wl,--wrap=realloc -Wl,--wrap=free" LIBPCREC=build-asan/libpcrec.a ASAN_OPTIONS=detect_leaks=1:allocator_may_return_null=1:fast_unwind_on_malloc=0 python3 -I tests/growth/run_growth.py --lib --only depth`
  (fails with the leak; the same series with no ladder is clean).
  The library stage of `make test-growth` is therefore red until NEW-2 is fixed.

No timeout fired in any run so far.

## Validation dispatched

- `make test-stackdepth`: 78 checks passed, 0 failed (the absorbed depth arm).
- Queued: `300-grow1-growth` (box queue, started 2026-11-21 02:26 local, cap
  14,400 s, est 5,400 s; job script
  /var/tmp/pcrec-pcrec/scratch/grow1/300-grow1-growth, copy under
  worktrees/.boxqueue/): runs `bash tests/growth/run_growth.sh` (CLI stage for
  all 1,467 cells x 5 runs, then both library stages). OWED: the matrix family
  numbers and the whole-series library verdict. Read its verdict with
  `scripts/boxqueue status` / `scripts/verdict`; the sweep prints
  `runs passed:` / `runs failed:` / `runs known-red:` and per-family lines, and
  every failure carries its repro. Expect rc 1 until NEW-2 is fixed (library
  stage) and possibly for matrix cells (findings to file as they appear).
- Cloud `make test` dispatched on the lane tip (last act).
- plan_lint: 0 violations.

## STATE AT HANDOFF

Committed on lane/grow1; the report is committed. Last ruling applied: R-1.
Not done: the first-run numbers of the matrix family and the whole library
series (queued, OWED); the utf8 depth row ([STACKDRIVER-ENC]) and the
thread-size ladder (growth-stackcap: future direction, not built, by ruling).
Do not edit tests/growth/ while the queued job runs (it executes the worktree).
OWED: 300-grow1-growth (box queue KEY `grow1-growth`, which is what `boxqueue state` takes; matrix family numbers and the whole library-series verdict; a follow-up lane folds them in).
