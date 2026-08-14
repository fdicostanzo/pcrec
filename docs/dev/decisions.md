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

**AFFIRMED AND WIDENED 2026-08-11 (Frank), in response to a session that asked
permission before convening a panel.** Subagents may be used AS NEEDED on this
project; no per-occasion approval is required, and asking for it is a
misreading. **Consider a LOWER model where the work fits one** — that is the
standing preference, not an exception to be justified. The split that decides
the model is the one D5 already draws, plus the FACTS-vs-JUDGEMENT split
measured 2026-08-09: fact-gathering (what a binary does, what a document says,
what a sweep measures) delegates well and delegates cheaply; architectural
judgement stays in the main session, where the design context is. The critic
panels of D6 are subagent work by definition and are covered by this.

This does not relax the SCOPE MANDATE: every subagent brief still restates that
work touches only this repository, and critics work read-only.

## D6 — 2026-08-09 — Adversarial critic review gate at every major checkpoint

At the close of each milestone (and any comparably large checkpoint), spawn a
panel of adversarial critic subagents over the work since the previous
checkpoint — separate lenses (correctness/semantics, robustness, architecture,
tests/process), explicitly instructed to be unfriendly and to surface problems,
with evidence/reproduction required per finding (CONFIRMED vs SUSPECTED) and a
list of what was probed-and-held so clean areas are distinguishable from
unprobed ones. Findings are compiled + triaged into docs/dev/reviews/<date>-<milestone>.md;
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

POSTSCRIPT (2026-08-11, R3.6/R3.7 landed): the earning machinery exists —
`compare/run_history.tsv` accumulates independent runs with load provenance,
and `EARN=1 gate.sh` REPORTS (never applies) the margin each case's history
would justify, gated on 8 distinct dates. Its first real run says every case
is still too thin, so the ceiling stands. And case (i)'s "26%" movement above
under-stated it: ten independent quiet runs span 1.94x run-to-run (43.07-83.36
ns/call — a sub-100ns latency case), so its old floor value 69.72 (which
matched NO recorded run) was re-baselined to the ten-run median 50.56, margin
still clamped at 0.700. Single samples do not baseline the latency case;
`rebaseline.sh` is the mechanics.

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

> **Partly superseded by D20 (same day):** this entry's closing speculation
> that `pcrec_options`' scalar fields would need a SET-VALUED redesign is
> reversed there — the core API never becomes set-valued; D20 deletes that
> half. Recorded here because a reader who stops at this entry draws the
> wrong conclusion about lib/pcrec.h's stability (DOC-1, 2026-08-11).

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

The base tier reaches these doorways rarely and cheaply. Frank's principle —
"make the normal stuff compile fast, the weird stuff can cost a few lookups" —
holds, but by SIZE rather than BY CONSTRUCTION, which is not what this paragraph
said until R6 measured it (see the R6 CORRECTION at the end of this entry). A
95% pattern does not perform zero lookups; it performs one per non-negated
character class. That property is worth a guard, not just a claim (SR-5) — and
SR-5 must guard the measured property, not the one asserted here.

**THE LIMIT OF THE TABLE, measured at R6 and not known when D24 was written.**
The registry identifies a DOORWAY and names a MODULE. It cannot always identify
the CONSTRUCT. Two constructs decide on information that is not at the doorway:
`(?(R)` depends on whether a group named `R` is declared anywhere in the pattern
INCLUDING AFTER IT, and `\ddd` depends on the running capture count (`(a)\12`
is octal; with twelve groups it is a backreference). Both are cleanly rejected
today with the right module named, so this bounds the FUTURE rather than
describing a bug: modules 'conditionals' and 'backrefs' need parser state — a
capture count and a group-name table — that no lookup keyed on doorway text can
provide. It is also why R6 rejected a lookup signature taking only the doorway
text.

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
   indexed. The index has no customer WORTH BUYING: the scan runs once per
   non-negated character class over 3 rows (R6 measurement; the original text
   here said a base-tier pattern performs ZERO lookups, which is false), and
   otherwise only for a construct about to stop the compile with a diagnostic. Building an
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

**SR-2 AS BUILT (2026-08-10), and the handler field is deferred AGAIN.** The
four doorways are real function calls now, in src/parse/ext.c, and parse.c is
the base grammar and nothing else. Three things a reader of the step text would
not expect:

1. **Still no handler field**, and the reason has inverted. SR-1 deferred it
   because its type was a guess; ext.c now fixes all four signatures, so that
   objection is gone — and a better one replaced it. Every row today is
   `RS_MODULE` or `RS_REJECTED`, so every handler would be NULL and the branch
   that calls one would be DEAD CODE no test can reach. This project has lost
   more to unexercised structure than to missing structure: R4's F13 and F14
   were both "correct by construction" claims with nothing testing them, and
   both were holes. SR-6 adds the field alongside its first real handler, at
   which point the branch has a customer on its first day. The cost of waiting
   is now zero, because the signatures are written down in ext.c.
2. **`RF_CLASS_DELIM` joined the row schema.** The POSIX collating elements are
   recognised conditionally — the delimiter opens the construct only when the
   matching `X]` appears later, and the character class's own bracket can serve
   as its `[`. That is the CONSTRUCT's recognition rule, not base grammar, so
   leaving it in parse.c would have left the doorway half-moved. One flag
   carries both halves because they coincide on exactly the two collating rows;
   the flag's comment says so and says to split it if a third row disagrees.
3. **The dispatch functions are `noreturn`, deliberately as a tripwire.** Every
   row ends the compile with a diagnostic today, so the attribute is TRUE. When
   SR-6's first handler returns a value, gcc rejects the attribute at that exact
   moment. A claim that fails the build when it stops being true is worth more
   than a comment restating the plan.

**And the step earned its keep in a way the plan did not predict.** The
byte-identity proof (4173 hashed cases, zero differences) certified the
restructure; the SABOTAGE battery run against that proof found something better.
Deleting the new `at_class_open` guard changes nothing — 0 of 4173 cases, and no
test in the suite fails. Behind that invisible branch was a real over-acceptance:
pcrec compiles `[:alpha:]`, PCRE2 rejects it (K3). The generalisable habit is
not "write sabotage tests" but **ask which of the branches you just added no
test can see, and look at what is hiding behind each one.**

**Revisit when:** a second flavour earns its axis; or M4's VM makes the
`engines` column load-bearing; or the base grammar itself needs to vary
(BRE/ERE under V-D), which is the one case that genuinely needs a second
grammar file rather than a second table.

## D25 — 2026-08-10 — the `(*` doorway gets NAME tables, and a "not a known name" outcome distinct from "requires a module" (Q1)

**Decision.** Doorway 3 (`(*`) reads the verb NAME and answers with one of four
things instead of one: the quantifier error for an empty name, the name table's
"not recognized" message, a name's own message (`MARK` alone has one), or the
row's "requires module 'verbs'". The names live in `src/parse/registry.c` as two
`VerbName` tables — not as `RegRow`s — selected by the CASE of the first name
byte, exactly as libpcre2 selects between its own two tables.

**Why the old answer was wrong, not merely coarse.** One catch-all row answered
"requires module 'verbs'" for every name. `(*NOTAVERB)` was therefore promised
that a module would one day implement it, and no module ever will, because PCRE2
has no such verb. `(*)` was called a verb when PCRE2 reads `(` followed by a `*`
that quantifies nothing. `a(*CR)` was called a verb when a start-of-pattern
option away from the start is an error. Three wrong answers, all shipped.

**The reason it is worth building NOW rather than with module 'verbs' (SR-6),
which is where SR-1 put it.** SR-1's argument was sound at the time: naming
forty verbs that nothing distinguishes and no test exercises is fiction in a
file whose purpose is to stop syntax knowledge from being fiction. What changed
is the second half of that sentence. `docs/design/design_registry_selectors.md` §9
(T-12) is the strongest argument any review in this project has produced: every
finding in R4, R5 and R6 ran into "a check that iterates what EXISTS cannot see
what is MISSING", and for a NAME-keyed doorway that wall comes down the moment
an outside authority can be asked about a name pcrec has never heard of. That
check is worthless while pcrec's answer does not depend on the name. So Q1 is
not per-verb rows arriving early — it is the precondition for PC-3's only
mechanism that scales coverage without scaling human transcription.

**Why VerbName and not RegRow.** A `RegRow` carries a module, a feature bit, an
engine mask, a diagnostic template and a hand-written note. Fifty of them would
repeat one module fifty times and carry fifty notes nobody had measured — SR-1's
objection, still correct. A `VerbName` answers exactly one question ("does PCRE2
have this name, and in which forms") and **every bit of it is verified against
libpcre2 on every run** by `tests/registry/pcre2_check.c`. Nothing in those
tables is asserted; it is recorded measurement, and a measurement that has a
test is not fiction. The two are different KINDS of claim and they get different
schemas rather than one schema stretched over both.

**The form bits are the measurement, not a theory.** `VF_BARE`, `VF_ARG`,
`VF_EMPTYARG`, `VF_EQNUM`, `VF_GROUPARG`, `VF_ATSTART` were chosen because they
are what varies across libpcre2's actual behaviour, measured over the whole verb
surface: `(*ACCEPT:)` compiles and `(*MARK:)` does not; `(*pla:x` is "missing
closing parenthesis" (the name WAS recognised) while `(*ACCEPT:x` is "not
recognized"; `a(*CR)` is an error and `a(*ACCEPT)` is not. An earlier draft
tried to name five verb CATEGORIES instead; the categories were a theory about
PCRE2 and the bits are PCRE2's answer.

**Messages are PCRE2's own wording, byte for byte** — "(*VERB) not recognized or
malformed", "(*alpha_assertion) not recognized", "(*MARK) must have an argument"
— for the same reason the POSIX collating rows already were: where AGREEMENT is
the entire claim, saying it in different words makes the claim harder to check
and no clearer to read.

**What this deliberately does NOT do.** It does not implement any verb; every
name here still ends the compile. It does not give the lower table's names their
real modules (`(*pla:...)` is a lookahead and will belong to module
`lookaround`, not `verbs`) — that is SR-6's call, made with the module, and
answering it now would be the fiction all over again. And the at-start rule is
implemented as `offset == 0` rather than as a general "preceded only by at-start
verbs" scan, because any earlier verb ends the compile first, so the general
scan's only interesting branch is unreachable today; `pcrec_ext_verb` says so
and says what makes it wrong later.

**Revisit when:** SR-6 lands module 'verbs' and these names need real modules
and real handlers; or SR-9's `tail` selector arrives, at which point the upper
table's shape should be re-examined against it (they are orthogonal — §7 of the
selector design says so — but they touch the same doorway); or a libpcre2
upgrade makes `pcre2_check.c` fail, which is the table doing its job.

## D26 — 2026-08-10 — FUNCTIONAL compatibility with PCRE2, not bit-exact compatibility: effort tiers by distance from the core

**Decision.** pcrec takes PCRE2 as the SOURCE OF TRUTH for regex syntax and
semantics. It does not take one installed build of PCRE2 as a specification to
be reproduced byte for byte. Effort is spent in four tiers, and the tier decides
how much a divergence costs:

| tier | what | standard |
|---|---|---|
| 1. CORE | what a pattern MATCHES, for syntax pcrec implements | **exact.** A divergence is a bug, always |
| 2. RECOGNITION | is this real PCRE2 syntax, and which module owns it | **exact.** Naming a module that will never implement a construct is a defect; so is rejecting syntax PCRE2 accepts |
| 3. DIAGNOSTICS | the WORDING, error number and offset for constructs pcrec does not implement | **functional.** "requires module 'X'" or "not supported" discharges the obligation in full |
| 4. NEVER-IMPLEMENTING | constructs the architecture rules out (backtracking verbs, callouts, substitution) | **clean rejection and a name.** Nothing further |

**Why, in Frank's words (2026-08-10):** *"I think we are getting a bit
overconcerned about exact pcre2 compatibility. My focus on pcre2 was to use it
as the source of regex syntax and semantics but I see a lot of effort making
sure error messages are compliant... we have a limited effort resource and we
should expend it appropriately. We should be fully aligned at the core and
expend less effort the further from the core we get, particularly with regard to
features we have not yet implemented, and especially wrt features we never
will."*

**The argument that makes this correct rather than merely cheaper.**

1. **PCRE2 is a moving target and there is no specification.** Everything
   measured in R8 came from libpcre2 **10.46**; 10.47 is already out. Error
   numbers, message wording, the verb list and the option set all move between
   releases. A test suite that asserts 10.46's wording is asserting a fact with
   a shelf life, and it will go red for reasons that mean nothing.
2. **PCRE2 does not do this either.** It is the *Perl* Compatible Regular
   Expressions library and it ships a document listing where it diverges from
   Perl. The most compatible regex library in wide use does not reach 100% with
   its own namesake. "The closest we can achieve" was never the target; it is
   not even PCRE2's target.
3. **The effort was going to the wrong end.** R8 spent real work making pcrec
   reproduce PCRE2's exact wording for constructs pcrec's own compliance survey
   already marks `OUT-OF-SCOPE`. The clearest case: `(*LIMIT_MATCH=N)` and its
   two siblings, which docs/pcre2_compliance.md has recorded as OUT-OF-SCOPE
   since the 2026-08-09 survey — *"these bound a BACKTRACKING search. pcrec is
   O(n) by construction, so there is nothing to limit. D22 also removes the
   adversarial-input motivation."* pcrec now reproduces PCRE2's 32-bit
   accumulator overflow for those options to the exact digit (boundary
   4294967290, not 4294967296) and pins it in the suite. **Tier 4 work done to a
   tier 1 standard, on a row we had already decided not to build.**

**What does NOT change, and this is most of the value already built.** Tier 2 is
where Q1, PC-3 and the registry live, and it is exact. The `\v` bug, the `(?*`
wrong-module bug, `(*NOTAVERB)` being promised a module, `[a[:b]` being rejected
when PCRE2 compiles it — every one of those is a tier 1 or tier 2 defect and
this decision makes none of them cheaper. **Knowing which constructs are real
is precisely what Frank wanted PCRE2 for.**

**Nothing is removed.** Frank was explicit: *"don't rip anything out — let's
just set our focus going forward."* The exact wording already pinned in
`tests/reject/`, the verb tables' form bits and PC-3's identity assertions all
stay. They pass, they cost nothing per run, and deleting them is its own spend.

**What to do when a PCRE2 upgrade makes a check red** — the case this decision
exists to answer before it happens:

- a **tier 1 or 2** disagreement (a construct appeared, vanished, or changed
  meaning) is a real finding: investigate and follow it.
- a **tier 3 or 4** disagreement — new wording, a renumbered error, a new verb
  name for a construct pcrec will not implement — is DRIFT. Record it in the
  journal, reclassify that assertion as informational, and move on. **Do not
  chase the new wording.** `tests/registry/pcre2_check.c` asserts message
  identity today; the correct response to an upgrade making that red is to
  demote the assertion, not to re-measure PCRE2.

**A TENSION THIS DECISION CREATES, and it nearly cost a real guard within hours
of being written.** "Do not chase PCRE2's wording, error number or offset" reads
easily as "offsets do not matter". They do. What tier 3 releases you from is
matching PCRE2's NUMBER; it does not release you from pcrec's offset being
*right against pcrec's own convention*, which is to blame the construct it
actually recognised.

Measured, FIX-2: `[[.a[.b.].]` has a nested opener, and PCRE2 abandons the outer
one for the inner. With K4's rule 2, pcrec reports offset 4 — the inner opener,
the construct PCRE2 recognises. Without it, offset 1 — the outer bracket PCRE2
walked away from. PCRE2 says offset 9, which is neither, because it points at
the end. **Deleting rule 2 left a 1680-pattern generated differential at ZERO
failures**, because that differential compares verdicts, and it was D26 that had
talked me out of comparing offsets at all.

So the rule is: **pin your own offsets against your own convention; do not pin
them against PCRE2's.** The first is tier 2 — it is what makes a diagnostic
actionable, and it is the difference between blaming byte 1 and byte 4. The
second is tier 3 and a moving target like every other number here.

