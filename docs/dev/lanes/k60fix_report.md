# k60fix_report.md — K60's LADDER class, TAKE THE FIX (2026-09-18, lane k60fix)

Frank's ruling 2026-09-18 on `docs/dev/known_issues.md` K60: the LADDER
class (mechanism (B), 108/148 measured absorptions, `docs/dev/
k60_measurement.md` §2/§4) gets disposition (2) — carry the OOM in a
value the recovery point tests FIRST, ahead of every rung's own
eligibility test and the `[ART-SIZE]` ladder's own blanket "this K is
out" catch. Built per the memo's §4.4 standards-clean spelling: the bare
`if (setjmp(cx.jb))` is kept (C11 7.13.1.1p2 forbids `v = setjmp(...)`);
`ctx_nomem` sets a new `Ctx` field, `cx.failed_nomem`, before its
`longjmp`, and the handler tests that field first.

## What was built

- `src/core/internal.h` — `Ctx` gains `bool failed_nomem`, right before
  `jmp_buf jb`, with a comment stating the per-arrival-by-construction
  argument (the loop-local `memset` at `compile.c:704-706` is what makes
  this true, exactly as it already is for `size_cap_refused`/
  `dfa_overflowed`).
- `src/core/compile.c` — `ctx_nomem` sets `cx->failed_nomem = true`
  before calling `ctx_fail` (comment-only change to `ctx_fail` itself:
  none). `compile_driver`'s `setjmp` handler tests `cx.failed_nomem`
  FIRST, before the `ST_LADDER` branch and before every later rung's
  eligibility test (`retry_collapse`/`retry_drop`, the OPT-4 size rung,
  the K53-SELRETRY drop rung, the K59-PREMUL rung) — confirmed by
  reading the whole handler top to bottom (`src/core/compile.c:838-1130`)
  that no eligibility test runs before this check and no rung is skipped
  by placing it here. The `[ART-SIZE]` ladder's own catch-all comment is
  updated to state the exemption and why.
- Docs: `docs/dev/known_issues.md` K60 (status line + a `LANE K60FIX`
  note), `docs/dev/decisions.md` D109 (the landed spelling and why
  disposition (1) is struck rather than deferred), `docs/spec/
  match_api.md` §8.1 (D80 hunk — the caller-observable change: a compile
  that previously returned 0 under a non-final OOM now refuses with a
  diagnosed `-1`), `tests/core/alloc_check.c` + `tests/core/CLAUDE.md`
  (the "re-pin": see below, there is no numeric assertion to move).

No `abi` event: nothing about the emitted artifact changed. No sabotage
row added (see "What was NOT built", below).

## The :1890 answer — the other four `setjmp` sites, verified not assumed

The brief asked me to verify, not assume, the memo's claim that the
other four sites are untouched. Read all four:

- `pcrec_count_groups` (`src/core/compile.c:1890`): `if (setjmp(cx.jb))
  { job_cleanup(&cx); return -1; }` — ONE unconditional action on any
  nonzero return, no rung, no ladder, no per-attempt eligibility test.
  Reads no `Ctx` field at all in the handler. `failed_nomem` would be a
  no-op here: the function already does on any `ctx_nomem` arrival
  exactly what my fix makes the OTHER site do.
