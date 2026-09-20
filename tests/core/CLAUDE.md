# tests/core — unit checks on an internal helper that belongs to no single feature

[REVW.U L5-R0.3] (`docs/dev/reviews/lens_reports/lens5_unit_seams.md` R0.3):
this directory is the home for a NEW check on a `src/core/`-style helper
whose subject spans more than one feature directory, or belongs to no
feature at all. It is NOT a generic `tests/unit/` — every existing
unit-shaped check in this tree stays co-located with the suite that owns
its subject (`tests/codegen/cpset_model_check.c`,
`tests/parse/branch_count_check.c`, `tests/mrl/cwmax_check.c`,
`tests/backrefs/fold_agreement*_check.c`, `tests/utf8/
startbnd_backend_check.c`, `tests/registry/*.c`) — moving them here would
be a second home for something that already has one, for zero gain.

## What this directory is for

A helper qualifies for a check here when its SUBJECT does not belong to any
one existing test directory. The first instance
(`sat_arith_check.c`) checks three functions living in three different
directories (`src/opt/mrl.c`, `src/gen/emit_vm.c`, `src/opt/callgraph.c`) —
no single existing test directory owns all three. `sb.c`/`arena.c`
(`src/core/`) and the growable-array/text-kit primitives wave 1 builds
(R3/R4 of the same lens 5 report) are the intended future population.

## The build

Every check here builds through `tests/lib/unit_cc.sh`'s `unit_build`
function — the ONE way an internal-property check is compiled (`-Ilib
-Isrc`, `$SANFLAGS` threaded, `$LIBPCREC` linked, `-Werror` unconditionally).
See that file's own header for the policy argument.

## The cost budget (R0.4)

