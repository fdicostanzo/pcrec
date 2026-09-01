# Lane cc — [CC-CLANG] steps 1+2 report

hold acked: no builds/compiles until cc.lift

STATUS at last update: code-complete for steps 1 and 2, reasoned and
statically reviewed against the corpus's existing structural checks; **no
compile, no test run, no probe has executed yet** — the box hold
(`worktrees/cc.lift` absent) was in force for this lane's entire session, so
every number below is a *derivation*, not a *measurement*. Everything under
"Owed validation" must run before this lane can be called done.

## Branch

`lane/cc`, six commits on top of `14f7c44`:

1. `9f6e621` — lane start / hold ack.
2. `c657ae9` — step 1: clang compatibility, abi 13→14 (the `__has_attribute`
   noclone guard + the frameless resume-dispatch omission).
3. `25fc4ab` — re-pin `run_recursion_identity.sh`'s FILEPIN to `c657ae9`.
4. `3083c94` — step 2: `CLANGGEN=1` opt-in clang-compilee sweep mechanism.
5. `4ee1304` — per-directory CLAUDE.md pointers for `CLANGGEN=1`.
6. `8e0b624` — **downstream fix found during self-review**: the
   `[DD-14-RECURSION rule 1]` `goto *`-count check baked in "the fail label's
   dispatch is always present," which step 1 makes conditional. Fixed the
   check's own relation and its eleven-row fixture table (7 of 11 rows
   move 1→0), and made the *emitted* fail-label comment ("THE ONLY
   BACKTRACKER AND THE ONLY INDIRECT JUMP") conditional too, since that
   claim is literally false on a frameless artifact.
7. `6d92d3b` — re-pin FILEPIN again to `8e0b624` (commit 6 moved further src
   bytes in the same abi bump) and correct the accompanying comment: (A) is
   untouched for a *structural* reason (the fail label sits entirely outside
   `prog_region`'s awk range), not because of anything about the call-free
   population specifically.

## Step 1 — clang compatibility (abi 13→14)

**The `noclone` fix.** `src/gen/emit_dfa.c`'s `emit_search_head` now wraps
`__attribute__((noclone))` in a general `__has_attribute` feature-detection
guard (the `#ifndef __has_attribute` / `#define __has_attribute(x) 0`
fallback idiom), rather than naming clang. gcc keeps emitting the attribute
(it has `__has_attribute`, and `__has_attribute(noclone)` is true there);
clang's `__has_attribute(noclone)` reads false, so the line is compiled out
entirely instead of triggering an unknown-attribute warning.

**The frameless-dispatch fix.** `src/gen/emit_vm.c`'s fail label used to
unconditionally end with the pop-and-resume block (`goto
*run->resume_stack[frame_index].resume_label;`). A program with no `RX_PUSH`
site and no `RX_CALL` site anywhere in its tree can never make
`run->resume_depth` leave 0, so that block is unreachable there — and its
`goto *` is the only place in such a program that would take a computed
address at all, which is exactly what clang refuses ("indirect goto in
function with no address-of-label expressions") and gcc accepts.

The gate is `has_push = v.npush > 0 || v.has_linked_calls`, computed once,
early (right after `has_budget`, before `vm_count_slots`'s results are
consumed anywhere else) so it can be read at the fail-label emission site far
below. **Both terms are load-bearing**: `v.npush` (the pre-pass's own count of
emitted `RX_PUSH` sites) deliberately does *not* count a linked call site's
own frame — `vm_count_slots`'s `A_CALL` arm says so explicitly ("the call
site itself allocates nothing... not one of them allocates a slot") — but
`RX_CALL` still increments `resume_depth` at run time. Relying on `npush`
alone would have left a call-only, alternation-free program (a single linked
`(?1)` to a recursive group, say) with a live push at run time but no
dispatch to service it — a real miscompile, not merely a missed
optimization. I could not find this by inspection alone; it came from
tracing `vm_count_slots`'s `A_CALL` arm and `RX_CALL`'s own macro body
side by side.

Both the guard condition and the omitted block are documented at length in
`emit_vm.c`'s own comments (the file's header, right after the file's
"exactly ONE indirect jump" claim, and at the `has_push`/fail-label sites
themselves) — read those before touching this again.

**abi 13→14**, all four D76 sites touched: `emit_dfa.c`'s `.abi = 14,`;
`run_codegen_tests.sh`'s `[DD-14.FB]` `ABI_EXPECT=14` (plus its narrative
line); `docs/spec/match_api.md` §6's "abi is N" sentence and a new "abi 13→14"
narrated paragraph; `run_recursion_identity.sh`'s FILEPIN, now `8e0b624`
(comparison (A) is unaffected — see below).

**Comparison (A) reasoning (important, re-derived twice in this lane
because the first pass was sloppy about it):** `prog_region`'s own awk range
is `/^    goto rx_L0;$/,/^rx_accept:/` — inclusive up to and including the
accept label. The fail label, its comment, and the now-conditional dispatch
all sit *after* `rx_accept:` in the emitted text, so they are outside
`prog_region` on *every* artifact, frameless or not, call-bearing or not.
Comparison (A) is therefore structurally untouched by this whole step, not
merely untouched on the corpus it happens to sweep.

### A downstream break I found and fixed, not one I was told about

`tests/codegen/run_codegen_tests.sh`'s `[DD-14-RECURSION rule 1]` block
asserts an exact `goto *` count per fixture pattern, and its relation was
written as `1 (fail label, always) + shared callee bodies`. That "always" is
exactly the invariant step 1 breaks. Working through `vm_count_slots`'s
`A_CAP`/`A_CAT`/`A_ALT`/`A_REP`/`A_CALL` arms and the splice/link
eligibility rule (a non-cyclic call target splices; a splice site emits no
`RX_PUSH` and no `RX_CALL`), I found that **a bare `(a)b`, and any pattern
where every call splices to a body with no internal choice point of its
own, is *also* frameless** — not just the counter-rung-repeat shape the plan
row's own probe named. Of the fixture's eleven rows, seven have `want=1`
today and are genuinely push-free; the other four all carry a
*self-recursive* call (forcing linkage, since a cycle cannot splice) wrapped
in an internal `?` quantifier, which pushes on its own account independent
of the call — so those four are unmoved.

I updated the relation to `(has_push ? 1 : 0) + shared callee bodies`, moved
those seven rows' `want` from 1 to 0, and updated the surrounding prose (in
both `run_codegen_tests.sh` and `tests/codegen/CLAUDE.md`). **This is
reasoned from source, not measured** — I have not compiled a single one of
these eleven patterns. It is the single highest-value thing to re-verify
once `cc.lift` lands, because if my reasoning about splice eligibility is
wrong anywhere, this is where it will show.

