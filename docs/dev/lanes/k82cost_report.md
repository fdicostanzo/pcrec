# k82cost — K82 cause (B): the expected-cost admission design (2026-10-04, lane k82cost, opus)

DESIGN ONLY. Branch `lane/k82cost` from main `940fa06e`. No `src/`,
`tests/` or `docs/spec/` change, and no `make test`. The worktree was built
once, `make -j4 CC=gcc-16`, to read `--emit-facts` and emit the T3 twins.
The deliverable is `docs/design/litscan_k82b.md`. Its instruments and
transcripts are in `docs/dev/optloop/s4/k82cost/`.

## Summary (what a resuming agent needs)

1. **The model.** A discard gate's expected cost against no gate, per
   subject:
   `Δ = k·f + (k·β + σ·s)·(1−e^{−ρW})/ρ + over − E·W·e^{−ρW}`.
   - The rates ρ (markov1 run-rarity) and σ (byte-rate over the PICKed scan
     member) come from the bundle.
   - `f`, `β` and `s` are measured. Mac: 3.7 ns, 0.020 ns/B, 7.5 ns. Linux:
     3.4, 0.020 (`β` assumed), 8.0.
   - E is the engine's ns/B. It is the weak term, with no calibration yet.
   - The row argmins over {none, byte, run, byte-then-run}.
2. **Oracle rates** (the subject as its own exemplar): every K82 cell is
   called right, and the measured deltas are reproduced to within about 2.5x.
3. **No exemplar, which is the bench's compile**: 0 of the 5 cause-(B)
   movers are declined. NONE run-rarity is cardinality, 21 bits against an
   actual 7.4.
4. **`weblog`/`log` at 64 KiB**: the rule declines `mod-i`/`mod-r`/`cls-*`
   and keeps the customers. `ci-strasse` stays a mover.
5. **W is decisive.** At a log line every gate pays. The declined 16-bit knee
   was `log2(64 KiB)`.
6. **Robustness.** Uniform 2x scaling of the cost terms flips 0 of 44
   verdicts, and the Mac and Linux rows give identical verdicts. A 4x
   adverse gate/E ratio loses `union-select`.
7. **Twin T3** (the gate's candidate handed to the DFA), Mac ns/B at
   64 KiB:
   - `mod-i`: NEW 1.39, T3 0.81, DENY 0.76;
   - `cls-fold-pair`: 0.99, 0.55, 0.55;
   - `ci-strasse`: 0.65, 0.49, 0.53;
   - `ci-ascii-ctl`: 0.209, 0.208, 0.521.
8. **Recommendation:**
   1. land k82fix (A)+(C);
   2. build the handoff row (Q1) as K82(B)'s bench cure, through the panel;
   3. land this cost row + B4 once a per-form E probe exists.

   W should come from the bundle's own record length (Q2(b)). No builtin
   bigram (Q5). `set-leads` stays (Q6).

## OWED (none run by this lane)

- `memchr_cal.c` on ubuntubudu (the Linux `β`; command in
  `optloop/s4/k82cost/CLAUDE.md`).
- The T3 startpos answer differential.
- A Linux T3 alpha.
- The corpus mover census under builtin/`weblog`/`log`.
- The per-form E calibration (design §5 Q3).
