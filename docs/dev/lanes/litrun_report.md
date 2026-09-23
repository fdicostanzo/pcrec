# litrun — `[OPT-VMLIT]` trigger read (2026-09-23)

Lane `litrun`, sonnet, branch `lane/litrun` from `main`. Measurement only
(D77): nothing under `src/`. Frank's original question — the VM emits a
literal run as N per-byte if/goto tests; should it fuse them into a word
compare / `memcmp` — turned out to have PRIOR ART: `docs/dev/plan.md`'s
`[OPT-VMLIT]` row (TRIGGER PARTIALLY MEASURED 2026-08-31 by [OPT-5]
STEP 0), plus siblings `[WORD-FOLD]` (the caseless AND-mask cube compare)
and `[CLS-TREE]`/`[OPT-CLSPACK]` (the per-position class kit). The manager
course-corrected mid-task to frame this as the `[OPT-VMLIT]` trigger read
rather than a fresh census — the deliverable below is the corrected one.

**Deliverable**: `docs/dev/optloop/vmlit_trigger_read.md` (its own
CLAUDE.md entry), this report, and `lanes/CLAUDE.md`'s entry below.

## What was done

1. **Closed the row's open half.** `[OPT-VMLIT]`'s 2026-08-31 measurement
   confirmed the emitted form is per-byte, "never memcmp", but left open
   whether that's because gcc doesn't find the fusion or because pcrec
   never asks for it. Compiled the brief's literal-run patterns with
   `--engine=vm`, read the emitted C (confirmed the per-byte if/goto
   shape) and disassembled at `gcc-16 -O2`/`-O3` on this Mac (arm64), then
   hand-rewrote the run as an `&&`-chain and, separately, as an explicit
   `memcmp()`, disassembling both — plus the same pair on x86_64 via a
   light tailnet probe (`ssh duxevents@100.69.121.107`, gcc 15.2.0, two
   small compiles, no suite). Finding: gcc never fuses the `&&`-chain
   shape, at either optimization level or target; only explicit `memcmp()`
   gets gcc's own builtin fusion. This reproduces `docs/design/
   reqpos_2b.md` §3.2's already-measured lowering (cited as prior art,
   not re-derived) at a second landing site (the VM's per-attempt literal
   consume, vs. that note's search-side prefilter), and adds the new
   negative result that `&&` alone is not enough.
2. **The population — and an honest scope mismatch.** `[OPT-VMLIT]`'s own
   named trigger population is `bench/bounded`'s `ctx-lazy-*`/`ctx-
   greedy-*` and `bench/loglines`'s `level-context` cells against
   `pcre2-jit`. This lane did not measure that population — those
   subbenches are outside this lane's light-probe scope and a fresh JIT
   ratio is a bench-window operation, not something to run here. Read the
   patterns directly instead: they are exactly literal-word alternation
   branches (`fail|abort|panic`, `disk|memory|socket|quota`, etc), so the
   row's premise reads correctly, but the trigger number itself is still
   owed. As a SECOND, independently-found population (not a substitute):
   crossed `capability@0.1`'s `stampdiff.json` engine stamps against the
   60 losing match-regime cells of `cycle1_caps_view.md`+
   `cycle1_nocaps_view.md`, finding 5 genuine VM-route losing cells with a
   real literal run ≥4 (after catching a parser false positive on
   `(?<name>`/`(?&name)` group syntax) — and ruled out the prefilter as
   their cause (`RX_VM_PREFILTER` already `"hybrid"`).
3. **Pointed at the shipped design rather than inventing one.** The
   caseless form is `[WORD-FOLD]`'s own AND-mask cube compare
   (`(w & K) == T`), not a newly-invented masked compare — that row's own
   D77 census is still unrun, and this memo does not build on it, only
   cites it. `[CLS-TREE]`/`[OPT-CLSPACK]`'s shared atom-table form
   (`form_char_step0.md:84`) is named as the adjacent but different
   per-position kit member, not the answer for a sequence-level run.

## Recommended row disposition

**`[OPT-VMLIT]` stays `STATE:not-started`.** Its "never memcmp" clause is
now fully measured (cite this memo) — an emission choice, not a missed
compiler opportunity. The row should NOT open in cycle 3 on this lane's
5-cell `capability` population; that is a real but second population, not
the row's own named trigger. The gate that still decides the row: a bench
pass timing `ctx-lazy-*`/`ctx-greedy-*`/`level-context` against
`pcre2-jit` at the current pin.

## Validation

No `src/` changes to validate. Own build: `make -j4 CC=gcc-16` in the
worktree, clean. Every number in the memo names its exact command. Nothing
owed beyond the named bench measurement, which is explicitly out of this
lane's scope.
