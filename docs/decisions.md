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
is not comparable to what we had. Disabling the disjointness guard fails 2
cases in the entire 663-case .rxt corpus; it fails ~14 patterns in 500 here, at
TRIE_N=200 21 of 200, and each failure names the pattern rather than a subject
that happened to hit it. Disabling rule 1's accept split fails 132 of 200.

The trap, and the non-optional part: an equivalence check is vacuous if BOTH
builds have the optimization off. Then everything agrees and the script
certifies a deleted optimization — the exact "guard that cannot fail" shape R3
found twice in guards written the same day. So every equivalence check MUST
carry a positive control proving the shipped build still does the thing. Here
it is deterministic rather than timing-based: `(<256 8-bit binary
strings>){100}` needs ~230k NFA states unfactored and ~51k factored against a
131072 cap, so the two builds fail at different STAGES and the stage is visible
in the error text. Sabotage-validated: with the trie disabled in the shipped
build, identity passes 200/200 and the control is the only thing that fires.

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
never a regression in strictness. The CEILING is the part that needs stating:
it is NOT derived from the spread. A single run's within-run trial spread is a
sample, not a distribution, and this box's noise floor is ~10% even at
median-of-7 — gating tighter than 0.90 would manufacture failures out of noise
no matter how tight one run happened to look. The 1.05 safety factor pays for
the sample-vs-distribution gap; the ceiling pays for the floor being real.

Each run now also prints, per case, the smallest regression its margin can
actually fail on, and a summary line naming the weakest case in the matrix.
That number was always computable and for two checkpoints nobody computed it —
which is precisely how the gate came to be credited with a catch it could not
make. A guard should state its own blind spot in its own output.

Revisit-when: BENCH_TRIALS rises (a tighter median justifies a higher ceiling),
the matrix moves to different hardware, or a case's recorded spread stops
matching what it measures in practice.
