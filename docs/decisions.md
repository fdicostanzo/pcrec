# Decisions (ADR-lite)

One entry per significant decision. Format: id, date, decision, why, revisit-when.

## D1 — 2026-08-09 — Two-engine design (DFA + backtracking VM)

See APPROACH.md §2. PCRE leftmost-first semantics + irregular features force a VM;
long-text speed forces a DFA. Hybrid: DFA prefilter/islands, VM for captures and
irregular constructs. Revisit: never expected; this is load-bearing.

## D2 — 2026-08-09 — Build system: plain GNU make

Pure C, gcc-centric, no external deps; embedded consumers vendor generated .c/.h
files, not our build. Non-recursive Makefile, build/ output dir. `gmake` == `make`
on Linux. Revisit-when: packaging for distros/IDE consumers demands CMake configs.

## D3 — 2026-08-09 — Leftmost-first spans via priority subset construction

DFA states are priority-ordered NFA state lists; when a closure reaches ACCEPT,
lower-priority states are pruned and the DFA state is marked accepting; the runtime
records the last accept position seen. Surviving threads are always higher priority
than any recorded accept, so later accepts correctly override — this yields PCRE
leftmost-first (greedy/lazy-respecting) spans from a pure DFA, no VM needed for the
base tier. `$` (end-or-before-final-newline) handled as a per-state "accept at EOL
position" flag computed by a second closure pass. Revisit-when: captures (M4) need
tagged automata or VM anyway.

## D4 — 2026-08-09 — Test format .rxt + python-re cross-verification

Line-based .rxt files (pattern / m "subject" start end / n "subject" / perr);
harness compiles the generated C per pattern block and diffs driver output. Corpus
expectations are machine-verified against python3 `re`, whose semantics match PCRE
for the base tier. Revisit-when: M7 imports PCRE2's own testdata format; differential
fuzzing vs libpcre2 supersedes python-re as the oracle.

## D5 — 2026-08-09 — Subagent usage policy

Mechanical, spec-driven, self-verifiable work (test harness, test corpora, per-dir
CLAUDE.md upkeep) goes to cheaper-model subagents (sonnet/haiku) with an explicit
self-verification step in the task. Core compiler code (parser, IR, codegen) stays
in the main session for design coherence. Requested by Frank 2026-08-09.

## D6 — 2026-08-09 — Adversarial critic review gate at every major checkpoint

At the close of each milestone (and any comparably large checkpoint), spawn a
panel of adversarial critic subagents over the work since the previous
checkpoint — separate lenses (correctness/semantics, robustness, architecture,
tests/process), explicitly instructed to be unfriendly and to surface problems,
with evidence/reproduction required per finding (CONFIRMED vs SUSPECTED) and a
list of what was probed-and-held so clean areas are distinguishable from
unprobed ones. Findings are compiled + triaged into docs/reviews/<date>-<milestone>.md;
confirmed criticals are fixed before the next milestone starts, the rest become
plan.md steps. Requested by Frank 2026-08-09.

## D7 — 2026-08-09 — M2 engine shape: unanchored forward + reverse DFA, table-driven

For assertion-free patterns: forward search runs ONE pass over the subject using
the D3 priority construction over an NFA wrapped in a lowest-priority self-loop
(threads from earlier starts outrank later starts; accept-pruning kills the loop
on first match) — this yields the leftmost-first match END in O(n). A second,
NON-pruning reverse DFA (reversed concatenation order) scans backward from that
end; the earliest accepting position is the match START (no earlier start can
accept, else it would have owned the forward match). Emission for this engine is
table-driven (int16 transition tables + generic loop) — data initializers keep
gcc compile time flat where per-state computed goto was superlinear (R1 A-3) —
with a memchr (single escape byte) or bitmap skip loop while parked in the start
state. Patterns containing ^/$ remain on the M1 computed-goto attempt engine
until the fast path learns assertions. Computed-goto vs table for SMALL
assertion-free DFAs is deliberately unresolved: M2.3 benchmarks arbitrate.

## D8 — 2026-08-09 — `$` patterns run on the O(n) engine; `^` still does not

M2.7, forced by checkpoint review R2 finding A-2 (R1's "A-2 fixed" was only
true for assertion-free patterns; `$`-without-`^` still restarted the DFA at
every start position and measured textbook O(n^2)).

Engine selection is now `nfa_has_bot()` rather than `nfa_has_asserts()`:
`$` (N_EOL) needs only the per-state EOL variant the subset construction
already computes, applied in BOTH the forward and reverse machines at
end-of-subject / before-final-newline positions. `^` (N_BOT) needs a
position-dependent BOT variant in the REVERSE machine (checked at pp == 0),
which the DFA does not build — so `^` patterns stay on ENG_ATTEMPT. Fully
`^`-anchored patterns already get the start_max=0 fast path, so the remaining
slow shape is `^` on only SOME branches.

