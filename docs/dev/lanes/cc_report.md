# Lane cc — [CC-CLANG] steps 1+2 report

hold acked: no builds/compiles until cc.lift

STATUS at last update: code-complete for steps 1 and 2. The box hold
(`worktrees/cc.lift` absent) is still in force for anything that COMPILES my
own changes, but the manager granted a time-boxed amendment (until 22:05 EDT,
2026-08-31) to run single-pattern probes against the MAIN tree's *existing*
`build/pcrec` binary — no make, no gcc/clang, no test scripts. I used that
window to directly verify the highest-risk piece of step 1 (the
`[DD-14-RECURSION rule 1]` fixture-table rewrite) against the live, unmodified
compiler; see "Verified during the probe window" below. Everything else —
actually compiling my changes and confirming the new behavior — is still
unmeasured and blocked on `cc.lift`.

## Verified during the probe window (2026-08-31, ~21:13-21:16 EDT, main tree's `build/pcrec`, pre-[CC-CLANG])

For every one of the eleven `[DD-14-RECURSION rule 1]` fixture patterns,
I compiled it with the CURRENT (pre-change) `build/pcrec --engine=vm
--features all -o -` and counted actual `RX_PUSH(`/`RX_CALL(` *invocations*
(as opposed to their macro definitions, which are emitted unconditionally
and always add exactly one matching line each). An invocation count of 0
beyond the definition line means `has_push` will read false under my step 1
patch, i.e. the row's `goto *` count should move from 1 to 0.

| pattern | current `goto *` | RX_PUSH invocations | RX_CALL invocations | predicted new count |
|---|---|---|---|---|
| `(a)b` | 1 | 0 | 0 | **0** |
| `(a)(?1)` | 1 | 0 | 0 | **0** |
| `(a)(?1)(?1)(?1)` | 1 | 0 | 0 | **0** |
| `(a)(b)(c)(?1)(?2)(?3)` | 1 | 0 | 0 | **0** |
| `a(?R)?b` | 2 | 2 | 2 | 2 (unmoved) |
| `(?(DEFINE)(a))(?1)b` | 1 | 0 | 0 | **0** |
| `(?(DEFINE)(a)(b)(c))(?1)(?2)(?3)` | 1 | 0 | 0 | **0** |
| `(?(DEFINE)(a))b` | 1 | 0 | 0 | **0** |
| `(?(DEFINE)(?<w>a(?&w)?b))(?&w)` | 2 | 1 | 2 | 2 (unmoved) |
| `(?(DEFINE)(?<p>a(?&p)?b)(?<q>x(?&q)?y))(?&p)(?&q)` | 3 | 2 | 4 | 3 (unmoved) |
| `(?(DEFINE)(?<p>a(?&p)?b)(?<r>z))(?&p)(?&r)` | 2 | 1 | 2 | 2 (unmoved) |

Every row matches my prediction exactly — the seven rows I'd reasoned would
move to 0 all have zero real push/call activity today, and the four unmoved
rows all have real activity (their self-recursive call forces linkage, plus
each one's internal `?` pushes on its own account).

**Then I found a stronger check and re-ran all eleven through it**:
`--emit-ir`'s `; resume pts N` line is a direct print of `v->npush` itself
(`src/gen/emit_vm.c:6927`, `sb_printf(o, "; resume pts   %lld\n",
v->npush);`) — not a grep proxy, the exact quantity `has_push`'s first term
reads. `bash -c '.../pcrec -p rx --features all --engine=vm --emit-ir --
"$p"' | grep "resume pts"` for all eleven gives `npush` = `0, 0, 0, 0, 2, 0,
0, 0, 1, 2, 1` in fixture order — identical in shape to the table above (zero
exactly where `RX_CALL` invocations were also zero, nonzero exactly on the
four self-recursive rows) and, combined with each row's `RX_CALL` invocation
count already confirming `has_linked_calls`, this is as close to a direct
confirmation of `has_push`'s value as is possible without compiling my own
patch. Still not a run of the *actual patched compiler* — that needs
`cc.lift` — but the fixture-table rewrite in commit `8e0b624` is now
verified against both terms of the gate individually, not merely reasoned
about.

Also confirmed while probing: the frameless witness `[a-z]{0,4096}
--engine=vm` has zero `&&rx_` address-of-label expressions anywhere in its
emitted text (confirming it is exactly the clang-breaking shape named in the
plan row) and carries no `noclone` line at all — it has no DFA hybrid
prefilter, so `emit_search_head` is never called for it, which is a
different, unrelated fact about this specific witness (not a defect in my
fix). A hybrid pattern (`(a+)b`) DOES carry `noclone` on its
`static int rx_prefilter`, confirming the guard's placement covers VM
hybrids as documented. And under `-fno-splice-calls`,
`(a)(b)(c)(?1)(?2)(?3)` forces linkage and reads `goto *: 4` with 3 real
`RX_CALL` invocations — matching the design's own "three distinct callees is
4" figure and confirming that axis is untouched by my fix (that axis isn't
part of the rule-1 test, which always uses the default/splice behavior).

