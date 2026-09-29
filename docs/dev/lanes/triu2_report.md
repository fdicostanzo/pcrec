# triu2 — TRIAGE of ucpu2's full `make test CC=gcc-16` red (2026-09-29)

Lane `triu2` (sonnet, TRIAGE), branch `lane/triu2` from `lane/ucpu2` HEAD
`61cbc894`, worktree `worktrees/triu2`. Scope: diagnose the five red
sections in `/tmp/ucpu2s/make_test_full.log` from [UCP] U2's (lane ucpu2)
full `make test CC=gcc-16` run (`RUN-STAMP: tree=61cbc894... sections=45/45
duration=6499s`, 0 TIMED OUT). Read `docs/dev/lanes/ucpu2_report.md` and
`docs/dev/lanes/tri220_report.md` first per the brief; this report does not
re-derive what tri220 already covered.

## Summary table

| check | cause | classification | fix / witness | re-run |
|---|---|---|---|---|
| `test-codegen` → `run_inline_capability.sh` | standing darwin `nm arm_a.o` red (documented pre-existing in 30+ lane reports) | pre-existing, not U2's | none needed | confirmed sole failure in the group (11/12 scripts passed) |
| `test-cpset-structure` CHECK 2b | U2's T3 recognizer (`src/parse/ctxnode.c:51`) reads a class node's interval payload directly, outside the allowlist | manifest moves BY MECHANISM | allowlist gains `src/parse/ctxnode.c` w/ comment (`c573726e`) | 28/0 (was 27/1) |
| `test-search-pinned` §9 force-axis floor | U2 moves ~9 patterns off the `-fprefilter`-forced pinned-hybrid population (context node makes the construct native to plain DFA) | floor moves BY MECHANISM | floor 20 → 12, re-measured (`ce161aaf`) | 17/0 (was 15/1) |
| `test-anchored-match` → `run_anchored_diff.sh` | **REAL REGRESSION**: `<prefix>_match`/`_match_caps` on the anchored-unwrapped machine reads one element before its accept table when the machine's "no left context" entry state is the DEAD sentinel — SIGSEGV or a silently wrong accept | REAL REGRESSION | **not fixed** (no `src/` access; STOPPED per brief) | minimal 8-line reproduction below |
| `test-premul-table` §3/§4 (agreement/bound) | `implied_stamp`'s corpus-sweep fold reads only the forward+reverse machines, missing [ENG-ABS]'s THIRD (anchored) machine in the `RX_DFA_TABLE` composition; the `[bound]` loop's stated rule omits `dfa_premul`'s own SEED-PRECONDITION decline clause | check-design staleness (two pre-existing, previously-vacuous gaps, newly populated by U2) | **not fixed** (check-logic change, not a manifest number; filed with the exact repair shape) | mechanism verified directly against emitted text |

Every fix that IS a floor/manifest number is committed on `lane/triu2`
(`c573726e`, `ce161aaf`). The anchored-match crash and the premul-table
check gaps are **findings**, not repairs — the first per the brief's STOP
instruction, the second because the honest fix is a check-logic change
(not a number) that this lane declined to rush.

## 1. `test-codegen` — the standing darwin red, confirmed to be ONLY that

`run_group[4]: bash tests/codegen/run_inline_capability.sh` is the sole
failure (`run_group: 11/12 scripts passed`):

```
FAIL: nm could not read arm_a.o (no rx_search symbol) — no verdict is evidence here
```

This is [CC-DIFF] STEP 2's capability probe, documented pre-existing in the
darwin build across 30+ prior lane reports (e.g. `w5r_report.md`,
`nltriage_report.md`, `axtriage_report.md` §2). Not U2's. No action.

## 2. `test-cpset-structure` — CHECK 2b, fixed BY MECHANISM