- `src/parse/syntax_dump.c:778` (`doorway_call`'s probe Ctx): `if
  (setjmp(cx.jb)) { arena_free(&cx.arena); ... }` then returns — same
  shape.
- `src/parse/syntax_dump.c:1056` (`pcrec_probe_ask`'s Ctx): same shape,
  `arena_free` + return.
- `src/parse/syntax_dump.c:1565` (`pcrec_explain`'s Ctx): same shape,
  frees both `StrBuf`s + the arena, "ABANDON THE WHOLE ANSWER" by the
  file's own comment — one action, no per-attempt state to consult.

**Answer: none of the other four needed the same test.** Each already
takes the one action a `ctx_nomem` arrival should get (abandon, clean
up, return a diagnosed failure) regardless of what value arrived, and
none of them has a retry ladder or an eligibility test that could
absorb an OOM into a success. `make strict` (below) is clean including
the `-Wclobbered` promotion, confirming nothing about crossing these
`setjmp`s changed in a way the compiler can see either.

## Measured before/after (`make alloc --both`)

Fixed tree (this branch, commit `e33bceda`):

| witness | K | single-shot before | single-shot after | sustained after |
|---|---:|---:|---:|---:|
| W1 (DFA) | 72 | 15 (20.8%) | **15 (20.8%), unchanged** | 5 (6.9%), unchanged |
| W2 (VM cursor rung) | 11 | 0 (0.0%) | 0 (0.0%), unchanged | 0 (0.0%), unchanged |
| W3 (unicode-props/utf8) | 328 | 25 (7.6%) | **25 (7.6%), unchanged** | 0 (0.0%), unchanged |
| W4 (size-term ladder) | 158 | **108 (68.4%)** | **0 (0.0%) — FIXED** | 0 (0.0%), unchanged |

W1 and W3 are entirely mechanism (A), `emit_state_legend`'s silent
degradation (`src/gen/emit_dfa.c:3615-3618,3660`) — never calls
`ctx_nomem`, never reaches this recovery point, structurally unfixable
from here. That is lane d105's territory (K60's other half). This
lane's own `checks passed: 5 / checks failed: 3` on `make alloc` is
**expected**, not a defect: the 3 failures are W1 (single-shot) + W1
(sustained) + W3 (single-shot), all mechanism (A).

### Control: the branch point (before this fix) reproduces the memo exactly

Built a scratch, non-git tree at `git archive 6c9dac09` (the branch
point, before this lane's `src/` commit) in the session scratchpad, ran
`make alloc --both` there:

```
FAIL: W3 (unicode-props/utf8): 25 of 328 forced allocations were SUCCEEDED THROUGH anyway -- first at N=160
FAIL: W4 (size-term ladder): 108 of 158 forced allocations were SUCCEEDED THROUGH anyway -- first at N=29
PASS: W2 (VM cursor rung) ...
PASS: W4 (size-term ladder) [sustained]: every one of 158 ... diagnosed
```

W4 single-shot is **108 of 158 (68.4%)**, exactly the measurement
memo's number, on the unmodified tree. This is the "revert reproduces
the red" control the brief asked for — a `src/` revert (checking out
`6c9dac09` in place of this lane's commit) puts W4 straight back to
FAIL with the identical count; no separate reverted-tree artifact was
kept, since the scratch checkout already IS that tree and its
`build-alloc/` was rebuilt fresh for this run.

## Re-pinning `alloc_check.c`'s expectations — there is no numeric pin

`alloc_check.c`'s `report()` is behavioral, not numeric: PASS iff a
witness's `bad_n == 0` over the swept range; the absorption counts and
the single-vs-sustained comparison table are printed as **data**, never
asserted (the file's own comment at the table: "printed as data rather
than asserted"). So there was nothing to move to make a W4 absorption
RED — that already happens by construction (the control above IS that
demonstration), and reverting this lane's two-file `src/` commit alone
already turns `make alloc`'s W4 line red again with no test-side edit
needed.

What WAS stale and is fixed in its own commit (`293756a8`, separate
from the `src/` commit `e33bceda` per BOILERPLATE, since lane d105 also
edits this file's own W1/W3 narrative): the header comment in
`alloc_check.c` and the matching prose in `tests/core/CLAUDE.md` both
described K60 as entirely open with W4 at 108/158 — now stale. Both
gain a dated `[K60FIX]` note stating which witness is now expected to
PASS (W4) and which are expected to KEEP FAILING until lane d105 lands
(W1/W3) — so a reader of a red `make alloc` on this tree does not
mistake the known, pre-existing legend-class reds for a regression in
this commit.

## Validation

- `make -j4 CC=gcc-16` — clean.
- `make strict CC=gcc-16` — `strict: whole tree compiles clean with
  -Werror -Wshadow` (includes `-Wclobbered`'s promotion; the new
  `failed_nomem` field and the unchanged `volatile` set raised nothing).
- `make alloc CC=gcc-16` — see the table above: `checks passed: 5,
  checks failed: 3` (W1 x2, W3 x1 — mechanism (A), expected, unowned by
  this lane). `make: *** [alloc] Error 1` is therefore the EXPECTED
  overall exit for `make alloc` on this branch until d105 lands; it is
  not evidence against this fix.
- `make test-codegen CC=gcc-16` — `run_group: 8/9 scripts passed`. The
  one red, `run_inline_capability.sh` ("nm could not read arm_a.o (no
  rx_search symbol)"), reproduces IDENTICALLY on the unmodified
  `6c9dac09` scratch control — pre-existing, unrelated (an `nm`/
  toolchain probe issue in a [CC-DIFF] capability check, nothing to do
  with K60 or `compile_driver`). `run_codegen_tests.sh` itself (script 1
  of 9, the byte-identity/abi gates) is clean: `checks passed: 109,
  checks failed: 0`, including the abi-26 `rx_info` sizing checks and
  every anchor-resolution check ([SABANCHOR], 266 rows).
- `bash tests/rxtsource/run_rxtsource_tests.sh` — `checks passed: 212,
  checks recorded: 1, checks failed: 0`; `211 files / 3938 blocks /
  28949 expectation lines`, matching the pre-existing census (no
  `.rxt`/format change in this lane).
- `bash tests/core/run_core_tests.sh` — `checks passed: 1, checks
  failed: 0` (`sat_arith_check`: 7/7 sub-checks green — unaffected by
  this lane, run per the brief's target list).

## What was NOT built, and why

- **No mech sabotage row.** The brief named S259 as available (highest
  on `main` is S258) if I added one, but validating a sabotage row needs
  at least a single-row `make mech` rebuild, which the brief's own
  validation list excludes (light targets only; ONE heavy suite at a
  time, and lane d105 is running the heavy full-corpus emit-diff on this
  box concurrently). The `make alloc` before/after pair above (control:
  108/158 FAIL at the branch point; 0/158 PASS at this commit) is a
  stronger, already-run, reproducible positive/negative control for
  exactly this fix than a mech row would add, and is the evidence this
  report stands on instead.
- **`make test`** — explicitly out of scope per BOILERPLATE's
  one-heavy-suite rule (lane d105's full-corpus run). Owed to the
  manager's merge battery.

## Rulings received

None mid-flight; the brief's own text already carried Frank's 2026-09-18
ruling and the manager's k60meas-derived instructions in full.

## Handback

See the `SendMessage` to `main` for the numbers inline. Branch
`lane/k60fix`, not merged. Commits, in order: `e33bceda` (src fix),
`ddfabeec` (known_issues.md/decisions.md), `abe293c7` (docs/spec),
`293756a8` (tests/core expectations), this report.
