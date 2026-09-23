# b1ledger — reading the batch-1 ledger (O-45) against the D119 bar

Lane `b1ledger`, 2026-09-23, opus, from `467a08f3`. Analysis + compile-side
measurement only; nothing under `src/`/`cli`/`lib/`/`tests/`, nothing written
in pcrec-bench, NO clock read on this box.

**Delivered.** `docs/dev/optloop/cycle1_ledger_reading.md` (664 lines),
`docs/dev/summaries/2026-09-23-optloop-cycle1-exec-summary.md` (123),
`docs/dev/optloop/b1ledger/` (reproduction pieces + CLAUDE.md), and entries
in `docs/dev/optloop/CLAUDE.md`, `docs/dev/summaries/CLAUDE.md`, here.

**Verdicts.** [OPT-ANCHOR-VM] MEETS (13/13 targets); [OPT-ENDWIN] MEETS
(4/4); [OPT-REQBYTE] targets meet, carve-out clause FAILS (12 cells,
18.7-38.5%). Dispositions in the reading's §7.

**Five things worth reading the file for.**

1. A NULL CONTROL the ledger contained for free: 56 of 187 artifacts are
   program-identical across the pin, 16 of the 64 regressing cells sit on
   them, worst +8.46% at 35× its own IQR with `__text` byte-identical.
2. Two corrections to the brief's framing: [OPT-ENDWIN] on the DFA route is
   a start clamp, not a reverse pass; and the throughput regime is FIND-ALL
   (`adapter.py:3696-3698`), which this lane's first cost model missed.
3. The cost model is exact once the calls are counted (winpath/email
   predicted +23,120.8 ns, measured +23,103.5 / +23,059.6) — which is what
   licenses calling the 111×-60,674× residual a different mechanism.
4. The general finding is three rules, not one: dominance (one artifact
   `memchr`s byte 91 at line 49 and again at 107), admission (the rule is
   ALREADY at `emit_dfa.c:2999` for the prefilter, uninherited), placement
   (24 of 62 forced-VM artifacts lose gcc's partial-inlining split).
5. The `-o`-basename trap fired here, the fifth instance, and what caught it
   was a POPULATION COUNT reading zero where four had been hand-diffed.

**Validation COMPLETE** (docs only; no suite applies). `make -j4 CC=gcc-16`
clean; every emitted-C claim compiled with this tree's `build/pcrec` and a
scratchpad `git archive 25b1984f` build; the three throughput subjects
regenerated and sha256-checked against the bench's manifest (3/3).

**Owed to the manager.** The I-91 block (reading §8) is ready to append to
the bench inbox; blocks A and D confirm or refute §4.1's ranking and D is
the fix's own acceptance test. The arm64 disassembly must be replicated on
gcc-15.2/x86_64 before the partial-inlining mechanism is stated as fact.