Two adjacent, pre-existing inconsistencies I noticed but did **not** touch
(out of scope, flagged for whoever owns them next): `S168`'s own
`SAB_DOC_FIGURE` text still narrates pre-wave-G `goto *` counts for
`(a)(b)(c)(?1)(?2)(?3)` (a drift from before splice existed, unrelated to
this change); and `run_codegen_tests.sh`'s own rule-1 comment cites "sabotage
row S166" for rule 1, but `S166_callgraph_binds_early.sh` is actually rule
3's sabotage (`u.call.body` pass-ordering), not rule 1's.

## Step 2 — `CLANGGEN=1` opt-in clang-compilee sweep

Wired into the same four scripts `LINTGEN` rides (`tests/harness/run.sh`,
`tests/cli/run_cli_tests.sh`, `tests/codegen/run_codegen_tests.sh`,
`tests/registry/run_pc4.sh`) plus `tests/codegen/run_ir_listing.sh`, and
into the Makefile (`CLANGGEN ?= 0`, `export CLANGGEN`). Each script now
resolves its own `CC` as:

```sh
CC="${CC:-}"
if [ -z "$CC" ]; then
    if [ "${CLANGGEN:-0}" = "1" ]; then CC="clang"; else CC="gcc"; fi
fi
```

An explicit `CC=` always wins — the one precedence rule `LINTGEN` never
needed, since it only ever appends to `GENCFLAGS`. `make test CLANGGEN=1`
never touches `build/` (pcrec itself stays gcc-built, D2); unset, every
script computes `CC=gcc` exactly as before, byte-for-byte.

