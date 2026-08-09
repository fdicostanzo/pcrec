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
   duplicate a branch, so the total stays bounded by flat + O(branches).
   CORRECTION (R3 critic): the original wording said "bounded by the flat
   construction" and was used as a proof. It is false — the trie can use MORE
   NFA states than flat, by one extra N_EPS per branch ending exactly at a
   node (`bb|a|ba` is 10 vs 8). The excess is additive, not multiplicative
   (aggregate ratio 0.999 over 1212 sampled patterns), so D10's cap arithmetic
   is unaffected, but the bound is flat + O(branches), not flat.

2. Branches merge only on bit-IDENTICAL class bitmaps, but two DISTINCT groups
   can still OVERLAP, and overlapping groups are not mutually exclusive:
   `[ab]p|[bc]x|[ab]xy` on "bxy" is [0,2), but `[ab](?:p|xy)|[bc]x` is [0,3).
   Guard: reorder groups only within a maximal RUN of contiguous branches
   whose distinct bitmaps are pairwise disjoint; where a run ends, chain the
   runs in index order (sound for the same reason the eligible/ineligible run
   rule is).

   CORRECTION (R3 critic): the first version bailed the WHOLE node to the
   unfactored construction on any overlap, and D9 called that "conservative
   rather than wrong". It is not wrong, but it is a CLIFF — one branch of a
   3600-word keyword list beginning `[ab]` instead of a literal took compile
   time from 0.80 s to 44.9 s, losing the entire M2.8 win to one character,
   and KEYWORD-SCALE could not see it because its word list has no classes.
   Run-splitting recovers it (0.82 s; the 2%-classes variant 35.6 s -> 2.9 s),
   and the disjointness test is now an exact O(n) running-union check rather
   than an O(ng^2) one that additionally gave up outright above 64 groups.

Mixed lists are handled by trie-ing only maximal runs of CONSECUTIVE eligible
branches. CORRECTION (R3 critic): the invariant this rests on is not the loose
"first matching branch in index order wins" — D3 keeps lower-priority threads
alive past an accept precisely so a later higher-priority one can override.
The property a run fragment must have is stronger: its DFS leaf order,
restricted to any set of branches that can match at one start, must equal
index order. The composition step is sound given that, but it is CONDITIONAL
on rule 2 being right rather than an independent argument.
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
loop iterations, leaving only a split's preferred branch recursive.

CORRECTION (R3 critics, twice): "verified at -O0 on a 1,000,000-branch
alternation" is true but VACUOUS as evidence about `clo_visit` — at 1M branches
the build fails on the NFA cap during CONSTRUCTION and never computes a
closure. The largest alternation that actually reaches the DFA is ~65k
branches. The conclusion still holds (nothing segfaults at -O0), but the
experiment quoted did not demonstrate it. And the entry's own "revisit-when"
is already answered: deep PREFERRED-branch nesting is bounded by the parser's
250-deep group-nesting cap (src/parse/parse.c), which is the guard to cite.

Still open, and now tracked as DD-10: `compile_ast` and `clo_visit`'s t1 edge
have no stated frame budget. A 400-nested-branch-point alternation needs
~192 KB — fine on an 8 MB main thread, not on a musl 128 KB one.

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

### D11 addendum — 2026-08-09 (R3.2 critic): probed to 25.8M comparisons, held, and three claims corrected

R3.2's remaining unprobed item was the EOL vs non-EOL ordering asymmetry. It has
now been swept hard: **25,834,470 oracle-checked comparisons against PCRE2
10.46 across 6432 patterns, 0 divergences** on the shipped compiler, including
under ASan+UBSan with exact-size subject buffers. Boundaries covered: empty
subject, single `\n`, all-`\n` subjects, every subject of length <= 5 over
{a,b,=,\n}, every startpos including `startpos == n`, and subjects ending in
`\n`. The emitted C was also checked against the prose on all four halves
(forward/reverse x EOL/non-EOL) and matches it.

**Both directions of the asymmetry were sabotage-tested**, via a switch that
moves ONLY the order and is byte-identical to the shipped compiler when neutral:

- Forcing the NON-EOL order onto the EOL path: **238,144 divergences**. The rule
  is confirmed by a far wider margin than the 53 divergences cited above, e.g.
  `ab[a-z]*b$|[^\n]*$` on "ba\n" gives [3,3) where PCRE2 gives [0,2).
- Forcing the EOL order onto the NON-EOL path: **0 divergences** over 7.85M
  comparisons. So the EOL-safe order is semantically fine everywhere and the
  asymmetry buys nothing but speed.

**CORRECTION 1 — the speed claim rests on ONE pattern family, not on the
non-EOL path in general.** Only `[01]*1[01]{8}` shows the loss, and it
reproduces solidly: 156-159 -> 87-91 MB/s, non-overlapping ranges over 9+7
interleaved trials at two different times and at three -O levels. On the other
five throughput cases the EOL order measured a tie or slightly faster (needle
1.018, `a*b` 1.041, `a(b|c)+d` 1.015, bitmap 0.996, `=[^\n]*!` 1.040,
consistently signed across 7 interleaved trials each).

Be careful with those five numbers, and this entry originally was not: they were
taken at 1-min load 4.5-9.7 against tests/bench's own LOAD_LIMIT of 6.0, and the
critic could not re-run them on a quiet box (it reached load 26.7 by session
end). 1.5-4.1% is inside the band where this box's load matters, so the positive
claim "the EOL order is FASTER there" is SUGGESTIVE, not established. What IS
established is the negative, and it is all the correction needs: the EOL order
is not materially SLOWER on (a)-(e). So "both orders are correct, only one is
fast" is true of case (f) and is not a general property. Keep the asymmetry; do
not defend it as a broad win. Re-measuring the five on an idle box would settle
it.

**CORRECTION 2 — the 43% is a gcc optimisation-level artifact, not an
algorithmic cost.** Same two matchers, same subject, gcc 15.2.0: `-O0` 54.3 vs
53.9 (no gap), `-O1`/`-O2`/`-O3` ~156 vs ~90 (gap), **`-Os` 90.7 vs 91.7 (no
gap — the "fast" order is not fast at -Os)**. The decision still stands, since
the harness builds at -O1 and the bench at -O2, but D11 presents the gap as a
property of the loop and it is a property of THIS gcc at THESE levels. A
different compiler, or an embedder building at -Os, gets the slow number from
both orders.

**The load-bearing premise was never written down: ACCEPT MONOTONICITY.** Over
6432 patterns analysed, no DFA state anywhere has plain accept 1 with a
NON-accepting EOL variant. That is what makes "evaluate the accept once, at the
position the skip lands on" safe, and it is the premise the whole ordering rule
depends on. It follows from `clo_visit`: the EOL closure explores a superset of
the plain closure's edges in the same DFS order, so it reaches `N_ACCEPT`
whenever the plain closure does. D11 argued only "same state, therefore same
accept bit" — true for the positions a skip PASSES, and silent about the
position it LANDS on, which is the one position that can take a different view.
That is the same shape of gap as the M2.12 ordering bug (a proof about the
position before a skip, saying nothing about where the skip lands).

