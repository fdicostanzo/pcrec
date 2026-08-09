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