There is a general form worth carrying, because this is the THIRD branch in this
project that no test could see (R5's `at_class_open`, R7's `try_quant` offsets,
now this): **the failure is not line coverage — every one of those branches
EXECUTED.** It is that the assertions project onto a SUBSET OF THE OUTPUT
FIELDS, and the branch moved a field outside the projection. pcrec's diagnostic
has two fields, message and offset, and twice out of three the invisible one was
the offset. The question that finds these is not "is this line covered" but
**"which suite reads this FIELD of the output?"** — asked per field: verdict,
message, offset, emitted bytes.

**Consequences already taken:** `src/core/limits.h` sorts every policy number
into three sections — ours, PCRE2 syntax (exact), PCRE2 internals (minimums we
honour, not contracts we owe) — so a reader can tell which tier a number is in
before deciding whether a divergence matters. FIX-2 drops its proposed fifth
doorway kind (`RK_CLASSOPEN`), which existed only to reproduce PCRE2's two
different wordings at one doorway; under tier 3 one message serves, and the
cheap `RF_CLASS_DELIM` fix deletes the same dead parameter the expensive option
was justified by.

**Revisit when:** a user reports that a wording difference actually cost them
something; or pcrec grows a PCRE2-compatibility mode as a product feature rather
than as an internal standard; or the module set grows far enough that tier 4 is
nearly empty, at which point the gradient matters less than it does now.

**Addendum (DOC-1, 2026-08-11) — which PCRE2.** "Source of truth" means the
PINNED oracle the differentials actually run against — libpcre2 **10.46**
today, named in docs/pcre2_compliance.md's header — not whatever release is
current. Point 1 above already concedes releases move; this line closes the
loop it left open: a version bump is a deliberate re-measurement event (rerun
the differentials, re-pin what moved, record it), never ambient drift a test
should silently track. Until such an event, a claim measured on 10.46
remains the project's expected verdict even where a newer PCRE2 differs.

## D27 — some tests are written from the GOAL, by someone denied the code

**Decision.** At least some of pcrec's tests are written by an author who has
NOT read `src/` or `tests/`, working from the mandate, APPROACH.md, D26,
`docs/pcre2_compliance.md`, the public header, the CLI surface, and libpcre2 as
the source of truth. This sits alongside the D6 critic panel, it does not
replace it: **the panel reviews the implementation; the spec writer tests the
promise.**

**Why, and this is measured rather than argued.** Every checkpoint from R4 to R9
found the same defect in whatever check had just been built — a control sharing
a source with the thing it controls. R9 chased that down to its root, and the
deepest shared source is not a file. It is that the same author writes the code
and then writes the check FROM the code, so the check can only ever ask *does it
do what it does*.

Frank named it on 2026-08-10, mid-review: *"perhaps some of the issues with
testing are because the coder is writing the tests based on the code, not the
goal."* Run as an experiment the same day, with two writers barred from the
source. Result:

- **A tier-1 miscompile in the first hour** (SPEC-FA): `[0-[:digit:]]`, a class
  construct as a range endpoint, compiled to a matcher for a pattern libpcre2
  refuses with error 150. 546 instances in a 1,530-pattern sweep.
- **A tier-2 over-promise at a third doorway** (SPEC-classes-F1): ten escapes
  told a module owns them inside a class, where PCRE2 forbids them permanently.
- **Q2 independently re-derived** from the documents alone — a known finding
  reached without reading the registry, which is the control saying the method
  is not merely lucky.
- **Seven ambiguities in our own documents**, the first time anyone had read the
  spec cold.

What it beat: four adversarial critics WITH source access, 1,239,480 generated
patterns, ~2.4 billion name probes, ASan/UBSan, and the differential fuzzer.

**The mechanism of the miss, which is the generalisable part.** SPEC-FA was
masked by the ALPHABET the tests use. `a` is 0x61 and `[` is 0x5b, so
`[a-[:digit:]]` is rejected as an out-of-order range before the endpoint can
matter — and every range in this repository was `a`-based. A test derived from
the implementation inherits the implementation author's alphabet. Isolation, not
adversarialness, is the active ingredient: the critics were maximally
adversarial and shared the author's vocabulary.

And the sharpest instance: SPEC-classes-F1's fact was ALREADY in the repository,
in the `\N` row's own `note` field — correct, written down, and inert, because
`note` is read by no check. Knowledge the code does not act on is invisible to
tests derived from the code.

**How to apply.** When a checkpoint touches a doorway or a construct's
semantics, brief a writer with the goal documents and libpcre2 and forbid `src/`
and `tests/`. Ask for three things: the OBLIGATIONS derived before any case is
written; the cases; and — most valuable — the list of obligations it expects are
untested, made blind, to be diffed against what exists. Expectations come from
libpcre2 or python `re`, never from pcrec.

**Revisit when:** a spec-first round produces nothing on two consecutive
checkpoints, which would suggest the goal documents have gone stale rather than
that the method has stopped working; or the documents become detailed enough
that "reading the spec" and "reading the code" stop being different acts.

## D28 — a module has PORTS: semantics and syntax are answered separately

**Decided** 2026-08-10 (Frank), arising from Q2. **Status:** adopted in
principle; the interface itself is [MOD-0] and is not built. Q2's option-run
parser is in `registry.c` PROVISIONALLY and is the first thing MOD-0 moves.

**The problem Q2 exposed.** Construct BODY parsing has no home. `ext.c` was
created so that parse.c could hold the core syntax and nothing else, and its
role is to find the right handler for a matched extension — it is a router.
`registry.c` is declarative `static const` data plus a lookup. Neither is a
place to put a parser, and Q2 needed one: the `(?` doorway cannot answer "is
this a construct" without reading the whole option run, exactly as Q1 could not
answer it at `(*` without reading the whole verb name.

It is not a handful of cases. Ten construct families need body parsing, and the
two largest are ahead of us rather than behind: `\p{...}` is a loose format
requiring NORMALISATION (case, spaces, `_`, `-`, `^`, `Script=Latin`, the bare
`\pL` form) and `(?[...])` is a nested set algebra. Either would outweigh
everything in `ext.c` today. Three families already sit in `ext.c` (verb names,
the `LIMIT_*` magnitude rule, the class-bracket delimiter scan) and it was
already the wrong shape for them.

**The decision.** A module exposes several PORTS rather than one entry point:

1. **semantic** — what the construct MEANS. This is what SR-6's handler field
   was always for.
2. **syntax** — how to parse a complicated body. The doorway tables establish
   from key+tail that this IS, say, an options group; the syntax port works out
   the details.
3. optimisation — deferred. Do not design for it yet.

**Why two ports rather than one handler with a mode flag, which is the argument
that actually settles it:** they have different LIFECYCLES. Every module is
unimplemented today, and body parsing is still required right now, for all of
them, because "is this a construct at all" is tier 2 under D26 and therefore
exact. The syntax port is needed for every module before any semantic port
exists.

**A verdict shape Q2 measured rather than invented.** PCRE2 distinguishes two
kinds of bad body and only one of them means "no construct here":

    SYN_OK         the body parses
    SYN_MALFORMED  the construct, written wrongly — STILL promise the module.
                   `(?i-m-s)` is error 194, a malformed option setting;
                   `(?0J)` is error 114, a malformed recursion call.
    SYN_NOT        errors 111 and 141 — no construct; promise nothing.

Q2 got that distinction wrong in BOTH directions before the generated
differential refused it, which is why it is recorded here rather than left for
MOD-0 to rediscover.

**AMENDED BY D29 (2026-08-11).** Those three are a taxonomy of PCRE2'S ERROR
NUMBERS — did PCRE2 dispatch to a construct — and they were measured correctly.
They are NOT a taxonomy of what the DOORWAY does, and MOD-0's design review
found the two had been treated as one thing. `SYN_NOT` covers both `[[:foo:]]`
(an error, promise nothing) and `[a[.b]` (a pattern PCRE2 COMPILES, where the
`[` is an ordinary class member and the parser must carry on) — opposite
answers. D29 replaces the doorway-facing vocabulary with CLAIM / REFUSE /
DECLINE and keeps SYN_OK/SYN_MALFORMED as a sub-distinction inside CLAIM. Read
D29 before implementing a port.

**Revisit when:** MOD-0 designs the signature. Two warnings carried forward. A
`(const char *at, size_t avail, size_t *len)` validate-only signature is
already known to be too weak — `\p` must hand back a normalised name, not a
length. And a port designed against one example inherits that example's
alphabet (D27), so shape it against at least `unicode-props` and the EXISTING
`verbs` scan, not against `modifiers` alone, which is the simplest body there is.

**Also carried forward, and it is why Q2's parser sits where it does:** the
grammar and the measurements that establish it must not be separated. The
`(*LIMIT_*=digits` rule is the counter-example — its measured description is in
`registry.c` and its implementation in `ext.c`, and R8/C2-9 found them drifted,
with `ext.c` accepting `=99999999999` that the description forbids. Wherever
the port lands, the probes and the code go together.

## D29 — 2026-08-11 — a construct is RECOGNISED BY A FUNCTION, not selected by a key; and the doorway's three answers are not PCRE2's three

**Decided** 2026-08-11 (Frank), designing [MOD-0]. **Supersedes** SR-9's `tail`
as a lookup key. **Amends** D28's verdict vocabulary.

> ## ⚠ STATUS: REFUTED IN PART BY THE R10 PANEL — DO NOT BUILD FROM THIS YET
>
> `docs/dev/reviews/2026-08-11-r10-mod0-design.md`. Five critics reviewed this
> decision the day it was written, before any of it was built. **The SPINE
> survives** — a recogniser function per row, two ports with two signatures, the
> semantic port recursing into `p_alt`, no allocation in recognition, row
> options having exactly one customer, and a recogniser not returning the module.
> **The GUARD that justified retiring `check_tail_precedence` does not**, and
> four measured facts in this text were wrong. Corrections are marked inline
> below as `[R10]`. The sections marked **WITHDRAWN** must be redesigned before
> MOD-0.1 starts; R10's "Dispositions" section is the specification for that.
>
> The three headline refutations, each measured rather than argued:
>
> 1. **"Exactly one recogniser may answer" fires on a CORRECT registry** (C1-1,
>    C1-3). Every tailed bucket has a tail-less FALLBACK row whose honest
>    recogniser is "always matches", and in two of four buckets the fallback and
>    a sibling carry OPPOSITE verdicts. Silencing the guard requires
>    hand-encoding longest-tail-wins inside each function — this decision retires
>    the rule and keeps the obligation.
> 2. **A uniqueness guard was traded for a REACHABILITY guard** (C1-2).
>    `check_tail_precedence`'s second half catches "a tailed construct became
>    unreachable"; nothing here fires on ZERO answers. This decision's own
>    `-\d+)` collapse is an instance: `(a)(?-1` is error 114 — malformed body,
>    still the construct — and would go from a correct `recursion` answer today
>    to the `(?` catch-all. A tier-2 regression proposed as a simplification.
> 3. **`registry.c:62-72` already forbade this signature, dated the day before**
>    (C3-1): *"`\ddd` is an octal escape or a backreference depending on how many
>    capture groups the parser has seen SO FAR [...] **Do not design a handler
>    signature that assumes it can.**"* Measured: `(a)x11 \12` is octal,
>    `(a)x12 \12` is a backreference, `(?n)` flips it back. One doorway byte,
>    two constructs, two modules, discriminated by parser progress a pure
>    recogniser cannot see — and module attribution is tier 2 and EXACT under
>    D26. This decision does not cite it and specifies the forbidden signature.
>    It is D27's own mechanism, reproduced one day after D27 was written.

### The decision

A registry row names a RECOGNISER — a function that answers whether the text at
a doorway is that row's construct. The selector byte remains, as a BUCKET key
that cuts the candidate set; the recogniser is the truth. Every recogniser in
the bucket is called, and **exactly one may answer. Two answers is a registry
defect**, reported as an internal error at runtime and asserted over the
generated sweep — not resolved by precedence.

Frank's framing, which is the whole design in one sentence: *"the function is
designed to identify one proper form and reject if it doesn't match... the idea
is that exactly one should actually match but all are called."*

### Why this supersedes `tail`, and the argument is `\N`

