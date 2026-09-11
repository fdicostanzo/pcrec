# rpkg_report.md — the ruled five-item package (2026-09-10, lane rpkg)

Delivered on branch `lane/rpkg`, parked for the manager's post-battery merge
per the constraint in force for the whole working period (a battery was in
flight on this box at `build/battery_20260910_115427/`; only single-script,
single-compile probes were run — no `make test`, no suite sections, no
`mech`). Five commits, one per item plus a doc-index follow-up; each is
summarized below with what changed and how it was validated.

## Item 1 — K33/TS-4 platform scoping (commit `55aa5518`)

`tests/thread/run_stackdepth_tests.sh` arm A (the deep-tier death assertion)
now asserts SIGSEGV on Linux only. On darwin the same driver still runs and
the script RECORDS the observed outcome in a new fourth counter bucket
(`recorded`, printed as `outcomes recorded (darwin, verdict-free): N`),
distinct from pass/fail/known/skipped — modelled on
`tests/resource/run_resource_tests.sh`'s `uname -s = Darwin` SKIP shape
(the pattern the brief pointed at), but explicitly NOT a skip: the pthread
preflight above it already proves the toolchain works on this box, so
"the instrument is missing" would misstate what's actually happening.
Arms B, C and D are untouched.

**Validated**: `bash tests/thread/run_stackdepth_tests.sh` — exit 0, 5 PASS,
1 RECORD, 0 FAIL, 0 KNOWN pinned (K33's Linux pin only fires on Linux; on
darwin arm A now records rather than pins). Re-run clean at delivery.

## Item 2 — the darwin measurement (folded into item 1's commit + `docs/dev/known_issues.md`'s K33 DARWIN ADDENDUM)

Two numbers, measured live on this box (Apple M1, darwin, gcc-16, ARM64):

- **(a) Frame sizes**, `gcc-16 -fstack-usage` on the K33 witness
  (`^(a(?1)?b)$ --features recursion --engine=vm`): `rx_search` **3,184 B**
  (byte-identical to the Linux number `docs/dev/known_issues.md` already
  carries), `rx_search_deep` **131,200 B** — 16 B SMALLER than Linux's
  131,216 B. Deep-path headroom needed here: 134,384 B (Linux: 134,400 B).
- **(b) Actual pthread stack grant**: a standalone probe
  (`pthread_attr_setstacksize(&attr, 131072)`, then
  `pthread_get_stacksize_np` read back INSIDE the created thread) reports
  the thread was actually handed **143,360 B** — 12,288 B (3 pages) MORE
  than requested.

**Conclusion, stated plainly**: (b) is the cause, not (a). The ARM64 frame
is measurably almost identical to Linux's (16 B out of ~131 KB cannot
explain a 131,072 B thread not overflowing by 3+ KB); macOS silently grants
a requested `pthread_attr_setstacksize` MORE than it was asked for, and
143,360 B comfortably covers this artifact's 134,384 B deep-path headroom
(8,976 B to spare). K33's underlying defect — the deep path's storage does
not fit inside a musl-sized 128 KB thread — is real and platform-independent;
this specific REPRODUCTION (a thread sized to exactly 131,072 B) is
Linux-specific because darwin does not actually give a thread exactly that
size. Confirmed by running the real driver directly: `default`/`buffered`/
`shallow` all report `rc=1` (match) on this box, none crash.

Both numbers and the reasoning live in `docs/dev/known_issues.md`'s new
K33 DARWIN ADDENDUM section, and `tests/thread/CLAUDE.md`'s own
`run_stackdepth_tests.sh` bullet carries a matching summary.

## Item 3 — spec rephrase (commit `3dae8a10`, doc-index follow-up `eb6a9179`)

`docs/spec/limits.md` §5 and `docs/spec/match_api.md` §5.3: the K33
deep-tier fit criterion is now stated as free STACK HEADROOM AT THE CALL
SITE (`entry + deep >= 134,400 B` for the witness artifact class), not
thread-stack size — Frank's ruling from his 10KB-deep-caller point: a
call's frame lands wherever the stack pointer already sits, so a thread's
nominal size only equals its headroom at call depth ~0. Both documents keep
the measured musl-128KB / glibc-8MB numbers, now explicitly framed as
worked EXAMPLES of headroom at depth ~0 rather than as the rule itself.
Small, surgical hunks — `git diff --stat` on the two files: 35 and 8 lines
changed respectively, no section restructuring. `docs/spec/CLAUDE.md`'s own
per-file revision log got a short dated addendum on each bullet, matching
its established convention of logging every substantive pass.

**Validated**: read-through only (prose change, no code/behavior to run);
D80's "spec hunk in the same change" obligation is discharged by this item
itself plus item 1/2 being the caller-observable change it documents.