**Guard coverage, measured.** Deleting the reverse `pp + 1 < n` entry guard is
caught by 3 cases in the pre-existing corpus and by 14 in the mid-pattern-`$`
block added for it (17 across tests/base/). The critic reported that NO .rxt
case could catch it; that was overstated, and the corrected numbers are above.
Its underlying point holds: on a family where `$` always ends a branch, guard
removal gives 0 divergences over 7.7M comparisons, because no REVERSE skip
state carries an EOL variant in that shape. Both order sabotages are also
caught by tests/codegen/run_codegen_tests.sh, so the asymmetry has a structural
test as well as a behavioural one — rare for a performance decision here.

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

### D13 addendum — 2026-08-09 (R3.2 critic): probed against the REAL emitter, and HELD

R3.2 carried "whether D13's dispatch micro-benchmark represents the real
emitter shape" as unprobed. It has now been probed, and the answer is: **the
benchmark does NOT represent the emitter, and the decision it supports is right
anyway — for a reason D13 does not give.**

**The benchmark is gone and never existed here.** D13 cites "scratchpad
`dispatch.c`". CONFIRMED (`git log --all -S "dispatch.c"`): the only occurrence
of that filename anywhere in this repository's history is the D13 prose above
that introduced it. The measurement was never checked in, so it can never be
re-run — only re-derived, which is what this addendum is. A decision-critical
measurement that lives in a scratchpad is a measurement with a half-life.

**Structural gaps between a 6-state single loop and what emit_dfa.c emits:**
every real match runs TWO scans (forward for the end, non-pruning reverse for
the start), each with its own dispatch loop; each iteration also does
`if (facc[st]) last = pos;`, a `st == fs` prefilter branch and up to four
skip-state branches BEFORE the transition step; and the transition is
`ftr[st*ncls + fcls[s[pos]]]`, an extra dependent load through the byte
equivalence-class table that a 6-state toy has no reason to model. Most
importantly, for prefilter-eligible patterns most bytes never reach the
dispatch loop at all — the prefilter and skip loops exist precisely to avoid
it — so a synthetic loop that dispatches on every byte measures the path the
emitter works hardest to skip.

**Re-derived on real emitter output.** A critic transformed emit_dfa.c's OWN
generated C into a computed-goto equivalent (emitter untouched, `cls[]` lookup
preserved on both sides, results verified identical before timing) for three
patterns at real bench flags, median of 9 interleaved runs:

| pattern | states | random input | predictable input |
|---|---|---|---|
| `[01]*1[01]{8}` | 768, ncls 3, memchr | 0.91 | 2.75 |
| 50-word alternation | 225, ncls 27, bitmap | 0.42 | 2.87 |
| 300-word alternation | 2915, ncls 27, bitmap | 0.35 | 3.07 |

(goto/table; >1 means goto faster.) This reproduces the R3 self-correction —
predictability, not size, is the crossover variable — at realistic scale rather
than on a 6-state toy, across a 4x range of both ncls and state count, with the
direction never flipping. Treat the exact ratios as approximate: the critic
disclosed that box load ran from 0.44 to 14.49 during its runs, which under
D14's own rule would be INCONCLUSIVE. The effect sizes are far larger than the
per-arm spreads (<=1.43x), so direction is credible; precision is not claimed.

**The decisive argument is compile time, and D13 does not make it.** D13
arbitrates purely on runtime. But emit_dfa.c's own header and D7 chose tables
for ENG_UNANCH because of R1 A-3's superlinear gcc time, leaving runtime open
only for SMALL DFAs. Verified independently on a quiet box (load 0.95, gcc -c
only, so no link-time dilution):

| pattern | table | computed goto | ratio |
|---|---|---|---|
| 50-word alternation (6075 entries) | 0.07 s | 0.77 s | 10.9x |
| `[01]*1[01]{8}` (2304 entries) | 0.06 s | 2.22 s | 35.6x |
| 300-word alternation (78705 entries) | 0.29 s | **91.08 s** | **319x** |

The critic measured 5.7x / 16x / 210x on full builds; measuring compile only
removes constant link overhead and the ratios grow. Either way: for large
keyword/dictionary alternations — a common real use of this compiler, not an
edge case — computed goto is disqualified on compile time alone, before the
runtime question is reached.

**Corrections to the text above:** "Six states is about as small as a useful
DFA gets, so there is no crossover to arbitrate" overstates what was shown. The
DIRECTION never flips, but the magnitude on random input moves with ncls (0.91
at ncls 3 vs 0.35-0.42 at ncls 27), so 6 states is not representative along
that axis. And D13 reads as though runtime settles the question; it does not,
and for the large-alternation case compile time is both dominant and more
decisive.

**Revisit-when (widened):** was "long predictable state runs that skip loops
cannot cover". Add: this is now confirmed safe for LARGE KEYWORD/DICTIONARY
ALTERNATIONS WITH A WIDE FIRST-BYTE ESCAPE SET, which get bitmap prefilters
that skip almost nothing (nearly every byte is an escape byte) and therefore
run the disputed dispatch loop on every byte — the case where the question
actually bites, measured here, and where table wins on both axes.

## D14 — 2026-08-09 — `make bench` distinguishes "clean" from "not measured"

R3 critic finding against my own M2.9/D12 work. The LOAD_LIMIT downgrade added
earlier that day reported a budget miss as INCONCLUSIVE on a busy box — which
was right — and then exited 0, which was not. A build with a 3.4x/68x/5.5x
regression exited GREEN whenever the box was loaded, and with the default limit
at cores/2 against observed loads of 5-24, loaded was the normal case rather
than a corner. The guard against flakiness had become a guard against detection.

Exit codes are now three-valued: 0 = gated and clean, 1 = gated and failed,
2 = NOT GATED (one or more budgets inconclusive). Automation cannot read "I
could not measure" as "nothing regressed", and a human sees it in the summary.

Known limitation, stated rather than fixed: the load average is sampled ONCE
before a multi-minute run, so it describes the load before measurement, not
during it. Revisit-when: budgets start flapping between 0 and 2 on a box whose
load changes mid-run.

## D15 — 2026-08-09 — every optimization needs a bench case that EXERCISES it

