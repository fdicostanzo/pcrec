# Lane cc — [CC-CLANG] steps 1+2 report

**STATUS: DELIVERED.** Both steps are code-complete, fully validated against
the manager's pinned validation order, and every finding that order surfaced
is fixed and re-verified. `abi` moved 13→14. Branch `lane/cc`, not merged,
not pushed. See "Branch" below for the full commit list.

## Summary for someone in a hurry

Step 1 (clang compatibility) shipped with THREE real bugs found and fixed by
its own validation, not just the one incompatibility the plan row's probe
named:

1. **The named one**: a frameless VM artifact's fail label emitted an
   indirect `goto *` with no address-of-label expression anywhere in the
   function — clang refuses this, gcc accepts it. Fixed by gating the whole
   pop-and-resume dispatch on `has_push` (`v.npush > 0 || v.has_linked_calls`).
2. **Found by `run_codegen_tests.sh` itself**: my first comment explaining
   the omission spelled out the literal token `RX_CALL`, tripping a
   call-free-artifact literal-presence check — the exact "a comment
   mentioning a denylisted symbol trips it" trap this codebase's TS-1
   section already documents. Reworded.
3. **Found by clang-compiling with `-Werror` (this project's actual default
   GENCFLAGS)**: the frameless branch's guard (`if (resume_depth==0) return
   -1;`, no `else`) is a real fall-off-the-end bug — **both gcc and clang
   reject it** ("control reaches end of non-void function"). Fixed by making
   the return unconditional, since `resume_depth` is provably always 0 there.
4. **Found by the CLANGGEN=1 sweep mechanism's first real run**: the
   reverse-deterministic rung's `iteration` counter is write-only under a
   bare unbounded `X*` — gcc's `-Wunused-but-set-variable` doesn't catch a
   write-only local reached only via `x++`; clang's does. Fixed by adding it
   to this file's own existing per-loop `(void)`-cast list (which already
   handles three sibling locals for the identical reason) and correcting
   that list's comment, which wrongly claimed `iteration` is used by every
   shape.

Each fix moved emitted bytes, so `abi`'s identity-gate FILEPIN was re-pinned
five times across the change; the final pin is `ec6f481`. Every fix was
re-verified against `run_codegen_tests.sh` (106/106), the identity gate
(16/16, all 4 axes, both comparisons — run in full, not sampled), `make
test-codegen` (5/5), `make strict` (clean), direct gcc/clang `-Werror`
compiles of all 11 rule-1 fixtures plus the original probed witness, gcc
answer-identity spot-checks, and CLANGGEN=1 runs over three corpus
directories (named_groups, recursion, base — 5,425 case assertions, 0
failures after the fixes). The one-time `make CC=clang` compiler survey
found pcrec's own sources compile with zero warnings under clang.

## Step 1 — clang compatibility (abi 13→14)

**The `noclone` fix.** `src/gen/emit_dfa.c`'s `emit_search_head` wraps
`__attribute__((noclone))` in a general `__has_attribute` feature-detection
guard rather than naming clang. gcc keeps emitting the attribute (it has
`__has_attribute`, and `__has_attribute(noclone)` is true there); clang's
reads false, so the line compiles out entirely instead of warning.

**The frameless-dispatch fix.** `src/gen/emit_vm.c`'s fail label used to
unconditionally end with the pop-and-resume block. A program with no
`RX_PUSH` site and no `RX_CALL` site anywhere in its tree can never make
`run->resume_depth` leave 0, so that block is unreachable — and its `goto *`
is the only place in such a program that would take a computed address at
all, which is what clang refuses and gcc accepts. The gate is `has_push =
v.npush > 0 || v.has_linked_calls`, computed once early. **Both terms are
load-bearing**: `v.npush` deliberately does *not* count a linked call site's
own frame (`vm_count_slots`'s `A_CALL` arm says so explicitly), but `RX_CALL`
still increments `resume_depth` at run time — relying on `npush` alone would
leave a call-only, alternation-free program with a live push and no dispatch
to service it, a real miscompile. Found by tracing `vm_count_slots`'s
`A_CALL` arm and `RX_CALL`'s macro body side by side, not by inspection.

**abi 13→14**, all four D76 sites touched, plus the identity gate's FILEPIN
— re-pinned FIVE times across this change as each subsequent fix moved more
emitted bytes (`c657ae9` → `8e0b624` → `353306a` → `c13fd7b` → `ec6f481`,
final). All five re-pins sit either before `goto <p>_L0;` or after
`<p>_accept:` in the emitted text, so comparison (A) — the byte-identical
claim against the unchanged pre-module pin `ac4917d` — is untouched by every
one of them; confirmed directly (see "Validation" below), not just argued
structurally.

### The downstream break: `[DD-14-RECURSION rule 1]`'s own relation was wrong

`run_codegen_tests.sh`'s rule 1 asserted `goto *` count == `1 (fail label,
always) + shared callee bodies`. That "always" is exactly the invariant
step 1 breaks. Working through `vm_count_slots`'s arms and the splice/link
eligibility rule, the frameless population is bigger than the plan row's own
probe named: **a bare `(a)b`, and any pattern where every subroutine call
splices to a callee with no internal choice point of its own, is also
frameless** — not just a counter-rung bounded repeat. Of the fixture's
eleven rows, seven were genuinely push-free and moved `want` 1→0; the other
four all carry a self-recursive call (forcing linkage) wrapped in an
internal `?` that pushes on its own account regardless of linkage, so they
are unmoved. Fixed the relation to `(has_push ? 1 : 0) + shared callee
bodies` and the fixture table; updated `tests/codegen/CLAUDE.md`'s matching
entry. **This is the fact for the journal/plan row at merge**: the frameless
population is bigger than the charter names, and `has_push` is the general
correct condition rather than scope creep.

Two adjacent, pre-existing inconsistencies noticed but **not** touched (out
of scope, flagged for whoever owns them next): `S168`'s `SAB_DOC_FIGURE`
text still narrates pre-wave-G `goto *` counts (a drift from before splice
existed); `run_codegen_tests.sh`'s rule-1 comment cites "sabotage row S166"
but `S166_callgraph_binds_early.sh` is actually rule 3's sabotage.

### Bug 2 — the `RX_CALL` comment leak (found by `run_codegen_tests.sh`)

The first wording of the `has_push == false` comment explained the omission
by naming what's absent — "no RX_PUSH, no RX_CALL site" — which spells the
literal token `RX_CALL` into a call-free or fully-spliced artifact's own
text. `[DD-14-RECURSION rule 2]`'s literal presence check caught it
immediately: exactly the "an emitted comment that merely mentions a
denylisted symbol will trip it" trap this codebase's own TS-1 section
documents, with the identical fix — reword rather than weaken the check.
Reworded to "no linked subroutine call" (no literal `RX_CALL` token).
Commit `353306a`.

### Bug 3 — `-Wreturn-type` fall-through (found by clang-compiling the fixtures with `-Werror`)

The manager's pinned validation order's step 3 ("clang-compile all 11
fixtures — the real independent oracle") found a genuine defect distinct
from the one the plan row's probe named: the frameless branch kept the
original `if (run->resume_depth == 0) return -1;` guard with no covering
`else`, then closed the function. Syntactically this is a possible
fall-through even though `resume_depth` is provably always 0 there, and
**both compilers reject it** — clang: "non-void function does not return a
value in all control paths"; gcc: "control reaches end of non-void
function" (verified directly, not assumed). `run_codegen_tests.sh` never
saw this because rule 1 only greps the emitted `.c`, it never gcc-compiles
these fixtures. Fixed by making the return unconditional in that branch —
the honest text the proof already licenses, not a conditional dressed as
always-true — and skipping the step-budget decrement in the same branch
since it would now be unreachable dead code after the unconditional return.
Commit `c13fd7b`.

### Bug 4 — `-Wunused-but-set-variable` on the revdet iteration counter (found by CLANGGEN=1's first real run)

Running `CLANGGEN=1` against `tests/named_groups` (step 6 of the pinned
order) immediately found a THIRD, previously undiscovered incompatibility,
unrelated to the resume-dispatch mechanism entirely: the reverse-
deterministic rung's per-loop `iteration` counter is read only when
`a->u.rep.rmax >= 0` (the scan-head bound test) or `a->u.rep.rmin > 0` (the
commit/short-label tests) — so a bare unbounded `X*` (rmin 0, rmax -1, e.g.
`((?<a1>a)|(?<b1>b))*`) writes it (reset, incremented every iteration) and
never reads it at all. gcc's `-Wall` does not flag a write-only local
reached only through `x++` under `-Wunused-but-set-variable`; clang's does
— verified directly on the exact pattern (gcc accepts, clang rejects, both
at `-O1 -Wall -Wextra -Werror`). The fix follows the file's own existing
precedent one line above: `cursor`/`prev_position`/`groups_seen` are
already `(void)`-cast because they too are "used only by shapes that do not
always occur," with the comment explicitly (and, it turns out, wrongly)
claiming `iteration` is used by every shape. Added it to the same list,
corrected the comment. Commit `ec6f481`.

## Step 2 — `CLANGGEN=1` opt-in clang-compilee sweep

Wired into the same four scripts `LINTGEN` rides (`tests/harness/run.sh`,
`tests/cli/run_cli_tests.sh`, `tests/codegen/run_codegen_tests.sh`,
`tests/registry/run_pc4.sh`) plus `tests/codegen/run_ir_listing.sh`, and
into the Makefile (`CLANGGEN ?= 0`, `export CLANGGEN`). Each script resolves
its own `CC` as:

```sh
CC="${CC:-}"
if [ -z "$CC" ]; then
    if [ "${CLANGGEN:-0}" = "1" ]; then CC="clang"; else CC="gcc"; fi