Measured: `a*b$` over all-'a' went from 0.199/0.738/2.886 s at 20/40/80 KB
(4x per doubling) to flat ~0.011 s through 160 KB; a realistic log pattern
with and without a trailing `$` is now at parity (69 vs 66 MB/s, same method)
where it was 14.3x apart. Revisit-when: the reverse BOT variant is built
(would let `^` join too, closing DD-7's engine-unification item).

The EOL path deliberately omitted the memchr prefilter and skip loops — both
advance past positions without consulting accept flags, unsound when a state
can accept at EOL. SUPERSEDED by M2.12/D11, which restored them.

## D9 — 2026-08-09 — alternation prefix trie: the two soundness rules

M2.8, closing checkpoint review R2 finding A-4. `src/ir/nfa.c` now factors
shared prefixes of flat alternations instead of emitting one class chain per
branch.

Naive trie factoring is WRONG, and wrong in a way that changes the reported
SPAN, not merely which branch "won". Two independent hazards, each confirmed
against python3 `re` and against pcrec's own unfactored construction, each
guarded separately, and each validated by sabotage (disable the guard and
named cases in tests/base/alternation_trie.rxt fail):

1. A branch that ENDS at a trie node competes with longer branches continuing
   through it, and no single accept-vs-descend order serves every subject:
   `abc|a|abd` on "abd" is [0,1), but `a(?:bc|bd)|a` is [0,3). Guard: at such
   a node, partition the branch list by INDEX around the ending branch —
   everything before it, its accept, everything after — and recurse into each
   part at the same depth. Parts may duplicate shared structure but never
   duplicate a branch, so the total stays bounded by the flat construction.

2. Branches merge only on bit-IDENTICAL class bitmaps, but two DISTINCT groups
   can still OVERLAP, and overlapping groups are not mutually exclusive:
   `[ab]p|[bc]x|[ab]xy` on "bxy" is [0,2), but `[ab](?:p|xy)|[bc]x` is [0,3).
   Guard: reorder groups only when their bitmaps are pairwise disjoint (fast
   path: all singletons, which is the keyword case); otherwise emit that
   node's list unfactored.

Mixed lists are handled by trie-ing only maximal runs of CONSECUTIVE eligible
branches: "first matching branch in index order wins" survives replacing an
index RANGE with a sub-alternation that picks its own first matching member.
A branch is eligible iff it is a left-leaning A_CAT chain of A_CLASS leaves;
notably a nested group inside a branch (`x(?:yz)|xy`) makes it ineligible,
which is conservative rather than wrong.

The argument above proves the strong property (same winning BRANCH), not just
the weak one (same span). Today only spans are observable, so the weak
property would suffice — do not let anyone "simplify" this to a span-only
argument, because M4 capture groups make branch identity observable and the
weak argument would then silently be a landmine. Revisit-when: captures land.

## D10 — 2026-08-09 — the NFA state cap is a memory backstop, not the ceiling

`PCREC_MAX_NFA_STATES` went 20000 -> 131072 in M2.8. The old value was simply
the wrong limiter: it fired before the DFA caps, which are the ones grounded
in measured emitter cost (R1 A-3). Measured at the new value: a 6000-word
keyword list compiles (1.46 s, 56 MB RSS); a 10000-word list fails on the DFA
cap with its actionable "VM engine arrives in M4"; a 20000-word list fails
fast (0.05 s) on the NFA cap. That is the intended ordering.

The arithmetic: sizeof(NState) is 48 B, two machines are built (forward and
reverse), so 131072 states is ~12.6 MB of NFA plus ~2 MB of closure scratch.

Stack depth deliberately does NOT appear in that derivation any more. It used
to: `clo_visit` recursed on a split's t2 edge, so an alternation chain nested
one frame per branch. gcc turned that into a jump at -O2 but NOT at -O0, where
a 200000-branch alternation segfaulted and 100000 survived — i.e. the safe cap
depended on the optimisation level. All tail-position edges are now explicit
loop iterations, leaving only a split's preferred branch recursive; verified
at -O0 on a 1,000,000-branch alternation. Revisit-when: a pattern shape is
found whose PREFERRED-branch nesting is deep.

## D11 — 2026-08-09 — scan avoidance under EOL: bound the skip AND order it first

M2.12, restoring what D8/M2.7 traded away. Two rules, and the second is the
one that is easy to miss:

1. **Bound every skip at n-1, not n.** A prefilter or self-loop skip advances
   `pos` without consulting accept flags, which is unsound exactly when a
   state can accept at an EOL position. Stopping at n-1 leaves the last two
   positions — the only ones where an EOL view can apply — to the stepped
   loop. The forward memchr additionally loses its `return 0` early-out, since
   the start state's EOL view may still accept at n-1 or n.

2. **Run scan avoidance BEFORE the accept/EOL evaluation, not after.** The
   first attempt at M2.12 got rule 1 right and still produced 53 divergences
   over a sweep of 27 `$` patterns x 69 subjects, including whole matches
   lost (`.*=.*$` on "xyz=abc\n" -> nomatch). Bounding a skip at n-1 means it
   can LAND on n-1, and the loop then consumed that byte without ever taking
   its EOL view. Evaluating after the skip fixes it, and is equally correct
   without EOL: every position a skip passes has the same state and therefore
   the same accept bit, and `last` (forward) / `sfound` (reverse) want the
   extreme position, which is exactly where the skip stops. That also makes
   the per-skip-state `last = pos` line redundant, so it is gone.

Rule 2 applies to the EOL path ONLY, and that asymmetry is load-bearing.
CORRECTION (same day): the first version of this entry claimed non-EOL output
was byte-identical across 8 probe patterns. That was true of an EARLIER draft
of M2.12 and false of what shipped — the reorder was applied unconditionally,
which changed the non-EOL loop and cost **43%** on `[01]*1[01]{8}`
(158.4 -> 90.8 MB/s, tight spreads). The prefilter got hoisted above the
accept check, and while both orders are equally CORRECT without EOL, only one
is fast. The emitter now reorders only when `eol` is set, the in-skip
`last`/`sfound` recording is retained on the non-EOL path where the accept
check precedes the skip, and non-EOL output is now genuinely byte-identical to
pre-M2.12 across those 8 patterns.

Rule 2 is also why the two emitters M2.7 forked are merged back into one
EOL-aware `emit_unanchored`: the fork is how the `$` path lost scan avoidance
for a whole milestone without any test noticing.

Measured (7 trials each, load avg ~0.95): `ERROR: .*$` over 8 MB of log text
went 291 -> 22248 MB/s median, with non-overlapping ranges, and is now at
parity with `ERROR: .*` (22797 median). The non-EOL path is a statistical TIE
before vs after (13840-24282 vs 15242-24439) — an early single-sample reading
suggested a 1.4x gain there and was noise. Revisit-when: `^` joins this engine
(D8/DD-7), since a reverse BOT variant would add a second position-dependent
view with the same ordering hazard.

## D12 — 2026-08-09 — benchmark budgets are set from measured medians, not vibes

M2.9, closing R2-B3/B4. The old budgets were 9x-300,000x looser than the
numbers they guarded, so none of them could fail. Concretely: a sabotage build
with the memchr prefilter and skip states disabled measures 354/319/318 MB/s
on throughput cases (a)/(b)/(c) — a 5.4x/68x/5.6x regression — and the OLD
budgets of 200/50/50 MB/s would have passed all three.

Every budget is now the measured median on the reference box divided by ~1.75,
so a ~1.75x regression fails. Under the new budgets that same sabotage fails
all three, which is how the numbers were chosen and is the check to repeat
whenever they are retuned.

Supporting rules, because a tight budget on a noisy measurement is just a
flaky test:
- Every timed run is pinned (`taskset -c $BENCH_CPU`; `chrt -f 50` is probed
  and used only if permitted, which it is not on this box).
- Every measurement is BENCH_TRIALS repeats (default 5), judged on the MEDIAN,
  with the max/min spread printed on the row so noise is visible rather than
  averaged away. Observed per-trial spread here is 1.03x-1.49x.
- Governor, turbo, core count, pinning status and load average are printed
  with every run.
- No measurement may be sub-millisecond. Case (b) and the linearity subjects
  were being timed at 0.75 ms and 1.4 ms, i.e. mostly timer and startup cost;
  raising their iteration counts to 20 moved (b) from an apparent 10534 MB/s
  to a real 21910 MB/s and the linearity ratio from 2.70 to 3.63 against a
  theoretical 4.0.
- Case (c) measured EARLY EXIT, not throughput: its subject planted a match
  4 KB into 8 MB. Its subject is now match-free so the scan is real, which
  moved it from a meaningless 5,547,850 MB/s to 1794 MB/s.

Revisit-when: the reference box changes (every value is env-overridable, which
is the intended way to retune), or a budget starts failing on noise rather
than on a regression — in which case raise BENCH_TRIALS before loosening the
budget.

## D13 — 2026-08-09 — skip eligibility is a fraction of LIVE bytes; and the D7 arbitration is resolved: table always

M2.10, from R2-A5. Two separate things, both settled by measurement.

**Skip eligibility.** `pick_skip_states` required a state to self-loop on >=192
of 256 bytes. That rule silently assumed subjects are wide-alphabet text. It
admits the `.*` state of `.*=.*` (255 live, 255 stay) and rejects the `[01]`
state of `[01]*1[01]{8}` (2 live, 2 stay) — even though the latter stays on
100% of the bytes that pattern can ever see. That rejection is most of what
R2-A5 described as case (f) having "no skip-eligible states".

The criterion is now stay/live >= 75%, where live counts bytes whose
transition is not dead. A skip loop pays off exactly when the machine, once in
a state, tends to remain there, and that is a property of the live alphabet,
not of the byte space; dead bytes end the run either way, so counting them
against the state measures the wrong thing.

**REVERTED, same day, by its own measurement.** The reasoning above is sound
and the result was a regression. Admitting the `[01]` state gives case (f) one
REVERSE skip table and measures ~27% SLOWER on the case it was meant to fix:
158.6/159.1 -> 118.7 MB/s on the compare harness, 159.1/157.5 ->
115.9/115.8 MB/s on bdriver, spreads 1.01-1.02x.

The +40% originally recorded here was a bad measurement: the "before" sample
read 83.7 MB/s where the true value is ~158, taken un-interleaved at load 1.69
and never repeated. Interleaved repeats on two independent harnesses agree it
was noise. The lesson is not subtle and had already been written down twice in
this journal — a single sample is not a measurement — and it still cost a
shipped regression.

Mechanism unknown and deliberately left so rather than guessed at: the
suspicion is that a backward byte-at-a-time skip loop loses to the reverse
table walk, which would mean skip loops are worth less in the REVERSE machine
than the forward one. Untested. `tests/codegen/run_codegen_tests.sh` now
asserts the state stays skip-INELIGIBLE, so the idea cannot be re-landed on
plausibility alone.

**The D7 arbitration.** D7 promised, and M2.3 claimed to have delivered, an
arbitration between computed-goto and table dispatch for small DFAs;
`emit_unanchored` has always been unconditionally table-driven. R2-A5 caught
the false claim. Resolved now by direct micro-benchmark
(scratchpad `dispatch.c`, both dispatch styles over the same 6-state DFA, same
subject, same flags): **computed goto is 2.59x SLOWER** (144 vs 374 MB/s),
stable to within 0.5% over 5 runs.

Six states is about as small as a useful DFA gets, so there is no crossover to
arbitrate — the table wins across the whole range, and the unconditional table
emitter was right all along. M2.3's error was claiming an arbitration had
happened, not the choice it landed on. The mechanism is that a data-dependent
indirect jump mispredicts on essentially every byte, while a small transition
table is an L1 hit with no misprediction at all.

CORRECTION (same day, from my own follow-up measurement — no critic needed to
catch this, only a second experiment): "there is no crossover" is WRONG as a
blanket statement. The crossover is not in DFA SIZE, it is in transition
PREDICTABILITY, and it is large:

| input to the same 6-state DFA | table | computed goto | goto/table |
|---|---|---|---|
| random bytes (data-dependent) | 350-374 MB/s | 140-144 MB/s | 2.48-2.65 |
| alternating bytes (predictable) | 372-373 MB/s | 1318-1342 MB/s | **0.28** |

So computed goto is ~3.5x FASTER when the transition sequence is predictable,
because the indirect-branch predictor runs ahead; and ~2.5x slower when it is
not, because it mispredicts on nearly every byte. The table is flat across
both, which is its real virtue.

The decision stands — unconditional table — because general regex scanning
over real subjects is the data-dependent case, and the predictable case is
largely what the skip loops already cover. But the reason is "unpredictable
transitions dominate", not "goto is simply slower", and anyone reading the
original wording would have been misled.

Second caveat on the same benchmark: at -O1 the table version measures 7234
MB/s against 350 MB/s at -O2, a 20x swing that no property of the DFA
explains. Something in the micro-benchmark's accumulator loop is being
optimised in a way that does not reflect real scanning, so treat the ABSOLUTE
numbers here as untrustworthy and only the within-level ratios as meaningful.
The direction is robust across -O1/-O2/-O3 (58.5x / 2.48x / 2.65x, all
favouring the table on random input).

Revisit-when: a workload appears with long, highly predictable state runs that
skip loops cannot cover — that is now a MEASURED opportunity rather than a
hypothetical one.
