# santriage — battery san/lint instant-exit triage

Lane: santriage (sonnet). Branch `lane/santriage`, worktree
`worktrees/santriage`. Task: diagnose why the stage-4 merge battery
(`build/battery_20260908_stage4/`, commit 83f7175b) read `san` rc=2 and
`lint` rc=0, both in ZERO seconds (00:23:46 -> 00:23:46 per the trailer),
against a normal `make san` runtime of ~45 min.

## 1. What happened

`build/battery_20260908_stage4/san.log`:

```
== san: building the compiler axis at build-san/ ==
cc -O1 -g -fsanitize=address,undefined,leak -fno-sanitize-recover=undefined -Wall -Wextra -std=gnu11 -Ilib -Isrc -c -o build-san/obj/core/arena.o src/core/arena.c
clang: error: unsupported option '-fsanitize=leak' for target 'arm64-apple-darwin25.6.0'
make[1]: *** [build-san/obj/core/arena.o] Error 1
make: *** [san] Error 2
```

`build/battery_20260908_stage4/lint.log`:

```
== lint: gcc -fanalyzer ==
lint: SKIP gcc -fanalyzer: cc does not support -fanalyzer on this box
lint: SKIP clang-tidy: not installed
lint: SKIP cppcheck: not installed
lint: clang found but not used as a second compiler here -- see docs/testing.md rejection note
lint: done
```

Both stages ran (not a launch/mis-invocation problem — `scripts/battery.sh`'s
stage loop faithfully captured each `make`'s own real exit code and moved
on); both died/no-opped one command deep, hence zero wall time.

## 2. Root cause (same cause for both)

`scripts/battery.sh`'s `san` and `lint` stages invoke `make san` / `make
lint` with no `CC=` override, so both build the COMPILER AXIS (`src/core/
arena.c` etc.) through the Makefile's own `CC ?= gcc` default (Makefile:4).
On this Mac, `gcc` and `cc` both resolve to `/usr/bin/gcc`/`/usr/bin/cc`,
which is **Apple clang 21.0.0**, not GNU gcc:

```
$ gcc --version
Apple clang version 21.0.0 (clang-2100.1.1.101)
Target: arm64-apple-darwin25.6.0
```

The real GNU gcc on this box is Homebrew's `gcc-16` (16.2.0) at
`/opt/homebrew/bin/gcc-16`, exactly as `tests/lib/cc_resolve.sh` already
documents and as BOILERPLATE.md's worktree-build convention already
requires (`make -j4 CC=gcc-16`) — but `cc_resolve.sh` was wired only into
test SCRIPTS (its own header: "does NOT change the top-level Makefile's own
`CC ?= gcc` default"), and `scripts/battery.sh`'s stage-loop `make`
invocations were never given the same treatment. This is the SAME class of
defect as the harness bug fixed at c480414c ("tests/harness/run.sh hardcoded
CC='gcc'... EVERY harness section had compiled generated code with clang
since the Mac move") — that fix covered the COMPILEE axis (generated
matcher code inside the test harness); this lane's finding is the sibling
gap in the COMPILER axis for the `san`/`lint` Makefile targets specifically.

**`san`**: `-fsanitize=leak` is an outright unsupported flag under Apple
clang on arm64-apple-darwin (a hard compiler error, not a silent no-op —
different in kind from K26's Linux finding that LeakSanitizer is a
*runtime* no-op there). The build dies on the FIRST object file
(`build-san/obj/core/arena.o`), before any of the other two sanitizers or
any suite script runs, hence rc=2 in under a second.

**`lint`**: the Makefile's own `lint:` target guard-probes
`$(CC) -fanalyzer -fsyntax-only ...` before doing any real analysis
(Makefile:1309), and correctly detects that Apple clang has no
`-fanalyzer` at all — so it SKIPS, echoes why, and (since clang-tidy and
cppcheck are also not installed on this box) reaches `lint: done` having
run **zero** static analysis. The guard's SHAPE is legitimate (an explicit,
loud SKIP line per tool, never a silent pass) — but on this box, run with
the default `$(CC)`, it means `make lint` has been a complete no-op on
every Mac battery since the move, which is exactly the "a stage that can
never fail is worse than a stage that fails loudly" failure mode: it reads
green and asserts nothing.

## 3. Classification

Environment/battery.sh defect, not a stage-4-merge effect and not a new
darwin incompatibility in pcrec itself. Confirmed by history:

- The Mac move happened 2026-09-04 evening (fifty-third session part 1,
  `docs/dev/dev_journal.md:21390`, "THE MAC: wake on the new box").
- The only prior `battery_v5` run whose journal entry records `san`
  actually completing GREEN (`docs/dev/dev_journal.md:21171`, "san 55 min
  (34 scripts, -P4)") was the fifty-second session's 13:4x run on
  2026-09-04 — which STARTED at `docs/dev/dev_journal.md:21048` (09:2x),
  BEFORE the Mac move (part 1 is later the same day). That run was on the
  old Linux box, where bare `gcc` genuinely is GNU gcc.
- Every full-battery `san`/`lint` GREEN mentioned in the journal AFTER the
  move (2026-09-05 "the battery started 11:45", 2026-09-08's night runner
  "san 35/35; axes 24080/24080") is explicitly on `ubuntubudu`
  (`docs/dev/dev_journal.md:22169`, "on ubuntubudu"), the Linux reference
  box, not the Mac.
- `build/battery_20260908_stage4/` is `scripts/battery.sh` run locally in
  this Mac repo — the first time this script's `san`/`lint` stages have
  ever actually executed on darwin.

So this was a latent gap since the Mac move, surfaced for the first time
today because this is the first Mac-local `battery.sh` run, not something
the stage-4 merge (a fold-closure Unicode change, nothing near
`scripts/battery.sh` or the Makefile's sanitizer/lint machinery) caused.

## 4. Fix

`scripts/battery.sh` now sources `tests/lib/cc_resolve.sh` (same file
`tests/harness/run.sh` already uses) right after its existing
`ncpu.sh`/`loadavg.sh` sourcing, and passes the resolved `CC` explicitly to
the `san` and `lint` stage `make` invocations only:

```
san)
    SAN_PROCS="$SAN_PROCS" make CC="$CC" san > "$slog" 2>&1
    ;;
