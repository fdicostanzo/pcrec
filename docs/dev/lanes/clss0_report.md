# clss0 — [CLS-TREE] S0 lane report

2026-09-28, lane clss0, Sonnet, Mac-local (worktree `worktrees/clss0`,
branch `lane/clss0`). Charter: the manager's brief (D129's S0 charter:
a1 remainder, a5, the [OPT-CLSPACK] timing arm, the §7(b) executor-brief
update). Design note: `docs/design/cls_tree_design.md`. Ruling: D129
(`docs/dev/decisions.md`).

## What shipped

Four commits on `lane/clss0`:

1. `2f02babe` — a1 byte-tier remainder + a5 asm-counting.
2. `b9ab1a43` — the [OPT-CLSPACK] timing arm (`bench_bytes.py` +
   `bench2-bytes`), Mac-smoked for correctness.
3. `e64e2c13` — design note §7 update (findings, withdrawals, the combined
   executor brief).
4. This report.

All box-independent (counts, bytes, answers) except the smoke run's own
timing, which is explicitly marked NOT CITABLE (Darwin, noisy box, tiny
probe count).

## a1: byte-tier whole-set remainder — CONFIRMED

`verify_whole.py` already dispatched on population name, so
`python3 verify_whole.py byteclasses` needed no code change: 41 sets, 0/41
mismatches, written to `results/whole_byteclasses.tsv`. What was missing was
the COMPARISON that turns two more size columns into a verdict — added as
`compare_whole_kit.py`, which joins those sizes against `sweep_byteclasses.tsv`'s
own lam=0 ("size") policy row (the kit's size-minimal answer) and classifies
each set WHOLE-WINS / TIE / kit-wins. Result, all 41 corpus byte classes
(`results/whole_vs_kit_byteclasses.tsv`):

    WHOLE-WINS = 0, TIE = 13, kit-wins = 28

**CONFIRMED, not merely expected**: no byte class in the corpus population
has a whole-set (`page2w`/`page3w`) object strictly smaller than the kit's
own size-minimal answer. A byte-tier whole-set DP candidate would win
nothing on size there — `MASK64`/`CUBES`/`BITMAP` already cover a
&le;256-code-point domain at kit prices with no per-page index overhead, as
the design note's §7 a1 expected.

Source: `studies/cls_tree_study/verify_whole.py` (unchanged),
`studies/cls_tree_study/compare_whole_kit.py` (new),
`studies/cls_tree_study/results/whole_byteclasses.tsv`,
`studies/cls_tree_study/results/whole_vs_kit_byteclasses.tsv`. Reproduce:
`make -C studies/cls_tree_study whole-byteclasses`.

## a5: kit byte-form asm-counting — extended from one witness to the population

`studies/form_char_twins/asm_evidence.c` measured ONE hand-picked
fold-vs-bitmap pair. `asm_count.py` (new) generalizes the method to every
kit byte form the emitter can build (`ALL`/`RANGES`/`CUBES`/`MASK64`) vs
`BITMAP` (today's shape), over the real 41-class corpus population, using
the SAME `emit.py`/`kit.py` machinery `sweep.py` uses (not hand twins):
each class's whole interval list is treated as one section, every kit
member that fits is emitted as a real matcher function, all compiled
together in one `gcc -O2 -S -std=gnu11` (non-static functions, so none are
dead-code-eliminated), and a per-function instruction count is read
directly off the assembly (`.globl`-delimited blocks, directives/labels/
comments excluded, branch mnemonics identified by an exact-match regex
checked against this box's own output rather than assumed — `bhi` etc. are
spelled without a dot here).

Mean instruction counts (arch=arm64, this box; Mach-O — **not** the x86_64
target `form_char_twins/results/three_spellings.s` was last regenerated on;
instruction COUNTS are the portable comparison, mnemonic text is not, and
the script's own header says so):

| form | n (sets it fits) | mean | min | max | ever branches? |
|---|---|---|---|---|---|
| `MASK64` | 15 | 7.40 | 7 | 8 | never |
| `RANGES` | 41 | 9.12 | 4 | 13 | sometimes (degenerates branchless when an interval touches a domain edge) |
| `CUBES` | 19 | 11.63 | 6 | 23 | usually (up to 4-cube covers cost 23) |
| `BITMAP` | 41 | 12.37 | 7 | 13 | usually; always carries one load (rodata > 0 on every row) |
| `ALL` | 0 | — | — | — | fits no class in this population (no byte class is one contiguous run) |

Source: `studies/cls_tree_study/asm_count.py` (new),
`studies/cls_tree_study/results/asm_count_byteclasses.tsv`. Reproduce:
`make -C studies/cls_tree_study asm-byteclasses`.

## The [OPT-CLSPACK] timing arm (D129 item 5)

D129 ruling 5: [OPT-CLSPACK]'s STEP 0 measured the shared atom table 24%
faster than the bit array at N=16 on `.text`/`.rodata` alone; the kit's
inline byte tests were never timed against either. `bench_bytes.py` (new)
is the missing arm.

**Design.** Unlike `bench.py`'s existing arms (one class's matcher timed at
a time), [OPT-CLSPACK]'s question is about MANY class sites live in the
SAME loop — the shape a real matcher's inner scan loop has when several
`[...]` sites are hot. So the harness's inner loop, every iteration, picks
a random SITE among N live classes (N &isin; {4, 16, 32}, bracketing the
plan row's own ~10-class crossover estimate) and a random byte, and
dispatches through a per-arm site-indexed function-pointer/index table:

- `bitmap` — TODAY's shipped shape: a 32-byte (256-bit) membership table
  per class, indexed directly by the byte (no base subtraction, no bound
  test — a byte class site always sees a full byte). Read straight off
  `byteclasses.tsv`'s own hex column, not rebuilt through `kit.FormBitmap`
  (whose section-relative indexing is a code-point-kit concern that does
  not apply to a byte class's flat domain).
- `kit` — the sectioning DP's own answer per class at `lam=16` ("mid", the
  calibration default the byteclasses/uprops sweeps already use), emitted
  by the real `emit.py`/`section.py` machinery.
- `atom` — [OPT-CLSPACK]'s general form, generalized from
  `form_char_twins/twin_D.py`'s `make_atom` (which parsed a base.c's own
  emitted tables) to build straight from the N classes' membership sets:
  one shared byte&rarr;atom[256] index (every byte's atom is the SET of
  classes it belongs to, restricted to just these N) plus a 64-bit mask per
  class. **Refuses loudly, not silently**, if N distinct classes would ever
  need more than 64 atoms — a real finding, not a thing to paper over.

Checked against an INDEPENDENT bsearch reference (`emit.reference`, one per
class, dispatched by site) — deliberately **not** the bitmap arm, even
though its table already IS the ground-truth membership word: sharing that
source between an arm and its own check is exactly the K35 blind spot
(`docs/dev/learnings.md` §3).

Wired as `make bench2-bytes` (same load gate/protocol as `bench2`: 11
interleaved rounds, load1 &lt; 0.5 gated and refusing rather than caveating,
every round checksummed). Reads the already-committed `results/
byteclasses.tsv` — no `build/pcrec` rebuild needed in a fresh checkout.

**Smoked on the Mac for CORRECTNESS ONLY**, per the brief ("never for
timing"): `results/smoke_bytes.tsv`, `rounds=2`, `nprobe=4096`,
`load1_at_start=1.97` (a `make test` was running elsewhere on this box;
`--max-load` was overridden for this smoke invocation only, since it is not
a citable measurement either way). **0 answer mismatches** at N=4 (5
atoms), N=16 (16 atoms), N=32 (29 atoms) — all three N values stay well
under the 64-atom ceiling on the real corpus population. The full-size run
(default 11 rounds &times; 2^20 probes) is OWED to the ubuntubudu executor;
see the brief below.

Source: `studies/cls_tree_study/bench_bytes.py` (new). Reproduce (smoke
only): `python3 bench_bytes.py --ns 4,16,32 --smoke --max-load 99 --out
smoke_bytes.tsv`. Heavy/citable: `make bench2-bytes` on a quiet box.

## The updated §7(b) executor brief (verbatim, as landed in the design note)

> **pcrecdev2 — [CLS-TREE] S0 timing session (read-only study run; writes
> ONLY `studies/cls_tree_study/results/bench2.tsv`,
> `studies/cls_tree_study/results/bench2_bytes.tsv`,
> `studies/cls_tree_study/results/capC_isolated.tsv`, and
> `studies/cls_tree_study/build/`).**
> Box: ubuntubudu, quiet (the harness itself refuses at load1 &ge; 0.5 and
> never caveats; a refusal is a result — report it with its load readings,
> do not loosen `--max-load`). Tree: pcrec at `<COMMIT the manager names>`
> (at or after the merge of `lane/clss0`; nothing in `src/` is read for
> b1/the isolated re-run — the study reads `src/parse/uprops_tables.inc`
> and its own committed `results/byteclasses.tsv` only. `bench2-bytes`
> needs no `build/pcrec` either — same committed-input rule).
> ```
> cd <pcrec checkout on ubuntubudu>
> git log -1 --format=%h                                  # record the pin
> gcc --version | head -1                                 # record the compiler
> mkdir -p build/clstree_s0
>
> # --- b1: kit/whole-set ns/char, the committed 2026-09-11 arm set + whole-set tables ---
> gnutimeout 7200 make -C studies/cls_tree_study bench2 CC=gcc \
>     > build/clstree_s0/b1_bench2.log 2>&1
> tail -5 build/clstree_s0/b1_bench2.log
> wc -l studies/cls_tree_study/results/bench2.tsv
> head -1 studies/cls_tree_study/results/bench2.tsv        # load1_at_start
>
> # --- CLSPACK: N=4/16/32 live byte-class sites, bitmap vs kit vs shared atom table ---
> gnutimeout 1800 make -C studies/cls_tree_study bench2-bytes CC=gcc \
>     > build/clstree_s0/clspack_bench2_bytes.log 2>&1
> tail -5 build/clstree_s0/clspack_bench2_bytes.log
> wc -l studies/cls_tree_study/results/bench2_bytes.tsv
> head -1 studies/cls_tree_study/results/bench2_bytes.tsv  # load1_at_start
>
> # --- isolated ^C/member re-run [r1 MEAS-2]: the one bimodal cell, alone, more rounds ---
> gnutimeout 600 python3 studies/cls_tree_study/bench.py \
>     --population k53 --sets '^C' --regimes member --lams 0,16,256 \
>     --rounds 41 --out capC_isolated.tsv \
>     > build/clstree_s0/measc_isolated.log 2>&1
> tail -5 build/clstree_s0/measc_isolated.log
> wc -l studies/cls_tree_study/results/capC_isolated.tsv
>
> echo "CLS-TREE-S0-TIMING DONE"
> ```
> Expected row counts (fewer only if a build/run fails — a `BUILD FAIL` or
> `RUN FAIL` line is a finding, report it verbatim; any `ANSWER MISMATCH`
> line aborts that command's run and is a finding):
>   - `bench2.tsv`: 4,620 data rows (12 sets &times; 5 regimes &times; 7
>     arms &times; 11 rounds).
>   - `bench2_bytes.tsv`: 132 data rows (3 N values {4,16,32} &times; 4 arms
>     {refbs,bitmap,kit,atom} &times; 11 rounds); also report the `n_atoms`
>     column's three values (expect small integers well under 64 — a
>     refusal naming ">64 atoms" is itself the finding, not a crash).
>   - `capC_isolated.tsv`: 205 data rows (1 set &times; 1 regime &times; 5
>     arms {refbs, bitmap1, lam0, lam16, lam256} &times; 41 rounds).
> The `CLS-TREE-S0-TIMING DONE` line is the done-trailer — its absence
> means the session did not reach the end (report whichever log's `tail`
> is last). Return all three TSVs (commit on a scratch branch or scp back)
> plus the `build/clstree_s0/*.log` files, the recorded pin/compiler, and
> the three `load1_at_start` readings. Wall time: b1 is dominated by 60
> set&times;regime runs of 7 arms &times; 11 rounds &times; 1 M probes (the
> 2026-09-11 run of 5 arms &times; 4 regimes fitted inside the I-65
> session); `bench2-bytes` is 3 builds &times; 11 rounds &times; 4 arms
> &times; 2^20 probes, small (well under b1's); the isolated re-run is 1
> build &times; 41 rounds &times; 5 arms &times; 2^20 probes, also small.
> Total session is expected to land well inside b1's own 7200 s budget —
> the two added commands' own timeouts (1800 s, 600 s) are generous
> relative to their actual size, not a sign they are expected to run long.

**Total expected wall time on ubuntubudu**: dominated entirely by b1
(the 2026-09-11 precedent run — a smaller arm/regime set — fit inside one
I-65 session; this session's b1 is the full 7-arm/5-regime/11-round set
against 12 sets, hence its own 7200 s ceiling). `bench2-bytes` and the
isolated re-run are each orders of magnitude smaller (a handful of builds,
&le;41 rounds, one class population's worth of probes each) and should each
land in low tens of seconds to a few minutes. **Practical estimate: the
session's wall time is b1's, plus low single-digit minutes for the other
two — call it "however long b1 alone would have taken, plus a few
minutes."**

## The two withdrawals/re-homings recorded in §7(a)

- **a3 (S5's renumbering population) — WITHDRAWN.** D129 Q4: S5 (the
  minimal-automaton splice) is dropped. The splice shrinks no artifact (the
  emitted DFAs are already the class's minimal automata, 299/453 states)
  and buys compile time only; the island ([UCP]'s mechanism) is what
  shrinks the DFA route and removes the class's K67 share. No renumbering
  population is ever needed, so this measurement is not merely deferred —
  it has no reason to exist.
- **a2 (the `A_CLASS` reader census) — RE-HOMED, not measured here.** Per
  the staging table (§6), this is S3's first act, not an S0 measurement: it
  classifies readers against `A_WCLASS`, which does not exist until S3
  builds it. Charter it there rather than doing partial/premature work
  here against a target that does not yet exist.

## What's owed after this lane

1. The ubuntubudu executor session above (b1 + bench2-bytes + the isolated
   `^C` re-run) — relay via pcrecdev2, queued behind whatever else holds the
   box (D129 named it queued behind [B115]).
2. Once that returns: CT-2's per-probe time model calibration and CT-3's
   λ re-proposal (the design note's own next steps), now with the CLSPACK
   arm's numbers feeding [OPT-CLSPACK]'s Q5-revised disposition and the
   isolated re-run either confirming the `^C` bimodality as environmental
   (drop it, as the note already does) or reopening it as a real finding.
3. [UCP] design work proceeds in parallel (D129 Q7) — unaffected by
   anything in this lane.

## Validation

- `make -C studies/cls_tree_study whole-byteclasses` — 0/41 mismatches,
  re-ran clean.
- `make -C studies/cls_tree_study asm-byteclasses` — re-ran clean, 116
  data rows (41 classes &times; forms that fit each), no build failures.
- `python3 bench_bytes.py --ns 4,16,32 --smoke --max-load 99 --out
  smoke_bytes.tsv` — re-ran clean, 0 answer mismatches (would `sys.exit`
  loudly otherwise).
- `make -n bench2-bytes` — dry-run checked, recipe expands correctly; the
  HEAVY form was deliberately never run on this box (owed to ubuntubudu
  per the brief above).
- No `make test`/`mech`/heavy suite touched — a full `make test` was
  running on this box for this lane's whole duration.

All validation numbers above are COMPLETE for this lane's own scope. The
one thing OWED past this lane's end is the ubuntubudu executor session
itself (log path `build/clstree_s0/*.log` on that box once run), which is a
manager-relayed, not a clss0-run, step.
