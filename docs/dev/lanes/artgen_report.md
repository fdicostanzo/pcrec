# Lane artgen: report ([ARTREV] S5, the generalizer, pilot; 2026-10-06, opus)

Branch `lane/artgen` off main `6a0b7953`. Its `src/` is identical to the ARTREV pin `57db5152`, and
all three pilot artifacts regenerate sha256-identical. Deliverable:
`docs/dev/optloop/artrev/generalize.md`, plus `docs/dev/optloop/artrev/gen/`, which holds the census
script, selftest transcript, summary and per-row TSV. `docs/dev/optloop/CLAUDE.md` is updated and a
new `gen/CLAUDE.md` added. `plan.md` is NOT edited: the rows are drafts in generalize.md §4.

## What was done

- **The leads, merged.** The 25 counted pilot leads were merged into 15 ideas (I1-I15), with the
  A07 pair's duplicates kept under both reviewer ids. Each idea carries:
  - the emitter site (file:line at `6a0b7953`);
  - a counted population;
  - known vs new against the plan rows;
  - its START-SET stage-3 interaction;
  - a give-up tag;
  - cost and D119 class.
- **The census** (`gen/census.py`): 3,704 distinct corpus patterns (3,333 compile) and 345 bench
  patterns (321 compile), read-only at pcrec-bench `eb634d9d`.
  - It uses 15 classifiers and runs in ~2 min on the Mac. No gcc, no timing.
  - **Selftest: 31/31 controls pass** (`gen/selftest.txt`, written by `census.py --selftest`). The
    first run failed 5, and those failures fixed the instrument:
    - a misread stamp: `RX_REQ_RUN`'s `@N` is the scan member's index, not the run's offset;
    - an SCC reader that could not see A09's {406,435} stay set;
    - three ill-chosen controls.
- **START-SET stage 3**, `lane/ssbuild3` tip `c9154808`, was built in scratch (`build-artrev/`, not
  committed) to read stage 3's reach directly.
  - It takes a first-* row on 18 bench artifacts, which equals startset.md's own count of 18.
  - It moves A09 to A09 L2's exact shape.
  - It leaves A01 and A07 byte-identical apart from the abi stamp.
- **Two "already shipped" checks**, made by compiling variant spellings with the pin compiler:
  - The possessive spelling of A07 (`\b(\w++)\b\s++\1\b`) compiles frameless and `inline`, with
    `rx_fail: return -1`. That is L2 plus the inline half of L4, with no new codegen.
  - A findings bundle analyzed from the cell's own loglines subjects makes the shipped emitter pick
    A01 L2's `'t'`.

## Headlines (details in generalize.md §0)

1. **A07's biggest scratch wins are mostly a possessify ANALYSIS gap.**
   - I6 adds two sound arms in `possessify.c`: a `\b` follow over word-pure bodies with m ≥ 1, and
     a backreference FIRST taken from its group.
   - The shipped emitter does the rest (I8 = [CC-DIFF], already shipped).
   - The residual is trail elision (I7, NEW) and a context-aware VM start filter (I5, generalising
     the START-SET VM hat).
   - **I6's population is 1 bench / 2 corpus.** That is a large ratio on a tiny population.
2. **The CTX group is the population story.** `level-context` and `ctx-*` carry I11 (= stage 3), I13
   (multi-state stay set, generalising [OPT-3-RUNEND]), I14 (count-collapsed hybrid skips the VM,
   NEW) and I15 (frameless lazy step, NEW).
3. **I1 is [ENG-TACTICS] (b) reverse-inner on the DFA route.** Population 17 bench / 90 corpus. On
   12 of the 17 the rarer byte is already known to the emitter (K82 `set-leads` presence `memchr`),
   but it is never used as the scan anchor.
4. **I4 (A01 L4) is a concrete candidate mechanism for K88**: the handoff re-scan K88 asked to have
   twinned. Population 36 bench / 114 corpus.
5. **I2 needs no emitter change** ([FINDINGS], measured). I9 and I10 are codegen-micro and flagged.
6. **`changes-giveup-surface`**: I6 (5,380 repairs) and I7 (294,884, stacked). I14 only in its
   superseded r2 form, which had 5,562 repairs; build r3, which is exact. Each tagged idea names its
   spec hunk (the one-way give-up sentence in the tuning.md §2.20/§2.35 precedent form, limits.md §7)
   and a K65-style check.

## Validation

- `python3 docs/dev/optloop/artrev/gen/census.py --selftest` gives 31 controls, 0 failed.
- The full census run produced the committed `gen/summary.txt` and `gen/rows.tsv.gz`.
- No `make test` was run (not required: no `src/` change). Nothing was run on ubuntubudu.

## Owed / for the manager

- **S4 join.** generalize.md §1.4 says how the confirmer's verdicts fill the `confirmed` column (by
  idea, as `artifact:lead=VERDICT`).
- **Optional confirmer arm** (sent to main mid-lane): time the pin compile of `\b(\w++)\b\s++\1\b`
  against orig. It measures I6 alone through the SHIPPED emitter. Run hardened identity on it first.
- **Census coverage caveat.** The pattern reader used by K6, K12 and K15 parses 56% of bench and 37%
  of corpus patterns.
  - For K6, the 19 unparsed framed bench VM patterns were hand-checked and none has the shape.
  - Corpus K6 is a floor.
  - K3, K7 and K15 counts are necessary-condition upper bounds.
- **Re-pin.** Re-run the census when stage 3 lands. K11's `SS3` column then equals main.
