# waveu — [REVW.U] the code review's NETS wave

Lane `waveu` (sonnet), branch `lane/waveu`, PARKED on 4 commits off main
`1d4a7548`. Authority: `docs/dev/reviews/2026-09-17-code-review.md` §3
wave U; detailed specs in `lens_reports/lens5_unit_seams.md` (R0, R1, R2)
and `lens_reports/lens8_error_cleanup.md` (F6).

## Summary

| deliverable | commit | status |
|---|---|---|
| L5-R0 — name the unit tier | `9a422f1d` | done, validated |
| L5-R2 — sat-arithmetic agreement check | `d2955d96` | done, validated |
| L5-R1 — allocation-failure injector | `c6afe149` | done, validated |
| L8-F6(a)/(b)/(c) | `2271370c` | done, validated |

`make strict` clean throughout (checked after every deliverable).
Full `make test` launched at hand-off per DO-THEN-FINISH — see
"Owed" below for the log path and exact completion line to check.

---

## Deliverable 1 — L5-R0: name the unit tier

`tests/lib/unit_cc.sh`'s `unit_build` function is the one build for the
ten pre-existing internal-property checks the lens report found
scattered across six directories with four divergent flag policies.
Adopted IN PLACE (not relocated, per the brief) at the seven sites that
link only `libpcrec.a`: `cpset_model_check.c`, `branch_count_check.c`,
`cwmax_check.c`, `registry_check.c`, `pcre2_check.c`,
`definitions_check.c`, `definitions_oracle_gen.c`.