fi
```

An explicit `CC=` always wins. `make test CLANGGEN=1` never touches `build/`
(pcrec itself stays gcc-built, D2); unset, every script computes `CC=gcc`
byte-for-byte as before. Documented in `docs/testing.md`'s "Sanitizer + lint
battery" section and in `tests/CLAUDE.md` / `tests/codegen/CLAUDE.md`.

**One known, deliberate interaction, documented rather than special-cased
around:** `run_codegen_tests.sh`'s K24 partial-inlining check asserts that
gcc's own partial-inlining pass clones a stripped-attribute function — no
clang analogue, since clang performs no such pass. That check reads
differently (not wrongly) under `CLANGGEN=1`; not made compiler-agnostic
(out of this row's scope).

## Validation performed (all of it — box lifted, ran to completion)

In the order actually run, per the manager's pinned shape:

1. **`bash tests/codegen/run_codegen_tests.sh`** — 106/106, including all 11
   rule-1 rows exactly as the table predicts and rule 2's three-direction
   check clean. (First run found bug 2 above; fixed, re-ran clean.)
2. **Independent grep of the actual emitted artifacts** (bypassing the
   check's own pass/fail line): for each of the 11 fixtures, compiled with
   the patched `build/pcrec` and grepped `goto \*run->resume_stack` directly
   — all 11 match the table exactly, confirmed by a script with no
   dependency on `run_codegen_tests.sh`'s own logic.
3. **clang-compiled all 11 fixtures** at `-O1 -Wall -Wextra -Werror` (this
   project's default GENCFLAGS) — found and fixed bug 3; all 11 plus the
   original probed witness (`[a-z]{0,4096}` `--engine=vm`) now compile clean
   under both gcc and clang.
4. **gcc answer-identity spot-checks**: `(a)b`, `(a)(?1)` (2 moved rows) and
   `a(?R)?b` (1 unmoved row), each built with the UNPATCHED main-tree
   `build/pcrec` and the patched worktree `build/pcrec`, both via
   `--emit-main`, run on 8 subjects each (24 cells) — 24/24 agree exactly.
5. **`make test-codegen`** (PROCS=4, async, backgrounded with
   setsid+PID-file since >2 min) — 5/5 scripts, 0 failures
   (`run_codegen_tests.sh`, `run_dfa_stamps.sh`, `run_offset_skip.sh`,
   `run_size_term.sh`, `run_trie_identity.sh`). **`make strict`** — clean.
   Both re-run after bug 4's fix; still clean.
6. **`CLANGGEN=1` sections** — `tests/named_groups` (found bug 4; 128/4 →
   132/132 after the fix), then expanded for confidence to
   `tests/recursion` (1690/1690) and `tests/base` (3603/3603) — 5,425 case
   assertions total, 0 failures, 0 new findings beyond bug 4.
7. **`bash tests/codegen/run_recursion_identity.sh`** — run FIVE times, once
   per re-pin, each a full four-axis (default/vm/noprefilter/nocaptures)
   sweep over the whole corpus (2,825 patterns), backgrounded
   (setsid+PID-file, 200-450s each). Final run at the final pin `ec6f481`:
   **16/16 pass**, comparison (A) byte-identical against the unchanged
   pre-module pin `ac4917d` on all four axes (confirming the "everything
   sits outside prog_region" claim directly, not just structurally), (B)
   byte-identical against `ec6f481` on all four axes, zero refusal
   mismatches throughout.
8. **`make CC=clang` compiler-itself survey** — built with
   `BUILD_DIR=build-clang-survey` (a separate tree, matching the
   `ubsan`/`asan` precedent, so `build/`'s gcc build was never touched);
   pcrec's own sources (`src/`, `cli/main.c`) compile with **zero errors,
   zero warnings** under clang 21.1.8 at `-Wall -Wextra`; the resulting
   binary runs and compiles a pattern correctly. Scratch directory removed
   after recording the finding — not wired into any target, per D2 (gcc
   stays the target compiler).

`build/pcrec` is gcc-built and intact throughout; confirmed working after
the survey.

## Branch

`lane/cc`, 18 commits on top of `14f7c44` (`git log lane/cc` for the exact
list). Not merged, not pushed. In order:

1. `9f6e621` — lane start / hold ack.
2. `c657ae9` — step 1: clang compatibility, abi 13→14.
3. `25fc4ab` — re-pin #1 (FILEPIN → `c657ae9`).
4. `3083c94` — step 2: `CLANGGEN=1` mechanism.
5. `4ee1304` — CLAUDE.md pointers for `CLANGGEN=1`.
6. `8e0b624` — rule-1 relation/table fix (`has_push`-conditional leading
   term); re-derived during self-review, pre-lift.
7. `6d92d3b` — re-pin #2 (FILEPIN → `8e0b624`), corrected comparison (A)
   reasoning to the structural argument.
8-11. `7694103`, `11a20e6`, `0d1eec7`, `94a9c6b` — report writes and the
   probe-window verification tables (pre-lift).
12. `d734550` — pinned the manager's validation order into the report;
    named the check-design flaw in the probe-window verification.
13. `353306a` — **bug 2 fix**: `RX_CALL` comment leak.
14. `55adf44` — re-pin #3 (FILEPIN → `353306a`).
15. `c13fd7b` — **bug 3 fix**: `-Wreturn-type` fall-through, unconditional
    return.
16. `9e1c6dd` — re-pin #4 (FILEPIN → `c13fd7b`).
17. `ec6f481` — **bug 4 fix**: revdet `iteration` `(void)`-cast.
18. `484613c` — re-pin #5, final (FILEPIN → `ec6f481`).

This report's own final update (recording the DELIVERED status) is a 19th
commit landing right after this one.

## Files touched

- `src/gen/emit_dfa.c` — `__has_attribute` noclone guard; abi 13→14 comment
  and bump.
- `src/gen/emit_vm.c` — `has_push` gate; conditional fail-label dispatch,
  comment, and return statement; the revdet `(void)`-cast fix; file-header
  note on the exception to "exactly one indirect jump."
- `docs/spec/match_api.md` — abi 13→14 narrated paragraph, "abi is 14"
  sentence.
- `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=14`; `CLANGGEN`
  resolution + K24 interaction note; `[DD-14-RECURSION rule 1]`'s relation
  and eleven-row fixture table.
- `tests/codegen/run_recursion_identity.sh` — FILEPIN → `ec6f481` (five
  re-pins, each documented); comparison (A) structural-unaffected reasoning.
- `tests/codegen/run_ir_listing.sh`, `tests/cli/run_cli_tests.sh`,
  `tests/registry/run_pc4.sh`, `tests/harness/run.sh` — `CLANGGEN`
  resolution.
- `Makefile` — `CLANGGEN ?= 0` / `export CLANGGEN`.
- `docs/testing.md` — new CLANGGEN subsection.
- `tests/CLAUDE.md`, `tests/codegen/CLAUDE.md` — env-var pointers, rule-1
  addendum.

## Open items for the manager

- The two pre-existing drifts noted under step 1 (S168's stale doc figure,
  S166 mislabeled as rule 1's sabotage) — not this row's to fix, flagged for
  whoever next touches that area.
- STEP 3 (the bench's partial cc axis) is explicitly behind Frank's perf
  hold and out of this lane's scope.
- The full `CLANGGEN` sweep over the whole corpus stays with the manager,
  per their instruction — this lane validated 5,425 case assertions across
  three directories (named_groups, recursion, base) with 0 remaining
  failures, which is a reasonable prior that the mechanism is sound, but not
  a substitute for the full sweep.
- Journal/plan-row note owed at merge, restated from above: the frameless
  population `has_push` covers is bigger than the plan row's own counter-
  rung witness names (a bare `(a)b` and any fully-spliced call chain are
  frameless too).