A shape, not a stopwatch: **one gcc invocation and one process spawn per
SUBJECT.** No check in this tier may invoke `pcrec` or `gcc` per case (that
is a differential driver and belongs in the suite that owns the feature,
under D45's gen-timeout budgets), and no check in this tier may read the
`.rxt` corpus. `sat_arith_check.c` is one binary holding several sub-checks,
`cwmax_check.c`'s own established pattern.

## Files

- **sat_arith_check.c** / **run_core_tests.sh** — [REVW.U L5-R2] THE
  SATURATING-ARITHMETIC AGREEMENT: `pcrec_mrl_sat_add`/`pcrec_mrl_sat_mul`
  (`src/opt/mrl.c`), `pcrec_vm_fadd`/`pcrec_vm_fmul` (`src/gen/emit_vm.c`) and
  `pcrec_cg_sat_add`/`pcrec_cg_sat_mul` (`src/opt/callgraph.c`) must agree — the tree
  states the requirement twice in prose (`src/opt/CLAUDE.md`'s `mrl.c`
  entry, `emit_vm.c`'s own comment above `pcrec_vm_fadd`) and, until this check,
  enforced it nowhere. Checked for CROSS-FAMILY EQUALITY over the
  non-negative domain every real caller uses (which also answers lens 1's
  own open question — `pcrec_cg_sat_add`'s extra `CG_EXP_INF` guard is redundant
  on that domain, proved by evaluation rather than by reading) and for
  three algebraic laws the callers rely on and the implementations do not
  themselves state: MONOTONE, CAPPED, ABSORBING. See the check's own
  header for the domain argument (why no pair literally pairs `LLONG_MAX`
  with itself — that is genuine signed-overflow UB in the subject
  functions, and this file is wired into `san_scripts.txt`, so a real hit
  there would ABORT the sanitizer battery rather than FAIL cleanly) and
  the four-sabotage failing-direction story, of which one — a one-character
  boundary weakening in `pcrec_mrl_sat_mul` — is invisible to every answer-level
  check in the tree by construction (it under-estimates, which is
  `pcrec_minw`'s safe direction). Sabotage row S254.

  **The six functions are not `static` any more** (`src/opt/mrl.c`,
  `src/gen/emit_vm.c`, `src/opt/callgraph.c`, declared in
  `core/internal.h` beside `pcrec_minw`) — a linker cannot reach a
  file-private symbol from a separate translation unit, and this check
  calls the shipped functions directly rather than transcribing their
  bodies (a transcription checks only itself). No behaviour change: this
  is pcrec's own compile-time arithmetic, never emitted into generated
  text, so it is not an `abi` event.

  Written against TODAY's three separate implementations. Lens 1's X3
  (wave 2 of the code review) unifies them into `pcrec_sat_add`/
  `pcrec_sat_mul` taking the ceiling as a parameter; this check must keep
  passing unchanged against the unified pair — that is what proves the
  unification changed nothing, and the six declarations in `internal.h`
  retire with it, not before.

- **sb_fragf_check.c** — [REVW.2] wave 2 stage 3: `pcrec_sb_fragf`'s own
  property, below any emitted artifact. The primitive promises that
  truncation is impossible BY CONSTRUCTION, and stage 3 routes ~90 retired
  hand-sized emitter scratch buffers through it, so this one function is
  where the K38 class becomes either impossible or universal. **No
  answer-level check in this tree can see which**: lens 10 measured that
  nothing truncates today at a 60-byte prefix, and every corpus test runs
  at `rx`, two bytes — so a wrong size argument here would drop the last
  byte of every long fragment and the whole suite would stay green. Six
  sub-checks: agreement with an independent `snprintf` over a 4,001-row
  length sweep crossing every retired fixed size; the result's length is
  EXACT; an empty format returns a real empty string and never NULL; a
  239-byte identifier derived from a `PCREC_MAX_PREFIX_LEN` prefix is
  complete (the K38 witness, past `vm_rolef`'s 160); an earlier fragment
  survives 400 later ones across an arena block boundary with no aliasing
  (the property that distinguishes a fragment from the stack buffer it
  replaces); and the mixed-conversion case including `%%`.

  **ITS OWN BLIND SPOT, MEASURED RATHER THAN ARGUED, and it is the reason
  to read the file's header before trusting the row.** Two plants were
  tried. A wrong `vsnprintf` SIZE argument turns 5 of the 6 sub-checks red.
  An ALLOCATION one byte short does not move it at all — and does not move
  AddressSanitizer either, because `arena_alloc` rounds to 16 and zeroes,
  and ASan sees only the arena's own 64 KiB block `malloc`, never the
  intra-block slice. So "sized exactly to the result" is enforced at the
  format call and is unobservable at the allocation, by every instrument
  this tree has.

- **sb_stamp_check.c** — [REVW.2] wave 2, EP2 step 10 / lens 1 X8:
  `pcrec_sb_stampf`/`pcrec_sb_stampwf`/`pcrec_sb_stamp_str`, the artifact-stamp primitives,
  which emit `#define <UPPER>_<NAME> <value>` at all 73 former hand-written
  stamp sites across the two emitters. **ITS JUSTIFICATION IS THE OPPOSITE
  OF `sb_fragf_check.c`'s ABOVE, and the file's header says so first**: every
  byte these write lands in the emitted `.c`, so the four byte-identity gates
  and the full-corpus emit-diff DO see a defect here, immediately and on
  thousands of artifacts. A check whose justification is borrowed from its
  neighbour is a check nobody can size.

  What it adds is two things the gates cannot give. **(a) WHICH property
  broke** — a gate says "artifact differs at byte 4,117"; these sub-checks say
  "the separator space is gone" or "the name field is right-justified".
  **(b) THE PARAMETER SPACE THE SHIPPED SITES DO NOT REACH** — they use
  exactly two padding widths (9 and 24) and one prefix length (`rx`, two
  bytes), where this sweeps widths 0..64 against name lengths 1..64 and builds
  one stamp at `PCREC_MAX_PREFIX_LEN`. Six sub-checks, oracle an independent
  `snprintf` into an oversized buffer.

  **FOUR PLANTS, AND THEY DO NOT BEHAVE ALIKE** (transcripts in the header
  and in `docs/dev/lanes/w2x_report.md`). The separator space deleted takes
  five sub-checks red and leaves 6 correctly GREEN (still one line, the wrong
  one). The newline dropped takes all six. `pcrec_sb_stamp_str` losing its quotes
  takes ONLY sub-check 4, which is that sub-check's whole reason for existing
  separately. And the sharpest: **`%-*s` written `%*s` leaves sub-check 1
  GREEN**, because at width 0 the two spellings are identical — which is why
  the sweep has to carry the width, and why 30 of the 37 `emit_vm.c` call
  sites could not have caught it.

- **alloc_inject.h** / **alloc_check.c** / **run_alloc_tests.sh** —
  [REVW.U L5-R1] THE ALLOCATION-FAILURE INJECTOR (`make alloc`, opt-in,
  NOT part of `make test`). `alloc_inject.h` is `-include`d ahead of
  every source file in a SEPARATE build tree (`ALLOC_DIR := build-alloc`
  in the Makefile — the `make ubsan`/`make asan` shape one axis over;
  nothing under `src/`/`cli/`/`lib/` is edited, `build/` is never
  touched), redirecting every `malloc`/`calloc`/`realloc`/`strdup` call
  to a `pcrec_inject_*` function `alloc_check.c` defines, so the check
  can force the Nth allocation in a real `pcrec_compile()` call to
  return NULL and assert the library never `abort()`s, segfaults, or
  silently succeeds — only diagnoses. One `fork()` per trial (the
  outcomes under audit include SIGABRT, which cannot run in-process
  without taking the whole sweep with it), K (allocations per witness)
  measured by a "never fail" profiling pass rather than guessed, over
  three fixed witnesses (R0.4's tier budget: no per-case `pcrec`/`gcc`
  call, so this is a deliberate, named exception rather than a
  corpus sweep).

  **CONFIRMS F1 (fix-now #1, `23eb3d34`) IN BOTH DIRECTIONS.** Built at
  `23eb3d34`'s parent (F1 unrepaired) and pointed at the `--engine=vm`
  witness `[a-z]{2,10}`: `1 of 11 forced allocations KILLED THE PROCESS
  BY SIGNAL ... signal 6` (SIGABRT — `sb_grow`'s unattached-buffer
  `abort()`, `scr_test`/`scr_desc`'s own reaching sequence). On the
  current (fixed) tree the same witness: `every one of 11 forced
  allocation failures was diagnosed ... never abort/signal/success`. See
  `docs/dev/lanes/waveu_report.md` for the full transcript.

  **AND IT FOUND K60 (docs/dev/known_issues.md, filed not fixed) ON ITS
  FIRST REAL RUN** — its own two other witnesses (a plain DFA compile,
  and `\p{L}` under `-e utf8`, which needs `[K53-SELRETRY]`'s drop rung
  to compile at all) show `pcrec_compile` SUCCEEDING despite a forced
  allocation failure, at a real, non-trivial rate (21% / 8% of the
  allocations swept): a stale per-attempt eligibility flag
  (`cx.size_cap_refused`/`cx.dfa_overflowed`, never reset between
  retries) and the size-term ladder's own documented "ANY reason means
  this K is out" catch-all both absorb a genuine OOM as "try a different
  internal attempt" rather than propagating it — invisible to every
  existing check because the final artifact is a correct compile with
  `rc == 0`, and invisible to `tests/resource/`'s `ulimit -v` approach
  because an address-space limit cannot be steered to a non-final
  attempt specifically.

  **[K60MEAS] (2026-09-18, lane k60meas) — TWO NEW MODES AND A FOURTH
  WITNESS, and the K60 text above is now WRONG about the mechanism.**
  `docs/dev/k60_measurement.md` is the memo; read §5 before citing K60.
  The instrument gained:
  - **SUSTAINED mode** (`--sustained`/`--both`): fail allocation N *and
    every allocation after it*, against today's single-shot mode. What it
    settles is that single-shot cannot tell "degraded gracefully" from "the
    next allocation happened to succeed", because in single-shot mode it
    always does. Measured: W3 collapses 25 absorbed → **0**, W4 108 → **0**,
    W1 15 → **5** (and those five are the compile's LAST five allocations,
    so nothing needs memory after them).
  - **CALL-SITE attribution** (`--sites`): the four macros carry
    `__FILE__`/`__LINE__` through to the injector, which reports the forced
    allocation's own site. Text substitution rather than `backtrace()`,
    because on darwin `backtrace_symbols` cannot name a `static` function
    in a statically linked archive and every allocation site here is in one.
    This is what turns "15 of 72 absorbed" into an attributed mechanism.
  - **W4, the SIZE-TERM LADDER witness** — a real corpus pattern, found by
    sweeping the corpus with an attempt-counting probe. It exists because
    the `[ART-SIZE]` ladder's blanket catch is one of the two mechanisms
    K60 names and **W1-W3 structurally cannot reach it** (the ladder's own
    `fit.chosen == ENGM_VM` conjunct excludes the two DFA witnesses; W2 is
    far below the `emit_code` threshold). On its first run it measured
    **108 of 158 (68.4%)** — the worst rate in the file — all of them
    genuine `ctx_nomem`-routed allocations.

  **[K60FIX] (2026-09-18, lane k60fix) — W4's 108/158 IS NOW 0/158.**
  K60's ladder-class mechanism (the
  `[ART-SIZE]` catch, W4's own witness) is fixed at the recovery point
  (`src/core/compile.c`'s `setjmp` handler tests a new `Ctx.failed_nomem`
  field FIRST — see `docs/dev/decisions.md` D109). Re-running `make alloc
  --both` on the fixed tree: `PASS: W4 ... every one of 158 forced
  allocation failures was diagnosed` (was `FAIL: 108 of 158 ...
  SUCCEEDED THROUGH anyway`), W2 unchanged (0/11 PASS), and **W1 (15/72
  single-shot, 5/72 sustained) and W3 (25/328 single-shot) were UNCHANGED
  BY THIS FIX** — both are `emit_state_legend`'s silent degradation
  (mechanism (A)), which never calls `ctx_nomem` and could not be reached
  from this fix by construction; that class was lane d105's.

  **[D105] closed it the same day** (`6e14d210`): the legend's raw
  allocations are DELETED rather than rerouted, so W1 reads 15 → 0 and W3
  25 → 0 in both modes. **`make alloc` is now green on all four
  witnesses and K60 is closed in both its classes**, so — unlike the two
  days this note's previous wording covered — any FAIL from `make alloc`
  is a real regression, whichever witness it names. The pins below are
  what make that statement checkable rather than remembered.

  **The four injector symbols are `pcrec_inject_*_at` now, and the rename
  is the point.** This header is `-include`d and the Makefile's object rule
  names its prerequisites by hand (no `-MMD` in this tree), so editing
  `alloc_inject.h` leaves `build-alloc/` STALE — and the four functions are
  resolved at LINK time from a separate TU with no shared prototype, so a
  stale one-argument call against a four-argument definition is a wild
  pointer and a SIGSEGV *inside the injector*, indistinguishable from the
  abort/signal outcome the check exists to detect. Measured on this
  instrument's first extension: 60 of 72 trials read "killed by signal 11",
  entirely a stale tree. Changing the injector's ABI now changes its symbol
  NAMES, so a stale object fails to link instead.

  **[D105] (2026-09-18, lane d105) — THE WITNESSES ARE PINNED NOW, on TWO
  numbers each, and the legend class is FIXED.** `emit_state_legend`'s five
  raw allocations per emitted machine are gone (`src/gen/emit_dfa.c`; the
  compile refuses through the arena's `ctx_nomem` instead of dropping a
  legend silently), so W1 reads 15 absorbed -> **0** and W3 25 -> **0** in
  both modes. Each `Witness` row carries two kinds of expectation:
  - a POPULATION expectation — the profiling pass's own allocation count
    swept. It exists because "no absorption" is a claim this check can
    satisfy by NOT REACHING THE COMPILE (K35), and it is not
    belt-and-braces: W3's SUSTAINED sweep absorbs zero even against the
    UNREPAIRED library, so the absorption expectation alone reads PASS
    there and only the population one catches it. D105's own evidence is
    this number moving — W1 72 -> 57, W3 328 -> 303, exactly the deleted
    allocations.
  - `expect_absorbed_single` / `expect_absorbed_sustained`, what a FILED,
    OPEN defect accounts for, with `absorbed_why` naming it. A mismatch in
    EITHER direction fails: above is a regression, below means the defect
    moved or was fixed and the expectation is stale — so a fix re-pins its
    own witness instead of quietly turning a red line green. Both K60
    classes are now closed (D105 + D109 below), so every row pins these at
    exact zero and `absorbed_why` is NULL on all four — any absorption
    anywhere is a regression.

  **[D110] (2026-09-18, lane allocpins) — THE POPULATION EXPECTATION IS A
  FLOOR (`Witness.min_total`), NOT AN EQUALITY PIN.** The trigger was
  measured, not guessed: `[REVW.2]`'s wave 2 slices A+C moved W4's
  population 158 -> 162 by two BYTE-NEUTRAL, SIZE-NEUTRAL refactors
  (`pcrec_sb_fragf`'s fragment retirement changing the arena-call SHAPE, nothing
  a caller can observe) — an equality pin re-pins on that kind of ordinary
  churn exactly as readily as on K35's actual hazard (a population that
  FALLS, toward an empty or partial sweep), which is a tax on every future
  allocation-shape-moving refactor for no corresponding signal. Each
  witness's `min_total` is now HALF its population as measured at the
  ruling (W1 57 -> 28, W2 11 -> 5, W3 303 -> 151, W4 162 -> 81): far enough
  below the live population that an ordinary refactor's incidental
  movement (four allocations out of 162, the measured instance) has wide
  margin, and still high enough that a real collapse trips it. Absorption
  expectations are UNCHANGED — still exact, both directions, in both modes.
  Verified in the failing direction: a scratch edit setting W2's floor to
  1000 (population 11) reads `FAIL: W2 (VM cursor rung): the swept
  POPULATION fell BELOW its floor -- 11 forced allocations, floor 1000`
  (and the `[sustained]` twin), `checks failed: 2`. See
  `docs/dev/decisions.md` D110 and `tests/resource/run_resource_tests.sh`
  section 2b, which now asserts this file's own verdict rather than only
  its abort/signal outcome (below).

  **`run_alloc_tests.sh` pipes `2>&1` into its log**, because `alloc_check`
  writes PASS to stdout and FAIL to stderr: without it the script's own
  failure message counted `^FAIL` out of a file that could not contain any
  and reported "0 witness(es) misbehaved" on every red run (found while
  validating D105). It defaults to `ALLOC_ARGS=--both`, so `make alloc`
  runs both sweeps. `tests/resource/run_resource_tests.sh` section 2b —
  the `make test` caller — runs this binary **argument-free**, on the
  single-shot sweep alone (its own claim needs no more), but per D110 now
  reads this binary's OWN verdict (rc and the absence of `SUCCEEDED
  THROUGH` lines) in addition to the signal grep — see that section's own
  header comment for the reasoning: both K60 classes are closed, so an
  absorption reappearing (from a regression OR from the population
  collapsing below its floor) is exactly what `make test` should now
  refuse to pass silently. `make alloc` (opt-in) rides `scripts/
  battery.sh`'s `alloc` stage (D110) — `make test` itself is NOT the home
  for the per-witness pins, only for section 2b's coarser verdict check.

Maintenance: update this file when files are added/removed or their roles change.