R3 critic finding, and the sharpest one of the checkpoint. Deleting the bitmap
half of the start prefilter — keeping only the memchr fast path, a plausible
"simplify the special case away" edit — costs ~1.5x on multi-first-byte
patterns (452 -> 303 MB/s here, ~20% on the critic's own subject), and passed
`make test`, `make bench`, the python oracle, the differential fuzzer AND
`gate.sh`. Five nets, all green, on a real regression.

Root cause: all four THROUGHPUT patterns had exactly ONE escape byte, so every
one of them took the memchr branch. The feature was half-covered and D12's
"sabotage-validated" claim covered only that half. `gate.sh` missed it too
because emitted code is byte-identical for 7 of 9 compare cases, and one of the
two that changed measured FASTER (it is an early-exit case — see below).

Case (d), `(alpha|beta|gamma|delta|epsilon)` over an 8 MB alphabet with no
'a', now covers the bitmap branch. Its budget is deliberately tighter than the
others' /1.75: the regression it guards is only ~1.5x, so a 1.75x margin would
let exactly this through again. Measured spread on it is 1.03-1.08x, among the
tightest in the suite.

The general rule this establishes: a sabotage validation must disable the
SPECIFIC branch under test, not the feature that contains it, and a feature
with two code paths needs a case that reaches each. Revisit-when: any new
scan-avoidance path is added.

## D16 — 2026-08-09 — behaviour-preserving optimizations get an EQUIVALENCE check, not just a signature check

`tests/codegen/` was built on the premise that a behaviour-preserving
optimization can only be guarded by asserting its SIGNATURE appears in the
emitted C — a skip table exists, `start_max = 0` is present, a table is under N
entries. That premise is what led the M2 journal to conclude M2.8 (the
alternation prefix trie) was not structurally testable at all, since the trie
changes the NFA and the NFA is not an output.

That was wrong, and an R3 critic showed why. The trie is required to be
OUTPUT-PRESERVING: subset construction plus minimization must erase the
difference completely. So building a second compiler with the optimization off
and diffing the emitted C is a direct test of the optimization's SOUNDNESS,
across as many patterns as you care to generate, with no subjects and no gcc.

Decision: when an optimization is supposed to be output-preserving, guard it
with an equivalence diff against a reference build, and prefer that to
signature greps. `-DPCREC_NO_TRIE` is the switch for M2.8;
`tests/codegen/run_trie_identity.sh` is the check. 500 patterns in ~4 s.

Why this is worth a decision entry rather than just a test: the detection power
is not comparable to what we had. Measured, with the recipe recorded in
tests/codegen/CLAUDE.md so every number here can be replayed:

| sabotage | .rxt corpus | identity @200 | identity @500 |
|---|---|---|---|
| disjointness guard off (`return n` first in `disjoint_run_len`) | 2 cases | 21 | 64 |
| rule 1's accept split hoisted instead of index-partitioned | 16 cases | 38 | 94 |

CORRECTION (R3 guards critic F6/F7). The first version of this entry said "~14
patterns in 500" and "rule 1 off -> 132 of 200". Both were wrong, in different
ways, and both are the failure mode this project keeps repeating:

- "14 in 500" was never measured. It was the original R3 critic's figure for a
  DIFFERENT corpus, copied across without re-running. The real number is 64 —
  the check is 4.5x stronger than it was advertised as.
- "132 of 200" came from a contaminated tree. The sabotage loop that produced it
  used `git checkout` to revert between runs inside a tarball copy that was not
  a git repo, so the failure was swallowed by `|| true` and rule 1's sabotage
  was applied ON TOP of rule 2's. 132 is the two-guards-off number. Worse, the
  natural rule-1 sabotage (skip the accept split, leave everything else) makes
  rule 2 read `seq[depth]` for an item with `len == depth` — a 32-byte arena
  over-read — so its count is not stable between builds (171 here, 176 for the
  critic). The citable form is the memory-safe one in the table, which removes
  the accepts from the list but hoists them instead of partitioning around each.

The lesson is the recipe, not the number: a sabotage figure without the exact
edit that produced it cannot be checked, and this one was wrong for two
independent reasons before anyone tried.

The trap, and the non-optional part: an equivalence check is vacuous if BOTH
builds have the optimization off. Then everything agrees and the script
certifies a deleted optimization — the exact "guard that cannot fail" shape R3
found twice in guards written the same day. So every equivalence check MUST
carry a positive control proving the shipped build still does the thing.

AND THE CONTROL MUST FIRE INSIDE THE CORPUS'S OWN RANGE. This is the part the
first version got wrong, and it is the more useful half of the rule. That
version had ONE control, at 256 branches, while every generated pattern had
3..8. A critic broke it in one clause —
`elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)`, the shape of a
plausible "only factor when it is worth it" heuristic — and left the identity
check, the control, `make bench`'s KEYWORD-SCALE budget and the entire
`make test` suite green with M2.8 effectively deleted for every hand-written
pattern. The control proved the trie fired for one 256-branch pattern; nothing
proved it fired for anything a user would write.

There are now three controls, at 4, 8 and 256 branches. Each is deterministic
rather than timing-based: sized so the two builds fail at DIFFERENT STAGES, with
the stage visible in the error text. The two small ones are `^`-anchored on
purpose — without `^` the engine also builds a reverse machine, a shared PREFIX
barely factors in reverse, and the control degenerates to unfactored/unfactored.
Validated against both sabotages: with the trie disabled outright, identity
passes 200/200 and only the controls fire; with the critic's `nbr >= 100`
threshold, the 4- and 8-branch controls fail and the 256 one still passes.

Cost: the check builds a second compiler at -O0 on every `make test` (~0.4 s).
Accepted. Revisit-when: another output-preserving optimization lands (the
reverse machine's unconditional factoring, F5, is the obvious next one), or the
NFA/DFA caps move and the positive control needs re-sizing.

## D17 — 2026-08-09 — the compare gate's margin is per case, derived from that case's own spread

`gate.sh` used one global margin of 0.70 for all nine cases, which fires only
below 1.43x. R3's claims critic pointed out the consequence: M2.10's 27%
regression could NOT have been caught by this gate, and the review had credited
it with catching that case anyway. Only the 43% one was in range.

A single margin has to be sized for the noisiest case in the matrix, so every
quiet case is gated far more loosely than its own measurement supports —
spreads across the matrix run 1.03x to 1.49x, a 15x difference in how much
headroom each case actually needs.

Decision: `floors.tsv` carries a fourth column, a per-case margin, and
`UPDATE=1` derives it from that case's observed trial spread as

    margin = clamp(1 / (spread * 1.05), 0.70, 0.90)

The floor keeps a noisy case no looser than the old global default, so this is
never a regression in strictness. The CEILING is NOT derived from the spread: a
single run's within-run trial spread is a sample, not a distribution, so the
1.05 safety factor pays for that gap and the ceiling caps how far one lucky run
can tighten the gate.

CORRECTION (R3 guards critic F12): the ceiling was justified here, in gate.sh
and in floors.tsv by "this box's noise floor is ~10% even at median-of-7", and
THAT NUMBER IS NOT BACKED BY ANY MEASUREMENT IN THIS REPOSITORY. The three runs
the repo does contain (floors.tsv, results-…-20260809, results-…-20260809-2)
move run-to-run by <= 3.3% on eight of the nine cases — a third of the claimed
floor — and the one case that moves 26% is the latency case, which sits at the
0.700 FLOOR and gets no benefit from the ceiling argument at all. Writing an
unmeasured constant into the decision entry whose subject is not gating on
unmeasured constants is the joke telling itself.

The ceiling STAYS at 0.90 for now, and deliberately: three runs is a thin basis
for tightening a gate, and tightening on it would repeat the error rather than
fix it. What changed is that the justification is now the recorded data plus an
admission of over-conservatism, instead of a number nobody measured. Cases a-h
would tolerate 0.95 with 1.5-3x headroom over their observed movement, and
[R3.7] carries collecting enough runs to earn it.

Validated: a uniform 27% regression fails 8 of 9 cases where it previously
failed 0 (independently reproduced by a critic). CAVEAT, and it belongs next to
the headline: case (e) fails that test by only 3.4%, and its margin came from
one run's spread of 1.26x — the noisiest throughput case in the matrix. Had that
run measured 1.31x, the derived margin would catch 1.375x rather than 1.32x and
the headline would read "7 of 9". The figure is a property of one sampled spread
of the two noisiest cases, not of the design. At 20% the result is already 6 of 9.

Each run now also prints, per case, the smallest regression its margin can
actually fail on, and a summary line naming the weakest case in the matrix.
That number was always computable and for two checkpoints nobody computed it —
which is precisely how the gate came to be credited with a catch it could not
make. A guard should state its own blind spot in its own output.

Revisit-when: BENCH_TRIALS rises (a tighter median justifies a higher ceiling),
the matrix moves to different hardware, or a case's recorded spread stops
matching what it measures in practice.

## D18 — 2026-08-09 — hyperspecialization: options are compiled away, and every option dimension must EARN its engine

Stated by Frank 2026-08-09 as perspective that should have been set at the
start, and recorded here because it resolves trade-offs the earlier entries
left open.

**Priority order, explicit.** pcrec's reason to exist is SPEED OF EXECUTION
first, speed of COMPILATION second. Other regex libraries offer other benefits;
this one offers those. Where a decision trades generality, binary size, or
elegance against execution speed, execution speed wins unless something else
is stated. D12/D15's insistence on measured budgets is downstream of this.

**Hyperspecialization is the mechanism.** Anything fixed at compile time is
compiled AWAY, never tested at run time. If case-insensitivity is given as a
pattern option, the whole compilation assumes it — no runtime flag, no branch
in the hot loop. Same for encoding. The generated matcher is a bespoke tool for
exactly one configuration, which is the same principle that already makes the
whole project an AOT compiler rather than an interpreter.

**THE INTERFACE TAKES A SET PER DIMENSION, and the product is over those
sets.** This is the load-bearing shape and it is easy to get subtly wrong
(Frank corrected two drafts of this paragraph). It is NOT a boolean
"open/closed" per option. The caller names, for each dimension, the set of
values it wants that compilation to serve:

    case:     {insensitive}                -> |set| = 1
    encoding: {ascii, utf8}                -> |set| = 2
                                              => product = 2 backends

A dimension whose set has ONE element is fully specialized and compiled away —
including when that element is not the default. Asking for case-insensitive
ONLY is not "opening" case-sensitivity; it is hyperspecializing to the
insensitive point, with no runtime flag and no dispatch, exactly as if the
caller had asked for sensitive only. Both are singletons; only the specialized
value differs.

A dimension is an AXIS only when its set has two or more elements, and the
cartesian product is over those sets alone — never over the option space pcrec
happens to support. So the product is small because it is requested small, not
because we prune it afterwards. A caller naming a singleton everywhere gets
exactly one engine.

**At EXECUTION time the caller supplies the specific value for each PLURAL
dimension, and the dispatcher selects the matching engine.** Singleton
dimensions do not appear in the runtime signature at all — they were compiled
away, so there is nothing to pass. The generated entry point therefore carries
exactly one selector per plural dimension and nothing else:

    case {insensitive}, encoding {ascii, utf8}
      -> rx_search(s, n, startpos, m, RX_ENC_UTF8)      /* one selector */

    case {sensitive, insensitive}, encoding {ascii, utf8}
      -> rx_search(s, n, startpos, m, RX_CASE_CI, RX_ENC_ASCII)

    everything singleton
      -> rx_search(s, n, startpos, m)                   /* today's signature */

Two properties this has to preserve, and they are the whole point:

1. **Dispatch is once per SEARCH CALL, never per byte.** Selecting the engine
   is a table index or a switch on a small tuple, resolved before the scan
   starts. A selector that reached the hot loop would reintroduce exactly the
   runtime branch hyperspecialization exists to remove, and would make the
   plural case slower than compiling twice.
2. **The all-singleton case pays NOTHING for the mechanism.** No dispatcher, no
   indirection, no extra parameter — the entry point IS the specialized
   function, byte for byte what pcrec emits today. The general mechanism must
   not tax the common case; that would invert D18's own priority.

Worth building both surfaces, because they cost the same: a NAMED entry point
per combination (`rx_search_ci_utf8`) alongside the selector-taking dispatcher.
A caller who knows its configuration statically calls the named one and pays no
dispatch at all — even an indirect call — while a caller choosing at run time
uses the dispatcher, which is then a thin switch over the same named functions.

Consequence for the API, and it is not the shape `pcrec_options` has today:
the option fields are currently scalars (`int encoding`), which can express
"utf8" but not "{ascii, utf8}". A set-valued request surface is a real design
change, and the generated searcher contract in lib/pcrec.h — currently a fixed
`<prefix>_search(s, n, startpos, m)` — becomes a signature that DEPENDS on
which dimensions are plural. That is squarely DD-3's territory (generated-API
versioning/compat policy, already marked "before M3").

**And the test that keeps that from exploding: every dimension must EARN its
place.** Before a dimension becomes a product axis, measure whether
specializing to it actually buys anything. A dimension can fail that test three
ways, and all three are wins:

1. **It folds into the front end.** The option changes what the automaton is
   built FROM, not how it runs, so there is one engine and no axis.
2. **It is free at run time.** Handling it with a runtime check costs nothing
   measurable, so a shared engine is strictly better than two.
3. **It is a wrapper.** The option is a shell around an unchanged backend.

Only a dimension that survives all three becomes a real axis. The product is
then over the SURVIVORS, which is what keeps 4 options from meaning 16 engines.

**Predictions, to be tested rather than assumed** — recorded now so the results
can be checked against them:

- **ASCII case-insensitivity: predicted to FOLD (case 1), completely.** The DFA
  already runs on class bitmaps over byte equivalence classes; folding is
  `bitmap |= swapcase(bitmap)` at class-construction time. Zero runtime cost,
  no second engine, and byte-class merging may even SHRINK the tables. If this
  holds, DD-1 is not an engine question at all for the ASCII tier.
- **Encoding ascii/utf8: predicted to FOLD (case 1).** APPROACH §4 and §10
  already commit to byte-wise UTF-8 automata with "no runtime decode step in
  the hot path", explicitly so that "ASCII and UTF-8 share one DFA emitter".
  Unicode classes become byte-range trees at construction time. If that holds
  as built, encoding is a front-end axis, not an engine axis.
- **Streaming: predicted NOT to be a wrapper (fails case 3).** This is the one
  where evidence already contradicts the optimistic answer, and M3.0 exists
  because of it: the D7 engine finds the match END forward and then rescans
  BACKWARD for the start, over bytes a stream may no longer hold. That is not
  a shell around an unchanged backend; it is a constraint on the backend.
- **Anchoring: an EXISTING axis that has never passed this test.** ENG_UNANCH
  vs ENG_ATTEMPT is already a cartesian split in the shipped compiler, and it
  exists for an IMPLEMENTATION reason — the reverse machine cannot check `^`
  at pp == 0 — not because anyone measured a per-start attempt loop to be
  faster. By this criterion it is an unjustified dimension, which is exactly
  what DD-7 was opened to close. Note the cost is not hypothetical: `^` on only
  SOME branches is the known slow shape (D8).

**SELECTION AND EXECUTION ARE TWO STEPS, and selection is itself generated.**
The caller resolves the engine once and then executes it one or more times, so
selection cost is amortised over every subsequent search rather than paid per
call. And because the dimensions are known at COMPILE time, the selector is not
a general-purpose routine — it is emitted specialized to the product that was
actually requested. If the only plural dimension is case sensitivity, selection
is literally `if (ci) return engine1; else return engine2;`. No table, no
registry, no lookup by name. A caller that already knows its engine skips the
step entirely and calls the named entry point directly.

**Multi-engine output: the naming constraint, measured rather than assumed.**
More than one engine in one source file means symbols must not clash. Checking
what the emitter actually produces (`.*=.*$`, 15 distinct emitted identifiers):

- **12 of them are FUNCTION-LOCAL statics** — `fcls ftr facc fev fs<N> rcls rtr
  racc rev rs<N> first` — declared inside `<prefix>_search`'s body. Two engines
  in two functions do not collide on any of these, and they need no change.
- **Only three are file-scope**: the `<prefix>_span` typedef, and the
  declaration and definition of `<prefix>_search`.

So the work is much smaller than "namespace everything": emit `<prefix>_span`
ONCE and share it, and give each engine a distinct function name. The
named-entry-point scheme (`rx_search_ci_utf8`) supplies exactly that, so the
naming answer and the API answer are the same answer.

*Confirmed when OS-0b landed (2026-08-09):* the parenthetical above — emitting
the typedef twice declares two distinct anonymous struct types rather than
benignly redefining one — was written from the standard and is correct. gcc
says `error: conflicting types for 'rx_span'; have 'struct <anonymous>'`, under
-std=gnu11 and -std=c99 alike. It is now asserted by a test that compiles a
duplicated-typedef file and requires the build to FAIL, so the rule has a
demonstration rather than a citation.

**One consequence for the tests, worth knowing before it bites.**
`tests/codegen/run_codegen_tests.sh` hardcodes symbol patterns (`rx_ftr[`,
`rx_fs[0-9]+\[256\]`, ...). With one engine per file those are unambiguous.
With several, a grep for `rx_fs[0-9]+\[256\]` can be satisfied by ANY engine in
the file, so a check that means "this pattern emits a skip table" silently
degrades into "some engine here does" — it gets WEAKER without ever failing,
which is this project's signature failure mode.

*Done in OS-0b (2026-08-09), ahead of anything emitting two engines.* The count
in the sentence above was originally "9 symbol patterns" and was wrong: it is
19 grep sites across 11 generated files, all now scoped to one engine's body,
extracted by entry name. The scoping is controlled by a two-engine fixture the
suite builds and compiles, which requires a scoped grep to attribute a skip
table to the engine that has one and not to the engine that does not — so a
broken extractor fails rather than certifies. See tests/codegen/CLAUDE.md for
the five validated sabotages.

**Where the dispatch cost would show up, if it shows up at all.** The compare
matrix already has case (i), a short-subject per-call-overhead regime at ~70
ns/call. That is the case where an indirect call and lost inlining would be
measurable; the throughput cases would not see it. So it is already
instrumented, and it is the case to watch when the selector lands.

**SUPERSEDED IN PART BY D20:** the product machinery is a separate, OPTIONAL
MODULE layered on the compiler — an engine FINDER driving an engine GENERATOR
that knows nothing about dimensions. Read D20 before implementing any of this;
in particular the set-valued request surface belongs to the finder and never
enters `pcrec_options`, which correctly stays scalar.

**Revisit-when:** a new option is proposed (multiline, dotall, ungreedy,
`\G`), or any of the four predictions above is measured. Each measurement
belongs in the plan step for its dimension, with the number attached.

## D19 — 2026-08-09 — thread-safety: usable FROM threads, never threaded

Requested by Frank 2026-08-09, with the scope stated sharply and worth keeping
that way: **neither the compiler nor the generated matchers are internally
parallel, and there is no plan for them to be.** No worker pools, no parallel
subset construction, no threads in generated code. The requirement is only that
a caller may USE them from a multi-threaded program:

- concurrent `pcrec_compile()` calls on different patterns in different threads;
- concurrent `<prefix>_search()` calls against the SAME generated matcher.

**Audited state (measured 2026-08-09, not assumed). Both properties already
hold.**

*Generated code* — for a representative pattern the emitter produces 12
statics and every one is `static const` with a constant initialiser, so they
land in .rodata and are initialised at load time: no lazy initialisation, no
guard variable, nothing to race on. There is no `malloc`/`free`, no `errno`, no
locale dependency, and no non-reentrant libc call. All working state (`pos`,
`st`, `last`, `est`, ...) is stack-local, and the only write through a caller
pointer is `*m`. Reentrant by construction.

*Compiler library* — there is NO file-scope mutable state anywhere in `src/`.
Every file-scope static is either a function or `static const EscMod
esc_modules[]`. `Ctx` — including its `jmp_buf` — is a LOCAL of
`pcrec_compile`, so the setjmp/longjmp error path is per-call and per-thread.
All per-build state is arena memory owned by the Job.

**Correction to R3 while auditing this.** The R3 review recorded that "the
generation counter is file-scope while the marks are per-build arena memory".
It is not file-scope: `gen` is a member of `Marks`, and `Marks marks` is a local
of `pcrec_build_dfa`. The hazard the review described (the wrap path must clear
the CURRENT build's array) is real and the code handles it correctly — but the
scope claim was wrong, and had it been TRUE it would have been exactly the
thread-safety defect this entry is about. A wrong description of correct code
is still worth fixing, because the next reader reasons from the description.

**Why this gets mechanized rather than documented.** Thread-safety here is the
same shape of invariant this project has repeatedly lost: true by construction,
invisible to every existing test, and destroyable by a plausible one-line
change that passes everything. Concretely, each of these would break it and
none would fail a current test:

- a memoisation cache or lazily-built table in emitted output — one `static`
  that is not `const`;
- a scratch buffer hoisted to file scope to avoid a stack allocation;
- an `errno`-setting or locale-dependent libc call reaching generated code;
- a statistics or diagnostics counter added at file scope in the compiler;
- and, under D18, a selector that CACHES its choice in a global. The two-step
  "resolve the engine, then execute it many times" shape must keep the resolve
  step pure — the caller holds the result, the library does not.

**Stack is part of this, and it is already open.** Running under threads is not
only about data races: a thread stack is typically far smaller than the main
thread's 8 MB, and musl's default is 128 KB. DD-10 (unbounded C-stack recursion
in `compile_ast` and `clo_visit`'s t1 edge — a 400-nested-branch-point
alternation needs ~192 KB) is therefore a THREAD-SAFETY item and not merely a
robustness one, and this requirement raises its priority. The existing
`tests/cli` case-8 budget (9000 branches under `ulimit -s 512`) is the right
shape; what it lacks is a sibling that binds `compile_ast`.

**Revisit-when:** generated code ever needs mutable state (a captures buffer in
M4 is the first candidate — it must be caller-provided or stack-local, never
static), or the library gains anything at file scope.

## D20 — 2026-08-09 — the engine GENERATOR and the engine FINDER are separate modules; the finder is optional

Refines D18 (Frank, 2026-08-09). The cartesian-product machinery is a MODULE
layered on top of the compiler, not a change to it.

- **Engine generator** — what pcrec is today. Given a fully-CLOSED option set
  (every dimension a singleton) it emits one engine. It knows nothing about
  dimensions, products, selection or dispatch. Its only obligation to the layer
  above is to respect constraints on how the engine is emitted — above all
  NAMING, so several engines can coexist in one file (OS-0b).
- **Engine finder** — optional. Given the SETS, it drives the generator once
  per point of the product and emits the selector over the results.

Three consequences, and the third is the one that changes the plan:

1. **You pay for the product only if you use it.** No dispatcher, no selector,
   no extra symbol when nobody asked for one — which is D18's "the
   all-singleton case pays nothing", now true by construction rather than by
   care.
2. **The core API never becomes set-valued.** OS-0 was written as "`pcrec_options`
   holds scalars and cannot express {ascii, utf8}". Under this split it never
   needs to: scalars are exactly right for a generator that only ever compiles
   one point. The set-valued surface belongs to the finder module and lives
   entirely there. That deletes the API-change half of OS-0 and shrinks what
   has to be settled before the OS dimensions can be worked.
3. **The finder can be built MUCH later, or never.** Because the coupling is
   one naming constraint, nothing about it has to be decided now. Frank's
   point: use build notes and experience to determine (a) which dimensions
   would actually benefit and (b) whether the feature is needed at all. A
   dimension that folds (D18 case 1) never reaches the finder, so if the
   predictions hold the finder may have no customer for a long time — which is
   a good outcome, not a stalled one.

**Revisit-when:** a dimension survives D18's earn-its-axis test with a
measurement behind it, i.e. the finder acquires its first real customer.

## D21 — 2026-08-09 — optimization happens in WAVES, in this order: algorithmic, then profiled code, then compile time

Frank, 2026-08-09. Not a milestone but a shape to apply at the appropriate
points, and the ORDER is the decision:

**A. Algorithmic search optimization first, and RESEARCH IS PART OF IT.**
pcrec is open source and pulling from other open-source work is the point, not
a compromise. Before hand-tuning anything, survey what the good engines do that
we do not. Candidates worth investigating, recorded as leads rather than
commitments:

- *rare-byte prefilter selection* — pcrec picks memchr only when there is
  exactly ONE escape byte and otherwise falls to a bitmap; ripgrep/Hyperscan
  choose the RAREST byte by frequency table, which is a different and usually
  better decision. Our case (d) bitmap path is the one this would attack.
- *memchr2/memchr3* for 2-3 escape bytes, the gap between our memchr and
  bitmap paths.
- *multi-byte literal search* — Two-Way/Boyer-Moore or memmem for literal
  prefixes, instead of scanning to a single byte then stepping.
- *Teddy / SIMD multi-pattern prefilter* (Hyperscan, used by rust-regex) for
  the keyword-alternation shape M2.8 already targets.
- *reverse-inner and suffix literal* optimizations (rust-regex) — pick a
  literal from the middle or end when the prefix is weak.
- *shift-or / bitap* bit-parallel simulation for short patterns.
- *transition-table compression* (row displacement) — we already do alphabet
  compression via byte equivalence classes, but not table packing.

**B. Then profiling for code-level optimization.** Only after the algorithm is
right, because profiling a bad algorithm optimizes the wrong loop. This is
where D13's finding lives: throughput here is dominated by transition
PREDICTABILITY, so profile-driven work should target branch behaviour and
memory layout rather than instruction count.

**C. Compile-time optimization last.** It is the second priority (D18) and
optimizing it before execution speed is settled risks trading the primary goal
for the secondary one. Note also that M2.9's compile budgets measure only
pcrec's half; after M2.8 gcc is the LARGER half (0.79 s vs 1.36 s at 3600
words), so a compile-time wave has to include what gcc does with our output,
not just what we do.

**Revisit-when:** each wave is scheduled; record the survey results even for
techniques rejected, because "we looked at Teddy and it does not fit because X"
is worth as much as adopting it.

## D22 — 2026-08-09 — adversarial patterns are OUT OF SCOPE; correctness is not

Frank, 2026-08-09, and it resolves a question the earlier entries left drifting.

**pcrec does not have to be hardened against deliberately hostile patterns.**
It is a compiler that a developer runs over patterns they control, ahead of
time. It is not a service accepting untrusted regex from the internet. We check
what we can cheaply, but contorting the design to survive an attacker is not a
goal and should not be traded against execution speed (D18).

What this DOES and does NOT change:

- **DD-2 (ReDoS stance, VM match/step limits) is downgraded.** With the M4 VM
  it stays worth having a bound so a pathological pattern fails honestly rather
  than hanging, but it is a robustness feature, not a security boundary, and it
  should not be designed as one.
- **The NFA and DFA caps stay exactly as they are.** They already do the right
  thing — a clean, attributable error instead of an OOM or a hang. That is good
  engineering for a legitimate too-big pattern, and it is enough.
- **The stack budgets STAY, and their justification changes.** trie_build's
  256-frame budget and DD-10/TS-4's unbounded `compile_ast` are NOT about
  attackers. They are about a legitimate deeply-nested pattern from a trusted
  source on a 128 KB musl thread stack (D19). That is an ordinary correctness
  bug for a threaded caller and it keeps its priority.
- **Differential fuzzing stays, and its purpose is sharpened.** `tests/fuzz`
  exists to find places where pcrec and PCRE2 DISAGREE — a correctness tool. It
  is not a security fuzzer and should not be justified as one.
- **Correctness on weird-but-legitimate input is untouched.** Empty subjects,
  embedded NULs, 0xFF bytes, subjects that are all newlines, `startpos == n` —
  all still have to be right, and the R3.2 sweeps covering them were the right
  work.

**Revisit-when:** someone proposes running pcrec on patterns from an untrusted
source, at which point this entry is the thing to reopen rather than quietly
work around.

## D23 — 2026-08-09 — ASCII case-insensitivity FOLDS: the first dimension put through D18's earn-its-axis test, and it fails to earn one

D18 recorded four predictions so results could be checked against them rather
than remembered favourably. This is the first one settled (OS-1), and it is
also the first use of the earn-its-axis rule on a real dimension.

**Prediction: case 1, folds into the front end, completely. HELD.** Every
literal and class is already a 256-bit bitmap, so caselessness is
`bitmap |= swapcase(bitmap)` at parse time (`cls_casefold` in src/parse). NFA
construction, subset construction, byte equivalence classes, minimization and
emission are unchanged and unaware. Structurally: `-i 'aBc'` emits C
BYTE-IDENTICAL to `'[aA][bB][cC]'`, `-i '[^a]'` byte-identical to `'[^aA]'`,
and a letter-free pattern is byte-identical with and without `-i`. There is no
second engine to dispatch between, so **case is not an axis** and the ASCII
half of DD-1 becomes a parser change rather than an engine question.

**Measured against the design being rejected** — a runtime-checked engine that
compiles the lowercased pattern and maps every subject byte through `lc[]` in
the hot loop, built by transforming pcrec's own output so the two differ only
in where case is handled (7 interleaved trials, 8 MB no-match subject, load
0.59 before / 1.01 after, reproduced in a second run):

| pattern | folded | runtime-checked | table entries |
|---|---|---|---|
| `(error\|warning\|fatal)` | **511.7 MB/s** (505-520) | 458.9 (453-463) | 192 both |
| `[a-z]+@[a-z]+` | **226.5** (221-229) | 219.9 (218-222) | 12 both |
| `[0-9]+-[0-9]+` (no letters) | **2650** (2476-2703) | 1964 (1576-2008) | 12 both |

Folding wins everywhere. The keyword and letter-free gaps are outside their
spreads; the `[a-z]+@` gap is ~3% with ranges just touching, so treat its
DIRECTION as established and its size as not. The letter-free row is the
useful control: the runtime variant pays 26% for the `lc[]` indirection on a
pattern with no letters at all, i.e. that tax is the mechanism's, not
case's.

**One prediction was too optimistic, and it is worth correcting.** D18 said
byte-class merging "may even SHRINK the tables". Almost never: folding adds
each letter's other case to an existing class, so `ncls` is normally unchanged
and the tables come out the SAME size (192/192 and 12/12 above). Shrinking
needs the pattern to already mention both cases — `aA` goes 9 entries to 6 —
which is rare in real patterns. "Same size" is the honest expectation.

**And one cost nobody predicted, which is the largest number here.** Folding a
pattern that STARTS with a letter destroys the single-byte memchr prefilter:
`hello` has one escape byte from the start state, `-i hello` has two (`h` and
`H`), so the emitter falls to the bitmap loop — 2606 MB/s to 1245, a 52% loss.
That is a cost of CASELESSNESS, not of folding: a runtime-checked engine cannot
use memchr either (a single-byte search cannot see both cases), which is why
that row has no runtime-checked variant at all. It lands squarely on D21's
OPT-A lead — memchr2/memchr3 covers exactly this two-escape-byte gap, and this
is now a second measured customer for it alongside case (d).

**Scope, and the two boundaries where "it folds" stops being true.** The claim
above is unconditional about the CLASS-BASED tier and must not be read wider
than that. Two constructs can defeat it, and neither is shipped, so this is a
note for whoever implements them rather than a correction:

1. **Backreferences (M6/backrefs, and the M4 VM before them).** `(?i)(a)\1`
   compares captured SUBJECT text against subject text. That is not a
   class-membership test, so there is no bitmap to fold it into: a caseless
   backreference needs a case-insensitive comparison at MATCH time. It is the
   one place where caselessness could still cost something at run time, and it
   is where this dimension would have to be re-examined against D18's rule.
2. **Unicode folding (DD-1/M5).** ASCII folding is a bijection on 52 bytes, so
   it is a bitmap OR. Unicode folding is not: it has one-to-many foldings
   (`ß` -> `ss`), multi-byte fold pairs that cross byte-class boundaries, and
   pairs whose members have different UTF-8 lengths. None of that is a
   256-bit-bitmap operation, so the "it is just `bitmap |= swapcase(bitmap)`"
   argument does NOT carry over and DD-1 must settle it on its own evidence.

Everything else in the base tier folds: literals, classes, ranges, negated
classes, `.`, quantifiers, alternation and anchors are all built from class
bitmaps or carry no case at all.

**Scoped modifiers cost nothing extra, which is worth knowing before M6.**
`(?i)`, `(?i:...)` and `(?-i)` currently fail cleanly with "requires module
'modifiers'". When that module lands, the fold does not need redesigning: it is
applied per-class at CONSTRUCTION time, so a scoped flag means "whichever
setting is in effect where this class is parsed" — a parser state variable
saved and restored at group boundaries, with `options.caseless` as its initial
value. The option and the inline syntax become two spellings of the same
front-end change, and scoped case-insensitivity is still one engine with no
runtime cost. Scoping strengthens this decision rather than complicating it.

ASCII only: in the C locale bytes >= 0x80 have no case, and Unicode folding
stays with DD-1/M5 per boundary 2 above. The fold is applied at each site that builds a
positive class set — `char_node` and `p_class` — and NOT as a post-parse AST
walk, because AST depth is unbounded in pattern length and such a walk would
add exactly the recursion DD-10/TS-4 is trying to remove.

**The subtle half, recorded because nothing downstream can catch it.** A
negated class must be folded on the POSITIVE set and then complemented.
`[^a]` caseless is "neither a nor A"; folding after negating gives
{all but a} | swapcase{all but a} = every byte, so `[^a]` would match
everything. Both orders produce a case-CLOSED set, so no invariant, no
structural property and no equivalence check distinguishes them — only
behaviour does. tests/base/caseless.rxt pins it with `n "A"` lines, and
run_codegen_tests.sh pins the shape by requiring `-i '[^a]'` to equal
`'[^aA]'` and to DIFFER from `'[^A]'`.

## D24 — 2026-08-09 — the syntax construct REGISTRY: one declarative table, four dispatch doorways, static data with dynamic selection

Raised by Frank after reviewing the PCRE2 compliance report: is a single
parse.c the right long-term shape, given that PCRE2 has flavours, options, and
"exists but only on certain engines" caveats? The stated fear is the failure
mode where a codebase fills with `if python-compat do X else if pcre2-dfa do Y
else Z`, and every change cascades.

**The file size is not the problem, and splitting by size would be a refactor
masquerading as a fix.** parse.c is 467 lines and neither bug found on
2026-08-09 (`\v`, POSIX collating elements) was caused by that, nor would have
been caught by making it five files.

**The problem is that one construct's identity lives in up to five places.**
Measured: `esc_modules[]` (10 rows), `esc_char_value()`'s switch (8 cases), the
`(?X` dispatch chain (11 branches), the reject table (60 call sites), the
compliance report (90 rows). `\v` was places 1 and 2 disagreeing — the
declarative table said "class escape, module classes", the imperative switch
said "control character 0x0B", ten lines apart, with nothing enforcing that
they agree. Writing the reject table and the report then MANUFACTURED two more
copies of the same knowledge, so the drift clock is already running on work
done the same day.

**Frank's structural insight, which the data supports and which the design now
rests on: syntax is the driver, and the weird stuff arrives through a tiny
number of doorways.** Every non-base construct in PCRE2's entire surface enters
through exactly four:

    after `\`             one byte decides    \d \v \p \K \g \Q \R \1
    after `(?`            one byte decides    (?= (?< (?> (?# (?C (?| (?( (?R (?& (?i
    after `(*`            a NAME decides      (*SKIP) (*CR) (*script_run:
    after `[[` in a class one byte decides    [[:alpha:]] [[.a.]] [[=a=]]

The base tier reaches exactly ONE of them, once: `(?:`. So Frank's principle —
"make the normal stuff compile fast, the weird stuff can cost a few lookups" —
is satisfied BY CONSTRUCTION rather than by optimisation: a 95% pattern
performs zero registry lookups. That property is worth a guard, not just a
claim (SR-5).

**FOUR AXES, KEPT APART ON PURPOSE.** The `if flavour else if flavour` bloat
comes from answering four different questions with one mechanism:

| axis | question | mechanism | resolved |
|---|---|---|---|
| flavour | which construct does this byte MEAN? (`\v` = vertical whitespace or VT) | which table row the dispatch byte binds to | once per compile |
| option | what does the construct DENOTE? (`(?i)`, UCP) | scalar parameter to the handler (D18/D20) | once per compile |
| enablement | is it available at all? | one bit test at dispatch -> clean rejection | at dispatch |
| engine | can it LOWER to the selected engine? | a lowering-time check, NOT parse-time | after parse |

The load-bearing property: a flavour change REBINDS A ROW. It cannot reach
inside another construct's handler, because PCRE2's `\v` handler and python's
`\v` handler are different functions rather than one function with a branch.
That is D18's hyperspecialization applied to the front end, and it is why the
cascade Frank is worried about cannot form.

The fourth axis also fixes a conflation shipped today: pcrec's parser rejects
`\1` with "requires module 'backrefs'", but backreferences are not a PARSING
problem — they parse fine and cannot LOWER to a DFA. When M4's VM lands, `\1`
becomes parseable, lowerable-to-VM and not-lowerable-to-DFA simultaneously, and
"requires module X" and "requires engine Y" become different sentences with
different owners. The registry carries an `engines` column from the start so
this is a column gaining teeth rather than a retrofit.

**STATIC TABLE, DYNAMIC SELECTION.** Frank's concern was that a registry would
have to be dynamic, or "we would be compiling the compiler to compile regex".
Resolved by splitting those:

- The table is `static const` C data, authored once. Handlers are C functions,
  so a genuinely new construct means rebuilding pcrec regardless — that is
  unavoidable for a compiler written in C and is not what the concern is about.
- SELECTION is to be fully dynamic: flavour and feature mask resolved at
  pattern-compile time, per call, from `pcrec_options`. **Stated as intent, not
  as description (R4 correction):** as of SR-1 `pcrec_options` has no flavour or
  enablement field, and nothing outside tests/registry/ reads the
  feature/flavour/engine columns at all. The separation of the four axes is real
  in the DATA and still nominal in the CODE; it becomes load-bearing at SR-7.
- A runtime-MUTABLE registry is rejected. It buys nothing over the above and
  costs the thread-safety property D19 established: a mutable global registry is
  exactly the file-scope mutable state D19's compiler-side property forbids.
  **Correction (R4 critic pass, same day).** This bullet originally read "D19
  established and TS-1 now guards". TS-1 does not guard it. TS-1 scans EMITTED
  OUTPUT only — the .c/.h pcrec generates for a pattern — and would not notice a
  mutable global added to src/. D19's compiler-side property is AUDITED BY HAND
  and mechanized by nothing. The conclusion stands; the guarantee cited for it
  did not exist, and the miscitation had already been copied into
  src/parse/registry.c and src/core/internal.h before a critic caught it. This
  is the same failure mode as D19's own correction to R3 — a wrong description
  of correct code, which the next reader reasons from.

**The registry generates DOCUMENTATION AND TESTS, never the compiler** — and
better than generating them, it is DUMPED and they consume the dump:
`pcrec --list-syntax` emits the table, `tests/reject/` iterates that dump
instead of its hand-written 93 entries, and docs/pcre2_compliance.md is
rendered from it. Add a row and both the test and the report cover it with no
edit. That permanently kills the five-way duplication that produced `\v`.

**FAMILIES ARE NAMED MASKS**, which is where the "only on certain engines"
problem dissolves:

    { "pcre2-10.46", FLAV_PCRE2,  FEAT_STABLE }
    { "pcre2-dfa",   FLAV_PCRE2,  FEAT_STABLE & ~(BACKREFS|RECURSION|COND_CAPTURE) }
    { "python-re",   FLAV_PYTHON, ... }

`pcre2-dfa` is the engine-capability axis expressed as a family. PCRE2's own
DFA exclusion list stops being prose in a report and becomes a definition.

**DEFERRED BY DESIGN: build the registry now, the FLAVOURS later.** Ship with
the flavour column present and exactly ONE flavour. D18's earn-its-axis rule
applies verbatim to the front end: we have precisely one known flavour-varying
row (`\v`), and building selection machinery for a set of one is the mistake
OS-0 is deliberately not making. The registry pays for itself immediately by
collapsing the duplication; flavours turn on when a second one earns it.

**Scope discipline, stated because the report tempts otherwise.** Frank's
priority is the 95% people actually use. The registry is not licence to
implement exotic constructs — it is the mechanism that lets them be NAMED,
REJECTED CLEANLY and QUERIED at near-zero cost while effort goes to the common
path. A row with a NULL handler is a complete, correct, tested outcome.

**SR-1 AS BUILT (2026-08-09), two departures from the plan text.** Both are
small, both would surprise a reader who took the step description literally.

1. **No [256] index per kind — a linear scan over the rows.** The plan said
   indexed. The index has no customer: SR-5's own claim is that a base-tier
   pattern performs ZERO lookups at these doorways, so the scan runs only for a
   construct that is about to stop the compile with a diagnostic. Building an
   index for that is the unmeasured axis D18 forbids, and in C it would need
   either a hand-maintained parallel array — a SECOND HOME FOR THE SELECTOR
   BYTES, which is the exact failure this table exists to end — or an X-macro
   the codebase uses nowhere else. Revisit if a doorway ever lands on a hot
   path, which today nothing suggests.
2. **No handler field yet.** Its four signatures are determined by SR-2's
   dispatch functions, not by the table; a field that is NULL in all 67 rows
   and whose type is a guess is worse than one added when its type is known.
   `RS_MODULE` carries the "known but unimplemented" meaning meanwhile, and the
   third status `RS_REJECTED` had to be added for constructs PCRE2 rejects TOO
   (POSIX collating elements), where there is no module to name and agreement
   is compliance — a state the handler pointer alone could not express.

Also as built: the table describes NON-BASE constructs only, so `\n` `\t` `\xHH`
and friends never reach it, and two "requires module" diagnostics stay in
parse.c because they are sub-cases of base constructs rather than doorways —
`\x{...}` (reached only from the base `\x` handler) and the possessive `+`
suffix. Giving either one a doorway would cost the base tier a lookup for
nothing. They are the two known outstanding second homes.

**Revisit when:** a second flavour earns its axis; or M4's VM makes the
`engines` column load-bearing; or the base grammar itself needs to vary
(BRE/ERE under V-D), which is the one case that genuinely needs a second
grammar file rather than a second table.