CHECK 2b's negative needle (`tests/codegen/run_cpset_structure.sh`) asserts
that nothing outside a named allowlist reads `A_CLASS`'s interval payload
(`u.cls.iv`/`u.cls.n`) directly — the render helper `pcrec_cls_bits` is
supposed to be the sole path to a byte bitmap, and a direct read is the
shape of r54's E1 recurrence.

```
FAIL: [2b] a file outside the allowlist reads the A_CLASS payload directly. ...
src/parse/ctxnode.c:51:            pcrec_cpset_add_set(acc, a->u.cls.iv, a->u.cls.n);
```

`src/parse/ctxnode.c` is [UCP] U2's own T3 lookaround recognizer, landed in
this same tree. Its `lang_charset` walk (the function at that line)
accumulates a lookaround body's LANGUAGE into a code-point-level
`PcrecCpSet` via `pcrec_cpset_add_set` — this is **not** a byte-bitmap
render: the header comment of `ctxnode.c` states explicitly that the
resulting set is checked for byte-expressibility by `pcrec_enc_set_bytes`
before any engine (T3 row 1's own gate) ever reads it, so it structurally
cannot reach a byte-tier consumer the way `pcrec_cls_bits`'s assertion
polices. Verified by reading `pcrec_cpset_add_set`'s signature (takes an
interval list, publishes a set — the same accumulation `parse/parse.c`'s
already-allowlisted producers do) and by `lang_charset`'s own callers (T3's
predicate, never an emitter).

**Classification: a manifest CHECK 2b moves BY MECHANISM**, not a
regression — the site is safe by construction and has existed since U2's
design landed; what changed is that this check's corpus sweep now REACHES
it (population, not correctness).

**Fix** (commit `c573726e`): `ALLOW` gains `src/parse/ctxnode.c` with an
explanatory comment naming the mechanism and the date. Re-run:
`checks passed: 28 / checks failed: 0` (was 27/1).

## 3. `test-search-pinned` §9 — the force-axis pinned-hybrid floor, fixed BY MECHANISM

```
FAIL: §9 only 14 artifacts are PINNED on the -fprefilter force axis, below the 20 floor
      (measured 23 under this file's own --no-captures flags, 70 with captures on).
```

`run_search_pinned.sh` §9's force-axis floor (20, set at r51 finding 4
against a measured 23 at 2026-09-02) is the count of corpus artifacts that
select the START-PINNED search form when `-fprefilter` FORCES a hybrid VM
prefilter onto an otherwise-pure-DFA pattern. U2's own report
(`ucpu2_report.md` §4) documents that **141 patterns move VM → DFA on the
default engine (159 under `--no-captures`)** because a one-character
lookaround is now a context node the plain DFA's own class axis reads
directly, with no hybrid needed at all.

