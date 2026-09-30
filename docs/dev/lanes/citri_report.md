# Lane citri: CI red on `test-clskit` (report)

**Lane:** citri, sonnet, triage + fix. **Branch:** `lane/citri` from main
`58a2a417`. Not pushed (a push cancels CI; the manager pushes).

## 1. Cause

CI's `make test` (serial, PROCS=4, nothing else running) failed only
`test-clskit`, and the check DID say why: 23 `D45 CPU BUDGET ... exceeded 10s of
CPU time` blocks (`gcc: internal compiler error: CPU time limit exceeded signal
terminated program cc1`), then the derived FAILs (459 of 591 sets, 144 law runs)
that read like a separate problem and are not. So the check was not silent; the
run's own summary lines just hid the 23 causes above them.

**It is the compiler version, not load, not a runner budget, not a regression.**
CI is gcc 13.3 (Ubuntu 24.04); the Mac is gcc-16, ubuntubudu gcc-15, and the same
commit is green on both.

Evidence (all from the CI artifact `pcrec-test-logs` and a local re-emit of the
same 51 units, byte-for-byte the same chunking at 58a2a417):
- The 28 units that BUILT on CI are in `watchdog.log` (their RUN records); the
  23 that failed are exactly the other 23 of 51. Joining against each unit's
  compile CPU on the Mac (gcc-16, `-O1 -Werror`, solo): every unit under ~0.9 s
  passed, nearly every unit over ~1.0 s failed (the exceptions, 0.91 s failed and
  1.23/1.34 s passed, are a noisy ~8-11x factor). So gcc-13 needs ~10x the Mac's
  CPU to COMPILE this text.
- The same units RUN only 1.7-2.1x slower on CI than on the Mac (chunk_003 0.86
  vs 0.49 s, _007 2.68 vs 1.32, _005 2.12 vs 1.33, _012 0.31 vs 0.18), which is the
  runner's CPU ratio. So ~5x of the 10x is gcc-13 on this text (class-matcher
  units: hundreds of KB of `static const` tables and multi-thousand-line
  `static inline` functions).
- clstri measured gcc-15 on the Ryzen at ~2.4x the Mac on a 5.2 MB unit, i.e.
  the same ratio as the CPU; gcc-15 and gcc-16 behave alike, gcc-13 does not.
- It is not load: `make test` in CI is serial; on the Mac the run and compile
  CPU are stable to a few percent. The 9-failed run at e3ce677f versus 23 at
  58a2a417 is the same threshold moving across a noisy 8-11x factor, plus
  clstri's re-chunking in between.
- Not a pcrec compile-time regression: nothing else in the suite (thousands of
  artifact compiles) came near the budget on the same runner, and the units are
  the checker's own text (every kit form forced over every set), not shipped
  artifacts.

What I could NOT do: run gcc-13 (no build-capable Linux in this lane), so the
"~5x is gcc-13" split is inferred from the CI/Mac compile-vs-run ratios, not
measured directly. The fix below is sized to the inference and prints the number
that would refute it.

## 2. Fix (`tests/clskit/` only; no `src/`, no abi, no spec)

D45's rule is that a compile over budget is a shape to fix, not a budget to
raise, and the shape here is the unit size. clstri had already moved to packing by
emitted bytes, but with a 1.5 MB budget calibrated on gcc-15/16 and with an
ATOMIC unit per composition group (six sets x ~13 variants, 2-3.2 MB, seven such
units: 2.1-2.7 s on the Mac, so 20-30 s on gcc-13, unfixable by any byte budget).

1. `clskit_driver.c` packs VARIANTS, not groups. The only indivisible part of a
   group is its LAW bundle (the K4 and P3 variants of every set in a group that
   has compositions, plus the group's COMPS rows, since the law compares a result's
   variant against its operands' in one process, about 400 KB for the worst
   group). Every other variant is checked against its own set's reference alone, so
   it may sit in any unit that carries that set's reference arrays (copied into
   each). `CHUNK_BYTES` 1,500,000 -> 250,000, sized for gcc-13 (Mac 0.2-0.4 s a
   unit, ~2-4 s there). Largest unit 0.4 MB (a law bundle).
2. The script counts sets by `idx=` (new field on `CHECKED`, since a set's
   variants can now span units; names repeat, so counting by name read 491 of 591 on
   my first attempt, which is how the guard was seen to fire) and checks the
   variants SUM against the driver's own `VARIANTS n` line, so a variant or set
   that lands in no unit still fails loudly.
3. Every run prints its headroom: `clskit: compile CPU per unit (D45 budget 10s):
   331 units, max 0.58 s, total 116.9 s` (the compile's user+sys via the
   subshell's `times`, the RLIMIT_CPU clock). Next CI run states the gcc-13 max
   directly, which either confirms the ~10x factor or corrects it.

Docs: `tests/clskit/CLAUDE.md` (driver paragraph), `docs/testing.md` "CI" (new
paragraph naming the run and the finding), header comments in the driver and
`checker_main.inc`.

## 3. Validation

`make test-clskit CC=gcc-16` in the worktree (log
`/tmp/citri_s/clskit3.log`, scratch, not committed): **5 passed / 0 failed**.
331 units, 591 sets, 7,586 variants, 8,451,676,390 code-point checks, 0
mismatches; 146 compositions x {K4, P3} law, 325,320,704 checks, 0 mismatches;
crosscheck 20,685 selections, 0 disagreements (numbers identical to before the
change, only the unit count moved 51 -> 331). Compile CPU per unit max 0.58 s
(under 4-way parallel), total 116.9 s (was 58.7 s: the per-invocation and copied
reference-array overhead; on CI at ~10x this is ~5 min of a 54 min run).
Failing direction: the first draft's name-keyed count read `491 sets checked of
591`, i.e. the coverage guard fires on a lost set. I did NOT plant a lost
variant to see the new `variants` sum fire (its shape is the sets guard's).

## 4. Owed

- **CI verification is owed**: push, and read the `clskit: compile CPU per unit`
  line in the run. Expected on gcc-13: max ~4-6 s. If it reads over ~7 s, the
  10x inference is low and `CHUNK_BYTES` should drop again (each halving is
  ~free); if the line is missing, the script did not run.
- Margin caveat: law bundles are the floor (cannot be split); the densest 0.39 MB
  unit costs 0.6 s solo on the Mac, so the worst-case margin against the 10 s
  budget is ~1.7x at a 10x factor. Not further reduced because the return is
  small and the unit count (331) already doubled total CPU.
- No mech row: S360-S364 plant defects in `src/gen/clskit.c`, unaffected; I did
  not re-drive them (the check's pass/fail count is unchanged, 5/0).