## Item 4 — gen-timeout darwin verdict (commit `2d0471a3`)

**K56 filed** (`docs/dev/known_issues.md`, INFRASTRUCTURE): Homebrew GCC
16.2.0/ARM64-darwin segfaults (rc=139) while reporting its own SIGXCPU
kill under a tight `ulimit -t`, because darwin libc's
`strsignal(SIGXCPU)` reads "Cputime limit exceeded" (no space) where Linux
glibc's reads "CPU time limit exceeded" (one space) — and gcc's driver
crashes formatting that string into its ICE report on this
platform/version. **Reproduced standalone, no pcrec involved**:
`(ulimit -S -t 1; gcc-16 -O2 -c -o /dev/null <a slow-to-compile .c file>)`
reliably exits 139 with that exact message. 16.2.0 is the newest Homebrew
gcc available on this box; a Homebrew bug-report draft exists and is held
by the manager (per the scope mandate — filing to a third party is outside
the two mandated repos).

**Fix**: `tests/lib/gen_timeout.sh`'s `gen_cc` CPU-kill detector now
accepts EITHER wording as the marker (independent of `rc`), so a
darwin-shaped rc=139-with-marker is claimed as a CPU-budget kill and gets
the normal D45 diagnostic, exactly like Linux's clean rc=152. A bare
rc=139 with NEITHER wording present (an unrelated crash) still falls
through unclaimed on every platform, Linux included — the strict clean-exit
shape there is unchanged, since real Linux gcc never emits this text for
anything but a genuine SIGXCPU delivery.

**Validated**: `bash tests/lib/run_gen_timeout_tests.sh` went from 17/18
(the CPU-fire positive control red: "CPU control fired (rc=139) but the
diagnostic is wrong") to **18/18** on this box.

## Item 5 — two riders (commits `72e246e4`, `e76342cd`)

**(a)** `tests/possessify/run_possessify_tests.sh:292` (now a few lines
later after the fix) had a bare BSD `sed -i EXPR FILE`, which BSD sed reads
as extension=EXPR script=FILE — the identical defect
`tests/mrl/run_mrl_tests.sh` already documented and fixed. Applied the same
`sed -i.bak ... && rm -f FILE.bak` shape verbatim. Also: a `gen_cc` failure
building either boundary fixture, or an unparseable `subject_ceiling`, used
to fall through the section's `if` silently — both boundary checks (the
below-ceiling agreement and the floor-is-never-an-over-promise check)
simply never ran, with no `ok`/`bad` call recording that. Added a loud
`bad()` on that path.

**Validated**: `bash tests/possessify/run_possessify_tests.sh` — 18/18, and
the two boundary checks (previously silently absent or broken by the sed
bug) now execute and pass, printed explicitly in the output.

**(b)** `docs/dev/tt4m_batch_customers.md` — `[TT-4M-TIME]`'s enumeration
half, found BY GREP rather than memory (chartered because a from-memory
count was wrong once — the CORRECTION that `san`'s `run_san_group`
re-invokes `run.sh` under `GENCFLAGS` too). Two categories: direct
`tests/harness/run.sh` re-invokers (8 sites/groups, cited file:line, each
marked whether it forwards `HARNESS_BATCH` today — only `run_axes.sh`
does), and per-pattern `pcrec`+`gcc` compile loops outside `run.sh`
entirely (`tests/bench/run_bench.sh`'s GCC-TIME loop — explicitly NOT a
real candidate, its per-pattern timing IS its measurement; `fuzz.py`'s
per-mutation compile — a genuine candidate for an analogous mechanism,
python so `HARNESS_BATCH` itself cannot reach it). Names `make mech`'s
per-sabotage `run_sabotage_matrix.sh:1952` as the highest-value unclaimed
customer on population/runtime alone — not measured, enumeration only.

**Validated**: read-only research deliverable; no code to run. `docs/dev/
CLAUDE.md`'s file list updated with the new memo's entry.

## Rulings received

None mid-flight — the brief was self-contained and no ruling request was
needed during this lane's working period.

## What's owed

Nothing from this package. The two riders' own scope is explicitly
enumeration/small-fix; item 6 in the batch-customers memo ("is wiring rows
1/2/4/6/8 worth it") is named as a future measurement question, not owed
by this lane.

## Delivery bar

Branch `lane/rpkg`, 6 commits, this report committed. Every touched test
script re-run individually and green at delivery (stackdepth 5P/1R/0F,
gen-timeout 18/18, possessify 18/18). No heavy suite run — the box's
battery (`build/battery_20260910_115427/`) was still in its `mech` stage
at delivery time; the full battery is the manager's at merge, per the
standing rule.