**Scoping decision, not an oversight**: the two `fold_agreement_check.c`
sites (`tests/backrefs/run_backref_diff.sh`) and
`startbnd_backend_check.c` (`tests/utf8/run_startbnd_diff.sh`) stay on
their existing `$GENCFLAGS`/`gen_cc` regime — they compile alongside a
GENERATED matcher artifact, which is a deliberate, already-uniform
policy for generated code (D45's budgets) and orthogonal to the four
divergent policies R0 is about. Documented in `unit_cc.sh`'s own header.

**A real defect surfaced and fixed**: `tests/registry/definitions_check.c`
had four `RegDef` struct literals one field short (5 of 6, relying on
C's zero-fill) — invisible under this site's previous no-`-Werror`
build, `-Wmissing-field-initializers` under R0.1's unconditional
`-Werror` policy caught it immediately. Fixed (trailing `, NULL` on each,
matching `registry.c`'s own documented precedent for the same field).

**Validated**: all seven adopted sites rebuilt clean and green
individually; `bash tests/registry/run_registry_tests.sh` (the heaviest,
chains PC-3) 623/0 including PC-3's own 209/0; `make strict` clean.

R0.2 (add `run_cpset_structure.sh`/`run_mrl_tests.sh` to
`san_scripts.txt`) was **already done** by the prior `fixnow` lane
(commit landed on `main` before this lane branched) — confirmed by
reading `tests/lib/san_scripts.txt` at branch point, not re-done.

---

## Deliverable 2 — L5-R2: the saturating-arithmetic agreement check

`tests/core/sat_arith_check.c` (new home: `tests/core/`, per R0.3 — a
check whose subject spans more than one feature directory). Checks
`mrl_sat_add`/`mrl_sat_mul` (`src/opt/mrl.c`), `vm_fadd`/`vm_fmul`
(`src/gen/emit_vm.c`) and `cg_sat_add`/`cg_sat_mul`
(`src/opt/callgraph.c`) for cross-family equality plus three algebraic
laws (Monotone, Capped, Absorbing) — a requirement `src/opt/CLAUDE.md`
and `emit_vm.c`'s own comment state twice in prose and enforced nowhere.

**One src/ edit, deliberately minimal**: the six functions are no
longer `static` (declared in `core/internal.h` beside `pcrec_minw`) —
a linker cannot reach a file-private symbol from a separate translation
unit, and the alternative (transcribing the bodies into the check) would
defeat the check's whole point (comparing three SPELLINGS of one
algorithm, not writing a fourth). No behaviour change: this is pcrec's
own compile-time arithmetic, never emitted into generated text, so it
is not an `abi` event — confirmed by the build being byte-neutral (no
codegen paths touch these functions).

**A2 rider answered by evaluation, not by reading**: lens 1's X3 flagged
`cg_sat_add`'s extra `CG_EXP_INF` guard as "appears redundant." CHECK 1
runs the three implementations over the non-negative domain every real
caller uses and finds zero disagreement — the guard IS redundant on
that domain (proven, not read), which the check's own PASS line states.

**Sabotage S254** (mrl arm "core", newly registered in
`tests/mech/run_sabotage_matrix.sh`): `mrl_sat_mul`'s boundary guard
weakened `a > MRL_MINW_MAX / b` → `a >= ...`. This is lens 5's own "the
one that matters" — it under-estimates by one, `pcrec_minw`'s SAFE
direction, so no answer-level check in the tree can see it.

Hand-verified before committing: `checks passed: 7 / checks failed: 0`
clean; with the plant, `mul: mrl_sat_mul/vm_fmul/cg_sat_mul DISAGREE at
(1, 549755813889): 1099511627776 / 549755813889 / 549755813889` — exactly
the predicted boundary pair, `checks passed: 6 / checks failed: 1`.

**Verified through the real mech driver** (`bash tests/mech/
run_sabotage_matrix.sh S254`, tree `d2955d96`):

```
S254-mrl-sat-mul-boundary-off-by-one  src/opt/mrl.c  ...  core  core:1fail/6pass  DETECTED
```

`make test-core` wired into `TEST_SECTIONS`/`.PHONY`, `san_scripts.txt`
(threads `$SANFLAGS` via `unit_build`).

---

## Deliverable 3 — L5-R1: the allocation-failure injector

`tests/core/alloc_inject.h` (`-include` header, redirects
`malloc`/`calloc`/`realloc`/`strdup` to `pcrec_inject_*`) +
`tests/core/alloc_check.c` (the check driver, defines the four
functions calling the REAL allocators unless steered to fail) +
`tests/core/run_alloc_tests.sh`, wired as opt-in `make alloc`
(`ALLOC_DIR := build-alloc`, one extra `CFLAGS` flag — the `make
ubsan`/`make asan` shape one axis over). **Zero edits under
`src/`/`cli/`/`lib/`; `build/` never touched.** Builds the LIBRARY only
(not `all`/the CLI binary — nothing defines the injected symbols for a
standalone `pcrec` binary, and the library is the one artifact this
axis needs).

Reclassified from lens 8's assumed DESIGN-EVENT tier to LOCAL per the
manager synthesis's own ruling (§4 row M2) on this exact spelling.

### The F1 red/green transcript (the deliverable's acceptance criterion)

Witness `W2` (`[a-z]{2,10}`, `--engine=vm` — forced explicitly; AUTO
selection routes this pattern to the DFA by default and never reaches
`vm_cursor_rep`/`scr_test` at all, a correction to the naive reading of
lens 8's own witness description, made after the first draft's
witnesses showed no signal-class result on either tree).

**Built at `23eb3d34`'s PARENT (`93b066ae`, F1 unrepaired)** — `git
archive 93b066ae` into the session scratchpad, `make BUILD_DIR=build-alloc
CFLAGS="-O1 -g -include .../tests/core/alloc_inject.h" build-alloc/libpcrec.a`:

```
FAIL: W2 (VM cursor rung): 1 of 11 forced allocations KILLED THE PROCESS
BY SIGNAL (K7's abort() class) -- first at N=3, signal 6
```

Signal 6 = SIGABRT — `sb_grow`'s unattached-buffer `abort()`, exactly
F1's own reaching sequence, live.

**Same witness on the current (F1-fixed) tree:**

```
PASS: W2 (VM cursor rung): every one of 11 forced allocation failures
was diagnosed (rc == -1, non-empty message), never abort/signal/success
```

### K60 — found on the injector's first real run, filed not fixed

Two other witnesses (W1, a plain DFA compile of `[a-z]+`; W3, `\p{L}`
under `-e utf8 --features unicode-props`, which needs
`[K53-SELRETRY]`'s drop rung to compile at all) show `pcrec_compile`
**SUCCEEDING** despite a forced allocation failure, on the CURRENT
(already F1-fixed) tree, at a real rate: 15/72 (21%) and 25/328 (8%) of
allocations swept. Confirmed by reading `src/core/compile.c`:
`cx.size_cap_refused`/`cx.dfa_overflowed` are set once and **never reset**
across retry attempts, so a genuine allocation failure on a non-final
attempt is misread by a later rung's eligibility test as "another size
overflow" and silently retried away; a sibling mechanism (the
size-term ladder's own documented "ANY reason, this K is out" catch-all)
likely explains W1, which never approaches any size cap at all. Filed
as **K60** in `docs/dev/known_issues.md` with three dispositions left to
Frank (K59's own precedent for a filed retry-ladder finding), deferred
rather than fixed — a design question about the retry ladder's shared
`setjmp`, out of this wave's scope.

**A real pipeline-exit-status bug found and fixed along the way**: both
new scripts (and `run_core_tests.sh` from deliverable 2) originally used
`if "$BIN" | tee "$OUT"; then` — a pipeline's exit status is `tee`'s,
never `$BIN`'s, so a genuinely failing check would have reported green.
First caught when `make alloc` printed its "every allocation diagnosed"
success line despite two `FAIL:` lines in the same output. Fixed with
`${PIPESTATUS[0]}` (the `run_registry_tests.sh` precedent already in
the tree). Re-verified: `make alloc` now correctly exits nonzero (K60);
`make test-core` stays green (unaffected, sat_arith_check always passed).

---

## Deliverable 4 — L8-F6(a)/(b)/(c)

All three land in `tests/resource/run_resource_tests.sh`, which owns the
`ctx_nomem` discipline's checks.

**F6(a) — the grep-derived allocation-site census (new Section 0).**
Replaces the header's own hand-written six-file claim (stale: the code
review found `src/opt/scanedge.c` and `src/gen/emit_dfa.c` had both
gained raw allocations since it was written, unnoticed). A FILE-SET
manifest, not a bare count (K35 — an exact count disarms via its own
failure message; the file set is the population the discipline's claim
is actually about). Current population, confirmed by the check's own
first run: 10 files, 40 sites (`cli/main.c` 9, `arena.c` 1, `compile.c`
1, `sb.c` 2, `emit_dfa.c` 5, `dfa.c` 3, `nfa.c` 1, `minimize.c` 7,
`scanedge.c` 10, `rxt_source.c` 2). Per-file counts printed, never
pinned.

**F6(b) — a darwin-viable positive control (new Section 2b).** Section
2's `ulimit -v` approach is Linux-only and has been the discipline's
ONLY positive control since [M4.7b] — SKIPPED on this dev box since the
2026-09-04 Mac move, and F1 shipped and lived unnoticed in exactly that
window (the code review's own F6 finding, now closed). Section 2b runs
unconditionally on both platforms using the deliverable-3 injector,
building its own scratch library under `$WORKDIR/build-alloc/` (never
the top-level tree). **Deliberately scoped to K7's own promise, not
K60's**: it greps the injector's labelled output for `KILLED THE
PROCESS BY SIGNAL` specifically and ignores the "succeeded anyway"
category — `make test` must not go red for a filed-not-fixed defect
that belongs to `make alloc`, not to this section.

**F6(c) — three sabotage rows, the discipline's first (zero before
this).** All in mech arm `resource` (pre-existing; this is its first
row targeting this class):

- **S255** (`arena.c`) — `ctx_nomem`'s conditional neutered to `if (0)`,
  every arena allocation failure aborts.
- **S256** (`sb.c`) — same shape, every StrBuf realloc failure aborts.
- **S257** (`compile.c`) — the attachment block drops `csb`/`hsb`'s
  `.cx` entirely, F1's own shape on the PRIMARY code-string buffer.

**Validated**: full `run_resource_tests.sh` run on the current tree,
27/0. Verified through the real mech driver — one row per invocation
(`run_sabotage_matrix.sh`'s usage is `[S<id>]`, a single optional
filter, not a list; the first attempt passing three IDs silently ran
only the first), against tree `2271370c`:

```
S255-arena-ctx-nomem-neutered        src/core/arena.c    resource  resource:1fail/26pass  DETECTED
S256-sb-ctx-nomem-neutered           src/core/sb.c       resource  resource:1fail/26pass  DETECTED
S257-compile-csb-attachment-dropped  src/core/compile.c  resource  resource:1fail/26pass  DETECTED
```

All three: 26 of 27 `run_resource_tests.sh` checks stay green under the
plant, and exactly the new Section 2b check (K7's abort-promise) goes
red — the plant reaches the injector's witnesses (all three route
through the sabotaged allocator) and nothing else in the file, which is
the correct, narrow signature for this class of defect.

---

## Mech verification

Ran individually (`bash tests/mech/run_sabotage_matrix.sh S255`, `...
S256`, `... S257`) against tree `2271370c`. `mech run COMPLETE: 1 rows
(unexpected: 0, undetected: 0, unreached: 0, anomalies: 0,
oracle-skipped: 0)` on each of the three runs.

---

## Directory CLAUDE.md updates

- `tests/lib/CLAUDE.md` — `unit_cc.sh` entry added.
- `tests/core/CLAUDE.md` — new, all four files documented (sat_arith
  check + the three injector files), including the F1 transcript
  summary and K60.
- `tests/resource/CLAUDE.md` — Section 0/2b documented in the file
  listing; new "[REVW.U L8-F6(c)]" section for the three sabotage rows.
- `docs/testing.md` — new "The unit tier and the allocation-failure
  injector ([REVW.U], 2026-09-17)" section (D80: caller-observable
  surfaces — a new `make` target, a new test section — carry their
  process-record hunk in the same change).
- `docs/dev/known_issues.md` — K60 filed.

## What's left (owed)

- **Full `make test`** is the lane's LAST act (DO-THEN-FINISH), launched
  backgrounded. Log: `build/waveu_test.log` in this worktree. Completion
  line to grep: `sections ran: N/N` (the trailer's own summary format —
  see `tests/lib/test_trailer.sh`). NOT read by this lane; a fresh agent
  or the manager reads it and completes the delivery per BOILERPLATE.
- **Known pre-existing red, not this wave's**:
  `tests/codegen/run_inline_capability.sh`'s darwin nm-probe FAIL (named
  in the brief as out of scope).
- **K60 itself** is filed, not fixed — three dispositions left to Frank,
  per the brief's own instruction not to improvise a bigger design when
  a spec item's premise doesn't hold as expected (here: the injector
  found something bigger than F1 alone, and fixing it is a design
  decision, not a nets-wave task).
