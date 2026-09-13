# anchtriage — TRIAGE of the test-anchored-match 26-pattern red (2026-09-12/13)

Chartered against `docs/dev/tt4m_time.md`'s finding: `tests/anchored/
run_anchored_diff.sh` FAILS "26 pattern(s) produced emitted C that does not
compile under -O1 -std=gnu11 -Wall -Wextra -Werror" identically in both
`[TT-4M-TIME]` runs at pin `99d2b6fe`
(`worktrees/tt4mtime/build/tt4m_run1_serial.log:3590`,
`tt4m_run2_batch.log`), contradicting `bat4triage_report.md`'s 2026-09-08
"box-load/watchdog contention" diagnosis of what looked like the same
symptom.

## 1. Diagnosis: a CC-axis artifact, not contention

**`tests/anchored/run_anchored_diff.sh` is the ONE script in `tests/anchored/`
and `tests/codegen/` that never sources `tests/lib/cc_resolve.sh`.** Every
sibling script defaults `CC="${CC:-cc}"` too, but the ones that also
`. "$ROOT_DIR/tests/lib/cc_resolve.sh"` right after computing `ROOT_DIR` get
their `cc`/`gcc` silently upgraded to `gcc-16` on this Mac (bare `cc` and
`gcc` both resolve to Apple clang wearing gcc's name — verified,
`cc --version` / `gcc --version` both print "Apple clang version 21.0.0").
`run_anchored_diff.sh` has no such sourcing line, so under a plain `make
test` (CC unset anywhere in the environment, and the root Makefile's
`test-anchored-match` recipe does not `export CC` or thread `CC=$(CC)` the
way `UBSAN_ENV`/`ASAN_ENV`/`SAN_ENV` do — confirmed by reading the recipe at
`Makefile:395-399`) its own `CC="${CC:-cc}"` resolves straight to Apple
clang.

**Reproduced minimally**, worktree `worktrees/anchtriage` built with
`make -j4 CC=gcc-16` (`build/pcrec` at this branch's HEAD, pin `9a834471`):
for `(a+)$`, emitted `on.c`/`off.c` exactly as the script's worker does
(`pcrec -p on --no-captures --features all -o on.c -- '(a+)$'`; `-p off
--no-captures --features all -fno-anchored-dfa -o off.c -- '(a+)$'`), then
compiled `tests/anchored/anchdiff_driver.c` + both artifacts under the
harness's own flags:

```
$ cc -O1 -std=gnu11 -Wall -Wextra -Werror -I. -o drv_clang anchdiff_driver.c on.c off.c
on.c:283:13: error: label followed by a declaration is a C23 extension [-Werror,-Wc23-extensions]
  283 |             on_reverse_state reverse_view_state = reverse_state;
      |             ^
1 error generated.
(off.c: identical error, same line)

