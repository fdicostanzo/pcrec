# santriage3 report — checkpoint battery `san`-stage triage, 2026-09-18

Battery: `battery_20260918_051433` on ubuntubudu (`/home/duxevents/pcrec/
worktrees/validate`), pinned at main `272bf970`. `san` stage rc=2 (1 of 38
scripts failed). Read-only triage of `san.log` over ssh; the fix built and
validated LOCALLY on this Mac, worktree `worktrees/santriage3`, branch
`lane/santriage3`, off main `272bf970`. Nothing run on ubuntubudu (the
battery's mech stage was still in flight there for this lane's whole
working period).

## VERDICT

**The `272bf970` pin holds. Does not slip.** The `san` stage's single
failure is class (ii) — a harness/wiring gap unmasked for the first time,
not a regression in the mechanism `272bf970` shipped, and not a new defect
in `src/`. Fixed with a one-line change to a `tests/` helper program.

The finding is genuinely class (i) in the narrow sense that ASan's
LeakSanitizer really did fire and really did detect a real leak — but the
defect itself is **pre-existing** (the test file has carried it since
[M5.0] stage 1, weeks ago), not new. It only surfaced now because two
things changed together, neither of them a regression: wave U's
`unit_build` threaded `$SANFLAGS` into this file's compile for the first
time ever, and — separately, confirmed below — LeakSanitizer is genuinely
LIVE on ubuntubudu today, unlike K26's documented no-op on "this box" back
on 2026-08-18.

## The one failure