**One known, deliberate interaction, documented rather than special-cased
around:** `run_codegen_tests.sh`'s K24 partial-inlining check
(`gen_cc "K24 noclone control" ...`) asserts that gcc's own partial-inlining
pass clones a stripped-attribute function — a claim with no clang analogue,
since clang performs no such pass. That one check is *expected* to read
differently under `CLANGGEN=1`, and I did not attempt to make it
compiler-agnostic (out of this row's scope, and D18 says don't gold-plate
ahead of a measured need).

Documented in `docs/testing.md`'s "Sanitizer + lint battery" section (new
"CLANGGEN" subsection immediately after LINTGEN's), and in `tests/CLAUDE.md`
/ `tests/codegen/CLAUDE.md`.

## The `make CC=clang` compiler-itself survey

**Not run.** This needs the box lift and is explicitly scheduled *after* it,
async, not alongside other heavy work, per the brief. No findings to report
yet.

## Owed validation (all blocked on `cc.lift`)

In the order I'd run them:

1. **The four originally-probed shapes**, re-confirmed against the *fixed*
   compiler: `[a-z]{0,4096}` `--engine=vm` compiles clean under clang (the
   original failing shape); the DFA/memchr, backtracking-VM `(a|ab)+c`, and
   recursion artifacts still agree gcc-vs-clang cell-for-cell.
2. **`bash tests/codegen/run_codegen_tests.sh`** — the big one. This is
   where the `[DD-14-RECURSION rule 1]` fixture-table rewrite either holds or
   doesn't; if any of the seven "moved to 0" rows actually still emits a
   `goto *`, my splice-eligibility reasoning for that specific pattern was
   wrong and needs re-deriving from a real `--emit-ir` dump rather than from
   the source alone.
3. **`make test-codegen`** more broadly, and **`make strict`** (PROCS=4,
   async, per the brief).
4. **Frameless artifacts under gcc stay answer-identical** — spot-check a
   few (`[a-z]{0,4096}` `--engine=vm`, `(a)b` `--engine=vm`, `(a)(?1)`
   `--engine=vm`) against their pre-change answers over a handful of
   subjects, since the whole claim of this row is "the omitted dispatch was
   already unreachable," and that claim deserves a direct check, not just a
   structural one.
5. **A small `CLANGGEN=1` section** (not the full sweep — the manager
   schedules that) to confirm the mechanism itself works end to end. Given
   the K24 interaction above, I'd pick a plain corpus section (e.g. a single
   `.rxt` directory through `tests/harness/run.sh`) rather than
   `test-codegen` for this first small-scale check, to keep the result
   legible; `test-codegen` is still worth running separately once its rule-1
   table is confirmed correct under gcc.
6. **`make CC=clang`** compiler-itself survey, once, async, not alongside
   other heavy work — findings to be appended to this report, not wired into
   any target.

## Files touched

- `src/gen/emit_dfa.c` — `__has_attribute` noclone guard; abi 13→14 comment
  and bump.
- `src/gen/emit_vm.c` — `has_push` gate; conditional fail-label dispatch and
  its emitted comment; file-header note on the one exception to "exactly one
  indirect jump."
- `docs/spec/match_api.md` — abi 13→14 narrated paragraph, "abi is 14"
  sentence.
- `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=14`; `CLANGGEN`
  resolution + K24 interaction note; `[DD-14-RECURSION rule 1]`'s relation
  and eleven-row fixture table.
- `tests/codegen/run_recursion_identity.sh` — FILEPIN → `8e0b624`; comparison
  (A) structural-unaffected reasoning, twice revised.
- `tests/codegen/run_ir_listing.sh`, `tests/cli/run_cli_tests.sh`,
  `tests/registry/run_pc4.sh`, `tests/harness/run.sh` — `CLANGGEN` resolution.
- `Makefile` — `CLANGGEN ?= 0` / `export CLANGGEN`.
- `docs/testing.md` — new CLANGGEN subsection.
- `tests/CLAUDE.md`, `tests/codegen/CLAUDE.md` — env-var pointers, RULE 1
  addendum.

## Open items for the manager

- Everything in "Owed validation" above — none of it has run.
- The two pre-existing drifts noted under step 1 (S168's stale doc figure,
  S166 mislabeled as rule 1's sabotage) — not this row's to fix, flagged for
  whoever next touches that area.
- STEP 3 (the bench's partial cc axis) is explicitly behind Frank's perf
  hold and out of this lane's scope.