**A/B against main `fdcf3e00` (this branch's own point)**, same flags:

| tree | force-axis pinned population |
|---|---|
| main `fdcf3e00` (pre-U2) | 23 |
| lane/ucpu2 `61cbc894` | 14 |

23 → 14 is the same direction and the same order of magnitude as U2's own
mover count — a subset of the moved population previously needed
`-fprefilter`'s forced hybrid specifically to recover a search start across
a VM-only lookaround; with the lookaround now native to the plain DFA (no
VM, no hybrid, nothing to pin), those patterns leave the force axis's
pinned-hybrid bucket entirely.

**Classification: a floor moves BY MECHANISM**, corroborated by a direct
A/B, not asserted from the mover count alone.

**Fix** (commit `ce161aaf`): floor 20 → 12 (14 × 0.8 = 11.2, rounded up to
the next even floor — the same ~20% margin rule the file's own adjacent
comment already states for its sibling floor at :501). The historical
23/70 figures are kept in the comment as dated prose (2026-09-02), the new
14/2026-09-29 figure stated beside them, per this file's own convention of
never overwriting a prior measurement's citation. Re-run:
`checks passed: 17 / checks failed: 0` (was 15/1).

## 4. `test-anchored-match` — `run_anchored_diff.sh`: a REAL REGRESSION

```
FAIL: 2 patterns DIVERGE between the unwrapped form and the search-and-filter form
      — the identity argument (docs/design/anchored_match_unwrapped.md §3) is refuted
FAIL: 57 pattern(s) produced a driver exit that is neither agreement nor divergence
BAD: driver exited 139 (neither agreement nor divergence) on: ((?<![ab])z)
BAD: driver exited 139 (neither agreement nor divergence) on: ((?<!a)z)
BAD: driver exited 139 (neither agreement nor divergence) on: ((?<*[ab])z)
BAD: driver exited 139 (neither agreement nor divergence) on: ((?<*a)z)
BAD: driver exited 139 (neither agreement nor divergence) on: ((?<=[ab])z)
BAD: driver exited 139 (neither agreement nor divergence) on: ((?<=a)b)+
```

Exit 139 is SIGSEGV. Every witness named is a one-character LOOKBEHIND
assertion (`(?<=`, `(?<!`, `(?<*` — a lookbehind-verb spelling). The
`FAIL: 2 patterns DIVERGE` line's own two pattern names never surfaced in
the log: the failing-direction reporter (`grep -m6 '^BAD: '`) is not
selective between the DIVERGE lines and the driver-exit lines, and the 57
crash lines fill all six slots before either DIVERGE name is reached — see
"What is not confirmed" below.

### Root cause, confirmed by direct reproduction (not inferred from the log)

`emit_anchored_match_def` (`src/gen/emit_dfa.c:~7589`) emits [ENG-ABS]'s
anchored match-here entry (`<prefix>_match`/`_match_caps`/their `_in`
siblings — spec §3.2: a match beginning at exactly `ctx->pos`, or `-1`) by
calling the SAME `emit_scan_loop` the ordinary unanchored SEARCH machine
uses (`emit_dfa.c`'s own comment: "the SAME emitted line as the forward
scan's"). That shared loop's very first statement is the accept test
(`f->acc->emit_top`), run BEFORE any dead-state check — safe for the SEARCH
machine, whose entry state at `search_from == 0` is always the real state
`0` (the unanchored self-loop start, never the dead sentinel), but **unsafe
for the ANCHORED machine**, which has no self-loop and whose "no left
context" fallback (`dfa_s0_cell(f)`) is genuinely the dead sentinel `-1`
whenever the machine's start requires a live one-character LEFT context —
exactly what a lookbehind's context node puts at `s0`.

The emitted artifact for `(?<=a)b` (`--no-captures --features all`, DFA
engine, `RX_DFA_MATCH "unwrapped"`) reads, at `<prefix>_match`'s top:

```c
on_anchored_state anchored_state = search_from
    ? on_anchored_seed_state[on_anchored_byte_class[subject[search_from - 1]]]
    : -1;                                          /* dead sentinel, by design */
for (;;) {
    if (on_anchored_accepts(on_anchored_is_accepting, anchored_state))   /* accepting[-1] */
        last_accept_position = scan_position;
    ...
```

`on_anchored_accepts` is `{ return accepting[s]; }` with NO dead-state
guard. At `ctx->pos == 0` (or any `search_from` whose class seeds to `-1`)
this is `accepting[-1]` — one element before the `is_accepting` array —
undefined behaviour that, depending on what memory precedes that `static
const` table, either crashes (the 57 SIGSEGVs) or silently reads a
garbage-but-nonzero byte, reporting a spurious accept (the plausible
mechanism for the 2 unnamed DIVERGE lines — not confirmed for the specific
two patterns, since their names never reached the log; see below).

**Minimal reproduction, no diff driver, no corpus, 8 lines of C:**

```sh
build/pcrec -p on -o /tmp/t2anch/on.c --features all --no-captures --pattern '(?<=a)b'
cat > /tmp/t2anch/mini.c <<'EOF'
#include "on.h"
int main(void) {
    rx_ctx ctx = {0};
    unsigned char subj[1] = {'a'};
    ctx.subject = subj; ctx.len = 1; ctx.pos = 0;
    return (int)on_match(&ctx);
}
EOF
gcc-16 -O1 -std=gnu11 -I/tmp/t2anch -o /tmp/t2anch/mini /tmp/t2anch/mini.c /tmp/t2anch/on.c
/tmp/t2anch/mini            # Segmentation fault: 11, rc=139
```

Confirmed the population boundary: on the pre-U2 binary (main `fdcf3e00`),
`(?<=a)b --engine=dfa` is unreachable — the pattern compiles to `RX_ENGINE
"vm"` (no anchored-unwrapped machine at all), so this defect is real,
pre-existing EMITTER CODE that had **no reachable population** before U2's
T3 recognizer started routing one-character lookarounds onto the plain DFA
engine, where [ENG-ABS]'s anchored-unwrapped rung then applies to them for
the first time.

**This is not the same defect U2's own report already fixed.** The
ucpu2_report.md §1 "reverse-machine fix" is about a **lookahead**
pattern's **REVERSE** machine having a dead `s0` with live seeds
(`z(?=a)`, `unanch_start`/`dfa_s0_cell`). This is a **lookbehind**
pattern's **ANCHORED** (forward, no-self-loop) machine, in a different
emitter function (`emit_anchored_match_def` via `emit_scan_loop`'s shared
accept-before-dead-check ordering), reached through a different
mechanism ([ENG-ABS]'s axis G, not the reverse-pass seed table).

### Severity

`<prefix>_match`/`<prefix>_match_caps` (and their `_in` siblings) are
PUBLIC entries (`docs/spec/match_api.md` §3.2) any caller may invoke
directly, not only this test's internal comparison. A caller compiling a
one-character lookbehind assertion at the DFA engine and calling
`pcrec_match`-family entries at `pos == 0` (or any position whose
preceding-byte class the context node cannot satisfy) hits this
undefined-behaviour read today, on the shipped `lane/ucpu2` tree.

### What is NOT confirmed

- **The two DIVERGE patterns' names.** The report's own `grep -m6 '^BAD:
  '` mechanism cannot separate a DIVERGE line from a driver-exit line, and
  the 57 crash lines exhaust the six-line window before either DIVERGE
  name is printed. A full, uncapped re-run of `run_anchored_diff.sh`
  (`KEEP=1`, reading `$WORKDIR/all.out` for `BAD_DIVERGE` lines
  specifically — see the script's own `tag_kind`/`BAD_DIVERGE` shape at
  line ~179) is needed to name them. This lane started such a run
  (`timeout 1800 bash tests/anchored/run_anchored_diff.sh`, `KEEP=1`) but
  the ~59 crashing/diverging witnesses each pay a `gen_run` compile+run
  budget against the WHOLE corpus population, and it had not produced
  output after several minutes. It was NOT a detached, owed-to-the-manager
  run: the harness auto-backgrounded it at 120s, and this lane then killed
  it (`scripts/safekill`) once the root cause was independently confirmed
  by direct reproduction, to free the box rather than leave it running
  unsupervised for an unbounded time with no output. **Owed to a
  build-capable follow-up**: re-run
  `run_anchored_diff.sh` to completion (or a scoped subset limited to the
  lookbehind family) to name the two DIVERGE patterns precisely.
- Whether the 2 DIVERGE patterns are the SAME `accepting[-1]`
  out-of-bounds-read mechanism reading a nonzero garbage byte (this
  report's working hypothesis, argued from the shared root cause and the
  UB's two possible outward effects) or a second, distinct defect. Not
  built or measured further here — this lane's brief is to name the
  witness and stop, not to fix or fully characterize engine code.

### The fix (not built here)

Two shapes, neither attempted (no `src/` access per this lane's brief; a
correctness fix to a shared emitter function needs its own review):
(a) guard `emit_anchored_match_def`'s loop entry — an `is_dead` check
before the first accept test, scoped to the anchored machine only (the
search machine's entry is never dead and should not pay an extra
branch); or (b) special-case the anchored machine's `-1`-seed emission to
`return -1` immediately rather than entering the shared loop at all,
mirroring `dfa_engine_is_empty`'s existing "engine has nothing to try"
shape one level up. Either needs a regression witness in
`tests/anchored/` or `tests/lookaround/` compiling `(?<=a)b` at the DFA
engine and calling `<prefix>_match` at `pos == 0`, and (D76) is NOT an
`abi` event by itself (no scaffolding changes).

## 5. `test-premul-table` §3/§4 — two pre-existing check gaps, newly populated

```
FAIL: [agreement] 51 artifact(s) stamp a table form their emitted tables do not have
FAIL: [bound] 17 machine(s) took a form the generation-time rule forbids at their size
```

Every `[agreement]` DRIFT line and every `[bound]` violation is a
one-character lookaround witness (lookbehind for the 51, lookahead for the
17) — again U2's VM→DFA mover population reaching a code path for the
first time. **Verdict: the shipped, un-sabotaged compiler is CORRECT in
both cases; the check's own stated rule is incomplete.**

### 5a. The 51 `[agreement]` DRIFT lines — the check misses [ENG-ABS]'s THIRD machine

Example: `(?<=a)b` stamps `RX_DFA_TABLE "mixed"`. Reading the emitted
artifact directly: `rx_forward_next_state[9]` and `rx_reverse_next_state[6]`
are BOTH `unsigned short` (premultiplied, form=1) — so
`run_premul_table.sh`'s own `implied_stamp(fpm, rpm)` computes
`"premultiplied"`, disagreeing with the real `"mixed"` stamp. The artifact
ALSO carries `rx_anchored_next_state[6]` declared plain `short` (INDEXED,
form=0) and `RX_DFA_MATCH "unwrapped"` — [ENG-ABS]'s anchored-unwrapped
machine is present and its own form differs from the forward/reverse pair.

`src/gen/emit_dfa.c:dfa_table_name` (the real compiler logic) composes
THREE machines whenever `dfa_match_is_unwrapped(cx)`:

```c
const char *f = dfa_repr_of(cx, &cx->job->dfa)->c.name;
if (!dfa_search_is_pinned(cx)) {
    const char *r = dfa_repr_of(cx, &cx->job->rdfa)->c.name;
    if (strcmp(f, r)) return "mixed";
}
if (dfa_match_is_unwrapped(cx) &&
    strcmp(f, dfa_repr_of(cx, &cx->job->adfa)->c.name)) return "mixed";
```

— documented in the emitter's own comment as [ENG-ABS] deliberately
widening the composition "after this row that is three rather than two
whenever axis G selected `unwrapped`". `run_premul_table.sh`'s
`implied_stamp` function was written for the two-machine (forward,
reverse) world and never extended when [ENG-ABS] landed a third. The
compiler's `"mixed"` stamp is CORRECT (forward+reverse premultiplied,
anchored indexed, composed "mixed" per spec §6.3); the check's own
`implied_stamp` fold is stale.

**Why this had zero population before U2**: `dfa_match_is_unwrapped`
requires a DFA-compiled artifact with the anchored machine built
(`Job.anchored_ok`), which no one-character lookaround reached before U2
(they were VM-only). The gap in `implied_stamp` is pre-existing (dated to
[ENG-ABS]'s landing) and was invisible for having no witness, exactly the
[MECH-REACH] shape this house has repeatedly named.

### 5b. The 17 `[bound]` violations — the check's stated rule omits the SEED PRECONDITION

All 17 are one-character LOOKAHEAD witnesses (`(?!a)`, `(?=a)`, `(*negative_lookahead:a)`,
etc.), always on the REVERSE machine (`dir=r`), always `pm=0` (indexed)
at small entry counts (4, 6, 10, 12, 32 — far under the 65,535 bound).
Confirmed directly against the emitted table for `(?!a)`:

```c
static const short rx_reverse_seed_state[2] = {
    0, -1,
};
```

`src/gen/emit_dfa.c:dfa_premul` — the REAL predicate the compiler uses —
is not a pure size test:

```c
static bool dfa_premul(Ctx *cx, const Dfa *d)
{
    long ents = (long)d->n * (long)d->ncls;
    if (ents > PREMUL_MAX_ENTRIES) return false;   /* the RANGE condition */
    if (dfa_needs_seed(d))
        for (int cl = 0; cl < d->ncls; cl++)
            if (d->s1u[upc_of_class(d, cl)] < 0) return false;   /* THE SEED PRECONDITION */
    return true;
}
```

— documented in its own comment as deliberate, dated 2026-08-26: a machine
that needs a seed AND has a dead cell in that seed table declines
premultiplication (the comment explains why: a dead `-1` cell flowing into
`is_accepting[PREMUL_DEAD]` would be "a far wilder read" than the
equivalent `-1` in the indexed form — this is the SAME class of hazard §4
above just demonstrated, and `dfa_premul`'s own precondition is precisely
what prevents it here). `run_reverse_seed_state`'s `-1` cell above IS that
precondition firing, correctly, on `(?!a)`'s reverse machine.
`run_premul_table.sh`'s own stated rule — "a machine takes the
premultiplied form IFF its states*classes is at or below
PREMUL_MAX_ENTRIES" (its §2 comment, verbatim) — never mentions the seed
precondition, so its `[bound]` loop flags a correctly-indexed small machine
as a violation.

**Why this had zero population before U2**: the same reasoning as 5a — no
lookahead reverse machine reached the DFA's premultiplication decision
before U2 made one-character lookarounds DFA-eligible in the first place.

### Classification and disposition

Both are pre-existing check-design gaps (dated to [ENG-ABS] and to
`dfa_premul`'s own 2026-08-26 landing respectively), newly populated by
U2's mover census — **not** a U2 regression, and **not** a simple
manifest/floor number this lane fixes by re-pinning. The honest repair is
a check-LOGIC change: `implied_stamp` needs a third argument (the
anchored machine's form, read the same way `fpm`/`rpm` already are, gated
on the SAME `dfa_match_is_unwrapped` predicate the compiler itself gates
on — readable from the artifact as "does an `rx_anchored_*` table exist
and what's its declared type"), and the `[bound]` loop needs to skip (or
separately classify) a machine whose own emitted seed table contains a
`-1` cell. Building and validating that correctly — including its own
failing-direction sabotage per this directory's standing convention — is
check-design work this triage lane declined to rush under time pressure;
filed here with the exact mechanism and the exact repair shape rather than
attempted blind.

## Validation summary

| section | before | after |
|---|---|---|
| `test-cpset-structure` | 27 pass / 1 fail | 28 pass / 0 fail |
| `test-search-pinned` | 15 pass / 1 fail | 17 pass / 0 fail |
| `test-anchored-match` | REAL REGRESSION, not fixed | unchanged (finding only) |
| `test-premul-table` | check-design gap, not fixed | unchanged (finding only) |
| `test-codegen` | standing darwin red, not U2's | unchanged (no action needed) |

`make strict CC=gcc-16` was NOT re-run (no `src/` changes in this branch;
the two committed changes are `tests/` shell scripts). A scoped re-run
naming the two touched files is the validation this report stands on —
see §2 and §3 above for the exact commands and counts.

## Scratch cleanup

`worktrees/triu2-main` (the main-`fdcf3e00` A/B reference, used for §3's
and §4's population comparisons) removed
(`git worktree remove worktrees/triu2-main --force`). `/tmp/t2anch`,
`/tmp/t2`, and this lane's other `/tmp/triu2*` scratch removed. The
detached `run_anchored_diff.sh` chain this lane started and then killed
(§4, "What is NOT confirmed") left no scratch under the repo (its own
`mktemp -d` WORKDIR was outside the repo and unlinked by its own `trap
cleanup EXIT`, which fires on SIGTERM).