`run_san_group: 37/38 scripts passed` — every other san script is clean.
The single failure: `tests/codegen/run_cpset_structure.sh` CHECK 4 ("the
interval algebra, model-checked against a bitset oracle"), `san.log:2209-
2274`. No other `AddressSanitizer`/`runtime error:`/`UndefinedBehaviorSanitizer`
report anywhere in the 3,209-line log; the sole sanitizer report is:

```
FAIL: [4] the interval algebra DISAGREES with the bitset oracle:

=================================================================
==270989==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 65560 byte(s) in 1 object(s) allocated from:
    #0 ... in malloc
    #1 ... in arena_alloc src/core/arena.c:14

Indirect leak of 721160 byte(s) in 11 object(s) allocated from:
    #0 ... in malloc
```

## Attribution and root cause

`tests/codegen/run_cpset_structure.sh`'s CHECK 4 runs
`tests/codegen/cpset_model_check.c` (a self-contained unit-tier program:
400 trials x 60 randomized `add`/`remove`/`complement` operations plus 7
edge cases against `src/core/cpset.c`'s interval algebra, oracle-checked
against a flat 4096-byte bitset it maintains independently). Since wave U
([REVW.U L5-R0.1], `tests/lib/unit_cc.sh`'s `unit_build`), this file is
compiled with `$SANFLAGS` for the first time — its own comment says so:
"this file's build site named no `$SANFLAGS` at all before this — the
tree's best unit check had never been built under a sanitizer." That is
the compiler axis.

`main()` in `cpset_model_check.c` builds one `Ctx cx` with its own arena
(`cx.arena.cx = &cx;` after a `memset`), runs the whole 400-trial sweep
and all 7 edge cases against it, prints its verdict, and **returns without
ever calling `arena_free(&cx.arena)`** — unlike every real code path in
`src/`: `src/core/compile.c:229` calls it, and `src/parse/syntax_dump.c`
calls it at nine separate return sites. `src/CLAUDE.md`: "All AST and IR
memory is allocated from an Arena in the Job and freed wholesale on error
or completion." This test program simply never performs that "wholesale
free" step. The leak sizes match exactly: one head `ABlock` of
`ABLOCK_MIN` (64 KiB, `src/core/arena.c:6`) plus overhead = 65,560 bytes
(the DIRECT leak, the arena's `head` pointer), and 11 more blocks reachable
only via the chain's `->next` pointers (the INDIRECT leak,
721,160 bytes) — 12 arena blocks total across 400×60 operations plus the
edge cases, exactly consistent with `arena_alloc`'s block-chain design.

**Reached the shell's `FAIL` label because the exit code, not the
algebra, is what the shell reads.** `run_cpset_structure.sh`'s CHECK 4:

```sh
elif ! MODEL_OUT="$("$WORKDIR/cpsetmodel" 2>&1)"; then
    bad "[4] the interval algebra DISAGREES with the bitset oracle:"
    printf '%s\n' "$MODEL_OUT" | head -10 >&2
```

`ASAN_OPTIONS="detect_leaks=$(SAN_DETECT_LEAKS)"` is exported over the
whole `san` stage (`Makefile:1337`; `SAN_DETECT_LEAKS := 1` on non-Darwin,
`:= 0` on Darwin per K54's fix). On ubuntubudu that is `detect_leaks=1`,
so LeakSanitizer's own atexit hook — running AFTER `main()` returns, with
`bad == 0` and the "PASS" line already printed to stdout — detects the
leak, prints its own report, and overrides the process exit code to
nonzero. The shell reads that nonzero as "the algebra disagreed," which it
never did. (`$MODEL_OUT`'s buffered "cpset model check: PASS (...)" line
is itself missing from the captured log — consistent with LSan's fatal
path calling a raw `_exit()` that skips the normal C-runtime flush of
stdio's buffered stdout, though that detail is not load-bearing to the
diagnosis.)

## Local verification (this Mac, respecting K54)

Built the tree with `make -j4 CC=gcc-16` (clean), then verified in three
steps, all narrow and none touching ubuntubudu:

1. **Plain, unsanitized build of `cpset_model_check.c`** against
   `build/libpcrec.a`: `cpset model check: PASS (400 trials x 60 ops + 7
   edge cases)`, rc=0. The interval algebra itself is correct — no
   MISMATCH, no INVARIANT violation, no EDGE-case failure anywhere in the
   sweep.
2. **Built under the exact `SAN_CFLAGS`**
   (`-O1 -g -fsanitize=address,undefined,leak -fno-sanitize-recover=undefined`),
   run with `ASAN_OPTIONS=detect_leaks=0` (matching this box's own
   `SAN_DETECT_LEAKS=0` Darwin derivation, per K54 — **never** ran with
   `detect_leaks=1` locally, which K54 documents as hanging every
   gcc-16-sanitized process on this box regardless of pattern or of
   whether a real leak exists): PASS, rc=0. ASan and UBSan, with leak
   detection off, find nothing else wrong — no buffer/UB issue beyond the
   leak.
3. **Applied the fix** (`arena_free(&cx.arena);` before `return bad;`),
   rebuilt build-san (`make BUILD_DIR=build-san CFLAGS="$SAN_CFLAGS"
   CC=gcc-16 all`, clean), and ran the **whole**
   `tests/codegen/run_cpset_structure.sh` script end to end under the
   real `SAN_ENV` shape (`SANFLAGS`/`GENCFLAGS`/`ASAN_OPTIONS` etc., with
   `detect_leaks=0` — Darwin's own san posture): **28/28 checks pass**,
   including CHECK 4 now printing `PASS: [4] cpset model check: PASS (400
   trials x 60 ops + 7 edge cases)`.

Step 3 cannot exercise `detect_leaks=1` itself on this box (K54), so the
literal "LeakSanitizer no longer reports" claim is confirmed by code
review rather than by a local repro under the real flag: `arena_free`
(`src/core/arena.c:35`) walks `a->head`'s whole `ABlock` chain and
`free()`s every block, which is exactly the leaked allocation path
(`arena_alloc`, same file:14) the report names. There is no other
allocation site in `cpset_model_check.c` — `pcrec_cpset_*` and
`pcrec_cls_bits*` allocate only through this one arena. The next
ubuntubudu run (where `detect_leaks=1` is live and can actually observe
the absence of the report) is the confirming evidence owed to the
manager; nothing in this diagnosis is speculative about the mechanism.

`make -j4 CC=gcc-16` and `make strict CC=gcc-16` both clean on the fixed
tree (`strict: whole tree compiles clean with -Werror -Wshadow` — note
`make strict` scopes to `src`/`cli`/`lib`, not `tests/`; the `tests/`-file
compile was validated directly above under `-Wall -Wextra -Werror` plus
the exact `SANFLAGS`, which is how `unit_build` itself compiles it).

## Is LeakSanitizer really live on ubuntubudu now?

Yes — this run is itself the evidence. K26 (filed 2026-08-18, "this box")
measured LeakSanitizer as a silent no-op: a program deliberately leaking
12,345 bytes exited 0 and reported nothing, attributed to
`/proc/sys/kernel/yama/ptrace_scope`. This run's `==270989==ERROR:
LeakSanitizer: detected memory leaks` is a real, non-vacuous leak report
on ubuntubudu today, so LSan is now catching real leaks there — the exact
"positive leak canary" K26 called for is effectively satisfied by this
incident. K26 itself is not re-opened by this triage (it named a box
state, not a promise this lane can verify system-wide), but its own
canary obligation should be reconsidered in light of this evidence — that
disposition is for the manager, not decided here.

## Disposition of the two design questions in the brief

- **Class**: (ii), harness/wiring — a test HELPER's own missing teardown,
  newly exposed by SANFLAGS wiring + live LSan, not a regression in
  `272bf970`'s own diff and not a defect in `src/core/cpset.c`'s algebra.
- **Fix taken**: the narrow one-line fix (add the missing `arena_free`
  call), matching this file's own sibling test programs and the whole
  tree's stated convention. No manifest removal considered or needed —
  `run_cpset_structure.sh` stays in `san_scripts.txt`.
- **The alloc-injector "two allocators in one process" argument the brief
  raised as a possible class-(ii) mechanism does NOT apply here — and,
  correcting the brief's own premise, it was never a live question.**
  `tests/core/run_alloc_tests.sh` (`tests/core/alloc_inject.h`, wave U's
  L5-R1) is **NOT in `tests/lib/san_scripts.txt` at all** — checked
  directly, `grep -c 'alloc' tests/lib/san_scripts.txt` finds nothing, and
  it has its own separate opt-in `Makefile` target (`alloc:`, `Makefile:
  1407`, `make alloc`) with its own build tree, entirely outside `make
  san`. So "wave U added FOUR entries to san_scripts.txt" (the brief's
  framing) is off by one: the manifest carries 38 entries and wave U/L5-
  R0.2 together added exactly THREE — `run_cpset_structure.sh`,
  `run_mrl_tests.sh` (both L5-R0.2, fix-now) and `run_core_tests.sh`
  (wave U's own, `tests/lib/san_scripts.txt`'s own comment: "the unit
  tier's own home... this entry is what actually instruments it under
  the sanitizer axes"). `run_alloc_tests.sh` never ran under this `san.log`
  at all — its own name does not appear anywhere in the file — so there
  is nothing to classify there and no manifest change to consider; the
  injector's coexistence with ASan is a question for `make alloc` alone,
  untouched by this triage. `run_mrl_tests.sh` (`san.log:2517-2566`) and
  `run_core_tests.sh` (`san.log:3192-3209`, the log's tail) are BOTH
  clean, 27/0 and 7+1/0 respectively — this triage's one failure is
  isolated to `run_cpset_structure.sh` CHECK 4 alone, not a wave-U-wide
  sanitizer problem.

## Files

- Fix: `tests/codegen/cpset_model_check.c` (one line, `ddcc8c20`)
- san.log read: `/home/duxevents/pcrec/worktrees/validate/build/
  battery_20260918_051433/san.log` (3,209 lines, copied read-only to this
  session's scratchpad for local grep/analysis, not committed)
- Local validation logs: not committed (ephemeral `gcc-16`/script-run
  output, no scratch files persisted outside the scratchpad — build-san/
  and build/ are gitignored build trees inside this worktree)

## Validation summary for the handback

- `make -j4 CC=gcc-16`: clean.
- `make strict CC=gcc-16`: clean (`src`/`cli`/`lib` scope).
- Plain build of `cpset_model_check.c`: PASS, rc=0.
- `SAN_CFLAGS` build, `detect_leaks=0` (this box's own san posture):
  PASS, rc=0, both pre-fix and post-fix (pre-fix has no leak to see
  without `detect_leaks=1`, which K54 forbids running locally; post-fix
  the whole `run_cpset_structure.sh` — 28/28 checks — passes end to end
  under the real `SAN_ENV` shape).
- No other script's san.log section shows any sanitizer report or
  failure; `37/38 -> expected 38/38` after this fix, pending the next
  ubuntubudu run where `detect_leaks=1` is live and can confirm the leak
  report itself is gone (owed to the manager, not run here per the "one
  heavy suite at a time" / "battery is still running on ubuntubudu"
  constraints).

Branch `lane/santriage3` (commit `ddcc8c20`) is PARKED on top of main
`272bf970`, not merged.