SR-9's `tail` is a LITERAL PREFIX resolved by LONGEST-TAIL-WINS. That rule
arrived unguarded, with row ORDER silently standing in for it, and it took
`check_tail_precedence` plus a shortest-first writing discipline to make it
observable at all (see SR-9's own notes in `src/parse/CLAUDE.md`).

~~`\N` and `\N{U+...}` are two rows resolved by that rule today. As recognisers
they are "N not followed by `{`" and "N followed by `{U+`...`}`" — disjoint,
and if anyone writes the naive `\N` recogniser as "always matches", **both fire
and the ambiguity guard says so out loud**. The design converts a silent
precedence into a checkable defect. That case is MOD-0's acceptance test and is
written first.~~

**[R10 — WITHDRAWN; this paragraph is wrong in three ways at once (C1-1, C1-2,
C1-6).]**

1. **The bucket has THREE rows, not two** (`registry.c:223` says so in its own
   heading), and the prefix-related pair longest-tail-wins actually resolves is
   `{` vs `{U+` — the RS_REJECTED row against the module row — not bare `\N` vs
   `\N{U+`. The bare row carries no tail and is resolved by a different clause.
2. **Written honestly, those two recognisers return REFUSE and CLAIM on
   `\N{U+0041}`** — two non-DECLINE answers on a table that is CORRECT, which
   `build/pcrec` answers right today. Generalised by measurement: all four tailed
   buckets have one tail-less FALLBACK row whose honest recogniser IS "always
   matches" (that is the row, not a naive rendering of it), and in the `\N` and
   `(?P` buckets the fallback and a sibling hold OPPOSITE verdicts.
3. **`{U+`...`}` is not the shape.** There is no `}` in the construct: all 253
   probeable bytes after `\N{U+` give error 193, as do `\N{U+`, `\N{U+}` and
   `\N{U+0041`. A recogniser written to the sentence above declines on the
   truncated forms, the REFUSE recogniser then answers ALONE — one answer, guard
   silent — and pcrec reports "PCRE2 does not support `\N{name}`" for a
   construct `unicode-props` owns.

And as an acceptance test it exercises only the guard FIRING on a planted
defect, which nobody doubted. The retirement it licenses depends on two
properties it never touches: no false positives (refuted in 2 of 4 buckets), and
coverage of what the retired check covered (refuted, C1-2). `registry.c:244`
also records that this is the table's ONLY prefix-related pair, so n=1 — wake
§7: *"Fixing the narrowest instance and calling it the class is the most
expensive error available here."*

A literal prefix also cannot express a construct's real shape, which forces one
construct to be written as many rows. Measured 2026-08-11: **[R10: 18 rows, not
17.]** ~~17 rows carry a tail (16 `GROUP_T`, 1 `REJECTED_T`)~~, and **ten of
them are `(?-0)`..`(?-9)`** — one construct, ten rows, because a tail is a
prefix and not a pattern. One recogniser reading `-\d+)` collapses them.
**[R10: the collapse is DEFERRED — `-\d+)` declines on `(a)(?-1`, `(a)(?-1x)`
and `(a)(?-1:x)`, which are error 114, a malformed body of a construct PCRE2
recognises and pcrec answers correctly today.]**

**[R10 — the count, and how it was got wrong.]** 18 rows carry a tail. Two
critics found it independently by ITERATING `pcrec_registry()`; the 17 came from
one grep for two macro NAMES, and `registry.c:257` — the `\N{U+0041}` row —
carries its tail as a raw struct literal through neither macro. That row is the
centrepiece of the `\N` argument above, so the same row was miscounted twice, in
two different ways, in the passage arguing the design is safe because its case
works. It is also the one row a mechanical macro-conversion would skip. The
general lesson, alongside wake §7's "generate the input space, never list it":
**counting a population by the syntax used to WRITE it counts the syntax, not
the population.**

**`--list-syntax` is not affected.** Measured: `syntax_dump.c` never renders
`tail` — the SR-4-frozen 12 columns do not include it, and the `syntax` column
already shows how a row is written. ~~Removing `tail` from the engine's
vocabulary breaks no interface and changes no test.~~

**[R10 — that last sentence is WITHDRAWN, and it inverts this document's own
standard.]** It is true only of the dump. Three checks read `.tail`:
`registry_check.c:170-176` (a row's `syntax` must contain its own tail),
`:177-194` ((sel,tail) uniqueness, a TOTAL static check) and `:427-487`
(precedence plus liveness). All three lose their subject; this decision accounts
for one. Worse, it argues "no check reads this field" as a SAFETY PROOF here and
cites wake §6's seven unread columns as the DISEASE three sections below. `tail`
is not one of those seven — it is a THIRTEENTH field that is not dumped at all,
so by this document's own standard it is the worst-guarded field in the struct,
not the safest.

### The doorway has THREE answers and they are not D28's three

This is the finding that would have been baked in wrong. D28's
SYN_OK/SYN_MALFORMED/SYN_NOT classifies PCRE2's error numbers. What a doorway
needs is a classification of PCREC'S RESPONSE, and `pcrec_ext_class_bracket`
already implements exactly three, one of which D28 has no name for:

| answer | PCRE2's behaviour | the doorway does | example |
|---|---|---|---|
| **CLAIM** | recognises the construct, body valid or not | name the module | `[[:alpha:]]` |
| **REFUSE** | errors, and no module can ever make it valid | this message, no module | `[[:foo:]]` |
| **DECLINE** | COMPILES it, as something else | not mine — carry on | `[a[.b]` |

REFUSE and DECLINE both map onto `SYN_NOT` and they are opposites. Collapsing
them is what K3, K4, FIX-2 and R9/SPEC-FA were each a local instance of, so a
vocabulary that cannot express the difference would have re-created all four.
~~D28's OK/MALFORMED survives INSIDE Claim, as a sub-distinction that starts
mattering when a semantic port exists.~~

**[R10 — the three answers are right and the AXIS is wrong (C2-3, C2-6, C2-1).]**

- **The table's own column does not determine two of its three answers.**
  "Recognises the construct, body valid or not" and "errors" are BOTH true for
  every malformed body — the case this decision spends its longest paragraph on.
  `[[:foo:]]` (error 122) is REFUSE while `(?i-m-s)` (error 194) is CLAIM, and
  nothing in the column separates them. The real discriminator is **did PCRE2
  DISPATCH**, which is D28's axis — demoted above to "a sub-distinction" and it
  is not one. `SYN_NOT` vs `SYN_{OK,MALFORMED}` IS the CLAIM/not-CLAIM line, and
  DECLINE-vs-REFUSE is a SECOND, ORTHOGONAL axis. Two bits, four cells.
- **The fourth cell is occupied.** `[^]` under `PCRE2_ALLOW_EMPTY_CLASS`
  compiles: PCRE2 does not dispatch (not CLAIM), it errors (not DECLINE), an
  option makes it valid (not REFUSE). pcrec agrees with PCRE2's default here by
  accident, since the reasoning that would justify it is absent.
- **REFUSE's second clause is measurably false.** "no module can ever make it
  valid": `\U` and `\u` COMPILE under `PCRE2_ALT_BSUX`, an option that exists for
  that purpose, and `\N{name}` compiles under
  `PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL` — for a construct pcrec ships an
  `RS_REJECTED` row about. **PCRE2 itself already ships the module.**
- **And DECLINE is unbound.** "PCRE2 COMPILES it, as something else" — under
  which options? Under `PCRE2_LITERAL` every byte string compiles. The verdicts
  are defined against a moving object and D26, D28 and D29 mention compile
  options nowhere; the one outside authority cannot see any of it, because
  `pcre2_check.c:50` states *"ALL COMPILES USE options = 0"*. The repair is to
  bind the mode as PCREC'S OWN decision rather than as a claim about PCRE2.
- **One tier-1 consequence, since a verdict differential cannot see it.**
  `\x{41}` compiles both ways but MEANS `A` by default and NUL-plus-`{41}` under
  `ALT_BSUX`. That is D26's "assertions project onto a SUBSET OF THE OUTPUT
  FIELDS" with the blind field being the emitted matcher.

Measured against this: `PCRE2_UTF` flips NO construct verdict (confirming the
wake §6 claim the critic was briefed to falsify), and neither do `UCP`,
`CASELESS`, `MULTILINE`, `DOTALL`, `UNGREEDY`, `AUTO_CALLOUT` or any
`EXTRA_ASCII_*`. The option-dependence is a small nameable set, which is what
makes binding the mode cheap.

### Two ports, and now for a better reason than lifecycle

D28 argued two ports rather than one handler-with-a-mode-flag from their
different LIFECYCLES. The stronger argument, found designing the signature:
**they cannot share a signature.** One is a predicate, the other is a parser.

    recogniser     pure. No Ctx, no allocation, no failure path.
                   (pat, patlen, at, ctx_flags) -> CLAIM/REFUSE/DECLINE + spans
    semantic port  takes Ctx *. Allocates AST nodes, may longjmp, and CALLS
                   p_alt BACK for a nested body.

**[R10/C3-7 — THE SENTENCE BELOW IS FALSE AS WRITTEN, and this decision
contradicts it two paragraphs earlier. Correct version:] RECOGNITION MUST NOT
DEPEND ON PARSING A NESTED PATTERN — it must never reach back into `p_alt`.**
That narrower form survives every probe. The version written below forbids the
delimiter-pair scan, the option-run scan and the verb-argument scan that pcrec
ALREADY SHIPS: measured, PCRE2's own recognition depends on the body in five
shipped constructs — `[a[.b]` compiles while `[[.a.]]` is error 113 (does `.]`
appear before the class ends?), `[[:foo:]]` vs `[[:alpha:]]` (is the body a known
name?), `(?iZ)` vs `(?i-m-s)` (does the run parse?), `(*LIMIT_MATCH=4294967290)`
(the argument's magnitude), `(*pla:x` vs `(*ACCEPT:x` (is the argument
terminated?) — and in the base tier `a{1}` is a quantifier while `a{x}` is four
literals. Worse, this decision nominates `pcrec_ext_class_bracket` as the shipped
implementation of its three answers, and that function's whole body is K4's
forward scan over the construct's BODY whose `return`s ARE the DECLINE: **the
model implementation of recognition is a body scan, in the section forbidding
body-dependent recognition.** Recognisers scanning OPAQUE bodies is not merely
permitted, it is mandatory. What must never happen is reaching into `p_alt`, and
the reason holds: there is no `(?...)` construct PCRE2 DECLINEs, so no
nested-pattern parse can change a `(?` verdict.

~~**RECOGNITION MUST NOT DEPEND ON THE BODY PARSING**, because PCRE2's does not.~~
`(?i:(` is still an option group: PCRE2 dispatches and then reports error 114,
missing closing parenthesis. A recogniser that recursed into the body would
watch the sub-parse fail and could reasonably DECLINE — which is precisely the
UNDER-promise Q2 made and the generated differential refused. A malformed body
is still the construct. This is why the recursion lives in the semantic port
and nowhere else.

The recogniser must also be pure in the D19 sense — no file-scope state, no
caches. A scanner is exactly where someone would put one.

**[R10 — the argument above is only half the question, and the repository had
already written down the other half (C3-1). THIS IS THE PANEL'S MOST SERIOUS
FINDING.]** "Recognition must not depend on the body parsing" is about
DOWNWARD dependence, and it is correct. It is silent on LEFTWARD dependence:
recognition of a construct depending on what the parser has already done.
`src/parse/registry.c:62-72`, dated 2026-08-10 — the day before this decision:

> `\ddd` is an octal escape or a backreference depending on how many capture
> groups the parser has seen SO FAR. `(a)\12` is octal 012; with twelve groups
> it is a backreference to group 12. [...] whoever implements modules
> 'conditionals' and 'backrefs' needs parser STATE the registry cannot supply — a
> running capture count, and a whole-pattern group-name table. A row can say
> "this doorway belongs to module X"; it cannot say which construct X should
> build. **Do not design a handler signature that assumes it can.**

Measured, rather than taken from the comment: `(a)x11 \12` is octal (it consumes
LF); `(a)x12 \12` is a backreference to group 12; `(?n)(a)x12 \12` is octal
again; `(?n:(a)x12)\12` likewise, so the option is SCOPED; parens inside
`\Q...\E` and inside a class do not count; forward groups do not count. And
`\1..\9` is a DIFFERENT rule — whole-pattern count, so `\8(a)x8` compiles while
`\8(a)x7` and `\8` alone are error 115.

So one doorway byte is **two constructs owned by two different modules**,
discriminated by a running capture count under scoped option state.
`(pat, patlen, at, ctx_flags)` cannot compute it; a `static const` row cannot
declare it; and module attribution is tier 2 and EXACT under D26, so this is not
a rounding error. The moment octal escapes get the row `registry.c:305` already
records as owed, bucket `1` holds two recognisers that must BOTH claim `\12`, and
pcrec reports an internal error for a pattern PCRE2 compiles — this decision's
own "Revisit when" trigger, reached before the first module ships.

**What this does NOT break:** the pure/impure split itself, or the claim that
recognition must not recurse into the body. Both survive. What it breaks is the
assumption that a pure recogniser can answer IDENTITY wherever it can answer
SHAPE. The digit buckets must be named as out of reach in the decision, not
discovered during MOD-0.4. A separate critic measured that `(?x)`, `(?xx)`,
`(?i)`, `(?J)` and `(?n)` move NO doorway recognition boundary and that PCRE2
does not strip extended-mode whitespace inside `(?` or `(*` — so the leftward
dependence is narrow and nameable rather than pervasive, which is what makes the
repair tractable.

**And the meta-lesson, which is D27's own mechanism reproduced one day after D27
was written:** the warning was in the repository, dated, specific, and addressed
to exactly this decision. D27 says knowledge the code does not act on is
invisible to tests derived from the code. R10 adds: it is equally invisible to
DESIGNS derived from reading the code, because reading `registry.c` for its DATA
while designing a signature is precisely the reading that skips a comment about
signatures.

### Recognisers allocate NOTHING, and that dodges K7

D28 carried forward that `(const char *at, size_t avail, size_t *len)` is too
weak because `\p{...}` must hand back a NORMALISED name rather than a length.
The obvious repair — pass an `Arena *` — is wrong. Measured 2026-08-11:
`arena_alloc` calls `abort()` on malloc failure (`src/core/arena.c:15`), which
IS K7's "aborts the caller's process under a memory limit". Handing the arena
to every recogniser would spread K7 across the whole module layer.

Instead a recogniser returns SPANS INTO THE PATTERN, plus — for the one case
that needs it — a CALLER-PROVIDED FIXED BUFFER for normalisation, ~~since
property names are length-bounded~~. The recogniser allocates nothing and cannot
abort.

**[R10 — the conclusion holds; the reason given for it is FALSE, and a builder
following the sentence literally ships a truncating recogniser (C3-2).]** It
reasons from a bound on the OUTPUT to a bound on the WORK. The normalised name
is bounded; the body handed to the recogniser is not, and the two are not close.
Measured: `\p{____[x100000]_L}` — a 100,006-byte body — COMPILES, because PCRE2
normalises WHILE STREAMING and never buffers the raw text. Its limit is on
SIGNIFICANT characters and it is **48**: `\p{a x48}` is error 147 (name read and
looked up), `\p{a x49}` is error 146 (buffer full), and 100,000 leading
underscores change neither. Both obvious implementations of "copy the span into
the buffer, then normalise" are wrong — overrun, or a silent truncation that
turns `\p{____L}` from CLAIM into REFUSE, which is a tier-2 miscompile of
exactly the SPEC-classes-F1 shape. The only correct shape is **normalise into
the buffer as you scan, counting significant characters only, and stop at 49** —
a real algorithm with a real off-by-one, not "a fixed buffer". The 48 is
load-bearing even though the 147/146 wording is tier 3, and it belongs in
`core/limits.h`'s PCRE2-internals section beside `PCREC_VERB_NAME_MAX`.

### Bodies come in three kinds, and only two can be owned end to end

Answering "could the recogniser find the whole structure":

1. **Opaque text** — a verb name, an option run, a POSIX name, `\p{...}`, and
   note `\Q...\E` and `(?#...)`, which extend arbitrarily far. Owned end to end.
2. **A nested PATTERN** — `(?i:...)`, `(?=...)`, `(?>...)`, conditionals. The
   recogniser owns the HEAD ONLY; the semantic port recurses into `p_alt`
   (`src/parse/parse.c:500`). A recogniser that scans for "the matching `)`"
   gets nesting wrong the first time someone writes `(?i:(a))`.
   **[R10/C3-6 — `p_alt` IS NOT A USABLE CALLBACK as the code stands, so MOD-0
   includes a parse.c change this decision does not price.]** Two measured
   reasons. (a) The GROUP NODE IS ERASED: `p_atom`'s group case returns the body
   with no wrapper (`parse.c:275`), so `(a|b)|c` and `a|b|c` build the identical
   AST — verified end to end, the generated C is byte-identical apart from the
   pattern comment. PCRE2 needs exactly that distinction here:
   `(a)(?(1)(a|b)|c)` compiles and `(a)(?(1)a|b|c)` is error 127, "conditional
   subpattern contains more than two branches", so **a `conditionals` port
   calling `p_alt` back cannot recover the top-level branch count** and cannot
   produce that error. Conditionals are not a type-2 body until it survives.
   (b) The depth DECREMENT sits at `parse.c:266`, AFTER the doorway call at
   `:259`, so it is on a path a module never reaches — "one depth counter, not
   two" is right as a rule and unimplementable against today's control flow.
3. **A self-contained sub-language** — `(?[...])` set algebra. Owned end to end,
   because that grammar belongs to module `classes`, not to the base parser.
   **[R10/C3-5 — it NESTS, and PCRE2 caps the nesting at 13.]** So a recogniser
   specified as pure with no failure path must carry its own bounded stack and
   its own depth rejection — a SECOND depth budget, in the layer this decision
   just finished saying must have exactly one. Either that is stated as an
   exception with its cap in `limits.h`, or `(?[...])` is not type-3.

So a recogniser's reported length means THE HEAD I CONSUMED, never "the whole
construct". Two answers to "where does this construct end" is the drift shape
D24 exists to prevent, so the semantic port must begin consuming exactly where
the recogniser's head ended, asserted.

### This inverts the layering, deliberately

Today the flow is one-way: parse.c -> ext.c -> registry, and `src/parse/CLAUDE.md`
and D24 both describe ext.c as a ROUTER with modules as leaves. A semantic port
calling `p_alt` back makes parse.c and the modules MUTUALLY RECURSIVE. That is
how a recursive-descent parser with extensible atoms is supposed to work, and
it is adopted here rather than discovered later — but it is a change to the
stated architecture, and the docs say so now.

**One depth counter, not two.** `cx->depth` against `PCREC_MAX_GROUP_DEPTH` is
maintained by `p_atom`'s group case (`parse.c:242`, `:266`). A module that
recurses counts against THAT counter. Two nesting limits would drift, which is
the two-homes failure D24 exists to prevent. The cap itself does not move — it
is a PCRE2-syntax number, exact under `limits.h`'s tiering — but the STACK COST
PER LEVEL grows by a module frame, which belongs in DD-10's account rather than
being action now.

**The payoff confirms the shape.** `(?i:...)` sets an option for its body only,
and D23/OS-1 already put caseless folding in the parser as parse-time state. So
`modifiers`' semantics are literally *set parse state, parse body, restore* — a
semantic that CANNOT be written without the callback. The simplest module is the
one that proves the callback is needed, which is a pleasant inversion of D28's
warning about shaping the interface on `modifiers` alone.

### `tail_default`, and row options have exactly ONE customer

Frank's proposal: give the function options from the row, and write a
`tail_default` recogniser that checks a literal tail as the lookup does today —
"at a minimum useful as a transition."

**Adopted, and kept permanently rather than as a transition.** Where a literal
prefix genuinely IS the whole shape, `tail_default` is the honest answer;
`(?<=` is exactly "`<` then `=`" and a bespoke function there is noise. What
makes it safe rather than a loophole is that the ambiguity guard polices it for
free: two `tail_default` rows whose tails are prefix-related both match, and
that is now a loud defect. ~~`\N` is the case that cannot use it. So the guard
forces a real recogniser exactly where a prefix is not the truth, and nowhere
else — and this is also what stops removing `tail` from forcing a rewrite of
seventeen rows in one change.~~

**[R10/C3-10 + C1-3 — the hazard is not prefix-related TAILS, and it is FOUR
buckets rather than one.]** It is a TAIL-LESS row sharing a bucket with tailed
rows: `tail_default(NULL)` claims everything in its bucket, so the bare row is
the problem wherever it appears. Enumerated from `registry.c`, every bucket with
more than one row has one — `\N`, `(?-`, `(?<`, `(?P` — so "and nowhere else"
understates the migration fourfold, and in two of those four the bare row's
verdict is the OPPOSITE of a sibling's, which is what makes the guard fire on a
correct table.

**Row options were evaluated for a second customer and there is none.** Frank
asked; the search was run against every family that shares an algorithm across
rows, and in each one the discriminator is data the function already has:

| shared algorithm | rows | what discriminates | needs an option? |
|---|---|---|---|
| class delimiter-pair scan | `:` `.` `=` | the row's `sel` | no |
| property recogniser | `\p` `\P` | polarity, from `sel` | no |
| relative subroutine call | ten digit rows | sign, from `sel` | no |
| verb name tables | one row | case of the first byte; the module's own tables | no |
| POSIX name set | one row | the module's own table | no |
| literal prefix | 17 tailed rows | THE TAIL STRING | **yes** |

So no generic option field is built. `const char *tail` stays exactly as it is,
and only its READER changes: today the lookup engine interprets it and applies
longest-wins; after MOD-0 it is a parameter one recogniser reads and the engine
never looks at it. D18's earn-its-axis rule applied to a struct field.

### A recogniser does NOT return the module

Frank: *"i also couldn't think of a value in having the function return the
semantic module."* Agreed, and the reason is D24's. The ROW names the module. A
function that could return a different one would be a second, contradictable
home for module attribution, which is tier 2 and EXACT under D26 — the `\v`
shape again. The recogniser answers "is this my shape"; the row answers "whose
is it". When one byte's shapes belong to different modules, those are different
ROWS, which is what `(?P<` / `(?P=` / `(?P>` already are.

### Where the line falls between DATA and CODE

Converting flags into functions moves knowledge from the declarative registry
into imperative code, which is a partial reversal of what D24 bought. The line:

- a flag stating a CITABLE FACT ABOUT THE CONSTRUCT stays data.
  `RF_CLASS_INVALID` — "PCRE2 forbids this inside a class, permanently" — is a
  claim about PCRE2, greppable and dumpable, and D27 measured what happens to
  facts that live only in code: they become invisible to tests derived from it.
- a flag meaning "CALL A SPECIAL SCANNER" becomes the recogniser pointer.
  `RF_OPTION_RUN` and `RF_CLASS_DELIM` are only that, and both retire.

`RF_CLASS_NAMED` is the hard case, being both. It stays as the fact, and the
recogniser reads it.

### What this retires, and what replaces it

Removing `tail` from the engine retires `check_tail_precedence` and the
shortest-first row-writing discipline. That is only a fair trade if the
ambiguity guard is worth more than they were, so it is specified rather than
assumed:

1. ~~**Runtime**: all recognisers in a bucket run; two non-DECLINE answers is an
   internal error. A runtime guard cannot narrow silently the way a check can.~~
2. ~~**Generated sweep**: uniqueness asserted over the generated input space, not
   only over the rows' own `syntax` probes.~~

~~Both, because a runtime check only fires on inputs someone actually compiles.~~

**[R10 — BOTH HALVES WITHDRAWN. `check_tail_precedence` is NOT retired until a
replacement demonstrably catches what it catches (C4-4, C4-5, C4-7, C1-4).]**

- **"A runtime guard cannot narrow silently" is backwards.** A check can assert
  it had something to OBSERVE — `check_tail_precedence` does exactly that
  (`registry_check.c:473-479`) and fails loudly when its subject disappears. A
  runtime guard emits nothing when it holds, so its success is indistinguishable
  from its absence. **The trade is a check that FAILS when it has nothing to
  watch, for one that PASSES when it has nothing to watch.**
- **The disarming edit is `break`**, it is silent, it is the natural performance
  edit, and this document supplies the pressure to make it in its own landmine
  section. `src/parse/CLAUDE.md` records the experiment already run: "reducing
  find() to first-matching-tail produced ZERO failures repository-wide".
- **Uniqueness is monotone toward DELETION.** One recogniser in a bucket is never
  ambiguous; zero never is. R5's recorded incident — deleting seven rows left all
  seven suites green while "the parser and the table AGREED IN UNISON" — is
  invisible to it. The project's answer to that was a HAND-WRITTEN manifest
  (`check_required_rows`), for the stated reason that a control must not share a
  source with the thing it controls.
- **Zero answers is not a defect under this rule at all**, so the guard cannot
  see the UNDER-promise — the failure mode this decision spends a whole section
  warning about.
- **The sweep half has no external oracle even in principle**, because libpcre2
  has no opinion about pcrec's buckets. And measured: today's four generated
  sweeps supply 0-2 bytes after the selector and land on ZERO of the 18 tailed
  rows, while the project's deepest generated suffix space is a hand-LISTED
  21-symbol alphabet (`pcre2_check.c:1687`) that excludes `)` and digits 1-9 —
  precisely what `-\d+)` needs. Citing wake §7's "generate, never list" to
  license a sweep that would be seeded from a list is the error, not the cure.

**The strongest replacement candidate, which is not in this decision (C4-6):**
*a row's own `syntax`, fed to its bucket, must be CLAIMed by exactly that row's
recogniser and by no other.* It is genuinely cross-source — `syntax` is data,
the recogniser is code, written at different times for different reasons — and
it delivers REACHABILITY and ATTRIBUTION in one assertion. It is the successor
to `registry_check.c:170-176`.

### Opportunities this opens, taken as part of MOD-0

**[R10 — the first two are WITHDRAWN AS CONTROLS (C4-1, C4-2, C4-3). Both may
exist; neither may be the check.]**

- **`--explain` never enters a doorway.** It is a mutual-prefix match of the
  query against the `syntax` COLUMN, printing other columns of the same row
  (`syntax_dump.c:225-274`; no `ext_` or `registry_find` reference in the file).
  **The worked example below does not run** — `--explain '(?i-m:'` reports "no
  construct matches". So MOD-0.7 is not "point an existing consumer at new
  fields", it is "replace a table self-join with a live invocation of the parser
  front half" — and once rewritten it prints `recogniser(query)`, so asserting on
  it asserts only that the recogniser agrees with itself. Demonstrated: swapping
  the module attribution between two rows of `--explain '(?<'` — a tier-2 error
  — leaves all three of tests/cli case10's assertions green, and the same
  sabotage on the `\N` rows passes four for four. The argument here applies wake
  §6's test (is there a reader) and skips §7's (**can the reader dissent**);
  `--list-syntax` already PRINTS all seven of §6's unread columns, so printing is
  the disease, not the cure. What WOULD be a control: print the ROW's declared
  attribution AND the recogniser's answer and assert they agree per row — the one
  cross-source comparison this design makes available.
- **Probes travelling with the module is co-location applied to a CIRCULARITY
  problem**, and drift and circularity have opposite cures. `pcre2_check.c:40-50`
  states the rule this scheme has no analogue for: the candidate POOL comes from
  libpcre2's own binary and every claim pcrec makes must be independently
  reproduced by it, *"without that last rule the pool can quietly become pcrec's
  own table"*. A corpus in the module's own `.c` is the author's list, so
  whatever libpcre2 says about each probe, **the SET is pcrec's** — D27's alphabet
  finding verbatim. Keep the corpus as DOCUMENTATION of a module's measured
  grammar; it may not be the differential's input set.

The third stands.


- **A module's PROBES travel with its recogniser.** D28 carried forward that a
  grammar and the measurements establishing it must not be separated, with
  R8/C2-9's drifted `LIMIT_*` rule as the counter-example. A module file
  exporting its recogniser AND its measured probe corpus lets the differential
  iterate modules and run each one's own probes — extending SR-1's "a new row
  covers itself" from rows to BODIES, which have no such coverage today.
- **`--explain` becomes the consumer that makes the port's output real.** Wake §6
  records seven RegRow columns that no check reads; a port with fields nobody
  consumes would be the eighth. `--explain '(?i-m:'` reporting what was
  recognised, the answer, the blame offset and the normalised name is a CLI
  surface reading every field, testable from tests/cli, rather than fields
  idling until semantics arrive.
- **`pcrec_ext_class_pair_opens` collapses.** It is a second copy of the
  delimiter scan, written for range endpoints (R9/SPEC-FA). Under recognisers,
  "does a construct open here" is "does any recogniser in this bucket not
  DECLINE" — and the duplicate is a copy of the exact scan K4 got wrong three
  times running.

### Landmines recorded before they are stepped on

- **The exact row count moves.** `registry_check.c` asserts 100 rows exactly,
  and collapsing ten digit rows to one changes it. R8/C4-10 measured that all
  three exact-count tripwires PRINT THEIR OWN REMEDY, and following that
  verbatim is how a real construct with a WRONG MODULE passes everything.
  Re-derive the number by measurement; do not apply the printed fix.
- **A row parse.c answers first would carry a DEAD recogniser** — `(?:` — that
  nothing ever calls. It needs an assertion, and it is the same claim SR-5
  exists to instrument.
- **The class-bracket doorway is on the base-tier path**, once per non-negated
  `[` (measured R6). Three recogniser calls against one lookup plus an inline
  scan is probably a wash, but SR-5 has not run, so MEASURE IT OR SAY NOTHING.

### Considered and rejected

- **Byte-SET rows.** The 12 option-setting rows exist only because a bucket key
  is one byte; a byte set collapses them to one row. Rejected: it discards
  twelve documented `syntax` probes and `note`s and narrows the 255-byte sweep,
  which is the silent-narrowing failure mode wake §7 names. Twelve rows sharing
  one recogniser keeps both.
- **Making the registry TOTAL over base syntax.** Tempting under recognisers —
  one table for every construct, and `\x{...}` and the possessive `+` stop being
  acknowledged exceptions living in parse.c. Rejected here: it touches the hot
  compile path and APPROACH assigns parse.c the base grammar. Recorded as a
  direction, not taken.

**Revisit when:** a construct needs a recogniser that cannot be pure — the first
real candidate would be one whose recognition genuinely requires allocation, and
`\p{...}`'s fixed buffer is the test of whether that case exists; or the
ambiguity rule proves too strict, the likeliest place being a MALFORMED body
that two modules both plausibly claim (`(?P` with a bad tail is the one to
watch), where libpcre2's error number is the arbiter and the recognisers get
tightened rather than the rule relaxed; or the base-tier path measurement (SR-5)
shows the all-recognisers-run cost is not a wash at the class doorway.

## D30 — 2026-08-11 — MOD-0's design, RESOLVED after R10: declared rank, an answer that is not an enum, and a bound compile mode

**Decided** 2026-08-11 (Frank), after the R10 panel refuted D29 in part.
**Supersedes** the sections of D29 marked WITHDRAWN; D29 stands as the record of
what was tried and why it failed, and its surviving spine is not restated here.
**Status:** adopted. MOD-0 builds it. Read D29's `[R10]` marks and
`docs/dev/reviews/2026-08-11-r10-mod0-design.md` first — this decision is only the
resolution of the seven questions R10 left open.

### 1. Resolution is by DECLARED RANK, and it is data

A row declares an integer `rank`. Every recogniser in the bucket runs; the
**highest-ranked ANSWERING row wins**; **two answering rows at EQUAL rank is the
registry defect**. Rank lives in the row, not in the function.

**What this fixes, and it is R10's central objection.** C1-1 showed that under
"exactly one may answer" the only way to keep the guard silent is to hand-encode
longest-tail-wins inside each recogniser — *"D29 retires the rule and keeps the
obligation"*. Under rank, **no recogniser needs to know its siblings**. The
bare fallback row honestly answering "always" at rank 0 is CORRECT rather than
naive, which dissolves C1-3 and C3-10 entirely, and precedence returns to being
DATA, which is the side of D24's line it belongs on.

**MEASURED before adopting, not argued** (scratchpad, against
`build/libpcrec.a`). Ranks were hand-assigned as 0/25/40/70 — deliberately NOT
`strlen(tail)`, so the mechanism cannot be tail length renamed — and rank-wins
was compared against today's engine over a generated depth-0..3 suffix space
across every multi-row bucket:

    multi-row-bucket probes:                   176544
    rank-wins AGREES with longest-tail-wins:   176544
    DISAGREEMENTS: 0    equal-rank collisions: 0    zero answers: 0

Both directions of sabotage were then run, because an unsabotaged green check is
worth nothing here:

    invert {U+ vs { .......... 1 disagreement / 176544
    fallback outranks all .... 21437 disagreements

**AND THE CAVEAT IS LOAD-BEARING.** Inverting the one genuinely prefix-related
pair is observable on **exactly one input in 176,544**. That is the same n=1
fragility `check_tail_precedence` documents in its own liveness clause. **The
liveness assertion is CARRIED OVER, not retired with the check it belonged to:**
if no probe in the space distinguishes a ranked pair, the rule is untested and
the check must say so rather than print a PASS.

> ## ⚠ SUPERSEDED IN PART BY **D32** (2026-08-11). §6 is DROPPED entirely;
> ## §1's rank survives as a LOCAL TIEBREAK; §2's check wording is FALSE.
> ## The refutations below are kept because they are the reasons.
>
> ## ⚠ PARTLY REFUTED BY THE R11 PANEL, 2026-08-11 — see
> ## `docs/dev/reviews/2026-08-11-r11-parse1-mod01.md`. §2's central sentence is
> ## FALSE and §1-2's checks are weaker than claimed. NOT YET RE-RESOLVED.
>
> Three measured refutations, all found before MOD-0.1 was built:
>
> 1. **§2's "pcrec must promise a module wherever libpcre2 DISPATCHES" is
>    false** — 93 counterexamples in 1,672 generated probes, and ALL 93 are
>    pcrec behaving CORRECTLY (REFUSE cases, base-tier constructs pcrec
>    implements, D25's `(*MARK)` answer). "Dispatched" does not imply a module
>    is owed; that needs the other two of §3's three facts. **§3 gets this right
>    and §2 ignores it two sections apart** — the same failure §3 diagnoses in
>    D29.
> 2. **Rank is almost entirely unchecked.** 20 of 22 rows accept ANY value up to
>    250 without any proposed check failing; the one prefix-related pair is a
>    single THRESHOLD, not a checked ordering (68 interior values pass). And the
>    per-row `syntax` check and the rank sweep fire on IDENTICAL boundaries in
>    all 5,632 probes — §2 requires both and one adds nothing.
> 3. **§1's "two answering rows at equal rank is the defect" HOLDS** (0
>    collisions over 3,507 probes on the correct table) — but module-swap and
>    row-deletion are invisible to both new checks, and `check_tail_precedence`'s
>    liveness obligation has no committed successor, so it cannot be retired.
>
> Also: the returning-doorway defect this decision never priced is FOUR call
> sites across three doorways, and `pcrec_ext_escape`'s pair is UNDEFINED
> BEHAVIOUR — making it return makes `build/pcrec` SIGSEGV on `[a\qb]`.

### 2. The per-row `syntax` check is the primary instrument (R10/C4-6)

*A row's own `syntax`, fed to its bucket, must be won by THAT row and by no
other.* Measured: 22 rows, and it is **TOTAL, terminating, needs no generated
space and no oracle** — the properties C4-5 noted the static `(sel,tail)` check
had and that a generated sweep loses. Against the same two sabotages it scored
1 and 18 failures, catching the mis-rank the 176k sweep caught by a single
probe.

It is the successor to `registry_check.c:170-176` and it delivers ATTRIBUTION
(C4-1's hole) and CANONICAL-FORM REACHABILITY in one assertion.

**What neither check covers, stated so it is not mistaken for covered.** C1-2's
reachability gap survives both: the per-row check proves a row wins its own
CANONICAL form, not that its recogniser is wide enough for a malformed body.
`-\d+)` declining on `(a)(?-1` (error 114) is still zero answers and still a
tier-2 regression. Closing it needs a PC-3-style differential with an external
oracle: **pcrec must promise a module wherever libpcre2 DISPATCHES.** That
differential is part of MOD-0.1, not an optional extra, and `-\d+)`'s collapse
does not land until it passes.

### 3. The doorway's answer is NOT an enum

R10/C2-8: the `(*` doorway already ships FOUR answers, adopted deliberately in
D25 and pinned in three independent places. `(*MARK)` is the forcing case —
PCRE2 recognises the name, so under D29's CLAIM row pcrec owed "requires module
'verbs'", and it deliberately does not. **One enum cannot carry "CLAIM the
construct but name NO module."**

So the answer is three independent facts, not one value:

    dispatched?   did PCRE2 recognise a construct here   (D28's axis, restored
                                                          as PRIMARY, not a
                                                          sub-distinction)
    compiles?     does PCRE2 accept the pattern
    message?      whose text: none / the row's / the name's own / the doorway's

The old three answers are just cells: CLAIM = (yes, *, row's), REFUSE = (no, no,
doorway's), DECLINE = (no, yes, none), `(*MARK)` = (yes, no, the name's own),
and C2-6's `[^]` = (no, no, but an option makes it valid) has a cell instead of
being an anomaly. The cost is that a doorway reads three fields instead of
switching on one: more code, less lore.

**Why D29 got this wrong is the methodological point worth keeping.** It derived
three answers from ONE doorway (`pcrec_ext_class_bracket`) — a sample of size
one — while citing D27 three sections later and applying it to the recogniser
SIGNATURE but not to the VERDICT. **The same document stated D27's rule and
broke it, two pages apart.** Apply D27 to every enumeration, not only to
signatures.

### 4. The compile MODE is bound, and it is PCREC's decision

R10/C2-1: REFUSE's "no module can ever make it valid" is measurably false —
`\U` and `\u` compile under `PCRE2_ALT_BSUX`, `\N{name}` under
`PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL`, and **1,896 of 8,960 generated
`\`-doorway patterns move from error to COMPILES under that one option.** The
`\` doorway holds ~60 of 100 rows, so this is most of a doorway.

pcrec therefore **writes down the mode it compiles for** — an explicit list of
the option semantics pcrec implements — and quantifies its verdicts over that.
`\U` is REFUSE **because pcrec will not offer `ALT_BSUX`**, which is a decision
pcrec can defend, rather than a false claim about PCRE2. This is cheap because
the option-dependence is a small nameable set (measured: `UTF`, `UCP`,
`CASELESS`, `MULTILINE`, `DOTALL`, `UNGREEDY`, `AUTO_CALLOUT` and every
`EXTRA_ASCII_*` flip NO construct verdict at all).

> **CORRECTION, 2026-08-11 (R13/C5-F14, verified independently by the author).**
> **`PCRE2_UTF` DOES flip a construct verdict**, so the parenthesis above is
> wrong about the first option it lists. Measured against libpcre2 10.46, with
> the UTF bit established behaviourally (bit 19, `0x00080000`, the bit that
> makes `\xff` raise "UTF-8 error: illegal byte"):
>
>     \N{U+0041}     opt=0  err 193    opt=UTF  COMPILES
>     [\N{U+0041}]   opt=0  err 193    opt=UTF  COMPILES
>
> And it is **K10's own construct** — the row this project has used as its
> worked example in D32, D33 and the extension design. The registry's own `note`
> on that row already says *"PCRE2 error 193 outside UTF mode, which is
> recognition, not rejection"*, so the table knew what this measurement denied.
> Two homes for one fact, one of them wrong — the shape the single table exists
> to prevent.
>
> **The methodological point is worth more than the correction.** R13's C2
> independently measured `PCRE2_UTF` as changing **0 of 120,099** verdicts and
> was RIGHT — its probe space was strings of length 1..3, which cannot contain
> a ten-character construct. Two correct sweeps, opposite conclusions, and the
> difference is entirely which family the generator could express. *Counting a
> population by a generator that cannot produce it counts the generator.*
>
> The rest of the list (`UCP`, `CASELESS`, `MULTILINE`, `DOTALL`, `UNGREEDY`,
> `AUTO_CALLOUT`, `EXTRA_ASCII_*`) is not disturbed by this, but it was
> established by the same method and should be re-swept over a space that can
> express multi-character constructs before it is relied on again.

**The quantifier ranges over five things, and D29 named none of them:**
construct, POSITION (`(*CR)` compiles and `a(*CR)` is error 160 — `verbs` will
make it valid, just not there), context flags, the bound MODE, and the PCRE2
VERSION. A row author deciding "is my row REFUSE" reads this list.

This also gives D26's upgrade rule something to bite on: a future PCRE2 adding
an option does not retroactively make pcrec's diagnostics lies, because they
were never quantified over every possible PCRE2 mode.

### 5. `p_alt` is fixed FIRST, as its own step

R10/C3-6 measured two defects that make `p_alt` unusable as a module callback:
the group node is ERASED (`(a|b)|c` and `a|b|c` generate byte-identical C), so a
`conditionals` port cannot recover the branch count PCRE2 needs for error 127;
and `cx->depth--` sits at `parse.c:266`, after the doorway call at `:259`, on a
path a module never reaches.

That work is **split out ahead of MOD-0** rather than absorbed into it. It is
base-grammar work on the hot path with its own regression risk, it is
independently testable (the AST-identity property is exactly what
`tests/codegen` pins), MOD-0 already carries four modules, and the callback
should exist BEFORE the first semantic port needs it rather than being
discovered mid-module.

### 6. The digit buckets are OUT OF REACH of a pure recogniser, and this is a stated exception

R10/C3-1, and `src/parse/registry.c:62-72` said so the day before D29 was
written. `\12` is octal or a backreference by running capture count, under
SCOPED `(?n)`, ignoring parens inside classes and inside `\Q...\E`; `\1..\9`
uses a whole-pattern count instead. That decides the MODULE, which is tier 2 and
EXACT.

Widening the signature to carry parse progress is REJECTED: purity is what makes
a recogniser usable as a predicate (`pcrec_ext_class_pair_opens` is the existing
customer), and that is the more valuable property.

So: **the digit buckets' recognisers answer SHAPE only, and their module
attribution is explicitly deferred to the SEMANTIC port**, which holds `Ctx` and
therefore holds the count. This is the one place D29's "the ROW names the
module" rule genuinely fails, and it is recorded as an exception with its reason
rather than left as a gap for MOD-0.4 to rediscover.

### 7. `classes` is built BEFORE `modifiers`

R10/C2-11: at options = 0, `[a- ]` is error 108 while `(?xx)[a- ]` COMPILES,
because `xx` deletes the space — at the class range endpoint `3fca0d8`
(SPEC-FA) fixed one commit before the panel. **pcrec is safe today only because
`(?x)` is rejected outright as unimplemented: the guard IS the
unimplemented-ness**, and building `modifiers` removes it.

The original order built `modifiers` first as the cheap module that would shape
the interface. The interface is being redesigned anyway, so that reason is
spent. The module that OWNS the class doorway is built before the module that
can change its lexing.

### 8. K10 ships known, scheduled with `unicode-props`

`[\N{U+41}]` is answered "not valid inside a character class" where libpcre2
recognises it (error 193, every class position). The fix is removing one flag;
the TEST is the work, because the in-class sweep's template supplies one byte of
tail and `registry_check.c:875-876` exempts `RF_CLASS_INVALID` rows from that
sweep anyway. Fixing the flag alone would leave the same four blind nets for the
next reader.

Accepted cost, Frank's call: `tests/reject/` stops carrying zero known-wrong
pins, which it had reached for the first time at R9. Recorded in
docs/dev/known_issues.md as K10 and scheduled with MOD-0.6.

**Revisit when:** a bucket needs two rows to win at once (rank makes that a
defect by construction, so the first real instance is a genuine falsification);
or the reachability differential in §2 turns out not to cover the malformed-body
class, which is the one gap this decision leaves open by design; or pcrec grows
a compile-option surface, at which point §4's bound mode becomes a set rather
than a point and every REFUSE is requantified.

## D31 — 2026-08-11 — PARSE-1: `p_alt` REPORTS what it already computed; the group node stays erased

**Decided** 2026-08-11, after a design panel (four lenses) against a written
candidate design. **Implements** D30 §5. **Partly corrects** R10/C3-6, which is
the point of the entry.

### The diagnosis in R10/C3-6 and D30 §5 was partly wrong

R10: *"a `conditionals` port calling `p_alt` back cannot recover the top-level
branch count."* True only of recovering it FROM THE AST AFTER THE FACT. **`p_alt`
always computed the number and threw it away** — `p_atom` consumes a whole group
as ONE atom, so the erasure at the group case sits strictly BELOW `p_alt`'s
top-level loop and cannot perturb its count. `(?(1)(a|b)|c)` counts 2;
`(?(1)a|b|c)` counts 3.

**The group node being erased is real, and it is not what blocks error 127.**
Building an `A_GROUP` wrapper on that reasoning would have been building a node
to fix a problem it was mis-diagnosed into. The erasure STAYS.

### The class this had to cover, measured rather than assumed

32 construct families that take a nested pattern body x 29 generated bodies =
928 probes, libpcre2 10.46, options = 0. Exactly two families' verdicts depend
on the body's top-level structure, and they are the same fact at two thresholds:
conditionals (all 13 condition forms) error 127 above TWO branches, and
`(?(DEFINE)` error 154 above ONE. Empty branches count; `|` position never
matters; verified to 50 branches. Branch reset `(?|...)` has no limit at all.

A panel critic then found the sweep had omitted `modifiers` — **this project's
own next-in-line consumer of the interface being designed** — and closed it
(36 probes, no dependency), plus two missing verb spellings (27 probes, held).
Benign outcome, real method gap: D27's alphabet lesson applies to a set the
author generated as much as to one they listed.

### What is built

1. **`p_alt` reports `AltInfo {nbr, last_bar}`.** A STRUCT, not an `int`, and
   the panel is why: `ctx_fail(cx, pos, ...)` takes a POSITION as a REQUIRED
   argument, so a module cannot RAISE "more than two branches" from a count
   alone. D26 puts pcrec's own offsets against pcrec's own convention in TIER 2
   — only chasing PCRE2's specific number is tier 3 — and `Ast` has no position
   field, so leaving the AST alone forecloses recovering one later. One `size_t`
   at the site that already touches `cx->pos` costs what the count costs.
2. **The group case is split** into `p_group` (entry/exit bookkeeping) and
   `p_group_body` (everything between the parens, owning neither end), so a
   module handler that returns cannot skip the exit. The longjmp bypass is
   correct STRUCTURALLY: compile.c holds the only `setjmp`, its failure branch
   cleans up and returns, and `Ctx` is stack-local and zeroed per call.
3. **`caseless` moved into `Ctx`**, seeded once from the const caller-owned
   `opt`, and saved/restored around every group body. Measured 17/17 against
   libpcre2: `(?i)` inside a group holds to the end of THAT group, **leaks
   across its sibling alternation branches** (`(a(?i)b|c)d` matches `Cd`), and
   restores at the immediately-enclosing `)`. So the restore belongs at the
   group boundary in the BASE GRAMMAR — the parser must not need to know a
   module fired. This defect was not in R10's list; it was found by asking what
   `modifiers` needs, which is D27's method applied to a design.

### What is NOT built, recorded so it is not rediscovered

**A doorway that returns a node still has its node silently DISCARDED** —
control falls through into the body parse and nothing distinguishes "handled"
from "carry on". PARSE-1 fixes the depth SYMPTOM; the control shape is MOD-0.1's.
`pcrec_ext_class_bracket` is the shipped precedent for declining (`ext.c:383,471,474`,
and it alone of the four is not `noreturn`), so MOD-0.1's contract derives from
that or justifies differing.

### The checks, and the one that had to be thrown away

`tests/parse/`. The count is compared against an INDEPENDENT reference counter
(a flat byte scan, not a transcription of `p_alt`), which **libpcre2 arbitrates**
through its 127/154 thresholds — for two constructs pcrec does not implement,
which is exactly PC-3's shape of checking before the customer exists. 16,384
bodies, 32,768 arbitrations, zero disagreements. Three sabotages of `p_alt`
itself were verified caught (12,288 failures each) before the commit.

**The check the design ORIGINALLY proposed was refuted and demoted.** Asserting
`(a|b)|c` == `a|b|c` in emitted C is passed by a build containing NONE of
PARSE-1 — the property held before the feature existed, and candidate B's whole
design is that the AST does not change. It is kept as a FORWARD-pointing
regression net (a later naive `A_GROUP` trips it) and may never be cited as
evidence PARSE-1 is present or correct.

**Two properties are SKIP-shaped, not `check_tail_precedence`-shaped**, and the
panel corrected the citation before it was built: `check_tail_precedence` calls
`bad()` (exit 1) when its subject vanishes because the property WAS live and
going dead is a regression. Depth balance and caseless scoping were NEVER live —
they need code that does not exist — so wiring them to `bad()` would have left
`make test` permanently RED from PARSE-1 until MOD-0.2. `pcre2_check.c`'s
loud-SKIP-exit-0 is the right precedent, and both print on every run.

### Costs measured, including a claim of the author's that was false

Candidate A (`A_GROUP` wrapper) was rejected on measurement. It does NOT cost
throughput: the D9 trie is output-preserving, so `(alpha|beta|...)` emits
byte-identical C with and without it, and the author's first inference that bench
case (d) would regress was simply wrong. It costs pcrec's OWN COMPILE TIME —
15x on a 300-branch shared-prefix alternation — and only where a group wraps a
PROPER SUB-RUN of an outer alternation, since a whole-alternation wrap sits above
the spine and a pass-through case recurses. A panel critic then showed `make
bench` DOES time pcrec's own compile in two of three sections, so the author's
reason for saying bench could not catch this was also wrong; bench simply
contains no pattern of the regressing shape, which is a gap closeable by adding
one.

**Revisit when:** a construct needs a nested body's structure BEYOND its
top-level branch count (the 928 probes say none does today); or a module wants
a per-branch position rather than the last separator, which `AltInfo` can carry
without changing shape; or MOD-0.1 settles the returning-doorway contract, at
which point the two SKIP-shaped properties become observable and must be
promoted from SKIP to real assertions.

### D31 ADDENDUM — 2026-08-11, the R11 panel's late material, arriving AFTER the commit

**Process first, because it is the finding about the process.** `0ebbdc7` was
committed with C2's findings file at 53 lines. It finished at **680**. Three of
four critics in this panel delivered their bulk after being read, and one
delivered after the COMMIT — which is R8's recorded failure ("do not close a
checkpoint until the reports are in hand") reproduced despite R10 adding the
re-poll rule and despite that rule being applied twice successfully in the same
session. The re-poll must extend PAST the commit, or the rule only moves the
cliff. Everything below is a follow-up commit, not an amendment.

**1. `p_alt` had NO LINKAGE, and that was PARSE-1's stated purpose (C2-8).**
`p_alt`/`p_alt_info` are `static` to parse.c, so `ext.c` cannot call either, and
`pcrec_parse_info` is the WRONG entry point for a nested body — it requires
end-of-pattern and ctx_fails on `)`. A module handed it fails on every body.
Fixed: `pcrec_parse_body(Ctx *, AltInfo *)`, which parses a body and stops AT
its terminator without consuming it. The step titled "make `p_alt` a usable
module callback" had fixed the count, the depth and the parse state, and left
the callback uncallable.

**2. The contract guidance shipped in `0ebbdc7` was WRONG (C2-5, C2-10).** It
said MOD-0.1 should derive `pcrec_ext_group`'s contract from
`pcrec_ext_class_bracket`'s "or justify differing". The justification exists and
the answer is DIFFER: the two doorways' non-fail outcomes are **disjoint**.
class_bracket's three `return;` sites never write `cx->pos`, so its only
normal-return outcome is DECLINE with the cursor unchanged. The `(?` doorway can
never decline at all — `registry.c:505`'s catch-all is `REJECTED` — so its only
future normal-return outcome is CLAIM, cursor past its own `)`. One signature
over both would make "returns normally" mean opposite things by doorway, which
is D30 §3's "the answer is not an enum" one level up. Corrected in parse.c.

**3. The silent-discard defect is REPRODUCED, and it is an exit-0 miscompile.**
Give `pcrec_ext_group` one selector byte that returns a node instead of failing,
and `(?%x)b)` compiles to byte-identical C to the bare pattern `b` — the
module's node AND the pattern's own unmatched trailing `)` both vanish with no
diagnostic. Still MOD-0.1's to fix; now recorded with its repro rather than as a
hypothetical.

**4. "These two checks cannot fail today" was FALSE (C2-9).** A fixture doorway
gated on a selector byte no registry row uses makes depth balance observable NOW
with no module. So the SKIP-vs-`check_tail_precedence` question was the wrong
question for these two: they are UNOBSERVED, not unobservable. The runner's text
is corrected, and MOD-0.1 should ship real checks rather than either precedent.

**5. The depth cap and balance are now asserted, and the ordering is the
lesson.** Cap: 250 accepted / 251 rejected, both sides, for `(...)` and
`(?:...)` — C2 measured the same boundary over 780 generated probes. Balance:
sequential groups before a deep nest, and long sibling runs. **The cap probes
alone were measured BLIND to a double-decrement** — a purely nested pattern only
tests the cap on the way IN, and a leaked decrement fails OPEN. That blindness
was found by sabotage, not by foresight; the balance probes exist because of it.
All four sabotages (double-decrement, no-decrement, no-increment, off-by-one
cap) verified caught.

**Also recorded, not acted on:** C3 measured that `(?^)` resets past a
compile-time `PCRE2_CASELESS` — it is reset-to-hardwired-constant, not
restore-to-saved-value and not restore-to-`opt` — which is a landmine for
`modifiers`, not for PARSE-1. And 3 of 8 scoped options fit the "bool at a fixed
site" shape; `(?x)`/`(?xx)` need a pervasive lexer change and `(?n)`/`(?J)` need
capture/name infrastructure that does not exist, so `Ctx`'s scoped-state slot
should be expected to grow a struct or bitmask rather than more bools.

## D32 — 2026-08-11 — MOD-0's interface, RESOLVED: a row names a PARSER FUNCTION; rank is a LOCAL tiebreak; purity is PER-DOORWAY

**Decided** 2026-08-11 (Frank), after three panels — R10 (refuted D29), R11
(refuted parts of D30), R12 (a comparative panel on the alternative). **Amends
D30**, whose spine survives; **drops D30 §6 entirely**; **supersedes** D29's
two-port split. Read D30's inline R11 warning block, R11 and R12 first — this
entry is the resolution, not the argument.

> **AMENDED IN PART BY D33 (2026-08-11). Read D33 before building from this
> entry.** D32's spine stands — a row names a parser function, rank is a local
> tiebreak, purity is per-doorway — but three things change. A row names **two**
> functions, one per POSITION, not one. §6's "the terminal outcome is exactly
> what `ext.c` does today" is **false as written**: `ext.c` raises by `ctx_fail`,
> which longjmps, and D33 requires the claim to be RETURNED so a caller can see
> it before the diagnostic fires. And §5's claim that the class doorway needs a
> speculative pure predicate is **withdrawn** — `pcrec_ext_class_pair_opens` is
> deleted, because it was necessary only while the construct's error could
> escape past its caller.

### 1. A row names ONE PARSER FUNCTION, which is a continuation of the parser

Not D29's pure recogniser plus a separate semantic port. **One function per row**,
taking `Ctx *`, which decides whether the text is its construct and — once its
module is implemented — parses it, recursing through `pcrec_parse_body` for a
nested body.

**Why the two-port split is dropped.** It was justified by a type-level boundary
between deciding and building. That boundary bought less than it cost:

- its hand-off contract was **already wrong** before anything was built —
  `head_len` assumes every recogniser's `at` sits after the selector byte, and
  `RF_OPTION_RUN` rows start AT it (R11/M1);
- "the semantic port begins exactly where the head ended, ASSERTED" **named no
  mechanism**: `src/` contains zero `assert()` calls;
- `span_at`/`span_len` had **no consumer at all**, present or named-future —
  D24/SR-2's own recorded hazard, *"lost more to unexercised structure than to
  missing structure"*;
- and it forced D30 §6's exception (below), which the one-function model deletes.

### 2. Functions are POSITIVE and LOCAL — and this is the crux

Each function recognises **its own proper form and knows nothing about its
siblings**:

    \N{U+…}   "does the text start with `{U+`?"
    \N{name}  "does it start with `{`?"
    \N        "am I `\N`?"   — trivially yes

**The elimination is done by RANK, not by each function re-deriving it.** The
bare row answering "always" is **CORRECT**, exactly as D30 §1 said, and the
author's counter-proposal — write disjoint forms so `\N` reads *"N not followed
by `{`"* — is WORSE and was rejected: it puts negative knowledge of every
sibling into every function, so adding a `\N[` form tomorrow means editing a
function that never mentioned `[`. That is precisely what rank exists to
prevent.

**Multiple functions answering is NORMAL, not a defect.** D29's "exactly one may
answer" stays retired (R10/C1-1). **Two ANSWERING rows at EQUAL rank is the
defect**, reported as an internal error — measured not to fire on the correct
table: 0 collisions over 3,507 generated probes across all four buckets.

### 3. Rank is a LOCAL TIEBREAK, not a global order

Rank exists **only where rows clash** — measured: four buckets, 22 rows. The
other 78 rows are alone in their bucket and carry no meaningful rank.

**This dissolves R11/M3's finding rather than repairing it.** M3 measured "20 of
22 rows have completely unconstrained rank values" and the author read it as a
hole. It is not: rank only means something between clashing rows, so the 20 are
rows whose value genuinely does not matter, and nothing should pretend to
constrain it. What IS constrained is what needs to be, and the per-row `syntax`
check does it for free — feed `\N{U+0041}` to its bucket and if bare `\N`
outranked `\N{U+`, bare wins and the check fails.

### 4. RANK, not ORDER — and the difference is measured

Declaration order was proposed as the rule (it is stated exactly, so nothing
stands in for anything). **It is refuted, on the shipped table, with no edit
required** (R12/P2):

- `registry.c:242`'s tail-less `\N` is declared FIRST, so first-match hands it
  `\N{U+0041}` — **16 of 17 boundary probes wrong**;
- pin the fallback last and `"{"` (`:254`) still precedes `"{U+"` (`:257`) —
  **7 of 17**, including the canonical example.

And the irony is exact: `src/parse/CLAUDE.md:166` records those rows are written
SHORTEST-first *deliberately*, so `check_tail_precedence` would have a real
prefix pair to observe. **The hardening that made the old check meaningful is
what breaks the new rule.**

**The decisive property is blast radius.** Rank travels with the row; order is a
property of the file:

    adjacent swaps (the realistic minimal edit)    4 of    96 load-bearing
    arbitrary swaps (any two of 100 rows)        520 of 2,308 (22.5%)

The 520 is real, not a harness artefact: swapping an UNRELATED row with one
inside a bucket's span moves that bucket member out of relative order and drags
the unrelated row in — corrupting the bucket **as a side effect of where the
swap LANDS**. Rank's hazard is confined to the row whose value is wrong; order's
can implicate rows never touched.

### 5. PURITY IS PER-DOORWAY, and D30 §6's digit exception is DROPPED

D30 §6 declared the digit buckets out of reach: `\12` is octal or a
backreference by a running capture count, so *"their module attribution is
explicitly deferred to the SEMANTIC port"* — a wart on a property D26 makes
TIER 2 and EXACT. It shows today: pcrec answers `\12` with a hedged
*"\1 (backreference/octal) requires module 'backrefs'"*, one module named for
two constructs.

**A parser-continuation function has the running count, so it just decides.**
The exception disappears rather than being documented.

**The trade D30 made was bad, and the reason is structural: purity was made
GLOBAL when it is needed at exactly ONE doorway.** The class doorway needs a
pure decide phase for `pcrec_ext_class_pair_opens`, the parser's only
speculative customer. The escape doorway needs the capture count. **Different
doorways — they never conflict.** D30 paid for global purity with an exception
at a doorway that never needed it.

Deciding is pure everywhere it must be, measured rather than assumed: an
instrumented arena over the REAL `pcrec_compile`, forcing an unbounded declining
delimiter scan, allocated **18 calls / 318 bytes identically at N = 1,000 /
100,000 / 2,000,000** — zero growth with scan length (R12/P1).

**Two counters are owed, not one** (R11/C3-2, re-measured here): `\ddd` uses the
count SO FAR — which the function has. `\1..\9` uses the WHOLE-PATTERN count, a
forward reference: `\8` followed by eight groups COMPILES, seven does not. No
already-built state reaches that; it needs a pre-scan. `[MOD-STATE]` owns it,
unchanged. `p_group_body` already carries the hook comment at the one place a
capturing `(` is known.

### 6. The terminal outcome is the ROW'S EXISTING VOCABULARY, not a uniform enum

A three-outcome protocol (NOT_MINE / PARSED / UNIMPLEMENTED→render the module)
was proposed and is REJECTED (R12/P3). It holds at one doorway of four:

- **it would resurrect a bug FIX-2 removed.** The class `:` row has FOUR live
  terminal shapes — `[[:alpha:]]` (module), `[:alpha:]` (`open_msg`, no module),
  `[[:foo:]]` (bad name), `[x[:<:]]` (wrong position). Rendering "requires module
  'classes'" mechanically is the exact over-promise FIX-2 removed, for **three of
  its four shapes**;
- module-shaped outcomes are a **minority even at the escape doorway** — ~18 of
  41 rows;
- `NOT_MINE` is **structurally unreachable at VERB** (one row, one unconditional
  call site, nothing to hand back to), and `(*)` fits none of the three.

So the outcomes are **NOT_MINE / PARSED / TERMINATED**, where TERMINATED's
message is selected by the row's existing `RD_MODULE` / `RD_FIXED` / `open_msg`
vocabulary and D25's four `(*` answers — **i.e. exactly what `ext.c` does
today**. This is what keeps D32 a change to how a row is SELECTED and not to
what happens after.

### 7. `sel` survives, DEMOTED from key to checkable pre-test

`sel` becomes a cheap filter — "don't call me unless the byte matches" — and the
function is the truth. Which makes `sel` **redundant, and redundancy is
checkable in a way a key never was**: for every row with a non-null `sel`,
assert its function **returns exactly `NOT_MINE`** for every input whose first
byte differs.

That wording is deliberate. "Does not return PARSED" would pass vacuously for
all 100 rows today, since every row is a stub — R11/C4-1's failure shape
(a check whose pass condition holds before the feature exists) and it was caught
in review (R12/P4).

### 8. What is NOT adopted, recorded so it is not re-proposed

- **Trial mode** — a `Ctx` copy plus a flag tripping `arena_alloc`/`ctx_fail`.
  REFUTED by building it (R12/P1): the loop commits only after the function
  RETURNS, so any construct with a body must allocate inside the trial-covered
  call, aborting every CORRECT implementation. A real handler must therefore
  clear the flag — one line, on mutable state it owns — and the trip did not
  fire. It also buys **nothing** over design A for its own motivating customer,
  since `pcrec_ext_class_pair_opens` is safe to call speculatively only because
  it is already pure. And the arena leak is not benign: **~76-80 bytes per byte
  scanned, 76.4 MB at N = 1,000,000**, unreachable from the real `Ctx` so
  `arena_free` frees none of it.
- **One function per BUCKET** (the author's synthesis after P2 killed order). Not
  needed: §2's positive-functions-plus-rank removes the arbitration problem it
  was invented to solve, and it would have cost D24's "add a row and nowhere
  else" in four places.
- **Disjoint proper forms with no rank** (the author's, §2) — worse, see §2.
- **Declaration order as the rule** — §4.

### 9. Checks

1. **the per-row `syntax` check** — a row's own `syntax`, fed through the REAL
   dispatch, must be claimed by THAT row. TOTAL over 22 rows, terminating, no
   generated space, no oracle. **Primary**, and it constrains exactly the rank
   orderings that matter (§3).
2. **equal-rank collision detection** at dispatch — an internal error.
3. **`sel`-redundancy**, worded per §7.
4. **the reachability differential** — D30 §2's wording *"pcrec must promise a
   module wherever libpcre2 DISPATCHES"* is FALSE and is NOT adopted: 93
   counterexamples in 1,672 probes, all of them pcrec being correct, confirmed by
   three independent harnesses. The rule is a RESIDUE assertion, and its
   definition needs a FOURTH category beyond base-tier / `RS_REJECTED` / D25's
   answers, because **46 of the 93 (49%) come from neither a row nor D25** —
   there is no registry row at all for `\U`/`\u`/`\F`/`\L`/`\l`. Baseline to
   beat, measured: **2 of 4 buckets have any live external coverage, 0 of 4 have
   complete coverage of the malformed-body class, `\N` has none.**
   Classifier requirements: THREE-way, and it must name **every doorway's**
   no-construct code — including **103** at the escape doorway, which R11
   published a criterion without.
5. **the rank sweep is a MIGRATION SCAFFOLD, not a permanent check.** Its oracle
   is the engine it replaces, and MOD-0.2 deletes that engine. Build it, run it
   through the migration, and **delete it in the same commit that removes `tail`
   from the lookup engine.**

`check_tail_precedence` is NOT retired until its liveness obligation has a
committed successor — R11/M3 located the natural one, a "did any generated probe
have more than one matching row" counter, baseline nonzero per bucket
(111 / 333 / 333 / 2730).

### 10. Known to be unguarded by BOTH designs, stated rather than implied

Module swap between two rows, and row deletion. `tests/reject/`'s hand-written
manifest remains their only guard, unchanged by this decision. Do not let §9's
list imply otherwise.

**Revisit when:** two rows in one bucket genuinely need the same rank (the rule
makes it a defect by construction, so the first real instance is a falsification);
or a doorway other than the class bracket acquires a speculative customer, at
which point per-doorway purity needs restating; or `[MOD-STATE]` lands the
whole-pattern capture count, which is the only part of §5 this decision does not
resolve.

## D33 — 2026-08-11 — ONE table, TWO PORTS per row: a class port returning a set, an AST port returning a node; the claim is RETURNED, not raised

**AMENDED IN PART BY D34 + extension_design.md PART II (2026-08-11, same
day). Two numbered sections below are FALSIFIED — this entry's own
revisit-when fired.** §4's position-independent arbitration: R13 measured
`\12` selecting a different row by position (backreference at atom, octal in
class, same count); replaced by PER-PORT recognition, Part II §14. §6's
static shape-column endpoint rule: R13/R14 measured the DOORWAY deciding, not
the shape; replaced by evaluate-first with one deviating cell, Part II §16.
The rest of this entry stands. Read D34 before building from it.

**Decided** 2026-08-11 (Frank), in conversation, refining D32 rather than
replacing it. D32's spine is untouched: a row still names a parser function, rank
is still a local tiebreak, purity is still per-doorway. What changes is that a
row names **two** functions, one per POSITION, and that a doorway's terminal
answer is a value the caller receives rather than a `ctx_fail` that longjmps past
it. **Supersedes D32 §5's claim that the class doorway needs a speculative
predicate**, and deletes `pcrec_ext_class_pair_opens`.

### 1. The shape

One row per construct. Two function references on it:

    class port   parses the construct INSIDE `[...]`  -> a set (or a scalar)
    AST  port    parses it OUTSIDE a class            -> an Ast *

Two tables — one keyed for class context, one for atom context — was considered
and rejected. The two tables' OVERLAP is exactly the escape doorway's
class-shaped rows, and **that overlap is where K10 lives**: K10 is one construct
whose class-position facet (`RF_CLASS_INVALID`) contradicts its own
atom-position `note`. Split it across two independently-keyed tables and that
contradiction becomes two rows with nothing forcing them to agree — the same
failure one level up, and harder to check, because there is no longer a single
object to compare against itself. Related data stays together.

### 2. The AST port of a class-shaped construct is a GENERIC WRAPPER

Not one function per construct per position. `char_node` (`parse.c:76-82`)
already normalises a literal to a singleton `A_CLASS` node, `internal.h:42`
records that literals ARE singleton classes, and codegen emits membership tests
from `cls[32]`. So "the code to check whether the piece belongs" is not
something an AST-port function writes — it is what the backend already does with
a bitmap.

Therefore the AST port for every class-shaped row is ONE shared wrapper that
calls the class port and wraps the result in an `A_CLASS` node. And for the ten
character-type escapes (`\d \D \w \W \s \S \h \H \v \V`) the class port is
DATA — a bitmap plus a negate flag — read by one shared handler. Not two
functions per class; not even one function per class.

### 3. A NULL class port means exactly one thing, and `\b` is what makes that true

Measured 2026-08-11 against libpcre2 10.46:

    [\A] [\Z] [\K] [\R] [\X]   err 107  escape sequence is invalid in class
    [\N]                       err 171  \N is not supported in a class
    [\b]                       COMPILES — backspace 0x08

Today `ESC_CLASS_BASE` (one row, `\b`, `registry.c:261`) and
`ESC_CLASS_INVALID` (10 rows) BOTH amount to "the class doorway is not taken",
for opposite reasons: `\b` because the base grammar answers first
(`parse.c:152`), the other ten because PCRE2 forbids them permanently. A NULL
port cannot say both.

**Resolution: `\b`'s class port returns `EXT_SCALAR 0x08`.** Then a NULL class
port means exactly one thing — *no module, permanently invalid in a class* — and
this decision deletes `parse.c:152`'s special case, `RF_CLASS_BASE` and
`RF_CLASS_INVALID` together. **K10 becomes structurally unrepresentable**: there
is no flag left to contradict the behaviour, because the presence of the
function IS the answer and the dispatcher uses that same object.

> **HALF-FALSIFIED IN EXECUTION (MOD-0.3d, 2026-08-12 — R16 docs critic
> flagged the missing mark).** RF_CLASS_BASE retired exactly as written;
> RF_CLASS_INVALID did NOT, because this section's precondition — "a NULL
> class port means exactly one thing" — is measurably false before the
> port population is total: the lexical rows' class_expect is "err 106"
> for probe-shape reasons ([\Q] quotes the closing bracket) and
> unicode-props' rows carry honest NULLs that mean "awaiting MOD-0.6",
> not "permanently invalid". Retirement rescheduled to MOD-0.6; K10 is
> accordingly still OPEN and still representable until then. The measured
> record is the 2026-08-12 journal entry and e38ce62's commit message.

`\N`'s wording differing from the other nine (171 vs 107) is TIER 3 under D26
and is deliberately not modelled.

### 4. Arbitration is POSITION-INDEPENDENT; only the port consulted differs

Measured on the `\N` bucket, the only prefix-related tail pair in the table:

    [\N]        err 171   bare row wins, class port NULL      -> refuse
    [\N{name}]  err 137   {name} row wins, class port present -> same answer as outside
    [\N{U+41}]  err 193   {U+}   row wins, class port present -> same answer as outside

So it is NOT "filter to rows that have a class port, then rank". It is
**arbitrate exactly as today, then consult the winner's port**; a NULL port is a
REFUSAL, never a reason to select a different row. This matters because the
other reading silently re-ranks the bucket at class position and would make
`[\N]` answer `\N{name}`'s error.

Consequences: `check_tail_precedence` and D32 §2's equal-rank-is-a-defect rule
are unchanged, one `rank` column still suffices, and a new invariant becomes
checkable — **the same row must be selected at both positions.**

### 5. THE LOAD-BEARING CHANGE: a claim is RETURNED, not raised

D32 §6 said the terminal outcome is "exactly what `ext.c` does today", and what
`ext.c` does today is `ctx_fail`, which longjmps. **Everything in this entry
depends on that stopping.** A handler must return its claim — including a claim
that carries a diagnostic — so the caller sees the claim before the diagnostic
fires and can override it.

    typedef enum { EXT_NOT_MINE, EXT_SCALAR, EXT_MEMBERS, EXT_NODE } ExtWhat;

    typedef struct {
        ExtWhat what;
        int     scalar;   /* EXT_SCALAR:  a code point — the ONLY shape legal
                             as a range endpoint */
        Ast    *node;     /* EXT_MEMBERS: A_CLASS whose cls[] the caller ORs in
                             EXT_NODE:    a subtree the caller splices in */
        /* plus the pending diagnostic for a claim that terminates */
    } ExtResult;

**Blast radius, counted rather than estimated: 23 `ctx_fail` sites, all in
`ext.c`.** `parse.c`'s 20 and `compile.c`'s 4 are base grammar and are not
touched. A diagnostic must become representable instead of raised — `ctx_fail`
is printf-style varargs — so this needs either a formatted buffer on `Ctx` at
claim time or the row plus enough context to format later.

**This is the piece to attack.** If a diagnostic cannot cleanly outlive its
handler, `pcrec_ext_class_pair_opens` comes straight back and §6 collapses.

### 6. The range-endpoint rule falls out, and `pair_opens` is DELETED

D32 §5 justified a speculative pure predicate at the class doorway. That
justification was **wrong, and the reason it looked right is worth keeping**: at
an endpoint PCRE2's "invalid range" beats the construct's own diagnostic, so
parsing the construct first appeared to lose the right answer —

    [0-[:foo:]]  err 150 invalid range    vs  [[:foo:]]  err 130 unknown POSIX class name
    [0-[.ab.]]   err 150 invalid range    vs  [[.ab.]]   err 113 collating not supported
    [0-[=x=]]    err 150 invalid range    vs  [[=x=]]    err 113

— but only because the construct's error ESCAPES by longjmp. Once a claim is
returned (§5), the endpoint caller sees the claim first and overrides.

**The rule is two questions: did anything claim (run the port), and is the ROW'S
SHAPE set-valued (a static column).** Verified against every case measured
2026-08-11:

    [0-[:digit:]]              claims, set        -> 150   PCRE2 150
    [0-[:foo:]]                claims, set, bad name -> 150 PCRE2 150
    [0-[.ab.]] [0-[=x=]] [0-[:<:]]  claims, set   -> 150   PCRE2 150
    [0-[a]  [0-[:]  [0-[:digit]  [0-[.]  declines -> literal, compiles   PCRE2 COMPILES
    [0-\d]  [0-\p{L}]          claims, set        -> 150   PCRE2 150
    [0-\N{U+41}]               claims, SCALAR     -> its own 193         PCRE2 193
    [0-\q]                     no row, not claimed -> escape's own error PCRE2 103

The shape must be a STATIC column, not a parse outcome: `[:foo:]` is
set-shaped-but-invalid and still yields 150, while `\N{U+41}` is scalar-shaped
and its own mode error stands. The shipped code needs `pair_opens` precisely
because it has no way to ask the second question and hard-codes the answer for
one doorway.

**This also closes K12** (`[0-\d]` answered "requires module 'classes'" where
PCRE2 says invalid range): SPEC-FA implemented the endpoint rule for the BRACKET
shape only, and pcrec is correct today only because `\d` is refused before the
range code can look at it — the guard IS the unimplemented-ness, exactly as
`docs/dev/plan.md:577` warns for `(?xx)[a- ]`. Under a shape column, one rule covers
both shapes.

### 7. The class structure is 8-BIT NOW, and MOD-0.6 owns widening

`uint8_t cls[32]`, matching the `Ast` node today. `\p{...}` needs more than 256
bits and `\v` under UTF reaches U+2028/2029. Designing the wide form now is the
unexercised structure D24/SR-2 warns about ("lost more to unexercised structure
than to missing structure"); leaving it unsaid is how MOD-0.6 discovers it.
Stated here so it is a decision.

> **AMENDED 2026-08-12 (Frank, thirteenth session).** Widening DEFERS to the
> first milestone that PRODUCES a wide set (M5-era `\p` matching). MOD-0.6 as
> scoped in plan.md is recogniser-only — no producer lands, so a widened
> structure built there would itself be the unexercised structure this section
> warns about. Ownership split: MOD-0.6 owns the `\p`/`\P`/`\N{U+` REFUSAL
> surface; the first wide producer owns the structure.

### 8. What this deletes

    pcrec_ext_class_pair_opens          (ext.c:354)  — §6
    RF_CLASS_BASE, RF_CLASS_INVALID     — §3
    parse.c:152's `\b` special case     — §3
    the `in_class` parameter            — position selects the PORT
    registry_check.c:875's skip_flag    — went with RF_CLASS_INVALID; K10's
                                          fourth blind net
    two missing doorway epilogues       — one epilogue, so they cannot be missing
    esc_class_value's bare `int`        — becomes a tagged field, which is
                                          K11's UB shape

### 9. Migration obligations

1. **SPEC-FA's accept-controls must be shown passing through the new path** —
   `[0-[a]`, `[0-[:]`, `[0-[:digit]`, `[0-[.]`.
   `tests/reject/run_reject_tests.sh:1019` states that without them the fix
   could over-reject every `[` endpoint and nothing would notice.
2. **The in-class sweep must be extended past one byte of tail context.** Its
   template is `"[\\%c]"`, so it can probe `[\N]` and never `[\N{U+41}]` — K10's
   fourth net. Removing `RF_CLASS_INVALID` without this leaves the gap in a new
   place.
3. **Every `EXT_*` outcome needs a probe that is false today.** R11/C4-1's
   failure shape: a check whose pass condition already held before the feature
   existed. Ask of each: *was this already true yesterday?*

### 10. Still unresolved, carried from D32 §10

Module swap between two rows, and row deletion. `tests/reject/`'s hand-written
manifest remains their only guard. This decision does not improve it.

**Revisit when:** a diagnostic is found that cannot outlive its handler (§5 is
falsified and `pair_opens` returns); or a construct is found whose SELECTED ROW
differs by position (§4 is falsified); or MOD-0.6 needs the class structure
wider than 256 bits (§7, expected, not a falsification).

## D34 — 2026-08-11 — Frank's rulings on the extension design's open questions; PART II is the redesign of record

**Decided** 2026-08-11 (Frank, fourth session of the day), after reviewing
`docs/design/extension_design.md` and its R13 refutations. Frank agreed with the
recommendations presented for each §10 open question; this entry records the
rulings, and **Part II of the design document (§11-§17) is the single design
pass they called for** — written the same session, PROPOSED pending the R14
panel. Where a ruling's rationale is long it lives in Part II, not here.

The rulings, by §10 item:

1. **(items 1+13)** A row carries TWO ORTHOGONAL COLUMNS: `status` (fact about
   PCRE2 — RS_BASE / RS_MODULE / RS_REJECTED / RS_NOT_OFFERED(option)) and
   `disposition` (fact about pcrec's roadmap — RD_PLANNED / RD_NEVER).
   "Requires module 'X'" renders only for RD_PLANNED. This is the K14 fix and
   it retires §10.1 as posed (both of its options were category errors).
2. **(item 2)** The bound-mode LIST is deferred to its own document, after an
   option sweep whose generator can produce the constructs (the §7 framing
   broke: `\x` is base grammar whose meaning ALT_BSUX changes, so the bound
   mode is not expressible as row statuses or names).
3. **(item 4)** Feature mask stays 32-bit, with a loud check at the ceiling.
4. **(item 5)** Toggles are CLI-only (`--without=NAME`), test-facing, not
   public API.
5. **(item 6)** RECOGNISERS AND EXTENT SCANS ARE ALWAYS LIVE; only producers
   gate. The whole-pattern pre-scan becomes the lexer in count mode; `backrefs`
   can land alone. (Part II §12.)
6. **(item 7)** Recognition is PER-PORT; the two ports of one row may disagree
   about presence, and that is PCRE2's own behaviour (`\12` at 12 groups:
   backref at atom, octal in class). ONE rank per row until a measured
   counterexample. (Part II §14. This supersedes D33 §4's position-independent
   arbitration — D33's own revisit-when trigger, hit by R13.)
7. **(item 8)** The class-position literal fallback (`\g \k \8 \9`, measured
   as the complete set over all 62 `[\c]` probes) becomes EXPLICIT data-driven
   class ports producing the letter as a scalar. A NULL class port regains its
   single meaning: permanently invalid at class position. This is the K13 fix.
   (Part II §14.3.)
8. **(item 9)** `\Q`, `\E`, `(?#...)` are LEXICAL-MODE constructs owned by the
   tokenizer: rows with NO ports, gated at the token. The sixth outcome is
   REJECTED; the five outcomes stay five and are again total over their
   domain. Lexical locus and gating are different axes: these rows keep their
   names (`quoting`, `comments`) and their refusals until implemented — they
   are NOT base grammar. (Part II §13, and 24 measurements behind it.)
9. **(items 10/10a)** C1's `want`×`may` re-cut of the ASK contract is ADOPTED
   as the basis, pending R14: want ∈ {CLAIM, VERDICT, RESULT}, may =
   {ALLOCATE, RECURSE, DIAGNOSE}, cursor moves only under RESULT; the gate
   demotes want and preserves may. (Part II §15.)
10. **(item 11)** The endpoint rule is MEASURED, not derived: evaluate the
    item at class position, its own error wins, success + SET → error 150 —
    with exactly ONE deviating cell (bracket doorway, HIGH side: the syntactic
    pair-open after `-` short-circuits to 150 unevaluated). The static SHAPE
    column loses its only consumer and is dropped. (Part II §16, 33 cells.)
11. **(item 12)** §8's check list is rebuilt by an author DENIED the design
    document (D27's separation, now measured to work twice); Part II §17.3
    hands that author nine invariants as inputs, not checks.

**Why record rulings separately from the design:** the document is where the
reasoning lives and will keep being revised by panels; this log is where "Frank
decided X on date Y" has to survive that revision.

**Revisit when:** R14 refutes a Part II section (expected route: §16's rule on
a cell outside the 33 measured, or §12.2's extent set proving incomplete); or
a bucket is found where two rows clash at both positions with different
winners (reopens one-rank-per-row); or the bound-mode sweep contradicts
RS_NOT_OFFERED as a status.

**Postscript, same session:** R14 ran against Part II and the expected route
fired — §16's rule was refuted on cells outside the 33 (a second deviating
cell, `[:<:]`, printed in the design's own table; a five-step evaluation
order), §12.2's extent set was proven incomplete ("backrefs can land alone"
is withdrawn), and §14.2's digit rule fell to the bucket it had not probed
(`\81` is err 115, not octal). Corrections are inline in Part II marked R14;
`docs/dev/reviews/2026-08-11-r14-part2.md` is the panel record; §18 holds the
five decisions R14 left for Frank (migration order, whether `may` survives,
where `quantifiable`/`captures` live, K13-fix sequencing, the bound-mode
document's scope). The rulings above stand except where §18 reopens them.

## D35 — 2026-08-12 — probe OUTPUT reports are archived as stable-named, diffable evidence files (docs/measurements/), never as oracles

**Decision (Frank, thirteenth session).** The full output of a
`tests/probes/` measurement run is archived in `docs/measurements/<probe>.txt`
via `scripts/measure.sh <probe>`, with a header recording the run's date,
repo commit, libpcre2 package version, and gcc version. The filename is
STABLE per probe rather than dated, so a re-measurement lands as a `git
diff` against the previous report — "what changed" is one command, which is
the point (Frank: "useful to see changes specifically so we know quickly
what changed. record source information obviously like version").

**Why.** Probe sources were always committed for reproducibility, but raw
outputs were session-scratch: R18 NOTED that MOD-0.4's 602-comparison
byte-identity sweep survives only as prose in the review file, and a future
libpcre2 upgrade makes any past run unreproducible — the pre-bump evidence
would exist nowhere. An archived report closes that at the cost of one file
per probe.

**The boundary that keeps this from becoming the stale-record failure:** a
report is EVIDENCE for reviews and design notes, never an oracle — no check
may read these files (the live re-measured checks in tests/registry/ remain
the strong form). Regeneration is DELIBERATE (probe change, oracle version
bump per D26's addendum, or a review needing current evidence), and the
diff is committed with a note on what moved.

**REFINED same session (Frank): a report is a PURE FUNCTION of its
dependencies, so validity is checkable without re-running.** The header
stamps the probe source's git blob hash, the ABI shim's blob hash, and the
oracle package version; `scripts/measure.sh --stale` compares every
report's stamps against the current tree and installed oracle and answers
VALID or STALE with the reason. A report whose stamps match its
dependencies never needs regeneration — "regenerate deliberately" above
reduces to "regenerate exactly when --stale says so (and commit the diff
with a note on what moved)". Environment residue (gcc version) is stamped
but NOT a staleness input: a well-defined probe's output does not depend
on the compiler that built it, and if one ever does, that is a probe bug.

**Revisit-when:** a report's diff ever becomes load-bearing in a check, or
the directory grows enough that nobody reads diffs — either is the signal
the convention has drifted from evidence into oracle or noise.

## D36 — `(?C` callouts re-scoped: NEVER → PLANNED, M4-hosted, pcrec-native binding (2026-08-12)

**Decision (Frank, fourteenth session):** the callout family `(?C)` /
`(?Cn)` / `(?C"text")` moves from ROADMAP_NEVER (K14's out-of-scope ruling,
"revisit only with a concrete customer") to a PLANNED module `callouts`,
explicitly LOW priority — parked at [M4-CALLOUTS] in the queue, behind the
M4 VM engine that hosts it. The compliance survey's revisit trigger was the
roadmap owner wanting it; that happened.

**The design layering that made the flip acceptable** (from the same
discussion, recorded so the M4 designer inherits it): compatibility splits
three ways. The PATTERN layer (syntax, where callouts may appear, matching
semantics) is D26-exact and fully PCRE2-compatible. The CALLBACK CONTRACT
(block contents, return-code meaning: 0 continue / >0 fail path / <0
abort) mirrors pcre2_callout_block field for field. The REGISTRATION API is
pcrec-native by design, as pcrec's whole API already is: the generated C
declares `extern int rx_callout_n(...)` and the embedding program defines
it — compile-time binding, no indirect call for patterns without callouts,
and V-A's compat layer implements pcre2_set_callout as a trampoline ON TOP
of the extern (dynamic-over-static composes; the reverse pays indirection
everywhere). Callouts are ENGINE-FORCING like backrefs: the compiled DFA
erases pattern positions at construction, so callout patterns compile to
the VM engine only. Fire-point precision is documented engine-relative —
PCRE2 itself requires PCRE2_NO_START_OPTIMIZE for predictable callout
invocation, which is the precedent that fire counts are not the contract.

**Explicitly rejected:** accept-and-discard (semantically sound for the
no-callback case, but it silently swallows the user's stated intent to
hook the match — refuse loudly instead until the module lands).

**Revisit-when:** M4's design begins (the behavior step), or any lane is
free for the flip step ([M4-CALLOUTS] part 1 — do not start it while
another lane owns registry.c/reject/case11).

## D37 — default-on policy: frozen NAMED sets, graduation criterion, stamped artifacts (2026-08-12)

**Decision (Frank, fourteenth session, ruling on the R20/0.8c sheet's item
1):** the middle path — modules ship DEFAULT-ON once they have survived a
checkpoint panel AND carry PC-3 differential coverage — amended by Frank's
consistency constraint: *"the set of standards should be consistent; if it
surprisingly changed at some point it might annoy developers midway through
their project."*

**The mechanism, so the default can grow without ever surprising anyone:**

- The default enabled set is a FROZEN NAMED SET. `std1` = {classes,
  modifiers} — the two modules that qualify today. A frozen set's contents
  NEVER change after it ships; `--features std1` compiles identically
  forever.
- unicode-props is NOT in std1: recogniser-only, no producer — the gate is
  measured byte-identical either way, and a set member with no effect is a
  false promise of one.
- Future graduates form the NEXT named set (`std2` = `std1` + {x}), they do
  not join an existing one. The BARE default (no `--features`) maps to a
  named set, and that mapping advances only at an ANNOUNCED version
  boundary — never within a version line — with every older named set
  remaining available verbatim forever. A developer mid-project either
  passes nothing and is protected by the version line, or pins `--features
  stdN` and is protected unconditionally.
- Emitted C is SELF-DESCRIBING: the header comment and a macro stamp the
  set name AND its expanded module list, so any artifact can be reproduced
  by any future pcrec by passing the stamped expansion — reproducibility
  does not depend on remembering what "default" meant that year.
- `--features none` remains the escape hatch and the honest empty set;
  explicit sets always win over the bare default.

**Why:** friction vs honesty resolved by separating them — `(?i)foo`
working out of the box is friction repair; the frozen-name discipline is
what keeps the honesty (nothing under a developer changes without an
announced, opt-outable boundary).

**Consequences owed at implementation** (recorded so the row inherits
them): reject_gated rows and every default-gate measurement in the suites
assume the default is EMPTY today — flipping the bare default inverts those
assumptions across reject counts, corpus `features` directives, check07's
gate equivalence, and the PC-3 gate state; the implementation row carries a
full re-baseline, and check09 per-name arming + check01 aperture/floors
(whose meanings shift with the default) land WITH it, not before.

**Revisit-when:** the first post-std1 graduation — it defines the
announcement mechanics in practice.

**Addendum (2026-08-13, [STD1b] landing, found by the oracle re-baseline
lane):** there are TWO "defaults" and the flip moves only one. The bare
default D37 names is the CLI-invocation default — cli/main.c resolves a
missing `--features` through `PCREC_DEFAULT_FEATURES`. A LIBRARY caller
that links libpcrec.a and calls `pcrec_compile()` without
`pcrec_enabled_set_spec()` runs at the raw enabled mask, which is EMPTY at
process start and stays empty: `pcrec_enabled_set_spec` is internal.h
surface, not lib/pcrec.h, because D20 rules the enabled set is internal
configuration, not a caller-facing option. So the library's raw default is
deliberately NOT a D37 named set today; tests/registry relies on this
(pcre2_check.c compiles at the empty set by construction and is
flip-immune). The question "what default does a promoted library channel
get" re-opens WITH that promotion, not before.

## D38 — M4 pre-freeze rulings: callout/match ABI, substitution contract, PC-5 dispositions (2026-08-14)

**Decision (Frank, eighteenth session, ruled interactively over the three
pre-freeze design inputs — docs/design/design_callout_abi.md,
docs/design/subst_template_design.md, docs/pcre2_options.md).** This entry
is the authoritative record; the three documents carry the applied text.

**Callout / match ABI:**

1. The aligned primitive is `rx_matchfn = ptrdiff_t (const rx_ctx *)`,
   `rx_ctx = { const unsigned char *subject; size_t len, pos, ncap;
   const ptrdiff_t (*caps)[2]; void *user }`. Returns matched length >= 0
   or -1.
2. The BINDING UNIT is a struct, not a bare function symbol:
   `rx_callout_ref { rx_matchfn *fn; void *user }`, one
   `extern const rx_callout_ref rx_callout_<name>` per callout. The
   engine copies `ref->user` into `ctx->user` before calling `ref->fn`.
   Per-binding static state; per-thread state is the callout's own
   business via `_Thread_local` (an `&tls_var` static initializer does
   not compile — noted so nobody tries). Using a compiled matcher as a
   callout is a one-line const struct wrap. Rejected: a single
   process-global user pointer (one value shared by all callouts), and a
   per-call user parameter (Frank: "ouch" — over-callback-friendly).
3. The match-here entry is exported UNCONDITIONALLY on every generated
   matcher (OS-0 naming; D37's artifacts-carry-their-contract precedent).
4. Native abort: NONE in v1 — match-or-fail only. Return values < -1 are
   RESERVED for a future abort semantic and enforced today by generated
   call sites: `if (ret < -1) __builtin_trap();` (freestanding-safe;
   libc abort() rejected for the no-libc line; longjmp abort rejected —
   setjmp cost on the warm entry path + volatile-locals hazard at -O2,
   and -2 gives the same expressiveness on the cold path).
5. Captures: OPAQUE across the composition boundary in v1. A callout
   sees the outer captures-so-far; a composed matcher's inner captures
   are invisible; the group form captures only the consumed span. The
   designated v2 path (recorded, not scheduled): declared-in-syntax
   export — the outer pattern states the callee's exported group count
   (direction: `(?Cc<n>"fn")`) because group numbering is compile-time
   (subst C1); requires a non-const ctx + capacity field, i.e. a DD-3
   struct revision.
6. `ncap` is a mid-match watermark at callout sites and is pinned to
   `ngroups + 1` with every pair written on a completed match (subst C6).
7. Syntax remains UNDECIDED (R-d): callout binding near-PCRE2 (`(?C...)`
   family favored — no collision, `(?C` is already a rejected doorway);
   embedded code possibly its own spelling (`\{ strlen($1) == 5 }`
   sketch); any spelling that reinterprets a currently-valid pattern is
   module-gated.

**Substitution (subst_template_design.md §9, all fourteen ruled):**

- Q1 `$0` is core. Q2 bare `$name` supported (greedy; the compile-time
  check defuses the footgun). Q3 unset-but-existing group renders EMPTY
  by default, as a GENERATION AXIS with a strict PCRE2-error variant —
  python becomes the clean oracle (§8.2). Q4 length-only, NO NUL
  termination or budget (8-bit clean; embedded NULs are legal output —
  Frank's own concern, answered by this shape). Q5 namespace rule
  ADOPTED as testable (every pcrec-only form must be a spelling PCRE2
  rejects) and `${!...}` reserved as the extension prefix. Q6 subsumed
  by ruling 2 above: renderer bindings use the same ref-struct shape.
  Q7 `--replace` now (repeatable per §5.5); V-E's manifest gains a
  template field when designed. Q8 `pcrec_error` gains a WHICH-INPUT
  tag (enum pattern/template) beside `pos` — lib/pcrec.h change at the
  M4 freeze. Q9 confirmed (byte offsets per DD-12; UTF is M5's). Q10
  duplicate names deferred with module named-groups. Q11 sizing is
  EXACT BY CONTRACT: renderers must honor out==NULL sizing and be
  deterministic across the passes; violations are the embedder's bug.
  Q12 `rx_span` BREAKS AT THE M4 FREEZE — becomes the ptrdiff_t pair
  type in one announced break (Frank: ptrdiff_t "clearer in a utf
  environment"); no permanent conversion seam. Q13 renderer =
  `rx_matchfn` + output buffer (`rx_renderfn(const rx_ctx*, unsigned
  char *out, size_t cap) -> ptrdiff_t`), same return discipline, shared
  out==NULL sizing. Q14 `const unsigned char *subject` (already
  applied).
- Also accepted: §2's C1–C11 as REQUIREMENTS on M4's match API (with
  §2.2's non-requirements); the module tiering `subst` /
  `subst-extended` / `subst-pcrec` (the run-time SUBSTITUTE_EXTENDED
  bit ceases to exist — a template's dialect is a singleton dimension);
  one function both modes with count-as-return.

**PC-5 (docs/pcre2_options.md):** the PROPOSED disposition column is
RATIFIED wholesale, with three rows ruled individually (outcomes match
the proposals): LITERAL = GENERATION-AXIS, later; DFA_SHORTEST = LATER
pending its own design note; COPY_MATCHED_SUBJECT = NEVER (allocation-
free generated matchers; caller owns the buffer — a documented
non-goal). Every row stays individually re-openable; adopting any flag
remains a deliberate re-measurement event (oracle pinned at options=0).

**Why:** these three documents are the declared inputs to M4's match-API
freeze; ruling them before M4.0 expands means the freeze starts from
settled ground. The rulings repeatedly chose: compile-time over
run-time (tiering, bounds checks, bindings), lengths over terminators,
per-binding state over globals, and reserved-and-trapped value space
over speculative mechanism.

**Revisit-when:** the M4 match-API design freeze itself (these are its
inputs, and rx_span's break lands there); D20's promotion for anything
library-default-shaped; V-E's manifest design for capture export and
the template field; the abort reservation if a real customer for
native abort appears.

**D38 addendum (Frank, same session): PARALLEL OPTION NAMING.** Every
PCRE2 option pcrec adopts (in whatever ruled form) gets a parallel
pcrec-native name — e.g. `PCRE2_LITERAL` and `PCREC_LITERAL`. The
PCREC_* spelling is pcrec's own surface (SR-10's namespace discipline);
the PCRE2_* spelling serves callers porting from PCRE2. LAYERING
SUB-QUESTION deliberately left open until V-A's design: whether pcrec
core accepts the PCRE2_* spellings directly (documented aliases) or
they exist only in V-A's compat layer. docs/pcre2_options.md carries
the scheme note; nothing emits either name until its owning row lands.

**D38 addendum, resolved same session (Frank):** the layering question
closes immediately — `PCRE2_*` IS FOR COMPATIBILITY, full stop. The
native surface is uniformly `PCREC_*` for every flag, because pcrec
will need its own non-PCRE2 flags and a mixed surface — some spelled
PCRE2_, some PCREC_ — is confusing. One canonical namespace
(PCREC_*), one compat aliasing surface (PCRE2_*, the V-A direction);
no flag is ever native under the PCRE2_ prefix.

## D39 — group naming: exported name→number index per pattern; appended numbering for rx references (2026-08-14)

**Decision (Frank, eighteenth session, same conversation as D38):**

1. **Per-pattern name→number index, exported.** The mapping is static,
   so it does NOT travel in rx_ctx or any callback parameter; instead
   every generated pattern exports a const structure for name → group
   number lookup (direction: a sorted `{const char *name; int number;}`
   array + count, bsearch-able; .rodata only, zero runtime cost).
   This AMENDS subst C10's non-requirement list ("no name table in the
   artifact"): template `${name}` still resolves at compile time — the
   exported index is a separate, deliberate artifact obligation, whose
   second customer is V-A's `pcre2_substring_number_from_name`. It
   joins the M4 freeze list (the artifact contract grows the index
   alongside the match-here entry).
2. **rx references (future: one regex refers to another, inserted at
   that point — V-E territory) use APPENDED numbering.** Inserted
   groups are NOT renumbered inline into the primary's sequence ("too
   complicated" — and inline renumbering makes the primary's numbers
   change whenever the referenced regex changes, the (?(DEFINE)
   brittleness). Instead: the primary keeps its own 1..N stable;
   inserted regexes' groups append at N+1.. in insertion order; group
   NAMES are kept and the point-1 index is the lookup path into
   results. Consequences inherited by V-E's design: backrefs inside an
   inserted regex renumber to their appended positions at insert time
   (compile-time); the caps array length stays a compile-time constant
   (1 + N_primary + sum of inserted), so subst C1/C7 hold.

**Open sub-question (recorded, ruled at V-E design time):** name
COLLISIONS in the flat index — primary and inserted regex sharing a
name, or the same regex inserted twice. Candidates: qualified names
for inserted groups (`sub.year` style — seemingly forced by the
inserted-twice case), compile error on collision, first-wins.

**Revisit-when:** M4 freeze (the index joins the artifact contract);
V-E's design start (numbering + collision policy applied there).

**D39 addendum (Frank, same session): the collision sub-question
RESOLVES toward LABELED REFERENCES.** An insertion site carries a
caller-supplied reference label — `"a:reg1"`, `"b:reg1"` for the same
regex inserted twice — and that reference is saved as an ADDITIONAL
COLUMN in the static name→number index. Nested insertions compose the
labels into a PATH (Frank's example: `"c:a"`). Consequence adopted with
it: the F8 index struct is BORN with the ref column at the M4 freeze —
`{const char *name; int number; const char *ref}` with NULL/empty ref
for the primary's own groups — so V-E's arrival extends data, not ABI
(no DD-3 break of the exported index). Still open, ruled at V-E design
time: the path spelling (order/separator of "c:a"), whether the label
is mandatory per insertion or optional-with-default for single
insertions, and lookup-key semantics (name-alone when unambiguous vs
ref+name). Frank also notes more group-names-static questions may
surface; they land here as further addenda.
