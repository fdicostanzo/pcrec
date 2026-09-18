# Lane mtriage report — triage of the red `make test` on main f6474777

Branch `lane/mtriage`, worktree `worktrees/mtriage`. Task: disposition the
two FAILs and the timeout in the manager's `make test` run at main
`f6474777` (the merge of `lane/k60fix` [D109] and `lane/d105` [D105]),
log `maketest_f5427d53.log` (launched 14:03:32, killed by the manager's
own `timeout 5400` at 15:31:31, `== make test rc=124`).

## Finding 1 — `[census]` FAIL: REAL, and the census did its job. RE-PINNED.

Evidence line (log, run_group under `test-resource`):

```
FAIL: [census] the raw-allocation FILE SET moved — the discipline's own
population changed and nothing named it. Expected:
cli/main.c
src/core/arena.c
src/core/compile.c
src/core/sb.c
src/gen/emit_dfa.c
src/ir/dfa.c
src/ir/nfa.c
src/opt/minimize.c
src/opt/scanedge.c
src/parse/rxt_source.c
Got: [same list minus src/gen/emit_dfa.c]
```

Hypothesis verified: commit `6e14d210` ("[D105] emit_state_legend: delete
the silent-degradation path by restructuring", main history under `d105`)
deleted all five raw `malloc`s from `src/gen/emit_dfa.c` — the four BFS
scratch arrays (`dist`/`from`/`via`/`queue`) moved to the compile's arena,
and the unbounded `path = malloc((size_t)(maxd + 1) * sizeof(int))` was
deleted outright (the legend now reads only `[0..39]`, sized statically).
Confirmed directly:

```
$ grep -c -E '\b(malloc|calloc|realloc|strdup)[[:space:]]*\(' src/gen/emit_dfa.c
0
```

So `src/gen/emit_dfa.c` left the raw-allocation population entirely — this
is exactly the census doing its documented job (`tests/resource/
run_resource_tests.sh`'s own header: "A file gaining or losing its
first/last raw allocation site is the event this section exists to make
loud"), not a broken check. **This is a delivery-bar miss on d105's part
— re-pinning a census its own change moved is squarely "RE-PIN EVERY
MANIFEST/COUNT/PIN YOUR CHANGE MOVES", no blame text needed beyond
naming it.**

**Disposition: RE-PINNED.** Removed `src/gen/emit_dfa.c` from the
`expected` manifest in `tests/resource/run_resource_tests.sh`'s
`census_allocsites()` per the check's own re-pin procedure ("Re-derive
by running this section's own grep (above) when a file's raw-allocation
population changes — never edit this list to make a red run pass without
re-reading why it moved"). Population is now 9 files. Re-ran the grep by
hand first and it matches the new pinned list exactly. Committed as
`4576e105`.

No other reader of the file-set/count needed a matching update:
`docs/dev/decisions.md`'s D105 entry and `docs/dev/k60_measurement.md`
both describe the file's PRE-fix allocation shape as history (the
decisions.md passage is explicitly headed "STATUS 2026-09-18 (superseded
by the line above)"), and `tests/core/CLAUDE.md`'s `[D105]` section
already documents the post-fix state ("`emit_state_legend`'s five raw
allocations per emitted machine are gone") accurately — d105's own lane
wrote it correctly there; only this one census manifest was missed.

## Finding 2 — `nm could not read arm_a.o`: the documented standing darwin red. No fix.

Evidence line (log, `test-codegen`'s `run_group`, section 5 of 9):

```
FAIL: nm could not read arm_a.o (no rx_search symbol) — no verdict is evidence here
```
— from `tests/codegen/run_inline_capability.sh` line 192's `bad "$NM could
not read $o.o (no rx_search symbol) — no verdict is evidence here"`, and
nothing else: `run_group` reports `8/9 scripts passed` for `test-codegen`,
this is the sole failure, and `make[1]: *** [test-codegen] Error 1` is the
only error line the section produces.

This matches `docs/dev/wake.md:124-125`'s recorded "Known pre-existing
darwin red: `tests/codegen/run_inline_capability.sh`'s `nm could not read
arm_a.o`. It carries `TEST_RC=2` on an otherwise green suite." Both merged
lanes independently confirmed and A/B-verified it as pre-existing at their
own branch points:
- `docs/dev/lanes/k60fix_report.md:144-145`: "one red, `run_inline_capability.sh`
  (\"nm could not read arm_a.o (no rx_search symbol)\"), reproduces
  IDENTICALLY on the unmodified [tree]."
- `docs/dev/lanes/d105_report.md:288-295`: "`make test-codegen CC=gcc-16`
  … one red: `run_inline_capability.sh` — same before and after the merge
  … PRE-EXISTING and A/B verified … fails identically."

**Disposition: NO FIX. Standing darwin-only infrastructure limitation**
(the script's own `nm`-must-work precondition failing on this box/toolchain
combination, not a pcrec regression), reproduced independently by three
parties (wake.md's prior record, k60fix, d105) at three different tree
states. Nothing to change.

## Finding 3 — the timeout is a finding: too tight a bound for a suite that grew, not an anomalous run

**Sections that completed** (whether green or red) before the 15:31:31
kill, walking the log in `TEST_SECTIONS` order and matching each
section's own `bash tests/…`/`GROUP_PROCS=… run_group.sh` invocation:

| # | section | outcome |
|---|---|---|
| 1 | test-corpus | PASS |
| 2 | test-cli | PASS |
| 3 | test-reject | PASS |
| 4 | test-registry | PASS |
| 5 | test-parse | PASS |
| 6 | test-gentimeout | PASS |
| 7 | test-codegen | **FAIL** (Finding 2, sole cause) |
| 8 | test-vm | PASS |
| 9 | test-possessify | PASS |
| 10 | test-rungselect | PASS |
| 11 | test-counterk | PASS |
| 12 | test-mrl | PASS |
| 13 | test-prefilter | PASS |
| 14 | test-altcls | PASS |
| 15 | test-island | PASS |
| 16 | test-assertions | PASS |
| 17 | test-atomic | PASS |
| 18 | test-backrefs | PASS |
| 19 | test-lookaround | PASS |
| 20 | test-recursion | PASS |
| 21 | test-encseam | PASS |
| 22 | test-resource | **FAIL** (Finding 1, sole cause) |
| 23 | test-capturediff | PASS |
| 24 | test-known-fail | PASS |
| 25 | test-thread | PASS |
| 26 | test-stackdepth | PASS |
| 27 | test-premul-table | PASS |
| 28 | test-anchored-match | PASS |
| 29 | test-search-pinned | PASS |
| 30 | test-vm-frameless | PASS |
| 31 | test-dfa-uniform-fold | **KILLED mid-run** (`Terminated: 15`) |
| 32-40 | test-tune-dial, test-prefilter-collapse, test-rxtsource, test-definitions, test-entry-shape-identity, test-cpset-structure, test-startbnd, test-uprops, test-core | **never started** |

**30 of 40 sections completed** (28 green, 2 red — both disposed above),
section 31 was mid-execution when killed (its own §1 and §2 both printed
PASS; the kill landed inside §3, the full-corpus fold-population sweep —
plausibly that script's most expensive part), and the remaining 9 sections
never launched. `TEST_SECTIONS` is confirmed to hold exactly 40 targets
(`Makefile:208-218`, counted by hand).

**The bound was too tight, not the run anomalously slow.** `docs/dev/
tt4m_time.md` (measured 2026-09-12/13, lane tt4mtime, on this exact Mac)
records a clean serial `make test` at **5124.29s (~85.4 min) wall**, the
only recorded full-suite darwin serial timing. But that measurement was
taken against a **38-section** suite (its own text: "batching can only
touch 2-3 of the suite's 38 sections"); `TEST_SECTIONS` today has grown to
**40**. The manager's run had elapsed 15:31:31 − 14:03:32 = **87m59s
(5279s)** — already past the recorded 85.4-minute baseline in wall time —
while still 10 sections short of finishing (section 31 in progress, 32-40
unstarted). That is consistent with, not contradictory to, the documented
baseline: the suite has grown by 2 sections since the baseline was taken
(and `docs/testing.md`'s own "Tiered testing" note says outright the suite
"keeps growing, because the project only ever ADDS tests"), so the true
current serial wall time exceeds 5124.29s, and the manager's 5400s (90 min)
bound left essentially no margin over a baseline that was already stale
by two sections' worth of work. **Recommend raising the bound** (e.g. to
7200s/2h) for future darwin serial `make test` runs, or re-measuring the
current 40-section serial baseline once wave 2 settles.

**No concurrent-load explanation.** d105's "full-corpus emit-diff" (the
box's one heavy item the journal names as running during the k60fix/d105
lanes) had already completed well before the manager's run started: the
lane's own report committing its emit-diff numbers (`f9a96049`, "[D105]
lane report: the restructuring, the pins, and both emit-diff arms") is
timestamped 13:47:56, and the merge completing `[D105-BUILD]` (`f6474777`)
landed at 14:01:49 — the manager's `make test` launched at 14:03:32, two
minutes after the merge and roughly 16 minutes after d105's own heavy run
had already finished and been reported. No overlap; the slow-down is fully
explained by the two-more-sections-than-baseline gap above, with no need to
invoke box contention.

## Validation

- `make strict`: GREEN (`strict: whole tree compiles clean with -Werror
  -Wshadow`).
- `bash tests/resource/run_resource_tests.sh`, Section 0 alone: GREEN —
  `PASS: [census] raw allocation sites live in exactly the 9 pinned
  files: cli/main.c src/core/arena.c src/core/compile.c src/core/sb.c
  src/ir/dfa.c src/ir/nfa.c src/opt/minimize.c src/opt/scanedge.c
  src/parse/rxt_source.c`.
- Full `run_resource_tests.sh` (all sections): **GREEN.** `checks passed:
  27`, `checks failed: 0`, `checks inconclusive: 0`, `sections skipped: 1`
  (Section 2, the darwin `ulimit -v` skip, per `[MACPORT]` — expected on
  this box).
- Full `make test`: **NUMBERS OWED.** Launched in background per the
  DO-THEN-FINISH lifecycle rule, wrapped in `scripts/watchdog`, AFTER this
  report's commit:

  ```
  cd /Users/fdicostanzo/pcrec/worktrees/mtriage && \
  scripts/watchdog -s 14400 -m 8000000 -c 14400 -S mtriage_maketest -- make test \
    > /private/tmp/claude-501/-Users-fdicostanzo-pcrec/bf752a3a-7b5d-4184-b1df-a27e9c576db1/scratchpad/mtriage_maketest.log 2>&1 &
  ```

  Output/completion: the harness's own final `checks passed:`/`checks
  failed:` summary and section trailer at the tail of that log; the
  watchdog's own audit line (`ts=... section=... label=mtriage_maketest
  verdict=... wall=... cpu=... peak_rss_kb=... exit=... cmd=...`) is
  appended to `worktrees/mtriage/build/watchdog.log` on completion.

## Commits

- `4576e105` — `tests/resource: re-pin the allocation-site census file
  set (9 files, not 10)` on `lane/mtriage`.

## Handback

Sent to "main" before ending this turn (see the SendMessage in this
session). Owed: the full `make test` run's final `checks failed:` /
watchdog exit line, from the background log named in that handback.

**Never merge to main** — this report and the branch are for the manager
to review and merge.