## Branch

`lane/cc`, ten commits on top of `14f7c44` at last update (code/doc commits
1-7 below; 3 more are report-only updates recording the probe-window
verification, `11a20e6`/`7694103`/`0d1eec7` — read the report history via
`git log lane/cc` for the exact list, since this section is not kept
byte-current with every report-only commit):

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
8-10. `7694103`, `11a20e6`, `0d1eec7` — this report, written and then twice
   strengthened with the probe-window verification tables (see that section
   above).

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

## Owed validation (all blocked on `cc.lift`) — PINNED SHAPE (manager ruling, 2026-08-31)

**The check-design flaw in my own probe-window verification, named by the
manager and worth stating plainly rather than glossing over:** the rule-1
fixture table's `want` values and my `has_push` code are BOTH derived from
the same reading of `vm_count_slots`'s splice/link eligibility rules. A
check and the code it checks sharing one source of reasoning is this
project's own most-repeated check-design failure (`docs/dev/learnings.md`
§3, memory `pcrec-check-design-lessons`) — if my reading of the eligibility
rule is wrong in some way that is consistently wrong in both places, the
probe-window table proves nothing; it would just show two wrong numbers
agreeing. `--emit-ir`'s `v->npush` print is closer to a real check for the
CODE (it reads the compiler's own internal count independent of my
predicted "which patterns are push-free" reasoning) but nothing in the
probe window is independent of that reasoning for the FIXTURE TABLE's own
`want` values.

**So the validation order at lift is PINNED as follows, superseding my
earlier list**, run in order, with (2) and (3) restoring genuine
independence:

1. `bash tests/codegen/run_codegen_tests.sh` as planned — the check against
   itself, first, cheap.
2. **Independent of the check's own PASS/FAIL line**: for each of the 11
   fixtures, grep the actual emitted artifact for the dispatch text
   (`goto \*run->resume_stack`) and tabulate presence/absence row by row
   against the report table above — the emitted text is the fact, the
   check's exit code is not. If a row disagrees with the check's own
   verdict, the check itself has a bug independent of `has_push`.
3. **clang-compile all 11 fixtures.** This is the real independent oracle:
   clang has no idea what `has_push` is or what my table predicts — it only
   knows whether an indirect goto has an address-of-label expression in
   scope. Any artifact I classified as push-free that is actually NOT will
   fail clang loudly, in exactly the shape that motivated this whole row.
   This is the check that actually discharges the risk the manager named.
4. **gcc answer-identity spot-checks**: at least 2 of the 7 "moved" rows and
   1 of the 4 "unmoved" rows, confirming the omitted dispatch changed no
   answer (the structural claim "it was already unreachable" made
   behavioural).
5. `make test-codegen` more broadly, and `make strict` (PROCS=4, async).
6. A small `CLANGGEN=1` section (not the full sweep — the manager schedules
   that). Given the K24 interaction noted above, a plain corpus section
   (e.g. one `.rxt` directory through `tests/harness/run.sh`) rather than
   `test-codegen`, to keep the first result legible.
7. `make CC=clang` compiler-itself survey, once, async, not alongside other
   heavy work — findings appended to this report, not wired into any target.

## For the journal / plan row at merge (manager's instruction)

**The frameless population is bigger than [CC-CLANG]'s own charter names.**
The plan row's probe named ONE witness — a counter-rung bounded repeat
(`[a-z]{0,4096}` `--engine=vm`) — as the frameless shape needing the fix.
Working the change through, the actual population is broader: ANY VM
program with no `RX_PUSH` site and no `RX_CALL` site is frameless, which
includes a bare capturing concatenation with no alternation/quantifier/
lookaround/call at all (`(a)b`), and any pattern where every subroutine call
splices to a callee with no internal choice point of its own (`(a)(?1)`,
`(a)(b)(c)(?1)(?2)(?3)`, an unused or singly-called `(?(DEFINE)...)`).
This is a real fact about the shape of the fix, not a scope creep — the
`has_push` gate is the general, correct condition and the plan row's own
counter-rung witness is one instance of it, not the whole of it.

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
