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

Rule 2 is why the two emitters M2.7 forked are now merged back into one
EOL-aware `emit_unanchored`: the fork is how the `$` path lost scan avoidance
for a whole milestone without any test noticing. Non-EOL output is
byte-identical across 8 probe patterns, so the merge is a no-op there.

Measured (7 trials each, load avg ~0.95): `ERROR: .*$` over 8 MB of log text
went 291 -> 22248 MB/s median, with non-overlapping ranges, and is now at
parity with `ERROR: .*` (22797 median). The non-EOL path is a statistical TIE
before vs after (13840-24282 vs 15242-24439) — an early single-sample reading
suggested a 1.4x gain there and was noise. Revisit-when: `^` joins this engine
(D8/DD-7), since a reverse BOT variant would add a second position-dependent
view with the same ordering hazard.