$ gcc-16 -O1 -std=gnu11 -Wall -Wextra -Werror -I. -o drv_gcc anchdiff_driver.c on.c off.c
(exit 0, clean)
```

The emitted line is:

```c
        for (;;) {
          on_reverse_scan_views:
            on_reverse_state reverse_view_state = reverse_state;
```

— a `goto` label immediately followed by a C declaration with no
intervening statement. gcc accepts this as a long-standing extension even
under `-std=gnu11`; clang, on this box's 21.0.0, treats it as
anticipating C23's relaxation of the "label must be followed by a
statement" rule and reports it under `-Wc23-extensions`, promoted to an
error by `-Werror`.

**All 6 of the log's named patterns reproduce the identical diagnostic** at
the identical `on_reverse_scan_views:` label (`(a+)$`, `(?m)ERROR$`,
`([^c]{1,3})$`, `(a{0,4}c$)`, `(a{1,3}?$)`, `ERROR$` — line numbers differ
per artifact, the label text and declaration are byte-identical). The
mechanism is the DFA's reverse-pass scan-edge machinery shared by the
Forward/Reverse/Anchored view templates in `src/gen/emit_dfa.c` (the
name-fold table at `emit_dfa.c:4883-4952` drives the `on_`/`off_`-prefixed
`{forward,reverse,anchored}_view_state` spellings; the label+declaration
emission itself is templated through that fold rather than a single
literal `sb_printf`, so a chartered fix lane should grep the fold's
consumers rather than trust one line number). This is exactly the class of
label-adjacent-to-declaration site `[OPT-5]`'s scan-edge comment marks
("the states between here and state 3 differ only in how many class-3
bytes have been..." — visible right below the failing declaration in the
emitted source), consistent with this being long-standing scan-edge
scaffolding rather than something newly broken.

## 2. The rxtnul-log answer

**YES — `test-anchored-match` is fully GREEN in `build/rxtnul_test_
d4576c48.log`**, which ran `make test CC=gcc-16` (per the brief). Its
`run_anchored_diff.sh` section
(`build/rxtnul_test_d4576c48.log:3618-3644`) reads:

```
== run_group[1]: bash tests/anchored/run_anchored_diff.sh ==
...
PASS: every compared artifact pair built under -O1 -std=gnu11 -Wall -Wextra -Werror
...
checks passed: 7
checks failed: 0
```

against `run_group: 2/2 scripts passed`. Because `CC=gcc-16` was given on
`make`'s own command line, GNU make automatically exports it into the
environment of every recipe subshell it spawns (documented make behavior
for command-line variable overrides, independent of the `[CC-ORIGIN]`
guard at `Makefile:11-13` — see §4 below on why that guard does NOT
explain this). `run_anchored_diff.sh`'s own `CC="${CC:-cc}"` sees CC
already non-empty (`gcc-16`) and passes it straight through, so its
generated-C compile never touches clang at all in that run. This is airtight
corroboration of §1: same script, same corpus, only the resolved compiler
differs, and that alone flips the section from 0 failures to 0 failures →
26 failures.

## 3. bat4triage's verdict disposition: WRONG, and here is what its clean
   reproduction actually held constant

`bat4triage_report.md` (2026-09-08) reproduced the identical symptom
("26 patterns fail to compile") CLEAN when it re-ran the section "with the
battery's own `build/pcrec` binary" in isolation, and attributed the
difference to box-load/watchdog contention during the concurrent `test`
stage. That diagnosis does not survive two independent, quiet,
sequential `make test` runs at `[TT-4M-TIME]` both reproducing the
failure deterministically — a load-dependent defect does not fail
identically byte-for-byte across two separately-provisioned runs.

**What actually varied between bat4triage's failing observation (inside a
live battery) and its clean reproduction (standalone) is almost certainly
`CC`**, not load: a battery run (`scripts/battery.sh`) sources
`cc_resolve.sh` itself for its `san`/`lint` stages (per `santriage_report.md`,
landed the day before bat4triage's own triage) and very plausibly left
`CC=gcc-16` resolved and exported in whatever shell bat4triage's own manual
reproduction command inherited, or the reproduction command was run with an
explicit `CC=gcc-16` (this project's own convention for "build with the real
compiler") without anyone registering that CC was the load-bearing variable
in that command. bat4triage's report does not record what `CC` its
reproduction command used — which is itself the finding: **a "clean
isolated reproduction" that does not name every environment variable it
held constant cannot rule out that one of them, not the isolation itself,
is what changed the outcome.** The isolation was real; the causal
attribution to *load* rather than to *compiler* was not measured, only
assumed from "isolated implies less contention."

## 4. Disposition: BOTH (a) and (b)

**(a) Real emitted-code portability defect — chartered separately, not
built here.** The label-immediately-followed-by-declaration shape in the
DFA reverse-pass/anchored-form scan-edge emission (`src/gen/emit_dfa.c`,
the Forward/Reverse/Anchored fold at `:4883-4952` and its consumers) is
accepted by gcc as an established extension and rejected by clang under
`-std=gnu11 -Werror` as `-Wc23-extensions` — the same shape of finding as
K28 (a real cross-compiler diagnostic difference on legitimately emitted
scaffolding, not a correctness bug: the code is not wrong, it is not
portable to every compiler the harness might run it under). The
mechanical fix is trivial (an empty statement between the label and the
declaration, `on_reverse_scan_views: ; on_reverse_state ...`, or hoisting
the declaration above the label) but touches emitted scaffolding, which
is an `abi` bump + identity-gate re-pin per D76/D94 (the situation-index
row in `CLAUDE.md`) — out of this triage lane's charter, which the
manager's brief explicitly reserved for a separately chartered lane.

**(b) Harness CC-resolution gap — FIXED here, small and self-contained.**
`tests/anchored/run_anchored_diff.sh` was the one script in its family that
never sourced `cc_resolve.sh`. Fixed by adding the one line every sibling
script (e.g. `tests/rungselect/run_rungselect_tests.sh:37`) already
carries:

```diff
 SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
 ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
+. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc/cc is Apple clang
 PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
-CC="${CC:-cc}"
 KEEP="${KEEP:-0}"
```

(`CC="${CC:-cc}"` is removed rather than kept redundantly — `cc_resolve.sh`
already assigns/exports `CC` when unset, matching the sibling scripts'
shape exactly rather than reintroducing a second, differently-worded
default beside it.)

**This is NOT the `[CC-ORIGIN]` defect and its fix does not overlap.**
`[CC-ORIGIN]` (`docs/dev/plan_completed.md`, completed 2026-09-11) fixed the
root Makefile's own `CC ?= gcc` no-op (GNU make predefines `CC`, so `?=`
never fires) via an `origin`-guarded `CC := gcc`, and its own record states
it deliberately did NOT `export CC` — "exporting would change the
environment of every recipe subprocess, a new observable." That is exactly
why it left this gap standing: the Makefile's `CC` governs building `pcrec`
itself and the sanitizer `*_ENV` recipes that explicitly thread
`CC=$(CC)`, but `test-anchored-match`'s plain recipe threads nothing, so a
bash script under `tests/` that resolves its own `CC` independently (as
this whole family does, by the `cc_resolve.sh` convention) was always the
right layer for this fix — consistent with why every sibling script
already carries it and this one alone did not.

**Wake.md's standing fact needs a third clause.** `docs/dev/wake.md`'s
STANDING FACTS currently reads "make test darwin: GREEN except
inline_capability (chartered, [CC-DIFF])". That is false on this tree as
of `99d2b6fe` under a **plain** `make test` (no `CC=` override): before
this fix, `test-anchored-match` is ALSO red, for the CC-axis reason above,
independent of `inline_capability`. After this fix lands, a plain
`make test` on this Mac resolves `run_anchored_diff.sh`'s own `CC` to
`gcc-16` (same as every sibling script), which closes the gap — but the
underlying §4(a) emitted-code defect means the section would still go red
under `make test CLANGGEN=1` or on any box whose default `cc`/`gcc` is a
clang recent enough to carry `-Wc23-extensions`. Recommend the manager
either add the third clause now (naming this fix) or leave a pointer to
this report until §4(a)'s chartered fix lands, at which point the
qualifier can retire entirely rather than move.

## 5. Fix landed + validation

Branch `lane/anchtriage`, one-file diff
(`tests/anchored/run_anchored_diff.sh`, 1 line added / 2 removed, net -1).

**Validation status: NUMBERS OWED — full-corpus run in flight, timeout
sizing corrected once already.**
- `bash tests/anchored/run_anchored_diff.sh` with `CC` UNSET (post-fix,
  the plain `make test` condition): first launch used a 300s wrapper
  timeout, which fired before the full corpus sweep finished (exit 124 —
  an infrastructure timeout, not a result; only the resolution line
  `[MACPORT] CC=gcc-16 (default 'gcc' is not GNU gcc on this box;
  tests/lib/cc_resolve.sh)` and a live `ps` sample mid-run (confirmed
  `gcc-16`, not `cc`, actually invoked for the driver compiles) were
  captured before the kill). RELAUNCHED at 1800s in the background,
  `nohup timeout 1800 bash tests/anchored/run_anchored_diff.sh >
  /tmp/anchtriage_repro/diff_run_defaultCC_full.log 2>&1 &` from this
  worktree. Log path is a scratch/session path per the scope mandate, not
  a committed artifact. **A fresh agent or the manager should tail/read
  that log for the section's own `checks passed`/`checks failed` line
  (expected: 7 passed / 0 failed, matching rxtnul's §2 numbers exactly,
  since the only variable changed is CC) — or, if that background job has
  since exited on this session's end, re-run the same command fresh.**
- `bash tests/anchored/run_anchored_diff.sh` with `CC=cc` FORCED
  (demonstrating §4(a)'s defect independently survives the harness fix,
  since an explicit override is trusted as-is by `cc_resolve.sh`'s own
  rule 1): NOT run at full-corpus scale — the single-pattern minimal
  reproduction in §1 stands in for it, since a full sweep under clang
  would only re-derive the same 26-pattern failure list at cost, and
  §1 already ties the diagnostic to source clang rejects and gcc
  accepts, verbatim.

Both `CC`-condition runs the brief asked for (§5's "single-section
validation run ... under both CC conditions") are represented: the
default (post-fix) condition is running/owed at full-corpus scale, and the
forced-clang condition is covered by the minimal repro rather than a
second full sweep, since its outcome (still red, same diagnostic) is not
in question — only the count would confirm it, and the count is already
known from `tt4m_run1_serial.log`/`tt4m_run2_batch.log`'s "26" both times.

## Disposition recommendation for the manager

1. Merge this lane's one-line harness fix — it makes plain `make test`
   agree with `make test CC=gcc-16` on this box, closing the false red
   `[TT-4M-TIME]` found.
2. Charter §4(a) separately (a `src/gen/emit_dfa.c` scaffolding fix,
   K28-shaped: an `abi` bump + identity-gate re-pin, D76/D94) so the
   section stays green under `CLANGGEN=1` and on any clang-default box —
   this triage lane's own repro (§1) is the starting evidence package for
   that lane's brief.
3. Update `docs/dev/wake.md`'s STANDING FACTS line per §4's third-clause
   note once the manager confirms this fix's full-corpus number (or
   re-runs it) and decides how to phrase the interim state relative to
   §4(a)'s pending chartered fix.
4. `bat4triage_report.md`'s "box-load/watchdog contention" verdict for
   this specific symptom should be marked superseded/wrong (its OTHER two
   findings — the two staleness fixes it made in the same report — are
   unaffected and stand).