lint)
    make CC="$CC" lint > "$slog" 2>&1
    ;;
```

`CC` is also threaded through the detached-subshell `printf %q` splice at
the bottom of the file (the same mechanism every other stage knob —
`TEST_MAKE_J`, `SAN_PROCS`, etc. — already uses), since the setsid'd
`bash -c` is a fresh process that inherits nothing implicitly.

`test`/`strict`/`axes`/`mech` are deliberately UNTOUCHED: they build pcrec
itself under plain ISO C (no `-fanalyzer`, no sanitizer flags), which Apple
clang compiles correctly, so their already-green (or independently-red,
per bat4triage's `test` triage) results are unaffected by this change.
Whether those four stages should ALSO build under `gcc-16` for full
consistency with the "gcc is the target compiler" convention (D2) is a
broader question this lane did not take — nothing about them is currently
broken.

`docs/dev/CLAUDE.md`... no — `scripts/CLAUDE.md`'s `battery.sh` entry is
updated in the same commit with a `[SANTRIAGE]` paragraph naming the defect
and the fix, per the directory-CLAUDE.md convention.

## 5. Validation (read + probe only, per the box hold — no san/lint/battery run started)

1. `bash -n scripts/battery.sh` — syntax OK.
2. Reproduced the EXACT failing compile line from `san.log`, swapping `cc`
   for `gcc-16`, into the session scratchpad (not `build-san/`):
   ```
   gcc-16 -O1 -g -fsanitize=address,undefined,leak -fno-sanitize-recover=undefined \
       -Wall -Wextra -std=gnu11 -Ilib -Isrc -c -o <scratch>/arena_san_test.o src/core/arena.c
   ```
   rc=0, real `.o` produced (23016 bytes). This is the smallest possible
   repro of the `san` fix, not a build of the `build-san/` tree.
3. Reproduced the `lint:` target's own guard probe with `gcc-16`:
   ```
   gcc-16 -fanalyzer -fsyntax-only -x c -std=gnu11 - < /dev/null
   ```
   rc=0 (Apple clang's identical probe is what produced the SKIP line in
   today's log). This proves the guard will now take the "run the real
   analysis" branch instead of skipping, without running the analyzer over
   the whole tree.
4. Verified `tests/lib/cc_resolve.sh`'s resolution AND the `printf %q`
   round-trip used to carry `CC` into the detached subshell, in isolation
   (no `make`, no battery launch):
   ```
   $ . tests/lib/cc_resolve.sh; echo "$CC"
   [MACPORT] CC=gcc-16 (default 'gcc' is not GNU gcc on this box; tests/lib/cc_resolve.sh)
   gcc-16
   ```
   round-tripped through `printf %q`/`eval` unchanged.
5. Did NOT run `make san`, `make lint`, or `scripts/battery.sh` itself
   (box was under the stage-4 battery's own mech tail when this lane
   started, and BOILERPLATE.md's rule is single-command probes only while
   held).

## 6. Owed to the manager

- A real `make san CC=gcc-16` / `make lint CC=gcc-16` run, post-battery, on
  a quiet box — this lane proved the LAUNCH defect is gone, not that the
  full suites are clean under gcc-16 end to end.
- `make lint CC=gcc-16` will be doing REAL static analysis on this box for
  the first time ever; expect it may surface findings the guard's silent
  skip has been hiding since the Mac move. That triage is separate from
  this lane's launch-defect fix.
- Whether `test`/`strict`/`axes`/`mech` should also build under `gcc-16`
  for full consistency with D2 ("gcc is the target compiler") is an open
  question this lane did not take a position on — they are not currently
  broken.

## Rulings received

None — no manager ruling arrived mid-flight; this lane ran start to finish
on its original brief.
