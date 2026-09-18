# tests/resource — what compiling a pattern COSTS

Every other suite in this tree asserts something about the LANGUAGE: what a
pattern matches, which diagnostic it draws, which engine it routes to. This one
asserts something about the PROCESS — peak memory, wall and CPU time, and the
manner of failure — because K7 was a bug that no assertion about the language
could see.

## Files

- **run_resource_tests.sh** — the [M4.7b] K7 pin, now SIX sections (this
  list itself was stale — missing 1b — until [SIZECAP-CPU] below):

  0. **[REVW.U L8-F6(a)] The allocation-site census.** Every raw
     `malloc`/`calloc`/`realloc`/`strdup` call in `src/`+`cli/`, swept by
     grep and compared as a FILE SET against a pinned manifest — replacing
     the header's own hand-written six-file claim, which the code review
     found stale (`src/opt/scanedge.c` and `src/gen/emit_dfa.c` both
     gained raw allocations since it was written, unnoticed). Per-file
     site counts are PRINTED, never pinned (K35: a count is a shape a
     legitimate refactor moves; the FILE SET is the population this
     discipline's own claim is about).

  1. **Bounded outcome.** Eleven large-bounded-repeat shapes (K7's own repro
     list plus multi-byte, class and choice-point bodies) each compile or draw
     a diagnostic, under a peak-tree-RSS ceiling and wall/CPU budgets enforced
     by `scripts/watchdog`. A watchdog kill (122/123/124), an abort (134) or a
     SIGKILL (137) is a FAILURE — those are the four ways K7 used to end.
     WHICH shapes compile and which refuse is deliberately NOT asserted: that
     boundary is `PCREC_MAX_SUBSET_ELEMS`'s to move, and pinning it here would
     make this file a control calibrated against the thing it controls.

  1b. **[ART-SIZE]/D84 — the `size_moved` loop.** Shapes whose ACCEPTANCE
      moved when the emitted-size caps landed, pinned with the size each
      used to produce and re-driven through the total-cap refusal plus the
      `--max-emit-bytes` override's round trip. This loop's own refusal
      path can cost roughly 2x an ordinary compile — a cap hit retries once
      under [K59-PREMUL]'s drop ladder before refusing again — so it runs
      under `SIZECAP_CPU`, a WIDER CPU budget than section 1's `K7_CPU`
      ([SIZECAP-CPU], 2026-09-18, lane btriage2: `battery_20260918_051433`
      killed this loop's row 1 at `K7_CPU`'s 45s on ubuntubudu, a materially
      slower single core than the Mac dev box that calibrated it — not box
      contention, the battery's own load line was near-idle). See the
      loop's own header comment in the script for the measurement.

  2. **A failed allocation is diagnosed, not aborted.** Four compiles under a
     40 MB (25 MB for the last) `ulimit -v`, which makes malloc genuinely
     return NULL partway through. Each must exit 1 with a diagnostic, never
     134. This is a positive control for `ctx_nomem()` and the seven
     allocation sites that route to it, and it is a SEPARATE section for a
     reason: with the section-1 budget in place, those shapes are refused by
     the budget long before any malloc fails, so section 1 cannot reach the
     allocator paths at all. Revert `ctx_nomem` to `abort()` and section 2
     fails while section 1 stays green.

  2b. **[REVW.U L8-F6(b)] A darwin-viable positive control, unconditional.**
      Section 2's `ulimit -v` approach has been the DISCIPLINE'S ONLY
      positive control since [M4.7b], and it has been SKIPPED on this dev
      box since the 2026-09-04 Mac move — F1 (Job.scr_test/scr_desc's
      missing `.cx` back-pointer, fix-now #1 of the 2026-09-17 code
      review) shipped and lived unnoticed in exactly that window. Section
      2b runs on BOTH platforms: `tests/core/alloc_check.c`'s allocation-
      failure INJECTOR (`tests/core/CLAUDE.md`) steers a chosen Nth
      allocation to fail — no `ulimit`, no platform dependency — and this
      section asserts K7's own promise specifically (no forced allocation
      failure kills the process). It builds its OWN scratch injected
      library under `$WORKDIR/build-alloc/` (never `build/`, never the
      top-level `build-alloc/` — `make alloc`'s own tree) using this
      script's already-resolved `$CC`.

      **Deliberately scoped narrower than `make alloc`'s own verdict.**
      The injector's three witnesses also surface K60
      (docs/dev/known_issues.md, filed 2026-09-17, not fixed): a compile
      can SUCCEED despite a forced allocation failure, via an unrelated
      retry-ladder absorption mechanism. That is real and already
      tracked in the opt-in `make alloc` target; `make test` must not go
      red for a known, disposed defect that is not this section's job.
      Section 2b greps the injector's own labelled output for
      `KILLED THE PROCESS BY SIGNAL` specifically (K7's abort()-class
      outcome) and ignores the "succeeded anyway"/"empty message"
      categories.

  3. **The refusal's identity.** `a{0,65535}` must refuse inside the existing
     "too complex for the DFA engine" family AND name the subset construction,
     so a reader knows which of the two DFA bounds they hit; and an
     exponential-blowup pattern must still reach the state-COUNT cap, which
     is how this file notices if the new bound ever took the old one's
     customers away.

## [TT-10] the load guard (2026-08-25)

Section 1's cells assert a CPU/wall/RSS ceiling, and two of them
(`[a-z]{0,30000}`, `(a|b){0,30000}`) were measured going RED under real box
contention even though `K7_CPU` is already CPU-accounted through
`scripts/watchdog -c` — CPU-time ACCOUNTING itself inflates under real
contention, not merely wall stretching around fixed work (K31 addendum,
`docs/dev/plan.md`). `tests/lib/load_guard.sh` (its own header carries the
measurement and the threshold justification) is sourced here: a 123 (CPU
exceeded) or 124 (wall exceeded) outcome is reclassified **INCONCLUSIVE** —
a third, separately-counted outcome, never PASS, never FAIL — when the
1-minute load average / `nproc` exceeds `LOAD_GUARD_RATIO` (default 2.0) at
the moment that specific cell's watchdog kill fires. Every other outcome (0,
1, 122, 134, 137) is unaffected, since none of them can be produced by CPU
inflation. D45-style budgets (`K7_CPU`/`K7_MEM`/`K7_SECS`) are unchanged by
this. Validated solo (19/0/0, unchanged) and under an 8-way `yes`-spinner
artificial load (green-or-INCONCLUSIVE, never FAIL — see
`docs/dev/dev_journal.md` for the run's numbers).

## [MACPORT] Section 2 is a loud SKIP on darwin (2026-09-04)

`ulimit -v` (RLIMIT_AS) is not enforceable on macOS at all — verified live:
`ulimit -v N` itself errors ("cannot modify limit: Invalid argument")
rather than merely failing to bind. Section 2's own positive control
already treats an unbinding limit as a FAILURE (K7's own "a silently
vacuous control" rule), which is correct on Linux and would score every
cell FAIL on darwin for a platform limitation, not a real regression.
Frank's ruling (interim disposition): `run_resource_tests.sh` detects
`uname -s = Darwin` and prints one `SKIP:` line naming the whole section,
counted in a new fourth bucket (`sections skipped`) distinct from
pass/fail/inconclusive — never a fabricated pass, never a red run for
something this platform cannot do. The Linux path (including the "limit
did not bind" FAILURE branch) is unchanged. Section 1 and Section 3 are
unaffected and run identically on both platforms (26 checks, 0 failures,
measured on Apple M1 Max/Darwin 25.6, CC=gcc-16).

## Why this suite is not on the sanitizer axes

`make ubsan`/`asan`/`lint` do not run it, by design. Section 2 needs
`ulimit -v` to force a real allocation failure, and an ASan build reserves tens
of terabytes of address space at startup — every case would die before `main`.
Section 1's memory ceiling has the mirror-image problem: instrumentation
legitimately multiplies footprint, so a ceiling calibrated on the plain axis
either flakes under ASan or is loosened until it asserts nothing. Resource
promises are measured on the axis they are made on. The `test-resource` target
in the Makefile carries the same note.

## Env

`PCREC` (default `build/pcrec`), `K7_MEM`, `K7_SECS`, `K7_CPU` (section 1's
own bound; see the script's own header for its current defaults, which have
moved since this paragraph was written and are not re-copied here per this
file's own K35 lesson). `SIZECAP_CPU` (default `90`, [SIZECAP-CPU]
2026-09-18) is section 1b's OWN, wider CPU budget — see that section's entry
above. Same revisit-when as D45's budgets: a LEGITIMATE case measured needing
more raises the default with the measurement recorded, never silently.

Maintenance: update this file when files are added/removed or their roles change.

## [OPT-4.1] the size-rung cell became a PAIR (2026-08-30)

`(a|b){0,30000}` was the tree's ONE witness that ruling B's size rung ships an
artifact where the exact one is refused. It is also NULLABLE — its collapsed
language `(a|b)*` matches the empty string at every position — so under
[OPT-4.1] the rescue is DECLINED there and the artifact ships with NO prefilter
instead, which is smaller still and rescues the compile just as well.

**SO THE ROW IS TWO CELLS NOW, AND EACH IS THE OTHER'S CONTROL.**
`(a|b){0,30000}` must compile small with `RX_VM_PREFILTER "none"` and no
language macro; `(a|b){1,30000}` — the same pattern one character over, NOT
nullable — must still take the rung and stamp `_LANG_WHY "size cap retry,
exact N > cap"`. Neither direction is safe alone: without the twin, a compiler
that had stopped taking the size rung at all would leave the nullable cell
green (no prefilter is exactly what it asserts) while every oversize
collapsible pattern started refusing; without the nullable cell, a compiler
that had stopped declining would leave the twin green while shipping a scan
that can never dismiss a position.

**AND THE TWIN IS THE `size cap retry` STAMP VALUE'S ONLY WITNESS IN THE
TREE** (K35). No corpus pattern reaches either rung at the default, and
pcrec-bench reaches neither across 74 forms (its O-10 ask (v)); the other two
`size_moved` rows are DFA-engine artifacts, which take no VM prefilter
decision at all. If the twin is ever removed, that bucket becomes tested only
by `make check`.

The nullable cell's own contract is that nothing which compiles today stops
compiling: dropping the prefilter is strictly smaller than collapsing it, so
the rung still rescues (`docs/spec/limits.md` §3.3 states it caller-side).

## [LIM-1] the pair's own verdict moved from LANG_WHY's prefix to ENGINE_SEL (2026-08-30)

D90's fold-in gave the SIZE rung's own SUCCESS a distinct `RX_ENGINE_SEL`
value, `"size-cap-retry"` — before this it stamped `"selected"`,
indistinguishable from a compile that never touched any cap
(`docs/spec/match_api.md` §6.3's own value table names the gap this closed).
`(a|b){1,30000}`'s cell is that value's STANDING WITNESS: nothing else in the
tree reaches `RX_ENGINE_SEL "size-cap-retry"` (`tests/codegen/
run_prefilter_collapse.sh` §7b's own `sel_witness size-cap-retry` reuses this
exact pattern rather than inventing a second one, per this pair's own
one-witness-two-readers precedent). The verdict now reads `RX_ENGINE_SEL`
directly rather than a `${szwhy#size cap retry}` string-prefix test; `LANG_WHY`
is still read and still reported, for the byte comparison it alone carries.
`(a|b){0,30000}`'s nullable twin gained the matching check —
`RX_ENGINE_SEL "declined-nullable"` — since [LIM-1] widened that value's own
reach from the [SEL-1] rung alone to both rungs (`src/opt/select_engine.c`'s
own comment at the fit site has the derivation).

## [OPT-4.2] the tripwire cell FLIPPED (2026-08-31)

The `[OPT-4.2 tripwire]` cell just below the pair above (this file's own
manager-filed comment, dated 2026-08-31) pinned a KNOWN, dated gap rather
than a fix: [OPT-5]'s scan edge made `'(a|b){0,30000}'` compile comfortably
under every cap, so it never reaches either rung above and the [OPT-4.1]
decline — scoped to `collapse_reason != CR_NONE` — never applied to it. The
ordinary hybrid still built and shipped its own EXACT prefilter, nullable or
not, at 34,522 B, hybrid/exact — the same 1.2-9.9x loss shape as the pair
above, on a population [OPT-4.1] never covered.

[OPT-4.2] generalizes the decline off the rung entirely
(`src/opt/select_engine.c`'s `prefilter_declined_nullable_default`), and the
cell now asserts the FIXED behavior instead of the gap: `RX_VM_PREFILTER
"none"`, `RX_ENGINE_SEL "declined-nullable-default"`, no `_LANG_WHY` macro at
all (there is no prefilter left to name a language for). It is kept as a
THIRD cell rather than folded into the pair above, because it is testing a
DIFFERENT population from either rung cell: no cap is ever hit here, so the
one thing distinguishing this row from an ordinary `"selected"` compile is
the decline itself.

## [REVW.U L8-F6(c)] the discipline's first sabotage rows (2026-09-17)

The `ctx_nomem`/`abort()` discipline had ZERO sabotage rows before this —
`arena.c`, `sb.c`, and `compile.c`'s own attachment block were all
untouched by `tests/mech/sabotages/` (the code review's F6 finding).
Three rows now, all in mech arm `resource` (this file), each verified
DETECTED in both directions via `bash tests/mech/run_sabotage_matrix.sh
<id>` against the committed tree:

- **S255** — `src/core/arena.c`: `arena_alloc`'s `ctx_nomem` route
  neutered (`if (0)` instead of `if (a->cx)`), so every arena allocation
  failure aborts, on every compile.
- **S256** — `src/core/sb.c`: `sb_grow`'s `ctx_nomem` route neutered the
  same way, so every StrBuf realloc failure aborts — every attached
  buffer, not only the two F1 missed.
- **S257** — `src/core/compile.c`: `compile_driver`'s attachment block
  drops `csb`/`hsb`'s `.cx` back-pointer entirely — F1's own shape
  (fix-now #1, `23eb3d34`), reproduced on the PRIMARY code-string buffer
  rather than `scr_test`/`scr_desc`.

Each is caught by Section 2 (Linux, `ulimit -v`) AND Section 2b (both
platforms, the allocation-failure injector) — the two are independent
instruments over the same population, and a row detected by only one
would be worth a note about which.
